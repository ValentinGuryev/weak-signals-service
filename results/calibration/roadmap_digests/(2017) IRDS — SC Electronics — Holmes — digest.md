# Holmes & DeBenedictis — Superconductor Electronics and the International Roadmap for Devices and Systems (2017)

**Файл:** `data/raw/conferences/snf_ieeecsc/downloads_renamed/(2017) [ART] International Roadmap for Devices and Systems.pdf`
**Источник:** IEEE/CSC & ESAS Superconductivity News Forum (global edition), October 2017.
**Авторы:** D. Scott Holmes (Booz Allen Hamilton), Erik P. DeBenedictis (Sandia National Laboratories).
**Поддержка:** ODNI/IARPA (Holmes), Sandia (DeBenedictis).
**Релевантность:** 5/5 — **ключевой «мостик» между эрами roadmap'ов СП-электроники** (2010 European Roadmap → 2022 IRDS CEQIP). Показывает сдвиг от «RSFQ заменит CMOS» к «SCE для квантовых вычислений/датчиков».

---

## Суть

Статья вводит **Superconductor Electronics (SCE)** в **IRDS** (International Roadmap for Devices and Systems), преемника ITRS. Ключевой сдвиг: драйвер roadmap'а изменился с масштабирования физических размеров (ITRS) на **требования приложений** (application-driven), и Beyond CMOS теперь включает не-полупроводниковые технологии: мемристоры, спинтронику, straintronics, SCE.

## Ключевые факты

### Смена парадигмы
- ITRS (2001-2014): масштабирование транзисторов → ITRS 2.0 (2015) → IRDS (IEEE Rebooting Computing);
- IRDS миссия: «от устройств к системам и от систем к устройствам»; Beyond CMOS — фокус;
- SCE-логика: SFQ-семейства — RSFQ, RQL, EFSFQ, eSFQ, AQFP, phase-mode.

### Применения и драйверы (таблица)
| Применение | Драйвер |
|---|---|
| R&D (осн. драйвер) | **Quantum information processing**, sensor/detector arrays, superconducting computing, гос. финансирование |
| Metrology | Voltage standard |
| RF signal processing/control | Цифровые RF-приёмники, DSP |
| Data preprocessing / network routing | RF processor, DSP, SOC-NW |
| HPC / Data center | MPU-HP, microserver |

**Коммерческие применения 2017:** Josephson voltage standards, **digital-RF receivers**, **quantum annealing coprocessors (D-Wave)**. Криогенные сенсорные матрицы (астрономия) растут — нужны мультиплексирование и обработка вблизи сенсоров. Микропроцессоры/память — в разработке, не коммерческие.

### Бенчмаркинг
- RQL ALU: 205 aJ/op, 402 ps (32-bit), 16.3 GHz при 4.2 K, Jc=100 μA/μm²;
- Стоимость крио: 400-10 000 Вт(300K)/Вт(4.2K) — при 4.2K RQL получает преимущество ×1000;
- Нужны модели area/delay/energy для JTL/PTL, clocking, refrigeration.

### Foundry-вызов (ключевой)
- 2 foundry c >100 000 JJ: **MIT Lincoln Lab** (не может коммерческие продукты) + **D-Wave** (ограниченный доступ);
- Нужен ≥1 коммерческий foundry с процессами под SCE и приемлемым yield;
- Желателен multi-project wafer (MPW) + полные PDK.

### Roadmap
- IRDS: текущий (7 лет) + долгосрочный (8 лет), обновления по нечётным годам;
- Области SCE-roadmap: foundry/fabrication, packaging/integration, design tools;
- **Ожидание: SCE-роадмапы будут менее детальны, чем CMOS** (2017).

## Выводы / Relevance для проекта
1. **Мост 2010→2022:** в 2017 SCE уже позиционируется для QIP/датчиков/вычислений, НЕ «замена CMOS на десктопе». RSFQ-цифра → ниша (data centers, квантовые контроллеры);
2. **Подтверждает кейс rsfq_cmos (#46, «не стоило»):** к 2017 сами IRDS-авторы видят RSFQ-цифру как «partial», нужную для QIP-инфраструктуры, а не массовый продукт;
3. **Foundry-проблема** (нет коммерческого foundry) — ключевой барьер, сохранялся до 2024 (ScGA + imec);
4. **Связь с кейсами:** jtwpa (чтение кубитов — QIP-инфраструктура), sc_qubits (transmon), cryo_cmos (#31 — «cryogenic semiconductor electronics» уже в IRDS 2017!).

## Статус обработки
- ✅ Выжимка (2026-09-02). Полный текст разобран (454 строки).
