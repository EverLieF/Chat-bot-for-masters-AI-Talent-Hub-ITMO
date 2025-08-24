from __future__ import annotations
import os, json, datetime, pathlib
from .fetch import get_official_plan_link, download, ABIT_PAGES
from .parse import parse_pdf_tables, parse_excel_tables, normalize_to_plan
from .models import Plan

def infer_version() -> str:
    y = datetime.datetime.now().year
    return f"{y}-{y+2}"

def scrape_program(program: str, out_dir: str = "datasets/normalized"):
    page_url = ABIT_PAGES[program]
    link = get_official_plan_link(program)
    if not link:
        raise RuntimeError(f"Не удалось найти ссылку 'Скачать учебный план' на {page_url}")
    path = download(link)
    rows = parse_excel_tables(path) if link.lower().endswith(('.xlsx','.xls')) else parse_pdf_tables(path)
    plan = normalize_to_plan(program=program, version=infer_version(), source_url=page_url, rows=rows)
    validated = Plan.model_validate(plan)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{'AI' if program=='AI' else 'AI_Product'}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(validated.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"OK: сохранено {out_path} ({len(validated.courses)} курсов)")
    return out_path

def main():
    for program in ["AI", "AI Product"]:
        try:
            scrape_program(program)
        except Exception as e:
            print(f"[WARN] {program}: {e} — используем sample JSON")
            sample = "datasets/normalized/AI.sample.json" if program=="AI" else "datasets/normalized/AI_Product.sample.json"
            target = "datasets/normalized/AI.json" if program=="AI" else "datasets/normalized/AI_Product.json"
            pathlib.Path(target).write_text(pathlib.Path(sample).read_text(encoding="utf-8"), encoding="utf-8")
            print(f"Копия {sample} → {target}")

if __name__ == "__main__":
    main()