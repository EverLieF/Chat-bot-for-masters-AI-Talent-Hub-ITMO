from __future__ import annotations
import os, asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
from ..search.answerer import answer
from ..search.utils import load_plans
from ..core.config import settings
from ..reco.rules import recommend

router = Router()
USER_PROFILES = {}

def get_plans():
    paths = ["datasets/normalized/AI.json", "datasets/normalized/AI_Product.json"]
    if not all(os.path.exists(p) for p in paths):
        paths = ["datasets/normalized/AI.sample.json", "datasets/normalized/AI_Product.sample.json"]
    return load_plans(paths)

@router.message(Command("start"))
async def cmd_start(m: Message):
    await m.answer("Привет! Я помогу выбрать между программами ИТМО: «Искусственный интеллект (AI)» и "
                   "«Управление ИИ‑продуктами (AI Product)», а также спланировать учебу.\n"
                   "Команды: /program, /compare, /plan, /electives, /help")

@router.message(Command("help"))
async def cmd_help(m: Message):
    await m.answer("Задавайте вопросы о программах AI и AI Product: курсы, семестры, ECTS, треки, поступление. "
                   "Нерелевантные вопросы я вежливо отклоняю.")

@router.message(Command("program"))
async def cmd_program(m: Message):
    await m.answer("Какая программа интересует? Ответьте: AI или AI Product.")

@router.message(Command("compare"))
async def cmd_compare(m: Message):
    await m.answer("AI — инженерия ML и исследования; AI Product — менеджмент AI‑продуктов и аналитика. "
                   "Спросите про конкретные модули — покажу ECTS и семестры с цитатами.")

@router.message(Command("plan"))
async def cmd_plan(m: Message):
    await m.answer("Примеры запросов: «Обязательные курсы 1 семестра AI», «Сколько ECTS по выборным в AI Product?»")

@router.message(Command("electives"))
async def cmd_electives(m: Message):
    USER_PROFILES.setdefault(m.from_user.id, {"background": "", "level": "средний", "interests": [], "semester": 1, "target_ects": 30})
    await m.answer("Опишите бэкграунд (математика/код/продукт/ML Ops), уровень (нач./ср./продв.) и интересы (NLP/CV/RecSys/безопасность).")

@router.message()
async def generic(m: Message):
    text = m.text or ""
    if any(k in text.lower() for k in ["интерес", "уров", "бэк", "опыт"]):
        prof = USER_PROFILES.setdefault(m.from_user.id, {"background": "", "level": "средний", "interests": [], "semester": 1, "target_ects": 30})
        if "нач" in text.lower(): prof["level"] = "начальный"
        if "ср" in text.lower(): prof["level"] = "средний"
        if "прод" in text.lower(): prof["level"] = "продвинутый"
        for key in ["nlp","cv","recsys","безопас"]:
            if key in text.lower() and key not in prof["interests"]:
                prof["interests"].append(key)
        if any(k in text.lower() for k in ["продукт", "аналит"]):
            prof["background"] = "продуктовая аналитика"
        if any(k in text.lower() for k in ["инфра", "mlops", "инженер"]):
            prof["background"] = "инфраструктура / MLOps"
        plans = get_plans()
        target = next((p for p in plans if p["program"] == ("AI Product" if prof["background"].startswith("продукт") else "AI")), plans[0])
        recs = recommend(target, prof)
        def fmt(lst):
            return "\n".join([f"• {c['name']} ({c['ects']} ECTS; {c['module']}). [{c['source_ref']}]" for c in lst]) or "—"
        await m.answer("Предложение выборных (primary/secondary/stretch):\n"
                       f"{fmt(recs['primary'])}\n\nАльтернативы:\n{fmt(recs['secondary'])}\n\nStretch:\n{fmt(recs['stretch'])}")
        return
    await m.answer(answer(text))

async def main():
    load_dotenv()
    token = settings.TELEGRAM_TOKEN
    if not token:
        print("Нет TELEGRAM_TOKEN — бот не запущен. Установите переменную окружения.")
        return
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())