"""M2b: price-history pipeline via PyAirbyte (Airbyte's Python engine).

Pulls daily closes for the universe through Airbyte's source-yahoo-finance-price
connector and lands them in the ClickHouse `prices` table — the same table the
screener's IV-percentile factor reads from.

Usage: python airbyte_prices.py
"""
import datetime as dt

import airbyte as ab

import config
import db


def run():
    source = ab.get_source(
        "source-yahoo-finance-price",
        config={
            "tickers": ",".join(config.UNIVERSE),
            "interval": "1d",
            "range": "1y",
        },
        install_if_missing=True,
    )
    source.check()
    source.select_all_streams()
    result = source.read()

    rows = []
    for stream_name, dataset in result.streams.items():
        for rec in dataset:
            rec = dict(rec)
            # connector returns yahoo chart payloads; flatten defensively
            ticker = (rec.get("ticker") or rec.get("symbol")
                      or (rec.get("meta") or {}).get("symbol"))
            ts = rec.get("date") or rec.get("timestamp") or rec.get("datetime")
            close = rec.get("close") or rec.get("adjclose")
            volume = rec.get("volume") or 0
            if not (ticker and ts and close):
                continue
            if isinstance(ts, (int, float)):
                ts = dt.datetime.utcfromtimestamp(int(ts))
            elif isinstance(ts, str):
                ts = dt.datetime.fromisoformat(ts[:19])
            rows.append((str(ticker), ts, float(close), int(volume or 0)))

    if not rows:
        # dump one raw record per stream so we can adapt the field mapping
        for stream_name, dataset in result.streams.items():
            for rec in dataset:
                print(f"sample[{stream_name}]:", dict(rec))
                break
        raise SystemExit("no rows parsed — check field mapping above")

    ch = db.client()
    db.ensure_schema(ch)
    ch.insert("prices", rows, column_names=["ticker", "ts", "close", "volume"])
    print(f"airbyte pipeline done: {len(rows)} price rows -> ClickHouse")


if __name__ == "__main__":
    run()
