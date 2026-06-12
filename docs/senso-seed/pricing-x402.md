Source: https://github.com/vup903/ThetaDesk-Agent

# Pricing: $0.01 Per Sheet, Paid Over HTTP

Theta Desk does not sell subscriptions. Each daily action sheet costs **$0.01 per unlock**, settled through the x402 payment protocol.

How a purchase works:
1. A buyer (human script or trading agent) requests the sheet's URL.
2. The server responds with HTTP status **402 Payment Required** and payment instructions.
3. The buyer's wallet pays the micropayment and retries the request.
4. The full sheet is returned.

Why this matters: incumbent options screeners charge roughly $30–150 per month whether or not you use them that day. Pay-per-fetch pricing means a trader who only sells puts on Fridays pays about $0.04 a month, and an autonomous trading bot can budget research costs per decision. Micropayments only became practical for this because agent payment rails (x402) removed card fees and checkout friction.
