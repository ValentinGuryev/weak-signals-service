# Wishlist — baselines (литература для сравнения по методологии)

> **Создан:** 2026-09-14. **Цель:** дособрать канонические статьи, которые мы **пропустили** при
> первичном сборе, но которые использует Медведев (EXP-14) и/или которые покрывают методы,
> где у нас есть зазор (грантовые/конференционные сигналы отдельно; источники co-word/EScore;
> LBD; burst detection). Формат: `literature/TRIZ/` §4.2a (статусы 📥/⛔/🔶; выжимки по §4.3 после скачивания).
>
> **Источник отбора:** перекрёстный анализ (что цитируют наши бейзлайны) + OpenAlex/Crossref
> (2026-09-14, ~40 запросов разведки). Релевантность: `!!!`=5/5, `!!`=4/5, `!`=3/5.
>
> **СТАТУС (обновлено 2026-09-14): все 16 кандидатов СКАЧАНЫ и обработаны по §4.3**
> (переименованы по протоколу + выжимки .md в `baselines/`). Осталось ниже только для истории
> выбора; статусы всех = ✅ скачано. Обзор добавленного — см. конец файла.

## A. Классика, которой у нас НЕТ (каноны, закрывающие зазоры) — высокий приоритет

### A1. Callon, Courtial, Laville 1991 — Co-word analysis (первоисточник co-word-бейзлайна)
- **DOI:** 10.1007/bf02019280 · **Релевантность:** !!! 5/5
- **Зачем:** Медведев (EXP-14) ссылается на co-word «Callon 1991 / Leydesdorff 2016». Саму Callon 1991
  у нас НЕТ (Leydesdorff-Nerghes 2016 есть). Первоисточник нужен, чтобы корректно реализовать/цитировать
  co-word baseline и индекс эквивалентности e(i,j)=c²/(c_i·c_j).
- **Статус:** ✅ скачано (2026-09-14) → `(1991) !!! Callon, Courtial, Laville — Co-Word Analysis (Polymer Chemistry).pdf/md`

### A2. Ansoff 1975 — Managing Strategic Surprise by Response to Weak Signals
- **DOI:** 10.2307/41164635 · **Релевантность:** !!! 5/5 (751 цит.)
- **Зачем:** **каноническое определение «weak signals»** — с чего началась вся область. У нас есть
  применение (Ilmola, Ebadi), но не первоисточник. Для раздела related work и защиты: «weak signal
  — термин введён Ансоффом (1975)».
- **Статус:** ✅ скачано (2026-09-14) → `(1975) !!! Ansoff — Managing Strategic Surprise by Response to Weak Signals.pdf/md`

### A3. Kleinberg 2002 — Burst and Hierarchical Structure in Streams
- **DOI:** 10.1145/775047.775061 · **Релевантность:** !!! 5/5 (856 цит.)
- **Зачем:** **burst detection** — формализация «всплеска» (наше W3/W2, Ueda surprisingness
  = потомки Kleinberg). Это недостающий алгоритмический первоисточник для фичи «аномалия частот».
- **Статус:** ✅ скачано (2026-09-14) → `(2002) !!! Kleinberg — Bursty and Hierarchical Structure in Streams.pdf/md`

### A4. Swanson 1986 — Fish Oil, Raynaud's Syndrome, and Undiscovered Public Knowledge
- **DOI:** 10.1353/pbm.1986.0087 · **Релевантность:** !!! 5/5 (612 цит.)
- **Зачем:** **основа LBD** (literature-based discovery) = наш S3-аналог; Kastrin 2020 на неё опирается.
  Первоисточник «обнаружения скрытых связей» — основа нашей фарма-валидации (drug repurposing).
- **Статус:** ✅ скачано (2026-09-14) → `(1986) !!! Swanson — Fish Oil, Raynaud's Syndrome, Undiscovered Public Knowledge.pdf/md`

### A5. Chen 2006 — CiteSpace II: Detecting and visualizing emerging trends
- **DOI:** 10.1002/asi.20317 · **Релевантность:** !!! 5/5 (5881 цит.)
- **Зачем:** CiteSpace — инструмент, которым Kastrin (LBD) и Chichorro (патентометрия) делали анализ.
  Даёт методологию burst/betweenness = наш S3/σ-инновационность (H25). Ссылка на инструмент в related work.
- **Статус:** ✅ скачано (2026-09-14; журнал JASIST 57(3) 2006, PDF принят 2005) → `(2006) !!! Chen — CiteSpace II Detecting and Visualizing Emerging Trends.pdf/md`

### A6. Cozzens et al. 2010 — Emerging technologies: quantitative identification and measurement
- **DOI:** 10.1080/09537321003647396 · **Релевантность:** !! 4/5 (206 цит.)
- **Зачем:** цитируется Wang 2018 (критика «измерение вместо идентификации»). Обзор подходов
  к количественному измерению emerging tech — полезен для раздела ограничений.
- **Статус:** ✅ скачано (2026-09-14) → `(2010) !! Cozzens, Gatchair, Kang, Kim, Lee, Ordóñez, Porter — Emerging Technologies Quantitative ID and Measurement.pdf/md`

### A7. Van Eck & Waltman 2010 — VOSviewer (software survey)
- **DOI:** 10.1007/s11192-009-0146-3 · **Релевантность:** !! 4/5 (18092 цит.)
- **Зачем:** VOSviewer = стандарт кластеризации/визуализации, которым пользуются Small 2014
  (VOS-алгоритм) и Wang 2018. У них кластеризация direct citation; у нас — crosscite/clustering.
  Ссылка на инструмент и алгоритм.
- **Статус:** ✅ скачано (2026-09-14; open access; репозиторий `neesjanvaneck/VOSviewer-Online` ★139) → `(2010) _!!_ van Eck, Waltman — VOSviewer Software Survey.pdf/md`

## B. Гранты/конференции как ОТДЕЛЬНЫЕ сигналы (сравнить с нашими S1d/S1c) — средний приоритет

### B1. Van Raan & Van der Velde 1991 — Bibliometric mapping and early warning (materials science)
- **DOI:** 10.1093/rev/1.2.115 · **Релевантность:** !!! 5/5 — ** единственная найденная** работа
  именно про **early warning по грантам/областям в материаловедении** (доменно близко к СП).
- **Зачем:** прямое сравнение с нашим грантовым сигналом (grant_signal, NSF/CORDIS/РНФ): как авторы
  в 1991 предсказывали emerging topics в materials science. Ранний пример «грантового раннего предупреждения».
- **Статус:** ✅ скачано (2026-09-14) → `(1991) !!! van Raan, van der Velde — Bibliometric Mapping and Early Warning (Materials Science).pdf/md`

### B2. Mund & Neuhäusler 2015 — Early-stage identification of emerging topics (bibliometric ch.)
- **DOI:** 10.1016/j.joi.2015.09.004 · **Релевантность:** !! 4/5
- **Зачем:** «ранняя стадия emerging по библиометрическим характеристикам» — ровно наш этап 1 скрининг
  (novelty×growth×impact). Может дать дополнительные критерии для порога.
- **Статус:** ✅ скачано (2026-09-14) → `(2015) !! Mund, Neuhäusler — Early-Stage Identification of Emerging Topics.pdf/md`

### B3. Shehabuddeen & Probert 2005 — Technology intelligence early warning
- **DOI:** 10.1109/iemc.2004.1407130 · **Релевантность:** !! 4/5
- **Зачем:** technology intelligence для early warning — пересечение применения/конференций/патентов;
  сравнение с нашим конференционным сигналом (conference_signal).
- **Статус:** ✅ скачано (2026-09-14) → `(2005) !! Shehabuddeen, Probert — Excavating the Technology Landscape Early Warning Signals.pdf/md`

### B4. Guo, Wang, Li, Zhu 2016 — Subject-action-object morphology for technological change
- **DOI:** 10.1016/j.techfore.2016.01.028 · **Релевантность:** !! 4/5 (81 цит.)
- **Зачем:** SAO-морфология для направления технологических изменений — потенциальная фича
  для S2-семантики (аналогия: наш wordshift, но структурный SAO-подход).
- **Статус:** ✅ скачано (2026-09-14) → `(2016) !! Guo, Wang, Li, Zhu — SAO Morphology for Technological Change Direction.pdf/md`

### B5. Guo, Weingart, Börner 2011 — Mixed-indicators model for identifying emerging research areas
- **DOI:** 10.1007/s11192-011-0433-7 · **Релевантность:** !! 4/5 (92 цит.)
- **Зачем:** смешанные индикаторы (mixed) emerging areas — близко к нашему мульти-базовому S1
  (несколько сигналов сразу). Сравнение подходов «смешанный vs одиночный сигнал».
- **Статус:** ✅ скачано (2026-09-14) → `(2011) !! Guo, Weingart, Börner — Mixed-Indicators Model for Emerging Research Areas.pdf/md`

## C. Современные продолжения (для контекста и возможных бейзлайнов)

### C1. Ranaei, Suominen, Porter, Carley 2019 — Evaluating technological emergence (3 approaches)
- **DOI:** 10.1007/s11192-019-03275-w · **Релевантность:** !!! 5/5 — та же школа, что EScore (Carley 2018,
  Garner 2017), но сравнение ВОСПРОИЗВОДИМЫХ подходов к тех.Обнаружению возникновения.
- **Зачем:** прямые наследники EScore — показать эволюцию метода; возможный дополнительный бейзлайн.
- **Статус:** ✅ скачано (2026-09-14; open access) → `(2019) !!! Ranaei, Suominen, Porter, Carley — Evaluating Technological Emergence.pdf/md`

### C2. Mühlroth, Kölbl, Grottke 2023 — Innovation signals: ML to separate noise from news
- **DOI:** 10.1007/s11192-023-04672-y · **Релевантность:** !! 4/5 (13 цит.)
- **Зачем:** «инновационные сигналы + ML шум/сигнал» — формально близко к нашему LLM-фильтру
  и к тому, как Медведев отделяет шум от трендов. Свежая (2023).
- **Статус:** ✅ скачано (2026-09-14; open access) → `(2023) !! Mühlroth, Kölbl, Grottke — Innovation Signals ML Noise from News.pdf/md`

### C3. Strumsky & Lobo 2015 — Identifying sources of technological novelty (patents)
- **DOI:** 10.1016/j.respol.2015.05.008 · **Релевантность:** !! 4/5 (165 цит.)
- **Зачем:** патентная схема (против классификаций) для новизны — сравнение с нашим патентным сигналом
  (Lens/GP): как классификации искажают измерение технологической новизны.
- **Статус:** ✅ скачано (2026-09-14) → `(2015) !! Strumsky, Lobo — Identifying the Sources of Technological Novelty.pdf/md`

### C4. Jung & Segev 2022 — Common pattern in ancestors of emerging topics (pan-domain)
- **DOI:** 10.1016/j.knosys.2022.110020 · **Релевантность:** !! 4/5 — **пан-доменное предсказание**
  emerging-тем по общему паттерну предков (AUGUR-наследник).
- **Зачем:** прямой аналог нашей заявки «скрининг кандидатов по всей базе» (Этап 1) — показать,
  что пан-доменная детекция существует и как она работает.
- **Статус:** ✅ скачано (2026-09-14) → `(2022) !! Jung, Segev — Common Pattern within Ancestors of Emerging Topics.pdf/md`

## D. Грант/конференция как сигнал — что НЕ нашли (важно для честности)
- **Статей, где грантовые ИЛИ конференционные данные используются ОТДЕЛЬНО как детектор трендов,
  в открытой литературе почти НЕТ** (найдено только ~4 на ~40 запросов, из них релевантных 2-3).
  Это **наша сильная сторона** (S1d гранты 5 стран, S1c конференции TAS/SNF): подтверждает новизну
  мульти-базового подхода и даёт материал для related work (мы — одни из немногих).
- Рекомендация: в статье/защите отметить «гранты/конференции используются, но редко систематически;
  наше пересечение баз — редкость» (наши кейсы 007/011/010 это показывают).

## Примечание о приоритете скачивания (ИСТОРИЯ — все скачано 2026-09-14)
> Ранее приоритет был: открытые (Kleinberg/Chen/Ranaei) → платные по команде (Callon/Ansoff/Swanson)
> → грант/конференции (B1-B5). Все 16 в итоге получены 2026-09-14 без sci-hub.

## Итог добавления 16 (2026-09-14) — все скачаны и обработаны по §4.3
| Код | Файл в `baselines/` | Релевант. | Зачем |
|---|---|---|---|
| A1 | (1991) !!! Callon — Co-Word Analysis | !!! | первоисточник co-word-бейзлайна |
| A2 | (1975) !!! Ansoff — Managing Strategic Surprise | !!! | канон термина weak signals |
| A3 | (2002) !!! Kleinberg — Bursty Structure in Streams | !!! | burst detection (W2/W3) |
| A4 | (1986) !!! Swanson — Fish Oil, Raynaud's | !!! | основа LBD / S3 |
| A5 | (2006) !!! Chen — CiteSpace II | !!! | front×base, σ-инновационность |
| A6 | (2010) !! Cozzens — Quantitative ID & Measurement | !! | мульти-индикаторность |
| A7 | (2010) _!!_ van Eck, Waltman — VOSviewer | !! | стандарт кластеризации (есть репо) |
| B1 | (1991) !!! van Raan — Early Warning (Materials Sci) | !!! | грант/early warning, доменно близко |
| B2 | (2015) !! Mund, Neuhäusler — Early-Stage ID | !! | ранняя стадия emerging (Этап 1) |
| B3 | (2005) !! Shehabuddeen — Technology Landscape | !! | TI / конференц. сигнал |
| B4 | (2016) !! Guo — SAO Morphology | !! | структурная семантика (S2) |
| B5 | (2011) !! Guo, Weingart, Börner — Mixed-Indicators | !! | смешанные индикаторы (S1) |
| C1 | (2019) !!! Ranaei — Evaluating Technological Emergence | !!! | наследник EScore, кандидат в бейзлайн |
| C2 | (2023) !! Mühlroth — Innovation Signals ML | !! | ML шум/сигнал (наш фильтр) |
| C3 | (2015) !! Strumsky, Lobo — Tech Novelty | !! | патентная новизна |
| C4 | (2022) !! Jung, Segev — Common Pattern Ancestors | !! | пан-доменная детекция (Этап 1) |

**Итог:** wishlist закрыт полностью — все 16 кандидатов скачаны, переименованы по §4.3, имеют выжимки .md.
Библиотека `baselines/` пополнилась канонами (co-word, weak signals, burst, LBD, CiteSpace, VOSviewer)
и работами по грантам/конференциям как отдельным сигналам. Дублей с существующими PDF не обнаружено.