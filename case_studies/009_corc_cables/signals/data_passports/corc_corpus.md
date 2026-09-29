# Паспорт данных: корпус публикаций CORC (кейс 009)

- **Файл:** `data/raw/openalex/corc_corpus.json` (вне git, как data/raw).
- **Скрипт:** `src/openalex_corc.py`.
- **Запросы (OpenAlex title_and_abstract.search, OR):**
  1. `"CORC cable" OR "CORC wire"`
  2. `"CORC" AND ("REBCO" OR "HTS" OR superconductor OR "round core")`
  3. `"conductor on round core"`
- **Дата сбора:** . **Число записей:** 353 (после дедупликации по id).
- **Метод:** cursor-пагинация, per-page=200, ПОЛНЫЙ select за 1 проход:
  id, doi, title, display_name, year, date, cited_by_count, abstract_inverted_index (→abstract),
  authorships (→ authors с аффилиациями), referenced_works (→ references), type, concepts.
  (source нельзя в select — 400 OpenAlex; журнал не сохранён.)
- **Полнота:** abstract 298/353 (84%), авторы 353/353, references 309/353 (87%).
- **Как восстановить:** `.venv/bin/python src/openalex_corc.py`.
- **Расход OpenAlex:** ~9 запросов (3 запроса × ~2-3 страницы). Лимита нет (только rate-limit),
  в api_budget не логируется (OpenAlex без квоты на число).

## Содержание полей записи
- id, doi, title, year, date, cited_by (цитаты), abstract (реконструирован),
- authors: [{name, institution}] (первые аффилиации), references: [OpenAlex id],
- type (article/review/...), concepts: [display_name].

## Ограничения
- Запрос «CORC» отдельно НЕ использован (аббревиатура ловит мусор: cell types и пр.).
- 12 работ — соседние темы (HTS-ленты, CICC, ASCEND-авиация) — пересекаются, не мусор;
  чистка по смыслу — при S2/S3-анализе.
- 1992: 1 ранняя работа (не CORC-кабель, артефакт «round core»?) — проверить.
