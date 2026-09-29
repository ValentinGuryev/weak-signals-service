# Паспорт: поле декарбонизации + корпуса SAF/BLI/аммиак (кейс 008)

- **Файл:** `results/case_signals/s3_cross_decarb_aircraft.json`
- **Скрипт:** `src/s3_cross_decarb_aircraft.py`
- **Дата:** 
- **Санкция:** команда «делай 20 запросов» (паузы 4с, retry при 429)
- **Запросы использовано: 9** (6 counts + 3 корпуса; часть 2 корпусов имела 429-retry)
  (в api_budget — см. ниже)

## Часть 1: counts полей декарбонизации (group_by, только числа)
| поле | запрос | всего | 2018 | 2025 |
|---|---|---|---|---|
| saf | "sustainable aviation fuel" OR "alternative aviation fuel" OR biojet OR bio-jet | ~4763 | 87 | 1164 |
| hydrogen_aviation | "hydrogen" aircraft propulsion OR "hydrogen-powered aircraft" OR "liquid hydrogen" aircraft | ~4260 | 58 | 614 |
| electric_aircraft_all | "electric aircraft" OR "electrified aircraft" OR "electric propulsion" aircraft | ~399k | 14863 | 21110 |
| turboelectric_bli | turboelectric OR "boundary layer ingestion" OR "distributed electric propulsion" | ~1840 | 110 | 213 |
| ammonia_aviation | "ammonia" aircraft OR "ammonia" aviation OR power-to-liquid aviation | ~403 | 3 | 93 |
| battery_aviation | "battery" electric aircraft OR "lithium" aircraft battery | ~2899 | 126 | 432 |

⚠️ `electric_aircraft_all` ~399k — ШИРОКИЙ шум (ловит «electric propulsion» + aircraft порознь),
НЕ годится как знаменатель сам по себе; показан только как контраст (широкое определение).

## Часть 2: корпуса конкурентов (полный select: references есть)
| имя | запрос | работ | страниц |
|---|---|---|---|
| saf_core | "sustainable aviation fuel" aircraft | 599 | 6 |
| turbo_bli | "turboelectric" aircraft OR "boundary layer ingestion" aircraft | 254 | 3 |
| ammonia_av | "ammonia" aircraft propulsion OR "ammonia" aviation fuel | 85 | 1 |

- Поля записей: id, title, year, cited_by, abstract, referenced_works, authorships
- **Восстановление:** повторный запуск `src/s3_cross_decarb_aircraft.py`
- **Остаток бюджета:** `results/runtime/api_budget.md` (25 запросов 008 S3 + 9 decarb = 34 в этой сессии по 008)
