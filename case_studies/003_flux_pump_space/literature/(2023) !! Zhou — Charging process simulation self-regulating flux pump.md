# Zhou — Charging process simulation of a coil by a self-regulating high-Tc superconducting flux pump (2023)

## [Библиография]
Авторы: Pengbo Zhou, Yanyu Zhou, Mark Ainslie, Asef Ghabeli, Francesco Grilli, et al. (Southwest Jiaotong University; Cambridge; Karlsruhe)
Название: Charging process simulation of a coil by a self-regulating high-Tc superconducting flux pump
Журнал: Superconductivity 7, 100061 (2023)
Год: 2023
DOI: 10.1016/j.supcon.2023.100061
Тип: рецензируемая статья

## Релевантность проекту: 4/5
**Моделирование зарядки self-regulating flux pump (H-formulation + электрическая цепь)** — комбинированная FEM-модель: захватывает критические черты (сверхпроводящие свойства, влияние вторичного сопротивления); показано: добавление миллиомного нормального сопротивления в зарядный контур улучшает зарядку (макс. ток, скорость, потери). Заполняет 11 (моделирование). Дополняет Geng 2016 (self-regulating), Zhou 2020, Francis 2023.

## Суть работы
Численное моделирование зарядки катушки self-regulating HTS flux pump: комбинация H-formulation FEM + электрическая цепь. Модель захватывает: сверхпроводящие свойства, влияние вторичного сопротивления; согласуется с экспериментом (качественно и количественно). Ключевой результат: добавление миллиомного (нормального) сопротивления последовательно с зарядным контуром **улучшает** зарядку (макс. ток, скорость); раскрыто влияние на потери. Подход обобщаем для оптимизации различных flux pumps.

## Ключевые результаты
- **H-formulation FEM + электрическая цепь** — комбинированная модель.
- Захватывает: сверхпроводящие свойства, влияние вторичного сопротивления.
- Согласие с экспериментом (качественно + количественно).
- **Миллиомное сопротивление** в зарядном контуре → улучшение зарядки (макс. ток, скорость).
- Влияние на потери раскрыто.
- Обобщаемо для оптимизации flux pumps.
- Контекст: self-regulating требует меньше тепловыделяющих элементов в криостате.

## Теоретическая модель
- 2D FEM (H-formulation) + электрическая цепь (lumped-параметры).
- Self-regulating: асимметричный ток > Ic bridge → flux flow → выпрямление.

## Параметры (моделирование)
| Параметр | Значение | Примечание |
|----------|----------|------------|
| Модель | H-formulation FEM + circuit | |
| Тип | self-regulating HTS flux pump | |
| Сопротивление | миллиомное (вторичное) — улучшение | |
| Потери | раскрыты | |

## Связь с нашим проектом
- Раздел 11 (моделирование): комбинированная модель.
- Раздел 2.5 (потери): влияние сопротивления.
- Дополняет: Geng 2016, Francis 2023, Zhou 2020, Ghabeli 2021.

## Цитаты (дословные, с номером страницы/раздела)
> «The proposed model combines an H-formulation finite element method (FEM) model with an electrical circuit» (Abstract, p. 1)
> «we have demonstrated how the addition of a milliohm range, normal-conducting secondary resistance in series with the charging loop can improve the charging process» (Abstract, p. 1)
> «The modeling approach... can be generalized to the optimization and design of various types of flux pumps» (Abstract, p. 1)
