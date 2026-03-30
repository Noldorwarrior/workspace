#!/usr/bin/env python3
"""
verify_regression.py — Автоматическая проверка регрессий.
Сравнивает текущий документ с предыдущим отчётом верификации:
если ранее найденные и исправленные проблемы вернулись — это регрессия.

Использование:
    python verify_regression.py --current doc_v2.docx --previous-report prev_verification.json
    python verify_regression.py --json --current doc_v2.docx --previous-report prev_verification.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import openpyxl
except ImportError:
    openpyxl = None


def extract_text(filepath):
    """Извлечь текст из файла для поиска регрессий."""
    ext = Path(filepath).suffix.lower()
    if ext == ".docx" and Document:
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs)
    elif ext in (".xlsx", ".xls") and openpyxl:
        wb = openpyxl.load_workbook(filepath, data_only=True, read_only=True)
        lines = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                lines.append(" ".join(str(c) for c in row if c))
        wb.close()
        return "\n".join(lines)
    elif ext in (".txt", ".md", ".csv"):
        return Path(filepath).read_text(encoding="utf-8")
    return ""


def load_previous_findings(report_path):
    """Загрузить findings из предыдущего отчёта верификации."""
    data = json.loads(Path(report_path).read_text(encoding="utf-8"))
    findings = []
    for check in data.get("checks", []):
        for f in check.get("findings", []):
            if f.get("severity") in ("error", "warning"):
                findings.append(f)
    return findings


def check_regression(current_text, previous_findings):
    """Проверить, вернулись ли ранее найденные проблемы."""
    regressions = []
    checked = 0

    for prev in previous_findings:
        checked += 1
        location = prev.get("location", "")
        description = prev.get("description", "")
        expected = prev.get("expected", "")
        actual = prev.get("actual", "")

        # Извлекаем ключевые числа и слова из previous finding
        regression_found = False
        reason = ""

        # Проверка 1: если actual-значение (ошибочное) всё ещё в тексте
        if actual and actual not in ("—", "не найдено", "существует"):
            # Ищем числовое значение
            numbers = re.findall(r'[\d.,]+', actual)
            for num in numbers:
                clean_num = num.replace(",", ".").rstrip(".")
                if clean_num and len(clean_num) >= 2:
                    # Ищем это число в текущем тексте
                    if clean_num in current_text.replace(" ", ""):
                        # Проверяем, не совпадает ли с expected (тогда это не регрессия)
                        expected_nums = re.findall(r'[\d.,]+', expected) if expected else []
                        expected_clean = [n.replace(",", ".").rstrip(".") for n in expected_nums]
                        if clean_num not in expected_clean:
                            regression_found = True
                            reason = f"Ошибочное значение «{actual}» всё ещё присутствует в документе"
                            break

        # Проверка 2: битые ссылки — если ссылка была битой, проверяем что цель появилась
        if "Битая ссылка" in description or "не найден" in description:
            # Извлекаем имя цели из location (напр. "Таблица 3", "Приложение В")
            target = location.strip()
            if target and target.lower() not in current_text.lower():
                regression_found = True
                reason = f"Цель «{target}» по-прежнему отсутствует"

        # Проверка 3: нумерация — дубликаты и пропуски
        if "Дубликат" in description or "Пропуск" in description:
            # Проверяем, не вернулась ли та же проблема
            obj_match = re.search(r'(Таблица|Рисунок|Приложение|Схема|График)\s+(\d+)', location)
            if obj_match:
                obj_type, obj_num = obj_match.group(1), obj_match.group(2)
                pattern = rf'{obj_type}\s+{obj_num}'
                matches = re.findall(pattern, current_text, re.IGNORECASE)
                if "Дубликат" in description and len(matches) > 1:
                    regression_found = True
                    reason = f"Дубликат {obj_type} {obj_num} вернулся"

        if regression_found:
            regressions.append({
                "severity": "error",
                "location": location,
                "expected": f"Исправлено (было: {prev.get('severity', '?')})",
                "actual": "Регрессия",
                "description": f"Регрессия: {reason}. Оригинальная проблема: {description[:150]}",
            })

    return regressions, checked


def verify(current_file, previous_report):
    """Главная функция верификации регрессий."""
    if not Path(current_file).exists():
        return {
            "script": "verify_regression.py",
            "status": "error",
            "details": f"Файл не найден: {current_file}",
            "items_checked": 0, "items_passed": 0,
            "items_warned": 0, "items_failed": 0,
            "findings": [],
        }

    if not Path(previous_report).exists():
        return {
            "script": "verify_regression.py",
            "status": "skip",
            "details": "Предыдущий отчёт не найден (первая итерация?)",
            "items_checked": 0, "items_passed": 0,
            "items_warned": 0, "items_failed": 0,
            "findings": [],
        }

    current_text = extract_text(current_file)
    previous_findings = load_previous_findings(previous_report)

    if not previous_findings:
        return {
            "script": "verify_regression.py",
            "status": "pass",
            "details": "Предыдущих проблем не было — регрессий быть не может",
            "items_checked": 0, "items_passed": 0,
            "items_warned": 0, "items_failed": 0,
            "findings": [],
        }

    regressions, checked = check_regression(current_text, previous_findings)

    items_failed = len(regressions)
    status = "fail" if items_failed > 0 else "pass"

    return {
        "script": "verify_regression.py",
        "status": status,
        "details": f"Проверено предыдущих проблем: {checked}, регрессий: {items_failed}",
        "items_checked": checked,
        "items_passed": checked - items_failed,
        "items_warned": 0,
        "items_failed": items_failed,
        "findings": regressions,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", required=True, help="Текущий файл для проверки")
    parser.add_argument("--previous-report", required=True, help="JSON-отчёт предыдущей верификации")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = verify(args.current, args.previous_report)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"🔄 Регрессия: {result['status']} ({result['items_failed']} регрессий из {result['items_checked']} проверок)")
        for f in result["findings"]:
            print(f"  ❌ {f['location']}: {f['description']}")
