Source: https://github.com/vup903/ThetaDesk-Agent/blob/main/ARCHITECTURE.md

# How Theta Desk Works

The system is a four-stage autonomous pipeline:

1. **Ingest** — Options chains, spot prices, and earnings dates for a configurable US equity universe are pulled from market data sources. Price history flows in through Airbyte pipelines. Everything lands in ClickHouse time-series tables (`option_chain`, `prices`).
2. **Screen** — ClickHouse SQL computes the factors: annualized premium yield, implied-volatility percentile versus one year of history, open-interest liquidity floors, and an earnings-date-avoidance flag. Candidates are cross-sectionally ranked into a composite score.
3. **Analyze** — For the top-ranked candidates, the Claude-powered analyst writes a short risk narrative: why the premium is rich, what the IV level implies, what events sit before expiry. Each narrative carries citations to its sources.
4. **Publish** — The action sheet (candidates + analyses) is ingested into Senso, generated as a brand-aligned brief, and published to cited.md behind an x402 paywall priced at $0.01 per unlock.

A daily scheduler on Render triggers the run. A replay mode can re-run any past day's real data for demonstrations.
