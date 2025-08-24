from __future__ import annotations
from typing import Dict, List
from .retriever import is_relevant, retrieve
from ..core.llm import summarize_answer

DISCLAIMER = "Источник истины — учебные планы с abit.itmo.ru. Внешние данные требуют подтверждения по официальным планам."

def _fmt_citation(meta: Dict) -> str:
    program = meta.get("program")
    src = meta.get("source_ref", "")
    return f"Учебный план {program}, {src.replace(':', ', ')}"

def answer(query: str) -> str:
    if not is_relevant(query):
        return ("Я могу помогать только по магистерским программам ИТМО «Искусственный интеллект (AI)» "
                "и «Управление ИИ‑продуктами (AI Product)». Задайте, пожалуйста, релевантный вопрос.")
    items = retrieve(query)
    if not items:
        return "Не нашёл ответ в учебных планах. Уточните запрос."
    bullets = []
    for it in items[:6]:
        m = it["meta"]
        bullets.append(f"{m.get('name')} — {m.get('program')}, семестр {m.get('semester')}, {m.get('ects')} ECTS, "
                       f"{'обяз.' if m.get('type')=='required' else 'выбор.'}; модуль: {m.get('module')} "
                       f"([{_fmt_citation(m)}])")
    # Try Mistral to condense
    summary = summarize_answer(query, bullets)
    if summary:
        return summary + "\n\n" + "\n".join(f"• {b}" for b in bullets[:4]) + "\n\n" + DISCLAIMER
    # fallback: just bullets
    return "Подобрал релевантные дисциплины и нормы из планов:\n" + "\n".join(f"• {b}" for b in bullets[:4]) + "\n\n" + DISCLAIMER