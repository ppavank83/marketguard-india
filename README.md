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

**Work in progress**

Completed so far:

- Historical market-data collection
- Feature engineering
- Random Forest model training
- Historical backtesting
- Rank-based classification design
- Leakage checks
- Production snapshot pipeline
- Command-line interface
- Unit tests
- Reproducible Python environment

Current work:

- GitHub Actions CI
- Deep learning model experiments
- Production-only feature generation
- Daily pipeline automation
- API and dashboard development

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

## Current Models

The current production baseline uses two Random Forest classification pipelines.

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

Large datasets and trained model files may be excluded from Git.

The current prediction pipeline uses only the 79 ordered model features during inference. Future target columns are not passed to the models.

A dedicated production-only feature pipeline will later remove the dependency on the research target dataset.

---

## Work in Progress

### GitHub Actions CI

GitHub Actions will be added to automatically:

- Install Python 3.12
- Install project dependencies
- Compile production modules
- Run the test suite
- Show pass or fail checks on pull requests

### Deep Learning Experiments

Deep learning models will be tested against the existing Random Forest baseline.

Planned experiments include:

- Multilayer perceptron
- Residual MLP
- Tabular Transformer
- LSTM
- GRU
- Temporal convolutional network
- Sequence Transformer
- Random Forest and neural-network ensembles

Deep learning models will use strict chronological train, validation, and test periods.

A deep learning model will only replace the current production model when it shows a meaningful and stable improvement on untouched historical data.

### Production Feature Pipeline

A dedicated production feature pipeline will:

- Download or update market data
- Build features using only current and past information
- Produce the expected model columns
- Validate data freshness
- Validate feature completeness
- Avoid future target columns
- Generate the latest feature snapshot

### Daily End-to-End Pipeline

The complete daily workflow will eventually be:

```text
Market-data update
        ↓
Production feature generation
        ↓
Model scoring
        ↓
Relative ranking
        ↓
Opportunity-risk classification
        ↓
Historical snapshot storage
        ↓
API and dashboard update
```

---

## Future Plan

### Near-Term Development

1. Add GitHub Actions CI
2. Preserve the current Random Forest benchmark
3. Build deep learning training datasets
4. Train MLP models
5. Test sequence models
6. Compare Random Forest and deep learning
7. Test model ensembles
8. Select the final production model
9. Build production-only feature generation
10. Build a one-command daily pipeline
11. Expand unit and integration tests

### Application Development

Planned application work includes:

- Historical snapshot storage
- FastAPI backend
- Streamlit dashboard
- Market overview page
- Opportunity screener
- Downside-risk screener
- Stock detail pages
- Rank history
- Classification history
- Data-confidence indicators
- Model methodology page

### Explainability

Planned model explanations include:

- Important features behind each prediction
- Volatility context
- Momentum context
- Moving-average context
- Sector-relative strength
- Market-relative strength
- SHAP or permutation-based explanations

### Alerts and Watchlists

Planned alert conditions include:

- Stock enters Attractive Risk-Reward
- Stock enters High Opportunity / High Risk
- Stock moves into Q1 Highest Risk
- Downside probability crosses a warning level
- Opportunity rank changes significantly
- Classification changes
- Data confidence becomes limited

### Portfolio-Risk Module

Planned portfolio features include:

- Portfolio-weighted downside risk
- Sector concentration
- High-risk position exposure
- Correlated risk groups
- Position-size guidance
- Portfolio classification summary

### Deployment

Planned deployment work includes:

- Docker containerization
- FastAPI deployment
- Streamlit deployment
- Azure Container Apps or App Service
- Azure SQL or PostgreSQL
- Azure Blob Storage
- Scheduled end-of-day jobs
- Application logging
- Failure notifications
- Health monitoring

### Model Monitoring

Planned monitoring includes:

- Missing-stock detection
- Stale-price detection
- Missing-feature rates
- Feature drift
- Probability drift
- Classification drift
- Rank stability
- Realized 20-day outcomes
- Downside-event tracking
- Model-version tracking

### Retraining

Future retraining will use a controlled process:

1. Create a new training dataset
2. Preserve chronological splits
3. Train candidate models
4. Compare against the production model
5. Run historical snapshot backtests
6. Test calibration
7. Check risk separation
8. Promote only approved models
9. Preserve old model versions

---

## Planned API

Possible future API endpoints include:

```text
GET /health
GET /snapshot/latest
GET /snapshot/{date}
GET /stocks/{symbol}
GET /stocks/{symbol}/history
GET /rankings/opportunity
GET /rankings/downside-risk
GET /classifications/{class_name}
```

---

## Planned Dashboard

The dashboard is expected to include:

- Latest snapshot date
- Prediction-ready stock count
- Data-confidence summary
- Opportunity-tier distribution
- Downside-risk distribution
- Combined classification distribution
- NIFTY 100 stock screener
- Stock-level probabilities
- Opportunity and risk ranks
- Historical classification changes
- Price and feature context
- Methodology and limitations

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
