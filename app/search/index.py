from __future__ import annotations
import os, pickle
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from .utils import load_plans, chunk_courses

DATA_PATHS = ["datasets/normalized/AI.json", "datasets/normalized/AI_Product.json"]
BM25_PATH = "artifacts/bm25.pkl"

def build_bm25(docs: List[Dict[str, Any]]):
    corpus = [d["text"] for d in docs]
    tokenized = [t.lower().split() for t in corpus]
    bm25 = BM25Okapi(tokenized)
    os.makedirs("artifacts", exist_ok=True)
    with open(BM25_PATH, "wb") as f:
        pickle.dump({"bm25": bm25, "docs": docs}, f)
    print(f"OK: BM25 индекс построен ({len(docs)} документов) → {BM25_PATH}")

def main():
    plans = load_plans(DATA_PATHS)
    docs = []
    for p in plans:
        docs += chunk_courses(p)
    if not docs:
        plans = load_plans(["datasets/normalized/AI.sample.json", "datasets/normalized/AI_Product.sample.json"])
        for p in plans:
            docs += chunk_courses(p)
    build_bm25(docs)

if __name__ == "__main__":
    main()