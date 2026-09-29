# Russo — Development of flux pump-based supply systems for superconducting coils (PhD thesis, 2023)

## [Библиография]
Авторы: Giacomo Russo (Dottorato di Ricerca IBES, Università di Bologna, Италия; Esame finale anno 2024)
Название: Development of flux pump-based supply systems for superconducting coils
Тип: Диссертация (PhD thesis), Università di Bologna, Ciclo XXXVI, Settore ING-IND/31 (Elettrotecnica)
Год: 2023 (защита 2024)
DOI: нет (PhD thesis, Bologna)
Научный руководитель: Antonio Morandi (предположительно, по соавторству Russo & Morandi 2023)

## Релевантность проекту: 5/5
**Диссертация прямо по теме — системы питания flux pump (traveling field).** Даёт: (1) численную VIE-модель dynamo/linear flux pump (быстрее H-formulation), валидированную; (2) AI-модели (ANN, XGBoost, KRR) для Jc(T,B) и n(T,B); (3) новую полную эквивалентную схему flux pump; (4) application-oriented процедуру оптимального дизайна; (5) два case study: HTS dynamo для EcoSwing (первый в мире сверхпроводящий ветрогенератор) и linear flux pump для DTT (fusion, 42.5 кА TF-катушки). Ключевой вывод: производительность flux pump сильно зависит от номинального тока и полного сопротивления нагрузки. Закрывает 2.3 (dynamo/linear), 11 (моделирование), 12 (fusion, ветро), 2.5 (потери/токовводы). Дополняет Russo & Morandi 2023 (статья), Mataira PhD (механизм), Ghabeli (модели).

## Суть работы
Диссертация решает проблему инженерного проектирования flux pump: физика сложна и контринтуитивна → численное моделирование + оптимальный дизайн. Четыре части: (гл. 1) обзор состояния (TRFP: магнитные/тепловые/overcurrent/non-conventional; dynamo: механизм traveling field; linear); (гл. 2) VIE-модель + AI (Jc/n) + полная эквивалентная схема; (гл. 3) application-oriented оптимальный дизайн: HTS dynamo для EcoSwing (ветро) и linear flux pump для DTT (fusion); (гл. 4) выводы. Фон: токовводы и power electronics ограничивают HTS-магниты (теплоприток, джоулевы потери, сложность ИП для больших токов, гармоники в сеть); flux pump — контактный/низковольтный/высокотоковый альтернативный способ.

## Глава 1. Обзор состояния flux pump
- TRFP подтипы: магнитно-активированные (Jc(B) и AC-field), термически-активированные, overcurrent-переключатели, non-conventional.
- Dynamo: traveling field механизм (бегущее поле, частичное выпрямление); state of the art.
- Linear type flux pumps.
- Мотивация: fusion-магниты (токи десятки кА → ИП сложны и дороги, гармоники в сеть); токовводы — тепловая нагрузка.

## Глава 2. Численная модель (VIE + AI + эквивалентная схема)
### 2.1. VIE-метод (volume integral equation)
- FEM (volume integral equation) для dynamo flux pump: энергетические характеристики, выходы.
- Валидировано на dynamo из [132,133] (магнит, вращающийся против часовой, угловая скорость ω).
- Два режима работы: (1) current-driven (идеальный источник тока; open-circuit — предельный случай); (2) RL-нагрузка (HTS-катушка; Rext + L; зарядка до Ic).
- Параметры (табл. 1): ширина PM a_PM = 6 мм; Ic ленты 283 А (без зависимости от поля).
- Энергетический баланс; электрическая характеристика.
- **Полная эквивалентная схема** (complete, empirical, serviceable) — те же выходы, быстрый системный анализ.

### 2.2. AI-модели для Jc(T,B) и n(T,B)
- ANN (Artificial Neural Networks), XGBoost (eXtreme Gradient Boosting), KRR (Kernel Ridge regressor).
- Реконструкция поверхности Ic на единицу ширины и n-value от температуры и поля.
- Оценка: результаты для Ic (per unit width) и n-value; чувствительность к гиперпараметрам.

### 2.3-2.4. Валидация и применение
- Численная валидация финальной FEM-модели traveling field flux pumps.
- Производительность разных коммерческих HTS-лент для flux pump.
- Влияние рабочей температуры.

## Глава 3. Application-oriented оптимальный дизайн
### 3.1. Процедура
- Пошаговый оптимальный дизайн traveling field flux pumps (рис. 64 flowchart); основа — VIE-модель с плотной матрицей взаимных индуктивностей.

### 3.2. Case study 1: HTS dynamo для EcoSwing (ветро)
- EcoSwing — первый в мире сверхпроводящий ветрогенератор (EU H2020), установлен и работал в существующей турбине.
- 20 пар полюсов (ротор с HTS field winding) + обычный статор; **>650 ч работы**; TRL 4-5 → 6-7.
- Field winding: 40 racetrack HTS-катушек (ReBCO TPL 2100); железные полюса ротора в криостате; cold heads на роторе.
- Характеристики (табл. 9): **I_rated = 330 А; L_load(I_rated) = 10 Гн; полная мощность охлаждения 35 кВт; P_clamp (токовводы) = 726 Вт**.
- Питание: voltage source + dump resistor + freewheeling diode + IGBT; slip rings/щётки.

### 3.3. Case study 2: linear flux pump для DTT (fusion)
- DTT (Divertor Tokamak Test, Frascati, Италия; ENEA/ENI/CREATE) — европейский токамак для диверторных конфигураций.
- TF magnet: **18 TF катушек, последовательно, 4.5 К (жидкий гелий); каждая rated 42.5 кА** (запас 10%).
- Потери токовводов: ~245 кВт (норм. работа), 320 кВт, 230 кВт (в разных режимах) [188-190].
- Linear flux pump для TF coil cold test facility; модульность (шесть TF катушек) для energization TF катушки.

### 3.4. Влияние нагрузки
- Производительность flux pump **сильно зависит от номинального тока и полного сопротивления нагрузки**; влияние на жизнеспособность.

## Глава 4. Выводы
- Flux pump — контактный/низковольтный/высокотоковый способ питания HTS-магнитов.
- Модель (VIE + AI) + эквивалентная схема — инструменты дизайна.
- Оптимальный дизайн применён к EcoSwing (ветро) и DTT (fusion).
- Зависимость от нагрузки — ключевой фактор жизнеспособности.

## Ключевые результаты (сводка)
- **VIE-модель** (volume integral equation) — быстрее H-formulation; валидирована.
- **AI**: ANN / XGBoost / KRR для Jc(T,B), n(T,B).
- **Полная эквивалентная схема** — быстрый системный анализ.
- **EcoSwing dynamo**: 330 А, 10 Гн, 35 кВт охлаждение, 726 Вт токовводы; >650 ч.
- **DTT linear**: 18 TF, 42.5 кА, 4.5 К; потери токовводов 245/320/230 кВт.
- **Вывод**: производительность ∝ номинальный ток и полное сопротивление нагрузки.

## Теоретическая модель
- VIE (volume integral equation) — FEM для traveling field (dynamo, linear).
- AI (ANN/XGBoost/KRR) — эмпирические поверхности Jc(T,B), n(T,B).
- Полная эквивалентная схема (те же выходы, быстрая).
- Оптимальный дизайн (application-oriented, пошаговый).

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| Тип | traveling field (dynamo, linear) | |
| Модель | VIE + AI (Jc/n) | |
| PM ширина | 6 мм (табл. 1) | |
| Ic (лента) | 283 А (без поля) | |
| EcoSwing | I 330 А, L 10 Гн, 35 кВт | ветро |
| DTT | 42.5 кА, 18 TF, 4.5 К | fusion |
| Нагрузка | номинальный ток, сопротивление | ключевой фактор |

## Конструкция flux pump
HTS dynamo (EcoSwing): 40 racetrack (ReBCO TPL 2100), 20 пар полюсов, cold heads на роторе, питание IGBT + dump. Linear flux pump (DTT): TF coil cold test facility, модульность.

## Ограничения и замечания авторов
- Производительность зависит от load (ток, сопротивление).
- VIE — для traveling field (не TRFP).
- AI — эмпирический (данные лент).
- EcoSwing — концепт применён, но flux pump для ротора — проектируемый (фактически использован slip-ring; FP — будущее).
- DTT — 42.5 кА: flux pump — потенциальная замена токовводов (потери 245-320 кВт).

## Связь с нашим проектом
- Раздел 2.3 (dynamo/linear): дизайн и характеристики.
- Раздел 11 (моделирование): VIE + AI + эквивалентная схема.
- Раздел 12 (fusion): DTT; ветро: EcoSwing.
- Раздел 2.5 (потери): токовводы 726 Вт (EcoSwing), 245-320 кВт (DTT).
- Дополняет: Russo & Morandi 2023, Mataira PhD, Ghabeli, Wang 2022.

## Цитаты (дословные, с номером страницы/раздела)
> «The model embeds artificial intelligence methods to address the relationship between critical current and n-value of HTS tapes concerning temperature and magnetic field» (Abstract, p. I)
> «The study found that the performance of the flux pumps is highly dependent on the rated current and its total resistance» (Abstract, p. I)
> «the field winding of the world first superconducting generator: the EcoSwing wind turbine» (Sec. 3.2, p. 135)
> «Each TF coil is rated for a current of 42.5 kiloamperes» (Sec. 3.3, p. 153)
