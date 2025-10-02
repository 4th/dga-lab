# gateway/app.py
import os
import httpx
from fastapi import FastAPI, HTTPException, Response
from typing import Optional

from common.schemas import (
    IngestRequest,
    ScoreRequest,
    MutateRequest,
    EvalRequest,
)

app = FastAPI(title="gateway")

# Default to Docker Compose service names; allow overrides via env vars.
INGEST_URL = os.getenv("INGEST_URL", "http://ingest:8081/ingest/domains")
SCORE_URL  = os.getenv("SCORE_URL",  "http://detector:8501/score")
MUTATE_URL = os.getenv("MUTATE_URL", "http://mutator:8083/mutate")
EVAL_URL   = os.getenv("EVAL_URL",   "http://orchestrator:8084/eval")

HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10.0"))


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "ingest_url": INGEST_URL,
        "score_url": SCORE_URL,
        "mutate_url": MUTATE_URL,
        "eval_url": EVAL_URL,
        "timeout_sec": HTTP_TIMEOUT,
    }


async def _post_json(url: str, payload: dict) -> Response:
    """
    Proxy a POST with JSON to a backend service and return a FastAPI Response
    that preserves status code and content-type. Raises HTTPException on transport errors.
    """
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            r = await client.post(url, json=payload)
    except httpx.HTTPError as e:
        # Transport-level failure (DNS, connect, timeout, etc.)
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {e}") from e

    # Pass through upstream response (status + content + content-type)
    return Response(
        content=r.content,
        status_code=r.status_code,
        media_type=r.headers.get("content-type", "application/json"),
    )


@app.post("/ingest")
async def ingest(req: IngestRequest):
    # Send to ingest-api
    return await _post_json(INGEST_URL, req.model_dump())


@app.post("/score")
async def score(req: ScoreRequest):
    # Send to detector
    return await _post_json(SCORE_URL, req.model_dump())


@app.post("/mutate")
async def mutate(req: MutateRequest):
    # Send to mutator
    return await _post_json(MUTATE_URL, req.model_dump())


@app.post("/eval")
async def eval_(req: EvalRequest):
    # Send to evasion-orchestrator
    return await _post_json(EVAL_URL, req.model_dump())
