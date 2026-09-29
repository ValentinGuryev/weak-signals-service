# A Strategic Roadmap for Implementing Superconductivity Towards Zero-Emission Transport (2026)

**Файл:** `Breschi_2026_Supercond._Sci._Technol._39_011001.pdf`
**Библиография:** M. Breschi (Univ. Bologna), A. Godeke, L. Quéval (Paris-Saclay), Z. Melhem (Oxford Quantum Solutions/Lancaster), M. Ainslie (KCL), L. Cavallucci, P. Cheetham (FAMU-FSU), L. Cooley (FSU), K. Haran (UIUC), M. Husband (GKN Aerospace), E. Nilsson (AIRBUS), S. Pamidi, M. Parizh (GE), X. Pei (Bath), W. Song (Glasgow), L. García-Tabarés (CIEMAT), M. Tomsic (Hyper Tech), M. Zhang (Strathclyde). «A strategic roadmap for implementing superconductivity towards zero-emission transport». Supercond. Sci. Technol. 39 (2026) 011001. DOI: 10.1088/1361-6668/ae34ec.
**Организация:** Transport Group of the **Superconductivity Global Alliance (ScGA)** — 30+ авторов из промышленности (Airbus, GKN, GE) и академии. Опубликован 30 января 2026 (самый свежий документ в папке!).
**Релевантность:** 5/5 — **свежайший (2026) стратегический роадмап по СП для транспорта** (авиация + суда). Показывает, что сообщество считает перспективным ПРЯМО СЕЙЧАС. Ключ для кейсов sc_aircraft_motors, cryogenic power electronics, lh2-трендов.

---

## Суть работы

Стратегический роадмап внедрения сверхпроводимости в транспорт (авиация + суда + поезда) для zero-emission. Главный тезис: **blueprints G20 по декарбонизации транспорта «упустили сверхпроводимость»**, которая даёт уникальные power density и эффективность. Два «grand challenges»: (1) грузовое судно 10 MW с полностью СП-моторами на LH2; (2) авиалайнер 30 MW с LH2 + СП.

## Рыночные возможности (оценки)

| Сектор | Рынок | СП-возможность |
|---|---|---|
| Авиация | $300-800 млрд | **>$250 млрд** (если 50% флота на СП) — крупнейший потенциал |
| Морской | ~$50 млрд (container/bulk) | $12.5 млрд (25% крупнейших судов) |
| Ж/д | $300-550 млрд | ~$40 млрд (10% связей на Mag-Lev) |

- **Авиация — крупнейший рынок, но hardest to electrify** (привлекает инвесторов);
- Транспорт = 16.2% выбросов; ~80% самолётов — short-range single-aisle (до 5500 км, до 230 пасс.) — **именно их реально сделать emission-free**;
- Поезда уже электрифицированы (менее актуально); Mag-Lev требует новой инфраструктуры.

## State-of-the-art (2026)

### Авиация
- **NASA N3X** (Hybrid Wing Body, turboelectric distributed propulsion): 2 HTS-генератора + 10-20 HTS-моторов, ~40 MW;
- **Airbus UpNext: ASCEND завершён → CRYOPROP** (2-я фаза): ретрофит обычного самолёта с LH2 и 2 СП-пропульсионными моторами (отличие от NASA — не распределённая);
- Boeing (SUGAR с NASA, Wisk, партнёрство GE Aviation/NASA по hybrid-electric); GKN H2GEAR (£50 млн+, LH2 sub-regional с крио-powertrain); Испания HIVOMOT (EU, HTS-мотор); Mako (UK), MAEVE (NL), Aura-Aero (FR);
- СП-кабели для авиации разрабатываются.

### Морской транспорт
- **US Navy:** superconducting degaussing — **80% снижение веса** vs Cu; **5 MW HTS мотор (2005, CAPS Tallahassee)**; **36.5 MW HTS мотор (2011, Philadelphia)** — 70% вес, 50% размер;
- **MHD-пропульсия** (менее конвенционально) — синергия с high-field магнитами для ускорителей;
- Все-electric ships: MVDC 12-18 kV, ~100 MW установленной мощности;
- 90% новых круизных судов — IFEP (integrated full electric propulsion); из 67 судов >10000 т — 42 IFEP;
- **LNG-танкеры + HTS-моторы** — синергия крио (LNG уже при −162°C).

## Конкурентные/альтернативные технологии (важно для S5!)
1. **Синтетические альтернативные топлива** (near-term для авиации);
2. **Обычные резистивные компоненты** (дёшево, надёжно);
3. **High-purity Al проводники** (при 20 K, в LH2-самолётах — конкурент СП!);
4. **SiC/GaN силовая электроника**;
5. **Li-ion батареи** (solid-state, supercaps — emerging);
6. Обычные турбовентиляторы/дизели.

**Вывод S5:** технологии не обязательно прямые субституты СП — но (3) high-purity Al @ 20 K — реальный конкурент для LH2-платформ.

## Ключевые цифры/TRL (Таблица 1)

| Компонент | TRL (2026) |
|---|---|
| DC MTS/HTS проводники | 8 |
| AC MTS/HTS (низкие AC-потери) | 6 |
| Частично-СП генератор | 7 |
| **Полностью-СП генератор** | **2** |
| Частично-СП мотор | 4 |
| **Полностью-СП мотор** | **2** |
| DC HTS-кабель (5 kA авиа / 10 kA судно) | 6 |
| AC HTS-кабель | 6 |
| **Криогенная силовая электроника** | **5** |
| **LH2 хранение/распределение** | **2** |
| **Системная интеграция** | **2** |

**Ключевые выкладки:**
- Плотность тока СП ~500 A/мм² vs Cu ~5 A/мм² (при RT) — **2 порядка**;
- Boeing 787: 1 MW, PTW 2.2 kW/kg (сегодня); авиалайнер 200+ пасс. требует **30 MW и PTW >10 kW/kg**;
- **>150 т батарей** для A320 (80 т) — батареи нереальны;
- LH2-cooled partially-SC машина: **PTW ~10 kW/kg**; fully-SC: **>30 kW/kg** («мощность малолитражки с массой литровой бутылки воды»);
- Высота полёта ограничивает напряжение ~10 kV → для 30 MW нужно ~3 kA → Cu неподъёмна;
- **AC-потери** — гл. барьер fully-SC (генераторы на высокой частоте); низкие AC-потери у MgB2 и Bi-2212 (не REBCO!);
- **Редкоземельные PM:** производство надо ×5 за 20 лет (EV+ветер) — невозможно; 85-90% рынка у одной страны к 2035 → **геополитический аргумент за СП-машины**;
- Power electronics = >50% потерь криосистемы.

## Hydrogen-СП синергия
- LH2: 120 MJ/kg (vs kerosene 43) — гравиметрически ×3; но объемно 8.5 MJ/л (¼ kerosene); 20.3 K;
- **Latent heat LH2 446 kJ/kg — в ~5× больше LN2** → большой тепловой буфер;
- LH2 = топливо + хладагент (для MTS MgB2 и subcooled HTS);
- Один крио-контур для топлива и охлаждения.

## Роадмап (Таблица 2): 4/7/10 лет
- Fully-SC мотор/генератор: базовые элементы (4 г.) → прототип в лабе (7) → **готов к коммерции в авиации (10 лет = 2036)**;
- DC/AC HTS-кабель: демо в лабе (4) → ready (7);
- Крио-силовая электроника: оптимизация → демо → ready (10);
- LH2 хранение: критерии безопасности → прототип → ready (10).

## Grand Challenges и потребности R&D
1. **Грузовое судно 10 MW** с fully-SC моторами на LH2 (топливо+хладагент);
2. **Авиалайнер 30 MW** с LH2 + СП.

Нужны: длинные однородные проводники; СП-кабели с низкими AC-потерями; coil winding/joints (связь с кейсом 003!); компактные plug-and-play криосистемы (kW-диапазон); **криогенная изоляция**; крио-power electronics; системная интеграция; **quench-детекция с AI/big data**.

## Партнёры/консорциумы (список компаний — в реестр!)
- **Авиация:** Airbus, BAE, Boeing, GE, GKN, Honeywell, Lockheed, Mitsubishi Electric, Northrop, Rolls-Royce, RTX (Collins/P&W), Safran, Siemens, Thales;
- **Морская:** ABB, BAE, General Dynamics, Mitsubishi, RR, Safran, Siemens, Thales, Toshiba;
- **Кабели СП:** Advanced Conductor Technologies, Furukawa, Nexans, Prysmian, Solid Material Solutions, Sumitomo;
- **Крио:** Air Liquide, Air Products, Chart, Cryofab, Cryomech, Cryostar, Linde, Oxford Instruments, Sumitomo Heavy;
- **Водород:** Air Liquide, Air Products, Ballard, Hydrogenics, ITM, Linde, McPhy, Plug Power;
- **Провод:** ASG (Columbus), Bruker, Hyper Tech, Luvata, Shanghai SC, Solid Material, Sumitomo, Faraday Factory Japan, SuNAM, SuperPower, Theva.

## Значимость для проекта

1. **Самый свежий документ (2026) — «что сообщество хочет делать сейчас»:** полный консенсус, что СП для транспорта (авиация/суда) — следующий большой рынок, на горизонте 10 лет (2036);
2. **Калибровка:** это роадмап «на будущее» (нет ретроспективы — только прогноз). Сравним через 5-10 лет; но паттерн TRL честный (fully-SC = 2!);
3. **Для кейсов:** sc_aircraft_motors (главный источник 2026), cryo_cmos/cryogenic power electronics, lh2-тренды (Haran 2017 тоже), sc_wind_generators (упомянут EcoSwing TRL 7!);
4. **Геополитический аргумент (редкоземельные магниты)** — новый драйвер для СП-машин (в дополнение к физике);
5. **S5-конкуренты:** high-purity Al @ 20K, SiC/GaN, батареи — надо следить;
6. **Компании в реестр** (см. список партнёров — много новых: H2GEAR, HIVOMOT, ASCEND/CRYOPROP, Mako, MAEVE, Aura-Aero);
7. **Связь с кейсом 003 (joints):** «superconducting joints» в списке R&D-потребностей.

## Ключевые цифры
- Транспорт = 16.2% выбросов; ~80% самолётов short-range;
- Плотность тока: СП ~500 vs Cu ~5 A/мм²;
- PTW: 787 сегодня 2.2 kW/kg; нужно >10; fully-SC >30 kW/kg;
- A320: >150 т батарей (утопия);
- 30 MW → 3 kA @ 10 kV;
- US Navy: 36.5 MW мотор (2011), 70% вес / 50% размер; degaussing −80% вес;
- LH2: 120 MJ/kg, 8.5 MJ/л, latent heat 446 kJ/kg (×5 LN2);
- RE-PM: нужно ×5 производства за 20 лет;
- EcoSwing 3.6 MW ветрогенератор (2020) — TRL 7 демо;
- TRL fully-SC мотор/генератор = 2; LH2-инфраструктура = 2.

## Замечания
- ScGA (Superconductivity Global Alliance) — новая инициатива (Transport Group);
- Перспектива (Perspective), не Topical Review — но с конкретными TRL и роадмапом;
- 30+ соавторов из Airbus/GKN/GE — промышленный консенсус;
- Опубликован 30.01.2026 — актуален на момент проекта.
