# Wishlist — статьи для кейса IBAD-MgO

> Правило: только документы, которых у нас НЕТ. Скачанные → в `literature/` кейса, строки вычищаются.
> Проверено : в `literature/` и `case_studies/*/literature/` IBAD-статей нет — все пункты актуальны.

## К скачиванию

| # | Статья | Год | DOI | Релевантность | Статус | Почему |
|---|--------|-----|-----|---------------|--------|--------|
| 1 | Arendt & Foltyn — Biaxially Textured IBAD-MgO Templates for YBCO-Coated Conductors | 2004 | 10.1557/mrs2004.160 | 5/5 (!!!) | 📥 | Ключевой обзор (194 цит.), определяет архитектуру шаблона |
| 2 | Wang et al. — Deposition of in-plane textured MgO on amorphous Si₃N₄ by IBAD | 1997 | 10.1063/1.120227 | 5/5 (!!!) | 📥 | Фундамент метода (295 цит.), IBAD-MgO vs IBAD-YSZ |
| 3 | Matias et al. — Very fast biaxial texture evolution using high-rate IBAD of MgO | 2009 | 10.1557/jmr.2009.0036 | 5/5 (!!!) | 📥 | «Снятие предела» скорости — ядро аргумента S4 |
| 4 | Kreiskott et al. — Reel-to-reel IBAD-MgO based coated conductors | 2004 | 10.1088/0953-2048/17/5/008 | 4/5 (!!) | 📥 | R2R = промышленная масштабируемость (48 цит.) |
| 5 | Foltyn et al. — Performance of meter-long YBCO/IBAD flexible tapes | 1999 | 10.1109/77.784682 | 4/5 (!!) | 📥 | Ранний успех на длинных лентах (141 цит.) |
| 6 | Paranthaman et al. — Chemical solution planarization for IBAD-MgO templates | 2014 | 10.1088/0953-2048/27/2/022002 | 4/5 (!!) | 📥 | Удешевление: замена электрополировки хим. раствором (33 цит.) |
| 7 | Iijima et al. — R&D of Biaxially Textured IBAD-GZO Templates | 2004 | 10.1557/mrs2004.162 | 3/5 (!) | 📥 | Альтернатива MgO: IBAD-GZO у Fujikura (65 цит.) |
| 8 | Xu et al. — Long-length GdBCO with IBAD/PLD (Fujikura 400 м) | 2008 | 10.1088/1742-6596/97/1/012273 | 3/5 (!) | 📥 | Промышленный масштаб Fujikura (13 цит.) |
| 9 | Hühne et al. — IBAD-MgO via ion-beam assisted PLD | 2005 | 10.1016/j.physc.2005.02.080 | 3/5 (!) | 📥 | Европейская альтернатива (IFW Dresden, 20 цит.) |
| 10 | Yamada et al. — Progress of PLD and IBAD in SRL-Nagoya (self-epitaxial CeO₂) | 2004 | 10.1088/0953-2048/17/2/065 | 3/5 (!) | 📥 | Японская госпрограмма, ISTEC (30 цит.) |

## Скачано
*(пусто — ничего не скачано)*

## Документы для верификации цены REBCO $/кА·м (график 3)

| # | Документ | Год | DOI/URL | Релевантность | Статус | Почему |
|---|----------|-----|---------|---------------|--------|--------|
| 11 | DOE/AMSC — отчёт с цифрами цены coated conductor | 2010-е | (найти) | 4/5 (!!) | 📥 | Документальный источник цены $/кА·м |
| 12 | SuperPower/Furukawa — прайс или отчёт о стоимости | 2010-е | (найти) | 4/5 (!!) | 📥 | Реперная точка цены |

## Данные в проекте (не wishlist, уже есть)

- Патенты: `data/raw/patents/topics_window/ibad_tapes.json` (28 релевантных) + `ibad_tapes_OLD_wide_query.json` (300, окно 2006-2018)
- Анализ: `signals/patent_signal.md` (в папке кейса)
- SNF-тег: `results/snf_index/topics_map.json` → `ibad_tapes` (476 докладов)
- Рынок подложек: `results/market/hastelloy_procurement/` (Hastelloy C-276, $54-74/кг, модель)
