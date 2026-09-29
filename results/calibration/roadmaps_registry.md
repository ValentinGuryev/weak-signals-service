# Реестр roadmap/readiness-документов (СП) — для анализа «сигналов за» тренды

> **Цель:** собрать все roadmap/readiness/vision-документы по сверхпроводимости (2008-2024),
> чтобы анализировать «сигнал поддержки» (про-сигнал) для кейсов: какие темы были в повестке
> планировщиков, когда и как «вес» темы менялся.
> **Дата:** . Источники: `literature/Trends/` + SNF-база.
> **Ключевой инсайт:** roadmap'ы — живой индикатор «веры планировщиков». Пока тема в активной
> повестке (раздел, sub-project) — сильный про-сигнал; как только остаётся общим упоминанием
> или исчезает — про-сигнал угас (раньше, чем публикации). Пример: SMES — активен 2008-2011,
> к 2015-16 лишь общее упоминание, к 2022+ исчез.

---

## 1. Roadmap'ы по годам

| Год | Документ | Домен | Про-SMES? | Файл |
|---|---|---|---|---|
| 2010 | **The 2010 European Roadmap on Superconductive Electronics** (FLUXONICS/FP7) | электроника | — | `literature/Trends/(2010) !!! European Roadmap...` |
| 2015 | **HTS Roadmap for the Electric Power Sector 2015-2030** (Marchionini: Energetics/ISTEC/Univ.Tokyo/RSE) | **энергетика** | 1 упоминание, без раздела | `data/raw/conferences/snf_ieeecsc/downloads_renamed/(2015) [ASC] HTS Roadmap...` |
| ~2016 | **HTS Application Readiness Map – Energy Delivery** (ESNF) | энергетика | 1 упоминание преимуществ, без TRL | `downloads_renamed/[DOC] HTS Application Readiness Map...` + v2/collections |
| 2017+ | **International Roadmap for Devices and Systems (IRDS)** (Holmes) | электроника | — | `downloads_renamed/(2017) [ART] International Roadmap...` |
| 2017 | **SC Electronics and the IRDS** (Holmes/DeBenedictis, ISEC) | электроника | — | v2 |
| 2018 | **Roadmapping is an important tool... (E45)** | электроника | — | downloads_renamed |
| 2018 | **New Roadmapping Effort for Cryogenic Electronics** | крио-электроника | — | downloads_renamed |
| 2022-23 | **Keys Needs in the Technology Roadmap for Superconductor Electronics** | электроника | — | downloads_renamed + v2 |
| 2022 | **Superconducting Quantum Computing Technology Roadmap: First Cut** (Holmes, IRDS) | квант. вычисления | — | downloads_renamed + v2 |
| 2024 | **Grand challenges, Strategic Roadmap and Consortia for SC Electronics & QIP** | электроника/кванты | — | downloads_renamed |

### Digests (детальные выжимки, results/calibration/roadmap_digests/)
| Документ | Digest |
|---|---|
| IEA HTS Roadmap 2015-2030 (2016) | `(2016) IEA HTS Roadmap 2015-2030 — Marchionini — digest.md` |
| IEA Readiness Map Energy Delivery (~2021) | `(2021) IEA HTS Readiness Map — Energy Delivery — digest.md` (TRL-таблица 8 применений) |
| IRDS SC Electronics (2017) | `(2017) IRDS — SC Electronics — Holmes — digest.md` |
| European Roadmap 2010 + IRDS 2022-24 | `SCE-roadmaps_BEFORE-2018_vs_AFTER-2022.md` (⭐ сравнение эпох) |

## 2. Документы-предшественники из literature/Trends (2008-2012, «эпоха веры в энергетику»)

| Год | Документ | Про-SMES |
|---|---|---|
| 2008 | Prusseit — Superconductor Industry in Germany | SMES в списке HTS-энергоприменений |
| 2009 | Hasuo — Recent Activities at ISTEC (Japan) | SMES — sub-project NEDO (нац. программа) |
| 2010-11 | Braunschweiger Supraleiterseminar | СП в энергетике (энергопереход) |
| 2012 | Lin & Zheng — History of Applied SC in China | SMES 1 МДж HTS (2010), HTS-подстанция |

## 3. Наблюдения (для методологии)

1. **Сдвиг фокуса roadmap'ов:** 2008-2012 — «энергетика» (кабели, FCL, SMES, генераторы);
   2015-2016 — энергетика, но SMES уже на обочине (кабели/FCL/трансформаторы в центре);
   2017+ — **электроника/квантовые вычисления** доминируют (IRDS, cryo-electronics, quantum roadmap).
2. **Что предсказали верно/неверно** (по TRENDS_REPORT): верно — детекторы (SNSPD/MKID), квантовые
   вычисления, крио-фри; неверно — энергетические HTS (кабели в сетях, SMES, SFCL массово).
3. **Roadmap'ы ≠ предсказание рынка:** они отражают гос. политику/консенсус академии, пишутся
   медленно, не видят экспоненциальных конкурентов (Li-ion). Про-сигнал из roadmap'а надо
   **взвешивать по времени**: «свежий раздел» ≠ «общее упоминание» ≠ «исчезновение».
4. **Для ML:** фича-кандидат `roadmap_weight` (раздел/упоминание/нет по годам) + `roadmap_trend`
   (растёт/падает вес темы в roadmap'ах) — ранний индикатор, опережающий публикации (SMES).

## 4. Связь с кейсами

- **005_SMES:** детальный разбор — `case_studies/005_SMES/signals/pro_signals_roadmaps.md`;
- **hts_ac_cables / sfcl / transformers / генераторы:** Readiness Map 2016 + HTS Roadmap 2015 дают
  TRL-статус этих тем (для калибровки «дорожных карт»);
- **электроника/кванты (rsfq_cmos, jtwpa, sc_qubits):** IRDS + Quantum Roadmap 2022-23 — как
  планировщики видят СП-электронику. ⭐ Сравнение эпох (2010 vs 2022): `roadmap_digests/SCE-roadmaps_BEFORE-2018_vs_AFTER-2022.md`.

## 4а. ⭐ Roadmap'ы по СП-электронике: хронология фокуса (2026-09-02)

| Год | Документ | Фокус |
|---|---|---|
| 2009-10 | S-Pulse N2/N3 + **European Roadmap 2010** | Детекторы/измерения (приор. 1-2), ADC, RSFQ-цифра «как замена CMOS» |
| 2017 | IRDS SC Electronics (Holmes/DeBenedictis) | **Мост:** SCE → QIP/датчики/вычисления; коммерч.: voltage std, digital-RF, D-Wave |
| 2018 | New Roadmapping Effort (Cryo Electronics & QIP) | IFT в IRDS, cryo-semiconductor включён |
| 2022-23 | Quantum Roadmap First Cut + Keys Needs | **QIP доминирует** (1M кубитов IBM/Google); RSFQ — «partial, not ready»; честно: «не знаем как построить QC» |
| 2024 | Grand Challenges (ScGA) | White paper SCE+QIP, TRL, консорциумы, **imec**; UN SDG |

**Главный сдвиг:** от «СП-электроника для измерений/цифры» (2010) к «СП-электроника как инфраструктура квантовых вычислений» (2022+). RSFQ-мечта «заменить CMOS» тихо умерла в roadmap'ах к 2017-2022.

## 5. TODO

- [x] Прочитать детально Readiness Map 2016/2021 (TRL кабелей/FCL/трансформаторов) → выжимка: `results/calibration/roadmap_digests/(2021) IEA HTS Readiness Map — Energy Delivery — digest.md`;
- [x] Прочитать HTS Roadmap 2015-2030 (расширенный абстракт) → выжимка: `results/calibration/roadmap_digests/(2016) IEA HTS Roadmap 2015-2030 — Marchionini — digest.md`;
- [x] Разобрать IRDS 2017 → digest; сравнить эпохи SCE-roadmap'ов (2010 vs 2022) → `SCE-roadmaps_BEFORE-2018_vs_AFTER-2022.md`;
- [ ] Найти полный IRDS CEQIP 2022 report (irds.ieee.org/editions) — в SNF только слайды;
- [ ] Свести: какие темы из roadmap'ов 2010-х выстрелили/нет → таблица для ML (roadmap-калибровка);
- [ ] Внести данные сравнения в кейсы sc_qubits / rsfq_cmos / cryo_cmos / jtwpa.
