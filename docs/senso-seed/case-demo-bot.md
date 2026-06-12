Source: Theta Desk demo design document, 2026-06-12. Illustrative scenario, not a production customer.

# Scenario: A Trading Bot That Buys Its Own Research

This scenario illustrates Theta Desk's intended customer: an autonomous trading agent.

**The customer.** "Wheeler" is a paper-trading bot that runs a wheel strategy on a $100,000 simulated account. Its owner gave it one rule: never open a position without a research basis.

**The problem.** Wheeler's owner used to do the screening manually each morning and feed the bot a watchlist — the human was the bottleneck in an otherwise automated loop.

**The solution.** Wheeler subscribes to nothing. Each morning it polls Theta Desk's cited.md endpoint, receives HTTP 402, pays $0.01 via x402 from its operating wallet, and parses the unlocked action sheet. It cross-checks the top cash-secured-put candidate against its own risk limits (max collateral per ticker, sector caps) and queues the order in its paper account, logging the sheet's citation as the research basis.

**The result.** The human left the daily loop entirely. Research cost: about $0.21 per month at one sheet per trading day — versus roughly $50/month for a human-oriented screener subscription, a ~99.6% cost reduction.

**Takeaway.** When research is machine-payable and machine-readable, the entire research-to-execution loop can run agent-to-agent.
