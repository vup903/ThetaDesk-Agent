Source: https://github.com/vup903/ThetaDesk-Agent

# Product: The Daily Action Sheet

Theta Desk's core product is one publication: the **Daily Wheel Strategy Action Sheet**.

Each sheet contains, for every screened candidate:
- Ticker, option type (cash-secured put or covered call), strike, and expiry
- Premium (bid), spot price, and **annualized premium yield** (premium / collateral, annualized)
- Implied volatility and its percentile versus the trailing year
- Open interest and volume (liquidity check)
- Earnings-date check: whether an earnings report falls before expiry
- A composite score and rank
- A short cited risk analysis written by the desk's LLM analyst

The sheet is published once per US trading day to cited.md. The headline and summary are free; the full candidate table and analyses unlock for $0.01 via x402. Output is structured markdown, designed to be equally readable by humans and parseable by trading agents.

The sheet is research, not advice: it never recommends position sizes and always discloses assignment risk.
