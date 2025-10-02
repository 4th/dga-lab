
from fastapi import FastAPI
from pydantic import BaseModel
from common.schemas import ScoreRequest
import math

app = FastAPI(title="feature-extractor")

def domain_features(d: str):
    v = sum(1 for c in d if c in 'aeiou')
    c = sum(1 for c in d if c.isalpha()) - v
    length = len(d)
    uniq = len(set(d))
    digits = sum(1 for c in d if c.isdigit())
    entropy = 0.0
    from collections import Counter
    counts = Counter(d)
    for k,n in counts.items():
        p = n/length
        entropy += -(p*math.log2(p))
    return {"len": length, "uniq": uniq, "digits": digits, "vcr": (v/(c+1e-6)), "entropy": entropy}

@app.post("/features")
def features(req: ScoreRequest):
    f = domain_features(req.domain)
    return {"domain": req.domain, "features": f}
