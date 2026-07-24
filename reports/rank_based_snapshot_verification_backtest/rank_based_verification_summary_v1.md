# Rank-Based Snapshot Verification Backtest

## Verification Scope

- Historical period: 2024-01-02 to 2026-06-01
- Monthly rebalance dates: 30
- Stocks per rebalance date: 90
- Historical observations: 2700
- Clean evaluation period: 2025-01-01 to 2026-06-01
- Clean monthly observations: 18

## Reproduction Result

Notebook 10 independently reproduced the Notebook 08 point estimates and
paired-bootstrap confidence intervals.

- Combined-class reference match: **True**
- Risk-quintile reference match: **True**

## Leakage Audit

- Model features: **79**
- Outcome-feature overlap: **0**
- Suspicious future or target feature names: **0**
- Historical feature order matches fitted models: **True**

The verification scoring process passed the direct target-leakage audit.

## Attractive Versus Unfavourable

- Future-return difference: **-0.02 pp**
- Worst-path difference: **1.84 pp**
- 5% downside-event difference: **-13.70 pp**
- 10% downside-event difference: **-9.60 pp**

The worst-path and downside-event confidence intervals exclude zero. The
future-return and excess-return confidence intervals include zero.

## Highest-Risk Versus Lowest-Risk Quintiles

- Future-return difference: **1.33 pp**
- Worst-path difference: **-1.45 pp**
- 5% downside-event difference: **13.58 pp**
- 10% downside-event difference: **8.33 pp**

The downside model reliably separates future drawdown exposure but does not
reliably separate final returns.

## Method Stability

The V1 fixed probability bands produced highly variable broad risk-group sizes:

- Higher Fixed-Band Risk: **1 to 87 stocks**
- Lower Fixed-Band Risk: **3 to 89 stocks**

The V2 rank-based method maintained:

- Higher Relative Risk: **45 stocks**
- Lower Relative Risk: **45 stocks**

V1 and V2 classifications differed for **738 of
2700 stock-month observations
(27.33%)**.

## Final Conclusion

The exact Notebook 09 implementation is historically verified as a
**relative downside-risk ranking and stock-screening framework**.

It is not validated as a reliable alpha model, market-beating strategy, or
direct buy/sell system.

The V2 rank-based method should remain the primary combined classification.
Fixed raw-probability bands should remain descriptive alert levels only.
