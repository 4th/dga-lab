
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI(title="telemetry")

class LogEvent(BaseModel):
    kind: str
    data: Dict[str, Any]

LOGS = []

@app.post("/log")
def log(ev: LogEvent):
    LOGS.append(ev.dict())
    return {"status":"ok","count": len(LOGS)}

@app.get("/log")
def get_logs():
    return {"logs": LOGS}
