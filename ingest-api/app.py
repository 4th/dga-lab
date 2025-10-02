
from fastapi import FastAPI
from typing import List
from common.schemas import IngestRequest
app = FastAPI(title="ingest-api")

STORE: List[str] = []

@app.post("/ingest/domains")
def ingest(req: IngestRequest):
    STORE.extend(req.domains)
    return {"status":"ok","batch_id":req.batch_id,"count":len(req.domains)}
