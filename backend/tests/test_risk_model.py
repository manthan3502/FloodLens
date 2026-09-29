import math

import pytest
from app.ml.susceptibility import CONFIG, score_cell

FEATURES = {
    "elevation": 550,
    "slope": 2,
    "dist_to_river": 200,
    "historical_evidence": 0.2,
}
NORMAL = {"rainfall_24h_mm": 3.7, "rainfall_72h_mm": 13.5}
EXTREME = {"rainfall_24h_mm": 53.34, "rainfall_72h_mm": 140.52}


def test_deterministic_bounded_and_monotonic_rainfall():
    a = score_cell(FEATURES, NORMAL, (500, 800))
    assert a == score_cell(FEATURES, NORMAL, (500, 800))
    assert (
        0
        <= a["risk_score"]
        < score_cell(FEATURES, EXTREME, (500, 800))["risk_score"]
        <= 1
    )
    assert math.isclose(sum(a["contributions"].values()), a["risk_score"])


@pytest.mark.parametrize("field", ["elevation", "slope", "dist_to_river"])
@pytest.mark.parametrize("value", [None, float("nan"), float("inf")])
def test_required_missing_rejected(field, value):
    with pytest.raises(ValueError):
        score_cell(FEATURES | {field: value}, NORMAL, (500, 800))


def test_unknown_history_is_explicit_and_not_dry():
    result = score_cell(FEATURES | {"historical_evidence": None}, NORMAL, (500, 800))
    assert result["history_missing"]
    assert result["factors"]["historical_evidence"] == 0.5


def test_population_and_accessibility_do_not_affect_susceptibility():
    assert score_cell(FEATURES, NORMAL, (500, 800)) == score_cell(
        FEATURES | {"population": 1e9, "dist_to_road": 1e8}, NORMAL, (500, 800)
    )


def test_invalid_weights_and_rainfall_rejected():
    with pytest.raises(ValueError):
        score_cell(FEATURES, NORMAL, (500, 800), CONFIG | {"weights": {"elevation": 1}})
    with pytest.raises(ValueError):
        score_cell(FEATURES, NORMAL | {"rainfall_24h_mm": -1}, (500, 800))


def test_lower_flatter_closer_has_no_lower_score():
    low = score_cell(
        FEATURES | {"elevation": 500, "slope": 0, "dist_to_river": 0},
        NORMAL,
        (500, 800),
    )
    high = score_cell(
        FEATURES | {"elevation": 900, "slope": 30, "dist_to_river": 9000},
        NORMAL,
        (500, 800),
    )
    assert low["risk_score"] > high["risk_score"]
