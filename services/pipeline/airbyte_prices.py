"""M2b: price-history pipeline via PyAirbyte (Airbyte's Python engine).

Airbyte's source-file connector extracts daily-price CSVs from Alpha Vantage
and lands them in the ClickHouse `prices` table — the same table the
screener's IV-percentile factor reads from. ReplacingMergeTree dedups
overlaps with the yfinance backfill.

Usage: python airbyte_prices.py [TICKER ...]   (defaults to config.UNIVERSE)
Note: Alpha Vantage free tier = 25 requests/day; one full universe load = 10.
"""
import datetime as dt
import os
import pathlib
import sys
import time

import airbyte as ab
import httpx

import config
import db

AV_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "")
DATA_DIR = pathlib.Path(__file__).parent / "data" / "av_csv"


def csv_url(ticker):
    return ("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
            f"&symbol={ticker}&apikey={AV_KEY}&datatype=csv&outputsize=compact")


def download_csv(ticker):
    """One metered Alpha Vantage request per ticker; validates it's real CSV."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{ticker}.csv"
    body = httpx.get(csv_url(ticker), timeout=60).text
    if not body.lstrip().startswith("timestamp"):
        raise RuntimeError(f"Alpha Vantage non-CSV reply: {body[:80]}")
    path.write_text(body, encoding="utf-8")
    return path


def load_ticker(ticker):
    name = f"prices_{ticker.lower()}"
    path = download_csv(ticker)
    source = ab.get_source(
        "source-file",
        config={
            "dataset_name": name,
            "format": "csv",
            "url": str(path),
            "provider": {"storage": "local"},
        },
        install_if_missing=True,
    )
    source.check()
    source.select_all_streams()
    result = source.read()

    rows = []
    for rec in result[name]:
        rec = dict(rec)
        ts, close = rec.get("timestamp"), rec.get("close")
        if not (ts and close):
            continue  # rate-limit notes / junk rows
        rows.append((ticker, dt.datetime.fromisoformat(str(ts)[:10]),
                     float(close), int(float(rec.get("volume") or 0))))
    return rows


def run(universe=None):
    if not AV_KEY:
        raise SystemExit("ALPHAVANTAGE_API_KEY missing in .env")
    universe = universe or config.UNIVERSE
    ch = db.client()
    db.ensure_schema(ch)

    total = 0
    for ticker in universe:
        try:
            rows = load_ticker(ticker)
            if rows:
                ch.insert("prices", rows, column_names=["ticker", "ts", "close", "volume"])
            total += len(rows)
            print(f"  {ticker}: {len(rows)} rows via Airbyte source-file")
        except Exception as e:
            print(f"  {ticker}: FAILED ({str(e)[:120]})")
        time.sleep(13)  # stay under Alpha Vantage's 5 req/min free limit
    print(f"airbyte pipeline done: {total} price rows -> ClickHouse")


if __name__ == "__main__":
    run(sys.argv[1:] or None)
