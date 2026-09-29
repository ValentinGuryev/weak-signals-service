# Паспорт базы: патенты кейса #87 (cryo_sc_computing)

- **Файл:** `data/raw/patents/cases/087_cryo_sc_computing.json` (33 записи)
- **Источник:** ручные патенты Google Patents (`data/raw/patents/patents.google.manual/`, суффикс `__cryo_sc_computing`)
- **Дата сбора/разбора:** 2026-09-17
- **Протокол:** внутренний контракт §4.2c (ручные патенты); Lens.org закрыт
- **Число записей:** 33
- **Поля:** publication_number, title, assignee, date_of_patent/publication_date, abstract, source="manual", cases=["cryo_sc_computing"]
- **Метод отбора:** из пачки ~189 необработанных PDF выбраны 76 крио-релевантных (по ключевым словам cryogenic/superconduct/SFQ/RSFQ/Josephson/cryotron/quantum); из них 33 — прямо относящиеся к СП/крио-ВЫЧИСЛЕНИЯМ и СП-ПАМЯТИ для вычислений → переименованы с суффиксом кейса; остальные ~43 крио-релевантных отнесены к другим кейсам (fusion_magnets/hts_tapes/011_srf/008_aircraft/001_ibad) и НЕ входят сюда.
- **Дубликаты:** дедуп по publication_number (2 уровня §4.2c) — новых в JSON кейса #87 не было (база создана впервые); семейства US/EP/WO/CN различных юрисдикций одного изобретения различаются, отмечены в patent_signal.
- **Как восстановить:** PDF лежат в `patents.google.manual/*__cryo_sc_computing.pdf`; пересборка JSON — скриптом извлечения pdftotext (см. лог `results/runtime/manual_patents_processing_*.md`).
- **Ограничения:** assignee/title у части патентов (Google Patents layout) заполнены вручную по 1-й странице; абстракты обрезаны до ~800 симв.; годы — даты ВЫДАЧИ (не подачи).
