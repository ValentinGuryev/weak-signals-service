# Патентный сигнал: corc_cables

- Запрос: `"CORC" OR "conductor on round core"`
- Патентов: 300
- Релевантных: 180 (60%), нерелевантных: 120

## Динамика по годам (priority_date)

| Год | Патенты | Крупные игроки | Университеты/НИИ | Прочие |
|---|---|---|---|---|
| 2006 | 15 | 2 | 3 | 10 |
| 2007 | 18 | 2 | 0 | 16 |
| 2008 | 15 | 2 | 2 | 11 |
| 2009 | 26 | 0 | 3 | 23 |
| 2010 | 21 | 0 | 1 | 20 |
| 2011 | 32 | 1 | 2 | 29 |
| 2012 | 26 | 1 | 4 | 21 |
| 2013 | 33 | 2 | 1 | 30 |
| 2014 | 24 | 4 | 1 | 19 |
| 2015 | 22 | 5 | 1 | 16 |
| 2016 | 26 | 4 | 1 | 21 |
| 2017 | 26 | 9 | 4 | 13 |
| 2018 | 16 | 1 | 2 | 13 |

## Заявители

- Крупные игроки: **33**
- Университеты: 16
- Институты/НИИ: 9
- Прочие (вкл. китайские): 242

### ТОП-10 заявителей

| Заявитель | Патентов |
|---|---|
| Intel | 14 |
| Qualcomm | 8 |
| Advanced Conductor Technologies Llc | 6 |
| Nomaco Inc. | 5 |
| Interdigital Patent Holdings, Inc. | 5 |
| Noxopharm Limited | 5 |
| Fujifilm Corporation | 4 |
| Proionic Gmbh | 3 |
| Bristol-Myers Squibb Company | 3 |
| 富士フイルム株式会社 | 3 |

## Примеры патентов по годам

- **2018** ✅ US11587701B2 — Series-connected superconducting magnet cables (Advanced Conductor Technologie)
- **2017** ✅ US10593444B2 — Self-monitoring superconducting cables having integrated optical fiber (North Carolina State Universit)
- **2013** ✅ US20140302997A1 — Superconducting Power Cable (Makoto Takayasu)
- **2011** ⚠️ US10774690B2 — Compact energy cycle construction utilizing some combination of a scro (Air Squared, Inc.)
- **2016** ✅ ES2781474T3 — Heterocyclic amides useful as protein modulators (Glaxosmithkline Ip Dev Ltd)
- **2014** ✅ US10254645B2 — Photosensitive resin composition, method for producing cured film, cur (Fujifilm Corporation)
- **2009** ✅ US8356373B2 — Unitary composite/hybrid cushioning structure(s) and profile(s) compri (Noel Group Llc)
- **2015** ✅ CA3001291C — Antenna structure for exchanging wireless signals (At&T Intellectual Property I, )
- **2007** ⚠️ EP2683051B1 — Contactless multi-charger system and controlling method thereof (Intel Corporation)
- **2006** ✅ EP1923028B1 — Three-dimensional apertured film for transmitting dynamically-deposite (Tredegar Film Products Corpora)
- **2010** ⚠️ CA2795139C — Fibrous structure with absorbency, barrier protection and lotion relea (The Procter & Gamble Company)
- **2008** ⚠️ CA2722455C — Shape-memory self-retaining sutures, methods of manufacture, and metho (Angiotech Pharmaceuticals, Inc)
- **2012** ⚠️ CA2884848C — Benzamide and heterobenzamide compounds (Pfizer Inc.)
---

## ⭐ Распределение патентов по годам (обновление 2026-09-09)

**Файл:** `plots/corc_patents_by_year.png` (стек по игрокам + кумулятивно). Чистые CORC-документы: **54**
(объединение lens_grants 116 + google_window 300 + recall 43, дедуп по норм.номеру, чистка фармы/телеф. кабеля).

### По годам приоритета

| Год | Патенты | Кто |
|---|---|---|
| **2013** | **8** | **ACT 7** + Takayasu 1 (рождение CORC, сразу после DOE SBIR Ph1 2012!) |
| 2014 | 1 | Rey (индивид.) |
| 2015 | 2 | ACT (cable machine) |
| **2018** | **13** | **ACT 9** (magnet/quench/power) + Китай-энергетика 4 |
| 2020 | 3 | Ун-ты Китая 2 + компании 1 |
| 2021 | 6 | **NKT 5** (совместный power cable) + кит. компании |
| 2022-23 | 3 | кит. компании/ун-ты/Hefei |
| **2024** | **10** | **Китай доминирует**: Jiaotong 6, энергетика 2, Hefei 2 |
| 2025-26 | 8 | Hefei/энергетика/Jiaotong/компании |

### Кумулятивно
- **К 2018 (окно): 24 патента** — уже заметный портфель (ACT 18 из них)
- 2021: +NKT (35) → 2024: взрыв Китая (48) → 2026: 54

### Чтение для кейса
1. **Патентный сигнал 2018 = сильный**: 24 документа, из них **ACT (DOE-грантополучатель) 18** —
   непрерывно 2013→2018. Это подтверждает: грант DOE (2012) → патенты (2013-18) → зрелость к окну.
2. **Китай в 2018 = 4** (энергетика, CRAFT) — только входит; **взрыв 2024+** (вторичные патенты) — догоняет.
3. **NKT (2021)** — совместный патент = выход ACT в энергетику (маркер коммерциализации).
4. **География-паттерн:** США (ACT) — базовый IP 2013-2018; Китай — вторичный 2024+; Европа — NKT 2021.
5. ⚠️ **Полнота ограничена** (~54 из ~80-100 реальных): ACT-семейства без «CORC» в абстракте добирались
   вручную; CN-патенты без латинского термина могли уйти. Для строгих долей — нужен полный сбор.
