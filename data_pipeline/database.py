"""Shared database URL and verified TLS configuration."""

import os
import ssl
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUPABASE_CA_CERT = (
    PROJECT_ROOT / "backend" / "certs" / "supabase-prod-ca-2021.crt"
)
SSL_MODES = {"require", "verify-full", "verify-ca"}


def database_url():
    url = os.getenv("DATABASE_URL")
    env_path = PROJECT_ROOT / ".env"
    if not url and env_path.exists():
        url = next(
            (
                line.split("=", 1)[1]
                for line in env_path.read_text().splitlines()
                if line.startswith("DATABASE_URL=")
            ),
            None,
        )
    if not url:
        raise RuntimeError("DATABASE_URL is required")
    return url


def requires_ssl(url):
    mode = parse_qs(urlparse(url).query).get("sslmode", [None])[0]
    return os.getenv("ENV") == "production" or mode in SSL_MODES


def verified_ssl_context():
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=SUPABASE_CA_CERT)
    return context
