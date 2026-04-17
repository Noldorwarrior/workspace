"""Тесты для verify_sums.py"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "verification" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
TEST_DATA = Path(__file__).parent / "test_data"

import verify_sums as mod


class TestVerifySums:
    def test_good_xlsx_passes(self):
        result = mod.verify(str(TEST_DATA / "good.xlsx"))
        assert result["status"] == "pass"
        assert result["items_checked"] > 0

    def test_bad_xlsx_finds_errors(self):
        result = mod.verify(str(TEST_DATA / "bad.xlsx"))
        assert result["items_warned"] > 0 or result["items_failed"] > 0
        descriptions = [f["description"] for f in result["findings"]]
        # Должна обнаружить неверную сумму или выход за границы
        assert len(result["findings"]) > 0

    def test_empty_xlsx_no_crash(self):
        result = mod.verify(str(TEST_DATA / "empty.xlsx"))
        assert result["status"] in ("pass", "warn", "fail")
        assert isinstance(result["findings"], list)

    def test_output_format(self):
        result = mod.verify(str(TEST_DATA / "good.xlsx"))
        required_keys = {"script", "status", "details", "items_checked",
                         "items_passed", "items_warned", "items_failed", "findings"}
        assert required_keys <= set(result.keys())
        assert result["script"] == "verify_sums.py"

    def test_find_sum_rows(self):
        import openpyxl
        wb = openpyxl.load_workbook(str(TEST_DATA / "good.xlsx"), data_only=True)
        ws = wb.active
        rows = mod.find_sum_rows(ws)
        assert 5 in rows  # "Итого" в строке 5

    def test_boundary_percent_over_100(self):
        result = mod.verify(str(TEST_DATA / "bad.xlsx"))
        over100 = [f for f in result["findings"] if "выше максимума" in f.get("description", "")]
        assert len(over100) > 0

    def test_negative_financial(self):
        result = mod.verify(str(TEST_DATA / "bad.xlsx"))
        neg = [f for f in result["findings"] if "Отрицательное" in f.get("description", "")]
        assert len(neg) > 0
