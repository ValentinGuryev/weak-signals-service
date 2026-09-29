# Gawith — A half-bridge HTS transformer–rectifier flux pump with two AC field-controlled switches (2018)

## [Библиография]
Авторы: J.D.D. Gawith, J. Geng, C. Li, B. Shen, X. Zhang, T.A. Coombs (University of Cambridge)
Название: A half-bridge HTS transformer–rectifier flux pump with two AC field-controlled switches
Журнал: Superconductor Science and Technology 31, 085002 (2018)
Год: 2018
DOI: 10.1088/1361-6668/aac86d
Тип: рецензируемая статья (SUST)

## Релевантность проекту: 4/5
**Half-bridge TRFP с двумя AC-полевыми переключателями + SPICE-модель** — теория, прототип, сравнение с SPICE (хорошее качественное согласие); все waveforms (ток, напряжение, мощность) — впервые. Заполняет 2.3 (полумост) и 11 (SPICE-моделирование). Дополняет Geng 2015 (AC-полевой switch), Gawith 2019 (оптимизация), Wang 2022.

## Суть работы
Half-bridge HTS transformer-rectifier flux pump с двумя AC-полевыми HTS-переключателями (S1, S2). Теория работы → упрощённая SPICE-модель → прототип → сравнение. Хорошее качественное согласие. Впервые представлен анализ всех waveforms (ток, напряжение, мощность). Вывод: SPICE — полезный инструмент для дизайна будущих flux pumps. Переключатели: AC-поле на участки HTS (импеданс 100 мкОм ↔ 1 нОм).

## Ключевые результаты
- **Half-bridge**: два AC-полевых переключателя (S1, S2).
- **SPICE-модель**: импеданс S1/S2 варьируется синхронно с primary (100 мкОм ↔ 1 нОм); согласуется с экспериментом (качественно).
- **Все waveforms** (ток, напряжение, мощность) — впервые.
- **Нагрузка**: Ic 35 А, n = 10 (в модели); primary 6 А (треугольный).
- **Первый анализ** всех waveforms для HTS flux pump.
- **SPICE** — инструмент дизайна.

## Теоретическая модель
- TRFP: трансформатор (L1/L2) + переключатели (S1/S2) + нагрузка; AC-поле управляет импедансом S1/S2.
- SPICE: импеданс 100 мкОм (off) ↔ 1 нОм (on).

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | AC-поля на S1/S2 | |
| f | синхронно с primary | |
| Направление | ⊥ ленте (переключатели) | |
| Геометрия | half-bridge; S1/S2 (AC-полевые) | |
| I_max | ~35 А (Ic нагрузки) | |
| Потери | проанализированы (мощность) | |

## Конструкция flux pump
Half-bridge TRFP: трансформатор (primary 6 А), два AC-полевых HTS-переключателя, нагрузка (Ic 35 А); SPICE-модель.

## Ограничения и замечания авторов
- Качественное (не количественное) согласие SPICE.
- Отрицательное напряжение на нагрузке (неправильный тайминг переключателей) — улучшение на будущее.
- Первый полный анализ waveforms.

## Связь с нашим проектом
- Раздел 2.3 (полумост): два переключателя.
- Раздел 11 (моделирование): SPICE.
- Раздел 2.5 (потери): waveforms мощности.
- Дополняет: Geng 2015, Gawith 2019, Wang 2022.

## Цитаты (дословные, с номером страницы/раздела)
> «There is good qualitative agreement between simulation and experiment and all current, voltage and power waveforms from experiment are presented» (Abstract, p. 1)
> «SPICE simulation can provide designers of future HTS flux pumping systems with a useful tool for making design decisions» (Abstract, p. 1)
> «this is the first time an analysis of all voltage, current and power waveforms has been given for an HTS flux pump» (Sec. 1, p. 2)
