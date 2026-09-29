# Leuw — A half-wave superconducting transformer-rectifier flux pump using Jc(B) switches (2022)

## [Библиография]
Авторы: Bradley Leuw, Jianzhao Geng, James H.P. Rice, Dominic A. Moseley, Rodney A. Badcock (Robinson Research Institute, VUW; Cambridge)
Название: A half-wave superconducting transformer-rectifier flux pump using Jc(B) switches
Журнал: Superconductor Science and Technology 35, 035009 (2022)
Год: 2022
DOI: 10.1088/1361-6668/ac4f3d
Тип: рецензируемая статья (SUST)

## Релевантность проекту: 5/5
**Новый тип переключателя: Jc(B) (DC-поле подавляет Jc)** — half-wave transformer-rectifier с DC-магнитными переключателями: зарядка 2.42 мГн нагрузки до 54.5 А (Ic) за 25 с, ripple ~1 А; **КПД: Jc(B) 92% vs dynamic resistance 50%** (расчёт); формулы КПД (ур. 1-3). Прямой ответ на 2.3 (новые переключатели) и 2.5 (КПД). Дополняет Leuw 2023 (PhD), Geng 2020, Wang 2022 (обзор).

## Суть работы
Разработка и экспериментальная проверка half-wave transformer-rectifier HTS flux pump с Jc(B) переключателями: выпрямление через E-J соотношение HTS с приложением DC-магнитных полей (поле подавляет Jc → переключатель в flux flow, «off»). Схема: понижающий трансформатор, Jc(B) переключатели Rs (series) и Rp (parallel), нагрузка. Фазы: (I) выпрямление (Rp в flux flow → vcoil → ток в нагрузку), (II) поддержание (Rs в flux flow, Rp сверхпроводящий). Нагрузка: double pancake 2.42 мГн (163 витка AMSC 4 мм, Ic 54.5 А). Результат: **54.5 А за 25 с**, ripple ~1 А; первое экспериментальное подтверждение Jc(B) switch rectifier. КПД: Jc(B) **92%** vs dynamic resistance **50%** (расчёт).

## Дизайн
- **Трансформатор**: понижающий; кремнистая сталь (Bsat ~1.4-1.9 Тл).
- **Переключатели**: Rs (series, 555 нОм), Rp (parallel, 830 нОм) — Jc(B), электромагниты.
- **Нагрузка**: double pancake 2.42 мГн (163 витка AMSC 4 мм, Ic 54.5 А при 77 К).
- **Мост/нагрузка loop resistance**: 4 мкОм (из спада).
- **Управление**: NI 9264 (3 сигнала: i1, Bp, Bs), LabVIEW; NI 9205 (1 кГц); Takasago BWS 40-15.
- **Фазы**: выпрямление (Rp off) / поддержание (Rs off).

## Результаты
- **54.5 А (Ic) за 25 с** (2.42 мГн нагрузка); ripple ~1 А.
- **vcoil**: первый цикл 205 мВ (пик).
- **КПД (расчёт)**: Jc(B) switch — **92%**; dynamic resistance — **50%**; сравнение с InnoST 1G Bi-2223 (абсолютная разница).
- **Формулы КПД**: η_Half = P_out/(P_I + P_II) (ур. 1); упрощение (ур. 2); максимальная эффективность (ур. 3) — IL/(IL + 2·Ic(Bapp)) и IL/(IL + Ic(Bapp)).
- **Оптимизация**: увеличение i1 с ростом iL (быстрее); повышение частоты/снижение поля в конце (меньше ripple).

## Теоретическая модель
- E-J соотношение HTS + DC-поле → Jc(B) → переключатель (flux flow).
- КПД: η_Half = ∫v_coil·i_L dt / (∫v_coil·i_L dt + ∫v_coil·i_B dt + ∫v_s·i_2 dt) (ур. 1-2).
- Максимальная эффективность (ур. 3): IL/(IL + 2Ic(Bapp)) (half-wave), IL/(IL + Ic(Bapp)).

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | DC-поля Bp, Bs (Jc(B) switch) | |
| f | не указана явно (AC primary) | |
| Направление | DC-поля на переключателях | |
| Геометрия | half-wave TRFP; Rs/Rp (Jc(B)); нагрузка 2.42 мГн | |
| I_max | 54.5 А (Ic нагрузки) | |
| Потери | КПД 92% (Jc(B)) vs 50% (dyn. res.); Rs 555 нОм, Rp 830 нОм | |

## Конструкция flux pump
Half-wave transformer-rectifier с Jc(B) switch: трансформатор (Si-сталь), Rs (series) + Rp (parallel) Jc(B) переключатели (электромагниты), нагрузка double pancake (2.42 мГн, Ic 54.5 А); LN2; Takasago BWS 40-15; NI 9264/9205.

## Ограничения и замечания авторов
- КПД Jc(B) 92% — значительно выше dynamic resistance (50%).
- Ripple ~1 А (можно уменьшить частотой/полем в конце).
- Быстрая зарядка — увеличением i1 с ростом iL.
- Первое подтверждение Jc(B) switch rectifier — открывает новую область.
- Low power efficiency HTSFP — мотивация.

## Связь с нашим проектом
- Раздел 2.3 (переключатели): Jc(B) — новый тип.
- Раздел 2.5 (КПД): формулы (1)-(3), 92% vs 50%.
- Раздел 2.2 (ток/время): 54.5 А/25 с.
- Дополняет: Leuw 2023 (PhD), Geng 2020, Wang 2022, Mallett 2026 (цитирует).

## Цитаты (дословные, с номером страницы/раздела)
> «A quasi-persistent current of 54.5 A has been... achieved... using Jc(B) switching» (Abstract, p. 1)
> «the load reaches its critical current of 54.5 A in 25 s» (Sec. 3, p. 3)
> «the maximum efficiency is only... IL/(IL + 2Ic(Bapp))... The absolute efficiency discrepancy between Jc(B) (92%) and dynamic resistance (50%) efficiency implies» (Sec. 4-5, p. 4-5)
> «Rs and Rp are 555 nΩ and 830 nΩ respectively» (Sec. 2, p. 2)
