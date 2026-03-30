"""Тесты для verify_docx_format.py"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "verification" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
TEST_DATA = Path(__file__).parent / "test_data"

import verify_docx_format as mod


class TestVerifyDocxFormat:
    def test_good_docx_passes(self):
        result = mod.verify(str(TEST_DATA / "good.docx"))
        assert result["status"] in ("pass", "warn")  # warn допустим для info
        assert result["items_checked"] > 0
        assert result["script"] == "verify_docx_format.py"

    def test_bad_docx_finds_issues(self):
        result = mod.verify(str(TEST_DATA / "bad.docx"))
        assert result["items_warned"] > 0 or result["items_failed"] > 0
        assert len(result["findings"]) > 0

    def test_empty_docx_no_crash(self):
        result = mod.verify(str(TEST_DATA / "empty.docx"))
        assert result["status"] in ("pass", "warn", "fail")
        assert isinstance(result["findings"], list)

    def test_output_format_complete(self):
        result = mod.verify(str(TEST_DATA / "good.docx"))
        required_keys = {"script", "status", "details", "items_checked",
                         "items_passed", "items_warned", "items_failed", "findings"}
        assert required_keys <= set(result.keys())

    def test_cm_from_emu_none(self):
        assert mod.cm_from_emu(None) is None

    def test_cm_from_emu_value(self):
        assert mod.cm_from_emu(360000) == 1.0

    def test_pt_from_emu_none(self):
        assert mod.pt_from_emu(None) is None

    def test_pt_from_emu_value(self):
        assert mod.pt_from_emu(12700) == 1.0
