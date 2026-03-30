# Результаты тестирования скриптов верификации

**Дата:** 2026-03-30
**Python:** 3.11.14
**pytest:** 9.0.2

## Итог: 80/80 тестов PASSED

```
audit/tests/test_auto_verify.py          11 PASSED
audit/tests/test_diff_versions.py         8 PASSED
audit/tests/test_generate_report.py      12 PASSED
audit/tests/test_verify_cross_file.py     5 PASSED
audit/tests/test_verify_dates.py          8 PASSED
audit/tests/test_verify_docx_format.py    8 PASSED
audit/tests/test_verify_numbering.py      4 PASSED
audit/tests/test_verify_pptx_format.py    3 PASSED
audit/tests/test_verify_pptx_html_sync.py 8 PASSED
audit/tests/test_verify_references.py     6 PASSED
audit/tests/test_verify_sums.py           7 PASSED
```

## Покрытие по типам тестов

| Скрипт | Позитивные | Негативные | Граничные | Unit-функции |
|--------|:----------:|:----------:|:---------:|:------------:|
| auto_verify.py | + | + | + | + |
| verify_docx_format.py | + | + | + | + |
| verify_sums.py | + | + | + | + |
| verify_references.py | + | + | + | + |
| verify_cross_file.py | + | + | + | + |
| verify_dates.py | + | + | + | + |
| verify_numbering.py | + | + | + | - |
| verify_pptx_format.py | + | + | - | - |
| verify_pptx_html_sync.py | + | + | + | + |
| diff_versions.py | + | + | + | + |
| generate_report.py | + | + | - | + |

## Тестовые данные (сгенерированы программно)

Все файлы в `audit/tests/test_data/`:
- good.docx, bad.docx, empty.docx — формат docx
- good.xlsx, bad.xlsx, empty.xlsx — суммы xlsx
- refs_ok.docx, refs_broken.docx — ссылки
- numbering_ok.docx, numbering_bad.docx — нумерация
- dates.docx — даты
- good.pptx, bad.pptx — pptx формат
- matching.html, mismatched.html — html для sync
- cross.docx, cross.xlsx — кросс-файл
- v1.docx, v2.docx — diff версий
- sample.txt — текстовый файл
