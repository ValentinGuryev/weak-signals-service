# Rice — A full-wave HTS flux pump using a feedback control system (2023)

## [Библиография]
Авторы: James H.P. Rice, Ben P.P. Mallett, Dominic A. Moseley, Alexander Petrov, Heng Zhang, Steven Wray, Rodney A. Badcock (Robinson Research Institute, VUW; HTS-110)
Название: A full-wave HTS flux pump using a feedback control system
Журнал: Superconductivity 8, 100064 (2023)
Год: 2023
DOI: 10.1016/j.supcon.2023.100029 (из имени файла S2772830723000297)
Тип: рецензируемая статья (Full Length Article)

## Релевантность проекту: 4/5
**Полноволновый HTS flux pump с feedback control** — отрицательный DC-офсет во вторичной обмотке (от намагничивания сердечника) ограничивает выход; увеличение primary тока пропорционально load току → выход **с 35 А до >275 А**; воспроизведено coupled electrical/magnetic-circuit моделью. Прямой ответ на 2.3 (full-wave, feedback) и 2.5 (потери). Дополняет Geng 2020, Mallett 2023, Francis 2023.

## Суть работы
Полноволновый (full-wave, center-tapped) HTS flux pump: трансформатор с center-tapped вторичной (N21 = N22 = 2), переключатели (applied magnetic field, dynamic resistance + нелинейная резистивность). Ключевая проблема: **отрицательный DC-офсет во вторичной обмотке** (от намагничивания ферритового сердечника), связанный с load током, ограничивает выход. Решение: **feedback control** — увеличение primary тока пропорционально load току → выход **с 35 А до >275 А**. Воспроизведено coupled electrical/magnetic-circuit моделью. Лента SCN12700 (Ic 798 А, n ≈ 45 при 77 К).

## Ключевые результаты
- **35 А → >275 А** (увеличение primary тока пропорционально load току).
- **Отрицательный DC-офсет** во вторичной (от намагничивания сердечника) — ограничение.
- **Feedback control**: primary ток ∝ load ток → компенсация.
- **Full-wave**: center-tapped secondary; ниже ripple (чем half-wave).
- Воспроизведено coupled electrical/magnetic-circuit моделью.
- Лента SCN12700 (Ic 798 А, n ≈ 45, 77 К).
- Full-wave — преимущество (низкий ripple, высокий ток) vs LTS (Ishmael — не построен).

## Теоретическая модель
- Full-wave center-tapped transformer rectifier; dynamic resistance + нелинейная резистивность.
- DC-офсет от намагничивания сердечника.
- Coupled electrical/magnetic-circuit модель (воспроизводит).

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | applied magnetic field (переключатели) | |
| f | ~1 Гц (primary) | |
| Направление | ⊥ ленте (переключатели) | |
| Геометрия | full-wave center-tapped; SCN12700 (Ic 798 А) | |
| I_max | >275 А (с feedback) | |
| Потери | внутреннее сопротивление = паяные соединения | |

## Конструкция flux pump
Full-wave HTS TRFP: трансформатор (center-tapped secondary N=2), переключатели (applied field), нагрузка; feedback control (primary ток).

## Ограничения и замечания авторов
- DC-офсет — фундаментальное ограничение full-wave (намагничивание сердечника).
- Feedback control — решение (primary ∝ load).
- Воспроизводимость моделью — подтверждение.

## Связь с нашим проектом
- Раздел 2.3 (full-wave, feedback): конструкция.
- Раздел 2.5 (потери): внутреннее сопротивление.
- Раздел 11 (модель): coupled circuit.
- Дополняет: Geng 2020, Mallett 2023, Francis 2023, Leuw 2022.

## Цитаты (дословные, с номером страницы/раздела)
> «Increasing the primary current proportional to the load current during operation allowed for the maximum output of the flux pump to be increased from 35 A to more than 275 A» (Abstract, p. 1)
> «a negative DC offset in secondary current develops, limiting the voltage and current output of the device» (Sec. 1, p. 3)
> «This feedback control system is then demonstrated in both experiment and simulation to increase load current output» (Sec. 1, p. 3)
