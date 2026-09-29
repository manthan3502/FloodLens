import pytest
from app.main import app
from app.services.risk_service import snapshot
from fastapi.testclient import TestClient

client = TestClient(app)


def test_real_postgis_geojson_scenarios_and_detail():
    response = client.get("/villages")
    assert response.status_code == 200, response.text
    baseline = response.json()
    assert baseline["type"] == "FeatureCollection"
    assert len(baseline["features"]) == 380
    for feature in baseline["features"]:
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "MultiPolygon"
        assert 0 <= feature["properties"]["risk_score"] <= 1
        x, y = feature["geometry"]["coordinates"][0][0][0]
        assert 73.7 <= x <= 74.85 and 16.3 <= y <= 17.1
    extreme = client.post("/scenarios/evaluate", json={"scenario_id": "extreme"}).json()
    assert all(
        a["properties"]["risk_score"] < b["properties"]["risk_score"]
        for a, b in zip(baseline["features"], extreme["features"], strict=True)
    )
    detail = client.get(
        f"/villages/{baseline['features'][0]['id']}?scenario_id=extreme"
    )
    assert detail.status_code == 200
    assert detail.json() == extreme["features"][0]["properties"]
    assert (
        sum(
            f["properties"]["population_estimate"] is None for f in baseline["features"]
        )
        == 9
    )


def test_other_endpoints():
    assert len(client.get("/rivers").json()["features"]) == 95
    meta = client.get("/model/metadata").json()
    assert meta["model_type"] == "susceptibility_index"
    assert meta["pr_auc_spatial_cv"] is None
    assert meta["priority_weights"] == {"w_risk": 0.65, "w_pop": 0.35}
    assert (
        client.post(
            "/priorities/calculate",
            json={"scenario_id": "normal", "available_teams": 5},
        ).status_code
        == 200
    )


@pytest.mark.parametrize(
    "body",
    [{"scenario_id": "invalid"}, {}, {"scenario_id": "heavy", "custom_rainfall": 20}],
)
def test_scenario_validation(body):
    result = client.post("/scenarios/evaluate", json=body)
    assert result.status_code == 422
    assert result.json()["error"]["fields"]


@pytest.mark.parametrize("teams", [-1, 1.5, "5", True, None])
def test_teams_validation(teams):
    assert (
        client.post(
            "/priorities/calculate",
            json={"scenario_id": "normal", "available_teams": teams},
        ).status_code
        == 422
    )


def test_missing_village_and_invalid_query():
    assert client.get("/villages/missing").status_code == 404
    assert client.get("/villages?scenario_id=bad").status_code == 422


def test_exact_area_weighted_aggregation():
    result = client.get("/villages").json()["features"][0]["properties"]
    assert (
        abs(sum(result["factor_contributions"].values()) - result["risk_score"]) < 1e-10
    )


def test_database_failure_is_explicit(monkeypatch):
    snapshot.cache_clear()

    def fail(*args, **kwargs):
        raise RuntimeError("private database error")

    monkeypatch.setattr("app.services.risk_service.query", fail)
    response = client.get("/villages")
    assert response.status_code == 503
    assert "private" not in response.text
    snapshot.cache_clear()
