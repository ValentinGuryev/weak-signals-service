# Mallett — Design and initial test results of a space-bound flux pump for the Hēki mission (2024)

## [Библиография]
Авторы: B.P.P. Mallett, J. Clarke, T. Endo, M. Goddard-Winchester, C. Shellard, J. Olatunji, R.A. Badcock, R. Pollock (Paihau Robinson Research Institute, Victoria University of Wellington, НЗ; Auckland Bioengineering Institute, University of Auckland, НЗ)
Название: Design and initial test results of a space-bound flux pump to energize the Hēki mission's superconducting magnet
Журнал: Superconductivity 12, 100129 (2024), Full Length Article
Год: 2024 (доступна онлайн 05.11.2024)
DOI: 10.1016/j.supcon.2024.100129
Тип: рецензируемая статья (Open Access, CC BY-NC-ND)

## Релевантность проекту: 5/5
Прямой первоисточник конструкции космического flux pump для миссии Hēki (МКС, JEM-EF #4): transformer-based self-rectifier архитектура, полные circuit-параметры (табл. 1), требования (≤0.5 Вт теплоприток, ≥15 А, ≥0.2 мВdc, <1 кг, >1500 ч), испытания в LN2 и conduction-cooled (100+ ч). Заполняет разделы 2.3 (self-rectifier), 2.4 (космос, SWaP), 2.5 (теплоприток, потери).

## Суть работы
Описаны дизайн и первые испытания flux pump (FP) для миссии Hēki — первого (по мнению авторов) HTS-электромагнита в космосе на пилотируемом аппарате. Магнит: 4 double-pancake катушки из SuperOx 04-20Ag-5Cu-40H REBCO, bore 62 мм, OD 100 мм, L 42 мм, цель ≥0.3 Тл (15 А); из-за ограничения рассеянного поля на МКС (<0.316 мТл на 70 мм от поверхности) максимальный рабочий ток 15 А (L = 0.16 Гн при 15 А). Без flux pump: медные токовводы дали бы ≥84 мВт/А теплоприток → 1.26 Вт при 15 А — не влезает в бюджет (<100 Вт на полезную нагрузку, криокулер CryoTel MT 90 Вт). Выбрана архитектура transformer-based self-rectifier (наименьший технический риск из трёх рассмотренных: dynamo [39], transformer self-rectifier [36], electromagnetic-switch transformer rectifier [40]). Дана эффективная circuit-модель (Simulink), механический и тепловой дизайн (COMSOL), испытания: LN2-прототип и conduction-cooled flight-simulate (>100 ч непрерывно).

## Ключевые результаты
**Требования к FP (раздел 2):**
- Теплоприток ≤ 0.5 Вт в криогенную среду (включая работу и провода).
- Зарядка: >15 А (0.3 Тл), напряжение ≥ 0.2 мВdc (усреднённое за цикл).
- Космос: масса <1 кг, conduction-cooled, вибростойкость к запуску, EMI, безопасность для пилотируемого аппарата, надёжность >1500 ч.

**Конструкция (раздел 3):**
- Transformer: primary 225 витков (медь), secondary 2 витка (HTS), ток primary ~1 А; I_c вторичной 300 А.
- Bridge (HTS, SuperOx 4 мм, self-field I_c 140 А, длина 1 м, coiled — две встречно намотанные длины для снижения индуктивности).
- R_series = 20 мкОм (пассивный резистор, trade-off с тепловыделением); R_bridge = 350 нОм; R_magnet = 2000 нОм (табл. 1).
- Модель: R_SC = (E_0·l/I_c)·(I/I_c)^(n−1) (ур. 1), E_0 = 1 мкВ/см; n — показатель.
- Ключевой результат: V_magnet ∝ I_2·R_series (цикл-усреднённое напряжение пропорционально сопротивлению secondary и DC-смещению); R_series — trade-off тепло/напряжение.
- Масса FP: 0.85 кг (~1/3 алюминий, 1/3 медь primary, 1/3 железо core). Размеры: 125×82×110 мм.
- Core: A 225 мм², l 150 мм, B_sat 1.9 Тл, H_sat 300 А/м, зазор 0.1 мм; ламинации 0.3 мм против eddy current; AC-потери в HTS ~10 мВт [49].

**Испытания (раздел 4):**
- LN2: зарядка до 15 А, V пик ~2 мВdc, падение до 0.5 мВdc при 15 А; тепловыделение 0.7 Вт при 15 А (почти вдвое выше лимита 11.9 А/Вт идеальных токовводов); лимит 15 А из-за паяных соединений 30 мкОм (много больше ожидаемых). Метрика: выход мВdc/Вт; требование >0.4 мВdc/Вт при целевом токе.
- Conduction-cooled (flight-like): криокулер 40 Вт вход → 1.5 Вт холода, 77 К у магнита; FP 2 А, 4 Гц → зарядка 5.4 А за 1200 с; V ~0.3 мВdc (0.5 мВdc/Вт); доп. 7.5 Вт на криокулере = 0.6 Вт теплопритока от FP (совпало с расчётом в пределах 50 мВт); bridge нагрелась +1.5 К; стабильно >100 ч; термоциклы 60–323 К.
- Деградация: повреждение сверхпроводника при эпоксидной приклейке (низкий I_c в тестовых катушках); решение — отверждение эпоксида при 330 К. Позже 15 А в conduction-cooled достигнуты.
- Модель: predicted V > 0.2 мВdc даже при I > 15 А — запас надёжности.

## Теоретическая модель
- Эффективная circuit-модель (Simulink): transformer (переменная магнитная проницаемость Si-стали), HTS как нелинейный резистор E-J power law (ур. 1); не включает тепловую физику и dynamic resistance [46].
- Тепловая модель COMSOL [31]: градиент между cold-tip и HTS < 7 К критичен; при 0.6 Вт диссипации FP разница между магнитом и bridge 2.2 К.
- AC-потери в HTS-проводнике не включены в circuit-модель; ~10 мВт оценка [49].
- Формула теплопритока: P_h = Σ_m (1/f)·∫ i_m(t)·v_m(t) dt (ур. 2) — по всем элементам (primary, secondary, R_series, bridge, пассивные сопротивления магнита); потери намагничивания core не включены.

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | поле создаётся током 1.4–2 А в primary | waveform asymmetric (рис. 3) |
| f (частота) | 4 Гц (conduction-cooled); 10 Гц (LN2) | 4 Гц — лимит электроники flight-copy |
| Направление | не перпендикулярно ленте — transformer-rectifier (bridge током) | иная физика, чем dynamo |
| Геометрия | transformer-based self-rectifier, bridge 1 м coiled, secondary 2 витка | |
| I_max | 15 А (миссия); тест 5.4 А (2-катушечный магнит) | 0.3 Тл цель |
| V_dc | 0.3–2 мВdc | 0.5 мВdc/Вт |
| Потери | 0.6 Вт (conduction-cooled), 0.7 Вт (LN2) | требование <0.5 Вт (полётная версия) |
| B_th | не применимо (нет AC-поля на ленту) | |

## Конструкция flux pump
Transformer-based self-rectifier, conduction-cooled, CryoTel MT (SunPower) криокулер (90 Вт макс, lift-factor до 20 при 77 К/296 К); медь в primary (проще тепловой дизайн, больше теплоприток — приемлемо); 28-AWG токовводы. Тепловые интерфейсы с shim-нагревателем для активного контроля температуры bridge (и I_c).

## Ограничения и замечания авторов
- Три архитектуры (dynamo, self-rectifier, electromagnetic-switch) все могли выполнить миссию и масштабируются до сотен ампер; self-rectifier выбран по минимальному риску.
- Нет кванч-защиты (no-insulation магнит — пассивная защита, малая запасённая энергия ~18.5 Дж/кг при 0.5 Тл, низкоимпедансный FP не может поддерживать разрушительный ток).
- Conduction-cooled показал худшую производительность vs LN2 из-за повреждённых компонентов (эпоксид); после фикса (330 К cure) достигнуты 15 А.
- Неизвестно влияние космической радиации на HTS — миссия включает два датчика радиации.
- Главный риск: производительность радиатора на орбите (определяет рабочую температуру).

## Связь с нашим проектом
- Раздел 2.4 (космос): первая реализация HTS-магнит + flux pump для космоса; полные требования миссии; SWaP (0.85 кг, <1 кг).
- Раздел 2.3 (self-rectifier): конструкция, параметры (табл. 1), сравнение архитектур.
- Раздел 2.5 (потери): P_h формула, 0.6 Вт, сравнение с токовводами (84 мВт/А).
- Раздел 2.2 (напряжение/скорость зарядки): 0.2–2 мВdc, метрика мВdc/Вт.
- Прямой вклад в LIT_REVIEW разделы «космические применения» и «self-rectifier flux pumps». Дополняет Olatunji 2024 (магнит), Pavri 2026 (квалификация), Pollock 2026 (полёт), Mallett 2026 (квалификация FP).

## Цитаты (дословные, с номером страницы/раздела)
> «A FP is required to reduce the heat flux associated with energizing the magnet, and to make this mission feasible» (Sec. 2, p. 2)
> «the cycle-averaged magnet charging voltage, V_magnet, is proportional to the resistance on the secondary winding, set by the passive resistor R_series ... V_magnet ≈ I_2·R_series» (Sec. 3, p. 4)
> «The FP was continuously operated for more than 100 h without significant change in these performance characteristics» (Sec. 4, p. 7)
> «the factor with the highest likelihood is the on-orbit performance of the thermal radiator since this ultimately will determine the FP and magnet operating temperatures» (Sec. 4, p. 7)
