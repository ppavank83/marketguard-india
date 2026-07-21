
# Downside Risk Model Final Summary Report

Generated on: 2026-07-21 22:20:57

## Target

The model predicts:

`target_big_downside_10pct_20d`

This target means:

- `1`: The stock fell at least 10% at any point in the next 20 trading days.
- `0`: The stock did not fall 10% in the next 20 trading days.

This is a path-risk target. It checks whether the stock had a large drawdown at any point during the next 20 trading days, not only whether the final 20-day return was negative.

---

## Target Distribution

| Split | Big Downside Rate |
|---|---:|
| Train | 14.76% |
| Validation | 12.54% |
| Test | 11.20% |

The target is imbalanced because most stock-date rows do not experience a 10% drawdown in the next 20 trading days.

Because of this, accuracy alone is misleading. A dummy model can get high accuracy by always predicting no big downside, but it catches zero actual downside events.

---

## Baseline Model Comparison

| Model | Test ROC AUC | Test Average Precision | Test Precision | Test Recall |
|---|---:|---:|---:|---:|
| Dummy | 0.5000 | 0.1120 | 0.00% | 0.00% |
| Logistic Regression Balanced | 0.5521 | 0.1265 | 13.01% | 38.05% |
| Random Forest Downside Balanced | 0.6894 | 0.2107 | 19.76% | 53.61% |

The Random Forest downside model clearly performs better than both the dummy baseline and logistic regression.

The test base downside rate is only 11.20%, while the Random Forest average precision is 21.07%. This means the model is meaningfully better than random selection at identifying high-risk stock-date rows.

---

## Final Selected Model

The selected downside-risk model is:

`random_forest_downside_balanced`

Model type:

`RandomForestClassifier`

The model uses class balancing:

`class_weight="balanced_subsample"`

This helps the model pay more attention to the minority class, which is the actual big downside event.

---

## Final Random Forest Performance

| Split | ROC AUC | Average Precision | Precision | Recall | F1 | Balanced Accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Train | 0.8050 | 0.4490 | 30.11% | 76.37% | 0.4319 | 0.7284 |
| Validation | 0.6554 | 0.2227 | 21.65% | 48.06% | 0.2985 | 0.6156 |
| Test | 0.6894 | 0.2107 | 19.76% | 53.61% | 0.2888 | 0.6308 |

The test ROC AUC is `0.6894`, which is much better than the random baseline of `0.5000`.

This shows that the model has useful signal for downside-risk prediction.

---

## Threshold Analysis

The model outputs a downside-risk probability. A threshold converts that probability into a binary risk alert.

Example logic:

    If predicted downside probability >= threshold:
        alert = high downside risk
    else:
        alert = not high downside risk

Different thresholds create different trade-offs:

- Lower threshold: catches more downside events, but creates more false alerts.
- Higher threshold: creates fewer alerts, but misses more actual downside events.

For a risk-warning system like MarketGuard, recall is important because missing dangerous cases is costly. However, precision also matters because too many false alerts reduce trust.

### Threshold Comparison on Test Data

| Threshold | Purpose | Alert Rate | Precision | Recall | Balanced Accuracy |
|---:|---|---:|---:|---:|---:|
| 0.51 | Selective high-confidence alert | 27.95% | 20.45% | 51.06% | 63.01% |
| 0.47 | Defensive risk monitoring | 37.75% | 18.32% | 61.76% | 63.51% |
| 0.50 | Middle-ground default | 30.38% | 19.76% | 53.61% | 63.08% |

### Threshold Interpretation

| Threshold | Best Use Case |
|---:|---|
| 0.51 | Selective high-confidence alerts |
| 0.47 | Defensive risk monitoring |
| 0.50 | Simple middle-ground default |

For MarketGuard India, the better approach is to use the predicted downside probability as a risk score instead of only using one hard threshold.

---

## Decile Risk Ranking Analysis

The model's probability scores were divided into 10 deciles.

| Decile | Meaning |
|---:|---|
| Decile 10 | Stocks with the highest predicted downside risk |
| Decile 1 | Stocks with the lowest predicted downside risk |

A useful risk model should show higher actual downside rates in Decile 10 than Decile 1.

---

## Validation: Top Risk Decile vs Bottom Risk Decile

| Metric | Decile 10 | Decile 1 |
|---|---:|---:|
| Avg predicted downside probability | 60.57% | 26.04% |
| Actual 10% downside rate | 27.78% | 8.13% |
| Actual 5% downside rate | 60.70% | 34.44% |
| Avg future minimum return | -7.44% | -4.08% |
| Avg future 20-day return | -1.28% | +0.70% |
| Avg excess return vs Nifty 50 | -0.73% | +0.77% |

Validation big downside lift:

`3.42x`

This means the highest-risk validation decile had around 3.4 times the actual 10% downside rate of the lowest-risk decile.

---

## Test: Top Risk Decile vs Bottom Risk Decile

| Metric | Decile 10 | Decile 1 |
|---|---:|---:|
| Avg predicted downside probability | 64.37% | 12.09% |
| Actual 10% downside rate | 24.30% | 3.55% |
| Actual 5% downside rate | 54.54% | 20.41% |
| Avg future minimum return | -6.04% | -3.08% |
| Avg future 20-day return | +1.87% | +0.52% |
| Avg excess return vs Nifty 50 | +1.59% | +0.27% |

Test big downside lift:

`6.85x`

This means the highest-risk test decile had around 6.9 times the actual 10% downside rate of the lowest-risk decile.

This is strong evidence that the model ranks downside risk correctly.

---

## Important Interpretation

In the test split, the high-risk decile still had a positive average 20-day return.

This is not a contradiction.

The model is not predicting:

Will the stock end negative after 20 days?

The model is predicting:

Will the stock fall at least 10% at any point during the next 20 trading days?

A stock can fall sharply during the 20-day window and still recover by the end of the period.

This is why the downside model is useful for path-risk monitoring.

---

## Recommended Risk Bands

Instead of only using a binary alert, MarketGuard should use risk bands.

| Risk Band | Probability Range |
|---|---|
| Low Risk | probability < 0.40 |
| Watch Risk | 0.40 to 0.47 |
| High Risk | 0.47 to 0.51 |
| Very High Risk | probability >= 0.51 |

These risk bands preserve more information than a simple alert/no-alert output.

---

## Final Conclusion

The downside Random Forest model is useful for MarketGuard India.

The model successfully ranks stocks by future downside risk.

Higher predicted downside probability is associated with:

- Higher actual 10% downside rate.
- Higher actual 5% downside rate.
- Deeper future drawdowns.

The downside model is stronger and more directly useful than the outperform model because MarketGuard's main purpose is risk monitoring, not simple buy/sell prediction.

This model should be used as the first baseline downside-risk model for the dashboard.
