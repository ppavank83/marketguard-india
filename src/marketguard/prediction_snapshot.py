"""Production pipeline for the MarketGuard rank-based prediction snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import math

import joblib
import numpy as np

import json
from datetime import datetime, timezone


SNAPSHOT_VERSION = "v2"
CLASSIFICATION_METHOD = "rank_based_relative_downside_risk"

EXPECTED_TOTAL_STOCKS = 100
EXPECTED_READY_STOCKS = 90

HIGH_OPPORTUNITY_END = 18
MODERATE_OPPORTUNITY_END = 45

RISK_QUINTILE_1_END = 18
RISK_QUINTILE_2_END = 36
RISK_QUINTILE_3_END = 54
RISK_QUINTILE_4_END = 72

HIGHER_RELATIVE_RISK_END = 45


SNAPSHOT_COLUMNS = [
    "date",
    "symbol",
    "yf_ticker",
    "company_name",
    "close",
    "outperform_probability",
    "outperform_rank_ready_universe",
    "opportunity_tier",
    "downside_probability",
    "downside_risk_rank_ready_universe",
    "downside_risk_band",
    "downside_risk_quintile",
    "relative_downside_risk",
    "opportunity_risk_class",
    "prediction_ready",
    "data_confidence",
    "missing_model_feature_count",
    "classification_version",
    "classification_method",
]

AUDIT_COLUMNS = [
    "date",
    "symbol",
    "yf_ticker",
    "company_name",
    "outperform_probability",
    "outperform_rank_ready_universe",
    "opportunity_tier",
    "downside_probability",
    "downside_risk_rank_ready_universe",
    "downside_risk_band",
    "downside_risk_quintile",
    "fixed_band_broad_risk",
    "relative_downside_risk",
    "risk_method_agreement",
    "opportunity_risk_class_v1_reference",
    "opportunity_risk_class_v2_rank_based",
    "classification_changed",
    "prediction_ready",
    "data_confidence",
]


@dataclass(frozen=True)
class SnapshotPaths:
    """Input and output paths used by the production snapshot pipeline."""

    feature_data: Path
    outperform_model: Path
    downside_model: Path
    output_dir: Path

    @classmethod
    def from_project_root(cls, project_root: str | Path) -> SnapshotPaths:
        root = Path(project_root).resolve()

        return cls(
            feature_data=root / "data/interim/targets/stock_features_with_targets_v1.parquet",
            outperform_model=root / "models/best_random_forest_outperform_nifty50_20d_v1.joblib",
            downside_model=root / "models/random_forest_downside_10pct_20d_v1.joblib",
            output_dir=root / "reports/rank_based_prediction_snapshot",
        )


@dataclass(frozen=True)
class SnapshotResult:
    """In-memory outputs produced by the snapshot-building logic."""

    snapshot: pd.DataFrame
    audit: pd.DataFrame
    metadata: dict[str, Any]


@dataclass(frozen=True)
class SavedSnapshotArtifacts:
    """Paths of artifacts written by the production pipeline."""

    dated_csv: Path
    dated_parquet: Path
    latest_csv: Path
    latest_parquet: Path
    audit_csv: Path
    audit_parquet: Path
    metadata_json: Path
    summary_markdown: Path



def assign_fixed_downside_risk_band(probability: float) -> str:
    """Assign the descriptive fixed downside-probability band."""

    if pd.isna(probability):
        return "Unavailable"

    if probability < 0.40:
        return "Low Risk"

    if probability < 0.47:
        return "Watch Risk"

    if probability < 0.51:
        return "High Risk"

    return "Very High Risk"


def classify_rank_based_snapshot(snapshot: pd.DataFrame) -> pd.DataFrame:
    """
    Add Notebook 09's opportunity, relative-risk, and combined classes.

    The input must already contain model probabilities, ready-universe
    ranks, and the prediction-ready flag.
    """

    required_columns = [
        "prediction_ready",
        "outperform_rank_ready_universe",
        "downside_risk_rank_ready_universe",
        "downside_probability",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in snapshot.columns
    ]

    if missing_columns:
        raise KeyError(
            "Snapshot is missing required classification columns:\n"
            + "\n".join(missing_columns)
        )

    classified = snapshot.copy()
    ready_mask = classified["prediction_ready"].fillna(False).astype(bool)
    ready_count = int(ready_mask.sum())

    if ready_count != EXPECTED_READY_STOCKS:
        raise ValueError(
            f"Expected {EXPECTED_READY_STOCKS} prediction-ready stocks, "
            f"found {ready_count}."
        )

    outperform_rank = pd.to_numeric(
        classified["outperform_rank_ready_universe"],
        errors="coerce",
    )

    downside_rank = pd.to_numeric(
        classified["downside_risk_rank_ready_universe"],
        errors="coerce",
    )


    # ---------------------------------------------------------
    # Validate ready-universe ranks
    # ---------------------------------------------------------

    rank_columns = {
        "outperform_rank_ready_universe": outperform_rank,
        "downside_risk_rank_ready_universe": downside_rank,
    }

    for column, ranks in rank_columns.items():
        ready_ranks = ranks.loc[ready_mask]

        if ready_ranks.isna().any():
            raise ValueError(
                f"{column} contains missing ranks for prediction-ready stocks."
            )

        if ready_ranks.nunique() != ready_count:
            raise ValueError(
                f"{column} does not contain one unique rank per ready stock."
            )

        if ready_ranks.min() != 1 or ready_ranks.max() != ready_count:
            raise ValueError(
                f"{column} must cover ranks 1 through {ready_count}."
            )

        if ranks.loc[~ready_mask].notna().any():
            raise ValueError(
                f"Limited-confidence stocks unexpectedly received {column}."
            )


    # Calculate boundaries from the number of ready stocks.
    high_opportunity_limit = math.ceil(ready_count * 0.20)
    moderate_opportunity_limit = math.ceil(ready_count * 0.50)

    risk_q1_limit = math.ceil(ready_count * 0.20)
    risk_q2_limit = math.ceil(ready_count * 0.40)
    risk_q3_limit = math.ceil(ready_count * 0.60)
    risk_q4_limit = math.ceil(ready_count * 0.80)

    higher_relative_risk_limit = math.ceil(ready_count * 0.50)


    # ---------------------------------------------------------
    # Fixed descriptive downside-risk bands
    # ---------------------------------------------------------

    classified["downside_risk_band"] = (
        classified["downside_probability"]
        .apply(assign_fixed_downside_risk_band)
    )


    # ---------------------------------------------------------
    # Opportunity tiers
    # ---------------------------------------------------------

    classified["opportunity_tier"] = "Limited Confidence"

    classified.loc[ready_mask, "opportunity_tier"] = "Low Opportunity"

    classified.loc[
        ready_mask & outperform_rank.le(moderate_opportunity_limit),
        "opportunity_tier",
    ] = "Moderate Opportunity"

    classified.loc[
        ready_mask & outperform_rank.le(high_opportunity_limit),
        "opportunity_tier",
    ] = "High Opportunity"


    # ---------------------------------------------------------
    # Detailed downside-risk quintiles
    # ---------------------------------------------------------

    classified["downside_risk_quintile"] = "Limited Confidence"

    classified.loc[ready_mask, "downside_risk_quintile"] = "Q5 — Lowest Risk"

    classified.loc[
        ready_mask & downside_rank.le(risk_q4_limit),
        "downside_risk_quintile",
    ] = "Q4 — Lower Risk"

    classified.loc[
        ready_mask & downside_rank.le(risk_q3_limit),
        "downside_risk_quintile",
    ] = "Q3 — Medium Risk"

    classified.loc[
        ready_mask & downside_rank.le(risk_q2_limit),
        "downside_risk_quintile",
    ] = "Q2 — High Risk"

    classified.loc[
        ready_mask & downside_rank.le(risk_q1_limit),
        "downside_risk_quintile",
    ] = "Q1 — Highest Risk"


    # ---------------------------------------------------------
    # Broad 50/50 relative-risk split
    # ---------------------------------------------------------

    classified["relative_downside_risk"] = "Limited Confidence"

    classified.loc[
        ready_mask,
        "relative_downside_risk",
    ] = "Lower Relative Risk"

    classified.loc[
        ready_mask & downside_rank.le(higher_relative_risk_limit),
        "relative_downside_risk",
    ] = "Higher Relative Risk"


    # ---------------------------------------------------------
    # Combined opportunity-risk classification
    # ---------------------------------------------------------

    classified["opportunity_risk_class"] = "Limited Confidence - Review"

    opportunity = classified["opportunity_tier"]
    relative_risk = classified["relative_downside_risk"]

    classified.loc[
        ready_mask
        & opportunity.eq("High Opportunity")
        & relative_risk.eq("Lower Relative Risk"),
        "opportunity_risk_class",
    ] = "Attractive Risk-Reward"

    classified.loc[
        ready_mask
        & opportunity.eq("High Opportunity")
        & relative_risk.eq("Higher Relative Risk"),
        "opportunity_risk_class",
    ] = "High Opportunity / High Risk"

    classified.loc[
        ready_mask
        & opportunity.eq("Moderate Opportunity")
        & relative_risk.eq("Lower Relative Risk"),
        "opportunity_risk_class",
    ] = "Balanced Opportunity"

    classified.loc[
        ready_mask
        & opportunity.eq("Moderate Opportunity")
        & relative_risk.eq("Higher Relative Risk"),
        "opportunity_risk_class",
    ] = "Caution"

    classified.loc[
        ready_mask
        & opportunity.eq("Low Opportunity")
        & relative_risk.eq("Lower Relative Risk"),
        "opportunity_risk_class",
    ] = "Low Opportunity / Lower Risk"

    classified.loc[
        ready_mask
        & opportunity.eq("Low Opportunity")
        & relative_risk.eq("Higher Relative Risk"),
        "opportunity_risk_class",
    ] = "Unfavourable Risk-Reward"


    classified["classification_version"] = SNAPSHOT_VERSION
    classified["classification_method"] = CLASSIFICATION_METHOD

    return classified


def extract_feature_names(fitted_model: Any) -> list[str]:
    """Extract the ordered feature names stored in a fitted sklearn model."""

    if hasattr(fitted_model, "feature_names_in_"):
        return list(fitted_model.feature_names_in_)

    if hasattr(fitted_model, "named_steps"):
        for step in fitted_model.named_steps.values():
            if hasattr(step, "feature_names_in_"):
                return list(step.feature_names_in_)

    raise AttributeError(
        "Could not find feature_names_in_ in the fitted model or pipeline."
    )


def predict_positive_probability(
    fitted_model: Any,
    features: pd.DataFrame,
) -> np.ndarray:
    """Return predicted probabilities for fitted target class 1."""

    classes = np.asarray(fitted_model.classes_)
    positive_class_locations = np.flatnonzero(classes == 1)

    if len(positive_class_locations) != 1:
        raise ValueError(
            f"Expected exactly one positive class labelled 1. Found: {classes.tolist()}"
        )

    positive_class_index = int(positive_class_locations[0])
    probabilities = fitted_model.predict_proba(features)

    if probabilities.shape[0] != len(features):
        raise ValueError(
            "The number of generated probabilities does not match the input rows."
        )

    return probabilities[:, positive_class_index]


def load_snapshot_inputs(
    paths: SnapshotPaths,
) -> tuple[pd.DataFrame, Any, Any, list[str]]:
    """Load and validate the feature dataset and two fitted models."""

    required_paths = {
        "feature dataset": paths.feature_data,
        "outperform model": paths.outperform_model,
        "downside model": paths.downside_model,
    }

    missing_paths = [
        f"{label}: {path}"
        for label, path in required_paths.items()
        if not path.exists()
    ]

    if missing_paths:
        raise FileNotFoundError(
            "Required snapshot inputs were not found:\n"
            + "\n".join(missing_paths)
        )

    feature_data = pd.read_parquet(paths.feature_data)
    outperform_model = joblib.load(paths.outperform_model)
    downside_model = joblib.load(paths.downside_model)

    outperform_features = extract_feature_names(outperform_model)
    downside_features = extract_feature_names(downside_model)

    if outperform_features != downside_features:
        raise ValueError(
            "The outperform and downside models do not use the same ordered features."
        )

    model_features = outperform_features

    required_columns = [
        "date",
        "yf_ticker",
        "model_ready_v1",
        *model_features,
    ]

    missing_columns = [
        column for column in required_columns
        if column not in feature_data.columns
    ]

    if missing_columns:
        raise KeyError(
            "The feature dataset is missing required columns:\n"
            + "\n".join(missing_columns)
        )

    feature_data = feature_data.copy()
    feature_data["date"] = pd.to_datetime(feature_data["date"])

    duplicate_rows = int(
        feature_data.duplicated(["date", "yf_ticker"]).sum()
    )

    if duplicate_rows:
        raise ValueError(
            f"The feature dataset contains {duplicate_rows} duplicate date/ticker rows."
        )

    unique_stocks = int(feature_data["yf_ticker"].nunique())

    if unique_stocks != EXPECTED_TOTAL_STOCKS:
        raise ValueError(
            f"Expected {EXPECTED_TOTAL_STOCKS} unique stocks, found {unique_stocks}."
        )

    if 1 not in np.asarray(outperform_model.classes_):
        raise ValueError("The outperform model does not contain target class 1.")

    if 1 not in np.asarray(downside_model.classes_):
        raise ValueError("The downside model does not contain target class 1.")

    return feature_data, outperform_model, downside_model, model_features



def assign_combined_class(
    opportunity_tier: str,
    broad_risk: str,
) -> str:
    """Assign the combined opportunity-risk class."""

    if opportunity_tier == "Limited Confidence":
        return "Limited Confidence - Review"

    mapping = {
        ("High Opportunity", "Lower Risk"): "Attractive Risk-Reward",
        ("High Opportunity", "Higher Risk"): "High Opportunity / High Risk",
        ("Moderate Opportunity", "Lower Risk"): "Balanced Opportunity",
        ("Moderate Opportunity", "Higher Risk"): "Caution",
        ("Low Opportunity", "Lower Risk"): "Low Opportunity / Lower Risk",
        ("Low Opportunity", "Higher Risk"): "Unfavourable Risk-Reward",
    }

    try:
        return mapping[(opportunity_tier, broad_risk)]
    except KeyError as error:
        raise ValueError(
            "Unsupported opportunity and risk combination: "
            f"{opportunity_tier!r}, {broad_risk!r}"
        ) from error


def build_rank_based_snapshot(
    feature_data: pd.DataFrame,
    outperform_model: Any,
    downside_model: Any,
    model_features: list[str],
) -> SnapshotResult:
    """Build Notebook 09's latest rank-based snapshot and V1/V2 audit."""

    required_identity_columns = [
        "date",
        "symbol",
        "yf_ticker",
        "company_name",
        "close",
        "model_ready_v1",
        "is_limited_history",
    ]

    required_columns = required_identity_columns + model_features

    missing_columns = [
        column for column in required_columns
        if column not in feature_data.columns
    ]

    if missing_columns:
        raise KeyError(
            "The feature dataset is missing snapshot columns:\n"
            + "\n".join(missing_columns)
        )


    # ---------------------------------------------------------
    # Select one latest row per stock
    # ---------------------------------------------------------

    latest_indices = (
        feature_data.groupby("yf_ticker")["date"]
        .idxmax()
    )

    latest = (
        feature_data.loc[latest_indices]
        .sort_values("yf_ticker")
        .reset_index(drop=True)
        .copy()
    )

    if len(latest) != EXPECTED_TOTAL_STOCKS:
        raise ValueError(
            f"Expected {EXPECTED_TOTAL_STOCKS} latest stock rows, found {len(latest)}."
        )

    if latest["yf_ticker"].nunique() != EXPECTED_TOTAL_STOCKS:
        raise ValueError("The latest snapshot does not contain 100 unique stocks.")

    snapshot_dates = latest["date"].dropna().unique()

    if len(snapshot_dates) != 1:
        raise ValueError(
            "Latest stock rows do not share one common snapshot date. "
            f"Found {len(snapshot_dates)} dates."
        )

    snapshot_date = pd.Timestamp(snapshot_dates[0])


    # ---------------------------------------------------------
    # Readiness and data-confidence fields
    # ---------------------------------------------------------

    latest["prediction_ready"] = (
        latest["model_ready_v1"]
        .fillna(False)
        .astype(bool)
    )

    latest["missing_model_feature_count"] = (
        latest[model_features]
        .isna()
        .sum(axis=1)
        .astype(int)
    )

    limited_history = (
        latest["is_limited_history"]
        .fillna(False)
        .astype(bool)
    )

    missing_features = latest["missing_model_feature_count"].gt(0)

    latest["data_confidence"] = "Normal Confidence"

    latest.loc[
        limited_history & ~missing_features,
        "data_confidence",
    ] = "Limited History"

    latest.loc[
        limited_history & missing_features,
        "data_confidence",
    ] = "Limited History + Missing Features"

    latest.loc[
        ~limited_history & missing_features,
        "data_confidence",
    ] = "Missing Features"


    ready_count = int(latest["prediction_ready"].sum())

    if ready_count != EXPECTED_READY_STOCKS:
        raise ValueError(
            f"Expected {EXPECTED_READY_STOCKS} prediction-ready stocks, "
            f"found {ready_count}."
        )


    # ---------------------------------------------------------
    # Score all 100 stocks
    # ---------------------------------------------------------

    scoring_features = latest[model_features]

    latest["outperform_probability"] = predict_positive_probability(
        outperform_model,
        scoring_features,
    )

    latest["downside_probability"] = predict_positive_probability(
        downside_model,
        scoring_features,
    )

    probability_columns = [
        "outperform_probability",
        "downside_probability",
    ]

    if latest[probability_columns].isna().any().any():
        raise ValueError("Model scoring produced missing probabilities.")

    for column in probability_columns:
        if not latest[column].between(0, 1).all():
            raise ValueError(f"{column} contains values outside the range 0 to 1.")


    # ---------------------------------------------------------
    # Rank only the prediction-ready universe
    # ---------------------------------------------------------

    ready_mask = latest["prediction_ready"]

    latest["outperform_rank_ready_universe"] = pd.Series(
        pd.NA,
        index=latest.index,
        dtype="Int64",
    )

    latest["downside_risk_rank_ready_universe"] = pd.Series(
        pd.NA,
        index=latest.index,
        dtype="Int64",
    )

    latest.loc[
        ready_mask,
        "outperform_rank_ready_universe",
    ] = (
        latest.loc[ready_mask, "outperform_probability"]
        .rank(method="first", ascending=False)
        .astype("Int64")
    )

    latest.loc[
        ready_mask,
        "downside_risk_rank_ready_universe",
    ] = (
        latest.loc[ready_mask, "downside_probability"]
        .rank(method="first", ascending=False)
        .astype("Int64")
    )


    # ---------------------------------------------------------
    # Apply exact V2 classifications
    # ---------------------------------------------------------

    classified = classify_rank_based_snapshot(latest)


    # ---------------------------------------------------------
    # Recreate the V1 fixed-band reference classification
    # ---------------------------------------------------------

    classified["fixed_band_broad_risk"] = "Limited Confidence"

    lower_fixed_band = classified["downside_risk_band"].isin(
        ["Low Risk", "Watch Risk"]
    )

    classified.loc[
        ready_mask & lower_fixed_band,
        "fixed_band_broad_risk",
    ] = "Lower Fixed-Band Risk"

    classified.loc[
        ready_mask & ~lower_fixed_band,
        "fixed_band_broad_risk",
    ] = "Higher Fixed-Band Risk"


    classified["v1_broad_risk_for_mapping"] = classified[
        "fixed_band_broad_risk"
    ].map({
        "Lower Fixed-Band Risk": "Lower Risk",
        "Higher Fixed-Band Risk": "Higher Risk",
    })

    classified["v2_broad_risk_for_mapping"] = classified[
        "relative_downside_risk"
    ].map({
        "Lower Relative Risk": "Lower Risk",
        "Higher Relative Risk": "Higher Risk",
    })


    classified["opportunity_risk_class_v1_reference"] = [
        assign_combined_class(opportunity, broad_risk)
        if prediction_ready
        else "Limited Confidence - Review"
        for opportunity, broad_risk, prediction_ready in zip(
            classified["opportunity_tier"],
            classified["v1_broad_risk_for_mapping"],
            classified["prediction_ready"],
        )
    ]

    classified["opportunity_risk_class_v2_rank_based"] = classified[
        "opportunity_risk_class"
    ]


    fixed_risk_comparison = classified["fixed_band_broad_risk"].replace({
        "Lower Fixed-Band Risk": "Lower",
        "Higher Fixed-Band Risk": "Higher",
        "Limited Confidence": "Limited",
    })

    relative_risk_comparison = classified["relative_downside_risk"].replace({
        "Lower Relative Risk": "Lower",
        "Higher Relative Risk": "Higher",
        "Limited Confidence": "Limited",
    })

    classified["risk_method_agreement"] = np.where(
        fixed_risk_comparison.eq(relative_risk_comparison),
        "Agree",
        "Disagree",
    )

    classified["classification_changed"] = (
        classified["opportunity_risk_class_v1_reference"]
        != classified["opportunity_risk_class_v2_rank_based"]
    )


    # ---------------------------------------------------------
    # Build exact output schemas
    # ---------------------------------------------------------

    snapshot = (
        classified[SNAPSHOT_COLUMNS]
        .sort_values(
            [
                "prediction_ready",
                "outperform_rank_ready_universe",
                "yf_ticker",
            ],
            ascending=[False, True, True],
            na_position="last",
        )
        .reset_index(drop=True)
    )

    audit = (
        classified[AUDIT_COLUMNS]
        .sort_values(
            [
                "prediction_ready",
                "outperform_rank_ready_universe",
                "yf_ticker",
            ],
            ascending=[False, True, True],
            na_position="last",
        )
        .reset_index(drop=True)
    )


    # ---------------------------------------------------------
    # Final structural validation
    # ---------------------------------------------------------

    if snapshot.shape != (EXPECTED_TOTAL_STOCKS, len(SNAPSHOT_COLUMNS)):
        raise ValueError(
            f"Unexpected snapshot shape: {snapshot.shape}."
        )

    if audit.shape != (EXPECTED_TOTAL_STOCKS, len(AUDIT_COLUMNS)):
        raise ValueError(
            f"Unexpected audit shape: {audit.shape}."
        )

    if list(snapshot.columns) != SNAPSHOT_COLUMNS:
        raise ValueError("Snapshot column order does not match the production contract.")

    if list(audit.columns) != AUDIT_COLUMNS:
        raise ValueError("Audit column order does not match the production contract.")


    snapshot_counts = {
        "total_stocks": len(snapshot),
        "prediction_ready": int(snapshot["prediction_ready"].sum()),
        "limited_confidence": int((~snapshot["prediction_ready"]).sum()),
        "data_confidence": snapshot["data_confidence"].value_counts().to_dict(),
        "opportunity_tier": snapshot["opportunity_tier"].value_counts().to_dict(),
        "downside_risk_quintile": (
            snapshot["downside_risk_quintile"].value_counts().to_dict()
        ),
        "relative_downside_risk": (
            snapshot["relative_downside_risk"].value_counts().to_dict()
        ),
        "opportunity_risk_class": (
            snapshot["opportunity_risk_class"].value_counts().to_dict()
        ),
    }

    comparison_counts = {
        "risk_method_agreement": audit["risk_method_agreement"].value_counts().to_dict(),
        "classification_changed": int(audit["classification_changed"].sum()),
        "classification_unchanged": int((~audit["classification_changed"]).sum()),
        "classification_changed_percent": float(
            audit["classification_changed"].mean() * 100
        ),
    }

    metadata = {
        "snapshot_version": SNAPSHOT_VERSION,
        "snapshot_date": snapshot_date.date().isoformat(),
        "classification_method": CLASSIFICATION_METHOD,
        "model_configuration": {
            "feature_count": len(model_features),
            "identical_ordered_feature_list": True,
        },
        "universe": {
            "total_stocks": EXPECTED_TOTAL_STOCKS,
            "prediction_ready_stocks": EXPECTED_READY_STOCKS,
        },
        "snapshot_counts": snapshot_counts,
        "v1_v2_comparison": comparison_counts,
    }

    return SnapshotResult(
        snapshot=snapshot,
        audit=audit,
        metadata=metadata,
    )



def make_json_safe(value: Any) -> Any:
    """Convert pandas, NumPy, and Path values into JSON-safe objects."""

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    if isinstance(value, np.bool_):
        return bool(value)

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if isinstance(value, Path):
        return str(value)

    return value


def build_snapshot_summary(result: SnapshotResult) -> str:
    """Build a concise Markdown summary for a saved production snapshot."""

    snapshot = result.snapshot
    audit = result.audit
    snapshot_date = result.metadata["snapshot_date"]

    class_counts = (
        snapshot["opportunity_risk_class"]
        .value_counts()
        .to_dict()
    )

    confidence_counts = (
        snapshot["data_confidence"]
        .value_counts()
        .to_dict()
    )

    attractive_stocks = snapshot.loc[
        snapshot["opportunity_risk_class"].eq("Attractive Risk-Reward"),
        "symbol",
    ].tolist()

    high_risk_opportunities = snapshot.loc[
        snapshot["opportunity_risk_class"].eq(
            "High Opportunity / High Risk"
        ),
        "symbol",
    ].tolist()

    changed_count = int(audit["classification_changed"].sum())
    changed_percent = audit["classification_changed"].mean() * 100

    class_lines = "\n".join(
        f"- {label}: **{count}**"
        for label, count in class_counts.items()
    )

    confidence_lines = "\n".join(
        f"- {label}: **{count}**"
        for label, count in confidence_counts.items()
    )

    attractive_text = ", ".join(attractive_stocks)
    high_risk_text = ", ".join(high_risk_opportunities)

    return f"""# Rank-Based Prediction Snapshot

## Snapshot Information

- Snapshot date: **{snapshot_date}**
- Snapshot version: **{SNAPSHOT_VERSION}**
- Classification method: **{CLASSIFICATION_METHOD}**
- Total stocks: **{len(snapshot)}**
- Prediction-ready stocks: **{int(snapshot["prediction_ready"].sum())}**
- Limited-confidence stocks: **{int((~snapshot["prediction_ready"]).sum())}**

## Data Confidence

{confidence_lines}

## Opportunity-Risk Classes

{class_lines}

## Attractive Risk-Reward

{attractive_text}

## High Opportunity / High Risk

{high_risk_text}

## V1 Versus V2 Comparison

- Changed classifications: **{changed_count}**
- Unchanged classifications: **{len(audit) - changed_count}**
- Changed percentage: **{changed_percent:.2f}%**

The production snapshot uses relative downside-risk ranks for its primary
combined classification. Fixed raw-probability bands remain descriptive alert
levels.

## Interpretation

The classification is historically validated as a relative downside-risk
screening framework. It is not validated as a proven alpha model or direct
buy/sell system.
"""


def save_snapshot_artifacts(
    result: SnapshotResult,
    paths: SnapshotPaths,
) -> SavedSnapshotArtifacts:
    """Save the production snapshot, audit, metadata, and summary."""

    paths.output_dir.mkdir(parents=True, exist_ok=True)

    snapshot_date = result.metadata["snapshot_date"]

    dated_csv = (
        paths.output_dir
        / f"rank_based_prediction_snapshot_{snapshot_date}_{SNAPSHOT_VERSION}.csv"
    )

    dated_parquet = (
        paths.output_dir
        / f"rank_based_prediction_snapshot_{snapshot_date}_{SNAPSHOT_VERSION}.parquet"
    )

    latest_csv = (
        paths.output_dir
        / f"latest_rank_based_prediction_snapshot_{SNAPSHOT_VERSION}.csv"
    )

    latest_parquet = (
        paths.output_dir
        / f"latest_rank_based_prediction_snapshot_{SNAPSHOT_VERSION}.parquet"
    )

    audit_csv = (
        paths.output_dir
        / f"v1_v2_classification_audit_{snapshot_date}_{SNAPSHOT_VERSION}.csv"
    )

    audit_parquet = (
        paths.output_dir
        / f"v1_v2_classification_audit_{snapshot_date}_{SNAPSHOT_VERSION}.parquet"
    )

    metadata_json = (
        paths.output_dir
        / f"rank_based_prediction_snapshot_metadata_{snapshot_date}_{SNAPSHOT_VERSION}.json"
    )

    summary_markdown = (
        paths.output_dir
        / f"rank_based_prediction_snapshot_summary_{snapshot_date}_{SNAPSHOT_VERSION}.md"
    )


    # ---------------------------------------------------------
    # Save snapshot and audit tables
    # ---------------------------------------------------------

    result.snapshot.to_csv(dated_csv, index=False)
    result.snapshot.to_parquet(dated_parquet, index=False)

    result.snapshot.to_csv(latest_csv, index=False)
    result.snapshot.to_parquet(latest_parquet, index=False)

    result.audit.to_csv(audit_csv, index=False)
    result.audit.to_parquet(audit_parquet, index=False)


    # ---------------------------------------------------------
    # Build production metadata
    # ---------------------------------------------------------

    output_files = {
        "dated_csv": dated_csv.name,
        "dated_parquet": dated_parquet.name,
        "latest_csv": latest_csv.name,
        "latest_parquet": latest_parquet.name,
        "audit_csv": audit_csv.name,
        "audit_parquet": audit_parquet.name,
        "metadata_json": metadata_json.name,
        "summary_markdown": summary_markdown.name,
    }

    metadata = {
        "pipeline": "marketguard.production_prediction_snapshot",
        "snapshot_version": SNAPSHOT_VERSION,
        "snapshot_date": snapshot_date,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification_method": CLASSIFICATION_METHOD,
        "input_files": {
            "feature_dataset": paths.feature_data.name,
            "outperform_model": paths.outperform_model.name,
            "downside_model": paths.downside_model.name,
        },
        **result.metadata,
        "classification_rules": {
            "opportunity_tiers": {
                "high": "ranks 1-18",
                "moderate": "ranks 19-45",
                "low": "ranks 46-90",
            },
            "risk_quintiles": {
                "q1_highest": "ranks 1-18",
                "q2_high": "ranks 19-36",
                "q3_medium": "ranks 37-54",
                "q4_lower": "ranks 55-72",
                "q5_lowest": "ranks 73-90",
            },
            "relative_risk": {
                "higher": "ranks 1-45",
                "lower": "ranks 46-90",
            },
            "fixed_probability_bands": {
                "low": "probability < 0.40",
                "watch": "0.40 <= probability < 0.47",
                "high": "0.47 <= probability < 0.51",
                "very_high": "probability >= 0.51",
            },
        },
        "limitations": [
            "Validated primarily for relative downside-risk screening.",
            "Not validated as a reliable alpha or market-beating strategy.",
            "Limited-confidence stocks receive probabilities but are excluded from ranks.",
        ],
        "output_files": output_files,
    }

    safe_metadata = make_json_safe(metadata)

    with metadata_json.open("w", encoding="utf-8") as file:
        json.dump(
            safe_metadata,
            file,
            indent=2,
            ensure_ascii=False,
        )


    # ---------------------------------------------------------
    # Save Markdown summary
    # ---------------------------------------------------------

    summary_text = build_snapshot_summary(result)
    summary_markdown.write_text(summary_text, encoding="utf-8")


    # ---------------------------------------------------------
    # Validate saved files
    # ---------------------------------------------------------

    saved_paths = [
        dated_csv,
        dated_parquet,
        latest_csv,
        latest_parquet,
        audit_csv,
        audit_parquet,
        metadata_json,
        summary_markdown,
    ]

    missing_paths = [
        path for path in saved_paths
        if not path.exists()
    ]

    if missing_paths:
        raise FileNotFoundError(
            "The following snapshot artifacts were not saved:\n"
            + "\n".join(str(path) for path in missing_paths)
        )

    return SavedSnapshotArtifacts(
        dated_csv=dated_csv,
        dated_parquet=dated_parquet,
        latest_csv=latest_csv,
        latest_parquet=latest_parquet,
        audit_csv=audit_csv,
        audit_parquet=audit_parquet,
        metadata_json=metadata_json,
        summary_markdown=summary_markdown,
    )


def run_snapshot_pipeline(
    paths: SnapshotPaths,
) -> tuple[SnapshotResult, SavedSnapshotArtifacts]:
    """Load inputs, build the latest snapshot, and save all artifacts."""

    feature_data, outperform_model, downside_model, model_features = (
        load_snapshot_inputs(paths)
    )

    result = build_rank_based_snapshot(
        feature_data=feature_data,
        outperform_model=outperform_model,
        downside_model=downside_model,
        model_features=model_features,
    )

    artifacts = save_snapshot_artifacts(
        result=result,
        paths=paths,
    )

    return result, artifacts