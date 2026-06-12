import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

CLICKHOUSE_HOST = os.environ["CLICKHOUSE_HOST"]
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ["CLICKHOUSE_PASSWORD"]

SENSO_API_KEY = os.getenv("SENSO_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PIONEER_API_KEY = os.getenv("PIONEER_API_KEY", "")
RUN_API_KEY = os.getenv("RUN_API_KEY", "")
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "https://thetadesk-agent.onrender.com,http://localhost:3000,http://127.0.0.1:3000",
    ).split(",") if origin.strip()
]

UNIVERSE = [t.strip() for t in os.getenv(
    "UNIVERSE", "AAPL,MSFT,NVDA,AMD,TSLA,GOOGL,AMZN,META,PLTR,SOFI"
).split(",") if t.strip()]

# cost fuses — keep a public demo endpoint from burning API credits
RUNS_PER_HOUR = int(os.getenv("RUNS_PER_HOUR", "6"))
RUNS_PER_DAY = int(os.getenv("RUNS_PER_DAY", "20"))
CLAUDE_DAILY_CALL_BUDGET = int(os.getenv("CLAUDE_DAILY_CALL_BUDGET", "40"))
REPLAY_PACE_SECS = float(os.getenv("REPLAY_PACE_SECS", "4"))

# screener gates
MIN_DTE, MAX_DTE = 14, 45          # days to expiry window
MONEYNESS_LO, MONEYNESS_HI = 0.85, 0.97   # strike/spot band for CSPs
MIN_OPEN_INTEREST = 100
MAX_SPREAD_PCT = 0.5               # (ask-bid)/mid must be below this
TOP_N_ANALYZE = 5
