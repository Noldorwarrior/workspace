#!/usr/bin/env python3
"""
generate_report.py — Генерация итогового отчёта верификации.
Принимает результаты скриптов (JSON) и LLM-проверок (md), сводит в единый отчёт.

Использование:
    python generate_report.py --script-results script_report.json --output report.md
    python generate_report.py --script-results script_report.json --agent-results agent.md --output report.md
    python generate_report.py --script-results script_report.json --output report.docx --format docx
"""

import argparse, json, sys
from datetime import datetime
from pathlib import Path


def load_script_results(filepath):
    if not filepath or not Path(filepath).exists():
        return None
    return json.loads(Path(filepath).read_text(encoding="utf-8"))


def load_agent_results(filepath):
    if not filepath or not Path(filepath).exists():
        return None
    return Path(filepath).read_text(encoding="utf-8")


def generate_md(script_results, agent_results, preset=None, mechanisms=None):
    lines = [
        "# 📊 Отчёт верификации",
        "",
        f"**Дата:** {datetime.now().strftime('%d.%m.%Y %H:%M')}",
    ]

    if preset:
        lines.append(f"**Пресет:** {preset}")
    if mechanisms:
        lines.append(f"**Механизмы:** {mechanisms}")
    lines.append("")

    # Скриптовые результаты
    if script_results:
        lines.extend([
            "## Скриптовые проверки (автоматические)",
            "",
            "| Скрипт | Статус | Проверено | ⚠️ | ❌ | Детали |",
            "|--------|--------|-----------|-----|-----|--------|",
        ])

        for check in script_results.get("checks", []):
            status_icon = {"pass": "✅", "warn": "⚠️", "fail": "❌", "skip": "⏭️", "error": "💥", "info": "ℹ️"}.get(
                check.get("status", "?"), "?"
            )
            lines.append(
                f"| {check.get('script', '?')} | {status_icon} | "
                f"{check.get('items_checked', 0)} | {check.get('items_warned', 0)} | "
                f"{check.get('items_failed', 0)} | {check.get('details', '')} |"
            )

        # Сводка
        summary = script_results.get("summary", {})
        lines.extend([
            "",
            f"**Итого скрипты:** проверено {summary.get('total_checked', 0)} | "
            f"✅ {summary.get('total_passed', 0)} | ⚠️ {summary.get('total_warned', 0)} | "
            f"❌ {summary.get('total_failed', 0)}",
            "",
        ])

        # Детали замечаний
        all_findings = []
        for check in script_results.get("checks", []):
            all_findings.extend(check.get("findings", []))

        if all_findings:
            lines.extend(["### Детали замечаний", ""])
            for f in all_findings:
                if f.get("severity") in ("warning", "error"):
                    sev = {"warning": "⚠️", "error": "❌"}.get(f["severity"], "?")
                    lines.append(f"- {sev} **{f.get('location', '?')}**: {f.get('description', '?')}")
            lines.append("")

    # LLM-результаты
    if agent_results:
        lines.extend([
            "## LLM-проверки (агентные)",
            "",
            agent_results,
            "",
        ])

    # Общий вердикт
    overall = "pass"
    if script_results:
        s = script_results.get("summary", {}).get("overall_status", "pass")
        if s in ("fail", "warn"):
            overall = s

    verdict = {"pass": "✅ Верификация пройдена", "warn": "⚠️ Верификация пройдена с замечаниями",
               "fail": "❌ Верификация выявила ошибки"}.get(overall, "?")
    
    lines.extend([
        "---",
        f"## Итоговый вердикт: {verdict}",
        "",
    ])

    return "\n".join(lines)


def generate_docx(md_content, output_path):
    """Конвертировать md-отчёт в docx."""
    try:
        from docx import Document
        from docx.shared import Pt, Cm, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = Document()
        for section in doc.sections:
            section.top_margin = Cm(2)
            section.bottom_margin = Cm(2)
            section.left_margin = Cm(2)
            section.right_margin = Cm(1.5)

        for line in md_content.split("\n"):
            if line.startswith("# "):
                p = doc.add_heading(line[2:], level=1)
            elif line.startswith("## "):
                p = doc.add_heading(line[3:], level=2)
            elif line.startswith("### "):
                p = doc.add_heading(line[4:], level=3)
            elif line.startswith("---"):
                doc.add_paragraph("─" * 60)
            elif line.startswith("|"):
                # Простая поддержка таблиц — пропускаем разделители
                if set(line.replace("|", "").strip()) <= {"-", " "}:
                    continue
                doc.add_paragraph(line, style="Normal")
            elif line.startswith("- "):
                doc.add_paragraph(line[2:], style="List Bullet")
            elif line.strip():
                doc.add_paragraph(line)

        doc.save(output_path)
        return True
    except ImportError:
        return False


def main():
    parser = argparse.ArgumentParser(description="Генерация отчёта верификации")
    parser.add_argument("--script-results", default=None, help="JSON с результатами скриптов")
    parser.add_argument("--agent-results", default=None, help="MD с результатами LLM-агента")
    parser.add_argument("--preset", default=None, help="Название пресета")
    parser.add_argument("--mechanisms", default=None, help="Список механизмов")
    parser.add_argument("--output", required=True, help="Путь к выходному файлу")
    parser.add_argument("--format", choices=["md", "docx"], default=None, help="Формат (авто по расширению)")

    args = parser.parse_args()

    script_results = load_script_results(args.script_results)
    agent_results = load_agent_results(args.agent_results)

    md_content = generate_md(script_results, agent_results, args.preset, args.mechanisms)

    output_format = args.format or ("docx" if args.output.endswith(".docx") else "md")

    if output_format == "docx":
        if generate_docx(md_content, args.output):
            print(f"💾 Отчёт сохранён: {args.output} (docx)")
        else:
            # Fallback to md
            md_path = args.output.replace(".docx", ".md")
            Path(md_path).write_text(md_content, encoding="utf-8")
            print(f"💾 Отчёт сохранён: {md_path} (md, python-docx не установлен)")
    else:
        Path(args.output).write_text(md_content, encoding="utf-8")
        print(f"💾 Отчёт сохранён: {args.output} (md)")


if __name__ == "__main__":
    main()
