# Mallett — Effective circuit modelling and experimental realization of an ultra-compact self-rectifier flux pump (2023)

## [Библиография]
Авторы: B.P.P. Mallett, S. Venuturumilli, J. Clarke, B. Leuw, J.H.P. Rice, D.A. Moseley, C.W. Bumby, R.A. Badcock (Robinson Research Institute, VUW)
Название: Effective circuit modelling and experimental realization of an ultra-compact self-rectifier flux pump
Журнал: Superconductor Science and Technology 36, 065005 (2023)
Год: 2023
DOI: 10.1088/1361-6668/accd9c (arXiv:2210.12999)
Тип: рецензируемая статья (SUST)

## Релевантность проекту: 5/5
**Ультра-компактный self-rectifier FP + полная эффективная circuit-модель** — 65×65×50 мм, 320 А DC, 60 мВ пик; модель воспроизводит зарядку, ток, напряжение, форму. Прямой ответ на 2.3 (self-rectifier, компактность) и 11 (моделирование). Это FP, использованный в Hēki (цит. в Mallett 2024/2026). Дополняет Mallett 2024/2026 (космос), Geng 2020.

## Суть работы
Эксперимент и моделирование ultra-compact self-rectifier flux pump: устройство в объёме 65×65×50 мм, генерирует до **320 А DC** в катушку и **60 мВ** пикового напряжения. Полная электромагнитная эффективная circuit-модель воспроизводит: flux-pumping (self-rectification), максимальный ток, напряжение, форму волны. Фазы: зарядка (charging) и поддержание (maintenance — компенсация потока в сердечнике).

## Дизайн и параметры
- **Объём 65×65×50 мм** — ультра-компактный.
- **Трансформатор**: железный сердечник из 0.3 мм ламинаций; B_sat = 1.7 Тл (мягкое железо, комнатная температура); нелинейная проницаемость μ(H).
- **Bridge**: Cu-обмотка; номинальный self-field Ic ~35 А (факт ~30 А); длина bridge.
- **Нагрузка**: индуктивность 2.5 мкГн (комнатная); номинальный Ic ~500 А (факт ~462 А).
- **Соединения**: 450 нОм (из спада тока).
- **Вход**: i1 {19.8, −4.45} А при 10 Гц (асимметричный).
- LN2 (77 К); Takasago BWS 40-15 (bipolar linear).

## Результаты
- **320 А** в нагрузку за <3 с; **60–65 мВ** пик (начало), 20 мВ (насыщение).
- **Модель**: воспроизводит (i) self-rectification, (ii) макс. ток и напряжение, (iii) форму волны.
- **Чувствительность**: к Ic bridge (30/462 А vs номинал 35/500 А) — неоднородности/деформации.
- **Соединения**: 450 нОм (из спада тока).
- **Модель**: i1,max/i1,min зависимости воспроизведены (только форма волны менялась).
- **Погрешность**: 5% (ток нагрузки).
- **AC-потери/гистерезис**: сердечник приближается к насыщению (учтены).

## Теоретическая модель
- Эффективная circuit-модель: нелинейное сопротивление сверхпроводника (E-J, ур. 1), трансформатор с переменной проницаемостью R(H) = l·μ(H)⁻¹·A⁻¹, фазы зарядки/поддержания.
- Self-rectification: асимметричный ток primary → выпрямление.
- AC-потери и гистерезис сердечника (учтены).

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | нет (self-rectifier) | |
| f | 10 Гц (i1) | |
| Направление | нет | |
| Геометрия | ultra-compact 65×65×50 мм; air-core трансформатор (железо 0.3 мм, Bsat 1.7 Тл) | |
| I_max | 320 А (<3 с); 60-65 мВ пик | |
| Потери | соединения 450 нОм; AC/гистерезис | |

## Конструкция flux pump
Ultra-compact self-rectifier: трансформатор (мягкое железо, Bsat 1.7 Тл, 0.3 мм ламинации), bridge (Cu, Ic ~35 А), нагрузка (2.5 мкГн, Ic ~500 А), соединения 450 нОм; LN2; i1 19.8/−4.45 А, 10 Гц; Takasago BWS 40-15.

## Ограничения и замечания авторов
- Чувствительность модели к Ic (неоднородности, деформации).
- Соединения 450 нОм — оценка.
- Модель — описательная (не идеально предсказательная).
- Компактность — ключ для космических/портативных применений.
- AC-потери/гистерезис сердечника — учтены, но приближённо.

## Связь с нашим проектом
- Раздел 2.3 (self-rectifier): компактный, 320 А.
- Раздел 11 (моделирование): эффективная circuit-модель.
- Раздел 2.4 (космос): это FP для Hēki (Mallett 2024/2026).
- Дополняет: Mallett 2024/2026, Geng 2020, Leuw 2023.

## Цитаты (дословные, с номером страницы/раздела)
> «The device fits inside a volume of 65 × 65 × 50 mm and generates up to 320 A dc through the coil and a peak output voltage up to 60 mV» (Abstract, p. 1)
> «approximately 320 A was supplied to the load coil in under 3 s» (Sec. 3, p. 4)
> «our effective-circuit model reproduces; (i) flux-pumping via self-rectification, (ii) the approximate maximum load-coil current and the magnitude of the voltage across the coil and (iii) the approximate waveform» (Sec. 3, p. 4)
> «The primary... of Cu and has a nominal self-field Ic of 500 A at 77 K... inductance of 2.5 µH» (Sec. 2, p. 2)
