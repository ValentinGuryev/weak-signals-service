# Li — Superconducting flux pumping for the high-field HTS magnet: the state of the art (2026)

## [Библиография]
Авторы: Gengyao Li, Chao Li, Ying Xin, Bin Li (Tianjin University, School of Electrical and Information Engineering, Китай)
Название: Superconducting flux pumping for the high-field HTS magnet: the state of the art
Журнал: The European Physical Journal B 99:4 (2026), Topical Review — Solid State and Materials
Год: 2026 (принята 14 ноября 2025)
DOI: 10.1140/epjb/s10051-025-01092-0
Тип: рецензируемый обзор (topical review)

## Релевантность проекту: 4/5
Самый свежий обзор (ноябрь 2025) по flux pumping для высокопольных HTS-магнитов. Даёт формулы динамического сопротивления (1) и (2), таблицу рекордов по типам насосов (табл. 1), систематизацию типов (traveling wave: dynamo/linear/circular; transformer-rectifier: half/full-wave). Прямо отвечает на вопросы 2.1, 2.3 и 2.5 (ограничения, shielding current в параллельных лентах).

## Суть работы
Обзор состояния дел (state of the art) по HTS flux pumps для зарядки высокопольных HTS-магнитов. Мотивация: HTS-магниты не могут работать в persistent mode из-за неизбежного сопротивления соединений (joint resistance) многослойных лент 2-го поколения, флюкс-крипа и фонового поля. Flux pump заряжает замкнутый HTS-магнит бесконтактно (электромагнитная связь), заменяя сильноточные DC-источники и толстые резистивные токовые вводы → меньше теплопритоков, ниже стоимость, безопаснее работа.
Две части: (1) динамическое сопротивление HTS-материалов — теория, формулы, пороги; (2) обзор HTS flux pumps по типам и рекордным параметрам.

## Ключевые результаты
- **Динамическое сопротивление (dynamic resistance):** приложение переменного магнитного поля к ленте с постоянным током ниже Ic индуцирует измеримое сопротивление → энерговыделение, нагрев поверхности. Напряжение (dynamic resistance voltage) всегда одного знака при данном направлении транспортного тока, независимо от ориентации поля. Исчезает мгновенно при снятии поля.
- **Формула Rdyn (постоянная Jc):**
  Rdyn = (4af l / Ic) × (Ba − Ba,th)   (1)
  где 2a — ширина ленты, f — частота, l — длина, Ic — критический ток, Ba — амплитуда поля, Ba,th — пороговая амплитуда для возникновения dynamic resistance.
- **Формула Rdyn (Jc зависит от поля):**
  Rdyn = (4af l / Ic0) × (Ba + c·Ba²)   (2)
  где Ic0 — критический ток ленты, c — константа связи поля с критическим током.
- Порог Ba,th: выводится из нормировки корреляции потерь намагничивания и приложенного поля (случай без транспортного тока); линейные зависимости: Rdyn от Ba (линейна), Ba,th от транспортного тока (линейна).
- Существующие теории адекватны только при малых токах и малых полях; при высоких транспортных токах/полях не учитывают тепловой эффект флюкс-движения.
- **Типы насосов (классификация):**
  - Traveling magnetic wave: dynamo-type (вращающиеся магниты на диске), linear-motor type (катушки с разными фазами → бегущая волна), circular (коротковолновые полюса, тепловое возбуждение).
  - Transformer-rectifier: half-wave, full-wave, full-bridge (2 AC field-controlled switches).
- **Таблица 1 — рекорды (по типам):**
  - Dynamo-type [66]: I_max = 1.3 кА, V = 7 мВ.
  - Linear-motor type [45]: I_max = 1.6 кА, V — не дано.
  - Self-rectifier [67]: I_max = 2.1 кА, V < 1 мВ.
  - Half-wave transformer-rectifier [57]: I_max = 1.1 кА, V — не дано.
  - Full-wave transformer-rectifier [68]: I_max = 0.5 кА, V = 25 мВ.
  - Максимальный ток — на килоамперном уровне; максимальное эффективное DC-напряжение — на милливольтном уровне.
- Рекорд тока среди всех насосов: >3.1 кА — два kilo-amp linear-motor насоса, соединённые параллельно [46].
- Linear-motor прототип с оптимизацией распределения поля и уменьшением длины волны — килоамперный выход [45]; миниатюрный linear насос 120 А [44].

## Теоретическая модель
- Динамическое сопротивление — фундамент HTS flux pumping: переменное поле «ломает» пиннинг вихрей, направленное движение флюкса даёт DC-напряжение (dynamic resistance voltage), заряжающее магнит.
- Уравнения (1) и (2) — основные.
- Моделирование: FEM с электромагнитно-тепловой связью [18, 20, 21]; гармонический анализ напряжения (отличие dynamic resistance voltage от flux flow voltage) [19]; машинное обучение для dynamo-насосов [39]; H-formulation [62].
- Сверхпроводящий переключатель на индуцированном токе в замкнутом контуре [24, 25]: взаимодействие DC транспортного тока и индуцированного экранирующего тока → переключающий эффект; глубокое связывание поля с лентой, быстрый отклик/восстановление [23].

## Параметры переменного поля (если применимо)
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac (амплитуда) | Ba — в формулах; порог Ba,th; конкретные мТл не приведены | формульный подход |
| f (частота) | f — в формуле Rdyn; диапазоны не указаны | — |
| Направление | B⊥ (перпендикулярно ленте) для dynamic resistance | «vertical alternating magnetic field» |
| Геометрия | одиночная лента; стопки [20,21]; параллельные ленты (shielding current проблема) | — |
| I_max | 3.1 кА (2 параллельных linear-motor); 1.3 кА dynamo; 1.6 кА linear; 2.1 кА self-rectifier; 1.1 кА half-wave; 0.5 кА full-wave | табл. 1 |
| dI/dt | не указана | — |
| B_th | Ba,th — формула (1); численные значения не даны | — |
| Потери | не численно; обсуждаются shielding current и циркулирующий ток | — |

## Конструкция flux pump
- Dynamo-type: постоянные магниты одинаковых размеров/намагниченности равномерно по периферии вращающегося диска; мотор через вал; полярность напряжения зависит от направления вращения. Применения: ветрогенераторы [33], бесщёточные HTS-моторы [34, 35], conduction-cooled для non-insulated катушек [37], through-wall конфигурация [38].
- Linear-motor: пара вертикальных железных сердечников, медные соленоиды с одинаковым числом витков, токи одинаковой амплитуды/частоты, разные фазы → бегущая волна; ленты в зазорах.
- Circular: интеграция теплового возбуждения с linear-motor; коротковолновые полюса; миллионы флюкс-квантов, сгруппированных в кластеры, затягиваются в замкнутый контур.
- Transformer-rectifier: flux induction system (трансформатор) + flux driving switch (на dynamic resistance); два замкнутых сверхпроводящих контура → разделение процессов индукции и привода → гибкое управление. Full-bridge с двумя AC field-controlled switches заряжает в оба полупериода → скорость зарядки ≥ 2× half-bridge [60].

## Ограничения и замечания авторов
- **Зарядная способность ограничена:** высокопольные HTS-магниты имеют большую индуктивность, высокий рабочий ток, большой поток → нужны одновременно высокое напряжение и высокий ток зарядки.
- Напряжение transformer-rectifier ограничено: < 100 мВ; ток — критическим током flux driving switch.
- **Проблема shielding current (экранирующего тока) в параллельных лентах:** для увеличения тока ленты соединяют параллельно, но экранирующий ток наводится в лентах против внешнего поля; полный ток = нагрузочный + циркулирующий; даже если нагрузочный < Ic, сумма может превысить Ic → квенч одной ленты рушит всю параллельную систему. Устранение циркулирующего тока — ключ к увеличению эффективного тока.
- Сложно одновременно получить большую площадь приложения поля и высокую плотность потока (ограничение геометрии магнитов) → как повысить dynamic resistance voltage при ограниченной площади — вызов.
- Топология traveling wave сложна (движущиеся магниты/много катушек), процессы индукции и привода связаны → трудно гибко управлять током зарядки.

## Связь с нашим проектом
- Раздел 2.1 (физика): формулы dynamic resistance (1), (2), порог Ba,th — прямое попадание.
- Раздел 2.3 (типы): полная классификация с рекордами (табл. 1) — dynamo, linear, circular, transformer-rectifier.
- Раздел 2.5 (потери/ограничения): shielding current в параллельных лентах, ограничение напряжения <100 мВ, проблема квенча — прямо о стопках/параллельных лентах (вопрос про стопку).
- Раздел 2.2 (параметры поля): формульная связь Rdyn(f, Ba, Ba,th) — база для оценок, хотя конкретных чисел мТл нет.
- Космос (раздел 2.4): упоминание через [12] — Hamilton, AIAA 2020, «Reducing mission cryogenic load via HTS dynamo» — прямая ссылка на космическое применение dynamo-насоса.

## Цитаты (дословные, с номером страницы/раздела)
> «HTS flux pumps are devices that can charge closed HTS magnets wirelessly in the way of electromagnetic coupling.» (Abstract)
> «the maximum charging current of various flux pumps is at the kiloampere level, and the maximum effective DC output voltage is at the millivolt level.» (Section 3.2)
> «the charging voltage induced by the transformer-rectifier flux pump is limited, which is generally less than 100 millivolts.» (Section 3.2)
> «the total current flowing through any single HTS tape is the sum of the load current component and the circulating current component. Even if the load current alone is below the critical current Ic of HTS tapes, the superposition of the circulating current can drive the total current to exceed Ic. This causes the HTS tape to quench.» (Section 4, (2))
> «how to eliminate the circulating current between multiple parallel tapes is the key to enhancing the effective charging current of flux pumps.» (Section 4, (2))
