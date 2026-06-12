"""Screen stage: factor math in ClickHouse SQL -> ranked candidates table.

Factors: annualized premium yield, IV percentile vs 1y realized-vol
distribution, liquidity gates, earnings-date avoidance, moneyness band.
Usage: python screener.py <run_id>
"""
import sys
import uuid

import config
import db

HV_SQL = """
SELECT ticker, groupArray(hv) AS hvs FROM (
    SELECT ticker, ts,
           stddevSamp(r) OVER (PARTITION BY ticker ORDER BY ts
                               ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) * sqrt(252) AS hv
    FROM (
        SELECT ticker, ts,
               log(close / lagInFrame(close, 1) OVER (PARTITION BY ticker ORDER BY ts)) AS r
        FROM prices WHERE ticker IN {tickers:Array(String)}
    )
    WHERE isFinite(r)
)
WHERE isFinite(hv) AND hv > 0
GROUP BY ticker
"""

CANDIDATES_SQL = """
SELECT oc.ticker, oc.expiry, oc.strike, oc.bid, oc.iv, oc.oi, oc.spot,
       dateDiff('day', today(), oc.expiry) AS dte,
       oc.bid / oc.strike * 365.0 / dte AS y_ann,
       e.next_earnings AS next_earnings,
       (e.next_earnings IS NULL OR e.next_earnings > oc.expiry) AS earnings_ok
FROM option_chain oc
LEFT JOIN earnings e ON e.ticker = oc.ticker
WHERE oc.snapshot_ts = (SELECT max(snapshot_ts) FROM option_chain)
  AND oc.side = 'csp'
  AND dte >= {min_dte:UInt32}
  AND oc.bid >= 0.05
  AND oc.oi >= {min_oi:UInt32}
  AND oc.strike >= {m_lo:Float64} * oc.spot
  AND oc.strike <= {m_hi:Float64} * oc.spot
  AND oc.ask > oc.bid
  AND (oc.ask - oc.bid) / ((oc.ask + oc.bid) / 2) <= {max_spread:Float64}
ORDER BY y_ann DESC
"""


def iv_percentile(iv, hvs):
    if not hvs:
        return 0.5
    return sum(1 for h in hvs if h < iv) / len(hvs)


def run(run_id=None):
    run_id = run_id or uuid.uuid4().hex[:12]
    ch = db.client()

    hv_map = dict(ch.query(HV_SQL, parameters={"tickers": config.UNIVERSE}).result_rows)
    rows = ch.query(CANDIDATES_SQL, parameters={
        "min_dte": config.MIN_DTE, "min_oi": config.MIN_OPEN_INTEREST,
        "m_lo": config.MONEYNESS_LO, "m_hi": config.MONEYNESS_HI,
        "max_spread": config.MAX_SPREAD_PCT,
    }).result_rows

    # keep the single best contract per ticker, then score cross-sectionally
    best = {}
    for (ticker, expiry, strike, bid, iv, oi, spot, dte, y_ann, next_earn, earn_ok) in rows:
        ivp = iv_percentile(iv, hv_map.get(ticker, []))
        cand = dict(ticker=ticker, expiry=expiry, strike=strike, bid=bid, iv=iv,
                    oi=oi, spot=spot, dte=dte, y_ann=y_ann, iv_pct=ivp,
                    next_earnings=next_earn, earnings_ok=bool(earn_ok))
        if ticker not in best or cand["y_ann"] > best[ticker]["y_ann"]:
            best[ticker] = cand

    cands = sorted(best.values(), key=lambda c: c["y_ann"], reverse=True)
    n = len(cands)
    for i, c in enumerate(cands):
        yield_rank = 1 - i / max(n - 1, 1)
        c["score"] = round(100 * (0.55 * yield_rank + 0.35 * c["iv_pct"]
                                  + 0.10 * min(c["oi"] / 5000, 1.0))
                           * (1.0 if c["earnings_ok"] else 0.6), 1)
    cands.sort(key=lambda c: c["score"], reverse=True)

    ch.insert("candidates",
              [(run_id, c["ticker"], c["expiry"], c["strike"], "csp", c["bid"], c["spot"],
                c["y_ann"], c["iv"], c["iv_pct"], c["oi"], int(c["earnings_ok"]),
                c["next_earnings"], c["score"]) for c in cands],
              column_names=["run_id", "ticker", "expiry", "strike", "side", "bid", "spot",
                            "premium_yield_ann", "iv", "iv_pct", "oi", "earnings_ok",
                            "next_earnings", "score"])

    for c in cands:
        print(f"  {c['score']:5.1f}  {c['ticker']:<6} {c['expiry']} {c['strike']:>8.1f}P "
              f"bid={c['bid']:.2f} yield={c['y_ann']*100:5.1f}% ivp={c['iv_pct']:.2f} "
              f"oi={c['oi']:<6} earn_ok={c['earnings_ok']}")
    print(f"screen done: {n} candidates, run_id={run_id}")
    return run_id, cands


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
