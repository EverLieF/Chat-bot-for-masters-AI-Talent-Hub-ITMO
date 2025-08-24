import os, json
from typing import List, Dict, Any

def load_plans(paths: List[str]) -> List[Dict[str, Any]]:
    plans = []
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                plans.append(json.load(f))
    return plans

def course_to_text(course: Dict[str, Any], program: str) -> str:
    fields = [
        f"Программа: {program}",
        f"Курс: {course.get('name')}",
        f"Код: {course.get('code')}",
        f"Семестр: {course.get('semester')}",
        f"ECTS: {course.get('ects')}",
        f"Тип: {'обязательный' if course.get('type')=='required' else 'выборный'}",
        f"Модуль: {course.get('module')}",
        f"Пререквизиты: {', '.join(course.get('prerequisites', [])) or '—'}",
        f"Источник: {course.get('source_ref')}",
    ]
    return "\n".join(fields)

def chunk_courses(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    chunks = []
    for c in plan.get("courses", []):
        text = course_to_text(c, plan.get("program"))
        chunks.append({"id": f"{plan['program']}::{c['code']}", "text": text, "meta": {"program": plan['program'], **c}})
    return chunks