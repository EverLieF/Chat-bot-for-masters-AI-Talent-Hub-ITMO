import os, shutil
from app.search.index import main as build_index
from app.search.answerer import answer

def setup_module(module):
    os.makedirs("datasets/normalized", exist_ok=True)
    for src, dst in [
        ("datasets/normalized/AI.sample.json", "datasets/normalized/AI.json"),
        ("datasets/normalized/AI_Product.sample.json", "datasets/normalized/AI_Product.json"),
    ]:
        shutil.copyfile(src, dst)
    build_index()

def test_answer_contains_citation():
    out = answer("Какие выборные дисциплины по AI?")
    assert "Учебный план" in out or "Источник истины" in out