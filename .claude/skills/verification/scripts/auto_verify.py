#!/usr/bin/env python3
"""
auto_verify.py — Главный оркестратор верификации.
Определяет тип файлов, запускает нужные проверки, собирает результаты.

Использование:
    python auto_verify.py --files doc.docx data.xlsx
    python auto_verify.py --files doc.docx --preset П1 --scripts format,sums,references
    python auto_verify.py --files presentation.pptx page.html --scripts pptx_format,pptx_html_sync
    python auto_verify.py --files doc.docx --all  # все применимые скрипты
"""

import argparse
import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# Реестр скриптов и их применимость
SCRIPT_REGISTRY = {
    "format": {
        "module": "verify_docx_format",
        "applies_to": [".docx"],
        "description": "Проверка формата docx по стандарту #6",
    },
    "sums": {
        "module": "verify_sums",
        "applies_to": [".xlsx", ".xls"],
        "description": "Сверка сумм и проверка границ в xlsx",
    },
    "references": {
        "module": "verify_references",
        "applies_to": [".docx"],
        "description": "Поиск битых внутренних ссылок в docx",
    },
    "cross_file": {
        "module": "verify_cross_file",
        "applies_to": ["*"],  # любая комбинация 2+ файлов
        "description": "Кросс-файловая согласованность",
        "min_files": 2,
    },
    "numbering": {
        "module": "verify_numbering",
        "applies_to": [".docx"],
        "description": "Проверка нумерации таблиц/диаграмм/приложений",
    },
    "dates": {
        "module": "verify_dates",
        "applies_to": [".docx", ".xlsx"],
        "description": "Валидация дат и хронологии",
    },
    "pptx_format": {
        "module": "verify_pptx_format",
        "applies_to": [".pptx"],
        "description": "Проверка формата слайдов (16:9, шрифты)",
    },
    "pptx_html_sync": {
        "module": "verify_pptx_html_sync",
        "applies_to": [".pptx", ".html"],
        "description": "Согласованность pptx и html версий",
        "min_files": 2,
        "requires_ext": [".pptx", ".html"],
    },
    "diff": {
        "module": "diff_versions",
        "applies_to": ["*"],
        "description": "Diff между версиями файлов",
        "min_files": 2,
    },
    "regression": {
        "module": "verify_regression",
        "applies_to": ["*"],
        "description": "Проверка регрессий по предыдущему отчёту",
        "min_files": 1,
    },
}

# Пресеты → скрипты
PRESET_SCRIPTS = {
    "М1": [],
    "М2": ["format", "sums"],
    "М3": ["format", "sums", "dates"],
    "М4": ["pptx_format", "pptx_html_sync", "cross_file"],
    "М5": [],
    "П1": ["format", "references"],
    "П2": ["dates"],
    "П3": ["sums", "cross_file", "references"],
    "П4": ["format", "references", "diff"],
    "П5": list(SCRIPT_REGISTRY.keys()),  # все
    "П6": ["cross_file"],
    "П7": ["dates", "references"],
    "П8": ["cross_file", "dates", "numbering"],
    "П9": [],
    "П10": ["format", "references", "numbering"],
    "П11": ["format"],
    "П12": ["references"],
    "П13": ["sums", "references", "dates"],
    "П14": ["diff", "format", "regression"],
}


def detect_applicable_scripts(files: list[str]) -> list[str]:
    """Определить применимые скрипты на основе расширений файлов."""
    extensions = {Path(f).suffix.lower() for f in files}
    applicable = []

    for name, info in SCRIPT_REGISTRY.items():
        # Проверка минимального количества файлов
        min_files = info.get("min_files", 1)
        if len(files) < min_files:
            continue

        # Проверка требуемых расширений
        required = info.get("requires_ext")
        if required and not all(ext in extensions for ext in required):
            continue

        # Проверка применимости
        if "*" in info["applies_to"]:
            applicable.append(name)
        elif any(ext in info["applies_to"] for ext in extensions):
            applicable.append(name)

    return applicable


def run_script(script_name: str, files: list[str]) -> dict:
    """Запустить отдельный скрипт верификации и вернуть результат в стандартном формате."""
    info = SCRIPT_REGISTRY[script_name]
    module_name = info["module"]
    script_path = SCRIPT_DIR / f"{module_name}.py"

    if not script_path.exists():
        return {
            "script": f"{module_name}.py",
            "status": "skip",
            "details": f"Скрипт {script_path} не найден",
            "items_checked": 0,
            "items_passed": 0,
            "items_warned": 0,
            "items_failed": 0,
            "findings": [],
        }

    try:
        # Фильтруем файлы по расширению (если не wildcard)
        if "*" not in info["applies_to"]:
            target_files = [
                f for f in files if Path(f).suffix.lower() in info["applies_to"]
            ]
        else:
            target_files = files

        if not target_files:
            return {
                "script": f"{module_name}.py",
                "status": "skip",
                "details": "Нет подходящих файлов",
                "items_checked": 0,
                "items_passed": 0,
                "items_warned": 0,
                "items_failed": 0,
                "findings": [],
            }

        # Запускаем скрипт как subprocess для изоляции
        cmd = [sys.executable, str(script_path), "--json"] + target_files
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        elif result.returncode == 0:
            return {
                "script": f"{module_name}.py",
                "status": "pass",
                "details": "Скрипт завершился успешно, но не вернул JSON",
                "items_checked": 0,
                "items_passed": 0,
                "items_warned": 0,
                "items_failed": 0,
                "findings": [],
            }
        else:
            return {
                "script": f"{module_name}.py",
                "status": "error",
                "details": result.stderr or f"Скрипт завершился с кодом {result.returncode}",
                "items_checked": 0,
                "items_passed": 0,
                "items_warned": 0,
                "items_failed": 0,
                "findings": [],
            }

    except subprocess.TimeoutExpired:
        return {
            "script": f"{module_name}.py",
            "status": "error",
            "details": "Таймаут (>60 сек)",
            "items_checked": 0,
            "items_passed": 0,
            "items_warned": 0,
            "items_failed": 0,
            "findings": [],
        }
    except Exception as e:
        return {
            "script": f"{module_name}.py",
            "status": "error",
            "details": str(e),
            "items_checked": 0,
            "items_passed": 0,
            "items_warned": 0,
            "items_failed": 0,
            "findings": [],
        }


def main():
    parser = argparse.ArgumentParser(description="Оркестратор верификации")
    parser.add_argument("--files", nargs="+", required=True, help="Файлы для проверки")
    parser.add_argument("--preset", default=None, help="Пресет (М1-М5, П1-П14)")
    parser.add_argument(
        "--scripts",
        default=None,
        help="Список скриптов через запятую (format,sums,...)",
    )
    parser.add_argument("--all", action="store_true", help="Все применимые скрипты")
    parser.add_argument(
        "--output", default=None, help="Файл для JSON-отчёта"
    )
    parser.add_argument(
        "--report-format", choices=["json", "md"], default="json",
        help="Формат отчёта"
    )

    args = parser.parse_args()

    # Проверяем существование файлов
    for f in args.files:
        if not os.path.exists(f):
            print(f"❌ Файл не найден: {f}", file=sys.stderr)
            sys.exit(1)

    # Определяем набор скриптов
    if args.scripts:
        scripts_to_run = [s.strip() for s in args.scripts.split(",")]
    elif args.preset and args.preset in PRESET_SCRIPTS:
        scripts_to_run = PRESET_SCRIPTS[args.preset]
    elif args.all:
        scripts_to_run = detect_applicable_scripts(args.files)
    else:
        scripts_to_run = detect_applicable_scripts(args.files)

    # Убираем неприменимые
    applicable = detect_applicable_scripts(args.files)
    skipped = [s for s in scripts_to_run if s not in applicable]
    scripts_to_run = [s for s in scripts_to_run if s in applicable]

    # Запускаем
    report = {
        "timestamp": datetime.now().isoformat(),
        "files_checked": args.files,
        "preset": args.preset,
        "scripts_requested": scripts_to_run,
        "scripts_skipped": skipped,
        "checks": [],
    }

    print(f"📋 Верификация: {len(scripts_to_run)} скриптов для {len(args.files)} файлов")
    print(f"   Файлы: {', '.join(args.files)}")
    print(f"   Скрипты: {', '.join(scripts_to_run)}")
    if skipped:
        print(f"   Пропущены (не применимы): {', '.join(skipped)}")
    print()

    for script_name in scripts_to_run:
        info = SCRIPT_REGISTRY[script_name]
        print(f"   ▶ {info['description']}...", end=" ", flush=True)
        result = run_script(script_name, args.files)
        report["checks"].append(result)

        status = result.get("status", "unknown")
        if status == "pass":
            print("✅")
        elif status == "warn":
            print(f"⚠️ ({result.get('items_warned', 0)} замечаний)")
        elif status == "fail":
            print(f"❌ ({result.get('items_failed', 0)} ошибок)")
        elif status == "skip":
            print("⏭️ пропущено")
        elif status == "info":
            print("ℹ️")
        elif status == "error":
            print(f"💥 ({result.get('details', '')})")
        else:
            print(f"? {status}")

    # Итоги
    total_checked = sum(c.get("items_checked", 0) for c in report["checks"])
    total_passed = sum(c.get("items_passed", 0) for c in report["checks"])
    total_warned = sum(c.get("items_warned", 0) for c in report["checks"])
    total_failed = sum(c.get("items_failed", 0) for c in report["checks"])

    report["summary"] = {
        "total_checked": total_checked,
        "total_passed": total_passed,
        "total_warned": total_warned,
        "total_failed": total_failed,
        "overall_status": "fail" if total_failed > 0 else ("warn" if total_warned > 0 else "pass"),
    }

    print()
    print(f"📊 Итого: проверено {total_checked} | ✅ {total_passed} | ⚠️ {total_warned} | ❌ {total_failed}")

    # Сохранение
    if args.output:
        output_path = Path(args.output)
        if args.report_format == "md":
            md = generate_md_report(report)
            output_path.write_text(md, encoding="utf-8")
        else:
            output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"💾 Отчёт сохранён: {output_path}")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


def generate_md_report(report: dict) -> str:
    """Генерация отчёта в формате Markdown."""
    lines = [
        "### 📊 Результаты верификации (скриптовые проверки)",
        "",
        f"**Дата:** {report['timestamp']}",
        f"**Файлы:** {', '.join(report['files_checked'])}",
        f"**Пресет:** {report.get('preset', 'авто')}",
        "",
        "| Скрипт | Результат | Проверено | Замечания | Ошибки | Детали |",
        "|--------|-----------|-----------|-----------|--------|--------|",
    ]

    for check in report["checks"]:
        status_icon = {"pass": "✅", "warn": "⚠️", "fail": "❌", "skip": "⏭️", "error": "💥"}.get(
            check.get("status", "?"), "?"
        )
        lines.append(
            f"| {check.get('script', '?')} | {status_icon} | "
            f"{check.get('items_checked', 0)} | {check.get('items_warned', 0)} | "
            f"{check.get('items_failed', 0)} | {check.get('details', '')} |"
        )

    summary = report.get("summary", {})
    overall = {"pass": "✅ Всё ок", "warn": "⚠️ Есть замечания", "fail": "❌ Есть ошибки"}.get(
        summary.get("overall_status", "?"), "?"
    )
    lines.extend(["", f"**Общий статус:** {overall}", ""])

    # Findings
    all_findings = []
    for check in report["checks"]:
        all_findings.extend(check.get("findings", []))

    if all_findings:
        lines.append("#### Детали замечаний")
        lines.append("")
        for f in all_findings:
            sev = {"warning": "⚠️", "error": "❌", "info": "ℹ️"}.get(f.get("severity", "?"), "?")
            lines.append(f"- {sev} **{f.get('location', '?')}**: {f.get('description', '?')}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
