# Паспорт: корпус SRF-резонаторов (кейс 011)

- **Файл:** `data/raw/openalex/srf_corpus.json` — **7579 работ** (1962-2026).
- **Дата:** . Скрипт: `src/openalex_srf.py`.
- **Запросы (OpenAlex, title_and_abstract.search, полные записи, cursor-пагинация per-page=200):**
  1. `"SRF accelerator"` / `"SRF cavity"` / `"SRF cavities"` / `"superconducting RF cavity"` / `"superconducting accelerator cavity"` → 5900;
  2. `"niobium cavity"` / `"niobium SRF"` / `"niobium superconducting cavity"` → 622;
  3. `"Nb3Sn cavity"` / `"Nb3Sn SRF"` / `"niobium-tin cavity"` → 39;
  4. `"superconducting cavity"` AND (accelerator OR CERN OR Fermilab OR JLab OR KEK) → 1018.
- **Поля:** id, doi, title, year, date, cited_by, abstract, authors(+institution), references, type, concepts.
- **Дедuп:** по id OpenAlex (в скрипте).
- **Мусор (грубо):** 84 записи «cavity» без SRF/Nb/accelerator-контекста (квант. оптика/общее) — 1.1%, на сигнал не влияет (проверено выборкой: PETRA/TRISTAN/KEK — на деле SRF-релевантны).
- **Типы:** article 4338, conference-paper 1832, preprint 556, report 407, dissertation 129...
- **Как восстановить:** `.venv/bin/python src/openalex_srf.py` (нужен доступ к api.openalex.org; OpenAlex free).
- **Расход:** OpenAlex ~30 запросов (free; в api_budget.md — с урока 010 про дневной 429 — остановок не было).
