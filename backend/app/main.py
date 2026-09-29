"""FloodLens API foundation. Data endpoints are introduced in milestone M3."""

import json
import logging
import os
import time

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.api.routes import router

app = FastAPI(title="FloodLens", version="0.1.0")
if os.getenv("ENV") == "production":
    configured_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if not configured_origins or any(
        not origin.strip().startswith("https://")
        for origin in configured_origins.split(",")
    ):
        raise RuntimeError("Production requires explicit HTTPS CORS origins")
app.include_router(router)
logger = logging.getLogger("floodlens")


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Check the request fields",
                "fields": [
                    {"field": ".".join(map(str, e["loc"])), "message": e["msg"]}
                    for e in exc.errors()
                ],
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "not_found" if exc.status_code == 404 else "request_error",
                "message": str(exc.detail),
            }
        },
    )


@app.middleware("http")
async def request_log(request, call_next):
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.error("request_failed", extra={"path": request.url.path})
        response = JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "data_unavailable",
                    "message": "Study data is temporarily unavailable",
                }
            },
        )
    logger.info(
        json.dumps(
            {
                "path": request.url.path,
                "status": response.status_code,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        )
    )
    return response


origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness only; this does not claim that data or the database are ready."""
    return {"status": "ok"}
