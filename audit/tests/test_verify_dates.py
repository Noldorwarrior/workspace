"""Тесты для verify_dates.py"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "verification" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
TEST_DATA = Path(__file__).parent / "test_data"

import verify_dates as mod


class TestVerifyDates:
    def test_dates_found(self):
        result = mod.verify([str(TEST_DATA / "dates.docx")])
        assert result["items_checked"] >= 3  # минимум 3 даты

    def test_suspicious_dates_flagged(self):
        result = mod.verify([str(TEST_DATA / "dates.docx")])
        # 1980 или 2035 должны быть замечены
        descriptions = " ".join(f["description"] for f in result["findings"])
        assert "1980" in descriptions or "2035" in descriptions

    def test_empty_docx_no_crash(self):
        result = mod.verify([str(TEST_DATA / "empty.docx")])
        assert result["status"] in ("pass", "warn", "fail")
        assert result["items_checked"] == 0

    def test_output_format(self):
        result = mod.verify([str(TEST_DATA / "dates.docx")])
        required_keys = {"script", "status", "details", "items_checked",
                         "items_passed", "items_warned", "items_failed", "findings"}
        assert required_keys <= set(result.keys())
        assert result["script"] == "verify_dates.py"

    def test_extract_dates_dmy_text(self):
        dates = mod.extract_dates("15 марта 2025 года")
        assert len(dates) == 1
        assert dates[0]["date"].month == 3

    def test_extract_dates_dmy_dots(self):
        dates = mod.extract_dates("01.04.2025")
        assert len(dates) == 1
        assert dates[0]["date"].day == 1

    def test_extract_dates_iso(self):
        dates = mod.extract_dates("2025-06-15")
        assert len(dates) == 1
        assert dates[0]["date"].year == 2025

    def test_extract_dates_empty(self):
        dates = mod.extract_dates("Нет дат здесь.")
        assert len(dates) == 0
