"""Initialize an empty deployment database, then serve the application."""

import os
import subprocess
import sys

from app.core.db import query


def main():
    subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            "backend/alembic.ini",
            "upgrade",
            "head",
        ],
        check=True,
    )
    count = query("SELECT count(*) AS n FROM grid_cells")[0]["n"]
    if count == 0:
        subprocess.run([sys.executable, "-m", "data_pipeline.seed"], check=True)
    if not query("SELECT id FROM model_metadata WHERE id='index-v1'"):
        subprocess.run([sys.executable, "-m", "data_pipeline.score"], check=True)
    os.execvp(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            os.getenv("PORT", "8000"),
        ],
    )


if __name__ == "__main__":
    main()
