
# DGA Detection Evasion — Kubernetes Microservices Skeleton

This repository provides a minimal end-to-end **Botnet DGA Detection Evasion** lab with pluggable microservices.
Each service is a FastAPI app with a tiny stub implementation so you can run locally (Docker Compose) or deploy to Kubernetes.

## Services
- `ingest-api`: Accepts domain batches.
- `feature-extractor`: Computes simple features from domains.
- `dga-detector`: Dummy CNN-like classifier (heuristic) — replace with your model server.
- `mutator`: Generates adversarial domain mutations.
- `evasion-orchestrator`: Iteratively queries detector with mutations until evasion succeeds.
- `gateway`: Facade to call other services.
- `telemetry`: Stub endpoint to receive logs/metrics.

## Quick start (local)
```bash
# 1) Create virtualenv
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Run a service (example: detector)
uvicorn dga-detector.app:app --reload --port 8501
# In other terminals, start the rest:
uvicorn ingest-api.app:app --reload --port 8081
uvicorn feature-extractor.app:app --reload --port 8082
uvicorn mutator.app:app --reload --port 8083
uvicorn evasion-orchestrator.app:app --reload --port 8084
uvicorn gateway.app:app --reload --port 8080
uvicorn telemetry.app:app --reload --port 8085
```

### Example flow
```bash
# Ingest some domains
curl -X POST http://localhost:8081/ingest/domains -H "content-type: application/json" -d '{
  "batch_id":"demo","domains":["secure-bank.co","paypa1-login.net","xkcd.com"]
}'

# Score a domain
curl -X POST http://localhost:8501/score -H "content-type: application/json" -d '{
  "domain":"paypa1-login.net"
}'

# Mutate a domain
curl -X POST http://localhost:8083/mutate -H "content-type: application/json" -d '{
  "domain":"paypa1-login.net","ops":["insert:pos=3:ch=x"]
}'

# Evasion test (orchestrator calls mutator+detector)
curl -X POST http://localhost:8084/eval -H "content-type: application/json" -d '{
  "domain":"paypa1-login.net","max_iters":5,"target_conf":0.25
}'
```

## Kubernetes
See `k8s/manifests.yaml` for a basic namespace, Deployments, Services, Ingress, HPA and NetworkPolicy examples.
Replace container images with your registry paths.

## Replace the dummy model
Swap out `dga-detector/app.py` with TensorFlow Serving, TorchServe, or your own model container.
Ensure it implements the `/score` contract defined in `common/schemas.py`.
