# Acheson — Operation of a plasma thruster featuring a 1.1 T high temperature superconducting magnet (2024)

## [Библиография]
Авторы: Chris R. Acheson, Kiyoshi Kinefuchi, Daisuke Ichihara, Daiki Maeshima, Ryoyu Mori, et al. (Robinson Research Institute, VUW; Nagoya University)
Название: Operation of a plasma thruster featuring a 1.1 T high temperature superconducting magnet
Журнал: Journal of Electric Propulsion 3, 17 (2024) (BRIEF COMMUNICATION)
Год: 2024
DOI: 10.1007/s44205-024-00080-3 (Research Square: 10.21203/rs.3.rs-4606168/v1)
Тип: рецензируемая статья (Journal of Electric Propulsion)

## Релевантность проекту: 5/5
**Первый ВТСП-плазменный двигатель >1 Тл** — CC-EST с conduction-cooled HTS-магнитом (non-pulsed): тяга 38–73 мН при центральном поле 1.13 Тл (на аноде 1.28 Тл), Isp 1050–1450 с, пиковый КПД 18.7% (с учётом магнита); Xe. Детальный дизайн магнита (10 double-pancakes, 20 катушек, SuperOx 4 мм), сравнение с рекордами (0.56/0.75/0.8/1.0 Тл). Прямой ответ на 2.4 (космос/электроракетная тяга). Дополняет Acheson 2023 (0.6-0.8 Тл), Kinefuchi 2024, Long IEPC 2022.

## Суть работы
Демонстрация CC-EST (central cathode electrostatic thruster) с conduction-cooled HTS-магнитом (non-pulsed mode): центральное поле 1.13 Тл, на аноде 1.28 Тл; Xe-пропеллент; тяга 38–73 мН; Isp 1050–1450 с; пиковый КПД 18.7% (с учётом мощности магнита). **Первый ВТСП-плазменный двигатель >1 Тл.** Мотивация: постоянные магниты ограничены (~0.5 Тл, трудно размагнитить, вечное рассеянное поле); медные — джоулевы потери; LTS (AMS-02, 1.8 К) — непрактичны в космосе. CC-EST не имеет ограничения поля (в отличие от HET), ExB-дрейф + электростатическое/электромагнитное ускорение.

## Дизайн магнита
- **20 катушек = 10 double-pancakes**; повторяет поле медного электромагнита прошлых тестов [13].
- **ID 120 мм, OD 168 мм, ~280 витков/катушка**; 2G SuperOx YBCO 4 мм.
- Внутренний диаметр сборки 100 мм; сборка в вакууме (включая разряд).
- Терминалы double-pancake — винтовые соединения.
- Conduction-cooled (миниатюрный cryocooler, space-compatible); non-pulsed.
- Анод-катод вставлен в тёплый bore магнита.

## Методика
- CC-EST: на аноде осевое B × радиальное E → азимутальный ExB-дрейф (как HET), но БЕЗ ограничения поля; электростатическое + электромагнитное ускорение.
- **Выпуклый анод** (stagnant ring) — снижение напряжения зажигания (проблема при высоких полях).
- **Heaterless hollow cathode**: 5 sccm Xe; keeper (KC8002); анод (TAKASAGO HX01000).
- **Thrust stand**: hanging pendulum; калибровка массами на монофиламенте; провода через подвес (минимизация влияния).
- Вакуум: 4 м цилиндр; 10⁻³ Па (катод), 10⁻² Па (полный разряд).
- Сравнение с рекордами полей: 0.56 Тл (Китай 2021, AF-MPDT), 0.75 Тл (Россия 2020), 0.8 Тл (предыдущая итерация), 1.0 Тл (LTS, США 1971), 1.13 Тл (медь, импульсный 0.5 мс, Япония 2010).

## Результаты
- **1.13 Тл** (центральное поле), **1.28 Тл** (на аноде).
- **Тяга 38–73 мН** (Xe).
- **Isp 1050–1450 с** (регулировка).
- **КПД 18.7%** (пиковый, с учётом магнита).
- **Non-pulsed** (непрерывный) — первый >1 Тл.
- Ключевой результат: HTS-магнит реален для космоса (conduction cooling, низкая мощность, устойчивость к дефектам ленты, практичный размер/вес).
- Милестоун: зажигание при поле >1 Тл.

## Теоретическая модель
- CC-EST: ExB-дрейф (как HET) + электростатическое/электромагнитное ускорение.
- КПД с учётом магнита (входная мощность магнита/криокулера).
- FEM-модель поля (рис. 2): Bb (катод), Ba (анод); лёгкая асимметрия (разброс витков).

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B | 1.13 Тл (центр), 1.28 Тл (анод) | |
| Пропеллент | Xe (5 sccm катод) | |
| Тяга | 38–73 мН | |
| Isp | 1050–1450 с | |
| КПД | 18.7% (с магнитом) | |
| Магнит | 20 катушек (10 DP), ID 120, OD 168, ~280 витков | |

## Конструкция (смежная, не flux pump)
CC-EST + conduction-cooled HTS-магнит (non-pulsed); Xe; криокулер; hanging pendulum thrust stand; вакуум 4 м.

## Ограничения и замечания авторов
- Первый >1 Тл — прорыв.
- КПД с учётом магнита — реалистично.
- Сравнение с предыдущими: 0.56-1.0 Тл (медь/LTS/постоянные) — здесь HTS.
- Применимо к AF-MPD (дальнейшее).
- Небольшая асимметрия поля (разброс витков).

## Связь с нашим проектом
- Раздел 2.4 (космос): >1 Тл доказано; conduction cooling.
- Раздел 2.5 (потери): КПД с магнитом.
- Раздел 2.3 (магнит): дизайн (10 DP).
- Дополняет: Acheson 2023, Kinefuchi 2024, Long 2022, Dam 2020.

## Цитаты (дословные, с номером страницы/раздела)
> «thrust of 38–73 mN was measured at a central bore magnetic field of 1.13 T and on-anode field of 1.28 T» (Abstract, p. 1)
> «the thruster's specific impulse was throttled between 1050s and 1450s. The peak thruster efficiency was 18.7%, inclusive of the power consumption of the magnet subsystems» (Abstract, p. 1)
> «The HTS magnet... consisted of 20 coils arranged as 10 double-pancakes... 2G SuperOx YBCO 4 mm» (Methodology, p. 3)
> «the highest previously-documented central bore fields... are 0.56 T in China in 2021, 0.75 T in Russia in 2020, 0.8 T... and 1.0 T using an LTS magnet in the USA in 1971» (Sec. Intro, p. 3)
