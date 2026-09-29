# Паспорт: корпуса конкурентов для S3-cross кейса 008 (СП-авиадвигатели)

- **Файл:** `results/case_signals/s3_cross_evolution_aircraft.json` (раздел `competitors`)
- **Скрипт:** `src/s3_cross_evolution_aircraft.py` (блок 3) + `src/s3_cross_evolution_aircraft2.py` (докачка после 429)
- **Дата:** 
- **Запросы (OpenAlex, санкция ≤25):** 25 всего (11 первый запуск: 5 траектории ядер + 2 batch внешних refs + 4 конкурента с 429-сбоями; 14 докачка)
- **Корпуса:**
  | имя | запрос | работ (raw) | страниц |
  |---|---|---|---|
  | pm_motor | "permanent magnet" motor aircraft | 100 (100) | 1 |
  | h2_fuelcell | "fuel cell" aircraft propulsion hydrogen | 502 (504) | 6 |
  | cryo_motor | cryogenic electric motor aircraft propulsion | 82 (82) | 1 |
  | cryo_cual | cryogenic copper motor aircraft OR "cryogenic aluminum" aircraft motor | 17 (17) | 1 |
- **⚠️ Выборки, НЕ полные цензы** (см. s3_cross_evolution.md §1). Доли нормированы на размер выборки.
- **Поля:** id, title, year, cited_by, abstract, referenced_works, authorships (полный select)
- **Восстановление:** повторный запуск скриптов (пауза 2.5с, ретраи на 429 с ростом паузы)
- **Остаток бюджета:** см. `results/runtime/api_budget.md`
