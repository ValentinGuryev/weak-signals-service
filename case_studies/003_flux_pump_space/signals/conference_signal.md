# Конференционный сигнал: flux pump (IEEE TAS) — кейс 003

> **Источник:** OpenAlex, IEEE Transactions on Applied Superconductivity (S119074828),
> поиск `abstract.search:"flux pump"` → **172 статьи** (1993-2026).
> **Файл данных:** `data/raw/conferences/flux_pump_ieee_tas.json`
> **Дата сбора:**  (бесплатный OpenAlex, без квот).
> **Статус:** ✅ база «конференции» для кейса 003 закрыта.

---

## 1. Динамика по годам

| Период | Статей | Динамика |
|---|---|---|
| 1993-2005 | ~12 | Единичные (1-2/год) — зарождение |
| 2006-2009 | ~5 | Затишье |
| **2010** | **10** | **Первый всплеск** (Hoffmann flux pump, Coombs) |
| 2011-2015 | ~13 | Рост |
| **2016** | **11** | **Второй всплеск** (dynamo-тип: Bumby, Jiang, Pantoja, Badcock) |
| 2017-2019 | ~26 | Устойчивый рост (Geng kA, transformer-rectifier) |
| **2020-2022** | **43** | **Пик** (2021: 19 — кА-уровни, космос, термояд) |
| 2023-2026 | **53** | Высокий плато (12-17/год) — зрелость |

**Вывод:** конференционный сигнал подтверждает S1 — тренд зародился ~2010 (Hoffmann),
ускорился 2016 (dynamo), вышел на плато 2020+ (кА-уровни, космос Hēki, термояд).

## 2. Ключевые доклады (эволюция темы)

| Год | Доклад | Значение |
|---|---|---|
| 2010 | **Hoffmann — Flux Pump for HTS Magnets** | Запуск HTS-направления |
| 2013 | **Walsh — NMR energized by HTS flux pump** | Применение (NMR) |
| 2016 | **Coombs — An Overview of Flux Pumps for HTS Coils** | Обзор (зрелость науки) |
| 2016 | **Bumby — External-Rotor HTS Flux Pump; Jiang — Dynamo** | Dynamo-тип (Robinson) |
| 2018 | **Hamilton — Squirrel-Cage Dynamo** | Новая архитектура |
| 2019 | **Geng — Transformer-Rectifier kA; Gawith — Optimization** | кА-уровни |
| 2021 | **Rice — 60 kA Flux Pump for Fusion TF Coils** | **Термояд!** (масштаб) |
| 2021 | **Shen — kA Level HTS Flux Pump soldering** | Инженерия |
| 2022 | **Iftikhar — Compact Flux Pumps (bifilar)** | Миниатюризация |
| 2024 | **Rice — 10 kA Transformer-Rectifier; Report** | Масштаб растёт |
| 2024 | **Olatunji — SC Magnet for Space Propulsion (Hēki!)** | **Космос** |
| 2024 | **Yang — 10 kA Full-Wave** | кА-класс |
| 2025 | **Hellmann — CubeSat magnetic radiation shielding** | Космос (продолжение) |
| 2026 | **Wang — Self-Rectifier HTS Flux Pump efficiency** | Зрелость (КПД) |

## 3. Топ-авторы (кто двигает тему)

| Автор | Статей | Школа |
|---|---|---|
| Wei Wang | 26 | Китай (North China/Shanghai?) |
| Tim Coombs | 17 | Кембридж (пионер transformer-rectifier) |
| Rodney Badcock | 14 | Robinson (НЗ) |
| Jianzhao Geng | 13 | Кембридж → кА-уровни |
| Zhenan Jiang | 13 | Robinson (НЗ) |
| Chris Bumby | 8 | Robinson (НЗ) |
| Andrés Pantoja | 7 | Robinson (НЗ) |

**Школы:** Robinson/НЗ (Badcock, Jiang, Bumby, Pantoja, Hamilton) + Кембридж
(Coombs, Geng, Fu) + Китай (Wang, Lei) — три центра.

## 4. Связь с 4 индикаторами

| Индикатор | Что даёт конференционный сигнал |
|---|---|
| **S1 (пересечение баз)** | ✅ Статьи (394 OpenAlex) + конференции (172 IEEE TAS) + патенты (96) + гранты — согласованы |
| **S2 (семантика)** | Динамика тем: 2010 «flux pump» → 2016 «dynamo» → 2020 «kA/космос/термояд» — сдвиг от физики к инженерии |
| **S3 (новизна)** | Всплеск 2010 (Hoffmann) — кластер «из ниоткуда» после LTS-эры (1963-1989) |
| **S4 (снятие предела)** | 60 kA для термояда (2021), 10 kA (2024), космос Hēki (2024) — масштаб растёт |

## 5. Вывод для кейса

Конференционный сигнал **подтверждает вердикт «стоило»**:
- Тренд зародился ~2010 (не вчера), прошёл стадии: физика (2010-2016) → инженерия (2016-2020) → масштаб/космос (2020+);
- **НЕ затухает** — плато 12-17 статей/год в 2023-2026;
- **Расширяется по применениям:** NMR → генераторы → термояд (60 kA) → космос (Hēki, CubeSat);
- Конференции (IEEE TAS) — основной канал публикаций (172 из 394 работ ≈ 44%).

## Примечания
- Собрано по `abstract.search:"flux pump"` в IEEE TAS (возможно, часть «current pump» не поймана — но основной пул покрыт);
- EuCAS (IOP JPCS) — 0 результатов (другой источник в OpenAlex);
- Данные: `data/raw/conferences/flux_pump_ieee_tas.json` (172 записи: title, year, doi, authors).
