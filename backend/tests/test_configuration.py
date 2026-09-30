import os
import ssl
import subprocess
import sys
from pathlib import Path

from app.core import db


def test_production_database_requires_verified_tls(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://example:placeholder@example.invalid/test?sslmode=require",
    )
    captured = {}

    def create(url, **kwargs):
        captured.update(kwargs)
        assert "sslmode" not in url.query

    monkeypatch.setattr(db, "create_engine", create)
    db.engine.__wrapped__()
    context = captured["connect_args"]["ssl_context"]
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname
    assert any(
        dict(name[0] for name in certificate["subject"]).get("commonName")
        == "Supabase Root 2021 CA"
        for certificate in context.get_ca_certs()
    )


def test_production_rejects_unconfigured_or_http_cors():
    env = os.environ | {
        "ENV": "production",
        "CORS_ALLOWED_ORIGINS": "http://localhost:5173",
        "PYTHONPATH": str(Path(__file__).resolve().parents[1]),
    }
    result = subprocess.run(
        [sys.executable, "-c", "import app.main"], env=env, capture_output=True
    )
    assert result.returncode != 0
    assert b"Production requires explicit HTTPS CORS origins" in result.stderr
