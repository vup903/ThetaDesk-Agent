Source: https://cited.md and https://www.x402.org (accessed 2026-06-12)

# The Agent Economy: x402 and Machine-Payable Research

A structural shift in 2025–2026: AI agents became buyers. Agent payment rails let software pay for resources over HTTP without accounts, cards, or checkout pages.

**x402** revives the reserved HTTP status code `402 Payment Required`. A server quotes a price in the 402 response; the client pays (typically a stablecoin micropayment, fractions of a cent in fees) and retries with proof of payment. This makes per-request pricing economic at $0.001–$0.01 — far below the floor of card-based billing.

**cited.md** is an agent-first content layer (powered by Senso): publishers push structured, attributed, verifiable content; AI agents retrieve it, cite it, and can settle payment per fetch via x402.

Why this matters for research products: subscription paywalls exclude machine buyers and casual users alike. Machine-payable publishing means a trading bot can buy exactly one day of research as an input to one decision — a transaction shape that did not exist before these rails.

Theta Desk is built natively for this distribution: its daily sheet is structured for agent parsing, published to cited.md, and priced per fetch.
