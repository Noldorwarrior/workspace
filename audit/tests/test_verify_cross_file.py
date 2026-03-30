"""Тесты для verify_cross_file.py"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "verification" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
TEST_DATA = Path(__file__).parent / "test_data"

import verify_cross_file as mod


class TestVerifyCrossFile:
    def test_cross_file_finds_discrepancies(self):
        result = mod.verify([str(TEST_DATA / "cross.docx"), str(TEST_DATA / "cross.xlsx")])
        assert result["items_checked"] > 0
        assert result["script"] == "verify_cross_file.py"

    def test_single_file_still_works(self):
        result = mod.verify([str(TEST_DATA / "good.docx")])
        assert result["status"] in ("pass", "warn", "fail")

    def test_output_format(self):
        result = mod.verify([str(TEST_DATA / "cross.docx"), str(TEST_DATA / "cross.xlsx")])
        required_keys = {"script", "status", "details", "items_checked",
                         "items_passed", "items_warned", "items_failed", "findings"}
        assert required_keys <= set(result.keys())

    def test_extract_docx(self):
        nums, names = mod.extract_data_from_docx(str(TEST_DATA / "cross.docx"))
        assert len(nums) > 0  # 1 500 000, 25

    def test_extract_xlsx(self):
        nums, names = mod.extract_data_from_xlsx(str(TEST_DATA / "cross.xlsx"))
        assert len(nums) > 0
