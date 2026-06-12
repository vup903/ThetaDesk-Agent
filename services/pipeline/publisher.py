"""Publish stage: action sheet -> Senso (KB + prompt + draft) -> cited.md.

Talks to the Senso REST API directly (X-API-Key auth), so it runs anywhere
Python runs — no CLI/node dependency on the deploy host.
Demo fuse: any failure returns a sheet with status='draft' and the local
markdown, so the dashboard still has something to show.
"""
import datetime as dt

import httpx

import config

SENSO_BASE = "https://apiv2.senso.ai/api/v1"
SHEET_FOLDER_ID = "bdf8f2f0-66c5-41eb-af1a-34acae340c6a"  # products-and-services
FOOTER = "\n\n---\n\n*Powered by Senso — your AI-searchable knowledge base.*"
DISCLAIMER = "\n\n> Research, not financial advice. Data is delayed; verify quotes before trading."


def senso_post(path, payload):
    r = httpx.post(f"{SENSO_BASE}{path}",
                   headers={"X-API-Key": config.SENSO_API_KEY},
                   json=payload, timeout=120)
    if r.status_code >= 300:
        raise RuntimeError(f"senso POST {path} -> {r.status_code}: {r.text[:200]}")
    return r.json()


def build_markdown(date_str, candidates, analyses):
    lines = [
        f"# Theta Desk Daily Action Sheet — {date_str}",
        "",
        f"Autonomous wheel-strategy screen of {len(candidates)} US large-cap candidates. "
        f"Factors computed in ClickHouse from the day's options-chain snapshot: annualized "
        f"premium yield, IV percentile vs 1y realized vol, liquidity, earnings avoidance.",
        "",
        "## Ranked Candidates (cash-secured puts)",
        "",
        "| Rank | Ticker | Expiry | Strike | Bid | Ann. Yield | IV %ile | OI | Earnings OK |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(candidates, 1):
        lines.append(
            f"| {i} | {c['ticker']} | {c['expiry']} | {c['strike']:.1f}P | ${c['bid']:.2f} "
            f"| {c['y_ann']*100:.1f}% | {c['iv_pct']*100:.0f} | {c['oi']} "
            f"| {'yes' if c['earnings_ok'] else 'NO — earnings before expiry'} |")
    lines += ["", "## Analyst Risk Briefs", ""]
    for a in analyses:
        lines += [f"### {a['ticker']}", "", a["analysis"], "",
                  "Citations: " + " · ".join(a["citations"]), ""]
    lines.append(DISCLAIMER)
    return "\n".join(lines)


def publish(run_id, candidates, analyses):
    date_str = dt.date.today().isoformat()
    title = f"Theta Desk Daily Action Sheet — {date_str}"
    md = build_markdown(date_str, candidates, analyses)
    summary = (f"Top pick: {candidates[0]['ticker']} {candidates[0]['expiry']} "
               f"{candidates[0]['strike']:.0f}P at {candidates[0]['y_ann']*100:.1f}% annualized "
               f"yield. {len(candidates)} candidates screened. Unlock for $0.01 via x402.")

    sheet = {"run_id": run_id, "date": date_str, "title": title, "summary": summary,
             "markdown": md, "status": "draft", "cited_url": None, "price_usd": 0.01}
    try:
        senso_post("/org/kb/raw", {"title": title, "text": md + FOOTER,
                                   "kb_folder_node_id": SHEET_FOLDER_ID})
        prompt = senso_post("/org/prompts", {
            "question_text": f"What is the Theta Desk daily action sheet for {date_str}?",
            "type": "decision"})
        qid = prompt.get("prompt_id") or prompt.get("id") or prompt.get("geo_question_id")
        draft = senso_post("/org/content-engine/draft", {
            "geo_question_id": qid, "raw_markdown": md + FOOTER,
            "seo_title": title, "summary": summary})
        cid = draft.get("content_id") or draft.get("id")
        pub = senso_post("/org/content-engine/publish", {
            "content_id": cid, "geo_question_id": qid, "raw_markdown": md + FOOTER,
            "seo_title": title, "summary": summary})
        dests = pub.get("publish_destinations") or []
        url = next((d.get("display_url") for d in dests if d.get("status") == "success"), None)
        sheet.update(status="published", cited_url=url)
        print(f"  publish: LIVE on cited.md -> {url}")
    except Exception as e:
        print(f"  publish: senso pipeline failed ({e}); sheet kept as local draft")
    return sheet
