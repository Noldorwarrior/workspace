# Карта проекта

## Корневая директория: /home/user/workspace/.claude/skills/verification/

## Обнаруженные компоненты:

### scripts/ (12 Python-файлов)
- `auto_verify.py` — оркестратор: выбор и запуск скриптов по пресету
- `verify_docx_format.py` — формат docx по стандарту #6 (18/18 параметров)
- `verify_sums.py` — сверка сумм/итогов, границы, merged cells, read_only
- `verify_cross_file.py` — кросс-файловая согласованность (числа, ФИО, семантика)
- `verify_references.py` — битые ссылки в docx (поабзацно, приоритет подписям)
- `verify_dates.py` — валидация дат (3 формата, datetime из openpyxl)
- `verify_numbering.py` — нумерация (дубликаты, пропуски, монотонность, буквы)
- `verify_pptx_format.py` — формат слайдов (16:9, шрифты по whitelist, ноты)
- `verify_pptx_html_sync.py` — согласованность pptx↔html (конфигурируемый паттерн)
- `verify_regression.py` — защита от регрессий по предыдущему отчёту
- `diff_versions.py` — diff между версиями файлов
- `generate_report.py` — генерация отчёта (md/docx, inline-разметка, таблицы)

### references/ (9 файлов)
- `mechanisms_factual.md` — №1,2,6,7
- `mechanisms_logical.md` — №10-17,30
- `mechanisms_source.md` — №18,19,28
- `mechanisms_numerical.md` — №3,4,20,23
- `mechanisms_format.md` — №5,8,9
- `mechanisms_consistency.md` — №21,22,24-26,29,32
- `mechanisms_audience.md` — №27,31
- `presets_matrix.md` — М1-М5, П1-П14, кросс-матрица
- `agent_patterns.md` — субагенты, параллелизм, оркестрация

### Прочее
- `SKILL.md` — маршрутизация, workflow, граничные случаи, 9 быстрых сценариев
- `CLAUDE.md.template` — шаблон для проектного CLAUDE.md

### Корневая CLAUDE.md
- `/home/user/workspace/CLAUDE.md` — ссылается на скилл верификации

## Итого: 23 файла в системе верификации + 8 файлов аудита + 11 тест-файлов
