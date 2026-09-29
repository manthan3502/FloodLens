"""Deterministic, uncalibrated relative susceptibility scoring; not probability."""

import json
import math
from pathlib import Path

CONFIG = json.loads(Path(__file__).with_suffix(".json").read_text())


def clip(value):
    return min(1.0, max(0.0, value))


def category(score):
    return (
        "Low"
        if score < 0.25
        else "Medium" if score < 0.5 else "High" if score < 0.75 else "Critical"
    )


def score_cell(features, scenario, elevation_bounds, config=CONFIG):
    required = ("elevation", "slope", "dist_to_river")
    for name in required:
        value = features.get(name)
        if value is None or not math.isfinite(value):
            raise ValueError(f"Missing or non-finite {name}")
    if not 0 <= features["slope"] <= 90 or features["dist_to_river"] < 0:
        raise ValueError("Invalid slope or river distance")
    lo, hi = elevation_bounds
    if not math.isfinite(lo) or not math.isfinite(hi) or lo >= hi:
        raise ValueError("Invalid elevation normalization bounds")
    daily, three_day = scenario["rainfall_24h_mm"], scenario["rainfall_72h_mm"]
    if (
        not all(math.isfinite(v) for v in [daily, three_day])
        or not 0 <= daily <= three_day
    ):
        raise ValueError("Invalid rainfall")
    history = features.get("historical_evidence")
    if history is not None and (not math.isfinite(history) or not 0 <= history <= 1):
        raise ValueError("Invalid historical evidence")
    factors = {
        "elevation": 1 - clip((features["elevation"] - lo) / (hi - lo)),
        "river_proximity": math.exp(
            -features["dist_to_river"] / config["river_decay_metres"]
        ),
        "slope": 1 - clip(features["slope"] / config["slope_cap_degrees"]),
        "historical_evidence": (
            config["unknown_history_value"] if history is None else history
        ),
        "rainfall": (
            clip(daily / config["rainfall_24h_reference_mm"])
            + clip(three_day / config["rainfall_72h_reference_mm"])
        )
        / 2,
    }
    weights = config["weights"]
    if (
        set(weights) != set(factors)
        or any(not math.isfinite(v) or v < 0 for v in weights.values())
        or not math.isclose(sum(weights.values()), 1)
    ):
        raise ValueError("Weights must be finite, nonnegative and sum to one")
    contributions = {name: value * weights[name] for name, value in factors.items()}
    score = clip(sum(contributions.values()))
    return {
        "risk_score": score,
        "risk_category": category(score),
        "factors": factors,
        "contributions": contributions,
        "history_missing": history is None,
    }
