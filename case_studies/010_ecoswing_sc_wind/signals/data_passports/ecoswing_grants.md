# Паспорт данных: гранты EcoSwing / СП-ветрогенераторы (кейс 010, S1d)

- **Файлы:**
  - `data/raw/grants_foreign/nsf_ecoswing_results.json` — NSF (91, из них 0 прямо релевантных);
  - `data/raw/grants_foreign/cordis_ecoswing_results.json` — CORDIS (17, из них contentType=project: 2 + 1 HIVOMOT);
  - `data/raw/grants_foreign/kaken_ecoswing.json` — KAKEN живой поиск (60, из них ветер-релевантных 0, класс «СП-машины» — 1: Kyoto HTS-ISM);
  - РНФ — локальная база `data/raw/rnf/rnf_cards.json` (407, ветер-специфичных 0, класс «СП-электрические машины» — 5).
- **Скрипт:** `src/grants_ecoswing.py` (NSF + CORDIS; свободные API без ключа) + heredoc-запросы CORDIS (INNWIND/UpWind/SUPRAPOWER/смежные), KAKEN — на функциях `src/grants_kaken.py`, detail-страницы CORDIS — urllib (656024, 723119).
- **Запросы:**
  - NSF (`api.nsf.gov/awards.json`, без ключа, rpp=25): "EcoSwing", "superconducting wind",
    "superconducting wind turbine", "superconducting wind generator", "superconducting generator",
    "superconducting machine", "high temperature superconducting generator".
  - CORDIS (`cordis.europa.eu/api/search/results`, без ключа): 'EcoSwing', 'superconducting wind',
    'superconducting wind turbine', 'superconducting wind generator', 'superconducting electrical machine',
    'superconducting machine', 'INNWIND', 'SUPRAPOWER' + доп. 'INNWIND.EU', 'UpWind', 'superconducting energy',
    'superconducting wind energy' (0), 'wind generator superconducting' (0), 'HIVOMOT'.
  - KAKEN (`kaken.nii.ac.jp/en/search/`, живой HTML): "superconducting wind", "superconducting generator",
    "superconducting electrical machine" (по 2 страницы).
  - CORDIS detail-страницы: `cordis.europa.eu/project/id/656024`, `/723119` (полные бюджеты, координаторы).
- **Дата сбора:** . **Число записей:** NSF 91, CORDIS 17, KAKEN 60.
- **Поля:** NSF — id, title, org, pi, amount, year, abstract, url; CORDIS — id, acronym, title, programme,
  start/end (битые даты `1 {{month_03}} 2015` — восстанавливать с detail-страницы), teaser, country,
  contentType (фильтровать == "project"), url + detail (бюджет EU-вклада для 656024/723119);
  KAKEN — grant_number, category, institution, pi, period, status, abstract (японский), url.
- **Как восстановить:** `.venv/bin/python src/grants_ecoswing.py` (+ heredoc по рис. выше; KAKEN — модуль
  `grants_kaken.fetch_kaken`). NSF/CORDIS/KAKEN — free, без ключа.
- **Расход:** NSF 7 запросов + CORDIS ~17 (API+detail) + KAKEN 6 страниц — free API (в api_budget.md).

## Ограничения и уроки канала
- **NSF ПУСТ (0 релевантных из 91)** — канал-артефакт, как в кейсах 007/008/009: в США СП-ветрогенераторы
  финансировались через **NIST ATP** (подтверждено PDF литературы кейса: Snitchler 2011 «Under a program
  funded by the NIST-Advanced Technology...») и DOE-каналы, а НЕ через NSF API. NSF-числа НЕ читать как
  «США не финансировали».
- **CORDIS API НЕ индексирует старые рамочные проекты:** UpWind (2006-11), INNWIND (2013-17),
  SUPRAPOWER — через API не находятся (0/шум), хотя проекты реальны (подтверждены литературой кейса —
  Shah 2025, roadmap_signal). Для них используем литературу, НЕ API.
- **EcoSwing в CORDIS есть** (id 656024, Дания, 2015-2019, €13.85M всего / €10.59M EU-вклад) —
  главный фактический якорь грантового сигнала.
- **KAKEN:** ветер = 0; нашёлся только класс «СП-электрические машины» (Kyoto HTS-ISM 2024, 3 кВт, 99%).
- **NSFC (Китай):** в локальной базе (129) 0 ветер-специфичных (все REBCO-хиты — магниты/фьюжн) —
  живая проверка NSFC не делалась (затратна), отметить как ограничение.