# Кейс: Сверхпроводящие авиадвигатели — калибровочный «провал»

> **Роль:** калибровочный кейс. Главный вопрос (по уточнённой концепции): **«Являлся ли тренд зарождающимся (слабым сигналом) в 2018?»** Вторично: инвестиционный аспект.
> **Вердикт (, решение автора):** ❌ **НЕ состоялся — провал, близко к SMES (005).** Возможность возрождения в будущем (водородная ниша) не исключена, но сейчас — провал.
> **Метка ML:** `label_2026 = 0` (не_состоялся), `commercial_events = 0` (нет M&A/IPO/раундов).
> **Статус:** кейс ЗАКРЫТ  (все сигналы S1-S5 + roadmap + IPO/M&A + анализ пределов собраны).
> **Сигналы:** s1a публикации, patent_signal (Lens+manual), conference_signal (SNF), grant_signal (РНФ-МАИ), semantic_s2, s3_cross_evolution, s5_alternatives, roadmap_signal, ipo_ma_signal, analysis_why_not_2026.

---

## 1. Суть технологии

**Сверхпроводящий авиадвигатель** — электромотор с обмотками из ВТСП (REBCO/MgB₂) для привода винтов/вентиляторов самолёта. Преимущество: мощность/вес выше (нет медных потерь, выше плотность тока). Мотивация: декарбонизация авиации (5% роста трафика/год, выбросы CO₂).

**Ключевые проекты (2017-2020):**
| Проект | Годы | Бюджет | Исход |
|---|---|---|---|
| **E-Fan X** (Airbus+RR+Siemens) | 2017-2020 | не раскрыт | **ОТМЕНЁН 24.04.2020** |
| **ASuMED** (H2020, 723119) | 2017-2020 | €4.78 млн | **CLOSED** |
| **NASA 1.4 MW HEMM** | 2018+ | — | дизайн/испытания, не коммерч. |
| **HIVOMOT** (H2020, 101008067) | 2021+ | — | периодич. отчёт period 2 |
| **NI HTS machine** (MSCA) | ~2021 | — | малый проект, HTS-ротор |

---

## 2. Сигналы 2018 (что говорило «это может быть трендом»)

### 2.1 Патенты (Google Patents, 100 шт «superconducting motor»)
- **Пик активности 2017: 9 патентов/год** (в 2-3× выше среднего 3-5).
- Но: тема старая (с 1974), не «взрывная». Авиационных — всего **3 из 100** (Rolls-Royce GB2548123A, GE CN105818990B, Kyoto JP7724526B2).
- Assignees: Sumitomo Electric (6), Kyoto Univ, Nanjing, Toyota — **авиация НЕ в фокусе** (в основном корабли/промышленность).

### 2.2 arXiv (supr-con, 36967 статей)
- Статьи «superconducting + motor/machine»: **растут 2023-2025 (7/6/7)** — активность есть.
- **Но авиационных — всего 1 за всю историю** (2019, «Topology comparison of SC AC machines for hybrid-electric aircraft»). Авиация — маргинальная ниша.

### 2.3 Гранты (CORDIS)
- **ASuMED (723119)** — €4.78 млн, ЕС, СП-мотор-демонстратор для авиации, 2017-2020 → **CLOSED**.
- **HIVOMOT (101008067)** — «High power and voltage operation of electric motors in aeronautics», СП-использование → отчёт period 2 (не завершён).
- **NI HTS machine** — MSCA, HTS-ротор для авиа-электродвижения.
- **SUPREME (101113107)** — СП-электроракетный двигатель (космос, НЕ авиация).

### 2.4 OpenAlex (прикладной слой: IEEE TAS + SuST)
- **Прикладные журналы НЕ выделяют авиа-моторы как тренд** (12 трендов в датасете, авиации нет).
- Отсутствие в прикладном слое = слабый сигнал зарождаемости.

### 2.5 Конференции (IEEE TAS, 2175 статей)
- В датасете IEEE TAS **нет статей по авиа-моторам** — тема не представлена на главной СП-конференции.

---

## 2.6 ГЛАВНЫЙ СИГНАЛ 2017-2018: «ГОНКА» КОРПОРАЦИЙ (проверяемые источники)

**Сильнейший сигнал «нового тренда» — одновременные анонсы крупнейших авиа-корпораций о создании электролётов.** Это документировано по первичным и отраслевым источникам:

### E-Fan X (Airbus + Rolls-Royce + Siemens) — анонс 28.11.2017
- **Первичные PR:** [Airbus](https://www.airbus.com/newsroom/press-releases/en/2017/11/airbus--rolls-royce--and-siemens-team-up-for-electric-future-pa), [Rolls-Royce](https://www.rolls-royce.com/media/press-releases/yr-2017/28-11-2017-airbus-rr-and-siemens-team-up-for-electric-future.as), [Siemens PDF](https://www.siemens.com/press//pool/de/pressemitteilungen/2017/corporate/PR2017110098COEN.pdf)
- **Детали:** BAe 146 с заменой 1 из 4 турбовентиляторов на **2 MW СП-мотор Siemens** (адаптирован RR, питание от AE2100, батарея 2 т), полёт планировался 2020.
- **Отраслевые:** [FlightGlobal 29.11.2017](https://www.flightglobal.com/news/articles/airbus-siemens-r-r-plan-hybrid-flights-by-2020-443704/), [Leeham](https://leehamnews.com/2017/11/29/airbus-rolls-royce-siemens-develops-hybrid-electric-demonstrator/), [AIN](https://www.ainonline.com/aviation-news/air-transport/2017-11-28/airbus-lead-bae-146-electric-propulsion-demonstration), [Aviation Week](http://aviationweek.com/technology/airbus-e-fan-x-pave-way-electric-regional-aircraft)
- **Wikipedia:** [Airbus E-Fan X](https://en.wikipedia.org/wiki/Airbus_E-Fan_X) — статус «Cancelled».

### Zunum Aero (Boeing HorizonX + JetBlue) — стартап, $6.2M в 2017
- **Boeing HorizonX + JetBlue Technology Ventures вложили $6.2 млн (Series A, апрель 2017)** — гибрид-электрический региональный самолёт до 50 мест. [Wikipedia Zunum Aero](https://en.wikipedia.org/wiki/Zunum_Aero)
- **Отраслевые:** [Aviation Week — Boeing/JetBlue back hybrid-electric startup](http://aviationweek.com/technology/boeing-jetblue-back-hybrid-electric-regional-startup), [FlightGlobal — Zunum launches](https://www.flightglobal.com/news/articles/zunum-launches-hybrid-electric-aircraft-for-regional-441877/), [IEEE Spectrum](https://spectrum.ieee.org/zunum-aeros-hybrid-electric-airplane-aims-to-rejuvenate-regional-travel)
- **Крах:** после фев 2018 не смог собрать **$50 млн Series B** → лейоффы, [Forbes 2019](https://www.forbes.com/sites/jeremybogaisky/2019/07/02/zunum-aero-nears-zero-founders-struggle-to-raise-money-after-layi), [AIN 2019](https://www.ainonline.com/aviation-news/air-transport/2019-01-03/zunum-runs-financing-trouble). Позже **судился с Boeing** ([The Verge 2020](https://www.theverge.com/2020/11/24/21612702/zunum-aero-sues-boeing-fraud-hybrid-electric-jet), [Reuters 2024 — Boeing отменил $72M вердикт](https://www.reuters.com/legal/litigation/boeing-convinces-us-judge-overturn-72-mln-trade-secrets-verdict-2024-08-14/)).

### Wright Electric (EasyJet) — анонс сент 2017
- **EasyJet объявила (сент 2017):** разработка электрического 180-местного самолёта к 2027 с Wright Electric. [Wikipedia Wright Electric](https://en.wikipedia.org/wiki/Wright_Electric), [Guardian 27.09.2017](https://www.theguardian.com/business/2017/sep/27/easyjet-electric-planes-wright-electric-flights), [FlightGlobal](https://www.flightglobal.com/news/articles/easyjet-unveils-short-haul-electric-aircraft-ambitio-441543/), [TechCrunch 2017](https://techcrunch.com/2017/03/21/wright-electric-planes/)
- **Исход:** концепт без СП-мотора; к 2026 не коммерциализирован (Wright работал с EasyJet, но 180-местного электро-самолёта нет).

### Rolls-Royce ACCEL «Spirit of Innovation» — 2018+
- **RR начал (2018) проект ACCEL** — рекорд скорости на электро-самолёте (обычный мотор YASA, батареи, НЕ СП). Рекорд 2021-2022 ([BBC 21.01.2022](https://www.bbc.com/news/uk-england-derbyshire-60068786), [RR PR 15.09.2021](https://www.rolls-royce.com/media/press-releases/2021/15-09-2021-rr-all-electric-spirit-of-innovation-takes-to-the-skies)).
- **Смысл:** RR двигался к электрификации, но через батареи, а не СП.

### Boeing NeXt (городская авиация) — закрыт сент 2020
- Boeing создал **NeXt** (городская мобильность, eVTOL); PAV прототип полетел 22.01.2019. Но **NeXt закрыт сент 2020**. [Wikipedia Boeing NeXt](https://en.wikipedia.org/wiki/Boeing_NeXt), [AIN 17.09.2020](https://www.ainonline.com/aviation-news/business-aviation/2020-09-17/boeing-next-close-raising-doubts-over-evtol-activit).

### NASA (не корпорация, но контекст)
- NASA 1.4 MW HEMM (2018) — СП-роторные катушки (Scheidler 2018); NASA N3-X — концепт распределённого СП-электродвижения (не построен).

**Вывод по «гонке»:** мощный публичный сигнал 2017-2018 (Airbus+RR+Siemens, Boeing+JetBlue, EasyJet+Wright, RR ACCEL) создавал впечатление зарождающегося тренда. НО: (1) большинство проектов — НЕ СП (батареи/гибрид), (2) к 2020-2022 все закрыты/свёрнуты (E-Fan X отменён, Zunum обанкротился, Boeing NeXt закрыт), (3) СП-моторы остались только в E-Fan X/ASuMED/NASA — и те не коммерциализированы.

---

## 3. Вердикт (2018): был ли это зарождающийся тренд?

**🔶 ВЫГЛЯДЕЛ зарождающимся, но НЕ был:**

**Аргументы «за» (сильный публичный сигнал):**
- **Гонка корпораций 2017-2018** — Airbus+RR+Siemens, Boeing+JetBlue (Zunum), EasyJet+Wright, RR ACCEL — все анонсировали электролёты (см. §2.6). Такого одновременного движения «больших имён» достаточно, чтобы алгоритм пометил тему как emerging.
- Гранты ЕС (ASuMED €4.78 млн), NASA HEMM.

**Аргументы «против» (слабые базы):**
1. **Физический фильтр:** СП-преимущество (мощность/вес) есть, но крио-система (вес/объём/надёжность) + AC-потери в обмотках статора + сертификация авиации → экономика слабая.
2. **Мало патентов в авиа-нише** (3/100), нет индустриального фокуса.
3. **arXiv: 0 авиа-статей до 2019** — нет научного бума.
4. **Прикладной слой OpenAlex пуст** — журналы не сигналят.
5. **Большинство анонсов — НЕ СП** (батареи/гибрид): СП-моторы — лишь часть E-Fan X/ASuMED/NASA.

**Вывод:** публичный шум (гонка) был сильным, но базы + физический фильтр показывали, что **специфически СП-авиация — слабый сигнал**. Правильный вердикт: **не зарождающийся тренд (ложный/перегретый)**.

---

## 4. Исход 2026 (факт-чекинг — документы провала)

| Проект | Судьба | Документ |
|---|---|---|
| **E-Fan X** | ✅ ОТМЕНЁН 24.04.2020 (COVID + стратегия Airbus) | FlightGlobal 24.04.2020 |
| **ASuMED** | ✅ CLOSED (CORDIS статус «Project closed», проверено 2026-08-21) | CORDIS 723119 |
| **NASA 1.4 MW HEMM** | 🔶 дизайн/испытания роторных катушек (2018), не коммерциализирован | Scheidler 2018 (AIAA) |
| **HIVOMOT** | 🔶 продолжается (отчёт period 2), но НЕ демонстратор | CORDIS 101008067 |
| **СП-моторы Японии** | 🔶 для **кораблей** (Izumi 2022), НЕ авиации | 10.2221/jcsj.57.79 |

**Итог 2026:** ✅ **НЕ состоялся** (тренд был ложным/перегретым). Ни один СП-авиадвигатель не коммерциализирован. Направление электролётов живо, но **без СП** (батареи/водород — Airbus, RR; Zunum обанкротился, Boeing NeXt закрыт).

---

## 5. Почему провал (анализ)

1. **Крио-система убивает преимущество:** СП-мотор требует криоохлаждения (вес, объём, надёжность в полёте). Выигрыш в мощности/весе мотора съедается крио-системой.
2. **AC-потери:** обмотки статора работают на переменном токе → AC-потери в СП (гистерезис) → нужен доп. крио-нагрев (Sumption 2018).
3. **Сертификация авиации:** крио-системы не сертифицированы, новые риски (Courtin 2018).
4. **COVID-2020:** E-Fan X отменён, бюджетные приоритеты сместились.
5. **Альтернативы дешевле:** батареи/водород прогрессировали быстрее, чем ожидалось; СП не нужен для коротких маршрутов.

---

## 6. Урок для калибровки

**«Публичная гонка корпораций ≠ зарождающийся тренд. Проверяй базы + физический фильтр»:**
- Анонсы E-Fan X, Zunum, Wright (2017) — **мощный публичный шум**, создавал иллюзию тренда.
- Но базы (патенты 3/100 авиа, 1 статья arXiv, пустой прикладной слой OpenAlex) НЕ подтверждали СП-авиацию.
- **Ключевой урок: одновременные анонсы больших корпораций — сильный, но НЕДОСТАТОЧНЫЙ сигнал.** Надо отличать «гонку за гибрид-электрификацией» (реальную, но без СП) от «СП-авиации» (слабый сигнал).
- Физический фильтр (крио-вес + AC-потери + сертификация) отсекает раньше, чем рынок.
- **Методологический приём:** при анонсе «больших имён» проверять, специфична ли технология (СП) или это общий тренд (электрификация), и смотреть прикладной слой (OpenAlex) — он был пуст.

---

## 7. Литература / данные

- `literature/(2019) !!! AC machines for hybrid-electric aircraft — arXiv 1910.07077.pdf` ✅
- `wishlist.md` — документы, которые нужно скачать (провалы + сигналы + обзоры)

## 8. Открытые вопросы

- [ ] Точная судьба HIVOMOT (завершён? результаты?)
- [ ] NI HTS machine: был ли построен демонстратор?
- [ ] Япония (Kyoto, Sumitomo): статус авиа-СП-моторов 2024-2026?
- [ ] Скачать arXiv 1910.07077 — ✅ сделано
- [ ] NASA HEMM: финальный статус (продолжается/закрыт)?

---

## 9. Аналитика (не сигналы)

- **`analysis_why_not_2026.md`** — почему СП-авиамоторы не состоялись к 2026: два нерешённых
  физических предела (AC-потери в СП-статоре + тепловой runaway при крио, ток ~7% Ic, <40 кВт/кг),
  штрафная масса крио, вербализация в источниках (arXiv 2019 «не дотягивает», Klop 2025,
  Sumption 2018), механизм перелома 2020 (отмена E-Fan X + переключение на водород/крио-медь/SAF).
