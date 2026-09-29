# Francis — Electrical, magnetic and thermal circuit modelling of a superconducting half-wave transformer rectifier flux pump using Simulink (2023)

## [Библиография]
Авторы: A.C. Francis, S. Venuturumilli, D.A. Moseley, S. Claridge, B. Leuw, R.A. Badcock, C.W. Bumby (Robinson Research Institute, VUW; Open Star Technologies; MacDiarmid Institute)
Название: Electrical, magnetic and thermal circuit modelling of a superconducting half-wave transformer rectifier flux pump using Simulink
Журнал: Superconductivity 7, 100053 (2023)
Год: 2023
DOI: 10.1016/j.supcon.2023.100053
Тип: рецензируемая статья (Open Access)

## Релевантность проекту: 4/5
**Полная модель half-wave TRFP (электрика + магнит + тепло) в MATLAB/Simulink/Simscape** — первые полностью интегрированные характеристики всех элементов (look-up таблицы из экспериментов), включая тепловую эволюцию переключателей; показано, что малый нагрев переключателя сильно влияет на работу за много циклов. Заполняет 11 (моделирование) и 2.5 (тепловые эффекты). Дополняет Leuw 2022 (Jc(B)), Zhou 2023, Geng 2018.

## Суть работы
Модель half-wave магнитно-переключаемого (Jc(B)) transformer-rectifier FP в MATLAB/Simulink/Simscape: все элементы интегрированы; сверхпроводящие элементы — через look-up таблицы (экспериментальные характеристики); тепловая эволюция переключателей считается одновременно с магнитным переключением. Сравнение с реальным FP (Leuw 2022) — точность подтверждена. Ключевой вывод: малый нагрев магнитного переключателя может сильно изменить работу FP за много циклов. 5 элементов модели: форма волны, магнитная цепь трансформатора, электрическая вторичная цепь, сверхпроводящие компоненты, тепловые эффекты.

## Ключевые результаты
- **Полная интеграция**: электрика + магнит + тепло (Simscape).
- **Look-up таблицы**: экспериментальные характеристики сверхпроводящих элементов.
- **Тепловая эволюция** переключателей — одновременно с магнитным переключением.
- **Точность**: модель сравнивается с реальным FP (Leuw 2022) — согласуется.
- **Вывод**: малый нагрев магнитного переключателя → сильное влияние на работу за много циклов.
- 5 элементов: input waveform, transformer magnetic circuit, electrical secondary, superconducting components, thermal.

## Теоретическая модель
- Simscape: электрические, магнитные, тепловые библиотеки.
- Jc(B) switch (как Leuw 2022); E-J нелинейность.
- Look-up таблицы вместо аналитических приближений.

## Параметры (моделирование)
| Параметр | Значение | Примечание |
|----------|----------|------------|
| Модель | MATLAB/Simulink/Simscape | |
| Тип | half-wave TRFP, Jc(B) switch | |
| Элементы | 5 (waveform, transformer, secondary, SC, thermal) | |
| Тепло | эволюция переключателей | |

## Связь с нашим проектом
- Раздел 11 (моделирование): полная circuit-модель (электрика+магнит+тепло).
- Раздел 2.5 (потери): тепловые эффекты переключателей.
- Дополняет: Leuw 2022, Zhou 2023, Geng 2018, Mallett 2023.

## Цитаты (дословные, с номером страницы/раздела)
> «the characteristics of all circuit elements are fully integrated allowing all superconducting elements to be accurately incorporated» (Abstract, p. 1)
> «The thermal evolution of the switches, calculated simultaneously to the magnetic field switching interaction has also been included» (Abstract, p. 1)
> «the presented model illustrates how small amounts of heating at a magnetic switch can profoundly affect a FPs performance over many cycles» (Abstract, p. 1)
