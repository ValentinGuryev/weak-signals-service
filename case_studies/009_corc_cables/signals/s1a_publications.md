# S1a — Публикационный сигнал: CORC-кабели (кейс 009)

> **Дата:** . **Статус:** ✅ S1a собран (автоматически, полный корпус).
> **Метод:** OpenAlex title_and_abstract.search (3 узких запроса) + cursor-пагинация, полные записи
> (abstract, авторы+аффилиации, references, цитаты). Корпус: **353 работы** (1992-2026),
> дедуп по id. Паспорт: `signals/data_passports/corc_corpus.md`.
> **Данные:** `data/raw/openalex/corc_corpus.json`. Скрипт: `src/openalex_corc.py`.

---

## 1. Динамика публикаций

| Период | Работ | Комментарий |
|---|---|---|
| 1992 | 1 | артефакт (SET-oscillations, не CORC) |
| 2013-2015 | 16 | рождение (van der Laan 2013 — первый CORC-кабель) |
| **2016-2018** | **40** | **сигнал: ×2.5 рост; ядро сформировано** |
| 2019-2021 | 70 | рост |
| 2022-2026 | 226 | **взрыв ×5.6 от окна** (fusion: SPARC, EU-DEMO) |

**По годам:** 2013:3, 2014:6, 2015:7, 2016:16, 2017:8, 2018:16, 2019:15, 2020:28, 2021:27,
2022:42, 2023:43, 2024:44, 2025:62, 2026:35.

**Сигнал 2018:** 40 работ за 2016-18, рост ×2.5 от 2013-15. Малый объём + устойчивый рост + якорные
цитаты (van der Laan 2016 = 235, 2013 = 170). Суммарные цитаты корпуса: 5181; работ ≤2018: 57
с 2137 цитатами.

---

## 2. Ядро сигнала (≤2018) — ключевые работы

| Работа | Год | Цит. | Кто | Значение |
|---|---|---|---|---|
| van der Laan — Introduction of CORC wires | 2016 | 235 | CERN/Colorado | **основа** — CORC-провода |
| van der Laan — Characterization of HTS CORC cables | 2013 | 170 | CERN | **первый** CORC-кабель |
| Wang — Magnetization loss of CORC (T-A) | 2018 | 169 | Strathclyde | AC-потери |
| Mulder — 45 kA at 10 T REBCO-CORC CICC | 2016 | 79 | Colorado/CERN | **45 кА!** для детекторов |
| van der Laan — Record 344 A/mm² at 17 T | 2016 | 67 | FSU | рекорд плотности тока |
| Weiss — Viable dipole magnet with REBCO CORC | 2018 | 99 | Colorado | диполь-магнит |
| van der Laan — Bending of CORC (FEM) | 2018 | 94 | Colorado | механика |
| Mulder — 8 kA @ 10 T ReBCO-CORC | 2016 | 35 | CERN | CERN-тест |

**Конкуренты в ядре:** CroCo (KIT, 2016, 129 цит.) — альтернативный стековый проводник;
CICC-сравнения. CORC vs CroCo — как flux pump vs joint (два решения одной проблемы).

---

## 3. Игроки (авторы/институты)

**Топ-авторы:** van der Laan (66! — создатель CORC, ACT/Colorado), Weiss (53 — соавтор/ACT),
далее Китай: Sheng (28), Jin (23), Qin (23 — CICC), Ma (20), Yang (20); Sumption (22), Collings (19,
OSU), Nijhuis (19, Twente).

**Топ-институты:** CAS (139), Shanghai Jiao Tong (127), Cambridge (123), LBNL (104), Colorado Boulder
(97 — van der Laan), Lanzhou (86), Ohio State (83), North China Electric Power (74), Beijing Jiaotong
(74), Twente (68).

**Гео:** США (Colorado/ACT, FSU, LBNL, OSU) + Китай (CAS, SJTU, Lanzhou) + Европа (CERN, KIT,
Cambridge, Twente). Трёхполюсный (как SNSPD US/CN, но с сильной Европой/CERN).

---

## 4. Интерпретация (S1a-вывод)

1. **Сигнал 2018 = «малый объём + сильные якоря + конкретные заказчики»**: 40 работ, НО якорные
   работы van der Laan/CERN с рекордами (45 кА, 344 A/mm², 8 кА@10T) и CERN/DOE как заказчики.
2. **Рост ПОСЛЕ 2018 — взрывной** (×5.6): CORC стал стандартом для compact fusion (SPARC/CFS,
   EU-DEMO) — тренд УСИЛИЛСЯ, не умер.
3. **Конкурент** — CroCo (KIT): параллельный путь; CORC выиграл по гибкости/плотности тока.
4. **Сходство с другими успешными кейсами:** как flux_pump (малый объём + заказчик-миссия),
   как NI-coils (инженерный приём → стандарт магнитов). Отличие от SMES: есть конкретные
   заказчики (fusion-проекты) и рост конверсии.

**Профиль: «weak-сигнал 2018 (малый, но якорный) → состоялся к 2026 (стандарт fusion-кабеля)».**

---

## 5. Что дальше (следующие сигналы)
- **S1b патенты** (кто патентует CORC: ACT/van der Laan? Китай?);
- **S1d гранты** (DOE, CERN, EU-fusion);
- **S2/S3/S4/S5** по мере углубления.
