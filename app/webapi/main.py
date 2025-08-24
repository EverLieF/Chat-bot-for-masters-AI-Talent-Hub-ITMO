from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel
from ..search.answerer import answer
from ..search.utils import load_plans
from ..reco.rules import recommend

app = FastAPI(title="ITMO Program Assistant API (Refactor)")

class AskReq(BaseModel):
    query: str

class Profile(BaseModel):
    background: str = ""
    level: str = "средний"
    interests: list[str] = []
    semester: int = 1
    target_ects: int = 30

@app.post("/ask")
def ask(req: AskReq):
    return {"answer": answer(req.query)}

@app.post("/recommend/{program}")
def rec(program: str, prof: Profile):
    program = "AI" if program.lower() in ["ai","искусственный интеллект"] else "AI Product"
    paths = ["datasets/normalized/AI.json", "datasets/normalized/AI_Product.json"]
    plans = load_plans(paths) or load_plans(["datasets/normalized/AI.sample.json", "datasets/normalized/AI_Product.sample.json"])
    plan = next((p for p in plans if p["program"] == program), plans[0])
    return recommend(plan, prof.model_dump())