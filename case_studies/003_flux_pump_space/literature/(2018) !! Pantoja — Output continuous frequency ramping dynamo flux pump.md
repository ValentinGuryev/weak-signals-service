# Pantoja — Output During Continuous Frequency Ramping of a Dynamo-Type HTS Flux Pump (2018)

## [Библиография]
Авторы: Andres E. Pantoja, James G. Storey, Rodney A. Badcock, Zhenan Jiang, Sinhoi Phang, Chris W. Bumby (Robinson Research Institute, VUW)
Название: Output During Continuous Frequency Ramping of a Dynamo-Type HTS Flux Pump
Журнал: IEEE Transactions on Applied Superconductivity 28(3), 5202205 (2018)
Год: 2018
DOI: 10.1109/TASC.2018.2793261
Тип: рецензируемая статья

## Релевантность проекту: 4/5
**Частотные режимы HTS dynamo при непрерывном разгоне** — три режима: low (V_dc ∝ f), mid (V_dc ~ const, нестабильна), high (V_dc ~ 1/f падает). Механизм: само-нагрев от eddy токов → частичный кванч ленты. Дополняет Bumby 2017 (частота) — здесь детально про режимы и разгон. Отвечает на 2.2 (частота, пределы).

## Суть работы
Изучение выхода HTS dynamo (2G ReBCO, 77 К) как функции частоты вращения магнитов при непрерывном разгоне. Конструкция: круговой массив тонких магнитов на высокоскоростном роторе, ReBCO-статор, железное ярмо, все движущиеся части вне криостата. Три частотных режима: low (V_dc ∝ f, модель работает, f < 50 Гц), mid (V_dc ~ const, нестабильна), high (V_dc падает ~1/f). Причина: само-нагрев eddy токов (EMF-driven) → частичный кванч ленты. Разгон: хорошая воспроизводимость в low/high, сложное поведение в mid.

## Ключевые результаты
- **Три режима**: low (V_dc ∝ f), mid (V_dc ~ const, нестабильна), high (V_dc ~ 1/f).
- **Low**: f < 50 Гц, модель частичного выпрямления работает.
- **Mid**: выход ~постоянен, нестабилен.
- **High**: V_dc падает ~1/f; само-нагрев eddy → частичный кванч.
- **Разгон**: воспроизводимость в low/high; сложное поведение в mid.
- >300 А в нагрузку (широкая лента, ранее [18-20]).
- Модель полной физики отсутствует — оптимизация эмпирическая.

## Теоретическая модель
- Частичное выпрямление (переменный шунт в статоре) — low f.
- Само-нагрев eddy токов (EMF-driven) → частичный кванч — high f.
- V_dc ∝ f (low); V_dc ~ 1/f (high).

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | поле тонких магнитов (массив) | |
| f | low < 50 Гц; mid; high (1/f) | |
| Направление | перпендикулярно ленте | |
| Геометрия | круговой массив магнитов; ReBCO-статор; железное ярмо | |
| I_max | >300 А (широкая лента) | |
| Потери | eddy само-нагрев (кванч) на high f | |

## Конструкция flux pump
HTS dynamo: высокоскоростной ротор с круговым массивом тонких магнитов, ReBCO-статор, железное ярмо; движущиеся части вне криостата; LN2.

## Ограничения и замечания авторов
- Модель полной физики отсутствует (оптимизация эмпирическая).
- High f: eddy нагрев → кванч → подавление выхода.
- Mid f: нестабильность (не воспроизводимо).

## Связь с нашим проектом
- Раздел 2.2 (частота): три режима, пределы (~50 Гц линейность, 1/f падение).
- Раздел 2.1 (физика): eddy само-нагрев.
- Раздел 2.3: dynamo (через-стенку).
- Дополняет: Bumby 2017, Pantoja 2016, Badcock 2017.

## Цитаты (дословные, с номером страницы/раздела)
> «In the "mid" frequency region, the dc output voltage is roughly constant with frequency, but is unstable. At "high" frequencies, the dc voltage drops with increasing frequency following an approximately 1/f dependence» (Abstract, p. 1)
> «We discuss our results in the context of self-heating due to EMF-driven eddy currents, leading to partial-quenching of the coated conductor wire» (Abstract, p. 1)
> «the dc voltage increases proportional to frequency» (Abstract, p. 1)
