#!/usr/bin/env python3
"""
verify_dates.py — Валидация дат, хронологии, реалистичности интервалов.
"""

import argparse, json, re, sys
from datetime import datetime, timedelta
from pathlib import Path

MONTH_MAP = {"января":1,"февраля":2,"марта":3,"апреля":4,"мая":5,"июня":6,
             "июля":7,"августа":8,"сентября":9,"октября":10,"ноября":11,"декабря":12}

DATE_PATTERNS = [
    (r'(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})', 'dmy_text'),
    (r'(\d{1,2})\.(\d{1,2})\.(\d{4})', 'dmy_dots'),
    (r'(\d{4})-(\d{2})-(\d{2})', 'ymd_iso'),
]

def extract_dates(text: str) -> list[dict]:
    dates = []
    for pattern, fmt in DATE_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            try:
                if fmt == 'dmy_text':
                    d = datetime(int(m.group(3)), MONTH_MAP[m.group(2).lower()], int(m.group(1)))
                elif fmt == 'dmy_dots':
                    d = datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
                elif fmt == 'ymd_iso':
                    d = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                context = text[max(0, m.start()-30):m.end()+30]
                dates.append({"date": d, "text": m.group(0), "context": context.strip()})
            except (ValueError, KeyError):
                pass
    return dates

def verify(files: list[str]) -> dict:
    findings = []
    all_dates = []
    
    for f in files:
        ext = Path(f).suffix.lower()
        text = ""
        if ext == ".docx":
            from docx import Document
            doc = Document(f)
            text = "\n".join(p.text for p in doc.paragraphs)
        elif ext in (".xlsx", ".xls"):
            import openpyxl
            wb = openpyxl.load_workbook(f, data_only=True)
            for ws in wb.worksheets:
                for row in ws.iter_rows(values_only=True):
                    for c in row:
                        if c is None:
                            continue
                        # Обработка datetime-объектов из openpyxl напрямую
                        if isinstance(c, datetime):
                            all_dates.append({"date": c, "text": c.strftime("%d.%m.%Y"), "context": f"{f}: ячейка", "file": f})
                        else:
                            text += str(c) + " "
                    text += "\n"
        
        file_dates = extract_dates(text)
        for d in file_dates:
            d["file"] = f
        all_dates.extend(file_dates)

    # Проверка 1: даты в будущем (если контекст не прогнозный)
    now = datetime.now()
    future_years = [str(now.year + i) for i in range(0, 5)]
    prognosis_kw = ["план", "прогноз", "ожида", "целев", "будет"] + future_years
    for d in all_dates:
        if d["date"] > now:
            if not any(kw in d["context"].lower() for kw in prognosis_kw):
                findings.append({
                    "severity": "warning",
                    "location": f"{d['file']}: {d['text']}",
                    "expected": f"<= {now.strftime('%d.%m.%Y')}",
                    "actual": d["text"],
                    "description": f"Дата в будущем без прогнозного контекста: {d['text']}",
                })

    # Проверка 2: нереалистичные даты
    for d in all_dates:
        max_year = now.year + 10
        if d["date"].year < 1990 or d["date"].year > max_year:
            findings.append({
                "severity": "warning",
                "location": f"{d['file']}: {d['text']}",
                "expected": f"1990–{max_year}",
                "actual": d["text"],
                "description": f"Подозрительный год: {d['date'].year}",
            })

    items_checked = len(all_dates)
    items_warned = len([f for f in findings if f["severity"] == "warning"])
    items_failed = len([f for f in findings if f["severity"] == "error"])
    status = "fail" if items_failed > 0 else ("warn" if items_warned > 0 else "pass")

    return {
        "script": "verify_dates.py",
        "status": status,
        "details": f"Дат найдено: {items_checked}, подозрительных: {items_warned + items_failed}",
        "items_checked": items_checked,
        "items_passed": items_checked - items_warned - items_failed,
        "items_warned": items_warned,
        "items_failed": items_failed,
        "findings": findings,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(args.files)
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"📅 Dates: {result['status']}")
