import json
from urllib.error import HTTPError
from urllib.request import urlopen

import httpx

from scripts.deploy import start


def test_initialization_allows_frontend_to_retry_without_cors_failure(monkeypatch):
    origin = "https://floodlens-lilac.vercel.app"
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", origin)
    server, thread = start.start_initialization_server(0)
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{server.server_port}") as client:
            headers = {
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            }
            preflight = client.options("/scenarios/evaluate", headers=headers)
            assert preflight.status_code == 200
            assert preflight.headers["access-control-allow-origin"] == origin
            response = client.post(
                "/scenarios/evaluate",
                headers={"Origin": origin},
                json={"scenario_id": "normal"},
            )
            assert response.status_code == 503
            assert response.headers["access-control-allow-origin"] == origin
            assert response.json() == {"status": "initializing"}
            headers["Origin"] = "https://untrusted.example"
            rejected = client.options("/scenarios/evaluate", headers=headers)
            assert rejected.status_code == 400
            assert "access-control-allow-origin" not in rejected.headers
    finally:
        start.stop_initialization_server(server, thread)


def test_initialization_server_binds_and_reports_not_ready():
    server, thread = start.start_initialization_server(0)
    try:
        try:
            urlopen(f"http://127.0.0.1:{server.server_port}/health", timeout=2)
        except HTTPError as error:
            assert error.code == 503
            assert json.load(error) == {"status": "initializing"}
        else:
            raise AssertionError("Initialization server must not report readiness")
    finally:
        start.stop_initialization_server(server, thread)


def test_complete_seed_skips_import(monkeypatch):
    commands = []
    monkeypatch.setattr(start, "seed_is_complete", lambda: True)
    monkeypatch.setattr(start, "query", lambda sql: [{"id": "index-v1"}])
    monkeypatch.setattr(
        start.subprocess, "run", lambda command, check: commands.append(command)
    )

    start.bootstrap()

    assert len(commands) == 1
    assert "alembic" in commands[0]


def test_seed_completeness_checks_every_manifest_table(monkeypatch):
    counts = dict(start.SEED_COUNTS)
    monkeypatch.setattr(start, "query", lambda sql: [counts])
    assert start.seed_is_complete()

    counts["waterways"] -= 1
    assert not start.seed_is_complete()


def test_partial_seed_is_resumed_and_verified(monkeypatch):
    commands = []
    completeness = iter([False, True])
    monkeypatch.setattr(start, "seed_is_complete", lambda: next(completeness))
    monkeypatch.setattr(start, "query", lambda sql: [{"id": "index-v1"}])
    monkeypatch.setattr(
        start.subprocess, "run", lambda command, check: commands.append(command)
    )

    start.bootstrap()

    assert any("data_pipeline.seed" in command for command in commands)
