# Hamilton — Practical estimation of HTS dynamo losses (2020)

## [Библиография]
Авторы: Kent A. Hamilton, Rodney A. Badcock, Chris W. Bumby (Robinson Research Institute, VUW)
Название: Practical estimation of HTS dynamo losses
Журнал: IEEE Transactions on Applied Superconductivity 30(4), 4703105 (2020)
Год: 2020
DOI: 10.1109/TASC.2020.2980830
Тип: рецензируемая статья

## Релевантность проекту: 5/5
**Измерение потерь и КПД Squirrel-Cage HTS dynamo (kA-класс)** — максимум ~1700 А, 3.78 мВ при 600 RPM; сравнение с электронным ИП; **КПД ~10%** (цитируется в Mallett 2026); источники потерь (вязкое трение LN2, магнитное трение ярма, AC-потери). Прямой ответ на 2.5 (потери, КПД). Дополняет Hamilton 2018 (squirrel-cage), Mallett 2026.

## Суть работы
Измерение потерь и эффективности Squirrel-Cage HTS dynamo (Robinson, 8 статоров + 4 Nd-Fe-B магнита): torque-датчик (Proza PZTO21, ±1.5 Нм, ±0.2%), вход Pin = ω·τ (ур. 2), выход Pout = V·I (ур. 1), КПД η = Pin/Pout (ур. 3). Сравнение: электронный ИП (комнатная температура) vs HTS dynamo. Результаты: максимум ~1700 А, 3.78 мВ (600 RPM); V-I линейна (динамическое сопротивление); потери без статоров: вязкое трение LN2 + магнитное трение ярма. Контекст: dynamo передаёт мощность в криогенную цепь через стенку (беспроводно).

## Дизайн и методика
- **8×12 мм CC-ленты** на цилиндрическом железном ярме; шины (bus rings) 4×4.5 мм BSCCO (Di-BSSCO, >200 А) + 2×Sunam (SAN12600) 12 мм ReBCO (>500 А); flyleads Fujikura 10 мм (>500 А).
- **Усиление до >2 кА** (первоначально оценка 1800 А; ограничение — другие части цепи до 700 А).
- **Torque-сенсор**: Proza PZTO21 между мотором и ротором; ±1.5 Нм, ±0.2% (мотор 1.3 Нм при 3000 RPM).
- **Pin = ω×τ** (ур. 2, валовая мощность); **Pout = V×I** (ур. 1); **η = Pin/Pout** (ур. 3).
- 2×Agilent 6680 A 1 kA (эмуляция HTS-катушки [17]).
- Voltage taps на flyleads.

## Результаты
- **Максимум ~1700 А**; 3.78 мВ (600 RPM, максимум).
- **V-I линейна** (динамическое сопротивление); линейный коэффициент меняется с частотой.
- **КПД ~10%** (Mallett 2026 ссылается; здесь измерено).
- **Потери без статоров**: вязкое трение LN2 (ротор), магнитное трение (ярмо).
- **Сравнение**: dynamo vs электронный ИП (мощность для ввода/поддержания тока).
- Согласие с ранними низкотоковыми измерениями [16].

## Теоретическая модель
- Pout = V×I (ур. 1); Pin = ω×τ (ур. 2); η = Pin/Pout (ур. 3).
- Динамическое сопротивление (V-I линейна).
- Потери: LN2 drag, магнитное трение ярма, AC-потери (статоры).

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | 4 Nd-Fe-B магнита | |
| f | до 600 RPM (10 Гц) | |
| Направление | ⊥ лентам (осевое) | |
| Геометрия | 8 статоров (12 мм) + 4 магнита | |
| I_max | ~1700 А | |
| V_max | 3.78 мВ (600 RPM) | |
| Потери | трение LN2, ярмо, AC; КПД ~10% | |

## Конструкция flux pump
Squirrel-Cage HTS dynamo: 8×12 мм CC-ленты (ярмо), 4 Nd-Fe-B, шины BSCCO + ReBCO (Di-BSSCO), flyleads Fujikura; torque-сенсор; через-стенка.

## Ограничения и замечания авторов
- Потери трения (LN2, ярмо) — заметны.
- КПД ~10% (низкий, но беспроводная передача).
- Усиление шин до >2 кА (первоначально 1800 А оценка).
- AC-потери (статоры) — ранее не исследованы; здесь измерены.

## Связь с нашим проектом
- Раздел 2.5 (потери): КПД ~10%, источники потерь.
- Раздел 2.3 (конструкции): squirrel-cage.
- Раздел 2.4 (космос): цитируется в Mallett 2026 (сравнение КПД).
- Дополняет: Hamilton 2018, Mallett 2026, Wang 2022.

## Цитаты (дословные, с номером страницы/раздела)
> «the maximum current output is ≈1700 A. The maximum voltage delivered varies with angular frequency, and is 3.78 mV for the maximum shaft speed tested of 600 RPM» (Sec. III, p. 3)
> «the dynamo transmits this power into the closed cryogenic HTS circuit wirelessly through the cryostat wall» (Sec. I, p. 2)
> «the losses and efficiency of a Squirrel Cage HTS dynamo... are compared using the measured experimental data» (Sec. I, p. 2)
> «the torque sensor specified is ±1.5 Nm, with an accuracy of ±0.2%» (Sec. II, p. 3)
