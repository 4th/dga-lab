
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class IngestRequest(BaseModel):
    batch_id: str
    domains: List[str]

class ScoreRequest(BaseModel):
    domain: str
    features: Optional[Dict[str, float]] = None

class ScoreResponse(BaseModel):
    domain: str
    label: str
    confidence: float
    features: Dict[str, float] = Field(default_factory=dict)

class MutateRequest(BaseModel):
    domain: str
    ops: List[str] = []

class MutateResponse(BaseModel):
    original: str
    mutated: List[str]

class EvalRequest(BaseModel):
    domain: str
    max_iters: int = 5
    target_conf: float = 0.25

class EvalResult(BaseModel):
    domain: str
    iters: int
    success: bool
    final_confidence: float
    final_label: str
    mutated: str
