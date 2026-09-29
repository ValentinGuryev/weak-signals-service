# Грантовый сигнал (S1d): JTWPA / квантовые усилители (кейс 007)

> **Дата:** .
> **Вопрос:** кто и когда финансировал JTWPA/quantum-limited усилители через гранты?
> Согласуется ли с публикационным сигналом (взлёт 2021+) и вердиктом «✅ состоялся»?
> **Метод:** CORDIS (ЕС, Horizon/ERC/EIC) + NSF (США) + РНФ (Россия) + KAKEN (Япония) + NSFC + NIH.
> **Данные:** `data/raw/grants_foreign/cordis_jtwpa_results.json` (121 запись, 20 реальных проектов),
> `nsf_jtwpa_results.json` (131 грант), РНФ: `data/raw/rnf/rnf_cards.json` (407, из них 2 прямых).
> **Скрипты:** `src/grants_cordis_jtwpa.py`, `src/grants_nsf_jtwpa.py`.

---

## 1. CORDIS (Европа) — финансирование ЕСТЬ и РАСТЁТ, но в основном 2021+

**Запросы:** traveling/travelling wave parametric amplifier, JTWPA, TWPA, Josephson parametric amplifier,
kinetic inductance traveling wave, quantum-limited amplifier, DARTWARS, qubit readout amplifier,
superconducting microwave amplifier.
**Собрано:** 121 запись, **20 реальных проектов** (остальное — результаты/статьи/дубли).

### Ключевые проекты (усилители/чтение прямо)

| Проект | Страна | Программа | Старт* | Суть |
|---|---|---|---|---|
| **QMiCS** | Германия | FET (Quantum Flagship) | 2018 | Quantum Microwave Communication and Sensing — компоненты (усилители) |
| **SPA4AstroQIT** | Великобритания | ERC | 2019 | Broadband QL Parametric Amplifier для астрономии + QIT |
| **DARTWARS** | Италия | MSCA | 2021 | **Detector Array Readout with Traveling Wave AmplifieRS** — прямо TWPA для детекторных массивов |
| **TruePA** | Германия | Digital/Industry/Space | 2022 | **Truly Resilient QL Traveling Wave Parametric Amplifiers** — прямо JTWPA следующего поколения |
| **MiSS** | Италия | Digital/Industry/Space | 2024 | Microwave Squeezing with Superconducting (meta)materials |
| **SQELETON** | Франция | EIC | 2025 | **Scalable Qubit Readout** — «skeleton in the closet» квантовых вычислений (>100 кубитов) |
| **SPARTAN-FX** | Великобритания | ERC | 2025 | **SPA Receiver Technology for Astronomy and Fundamental Physics** |
| **QuAMP** | Швейцария | ERC | 2025 | **Democratizing access to QL microwave parametric amplifiers** |
| **SuperQuSense** | Франция | ERC | 2026 | СП-схемы для квантового sensing микроволн (тёмная материя, EPR, кубиты) |
| **Q-AMP** | Бельгия | — | 2022 | квантовые электрооптические усилители (др. ветка) |
| **SuperICQ** | Финляндия | — | 2026 | СП-интегральные схемы для масштабируемых квантовых систем |
| Strong-ESPRESSO | Литва | — | 2025 | EPR через QL-усилители |
| Prometheus | Финляндия | — | 2020 | 1000-кубитный квантовый компьютер (IQM) — драйвер чтения |

*Годы по id Horizon (8xxxxx=2018-20, 10xxxxx=2021+).

**Вывод CORDIS:** Европа **финансирует JTWPA/quantum-limited усилители**, но основной поток — **2021+**
(DARTWARS 2021, TruePA 2022, SQELETON/SPARTAN/QuAMP 2025). До 2018 — только QMiCS (2018) и SPA4AstroQIT (2019).
Полный контраст с SMES (005): там CORDIS = 0 проектов вообще.

---

## 2. NSF (США) — 2 прямых гранта, но канал неполон (артефакт, как в 006)

**Собрано:** 131 грант (rpp=25 обрезает, релевантных в выдаче 2):

| Грант | Организация | Сумма | Суть |
|---|---|---|---|
| **Broadband QL TWPA based on Superinductor** (UMass Boston) | UMass Boston | $344k | **Прямо JTWPA** (Bell! — тот же, что SQUID-TWPA 2014 в нашей литературе) |
| **SBIR Phase I: Versatile Low-Noise TWPA for Quantum** | Millimeter Wave Systems LLC | $225k | Коммерческий TWPA (SBIR) |

**Почему мало (методологически важно):** NSF API ловит только прямое «TWPA/amplifier» в названии/абстракте.
Реальное финансирование США идёт через **NQI (National Quantum Initiative, 2018), DOE, ARO, NSA, NASA** —
НЕ через NSF-гранты с явным «TWPA». (Как в SNSPD 006: NSF-числа нельзя читать как «США не финансировали».)
Прямые гранты MIT Lincoln Lab (JTWPA для IBM/ADMX), UCB (Siddiqi), NIST — финансируются DOE/ARO/NIST internal.

---

## 3. РНФ (Россия) — 2 прямых гранта по JTWPA (найдены!)

Из `data/raw/rnf/rnf_cards.json` (407 СП-проектов):

| Грант | Год | Руководитель/Организация | Суть |
|---|---|---|---|
| **21-42-04421** | 2021 | **Кошелец В.П. (ИРЭ РАН им. Котельникова, Москва)** — конкурс **с DFG (Германия)** | «Управляемые джозефсоновские метаматериалы для квантовых устройств»; ключи: **параметрические усилители бегущей волны**, сквиды, копланарные линии |
| **26-72-10142** | 2026 | **Копасов А.А. (МИСиС)** — молодёжный конкурс РНФ | «Физика сильно нелинейного режима джозефсоновских метаматериалов»; ключи: **джозефсоновский параметрический усилитель бегущей волны**, квантовый предел |

**Вывод РНФ:** Россия финансирует JTWPA точечно, но с 2021 (Кошелец/ИРЭ РАН — международный DFG-проект;
ИРЭ РАН был в топ-организациях нашего корпуса!). Второй грант (2026, МИСиС) — свежий. Ранних (до 2018) РНФ-грантов по JTWPA нет.

---

## 4. KAKEN (Япония) — ПЕРЕСМОТР: Япония ФИНАНСИРУЕТ JTWPA/TWPA (2026-09-06)

**⚠️ Исправление:** в старой KAKEN-базе (`kaken_results.json`, 232 гранта, собрана под другие темы) прямых
проектов по усилителям не было → ошибочный вывод «Япония не финансирует». **Живой поиск KAKEN (kaken.nii.ac.jp)
по терминам усилителей показал: Япония АКТИВНО финансирует.** Прямые проекты (`kaken_jtwpa_live.json`):

| Проект | Суть |
|---|---|
| **Development of low-power superconducting amplifiers for the coming 1000-qubit era** | прямо: усилители для 1000-кубитной эры |
| **Traveling-wave-type superconducting parametric amplifier using artificial periodic transmission line** | прямо: TWPA |
| **Development and application of traveling wave Josephson parametric amplifiers based on three-wave mixing** | прямо: TW JPA 3WM |
| High speed measurement of silicon spin qubits using a Josephson parametric amplifier | JPA для спин-кубитов |
| Study on parametric amplifier using high-temperature superconductor | ВТСП параметрический |
| Study of low-noise superconducting parametric amplifier for terahertz | низкошумный для ТГц |
| Josephson quasi-travelling-wave parametric amplifiers based on coupled resonators | квази-TWPA |

**Урок для методологии:** «0 в базе ≠ 0 в реальности» при узких запросах сбора. KAKEN-база собиралась
под strongly-точные темы (diode/fluxonium/...) и пропустила усилители. Вывод: Япония финансирует
усилители (1000-qubit era!) — НЕ подтверждает тезис «не финансируют».

## 4а. Китай — публикации есть (BAQIS/USTC), NSFC-база узкая (перепроверить)

В корпусе A: **BAQIS 10 работ** (Beijing Academy of Quantum Information Sciences), USTC 2, CAS 2 — Китай
ПУБЛИКУЕТ JTWPA. В NSFC-базе (129, старая, узкая) прямых грантов нет — артефакт сбора (как KAKEN).
Финансирование Китая идёт через национальные квантовые программы (BAQIS — гос. академия, Quantum 2030),
не ловится точечно. **Вывод: Китай, вероятно, финансирует (BAQIS — гос.), но подтвердить через NSFC
нельзя без докачки; честно помечаем как неверифицировано.**

## 5. Вывод S1d (v2, с исправлением)

- **В 2018 грантовый сигнал был СЛАБЫМ** (как и публикации): ЕС — QMiCS 2018/SPA4AstroQIT 2019;
  США — через NQI/DOE; Япония — через KAKEN-проекты усилителей; РФ — 0 до 2021;
- **2021+ — взрыв финансирования:** ЕС (DARTWARS/TruePA/SQELETON/SPARTAN/QuAMP), РФ (Кошелец/DFG),
  Япония (1000-qubit amplifiers), Финляндия (Prometheus 1000-кубитный компьютер);
- **География (v2, с Японией):** ЕС — лидер (15 из 24), UK отдельно (3), CH (2), US (2), RU (2), **JP —
  активно (KAKEN, отдельно от CORDIS/NSF)**;
- **Ключевое:** гранты — ПОЗДНИЙ (lagging) сигнал для JTWPA (взрыв после 2021), НО в Японии и США
  финансирование шло через национальные программы (KAKEN/NQI), которые точечные API не ловят.
- Контраст со SMES (005): там гранты = 0 ВООБЩЕ (проверено по всем каналам), здесь — живые гранты ERC/EIC/
  KAKEN/РНФ/DFG 2021+. Это сигнал «состоялся».

**TODO:** конференции (IEEE TAS/ASC/SNF) → S2/S3/S4 → NARRATIVE. Паспорт данных — ниже.
