# Паспорт: корпус EcoSwing / СП-генераторы для ветряков (кейс 010)

> **Файл:** `data/raw/openalex/ecoswing_corpus.json`.
> **Дата:** . Скрипт: `src/openalex_ecoswing.py` (по образцу openalex_corc.py).

## Запросы (OpenAlex, title_and_abstract.search, полные записи, cursor-пагинация per-page=200)
1. `"superconducting" AND ("wind generator" OR "wind turbine" OR "wind power")` → 1151
2. `"HTS generator" OR "high temperature superconducting generator"` → 127 (новых)
3. `"superconducting machine" OR "superconducting electrical machine"` → 572 (новых)
4. `"EcoSwing"` → 7 (новых)

**Итог:** 1857 сырых → по смыслу (wind/турбина/генератор/машина + SC/HTS/REBCO) **1560 релевантных**.
Поля: id, doi, title, year, cited_by, abstract, authors(+institution), references, type, concepts.

## Ключевые находки

### 1. Ядро EcoSwing (прямо про проект) — 8 работ
| Работа | Год | Цит. |
|---|---|---|
| Bergen et al. — Design and in-field testing of the world's first ReBCO rotor for a 3.6 MW wind generator | 2019 | 128 |
| Commissioning of the World's First Full-Scale MW-Class Superconducting Generator | 2020 | 73 |
| Ground Testing of the World's First MW-Class Direct-Drive Superconducting Wind Turbine | 2019 | 58 |
| The EcoSwing Project | 2019 | 24 |
| Experimental Validation of a Full-Size Pole Pair Set-Up of an MW-Class Direct Drive | 2019 | 31 |
| Measuring MNm torques | 2019 | 3 |
| Technology Transition of Large Scale Wind Turbine / Numerical Study on Energization of Field Coils | 2022 | 5-15 |
| Superconducting generators and cables for wind energy — A review | 2025 | 9 |

### 2. Контекст темы (топ-цитируемые релевантные)
- Trends in Wind Turbine Generator Systems (2013, 563) — зрелый обзор;
- High power density SC rotating machines (2017, 473) — обзор достижений;
- 10 MW Class Superconductor Wind Turbine Generators (2011, 229) — амбициозное обещание 2011;
- Superconducting wind turbine generators (2010, 217); Review of SC Generator Topologies for Direct-Drive (2013, 156);
- A Direct Drive Wind Turbine HTS Generator (2007, 137) — ранний концепт;
- **Жёсткий конкурент SMES/энергохранилища в корпусе** — многие топ-цитирования про SMES в ветриках
  (гибридное хранение), а не про генераторы: тема «пересекается» с накопителями.

### 3. Динамика (чистые, 3-летки)
1990-92:10 → 2002-04:31 → 2008-10:99 → 2011-13:207 → 2014-16:253 → 2017-19:247 →
2020-22:268 → 2023-25:232. Рост до 2014-16 (пик ~253), далее плато/слегка спад. НЕ взрыв, а зрелое плато.

## Воспроизводимость
- OpenAlex: 4 поиска × пагинация (~11 запросов). Открытый API, без квоты Lens.
- api_budget: добавить строку 2026-09-10 (OpenAlex ~11).