# MarketGuard India

MarketGuard India is an end-of-day machine learning risk-intelligence system for NIFTY 100 stocks.

The project evaluates stocks using:

- Probability of outperforming the NIFTY 50
- Probability of experiencing significant downside
- Relative opportunity ranking
- Relative downside-risk ranking
- Combined opportunity-risk classification
- Data readiness and confidence checks

The goal is to support stock screening and risk analysis. It is not an automated trading bot or a guaranteed buy/sell recommendation system.

---

## Project Status

**Version 1 complete**

Version 1 includes:

- Historical market-data preparation
- Feature engineering and 79 ordered model features
- Two production Random Forest classifiers
- Purged chronological validation
- Deep-learning benchmark experiments
- Bootstrap and moving-block-bootstrap comparisons
- Rank-based opportunity and downside-risk classification
- Reusable production snapshot code
- Command-line snapshot generation
- Unit tests and GitHub Actions CI
- Reproducible Python environments

Automated data updates, a production-only feature pipeline, API, dashboard, deployment, and monitoring are possible later extensions rather than Version 1 requirements.

---

## Current Universe

The current system covers the NIFTY 100 universe.

Latest production snapshot:

- Total stocks: **100**
- Prediction-ready stocks: **90**
- Limited-confidence stocks: **10**
- Model features: **79**
- Latest data date: **2026-07-14**

Stocks with insufficient history may still receive model probabilities, but they are excluded from the prediction-ready rankings.

---

## Final Production Models

Version 1 retains two Random Forest classification pipelines.

### Outperformance Model

Predicts the probability that a stock will outperform the NIFTY 50 over the next 20 trading days.

### Downside Model

Predicts the probability that a stock will experience a 10% downside event during the next 20 trading days.

Both models use the same ordered list of 79 engineered features.

The features include:

- Historical returns
- Momentum
- Volatility
- Moving averages
- Price trends
- Market-relative performance
- Sector-relative performance
- NIFTY 50 indicators
- NIFTY 100 indicators
- India VIX indicators

---

## Classification System

The model probabilities are converted into relative ranks among the 90 prediction-ready stocks.

### Opportunity Tiers

| Opportunity Rank | Tier |
|---|---|
| 1–18 | High Opportunity |
| 19–45 | Moderate Opportunity |
| 46–90 | Low Opportunity |

### Downside-Risk Quintiles

| Downside-Risk Rank | Risk Quintile |
|---|---|
| 1–18 | Q1 Highest Risk |
| 19–36 | Q2 High Risk |
| 37–54 | Q3 Medium Risk |
| 55–72 | Q4 Lower Risk |
| 73–90 | Q5 Lowest Risk |

### Broad Relative Risk

| Downside-Risk Rank | Relative Risk |
|---|---|
| 1–45 | Higher Relative Risk |
| 46–90 | Lower Relative Risk |

### Combined Opportunity-Risk Classes

The opportunity and risk groups are combined into:

- Attractive Risk-Reward
- High Opportunity / High Risk
- Balanced Opportunity
- Caution
- Low Opportunity / Lower Risk
- Unfavourable Risk-Reward
- Limited Confidence - Review

### Fixed Downside-Probability Bands

Raw downside probabilities are also grouped into descriptive alert bands:

| Downside Probability | Band |
|---|---|
| Below 0.40 | Low Risk |
| 0.40 to below 0.47 | Watch Risk |
| 0.47 to below 0.51 | High Risk |
| 0.51 and above | Very High Risk |

The rank-based relative downside-risk classification is used for the main production classification. Fixed probability bands remain descriptive alerts.

---

## Work Completed

### Data Collection and Feature Engineering

Completed work includes:

- Built the NIFTY 100 stock universe
- Collected historical stock-market data
- Added NIFTY 50 market features
- Added NIFTY 100 market features
- Added India VIX features
- Added sector-level features
- Created trend and momentum indicators
- Created volatility indicators
- Created moving-average indicators
- Created market-relative features
- Created sector-relative features
- Created approximately 200 research columns
- Selected 79 production model features
- Added stock-history checks
- Added feature-readiness checks
- Created future return and downside targets for research

### Model Development

Completed model work includes:

- Trained an outperformance classification model
- Trained a 10% downside classification model
- Stored preprocessing and model logic inside sklearn pipelines
- Validated model feature names and order
- Validated positive-class probability extraction
- Saved trained model artifacts with Joblib

### Historical Validation

The models and classifications were evaluated using historical monthly snapshots.

Completed validation includes:

- 30 monthly evaluation dates
- 2,700 stock-date predictions
- 90 prediction-ready stocks per date
- A separate 2025 onward evaluation period
- Fixed-band versus rank-based comparison
- Bootstrap confidence intervals
- Direct future-target leakage checks
- Opportunity and downside group comparison
- V1 versus V2 classification comparison

The strongest historical result was found in downside-risk screening.

Stocks ranked as higher risk experienced significantly more:

- 5% downside events
- 10% downside events
- Negative worst-path movement

The current opportunity model has not yet demonstrated statistically reliable excess-return separation.

For that reason, MarketGuard is currently positioned mainly as a relative downside-risk and screening system.

---

## Deep-Learning Experiments

The following tabular neural-network architectures were trained and evaluated:

- Multilayer perceptron
- Tabular residual network
- FT-Transformer
- TabNet
- Random Forest and neural-network ensembles

The experiments used chronological splits, training-only preprocessing, early stopping, class-imbalance handling, gradient safeguards, paired bootstrap analysis, and 20-trading-day moving-block bootstrap analysis.

Some neural models improved validation metrics, but those gains were not stable across market periods and did not generalize to the later test period. No deep-learning model was promoted.

Final chronological test results:

| Target and retained model | ROC-AUC | Average precision | Log loss | Brier score |
|---|---:|---:|---:|---:|
| Outperformance Random Forest | 0.5141 | 0.5296 | 0.6940 | 0.2504 |
| Downside-risk Random Forest | 0.6845 | 0.2056 | 0.5460 | 0.1840 |

Final decision:

```text
Outperformance model: Random Forest retained
Downside-risk model:  Random Forest retained
```

The opportunity model remains weak out of sample. The downside model is the more useful component and is intended primarily for relative risk screening.

Experiment notebooks and reports are stored under:

```text
notebooks/11_deep_learning_data_audit.ipynb
notebooks/12_tabular_mlp_baseline.ipynb
reports/deep_learning_experiments/
```

Regenerable neural-network checkpoints are excluded from Git.

---

## Production Pipeline

The research notebook logic has been converted into reusable Python code.

Main production module:

```text
src/marketguard/prediction_snapshot.py
```

Command-line entry point:

```text
scripts/generate_prediction_snapshot.py
```

The production pipeline can:

1. Load the feature dataset
2. Load the two fitted models
3. Validate required input files
4. Validate required dataset columns
5. Validate model feature order
6. Select the latest row for every stock
7. Score all 100 stocks
8. Rank the 90 prediction-ready stocks
9. Assign opportunity tiers
10. Assign downside-risk quintiles
11. Assign combined classifications
12. Generate a V1 versus V2 audit
13. Save CSV files
14. Save Parquet files
15. Save JSON metadata
16. Save a Markdown summary

The production pipeline was compared row by row against the original research notebook output and matched successfully.

---

## Testing

The project currently contains 15 unit tests.

The tests cover:

- Fixed downside-risk band boundaries
- Opportunity-tier group sizes
- Downside-risk quintile sizes
- Combined opportunity-risk classes
- Limited-confidence behavior
- Classification metadata
- Duplicate-rank rejection
- Incorrect ready-universe rejection

Current result:

```text
15 passed
```

---

## Repository Structure

```text
marketguard-india/
│
├── data/
│   └── raw/
│       └── universe/
│
├── models/
│   └── Trained model artifacts
│
├── notebooks/
│   └── Research, modeling, backtesting, and validation notebooks
│
├── reports/
│   └── Snapshot, audit, metadata, and backtest outputs
│
├── scripts/
│   └── generate_prediction_snapshot.py
│
├── src/
│   └── marketguard/
│       ├── __init__.py
│       └── prediction_snapshot.py
│
├── tests/
│   └── test_prediction_snapshot.py
│
├── .gitignore
├── config.yaml
├── environment.yml
├── LICENSE
├── project_plan.md
├── README.md
└── requirements.txt
```

---

## Environment Setup

The project uses Python 3.12.

### Option 1: Create the Conda Environment

```powershell
conda env create -f environment.yml
conda activate marketguard
```

### Option 2: Install from Requirements

```powershell
conda create -n marketguard python=3.12
conda activate marketguard
python -m pip install -r requirements.txt
```

---

## Run the Tests

From the project root:

```powershell
conda activate marketguard
$env:PYTHONPATH = "src"
python -m pytest tests -v
```

Expected result:

```text
15 passed
```

---

## Generate the Prediction Snapshot

Activate the project environment:

```powershell
conda activate marketguard
```

Run the production snapshot pipeline:

```powershell
python scripts\generate_prediction_snapshot.py
```

The default output directory is:

```text
reports/rank_based_prediction_snapshot/
```

A custom output directory can also be supplied:

```powershell
python scripts\generate_prediction_snapshot.py --output-dir reports/custom_output
```

---

## Generated Artifacts

The pipeline generates eight artifacts:

```text
rank_based_prediction_snapshot_<date>_v2.csv
rank_based_prediction_snapshot_<date>_v2.parquet
latest_rank_based_prediction_snapshot_v2.csv
latest_rank_based_prediction_snapshot_v2.parquet
v1_v2_classification_audit_<date>_v2.csv
v1_v2_classification_audit_<date>_v2.parquet
rank_based_prediction_snapshot_metadata_<date>_v2.json
rank_based_prediction_snapshot_summary_<date>_v2.md
```

The outputs contain:

- Stock symbols
- Company names
- Closing prices
- Outperformance probabilities
- Opportunity ranks
- Opportunity tiers
- Downside probabilities
- Downside-risk ranks
- Fixed downside-risk bands
- Risk quintiles
- Relative downside-risk groups
- Combined opportunity-risk classes
- Prediction readiness
- Data confidence
- Classification version information

---

## Required Local Inputs

The current production snapshot requires the following local files:

```text
data/interim/targets/stock_features_with_targets_v1.parquet

models/best_random_forest_outperform_nifty50_20d_v1.joblib

models/random_forest_downside_10pct_20d_v1.joblib
```

The two final Random Forest model artifacts are versioned in Git. Large historical datasets and regenerable deep-learning checkpoints remain local.

The current prediction pipeline uses only the 79 ordered model features during inference. Future target columns are not passed to the models.

A dedicated production-only feature pipeline will later remove the dependency on the research target dataset.

---

## Version 1 Scope

Version 1 is complete as a local, reproducible machine-learning research and inference project.

The following are intentionally outside the Version 1 scope:

- Automated daily market-data downloads
- Production-only feature generation
- Scheduled end-to-end execution
- FastAPI service
- Streamlit dashboard
- Cloud deployment
- Database-backed historical snapshots
- Alerts and watchlists
- Portfolio-risk analysis
- Automated retraining and drift monitoring

These are possible later enhancements, not requirements for the completed portfolio project.

---

## Future Enhancements

Potential later work includes:

- A point-in-time stock universe to reduce survivorship bias
- A production-only feature pipeline
- Walk-forward model evaluation
- Daily rank-IC and portfolio-bucket analysis
- Transaction-cost and turnover analysis
- API and dashboard interfaces
- Model explanations and monitoring
- Scheduled cloud execution

---

## Important Limitations

- MarketGuard is an experimental research project.
- Model probabilities are estimates, not guarantees.
- The system does not provide financial advice.
- The system should not be the only basis for an investment decision.
- Historical results do not guarantee future results.
- The current opportunity model has not demonstrated reliable market-beating performance.
- The downside model has shown stronger historical risk separation.
- Limited-history stocks are excluded from the ranked universe.
- Transaction costs are not currently included.
- Taxes are not currently included.
- Slippage is not currently included.
- Liquidity constraints are not currently included.
- Portfolio constraints are not currently included.
- Results depend on the quality and availability of market data.

---

## Final Project Goal

The final goal is to build an end-to-end machine learning risk-intelligence platform:

```text
NIFTY 100 market data
        ↓
Production feature engineering
        ↓
Machine learning and deep learning models
        ↓
Outperformance and downside probabilities
        ↓
Relative opportunity and risk rankings
        ↓
Combined classifications
        ↓
Historical storage
        ↓
API and dashboard
        ↓
Alerts and portfolio-risk tools
        ↓
Automated cloud deployment and monitoring
```

The project is designed to demonstrate:

- Data engineering
- Feature engineering
- Machine learning
- Deep learning
- Time-series validation
- Backtesting
- Production inference
- Automated testing
- API development
- Dashboard development
- Model monitoring
- Cloud deployment

---

## Disclaimer

This repository is for educational and research purposes only.

Nothing in this project should be interpreted as investment advice, financial advice, or a recommendation to buy, sell, or hold any security.
