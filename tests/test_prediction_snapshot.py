"""Tests for the production rank-based snapshot classification logic."""

import numpy as np
import pandas as pd
import pytest

from marketguard.prediction_snapshot import (
    CLASSIFICATION_METHOD,
    SNAPSHOT_VERSION,
    assign_fixed_downside_risk_band,
    classify_rank_based_snapshot,
)


def make_snapshot(downside_rank_order: str = "same") -> pd.DataFrame:
    """Create a synthetic snapshot with 90 ready and 10 limited stocks."""

    total_stocks = 100
    ready_stocks = 90

    prediction_ready = [True] * ready_stocks + [False] * 10
    outperform_ranks = list(range(1, ready_stocks + 1)) + [pd.NA] * 10

    if downside_rank_order == "same":
        ready_downside_ranks = list(range(1, ready_stocks + 1))
    elif downside_rank_order == "reversed":
        ready_downside_ranks = list(range(ready_stocks, 0, -1))
    else:
        raise ValueError(f"Unsupported downside rank order: {downside_rank_order}")

    downside_ranks = ready_downside_ranks + [pd.NA] * 10
    downside_probabilities = np.linspace(0.30, 0.70, ready_stocks).tolist()
    downside_probabilities += [np.nan] * 10

    return pd.DataFrame({
        "yf_ticker": [f"STOCK_{number:03d}" for number in range(total_stocks)],
        "prediction_ready": prediction_ready,
        "outperform_rank_ready_universe": outperform_ranks,
        "downside_risk_rank_ready_universe": downside_ranks,
        "downside_probability": downside_probabilities,
    })


@pytest.mark.parametrize(
    ("probability", "expected_band"),
    [
        (0.399999, "Low Risk"),
        (0.40, "Watch Risk"),
        (0.469999, "Watch Risk"),
        (0.47, "High Risk"),
        (0.509999, "High Risk"),
        (0.51, "Very High Risk"),
        (0.75, "Very High Risk"),
        (np.nan, "Unavailable"),
    ],
)
def test_fixed_downside_risk_band_boundaries(probability, expected_band):
    assert assign_fixed_downside_risk_band(probability) == expected_band


def test_rank_based_group_sizes():
    classified = classify_rank_based_snapshot(make_snapshot())

    assert classified["opportunity_tier"].value_counts().to_dict() == {
        "Low Opportunity": 45,
        "Moderate Opportunity": 27,
        "High Opportunity": 18,
        "Limited Confidence": 10,
    }

    assert classified["downside_risk_quintile"].value_counts().to_dict() == {
        "Q1 — Highest Risk": 18,
        "Q2 — High Risk": 18,
        "Q3 — Medium Risk": 18,
        "Q4 — Lower Risk": 18,
        "Q5 — Lowest Risk": 18,
        "Limited Confidence": 10,
    }

    assert classified["relative_downside_risk"].value_counts().to_dict() == {
        "Higher Relative Risk": 45,
        "Lower Relative Risk": 45,
        "Limited Confidence": 10,
    }


def test_same_rank_order_combined_classes():
    classified = classify_rank_based_snapshot(
        make_snapshot(downside_rank_order="same")
    )

    assert classified["opportunity_risk_class"].value_counts().to_dict() == {
        "Low Opportunity / Lower Risk": 45,
        "Caution": 27,
        "High Opportunity / High Risk": 18,
        "Limited Confidence - Review": 10,
    }


def test_reversed_rank_order_combined_classes():
    classified = classify_rank_based_snapshot(
        make_snapshot(downside_rank_order="reversed")
    )

    assert classified["opportunity_risk_class"].value_counts().to_dict() == {
        "Unfavourable Risk-Reward": 45,
        "Balanced Opportunity": 27,
        "Attractive Risk-Reward": 18,
        "Limited Confidence - Review": 10,
    }


def test_limited_stocks_do_not_receive_ready_universe_classes():
    classified = classify_rank_based_snapshot(make_snapshot())
    limited = classified.loc[~classified["prediction_ready"]]

    assert limited["opportunity_tier"].eq("Limited Confidence").all()
    assert limited["downside_risk_quintile"].eq("Limited Confidence").all()
    assert limited["relative_downside_risk"].eq("Limited Confidence").all()
    assert limited["opportunity_risk_class"].eq(
        "Limited Confidence - Review"
    ).all()
    assert limited["downside_risk_band"].eq("Unavailable").all()


def test_classification_metadata_columns():
    classified = classify_rank_based_snapshot(make_snapshot())

    assert classified["classification_version"].eq(SNAPSHOT_VERSION).all()
    assert classified["classification_method"].eq(CLASSIFICATION_METHOD).all()


def test_duplicate_ready_rank_is_rejected():
    snapshot = make_snapshot()
    snapshot.loc[1, "outperform_rank_ready_universe"] = 1

    with pytest.raises(ValueError, match="unique rank"):
        classify_rank_based_snapshot(snapshot)


def test_incorrect_ready_stock_count_is_rejected():
    snapshot = make_snapshot()
    snapshot.loc[89, "prediction_ready"] = False
    snapshot.loc[89, "outperform_rank_ready_universe"] = pd.NA
    snapshot.loc[89, "downside_risk_rank_ready_universe"] = pd.NA

    with pytest.raises(ValueError, match="Expected 90 prediction-ready stocks"):
        classify_rank_based_snapshot(snapshot)