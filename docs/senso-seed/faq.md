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
