import re
from typing import List, Dict, Any
import pdfplumber
import pandas as pd

COLUMN_MAP = {
    "дисциплина": "name",
    "наименование дисциплины": "name",
    "семестр": "semester",
    "зет": "ects",
    "з.е.": "ects",
    "ects": "ects",
    "кредиты": "ects",
    "модуль": "module",
    "тип": "type",
    "обяз": "type",
    "выбор": "type",
    "код": "code",
    "пререквизиты": "prerequisites",
    "примечания": "notes",
}

def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")

def _norm_header(name: str) -> str:
    s = name.strip().lower()
    for k, v in COLUMN_MAP.items():
        if k in s:
            return v
    return _slugify(s)

def _norm_type(val: str) -> str:
    s = str(val).strip().lower()
    if s.startswith("обяз"):
        return "required"
    if s.startswith("выбор"):
        return "elective"
    return "elective"

def parse_pdf_tables(path: str) -> List[Dict[str, Any]]:
    rows = []
    with pdfplumber.open(path) as pdf:
        for pageno, page in enumerate(pdf.pages, start=1):
            try:
                tables = page.extract_tables()
            except Exception:
                tables = []
            for tbl in tables or []:
                if not tbl or len(tbl) < 2:
                    continue
                header = [_norm_header(str(h or "")) for h in tbl[0]]
                for ridx, raw in enumerate(tbl[1:], start=1):
                    row = {header[i] if i < len(header) else f"col{i}": raw[i] for i in range(min(len(header), len(raw)))}
                    if "name" in row and (row.get("ects") or row.get("semester")):
                        if "type" in row:
                            row["type"] = _norm_type(row["type"])
                        if "ects" in row:
                            try:
                                row["ects"] = float(str(row["ects"]).replace(",", ".").strip())
                            except Exception:
                                continue
                        if "semester" in row:
                            try:
                                row["semester"] = int(str(row["semester"]).split()[0])
                            except Exception:
                                continue
                        if "prerequisites" in row and isinstance(row["prerequisites"], str):
                            row["prerequisites"] = [p.strip() for p in re.split(r"[;,]", row["prerequisites"]) if p.strip()]
                        row["source_ref"] = f"pdf:page={pageno},row={ridx+1}"
                        rows.append(row)
    return rows

def parse_excel_tables(path: str) -> List[Dict[str, Any]]:
    rows = []
    xls = pd.ExcelFile(path)
    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        if df.empty:
            continue
        df.columns = [_norm_header(str(c)) for c in df.columns]
        keep = [c for c in ["name","semester","ects","type","module","code","prerequisites","notes"] if c in df.columns]
        if not keep or "name" not in keep:
            continue
        sub = df[keep].copy()
        sub = sub[sub["name"].notna()]
        for _, r in sub.iterrows():
            row = {k: (r[k] if pd.notna(r[k]) else "") for k in keep}
            if "type" in row:
                row["type"] = _norm_type(row["type"])
            if "ects" in row and row["ects"] != "":
                try:
                    row["ects"] = float(str(row["ects"]).replace(",", ".").strip())
                except Exception:
                    continue
            if "semester" in row and row["semester"] != "":
                try:
                    row["semester"] = int(str(int(row["semester"])))
                except Exception:
                    continue
            if "prerequisites" in row and isinstance(row["prerequisites"], str):
                row["prerequisites"] = [p.strip() for p in re.split(r"[;,]", row["prerequisites"]) if p.strip()]
            row["source_ref"] = f"xlsx:sheet={sheet}"
            rows.append(row)
    return rows

def normalize_to_plan(program: str, version: str, source_url: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    courses = []
    for i, r in enumerate(rows, start=1):
        courses.append({
            "code": str(r.get("code") or f"{program[:3].upper()}{i:03d}"),
            "name": str(r.get("name") or "").strip(),
            "semester": int(r.get("semester") or 0),
            "ects": float(r.get("ects") or 0.0),
            "type": r.get("type") or "elective",
            "module": str(r.get("module") or ""),
            "prerequisites": r.get("prerequisites") or [],
            "notes": r.get("notes") or "",
            "source_ref": r.get("source_ref") or "",
        })
    rules = {"total_ects": 120, "min_electives_ects": 24,
             "per_semester_constraints": {str(s): {"min":24,"max":36} for s in range(1,5)}}
    return {"program": program, "version": version, "source_url": source_url, "courses": courses, "rules": rules}