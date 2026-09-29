# (2025) !!! Morandi — HTS power transmission (and distribution): status and prospects (CCA 2025)

## Метаданные
- **Автор:** Antonio Morandi (DEI, University of Bologna)
- **Год:** 2025 (презентация CCA 2025, CERN, Женева, 11-13.03.2025; SNF Issue No. 59, May 2025)
- **Источник:** SNF-коллекция (IEEE-CSC, ESAS, CSSJ Superconductivity News Forum), `(2024) [CCA] HTS power transmission...`
- **Тип:** Актуальный обзорный доклад (май 2025) — статус и перспективы ВТСП-кабелей передачи/распределения

## Резюме (релевантность 5/5 — свежайший обзор, экономика + геометрия)
Наиболее свежий обзор (2025) по всем аспектам ВТСП-кабелей: конструкция, конкуренция, экономика, применения.
Ключевые факты для кейса 012:

**1. Мотивация ВТСП-кабелей (для города/ЦОД):**
- **Ток в 5-10× выше, чем у обычного кабеля того же сечения** → либо больше мощности при том же напряжении
  (P=V·I), либо МЕНЬШЕ напряжение при той же мощности;
- **Сокращение right-of-way и занимаемой почвы (soil occupation)** — экономия земли в мегаполисах;
- **Значительно более быстрый монтаж**;
- **Использование существующей городской инфраструктуры** (utility civil infrastructures) — в существующие
  каналы/трассы, без новых раскопок;
- **Упрощение электрооборудования**: меньше ступеней конверсии, проще layout.
- Яркая формулировка: **«Superconductors will do for electricity what fiber optic cables did for telecoms by
  replacing the twisted pair»** — сверхпроводники революционизируют передачу, «ultra high capacity unobtrusively».

**2. Энергопотери (ключевое различие AC vs DC):**
- «In **DC cables no practical loss** occurs in the superconductor» (потерь в СК нет — критично!);
- Для AC — есть EM-потери в СК + шилд требует столько же СК, сколько ядро (AC-шилд);
- Сравнение потерь W/m проводится с учётом криоохлаждения (COP).

**3. Конструкция и напряжение (откуда вольты):**
- **DC-кабель:** core + shield, обе сверхпроводящие; токи сильно связаны (ISHIELD ≈ ICORE) — шилд несёт ток;
- **Геометрия по напряжению:** concentric (концентрические фазы) **10–20 кВ** · раздельные фазы в общем
  криостате **30–100 кВ** · раздельные фазы и криостаты **>100 кВ**;
- **Joints каждые 100-500 м** (производственные/транспортные ограничения);
- **Расстояние охлаждения (cooling&pumping): до 20-30 км** в зависимости от термогидравлики.

**4. Линия времени кабельных проектов (2025):** LIPA I 2008 · Incheon 2009 · Essen/AmpaCity 2013 (AC,
concentric, ReBCO) · Jeju DC 2014 · Yokohama 2013/2018 (AC 66kV) · Shingal 2019 (AC 23 kV) · Albany 2006-07 ·
Chicago 2021 · Shenzen 2021 · **SuperLink 2024** · **SuperRail Paris 2024** (постоянный ток, 1 полюс в
криостате) · Shanghai 2021-22 (35 kV, 133 MVA, 1200 м, 2G, energized 2022) · Echuca/Катания и др.

**5. Применения (актуально для ЦОД):**
- «Supplying established (metal industry) and **emerging (data centers) power-intense and current-intense
  DC customers**» — **дата-центры названы явно как emerging DC-клиенты**;
- Схема: AC sources → HVAC/HVDC transmission → subtransmission 30-150 kV → **Storage / Data centres /
  Metal industry / MVDC distribution / rail** — ЦОД на карте как цель нового распределения;
- Настоятельная потребность: «Meeting the increasing load demand of congested areas will require the
  upgrade and/or the reconception of distribution grids» — реконцепция сетей городов.

## Ценность для кейса 012
- **Самый свежий (2025) обзор, прямо называющий дата-центры как emerging DC-потребителя** — мост
  между «HVDC-передача» (пре-кейс sc_dc_cables) и «питание ЦОД» (новая формулировка).
- **Числа для питча:** ток ×5-10, напряжение 10-20кВ (concentric) / 30-100кВ / >100кВ, joints 100-500 м,
  охлаждение 20-30 км.
- **Формулировка «оптоволокно для электричества»** — сильный образ для защитного выступления.

## Связь с другими работами
- Провал AC: hts_ac_cables (Tres Amigas, LIPA, AmpaCity) — Morandi показывает, что AC-геометрии остаются,
  но DC-применения (Jeju, SuperLink, SuperRail) — растущий тренд.
- СПб DC (Sytnikov 2013), Ishikari DC (Yamaguchi 2019), Шанхай DC (Xie 2023-24).
- Свежие DC-проекты: SuperLink 2024, SuperRail 2024 (см. отдельные выжимки).

## Итоговая оценка
**5/5** — ключевой источник для формулировки кейса и питча: экономика (×5-10 ток, right-of-way),
физика напряжения (геометрия → вольты), DC-потери ≈ 0, явное упоминание дата-центров (2025).