"""Тесты для diff_versions.py"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "verification" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
TEST_DATA = Path(__file__).parent / "test_data"

import diff_versions as mod


class TestDiffVersions:
    def test_diff_finds_changes(self):
        result = mod.verify([str(TEST_DATA / "v1.docx"), str(TEST_DATA / "v2.docx")])
        assert result["status"] == "info"
        assert result["items_checked"] > 0
        assert len(result["findings"]) > 0
        assert result["script"] == "diff_versions.py"

    def test_diff_identical_files(self):
        result = mod.verify([str(TEST_DATA / "v1.docx"), str(TEST_DATA / "v1.docx")])
        assert result["items_checked"] > 0
        # Идентичные файлы — нет изменений в findings (кроме info с 0+/0-)
        changes = [f for f in result["findings"] if "Добавлено" in f.get("location", "") or "Удалено" in f.get("location", "")]
        assert len(changes) == 0

    def test_single_file_skips(self):
        result = mod.verify([str(TEST_DATA / "v1.docx")])
        assert result["status"] == "skip"

    def test_output_format(self):
        result = mod.verify([str(TEST_DATA / "v1.docx"), str(TEST_DATA / "v2.docx")])
        required_keys = {"script", "status", "details", "items_checked",
                         "items_passed", "items_warned", "items_failed", "findings"}
        assert required_keys <= set(result.keys())

    def test_extract_text_docx(self):
        lines = mod.extract_text(str(TEST_DATA / "v1.docx"))
        assert isinstance(lines, list)
        assert len(lines) > 0

    def test_extract_text_xlsx(self):
        lines = mod.extract_text(str(TEST_DATA / "good.xlsx"))
        assert isinstance(lines, list)
        assert len(lines) > 0

    def test_extract_text_txt(self):
        """Тест с текстовым файлом."""
        txt_path = TEST_DATA / "sample.txt"
        txt_path.write_text("Строка 1\nСтрока 2\n", encoding="utf-8")
        lines = mod.extract_text(str(txt_path))
        assert len(lines) == 2

    def test_extract_text_unknown_ext(self):
        """Неизвестное расширение — пустой список."""
        lines = mod.extract_text("/tmp/fake.xyz")
        assert lines == []
