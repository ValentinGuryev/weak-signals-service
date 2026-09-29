# Roadmap'ы по СП-электронике: ДО 2018 vs ПОСЛЕ 2022 — сравнение

> **Цель:** сравнить, о чём говорили roadmap'ы по сверхпроводящей электронике (SCE)
> в эпоху «до 2018» (European Roadmap 2010, S-Pulse, IRDS 2017) и «после 2022»
> (IRDS CEQIP 2022-23, Keys Needs 2023, Quantum Roadmap, Grand Challenges 2024).
> **Дата:** . Источники: `literature/Trends/` + SNF-база.
> **Автор анализа:** агент. Все факты — из документов (пути ниже).

---

## 1. Документы

### До 2018
| Документ | Год | Тип | Полнота в базе | Файл |
|---|---|---|---|---|
| European Roadmap on Superconductive Electronics (S-PULSE/FLUXONICS, FP7) | 2010 | полный roadmap (48 стр., Physica C 470) | ✅ полный PDF | `downloads_renamed_v2/collections/(2010) The 2010 European Roadmap...` + выжимка `literature/Trends/` |
| S-Pulse N2 (SC Electronics Manifesto) | 2009 | манифест | ✅ | `literature/Trends/(2009) !!! S-Pulse N2...` |
| S-Pulse N3 (Interface Amplifiers for RSFQ) | 2009 | статья | ✅ | `literature/Trends/(2009) !!! S-Pulse N3...` |
| **SC Electronics & IRDS (Holmes/DeBenedictis)** | **2017** | статья-манифест (полная) | ✅ | `downloads_renamed/(2017) [ART] International Roadmap for Devices and Systems.pdf` |
| New Roadmapping Effort for Cryogenic Electronics & QIP | 2018 | призыв к участию | ✅ | `downloads_renamed/(2018) [ASC] New Roadmapping Effort...` |

### После 2022
| Документ | Год | Тип | Полнота | Файл |
|---|---|---|---|---|
| **Superconducting Quantum Computing Technology Roadmap: First Cut** (IRDS CEQIP) | 2022 | презентация ASC (слайды!) | ✅ | `downloads_renamed_v2/(2022) [ASC] Superconductivity Conference...quantum computing technology roadmap_.pdf` |
| Keys Needs in the Technology Roadmap for SCE (Holmes) | 2022-23 | абстракт ASC | абстракт | `downloads_renamed/(2023) [ASC] Keys Needs...` |
| Grand challenges, Strategic Roadmap and Consortia for SCE & QIP (ScGA) | 2024 | абстракт ASC | абстракт | `downloads_renamed/(2024) [ASC] Grand challenges...` |

---

## 2. Что было в фокусе: ДО 2018

### European Roadmap 2010 — 4 приоритета (по убыванию)
1. **Ultra-Sensitive Sensing and Imaging** — СП-детекторы (мм→нм волны, meV→keV): THz-имиджинг, инфракрасные, масс-спектрометрия макромолекул. «Детекторы выбора»;
2. **Quantum Measurement Instrumentation** — квантовые стандарты (вольт, ток sub-nA), «quantum multimeter», привязка единиц к фундаментальным константам;
3. **Advanced Analog-to-Digital Converters** — сверхбыстрые АЦП (для software-defined radio, когнитивного радио);
4. **Superconductive Electronics Technology** — VLSI-интеграция, foundry, дизайн-инфраструктура (EDA).

**Ключевой контекст 2010:** Европа «уже отстала от США и Японии» (SWOT: threads — потеря позиций). RSFQ-цифра упоминается («scalable, 0.1 μW/gate при 100 GHz, 3D-интеграция»), но **приоритеты — sensing/measurement/ADC, НЕ замена CMOS**. S-Pulse N2 (2009) — манифест «квантово-ограниченные детекторы + цифровые схемы».

### IRDS 2017 (Holmes/DeBenedictis) — МОСТ
- Смена парадигмы: ITRS (масштабирование) → IRDS (application-driven, Beyond CMOS);
- SCE = часть Beyond CMOS (с мемристорами, спинтроникой);
- **Коммерческие применения SCE (2017):** Josephson voltage standards, **digital-RF receivers**, **quantum annealing coprocessors (D-Wave)**;
- Драйверы R&D: **quantum information processing, sensor/detector arrays, superconducting computing**;
- Метрики/бенчмарки: сравнение RQL-ALU (205 aJ/op, 402 ps, 16.3 GHz при 4.2 K) с beyond-CMOS при учёте стоимости крио (400-10 000 Вт/Вт);
- **Вызов foundry:** из 2 foundry (>100k JJ) MIT-LL не может делать коммерческие продукты, D-Wave — ограничен. Нужен коммерческий foundry;
- Дальнее будущее: HPC/data centers (много параллельных процессоров);
- **RSFQ-цифра → для квантовых контроллеров и data centers, НЕ «замена CMOS на десктопе».**

### New Roadmapping Effort 2018
- Создан IFT **Cryogenic Electronics and QIP** в IRDS (21 человек);
- Покрытие: superconductor electronics + cryogenic semiconductor electronics + cryogenic quantum computing;
- Отчёт 2018: applications/market drivers, present status, active research questions, metrics, roadmap.

---

## 3. Что в фокусе: ПОСЛЕ 2022

### IRDS CEQIP 2022 (Quantum Roadmap First Cut + слайды)
- **QIP (Quantum Information Processing) доминирует** (разделы 4.1-4.5): optimization, cryptanalysis, quantum simulation, QML;
- **Цель: 1 млн физических кубитов** (IBM и Google timelines);
- Ключевые технологии: physical qubits (низкие error rates), error correction (логические кубиты), readout, interconnects (крио→комната), control electronics;
- **Difficult challenges (2022-2029):** physical qubits (coherence/gate fidelity), logical qubits, readout, interconnects, control electronics;
- **«We still don't know how to build a full-scale quantum computer»;**
- Сравнение кубитов: supercond. (QV 512, 127 qubits), trapped ion (QV 4096, 32 qubits), quantum dot, photonic; **«no approach has emerged as most likely to scale to millions of qubits»** — автомобильная аналогия (1900: бензин/пар/электричество);
- **SCE (сама по себе): «partial roadmaps», «not yet ready for roadmaps»** — т.е. цифровая СП-электроника отодвинута на второй план;
- **Keys Needs 2023:** улучшения нужны для quantum computing, **AI**, large-scale digital computing — метрики: circuit density, complexity, energy efficiency.

### Grand Challenges 2024 (ScGA — Superconductivity Global Alliance)
- White paper по SCE + QIP; **grand challenges + TRL выбранных технологий + консорциумы**;
- Связь с UN SDG (17 целей устойчивого развития);
- Авторы: Holmes (USC), Leese (Tech Vector), **Anna Herr (imec)**, Foley (Австралия), Pepe (Napoli);
- **imec в игре** (европейский foundry-гигант!) — сигнал индустриализации.

---

## 4. ⭐ Сравнение: ДО 2018 vs ПОСЛЕ 2022

| Аспект | ДО 2018 (2010-2017) | ПОСЛЕ 2022 (2022-2024) |
|---|---|---|
| **Главный драйвер** | Наука/измерения: детекторы, квантовые стандарты, ADC | **Квантовые вычисления (QIP)** — 1M qubits |
| **Судьба RSFQ/SFQ-цифры** | Претендент на HPC/замену CMOS (2010); к 2017 — ниша (data centers, квант. контроллеры) | «Partial roadmaps, not ready» — отодвинута; нужна для control electronics кубитов |
| **Коммерческие продукты** | Voltage standards, digital-RF (2017) | Quantum annealing (D-Wave), квант. вычисления (IBM/Google) |
| **Детекторы** | Приоритет №1 (2010) | Упоминаются (sensing), но QIP в центре |
| **Foundry** | Проблема: нет коммерческого foundry (2017) | ScGA + **imec** (2024) — индустриализация |
| **Честность прогноза** | Уверенность в сроках (2010→2020) | «We still don't know how to build full-scale QC»; «no approach emerged as most likely» (2022) |
| **Роль СП** | Самоценная технология | Средство для QIP + cryo-semiconductor (cryo-CMOS) |
| **География** | Европа догоняет США/Японию (2010) | Глобально: США/Европа/Азия; imec, ScGA |

---

## 5. Ключевые инсайты для проекта

1. **Главный сдвиг (2010 → 2022):** от «СП-электроника для измерений/цифры» к «СП-электроника как инфраструктура квантовых вычислений». RSFQ-цифра «как замена CMOS» тихо умерла в roadmap'ах (к 2017 — ниша, к 2022 — «partial»);
2. **Что roadmap'ы предсказали верно:** детекторы (SNSPD/TES) — были приоритетом 2010, выстрелили; квантовые вычисления — выросли в главный тренд;
3. **Чего не предвидели:** что квант. вычисления пойдут через **transmon-кубиты, а не RSFQ-цифру**; что cryo-CMOS (полупроводник при 4 K) станет конкурентом/компаньоном SCE; скорость роста QC-индустрии;
4. **Методологический урок (для ML):** roadmap'ы 2010 и 2022 — РАЗНЫЕ миры (measurement→QIP). «СП-электроника» как тема — не монолит: детекторы (выстрелили), RSFQ-цифра (нет), квант. контроллеры (да). **При анализе тренда по roadmap'ам надо смотреть на конкретное применение, не на «СП-электронику» в целом;**
5. **Связь с кейсами:** rsfq_cmos (#46, «RSFQ как замена CMOS — не стоило» → подтверждено: в roadmap'ах 2022 RSFQ «partial»), jtwpa (#52, чтение кубитов — да, выстрелил), sc_qubits (transmon-путь — выстрелил), cryo_cmos (#31 — выстрелил: IRDS 2022 включает cryogenic semiconductor electronics);
6. **Ирония:** European Roadmap 2010 предупреждал «Европа отстаёт в цифровой SCE» — а к 2024 главные игроки QIP — США (IBM/Google) + imec (Европа через foundry). RSFQ-мечта Европы (FLUXONICS) не материализовалась как индустрия, но СП-электроника вернулась через QIP.

---

## 6. TODO
- [ ] Найти полный IRDS CEQIP 2022 report (irds.ieee.org/editions) — в SNF только слайды;
- [ ] Прочитать Grand Challenges 2024 white paper (ScGA) — в SNF абстракт;
- [ ] Сравнить с кейсами sc_qubits, rsfq_cmos, cryo_cmos, jtwpa (внести данные в их README);
- [ ] Добавить «roadmap-калибровку» в METHODOLOGY: отслеживать вес конкретного применения в roadmap'ах по годам.
