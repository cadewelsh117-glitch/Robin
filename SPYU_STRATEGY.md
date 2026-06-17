# SPYU Day-Trading Strategy

**Symbol:** SPYU (MAX S&P 500 4x Leveraged ETN)
**Account:** ••••4061 (Agentic, cash)

## Rules

1. Evaluate SPYU once per trading day at the US market open (9:30am ET).
2. Observe the first 1–5 minute opening range. Do NOT enter on the first tick.
3. Enter long only if price breaks AND holds above the opening range high with strong relative volume.
4. Risk no more than 1% of account equity per trade ($1.20 at current $120 equity).
5. Place a hard stop-loss (stop_market) immediately after entry at the opening range low.
6. Take partial profit at +0.50% of entry price; take full profit at +0.75% of entry price.
7. If stop is hit, do NOT re-enter the same day.
8. If there is major macro news or a large overnight gap (>1% in SPY), skip unless conditions are exceptionally strong.
9. Log every decision: date, entry, stop, target, result, reason.
10. Never average down. Never remove the stop. Never force a trade.
11. May hold SPYU overnight — only sell if news/macro risk warrants it.

## Position Sizing

```
risk_dollars  = account_equity * 0.01
stop_distance = entry_price - opening_range_low
shares        = floor(risk_dollars / stop_distance)   # whole shares only for stop orders
max_shares    = floor(buying_power / entry_price)
final_shares  = min(shares, max_shares)
```

If `final_shares < 1`, skip the trade (position too small to be meaningful).

## Volume Confirmation

- Pull 1-minute bars from 9:30–9:35am ET.
- Average volume of those bars must be at or above the 20-day average 1-minute opening range volume to qualify as "strong."

## Profit Targets

- T1 (partial, 50% of position): `entry * 1.005`
- T2 (full exit): `entry * 1.0075`

## Overnight Hold Policy

- Default: hold if no adverse macro/news signal.
- Sell next day if: major news overnight, SPY gap >1.5%, or clear technical breakdown.
