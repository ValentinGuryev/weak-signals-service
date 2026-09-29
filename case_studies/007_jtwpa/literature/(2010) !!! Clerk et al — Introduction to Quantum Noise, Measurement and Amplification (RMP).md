# (2010) Clerk et al — Introduction to Quantum Noise, Measurement and Amplification (Rev. Mod. Phys.)

**Файл:** `(2010) !!! Clerk et al — Introduction to Quantum Noise, Measurement and Amplification (RMP).pdf`
**Библиография:** A.A. Clerk, M.H. Devoret, S.M. Girvin, F. Marquardt, R.J. Schoelkopf. «Introduction to quantum noise, measurement, and amplification». Reviews of Modern Physics 82, 1155 (2010); arXiv:0810.4729.
**Аффилиации:** McGill; Yale (Devoret, Schoelkopf); Harvard/Yale (Girvin); LMU Munich (Marquardt).
**Релевантность:** 5/5 — **фундаментальный обзор квантового шума, измерения и усиления** (2000+ цит.). Даёт физическую основу «почему quantum-limited усилитель нужен и что это такое» — для мотивации в NARRATIVE.

---

## Суть работы

Канонический обзор (RMP): квантовый шум, измерение, усиление в линейных системах. Ключевой раздел V — **квантовый предел линейных усилителей** (standard quantum limit, SQL).

## Ключевые результаты (для кейса)

### Квантовый предел усилителя (SQL)
- Вывод **Haus-Caves** для бозонного усилителя: усилитель, усиливает обе квадратуры, **добавляет минимум 1/2 фотона шума** (на моду) — «half a photon added»;
- «SQL в упрощённой форме — half a photon added — всегда применяется при высоком усилении» (G ≫ 1);
- «Малым усилением нельзя обойти SQL» — нужно G ≫ 1, чтобы поднять сигнал над шумом следующего каскада;
- Эффективная шумовая температура: T_N ≥ ℏω / 2k_B (≈ 0.05 K при 5 ГГц) — квантовый предел в температурных единицах;
- Связь с детекторами положения, обратное действие (back-action), сжатие.

### Структура обзора
- V.A Preliminaries on amplification; V.B Haus-Caves derivation; V.D Gain and added noise; V.E Quantum limit on added noise and noise temperature.

## Значимость для кейса 007

1. **Физический фундамент S4:** «добавочный шум 1/2 фотона» — абсолютный предел, из которого исходит вся мотивация JTWPA. Macklin 2015 (near-quantum-limited, ~0.5 фотона) = достижение этого предела;
2. **Почему HEMT не тянет:** транзисторный усилитель добавляет ~10-100 фотонов (шумовая температура ~2-4 K >> 0.05 K квантового предела) → для чтения одиночных кубитов (сигнал ~1 фотон) непригоден;
3. Авторы — кто создал полевые кубиты Yale (Devoret/Schoelkopf) — связь «усилители ↔ кубиты» из первых рук;
4. **Температурная форма** T_N ≥ ℏω/2k_B — удобна для сравнения (в выжимках Malnou: 0.66 K ≈ 3 кванта).

## Замечания
- RMP (не open access; arXiv-версия полная);
- 2000+ цит. — самый цитируемый фундамент области;
- Для жюри: «JTWPA работает на физическом пределе, установленном квантовой механикой (Caves 1982, Haus-Caves; обзор Clerk 2010)».
