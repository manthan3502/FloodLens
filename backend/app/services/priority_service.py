"""Transparent two-term ranking; accessibility never changes the score."""

import math
import statistics


def rank_villages(villages, available_teams, weights):
    if type(available_teams) is not int or available_teams < 0:
        raise ValueError("Teams must be a nonnegative integer")
    if (
        set(weights) != {"w_risk", "w_pop"}
        or any(not math.isfinite(v) or v < 0 for v in weights.values())
        or not math.isclose(sum(weights.values()), 1)
    ):
        raise ValueError("Invalid priority weights")
    if not villages or available_teams == 0:
        return []
    if len({v["id"] for v in villages}) != len(villages):
        raise ValueError("Duplicate village IDs")
    known = [
        v["population_estimate"]
        for v in villages
        if v["population_estimate"] is not None
    ]
    if any(not math.isfinite(p) or p < 0 for p in known):
        raise ValueError("Invalid population")
    median = statistics.median(known) if known else None
    maximum = max(known, default=0)
    ranked = []
    for village in villages:
        risk = village["risk_score"]
        if not math.isfinite(risk) or not 0 <= risk <= 1:
            raise ValueError("Invalid risk")
        population = village["population_estimate"]
        effective = median if population is None else population
        normalized = (
            0.5
            if effective is None
            else math.log1p(effective) / math.log1p(maximum) if maximum > 0 else 0.0
        )
        priority = weights["w_risk"] * risk + weights["w_pop"] * normalized
        ranked.append(
            village
            | {
                "priority_score": priority,
                "normalized_population": normalized,
                "population_ranking_rule": (
                    "neutral_0.5_all_unknown"
                    if effective is None
                    else (
                        "study_median_for_unknown"
                        if population is None
                        else "log1p_over_study_max"
                    )
                ),
                "recommended_action": "Prioritize field assessment; verify local conditions",
            }
        )
    ranked.sort(key=lambda v: (-v["priority_score"], v["id"]))
    return [v | {"rank": index + 1} for index, v in enumerate(ranked[:available_teams])]
