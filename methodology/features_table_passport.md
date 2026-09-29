# Паспорт features_table.csv

> **Дата:** . **Версия колонок:** 55.
> Рядом: `methodology/ESCORE_RECALC_.md` (канон), `methodology/MODEL_SYNTHESIS.md` (модель).

## Что это
Сводная таблица фич 10 калибровочных кейсов (9 СП + 009 CORC) × 56 колонок.
Используется для ML (метка = `label_2026`) и ручного аудита новых кейсов.

## История версий
| Дата | Событие | Колонки |
|---|---|---|
| до  | прежняя версия (81 pubs у 001, старый escore min-max) | 51 |
|  | канонические ряды → ESCORE_RECALC (отдельный файл), таблица НЕ пересобрана (TODO) | 51 |
| **** | **актуализация**: pubs по канону (001: 81→133), escore τ=40, +5 колонок двухэтапной модели, починка строки 009 | **56** |
|  (2) | **escore_prod_2018 УДАЛЕНА** (вариант 1 автора): историческая, в модели не используется | **55** |

## Метод ()
1. **S1_pubs_total** — полный корпус темы (канон): 001=133 (было 81), 003_joint=103, 007=263.
   Источники рядов — ESCORE_RECALC_series.json / локальные корпуса OpenAlex. БЕЗ новых API-запросов.
2. **escore_prod_2018** — пересчитан: `novelty_n × growth_n × persist_n × impact_n` с impact_n = 1−exp(−x/40)
   (решение автора 2026-09-10). Служит для РАНЖИРОВАНИЯ кандидатов (Этап 1/2), НЕ для вердикта.
3. **Новые колонки** (двухэтапная модель, METHODOLOGY §2а):
   - `novelty_n`, `growth_n`, `persist_n`, `impact_n` — нормализованные компоненты (вариант X)
   - `escore_screen_2018` = **novelty × growth × impact** (БЕЗ persistence — look-ahead!) — **скор Этапа 1**,
     порог recall-first; Это константа для скрининга кандидатов.
4. **Строка 009 (CORC)** — была повреждена несэкранированными запятыми (название, тексты сигналов).
   Восстановлена по сигналам кейса (s1a, patent, conference, grant, s2, s3, roadmap) и коммиту 3e800f4.
5. **Строка 005 (SMES) — дособор по задаче автора 2026-09-10** (см. §10 ESCORE_RECALC):
   birth 1969 → **1988** (документировано: первая работа SMES на ВТСП, включая 1G BSCCO — 3 работы 1988;
   корпус см. smes_full_corpus.json); S3_incoming_max «—» → **27** (граф цитирований ВТСП-SMES подкорпуса,
   якорь 2009 2GJ YBCO / 2005 800kJ); S1_pubs_total 810 → **754** (ВТСП-SMES подкорпус,
   ✅ КАНОН 005 подтверждён автором 2026-09-10).
   Скоры: escore 0.0056, screen 0.0122 (НЕ проходит порог Этапа 1 — честно, по возрасту 30 и слабому росту).

## Колонки (55)
`case_id, case_name, label_2026, S1_pubs_total, S1_pubs_pre2010, S1_pubs_2011_2015, S1_pubs_2016_2019,
S1_pubs_2020plus, S1_pubs_growth_early_late, S1_pubs_peak_year, S1_pubs_peak_value, S1_conf_total,
S1_conf_pre2010, S1_conf_2016_2019, S1_conf_2020plus, S1_conf_peak_year, S1_pat_total, S1_pat_in_window2006,
S1_pat_first_year, S1_pat_growth, S1_grants_flag, S1_grants_countries, S2_shift_direction,
S2_markers_growing, S2_markers_falling, S2_gate_passed, S2_na, S3_birth_year, S3_dev_start, S3_dev_end,
S3_established_year, S3_dev_duration, S3_cluster_size, S3_incoming_max, s3_profile, S3_foundation_type,
S4_limit_broken, S4_param_improvement, S4_record_year, S4_industrial_players, S4_demo_scale,
S4_economics_verdict, roadmap_signal, roadmap_signal_note, verdict, evidence_strength, signal_class_2018,
adoption_2018, conversion_2018, growth_persistence_w3w2, novelty_n, growth_n, persist_n, impact_n,
escore_screen_2018`

> ⚠️ **escore_prod_2018 (novelty×growth×persist×impact) — УДАЛЕНА из таблицы 2026-09-10**
> (вариант 1 автора). Причина: в двухэтапной модели не используется — ни на Этапе 1 (там
> `escore_screen_2018` = nov×gr×im), ни на Этапе 2 (вердикт impact×adoption×conversion).
> Остаётся историческим артефактом: расчёт/значения — ESCORE_RECALC.md §2-4, §9.
> Ядро Этапа 1 и вердикт модели — см. METHODOLOGY §2а / MODEL_SYNTHESIS §2.

## Метка
- `label_2026`: 1 = состоялся, 0 = не состоялся, `в_развитии` = в развитии (007).
  (3-уровневая схема, решение автора 2026-09-06, CASE_BUILDING_GUIDE ШАГ 8.)

## Воспроизводимость
- Канон рядов: `results/ESCORE_RECALC_series.json`, `ESCORE_RECALC_values.json`.
- Пересчёт escore: python-блоки сессии 2026-09-09/10 (см. ESCORE_RECALC §2-3, §9).
- Строка 009: `case_studies/009_corc_cables/signals/s1a_publications.md` (+ patent/conference/grant/s2/s3/roadmap),
  корпус `data/raw/openalex/corc_corpus.json` (353 работы).