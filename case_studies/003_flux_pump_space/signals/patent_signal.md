# Патентный сигнал: flux pump + REBCO-соединения — кейс 003

> **Дата:**  (обновлено после пачки ручных патентов 09-04).
> **Базы кейса (2 темы):**
> - **Flux pump:** `data/raw/patents/cases/003_flux_pump.json` (**100** патентов, дедупл.)
> - **REBCO-соединения:** `data/raw/patents/cases/003_rebco_joints.json` (**51** патент, дедупл.)
> **Источники:** Lens (flux_pump_lens_clean 96→94, rebco_joint_lens_clean 51) + ручные PDF Google Patents
> (пачки 09-01: 43, 09-02: 43, **09-04: 90**).
> **Логи:** `results/runtime/manual_patents_processing_.md`, `..._.md`, `..._.md`.

---

## Сводка (из детальных FINDINGS_.md и литература/patents/)

### Flux pump (100)
- **Академия доминирует:** Sichuan Univ (17+), Hunan (4), Northeastern (3), North China Electric Power (3);
- **Промышленность историческая:** Siemens (11, 2000-08, NMR), BBC/EDF/EPRI/Japan Railway (1970-80-е);
- **Современные промышленные:** Victoria Link (Hēki, 9 — **+WO2025042296A1 thrust field generator**),
  Grid Logic (3), Magnifye (2), Rolls-Royce (SC switch), Cambridge Enterprise (2023);
- **КОСМИЧЕСКИЙ HTS-КЛАСТЕР НОВОЙ ЗЕЛАНДИИ (пачка 09-04, находка!):**
  - **Zenno Astronautics** (5): US12354791B2, US12139277, US20220084729A1, HK40066832B, HK40110731A
    (satellite systems с СП-электромагнитами и криоохлаждением);
  - **NeutronStar Systems** (3): GB2600493A, GB2606768A, WO2022243543A1 (thermal mgmt HTS-thruster);
  - **Open Star Technologies NZ** (1): WO2025137681A1 (поддержание криотемператур);
  - **JAXA** (Япония!): JP5417643B2 — 宇宙用超電導磁石装置 (космический СП-магнит, радиационные
    тепловые экраны, термоэлектрическая накачка) — **ПЕРВЫЙ японский патент в космической нише flux pump**;
    ⚠️ НО публикационный сигнал (см. `signals/seebeck_signal.md`): за патентом — мёртвая наука
    (7 работ Toshiba/Tokyo Tech 2002-2008, далее тишина). Патент — «лебединая песня» Seebeck-накачки.
  - +2 flux pump 王为/四川大学 (CN204946696U, CN205789468U).
- **Китайские универы патентуют flux pump**; до пачки 09-04 считалось, что японцы — НЕТ
  (разделение труда). JAXA-патент уточняет: Япония входит через КОСМИЧЕСКИЕ СП-магниты, не через наземный flux pump.

### REBCO-соединения (51)
- **Tokamak Energy** (4, exfoliated ReBCO joint 2017), **K-Joins** (4), **IEE CAS** (4+), SWIP (3);
- **Японцы — ПЕРЕСМОТР (пачка 09-04):** Furukawa/ISTEC патентуют соединения **SC-кабелей и SC-лент
  массово** (+15 патентов 2008-2021: JP2015018620A, JP2016091880A, JP2017117523A, US10541068,
  US9042951, US9123455, CN110326062A, EP3550619B1 и др.). Ранее (09-02) казалось, что японцы НЕ патентуют —
  не хватало JP-публикаций. **Уточнение:** Furukawa/ISTEC патентуют соединения кабелей/лент;
  RIKEN/Sumitomo патентуют persistent-магниты с iGS-соединениями (US20200075207A1, EP3739602A1).
- Китай: Eastern Superconducting, Shanghai Superconducting, Shenci Tech, Xi'an Juneng;

## Ключевой вывод
**Flux pump** — академическая/китайская тема (патенты универов) + **новозеландский космический кластер**
(Robinson→Zenno/Victoria Link/Open Star + немецкий NeutronStar) — прямое патентное подтверждение
космического применения (кейс 003: Hēki и последователи). Япония входит через космические СП-магниты (JAXA)
и соединения (Furukawa/ISTEC/RIKEN), а не через наземный flux pump.

## Файлы данных
- `data/raw/patents/cases/003_flux_pump.json` (**100**)
- `data/raw/patents/cases/003_rebco_joints.json` (**51**)
- Исходники: `data/raw/patents/topics/flux_pump_lens_clean.json` (113), `rebco_joint_lens_clean.json` (69)
- Ручные: `data/raw/patents/patents.google.manual/*__003_flux_pump_space.pdf`, `*__003_rebco_joints*.pdf`
