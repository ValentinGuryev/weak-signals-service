# Geng — Mechanism of a high-Tc superconducting flux pump: Using alternating magnetic field to trigger flux flow (2015)

## [Библиография]
Авторы: Jianzhao Geng, T.A. Coombs (Department of Engineering, University of Cambridge)
Название: Mechanism of a high-Tc superconducting flux pump: Using alternating magnetic field to trigger flux flow
Журнал: Applied Physics Letters 107, 142601 (2015)
Год: 2015
DOI: 10.1063/1.4932950
Тип: рецензируемая статья (APL)

## Релевантность проекту: 5/5
**ФИЗИЧЕСКИЙ ФУНДАМЕНТ transformer-rectifier HTS flux pump** — первый ясный механизм: высокочастотное AC-поле на «bridge» (участок YBCO-ленты) при одном направлении транспортного тока вызывает flux flow → динамическое сопротивление → накачка. Формулы: R_dyn = (4alf/Ic0)(Ba + c·Ba²) (ур. 1), баланс потока ΔΦ (ур. 2–4), аналитическое решение iL = A(1−e^(−t/τ)) (ур. 6). Числа: R_dyn = 0.131 мОм (0.106 мОм при DC), R_L = 3.73 мкОм, iL = 57.5(1−e^(−t/24)). Прямой ответ на вопросы 2.1 (физика) и 2.2 (амплитуда/частота поля).

## Суть работы
Предложен и экспериментально подтверждён механизм HTS flux pump: две токовые петли (charging loop и closed superconducting load loop) соединены HTS-«bridge» (кусок YBCO-ленты). Низкочастотный AC-ток ip индуцируется в charging loop трансформатором (200:2). Высокочастотное AC-поле Ba (перпендикулярно ленте) периодически прикладывается к bridge, когда ток достигает одной полярности → flux flow → динамическое сопротивление R_dyn → напряжение на bridge заряжает нагрузку.

## Механизм и модель
- **R_dyn** (высокое поле): R_dyn = (4alf/Ic0)·(Ba + c·Ba²) (ур. 1) — a — полуширина, l — длина под полем, f — частота поля, Ic0 — критический ток, c — фактор Jc(B); по Bean c = 0.
- **Баланс потока**: ΔΦ_on = (Ip − iL)·R_dyn·pT − iL·R_L·pT (ур. 2); ΔΦ_off = −iL·R_L·(1−p)T (ур. 3); ΔΦ = Ip·R_dyn·pT − iL·T·(R_dyn·p + R_L) (ур. 4).
- **Аналитическое решение**: L·diL/dt = Ip·R_dyn·p − iL·(R_dyn·p + R_L) (ур. 5); iL = A(1−e^(−t/τ)), A = Ip/(1 + R_L/(R_dyn·p)), τ = L/(R_L + R_dyn·p) (ур. 6).
- Переключение: Ba прикладывается при положительной полярности ip → bridge резистивна (зарядка); Ba снята → bridge сверхпроводящая (шунт нагрузки).

## Эксперимент
- **Bridge**: 35×6 мм² (YBCO 6 мм; в зазоре 1 мм электромагнита 36 мГн, железный сердечник 35×12 мм); Ic 123 А в зазоре (1 мкВ/см).
- **Трансформатор**: 200:2 (индукция ip).
- **ip ~90 А, 2 Гц**; **Ba 0.65 Тл, 20 Гц** (прикладывается 0.05 с/цикл).
- **Нагрузка**: double pancake 0.388 мГн, Ic 81 А (77 К).
- **Соединения**: 1.2×10⁻⁷ Ом (joint).
- **Управление**: LabVIEW + 2×Kepco, NI-USB6002.

## Результаты
- **iL = 57.5(1−e^(−t/24)) (ур. 7)** — совпало с моделью.
- **R_dyn = 0.131 мОм** (из фита); **0.106 мОм** (DC-измерение, 20 Гц/0.65 Тл); в flux pump чуть больше (эффективная частота 20–30 Гц).
- **R_L = 3.73 мкОм** (≫ соединение 1.2×10⁻⁷ Ом).
- **По Oomen (Bean)**: R_dyn = 0.044 мОм — меньше половины измеренного; разница из-за Jc(B) зависимости (полевая).
- **R_L растёт** при iL > 35 А (после 50 циклов): 0.4 → ~4 мкОм (iB = ip + iL > Ic bridge → ток через медный слой).
- **Порог**: накачка при положительной полярности (iB не меняет полярность).
- **Ключевой вывод**: накачка возможна без перевода HTS в нормальное состояние (только flux flow) — прорыв.

## Теоретическая модель
- Динамическое сопротивление (ур. 1), баланс потока за цикл (ур. 2–4), дифференциальное уравнение зарядки (ур. 5), решение (ур. 6).
- Flux flow при DC-токе + перпендикулярном AC-поле (Bean model, рис. 1b).

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | 0.65 Тл (AC-поле на bridge) | 20 Гц, 0.05 с/цикл |
| f (частота) | ip 2 Гц; Ba 20 Гц | |
| Направление | Ba ⊥ ленте (в зазоре электромагнита) | |
| Геометрия | bridge 35×6 мм² (YBCO 6 мм); трансформатор 200:2; нагрузка 0.388 мГн | |
| I_max | iL до 57.5 А (насыщение); Ic нагрузки 81 А | |
| R_dyn | 0.131 мОм (флюкс-памп); 0.106 мОм (DC) | |
| Потери | R_L 3.73 мкОм → 4 мкОм (после 50 циклов) | |

## Конструкция flux pump
Transformer-rectifier с dynamic resistance switch: трансформатор 200:2 (индукция ip), электромагнит 36 мГн (Ba, железный сердечник 35×12 мм, зазор 1 мм), bridge (6 мм YBCO, Ic 123 А в зазоре), нагрузка double pancake 0.388 мГн (Ic 81 А); LN2 77 К; LabVIEW + Kepco, NI-USB6002.

## Ограничения и замечания авторов
- Для больших токов нужна более широкая лента bridge (чтобы ip + iL не превышали Ic).
- R_dyn по Oomen/Bean недооценивает (нужна Jc(B)).
- R_L растёт при высоких токах (медный слой bridge).
- Ba прикладывается коротко (0.05 с) — эффективная частота выше 20 Гц.

## Связь с нашим проектом
- Раздел 2.1 (физика): механизм flux flow + динамическое сопротивление; формулы.
- Раздел 2.2 (амплитуда/частота): Ba 0.65 Тл/20 Гц; ip 2 Гц; R_dyn ∝ f·Ba.
- Раздел 2.3: transformer-rectifier с dynamic resistance switch.
- Раздел 2.5 (потери): R_dyn, R_L.
- Дополняет: Wang 2022 (обзор), Coombs 2016, Geng 2016 (self-switching), Geng 2018 (H-formulation).

## Цитаты (дословные, с номером страницы/раздела)
> «flux flow can be triggered when the superconductor carrying a direct current is subjected to a perpendicular AC magnetic field» (Abstract, p. 142601-1)
> «The proposed flux pump has clear physics and is easily controllable» (Abstract, p. 142601-1)
> «The proposed mechanism achieved flux pumping without driving high-Tc superconductor normal by high field, which is a main breakthrough» (p. 142601-3)
> «ip had a magnitude of about 90 A and a frequency of 2 Hz. Ba had a frequency of 20 Hz with a magnitude of 0.65 T» (p. 142601-2)
