# Кейс: Cryo-CMOS (криогенная электроника для кубитов) — стоило ли вкладываться в 2018?

> **Калибровочный кейс (2018 → 2026).** Гипотеза: ✅ СТОИЛО.
> Вопрос: стоило ли инвестировать в cryo-CMOS (управляющую электронику для кубитов на криогенных температурах) в 2018?
> Статус факт-чекинга: предварительный (Crossref/OpenAlex, ).

---

## 1. Суть технологии

**Cryo-CMOS** — КМОП-микросхемы, работающие при криогенных температурах (4K), для управления/чтения кубитов. Решает проблему масштабирования: тысячи кубитов нельзя соединить проводами с комнатной электроникой.

## 2. Сигнал 2018

- Degenhardt 2017 (11 цит.): «CMOS based scalable cryogenic control electronics for qubits»
- Ruffino 2018 (4 цит.): «Interfacing Qubits via Cryo-CMOS Front Ends» (Charbon — EPFL)
- Intel, Imec, EPFL — активные исследования
- **Выглядело**: необходимый компонент для масштабирования квантовых компьютеров

## 3. Вердикт 2018

**✅ ИНВЕСТИРОВАТЬ** — без cryo-CMOS не масштабировать кубиты.

## 4. Исход 2026 (факт-чекинг)

| Веха | Год | Статус |
|---|---|---|
| Cryo-CMOS front-ends (Ruffino) | 2018 | ✅ |
| Intel/Imec co-simulation (Gys 2022) | 2022 | ✅ |
| 16nm FinFET DAC (Polat 2026) | 2026 | ✅ прогресс |
| Обзор масштабирования (Underwood 2026) | 2026 | ✅ |
| **Коммерциализация** | 2026 | 🔶 (в составе квантовых систем, не отдельный продукт) |

**Итог 2026:** ✅ **ПОДТВЕРЖДЕНО — СТОИЛО.** Cryo-CMOS активно развивается (Intel, Imec, EPFL), стал ключевым для масштабирования кубитов. Не отдельный рынок, но критичный компонент растущей индустрии.

## 5. Почему стоило (анализ)

1. **Необходимость для масштабирования**: тысячи кубитов требуют криогенной электроники.
2. **Индустриальные гиганты**: Intel, Imec, TSMC вложились.
3. **Системная ставка на кванты** (IBM/Google растут) → cryo-CMOS нужен.
4. **Синергия с CMOS-индустрией** (16nm FinFET).

## 6. Литература (wishlist)

| Статья | Год | Суть | Цит. |
|---|---|---|---|
| Degenhardt et al. — «CMOS based scalable cryogenic control electronics» | 2017 | Ранняя | 11 |
| Ruffino et al. — «Interfacing Qubits via Cryo-CMOS» | 2018 | Front-ends | 4 |
| Gys et al. — «Co-simulation spin qubits + cryo-CMOS» | 2022 | Intel/Imec | 4 |
| Polat et al. — «16nm FinFET DAC for qubits» | 2026 | Прогресс | — |
| Underwood — «Transistors to transmons: cryo-CMOS control» | 2026 | Обзор | — |

## 6а. ⭐ Roadmap-подтверждение (2026-09-02): cryo-CMOS в официальных roadmap'ах IRDS
> Источник: `results/calibration/roadmap_digests/SCE-roadmaps_BEFORE-2018_vs_AFTER-2022.md` + `(2017) IRDS — SC Electronics — Holmes — digest.md`.

| Документ | Год | Статус cryo-CMOS |
|---|---|---|
| IRDS SC Electronics (Holmes/DeBenedictis) | 2017 | SCE-роадмап включает не только СП, но и **cryogenic semiconductor electronics** (cryo-CMOS) как часть экосистемы |
| New Roadmapping Effort for Cryogenic Electronics & QIP | 2018 | Создан IFT «Cryogenic Electronics and QIP» в IRDS (21 чел.); покрытие: SCE + **cryo-semiconductor** + QIP |
| IRDS CEQIP (Quantum Roadmap First Cut) | 2022 | QIP-раздел: control electronics — ключевой challenge (близко к кубитам, крио, вакуум); cryo-CMOS — часть решения |
| IRDS CEQIP members | 2023 | В команде — специалисты по cryo-Semi (Seoul Nat. Univ: Byun, Min; Rambus: Vogelsang) — направление институционализировано |

**Вывод для кейса:** cryo-CMOS — НЕ маргинальная идея, а официально признанное направление в главном мировом roadmap электроники (IRDS) с 2017 года. Это сильное внешнее подтверждение вердикта «✅ стоило»: технология была встроена в стратегию индустрии задолго до 2026.

## 7. Урок для калибровки

**«Необходимый компонент растущей платформы = стоило»** (как криокуллеры, токовводы):
- Квантовые компьютеры растут → cryo-CMOS обязателен для масштабирования
- Гиганты (Intel/Imec) подтверждают ставку
- Рынок — через квантовые системы, не отдельный

## 8. Открытые вопросы

- [ ] Кто лидеры 2026 (Intel, Imec, EPFL, китайские)?
- [ ] Масштаб: сколько кубитов реально управляются cryo-CMOS?
- [ ] Переход к квантовым процессорам — когда cryo-CMOS стандарт?
- [x] **(2026-09-02)** Roadmap-подтверждение: cryo-CMOS в IRDS с 2017 (см. §6а).
