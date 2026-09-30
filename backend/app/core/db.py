"""Small connection pool; credentials are supplied through the environment."""

from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from data_pipeline.database import database_url, requires_ssl, verified_ssl_context


@lru_cache
def engine():
    raw_url = database_url()
    url = make_url(raw_url).set(drivername="postgresql+pg8000")
    url = url.difference_update_query(["sslmode"])
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=3,
        max_overflow=2,
        connect_args=(
            {"ssl_context": verified_ssl_context()} if requires_ssl(raw_url) else {}
        ),
    )


def query(sql, params=None):
    with engine().connect() as connection:
        return [
            dict(row) for row in connection.execute(text(sql), params or {}).mappings()
        ]
