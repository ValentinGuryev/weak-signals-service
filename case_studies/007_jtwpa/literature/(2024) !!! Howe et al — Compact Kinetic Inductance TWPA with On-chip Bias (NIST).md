# (2024) Howe et al — Compact Superconducting Kinetic Inductance Traveling Wave Parametric Amplifiers with On-chip Bias Circuitry (NIST)

**Файл:** `(2024) !!! Howe et al — Compact Kinetic Inductance TWPA with On-chip Bias (NIST).pdf`
**Библиография:** L. Howe, A. Giachero, M. Vissers, J. Wheeler, J. Austermann, J. Hubmayr, J. Ullom. «Compact Superconducting Kinetic Inductance Traveling Wave Parametric Amplifiers with On-chip Bias Circuitry». IEEE-CSC, ESAS and CSSJ Superconductivity News Forum (global edition), Issue No. 57, Oct 2024. Материал дан на ASC 2024, Sept 2024, Salt Lake City, USA.
**Аффилиации:** NIST Boulder (США); University of Colorado Boulder; University of Milano-Bicocca + INFN Milano-Bicocca (Италия).
**Релевантность:** 5/5 — **KITWPA (главный конкурент JTWPA) от NIST (лидер по KIT) + связь с DARTWARS** — ключ к S5 (почему KITWPA не вытеснил JTWPA, в чём его ниша).

---

## Суть работы

Представляет **миниатюризацию KITWPA**: микрофабрикованные (на чипе) bias tee, направленные ответвители и диплексеры для работы 3WM Kinetic Inductance TWPAs (KIT). Цель — убрать громоздкие внешние СВЧ-компоненты (кабели, bias tees, couplers, diplexers), которые «драматически увеличивают footprint, сложность установки, уменьшают криогенный объём, вносят потери и отражения, мешающие работать у квантового предела».

## Ключевые результаты

### Контекст (важно для S5)
- **«Квантовые вычислительные системы и эксперименты фундаментальной физики требуют усилительных цепочек, работающих вблизи квантового предела добавочного шума»**;
- «И JPA, и TWPA используются как первые усилители для чтения в пределах нескольких квантов от квантового предела — **и в настоящее время входят в коммерческую индустрию**» (прямая цитата — коммерциализация!);
- Главная проблема всех демонстраций/продуктов: **громоздкие внешние СВЧ-компоненты** для подведения смещений.

### Результат
- Спроектированы и проверены микрофабрикованные bias tees, направленные ответвители и диплексеры для KIT;
- Показана работа KIT с интегрированными компонентами;
- **Уменьшение общего footprint усилителя почти в 5 раз**, число потерь/соединений — к практическому минимуму;
- «Значительный прогресс к миниатюризации и упрощению установок параметрических усилителей» → «более широкое применение».

## Значимость для кейса 007

1. **KITWPA — зрелый конкурент (S5):** NIST (Ullom/Hubmayr — лидеры KIT для CMB/радиоастрономии) в 2024 миниатюризирует KIT — технология жива и индустриализуется;
2. **Почему не вытеснил JTWPA:** KIT силён там, где нужны массивы каналов и нет требования интеграции с кубитными чипами (радиоастрономия/MKID, CMB — NIST/JPL); JTWPA — в кубитном чтении (встроен в чипы IBM/Google). Обе «входят в коммерческую индустрию» — сосуществование по нишам;
3. **Связь с DARTWARS** (грант №101027746 в благодарности!) — EU-консорциум (INFN Milano-Bicocca = Giachero — участник) по TWPA для радиоастрономии — подтверждает грантовый след для S1d;
4. **Финансирование:** NASA (2 гранта), DOE, DARTWARS/EU — мульти-источники, включая космос (NASA) — JTWPA/KIT нужны и для космических/фундаментальных экспериментов;
5. Ссылка [1] — Malnou PRX Quantum 2021 (KIT near-quantum-limited) — в нашем wishlist B2a.

## Замечания
- SNF-статья (1 стр.), полная версия — вероятно, IEEE TAS/ASC 2024 (Howe et al.);
- NIST Boulder — группа Ullom (KIT для CMB-S4, radioastronomy);
- DARTWARS — EU H2020/Horizon грант (101027746) — кандидат для grant_signal кейса 007.
