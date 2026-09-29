"""Exercise every documented endpoint against an actually running server."""

import json
import os

import httpx

with httpx.Client(
    base_url=os.getenv("API_BASE_URL", "http://localhost:8000"), timeout=60
) as client:
    checks = {}
    for path in ["/health", "/villages", "/rivers", "/model/metadata"]:
        response = client.get(path)
        response.raise_for_status()
        checks[path] = response.status_code
        if path == "/villages":
            village_id = response.json()["features"][0]["id"]
    response = client.get(f"/villages/{village_id}")
    response.raise_for_status()
    checks["/villages/{id}"] = response.status_code
    for path, body in [
        ("/scenarios/evaluate", {"scenario_id": "heavy"}),
        ("/priorities/calculate", {"scenario_id": "heavy", "available_teams": 3}),
    ]:
        response = client.post(path, json=body)
        response.raise_for_status()
        checks[path] = response.status_code
    print(json.dumps(checks, indent=2))
