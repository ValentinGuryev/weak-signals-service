# Fu — HTS Flux Pump Charging an HTS Coil: Experiment and Modeling (2021)

## [Библиография]
Авторы: Lin Fu, Koichi Matsuda, Boyang Shen, Tim Coombs (University of Cambridge)
Название: HTS Flux Pump Charging an HTS Coil: Experiment and Modeling
Журнал: IEEE Transactions on Applied Superconductivity 31(8), 9500805 (2021) (DOI 10.1109/TASC.2021.3090353)
Год: 2021
DOI: 10.1109/TASC.2021.3090353
Тип: рецензируемая статья

## Релевантность проекту: 4/5
**Модель зарядки катушки travelling wave flux pump (>90% Ic)** — L-R модель + E-J + динамическое сопротивление + э.д.с. (φ-модель, least-squares); эксперименты: ток >90% Ic. Прямой ответ на 11 (моделирование) и 2.1 (физика). Дополняет Fu 2015/2016, Wang 2022.

## Суть работы
Обновлённая модель travelling wave HTS flux pump для зарядки катушки: L-R цепь + E-J модель + динамическое сопротивление + э.д.с. (функция от φ, полиномиальные коэффициенты least-squares). Эксперименты: электромагнитный flux pump заряжает racetrack катушку; **индуцированный ток >90% Ic**; модель хорошо согласуется с экспериментом.

## Ключевые результаты
- **>90% Ic** (индуцированный ток).
- **Модель**: L-R + E-J + R_dyn + e.m.f. (φ-модель).
- **Least-squares** для полиномиальных коэффициентов.
- Хорошее согласие с экспериментом.
- Электромагнитный flux pump (без движущихся частей).

## Теоретическая модель
- L-R цепь зарядки; E-J (нелинейная резистивность); динамическое сопротивление; e.m.f. = f(φ).
- φ-модель (поток) + least-squares подгонка.

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | бегущая волна (электромагниты) | |
| Направление | ⊥ ленте | |
| Геометрия | racetrack катушка; электромагнитный FP | |
| I_max | >90% Ic | |

## Конструкция flux pump
Электромагнитный travelling wave flux pump (без движущихся частей): катушки → бегущая волна; racetrack-нагрузка.

## Ограничения и замечания авторов
- Модель — хорошая подгонка (least-squares).
- >90% Ic — высокий уровень зарядки.

## Связь с нашим проектом
- Раздел 11 (моделирование): L-R + E-J + R_dyn + e.m.f.
- Раздел 2.1 (физика): динамическое сопротивление.
- Дополняет: Fu 2015/2016, Wang 2022, Geng 2018.

## Цитаты (дословные, с номером страницы/раздела)
> «The induced current in superconducting coil can reach more than 90% of critical current» (Abstract, p. 1)
> «Our model was found to be a good fit to the experimental data» (Abstract, p. 1)
> «The proposed model has an electromotive force term... polynomial coefficients were identified using a least-squares method» (Sec. I, p. 1)
