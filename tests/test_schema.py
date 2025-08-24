from app.ingest.models import Plan
import json

def test_sample_schema():
    for path in ["datasets/normalized/AI.sample.json", "datasets/normalized/AI_Product.sample.json"]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        plan = Plan.model_validate(data)
        assert plan.rules.total_ects == 120
        assert sum(c.ects for c in plan.courses) > 0