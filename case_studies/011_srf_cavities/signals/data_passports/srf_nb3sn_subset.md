# Паспорт: подмножество Nb3Sn SRF (кейс 011, ТРЕНД по новому видению)

- **Файл:** `data/raw/openalex/srf_nb3sn_subset.json` — **327 работ** (полное: title+абстракт), из них **208 — title-ядро**. Контрольная группа Nb (для сравнения): 1229 работ.
- **Дата:** . Скрипт: `src/plot_pubs_nb3sn.py` (одновременно строит и график `plots/pubs_nb3sn_by_year.png`).
- **Источник:** фильтрация **существующего** корпуса `data/raw/openalex/srf_corpus.json` (7579 работ).
- **НОВЫХ API-запросов НЕ потребовалось:** запрос №3 паспорта srf_corpus («Nb3Sn cavity / Nb3Sn SRF / niobium-tin cavity»)
  был сделан при сборе  (39 работ по прямому запросу; остальные Nb3Sn-работы зацепили слои №1-2,4).
- **Паттерн фильтра:** `nb\s*3\s*sn | niobium[\s-]?tin | niob[\s-]?tin | b3sn` (title → ядро; abstract → полное).
- **Контроль (зрелая технология):** Nb SRF — `\bniobium\b|\bNb\b` в title БЕЗ Nb3Sn → 1229 работ.
- **Fields в подмножестве:** id, doi, title, year, date, cited_by, abstract, authors(+institution), references, type, concepts (скобкая копия из srf_corpus).
- **Как восстановить:** `.venv/bin/python src/plot_pubs_nb3sn.py` — локально, без сети (читает только srf_corpus.json).
- **Расход API:** 0 (пересборка из локальных данных; библиотека API-бюджета не изменена).