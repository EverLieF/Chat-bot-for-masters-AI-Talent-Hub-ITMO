from __future__ import annotations
import os, time, httpx
from .config import settings

# Простой LRU-кэш в памяти (на сессию)
_CACHE: dict[tuple[str, tuple[str, ...]], str] = {}
_LAST_CALL_TS: float = 0.0
_MIN_INTERVAL = 1.5  # сек между запросами к Mistral (троттлинг)

def _mistral_chat(messages: list[dict], model: str | None = None, max_retries: int = 2) -> str:
    api_key = settings.MISTRAL_API_KEY
    if not api_key:
        return ""  # нет ключа — тихо выходим (fallback наверх)

    # Прокси через ENV (совместимо с разными версиями httpx)
    if settings.PROXY:
        os.environ["HTTP_PROXY"] = settings.PROXY
        os.environ["HTTPS_PROXY"] = settings.PROXY

    # Троттлинг
    global _LAST_CALL_TS
    now = time.time()
    if now - _LAST_CALL_TS < _MIN_INTERVAL:
        return ""

    model = model or settings.MISTRAL_MODEL
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": 0.2, "max_tokens": 400}

    for attempt in range(max_retries + 1):
        try:
            with httpx.Client(timeout=60) as client:
                r = client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            _LAST_CALL_TS = time.time()
            return data["choices"][0]["message"]["content"].strip()
        except httpx.HTTPStatusError as e:
            # Мягко обходим 429: подождать и ещё раз; иначе — fallback без LLM
            if e.response is not None and e.response.status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 1.5 * (attempt + 1)
                time.sleep(delay)
                continue
            return ""
        except Exception:
            return ""
    return ""

def summarize_answer(question: str, bullets: list[str]) -> str:
    # Вызываем Mistral только если включён и есть ключ
    if settings.LLM_PROVIDER != "mistral" or not settings.MISTRAL_API_KEY:
        return ""
    # Простейший кэш по (вопросу, топ-6 фактов)
    key = (question.strip(), tuple(bullets[:6]))
    if key in _CACHE:
        return _CACHE[key]
    content = (
        "Ты помощник для абитуриента. Сформируй короткий ответ на русском, опираясь ТОЛЬКО на перечисленные факты. "
        "Не добавляй новых данных. Сохраняй числа/ECTS/семестры. 2–4 предложения.\n\n"
        "Вопрос:\n" + question + "\n\nФакты:\n- " + "\n- ".join(bullets)
    )
    out = _mistral_chat(
        [{"role": "system", "content": "Ты точный и лаконичный ассистент."},
         {"role": "user", "content": content}],
        model=settings.MISTRAL_MODEL,
        max_retries=2,
    )
    if out:
        _CACHE[key] = out
    return out or ""
