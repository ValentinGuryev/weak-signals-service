# Паспорт данных: корпус альтернатив CORC (кейс 009)

- **Файлы:** `data/raw/openalex/corc_alternatives_corpus.json` (полный), `corc_alternatives_counts.json` (агрегат).
- **Скрипт:** `src/openalex_corc_alternatives.py` (через прокси 127.0.0.1:9051 — обход rate-limit).
- **Дата сбора:** . **Число записей:** 454 (дедуп по id, 2000-2026).
- **Метод:** OpenAlex title_and_abstract.search по 8 технологиям, полный select (abstract, авторы,
  references, цитаты), cursor-пагинация; каждая работа помечена тегом (work.techs — может быть несколько).
- **Связанный корпус:** `corc_corpus.json` (353 работы CORC, собран ранее).

## Технологии и запросы
| tech | запросы | работ |
|---|---|---|
| tstc | "twisted stacked-tape cable/conductor" OR "TSTC" AND (REBCO/HTS) | 69 |
| roebel | "Roebel cable/conductor/assembled coated conductor" OR "RACC cable" | 251 |
| croco | "CroCo" AND (REBCO/HTS/superconductor/conductor) | 34 |
| slotted_core | "slotted-core/slotted core" AND HTS AND cable; "Twisted Stack Slotted"/"TSSC cable" | 30 |
| viper | "VIPER cable/conductor" OR "VIPER" AND REBCO AND (cable/conductor) | 34 |
| rutherford_hts | "Rutherford" AND (REBCO/"coated conductor") AND (cable/conductor) | 46 |
| spc_strand | "round strand" AND (REBCO/HTS/coated conductor/twisted stack) | 15 |
| star_wire | "STAR wire"/"isotropic round wire" AND REBCO | 3 |

## Качество
Мусор минимален (Roebel 5/251 — обзоры с упоминанием; TSTC 1; CroCo 1 — нем. обзор). Не чистил
(для полноты); при точном сигнале — пост-фильтр по ключевым словам.

## Нормированный сигнал (главный результат)
Доля CORC в потоке каблирования CC (CORC / (CORC + альтернативы)):
- 2013-15: 16 работ = **19%** (альтернативы 70, в осн. Roebel)
- 2016-18: 40 = **27%** (альтернативы 109)
- 2019-21: 70 = **45%** (альтернативы 87)
- 2022-26: 226 = **63%** (альтернативы 135)

**CORC вырос 19% → 63% доли: «гонка кабелей» — CORC побеждает. В окне 2018 CORC = 27% (лидер среди
растущих, Roebel стагнирует/падает после 2016).**

## Как восстановить
`.venv/bin/python src/openalex_corc_alternatives.py` (нужен SOCKS-прокси на 9051).

## Обновление 2026-09-09 (v2)
- **+HFRC** (highly flexible REBCO cable): 9 работ (2022-2025), докачаны. Корпус: 463 работы.
- **Чистка peer-review мусора:** «Review for.../Decision letter for.../Author response for...» —
  VIPER −8, Roebel −2 (артефакты fulltext-поиска, не статьи). Чистый корпус: 444 (+9 HFRC).
- **Blocks-in-Conduit** (McIntyre) — НЕ добавлен: поиск даёт 27, но всё мусор (геология «blocks in
  conduit»); реальная технология ~0 публикаций (концепт одной группы TAMU). Сам по себе сигнал.
- **Чистые counts:** `data/raw/openalex/corc_alternatives_counts_clean.json`.
- **График несглаженный (чистый):** `plots/corc_vs_alternatives_raw.png`.
