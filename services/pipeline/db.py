import clickhouse_connect

import config

DDL = [
    """
    CREATE TABLE IF NOT EXISTS prices (
        ticker String, ts DateTime, close Float64, volume UInt64
    ) ENGINE = ReplacingMergeTree ORDER BY (ticker, ts)
    """,
    """
    CREATE TABLE IF NOT EXISTS option_chain (
        snapshot_ts DateTime, ticker String, expiry Date, strike Float64,
        side LowCardinality(String), bid Float64, ask Float64, iv Float64,
        oi UInt64, volume UInt64, spot Float64
    ) ENGINE = MergeTree ORDER BY (ticker, expiry, strike, side, snapshot_ts)
    """,
    """
    CREATE TABLE IF NOT EXISTS earnings (
        ticker String, next_earnings Nullable(Date), snapshot_ts DateTime
    ) ENGINE = ReplacingMergeTree ORDER BY ticker
    """,
    """
    CREATE TABLE IF NOT EXISTS candidates (
        run_id String, ticker String, expiry Date, strike Float64,
        side LowCardinality(String), bid Float64, spot Float64,
        premium_yield_ann Float64, iv Float64, iv_pct Float64,
        oi UInt64, earnings_ok UInt8, next_earnings Nullable(Date),
        score Float64, created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree ORDER BY (run_id, score)
    """,
    """
    CREATE TABLE IF NOT EXISTS runs (
        run_id String, started_at DateTime, mode LowCardinality(String),
        status LowCardinality(String), stages String, universe_size UInt32,
        brief_url String, updated_at DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at) ORDER BY run_id
    """,
]


def client():
    return clickhouse_connect.get_client(
        host=config.CLICKHOUSE_HOST,
        username=config.CLICKHOUSE_USER,
        password=config.CLICKHOUSE_PASSWORD,
        secure=True,
    )


def ensure_schema(ch):
    for stmt in DDL:
        ch.command(stmt)


if __name__ == "__main__":
    ch = client()
    ensure_schema(ch)
    print("schema ok:", [r[0] for r in ch.query("SHOW TABLES").result_rows])
