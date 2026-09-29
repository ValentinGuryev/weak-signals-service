# Li — Charging Optimization of a YBCO Racetrack Coil With a Linear-Motor Type Flux Pump for an HTS Synchronous Motor (2021)

## [Библиография]
Авторы: Hong Li, Wei Wang, Xiaojun Niu, Jun Zheng, Yunfei Gao, Hanxin Ye, Yuntian Zhang, Jiafu Wei, Hang Xu, Qun Zhou, Xueshan Liu, Yong Lei, Boyang Shen (Sichuan University; Wuhan; Cambridge)
Название: Charging Optimization of a YBCO Racetrack Coil With a Linear-Motor Type Flux Pump for an HTS Synchronous Motor
Журнал: IEEE Transactions on Applied Superconductivity 31(8), 4603905 (2021)
Год: 2021
DOI: 10.1109/TASC.2021.3094425
Тип: рецензируемая статья

## Релевантность проекту: 4/5
**Зарядка NI racetrack катушки linear-motor flux pump (16.9 kW HTS-мотор)** — 3 статорных ленты (SSTC, THEVA), оптимизация длины волны; зарядка NI double racetrack (Ic 117 А, сопротивление с 48 А) при 77 К. Прямой ответ на 2.3 (машины, NI катушки) и 2.2 (длина волны). Дополняет Gao 2020, Wang 2022 (обзор, 16.9 kW).

## Суть работы
Зарядка NI double racetrack катушки (для 16.9-kW HTS-синхронного мотора) linear-motor flux pump (CSED — contactless superconducting excitation device). Три статорных ленты (SSTC-1, THEVA, SSTC-2) с измеренными соединениями (0.4752/0.3204/0.396 мкОм). NI racetrack (Ic 117 А при E0 = 1 мкВ/см; резистивная с 48 А), фиксация механическая (без эпоксида — сохраняет Ic). Оптимизация: 3 длины волны flux pump → лучшая комбинация (максимальный ток насыщения). Зарядка при 77 К.

## Ключевые результаты
- **NI double racetrack**: Ic 117 А (1 мкВ/см); резистивная с 48 А.
- **Статорные ленты**: SSTC-1 (0.4752 мкОм), THEVA (0.3204 мкОм), SSTC-2 (0.396 мкОм).
- **Оптимизация длины волны**: 3 варианта → лучшая (макс. ток насыщения).
- **Механическая фиксация** (без эпоксида) — сохраняет Ic, регулировка межвиткового давления.
- **Зарядка**: 77 К, linear-motor flux pump.
- Контекст: 16.9-kW HTS-мотор; CSED (brushless, без токовводов/колец).

## Теоретическая модель
- Linear-motor flux pump: 3-фазные обмотки + DC bias → бегущая волна → зарядка.
- NI racetrack (no-insulation) — ток между витками.

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | бегущая волна (linear-motor) | |
| λ | 3 варианта (оптимизация) | |
| Направление | ⊥ ленте | |
| Геометрия | 3 статорных ленты; NI racetrack (Ic 117 А) | |
| I_max | до Ic 117 А (цель) | |
| Потери | соединения 0.32–0.48 мкОм | |

## Конструкция flux pump
Linear-motor type (CSED): 3 статорных ленты (SSTC/THEVA), бегущая волна (3-фазные + DC); NI double racetrack (Ic 117 А); 16.9-kW HTS-мотор; 77 К.

## Ограничения и замечания авторов
- Эпоксидная пропитка снижает Ic — механическая фиксация лучше.
- Оптимум длины волны — эмпирический.
- NI coil: резистивная с 48 А (межвитковые токи).

## Связь с нашим проектом
- Раздел 2.3 (машины): 16.9-kW мотор, NI racetrack, CSED.
- Раздел 2.2 (длина волны): оптимизация.
- Раздел 2.5 (потери): соединения.
- Дополняет: Gao 2020, Wang 2022, Hamilton 2020.

## Цитаты (дословные, с номером страницы/раздела)
> «the critical currents of the coil is 117 A. The coil became resistive around IR = 48 A» (Sec. II-B, p. 2)
> «we tested three wavelengths of the flux pump, and chose the best combination... gave out the largest saturation current in the coil» (Sec. I, p. 2)
> «the joint resistance of SSTC-1, THEVA, and SSTC-2 were measured as 0.4752 μΩ, 0.3204 μΩ, and 0.396 μΩ» (Sec. II-A, p. 2)
