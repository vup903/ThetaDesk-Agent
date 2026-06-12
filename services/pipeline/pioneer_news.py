"""Pioneer (Fastino) integration: classify each candidate's latest headlines
into risk types before the Claude analyst writes its brief.

Demo fuse: any failure returns [] — the pipeline never blocks on this stage.
"""
import httpx

import config

PIONEER_BASE = "https://api.pioneer.ai/v1"
PIONEER_KEY = config.PIONEER_API_KEY
MODEL = "meta-llama/Llama-3.2-3B-Instruct"
LABELS = ["earnings_risk", "regulatory_risk", "legal_risk",
          "product_news", "macro_risk", "no_risk"]


def _classify(headline):
    r = httpx.post(
        f"{PIONEER_BASE}/chat/completions",
        headers={"X-API-Key": PIONEER_KEY},
        json={
            "model": MODEL,
            "max_tokens": 10,
            "messages": [{
                "role": "user",
                "content": ("Classify this stock headline into exactly one of "
                            f"{LABELS} and reply with only the label: {headline}"),
            }],
        },
        timeout=15,
    )
    r.raise_for_status()
    label = r.json()["choices"][0]["message"]["content"].strip().lower()
    return label if label in LABELS else "no_risk"


def get_news_tags(ticker, max_headlines=3):
    """Returns [{headline, label}] for the ticker's latest news."""
    if not PIONEER_KEY:
        return []
    try:
        import yfinance as yf
        news = yf.Ticker(ticker).news or []
        out = []
        for item in news[:max_headlines]:
            title = (item.get("content") or {}).get("title") or item.get("title")
            if not title:
                continue
            try:
                out.append({"headline": title, "label": _classify(title)})
            except Exception:
                continue
        return out
    except Exception:
        return []
