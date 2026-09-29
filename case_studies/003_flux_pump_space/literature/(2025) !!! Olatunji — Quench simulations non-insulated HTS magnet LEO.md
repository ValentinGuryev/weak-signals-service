# Olatunji — Quench Simulations of a Non-Insulated Compact HTS Magnet for Deployment in Low-Earth Orbit (2025)

## [Библиография]
Авторы: Jamal R. Olatunji, Max Goddard-Winchester, Celine M. Jane, Benjamin P.P. Mallett, Nicholas M. Strickland, Avinash A. Rao, Betina E. Pavri, Randy Pollock (Paihau-Robinson Research Institute, VUW)
Название: Quench Simulations of a Non-Insulated Compact HTS Magnet for Deployment in Low-Earth Orbit
Журнал: IEEE Transactions on Applied Superconductivity 35(5), 4901005 (2025)
Год: 2025
DOI: 10.1109/TASC.2024.3509830
Тип: рецензируемая статья

## Релевантность проекту: 5/5
**Кванч-безопасность NI HTS-магнита для космоса (Hēki)** — симуляции кванча non-insulated магнита в космических условиях: NI-катушки повышают кванч-устойчивость (обмен током между витками, термическая стабильность, меньше горячих точек); без сложных схем защиты. Прямой ответ на 2.4 (космос, надёжность) и 2.5 (кванч). Дополняет Strickland 2026 (магнит) и Pavri 2026 (квалификация).

## Суть работы
Симуляции кванча non-insulated (NI) HTS-магнита миссии Hēki (МКС, 2025). NI-катушки: отсутствие межвитковой изоляции позволяет обмен током между витками при кванче → улучшенная термическая стабильность, меньше горячих точек, повышенная кванч-устойчивость. Симуляции в типичных космических условиях: NI-магнит справляется с кванч-событиями без сложных схем защиты — преимущество для простоты и надёжности в космосе. Контекст: HTS-магниты для AF-MPD (снижение входной мощности в 100+ раз, поле ×4 [6]), радиационное экранирование [8], детекторы [9]. Кванч — внезапный переход в нормальное состояние (постоянное повреждение [10-12]).

## Ключевые результаты
- **NI-катушки**: обмен током между витками при кванче → термическая стабильность, меньше горячих точек.
- **Кванч-толерантность**: NI-магнит справляется без сложных схем защиты.
- **Космические условия**: симуляции (типичные условия LEO/ISS).
- **Мотивация**: HTS + AF-MPD снижает входную мощность в 100+ раз, поле ×4 (vs обычные) [6].
- Применения HTS-магнитов в космосе: AF-MPD, радиационное экранирование [8], детекторы [9].
- Поддержка применимости NI-технологии в будущих космических двигателях.

## Теоретическая модель
- NI-намотка: межвитковое сопротивление (частичная проводимость) → перераспределение тока.
- Электромагнитное + тепловое моделирование кванча.
- Сценарии космической среды.

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | нет (постоянный ток) | |
| f | нет | |
| Направление | нет | |
| Геометрия | NI HTS-магнит (Hēki, 4 double-pancake) | |
| Потери | кванч-события (моделирование) | |

## Конструкция (смежная)
NI HTS-магнит Hēki (4 double-pancake, wet-wound с проводящим эпоксидом); cryocooler + flux pump; МКС (NREP).

## Ограничения и замечания авторов
- NI-технология упрощает защиту (без сложных схем) — преимущество для космоса.
- Симуляции подтверждают кванч-толерантность.
- (Численные результаты — по графикам; контекст — надёжность миссии).

## Связь с нашим проектом
- Раздел 2.4 (космос): кванч-безопасность NI-магнита для МКС.
- Раздел 2.5 (потери/кванч): NI-толерантность.
- Дополняет: Strickland 2026 (магнит), Pavri 2026 (квалификация), Olatunji 2024 (pathfinder).

## Цитаты (дословные, с номером страницы/раздела)
> «NI HTS coils can enhance quench resistance and tolerance because the absence of turn-to-turn insulation allows current sharing during quench events, improving thermal stability and reducing the risk of hot spots» (Abstract, p. 1)
> «Simulations under typical space conditions demonstrate that NI magnets can manage quench events without complex protection circuits, which is advantageous for the simplicity and reliability required in space applications» (Abstract, p. 1)
> «the use of HTS magnets with AF-MPD thrusters lowered the input power by over 100 times and increased the applied magnetic field by over 4 times compared to conventional AF-MPD thrusters» (Sec. I, p. 1)
