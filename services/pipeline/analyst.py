"""Analyze stage: Claude writes a cited risk brief per top candidate.

Demo fuse: if the API key is missing or the call fails, fall back to a
deterministic template analysis so the pipeline never dies on stage.
"""
import datetime as dt

import config
import pioneer_news

SYSTEM = (
    "You are the research analyst at Theta Desk, an autonomous options-income "
    "research desk. Voice: quantitative, matter-of-fact, numbers first, no hype. "
    "You write 3-4 sentence risk briefs for cash-secured-put candidates. Each brief "
    "must: (1) state why the premium is attractive using the given numbers, "
    "(2) name the main risk (assignment, IV level, upcoming events), "
    "(3) never recommend position sizes or promise returns."
)

CITED_KB = [
    "https://cited.md/article/88f8ed10-7fcc-4e21-9289-6c689c966811",
    "https://cited.md/article/de4080bf-7fb1-47d0-b321-15fa8e6f097a",
]


def _fallback(c):
    earn = ("No earnings report falls before expiry." if c["earnings_ok"]
            else f"Caution: earnings on {c['next_earnings']} lands before expiry.")
    return (
        f"{c['ticker']} {c['expiry']} {c['strike']:.0f}P bids ${c['bid']:.2f}, an annualized "
        f"premium yield of {c['y_ann']*100:.1f}% on ${c['strike']*100:,.0f} collateral. "
        f"Implied volatility of {c['iv']*100:.0f}% sits at the {c['iv_pct']*100:.0f}th percentile "
        f"of the trailing year's realized-volatility distribution, so premium is rich relative "
        f"to the stock's own history. {earn} Main risk: assignment if "
        f"{c['ticker']} falls {((c['spot']-c['strike'])/c['spot'])*100:.1f}% below spot "
        f"(${c['spot']:.2f}) by expiry. Research, not financial advice."
    )


def _prompt(c):
    return (
        f"Candidate: sell {c['ticker']} cash-secured put, strike {c['strike']}, expiry {c['expiry']} "
        f"({c['dte']} days). Data snapshot: bid ${c['bid']:.2f}, spot ${c['spot']:.2f}, "
        f"annualized premium yield {c['y_ann']*100:.1f}%, IV {c['iv']*100:.1f}% "
        f"(={c['iv_pct']*100:.0f}th percentile vs 1y realized-vol distribution), "
        f"open interest {c['oi']}, earnings_ok={c['earnings_ok']} "
        f"(next earnings: {c['next_earnings']}). Write the risk brief, "
        f"ending with 'Research, not financial advice.'"
    )


def analyze(candidates, top_n=None):
    """Returns [{ticker, analysis, citations}] for the top-N candidates."""
    top = candidates[: top_n or config.TOP_N_ANALYZE]
    snapshot_note = f"Data: Theta Desk ClickHouse snapshot {dt.date.today().isoformat()} (Yahoo Finance, delayed)"
    citations = CITED_KB + [snapshot_note]

    client = None
    if config.ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        except Exception as e:
            print(f"  analyst: anthropic client unavailable ({e}); using fallback")

    out = []
    for c in top:
        tags = pioneer_news.get_news_tags(c["ticker"])
        tag_note = ""
        if tags:
            tag_note = (" Recent headlines (risk-classified by Pioneer): "
                        + "; ".join(f"[{t['label']}] {t['headline']}" for t in tags)
                        + ". Weave the most relevant one into the risk assessment.")
        text = None
        if client is not None:
            try:
                msg = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=400,
                    system=SYSTEM,
                    messages=[{"role": "user", "content": _prompt(c) + tag_note}],
                )
                text = msg.content[0].text.strip()
            except Exception as e:
                print(f"  analyst: {c['ticker']} API call failed ({e}); using fallback")
        if not text:
            text = _fallback(c)
        out.append({"ticker": c["ticker"], "analysis": text,
                    "citations": citations, "news_tags": tags})
        print(f"  analyst: {c['ticker']} brief ready ({len(text)} chars, {len(tags)} news tags)")
    return out
