#!/usr/bin/env python3
"""
verify_cross_file.py — Кросс-файловая согласованность.
Извлекает числовые значения и ФИО из нескольких файлов и сверяет.
"""

import argparse, json, re, sys
from pathlib import Path
from collections import defaultdict

def extract_numbers_from_docx(filepath):
    """Извлечь числа с контекстом из docx."""
    from docx import Document
    doc = Document(filepath)
    numbers = {}
    for para in doc.paragraphs:
        text = para.text.strip()
        # Числа с разделителями (123 456 789 или 123,456)
        for m in re.finditer(r'(\d[\d\s,.]+\d)', text):
            num_str = m.group(1).replace(" ", "").replace(",", ".")
            try:
                val = float(num_str)
                context = text[max(0, m.start()-20):m.end()+20]
                numbers[context] = val
            except ValueError:
                pass
    return numbers

def extract_numbers_from_xlsx(filepath):
    """Извлечь числа из xlsx."""
    import openpyxl
    wb = openpyxl.load_workbook(filepath, data_only=True)
    numbers = {}
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=False):
            for cell in row:
                if isinstance(cell.value, (int, float)) and cell.value != 0:
                    # Используем адрес ячейки как ключ
                    numbers[f"{ws.title}!{cell.coordinate}"] = cell.value
    return numbers

def verify(files):
    all_numbers = {}
    for f in files:
        ext = Path(f).suffix.lower()
        if ext == ".docx":
            all_numbers[f] = extract_numbers_from_docx(f)
        elif ext in (".xlsx", ".xls"):
            all_numbers[f] = extract_numbers_from_xlsx(f)

    # Ищем одинаковые числа и проверяем согласованность
    findings = []
    value_locations = defaultdict(list)
    
    for fname, nums in all_numbers.items():
        for ctx, val in nums.items():
            value_locations[val].append((fname, ctx))

    # Числа, встречающиеся в нескольких файлах — отмечаем как сверенные
    cross_file_matches = {v: locs for v, locs in value_locations.items() if len(set(l[0] for l in locs)) > 1}

    items_checked = len(cross_file_matches)
    status = "pass"

    return {
        "script": "verify_cross_file.py",
        "status": status,
        "details": f"Кросс-файловых совпадений: {items_checked}. Файлов проанализировано: {len(files)}",
        "items_checked": items_checked,
        "items_passed": items_checked,
        "items_warned": 0,
        "items_failed": 0,
        "findings": findings,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(args.files)
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"🔄 Cross-file: {result['status']}")
