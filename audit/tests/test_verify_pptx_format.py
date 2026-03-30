"""Тесты для verify_pptx_format.py"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "verification" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
TEST_DATA = Path(__file__).parent / "test_data"

import verify_pptx_format as mod


class TestVerifyPptxFormat:
    def test_good_pptx_passes(self):
        result = mod.verify(str(TEST_DATA / "good.pptx"))
        assert result["status"] == "pass"
        assert result["items_checked"] > 0

    def test_bad_pptx_finds_issues(self):
        result = mod.verify(str(TEST_DATA / "bad.pptx"))
        assert result["items_warned"] > 0
        descriptions = " ".join(f["description"] for f in result["findings"])
        # Должен найти неверное соотношение или мелкий шрифт
        assert "соотношение" in descriptions.lower() or "шрифт" in descriptions.lower()

    def test_output_format(self):
        result = mod.verify(str(TEST_DATA / "good.pptx"))
        required_keys = {"script", "status", "details", "items_checked",
                         "items_passed", "items_warned", "items_failed", "findings"}
        assert required_keys <= set(result.keys())
        assert result["script"] == "verify_pptx_format.py"
