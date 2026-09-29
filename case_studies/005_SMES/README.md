# Кейс 005: SMES (Superconducting Magnetic Energy Storage)

> **⭐ ГЛАВНЫЙ АРТЕФАКТ — [NARRATIVE.md](NARRATIVE.md)** (история кейса для жюри, каждый факт — с документом).
> **Вердикт:** ❌ «не стоило» — SMES не состоялся (нет коммерческих установок к 2026).
> **Ключевая причина (S5):** Li-ion BESS подешевел на 97% за 25 лет (гигафабрики/learning curve)
> → разрыв ~5000× по $/кВт·ч. См. `signals/s5_bess_competition.md`, `plots/plot_s5_smes_vs_bess.png`.

> **Вопрос кейса:** правда ли, что до ~2018 года SMES казался очень перспективным направлением, были объявлены амбициозные проекты (SMES-BESS, DVC-SMES, K-SMES), и все они были закрыты к 2022 году?
>
> **Цель:** факт-чекинг по статьям и открытым источникам (OpenAlex, arXiv, CORDIS, РНФ, патенты).

---

## 1. Первичный факт-чекинг (OpenAlex, )

### 1.1 Наука по SMES — НЕ упала
Динамика публикаций с «magnetic energy storage» в title (выборка 400 работ):
```
1990: 9 | 1993: 12 | 2002: 12 | 2005: 13 | 2008: 15 | 2012: 18 | 2015: 13 | 2018: 16 | 2021: 14 | 2022: 18 | 2023: 16 | 2024: 5
```
**Вывод:** публикации стабильны (10–18/год), даже рост в 2012, 2018, 2022. **Наука по SMES не умерла** — но и не взрывалась.

### 1.2 Проекты (демо/индустриальные) — НЕ в OpenAlex под этими именами
Критично: **«SMES-BESS», «DVC-SMES», «K-SMES» НЕ находятся в OpenAlex как проекты** (поиск даёт шум: SME = малый бизнес, Digital Value Chain). Это значит — **это отраслевые/демонстрационные проекты, не академические**. Их надо проверять по новостям/отчётам, НЕ по OpenAlex.

### 1.3 Найденные реальные SMES-проекты (академический след)

**K-SMES (Корея) — подтверждён!**
- **«Development of a 3MJ/750kVA SMES system»** (Cryogenics, 2006) — Hae-Jong Kim, Ki-Chul Seong, Jeonwook Cho, Joon-Han Bae et al. — **Hyundai Heavy Industries, Gyeongsang National Univ, Chonnam National Univ, KERI**.
- Серия: 1 MJ (2002), 3 MJ (2004–2006), 600 kJ HTS (2006–2007), 2.5 MJ HTS (2009), 5 MJ HTS (2011).
- Это **корейская национальная программа SMES** (Hyundai + KERI + университеты).

**Китайский HTS SMES (вероятно, SMES-BESS или родственный)**
- **«100 kJ/50 kW HTS SMES for Micro-Grid»** (IEEE TAS, 2014) — Meng Song, Jing Shi, Yang Liu et al. — **China Southern Power Grid + Huazhong University (HUST)**.
- **«Experimental demonstration and application planning of HTS energy storage system for renewable power grids»** (Applied Energy, 2014) — Jiahui Zhu, Weijia Yuan, Ming Qiu et al. — **China Electric Power Research Institute (CEPRI) + University of Bath**.

**DVC-SMES (Dynamic Voltage Compensation) — косвенные следы**
- Прямых статей под именем «DVC-SMES» нет. Ближайшие: **«SMES Based Dynamic Voltage Restorer for Voltage Fluctuations Compensation»** (IEEE TAS, 2010), **«Performance Evaluation of a MW-Class SMES-BES DVR System»** (IEEE TIA, 2018), **«A Superconducting Magnetic Energy Storage-Emulator/Battery Supported Dynamic Voltage Restorer»** (IEEE TEC, 2016, Bath).
- Вероятно, DVC-SMES = корейский/китайский проект по **DVR** (dynamic voltage restorer) на SMES.

### 1.4 SMES-BESS (гибрид SMES + батареи)
- 13 работ с «SMES BESS» в title (2009–2022): «Comparative performance of BESS and SMES» (2009), «A hybridized SMES/BESS Optimal Storage System» (2018), «Research on Control Strategy of SMES-BESS Hybrid Energy Storage System in DC Microgrid» (2022).
- Тренд: гибрид SMES (быстрый, мощность) + BESS (ёмкость, энергия) — **активно изучался в 2015–2022**.

### 1.5 Чего НЕТ в OpenAlex (пробел для проверки)
- **Нет статей о «закрытии» проектов** (закрытия не публикуют в академии).
- Нет официальных отчётов о судьбе K-SMES после 2011, китайских проектов после 2014–2016, DVC-SMES вообще.
- arXiv по SMES — почти пусто (SMES = инженерная тема, не arXiv).

---

## 2. Гипотезы о закрытии к 2022 (для проверки по новостям)

1. **Экономика:** SMES дорог (криогеника, ВТСП-ленты ~$50-100/kA·м), энергия/стоимость << батарей. Li-ion BESS подешевел в ~10 раз за 2010–2020 → SMES проиграл по $/кВт·ч.
2. **Технология:** SMES хорош для мощности (МВт, мс), но плох для энергии (МДж, сек) — малая ёмкость. Батареи/суперконденсаторы покрывают оба случая дешевле.
3. **Демо-статус:** проекты были демонстрационными (100 kJ–5 MJ, кВА–МВА) — после демо нет коммерциализации.
4. **Сдвиг к другим СП-применениям:** фокус ушёл на ВТСП-кабели (SCARLET), термояд (CFS), квантовые (кубиты) — где СП даёт уникальное преимущество.

---

## 3. Что нужно проверить (факт-чекинг по новостям/отчётам)

- [ ] Судьба **K-SMES** (Корея): последние упоминания, почему остановились после 5 MJ (2011).
- [ ] Судьба **китайских HTS SMES** (100 kJ/50 kW, CEPRI): закрыты ли.
- [ ] **DVC-SMES**: что это конкретно (страна, консорциум, годы), почему закрыт.
- [ ] **SMES-BESS**: гибридные проекты — были ли демо, их судьба.
- [ ] Обзоры 2020–2023: как оценивают SMES (Jubleanu 2022 «Overview of SMES technology», Vyas 2020).

---

## 4. Мульти-базовый сигнал (обновлён 2026-09-02)

| База | SMES | Комментарий |
|---|---|---|
| **OpenAlex** | стабильно 14-41/год, не растёт (пик 2023: 41) | наука жива, но не «горячая» |
| **Конкуренты (S5)** | BESS 693/год (2025), Supercap 549 — растут ×60 | **BESS раздавил SMES** (см. signals/s5_bess_competition.md) |
| **arXiv** | почти пусто | инженерная тема, не физика |
| **Патенты** | 100 в topics/smes.json, 84 релевантных | см. signals/patent_signal.md |
| **Проекты** | K-SMES остановлен (2012), Япония свернула, JRC: «no big facilities» | только CORC-SMES для ускорителей жив (2022) |

**S5-график:** `plots/plot_s5_smes_vs_bess.png` (SMES плоский vs BESS/Supercap экспонента).

### Сигналы кейса (signals/, 8 файлов)

| Файл | Содержание |
|---|---|
| `s5_bess_competition.md` | S5: BESS/Supercap раздавили SMES (×63/×61) |
| `s2_s3_s4.md` | S2 = не применим (инженерная с рождения); S3 = plateau; **S4 = физич. рекорды есть, экономич. предел НЕ снят** |
| `grant_signal.md` | Гранты NSF/CORDIS/KAKEN = 0; только гос. программы |
| `conference_signal.md` | IEEE TAS 54: пик 2007 → спад → Китай 2024 |
| `patent_signal.md` | SMES 130 патентов (Google+Lens) |
| `false_trend_signals.md` | ⭐ Обучающий кейс «ложный тренд»: окно 2003-2012, crossover 2009 |
| `pro_signals_roadmaps.md` | ⭐ Про-сигналы (2008-2011): roadmap'ы/обзоры (Prusseit, ISTEC/NEDO, Braunschweig, Lin-Zheng), говорившие ЗА SMES как энерготренд; урок: roadmap-поддержка ≠ успех |
| `niche_accelerators.md` | ⭐ Ниша ускорителей (2026-09-03): почему SMES безальтернативен ТОЛЬКО там; NICA (JINR+ASIPP), KEK; конденсаторный контраргумент; `niche_alive=1` |

### Карта графиков кейса (plots/)

| График | Что показывает |
|---|---|
| `plot_s5_smes_vs_bess.png` | SMES vs BESS/Supercap публикации 2005-2026 (экспонента конкурентов) |
| `plot_pubs_2005_2015.png` | Публикации SMES vs BESS 2005-2015, пересечение 2009 (ранний сигнал) |
| `plot_smes_window_crossover.png` | Окно тренда 2003-2012 + точка пересечения 2009 |
| `plot_patents_signal_2000_2020.png` | **Патентный отклик**: SMES (130) vs BESS (83) 2000-2020, по географии |
| `plot_grants_signal.png` | **Грантовый отклик**: NSF/CORDIS/KAKEN = 0 + нац. программы (NEDO, K-SMES...) |
| `plot_conference_signal.png` | **Конференционный отклик**: IEEE TAS 1993-2025 (пик 2007 → спад → Китай 2024) |
| `plot_prices_liion_vs_smes.png` | Цены Li-ion (экспонента) vs SMES (плато), лог-шкала |

**Данные для графиков:** публикации — `data/raw/openalex/smes_vs_bess_counts.json`;
патенты — `data/raw/patents/cases/005_smes.json` + `bess_lens.json`; конференции — `conference_hits.json`;
гранты — NSF/CORDIS API + литература. Скрипты: `src/plot_*smes*.py`, `src/plot_grants_signal.py`, `src/plot_conference_signal.py`.

---

## 5. Литература кейса

`literature/` — PDF + выжимки по протоколу внутренний контракт §4.2a/4.3. **28 PDF ↔ 28 MD** (2026-09-03):
основная библиотека (BPA 1979, Tatsuta 2004, KERI 2006/09, Chen 2009, Lee 2012, Kotoyori 2013,
Rong&Barnes 2017, Soman 2018, Ziegler&Trancik 2020, Fadly 2021, Li 2022, JRC 2025) +
**ниша ускорителей (13)** (Khodzhibagiyan 2020, Zheng 2023, Kondratiev 2022, Ise 2003, Sato 2004/07/10,
Akagi 2003, Praeg 1985, Ankenbrandt 2002, Butenko 2021, Penthia 2020, García-Tabarés 2025, Elalfy 2024,
Nomura 2010).

**Ключевые статьи для скачивания:**
1. Kim et al. «Development of a 3MJ/750kVA SMES system» (Cryogenics 2006) — K-SMES.
2. Song et al. «100 kJ/50 kW HTS SMES for Micro-Grid» (IEEE TAS 2014) — китайский.
3. Zhu et al. «Experimental demonstration... HTS energy storage» (Applied Energy 2014) — CEPRI/Bath.
4. Jubleanu «Overview of SMES technology» (2022) — обзор.
5. Vyas & Dondapati «Superconducting Magnetic Energy Storage (SMES)» (2020) — обзор.
6. Обзор энергохранилищ 2020–2022 (сравнение SMES vs BESS vs суперконденсаторы).

---

## 6. Открытые вопросы

- [ ] Точные годы запуска/закрытия каждого проекта (SMES-BESS, DVC-SMES, K-SMES).
- [ ] Страны и консорциумы (Корея, Китай, возможно Япония/ЕС/США).
- [ ] Причины закрытия (экономика/технология/политика).
- [ ] Есть ли живущие SMES-ниши (космос? импульсные источники? металлургия?).

---

## 7. Факт-чекинг: судьба K-SMES (дополнение 2026-08-18)

### Что подтверждено OpenAlex
- **K-SMES = корейская национальная программа** (Hyundai Heavy Industries + KERI + Gyeongsang/Chonnam/Korea University).
- Серия: 1 MJ (2002) → 3 MJ/750 kVA (2006, Cryogenics) → 600 kJ HTS (2006–2008) → 2.5 MJ HTS (2009–2010) → **5 MJ HTS (2011, «Design of HTS Toroidal Magnets for a 5 MJ SMES»)**.
- После 2011 — **нет публикаций** (последний след — 5 MJ).

### Гипотеза «150 кВт на криокуллеры для 2 МВт»
- **НЕ подтверждена и НЕ опровергнута** в OpenAlex/доступных полных текстах.
- Rong & Barnes 2017 (обзор вызовов SMES, US Army) — **не содержит** K-SMES/2МВт/150кВт (проверен полный текст).
- Данные об охлаждении — в **корейских/японских статьях по криокуллерам**: Kotoyori 2013 (IEEE TAS 23, 3800604), Song & Lee 2012 (Cryogenics 52, 648), Hirano 2016 (Cryogenics 50, 674) — добавлены в wishlist.
- **Для подтверждения 150 кВт нужен источник:** корейская статья по охлаждению K-SMES или отраслевой отчёт.

### Другие SMES-проекты (найдены)
- **Япония:** MVA-класс SMES (Chubu Electric + Toshiba, Bi-2212, 2005) — «Development of MVA Class HTS SMES System for Bridging Instantaneous Voltage Dips» (IEEE TAS, 2005).
- **Китай:** 100 kJ/50 kW HTS SMES (China Southern Power Grid + HUST, 2014), CEPRI + Bath демо (Applied Energy 2014).
- **США:** 1 MJ/100 kW HTS (Southampton 2020 — экономика: $200/кВт, >20 лет, >95%).

### Экономика SMES (из литературы)
- SMES: **выше мощность при меньшем капитальном косте (до $200/кВт)**, срок >20 лет, эффективность >95% (Zimmermann & Sharkh 2020).
- НО: технология недоразвита, нет крупных 2G-HTS установок, криокуллеры потребляют много.
- Конкуренция: Li-ion BESS подешевел ~10× за 2010–2020 → SMES проиграл по $/кВт·ч.

### Итог факт-чекинга
| Тезис | Статус |
|---|---|
| SMES был перспективен до 2018 | ✅ подтверждено (много проектов, обзоры) |
| K-SMES существовал (Корея) | ✅ подтверждено (до 2011) |
| SMES-BESS гибриды | ✅ существовали (13 работ, 2009–2022) |
| DVC-SMES | ⚠️ как проект не найден (вероятно DVR на SMES) |
| Проекты закрыты к 2022 | ⚠️ не подтверждено/опровергнуто (нет данных о закрытиях) |
| 150 кВт на криокуллеры (2 МВт) | ❓ нужен источник (корейские статьи по охлаждению) |

---

## 8. КЛЮЧЕВЫЕ НАХОДКИ из литературы (выжимки, 2026-08-18)

### 8.1 Гипотеза «150 кВт на криокуллеры» — НАЙДЕН ИСТОЧНИК ПУТАНИЦЫ!
Из **kim2009 (KERI 600 kJ SMES, Cryogenics)**:
- **«150 kW» в K-SMES — это ВЫХОДНАЯ мощность компенсации** (150 kW в течение 3 с, DC link 1.5 kV), а НЕ потребление криокуллеров!
- Реальные тепловые потери системы: **фоновые 6 Вт** + потери при заряде (~28 J AC).
- Потребление криокуллеров из розетки: ~6 Вт × (эффективность Карно ~1/200 при 6 K) ≈ **1–2 кВт электроэнергии** — НЕ 150 кВт.
- **Вывод:** гипотеза «150 кВт на криокуллеры» — вероятно, неверно интерпретированные 150 kW выходной мощности компенсации.

### 8.2 K-SMES: полная картина программы (3 фазы)
Из **seyeonlee2012 (5 MJ)**:
- Фаза 1: 600 kJ (соленоид, BSCCO) — ✅ сделано (kim2006, kim2009).
- Фаза 2: 2.5 MJ (тороид, 28 катушек, 2G REBCO).
- Фаза 3: 5 MJ (тороид, 64 SPC, **18.11 км REBCO-ленты, 14 K**) — проектировался в 2012, **последний след — нет публикаций о постройке**.

### 8.3 Экономика SMES (почему не пошёл в коммерцию)
Из **Fadly 2021 (диссертация Strathclyde)**:
- **Стоимость SMES: $70–100K/MJ** (utility). Для 5 MJ = $350–500K при ёмкости 5 МДж = **1.4 кВт·ч**! Абсурд vs Li-ion (~$150/кВт·ч).
- **Криогеника: 5–10% стоимости** (или $15–25K/MJ = 25%).
- Магнит: 20–25%, конвертер: до 30%.
- **Рефрижерация — НЕ доминирующий фактор** (5–10%) → опровергает «150 кВт» как главную причину.

### 8.4 Официальный вердикт ЕС (JRC 2025)
Из **JRC141463**: «SMES... implementation is **very low, with no relevant big facilities**... faces challenges related to **cost, complexity and scalability**» — официальное подтверждение неразвёрнутости.

### 8.5 SMES НЕ умер — есть живущая ниша: ускорители (R&D)! (обновлено 2026-09-03)
Из **Li 2022 (SuST)**: Китай (CAS Hefei) строит **1 MJ SMES для ускорителей** (CORC, 4 kA, 125 mH, kA/s).
Другие активные: ABB/BNL/SuperPower 425 kJ, Southampton 1 MJ, Bologna 500 kJ (MgB2, DRYSMES4GRID).

**Обновление (после докачки 13 PDF, 2026-09-03) — полная картина ниши ускорителей:**
- **NICA (ОИЯИ, Дубна) подтверждён:** JINR проектирует HTS SMES 3–5 МДж / 10–12 кА / 6–7 Тл (Brooks coil,
  CORC) для энергообмена бустер↔нуклотрон (Khodzhibagiyan 2020; тест-стенд — Kondratiev 2022);
- **Китайско-российская программа:** CAS Hefei/ASIPP + JINR — 12 kA forced-flow HTS SMES 0.5 МДж для NICA
  (Zheng 2023, изготовление) — тот же коллектив, что Li 2022 → единая kA-SMES программа;
- **Японская школа KEK (2003–2010):** SMES-компенсация пульсаций J-PARC/medical (Ise 2003, Sato 2004/07/10) —
  моделирование, не внедрено; Sato 2010 — прямое сравнение SMES vs маховик/battery/EDLC;
- **⚠️ Контраргумент:** действующий бустер NICA (запущен 2020-21) делает энергообмен **конденсаторами
  60 Ф/400 В** в источнике PIT11, а НЕ SMES (Butenko, УФН 2021) → ниша SMES = только двухкольцевой
  противофазный энергообмен; внедрённого SMES на ускорителях нет нигде (все — R&D/концепт).

**Полный разбор:** `signals/niche_accelerators.md`. Литература (13 PDF+MD, включая Khodzhibagiyan 2020,
Zheng 2023, Kondratiev 2022, Ise 2003, Sato ×3, Akagi, Praeg, Ankenbrandt, Butenko, Penthia, García-Tabarés,
Elalfy, Nomura) — в `literature/`.

### 8.6 Япония: барьер = стоимость (с 1998)
Из **tatsuta2004**: японская программа (20 MW/100 kWh, затем 100 MW/15 kWh LTS) признала: «considerable cost reduction of the coil was indispensable».

---

## 9. Итог для кейса (2026-08-18)

**Главный вывод:** SMES «умер» не из-за 150 кВт на криокуллеры (это путаница с выходной мощностью), а из-за **экономики**: $70–100K/MJ vs Li-ion ~$150/кВт·ч (разница в 1000× по энергии), при криогенике лишь 5–10% стоимости. Проекты (K-SMES, японские, китайские) завершились демо-стадией (≤5 MJ) без коммерциализации. Однако **ниша ускорителей жива как R&D** (Китай 2022, 1 MJ CORC-SMES; NICA: JINR+ASIPP 2020-2023, 3–5 МДж/12 kA; японская школа 2003-2010) — при том, что действующий бустер NICA использует конденсаторный энергообмен, а не SMES (verdict «не состоялся для массового рынка» сохраняется, `niche_alive=1`).
