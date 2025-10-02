
from fastapi import FastAPI
from common.schemas import ScoreRequest, ScoreResponse
import math

app = FastAPI(title="dga-detector")

def simple_score(domain: str, feats=None):
    if feats is None:
        # naive fallback features
        digits = sum(1 for c in domain if c.isdigit())
        uniq = len(set(domain))
        length = len(domain)
        entropy = len(set(domain))/max(1,length)
        v = sum(1 for c in domain if c in 'aeiou')
        c = sum(1 for c in domain if c.isalpha()) - v
        feats = {"len": length, "uniq": uniq, "digits": digits, "vcr": v/(c+1e-6), "entropy": entropy}
    # Heuristic: digits + high entropy + high uniq suggests DGA
    score = 0.0
    score += 0.2 * min(feats.get("digits",0), 5)
    score += 0.3 * min(feats.get("entropy",0), 4)
    score += 0.2 * min(feats.get("uniq",0)/max(1,feats.get("len",1)), 1.0)
    score = max(0.0, min(1.0, score))  # clamp
    label = "malicious" if score >= 0.5 else "benign"
    conf = score if label=="malicious" else 1.0-score
    return label, conf, feats

@app.post("/score", response_model=ScoreResponse)
def score(req: ScoreRequest):
    label, conf, feats = simple_score(req.domain, req.features)
    return ScoreResponse(domain=req.domain, label=label, confidence=round(conf,3), features=feats)
