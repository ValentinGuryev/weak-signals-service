# Паспорт: корпус sc_aircraft_motors (OpenAlex)

- **Файл:** `data/raw/openalex/sc_aircraft_motors_corpus.json`
- **Тема:** сверхпроводящие моторы/машины/пропульсия для авиации (кейс 008)
- **Скрипт:** `src/openalex_sc_aircraft.py`
- **Запросы ядра (Q_CORE, 5):**
  - "superconducting motor" (aircraft OR aviation OR aerospace OR flight)
  - "superconducting machine" (aircraft OR aviation OR aerospace)
  - "superconducting propulsion" (aircraft OR aviation OR aerospace)
  - "high temperature superconducting" (motor OR machine OR propulsion) (aircraft OR aviation OR aerospace)
  - "superconducting" (motor OR machine) "electric aircraft"
- **Select (полный, 1 проход):** id,title,publication_year,cited_by_count,abstract_inverted_index,
  referenced_works,authorships,primary_location,concepts (⭐ оптимизация : без *_full докачки)
- **Дата:** 
- **Работ:** 453 (ядро, после классификатора core/шум инлайн)
- **Классификатор:** `classify()` — сверхпровод + мотор/машина/пропульсия + авиация (в title/abstract)
- **Поля записи:** id, title, year, cited_by, abstract, referenced_works, authors(name/country/inst), source, doi
- **Counts:** `sc_aircraft_motors_counts.json` (core), `sc_aircraft_competitors_counts.json` (6 конкурентов)
- **Восстановление:** `.venv/bin/python src/openalex_sc_aircraft.py` (~7 запросов + пагинация)
- **⚠️ Бюджет:** OpenAlex лимитирует число запросов — при пересборке согласовать с автором.
