#!/usr/bin/env python3
"""
verify_numbering.py — Проверка последовательности нумерации таблиц, рисунков, приложений.
"""

import argparse, json, re, sys

try:
    from docx import Document
except ImportError:
    print("pip install python-docx --break-system-packages", file=sys.stderr)
    sys.exit(1)

NUMBERED_OBJECTS = {
    "Таблица": r"Таблица\s+(\d+)",
    "Рисунок": r"Рисунок\s+(\d+)",
    "Диаграмма": r"Диаграмма\s+(\d+)",
    "Приложение": r"Приложение\s+([А-ЯA-Z])",
    "Схема": r"Схема\s+(\d+)",
    "График": r"График\s+(\d+)",
}

def verify(filepath):
    doc = Document(filepath)
    full_text = "\n".join(p.text for p in doc.paragraphs)
    findings = []
    items_checked = 0

    for obj_type, pattern in NUMBERED_OBJECTS.items():
        numbers = [m.group(1) for m in re.finditer(pattern, full_text, re.IGNORECASE)]
        if not numbers:
            continue
        items_checked += len(numbers)

        # Для цифровых — проверяем последовательность
        if numbers[0].isdigit():
            nums = [int(n) for n in numbers]
            # Дубликаты
            seen = set()
            for n in nums:
                if n in seen:
                    findings.append({
                        "severity": "warning",
                        "location": f"{obj_type} {n}",
                        "expected": "уникальный номер",
                        "actual": f"дубликат",
                        "description": f"Дубликат: {obj_type} {n} встречается несколько раз",
                    })
                seen.add(n)
            # Пропуски
            if nums:
                expected_seq = list(range(1, max(nums) + 1))
                missing = set(expected_seq) - set(nums)
                for m in sorted(missing):
                    findings.append({
                        "severity": "warning",
                        "location": f"{obj_type} {m}",
                        "expected": "присутствует",
                        "actual": "пропущен",
                        "description": f"Пропуск в нумерации: {obj_type} {m} отсутствует (есть {min(nums)}–{max(nums)})",
                    })

    items_warned = len(findings)
    status = "warn" if items_warned > 0 else "pass"
    return {
        "script": "verify_numbering.py",
        "status": status,
        "details": f"Объектов: {items_checked}, проблем нумерации: {items_warned}",
        "items_checked": items_checked,
        "items_passed": items_checked - items_warned,
        "items_warned": items_warned,
        "items_failed": 0,
        "findings": findings,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    for f in args.files:
        if f.endswith(".docx"):
            result = verify(f)
            print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"🔢 {f}: {result['status']}")
