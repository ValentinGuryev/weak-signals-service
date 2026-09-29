# Паспорт данных: гранты CORC (кейс 009, S1d)

- **Файлы:** `data/raw/grants_foreign/nsf_corc_results.json` (132, из них 0 релевантных),
  `data/raw/grants_foreign/cordis_corc_results.json` (40, из них 11 contentType=project,
  3 релевантных кабельных).
- **Скрипт:** `src/grants_corc.py` (+ точечные дозапросы heredoc после обрыва сети).
- **Запросы:**
  - NSF (`api.nsf.gov/awards.json`, без ключа, rpp=25): "CORC conductor", "conductor on round core",
    "REBCO cable", "coated conductor cable", "superconducting cable fusion magnet", "round core superconductor",
    + точечно: "REBCO", "coated conductor", "YBaCuO coated conductor", "superconducting cable".
  - CORDIS (`cordis.europa.eu/api/search/results`, без ключа): 'CORC', 'REBCO cable',
    'coated conductor cable', 'superconducting cable', 'high temperature superconducting cable' (0),
    'fusion magnet cable' (0).
- **Дата сбора:** . **Число записей:** NSF 132, CORDIS 40.
- **Поля:** NSF — id, title, org, pi, amount, year (исправлен MM/DD/YYYY → год), start, abstract, url;
  CORDIS — id, acronym, title, programme, start/end (битые даты '1 {{month_09}} 2022'), teaser,
  country, contentType (фильтровать == "project"), url.
- **Как восстановить:** `.venv/bin/python src/grants_corc.py` (нужен доступ к api.nsf.gov и
  cordis.europa.eu; NSF/CORDIS — free API, без ключа).
- **Расход:** NSF ~16 запросов + CORDIS ~14 (free API, без квоты; залогировано в api_budget.md).

## Ограничения
- **NSF-канал для CORC ПУСТ** (0 релевантных из 132; шум: «corc»=Correlated-Electron/Organic Cycle,
  «cable»=power line). Причина: финансирование CORC в США идёт через **DOE (FES/SBIR)**, не NSF —
  как в кейсе 007 (JTWPA). NSF-числа НЕ читать как «США не финансировали».
- **CORDIS**: мусор по 'CORC' (биология: DeCoDe Platy, CancerCirculome — «CORC»-акронимы);
  реальные кабельные проекты — единицы (SCARLET, Super/Türkiye). «high temperature superconducting cable»
  и «fusion magnet cable» → 0 проектов.
- **DOE API** — недоступен (404/ключ, KNOWHOW); DOE-гранты — из литературы (отмечено в grant_signal).

## Дополнение v2 (2026-09-09): верификация по funding-блокам PDF

- **Метод:** grep по 11 PDF литературы кейса: `DE-SC/DE-FG/DE-AR` (DOE), «sponsored by»,
  «FUNDING», «supported by», Acknowledgments.
- **Находки (верифицированные номера DOE-грантов CORC):**
  - van der Laan 2013 (MT23, ACT): DOE FES STTR **DE-SC0007660**, DOE HEP SBIR **DE-SC0009545**,
    DOE HEP **DE-FG02-12ER41801** — финансирование CORC с 2012-13.
  - Ben Saâd 2025: DOE HEP DE-SC140009, ARPA-E DE-AR0001459, NSERC/Mitacs/CMC (Канада), DGAC (Франция).
  - Hartwig 2020 (VIPER): спонсор **Commonwealth Fusion Systems**.
  - Lyu 2025: JST SPRING JPMJSP2108. Tao 2024: NSFC 51977207/52207018 + CRAFT China. Sytnikov 2021: Росатом 313/1671-D.
- **Диссертации:** Bayer 2016 (KIT) — funding-абзаца нет (EUROfusion/F4E в тексте, KIT Scientific Publishing);
  Bykovskiy 2017 (EPFL, ResearchGate-версия) — funding-блока нет; CV: инженер ВНИИКП (Высоцкий) 2012-13 → EPFL SPC.

## Дополнение v3 (2026-09-09): патентная база грантополучателей (Lens, 13+ запросов)

- **Файл:** `data/raw/patents/cases/009_corc_grants.json` (116 патентов, 43 изобретения релевантных СП).
- **Скрипт:** `src/lens_corc_grants.py` (13 запросов: A ядро, B грантополучатели, C география, D импакт)
  + докачка ACT-семейств по известным номерам (title-фразы, +23 документа).
- **Дата:** 2026-09-09. API-вызовов: 13 (осн.) + ~6 (диагностика) + 5 (ACT-семейства) = ~24.
- **Лимиты/уроки Lens:**
  - Поле `biblio.legal_status` — НЕ существует (HTTP 400, «Unrecognized fields»).
  - Фильтр по `applicants`/`applicant_name`/`assignee` = 0 для ACT (match по многословным не работает);
    спасло — точечные title-фразы по известным номерам из Google-данных.
  - A1 (title CORC) ловит фарм-мусор (WYETH/MERCK «CORC»=акроним) — нужна чистка по abstract.
- **Поля:** publication_number, title, abstract, assignee, inventor, даты, cited_by_n, tags, url.
- **Как восстановить:** `.venv/bin/python src/lens_corc_grants.py` + блок ACT-семейств (heredoc).
