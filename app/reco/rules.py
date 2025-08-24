from __future__ import annotations
from typing import Dict, List, Any

def recommend(plan: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    interests = [s.lower() for s in profile.get("interests", [])]
    background = profile.get("background", "").lower()
    semester = profile.get("semester", 1)
    courses = plan.get("courses", [])
    primary, secondary, stretch = [], [], []
    for c in courses:
        if c.get("type") != "elective": continue
        name = str(c.get("name","")).lower()
        ok = False
        if "nlp" in interests and ("язык" in name or "nlp" in name): ok = True
        if "cv" in interests and ("компьютер" in name or "vision" in name): ok = True
        if "recsys" in interests and ("рекомен" in name): ok = True
        if "безопас" in interests and ("security" in name or "безопас" in name): ok = True
        if "аналитик" in background and ("продукт" in name or "аналит" in name or "a/b" in name): ok = True
        if "инфраструкт" in background and ("mlops" in name or "инфра" in name or "платформ" in name): ok = True
        if ok:
            primary.append(c)
        else:
            (secondary if c.get("semester") in [semester, semester+1] else stretch).append(c)
    return {"primary": primary[:6], "secondary": secondary[:6], "stretch": stretch[:6]}