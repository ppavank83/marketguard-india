# MarketGuard India

MarketGuard India is a work-in-progress machine learning project for ranking **risk and opportunity in Nifty 100 stocks**.

The system uses historical stock, market-index and sector-index data to estimate:

- The probability of a stock experiencing significant downside
- The probability of outperforming the Nifty 50
- The expected risk/reward category over the next 20 trading days

> **Status:** Research prototype. Not ready for live trading.

## Project Objective

The project is designed to answer two main questions for every eligible stock:

1. **Downside risk:** How likely is the stock to fall significantly during the next 20 trading days?
2. **Opportunity:** How likely is the stock to outperform the Nifty 50 during the same period?

The two model outputs are combined to classify stocks into groups such as:

- Attractive Risk-Reward
- High Opportunity / High Risk
- Balanced Opportunity
- Caution
- Low Opportunity / Lower Risk
- Unfavourable Risk-Reward

## Data

The current project uses daily historical data for:

- Nifty 100 stocks
- Nifty 50
- Nifty 100
- India VIX
- Nifty Bank
- Sector and industry indices

The data is downloaded primarily through `yfinance`.

## Work Completed

### 1. Stock and index universe

- Prepared the Nifty 100 stock universe
- Discovered and validated Yahoo Finance index tickers
- Added broad-market, volatility and sector-level indices
- Created reusable data-download workflows

### 2. Data-quality checks

- Checked missing OHLCV values
- Checked duplicate dates
- Detected zero and negative prices or volume
- Reviewed large daily price movements
- Compared raw and adjusted returns
- Identified possible stock splits and corporate-action effects
- Generated stock and index quality reports

### 3. Feature engineering

Created stock-level features including:

- 1, 5, 20, 60 and 120-day returns
- Log returns
- Rolling volatility
- Annualized volatility
- 20, 50, 100 and 200-day moving averages
- Price-to-moving-average ratios
- 60 and 252-day drawdowns
- RSI
- Trend and moving-average alignment flags
- Market and sector-index context

All rolling features are calculated separately for each stock using only information available at that date.

### 4. Target construction

Created leakage-safe 20-day targets including:

- Future 20-day return
- Future maximum upside
- Future worst-path return
- Nifty 50 excess return
- 5% and 10% downside events
- Nifty 50 outperformance target
- Four-class future risk/reward scenario target

Future and target columns are never used as model input features.

### 5. Baseline models

Developed baseline classification models for:

- Predicting a 10% downside event
- Predicting Nifty 50 outperformance
- Ranking stocks by opportunity
- Ranking stocks by relative downside risk

### 6. Model evaluation

The models are evaluated using time-based out-of-sample data, with particular attention to:

- ROC-AUC and classification metrics
- Risk and opportunity quintiles
- Outperformance rates
- Worst-path returns
- 5% and 10% downside rates
- Confidence intervals
- Rank-based combined classifications

### 7. Prediction snapshot pipeline

An initial reusable pipeline has been added for:

- Loading trained model metadata
- Preparing prediction data
- Creating stock-level prediction snapshots
- Assigning opportunity and relative-risk groups
- Producing combined risk/reward classifications

## Early Results

Early out-of-sample results show that the models can separate stocks by future downside behaviour.

For the combined rank-based classification:

| Metric | Attractive Risk-Reward | Unfavourable Risk-Reward |
|---|---:|---:|
| Average worst-path return | -3.04% | -4.88% |
| 5% downside rate | 25.02% | 38.72% |
| 10% downside rate | 6.45% | 16.05% |

The Attractive group experienced:

- 1.84 percentage points less average worst-path downside
- 13.70 percentage points fewer 5% downside events
- 9.60 percentage points fewer 10% downside events

However, the difference in final 20-day return was not statistically reliable. Current results support the system mainly as a **risk-ranking tool**, not yet as a proven return-generating strategy.

## Repository Structure

```text
marketguard-india/
├── data/
│   └── raw/universe/       # Stock-universe files
├── notebooks/              # Research and model-development notebooks
├── reports/                # Data-quality and model-evaluation reports
├── scripts/                # Executable pipeline scripts
├── src/marketguard/        # Reusable project modules
├── tests/                  # Automated tests
├── config.yaml             # Project configuration
├── environment.yml         # Conda environment
├── requirements.txt        # Python dependencies
└── project_plan.md         # Detailed project plan
```

## Installation

Clone the repository:

```bash
git clone https://github.com/ppavank83/marketguard-india.git
cd marketguard-india
```

Create the Conda environment:

```bash
conda env create -f environment.yml
conda activate marketguard
```

Alternatively, install the dependencies with:

```bash
pip install -r requirements.txt
```

## Current Work in Progress

- Validating production prediction snapshots
- Improving probability calibration
- Reviewing feature importance and stability
- Testing model behaviour across different market regimes
- Improving confidence intervals for overlapping 20-day targets
- Adding stricter pipeline validation and automated tests
- Separating research code from production code

## Future Plans

- Add transaction costs and turnover to the backtest
- Build portfolio-level simulations
- Add walk-forward model retraining
- Test more advanced ML models
- Add model and data-drift monitoring
- Schedule automatic data refreshes
- Build an API for generating prediction snapshots
- Create a dashboard for stock risk and opportunity rankings
- Add explainability for individual predictions
- Containerize the final pipeline with Docker
- Deploy a demonstration version to the cloud

## Limitations

- The project currently uses historical end-of-day data.
- Yahoo Finance data may contain missing values or corporate-action inconsistencies.
- Overlapping 20-day targets can create statistical dependence.
- Backtest results do not include all trading costs and execution constraints.
- Rank-based risk is relative to other stocks in the same period.
- Historical performance does not guarantee future performance.

## Disclaimer

This project is for educational, research and portfolio-demonstration purposes only.

It does not provide financial advice, investment recommendations or guaranteed trading signals. Any investment decision should include independent research and professional financial guidance.

## Author

**Pavan Kumar Pilli**

AI and Data Science graduate focused on machine learning, data science and production-oriented analytics projects.

## License

This project is available under the [MIT License](LICENSE).
