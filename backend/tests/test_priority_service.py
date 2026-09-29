import math

import pytest
from app.services.priority_service import rank_villages

WEIGHTS = {"w_risk": 0.65, "w_pop": 0.35}
VILLAGES = [
    {"id": "b", "risk_score": 0.8, "population_estimate": 100},
    {"id": "a", "risk_score": 0.8, "population_estimate": 100},
    {"id": "c", "risk_score": 0.2, "population_estimate": 10},
]


@pytest.mark.parametrize("teams,expected", [(0, 0), (1, 1), (2, 2), (50, 3)])
def test_sizes_order_and_determinism(teams, expected):
    result = rank_villages(VILLAGES, teams, WEIGHTS)
    assert len(result) == expected
    assert result == rank_villages(list(reversed(VILLAGES)), teams, WEIGHTS)
    assert [v["rank"] for v in result] == list(range(1, expected + 1))
    if result:
        assert result[0]["id"] == "a"


def test_unknown_population_is_not_silently_zero():
    result = rank_villages(
        VILLAGES + [{"id": "missing", "risk_score": 0.8, "population_estimate": None}],
        4,
        WEIGHTS,
    )
    missing = next(v for v in result if v["id"] == "missing")
    assert missing["population_estimate"] is None
    assert missing["normalized_population"] == 1
    assert missing["population_ranking_rule"] == "study_median_for_unknown"


def test_accessibility_and_history_cannot_change_priority():
    changed = [
        v
        | {
            "accessibility": {
                "category": "Difficult",
                "distance_to_major_road_m": 999999,
            },
            "historical_evidence": 1,
        }
        for v in VILLAGES
    ]
    base = rank_villages(VILLAGES, 3, WEIGHTS)
    assert [v["priority_score"] for v in base] == [
        v["priority_score"] for v in rank_villages(changed, 3, WEIGHTS)
    ]
    for v in base:
        assert math.isclose(
            v["priority_score"],
            0.65 * v["risk_score"] + 0.35 * v["normalized_population"],
        )


def test_all_missing_zero_and_empty_population():
    assert rank_villages([], 10, WEIGHTS) == []
    missing = [{"id": "x", "risk_score": 0.5, "population_estimate": None}]
    assert rank_villages(missing, 1, WEIGHTS)[0]["normalized_population"] == 0.5
    assert (
        rank_villages([missing[0] | {"population_estimate": 0}], 1, WEIGHTS)[0][
            "normalized_population"
        ]
        == 0
    )


@pytest.mark.parametrize("teams", [-1, 1.5, True])
def test_invalid_teams(teams):
    with pytest.raises(ValueError):
        rank_villages(VILLAGES, teams, WEIGHTS)


def test_bad_data_and_weights_rejected():
    with pytest.raises(ValueError):
        rank_villages(VILLAGES, 2, {"w_risk": 1, "w_pop": 1})
    with pytest.raises(ValueError):
        rank_villages([VILLAGES[0] | {"population_estimate": -1}], 2, WEIGHTS)
