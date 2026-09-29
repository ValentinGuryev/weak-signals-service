# Ручные запросы Google Patents — кейс #87 крио/СП-вычисления для ИИ-ЦОД

> Для РУЧНОГО поиска автором в браузере (Google Patents API недоступен; протокол внутренний контракт §4.2c).
> Назначение: патентный слой кейса `cryo_sc_computing` (из официального датасета №87; стадия
> Концепция/Исследование; игроки: Snowcap Compute, VEIR).
> После сбора PDF кладутся в `data/raw/patents/patents.google.manual/`, переименовать с суффиксом
> `__cryo_sc_computing`, разбор и JSON-сборка по §4.2c; анализ — `signals/patent_signal.md`.
> ⚠️ Логика запросов — по KNOWHOW §7 (синонимы через OR, терминологический ценз; «0 в базе ≠ 0 в реальности»).

## Приоритет 1 — ядро технологии

### GP-1 · СП-логика/процессоры (Джозефсоновские школы) — !!!
```
("Josephson junction" OR RSFQ OR "rapid single flux quantum" OR eSFQ OR "reciprocal quantum logic" OR AQFP)
AND (logic OR processor OR computing OR circuit)
```
**Цель:** карта школ сверхпроводящей цифровой логики (RSFQ/eSFQ/RQL/AQFP) — элементная база Snowcap
(команда Herr/Herr — экс-Northrop, школа RQL/eSFQ). Понимаем: что патентуется сейчас vs классика
1980-2000-х (IBM, HYPRES, Northrop).
**Ожидание:** много классических + свежий слой 2020-х (криотроны, eSFQ).

### GP-2 · Сверхпроводящая/криогенная ПАМЯТЬ (узкое место!) — !!!
```
("superconducting memory" OR "cryogenic memory" OR "Josephson memory" OR "cryo-CMOS memory" OR "SFQ memory")
```
**Цель:** ЗУ — главный bottleneck СП-вычислений (см. обзор Li & Peng 2026: суперпроводящие сдвиговые
регистры/кэш, cryo-CMOS DRAM): если у Snowcap-класса машин нет памяти — это критично для S4.
**Ожидание:** патенты по Джозефсоновской памяти (NIST/IBM/HYPRES), свежие по гибриду СП-логика + cold DRAM.

## Приоритет 2 — прикладной слой (актуализация 2025-26)

### GP-3 · Криогенный дата-центр / крио-вычисления прикладные — !!!
```
(cryogenic OR cryo) AND ("data center" OR datacenter OR "data-centre" OR "machine learning" OR "AI inference"
OR "artificial intelligence")
```
**Цель:** прикладные заявки на крио-ЦОД/ИИ — ровно слой, где идёт рост (разведка: cryo datacenter 26→59
в 2026). Ищем конкурентов/носителей (не только Snowcap) и «зачем» (энергоэффективность ЦОД).
**Ожидание:** мало, но свежих (2022-2026) — ключевой сигнал.

### GP-4 · Сверхпроводящие ИИ-ускорители / нейросети на Джозефсоновской базе — !!
```
(superconducting AND ("neural network" OR "AI accelerator" OR "machine learning" OR accelerator OR inference))
AND (Josephson OR flux OR cryogenic OR SFQ)
```
**Цель:** прямые заявки на СП-ускорители ИИ (включая аналоговые Джозефсоновские нейроны — существует
линия научных работ). Отделить «классические СП-компьютеры» от «СП-для ИИ».
**Ожидание:** средне; японские/американские группы.

## Приоритет 3 — смежные слои и носители

### GP-5 · cryo-CMOS (вычисления/контроллеры при крио-температурах) — !!
```
("cryo-CMOS" OR "cryo CMOS" OR "low-temperature CMOS" OR "cold CMOS") AND (computing OR memory OR controller
OR amplifier OR iterior circuit)
```
**Цель:** cryo-CMOS — самый растущий ряд в нашей разведке (94 в 2026), драйвер — квантовые контроллеры +
гибридные ЗУ (GP-2, холодный DRAM). Проверяем: патентуют ли компании (Intel, imec, Samsung?).
**Ожидание:** растёт с 2020-х; проверить производителей.

### GP-6 · Криосистемы/охлаждение для вычислительных чипов (энергобаланс!) — !!
```
(cryocooler OR dilution refrigerator OR "cryogenic cooling" OR "cryo system") AND (chip OR processor OR
"data center" OR computing)
```
**Цель:** S4-экономика: кто владеет крио-инфраструктурой для ВЫЧИСЛЕНИЙ (не квантовых) — компрессоры,
ожижители, интеграция с чипами. Ответ на вопрос «съедает ли криосистема выигрыш 25×».
**Ожидание:** квантовые в основном; проверить «для computing/ЦОД».

### GP-7 · Компании-носители (assignee) — !!
```
assignee:(Snowcap OR "Northrop Grumman" OR HYPRES OR SeeQC OR "IMRA" OR imec OR IBM)
AND (superconduct* OR cryogen* OR Josephson)
```
**Цель:** свежие патенты носителей: Snowcap (сам!), Североп-Грумман (команда Herr — там наследие RQL),
HYPRES/SeeQC (СП-цифровые лаборатории), imec (fab-путь). В GP assignee-фильтр — через расширенный поиск
(Experimental / фильтр по assignee).
**Ожидание:** Northrop/IBM — классика; Snowcap/SeeQC — свежее.

## После сбора (протокол §4.2c)
1. PDF → `data/raw/patents/patents.google.manual/` с суффиксом `__cryo_sc_computing`;
2. Дедуп по номеру патента и по (assignee + нормализованный title) — уровень изобретения;
3. JSON-сборка `data/raw/patents/cases/087_cryo_sc_computing.json` (или по правилу имён кейсов);
4. Анализ в `signals/patent_signal.md`: игроки, годы приоритета, окно 2018/2023/2026, география;
5. Галлюцинации запрещены: нет результатов → «0/не найдено» честно.

## Не дублировать
- Связанные темы: СП-квантовые контроллеры (cryo-CMOS для кубитов) — в GP-5 берём только из-за
  пересечения; сверхпроводящие кабели/передача (VEIR — питание ЦОД, НЕ вычисления) — отдельный кейс.