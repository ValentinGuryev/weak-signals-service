# Geng — An HTS flux pump operated by directly driving a superconductor into flux flow region in the E–J curve (2016)

## [Библиография]
Авторы: Jianzhao Geng, T.A. Coombs (Department of Engineering, University of Cambridge)
Название: An HTS flux pump operated by directly driving a superconductor into flux flow region in the E–J curve
Журнал: Superconductor Science and Technology 29, 095004 (2016)
Год: 2016
DOI: 10.1088/0953-2048/29/9/095004
Тип: рецензируемая статья (SUST)

## Релевантность проекту: 4/5
**Self-switching HTS flux pump (overcurrent)** — развитие Geng 2015: вместо AC-поля bridge переводится в flux flow превышением тока (асимметричный ток вторичной обмотки: положительный пик > Ic, отрицательный < Ic). Проще конструкции, без внешнего поля. Прямо отвечает на 2.3 (self-switching тип) и 2.1 (физика flux flow). Дополняет Geng 2015 (AC-field), Wang 2022 (overcurrent switch).

## Суть работы
Новый HTS flux pump: трансформатор со сверхпроводящей вторичной обмоткой, закороченной YBCO-«bridge». Высокий AC-ток индуцируется во вторичной обмотке с асимметричной формой (положительный пик ≫ отрицательного). Ток переводит bridge в flux flow только у положительного пика (превышение Ic bridge) → накачка. Нагрузка — double pancake 0.388 мГн (Ic 81 А); bridge 10 см, Ic 180 А; вторичная обмотка — параллельные YBCO-ленты (суммарный Ic 360 А); трансформатор 100:1; KEPCO-BOP 2020. Механизм проще существующих (без переключателей и внешнего поля). Ключевой вывод из Geng 2015: не нужно переводить HTS в нормальное состояние — переменное сопротивление (flux flow) достаточно.

## Ключевые результаты
- **Принцип**: асимметричный ток i(t) в контуре; только в области A (положительный пик) ток превышает Ic bridge → напряжение на нагрузке; в остальной части |i| < Ic.
- **Конструкция**: трансформатор 100:1; вторичная обмотка — параллельные YBCO (Ic 360 А); bridge 10 см (Ic 180 А); нагрузка 0.388 мГн (Ic 81 А).
- **Механизм**: flux flow в E-J кривой (без нормального состояния); переменное сопротивление HTS.
- **Простота**: без переключателей (heat/DC-field/AC-field) и без внешнего поля.
- Самонаводящийся (self-switching) — по аналогии с LTS self-switching pump.

## Теоретическая модель
- E-J кривая HTS: при J > Jc (flux flow) — напряжение; при J < Jc — сверхпроводящее.
- Асимметричный ток: i(t) с положительным пиком > Ic bridge и отрицательным < Ic → односторонняя накачка.

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | нет (самонаводящийся, без поля) | |
| f (частота) | частота i(t) (не приведена явно) | |
| Направление | нет | |
| Геометрия | трансформатор 100:1; bridge 10 см (Ic 180 А); нагрузка 0.388 мГн | |
| I_max | до Ic нагрузки 81 А (цель) | |
| Потери | flux flow в bridge (только у пика) | |

## Конструкция flux pump
Transformer-rectifier self-switching: трансформатор 100:1, вторичная (параллельные YBCO, Ic 360 А) + bridge (10 см, Ic 180 А) + нагрузка; KEPCO-BOP 2020 + NI-USB6002 (LabVIEW); LN2 77 К.

## Ограничения и замечания авторов
- Асимметрия тока критична (положительный пик > Ic, отрицательный < Ic).
- Работает в flux flow (без нормального состояния) — главное отличие от LTS.
- Bridge должна иметь Ic между пиками тока.

## Связь с нашим проектом
- Раздел 2.3 (конструкции): self-switching тип (без переключателей).
- Раздел 2.1 (физика): flux flow в E-J кривой.
- Раздел 2.2 (форма сигнала): асимметричный ток — форма влияет на накачку.
- Дополняет: Geng 2015 (AC-field), Wang 2022 (overcurrent), Coombs 2016 (обзор).

## Цитаты (дословные, с номером страницы/раздела)
> «The current always drives the bridge superconductor into the flux flow region only at around its positive peak value, thus resulting in flux pumping» (Abstract, p. 1)
> «The proposed flux pump is much simpler than existing HTS flux pumps» (Abstract, p. 1)
> «It is the variable resistivity of high-Tc superconductors that results in flux pumping» (Sec. 1, p. 2)
