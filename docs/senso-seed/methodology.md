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
