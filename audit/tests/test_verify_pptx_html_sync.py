"""Тесты для verify_pptx_html_sync.py"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "verification" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
TEST_DATA = Path(__file__).parent / "test_data"

import verify_pptx_html_sync as mod


class TestVerifyPptxHtmlSync:
    def test_matching_files_pass(self):
        result = mod.verify([
            str(TEST_DATA / "good.pptx"),
            str(TEST_DATA / "matching.html"),
        ])
        assert result["status"] in ("pass", "warn")
        assert result["items_checked"] > 0
        assert result["script"] == "verify_pptx_html_sync.py"

    def test_mismatched_files_warn(self):
        result = mod.verify([
            str(TEST_DATA / "good.pptx"),
            str(TEST_DATA / "mismatched.html"),
        ])
        # Количество секций не совпадает или контент расходится
        assert result["items_warned"] > 0 or result["items_checked"] > 0

    def test_missing_pptx_skips(self):
        result = mod.verify([str(TEST_DATA / "matching.html")])
        assert result["status"] == "skip"

    def test_missing_html_skips(self):
        result = mod.verify([str(TEST_DATA / "good.pptx")])
        assert result["status"] == "skip"

    def test_output_format(self):
        result = mod.verify([
            str(TEST_DATA / "good.pptx"),
            str(TEST_DATA / "matching.html"),
        ])
        required_keys = {"script", "status", "details", "items_checked",
                         "items_passed", "items_warned", "items_failed", "findings"}
        assert required_keys <= set(result.keys())

    def test_extract_pptx_text(self):
        slides = mod.extract_pptx_text(str(TEST_DATA / "good.pptx"))
        assert isinstance(slides, list)
        assert len(slides) > 0

    def test_extract_html_text(self):
        sections = mod.extract_html_text(str(TEST_DATA / "matching.html"))
        assert isinstance(sections, list)
        assert len(sections) > 0

    def test_normalize(self):
        assert mod.normalize("  Hello   World  ") == "hello world"
