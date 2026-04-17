"""Тесты для verify_references.py"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "verification" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
TEST_DATA = Path(__file__).parent / "test_data"

import verify_references as mod


class TestVerifyReferences:
    def test_refs_ok_passes(self):
        result = mod.verify(str(TEST_DATA / "refs_ok.docx"))
        assert result["status"] == "pass"
        assert result["items_failed"] == 0

    def test_refs_broken_finds_errors(self):
        result = mod.verify(str(TEST_DATA / "refs_broken.docx"))
        assert result["status"] == "fail"
        assert result["items_failed"] > 0
        assert any("Таблица 5" in f["description"] for f in result["findings"])

    def test_empty_docx_no_crash(self):
        result = mod.verify(str(TEST_DATA / "empty.docx"))
        assert result["status"] == "pass"
        assert result["items_checked"] == 0

    def test_output_format(self):
        result = mod.verify(str(TEST_DATA / "refs_ok.docx"))
        required_keys = {"script", "status", "details", "items_checked",
                         "items_passed", "items_warned", "items_failed", "findings"}
        assert required_keys <= set(result.keys())
        assert result["script"] == "verify_references.py"

    def test_extract_references(self):
        from docx import Document
        doc = Document(str(TEST_DATA / "refs_broken.docx"))
        refs = mod.extract_references(doc)
        types = {r["type"] for r in refs}
        assert "Таблица" in types

    def test_find_targets(self):
        from docx import Document
        doc = Document(str(TEST_DATA / "refs_ok.docx"))
        targets = mod.find_targets(doc)
        assert "1" in targets["Таблица"]
