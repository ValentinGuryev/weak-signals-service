# Кейс 009: CORC-кабели (Conductor on Round Core) — стоило ли вкладываться в 2018?

> **Роль:** девятый кейс (009), глубокий — по образцу 007 (автоматический, агент ведёт по
> CASE_BUILDING_GUIDE, автор — на стоп-точках и ревью). Ранее — калибровочный `corc_cables/`
> (реестр #42, вердикт ✅). Переименован в 009_corc_cables (конвенция §4.2).
> **Статус:** ✅ ГОТОВ К ЗАКРЫТИЮ (): S1a + патенты + гранты + S2-S5 + конференции +
> роадмапы + NARRATIVE (черновик) + 8 графиков + 13 PDF/выжимок + строка в features_table.
> Ждёт: ревью автора NARRATIVE и финального вердикта.
> **Калибровочный кейс (2018 → 2026).** Гипотеза: ✅ СТОИЛО.
> Вопрос: стоило ли инвестировать в CORC-кабели (REBCO-ленты на круглой сердцевине) в 2018?
> Статус факт-чекинга: подтверждён данными (OpenAlex/Lens/SNF/CORDIS/РНФ/веб, ).

---

## 1. Суть технологии

**CORC (Conductor on Round Core)** — гибкий ВТСП-кабель: REBCO-ленты намотаны спирально на круглую сердцевину. Преимущества: высокая плотность тока, гибкость, малые радиусы изгиба (<50 мм), масштабируемость — идеален для компактных магнитов (fusion, детекторы, ускорители).

## 2. Сигнал 2018

- van der Laan (Advanced Conductor Technologies) — разработчик CORC с 2010-х
- Weiss 2016 «Introduction of CORC wires» (232 цит.) — обзорная статья
- Mulder 2016 «45 kA at 10 T REBCO-CORC CICC» (79 цит.) — CERN, детекторные магниты
- Wang 2018 «Magnetization loss of CORC» (169 цит.) — AC-потери
- **Выглядело**: зрелый кабель для fusion/детекторов, CERN заинтересован

## 3. Вердикт 2018

**✅ ИНВЕСТИРОВАТЬ** — CORC стал ключевым кабелем для компактных термоядерных магнитов.

## 4. Исход 2026 (факт-чекинг)

| Веха | Год | Статус |
|---|---|---|
| Weiss 2016 — CORC wires intro (232 цит.) | 2016 | ✅ |
| Mulder 2016 — 45 kA CORC CICC (79 цит.) | 2016 | ✅ CERN |
| van der Laan 2019 — «Status of CORC a decade after» (245 цит.) | 2019 | ✅ |
| Weiss 2020 — Quench detection CORC for fusion (43 цит.) | 2020 | ✅ |
| Prestemon 2023 — modeling toolbox (DOE) | 2023 | ✅ |
| Anvar 2026 — Nb3Sn/MgB2 CICC vs ReBCO-CORC for fusion | 2026 | ✅ |

**Итог 2026:** ✅ **ПОДТВЕРЖДЕНО — СТОИЛО.** CORC — стандартный проводник для компактных fusion-магнитов (SPARC/CFS, EU-DEMO) и детекторов. CERN/DOE развивают.

## 5. Почему стоило (анализ)

1. **Прямая потребность fusion**: SPARC/CFS, EU-DEMO нужны кабели с током >40 кА при 10+ Тл.
2. **Гибкость + ток**: единственный класс кабелей с радиусом изгиба <50 мм при высоком токе.
3. **Индустриальная поддержка**: Advanced Conductor Technologies + CERN + DOE.
4. **Замена CICC**: CORC-вариант CICC выигрывает по плотности тока у Nb3Sn/MgB2 (Anvar 2026).

## 6. Литература (wishlist)

| Статья | Год | DOI | Цит. |
|---|---|---|---|
| Weiss et al. — Introduction of CORC wires | 2016 | 10.1088/0953-2048/30/1/014002 | 232 |
| Mulder et al. — 45 kA at 10 T REBCO-CORC CICC | 2016 | 10.1109/tasc.2016.2527241 | 79 |
| Wang et al. — Magnetization loss of CORC (T-A) | 2018 | 10.1088/1361-6668/aaf011 | 169 |
| van der Laan et al. — Status of CORC a decade after | 2019 | 10.1088/1361-6668/aafc82 | 245 |
| Mulder et al. — CORC CICC for fusion and detector magnets | 2017 | 10.1088/1757-899x/279/1/012033 | 30 |
| Anvar — Nb3Sn/MgB2 CICC vs ReBCO-CORC for fusion | 2026 | 10.3990/1.9789036572781 | — |

## 7. Урок для калибровки

**«Кабель с уникальной механикой под растущий рынок (fusion) = стоило»**:
- Узкая ниша (короткие радиусы изгиба + высокий ток) закрыта только CORC
- Растущий спрос fusion (SPARC) создал рынок «пик и лопата»
- Академическая зрелость к 2018 (232 цит.) — сигнал, а не шум

## 8. Открытые вопросы — статус (проверено 2026-09-09)

- [x] **Коммерческий объём ACT 2026?** — цифр нет (частная, Crunchbase/CB Insights за пейволом). Известно:
  ACT основана **June 2011** (Crunchbase); активна (сайт жив); свежий **DOE-грант DE-SC0024288**
  (long-length CORC CICC 20-80 кА для fusion, highergov); van der Laan MT-2025 (CICC + demountable joints);
  применения сайта: accelerator >20T, compact fusion, power, FCL, e-aircraft. ⚠️ Объём продаж — неизвестен.
- [x] **CORC vs HTS-CICC (Fusion Energy Systems) — кто выиграл?** — НЕ решён, каждый проект своим путём
  (оценка автора подтверждена): SPARC→VIPER (CFS свой), TRT→stacked/V-Shape (РФ), CFETR→slotted (Китай),
  DEMO→гибридный CS с CORC для внутр. слоя (кандидат). См. roadmap_signal.md.
- [x] **Статус EU-DEMO: CORC выбран окончательно?** — НЕТ, но ⭐ **CORC предложен для внутреннего слоя
  гибридного Central Solenoid (CS)** EU-DEMO (thermal-hydraulic analysis, Fusion Eng. Design 2025, ENEA);
  гибридный CS даёт +13% потока vs ITER-like; Corato (ENEA) CCA 2025 — WPMAG развивает HTS для CS.
  CORC — реальный кандидат для самого нагруженного элемента, но финального выбора нет.
