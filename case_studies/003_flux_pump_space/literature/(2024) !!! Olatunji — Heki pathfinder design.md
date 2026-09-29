# Olatunji — Hēki: A superconducting magnet for space propulsion on the ISS — Pathfinder design and experimental thermal testing (2024)

## [Библиография]
Авторы: Jamal Olatunji, Nicholas Strickland, Max Goddard-Winchester, Benjamin Mallett, Celine Jane, Cameron Shellard, Emile Webster, Betina Pavri, Avinash Rao, Randy Pollock (Paihau-Robinson Research Institute, Victoria University of Wellington, НЗ; IDS Consulting)
Название: Hēki: A superconducting magnet for space propulsion on the International Space Station — Pathfinder design and experimental thermal testing
Журнал: Superconductivity 12, 100133 (2024), Large Scale Application Report
Год: 2024 (доступна онлайн 23.11.2024)
DOI: 10.1016/j.supcon.2024.100133
Тип: рецензируемая статья (Open Access, CC BY-NC-ND)

## Релевантность проекту: 5/5
Предпроектный (pathfinder) дизайн миссии Hēki: электромагнитный дизайн HTS-магнита (4 double-pancake, SuperOx YBCO, центральное поле 0.5 Тл при I_op = 18 А), алгоритм массовой оптимизации магнитного экрана (0.3 мТл на 7 см от NREP), тепловой дизайн (75 K при <100 Вт), экспериментальная термовакуумная валидация. Прямые числа для разделов 2.4 (космос, SWaP: 15 кг, 13 л, 100 Вт) и 2.5 (тепловые потери, контактные сопротивления, MLI). Дополняет Pavri 2026 и Pollock 2026 (эта — про проектирование, те — про полёт).

## Суть работы
Подробное описание предварительного дизайна payload Hēki — первой попытки реалистичного космического payload с HTS-магнитом и flux pump в рамках жёстких SWaP ограничений малого спутника. NREP на МКС: масса 15 кг, объём 13 л, мощность 100 Вт. Цель: центральное поле ≥0.3 Тл (предпочтительно >0.5 Тл) при ограничении stray field <0.3 мТл на 7 см от поверхности NREP.
FEM-модели (COMSOL) для электромагнитного дизайна (включая алгоритм массовой оптимизации пассивного магнитного экрана) и теплового дизайна (кондукционное охлаждение, <100 Вт, <75 K). Термовакуумные эксперименты в симулированной космической среде для валидации моделей; трудные для измерения параметры (контактное сопротивление, эффективная emissivity MLI) определены эмпирически (Newton/Secant tuning).

## Ключевые результаты
- **Магнит:** 4 double-pancake катушки, SuperOx YBCO 2G HTS лента 4 мм; внутренний диаметр 64 мм (для анода AF-MPD 50 мм), наружный 90 мм; ~325 витков на double pancake (turn spacing 80 мкм); non-insulated (проводящий эпоксид между витками — квенч-защита).
- **I_op:** достижение 0.5 Тл при I_op = 15–25 А; критическая температура: 81 K (0.3 Тл), 77 K (0.5 Тл) → целевая рабочая T < 75 K (запас). При 18 А центральное поле >0.5 Тл с экраном.
- **Критический ток:** Ic_norm = 140 А (с запасом от 200 А); при 75 K, 18 А, 0.5 Тл — магнит работает на 40% от Ic; экран улучшает Ic на ~20%.
- **Магнитный экран (пассивный, low-carbon steel 1010):** алгоритм массовой оптимизации (dimensionless, N=100 шагов, bisection по τ); начальный экран 2.5 кг → оптимум 1.15 кг (инфлексия при ~1 кг); форма «бублика» (bagel), повторяет форму силовых линий; устойчив к вариациям кривых намагничивания (Sgobba 2011, 6 источников); снижает stray field до <0.3 мТл на 7 см при 0.5 Тл в центре; побочный эффект — усиление центрального поля.
- **Криокулер:** SunPower CryoTel MT (2.1 кг, 243 мм, 73 мм, space heritage); Qc = a·εc + b, a = 0.2917·Pin − 2.7483, b = 0.0213·Pin − 2.5443; εc = Tcold/(Thot − Tcold); точность ±0.15 Вт; ~5 Вт охлаждения при 75 K.
- **Тепловой дизайн:** магнит до 75 K при 65 Вт (T_NREP = −10 °C); при T_NREP = 20 °C — 86.5 Вт (почти весь бюджет); при 30 °C — превышение Tc (узкий диапазон!); радиация >50% теплопритоков несмотря на MLI; градиент <2 K по катушкам, <5 K между магнитом и flux pump.
- **Тепловой воротник:** оптимизация массовым алгоритмом; алюминий лучше меди: 9.2 Вт/К при 0.45 кг (медь 4+ кг); реально измерено всего 1.6 Вт/К (бутылочное горлышко — интерфейс cryocooler-collar).
- **Flux pump теплоприток:** ψ = 1 Вт/мВ (измерено), запас ψ = 2 Вт/мВ → Q_FP = 400 мВт при работе; V_DC ~ 0.2 В.
- **Соединения:** цель 100 нОм/соединение, 18 соединений → 1.8 мкОм; при 18 А <0.6 мВт (игнорируемо).
- **Экспериментальная валидация:** thermal strap измерена 0.58 Вт/К (ожидали 1); tuning (Secant/Newton, d=0.5, 15 итераций): MLI emissivity 0.015→0.034 (12 Вт/м² — вдвое хуже ожидаемого; у [39] ~5 Вт/м² для магнитов); copper-copper контакт 0.1→2.8 Вт/К; flux pump-frame 200→165 Вт/м²·К; baseplate-NREP 200→10 Вт/м²·К (плохо в вакууме); thermal gasket 6000→517 Вт/м²·К (в 11 раз хуже из-за закруглённой поверхности); переходный тест: охлаждение за ~16 ч (модель согласуется).
- **Итог:** <75 K достижимо при <100 Вт в имитации космоса, но запасы узкие; нужен radiative cooling криокулера → переделка дизайна (Pollock et al 2024 [23]).
- Запуск Q1 2025 (реально — сентябрь 2025).

## Теоретическая модель
- Электромагнитная: COMSOL homogenised multiturn conductor; J_e = I_op/(t_w·t_t); B = ∇×A, B = μ0μrH, J = σE + J_e; локализованный Ic с учётом B, угла и T (Supercurrent Facility измерения); Ic_norm = 140 А.
- Оптимизация экрана: φn = 1 − n/N; Y = 1 − (B − Bmin)/(Bmax − Bmin); f(Y) = 1 если Y ≤ τn; φn = ∫f(Y)dV/∫dV; bisection для τ; удаление зон с высоким Y (μr → 1). Универсальный (dimensionless) — применим к любой геометрии; повторно применён к тепловому воротнику (Y по heat flux).
- Тепловая: ϱiCp_i·∂T/∂t = ∇·(λi∇T) + ΣQs; Q_NREP = h_NREP(T_NREP − T); Q_rad = Fσε_MLI(T_NREP⁴ − T⁴); strap как бесконечная λ с контактными сопротивлениями (lumped 1 Вт/К); Q_FP = ψ·V_DC; провода — λ_eff = λi·(A_gauge·N_wires/A_wire).
- Тuning: X_(n+1) = X_n − d·(T_mod,n − T_exp)·(X_n − X_(n−1))/(T_mod,n − T_mod,n−1) (Secant/Newton, d = 0.5).

## Параметры переменного поля (если применимо)
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | не указана (steady-state зарядка flux pump) | — |
| f | не указана | — |
| Направление | не указано | — |
| Геометрия | 4 double-pancake, bore 64 мм, OD 90 мм; экран 1.15 кг | для AF-MPD |
| I_max | 18 А (рабочий), Ic 140 А (нормирован) | — |
| dI/dt | не указана | — |
| B_th | не указана | — |
| Потери | Q_FP = 400 мВт (flux pump); радиация >50% теплопритоков; strap 0.58 Вт/К; соединения <0.6 мВт | тепловой бюджет |

## Конструкция flux pump
- Transformer-based self-rectifier (архитектура Geng et al. 2016 [25]).
- Flux pump теплоприток ψ = 1–2 Вт/мВ.
- Пропитка/термические детали: не детализированы здесь (в [26, 27] Mallett et al.).
- Космос = вакуум → криостат не нужен; G10 струны, MLI, медный thermal bus + strap.

## Ограничения и замечания авторов
- Узкие тепловые запасы: T_NREP = 30 °C → превышение Tc; воротник 1.6 Вт/К реально (9.2 предсказано); gasket в 11 раз хуже.
- MLI хуже ожидаемого (0.034 vs 0.015) — мелкий магнит → много складок/швов; область для улучшения.
- Baseplate-NREP контакт плохой в вакууме (10 Вт/м²·К).
- Решение: radiative cooling криокулера (переделка), новое тестовое оборудование; работа в процессе.
- Радиационное воздействие космоса на Ic никогда не измерялось — не учтено (возможный результат миссии).
- Non-insulated катушки не моделировались в transient (будущие публикации).

## Связь с нашим проектом
- Раздел 2.4 (космос): **SWaP ограничения NREP (15 кг, 13 л, 100 Вт)**, требования ISS stray field 0.3 мТл @ 7 см, дизайн-философия малого спутника; кондукционное охлаждение <75 K при <100 Вт.
- Раздел 2.5 (потери): тепловые бюджеты — MLI, контактные сопротивления, strap, flux pump 400 мВт, квенч-защита (non-insulated).
- Раздел 2.3: transformer self-rectifier flux pump (Geng) для космоса.
- Раздел 2.1: Ic(B,θ,T), 40% от Ic при работе.
- Косвенно: сравнение с обычными электромагнитами AF-MPD (10–100 кВт!) — обоснование необходимости сверхпроводимости в космосе.

## Цитаты (дословные, с номером страницы/раздела)
> «conventional electromagnets consume between 10–100 kW of power solely for the magnet subsystem» (Section 1)
> «each watt of heat extracted at cryogenic temperatures requires at least 20 W of input power to the cryogenic cooling system» (Section 1)
> «NREP has a mass budget of 15 kg and volume budget of 13 L» (Section 2)
> «The critical temperature at the 0.3 T and 0.5 T field targets is 81 K and 77 K, respectively, so to provide a comfortable thermal margin, an HTS magnet temperature of under 75 K is preferred» (Section 3.1)
> «The geometry at 1.15 kg was therefore chosen as the optimum» (Section 3.1, магнитный экран)
> «an aluminium thermal collar was superior to a copper collar from a weight perspective: a conductance of 9.2 W/K can be achieved weighing only 0.45 kg» (Section 3.3)
> «the actual measured conductance was significantly lower at just 1.6 W/K» (Section 4.2)
