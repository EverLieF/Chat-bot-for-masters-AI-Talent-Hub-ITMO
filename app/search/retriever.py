from __future__ import annotations
import pickle
from typing import List, Dict, Any

BM25_PATH = "artifacts/bm25.pkl"
TOP_K = 8

def is_relevant(query: str) -> bool:
    q = (query or "").lower()
    allow = any(x in q for x in [
        "итмо","магистр","магистратура","учебн","план","курс","дисциплин","семестр","ects","зет",
        "выборн","обязат","нир","практик","трек","ai product","искусствен","интеллект","ml","поступить","пререквиз"
    ])
    deny = any(x in q for x in ["погода","курс доллара","новости","политика","игры","кино"])
    return bool(allow and not deny)

def load_bm25():
    with open(BM25_PATH, "rb") as f:
        payload = pickle.load(f)
    return payload["bm25"], payload["docs"]

def retrieve(query: str) -> List[Dict[str, Any]]:
    bm25, docs = load_bm25()
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)[:TOP_K]
    return [{"text": d["text"], "meta": d["meta"], "score": float(s)} for d, s in ranked if s > 0]