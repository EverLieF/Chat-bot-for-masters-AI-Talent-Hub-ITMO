from __future__ import annotations
import os

from dotenv import load_dotenv

load_dotenv()

class Settings:
    TELEGRAM_TOKEN: str | None = os.environ.get("TELEGRAM_TOKEN")
    PROXY: str | None = os.environ.get("PROXY")

    # LLM
    LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "mistral")
    MISTRAL_API_KEY: str | None = os.environ.get("MISTRAL_API_KEY")
    MISTRAL_MODEL: str = os.environ.get("MISTRAL_MODEL", "mistral-large-latest")

settings = Settings()