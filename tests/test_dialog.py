import json
from app.reco.rules import recommend

def test_recommender_buckets():
    plan = json.load(open("datasets/normalized/AI.sample.json", "r", encoding="utf-8"))
    prof = {"background":"инфраструктура", "level":"средний", "interests":["mlops"], "semester":1, "target_ects":30}
    recs = recommend(plan, prof)
    assert set(recs.keys()) == {"primary","secondary","stretch"}