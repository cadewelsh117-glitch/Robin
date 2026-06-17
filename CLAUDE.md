# Robin — SPYU Autonomous Trading Agent

This repo is the home for an autonomous SPYU day-trading strategy running via Claude Code on the web.

## What this agent does

At each loop trigger, the agent:
1. Checks whether the current UTC time falls inside the 9:30–9:45am ET window (13:30–13:45 UTC during EDT, 14:30–14:45 UTC during EST).
2. If outside the window, exits immediately with no action.
3. If inside the window, fetches the first 1–5 minute SPYU bars from Robinhood.
4. Evaluates the opening range breakout conditions per `SPYU_STRATEGY.md`.
5. If conditions are met and no trade has been placed today, sizes the position and places entry + stop orders autonomously.
6. Appends a row to `trade_log.md` regardless of whether a trade was placed.

## Files

- `SPYU_STRATEGY.md` — full strategy rules and sizing math
- `trade_log.md` — append-only log of every decision
- `CLAUDE.md` — this file

## Account

- Robinhood account ••••4061 (Agentic, cash, agentic_allowed=true)
- Equity: ~$120 → 1% risk = ~$1.20 per trade

## Loop schedule

The agent runs on a 5-minute polling loop. It only acts within the 9:30–9:45am ET window.
