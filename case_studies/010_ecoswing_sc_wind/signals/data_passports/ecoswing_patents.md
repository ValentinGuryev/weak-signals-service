# Паспорт данных: патенты EcoSwing / СП-ветрогенераторы (кейс 010, S1b)

- **Файл:** `data/raw/patents/cases/010_sc_wind.json` (117 изобретений; 77 релевантных; 283 raw-строки до дедупа).
- **Скрипт:** `src/lens_ecoswing.py` (API lens.org patent/search, Bearer-токен из .env).
- **Запросы (, 8 логических):**
  - A1 title/abstract "superconducting wind turbine" (25);
  - A2 "superconducting wind generator"|"wind power superconducting" (6);
  - A3 "high temperature superconducting wind"|"HTS wind generator" (12);
  - A4 superconducting generator + wind/offshore (title) (65 — широко, взято 40);
  - B1 "superconducting electrical machine"|"superconducting machine" (331 — взято 40);
  - B2 "superconducting generator" (478 — взято 40);
  - C1 EcoSwing|SUPRAPOWER (0 — ни один проект не патентует!);
  - C2 термины игроков KEPCO/Changwon/AMSC/Envision (0).
- **Дедуп:** уровень 1 = `{jurisdiction}_{doc_number}` (fallback: title+assignee); уровень 2:
  (assignee+норм.title) — в данных assignee отсутствуют (parties не отдаёт), поэтому уровень 2
  не влияет; счёт идёт по изобретениям (уровень 1).
- **Поля:** publication_number (jur_doc), title, abstract, assignee (пусто — ограничение API),
  inventors, cited_by, year (из priority_claims.earliest_claim.date), url.
- **Ограничение:** assignee пуст (Lens API не отдал parties.assignees в данном прогоне) —
  игроки реконструированы по юрисдикции номера (CN/US/KR/JP/EP/GB/CA/PL/RU/TW) и названию.
- **Как восстановить:** `.venv/bin/python src/lens_ecoswing.py` (нужен LENS_TOKEN; ~12-16 запросов).
- **API-бюджет:** 8 логич. + 2 диагностики + 1 тест = ~12-16 вызовов Lens (залогировано).

## Дополнение (2026-09-11, v2)
- Повторный прогон с исправленным парсингом parties (assignee = parties.applicants[].extracted_name.value —
  поле НЕ `assignees`!). СПАСИБО за замечание про игроков.
- Итог final: 109 изобретений, 53 релевантных (фильтр: СП+ветер в title/abstract; ДО-ВТСП LTS-машины
  без ветра — excluded, rel=false).
- Новые поля: `relevant` (bool), `player_type` (company/research_institute/government/individual/other),
  `assignee_norm` (агрегация GE).
- **GE (General Electric) — монополист ветро-СП патентов: 22/53 (42%)!** (алиасы GEN ELECTRIC +
  GENERAL ELECTRIC RENOVABLES объединены). Далее: UNIV HUNAN 3, Cooper Willard 2, Jeju Nat Univ 2+...
- Лимит Lens: **НЕ исчерпан** — 401 в первой попытке был из-за неверной схемы авторизации (Token →
  Bearer), а не лимита. Остаток ~410-415/1000.

## Дополнение (2026-09-11, v3 — аудит релевантности + слив ручных патентов)
- **⚠️ Аудит: база ЗНАЧИМО очищена от не-ветрового.** Ложные включения исправлены:
  - 1970-е (GB IRD/Siemens) + 80-90-е (JP New Sunshine: Toshiba/Mitsubishi/Tokyo Shiba; CA EPRI)
    — LTS-машины общего назначения, НЕ ветро → **rel=false** (правило: year<2000 → false).
  - JP_31616487 (1987, Toshiba «TURNING DEVICE») ловился по «turbine» = ГАЗОВАЯ турбина → false.
  - Осталась чистая волна ВТСП-ветра: 2004-2026.
- **Итог: 115 патентов (49 Lens-rel + 3 manual-rel + 63 не-рел. контекст), 52 релевантных.**
- **Слиты ручные Google Patents (`patents.google.manual/*sc_wind*`, §4.2c):**
  - ✅ Релевантны ветру (добавлены, source=manual): US_7843094 (Goodzeit 2010 dual-armature wind gen),
    US_8084909 (Goodzeit 2011), US_8040012 (AML/Meinke 2009 double-helix wind turbine claim).
  - ❌ НЕ-ветер (добавлены с rel=false для контекста): US_8575790 (Ogilvie 2013 «electrodynamic turbine»,
    wind=0 в тексте — тег sc_wind ложный), KR_20100044396 (KERI 2010 СП-мотор, 풍력=0), CN_111431406
    (SJTU 2020 крио-конвертор).
  - ⚠️ 3 скана без текстового слоя (CN102969873A, US12040129, WO2005060071A2) — их первые теги
    sc_aircraft_motors/cryocoolers (не ветер), помечены `manual_skipped_scans`; OCR не проводился.
- **Поля:** + source (lens|manual), relevant, player_type, assignee_norm, owners.
- Патентная картина по игрокам (52 релев.): **GE 22 → UNIV HUNAN 3 → Jeju Nat.Univ 2+2 → Goodzeit 2
  (++AML 1) → дальше по 1.** ТНК 59%, НИИ 26% — см. patent_signal.md.

## Дополнение (2026-09-11, v6 — AMSC + расширение ядра, ЛИМИТ Lens ИСЧЕРПЫВАЕТСЯ)
- **AMSC: 0 патентов** (проверено 6 запросами: "American Superconductor" как термин, "AMSC"+wind,
  старое написание "superconductive wind"×2, HTS wind generator, SC wind energy) — НИ ЗАЯВИТЕЛЕМ,
  НИ В ТЕКСТЕ. → AMSC **не патентовала ветро-СП** (10MW программа NIST ATP — грант без патентования).
- **+28 записей из AM3-AM6** (старое написание "superconductive wind", SC wind energy):
  - **DONGFANG Electric Corp (китайский ветро-ТНК) — 4 патента 2011-13** (offshore SC wind gen) — НОВЫЙ игрок!
  - **MIT + Commonwealth Fusion Systems — 3 патента 2021** (cooling system for SC wind power generator!)
  - State Grid Jiangsu (2021), Guangdong Ocean Univ (2020), Nanjing Posts&Telecom (2022-23), Ningbo Jianxin (2026).
- **БАЗА ТЕПЕРЬ: 114 записей, 56 релевантных** (после family-дедупа — меньше; дедуп по invention — при ШАГ 8).
- **Остаток Lens (по заголовкам ответа 2026-09-11): ~178 запросов/мес** до 2026-09-30. Расход с 09-09
  был выше логированного (~250 вкл. пагинации/повторы). ТРИАЛ заканчивается через 2 дня → стратегия «сжечь».

## Дополнение (2026-09-11, v7 — ФИНАЛ: +AMSC-пакет +topup 26 запросов)
- **AMSC = 0 патентов** (6 запросов: "American Superconductor", "AMSC"+wind, "superconductive wind"×2, HTS wind gen, SC wind energy) — ни заявителем, ни текстом. Не патентовала ветро-СП.
- **Topup 20 запросов** (пагинации A4/B1/B2, C-термины, D-азиат., E-компоненты, V-игроки):
  - Новые игроки: **DONGFANG Electric (CN ветро-ТНК, 4 пат.), MIT+Commonwealth Fusion Systems (3, 2021!), Guodian United Power (2), State Grid Jiangsu/Hunan, Henan Polytechnic (3), Nanjing Posts&Telecom (2), Guangdong Ocean, Tianjin Huaxia Cable, Ningbo Jianxin**.
  - C2 "superconducting wind powered" +20; E3 cryogenic-wind +8; V4 offshore+SC +25 — остальное 0 (REBCO-wind, HTS-wind-machine, CN/KR ключи — пусто).
  - V1 (Envision) — запрос вышел с 97603 = мусор (bool-синтаксис), релевантных 0.
- **БАЗА: 192 записи / 87 релевантных (по публикациям) / ~44 изобретения (после GE-family-дедупа).**
- **Расход Lens за 2026-09-11: ~26 (AMSC 6 + topup 20) + ранние ~14×4 прогона. Остаток: 152/мес (по headers).**
