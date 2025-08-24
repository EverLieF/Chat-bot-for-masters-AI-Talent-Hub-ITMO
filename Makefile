.PHONY: setup ingest index bot api test

setup:
	python -m venv .venv && . .venv/Scripts/activate || . .venv/bin/activate; pip install -U pip && pip install -r requirements.txt

ingest:
	python -m app.ingest

index:
	python -m app.search.index

bot:
	python -m app.tgbot

api:
	python -m app.webapi

test:
	pytest -q