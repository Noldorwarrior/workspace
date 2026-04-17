# TODO: Исправления по результатам аудита

> Сгенерировано автоматически. Дата: 2026-03-30
> Финальное обновление: 2026-03-30 — **все находки закрыты**

## 🔴 Критические — ВСЕ ИСПРАВЛЕНЫ ✅

- [x] **[CRIT-001]** №20 и №23 в субагентах — `agent_patterns.md`

## 🟡 Существенные — ВСЕ 20 ИСПРАВЛЕНЫ ✅

- [x] **[WARN-001]** Fallback этапа 0 — `SKILL.md`
- [x] **[WARN-002]** Описание этапа 3 — `SKILL.md`
- [x] **[WARN-003]** Уточнение self-режима — `SKILL.md`
- [x] **[WARN-004]** Конкретизация «элементов П7» — `SKILL.md`
- [x] **[WARN-005]** М5 +№14 — `presets_matrix.md`
- [x] **[WARN-006]** П6 +№1 — `presets_matrix.md`
- [x] **[WARN-007]** П8 +№1 — `presets_matrix.md`
- [x] **[WARN-008]** П13 +№7 — `presets_matrix.md`
- [x] **[WARN-009]** Хронология: кросс-проверка через №1+7 в П8
- [x] **[WARN-010]** line_spacing — `verify_docx_format.py`
- [x] **[WARN-011]** first_line_indent — `verify_docx_format.py`
- [x] **[WARN-012]** space_after — `verify_docx_format.py`
- [x] **[WARN-013]** Все runs в абзаце — `verify_docx_format.py`
- [x] **[WARN-014]** Merged cells + скрытые строки — `verify_sums.py`
- [x] **[WARN-015]** read_only >50MB — `verify_sums.py`
- [x] **[WARN-016]** Морфология `рисун\w*` — `verify_references.py`
- [x] **[WARN-017]** Границы дат `now.year+10` — `verify_dates.py`
- [x] **[WARN-018]** datetime из openpyxl — `verify_dates.py`
- [x] **[WARN-019]** Одноцифровые числа — `verify_cross_file.py`
- [x] **[WARN-020]** Экранирование `\|` — `generate_report.py`

## 🟢 Рекомендации — 26 из 27 РЕАЛИЗОВАНЫ ✅

- [x] **[REC-001]** Разделить mechanisms_document.md → format + consistency
- [x] **[REC-002]** 4 новых быстрых сценария (П5, П6, П12, П14)
- [x] **[REC-003]** Раздел «Граничные случаи» в SKILL.md
- [ ] **[REC-004]** Единый YAML-конфиг — ⏭️ пропущен (существенная переработка auto_verify.py)
- [x] **[REC-005]** П2 +№28 (эпистемический статус)
- [x] **[REC-006]** П8 +№1 (= WARN-007)
- [x] **[REC-007]** verify_regression.py — новый скрипт
- [x] **[REC-008]** Частичное выполнение (= REC-003)
- [x] **[REC-009]** Type hint run_script
- [x] **[REC-010]** Пустой stdout returncode=0
- [x] **[REC-011]** Предупреждение пустой пресет
- [x] **[REC-012]** Колонтитулы (18/18 стандарт #6)
- [x] **[REC-013]** Все runs (= WARN-013)
- [x] **[REC-014]** Заголовочная строка таблиц
- [x] **[REC-015]** Поблочная обработка references
- [x] **[REC-016]** Приоритет подписям таблиц
- [x] **[REC-017]** Стоп-слова ФИО
- [x] **[REC-018]** Type hints cross_file
- [x] **[REC-019]** Type hints dates
- [x] **[REC-020]** Монотонность нумерации
- [x] **[REC-021]** Буквенные приложения
- [x] **[REC-022]** Шрифты pptx (whitelist)
- [x] **[REC-023]** Комментарий min_font (в REC-022)
- [x] **[REC-024]** Конфигурируемый паттерн html
- [x] **[REC-025]** wb.close() в diff
- [x] **[REC-026]** Inline-разметка docx
- [x] **[REC-027]** JSONDecodeError
