# evasion-orchestrator/app.py
import os
from typing import Tuple

import httpx
from fastapi import FastAPI, HTTPException

from common.schemas import (
    EvalRequest,
    EvalResult,
    MutateRequest,
    ScoreRequest,
)

app = FastAPI(title="evasion-orchestrator")

# Inside Docker, use service names; allow overrides via env vars
MUTATE_URL = os.getenv("MUTATE_URL", "http://mutator:8083/mutate")
SCORE_URL = os.getenv("SCORE_URL", "http://detector:8501/score")

# Tweak timeouts/retries as needed
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10.0"))


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mutate_url": MUTATE_URL,
        "score_url": SCORE_URL,
    }


async def _mutate(client: httpx.AsyncClient, domain: str) -> str:
    """Call mutator once (simple single-op example)."""
    mreq = MutateRequest(domain=domain, ops=["insert:pos=3:ch=x"])
    try:
        resp = await client.post(MUTATE_URL, json=mreq.model_dump())
        resp.raise_for_status()
        data = resp.json()
        muts = data.get("mutated") or []
        if not muts:
            raise HTTPException(status_code=502, detail="Mutator returned no mutations")
        return muts[0]
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Mutator call failed: {e}") from e


async def _score(client: httpx.AsyncClient, domain: str) -> Tuple[str, float]:
    """Call detector and return (label, confidence)."""
    sreq = ScoreRequest(domain=domain)
    try:
        resp = await client.post(SCORE_URL, json=sreq.model_dump())
        resp.raise_for_status()
        data = resp.json()
        label = str(data.get("label", "unknown"))
        conf = float(data.get("confidence", 0.0))
        return label, conf
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Detector call failed: {e}") from e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Bad detector response: {e}") from e


async def try_mutations(
    domain: str, max_iters: int, target_conf: float
) -> Tuple[int, bool, float, str, str]:
    """
    Loop: mutate -> score -> success if benign & conf >= target_conf.
    Returns: (iters, success, final_confidence, final_label, mutated_domain)
    """
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        current = domain
        last_label, last_conf, last_mut = "malicious", 0.0, domain

        for i in range(1, max_iters + 1):
            mutated = await _mutate(client, current)
            label, conf = await _score(client, mutated)

            last_label, last_conf, last_mut = label, conf, mutated
            if label == "benign" and conf >= target_conf:
                return i, True, conf, label, mutated

            # continue iterating using the latest mutation
            current = mutated

        return max_iters, False, last_conf, last_label, last_mut


@app.post("/eval", response_model=EvalResult)
async def eval_domain(req: EvalRequest):
    iters, success, conf, label, mutated = await try_mutations(
        req.domain, req.max_iters, req.target_conf
    )
    return EvalResult(
        domain=req.domain,
        iters=iters,
        success=success,
        final_confidence=round(conf, 3),
        final_label=label,
        mutated=mutated,
    )
