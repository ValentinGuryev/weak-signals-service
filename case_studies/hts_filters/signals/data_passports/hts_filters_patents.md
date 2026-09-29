# Паспорт данных: патенты HTS-фильтров (кейс hts_filters, S1b)

- **Файл:** `data/raw/patents/cases/hts_filters.json` (80 уник. → 74 релев. → 70 изобретений).
- **Скрипт:** `src/lens_hts_filters.py` (4 запроса) + `src/lens_hts_filters_topup.py` (5 запросов-пагинация).
- **Дата:** . **API:** Lens.org patent/search, Bearer-токен из .env.
- **Запросы:**
  - A1 "superconducting filter"|"HTS filter"|"high temperature superconducting filter" (total=510 — оказыв. в основном семейные переводы; страницы p1-p5 собраны, новых = 3 из 160 → база НАСЫЩЕНА);
  - A2 "YBCO filter"|"superconducting microwave filter"|"superconducting bandpass"|"preselect"|"duplexer" (44+30);
  - A3 "superconducting power extractor"|"receive filter" (1);
  - B1 игроки: Tsinghua/Zongyi/Tianjin/Conductus (3).
- **Поля:** publication_number (jur_doc), title, abstract, assignee, inventors, year, relevant (bool), invention-маппинг в анализе.
- **Дедуп:** уровень 1 = publication_number (80 уник.); уровень 2 = (assignee + ядро title) → 70 изобретений. Переводы по юрисдикциям (EP/переводы CN/DE) схлопнуты (урок Р2).
- **Релевантность:** filter/bandpass/preselect/duplexer/microwave/resonator + СП. Исключён мусор: CMOS-устройство, «cavity cooling», «link system», ADC (не фильтры).
- **Ограничение:** A1 total=510 (в счётчике Lens), однако дополнительные страницы дали лишь +3 новых — база собрана практически полностью (насыщение).
- **Как восстановить:** `.venv/bin/python src/lens_hts_filters.py && .venv/bin/python src/lens_hts_filters_topup.py`.
- **Расход:** 9 запросов (≈131/мес остаток по заголовкам ).

## v2 (, конец сессии) — СТАТУС: база собрана, ФИЛЬТР ТРЕБУЕТ ФИНАЛЬНОГО ПРОХОДА
- **Что успели:** полный дособор для ПОЛНОТЫ (lens_hts_filters_full.py: 8 пагинаций A1 до 510 + 9 новых
  слоёв N1-N9) + слияние. **База: 162 уникальных → 137 релев. (автомат. фильтр) → 131 изобретение.
  Остаток Lens по заголовкам: 108/мес.**
- **НЕ успели / незакрытые вопросы (для след. сессии):**
  1. **Релевантность требует РУЧНОГО прохода**: автоматический фильтр (relevant=True/False) местами
     срабатывал ложно. Замечено: «FDD (Frequency Division Duplex) HTS RF front end» (TIANJIN 2009),
     «Low-insertion-loss duplexer» (Guangzhou 2010), «FDD multi-system HTS RF» (Nanjing 2016),
     «Tower mountable cryocooler and HTSC filter system» (1998 ×3) — РЕАЛЬНЫЕ телеком-фильтры,
     но регексп их пометил rel=False (зацепил HARD-слова: digital.analogue/и др. в абстракте).
     Также «COOLING SYSTEM OF HTS FILTER» (1999) и крио-фильтры — релевантны, но мой ранний
     junk-фильтр (water/boiler/…) их выбивал; ПОСЛЕДНИЙ проход (137) — уже без water/boiler,
     НО всё равно требует ручной сверки краёв.
  2. **Бытовой мусор нефильтровано-подтверждается**: водогрейки/котлы/солнечные теплотрубки с
     «superconductive» (N8-слой) — отсеяны автоматически, но не проверены по одному.
  3. **Семейный дедуп 131 изобретение** — из них переводы по юрисдикциям (Murata ×13! переводы
     EN/DE/FR/JP одного изобретения) — НЕ все схлопнуты идеально (якорь по 6 словам не идеален).
  4. **Анализ/график/patent_signal.md НЕ перестроены под финальную базу (задача была — полнота JSON).
- **Расход Lens по кейсу**: 4 (осн) + 5 (топуп) + 17 (full) = 26 запросов. Остаток 108/мес (2026-09-11).
- **Как продолжить:** переписать rel-правило (дуплексеры/крио-фильтры = релевантны; бытовые =
  мусор), вручную сверить ~25 краёв из «НЕ-релевантных», пересобрать изобретения, затем patent_signal.md.
