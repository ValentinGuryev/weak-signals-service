# Паспорт: jtwpa_corpus.json + jtwpa_census.json

- **Файлы:**
  - `data/raw/openalex/jtwpa_corpus.json` — корпус (331 после дедупа: A-ядро=265, B-KITWPA=66)
  - `data/raw/openalex/jtwpa_census.json` — ценз всего пространства TWPA (442 работы, классифицированы)
  - `data/raw/openalex/jtwpa_full.json` — абстракты+references (331, 290 с абстрактом)
  - `data/raw/openalex/jtwpa_counts.json` — counts по годам
  - `data/raw/openalex/jtwpa_competitors_full.json` — counts конкурентов (SNAIL/графен/HEMT/трансдукция)
- **Скрипты:** `src/openalex_jtwpa.py` (сбор+классификатор), `src/openalex_jtwpa_census.py` (ценз),
  `src/openalex_jtwpa_full.py` (абстракты), `src/plot_s1a_jtwpa.py` (график)
- **Запросы:** title_and_abstract.search: "traveling/travelling-wave parametric amplifier" (442),
  "Josephson parametric amplifier" (резонаторные JPA), 12 синонимов core/KIT + 8 конкурентных запросов
- **Дата:**  (v1),  (v2 — ценз, полное покрытие)
- **Поля:** id, title, year, cited_by, class, authors (name/inst/country), source; census: + класс
  (A_josephson/A_squid/A_snail/B_kinetic/C_JPA_res/NONSC/TWPA_unspecified/APPL)
- **Классы корпуса:** A = джозефсоновские проточные TWPA (ядро, кейс); B = KITWPA (кин. индуктивность, сосед)
- **Бюджет:** OpenAlex (~150 запросов суммарно, без лимита на число; прямой доступ)
