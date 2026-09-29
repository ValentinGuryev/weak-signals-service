# Патентный сигнал: ibad_tapes

> ⚠️ **АКТУАЛИЗИРОВАНО :** ниже — старое окно (2006-2018, Google 300/28).
> Свежие данные (полное окно 1995-2026, 100 патентов, Google+Lens) — в §0 ниже.
> Полный датасет: `data/raw/patents/topics_window/ibad_merged.json`.
> **Объединённая база кейса ():** `data/raw/patents/cases/001_ibad_mgo.json` (632 патента, все окна/источники, дедупл.).

## 0. АКТУАЛЬНО (): полное окно 1995-2026, 100 патентов

- Источники: Google (ibad_tapes_wide) + Lens (5 технологий), объединены, 0 дубликатов
- Фильтр: маркер IBAD/RABiTS/ISD + SC-контекст (0 ложных); 11 ручных добавлено
- **Пик 2009 (22 патента)** — совпадает с пиком публикаций (см. NARRATIVE §4)
- Вторая волна 2018 (9) — китайская

### Динамика (priority_year)

| Год | Патенты | | Год | Патенты |
|---|---|---|---|---|
| 1995 | 1 | | 2013 | 5 |
| 1997 | 1 | | 2014 | 3 |
| 1998 | 1 | | 2016 | 5 |
| 1999 | 1 | | 2018 | 9 |
| 2000 | 1 | | 2019 | 2 |
| 2001 | 1 | | 2021 | 2 |
| 2002 | 2 | | 2022 | 2 |
| 2003 | 2 | | 2024 | 1 |
| 2004 | 10 | | 2026 | 1 |
| 2005 | 5 | | | |
| 2006 | 1 | | | |
| 2007 | 1 | | | |
| 2008 | 2 | | | |
| **2009** | **22** | | | |
| 2010 | 8 | | | |
| 2011 | 9 | | | |
| 2012 | 2 | | | |

### География (страна заявителя) — диффузия US→JP→CN

| Волна | US | JP | CN | KR | EU |
|---|---|---|---|---|---|
| 1995-2008 | 15 | 5 | 0 | 2 | 2 |
| 2009-2012 | 8 | 28 | 1 | 2 | 0 |
| 2013-2026 | 4 | 2 | 20 | 2 | 2 |

### Топ заявителей (нормализовано)

| Заявитель | Патентов |
|---|---|
| **Fujikura** | 23 |
| UC (Foltyn et al.) | 7 |
| UT-Battelle/ORNL | 6 |
| LANL | 5 |
| Shanghai Superconductor | 5 |
| SuperPower | 4 |
| ANL/Chicago | 4 |
| SWCC/Showa | 4 |
| Univ Houston | 4 |
| ISTEC | 4 |
| Furukawa | 3 |
| SAMRI | 3 |
| UESTC | 3 |

---

# (исторический документ, окно 2006-2018, Google 300/28)

- Запрос: `"IBAD" OR "ion beam assisted deposition" OR "MgO template" superconducting`
- Патентов: 300
- Релевантных: 28 (9%), нерелевантных: 272

## Динамика по годам (priority_date)

| Год | Патенты | Крупные игроки | Университеты/НИИ | Прочие |
|---|---|---|---|---|
| 2006 | 13 | 4 | 2 | 7 |
| 2007 | 16 | 4 | 0 | 12 |
| 2008 | 26 | 6 | 0 | 20 |
| 2009 | 38 | 11 | 1 | 26 |
| 2010 | 39 | 17 | 3 | 19 |
| 2011 | 50 | 16 | 2 | 32 |
| 2012 | 27 | 8 | 3 | 16 |
| 2013 | 23 | 4 | 2 | 17 |
| 2014 | 12 | 0 | 2 | 10 |
| 2015 | 18 | 3 | 3 | 12 |
| 2016 | 16 | 9 | 4 | 3 |
| 2017 | 12 | 4 | 2 | 6 |
| 2018 | 10 | 3 | 3 | 4 |

## Заявители

- Крупные игроки: **89**
- Университеты: 17
- Институты/НИИ: 10
- Прочие (вкл. китайские): 184

### ТОП-10 заявителей

| Заявитель | Патентов |
|---|---|
| 株式会社フジクラ | 51 |
| Fujikura | 37 |
| Furukawa | 21 |
| 上海超导科技股份有限公司 | 9 |
| Sumitomo | 8 |
| Toshiba | 8 |
| AMSC | 6 |
| Furukawa Electric Co., Ltd. | 5 |
| 公益財団法人国際超電導産業技術研究センター | 5 |
| Ut-Battelle, Llc | 5 |

## Примеры патентов по годам

- **2015** ⚠️ WO2017105029A1 — Method for manufacturing superconductive wire material having supercon (한국전기연구원)
- **2009** ⚠️ WO2011052552A1 — Tape base material for a superconducting wire rod, and superconducting (古河電気工業株式会社)
- **2018** ⚠️ RU2696182C1 — High-temperature superconducting tape manufacturing method and tape (Общество С Ограниченной Ответс)
- **2007** ✅ US20090036313A1 — Coated superconducting materials (Liliana Stan)
- **2010** ⚠️ JP5730541B2 — Method for manufacturing substrate for superconducting wire, and metho (古河電気工業株式会社)
- **2008** ⚠️ JP5145109B2 — &hellip;  polycrystalline thin film and method for producing oxide sup (株式会社フジクラ)
- **2011** ⚠️ US9136046B2 — Superconducting wire rod and method for manufacturing superconducting  (Furukawa Electric Co., Ltd.)
- **2012** ⚠️ US9362025B1 — Coated conductor high temperature superconductor carrying high critica (Superconductor Technologies, I)
- **2006** ⚠️ US20070197395A1 — Method of patterning oxide superconducting films (American Superconductor Corpor)
- **2013** ⚠️ WO2015037846A1 — Superconductor and method of manufacturing same (주식회사 서남)
- **2017** ⚠️ CN110344008B — Pulse laser coating device (上海超导科技股份有限公司)
- **2014** ✅ CN103985479B — Preparation method of high-temperature superconducting coated conducto (赵遵成)
- **2016** ⚠️ US11501899B2 — Oxide superconductor and method for manufacturing the same (Kabushiki Kaisha Toshiba)