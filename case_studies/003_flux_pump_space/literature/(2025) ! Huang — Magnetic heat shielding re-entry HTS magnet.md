# Huang — Investigation of Magnetic Heat Shielding During Spacecraft Re-Entry Using HTS Magnet (2025)

## [Библиография]
Авторы: Xiyong Huang, Ben Parkinson, Nicholas Strickland, Steven Smart, Joseph Bailey, Vishnu Asokakumar Sreekala, Tulasi Parashar, Jakub Glowacki, Nicholas Long, Hubertus Weijers (Paihau-Robinson Research Institute, VUW)
Название: Investigation of Magnetic Heat Shielding During Spacecraft Re-Entry Using HTS Magnet – Preliminary Experimental Design
Журнал: IEEE Transactions on Applied Superconductivity 35(5), 4601006 (2025), Invited Paper
Год: 2025
DOI: 10.1109/TASC.2024.3521904
Тип: рецензируемая статья (Invited Paper)

## Релевантность проекту: 3/5
**Смежное космическое применение HTS-магнита (не flux pump)** — магнитное тепловое экранирование при входе в атмосферу: HTS-магнит 2 Тл для увеличения stand-off расстояния ударной волны (MHD-эффект) в ударной трубе DLR. Ценность: расширяет раздел 2.4 (космические применения ВТСП) за пределы AF-MPD; показывает техники проектирования HTS-магнитов (оптимизация катушек, non-insulated, криокулер). Не содержит накачки потока — релевантность 3/5 как контекст.

## Суть работы
Магнитное тепловое экранирование при входе в атмосферу: сильное магнитное поле отклоняет плазму ударной волны, увеличивая stand-off расстояние и снижая тепловую нагрузку. DLR ранее создавали 4.5 Тл импульсное поле медным магнитом (сильно ограничено теплом). Robinson построили HTS-магнит (ReBCO Faraday Factory) для непрерывного поля в ударной трубе DLR. Тело: закруглённый цилиндр OD 200 мм, Rc = 30 мм; катушки: 2 симметричных double-pancake, inner radius 15 мм, outer 61 мм, non-insulated (wet winding с проводящим encapsulant на основе силикона); криокулер (магнит при 14.4 К); целевое поле 2 Тл при 100 А на поверхности. Результаты: криокулер достиг 10 К baseline, магнит 14.4 К; I-V: при 55 А (1 Тл на оси) значительное напряжение в обоих панкейках — повреждение при намотке/охлаждении (расчётный Ic >300 А при 15 К); лимит 1 Тл. MHD-симуляция (OpenFoam, hy2Foam solver): при 2 Тл stand-off увеличивается с ~3 см до ~4 см, плотность в ударном слое растёт (2.5 → 25 г/м³), эффект неравномерен (у плеч — обратный).

## Ключевые результаты
- **Дизайн**: закруглённый цилиндр OD 200 мм; 2 симметричных double-pancake (inner 15 мм, outer 61 мм); 600 м проводника; non-insulated wet-wound.
- **Поле**: дизайн 2 Тл при 100 А; достигнуто 1 Тл при 55 А (повреждение катушек при намотке/охлаждении); Ic >300 А ожидался при 15 К.
- **Температуры**: cryocooler baseline 10 К; магнит 14.4 К (при 0.7 м расстоянии между магнитом и криокулером, 2 Вт первая стадия).
- **MHD-симуляция** (вход u0 = 5994 м/с, Ttr = 1187 К, Tv = 100 К): stand-off 3 см → 4 см при поле 2 Тл; плотность 2.5 → 25 г/м³; эффект неравномерный (у плеч обратный).
- **Сравнение с экспериментом**: измеренное поле по оси совпало с симуляцией.
- **Мотивация**: непрерывное поле vs импульсный медный магнит DLR 4.5 Тл.

## Теоретическая модель
- Магнитостатическое поле: ∇×∇×A = jm·μ (ур. 1) в OpenFoam.
- MHD-поток: hy2Foam solver (Navier-Stokes-Fourier extended), закон Ома j = σ(u×B) (ур. 2), проводимость Bush σ = σ0(T/T0)^n, σ0 = 5100 S/m, T0 = 12000 К, n = 2 (ур. 3).
- Сила Лоренца в уравнение импульса; джоулев нагрев в уравнение энергии.

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | нет (постоянный ток) | |
| f | нет | |
| Направление | осевое поле, перпендикулярно потоку плазмы | |
| Геометрия | 2 double-pancake non-insulated, OD 200 мм тело | |
| I_max | 55 А (1 Тл); дизайн 100 А (2 Тл) | |
| T | 14.4 К (магнит); 10 К (cryocooler baseline) | |
| Потери | не измерялись | |

## Конструкция (смежная, не flux pump)
HTS-магнит (ReBCO Faraday Factory) для ударной трубы DLR; non-insulated wet-wound (проводящий силиконовый encapsulant); криокулер на 0.7 м; медные токовводы с переходом в HTS; Hall-датчик для измерения поля.

## Ограничения и замечания авторов
- Повреждение катушек при намотке/охлаждении (плохой выбор encapsulant) — лимит 1 Тл вместо 2 Тл; новые катушки с модифицированным процессом.
- MHD-эффект неравномерен (у плеч обратный) — требуется детальный анализ теплового состояния.
- Цель — валидация MHD-моделей на эксперименте (2025).

## Связь с нашим проектом
- Раздел 2.4 (космос): применение HTS-магнита для теплового экранирования при входе (альтернатива AF-MPD).
- Раздел 2.5 (потери): техники конструирования non-insulated магнитов.
- Контекст: HTS-магниты в аэрокосмосе (Robinson), cryocooler-архитектура.

## Цитаты (дословные, с номером страницы/раздела)
> «DLR has previously created a 4.5 T pulsed field on the test model from a copper magnet... due to the enormous amount of heat generated from operating the copper magnet, the duration of the field was strongly limited» (Sec. I, p. 1)
> «a maximum of 1 T has been achieved on the surface of the cryostat at 55 A, compared to a design field of 2 T at 100 A» (Sec. VI, p. 4)
> «the shock stand-off distance increases from 3 cm to around 4 cm» (Sec. V, p. 4)
