"""Тесты для verify_numbering.py"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "verification" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
TEST_DATA = Path(__file__).parent / "test_data"

import verify_numbering as mod


class TestVerifyNumbering:
    def test_ok_numbering_passes(self):
        result = mod.verify(str(TEST_DATA / "numbering_ok.docx"))
        assert result["status"] == "pass"
        assert result["items_warned"] == 0

    def test_bad_numbering_finds_issues(self):
        result = mod.verify(str(TEST_DATA / "numbering_bad.docx"))
        assert result["status"] == "warn"
        assert result["items_warned"] > 0
        descriptions = " ".join(f["description"] for f in result["findings"])
        assert "Дубликат" in descriptions or "Пропуск" in descriptions

    def test_empty_docx_no_crash(self):
        result = mod.verify(str(TEST_DATA / "empty.docx"))
        assert result["status"] == "pass"
        assert result["items_checked"] == 0

    def test_output_format(self):
        result = mod.verify(str(TEST_DATA / "numbering_ok.docx"))
        required_keys = {"script", "status", "details", "items_checked",
                         "items_passed", "items_warned", "items_failed", "findings"}
        assert required_keys <= set(result.keys())
        assert result["script"] == "verify_numbering.py"
