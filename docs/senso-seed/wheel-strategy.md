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
