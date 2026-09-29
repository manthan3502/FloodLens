from typing import Annotated, Literal

from app.core.db import query
from app.services.priority_service import rank_villages
from app.services.risk_service import evaluate, rivers
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter()
Scenario = Literal["normal", "heavy", "extreme"]


class ScenarioRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario_id: Scenario


class PriorityRequest(ScenarioRequest):
    available_teams: Annotated[int, Field(strict=True, ge=0, le=100000)]


@router.get("/villages")
def villages(scenario_id: Scenario = "normal"):
    return evaluate(scenario_id)


@router.get("/villages/{village_id}")
def village(village_id: str, scenario_id: Annotated[Scenario, Query()] = "normal"):
    feature = next(
        (f for f in evaluate(scenario_id)["features"] if f["id"] == village_id), None
    )
    if feature is None:
        raise HTTPException(404, "Village not found")
    return feature["properties"]


@router.post("/scenarios/evaluate")
def scenario(request: ScenarioRequest):
    return evaluate(request.scenario_id)


@router.post("/priorities/calculate")
def priorities(request: PriorityRequest):
    weights = query("SELECT w_risk,w_pop FROM priority_weights_config WHERE id=1")[0]
    villages = [f["properties"] for f in evaluate(request.scenario_id)["features"]]
    return rank_villages(villages, request.available_teams, weights)


@router.get("/rivers")
def waterways():
    return rivers()


@router.get("/model/metadata")
def metadata():
    result = query("SELECT * FROM model_metadata WHERE id='index-v1'")[0]
    result["priority_weights"] = query(
        "SELECT w_risk,w_pop FROM priority_weights_config WHERE id=1"
    )[0]
    result["rainfall_scenarios"] = query(
        "SELECT * FROM rainfall_scenarios ORDER BY rainfall_24h_mm"
    )
    return result
