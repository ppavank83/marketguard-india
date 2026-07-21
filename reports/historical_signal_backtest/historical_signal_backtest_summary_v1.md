# Historical Signal Backtest Summary

## Backtest Design

- Monthly rebalancing
- 90 prediction-ready stocks per rebalance
- 30 rebalance dates from 2024-01-02 through 2026-06-01
- 2,700 historical stock observations
- 2025 onward treated as the cleaner test period

## Main Findings

### Opportunity Model

The opportunity model provides useful relative ranking, but the return advantage
was not statistically conclusive.

In the 2025+ test period, the highest-opportunity quintile exceeded the
lowest-opportunity quintile by 1.07 percentage points, but the 95% confidence
interval crossed zero.

The highest-opportunity quintile did show:

- An 8.64 percentage-point higher outperform rate
- A 7.10 percentage-point lower 10% downside-event rate
- Shallower average drawdowns

The model should therefore be used as a ranking signal rather than as a precise
return forecast.

### Downside Model

The downside model successfully separated relative drawdown risk.

Compared with the lowest-risk quintile, the highest-risk quintile experienced:

- 1.45 percentage points deeper average drawdowns
- A 13.58 percentage-point higher 5% downside-event rate
- An 8.33 percentage-point higher 10% downside-event rate

All three differences had confidence intervals excluding zero.

### Combined Classification

The rank-based combined classification produced meaningful risk separation.

Compared with Unfavourable Risk-Reward stocks, Attractive Risk-Reward stocks had:

- No reliable return advantage
- 1.84 percentage points shallower average drawdowns
- A 13.70 percentage-point lower 5% downside-event rate
- A 9.60 percentage-point lower 10% downside-event rate

## Final Decision

The combined MarketGuard classification is validated as a risk-screening
framework, not as a proven alpha-generating strategy.

Relative downside ranking should be used for the primary combined
classification. Fixed probability bands may remain as descriptive alerts.

The dashboard should clearly present:

- Opportunity rank
- Relative downside-risk rank
- Combined risk-screening category
- Data confidence
- Raw model scores with a calibration warning
