"""Initialize the deployment database while keeping Render's port open."""

import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from app.core.db import query

ROOT = Path(__file__).resolve().parents[2]
SEED_COUNTS = json.loads(
    (ROOT / "data/processed/seed-counts.json").read_text(encoding="utf-8")
)


class InitializationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'{"status":"initializing"}'
        self.send_response(503)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Retry-After", "10")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


class InitializationServer(ThreadingHTTPServer):
    allow_reuse_address = True


def start_initialization_server(port):
    server = InitializationServer(("0.0.0.0", port), InitializationHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def stop_initialization_server(server, thread):
    server.shutdown()
    server.server_close()
    thread.join()


def seed_is_complete():
    columns = ",".join(
        f'(SELECT count(*) FROM "{table}") AS "{table}"'
        for table in SEED_COUNTS
    )
    counts = query(f"SELECT {columns}")[0]
    return all(counts[table] >= expected for table, expected in SEED_COUNTS.items())


def bootstrap():
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
    if not seed_is_complete():
        subprocess.run([sys.executable, "-m", "data_pipeline.seed"], check=True)
        if not seed_is_complete():
            raise RuntimeError("Production seed is incomplete after import")
    if not query("SELECT id FROM model_metadata WHERE id='index-v1'"):
        subprocess.run([sys.executable, "-m", "data_pipeline.score"], check=True)


def main():
    port = int(os.getenv("PORT", "8000"))
    server, thread = start_initialization_server(port)
    try:
        bootstrap()
    finally:
        stop_initialization_server(server, thread)
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
            str(port),
        ],
    )


if __name__ == "__main__":
    main()
