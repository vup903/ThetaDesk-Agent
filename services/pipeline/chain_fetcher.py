"""Ingest stage: options chains + price history + earnings dates -> ClickHouse.

Usage: python chain_fetcher.py [TICKER ...]   (defaults to config.UNIVERSE)
"""
import datetime as dt
import math
import re
import sys

import httpx
import yfinance as yf

import config
import db

OCC_RE = re.compile(r"^([A-Z]+)(\d{6})([CP])(\d{8})$")


def fetch_cboe_chain(ticker, snapshot_ts, today):
    """Fallback chain source: CBOE delayed quotes (free CDN, no key).
    Used when Yahoo rate-limits the deploy host's IP."""
    j = httpx.get(
        f"https://cdn.cboe.com/api/global/delayed_quotes/options/{ticker}.json",
        timeout=30).json()
    spot = float(j["data"]["current_price"])
    rows = []
    for o in j["data"].get("options", []):
        m = OCC_RE.match((o.get("option") or "").replace(" ", ""))
        if not m or m.group(1) != ticker:
            continue
        d = m.group(2)
        expiry = dt.date(2000 + int(d[:2]), int(d[2:4]), int(d[4:6]))
        if not (config.MIN_DTE <= (expiry - today).days <= config.MAX_DTE):
            continue
        rows.append((snapshot_ts, ticker, expiry, int(m.group(4)) / 1000.0,
                     "csp" if m.group(3) == "P" else "cc",
                     float(o.get("bid") or 0), float(o.get("ask") or 0),
                     float(o.get("iv") or 0), int(o.get("open_interest") or 0),
                     int(o.get("volume") or 0), spot))
    return rows


def in_dte_window(expiry_str, today):
    expiry = dt.date.fromisoformat(expiry_str)
    return config.MIN_DTE <= (expiry - today).days <= config.MAX_DTE


def fetch_ticker(t, ticker, snapshot_ts, today):
    """Returns (chain_rows, price_rows, earnings_row) for one ticker."""
    spot = float(t.fast_info["lastPrice"])

    chain_rows = []
    expiries = [e for e in t.options if in_dte_window(e, today)][:3]
    for exp in expiries:
        chain = t.option_chain(exp)
        for side, frame in (("csp", chain.puts), ("cc", chain.calls)):
            for r in frame.itertuples():
                bid = 0.0 if math.isnan(r.bid) else float(r.bid)
                ask = 0.0 if math.isnan(r.ask) else float(r.ask)
                iv = 0.0 if math.isnan(r.impliedVolatility) else float(r.impliedVolatility)
                oi = 0 if math.isnan(r.openInterest) else int(r.openInterest)
                vol = 0 if (r.volume is None or math.isnan(r.volume)) else int(r.volume)
                chain_rows.append((snapshot_ts, ticker, dt.date.fromisoformat(exp),
                                   float(r.strike), side, bid, ask, iv, oi, vol, spot))

    hist = t.history(period="1y")
    price_rows = [(ticker, ts.to_pydatetime().replace(tzinfo=None),
                   float(row.Close), int(row.Volume))
                  for ts, row in hist.iterrows()]

    next_earnings = None
    try:
        dates = t.calendar.get("Earnings Date") or []
        if dates:
            next_earnings = dates[0]
    except Exception:
        pass

    return chain_rows, price_rows, (ticker, next_earnings, snapshot_ts)


def run(universe=None):
    universe = universe or config.UNIVERSE
    ch = db.client()
    db.ensure_schema(ch)
    snapshot_ts = dt.datetime.utcnow().replace(microsecond=0)
    today = dt.date.today()

    ok, failed = [], []
    for ticker in universe:
        try:
            chain_rows, price_rows, earn = fetch_ticker(yf.Ticker(ticker), ticker, snapshot_ts, today)
            if chain_rows:
                ch.insert("option_chain", chain_rows,
                          column_names=["snapshot_ts", "ticker", "expiry", "strike", "side",
                                        "bid", "ask", "iv", "oi", "volume", "spot"])
            if price_rows:
                ch.insert("prices", price_rows, column_names=["ticker", "ts", "close", "volume"])
            ch.insert("earnings", [earn], column_names=["ticker", "next_earnings", "snapshot_ts"])
            ok.append(ticker)
            print(f"  {ticker}: {len(chain_rows)} contracts, {len(price_rows)} price rows, earnings={earn[1]}")
        except Exception as e:  # Yahoo blocked? fall back to CBOE delayed quotes
            try:
                chain_rows = fetch_cboe_chain(ticker, snapshot_ts, today)
                if not chain_rows:
                    raise RuntimeError("cboe returned no contracts in DTE window")
                ch.insert("option_chain", chain_rows,
                          column_names=["snapshot_ts", "ticker", "expiry", "strike", "side",
                                        "bid", "ask", "iv", "oi", "volume", "spot"])
                ok.append(ticker)
                print(f"  {ticker}: {len(chain_rows)} contracts via CBOE fallback (yahoo: {e})")
            except Exception as e2:  # demo rule: one bad ticker never kills the run
                failed.append(ticker)
                print(f"  {ticker}: FAILED (yahoo: {e} | cboe: {e2})")

    print(f"ingest done: {len(ok)} ok, {len(failed)} failed, snapshot {snapshot_ts}Z")
    return snapshot_ts, ok, failed


if __name__ == "__main__":
    run(sys.argv[1:] or None)
