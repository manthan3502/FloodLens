"""Small connection pool; credentials are supplied through the environment."""

import os
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine, text


def database_url():
    url = os.getenv("DATABASE_URL")
    env_path = Path(__file__).resolve().parents[3] / ".env"
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
        # Repository root when running from a source checkout.
        env_path = Path(__file__).resolve().parents[4] / ".env"
        if env_path.exists():
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
    return url.replace("postgresql+psycopg://", "postgresql+pg8000://").replace(
        "postgresql://", "postgresql+pg8000://"
    )


@lru_cache
def engine():
    return create_engine(
        database_url(), pool_pre_ping=True, pool_size=3, max_overflow=2
    )


def query(sql, params=None):
    with engine().connect() as connection:
        return [
            dict(row) for row in connection.execute(text(sql), params or {}).mappings()
        ]
