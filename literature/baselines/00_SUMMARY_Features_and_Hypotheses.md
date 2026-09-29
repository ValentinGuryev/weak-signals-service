# Сводка: фичи и гипотезы из литературы (для проверки на наших кейсах)

**Создана:**  (дополнена : +10 статей; **: +10 статей из пачки TRIZ** — Ebadi AAES-2026, Chichorro-2022, Gibson-2018, Mints-2024, Gridach-2025, Wei-2025, Ueda-2026, SciAgents-2025, Turgel&Chernova-2024, SCI-IDEA-2026; новые гипотезы H24–H31, раздел 2и; **2026-09-14: +16 канонов/бейзлайнов из wishlist** — Ansoff, Callon, van Raan, Kleinberg, Shehabuddeen, Chen, Cozzens, VOSviewer, Guo-Börner, Mund, Strumsky, Guo-SAO, Ranaei, Jung-Segev, Mühlroth, Swanson; новые гипотезы H35–H40, раздел 2л; **2026-09-22: +2 — Cosmos 1.0 (Gong 2025) и TRI (McCarthy 2026)** — §1.10, ET100 в §2д, репо в §2е, гипотезы H41–H43 (§2м), §3.4)
**Назначение:** саммари идей из литературы (weak signal detection, topic evolution, S-кривая, TRIZ/TESE),
которые мы планируем проверить на наших калибровочных кейсах.
**⚠️ Назначение:** в файле — ТОЛЬКО идеи из литературы (не результаты/методы этого проекта).
**Выжимки:** `literature/baselines/*.md` и `literature/*.md` (полные библиографии в каждой).

---

## 📚 Библиотека источников

| Ключ | Работа (полная ссылка) | Где выжимка |
|---|---|---|
| **Ebadi 2022** | Ebadi, Auger, Gauthier. Detecting Emerging Technologies using Deep Learning and Weak Signal Analysis. arXiv:2205.05449 (2022) | `baselines/(2022) !!! Ebadi...` |
| **Ebadi 2024** | Ebadi, Auger, Gauthier. WISDOM: AI-Powered Framework for Emerging Research Detection. (2024) | `baselines/(2024) !!! Ebadi WISDOM...` |
| **BERTrend 2024** | Boutaleb, Picault, Grosjean. BERTrend: Neural Topic Modeling for Emerging Trends Detection. arXiv:2411.05930. Код: rte-france/BERTrend | `baselines/(2024) _!!_ Boutaleb...` |
| **Huang 2024** | Huang et al. Framework for Topic Evolution via Embedding Motion (2024). Код: WannaLearning/Demonstrating-Forecasting-and-Explaining-Topic-Evolution | `baselines/(2024) _!!_ Huang...` |
| **Wang 2026** | Wang Zhengyuan et al. Weak Signal Disruptive Tech Early Detection (кит.). (2026) | `baselines/(2026) !!! Wang...` |
| **Menning 2026** | Menning, Farkas, Vribék, van der Velden. Regulatory foresight weak signal mining: AI-based micro-topic emergence scoring. Array 31:101126. Код: HOLiFOOD/WSM | `baselines/(2026) _!!_ Menning...` |
| **Popper 2025** | Popper, Villarroel. Sustainable disruptive growth: foresight, wild cards, weak signals. Foresight STI Gov 19(1). DOI: 10.17323/fstig.2025.24753 | `baselines/(2025) !!! Popper...` |
| **Rotolo 2025** | Rotolo, Natalicchio, Porter, Schoeneck. Emerging tech, institutional groups, microneedles. TFSC 213:124006 | `baselines/(2025) !! Rotolo...` |
| **Shaeva 2024** | Shaeva, Khlopov. Detecting weak signals in futures research: collective intelligence. Foresight. DOI: 10.1108/FS-11-2023-0230 | `baselines/(2024) !! Shaeva...` |
| **Burmaoglu 2026** | Burmaoglu, Saritas, Kara. LLM-Augmented Innovation Regime Classification (патентометрия). Research Square preprint | `baselines/(2026) !! Burmaoglu...` |
| **Ilmola & Kuusi 2006** | Filters of weak signals hinder foresight. Futures 38:908-924. DOI: 10.1016/j.futures.2005.12.019 | `baselines/(2006) !!! Ilmola...` |
| **Daim 2006** | Daim, Rueda, Martin. Technology Forecasting Using Bibliometric Analysis and System Dynamics. PICMET 2006 | `baselines/(2006) !! Daim et al...` |
| **Daim 2009** | Daim, Suntharasaj. Technology diffusion: bibliometric analysis and Bass model. Foresight 11. DOI: 10.1108/14636680910963936 | `baselines/(2009) !! Daim, Suntharasaj...` |
| **Cuhls 2020** | Horizon Scanning in Foresight. Futures & Foresight Science. DOI: 10.1002/ffo2.23 | `baselines/(2020) !! Cuhls...` |
| **Ashton 2020** | Intelligent Technology Scanning. Foresight STI Gov. 14(3). DOI: 10.17323/2500-2597.2020.3.15.29 | `baselines/(2020) ! Ashton...` |
| **Ghane 2022** | TRIZ trend of engineering system evolution: review (2022) | `baselines/(2022) !! Ghane...` |
| **Ghane 2024** | Semantic TRIZ feasibility: systematic review (2024) | `baselines/(2024) !! Ghane Semantic...` |
| **Ghane 2026 (TESE)** | Navigating patent trends via system components completeness (2026) | `baselines/(2026) !! Ghane...` |
| **Chybowska 2019** | Review of TRIZ tools for forecasting evolution of technical systems. Manag. Syst. Prod. Eng. | `TRIZ/(2019) !! Chybowska...` |
| **Cascini 2012** | TRIZ-based Anticipatory Design of Future Products. J. Integr. Des. Process Sci. | `TRIZ/(2012) ! Cascini...` |
| **Jiang 2025** | Patterns of emerging technology impact: digital medical. Inf. Res. DOI: 10.47989/ir30iConf47221. Данные: jiangman29/Paper-Data | `baselines/(2025) _!_ Jiang...` |
| **Salatino 2017** | How are topics born (2017) | `literature/(2017) _!!!_ Salatino...` |
| **Salatino 2018** | AUGUR: Forecasting emergence of new research topics (2018) | `literature/(2018) !!! Salatino AUGUR...` |
| **Carley 2018** | An indicator of technical emergence. Scientometrics | `literature/(2018) !!! Carley...` |
| **Garner 2017** | Technological emergence indicators using emergence scoring | `literature/(2017) !!! Garner...` |
| **Rotolo 2015** | What is an emerging technology? Res. Policy | `literature/(2015) !!! Rotolo...` |
| **Small 2014** | Identifying emerging topics in science and technology | `literature/(2014) !!! Small...` (дубль по содержанию: `baselines/(2014) !!! Small...`, ручная пачка 2026-09-14) |
| **Wang 2018** | Bibliometric model for identifying emerging research topics | `literature/(2018) !! Wang...` |
| **Glanzel 2012** | Using core documents for detecting new emerging topics | `literature/(2012) !!! Glanzel...` |
| **Leydesdorff 2016** | Co-word maps and topic modeling comparison | `literature/(2016) ! Leydesdorff...` (Leydesdorff & Nerghes) |
| **Leydesdorff-Wouters-Bornmann 2016** | Professional and citizen bibliometrics (индикаторы как boundary objects) | `baselines/(2016) !! Leydesdorff...` (новая, ручная пачка 2026-09-14) |
| **Kastrin-Hristovski 2020** | Scientometric analysis of literature-based discovery (LBD) | `baselines/(2020) _!!_ Kastrin...` (репо akastrin/lbd-review) |
| **Lairgi 2026 (C-Unseen)** | C-Unseen: Weak Signal Detection in DTKGs via LLM Reasoning. arXiv:2608.26870. **Код: AuvaLab/itext2kg (962★)** | `baselines/(2026) _!!!_ Lairgi...` |
| **Ellermann 2025** | Leveraging GenAI for technology foresight. ICED25. DOI: 10.1017/pds.2025.10236 | `baselines/(2025) !!! Ellermann...` |
| **Hladchenko 2026** | Emerging/established topics in drone research (OpenAlex, WISDOM). arXiv:2606.03362 | `baselines/(2026) !! Hladchenko...` |
| **Park & Kim 2021** | Renewable energy topics: STM + weak signal concept. Energies 14:1497. DOI: 10.3390/en14051497 | `baselines/(2021) !! Park, Kim...` |
| **Piraintorn 2025** | Weak signals to enhance NPD ideation (insurance Thailand). PhD, Grenoble Alpes | `baselines/(2025) !! Piraintorn...` |
| **Roy 2026** | Management of weak signals in public administration. EKONBIZ 2026 | `baselines/(2026) ! Roy...` |
| **Park 2026 (JIK)** | AI as cognitive collaborator (assimilation/accommodation). J. Innovation & Knowledge 100892 | `baselines/(2026) ! Park (JIK)...` |
| **Battistella 2025** | CSFs for technology roadmapping in SME clusters. JET-M 77:101902 | `baselines/(2025) ! Battistella...` |
| **Laplante 2024** | Roadmap sectorielle AAM Canada (DRM+Delphi+S-PLAN). PolyPublie (фр.) | `baselines/(2024) ! Laplante...` |
| **Moghadam 2025** | CSFs in transfer of emerging technologies (Industry 4.0). IJAOR 13(4) | `baselines/(2025) ! Moghadam...` |
| **Ebadi 2026 (AAES)** | Ebadi, Auger, Gauthier. Unveiling Weak Signals of Emergence in Underwater Sensing Research Trends. Archives of Adv. Eng. Science 4(3):229-237. DOI: 10.47852/bonviewAAES42023902 | `baselines/(2026) !!! Ebadi... Underwater Sensing` |
| **Chichorro 2022** | Chichorro, Pereira, Dias, Lopes da Costa, Goncalves. Research Landscape and Trends in Corporate Foresight. Foresight STI Gov 16(3):49-66. DOI: 10.17323/2500-2597.2022.3.49.66 | `baselines/(2022) !! Chichorro...` |
| **Gibson 2018** | Gibson, Daim, Garces, Dabic. Technology Foresight: A Bibliometric Analysis to Identify Leading and Emerging Methods. Foresight STI Gov 12(1):6-24. DOI: 10.17323/2500-2597.2018.1.6.24 | `baselines/(2018) !! Gibson...` |
| **Mints 2024** | Mints, Simanaviciene, Polupanova. Early diagnosis of catastrophic events: weak signals detection based on information field monitoring. Гл. 3.5 монографии MRU (© 2024) | `baselines/(2024) ! Mints...` |
| **Gridach 2025** | Gridach et al. Agentic AI for Scientific Discovery: A Survey. ICLR 2025, arXiv:2503.08979 | `baselines/(2025) ! Gridach...` |
| **Wei 2025** | Wei et al. From AI for Science to Agentic Science: A Survey. arXiv:2508.14111v2. Репо: Awesome-Agent-Scientists | `baselines/(2025) _!_ Wei...` |
| **Ueda 2026** | Ueda, West, Veselovsky. What Should We Forecast? Benchmarking Agents on Early Question Discovery (HorizonBench). EPFL/Preseen (год по содержанию) | `baselines/(2026) !! Ueda...` |
| **SciAgents 2025** | Ghafarollahi, Buehler. SciAgents: Automating Scientific Discovery Through Bioinspired Multi-Agent Graph Reasoning. Adv. Mater. 37:2413523. DOI: 10.1002/adma.202413523. Репо: lamm-mit/SciAgentsDiscovery | `baselines/(2025) _!!!_ Ghafarollahi...` |
| **Turgel 2024** | Тургель, Чернова. Открытые библиографические базы данных: в поисках альтернативы Scopus и WoS. Экономика науки 10(3):34-51. DOI: 10.22394/2410-132X-2024-10-3-34-51 | `baselines/(2024) !! Turgel...` |
| **SCI-IDEA 2026** | Keya, Rabby, Auer, Vahdati, Mitra, Jaradeh. SCI-IDEA: Context-Aware Scientific Ideation. Machine Learning 115:103. DOI: 10.1007/s10994-026-07036-8 | `baselines/(2026) !! Keya...` |
| **Ansoff 1975** | Ansoff. Managing Strategic Surprise by Response to Weak Signals. California Management Review 18(2). DOI: 10.2307/41164635 | `baselines/(1975) !!! Ansoff...` |
| **Callon 1991** | Callon, Courtial, Laville. Co-word analysis as a tool for describing network of interactions (polymer chemistry). Scientometrics 22(1):155-205. DOI: 10.1007/bf02019280 | `baselines/(1991) !!! Callon...` |
| **van Raan 1991** | van Raan, van der Velde. Bibliometric mapping and early warning for emerging topics (materials science). Research Evaluation 1(2):115-127. DOI: 10.1093/rev/1.2.115 | `baselines/(1991) !!! van Raan...` |
| **Kleinberg 2002** | Kleinberg. Bursty and hierarchical structure in streams. KDD'02. DOI: 10.1145/775047.775061 | `baselines/(2002) !!! Kleinberg...` |
| **Shehabuddeen 2005** | Shehabuddeen, Probert. Excavating the technology landscape: technology intelligence to detect early warning signals. IEEE IEMC. DOI: 10.1109/iemc.2004.1407130 | `baselines/(2005) !! Shehabuddeen...` |
| **Chen 2006** | Chen. CiteSpace II: detecting and visualizing emerging trends. JASIST 57(3):359-377. DOI: 10.1002/asi.20317 | `baselines/(2006) !!! Chen...` |
| **Cozzens 2010** | Cozzens, Gatchair, Kang, Kim, Lee, Ordóñez, Porter. Emerging technologies: quantitative identification and measurement. TASM 22(3). DOI: 10.1080/09537321003647396 | `baselines/(2010) !! Cozzens...` |
| **VOSviewer 2010** | van Eck, Waltman. Software survey: VOSviewer. Scientometrics 84(2):523-538. DOI: 10.1007/s11192-009-0146-3. Репо: neesjanvaneck/VOSviewer-Online | `baselines/(2010) _!!_ van Eck...` |
| **Guo-Börner 2011** | Guo, Weingart, Börner. Mixed-indicators model for identifying emerging research areas. Scientometrics 89:421-435. DOI: 10.1007/s11192-011-0433-7 | `baselines/(2011) !! Guo, Weingart...` |
| **Mund 2015** | Mund, Neuhäusler. Early-stage identification of emerging topics: usability of bibliometric characteristics. J. Informetrics 9(4):1018-1033. DOI: 10.1016/j.joi.2015.09.004 | `baselines/(2015) !! Mund...` |
| **Strumsky 2015** | Strumsky, Lobo. Identifying the sources of technological novelty. Research Policy 44(8):1445-1461. DOI: 10.1016/j.respol.2015.05.008 | `baselines/(2015) !! Strumsky...` |
| **Guo-SAO 2016** | Guo, Wang, Li, Zhu. SAO-based morphology analysis for direction of technological change. TFSC 105:27-40. DOI: 10.1016/j.techfore.2016.01.028 | `baselines/(2016) !! Guo, Wang...` |
| **Ranaei 2019** | Ranaei, Suominen, Porter, Carley. Evaluating technological emergence using text analytics. Scientometrics 122:215-230. DOI: 10.1007/s11192-019-03275-w | `baselines/(2019) !!! Ranaei...` |
| **Jung-Segev 2022** | Jung, Segev. Identifying a common pattern within ancestors of emerging topics for pan-domain emergence prediction. Knowledge-Based Systems 258:110020. DOI: 10.1016/j.knosys.2022.110020 | `baselines/(2022) !! Jung...` |
| **Mühlroth 2023** | Mühlroth, Kölbl, Grottke. Innovation signals: ML to separate noise from news. Scientometrics 128:2649-2676. DOI: 10.1007/s11192-023-04672-y | `baselines/(2023) !! Mühlroth...` |
| **Gong 2025 (Cosmos)** | Gong, McCarthy, Griffith, McFarland, Rizoiu. Cosmos 1.0: a multidimensional map of the emerging technology frontier. Sci. Data 2025. DOI: 10.1038/s41597-025-06125-y. Данные: Figshare 10.6084/m9.figshare.28268561. Код: xian-gong-elaine/Cosmos_1.0 | `baselines/(2025) _!!!_ Gong et al...` |
| **McCarthy 2026 (TRI)** | McCarthy, Amarasiri, Gong. Translation Readiness Index: Measuring the Semantic Proximity of Research to Patented Science. arXiv:2606.31102. Код: EmmaScharfmann/PatentPaperPairs | `baselines/(2026) _!_ McCarthy...` |

**Пачка 2026-09-14 (16 канонов/бейзлайнов):** co-word (Callon 1991), weak signals (Ansoff 1975), burst (Kleinberg 2002), LBD (Swanson 1986), CiteSpace (Chen 2006), VOSviewer (2010), раннее предупреждение по материалам (van Raan 1991), мульти-индикаторы (Cozzens 2010, Guo-Börner 2011), ранняя стадия (Mund 2015), патентная новизна (Strumsky 2015), SAO-семантика (Guo 2016), EScore-наследник (Ranaei 2019), пан-домен (Jung-Segev 2022), ML сигнал/шум (Mühlroth 2023), TI (Shehabuddeen 2005). Все — из wishlist `baselines/wishlist.md` (закрыт полностью).

---

## 1. Фичи, предлагаемые в литературе

### 1.1 Количественные (частота терминов)

| Фича | Идея | Источник (где заявлена) |
|---|---|---|
| **GrowthRate** | Скорость роста частоты термина (3-летние окна) | Ebadi 2022: KEM/KIM, «рост частоты по окнам» |
| **Novelty** | Возраст термина (время с 1-го появления) | Ebadi 2022: новизна как измерение слабого сигнала |
| **Acceleration** | Вторая производная роста | Ebadi 2022 (KEM/KIM); Garner 2017 (emergence scoring) |
| **Visibility (DoV)** | TF/N × временной вес | Ebadi 2022 (формула DoV) |
| **Diffusion (DoD)** | Document frequency | Ebadi 2022 (формула DoD) |
| **Citation-based novelty** | Появление в core documents / цитатах | Glanzel 2012 (core documents); Small 2014 |

### 1.2 Семантические (эмбеддинги/лексика)

| Фича | Идея | Источник |
|---|---|---|
| **Topic embedding motion** | Движение темы в embedding-пространстве предсказывает эволюцию | Huang 2024 (проверено: ~50% невиданных тем) |
| **Semantic shift TRIZ** | Сдвиг лексики по TRIZ-трендам | Ghane 2024 (Semantic TRIZ) |
| **Noise filter тем** | Классификация noise/weak/strong | BERTrend 2024 |
| **Facets из работ (objective/method/eval/future-work)** | Структуризация контекста исследователя для генерации идей (сжатие работы до ~200 токенов) | SCI-IDEA 2026 (Keya) |
| **Translation Readiness (патентная близость текста)** | Семантическая близость title+abstract к патентованным исследованиям (SPECTER2+XGBoost, ROC-AUC 0.774) — латентный «язык изобретения» до появления патентов | McCarthy 2026 (TRI) |

### 1.3 Графовые (сети цитирований)

| Фича | Идея | Источник |
|---|---|---|
| **Bipartite time×keywords communities** | Louvain-сообщества «время × слова» | Ebadi 2022 |
| **Triplet structures** | Изменения триплетов в темпоральных сетях | Wang 2026 |
| **Topic birth (AUGUR)** | Предсказание рождения темы по сети | Salatino 2018 (AUGUR) |
| **σ-инновационность (CiteSpace)** | betweenness × burst > 1.5 = «революционная» работа/автор (потенциально = наш цитатный якорь) | Chichorro 2022 |
| **Concept-graph связность** | Плотность скрытых междоменных связей (концепт-граф + LLM-рассуждение) | SciAgents 2025 |

### 1.4 S-кривая / диффузия

| Фича | Идея | Источник |
|---|---|---|
| **Fisher-Pry (b, c)** | Параметры S-кривой по публикациям | Daim 2006 |
| **Inflection point** | Год перегиба S-кривой | Daim 2006 |
| **Bass p/q** | Коэффициенты диффузии (инновация/имитация) | Daim 2009 |
| **Time-to-adoption** | Прогноз лет до внедрения | Daim 2009 |
| **S-curve stage (TRIZ)** | Стадия по S-кривой 1-6 | Chybowska 2019; Ghane 2022 |

### 1.5 TRIZ/TESE (эволюция систем)

| Фича | Идея | Источник |
|---|---|---|
| **Idealness trend** | Рост идеальности системы | Ghane 2022 |
| **Micro-level transition** | Макро→микро переход | Ghane 2022 |
| **Dynamicization** | Рост динамизации | Ghane 2022 |
| **System completeness (TESE)** | Завершённость компонентов по патентам | Ghane 2026 |
| **Anticipatory design** | Проектирование «будущих» продуктов по паттернам | Cascini 2012 |

### 1.6 LLM-гибридные (LLM как калибратор/интерпретатор)

| Фича | Идея | Источник |
|---|---|---|
| **LLM-интерпретация микро-тем** | LLM даёт ярлыки/новизну/серьёзность слабых сигналов (НЕ заменяет эксперта) | Menning 2026 (WSM) |
| **LLM-калибровка патентометрии** | LLM как структурированный калибровочный агент внутри индикаторной схемы (не standalone-классификатор) | Burmaoglu 2026 |
| **Aha-детекция (пороги novelty×surprise)** | Кандидат-идея = превышение порогов новизны и удивления над контекстом профиля | SCI-IDEA 2026 |
| **⚠️ LLM-as-judge смещение** | LLM-оценки завышают экспертную на 3-4/10 и НЕ коррелируют с экспертами (r≈0.02–0.17) → автоматическая валидация не заменяет человека | SCI-IDEA 2026 |

### 1.8 Реляционные/графы знаний (LLM+DTKG)

| Фича | Идея | Источник |
|---|---|---|
| **Rare subgraph + corroboration** | Weak signal = редкий семантический подграф, корроборированный во времени (не частота термина) | Lairgi 2026 (C-Unseen) |
| **Lead time до strong signal** | Метрика: насколько рано сигнал пойман до «сильного» события | Lairgi 2026 (C-Unseen) |
| **Topic proportion × growth (STM)** | Замена keyword-частот на доли тем (ось X/Y) для сигналов | Park & Kim 2021 |
| **RAG для foresight** | LLM + retrieval поверх внешних баз = автопрофили технологий | Ellermann 2025 |

### 1.7 Сетевые (институциональные)

| Фича | Идея | Источник |
|---|---|---|
| **Institutional homophily** | Гомофилия (связи внутри группы GOV/HC/IND/NGO/RHE) в соавторстве при зарождении технологии | Rotolo 2025 (ERGMs) |
| **Recency-and-magnitude scoring** | Оценка «недавность × величина» для редких тем с ростом | Menning 2026 (WSM) |

### 1.9 Статистические / аномальные (пачка 2026-09-11)

| Фича | Идея | Источник |
|---|---|---|
| **σ-аномалия частоты (>4σ)** | Отклонение частоты термина от «спокойного» фона = ранний сигнал события; фон нормален при отсутствии возмущений | Mints 2024 |
| **Surprisingness (W-post/W-pre)** | Рост новостного объёма ПОСЛЕ события относительно следа ДО него — аналог нашего W3/W2 («всплеск») | Ueda 2026 (HorizonBench) |
| **Event coverage + lead time (бенчмарк)** | Доля будуще-значимых событий, покрытых вопросами кандидата, и насколько рано они подняты | Ueda 2026 (HorizonBench) |
| **Журнальная фрагментация** | Доля «одностатейных» журналов в поле ранней темы (154/191 у CF 2001-21) — индикатор неконсолидированности | Chichorro 2022 |
| **Консолидация площадок со временем** | Созревание темы: разброс журналов → концентрация (ср. нашу «унификацию термина» S2) | Chichorro 2022 (экстраполяция) |

### 1.10 Индексы рубежа технологий и multi-channel growth (Cosmos 1.0, пачка 2026-09-22)

| Фича | Идея | Источник |
|---|---|---|
| **Awareness Index (3yr/5yr slope)** | Скольжение просмотров Wikipedia-страницы технологии (2019–2023) — канал adoption без API-квот | Gong 2025 |
| **Единый паттерн «slope + growth index» × 3 канала** | Одна и та же метрика (3yr/5yr slope → индекс роста) по просмотрам Wikipedia, публикациям OpenAlex и патентам Google — унифицирует growth×adoption×conversion | Gong 2025 |
| **Age_of_Tech_Index + First_Pub_Year** | Возраст технологии по первому публикационному следу — кросс-чек нашего Novelty | Gong 2025 |
| **Generality_Index** | Широта охвата (универсальность технологии) — близко к патентной IPC-рекомбинации | Gong 2025 |
| **DeepTech_Index** | «Глубина» технологии (фундаментальность против прикладности) по Wikipedia-контенту | Gong 2025 |
| **Tech_Proximity (XGBoost tech vs non-tech)** | Классификатор «технология / не-технология» по эмбеддингу сущности — фильтр не-тех тем в выдаче | Gong 2025 (Tech Classifier) |
| **TFR (Crunchbase) + GS_Author_Counts** | Индустриальный след (темпы стартапов с привлечением капиталов) и академический охват (авторы Google Scholar) | Gong 2025 |

---

## 2. Гипотезы из литературы (которые будем проверять)

> Каждая гипотеза — утверждение ИЗ работы; мы проверяем его на наших кейсах.

### H1: Слабый сигнал = низкая частота + высокий рост
**Утверждение (Ebadi 2022, по Yoon 2012):** зарождающийся тренд — низкая базовая частота + высокая скорость роста.
**Проверка:** DoV/GrowthRate терминов 2018 → исход.
**✅ ПРОВЕРЕНО 2026-09-09 (9 кейсов) — H1 в лоб НЕ работает, «рост» буксует в 3 местах**
(см. `methodology/hypotheses/hypothesis_H1_check.md`):
- рост 15→18 ≥3× дают 4 кейса: flux_pump ✅, ni_coils ✅, но joint ❌ и aircraft ❌ — монетка;
- ibad ✅ (рост отрицательный, внедрён), snspd ✅ (к 2018 уже strong, не weak) — не ловятся ростом;
- **дефекты роста:** (1) не отличает «всплеск» от «каскада» (joint: W3/W2=0.58 vs flux_pump 1.94);
  (2) не отличает реальную работу от PR-хайпа (aircraft: рост есть, конверсии нет → conversion);
  (3) запаздывает/молчит при внедрении (ibad → adoption) и для зрелых strong (snspd).
- **Вывод:** GrowthRate — фича только в комбинации; добавить `growth_persistence` (W3/W2)
  + фильтры adoption/conversion из H23 + порог частоты (weak vs strong).
  В СП слабый сигнал = «малый объём + цитатный/инженерный якорь + тихий рост + конверсия позже»
  (jtwpa, snspd), а НЕ «низкая частота × рост» из H1.

### H2: Перегиб S-кривой отделяет раннюю стадию
**Утверждение (Daim 2006):** точка перегиба = середина роста; до неё — ранняя стадия.
**Проверка:** Fisher-Pry к данным кейсов; позиция 2018 vs перегиб.
**✅ ПРОВЕРЕНО 2026-09-09 (9 кейсов) — S-кривая даёт СТАДИЮ, но НЕ исход (6/9)**
(см. `methodology/hypotheses/hypothesis_H2_H3_check.md`):
- «в 2018 ДО перегиба ⇒ состоялся»: 6/9; промахи = те же 2 контр-примера (aircraft/joint — выглядят
  ранними, но хайп/всплеск → нужен conversion; ibad — после перегиба, но ВНЕДРЁН → нужен adoption);
- позиция перегиба: smes(2015)/rce(2016)/ibad(2013) — пройден; ni/jtwpa/snspd/flux_pump/aircraft/joint — 2023-29;
- **ограничение метода:** асимптота K и перегиб неизвестны в реальном времени (ретроспектива);
  у каскадных тем (snspd) одна логистика сглаживает; хвосты после 2018 дают ложный «ранний» перегиб.

### H3: Скорость S-кривой (b) предсказывает диффузию
**Утверждение (Daim 2006/2009):** крутая S-кривая = быстрая диффузия.
**Проверка:** b по публикациям кейсов.
**✅ ПРОВЕРЕНО 2026-09-09 (9 кейсов) — b слабо разделяет (медианы 0.172 vs 0.128, перекрытие)**
(см. `methodology/hypotheses/hypothesis_H2_H3_check.md`):
- ni_coils (0.284, 15 лет 10→90%) — быстрейший; joint (0.083, 53 года) — медленнейший;
- НО flux_pump ✅ (0.136) медленнее aircraft ❌ (0.141); smes ❌ (0.116) не мал → перекрытие;
- **вывод:** b — фоновая характеристика, не предиктор; в модель как слабая фича;
- Bass p/q (имитация) не проверяли — нет надёжных аналогов (урок: Li-ion неверный аналог для SMES).
- **итог блока:** S-кривая = 5-я проверка, сходящаяся к модели
  новизна×рост×влияние×persistence×adoption×conversion (добавляет фичу «стадия»).

### H4: Движение эмбеддингов предсказывает эволюцию темы
**Утверждение (Huang 2024):** геометрическое движение эмбеддингов предсказывает будущие темы (~50%).
**Проверка:** эмбеддинги тем по годам → предсказание новых подтем.

### H5: Частота обновления важнее числа документов
**Утверждение (BERTrend 2024):** популярность = f(документы, частота обновления); редкая+частая = слабый сигнал.
**Проверка:** метрика BERTrend по темам кейсов.

### H6: Фильтры искажают восприятие слабых сигналов
**Утверждение (Ilmola & Kuusi 2006):** цели и метод сканирования определяют, какие сигналы замечены.
**Проверка:** сравнение «что нашли» разными методами сканирования.

### H7: Рождение темы предсказуемо по сети
**Утверждение (Salatino 2018 AUGUR):** рождение новых тем предсказуемо по графу знаний.
**Проверка:** AUGUR-подход к появлению тем в корпусе.

### H8: Триплетные структуры — ранние индикаторы
**Утверждение (Wang 2026):** изменения триплетов в сетях предшествуют новым трендам.
**Проверка:** темпоральные сети → триплеты.

### H9: Патенты отражают завершённость системы (TESE)
**Утверждение (Ghane 2026):** полнота компонентов системы по патентам = стадия эволюции.
**Проверка:** TESE-анализ патентов кейсов.

### H10: Технологические индикаторы (emergence scoring)
**Утверждение (Garner 2017; Carley 2018):** комбинация novelty/growth/community/persistence = emergence score.
**Проверка:** EScore для терминов кейсов.
**✅ ПРОВЕРЕНО 2026-09-09 (9 кейсов) — EScore-произведение ЛУЧШИЙ одиночный метод (8/9)**
(см. `methodology/hypotheses/hypothesis_H10_check.md`):
- EScore = novelty×growth×persistence×impact (community заменён на impact — нет соавторной сети),
  данные только до 2018 (без leakage); порог ≥0.07;
- **8/9**: промах только ibad (0.037, но ✅ — внедрён) → нужен adoption;
- мультипликативность отсекает aircraft/joint (высокие novelty+growth, но слабое impact 0.13/0.09 →
  prod 0.074/0.057) — то, что не могли H1/H11/S-кривая; smes/rce корректно ❌ (impact≈0);
- **вывод:** EScore ≈ наше ядро (novelty×growth×persistence×impact); adoption/conversion — сверху
  (только ibad-тип ломает). **6 проверок (H23/H1/H18/H11/H2-3/H10) сходятся к модели:
  EScore × adoption × conversion.** Фича `escore_prod_2018` ДОБАВЛЕНА в features_table (51 кол.).

### H11: Emerging = радикальная новизна + рост + влиятельность
**Утверждение (Rotolo 2015):** emerging technology = радикальная новизна, относительно быстрый рост, заметное влияние.
**Проверка:** операционализация Rotolo-критериев на кейсах.
**✅ ПРОВЕРЕНО 2026-09-09 (9 кейсов) — Rotolo работает как позитивный гейт-фильтр, НО не различает adoption/conversion**
(см. `methodology/hypotheses/hypothesis_H11_check.md`):
- правило «новое (возраст<15) + растёт + влиятельно (impact>50)»: 7/9; промахи — те же 2 контр-примера,
  что H23/H1: **001_ibad** (старый 21 г., не растёт, но ВНЕДРЁН → ✅) и **008_aircraft** (нов, растёт,
  влиятелен, но PR-хайп → ❌); 007_jtwpa Rotolo корректно считает emerging (наше 🔶 = согласие);
- **Rotolo отсекает зрелое/мёртвое** (SMES: старое+не растёт+без ядра → ❌ корректно; rce: без влияния → ❌),
  но НЕ отличает «внедрён, публикации упали» (IBAD) от «умер» (SMES) → нужен adoption;
  и «реальный emerging» от PR-хайпа (aircraft — S3_birth 2017 = кластер вокруг E-Fan X, тема старая с 1990!)
  → нужен conversion + persistence;
- **Вывод:** Rotolo-атрибуты (новизна/рост/влияние) — НЕОБХОДИМЫЕ, но НЕ ДОСТАТОЧНЫЕ условия исхода.
  Rotolo про «emerging сейчас», мы про «состоялся к 2026» — для исхода нужны adoption/conversion.
  Это 4-я независимая проверка, сходящаяся к модели: новизна×рост×влияние×persistence×adoption×conversion.

### H12: Слабый сигнал = редкая тема + ускорение видимости
**Утверждение (Menning 2026):** weak signal = низкая частота + выше-среднее ускорение видимости во времени.
**Проверка:** micro-topic + recency/magnitude по корпусам кейсов.

### H13: Weak signal ≠ wild card ≠ тренд (различать)
**Утверждение (Popper 2025):** слабые сигналы, дикие карты и тренды — разные феномены; смешение искажает форсайт.
**Проверка:** классификация сигналов кейсов (weak vs wild card vs trend) → исход.

### H14: LLM-интерпретация повышает точность, не заменяя эксперта
**Утверждение (Menning 2026; Shaeva 2024):** LLM/AI даёт объяснимые ярлыки для weak signals; human-machine коллаборация эффективнее чистого ML.
**Проверка:** LLM-ярлыки vs ручная разметка на кейсах; explainable AI.

### H15: LLM-калибровка улучшает патентометрию (regime classification)
**Утверждение (Burmaoglu 2026):** rule-based классификаторы инновационных режимов дают много неклассифицируемых; LLM-семантическая калибровка решает это.
**Проверка:** классификация режимов по нашим патентным корпусам с LLM-калибровкой.

### H16: Институциональная гомофилия маркирует раннюю стадию технологии
**Утверждение (Rotolo 2025):** на ранней стадии коллаборации — внутри групп (GOV/IND), позже — HC/клиника.
**Проверка:** сеть соавторства по кейсам: кто с кем коллаборирует на ранней стадии.

---

## 2а. Дополнительные гипотезы (из новой пачки, 2026-09-07)

### H17: Weak signal = редкий + корроборированный во времени подграф (не термин)
**Утверждение (Lairgi 2026, C-Unseen):** слабый сигнал — семантически связный редкий подграф, чьё «напряжение» продолжается между снимками DTKG; keyword/topic-методы теряют реляционный слой.
**Проверка:** на наших кейсах — добавить слой сущность-связь (кто/что/когда) к частотным сигналам.

### H18: Операционная ценность = lead time (как рано пойман сигнал)
**Утверждение (Lairgi 2026):** детекция за 1 шаг до strong signal технически верна, но бесполезна; важна ранность.
**Проверка:** для кейсов — за сколько лет до 2026 сигнал был виден (у нас: сигнал 2018 → исход 2026, уже заложено).
**✅ ПРОВЕРЕНО 2026-09-09 (9 кейсов) — lead time сам по себе НЕ предиктор, ценность = корроборация**
(см. `methodology/hypotheses/hypothesis_H18_check.md`):
- ранность НЕ разделяет: SMES сигналил с 1969 (LT 57 лет) и НЕ состоялся; SNSPD с 2005 (LT 21) — состоялся;
  провальные LT 9-57 лет, успешные 10-22 — полное перекрытие;
- **что реально работает:** паттерны корроборации — (A) «ранний одиночный сигнал без подтверждения» =
  анти-сигнал (SMES pubs 1969 + 0 грантов/0 внедрения; aircraft: патентная активность в окно 2014-18
  ПАДАЛА 1-3/год — «гонка без патентов»); (B) «ранний корроборированный» (SNSPD: все базы сошлись,
  каскад; IBAD: патенты+adoption) = состоялся; (C) «поздний, но якорный» (JTWPA: счёт растёт поздно,
  но цитатный якорь Macklin 2015 = ранний сигнал качества);
- **⚠️ «число баз к 2018» НЕ разделяет** (joint=5 как flux_pump=5; ibad=4 как smes=4) — важно КАЧЕСТВО:
  какие базы (adoption у ibad vs grants=0 у smes), держится ли рост (joint W3/W2=0.58), conversion;
- **вывод:** lead time → в модель НЕ идёт; сервис должен показывать «когда сигнал стал НАДЁЖНЫМ»
  (корроборация ≥2 баз с удержанием). Сходится к модели H23/H1: класс + persistence + adoption + conversion.

### H19: Доля темы (не частота слова) — лучшая единица сигнала
**Утверждение (Park & Kim 2021):** keyword-карты (KEM/KIM) теряют сигналы; topic proportion из STM с ковариатой-год решает.
**Проверка:** доли BERTopic-тем по годам (уже сделано в PhysicA) → weak/strong классификация тем.

### H20: «0 в общей базе ≠ 0» — компонентные темы не видны на широких площадках
**Утверждение (наш вывод из PhysicA + Hladchenko 2026):** на широкой молодёжной конференции СП-компоненты (SNSPD/JTWPA) отсутствуют, хотя в мире живы; weak-signal темы «не видны» стандартными агрегатами.
**Проверка:** уже подтверждено анализом PhysicA (см. REPORT.md); усиливает наш принцип мульти-базы.

### H21: GenAI полезен через «аккомодацию» (перестройку процессов), не пассивное использование
**Утверждение (Park 2026 JIK):** эффект GenAI на инновации сильнее при когнитивной аккомодации; медиирует интеграцию знаний.
**Проверка:** дизайн нашей LLM-обёртки — давать объяснения/интерпретацию (sensemaking), не только вердикт.

### H22: Weak signals применимы в «регулируемых/консервативных» отраслях
**Утверждение (Piraintorn 2025; Roy 2026):** weak signals работают в страховании/госуправлении (не только tech); нужен коллективный sensemaking.
**Проверка:** аналогия с нашей СП (нишевая отрасль) — сигналы работают, если есть интерпретация.

---

## 2б. Ландшафт методов детекции weak signals (из новой пачки)

> Сводная картина эволюции методов — из обзоров C-Unseen (Lairgi 2026) и Hladchenko 2026.
> Ценность: обоснование нашего мульти-метода — каждый уровень теряет часть информации.

| Уровень метода | Единица анализа | Что теряет | Представители |
|---|---|---|---|
| **Keyword-частоты** | термин (слово) | контекст/смысл термина; сигналы-слова, не попавшие в KEM∩KIM, теряются | Yoon 2012 (DoV/DoD), KEM/KIM |
| **Topic modeling** | тема (распределение слов) | реляционную структуру МЕЖДУ сущностями темы | LDA, STM (Park&Kim 2021), BERTopic/BERTrend 2024 |
| **Graph-topology** | неразмеченный подграф | семантику (типы сущностей/связей) | BEAM (graphlets), co-occurrence графы |
| **TKG reasoning** | граф знаний | ориентирован на link prediction, нет механизма rarity | REGCN, GenTKG, LLM-DA |
| **DTKG + LLM (C-Unseen)** | размеченный редкий подграф + корроборация во времени | — (самый полный слой) | Lairgi 2026 |

**Вывод для нас:** слабый сигнал «живёт» на всех уровнях сразу; ни один метод не ловит его полностью.
Наш конвейер (S1-мульти-база: публикации+патенты+гранты; BERTopic-темы; цитатные кластеры) —
по сути «ансамбль уровней»; C-Unseen показывает недостающий уровень (сущность-связь-время).

---

## 2в. Таксономии сигналов у разных авторов (свести для нашей метки)

| Автор/работа | Классы сигналов | Примечание |
|---|---|---|
| Ansoff 1975 | weak vs strong | классика, бизнес |
| Ebadi 2022 / WISDOM (Hladchenko 2026) | **strong / weak / latent / NSWK** | 4 класса: latent (низкий объём+рост) = «спящие»; NSWK (высокий объём, нет роста) = «зрелые, не растущие» |
| Popper 2025 | weak signal ≠ wild card ≠ trend | разные феномены, не путать |
| Yoon 2012 / KEM-KIM | weak (низк.частота+рост) vs strong | по словам |
| Park&Kim 2021 (STM) | strong / weak / NSWK (+latent) | по долям тем |
| Lairgi 2026 (C-Unseen) | weak signal = редкий подграф + корроборация | структурное определение |
| Ueda 2026 (HorizonBench) | известные-известные / known-unknowns / **unknown-unknowns** (early question discovery) | ср. H13 (weak vs wild card): «вопросы о том, что станет значимым» — upstream от калибровки вероятностей |

**Вывод для ML-метки:** наша 3-уровневая метка «состоялся / в развитии / не состоялся» (по кейсам) —
это метка ИСХОДА. Таксономии выше — про класс СИГНАЛА в момент окна. Стоит сопоставить:
«в развитии» ≈ weak-signal, который корроборируется; «не состоялся» ≈ latent/NSWK, который не выстрелил;
«состоялся» ≈ weak → strong. Возможно, для features_table добавить колонку «класс сигнала в 2018 по WISDOM»
(weak/latent/NSWK/strong) как отдельную фичу-предиктор.

---

## 2г. Наблюдения из литературы, бьющие в наши кейсы

> Не «результаты проекта», а факты из прочитанного, которые стоит учесть при интерпретации кейсов.

1. **Накопители энергии: weak signals «выстреливают» (Park&Kim 2021).** В weak-signal темах ВИЭ —
   водород/суперконденсаторы/CAES (крупные накопители) с высоким ростом. → Прямая параллель с кейсом 005
   SMES: конкуренты (Li-ion BESS) выросли из слабого сигнала в доминанту; CAES/водород — соседние weak-сигналы
   той же ниши, которые тоже росли. Урок: для SMES в 2018 сигнал конкурента был уже strong, а не weak.
2. **Гео weak-signal тем: ЕС-14 сильны, Китай — внутренние цитаты (Hladchenko 2026).** В weak-signal топиках
   дронов ЕС-14 имел сильнейший citation impact; Китай доминировал объёмом за счёт domestic-цитирования.
   → Релевантно гео-картине JTWPA (кейс 007: Европа доминирует DE/IT/FR, Китай почти отсутствует) и SNSPD
   (двухполюсник US/CN). Паттерн «ЕС ведёт в emerging, Китай догоняет объёмом» повторяется.
3. **Residual -1 кластер BERTopic — не дефект, а «широкий методологический слой» (Hladchenko 2026).**
   У дронов -1 тема = 47% корпуса (control/unmanned/aerial…), у PhysicA = 32%. Это общий технический слой
   (методы, инженерия), HDBSCAN его не разбивает. → Не считать шум «потерей»; учитывать как «фон».
4. **Пример эволюции weak→strong сигнала (C-Unseen, OpenAI/DARPA).** Кейс «снятие бана ChatGPT в США»:
   отдельные факты 2023 → корроборация на Davos 2024 → strong signal (контракт DoD $200M) 2025.
   → Иллюстрация нашего S1: сигнал реален, когда несколько баз/событий корроборируют его во времени.
5. **Weak signals требуют sensemaking (Piraintorn 2025; Roy 2026).** В регулируемых отраслях ценность сигнала
   проявляется через коллективную интерпретацию, не через «голую детекцию». → Наш сервис должен выдавать
   интерпретацию (мотивация+кейс+источник), а не просто «сигнал/не сигнал».
6. **Roadmapping ≠ детекция (Battistella 2025; Laplante 2024).** Roadmap — организационный инструмент
   (CSF, Delphi); не путать с автоматической детекцией emerging. → Для калибровки роадмапов (кейс 007
   roadmap_signal) помнить: роадмап — это «что решили эксперты», а не «что показали данные».
7. **Weak→strong переход — редкое событие (Ebadi 2026, AAES).** Из 80 тем подводных сенсоров — 6 слабых
   сигналов (подтверждены экспертами), до «сильного» доходит ОДНА (deep learning for underwater imaging).
   → Калибровка ожиданий: кандидатов много, конверсия единицы %; наш Этап 2 (верификация) необходим.
8. **«DL-волна» прокатывается по всем доменам (Ebadi 2026).** Единственный weak→strong — deep learning →
   при цензах по СП-кейсам учитывать DL-примесь в корпусах (проверять термин-фильтрами, как в цензе).
9. **Корпоративный форсайт: поле фрагментировано (Chichorro 2022).** 433 работы в 191 журнале, 154 журнала
   — по одной статье; 10 топ-журналов держат основную массу. → Для ранних тем разброс площадок — норма;
   «консолидация площадок» потенциально = маркер созревания (проверить на наших кейсах: JTWPA → журналы,
   SNSPD → конференции SNF).
10. **LLM-as-judge не заменяет эксперта (SCI-IDEA 2026).** Автоматические оценки качества идей завышают
    3-4/10 и не коррелируют с человеком (r≈0.02–0.17). → Для нашей валидации: метка исхода 2026 — только
    с участием автора; LLM может давать ранжирование, не «истину».
11. **Информационные аномалии предшествуют событиям (Mints 2024).** Частоты ключевых слов в СМИ растут
    за месяцы до COVID-2020/войны-2022 (>4σ). → Методологическое подтверждение нашего «всплеска» как
    аномалии, а не тренда: всплеск ≠ каскад (правило W3/W2<1 → «всплеск» → ❌).
12. **Открытых БД достаточно для фронтиров (Turgel & Chernova 2024).** OpenAlex/Lens/Dimensions заменяют
    Scopus/WoS для определения фронтиров и исследований; НО на стадии «оценки научных результатов государством»
    альтернативы нет → нам: стек открытых баз оправдан, честно маркировать ограничения в статье.

---

## 2д. Бенчмарки и золотые стандарты

- **C-Unseen (Lairgi 2026): первый формальный бенчмарк weak signal detection** — Wiki-OpenAI
  (773 атомарных факта из истории Wikipedia OpenAI 2015–2025, 11 снимков, 5 strong-сигналов,
   роли background/weak_signal/corroboration/strong_signal; анонимизированный вариант Wiki-OpenAI-Anon).
  Базлайны: Yoon, BERTrend, BEAM. → Внешний бенчмарк для сравнения методов детекции.
- **Метрика lead time** — насколько рано сигнал пойман до strong signal (операционная ценность;
  детекция за шаг до события «технически верна, но бесполезна»). → Прямо переносится на наши ретро-кейсы:
  «за сколько лет до 2026 сигнал был виден».
- **Наш «золотой стандарт»** — кейсы с меткой исхода 2026 (features_table). Аналогия: у нас роль
  strong_signal играет «состоялся к 2026», роль weak_signal — «сигнал 2018». Можно разметить кейсы
  в формате Wiki-OpenAI (background/weak/corroboration/strong по годам).
- **HorizonBench (Ueda 2026): новый бенчмарк «early question discovery»** — 445 геополитических событий;
  агент по докутовым новостям генерирует форсайт-вопросы; метрики: event-level coverage, efficiency,
  lead time, surprisingness (W-post/W-pre). Факт: фронтир-LLM ≈ low-single-digit %% покрытия.
  → Для сервиса: метрика «доля состоявшихся трендов среди топ-N кандидатов» — аналог coverage;
  surprisingness ≈ наш W3/W2 (всплеск).
- **ET100 (Gong 2025): ручной золотой набор из 100 emerging technologies** внутри открытого датасета
  ET23k (23 544 сущности, кластеры TC7/TC3, флаг ET100_Flag, индексы по 3 каналам). → Внешний валидатор
  Этапа 1: пересечение наших тем OpenAlex/LaBSE с ET100 (точность) и с рубежом ET23k (полнота);
  данные: Figshare 10.6084/m9.figshare.28268561, клон `results/implementation_examples/repos/Cosmos_1.0`.

---

## 2е. Инструменты / код (обновление)

| Инструмент | Что даёт | Где | Статус |
|---|---|---|---|
| **C-Unseen (Lairgi 2026)** | LLM+DTKG детекция weak signals, код+промпты+датасет | github.com/AuvaLab/itext2kg (962★) | ✅ **клонирован** (repos/itext2kg, 2026-09-07), Apache 2.0 |
| **STM (R-пакет `stm`)** | темы с ковариатами (год) + доверительные интервалы; для малых корпусов строже BERTopic | CRAN | рассмотреть для малых кейсов |
| **OpenAlex MULTIOBS (BigQuery)** | гео-анализ, аффилиации, weak/strong темы (Hladchenko) | OpenAlex | источник для гео-разрезов |
| **WISDOM (Ebadi)** | фреймворк классификации strong/weak/latent/NSWK | клон ebadi-weak-signal | уже в repos/ |
| **SciAgents (lamm-mit)** | концепт-граф + мультиагентный поиск связей | github.com/lamm-mit/SciAgentsDiscovery, GraphReasoning | ✅ (2026-09-11, из PDF) |
| **Awesome-Agent-Scientists** | каталог agentic-science методов + кода (включая SciAgents/SCI-IDEA-класс) | github.com/AgenticScience/Awesome-Agent-Scientists | справочник будущих методов |
| **Cosmos 1.0 (Gong 2025)** | датасет ET23k × 149 кол. (индексы×3 канала, кластеры, ET100_Flag, Wikipedia2Vec 100d) + ноутбуки сбора индексов + Streamlit-обозреватель (cosmos_app.py) | github.com/xian-gong-elaine/Cosmos_1.0 (данные через Git LFS) | ✅ **клонирован** (2026-09-22, `results/implementation_examples/repos/Cosmos_1.0`; parquet 153 МБ скачан) |
| **TRI / PatentPaperPairs (McCarthy 2026)** | датасет patent-paper пар (~20k) + пайплайн SPECTER2+XGBoost «патентной близости» | github.com/EmmaScharfmann/PatentPaperPairs | репо открыто, не клонирован |

---

## 2ж. Ограничения данных (из литературы, для нашей методологии)

- **~50% аффилиаций unknown в OpenAlex** в weak-signal темах к 2025 (Hladchenko 2026) → гео-анализ
  emerging-тем по OpenAlex ненадёжен без ROR-регистров. Учесть при гео-разрезах наших кейсов.
- **BERTopic на мультиязычном корпусе кластеризует по ЯЗЫКУ, не по теме** (Hladchenko 2026, проверено
  на дронах) → мы в PhysicA брали multilingual-MiniLM — верное решение; для новых корпусов помнить.
- **Наукометрические паттерны цитирования искажаются domestic-концентрацией** (Китай) — «citation
  advantage» ≠ «глобальная интеграция» (Hladchenko 2026). При сравнении стран в кейсах различать.

### H23: Класс сигнала в год окна (WISDOM: weak/latent/NSWK/strong) — предиктор исхода
**Утверждение (Ebadi 2022; Hladchenko 2026; Park&Kim 2021):** темы/технологии делятся на 4 класса по
«доля × рост» (strong/weak/latent/NSWK); класс в момент окна (2018) может предсказывать исход.
**Проверка:** для каждого кейса определить класс сигнала в 2018 (weak — малый объём+рост; latent — малый
объём+нет роста; NSWK — большой объём+нет роста) → сопоставить с меткой исхода 2026. Гипотеза:
weak-класс в 2018 → чаще «состоялся/в развитии»; latent/NSWK → «не состоялся».
**✅ ПРОВЕРЕНО 2026-09-08 (9 кейсов): 7/9 подтверждают, 2 КОНТР-ПРИМЕРА**
(см. `methodology/hypotheses/hypothesis_H23_check.md`):
- **001_ibad (NSWK, но состоялся)** — «не растёт, потому что ВНЕДРЁН» (производство есть) ≠ SMES
  («не растёт, потому что УМЕР»). Различающий фильтр: стадия внедрения (adoption).
- **008_aircraft (weak, но не состоялся)** — «растёт, потому что PR-ХАЙП» (гонка без конверсии) ≠
  SNSPD («растёт, потому что реальная работа»). Различающий фильтр: конверсия в патенты-ТНК/рынок
  (conversion).
**Вывод:** класс WISDOM — полезная фича, НЕ достаточная. Модель = класс + adoption-фильтр +
conversion-фильтр. Подтверждает количественно уроки SMES и 008.

---

## 2и. Дополнительные гипотезы (из пачки 2026-09-11, статус: НЕ ПРОВЕРЕНЫ)

### H24: Weak→strong переход — редкое событие; валидация экспертами обязательна
**Утверждение (Ebadi 2026, AAES underwater):** из 80 тем лишь 6 — слабые сигналы (подтверждены экспертами),
до сильного доходит ОДНА (deep learning for underwater imaging). **Проверка:** на наших кейсах — доля
слабых сигналов 2018, ставших сильными к 2026 (калибровка ожиданий Этапа 1: конверсия единицы % —
норма, «шум» кандидатов не дефект).

### H25: σ-инновационность (центральность × всплеск цитирований) выделяет «революционные» работы
**Утверждение (Chichorro 2022, по Chen 2010):** междуцентральность × burst цитат (>1.5) маркирует
работы с потенциалом оригинальности/влияния. **Проверка:** на якорях кейсов (Macklin 2015, van der Laan 2013…)
— совпадает ли σ-высокая работа с нашим цитатным якорем (impact_n ≈ 1)? Может усилить фичу impact.

### H26: Аномалии частот (>4σ от «спокойного» фона) предшествуют событиям
**Утверждение (Mints 2024):** без возмущений частоты терминов ~нормальны; превышение порога ~4σ —
ранний сигнал (COVID/война за месяцы). **Проверка:** на наших рядах — срабатывает ли порог 4σ для
«всплесков» (ср. joint W3/W2=0.58) и отличает ли он всплеск от каскада. Внимание: у Mints фон — СМИ,
у нас — публикации (менее шумные); порог может быть ниже.

### H27: «Early question discovery» — отдельный бутылочный горлышек AI-форсайта
**Утверждение (Ueda 2026, HorizonBench):** фронтир-LLM при фиксированном бюджете находят лишь
low-single-digit %% будуще-значимых событий (445 событий); GPT-5.5 — сильнее, но далёк от полного.
**Проверка (для продукта):** генерация «вопросов-кандидатов» LLM — плохой вход для сервиса; наш
термино-центричный скрининг по мульти-базе recall-выше. Бенчмаркировать против HorizonBench нельзя
напрямую (разные объекты — события vs темы), но вести метрику «доля состоявшихся среди топ-N кандидатов».

### H28: Концепт-граф + LLM-рассуждение выявляют скрытые междоменные связи
**Утверждение (SciAgents 2025):** граф знаний + набор LLM-агентов находят связи, «ранее считавшиеся
неродственными» (демо: биокомпозит). **Проверка:** аналог нашего S3 «кластера из ниоткуда» — даёт ли
графовый слой кандидатов сверх цитатного (пересечения корпусов, «мосты»)? Пилот: фреймворк на нашем
корпусе конкурентов (010) — стоят ли агенты затрат vs простая корреляция.

### H29: Автоматическая LLM-оценка не коррелирует с экспертами (для меток — только человек)
**Утверждение (SCI-IDEA 2026):** LLM-as-judge завышает 3-4/10, r≈0.02–0.17 с экспертами (p>0.05);
домен — качество научных идей. **Проверка:** наши метки исхода 2026 размечает автор; LLM может
ранжировать кандидатов, но не ставить «истину». Защита от «автоматической экономии» в валидации.

### H30: Фаза форсайта определяет выбор методов (3-фазная схема)
**Утверждение (Gibson 2018, по Horton 1999):** pre-foresight → foresight → post-foresight; для каждой фазы
— свой набор методов; единого лучшего нет (5 критериев выбора). **Проверка/применение:** наш пайплайн =
pre-foresight (скрининг Этапа 1) + foresight (верификация Этапа 2); позиционировать в разделе related work;
на кейсах не тестируется (рамка, не предиктор).

### H31: Уровни зрелости agentic-автоматизации — рамка для сервиса и будущих методов
**Утверждение (Wei 2025):** AI в науке эволюционирует: оракул → ассистент → … → полная агентность;
5 ключевых способностей (гипотезы, планирование, исполнение, анализ, рефлексия). **Проверка/применение:**
позиционирование нашего сервиса (уровень «ассистент+калибратор»); каталог Awesome-Agent-Scientists —
источник будущих методов (ср. с wishlist TRIZ).

## 2к. Дополнительные гипотезы (из ручной пачки 2026-09-14, статус: НЕ ПРОВЕРЕНЫ)

### H32: Методология области сдвигается от co-occurrence к семантике по мере созревания (Kastrin)
**Утверждение (Kastrin-Hristovski 2020, LBD):** в области literature-based discovery магистральный подход
сместился от базовых co-occurrence к семантическим методам (рубеж 2000-х) и к сетевым идеям (последнее
десятилетие); фазы роста: incubation → developing → mature (закон Прайса, R²=0.65).
**Проверка на кейсах:** это ВНЕШНИЙ позитивный контроль для нашей S2-гипотезы (сдвиг «открытие →
инжиниринг»). У нас на СП S2 не сработал как ранний детектор (8/8 не показали сдвига, hypothesis_S2_check),
но Kastrin показывает, что в LBD сдвиг co-occurrence→semantic РЕАЛЕН. Вопрос: работает ли он в материаловедении?
План: прогнать сдвиг лексики co-occurrence→semantic (terms: co-occurrence, association rule, semantic,
embedding) по нашему корпусу (SRF/Nb3Sn) по периодам — проверить, повторяется ли паттерн Kastrin.
**Связь:** H4 (эмбеддинги), S2-план; подтверждает, что «сдвиг методологии» — это признак созревания
области, но НЕ ранний сигнал.

### H33: Индикаторы — boundary objects: смысл метрики задаётся практикой, а не формулой (Leydesdorff)
**Утверждение (Leydesdorff-Wouters-Bornmann 2016):** библиометрические индикаторы (JIF, h-index) —
социально конструируемые артефакты; 4 стейкхолдера с конфликтующими интересами; простые индикаторы
используются, тонкие — нет (непрозрачность).
**Проверка/применение:** не тест на кейсах, а методологическая рамка для защиты: (1) наше правило
«абсолютная точность ничего не значит» (METRICS-подход Медведева) получает теоретическое обоснование;
(2) предупреждение: наукометрическая экспертиза будет смотреть на то, КАК метрика используется
(нормировка, бэктест, честность ограничений), а не на её формулу. **Использовать** в README/METHODOLOGY
как обоснование честной подачи метрик.

### H34: «Раннее обнаружение» в LBD — drug repurposing = наш фарма-слой (Kastrin)
**Утверждение (Kastrin 2020):** LBD применяется в биомедицине для предсказания побочных эффектов и
drug repurposing; фронтир — deep learning и XAI.
**Связь с нашим проектом:** наш фарма-слой (pharma_calibration, 10 направлений) по сути — LBD-подход
на стороне «исхода» (что стало блокбастером); Kastrin даёт наукометрическую рамку (409 док., 3 фазы,
со-авторская фрагментация) для сравнения. **Применение:** в разделе related work показать, что наша
фарма-валидация — это LBD-методология, проверенная на 10 направлениях; преимущество — у нас исход
(одобрения FDA/EMA), а не только латентные связи. **Проверка:** сравнить фазы LBD (по Kastrin) с фазами
наших фарма-кейсов (CAR-T/GLP-1) — совпадает ли «развитие → зрелость».

### Замечание: Garner 2017 (JNIS) и Chang 2022 — гипотез НЕ добавляют
- **Garner-Hirsch-Albuquerque-Fargen 2017 (JNIS)** — медицинский обзор библиометрии (h-index, JIF,
Eigenfactor); релевантность 2/5. ⚠️ Это НЕ тот Garner, что в EScore (там Garner-Carley-Porter-Newman
PICMET 2017, уже есть в `literature/(2017) !!!`). Совпадение фамилии — не путать.
- **Chang-Garner-Basner-Weinberg-Owen-Smith 2022 (HDSR)** — linked data mosaic для science-policy;
релевантность 3/5: теоретическая рамка «данные как стратегический актив» для нашего мульти-базового
подхода (S1), но метода детекции не содержит.

## 2л. Каноны/бейзлайны (пачка 2026-09-14, wishlist закрыт) — гипотезы H35–H40

### H35: Бurst-структура (всплески поверх медленного фона) — форма «каскада сигналов» (Kleinberg 2002)
**Утверждение (Kleinberg 2002):** активность темы описывается иерархией всплесков: медленные длинные
всплески (фоновый рост) с вложенными острыми пиками; burst = аномальное ускорение поверх базовой
скорости. **Связь с нами:** наш каскад сигналов (конференция→грант→публикация→патент→рынок) и фичи
W2/W3 (аномалия частот) — операционализация Kleinberg. **Проверка:** на кейсе 011 сравнить профили
всплесков разных баз (публикации vs конференции) — есть ли «острые пики» на ранних базах раньше, чем на
поздних. **Прямой аналог:** Chen 2006 (CiteSpace) адаптирует burst для research-front.

### H36: EScore-наследники дают «целостный» взгляд, но не операциональны (Ranaei 2019)
**Утверждение (Ranaei-Suominen-Porter-Carley 2019):** три воспроизводимых подхода к technological
emergence — term counting (операционален, детален), EScore (целостен: частота×сообщество, но сложен),
LDA (стратегичен, тематичен). Методы дают РАЗЛИЧАЮЩИЕСЯ перспективы. **Проверка/применение:** Ranaei
2019 = кандидат в 5-й бейзлайн (рядом с EScore/Wang/co-word/EP Медведева EXP-14); сравнить наш скрининг
с EScore на одних кейсах. Аргумент для защиты: «универсального индикатора нет — важно пересечение баз»
(поддержка H33/boundary objects).

### H37: Патентная «новизна» искажена классификациями — distinction комбинация/origination (Strumsky-Lobo 2015)
**Утверждение (Strumsky-Lobo 2015):** новизна = комбинация новых и существующих кодов (combination) +
редкие случаи появления с немногими предками (origination); но классификации пересматриваются, поэтому
«новое» может быть переклассификацией старого. **Проверка:** в нашей патентной фиче (S1b, Lens/GP)
различать combination vs origination; предостережение для кейса 011 (кит. патентные классы).

### H38: Ранняя стадия emerging предсказуема по библиометрическим признакам, но с шумом (Mund-Neuhäusler 2015)
**Утверждение (Mund-Neuhäusler 2015):** на ранней стадии темы её библиометрические характеристики
(рост, цитируемость, разнообразие сообщества, новизна терминологии) частично предсказывают «взлёт»;
ни один признак не идеален. **Проверка:** сравнение «взлетевших vs невзлетевших» = наш backtest-дизайн;
критерии Mund — кандидаты в дополнительные пороги Этапа 1 (новизна×рост×влияние).

### H39: Смешанные индикаторы лучше одиночных — но только внутри библиометрии (Guo-Börner 2011; Cozzens 2010)
**Утверждение (Guo-Weingart-Börner 2011):** комбинация структурных/динамических индикаторов точнее
описывает и предсказывает emerging areas. (Cozzens 2010): один индикатор недостаточен, нужна
мульти-индикаторность + экспертная компонента. **Связь с нами:** наше пересечение РАЗНЫХ баз
(гранты/конференции/патенты/рынок) — расширение идеи «mixed indicators» за пределы библиометрии;
это наша новизна (см. wishlist §D: почти нет работ с грантами/конференциями отдельно).

### H40: Пан-доменная детекция по «паттерну предков» — прецедент нашего Этапа 1 (Jung-Segev 2022)
**Утверждение (Jung-Segev 2022):** общий паттерн в «предках» тем предсказывает рождение темы через
домены; модель-предиктор обучается на одних доменах и переносится на другие. **Связь с нами:** наш
скрининг кандидатов по всей базе (Этап 1) — пан-доменный по духу; Jung-Segev — научный прецедент,
который нужно цитировать и с которым сравнивать. Также H35 (burst) и H40 смыкаются: «предки» = всплески
связей до рождения темы.

### Замечание к пачке: Ansoff 1975, Callon 1991, Swanson 1986, van Raan 1991 — гипотез НЕ добавляют
- **Ansoff 1975** — вводит понятие «weak signal» и шкалу зрелости сигнала = **теоретическая рамка** нашего
  каскада (разные базы = разные стадии созревания одного сигнала). Не предиктор.
- **Callon 1991** — первоисточник co-word-бейзлайна (индекс эквивалентности e=c²/(c_i·c_j), стратегическая
  диаграмма центральность×плотность). Нужен для реализации co-word-бейзлайна, не новая гипотеза.
- **Swanson 1986** — основа LBD = методологический фундамент S3 и фарма-слоя (H34 уже есть).
- **van Raan 1991** — ранний прецедент early-warning по материалам; редкий пример грант/конференция-сигнала
  (поддержка новизны нашего подхода), не новая гипотеза.
- **Shehabuddeen 2005** (TI), **VOSviewer 2010**, **Chen 2006** (CiteSpace), **Guo-SAO 2016** — инструменты/рамки,
  поддерживают фичи (см. 3.1), новых гипотез не несут.

---

## 2м. Дополнительные гипотезы (пачка 2026-09-22: Cosmos 1.0 + TRI, статус: НЕ ПРОВЕРЕНЫ)

### H41: Bottom-up карта (эмбеддинги сущностей → кластеры) воспроизводит ручной список emerging технологий
**Утверждение (Gong 2025):** кластеризация Wikipedia2Vec-эмбеддингов 23 544 технологически-смежных сущностей (TC7/TC3) в сочетании с ручной верификацией ET100 даёт согласованную карту emerging technology frontier — зарождение видно в сущностном пространстве, не только в публикационной динамике.
**Проверка:** пересечение наших тем OpenAlex/LaBSE с ET100_Flag и кластерами ET23k (precision/recall нашего скрининга против их ручного золота).

### H42: Три канала (awareness × publication × patent) с единым паттерном slope+growth index различают стадии зрелости
**Утверждение (Gong 2025):** индексы 3yr/5yr slope по просмотрам Wikipedia, публикациям OpenAlex и патентам Google + Generality/DeepTech/Age-of-Tech структурируют рубеж технологий (8 категорий индексов); Industrial Signals (TFR+патенты) предшествуют коммерциализации.
**Проверка:** на наших кейсах год окна → 2026: зарождающиеся должны опережать по growth в «ранних» каналах (awareness/publication), состоявшиеся — в поздних (patent/adoption); при необходимости добавить RCA (OECD) как гео-фичу.

### H43: «Язык изобретения» различим по title+abstract до появления патентов
**Утверждение (McCarthy 2026):** статьи, сопряжённые с патентами, лингвистически отличимы от контроля тех же журналов (ROC-AUC 0.774 на SPECTER2+XGBoost); TRI коррелирует с индустриальной коллаборацией (r = 0.364, p < 0.001).
**Проверка:** на кейсах — коррелирует ли TRI-подобная фича (патентная близость текста темы) с исходом 2026 (conversion-канал Этапа 2); «язык изобретения» как лексический компонент S2.

---

## 3. Приоритеты

### 3.1 Фичи (по реализуемости)

| Приоритет | Фича | Источник |
|---|---|---|
| Высокий | GrowthRate, Novelty, DoV/DoD | Ebadi 2022 |
| Высокий | Fisher-Pry b, inflection | Daim 2006 |
| Высокий | Bass p/q | Daim 2009 |
| Средний | Topic embedding motion | Huang 2024 |
| Средний | Noise/weak/strong | BERTrend 2024 |
| Средний | Emergence score (EScore) | Garner 2017, Carley 2018 |
| Средний | Recency-and-magnitude (WSM) | Menning 2026 |
| Средний | LLM-калибровка патентометрии | Burmaoglu 2026 |
| Средний | Institutional homophily (ERGMs) | Rotolo 2025 |
| Низкий | Triplets | Wang 2026 |
| Низкий | TESE completeness | Ghane 2026 |
| **Средний** | σ-инновационность (burst×betweenness), журнальная фрагментация | Chichorro 2022 |
| **Средний** | Surprisingness / всплеск-метрика (ср. W3/W2) | Ueda 2026 (HorizonBench) |
| Средний | Facets-структуризация текстов (obj/method/eval/future-work) | SCI-IDEA 2026 |
| Средний | Concept-graph связность (пилот S3) | SciAgents 2025 |
| **Высокий** | **Burst-иерархия (Kleinberg-фича: W2/W3 через автомат состояний)** | Kleinberg 2002 |
| **Средний** | **SAO-морфология (структурная семантика направления)** | Guo 2016 |
| **Средний** | **Смешанный индикатор (взвеш. комб. growth+novelty+impact)** | Guo-Börner 2011, Cozzens 2010 |
| **Средний** | **Патентная комбинация/origination (разделение новизны)** | Strumsky-Lobo 2015 |
| **Средний** | **Ранняя-стадия-скоринг (критерии Mund)** | Mund-Neuhäusler 2015 |
| **Низкий** | **Индекс эквивалентности co-word e=c²/(c_i·c_j)** | Callon 1991 |

### 3.2 Гипотезы (по скорости проверки)

| Приоритет | Гипотеза | Источник |
|---|---|---|
| Высокий | H1 (низк. частота + рост) | Ebadi 2022 |
| Высокий | H2, H3 (S-кривая) | Daim 2006/2009 |
| Высокий | H10 (EScore) | Garner 2017 |
| Средний | H4 (эмбеддинги) | Huang 2024 |
| Средний | H5 (частота обновления) | BERTrend 2024 |
| Средний | H11 (Rotolo-критерии) | Rotolo 2015 |
| Средний | H12 (редкая тема + ускорение) | Menning 2026 |
| Средний | H14 (LLM-интерпретация) | Menning 2026, Shaeva 2024 |
| Средний | H16 (институц. гомофилия) | Rotolo 2025 |
| Низкий | H6 (фильтры), H7 (AUGUR), H8 (триплеты), H9 (TESE) | Ilmola/Salatino/Wang/Ghane |
| Низкий | H13 (weak vs wild card), H15 (LLM-патентометрия) | Popper 2025, Burmaoglu 2026 |
| Новые | H17 (редкий подграф), H18 (lead time) | Lairgi 2026 (**код: AuvaLab/itext2kg, клонирован**) |
| Новые | H19 (доля темы), H20 (0 в базе) | Park&Kim 2021, PhysicA-анализ |
| Новые | H21 (аккомодация GenAI), H22 (регулируемые отрасли) | Park 2026, Piraintorn 2025 |
| Новые | H23 (4-классовая метка WISDOM как предиктор) | Ebadi/WISDOM, Hladchenko 2026 |
| Новые | **H24 (weak→strong редок), H25 (σ-иноннов.), H26 (4σ порог)** | Ebadi 2026, Chichorro 2022, Mints 2024 |
| Новые | **H27 (question discovery), H28 (граф-связи), H29 (LLM-judge bias)** | Ueda 2026, SciAgents 2025, SCI-IDEA 2026 |
| Новые | H30 (3-фазы), H31 (agentic maturity) — рамки, не тесты | Gibson 2018, Wei 2025 |
| Новые | **H32 (co-occurrence→semantic сдвиг, внешний контроль S2)**, **H33 (boundary objects)**, **H34 (LBD=наш фарма-слой)** | Kastrin 2020, Leydesdorff-Wouters-Bornmann 2016 |
| Новые | **H35 (burst-иерархия=каскад сигналов)**, **H36 (EScore-наследник, 5-й бейзлайн)**, **H37 (патентная novelty искажена)** | Kleinberg 2002, Ranaei 2019, Strumsky-Lobo 2015 |
| Новые | **H38 (ранняя стадия предсказуема с шумом)**, **H39 (смешанные индикаторы)**, **H40 (пан-домен по предкам)** | Mund 2015, Guo-Börner/Cozzens 2010-11, Jung-Segev 2022 |

### 3.3 Фичи (по реализуемости, дополнение из новой пачки)

| Приоритет | Фича | Источник |
|---|---|---|
| **Высокий** | Rare subgraph + corroboration (C-Unseen) — **есть код** | Lairgi 2026 |
| Средний | Lead time до strong signal (метрика) | Lairgi 2026 |
| Средний | Topic proportion × growth (STM-стиль) | Park&Kim 2021 |
| Средний | Класс сигнала WISDOM (weak/latent/NSWK/strong) в features_table | Ebadi, Hladchenko 2026 |
| Низкий | RAG-профили технологий (продукт) | Ellermann 2025 |
| **Высокий** | **EScore-наследник как 5-й бейзлайн (term count / EScore / LDA)** | Ranaei 2019 |
| **Средний** | **Burst-based фича (всплески поверх фона)** | Kleinberg 2002, Chen 2006 |
| **Средний** | **co-word индекс эквивалентности (бейзлайн)** | Callon 1991 |
| **Низкий** | **SAO-структуры (если потребуется для S2)** | Guo 2016 |

### 3.4 Приоритеты (дополнение пачки 2026-09-22)

| Приоритет | Действие | Источник |
|---|---|---|
| **Высокий** | Сверить ET100_Flag (100 ручных emerging tech) с нашими SC-темами OpenAlex/LaBSE — внешняя валидация Этапа 1 | Gong 2025 |
| **Высокий** | Унифицировать фичи по паттерну «3yr/5yr slope + growth index» × 3 канала (pubs/patents/awareness) | Gong 2025 |
| **Средний** | Tech_Proximity-классификатор (tech vs non-tech) как фильтр не-тем в выдаче | Gong 2025 |
| **Средний** | TRI-фича патентной близости текста для канала conversion (Этап 2) | McCarthy 2026 |
| **Низкий** | Wikipedia pageviews как внешний adoption-канал (Wikimedia API, без квот) | Gong 2025 |

---

## 4. Заметки
- Проверка гипотез — на калибровочных кейсах (метка «состоялся к 2026 / нет»), горизонт сигнала 2018.
- Полные библиографии и детали методов — в выжимках (колонка «Где выжимка»).
