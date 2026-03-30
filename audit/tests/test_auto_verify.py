"""Тесты для auto_verify.py"""
import sys
import json
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "verification" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
TEST_DATA = Path(__file__).parent / "test_data"

import auto_verify as mod


class TestAutoVerify:
    def test_detect_applicable_docx(self):
        applicable = mod.detect_applicable_scripts([str(TEST_DATA / "good.docx")])
        assert "format" in applicable
        assert "references" in applicable
        assert "numbering" in applicable
        assert "dates" in applicable

    def test_detect_applicable_xlsx(self):
        applicable = mod.detect_applicable_scripts([str(TEST_DATA / "good.xlsx")])
        assert "sums" in applicable
        assert "dates" in applicable

    def test_detect_applicable_pptx(self):
        applicable = mod.detect_applicable_scripts([str(TEST_DATA / "good.pptx")])
        assert "pptx_format" in applicable

    def test_detect_applicable_multi_file(self):
        applicable = mod.detect_applicable_scripts([
            str(TEST_DATA / "good.pptx"),
            str(TEST_DATA / "matching.html"),
        ])
        assert "pptx_html_sync" in applicable

    def test_detect_applicable_requires_min_files(self):
        """cross_file и diff нужно 2+ файла."""
        single = mod.detect_applicable_scripts([str(TEST_DATA / "good.docx")])
        assert "cross_file" not in single
        assert "diff" not in single

        multi = mod.detect_applicable_scripts([
            str(TEST_DATA / "good.docx"),
            str(TEST_DATA / "empty.docx"),
        ])
        assert "cross_file" in multi
        assert "diff" in multi

    def test_preset_p5_all_scripts(self):
        assert len(mod.PRESET_SCRIPTS["П5"]) == len(mod.SCRIPT_REGISTRY)

    def test_preset_keys_exist_in_registry(self):
        for preset, scripts in mod.PRESET_SCRIPTS.items():
            for s in scripts:
                assert s in mod.SCRIPT_REGISTRY, f"Скрипт '{s}' в пресете {preset} отсутствует в реестре"

    def test_run_script_nonexistent(self):
        """Запуск несуществующего скрипта возвращает skip."""
        # Подменяем реестр временно
        mod.SCRIPT_REGISTRY["_test"] = {
            "module": "nonexistent_script_xyz",
            "applies_to": ["*"],
            "description": "Тест",
        }
        result = mod.run_script("_test", [str(TEST_DATA / "good.docx")])
        assert result["status"] == "skip"
        del mod.SCRIPT_REGISTRY["_test"]

    def test_run_script_real(self):
        """Запуск реального скрипта через subprocess."""
        result = mod.run_script("format", [str(TEST_DATA / "good.docx")])
        assert result["status"] in ("pass", "warn", "fail", "error")
        assert "script" in result

    def test_generate_md_report(self):
        report = {
            "timestamp": "2025-01-01T00:00:00",
            "files_checked": ["test.docx"],
            "preset": "П1",
            "checks": [
                {
                    "script": "verify_docx_format.py",
                    "status": "pass",
                    "items_checked": 10,
                    "items_warned": 0,
                    "items_failed": 0,
                    "details": "OK",
                    "findings": [],
                }
            ],
            "summary": {"total_checked": 10, "total_passed": 10, "total_warned": 0,
                         "total_failed": 0, "overall_status": "pass"},
        }
        md = mod.generate_md_report(report)
        assert "Результаты верификации" in md
        assert "verify_docx_format.py" in md

    def test_script_registry_completeness(self):
        """Все модули в реестре существуют на диске."""
        for name, info in mod.SCRIPT_REGISTRY.items():
            script_path = SCRIPTS_DIR / f"{info['module']}.py"
            assert script_path.exists(), f"Скрипт {script_path} не найден (реестр: {name})"
