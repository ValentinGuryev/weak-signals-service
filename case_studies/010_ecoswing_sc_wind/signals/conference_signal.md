# Конференционный сигнал (S1c): СП-генераторы для ветроэнергетики (кейс 010 EcoSwing)

> **Дата:** . **ШАГ 7 GUIDE.**
> **Вопрос:** как тема жила на конференциях (доклады) vs журналах? Запаздывают ли конференции?
> Кто и когда докладывал (география)? Согласуется ли с грантовым (ЕС-ядро) и публикационным сигналами?
> **Метод:** (1) SNF-индекс `results/snf_index/index.csv` — 2327 записей докладов ASC/EUCAS/MT/ICMC/ISS/
> ACASC/CEC-ICMC 2007-2025 (Superconductivity News Forum); (2) IEEE TAS `data/raw/conferences/
> conference_hits.json` — 2175 статей-трудов ASC (Springer/IEEE); (3) корпус OpenAlex кейса
> (435 conference-papers). **Без новых API-запросов.**
> **Статус: ДАННЫЕ, НЕ вердикт.**

---

## 1. SNF-индекс: ветро-доклады (26 записей по теме, ядро — 10)

| Год | Конф. | Доклад | Кто | Значение |
|---|---|---|---|---|
| 2010 | EUCAS | HTS high-dynamic electrical motors | (SUST-контекст) | ранний концепт |
| 2011 | ICMC | Superconducting Generators | Abrahamsen-линия | ранний обзор |
| 2012 | ASC | Next Generation Drive Train (Superconductivity) | (UK?) | **ветер-драйвтрейн!** |
| 2013 | ASC | Review of Superconducting Generator Topologies | — | обзор на ASC |
| 2013 | (SNF) | **New European Union Project SUPRAPOWER** | ЕС | европ. проект анонсирован |
| 2015 | CEC-ICMC | **Feasibility Study 10 MW-class SC Wind Turbine (M3OrD-02, инвайт)** | **Япония (Yamasaki)** | **японский feasibility** |
| 2018 | ASC | **Инвайт-постер 3LPo2B-01: KEPCO 10MW Floating Offshore + СП-генератор** | **Корея (M. Park et al.)** | **корейская гос. программа** |
| 2020 | ACASC | Korea Project — Basic Technologies of 10 MW Floating Wind | Корея | продолжение KEPCO |
| 2020 | ASC | An Innovative Wind Project (HTS magnet, test facility, offshore) | Корея (Park) | KEPCO-доклад |
| 2023 | (SNF) | Design and Testing of Real Scale MgB2 Coils for SUPRAPOWER 10MW Wind Generator | ЕС (SUPRAPOWER) | **финал SUPRAPOWER** |
| 2023 | ASC | Next Generation Drive Train Superconductivity for Large-Scale Wind Turbines | (UK/ЕС) | снова drive train |
| 2023 | ISS | Rotating Machines Using High Temperature Superconductors | Япония | яп. доклад (машины) |

> **⚠️ SNF = «Superconductivity News Forum»** — глобальный дайджест докладов СП-конференций.
> Общий контекст «СП-машины/моторы» в SNF шире (26 записей), ветро-специфичных — ~10.

---

## 2. IEEE TAS (труды ASC): историческая справка + возрождение

### 2а. ПРЕДЫСТОРИЯ: японский национальный проект «70 MW class superconducting generator» (1988-1999)

| Год | Доклад | Проект |
|---|---|---|
| 1997 | Development of a 70 MW class superconducting generator | **Япония, New Sunshine Project (AIST/MITI), нац. проект с 1988** |
| 1999 | Recent progress on 70 MW class superconducting generators | Super-GM (модели 70 MW, цель 200 MW) |
| 1999 | 70 MW class superconducting generator test | ротор со СП-обмоткой + статор с воздушным зазором |
| 1999 | Cryogenic and electrical performance at factory test of a rotor | 11-летняя программа с 1988 |

→ **ЯПОНИЯ финансировала нац. проект СП-генераторов С 1988 (!) до ~1999-2000, дискретно возродилась**
к 2015 (feasibility 10MW, Yamasaki). Это КАНАЛ, которого нет в NSF/KAKEN-поиске по ветру.

### 2б. Возрождение в TAS (2016-2026): ветер + смежные машины

| Год | Доклад | География |
|---|---|---|
| 2020 | Design and Optimization of an HTS Claw-Pole Machine | (генератор/машина) |
| 2021 | **Study on Electrical Design of Large-Capacity Fully SC Offshore Wind Turbine** | **ветер!** |
| 2021 | Influence of Coil Position on AC Losses of Stator SC Windings of Synchronous... | ветер (обмотки) |
| 2024 | **Thermal Modeling of a High-Voltage Fault-Tolerant Wind Generator With HTS Bulks** | ветер! |
| 2024-26 | Warm Rotor 200kW HTS Generator; Liquid-Hydrogen-cooled field coils; aircraft/marine | класс СП-машин |

### 2в. Класс «СП-машины» в TAS (не ветер, тот же технологический ряд) — 15-16 статей, всплеск 2023-26

```
generator: 1997-99 (4, Япония) → 2016 1 → 2020-26 (6, Korea/JH2/aircraft)
machine:   1999-2007 (5) → 2013-17 (4) → 2020-26 (6, aircraft/fusion)
motor:     2006-18 (7, DAPAS 2006, 3MW ship 2017-18) → 2025 (aircraft air-core)
```

---

## 3. Что показывают конференции: ВРЕМЕННАЯ ГЕОГРАФИЯ

| Период | Кто докладывает (SNF+TAS) |
|---|---|
| 1988-1999 | **Япония** (нац. проект 70/200 MW, New Sunshine) |
| 2006-2013 | **UK/ЕС** (Abrahamsen 2010-11, drive train 2012, генераторные топологии 2013, SUPRAPOWER 2013) |
| 2015 | **Япония** (feasibility 10MW, CEC-ICMC 2015, инвайт) |
| **2018-2020** | **КОРЕЯ (KEPCO 10MW floating offshore)** — новая заявка |
| 2021-2024 | Корея (TAS) + **SUPRAPOWER-финал (2023)** + возрождение ЕС drive train |
| 2025-26 | класс «СП-машины» (aircraft, liquid-H2, marine) — без ветра |

**Ключевое:** конференционное присутствие ветро-темы — **волны по географии**: Япония (90-е) →
ЕС (2010-13) → Япония (2015) → Корея (2018-21) → ЕС/SUPRAPOWER (2023). **EcoSwing на ASC 2018**
(инвайт-постер Корея-KEPCO же, а не EcoSwing-team... ⚠️ уточнить: постер 3LPo2B-01 = KEPCO, не EcoSwing).

> **⚠️ ВАЖНОЕ ОГРАНИЧЕНИЕ:** в SNF-индексе **прямых докладов EcoSwing (Дания) НЕТ** (поиск "EcoSwing" → 0).
> EcoSwing-команда публиковалась в журналах (SuST, IEEE TAS) и на EUCAS/ASC — но в SNF-дайджесте
> её доклады либо не попали, либо под названием «10MW floating» (Korea!). **Не путать KEPCO и EcoSwing.**
> Охват SNF неполон для конкретного проекта (урок 007: TAS/SNF — «классика», не все проекты).

---

## 4. Конференции vs публикации (S1c-гейт)

| Источник | Сигнал | Вывод |
|---|---|---|
| Публикации (корпус) | пик 2014-19, плато-спад (1560 раб.), conference-papers = 435 (28%) | тема живёт и в журналах, и на конференциях |
| SNF (доклады) | волны: Япония 90-е → ЕС 2010-13 → Корея 2018-21 → ЕС 2023 | **смена географии-лидера докладов** |
| IEEE TAS (труды) | 70MW Япония (1997-99) → пауза → возрождение 2020-26 | конференции **НЕ запаздывают**, а опережают публ. волны Кореи/Японии |

**Вывод для S1c:** конференционный сигнал **согласуется с грантовым** (ЕС-ядро 2010-13/2023,
но дополняет: **Корея KEPCO 2018-21** и **Япония 90-е/2015** — два гос. канала, которых нет
в NSF/CORDIS-грантах) и с S2 (после 2019 ядро темы остывает: свежие доклады — класс «СП-машины»,
не ветер). **«0 в базе ≠ 0 в реальности»**: корейская и японская программы видны ТОЛЬКО на конференциях.

---

## 5. Артефакты
- ✅ `case_studies/010_ecoswing_sc_wind/signals/conference_signal.md` (этот файл)
- Данные: `results/snf_index/index.csv` (локально), `data/raw/conferences/conference_hits.json` (TAS).
- API: 0 запросов (локальные базы).
- ⚠️ Паспорт SNF-индекса: `results/snf_index/index_summary.md` (2327 записей, conf: ASC 349, EUCAS 192,
  MT 107, CCA 100, ICMC 85, ISS 73, ISEC 61, ACASC 17...).

**⏸ СТОП (GUIDE ШАГ 7 п.6): показать пользователю.**