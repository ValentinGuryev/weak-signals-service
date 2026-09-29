# Wishlist — кейс 007 (JTWPA): литература для ответа на «какую проблему решает / какие конкуренты»

> Протокол §4.2a: только документы, которых НЕТ в библиотеке. Статусы: 📥 скачать / ⛔ недоступно / 🔶 позже.
> Релевантность: !!! = 5/5, !! = 4/5, ! = 3/5. Скачанный PDF → `literature/` `(YYYY) _*_ Author — Title.pdf` + выжимка → строка удаляется.
> Составлен  по анализу корпуса JTWPA (186 работ, 213 абстрактов, 147 references) — проблема и конкуренты извлечены из абстрактов, wishlist закрывает пробелы под S4/S5/NARRATIVE.

---

## A. Проблема и место технологии (обзоры/фундамент) — для «мотивации» в NARRATIVE

| ID | Документ | Зачем | Рел. | Статус |
|---|---|---|---|---|
| A1 | (2019) Krantz et al — Quantum information processing with superconducting circuits: a review (Rep. Prog. Phys., 875 цит.) | Где в стеке квантового компьютера стоит чтение и почему там нужен quantum-limited усилитель; контекст платформы (кубиты = драйвер) | !!! | 📥 |
| A2 | (2010) Clerk et al — Introduction to quantum noise, measurement, and amplification (Rev. Mod. Phys., 1997 цит.) | Фундамент: почему «квантовый предел шума» — физический предел, и что значит «добавочный шум ≤ half-photon» (S4 — снятие предела) | !!! | 📥 |
| A3 | (1982) Caves — Quantum limits on noise in linear amplifiers (Phys. Rev. D, 1729 цит.) | Первоисточник квантового предела линейных усилителей (якорь, цитируется 22× внутри корпуса) | !! | 📥 |
| A4 | (2020) Aumentado — Superconducting Parametric Amplifiers: The State of the Art in Josephson Parametric Amplifiers (IEEE Microwave Magazine, 243 цит.) | Обзор ВСЕХ типов СП параметрических усилителей (JPA, JTWPA, KITWPA, SNAIL, IMA, JPC) — единая карта конкурентов от авторитета (LBNL) | !!! | 📥 |
| A5 | (2021) Manucharyan? / (2021) Perspective on traveling wave microwave parametric amplifiers (APL, 92 цит.) | Перспектива/сравнение проточных TWPA (в т.ч. не-джозефсоновских) — конкуренты внутри семейства | !! | 🔶 |

## B. Конкуренты (S5) — какую проблему каждый закрывает и почему JTWPA выиграл/проиграл

### B1. JPA резонаторный (конкурент-предшественник, 33 упоминания в абстрактах)
| ID | Документ | Зачем | Рел. | Статус |
|---|---|---|---|---|
| B1a | (2007) Castellanos-Beltran et al — Widely tunable parametric amplifier based on a superconducting quantum interference device (APL, 352 цит.) | Первый JPA (2007) — родоначальник; понять, что JTWPA улучшает (узкополосность → широкополосность) | !! | 📥 |
| B1b | (2008) Castellanos-Beltran et al — Amplification and squeezing of quantum noise with a tunable Josephson metamaterial (Nature Phys, 646 цит.) | Развитие JPA, squeezing; конкурентная линейка 2008-2015 | !! | 📥 |
| B1c | (2015) Mutus et al / Google — (JPA в системах Google до JTWPA) | Какой усилитель Google реально использовал для чтения (JPA/TWPA) — внедрение у лидера | ! | 🔶 |

### B2. KITWPA (кинетическая индуктивность, 23 упоминания — главный сосед-конкурент)
| ID | Документ | Зачем | Рел. | Статус |
|---|---|---|---|---|
| B2a | (2021) Malnou et al — Three-Wave Mixing Kinetic Inductance Traveling-Wave Amplifier with Near-Quantum-Limited Noise Performance (PRX Quantum, 133 цит., NIST/JPL) | Прямой конкурент: KITWPA на NbTiN/TiN достиг near-quantum-limited БЕЗ джозефсоновских переходов — почему не вытеснил JTWPA (насыщение/динамический диапазон?) | !!! | 📥 |
| B2b | (2016) Ho Eom / JPL? — A wideband, low-noise superconducting amplifier... (KITWPA) | Ранний KITWPA JPL (2012-2016) | ! | 🔶 |

### B3. Классическая электроника (HEMT/крио-усилители — «статус-кво», которое JTWPA вытесняет)
| ID | Документ | Зачем | Рел. | Статус |
|---|---|---|---|---|
| B3a | (2012) Macklin et al — A wideband, low-noise superconducting amplifier with high dynamic range (Nature Phys, 423 цит.) | ВАЖНО: «superconducting amplifier» на джозефсоновских переходах (не параметрический) — мост между HEMT и JTWPA; high dynamic range | !!! | 📥 |
| B3b | Обзор/статья по cryogenic HEMT LNA (4K) | Сколько шума у HEMT при 4K (~2-4 K шум vs квантовый предел ~0.05 K) — почему HEMT не тянет чтение кубитов | !! | 🔶 поиск |

### B4. Смежные схемы внутри семейства СП-усилителей
| ID | Документ | Зачем | Рел. | Статус |
|---|---|---|---|---|
| B4a | (2022) Kerr reversal in Josephson meta-material and traveling wave parametric amplification (Nature Comm, 97 цит.) | SNAIL/метаматериал-линейка (Kerr reversal) — как решают проблему сжатия динамического диапазона | !! | 📥 |
| B4b | (2020) Planat et al — Photonic-crystal JTWPA (PRX, 109 цит.) — УЖЕ в README кейса §6 | фотonic-crystal версия — в wishlist НЕ включаем (см. ниже примечание) | — | — |

## C. Применения-драйверы (после 2018 — диверсификация) — «состоялся ли тренд»
| ID | Документ | Зачем | Рел. | Статус |
|---|---|---|---|---|
| C1 | (2023) Bartram et al — Dark matter axion search using a JTWPA (PRX/RSI, 72 цит.) | Аксионный драйвер: JTWPA для чтения haloscope (ADMX) — второй рынок после кубитов | !!! | 📥 |
| C2 | (2024/2025) DARTWARS / радиоастрономия — обзорная статья проекта | Третий драйвер: JTWPA/KITWPA для чтения MKID-массивов в радиоастрономии (EU-консорциум) | ! | 🔶 поиск |
| C3 | (2022) Microwave quantum radar JTWPA (2 статьи) | Четвёртый драйвер: квантовый радар — есть ли реальный спрос или hype | ! | 🔶 |

## D. Снятие предела (S4) — технические параметры
| ID | Документ | Зачем | Рел. | Статус |
|---|---|---|---|---|
| D1 | (2015) Macklin et al — A near–quantum-limited Josephson traveling-wave parametric amplifier (Science, 833 цит.) | ГЛАВНЫЙ якорь кейса — уже есть в корпусе/README | !!! | ⛔ нет arXiv-препринта (Science, платный); PDF только sci-hub по команде |
| D2 | (2016) Zorin — JTWPA with Three-Wave Mixing (PTB, 125 цит.) | Версия Zorin (3WM) — сравнение с 4WM Macklin | !! | 📥 |

---

## Вывод-обоснование (что уже знаем из корпуса, минимизируя wishlist)

**Проблема, которую решает JTWPA (из абстрактов, 186 работ):**
Чтение состояния квантовых кубитов (transmon) — СВЧ-сигнал в несколько фотонов нужно усилить без добавления
классического шума (иначе квантовое состояние разрушается). Классические HEMT-усилители при 4K добавляют
шум ~2-4 K (>> квантовый предел ~0.05 K), поэтому для чтения нужен quantum-limited усилитель.
67/186 работ прямо говорят о шуме/квантовом пределе, 81 — о чтении кубитов/квантовых вычислениях.
S4: Macklin 2015 снял предел (near-quantum-limited + широкополосность, 833 цит.).

**Конкуренты (по частоте упоминания в абстрактах):**
1. **JPA резонаторный** (33 упоминания) — предшественник 2007-2015, узкополосный (МГц), JTWPA выиграл широкополосностью;
2. **KITWPA/кинетическая индуктивность** (23) — главный сосед: near-quantum-limited БЕЗ JJ, но хуже по насыщению/динамическому диапазону и сложнее встраивается в кубитные чипы (общий материал TiN/NbTiN);
3. **SNAIL/метаматериал** (8) — линейка для 3WM, Kerr-компенсация (динамический диапазон);
4. **HEMT** — классика, вне квантового предела (упоминается редко, т.к. «статус-кво»);
5. JPC/конвертеры, циркуляторы — смежные (редко в абстрактах).

**Пробелы, которые закроет wishlist:** A1-A3 (мотивация: зачем quantum-limited), A4 (единая карта конкурентов),
B1a/B1b (JPA-линейка), B2a (KITWPA — главный конкурент), B3a (мост HEMT→JJ), B4a (SNAIL/Kerr), C1 (аксионы),
D1/D2 (технические якоря S4). Это ~10-12 PDF — компактно и целенаправленно.

> Вычищено из wishlist (2026-09-05): Planat 2020 (photonic-crystal JTWPA) — уже в README кейса §6; Macklin 2015 — в корпусе/README; A2 Clerk 2010, B1a Castellanos 2007, B1b Castellanos 2008, B2a Malnou 2021, B3a Eom 2012 (=ошибочно «Macklin 2012»), B4a Ranadive 2022, C1 Bartram 2023, D2 Zorin 2016 — скачаны с arXiv (открытый доступ), выжимки в literature/.
> ⚠️ Поправка: «Macklin 2012 wideband» в черновике wishlist — на деле **Eom et al. 2012 (JPL, KITWPA-родоначальник)**, не Macklin; файл переименован и выжимка сделана как Eom.
