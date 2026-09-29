# Паспорт данных — патентная база MgB2-МРТ (Lens)

- **Файл:** `data/raw/patents/cases/mgb2_mri.json`
- **Скрипт:** `src/lens_mgb2_mri.py` (6 логических запросов, Lens.org `patent/search`)
- **Дата:**  · **Запись:** 224 raw → 138 уник. (дедуп по publication_number)
- **Поля записи:** publication_number, title, abstract, assignee (до 4), inventors (до 4), cited_by, year (priority), query-тег
- **Запросы:** A1 MgB2×MRI (40) · A2 MgB2×wire/coil/tape×magnet (40) · A3 MgB2×cryogenfree×MRI (4) · A4 players×MgB2 (0) · A5 MgB2 в title total=774 (100) · A6 MgB2×magnet (40)
- **Восстановление:** `.venv/bin/python src/lens_mgb2_mri.py` (нужен LENS_TOKEN в .env)
- **Расход Lens:** 6 запросов (остаток см. `results/runtime/api_budget.md`)