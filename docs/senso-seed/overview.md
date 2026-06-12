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
