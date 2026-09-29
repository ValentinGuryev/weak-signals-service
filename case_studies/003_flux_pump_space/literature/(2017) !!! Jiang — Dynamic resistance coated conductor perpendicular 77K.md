# Jiang — Dynamic resistance of a high-Tc coated conductor wire in a perpendicular magnetic field at 77 K (2017)

## [Библиография]
Авторы: Zhenan Jiang, Ryuki Toyomoto, Naoyuki Amemiya, Xingyou Zhang, Chris W. Bumby (Robinson Research Institute, VUW; Kyoto University; Callaghan Innovation)
Название: Dynamic resistance of a high-Tc coated conductor wire in a perpendicular magnetic field at 77 K
Журнал: Superconductor Science and Technology 30, 03LT01 (2017), Letter
Год: 2017
DOI: 10.1088/1361-6668/aa54e5
Тип: рецензируемая статья (SUST Letter)

## Релевантность проекту: 5/5
**Фундаментальная формула динамического сопротивления для перпендикулярного поля (strip-геометрия)** — ключ для flux pump: R_dyn/L = (4af/Ic0)·(Ba − B_th) (ур. 4); B_th = 4.9284·μ0·Jc0·t/π·(1−i) (ур. 7, полоса); сравнение с slab (ур. 5), Ciszek (ур. 8), Mikitik-Brandt (ур. 9); флюкс-флоу слагаемое R_FF (ур. 10) при высоких токах. Эксперименты SuperPower (105.3 А) и Fujikura (266 А), до 112.5 Гц. Прямой ответ на 2.1 (физика) и 2.2 (порог B_th, амплитуда). Дополняет Wang 2022 (обзор, ур. 1-3), Jiang 2014.

## Суть работы
Экспериментальное измерение динамического сопротивления CC-лент (Wire A: SuperPower 4 мм, Ic0 = 105.3 А; Wire B: Fujikura 5 мм, Ic0 = 266 А) в перпендикулярном AC-поле (до 100 мТл, 112.5 Гц) при 77 К. Ключевые результаты: (1) начало R_dyn при пороговом поле B_th (определяется DC-током и полем проникновения); (2) нормированные магнито-потери дают однозначное B_p (полоса: B_p = 4.9284·μ0·Jc0·t/π); (3) R_dyn линейно по (Ba − B_th) (ур. 4) — согласуется с экспериментом для многих лент/частот; (4) B_th = B_p·(1−i) (ур. 7); (5) при высоких токах — дополнительный флюкс-флоу член R_FF (ур. 10), когда Ic(B) < I_t.

## Методика
- 15 см CC-лента в равномерном поле AC-магнита (100 мТл пик, до 112.5 Гц).
- 300 А DC-источник; voltage taps (5 см, индукционно-компенсированные); Keithley 2182.
- Wire A: SuperPower 4 мм, Ic0 = 105.3 А (1 мкВ/см); 20 мкм Cu (обе стороны).
- Wire B: Fujikura 5 мм, Ic0 = 266 А; 100 мкм Cu (только со стороны ReBCO).

## Ключевые результаты
- **R_dyn/L = (4af/Ic0)·(Ba − B_th)** (ур. 4) — линейно по (Ba − B_th), ∝ f, не зависит от частоты на цикл (гистерезис).
- **B_th (полоса)**: B_th = 4.9284·μ0·Jc0·t/π·(1−i) (ур. 7); B_p = 4.9284·μ0·Jc0·t/π; i = I_t/Ic0.
- **Сравнение**: slab B_th = B_p(1−i), B_p = μ0·Jc0·t (ур. 5); Ciszek (ур. 8, множитель 4/π); Mikitik-Brandt (ур. 9, нелинейный) — полоса-формула (7) лучше всего согласуется.
- **Флюкс-флоу R_FF** (ур. 10): при i > 0.5 и высоких Ba — дополнительный член (Ic(B) < I_t на части цикла).
- **Эксперименты**: Wire A (SuperPower, 105.3 А), Wire B (Fujikura, 266 А); согласие с (4)+(7) для i ≤ 0.5.
- **Согласие**: точное для многих лент (разные производители, размеры, Ic).
- B_th из x-intercept линейных фитов (для R_dyn > 0.1 мкОм/м/Гц).

## Теоретическая модель
- Strip-геометрия (перпендикулярное поле): полоса 2a × 2t, ток в центре (между −ai и +ai).
- Поле в полосе: B^⊥(y) = (μ0·t/2π)·∫J(u)/(y−u)du + Ba (ур. 1).
- Порог B_th из максимума нормированных магнито-потерь (Brandt): x = 2.4642 → B_p = 4.9284·μ0·Jc0·t/π (ур. 6).
- Мощность P = I_t·2ai·L·ΔB·f (ур. 3) → R_dyn (ур. 4).
- R_FF (ур. 10) — E-J power law.

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | до 100 мТл (пик), 112.5 Гц | |
| B_th | B_p·(1−i); B_p из (ур. 6) | |
| f | до 112.5 Гц; R_dyn ∝ f | |
| Направление | перпендикулярно ленте (полоса) | |
| Геометрия | 4 мм (SuperPower) / 5 мм (Fujikura) | |
| I_t | до i = 0.5+ (линейность); выше — R_FF | |
| Потери | R_dyn (гистерезис) + R_FF (флюкс-флоу) | |

## Конструкция (физика)
AC-магнит (100 мТл, 112.5 Гц), 15 см CC-лента, 300 А DC-источник, voltage taps (5 см, индукционно-компенсированные), Keithley 2182; 77 К.

## Ограничения и замечания авторов
- Для i > 0.5 — отклонение от линейности (флюкс-флоу R_FF).
- Формула (7) лучше всего для полосы; (9) Mikitik-Brandt может недооценивать B_th.
- Согласие для многих лент — универсальность подхода.
- R_dyn — диссипативные потери (теплоприток).
- Экранирующий эффект (Jc(B^) в центре больше среднего) — при i → 1.

## Связь с нашим проектом
- Раздел 2.1 (физика): ФУНДАМЕНТАЛЬНАЯ формула R_dyn (ур. 4) + B_th (ур. 7).
- Раздел 2.2 (порог/амплитуда): B_th, линейность по Ba.
- Раздел 2.5 (потери): R_dyn как теплоприток.
- Дополняет: Wang 2022 (обзор), Jiang 2014, Bumby 2016.

## Цитаты (дословные, с номером страницы/раздела)
> «The onset of dynamic resistance occurs at a threshold field amplitude, which is determined by the total DC transport current and the penetration field of the conductor» (Abstract, p. 1)
> «This approach implies a linear relationship between dynamic resistance and applied field amplitude, and also between threshold field and transport current» (Abstract, p. 1)
> «at high transport currents, the measured DC resistance includes an additional nonlinear term which is due to flux-flow resistance incurred by the DC transport current» (Abstract, p. 1)
> «Wire A was a 4 mm wide CC HTS wire manufactured by Superpower Inc. with a measured critical current Ic0 = 105.3 A... Wire B was a 5 mm wide CC HTS wire manufactured by Fujikura Ltd with a measured critical current Ic0 = 266.0 A» (Sec. 2, p. 4)
