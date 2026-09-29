# Конференционный сигнал: CORC-кабели (кейс 009)

> **Дата:** .
> **Вопрос:** когда CORC «зазвучал с трибун»? Совпадает ли конференционный сигнал с публикационным
> (рост 2016-18 → взрыв 2022+) и вердиктом «✅ состоялся»?
> **Метод:** (1) SNF-индекс `results/snf_index/index.csv` (Superconductivity News Forum — доклады
> IEEE CCA/ASC/MT/EUCAS и др., 2327 файлов), (2) IEEE TAS-корпус `data/raw/conferences/conference_hits.json`
> (2175 статей ASC-трудов), title-фильтр CORC/round core.
> **Ограничение:** SNF/TAS покрывают «сильноточную» сверхпроводимость — основную арену CORC; полный
> охват (EUCAS отдельно, китайские конференции) частично вне баз.

---

## 1. SNF-индекс (2327 докладов 2007-2025) — CORC: 16 записей, van der Laan с 2016

| Год | Конференция | Доклад (спикер) |
|---|---|---|
| 2016 | CCA (Aspen) | **Development of flexible HTS CORC® wires and terminations** (Weiss/van der Laan, ACT) |
| 2018 | CCA | **Recent progress on CORC® cable and wire development** (van der Laan, ACT) — invited |
| 2021 | CCA | **Development of High-strength CORC® Conductors for High-Field** (van der Laan, invited HF-5) |
| 2021 | CCA | **High-field Accelerator Magnet Tech using REBCO CORC®** (X. Wang, LBNL) |
| 2023 | CCA | **Latest development of CORC® cables/wires for high-field** (van der Laan, invited) |
| 2023 | (abstract) | **High-field Magnets for Compact Fusion Reactors + Accelerators from CORC®** (van der Laan) |
| 2023 | (abstract) | **HTS CORC® Power [cable]** (van der Laan) |
| 2024 | EFATS | **Electrical characterization of CFD CORC® cables 65-77 K** (Lacroix) |
| 2025 | EFATS | **Electrical Characterization of CFD CORC® Cables Between 65 and 77 K** (Lacroix) |
| 2025 | MT (Amsterdam) | **Development of high current CORC® cables, CICC, low [loss]** (van der Laan) |
| — | — | + 6 abstracts (STP380/STP452/STP639/STP640, Weiss ST527) — рекорды (246 A/mm²@17T) |

**Вывод SNF:** CORC присутствует на CCA (главная конференция по coated conductors) **непрерывно
2016→2025**, спикер — van der Laan (ACT) с invited-докладами (2018, 2021, 2023). Это «голос с трибун»:
технология на главной профильной сцене с 2016. Рекордные параметры (246 A/mm²@17T) — S4-элемент.

---

## 2. IEEE TAS (2175 статей ASC-трудов) — CORC: 14 статей, 2016→2025

| Год | Статей | Статьи |
|---|---|---|
| 2016 | 2 | High-Current HTS Cables: Status (van der Laan), Quasi-isotropic strands |
| 2018 | 1 | Quench Detection для HTS (аккустич.) |
| 2019 | 1 | Biaxial strain JC REBCO (CORC-контекст) |
| 2020 | 1 | **Contact Behavior of CORC Wires Under Stretching** |
| 2021 | 2 | CORC Cable Critical Current под циклическим изгибом; Parallel stacks для TF (РФ) |
| 2022 | 1 | Roebel (смежная) |
| 2023 | 1 | **Canted-Cosine-Theta HTS Dipole Magnet Using CORC Cable** |
| 2024 | 4 | CORC CICC для fusion CS; CORC со стальной оболочкой; SMES NICA (CORC); Customized CORC Cable |
| 2025 | 1 | CORC для SFCL (35 kV fault current limiter) |

**Вывод TAS:** CORC в ASC-трудах с 2016 (мало), **рост 2023-24** (fusion CS, dipole, SMES) — совпадает
с публикационным взрывом 2022+. Применения: fusion (CS), ускорители (dipole CCT), SMES (NICA), SFCL.

---

## 3. Хронология «с трибун» (объединение)

```
2016  ██  CCA (Weiss, CORC wires) + TAS (Status HTS cables)     ← ПЕРВЫЙ выход
2018  █   CCA invited (van der Laan progress) + TAS (quench)
2020  █   TAS (CORC stretching)
2021  ██  CCA invited ×2 (HF5 + Wang LBNL) + TAS ×2 (изгиб, РФ)
2023  ██  CCA invited (fusion!) + TAS (dipole CCT)
2024  ███ CCA (CFD) + TAS ×4 (fusion CS, sheath, SMES, custom)  ← ПИК
2025  ██  MT (CICC) + EFATS (CFD) + TAS (SFCL)
```

## 4. Вывод для кейса

1. **Конференционный сигнал 2018 = «уже на сцене, но мал»**: CCA 2016 (первый) + invited 2018 —
   CORC представлен на главной профильной конференции за 2 года до окна, спикер — сам основатель.
2. **Совпадает с публикационным**: рост после 2018, взрыв 2022-24 (fusion CS, dipole, SMES, SFCL) —
   конференции подтверждают, а не опережают.
3. **Специфика CORC:** доминирует ОДИН спикер (van der Laan/ACT, invited 2018/2021/2023) —
   технология «одного чемпиона», что контрастирует с широкими темами (Roebel — много групп).
   Это подтверждает патентную картину (ACT — единственный базовый патентообладатель).
4. **Расширение применений** (2024-25): от fusion к SMES (NICA), SFCL (35 kV), CFD-лентам — CORC
   выходит за пределы исходной ниши.
5. Для ML: conference-сигнал = подтверждающий (как в METHODOLOGY §4б — conf разрешает неоднозначность
   pubs), для CORC не опережает, но показывает «голос одного чемпиона» (ACT-доминирование).

## Артефакты
- Данные: `results/snf_index/index.csv` (16 CORC-записей), `data/raw/conferences/conference_hits.json` (14 TAS).
- Ограничение: SNF/TAS — сильноточная арена; EUCAS-китайские площадки частично вне охвата.
