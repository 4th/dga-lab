
from fastapi import FastAPI
from common.schemas import MutateRequest, MutateResponse
app = FastAPI(title="mutator")

def apply_ops(domain: str, ops):
    muts = set()
    if not ops:
        # default: single char insert at pos 3 with 'x'
        pos = min(3, len(domain))
        muts.add(domain[:pos] + 'x' + domain[pos:])
    for op in ops:
        try:
            if op.startswith("insert:"):
                parts = op.split(":")
                pos = int(parts[1].split("=")[1])
                ch = parts[2].split("=")[1]
                pos = max(0, min(pos, len(domain)))
                muts.add(domain[:pos] + ch + domain[pos:])
            elif op.startswith("swap:"):
                # swap positions i and j
                parts = op.split(":")
                i = int(parts[1].split("=")[1])
                j = int(parts[2].split("=")[1])
                if 0 <= i < len(domain) and 0 <= j < len(domain):
                    lst = list(domain)
                    lst[i], lst[j] = lst[j], lst[i]
                    muts.add("".join(lst))
        except Exception:
            continue
    return list(muts)

@app.post("/mutate", response_model=MutateResponse)
def mutate(req: MutateRequest):
    mutated = apply_ops(req.domain, req.ops or [])
    return MutateResponse(original=req.domain, mutated=mutated)
