"""Тесты для generate_report.py"""
import sys
import json
import tempfile
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "verification" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
TEST_DATA = Path(__file__).parent / "test_data"

import generate_report as mod


SAMPLE_SCRIPT_RESULTS = {
    "timestamp": "2025-03-30T12:00:00",
    "files_checked": ["doc.docx"],
    "preset": "П1",
    "checks": [
        {
            "script": "verify_docx_format.py",
            "status": "warn",
            "items_checked": 15,
            "items_warned": 2,
            "items_failed": 0,
            "details": "Проверено 15 элементов",
            "findings": [
                {
                    "severity": "warning",
                    "location": "Абзац 3",
                    "expected": "14pt",
                    "actual": "10pt",
                    "description": "Размер шрифта: 10pt вместо 14pt",
                },
            ],
        },
        {
            "script": "verify_references.py",
            "status": "fail",
            "items_checked": 5,
            "items_warned": 0,
            "items_failed": 2,
            "details": "Битых ссылок: 2",
            "findings": [
                {
                    "severity": "error",
                    "location": "Таблица 5",
                    "expected": "существует",
                    "actual": "не найдено",
                    "description": "Битая ссылка: Таблица 5 не найдена",
                },
            ],
        },
    ],
    "summary": {
        "total_checked": 20,
        "total_passed": 16,
        "total_warned": 2,
        "total_failed": 2,
        "overall_status": "fail",
    },
}


class TestGenerateReport:
    def test_generate_md_with_script_results(self):
        md = mod.generate_md(SAMPLE_SCRIPT_RESULTS, None)
        assert "Отчёт верификации" in md
        assert "verify_docx_format.py" in md
        assert "verify_references.py" in md
        assert "Таблица 5" in md
        assert "Итоговый вердикт" in md

    def test_generate_md_with_agent_results(self):
        agent_md = "## Результат LLM\n- Замечание 1\n- Замечание 2"
        md = mod.generate_md(None, agent_md)
        assert "LLM-проверки" in md
        assert "Замечание 1" in md

    def test_generate_md_both(self):
        agent_md = "Агентная проверка пройдена."
        md = mod.generate_md(SAMPLE_SCRIPT_RESULTS, agent_md, preset="П1", mechanisms="М1,М2")
        assert "П1" in md
        assert "М1,М2" in md
        assert "Агентная проверка" in md
        assert "verify_docx_format.py" in md

    def test_generate_md_none(self):
        md = mod.generate_md(None, None)
        assert "Отчёт верификации" in md
        assert "Итоговый вердикт" in md

    def test_generate_md_verdict_pass(self):
        results = dict(SAMPLE_SCRIPT_RESULTS)
        results["summary"] = dict(results["summary"])
        results["summary"]["overall_status"] = "pass"
        md = mod.generate_md(results, None)
        assert "Верификация пройдена" in md

    def test_generate_md_verdict_warn(self):
        results = dict(SAMPLE_SCRIPT_RESULTS)
        results["summary"] = dict(results["summary"])
        results["summary"]["overall_status"] = "warn"
        md = mod.generate_md(results, None)
        assert "замечаниями" in md

    def test_generate_md_verdict_fail(self):
        md = mod.generate_md(SAMPLE_SCRIPT_RESULTS, None)
        assert "ошибки" in md

    def test_generate_docx(self):
        md_content = mod.generate_md(SAMPLE_SCRIPT_RESULTS, None)
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = f.name
        try:
            result = mod.generate_docx(md_content, output_path)
            assert result is True
            assert Path(output_path).exists()
            assert Path(output_path).stat().st_size > 0
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_load_script_results_nonexistent(self):
        assert mod.load_script_results("/tmp/nonexistent_xyz.json") is None

    def test_load_script_results_valid(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(SAMPLE_SCRIPT_RESULTS, f, ensure_ascii=False)
            f.flush()
            path = f.name
        try:
            result = mod.load_script_results(path)
            assert result is not None
            assert result["preset"] == "П1"
        finally:
            Path(path).unlink(missing_ok=True)

    def test_load_agent_results_nonexistent(self):
        assert mod.load_agent_results("/tmp/nonexistent_xyz.md") is None

    def test_output_format_md_tables(self):
        md = mod.generate_md(SAMPLE_SCRIPT_RESULTS, None)
        assert "| Скрипт |" in md
        assert "|--------|" in md
