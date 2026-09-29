# Паспорт: CORC-патенты по грантополучателям (кейс 009)

- **Файл:** `data/raw/patents/cases/009_corc_grants.json` (93 патентов)
- **Скрипт:** `src/lens_corc_grants.py`
- **Запросы:** 13 (A1-A2 ядро, B1-B6 грантополучатели, C1-C3 география, D1-D2 импакт/legal)
- **Дата:** 
- **API-вызовов:** 13
- **Поля:** publication_number, title, abstract, assignee, inventor, priority/filing/publication_date, cited_by_n, legal_status, tags, url
- **Ограничение:** Lens НЕ отдаёт government interest (номера грантов DE-SC...) — грантовые номера только из NSF/CORDIS/РНФ/PDF
- **Как восстановить:** `.venv/bin/python src/lens_corc_grants.py`
