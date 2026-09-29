# Wang — Review of high temperature superconducting flux pumps (2022)

## [Библиография]
Авторы: Wei Wang, Jiafu Wei, Chao Yang, Chenghuai Wu, Hong Li (College of Electrical Engineering, Sichuan University, Чэнду, Китай)
Название: Review of high temperature superconducting flux pumps
Журнал: Superconductivity 3, 100022 (2022), REVIEW
Год: 2022
DOI: 10.1016/j.supcon.2022.100022
Тип: рецензируемый обзор (Open Access, CC BY-NC-ND)

## Релевантность проекту: 5/5
Ключевой обзор (!!!), охватывающий ВСЕ типы HTS flux pumps с историями, принципами, тремя теориями DC-выхода, численными рекордами и применениями. Особенно ценен разделом 3.2 (HTS travelling wave): три теории происхождения DC-напряжения (dynamic resistance, over-critical eddy current, macroscopic magnetic coupling) — прямой ответ на вопросы 2.1, 2.2, 2.3 KEY_QUESTIONS.

## Суть работы
Обзор за десятилетие 2012–2022. Сначала кратко рассматриваются LTS flux pumps (раздел 2): dynamo-type (нормальное пятно, pumpbridge из Pb, PbIn, PbBi, Nb, NbZr, NbTa с Bc2 < 1.0 Тл; схема Tilley 1967 [46]) и transformer-rectifier (half/full-wave; три типа переключателей — magnetic, thermal, overcurrent [63]; переключатели дают 50–80% потерь схемы). Затем HTS flux pumps двух больших классов (раздел 3): transformer-rectifier (3.1) и travelling wave (3.2). В разделе 3.2 детально разбираются три теории происхождения DC-выхода одиночной YBCO-ленты (stator): (a) теория динамического сопротивления, (b) теория сверхкритических вихревых токов, (c) теория макроскопического магнитного сцепления. Раздел 4 — применения: HTS-машины (1 kW CRED, 16.9 kW brushless, 12 MW wind), NMR/MRI (2 Тл dynamo, portable 1.5 Тл с segmented excitation), fusion (60 kA для TF-катушек, CICC test bed).

## Ключевые результаты
**Динамическое сопротивление (раздел 3.1.1):**
- Пороговое поле (постоянный Jc, модель Бина): **B_a,th = μ0/(2w)·(I_c0 − I_t)** (ур. 1), где w — толщина (ширина) ленты, I_c0 — критический ток ленты.
- RMS динамическое сопротивление: **R_dyn = (4aLf)/(I_c0)·(B_a − B_a,th)** для B_a ≥ B_a,th (ур. 2), где L — эффективная длина ленты под AC-полем, f и B_a — частота и амплитуда. Линейно по f и B_a, не зависит от формы B_a(t).
- При высоких B_a (модель Кима, J_c = J_c0/(1+c|B|)): R_dyn = (4aLf)/(I_c0)·(B_a + c·B_a²) (ур. 3).
- Динамическое сопротивление доминируется ТОЛЬКО перпендикулярной компонентой поля (Jiang [70–72]); R_dyn — диссипативное (не ЭДС).
- Для коммерческой YBCO-ленты измерено Jiang для перпендикулярного [70], неперпендикулярного [71] поля и стопки из 4 лент [72].

**HTS transformer-rectifier (3.1):**
- Geng 2015 [40]: первый dynamic resistance switch; при AC-поле 20 Гц, 0.65 Тл, R_dyn = 0.106 мОм на мосте.
- Geng 2019 [48]: 7 лент моста → **I_max = 1100 А** (первый >1 kA).
- Geng 2016 [42]: overcurrent switch; в 2020 [43]: 12 лент secondary, 6 лент bridge, 5 лент load → **I_max = 2 kA**.
- Jc(B) switch (Leuw 2022 [44]): полностью зарядил HTS-нагрузку 2.42 мГн до 54.5 А за 25 с.
- Screening current switch (Geng 2021 [78]): full-wave, I_max > 500 А.
- Моделирование: 2D FEM H-formulation (Geng 2018 [80]) — достаточно E-J power law с постоянным Jc (ур. 8–10); Kirchhoff (ур. 11). Circuit models: SPICE (Gawith), Simulink (Li) — секунды против часов FEM.

**HTS travelling wave (3.2):**
- Три типа: HTS dynamo [14], linear-pulse field [22,23], linear-motor type [27–29].
- Три теории DC-выхода:
  - (a) Dynamic resistance: YBCO-stator как источник V_0 и R_eff; V_0 и R_eff линейно растут с частотой вращения; при зазоре > 7.5 мм накачка практически невозможна [58]; I_S = V_0/(R_eff + R_конт) ≈ V_0/R_eff; R_eff ~ в 10² раз больше паяных сопротивлений [57].
  - (b) Over-critical eddy current (Bumby 2016 [60], Mataira 2019 [61]): нелинейный ρ (E-J power law) — необходимое условие ненулевого V_dc (ур. 13–15); 2D FEM с постоянным Jc и J_c(B,θ) совпали с экспериментом [61]; модель воспроизвела V_dc ∝ f [62]. Эксперимент с DC-катушкой под статором [31] развернул выход (+69.5 А → −28.7 А) — этот эффект постоянное Jc в H-formulation воспроизвести не может.
  - (c) Macroscopic magnetic coupling (Wang 2018 [32]): **V_dc = l_eff·⟨B_v⟩·v** (ур. 19), где ⟨B_v⟩ — средняя плотность потока сцепленных вихрей, v — скорость бегущего полюса. Одиночный униполярный бегущий магнитный волнус: B_y(x,t) = B_ac·sin(kx−ωt) + B_dc (ур. 20). Максимум выхода при |B_dc| = B_ac [91]; при B_dc = 0 выход = 0 [27]. «Four-quadrant control» [32,31]: разворот B_dc или v разворачивает выход; точность стабилизации тока < 0.15 А [31].
- Технические рекорды:
  - Hoffman 2011 [14]: первый HTS dynamo, 49 А в 2.7 мГн катушку при 77 К через 12 мм YBCO ленту.
  - Squirrel-Cage dynamo (Hamilton [26,108]): 8 параллельных 12 мм лент, ~700 А измерено, экстраполяция ~1300 А.
  - Through-wall excitation [103]: >30 А при 77 К.
  - Linear-pulse (Fu [23]): 6 медных соленоидов, 3 параллельных YBCO-статора, 60° сдвиг фаз, асимметричные трапециевидные импульсы; Bai 2021 [22]: 155 А при 75 К; после оптимизации до 90% I_c катушки [113].
  - Linear-motor type: 2018 [27] 0.8 А → после оптимизации параметров волны (ур. 20) 135 А [30]; 2022 [29] single-sided DC winding: **220 А при 77 К**, размер ~¼ ладони (самый маленький >200 А); 2021 [114]: 10 параллельных статоров, >640 А; 2022 [30]: 12 параллельных статоров, **>1610 А**, размер ~½ листа A4.
- Применения: CRED в 1-kW машине [115,116]; 16.9 kW brushless HTS-машина [38,39]; 12 MW ветрогенератор [33]; NMR 2 Тл (0.4H, 110 А) [6]; portable 1.5 Тл MRI (4 флакс-пампа, −30% HTS-провода [35,36,37]); fusion 60 kA [56]; CICC test bed [30].

## Теоретическая модель
- Модель Бина (критическое состояние) для порога B_a,th и R_dyn.
- Модель Кима J_c(B) для высоких полей (ур. 3).
- E-J power law (ур. 9) + H-formulation (ур. 8) для FEM transformer-rectifier; ключевой вывод: постоянного Jc достаточно для transformer-rectifier (ур. 8–11), но недостаточно для dynamo (эксперимент с DC-полем [31]).
- Магнитное сцепление вихрей: сила сцепления F_c = (B1−B2)·I·l = ∇B·D·I·l (ур. 18) — пропорциональна градиенту поля; при однородном поле сцепления нет (согласуется с Giaever DC transformer 1965 [95–97]); масштаб сцепления 10⁻² м против 10⁻⁷ м у Giaever.

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac (амплитуда) | 0.65 Тл (dyn. resistance switch) | Geng [40] |
| f (частота) | 20 Гц (dyn. resistance); 1 Гц (kA-level, [48]); 50 Гц (overcurrent LTS) | [40],[43],[48] |
| Направление | B⊥ (перпендикулярно) — доминирует | Jiang [70–72] |
| Геометрия | одиночная YBCO-лента 12 мм; стопка 4 лент [72]; 12 параллельных статоров [30] | |
| I_max | 49 А (dynamo 2011) → 700 А (Squirrel-Cage) → 1300 А (экстрапол.) → 220 А (linear-motor) → >1610 А (12 статоров) | [14],[26],[29],[30] |
| B_th (порог) | B_a,th = μ0/(2w)·(I_c0−I_t) | ур. 1 [67] |
| V_dc | V_dc = l_eff·⟨B_v⟩·v (magnetic coupling) | ур. 19 [32] |
| Потери | R_dyn ∝ f·(B_a−B_a,th); переключатели 50–80% потерь (LTS) | [67],[63] |

## Конструкция flux pump
Все три типа travelling wave (dynamo с вращающимися магнитами, linear-pulse с электромагнитами, linear-motor с 3-фазными обмотками + DC bias) и transformer-rectifier (half/full-wave) с переключателями (dynamic resistance, overcurrent, Jc(B), screening current). YBCO-ленты 12 мм. Рабочие температуры: 77 К (LN2), 75 К. Магниты NdFeB ~1 Тл.

## Ограничения и замечания авторов
- DC-выход travelling wave — «сложный предмет», три теории конкурируют; H-formulation с постоянным Jc НЕ воспроизводит эффект DC-поля dynamo — нужны дальнейшие исследования J_c(B,θ).
- Макроскопическое магнитное сцепление — мощный инструмент оптимизации, но количественный метод ещё не разработан.
- Linear-pulse field pumps по механизму ближе к transformer-rectifier (разные скорости нарастания/спада).
- Для dynamo V_0 (ЭДС холостого хода) до сих пор не объяснена простым законом Фарадея [58].

## Связь с нашим проектом
- Раздел 2.1 (физика): формулы порога и динамического сопротивления, три теории.
- Раздел 2.2 (параметры поля): линейность по f и B_a; оптимальность |B_dc|=B_ac; зависимость от зазора (7.5 мм предел); V_dc ∝ f.
- Раздел 2.3 (конструкции): полная классификация типов и рекордов.
- Раздел 2.4 (космос): 12 MW wind, brushless-машины — контекст; fusion.
- Раздел 2.5 (потери): R_dyn, потери переключателей, AC-потери (не включены в модели).
- Разделы LIT_REVIEW: история (LTS), классификация типов, теория, параметры поля, рекорды.

## Цитаты (дословные, с номером страницы/раздела)
> «the dynamic resistance is dominated solely by the perpendicular field component» (Sec. 3.1.1, p. 5)
> «R_dyn is linearly dependent on f and Ba of the applied AC magnetic field, however, it is not dependent on the form of Ba(t)» (Sec. 3.1.1, p. 5)
> «it was almost impossible to pump any current when the air gap exceeded 7.5 mm» (Sec. 3.2.2, p. 10)
> «the theory of macroscopic magnetic coupling ... predicts that the maximum DC output occurs at |B_dc| = B_ac» (Sec. 3.2.2, p. 14)
