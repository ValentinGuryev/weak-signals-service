# Паспорт: полный SMES-корпус (дособор )

> **Файл:** `data/raw/openalex/smes_full_corpus.json`.
> **Цель дособора:** закрыть пробелы кейса 005: (1) документированное рождение SMES на ВТСП
> (включая 1G BSCCO), (2) граф цитирований → якорные работы, (3) impact (S3_incoming_max).

## Запросы (OpenAlex, title_and_abstract.search, полные записи, cursor-пагинация per-page=200)
1. `"superconducting magnetic energy storage"` → 3201 работ
2. `"SMES" AND ("HTS" OR "BSCCO" OR "Bi-2223" OR "high-temperature" OR "high temperature superconductor")` → 591 новых

**Итог:** 3792 сырых → **3280 уникальных по id** → **3361 чистых** (SMES-смысл в title/abstract,
мусор отброшен: бетонные прутья 1945, химия железа 1969 и т.п.) → **ВТСП-SMES подкорпус 754 работы**
(SMES ∩ {HTS/high-temp/BSCCO/Bi-2223/YBCO/REBCO/coated conductor/2G} в title/abstract/concepts).

## Скрипт
`src/openalex_smes_full.py` (по образцу openalex_corc.py). Запуск .
Поля: id, doi, title, year, cited_by, abstract, authors(+institution), references, type, concepts.

## РЕЗУЛЬТАТЫ (закрытие пробелов)

### 1. Рождение SMES на ВТСП = **1988** (документировано, не мнение)
Первые работы SMES на ВТСП (3 в 1988, ничего раньше — контроль 1986-1990):
| Работа | Год | Цит. | DOI |
|---|---|---|---|
| The Potential Impact of Developing High Tc Superconductors on Superconductive Magnetic Energy Storage | 1988 | 14 | 10.1007/978-1-4613-9874-5_9 |
| Design study of SMES system using high temperature superconductors | 1988 | 12 | 10.1109/20.11369 |
| High temperature superconducting magnetic energy storage for future NASA missions | 1988 | 4 | — |

**Контраст с прежним birth=1969:** 1969 — идея Ferrier (LTS/NbTi), до ВТСП вообще (открыт 1986).
По корпусу первая работа SMES вообще — 1990 (title-поиск) / 1964 (ассортимент). Рождение технологии
SMES-на-ВТСП = 1988 → **age 2018 = 30**.

### 2. Граф цитирований ВТСП-SMES (754 работ)
Входящие цитаты ВНУТРИ подкорпуса, якорные работы (все годы / ≤2018):
| Якорная работа | Год | Вх.цит (все) | Вх.цит ≤2018 | Общ.цит |
|---|---|---|---|---|
| System Coordination of 2 GJ Class YBCO SMES | 2009 | 36 | **27** | 112 |
| Design of HTS Magnets for a 600 kJ SMES | 2006 | 34 | 21 | 65 |
| Design of a 800 kJ HTS SMES | 2005 | 29 | **27** | 55 |
| Conceptual Design of HTS Coil for SMES Using YBCO CC | 2007 | 26 | 19 | 54 |
| First Tests of a 800 kJ HTS SMES | 2008 | 25 | 23 | 59 |

### 3. Impact (S3_incoming_max) = **27**
Макс. входящих цитат внутри ВТСП-SMES ядра ≤2018 = 27 (две работы 2005/2009).
⚠️ Прежнее S3_incoming_max = «—» (не измерено) молча стало 0 → im_n=0 (аномалия).
Теперь честное значение: **im_n = 1−exp(−27/40) = 0.491** (не 0!)

### 4. Динамика ВТСП-SMES (для growth/persist)
- N14-15=60, N16-18=66 → **growth 1.10** (слабый)
- N17-19=64, N20-22=54 → **persist 0.84** (спад после окна)
- Пик активности 2010 (52), далее снижение (2016: 20, 2018: 22, 2022: 17)

### 5. Пересчитанные скоры SMES (сравнение)
| Параметр | было (аномалия) | стало (честно) |
|---|---|---|
| birth | 1969 | **1988** |
| age 2018 | 49 | **30** |
| impact | «—»→0 | **27** |
| novelty_n | 0.001 | **0.047** |
| impact_n | 0.000 | **0.491** |
| screen (N×G×I) | 0.000 | **0.012** |
| escore 4-комп. | 0.000 | **0.006** |

**Вывод:** даже на честных данных SMES НЕ проходит порог Этапа 1 (0.012 < 0.10) — но теперь по
заслуге: возраст 30 лет (novelty низкая), growth слабый (1.10), persist<1 (спад). Это НЕ аномалия, а
честный сигнал: ВТСП-SMES к 2018 — стареющая, слабо растущая, спадающая тема. (Обзоры-накопители
«Progress in electrical energy storage» имеют 3700+ цит — но это обзоры ВСЕХ накопителей, не SMES-ядра.)

### Примечание о полном корпусе vs ВТСП-ядре
- Полный SMES корпус: 3361 работ, рост 1.32, persist 0.99, top-цит. = обзоры накопителей (не SMES).
- ВТСП-SMES подкорпус (754) — предмет технологии «SMES на ВТСП» (как просил автор: включая 1G BSCCO).
- Рекомендуем КАНОн для 005 = ВТСП-SMES подкорпус (754), birth 1988, impact 27.

## Воспроизводимость
- OpenAlex запросов: 22 (2 поиска × cursor-пагинация; открытый API, без квоты Lens).
- Лог: `results/runtime/api_budget.md` (добавить строку 2026-09-10, OpenAlex ~22).