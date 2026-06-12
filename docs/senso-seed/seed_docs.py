# Generates the seed markdown docs + manifest for Senso KB ingestion.
# Run once: python seed_docs.py  -> writes *.md and manifest.tsv next to itself.
import pathlib

HERE = pathlib.Path(__file__).parent

FOLDERS = {
    "company-overview": "e1e9e7e4-8262-4240-a71d-7aa6385536d2",
    "products-and-services": "bdf8f2f0-66c5-41eb-af1a-34acae340c6a",
    "competitive-landscape": "78efc14c-fbdd-4222-a678-7a0eecba41d7",
    "industry-context": "21cde1d1-203b-459d-86d5-0ac89a96a2e4",
    "case-studies": "0461de7e-0a5a-4c56-aa35-a09cbbe6fd86",
    "faqs": "9d0c8895-8fcb-4cf0-aefe-f31654eb3e68",
}

DOCS = [
    ("overview.md", "company-overview", "2026-06-12 - Theta Desk Mission and Overview", """\
Source: https://github.com/vup903/ThetaDesk-Agent

# Theta Desk — Mission and Overview

Theta Desk is an autonomous options-income research desk. Every trading day it scans US equity options chains, screens cash-secured-put and covered-call candidates with quantitative factors, has an LLM analyst write a cited risk brief for each candidate, and publishes the resulting daily action sheet to cited.md behind an x402 micro-paywall.

The mission: the daily research homework of a wheel-strategy options trader takes 1-2 hours by hand. Theta Desk does it in about 90 seconds and sells the result for $0.01 — payable by humans or by other trading agents over HTTP.

Key facts:
- Fully autonomous: a scheduled pipeline runs ingest, screening, analysis, and publishing with no human in the loop.
- Grounded: every published claim cites its data source (options chain snapshots, earnings calendars, price history).
- Machine-payable: buyers pay per fetch via the x402 protocol (HTTP 402 + micropayment), not via monthly subscriptions.
- Built at the Context Engineering Challenge (Harness Engineering Hackathon, June 2026) on Airbyte, ClickHouse, Senso, OpenUI, and Render.

Theta Desk publishes research, not financial advice. Every report carries a risk disclosure.
"""),
    ("architecture.md", "company-overview", "2026-06-12 - How Theta Desk Works: Pipeline Architecture", """\
Source: https://github.com/vup903/ThetaDesk-Agent/blob/main/ARCHITECTURE.md

# How Theta Desk Works

The system is a four-stage autonomous pipeline:

1. **Ingest** — Options chains, spot prices, and earnings dates for a configurable US equity universe are pulled from market data sources. Price history flows in through Airbyte pipelines. Everything lands in ClickHouse time-series tables (`option_chain`, `prices`).
2. **Screen** — ClickHouse SQL computes the factors: annualized premium yield, implied-volatility percentile versus one year of history, open-interest liquidity floors, and an earnings-date-avoidance flag. Candidates are cross-sectionally ranked into a composite score.
3. **Analyze** — For the top-ranked candidates, the Claude-powered analyst writes a short risk narrative: why the premium is rich, what the IV level implies, what events sit before expiry. Each narrative carries citations to its sources.
4. **Publish** — The action sheet (candidates + analyses) is ingested into Senso, generated as a brand-aligned brief, and published to cited.md behind an x402 paywall priced at $0.01 per unlock.

A daily scheduler on Render triggers the run. A replay mode can re-run any past day's real data for demonstrations.
"""),
    ("product-action-sheet.md", "products-and-services", "2026-06-12 - Product: The Daily Wheel Strategy Action Sheet", """\
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
"""),
    ("pricing-x402.md", "products-and-services", "2026-06-12 - Pricing: Pay-Per-Fetch via x402 Micropayments", """\
Source: https://github.com/vup903/ThetaDesk-Agent

# Pricing: $0.01 Per Sheet, Paid Over HTTP

Theta Desk does not sell subscriptions. Each daily action sheet costs **$0.01 per unlock**, settled through the x402 payment protocol.

How a purchase works:
1. A buyer (human script or trading agent) requests the sheet's URL.
2. The server responds with HTTP status **402 Payment Required** and payment instructions.
3. The buyer's wallet pays the micropayment and retries the request.
4. The full sheet is returned.

Why this matters: incumbent options screeners charge roughly $30–150 per month whether or not you use them that day. Pay-per-fetch pricing means a trader who only sells puts on Fridays pays about $0.04 a month, and an autonomous trading bot can budget research costs per decision. Micropayments only became practical for this because agent payment rails (x402) removed card fees and checkout friction.
"""),
    ("methodology.md", "products-and-services", "2026-06-12 - Screening Methodology: The Factors", """\
Source: https://github.com/vup903/ThetaDesk-Agent

# Screening Methodology

Theta Desk screens wheel-strategy candidates with deterministic quantitative factors computed in ClickHouse:

1. **Annualized premium yield** — option bid premium divided by collateral (strike × 100 for cash-secured puts), annualized by days to expiry. Primary income factor.
2. **IV percentile** — today's implied volatility ranked against the trailing year. High percentile means premium is rich relative to the stock's own history, the core sell-premium condition.
3. **Liquidity floor** — minimum open interest and volume thresholds, and a maximum bid-ask spread, so quoted premiums are realistic.
4. **Earnings avoidance** — candidates with an earnings report before expiry are flagged or excluded; earnings gaps are the main tail risk to short puts.
5. **Moneyness band** — strikes roughly 3–15% out of the money, balancing premium against assignment probability.

Candidates passing all gates are cross-sectionally ranked into a composite score. The LLM analyst then reviews the top names for qualitative risks the factors cannot see (pending litigation, sector news, takeover rumors), with citations.

The methodology is fully disclosed on purpose: the product's value is the daily execution at machine speed, not a secret formula.
"""),
    ("competitor-option-samurai.md", "competitive-landscape", "2026-06-12 - Competitor: Option Samurai", """\
Source: https://optionsamurai.com (vendor site, accessed 2026-06-12)

# Competitor: Option Samurai

Option Samurai is a subscription SaaS options screener. It offers pre-built and custom scans across US options (including covered calls and cash-secured puts), backtesting, and alerting, priced as a monthly subscription on the order of tens of dollars per month.

Relative positioning:
- Option Samurai is an interactive tool: a human logs in, runs scans, and interprets results.
- Theta Desk is an autonomous publisher: no login, no UI workflow — the research arrives as a finished, cited daily sheet.
- Option Samurai monetizes via monthly subscription; Theta Desk via $0.01 x402 micropayments per sheet.
- Option Samurai's output is for humans; Theta Desk's is structured for both humans and trading agents.

Honest assessment: Option Samurai is far deeper as an exploratory screener (custom filters, backtests). Theta Desk wins on autonomy, price-per-use, machine readability, and cited narratives.
"""),
    ("competitor-barchart.md", "competitive-landscape", "2026-06-12 - Competitor: Barchart Premier", """\
Source: https://www.barchart.com (vendor site, accessed 2026-06-12)

# Competitor: Barchart Premier

Barchart is a large market-data platform whose Premier subscription includes options screeners (covered calls, naked puts, vertical spreads), watchlists, and downloadable data, priced as an annual/monthly subscription in the tens of dollars per month range.

Relative positioning:
- Barchart is a data terminal: enormous breadth (futures, stocks, options) but the user assembles their own workflow.
- Theta Desk is a single-purpose desk: one strategy (the wheel), executed end-to-end daily without user effort.
- Barchart sells access to tools; Theta Desk sells a finished research artifact.
- Barchart has no agent-native distribution; Theta Desk publishes to cited.md where AI agents can discover, cite, and pay for content programmatically.

Honest assessment: Barchart's data breadth and reliability are far beyond a hackathon project. Theta Desk's edge is the autonomous, machine-payable, cited end product.
"""),
    ("competitor-chameleon-optionstrat.md", "competitive-landscape", "2026-06-12 - Competitors: Market Chameleon and OptionStrat", """\
Source: https://marketchameleon.com and https://optionstrat.com (vendor sites, accessed 2026-06-12)

# Competitors: Market Chameleon and OptionStrat

**Market Chameleon** is an options analytics platform with screeners, IV rank data, earnings calendars, and flow analysis, sold as subscriptions that can exceed $100/month for full options features. Strong on raw analytics depth; like other incumbents, it is a human-operated terminal with subscription pricing.

**OptionStrat** is a popular options strategy visualizer and flow tracker with a freemium model (roughly $10–30/month for paid tiers). It excels at visualizing a trade the user has already designed, plus options-flow discovery. It does not autonomously originate and publish daily wheel-strategy research.

Pattern across the category: every incumbent (Option Samurai, Barchart, Market Chameleon, OptionStrat) is (1) subscription-priced, (2) human-operated, and (3) closed to programmatic agent buyers. Theta Desk inverts all three: autonomous origination, per-fetch micropayments, and agent-citable distribution on cited.md.
"""),
    ("wheel-strategy.md", "industry-context", "2026-06-12 - The Wheel Strategy, Explained", """\
Source: general options literature; summarized by the Theta Desk team, 2026-06-12

# The Wheel Strategy, Explained

The wheel is an income strategy built on selling option premium:

1. **Sell a cash-secured put (CSP)** on a stock you are willing to own, at a strike below the current price. You collect a premium. Collateral = strike × 100 in cash.
2. **If the put expires worthless** (stock stays above strike), you keep the premium and repeat.
3. **If assigned**, you buy 100 shares at the strike. You now own the stock at an effective discount (strike minus premium).
4. **Sell covered calls (CC)** against the shares, collecting more premium, until the shares are called away — then return to step 1.

Why practitioners like it: defined process, income in flat or mildly trending markets, and assignment converts to stock ownership rather than a pure loss.

The real risks: a sharp drawdown in the underlying (the put seller absorbs downside below strike), earnings-gap risk, and opportunity cost in strong rallies. Premium yield is compensation for these risks, not free money.

The daily homework problem: finding strikes with rich-but-liquid premium, checking IV levels versus history, and avoiding earnings dates across hundreds of tickers takes a human 1–2 hours per day. This is the labor Theta Desk automates.
"""),
    ("agent-economy.md", "industry-context", "2026-06-12 - The Agent Economy: x402 and Machine-Payable Research", """\
Source: https://cited.md and https://www.x402.org (accessed 2026-06-12)

# The Agent Economy: x402 and Machine-Payable Research

A structural shift in 2025–2026: AI agents became buyers. Agent payment rails let software pay for resources over HTTP without accounts, cards, or checkout pages.

**x402** revives the reserved HTTP status code `402 Payment Required`. A server quotes a price in the 402 response; the client pays (typically a stablecoin micropayment, fractions of a cent in fees) and retries with proof of payment. This makes per-request pricing economic at $0.001–$0.01 — far below the floor of card-based billing.

**cited.md** is an agent-first content layer (powered by Senso): publishers push structured, attributed, verifiable content; AI agents retrieve it, cite it, and can settle payment per fetch via x402.

Why this matters for research products: subscription paywalls exclude machine buyers and casual users alike. Machine-payable publishing means a trading bot can buy exactly one day of research as an input to one decision — a transaction shape that did not exist before these rails.

Theta Desk is built natively for this distribution: its daily sheet is structured for agent parsing, published to cited.md, and priced per fetch.
"""),
    ("case-demo-bot.md", "case-studies", "2026-06-12 - Scenario: A Trading Bot That Buys Its Own Research", """\
Source: Theta Desk demo design document, 2026-06-12. Illustrative scenario, not a production customer.

# Scenario: A Trading Bot That Buys Its Own Research

This scenario illustrates Theta Desk's intended customer: an autonomous trading agent.

**The customer.** "Wheeler" is a paper-trading bot that runs a wheel strategy on a $100,000 simulated account. Its owner gave it one rule: never open a position without a research basis.

**The problem.** Wheeler's owner used to do the screening manually each morning and feed the bot a watchlist — the human was the bottleneck in an otherwise automated loop.

**The solution.** Wheeler subscribes to nothing. Each morning it polls Theta Desk's cited.md endpoint, receives HTTP 402, pays $0.01 via x402 from its operating wallet, and parses the unlocked action sheet. It cross-checks the top cash-secured-put candidate against its own risk limits (max collateral per ticker, sector caps) and queues the order in its paper account, logging the sheet's citation as the research basis.

**The result.** The human left the daily loop entirely. Research cost: about $0.21 per month at one sheet per trading day — versus roughly $50/month for a human-oriented screener subscription, a ~99.6% cost reduction.

**Takeaway.** When research is machine-payable and machine-readable, the entire research-to-execution loop can run agent-to-agent.
"""),
    ("faq.md", "faqs", "2026-06-12 - Theta Desk FAQ", """\
Source: https://github.com/vup903/ThetaDesk-Agent

# Theta Desk FAQ

**Is Theta Desk financial advice?**
No. Theta Desk publishes automated research — screened candidates and risk notes. It does not know your situation, never recommends position sizes, and every sheet carries a risk disclosure.

**What exactly do I get for $0.01?**
One daily action sheet: every screened cash-secured-put / covered-call candidate with premium, annualized yield, IV percentile, liquidity stats, earnings check, composite score, and a cited risk analysis for the top names.

**How do I pay?**
Via x402: request the sheet URL, receive HTTP 402 with payment instructions, pay the micropayment, retry, and the content unlocks. Trading agents can do this programmatically.

**Where does the data come from?**
Public US market data: options chain snapshots, spot prices, one year of price history, and earnings calendars, stored in ClickHouse. Every sheet cites its sources and snapshot time.

**How fresh is the data?**
The pipeline runs on a daily schedule after the US market open; each sheet states its exact snapshot timestamp. Data may be delayed relative to exchange real time.

**What is the wheel strategy?**
An income approach: sell cash-secured puts on stocks you'd own; if assigned, sell covered calls until the shares are called away. See the strategy explainer in our knowledge base.

**Can the screen be wrong?**
Yes. Factors are computed from snapshots and can go stale; quoted premiums move. The sheet is a starting point for judgment, human or algorithmic — not an order list.

**Who built this?**
Theta Desk was built solo at the Context Engineering Challenge (June 2026) on Airbyte, ClickHouse, Senso, OpenUI, and Render.
"""),
]

manifest_lines = []
for filename, folder, title, text in DOCS:
    (HERE / filename).write_text(text, encoding="utf-8")
    manifest_lines.append(f"{filename}\t{FOLDERS[folder]}\t{title}")
(HERE / "manifest.tsv").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
print(f"wrote {len(DOCS)} docs + manifest.tsv")
