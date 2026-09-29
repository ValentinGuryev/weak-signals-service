# Ниша ускорителей для SMES — почему SMES жив именно там (кейс 005)

> **S5-дополнение к кейсу 005 (SMES).** Дата: .
> **Вопрос (задача автора):** почему у SMES осталась узкая специализация для УСКОРИТЕЛЕЙ?
> Какие характеристики SMES как накопителя энергии востребованы именно там?
> **Ответ:** ускорители с импульсными сверхпроводящими синхротронами — единственная ниша,
> где SMES даёт уникальную комбинацию: **МДж-масштаб энергии, МВт-мощность, мс/суб-секундный
> отклик, kA-токи и kA/s-скорость рампы** — при этом конкуренты (BESS/Li-ion) там неприменимы
> (слишком медленные, нет kA-рампы, деградируют на циклы), а крио-инфраструктура уже есть.

---

## 0. TL;DR для жюри / ML

> **ОБНОВЛЕНО  (после выжимок PDF):** добавлен критический факт — действующий бустер NICA
> работает на конденсаторном накопителе (НЕ SMES); NICA-SMES = активная **R&D**-программа (концепт/изготовление),
> а не внедрённая система. Вывод `niche_alive` уточнён: ниша реальна как R&D, но конкурент (конденсаторы)
> уже закрыл часть задачи на действующей машине.

1. **NICA (ОИЯИ, Дубна) — ПОДТВЕРЖДЁН как проект SMES** (вопреки ожиданию «0 упоминаний» — ранее
   в наших материалах NICA не было; найдено через литературный поиск 2026-09-03).
2. **Два трека NICA-SMES:** (а) JINR-собственный HTS SMES 3-5 MJ / 10-12 kA (Khodzhibagiyan 2020,
   Kondratiev 2022 — тест-стенд); (б) **китайско-JINR коллаборация CAS Hefei: 12 kA forced-flow
   HTS SMES для NICA** (Zheng 2023; тот же коллектив, что и CORC-SMES 1 MJ Li 2022 — кейс-ниша
   «единственная живая» теперь имеет ВТОРОЙ проект).
3. **Физическая причина ниши:** бустер и нуклотрон NICA работают **в противофазе** (период ~4 с);
   суммарная энергия их магнитов колеблется 1 → 2.6 MJ за период. SMES **перекачивает энергию
   между ними** — это не «хранение для сети», а **энергообмен внутри ускорителя** с к.п.д. ~95%
   и мс-откликом, чего не даёт ни BESS, ни маховик в таких масштабах тока.
4. **Для ML:** `niche_alive = 1` (SMES жив в спецнише как R&D), но verdict «не состоялся» для массового
   рынка **сохраняется** — ниша мала (единицы МДж × единицы установок), не меняет экономику.
   **Важно (по выжимке Butenko УФН 2021):** на действующем бустере NICA энергообмен делает
   конденсаторный накопитель 60 Ф/400 В внутри источника PIT11 — т.е. «безальтернативность» SMES
   справедлива только для парной противофазной работы бустер+нуклотрон (энергообмен МДж между
   двумя кольцами), а для одиночного кольца SMES НЕ безальтернативен (конденсаторы уже работают).
5. **Статусные проверки 2026 (выполнены, §7):** программа NICA-SMES ЖИВА и РАСШИРЯЕТСЯ — 6 работ
   2024-2026 (Zheng 2024 1 МДж eng.design, Li 2024 кабель, Li 2025 стабильность, Cheng 2025 джойнт,
   Khodzhibagiyan 2024 «3-MJ HTS device», Song 2026 10 МДж криотест) — но всё R&D, внедрённого SMES нет.
   Коллайдер NICA вводится в строй ~2025-26 (Butenko 2026), SMES в его планах не фигурирует.

---

## 1. Какие характеристики SMES востребованы на ускорителях (главный вопрос)

Синтез из литературы (японская школа KEK/Токийский ун-т: Sato, Shintomi, Ise 2003-2010; JINR:
Khodzhibagiyan 2020; CAS Hefei: Li 2022, Zheng 2023):

| Характеристика SMES | Требование ускорителя | Почему критично | Конкуренты не дают |
|---|---|---|---|
| **Высокая мощность при умеренной энергии (МВт при МДж)** | Импульсное возбуждение магнитов синхротрона: за ~4 с нужно отдать/принять 1-2.6 MJ | Пульсовая нагрузка на сеть → провалы/скачки напряжения, штрафы за power quality | BESS: мощность ограничена C-rate; конденсаторы: мало энергии |
| **Быстрый отклик (мс / суб-секунда)** | Компенсация пульсаций в реальном времени | SMES отдаёт мощность за мс (инвертор), BESS — за 100 мс+ (химия) | Li-ion: ~100 мс-1 с; маховик: с |
| **kA-токи и kA/s-скорость рампы** | Ток магнитов NICA 10-12 kA; рампы kA/s | SMES включается **последовательно** в цепь магнитов, ток должен совпадать | BESS/конденсаторы — низковольтные, не kA |
| **Очень много циклов (10⁵-10⁶)** | Период 4 с, 24/7 — миллионы циклов в год | SMES не деградирует на циклы (сверхпроводник); BESS деградирует (cycle life ~10³-10⁴) | Li-ion cycle life — главный лимит |
| **Крио-синергия (ускоритель уже криогенный)** | NICA/нуклотрон уже имеет гелиевую/крио-инфраструктуру | SMES не требует отдельной криосистемы — «бесплатный» холод | BESS не использует крио |
| **Высокий к.п.д. ~95%** | Энергообмен каждые 4 с, круглосуточно | Потери при постоянном цикле = деньги; SMES ~95% (только инвертор+крио) | BESS round-trip ~85-90% + деградация |
| **Компактность / нет движущихся частей** | Ограниченное место в туннеле | Маховик — движущиеся части, вибрации; SMES статичен | Маховик: механика |

**Ключевой инсайт:** на ускорителе SMES нужен не как «накопитель для сети» (там он проиграл BESS
по $/кВт·ч в ~5000×), а как **импульсный компенсатор реактивной/активной мощности в kA-цепях**,
где мерило — не $/кВт·ч, а **$/МВт·мс и циклостойкость**. Это другая экономика: важно МДж,
отданные за секунды, миллионы раз.

---

## 2. NICA (ОИЯИ/Дубна) — проверка: делают ли SMES

### 2.1 Результат проверки: ДА, делают (2 проекта, подтверждено литературой)

Ранее в наших материалах NICA **не упоминался** (grep по 005_SMES/literature/SNF — 0). Поиск
2026-09-03 (Crossref/OpenAlex) дал **3 профильные работы JINR/CAS-Hefei**:

### 2.2 Khodzhibagiyan et al. 2020 — «An approach to development of the HTS magnet for SMES at JINR»
- **DOI:** 10.1088/1742-6596/1590/1/012057 (J. Phys. Conf. Ser. 1590, 012057; 10 цитирований)
- **Авторы:** H. Khodzhibagiyan, V. Drobin, G. Dorofeev, V. Karpinskiy, A. Shurygin, M. Novikov,
  D. Kashaev, M. Zaslavskiy, G. Kachlishvili (JINR, Дубна)
- **Суть (из абстракта):**
  - NICA = бустер + нуклотрон, их магниты работают **в импульсном режиме в противофазе**,
    период ~4 с;
  - суммарная запасённая энергия магнитов меняется **1 → 2.6 MJ за период**;
  - SMES **перекачивает энергию между бустером и нуклотроном** (двигает энергию «туда-обратно»);
  - полезная энергия SMES ~1.6 MJ, полная **3-5 MJ**; поле несколько Тл; ток **10-12 kA**
    (не меньше тока магнитов);
  - для стабильности при 6-7 Тл и 4 с-импульсном режиме — **HTS кабель**;
  - форма: короткий соленоид (**Brooks coil**) из коаксиальных секций; кабели со спиральной
    структурой типа **CORC**.
- **Значимость:** это **прямое подтверждение** ниши «SMES для ускорителей» на NICA и — что важно —
  **второй (после CAS Hefei Li 2022) проект на CORC-кабеле**. JINR использует тот же CORC-подход.

### 2.3 Zheng et al. 2023 — «Development of 12 kA-level Forced-flow Cooling HTS SMES System for NICA Accelerator»
- **DOI:** 10.1109/asemd59061.2023.10369100 (IEEE ASEMD 2023)
- **Авторы:** Jinxing Zheng, Ming Li, Xufeng Liu, Xiongyi Huang, Shaotao Dai, Tao Ma (CAS Hefei),
  Hamlet Khodzhibagiyan, Mikhail Novikov (JINR)
- **Суть:** **12 kA-level forced-flow cooling HTS SMES для NICA** — совместный проект
  **CAS Institute of Plasma Physics (Hefei) + JINR**. 12 kA совпадает с требованием Khodzhibagiyan 2020.
- **Значимость:** тот же коллектив (Li, Zheng, Liu), что и CORC-SMES 1 MJ (Li 2022, SuST) —
  **китайская программа SMES для ускорителей теперь имеет явную цель NICA**. Это усиливает
  вывод «единственная живая ниша = ускорители, и она интернациональна (Китай+РФ)».

### 2.4 Kondratiev et al. 2022 — «Development of the Test Facility for Measurements of Current–Voltage Characteristics of HTS Tapes, Cables, and Magnets for SMES at JINR»
- **DOI:** 10.1134/s1547477122050223 (Phys. Part. Nucl. Lett.; JINR)
- **Авторы:** B. Kondratiev, N. Blinov, H. Khodzhibagiyan, E. Matyhanov, D. Neapolitanskiy, M. Novikov, A. Ryabov
- **Суть:** создан **тест-стенд JINR для измерения ВАХ HTS-лент, кабелей и магнитов для SMES**.
- **Значимость:** подтверждает, что программа JINR-SMES **жива и имеет инфраструктуру**
  (не только концепт-дизайн 2020).

### 2.5 ⚠️ КРИТИЧЕСКИЙ КОНТРАРГУМЕНТ: действующий бустер NICA работает на конденсаторах, НЕ на SMES

**Источник: Butenko et al. (УФН/Physics-Uspekhi 2021/2023) — «NICA Booster: a new-generation
superconducting synchrotron»** (DOI 10.3367/UFNe.2021.12.039138; полная выжимка в literature/).

- Бустер NICA запущен: первые сеансы **ноябрь–декабрь 2020 и сентябрь 2021** (инжекция пучка 19.12.2020).
- **Система питания бустера:** источник PIT11 (с НПП «ЛМ Инвертор»): ток до 10.0 kA, скорость до 7 kA/с
  (1.2 Тл/с), пик мощности нагрузки 2.86 МВт, **мощность из сети ≤300 кВт**.
- **Циклический энергообмен реализован ВНУТРИ PIT11** через **батарею электролитических конденсаторов
  60 Ф / 400 В**: она снимает циклическую нагрузку с сети и как идеальный фильтр убирает гармоники.
- PIT11 = 12 параллельных DC-DC (5 кГц → 60 кГц суммарно); нестабильность тока на плато 4×10⁻⁶.
- Т.е. задачи, которые Khodzhibagiyan 2020 предлагал решать SMES **для одного кольца**, на действующем
  бустере решены конденсаторами + DC-DC. Khodzhibagiyan — соавтор ОБЕИХ работ (SMES-концепт и бустер).
- **Вывод:** SMES-концепт JINR оправдан для следующего шага — **энергообмена бустер↔нуклотрон
  в противофазе** (обмен МДж между двумя кольцами), где конденсаторы одного источника не справляются.
  Это сильно сужает и уточняет «безальтернативность».

### 2.6 Дополнительный контекст: Khodzhibagiyan 2024 — «Development of Superconducting Accelerator Magnets at JINR»
- **DOI:** 10.54546/naturalscirev.100106 (Natural Science Review; обзор по СП-магнитам JINR c 1970-х)
- Показывает экспертизу JINR в СП-магнитах (мир. первый быстрый SC heavy-ion синхротрон —
  нуклотрон) — т.е. SMES для NICA делает команда с 50-летним опытом импульсных СП-магнитов.

---

## 3. Карта проектов SMES для ускорителей (обновлённая)

| Проект | Год | Параметры | Статус | Источник |
|---|---|---|---|---|
| **KEK/Япония: SMES-компенсация пульсаций синхротрона (JHF/J-PARC 50 ГэВ, medical)** | 2003-2010 | ~5 МДж (JHF), 104-170 МВт пульсаций, кА-токи, 3.6-4 с цикл; medical 4 МДж payback 16-33 г | моделирование/лаборатория, НЕ внедрено | Sato 2004, Ise 2003, Sato 2007, Sato 2010 |
| **UPS-SMES (NEDO, Япония)** | 2007 | 1 MJ conduction-cooled LTS pulse coil | коммерч. ниша | (в NARRATIVE) |
| **CAS Hefei: CORC-SMES для ускорителя** | 2022 | **1 MJ, 4 kA, 125 mH, 30 K, 4 T**, скорость рампы kA/s | прототип (DP-катушка на CORC) | Li 2022 (SuST 35, 125001) |
| **CAS Hefei + JINR: 12 kA HTS SMES для NICA** | 2023 | **12 kA**, forced-flow cooling | в разработке | Zheng 2023 (ASEMD) |
| **JINR: HTS SMES для NICA** | 2020- | **3-5 MJ, 10-12 kA, 6-7 T**, Brooks coil, CORC | концепт + тест-стенд (Kondratiev 2022); НЕ внедрён | Khodzhibagiyan 2020, Kondratiev 2022 |
| **NICA Booster (действующий): энергообмен** | 2020-2021 | конденсаторный накопитель 60 Ф/400 В, PIT11 10 kA, ≤300 кВт из сети | **РАБОТАЕТ (конкурент SMES!)** | Butenko 2021 (УФН) |
| **1 MJ HTS SMES, eng. design (Zheng 2024)** | 2024 | 1 МДж, kA-level, NICA | инженерный дизайн | Zheng 2024 (IEEE TAS 10.1109/tasc.2024.3446286) |
| **Forced-flow CORC cable eng. design** | 2024 | высокотоковый кабель для SMES | дизайн (5 цит.) | Li 2024 (IEEE TAS 10.1109/tasc.2023.3346831) |
| **6 kA SMES stability analysis** | 2025 | стабильность 6 kA для ускорителя | анализ (2 цит.) | Li 2025 (IEEE TAS 10.1109/tasc.2024.3520540) |
| **HTS joint 10kA CORC** | 2025 | джойнт для forced-flow CORC | R&D | Cheng 2025 (Physica C 10.1016/j.physc.2025.1354731) |
| **10 MJ SMES module (Beijing Jiaotong)** | 2025-26 | **10 МДж модуль, криотесты** | модуль испытан (крио); R&D | Song 2026 (J. Energy Storage 10.1016/j.est.2026.120670) |

**NB:** CAS Hefei (Zheng/Li/Liu) и JINR (Khodzhibagiyan/Novikov) — **одна коллаборация**: работы
2022 (CORC DP 1 MJ) и 2023 (12 kA NICA) — это, по-видимому, **единая программа** «kA-уровневый
HTS SMES для ускорителей», нацеленная на NICA. Т.е. «единственная живая ниша» в кейсе 005
(упомянутая как Li 2022) на деле — **активная российско-китайская программа 2020-2023+**.

---

## 4. Связь с другими кейсами

- **srf_cavities / detector_magnets / test_facilities** — ускорительная тематика NICA:
  бустер, нуклотрон, MPD/SPD-детекторы (см. README 006? нет — это кейсы ускорителей в реестре).
- **corc_cables** — CORC-кабель = ключевой проводник для kA-SMES (Li 2022, Khodzhibagiyan 2020).
  Перекрёстное подтверждение: CORC состоялся в нише ускорителей/fusion (Weiss 2020 fusion,
  Li 2022 SMES, Khodzhibagiyan 2020 SMES).
- **mgb2_mri / cryocoolers** — альтернативные проводники/крио для SMES (Bologna DRYSMES4GRID 500 kJ MgB2).

---

## 5. Вывод для калибровки / ML

1. **Новая фактура для кейса 005:** NICA-программа (JINR + CAS Hefei) — доказательство, что
   ниша «SMES для ускорителей» **реальна, активна в 2020-2026 и интернациональна** (как R&D).
   Статусные проверки (2026-09-03) подтвердили продолжение: 6 работ 2024-2026 (eng. design 1 МДж,
   кабель, стабильность, джойнт, 10 МДж криотест) — программа не остановлена.
2. **verdict НЕ меняется:** «не состоялся для массового рынка (BESS/Li-ion)» — ниша ускорителей
   мала (единицы установок × единицы МДж), экономика массового рынка не затронута. Даже 10 МДж-модуль
   (2026) — R&D, не коммерческий продукт.
3. **Фича `niche_alive` = 1, но с уточнением** — отличает «полностью мёртв» (нет) от «жив в спецнише» (да).
   По выжимке Butenko 2021: NICA-SMES — **R&D-ниша (концепт/дизайн), а НЕ внедрение**: действующий
   бустер работает на конденсаторах. Для ML: negative-пример SMES — это
   **«не состоялся на массовом рынке; жива R&D-ниша там, где S4-преимущество ещё не имеет дешёвого
   конкурента»** — «нишевая жизнь» в данном случае = длящиеся гос. R&D-программы, не коммерция.
4. **Самый сильный индикатор ниши (для features_table):** уникальная комбинация параметров
   (мощность/энергия/скорость/ток), которую конкуренты **физически не могут** дать —
   в отличие от массового рынка, где SMES проиграл по $/кВт·ч. **Но проверять и «дешёвого
   частичного конкурента»:** конденсаторный накопитель уже закрыл энергообмен одиночного кольца NICA.
5. **Вывод о «безальтернативности» (уточнённый по PDF):** SMES безальтернативен в узком окне
   «kA-токи + МДж-энергообмен между ДВУМЯ противофазными кольцами + kA/s + миллионы циклов»;
   для одиночного кольца дешевле конденсаторы+DC-DC (PIT11), для массового рынка — BESS.
   Ниша = единицы машин в мире (NICA; потенциально J-PARC-класс, medical-синхротроны), поэтому
   verdict «не состоялся (для рынка)» остаётся.
6. **Дополнительный урок (статусные проверки):** активная публикационная активность 2024-2026
   (6 работ по NICA-SMES) БЕЗ внедрения — ещё один пример «публикации/патенты/R&D ≠ коммерциализация»:
   даже целенаправленная международная программа (РФ+КНР, госфинансирование) за 6 лет (2020-2026)
   не довела SMES до работающей системы на ускорителе. Для ML: наличие длящихся R&D-программ
   (инженерные дизайны, анализы стабильности) — НЕ признак состоявшегося тренда.

---

## 6. Источники (найдены 2026-09-03, литературный поиск; PDF + выжимки — 2026-09-03)

> ✅ **Все ключевые PDF скачаны и имеют выжимки** в `case_studies/005_SMES/literature/` (28 PDF ↔ 28 MD).

**NICA-SMES (JINR/ОИЯИ + CAS Hefei):**
1. Khodzhibagiyan H. et al. (2020). An approach to development of the HTS magnet for SMES at JINR.
   J. Phys. Conf. Ser. 1590, 012057. DOI: 10.1088/1742-6596/1590/1/012057.
2. Zheng J., Li M., Liu X., Huang X., Dai S., Ma T., Khodzhibagiyan H., Novikov M. (2023).
   Development of 12 kA-level Forced-flow Cooling HTS SMES System for NICA Accelerator.
   IEEE ASEMD 2023. DOI: 10.1109/asemd59061.2023.10369100.
3. Kondratiev B. et al. (2022). Development of the Test Facility for Measurements of Current–Voltage
   Characteristics of HTS Tapes, Cables, and Magnets for SMES at JINR. Phys. Part. Nucl. Lett.
   DOI: 10.1134/s1547477122050223.
4. Khodzhibagiyan H. et al. (2024). Development of Superconducting Accelerator Magnets at JINR.
   DOI: 10.54546/naturalscirev.100106.

**Характеристики SMES для ускорителей (японская школа, компенсация пульсаций):**
5. Ise T., Furukawa K., Kobayashi Y., Kumagai S., Sato H., Shintomi T. (2003). Magnet power supply
   with power fluctuation compensating function using SMES for high intensity synchrotron.
   IEEE Trans. Appl. Supercond. DOI: 10.1109/tasc.2003.812898.
6. Sato H., Muto M., Shintomi T., Igarashi S., Ise T. et al. (2004). Compensation of load fluctuation
   of power supply system for large accelerator using SMES. PAC 2003. DOI: 10.1109/pac.2003.1289467.
7. Sato H., Shintomi T., Ise T., Miura Y., Nomura S. et al. (2010). Application of Energy Storage
   System for Stabilization of Accelerator Magnet Power Supply. IEEE Trans. Appl. Supercond.
   DOI: 10.1109/tasc.2010.2042797.

**Контекст CORC-SMES (уже в кейсе):**
8. Li M. et al. (2022). Research on a novel HTS double pancake coil based on CORC: used for kA-level
   SMES of accelerator. Supercond. Sci. Technol. 35, 125001. DOI: 10.1088/1361-6668/ac96b4.

**Статусные работы 2024-2026 (найдены литературным поиском 2026-09-03, PDF не скачаны — платно/не нужны):**
9. Zheng J., Cheng Y., Li M., Khodzhibagiyan H., Dai S., Novikov M. (2024). Engineering Design of
   1 MJ HTS SMES System With kA-Level Current Capacity for NICA Accelerator. IEEE TAS.
   DOI: 10.1109/tasc.2024.3446286.
10. Li M., Zheng J., Khodzhibagiyan H., Ma T., Huang X., Novikov M., Cheng Y. (2024). Engineering
    Design of Forced-Flow Cooling HTS Cable for SMES System With High Current Capacity. IEEE TAS.
    DOI: 10.1109/tasc.2023.3346831.
11. Li M., Zheng J., Cheng Y., Ma T., Dai S., Wang L. (2025). Stability Analysis of HTS SMES System
    With 6 kA Current for Accelerator. IEEE TAS. DOI: 10.1109/tasc.2024.3520540.
12. Cheng Y., Zheng J., Li M., Dai S., Ma T. (2025). Research on the HTS joint for 10kA-level CORC
    cable with forced-flow cooling. Physica C. DOI: 10.1016/j.physc.2025.1354731.
13. Song M., Yang R., Ma T., Geng J., Zhou Y., Xu Y. (2025/26). Development and Cryogenic Testing of
    a 10 MJ SMES Module. J. Energy Storage (препринт SSRN 2025). DOI: 10.1016/j.est.2026.120670.
14. Khodzhibagiyan H. et al. (2024). Development of Superconducting Accelerator Magnets at JINR.
    Natural Science Review. DOI: 10.54546/naturalscirev.100106 (упоминает «3-MJ HTS energy storage device»).
15. Butenko A. et al. (2026). Commissioning of Collider NICA and formation of first heavy ion beams.
    УФН/Physics-Uspekhi. DOI: 10.3367/ufne.2026.03.040109.
16. Parfenov P. (2025). Status of the MPD Experiment at NICA: Towards the First Data Taking.
    DOI: 10.1134/s154747712470211x.

---

## 7. Внешние статусные проверки (2026-09-03, литературный поиск Crossref/OpenAlex) — ВЫПОЛНЕНЫ

### 7.1 Статус NICA-SMES 2024-2026: программа ЖИВА и РАСШИРЯЕТСЯ (R&D, не внедрение)

**Найдено 6 новых работ 2024-2026 (продолжение коллаборации CAS Hefei/Beijing Jiaotong + JINR):**
| Работа | Год | Суть | Статус |
|---|---|---|---|
| Zheng, Cheng, Li, Khodzhibagiyan, Dai, Novikov — «Engineering Design of 1 MJ HTS SMES with kA-Level Current for NICA» (IEEE TAS, DOI 10.1109/tasc.2024.3446286) | 2024 | Инженерный дизайн 1 МДж kA-SMES для NICA | дизайн завершён |
| Li, Zheng, Khodzhibagiyan, Ma, Huang, Novikov, Cheng — «Engineering Design of Forced-Flow Cooling HTS Cable for SMES with High Current Capacity» (IEEE TAS, DOI 10.1109/tasc.2023.3346831, 5 цит.) | 2024 | Инженерный дизайн forced-flow CORC-кабеля | дизайн |
| Li, Zheng, Cheng, Ma, Dai, Wang — «Stability Analysis of HTS SMES System with 6 kA Current for Accelerator» (IEEE TAS, DOI 10.1109/tasc.2024.3520540, 2 цит.) | 2025 | Анализ стабильности 6 kA SMES | анализ |
| Cheng, Zheng, Li, Dai, Ma — «HTS joint for 10kA-level CORC cable with forced-flow cooling» (Physica C, DOI 10.1016/j.physc.2025.1354731) | 2025 | HTS-джойнт для 10 kA CORC | R&D |
| Song, Yang, Ma, Geng, Zhou, Xu — «Development and Cryogenic Testing of a 10 MJ SMES Module» (J. Energy Storage, DOI 10.1016/j.est.2026.120670; препринт SSRN 2025) | 2025-26 | **Криогенные испытания 10 МДж модуля** (Beijing Jiaotong, та же школа Dai/Ma) | модуль испытан (крио) |
| Khodzhibagiyan et al. — «Development of Superconducting Accelerator Magnets at JINR» (Nat. Sci. Review, DOI 10.54546/naturalscirev.100106, 3 цит.) | 2024 | Обзор JINR: упоминает **«3-MJ HTS energy storage device»** как результат работ | R&D |

**Вывод по статусу:**
- Программа NICA-SMES **не остановлена** — она перешла от концепта (2020) к **инженерному дизайну**
  (2023-2024) и **анализу стабильности / R&D компонентов** (2024-2025); Khodzhibagiyan 2024 называет
  3 МДж HTS-накопитель среди результатов JINR.
- **НО:** ни одна работа 2024-2026 не сообщает о **внедрении/испытании полного SMES на NICA** —
  всё остаётся на уровне «engineering design / analysis / component R&D / cryogenic module test».
- Параллельно школа Beijing Jiaotong (Dai, Ma, Geng, Song) развивает **10 МДж SMES-модуль**
  (криотесты 2025-26) — это уже не ускорительный масштаб, а шаг к сетевым применениям,
  но тоже R&D-модуль, не коммерческий продукт.
- **Итог для кейса:** «единственная живая ниша = ускорители (NICA)» подтверждается как **активная
  международная R&D-программа 2020-2026** (РФ+КНР), но внедрённого SMES на ускорителе по-прежнему нет.

### 7.2 Статус NICA-коллайдера (запуск): ввод в строй ~2025-2026
- **Butenko, Lebedev, Syresin, Trubnikov — «Commissioning of Collider NICA and formation of first heavy ion
  beams» (УФН/Physics-Uspekhi, DOI 10.3367/ufne.2026.03.040109)** — коллайдер NICA в стадии пусконаладки,
  формирование первых пучков тяжёлых ионов (2026).
- **«Status of the MPD Experiment: Towards the First Data Taking» (2025, DOI 10.1134/s154747712470211x)** —
  детектор MPD готовится к первым данным; «MPD physics performance in Bi+Bi at √sNN=9.2 ГэВ» (2025, 12 цит.).
- **Вывод:** коллайдер NICA вводится в строй в 2025-2026; **первые столкновения/данные — ожидаются**
  (это позже, чем планировалось, но факт запуска бустера/нуклотрона подтверждён с 2020-21).
- **Место SMES в планах NICA:** в доступных статусных работах (Butenko 2026, MPD 2025) SMES **не упоминается**
  как элемент вводимого коллайдера — согласуется с выводом §2.5: SMES — перспективный R&D для будущего
  энергообмена, действующие системы (бустер) работают на конденсаторах.

### 7.3 Медицинские синхротроны: SMES НЕ внедрён (подтверждено)
- Поиск (2018-2026, «SMES medical synchrotron therapy power compensation») не выявил **ни одной реальной
  установки SMES** в протонной/ионной терапии.
- Все работы по medical-синхротронам касаются систем питания/пучка без SMES; проработки Sato 2010
  (4 МДж SMES для Hyogo, payback 16-33 года) **не реализованы** — согласуется с экономическим выводом кейса.
- **Вывод:** сегмент medical-синхротронов (десятки центров) так и не стал нишей SMES — экономика
  (payback >16 лет) не сошлась; ниша ускорителей = только исследовательские комплексы (NICA-класс).

---

## 8. TODO (что можно докачать при необходимости)

- [x] ~~Статус 2024-2026 изготовления 12 kA SMES~~ — ✅ проверено: программа жива как R&D (6 работ 2024-26);
- [x] ~~Статус NICA collider~~ — ✅ проверено: ввод в строй ~2025-2026 (Butenko 2026, MPD 2025); SMES в планах
      вводимого коллайдера не фигурирует;
- [x] ~~Медицинские синхротроны~~ — ✅ проверено: внедрений SMES нет.
- [ ] (опционально) Скачать PDF Zheng 2024 (IEEE TAS, платно) — для полной выжимки «Engineering Design
      1 MJ» (сейчас — только метаданные/абстракт).
