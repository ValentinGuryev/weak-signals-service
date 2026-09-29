# TERMTECH_DESIGN — автоматический механизм дробления тем на технологии (v0, PILOT)

> **Заморожен 2026-09-25 ДО запуска пилота.** Автор утвердил архитектуру 25.09.
> Параметры ниже НЕ изменяются по результатам прогона: любой change = новая версия
> документа с причиной и датой (по образцу QA-регресса, methodology/QA_RETRIEVAL_PLAN).
> **Протокол антиподгонки:** механизм не видит QA-запросов и eval-списка; eval-список
> заморожен здесь же, ДО первого прогона; пороги — стандартные/литературные, не
> оптимизированные на 16 вопросах; sensitivity ±×2 по ключевым порогам обязателен
> в отчёте пилота.

## 1. Проблема и роль

Таксономия OpenAlex (4516 тем) — единицы «исследовательское направление», а не
«технология». Симптомы: (а) 3/16 технологий прямого запроса отсутствуют в выдаче;
(b) superconducting diode пропущен стандартными инструментами (arXiv-прецедент);
(в) технология на подъёме = доли процента работ темы → её рост агрегат темы не видит
(структурный false negative). TermTech добавляет уровень T2 «tech-единица» между
темой (T1) и работами (T3):

**T1 тема (4516) → T2 tech-единица (TermTech, именованная) → T3 работы.**

T2 = единица скрининга, выдачи и годовых серий; метрики novelty/growth/impact
считает существующий N×G×I без изменений (серия T2 = сумма серий её терминов).

## 2. Определение СП-среза (frozen)

Срез задаётся ДОМЕННО (пилот хакатона = сверхпроводимость), не запросом:

- **Правило:** темы таксономии, чей `display_name` матчит regex
  `superconduct|cryogen` (re.I, поле display_name, topics.parquet v 4516).
- **Результат (frozen, 6 тем):** T10037 Physics of Superconductivity and Magnetism,
  T11766 Iron-based superconductors research, T11803 Superconducting and THz Device
  Technology, T11808 Superconducting Materials and Applications, T12491 Superconductivity
  in MgB2 and Alloys, T13200 Spacecraft and Cryogenic Technologies.
- **Фильтры работ:** `list_has_any(topic_ids, {6 тем})` (любая тема, не только
  primary); `type IN` белый список NJ-1 (article, review, preprint, book-chapter,
  dissertation, book, letter, editorial, erratum, standard, report); `language='en'`
  (термин-мининг английский; не-англ. работы исключены — ограничение пилота,
  задокументировать в отчёте); годы **2016–2026** (горизонт T_stats).
- **Объём (замер 25.09):** 1 049 899 работ из 190 615 692 (~0.55%).
- **Источник текста:** `E:/openalex_derived/T_text/year=*/publication_year=*/data_0.parquet`
  (79 ГБ, колонки id, publication_year, title, abstract_inverted_index) — join с T_stats
  (локально) по id. Извлечение: `scripts/termtech_sp_slice.py`.

Известное ограничение правила: кейсы в квантовой нише (sc_qubits, topological_qubits)
могут жить вне 6 тем — для пилота не критично (eval-список §5 ограничён СП-доменом),
расширение regex = версия v1 с обоснованием.

## 3. Конвейер TermTech (5 шагов, параметры frozen)

**Шаг 1 — кандидаты-термины.** title + abstract (inverted index → текст), lowercase,
токены `[a-z0-9]+(?:[-+#.][a-z0-9]+)*` (co2, nb3sn, 2g-hts сохраняются); n-граммы
1–4 токена; граница — не-токен (предложение/пунктуация); рёбра n-граммы не содержат
стоп-слово (stoplist EN ~150, стандартная); числовые-only n-граммы отбрасываются.
Выход: для каждого термина — df (число работ), series по годам.

**Шаг 2 — ключность (collocation-фильтр).** Отбрасываем термины, не являющиеся
связной фразой: **kPMI ≥ 0.05**, где PMI = log P(t1..tn)/(∏P(ti)) на словах среза
(для униграмм шаг пропускается). Порог стандартный для collocation-фильтрации;
sensitivity ±×2 обязателен в отчёте. Дополнительно: **df ≤ 50% работ среза**
(отсекает общеупотребимое).

**Шаг 3 — эмердж-фильтр (выход в «технологии на подъёме»).**
- df ≥ **20** работ среза (min_df; ниже — шум одноразовых упоминаний);
- `first_year` = первый год с count ≥ 3;
- **growth** = (n[2023–2025]/3) / (n[2016–2022]/7 + 1); 2026 исключён из growth
  (неполный год), учитывается в df;
- ранжирование кандидатов по growth; флаг emerging = `first_year ≥ 2018`
  И n[2023–2025] ≥ 5.

**Шаг 4 — сшивка синонимов (СТАДИЯ 2, после пилота).** Эмбеддинг терминов (LaBSE,
локальный кэш, HF_HUB_OFFLINE=1) → консервативная кластеризация (cos ≥ 0.85) →
tech-единица = семантический кластер, каноническое имя = самый df-частотный термин.
В v0 пилота НЕ участвует (параметр кластеризации фиксируется при внедрении).

**Шаг 5 — метрики.** Серия tech-единицы = сумма серий её терминов; novelty/growth/
impact — существующий N×G×I (rank_directions_ngi) без модификаций.

## 4. Что НЕ входит в механизм (антиподгонка)

- Список §5 используется ТОЛЬКО для оценки recall, никогда как вход конвейера.
- QA-запросы q1–q4 не используются при построении/тюнинге TermTech.
- Ручная разметка — только валидация (выборочная), не источник инвентаря.

## 5. Eval: замороженный список технологий (recall-тест, ДО прогона)

Каждая технология: синонимы (то, что ДОЛЖЕН выдать термин-мининг, если технология
есть в срезе с df ≥ 20). Источник — CASE_REGISTRY (составлен ДО этой задачи).

| # | Технология | Синонимы-маркеры (frozen) |
|---|---|---|
| 1 | **СП-диодный эффект** ⭐ (известный пропуск) | superconducting diode; Josephson diode; superconducting diode effect |
| 2 | SNSPD | superconducting nanowire single-photon detector; nanowire single-photon |
| 3 | JTWPA | Josephson traveling-wave parametric amplifier; traveling wave parametric |
| 4 | Флакс-помпа | flux pump |
| 5 | IBAD-MgO | ion-beam assisted deposition; IBAD |
| 6 | RCE-DR | reactive co-evaporation; RCE |
| 7 | ВТСП-лента / coated conductor | coated conductor; REBCO tape; 2G HTS |
| 8 | MgB2 | MgB2; magnesium diboride |
| 9 | SMES | superconducting magnetic energy storage |
| 10 | No-insulation катушки | no-insulation; NI coil; no insulating |
| 11 | CORC кабели | CORC cable; conductor on round core |
| 12 | Токовые ограничители | superconducting fault current limiter; SFCL |
| 13 | Гидридные СП | superconducting hydride; hydrogen-rich supercond |
| 14 | Nb3Sn (зрелая контрольная) | Nb3Sn; niobium-tin |

**Критерий успеха пилота (frozen):**
1. **superconducting diode найден** (единица в кандидатах шага 3) — ключевой тест;
2. recall ≥ **10/14** по списку;
3. qualitative: топ-40 emerging-терминов просматривает автор (корректность);
4. sensitivity: recall не падает при ±×2 по df_min и kPMI.

Провал → честный отчёт, v2 с причиной изменения (не подгонка — документируем).

## 6. Артефакты и команды

- Извлечение среза: `scripts/termtech_sp_slice.py [--years 2026] [--smoke]`
  → `data/openalex_derived/sp_slice/sp_works.parquet` (id, year, title, abstract,
  topic_ids; language='en'; type-filter). Resume по годам.
- Мининг: `scripts/termtech_mine.py` → `results/termtech/candidates.parquet` +
  `results/termtech/eval_report.json` + топ-термины md.
- Логи: `results/runtime/termtech_*.log`; PID-файл (уроки план ночных работ).
- Ресурсы: чтение E: read-only (~79 ГБ, ~2–3 ч через 9p), mem ≤ 3GB, spill (если
  нужен) ТОЛЬКО E:/tmp_duck; одиночный процесс.

## 8. Отбраковка мусора T2 (добавлено 25.09, фильтр v0.1–v0.3)

**Почему:** пилот 25.09 показал, что топ по growth засорён НЕ-технологиями:
XML/MathML-разметкой из abstract'ов («xmlns a http», «math mrow»), copyright-строками
изданств («american physical society 2024»), affiliation-блоками («republic of china
email»), подписями к рисункам («image download powerpoint slide»), CSS/вёрсткой
(«display inline c»). Это артефакты восстановления текста и шаблоны документов,
а не технологии.

**Реализация:** `scripts/termtech_filter.py` — слой ВЫДАЧИ ПОСЛЕ frozen-конвейера
(параметры шагов 1–3 не меняются; вычитка `candidates.parquet` → `candidates_clean.parquet`).

| правило | что отсекает | пример |
|---|---|---|
| R1 markup | XML/MathML/TeX-токены | xmlns, math, mrow, msub |
| R2 year | токен-год 19xx/20xx, диапазоны | american physical society 2024 |
| R3 boilerplate | издательские/метаданные слова | published, proceedings, society |
| R4 stub | нет токена длиной ≥3 | c mi, e mi |
| R5 numeric | термин только из цифр | — |
| R6 css | фрагменты вёрстки | inline, div, class, style |
| R7 affil | affiliation/контакты + словослияния | republic of china email, workcorrespondence |
| R8 filler | общая академическая фразеология | valuable insights, findings underscore |
| R9 artifact | подписи/архивы/домены/сноски/годы-диапазоны | powerpoint slide, nsuworks.nova.edu, lotte jacobi, 0.16em |

**Протокол антиподгонки:** правила сформулированы как стандартные списки
документных артефактов, технологий из eval-списка §5 НЕ содержат и на QA-запросах
НЕ тюнинговались. **Маркерный тест целостности обязателен:** recall §5 ДО и ПОСЛЕ
фильтра должен совпасть (пилот 25.09: 12/14 → 12/14, отсеяно 10 596 из 94 584 = 11%).

**Выход:** `results/termtech/candidates_clean.parquet`, `top_terms_clean.md`,
`filter_report.json` (счётчик по правилам + recall до/после).

## 9. Гейт релевантности T1 (P1, 25.09)

См. следующий раздел (заполняется по результатам `scripts/sim_gate.py`).

## 10. Статусы версий

| версия | дата | что |
|---|---|---|
| v0 | 2026-09-25 | заморожен дизайн до пилота (этот документ) |
| v0 пилот | 2026-09-25 13:31 | ПРОГОН: recall **12/14**, superconducting diode **НАЙДЕН**, sensitivity 12/12/12 при ±×2 (df 40/10, kPMI 0.10/0.025); критерии 1–2 и 4 выполнены, критерий 3 (просмотр топ-40 автором) — на просмотре |
| v0.1 фильтр | 2026-09-25 13:35 | слой отбраковки мусора §8 (R1–R5): −7 001 термин, recall 12/14 |
| v0.3 фильтр | 2026-09-25 13:40 | R6–R9 добавлены: −10 596 терминов (11%), recall 12/14; топ emerging — реальные технологии (altermagnets, lk-99, bilayer nickelate, superconducting diode effect) |
