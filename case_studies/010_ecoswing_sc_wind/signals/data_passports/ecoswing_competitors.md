# Паспорт: корпус конкурентов кейса 010 (EcoSwing) — ШАГ 3 GUIDE

> **Файл:** `data/raw/openalex/ecoswing_competitors_corpus.json`
> **Дата:** . Скрипт: `src/openalex_ecoswing_competitors.py`.
> **Проблема (мотивация СП-генератора):** «генератор 10-20 MW из ветра, меньший вес/размер,
> высокий КПД, без редких земель».

## Запросы (OpenAlex, title_and_abstract.search, полные записи, cursor; 2005-2018 окно)
| Конкурент | Запрос | Работ (в корпусе) |
|---|---|---|
| **PM_DD** (постоянные магниты, прямой привод) | `"permanent magnet" AND ("direct drive") AND "wind"` | ~113 (до 2018) |
| **DFIG** (+редуктор) | `"doubly fed induction generator" AND "wind turbine"` | ~105 рел. |
| **hydraulic** (гидравлическая трансмиссия) | `"hydraulic transmission" AND "wind turbine"` | ~25 |
| **mag_gear** (магн. редуктор / псевдопрямой) | `("magnetic gear" OR "pseudo direct drive") AND "wind turbine"` | 1 |
| **no_rare_earth** (без редких земель) | `("rare earth free" OR "ferrite") AND "wind generator"` | 1 |
| **EcoSwing** | `"EcoSwing"` | 9 |

Итог: **601 работа** (дедуп по id). Поля полные (abstract, references, authors, concepts, cited_by).

## Ключевые работы конкурентов (2005-2018, топ по цит.)
- **DFIG+редуктор**: «Modeling of the Wind Turbine With a DFIG» (2006, 703 цит), «Impact of Increased
  Penetration of DFIG» (2009, 683), «Control of a DFIG in a Wind Turbine During Grid» (2006, 666) —
  зрелый, мощный мейнстрим.
- **PM-DD**: «Open-Circuit Fault Diagnosis in PMSG Drives» (2012, 276), «Key challenges and prospects
  for large wind turbines» (2015, 238); **«Superconducting wind turbine generators» (2010, 217)** — СП
  сам в этом корпусе как конкурент-тема.
- **гидравлика**: «Trends in Wind Turbine Generator Systems» (2013, 563), Digital Displacement (2007, 62)
  — небольшая ниша.
- **без редких земель**: «Intriguing Behavioral Characteristics of Rare-Earth-Free Flux Switching» (2018, 44)
  — молодой конкурент, только появляется.
- **магн. редуктор**: 1 работа (2016, 5) — слабо представлен.

## Динамика (counts 2005-18 / 2019-26)
- PM_DD: 113 / 0 — активен до окна; после 2019 запрос дал 0 (высокий узкий «permanent magnet +
  direct drive + wind», в OpenAlex может иметь др. формулировку). Осторожно с интерпретацией.
- DFIG: 401 / 0 — то же предупреждение (узкий запрос).
- hydraulic: 0 / 8; no_rare_earth: 0 / 6; EcoSwing: 0 / 9 — появляются после окна (в т.ч. наши выжимки).
- ⚠️ counts с «0 после 2018» — НЕ вывод «конкуренты умерли»: это артефакт узкого запроса
  (формулировки меняются). Для честных трендов нужны counts по классу-проблеме (S5), не по запросу.

## Вывод (данные, НЕ вердикт)
- В окне 2005-2018 конкуренты СП-генератора — **DFIG+редуктор (доминирует, тысячи цит.)** и **PM-DD
  (сотни цит.)**; гидравлика/магн. редуктор/без-редких-земель — мелкие.
- СП-генератор конкурирует с зрелыми, хорошо цитируемыми технологиями — это фон, а не «возможность».
- Статус: данные для ШАГ 3; финальные выводы — после ШАГ 5-8 и обсуждения с автором.

## Воспроизводимость
- OpenAlex ~12 запросов (записано в api_budget).
- Скрипт: `src/openalex_ecoswing_competitors.py`.