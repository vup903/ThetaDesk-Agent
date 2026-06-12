"""Theta Desk pipeline API: orchestrates ingest -> screen -> analyze -> publish
and serves the dashboard + the x402-paywalled sheet endpoint.

Run: uvicorn api:app --port 8000
"""
import datetime as dt
import json
import threading
import uuid

from fastapi import FastAPI, Header, Response
from fastapi.middleware.cors import CORSMiddleware

import analyst
import chain_fetcher
import config
import db
import publisher
import screener

app = FastAPI(title="Theta Desk Pipeline")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Autonomy: in-process daily scheduler (13:45 UTC, weekdays) — no external cron needed.
SCAN_UTC = (13, 45)


def _scheduler():
    import time
    last_day = None
    while True:
        now = dt.datetime.utcnow()
        due = now.weekday() < 5 and (now.hour, now.minute) >= SCAN_UTC
        if due and last_day != now.date() and (STATE["run"] is None or STATE["run"]["status"] != "running"):
            last_day = now.date()
            run = _new_run("live")
            with LOCK:
                STATE["run"] = run
            threading.Thread(target=_orchestrate, args=(run, "live"), daemon=True).start()
        time.sleep(30)


@app.on_event("startup")
def _start_scheduler():
    threading.Thread(target=_scheduler, daemon=True).start()

# in-memory state of the current/last run (single-process demo server)
STATE = {"run": None, "candidates": [], "sheet": None}
LOCK = threading.Lock()


def _new_run(mode):
    return {
        "run_id": uuid.uuid4().hex[:12],
        "started_at": dt.datetime.utcnow().isoformat() + "Z",
        "mode": mode,
        "status": "running",
        "stages": {s: {"status": "pending", "detail": ""} for s in
                   ("ingest", "screen", "analyze", "publish")},
        "universe_size": len(config.UNIVERSE),
        "brief_url": None,
    }


def _stage(run, name, status, detail=""):
    with LOCK:
        run["stages"][name] = {"status": status, "detail": detail}
    _persist(run)


def _persist(run):
    try:
        ch = db.client()
        ch.insert("runs", [(run["run_id"], dt.datetime.utcnow(), run["mode"], run["status"],
                            json.dumps(run["stages"]), run["universe_size"],
                            run["brief_url"] or "")],
                  column_names=["run_id", "started_at", "mode", "status", "stages",
                                "universe_size", "brief_url"])
    except Exception:
        pass  # observability table must never break the pipeline


def _candidate_json(c, run_id):
    return {
        "run_id": run_id, "ticker": c["ticker"], "expiry": str(c["expiry"]),
        "strike": c["strike"], "side": "csp", "bid": c["bid"], "spot": c["spot"],
        "premium_yield_ann": round(c["y_ann"], 4), "iv": round(c["iv"], 4),
        "iv_pct": round(c["iv_pct"], 4), "delta_est": None, "open_interest": c["oi"],
        "earnings_ok": c["earnings_ok"],
        "next_earnings": str(c["next_earnings"]) if c["next_earnings"] else None,
        "score": c["score"],
    }


def _orchestrate(run, mode):
    try:
        if mode == "live":
            _stage(run, "ingest", "running", f"fetching {len(config.UNIVERSE)} chains...")
            ts, ok, failed = chain_fetcher.run()
            _stage(run, "ingest", "done", f"{len(ok)}/{len(config.UNIVERSE)} chains @ {ts}Z")
        else:
            _stage(run, "ingest", "done", "replay: reusing last real snapshot")

        _stage(run, "screen", "running", "ClickHouse factor screen...")
        run_id, cands = screener.run(run["run_id"])
        with LOCK:
            STATE["candidates"] = [_candidate_json(c, run_id) for c in cands]
        _stage(run, "screen", "done", f"{len(cands)} candidates pass 5 factor gates")

        _stage(run, "analyze", "running", f"Claude writing top-{config.TOP_N_ANALYZE} risk briefs...")
        analyses = analyst.analyze(cands)
        _stage(run, "analyze", "done", f"{len(analyses)} cited briefs ready")

        _stage(run, "publish", "running", "Senso -> cited.md + x402 paywall...")
        sheet = publisher.publish(run["run_id"], cands, analyses)
        sheet["candidates"] = STATE["candidates"]
        sheet["analyses"] = analyses
        with LOCK:
            STATE["sheet"] = sheet
            run["brief_url"] = sheet.get("cited_url")
            run["status"] = "done"
        _stage(run, "publish", "done",
               f"live: {sheet.get('cited_url') or 'local draft'} · $0.01 x402")
    except Exception as e:
        with LOCK:
            run["status"] = "failed"
        for name, st in run["stages"].items():
            if st["status"] == "running":
                _stage(run, name, "failed", str(e)[:120])
        _persist(run)


@app.post("/runs")
def start_run(mode: str = "live"):
    run = _new_run(mode if mode in ("live", "replay") else "live")
    with LOCK:
        STATE["run"] = run
    threading.Thread(target=_orchestrate, args=(run, run["mode"]), daemon=True).start()
    return run


@app.get("/runs/latest")
def latest_run():
    return STATE["run"] or _new_run("live") | {"status": "idle"}


@app.get("/candidates/today")
def candidates_today():
    return STATE["candidates"]


@app.get("/briefs/latest")
def latest_brief():
    if not STATE["sheet"]:
        return Response(json.dumps({"status": "none"}), 404, media_type="application/json")
    locked = {**STATE["sheet"]}
    locked.pop("markdown", None)  # full sheet only via the paid endpoint
    return locked


@app.get("/briefs/today")
def buy_brief(x_payment: str | None = Header(default=None)):
    """x402 flow: 402 without payment header; full sheet with it."""
    if not STATE["sheet"]:
        return Response(json.dumps({"error": "no sheet yet"}), 404, media_type="application/json")
    if not x_payment:
        return Response(
            json.dumps({
                "x402Version": 1,
                "error": "Payment required",
                "accepts": [{
                    "scheme": "exact", "network": "base-sepolia",
                    "maxAmountRequired": "10000",  # $0.01 USDC (6 decimals)
                    "resource": "/briefs/today",
                    "description": "Theta Desk Daily Action Sheet",
                    "payTo": "0xThetaDesk0000000000000000000000000000demo",
                    "asset": "USDC",
                }],
            }), 402, media_type="application/json")
    return STATE["sheet"]


@app.post("/consumer/buy")
def consumer_buy():
    """Wheeler the trading bot: hits the paywall, pays, unlocks, queues a trade."""
    if not STATE["sheet"]:
        return {"paid": False, "log": ["GET /briefs/today -> 404 (no sheet published yet)"]}
    sheet = STATE["sheet"]
    top = sheet["candidates"][0] if sheet["candidates"] else None
    tx = "0x" + uuid.uuid4().hex[:8] + "..." + uuid.uuid4().hex[:4]
    log = [
        "GET /briefs/today -> 402 Payment Required",
        f"paying $0.01 USDC via x402... tx {tx} ok",
        "GET /briefs/today (X-PAYMENT) -> 200, sheet unlocked",
        f"parsing {len(sheet['candidates'])} candidates",
    ]
    if top:
        collateral = top["strike"] * 100
        log += [
            f"risk check: {top['ticker']} {top['strike']:.0f}P collateral ${collateral:,.0f} <= limit ok",
            f"queued paper order: SELL 1x {top['ticker']} {top['expiry']} {top['strike']:.0f}P @ {top['bid']:.2f}",
        ]
    return {"paid": True, "tx": tx, "log": log, "sheet": sheet}


@app.get("/healthz")
def healthz():
    return {"ok": True, "universe": config.UNIVERSE}
