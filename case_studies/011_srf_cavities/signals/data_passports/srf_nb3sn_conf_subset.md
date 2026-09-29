# Паспорт: конференционное подмножество Nb3Sn SRF (кейс 011, тренд)

- **Файл:** `data/raw/conferences/srf_nb3sn_conf_subset.json` — **59 conference-papers** Nb3Sn SRF (из 1832 conference-papers SRF-корпуса).
- **Дата:** . Скрипт: `src/plot_conf_nb3sn.py` (строит график `plots/conf_nb3sn_by_year.png`).
- **Источник:** фильтрация **существующего** корпуса `data/raw/openalex/srf_corpus.json` (type=conference-paper, 1832 шт.),
  паттерн `nb\s*3\s*sn | niobium[\s-]?tin | b3sn` (title/abstract).
- **НОВЫХ API-запросов не потребовалось** (всё локально; конференционный слой был в сборе ).
- **Контекст (что НЕ вошло — важный нюанс):** IEEE TAS-база `conference_hits.json` (2175 записей) содержит 149 Nb3Sn-статей,
  НО почти все — МАГНИТЫ (ITER, HL-LHC, ундуляторы, NMR): «полостных» там только 1 (2026, Co-sputtered films for SRF).
  SRF-сообщество публикуется НЕ в TAS → правильный конференц. сигнал полостей — из SRF-корпуса (1832 conf-papers).
- **Поля:** id, doi, title, year, abstract, authors, cited_by (как в srf_corpus).
- **Как восстановить:** `.venv/bin/python src/plot_conf_nb3sn.py` (локально, без сети).
- **Расход API:** 0.