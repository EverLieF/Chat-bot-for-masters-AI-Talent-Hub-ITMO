# ITMO Program Assistant — Refactor (Mistral)

Обновлённая структура, слегка переименованные модули и поддержка **Mistral** как LLM.

## Новая структура
```
app/
  core/        — конфиг и LLM (Mistral)
  ingest/      — загрузка/парсинг и нормализация учебных планов
  search/      — индексы BM25 и ответчик (RAG)
  reco/        — рекомендации выборных
  tgbot/       — Telegram-бот (aiogram)
  webapi/      — FastAPI API
datasets/
  raw/         — кэш исходников
  normalized/  — нормализованные JSON (есть *.sample.json)
artifacts/     — индексы/модели
docker/
tests/
```

## Быстрый старт (Windows / PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt

# В .env (или в переменные окружения) добавьте:
# LLM_PROVIDER=mistral
# MISTRAL_API_KEY=sk_...
# MISTRAL_MODEL=mistral-large-latest
# TELEGRAM_TOKEN=123456:ABC... (для бота)

python -m app.ingest
python -m app.search.index
python -m app.tgbot   # бот
# или API:
python -m app.webapi  # http://127.0.0.1:8000/docs
```

## Источники (истина)
- AI: https://abit.itmo.ru/program/master/ai
- AI Product: https://abit.itmo.ru/program/master/ai_product
- Якоря «Скачать учебный план» учтены в пайплайне.
Доп. источники (недоверенные до верификации) перечислены в первоначальном задании.

## Как работает Mistral
- Модуль `app/core/llm.py` вызывает **Mistral Chat Completions** (`/v1/chat/completions`), чтобы **сжать** найденные факты в короткий ответ **без добавления новых фактов**.
- Если `MISTRAL_API_KEY` не задан, ответ формируется без LLM (список фактов + цитаты).
- Ключевые переменные: `LLM_PROVIDER=mistral`, `MISTRAL_API_KEY`, `MISTRAL_MODEL`.

## Команды Makefile
```
make setup
make ingest   # скачать/нормализовать планы
make index    # построить BM25
make bot      # запустить Telegram-бота
make api      # запустить FastAPI
make test     # pytest
```

## Политика ответов
- Только вопросы по двум программам (AI / AI Product): учебные планы, дисциплины, ECTS, семестры, треки, поступление, проекты и т.п.
- Источник истины — официальные планы; внешние сведения помечаются как требующие подтверждения.

## Контест
https://contest.yandex.ru/contest/79334/enter

## Публичный репозиторий / Архив
- Заполните `REPO_LINK.txt` после загрузки на GitHub.