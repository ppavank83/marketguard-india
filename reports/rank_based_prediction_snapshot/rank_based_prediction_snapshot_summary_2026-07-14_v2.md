# Rank-Based Prediction Snapshot — Version 2

**Snapshot date:** 2026-07-14

**Generated at:** 2026-07-23T23:11:47.649058+00:00

## Purpose

This report documents version 2 of the MarketGuard latest prediction snapshot.

Version 1 used fixed downside-probability bands to control the combined opportunity-risk classification. Version 2 preserves those bands as descriptive alerts but uses cross-sectional downside-risk rank for the primary combined class.

## Version Lineage

| Stage | Notebook | Main role |
|---|---|---|
| v1 | `07_latest_prediction_snapshot.ipynb` | Fixed-band latest snapshot |
| Validation | `08_historical_signal_backtest.ipynb` | Historical fixed-versus-rank evaluation |
| v2 | `09_rank_based_prediction_snapshot.ipynb` | Rank-based latest snapshot |

## Latest Universe

- Total stocks: **100**
- Prediction-ready stocks: **90**
- Limited-confidence stocks: **10**
- Model features: **79**

## V2 Combined-Class Counts

| Combined class | Stock count |
|---|---:|
| Unfavourable Risk-Reward | 31 |
| Balanced Opportunity | 21 |
| Low Opportunity / Lower Risk | 14 |
| Attractive Risk-Reward | 10 |
| Limited Confidence - Review | 10 |
| High Opportunity / High Risk | 8 |
| Caution | 6 |

## V1 Versus V2

- Unchanged ready-stock classifications: **85**
- Changed ready-stock classifications: **5**
- Percentage changed: **5.56%**

All five changes occurred because the stocks were inside the riskier half of the current universe even though their fixed downside score remained in the `Watch Risk` band.

### Changed Stocks

| Symbol | Downside score | Risk rank | Risk quintile | V1 class | V2 class |
|---|---:|---:|---|---|---|
| VBL | 0.465680 | 41 | Q3 — Medium Risk | Balanced Opportunity | Caution |
| GODREJCP | 0.462327 | 42 | Q3 — Medium Risk | Low Opportunity / Lower Risk | Unfavourable Risk-Reward |
| BAJFINANCE | 0.461576 | 43 | Q3 — Medium Risk | Low Opportunity / Lower Risk | Unfavourable Risk-Reward |
| KOTAKBANK | 0.460402 | 44 | Q3 — Medium Risk | Low Opportunity / Lower Risk | Unfavourable Risk-Reward |
| BAJAJFINSV | 0.456490 | 45 | Q3 — Medium Risk | Low Opportunity / Lower Risk | Unfavourable Risk-Reward |

## Historical Evidence

Notebook 08 evaluated the rank-based classification over 18 monthly observations from 2025 onward.

Compared with the Unfavourable Risk-Reward group, the Attractive Risk-Reward group had:

- **0.02 percentage points lower final return**, with a confidence interval crossing zero
- **1.84 percentage points shallower worst-path returns**
- **13.70 percentage points fewer 5% downside events**
- **9.60 percentage points fewer 10% downside events**

The evidence supports the classification primarily as a downside-risk screen. It does not establish a reliable final-return or alpha advantage.

## Interpretation

- `downside_risk_band` is an absolute score-based descriptive alert.
- `downside_risk_quintile` gives detailed relative risk from Q1 to Q5.
- `relative_downside_risk` provides the broad higher/lower split used by the combined class.
- `opportunity_risk_class` is a screening label, not an investment recommendation.

## Limitations

- Raw model probabilities are not fully calibrated real-world probabilities.
- The clean historical test contains only 18 months.
- Transaction costs, slippage, turnover, liquidity, position sizing, and portfolio constraints are not included.
- Limited-confidence stocks remain outside the normal ranked universe.
