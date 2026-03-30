#!/usr/bin/env python3
"""
verify_cross_file.py — Кросс-файловая согласованность.
Извлекает числовые значения и ФИО из нескольких файлов и сверяет.
Обнаруживает как совпадения, так и расхождения между файлами.
"""

import argparse, json, re, sys
from pathlib import Path
from collections import defaultdict

# Зависимости (python-docx, openpyxl) импортируются лениво в extract-функциях


def extract_data_from_docx(filepath):
    """Извлечь числа и ФИО с контекстом из docx."""
    from docx import Document
    doc = Document(filepath)
    numbers = []
    names = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        # Числа с разделителями (123 456 789 или 123,456)
        # TODO [AUDIT-WARN-019]: Паттерн требует ≥2 цифры. Одноцифровые числа (напр. «5 человек») не находятся.
        for m in re.finditer(r'(\d[\d\s,.]+\d)', text):
            num_str = m.group(1).replace(" ", "").replace(",", ".")
            try:
                val = float(num_str)
                context = text[max(0, m.start()-30):m.end()+30].strip()
                numbers.append({"value": val, "text": m.group(1).strip(), "context": context})
            except ValueError:
                pass
        # ФИО (Фамилия И.О. или Фамилия Имя Отчество)
        for m in re.finditer(r'([А-ЯЁ][а-яё]+)\s+([А-ЯЁ])\.\s*([А-ЯЁ])\.', text):
            names.append({"name": m.group(0).strip(), "context": text[max(0, m.start()-20):m.end()+20].strip()})
        for m in re.finditer(r'([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)', text):
            names.append({"name": m.group(0).strip(), "context": text[max(0, m.start()-20):m.end()+20].strip()})
    return numbers, names


def extract_data_from_xlsx(filepath):
    """Извлечь числа и текст из xlsx."""
    import openpyxl
    wb = openpyxl.load_workbook(filepath, data_only=True)
    numbers = []
    names = []
    for ws in wb.worksheets:
        headers = {}
        for row_idx, row in enumerate(ws.iter_rows(values_only=False), 1):
            for cell in row:
                if row_idx == 1 and cell.value and isinstance(cell.value, str):
                    headers[cell.column] = cell.value
                if isinstance(cell.value, (int, float)) and cell.value != 0:
                    header = headers.get(cell.column, "")
                    context = f"{header}: {cell.value}" if header else str(cell.value)
                    numbers.append({
                        "value": cell.value,
                        "text": str(cell.value),
                        "context": f"{ws.title}!{cell.coordinate} ({context})",
                    })
                elif isinstance(cell.value, str):
                    for m in re.finditer(r'([А-ЯЁ][а-яё]+)\s+([А-ЯЁ])\.\s*([А-ЯЁ])\.', cell.value):
                        names.append({"name": m.group(0).strip(), "context": f"{ws.title}!{cell.coordinate}"})
                    for m in re.finditer(r'([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)', cell.value):
                        names.append({"name": m.group(0).strip(), "context": f"{ws.title}!{cell.coordinate}"})
    return numbers, names


def find_semantic_groups(all_data):
    """Найти семантически связанные числа по контексту."""
    groups = defaultdict(list)
    # Ключевые слова для группировки
    kw_patterns = [
        (r'штат|чел|сотрудник|человек|персонал', 'штат'),
        (r'бюджет|фот|оклад|зарплат|стоимост|сумм|руб', 'финансы'),
        (r'процент|доля|%|kpi|кпи', 'проценты'),
        (r'количеств|кол-во|число|шт', 'количество'),
    ]
    for fname, nums, _ in all_data:
        for n in nums:
            ctx_lower = n["context"].lower()
            for pattern, group_name in kw_patterns:
                if re.search(pattern, ctx_lower):
                    groups[group_name].append({"file": fname, **n})
                    break
    return groups


def verify(files):
    all_data = []
    for f in files:
        ext = Path(f).suffix.lower()
        if ext == ".docx":
            nums, names = extract_data_from_docx(f)
            all_data.append((f, nums, names))
        elif ext in (".xlsx", ".xls"):
            nums, names = extract_data_from_xlsx(f)
            all_data.append((f, nums, names))

    findings = []
    items_checked = 0

    # --- 1. Кросс-файловая сверка чисел по точному значению ---
    value_locations = defaultdict(list)
    for fname, nums, _ in all_data:
        for n in nums:
            value_locations[n["value"]].append({"file": fname, "context": n["context"], "text": n["text"]})

    cross_file_matches = {v: locs for v, locs in value_locations.items()
                          if len(set(l["file"] for l in locs)) > 1}
    items_checked += len(cross_file_matches)

    # --- 2. Семантическая группировка: одинаковый контекст, разные значения ---
    sem_groups = find_semantic_groups(all_data)
    for group_name, entries in sem_groups.items():
        # Проверяем: если одна семантическая группа, несколько файлов, разные значения
        files_in_group = set(e["file"] for e in entries)
        if len(files_in_group) < 2:
            continue
        items_checked += 1
        values_by_file = defaultdict(set)
        for e in entries:
            values_by_file[e["file"]].add(e["value"])
        # Находим значения, уникальные для каждого файла
        all_values = set()
        for vs in values_by_file.values():
            all_values.update(vs)
        for val in all_values:
            present_in = [f for f, vs in values_by_file.items() if val in vs]
            absent_in = [f for f, vs in values_by_file.items() if val not in vs]
            if present_in and absent_in and len(present_in) < len(values_by_file):
                # Значение есть в одних файлах, но не в других
                entry = next(e for e in entries if e["value"] == val)
                findings.append({
                    "severity": "warning",
                    "location": f"Группа «{group_name}», значение {val}",
                    "expected": f"одинаково во всех файлах",
                    "actual": f"есть в {', '.join(Path(f).name for f in present_in)}, нет в {', '.join(Path(f).name for f in absent_in)}",
                    "description": f"Возможное расхождение ({group_name}): {val} — контекст: «{entry['context']}»",
                })

    # --- 3. Кросс-файловая сверка ФИО ---
    all_names_by_file = defaultdict(set)
    for fname, _, names in all_data:
        for n in names:
            # Нормализуем: убираем пробелы, приводим к единому формату
            normalized = re.sub(r'\s+', ' ', n["name"]).strip()
            all_names_by_file[fname].add(normalized)

    if len(all_names_by_file) > 1:
        all_name_sets = list(all_names_by_file.items())
        for i in range(len(all_name_sets)):
            for j in range(i + 1, len(all_name_sets)):
                f1, names1 = all_name_sets[i]
                f2, names2 = all_name_sets[j]
                # ФИО в одном файле, но не в другом
                only_in_f1 = names1 - names2
                only_in_f2 = names2 - names1
                items_checked += len(names1 | names2)
                if only_in_f1 and names2:  # только если во втором файле вообще есть ФИО
                    for name in list(only_in_f1)[:5]:  # ограничиваем
                        findings.append({
                            "severity": "info",
                            "location": f"ФИО: {name}",
                            "expected": f"присутствует в обоих файлах",
                            "actual": f"только в {Path(f1).name}",
                            "description": f"ФИО «{name}» есть в {Path(f1).name}, но нет в {Path(f2).name}",
                        })

    items_warned = len([f for f in findings if f["severity"] == "warning"])
    items_failed = len([f for f in findings if f["severity"] == "error"])
    status = "fail" if items_failed > 0 else ("warn" if items_warned > 0 else "pass")

    return {
        "script": "verify_cross_file.py",
        "status": status,
        "details": f"Кросс-файловых проверок: {items_checked}. Совпадений: {len(cross_file_matches)}. Расхождений: {items_warned}. Файлов: {len(files)}",
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
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"🔄 Cross-file: {result['status']}")
