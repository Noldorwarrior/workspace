# TODO: Исправления по результатам аудита

> Сгенерировано автоматически. Дата: 2026-03-30
> Обновлено: 2026-03-30 (все 20 существенных + 1 критическая исправлены)

## 🔴 Критические — ВСЕ ИСПРАВЛЕНЫ

- [x] **[CRIT-001]** №20 и №23 в субагентах — `agent_patterns.md`

## 🟡 Существенные — ВСЕ ИСПРАВЛЕНЫ

### Документация / Пресеты
- [x] **[WARN-001]** Fallback этапа 0 — `SKILL.md`
- [x] **[WARN-002]** Расширено описание этапа 3 — `SKILL.md`
- [x] **[WARN-003]** Уточнён self режим для CC — `SKILL.md`
- [x] **[WARN-004]** Конкретизированы «элементы П7» — `SKILL.md`
- [x] **[WARN-005]** №14 в М5 — `presets_matrix.md`
- [x] **[WARN-006]** №1 в П6 — `presets_matrix.md`
- [x] **[WARN-007]** №1 в П8 — `presets_matrix.md`
- [x] **[WARN-008]** №7 в П13 — `presets_matrix.md`
- [x] **[WARN-009]** Хронология: П8 теперь содержит №1+7 для кросс-проверки дат/имён

### Код
- [x] **[WARN-010]** line_spacing — `verify_docx_format.py`
- [x] **[WARN-011]** first_line_indent — `verify_docx_format.py`
- [x] **[WARN-012]** space_after — `verify_docx_format.py`
- [x] **[WARN-013]** Все runs в абзаце — `verify_docx_format.py`
- [x] **[WARN-014]** Merged cells + скрытые строки — `verify_sums.py`
- [x] **[WARN-015]** read_only для файлов >50MB — `verify_sums.py`
- [x] **[WARN-016]** Морфология `рисун\w*` — `verify_references.py`
- [x] **[WARN-017]** Границы дат `now.year + 10` — `verify_dates.py`
- [x] **[WARN-018]** datetime из openpyxl напрямую — `verify_dates.py`
- [x] **[WARN-019]** Одноцифровые числа с контекстом — `verify_cross_file.py`
- [x] **[WARN-020]** Экранирование `\|` в MD-таблицах — `generate_report.py`

## 🟢 Рекомендации (бэклог)

- [ ] **[REC-001]** Разделить mechanisms_document.md на два файла
- [ ] **[REC-002]** Добавить быстрые сценарии для П5, П6, П12, П14
- [ ] **[REC-003]** Раздел «Граничные случаи» в SKILL.md
- [ ] **[REC-004]** Единый YAML-конфиг для генерации матрицы и PRESET_SCRIPTS
- [ ] **[REC-005–027]** 23 кодовых рекомендации — см. audit/03_code_audit.md
