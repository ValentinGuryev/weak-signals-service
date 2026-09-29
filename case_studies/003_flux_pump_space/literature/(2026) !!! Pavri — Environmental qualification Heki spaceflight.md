# Pavri — Environmental qualification of an HTS magnet and flux pump system for spaceflight (2026)

## [Библиография]
Авторы: B Pavri, R Pollock, N Long, M Goddard-Winchester, C Jane, D Wright, C Shellard, N Strickland, J Glowacki, E Webster, J Olatunji, A Rao, Z Jaeger-Letts, L Young, S Hellmann, B Mallett, X Huang, S Smart, M Malich, R Filgas (Paihau-Robinson Research Institute, Victoria University of Wellington, Новая Зеландия; Asteria Engineering; IDS Consulting; Czech Technical University in Prague)
Название: Environmental qualification of a high-temperature superconducting magnet and flux pump system for spaceflight
Журнал: Superconductor Science and Technology 39, 085017 (2026)
Год: 2026 (опубл. 13 августа 2026)
DOI: 10.1088/1361-6668/ae940f
Тип: рецензируемая статья (PAPER, Open Access)

## Релевантность проекту: 5/5
Прямое попадание в раздел 2.4 (космические приложения). Миссия Hēki — первый (в этом наборе статей) реальный космический полёт HTS-магнита с flux pump: запущена на МКС в сентябре 2025, работала на внешней платформе NREP (JEM-EF). Статья описывает полный цикл предпусковой квалификации: вибрация (GEVS workmanship), термовакуум (HEART rig, 275–300 K baseplate, до 100 Вт сброса тепла), EMC (SSP-30237), контроль рассеянного магнитного поля (лимит 3.16 Гс @ 70 мм). Даёт требования ISS/космической среды, которых больше нигде нет.

## Суть работы
Описание предпусковой программы тестов и анализа для payload Hēki — демонстрации TRL двух технологий: (1) HTS-магнит и (2) flux pump (индуктивный сверхпроводящий выпрямитель, заряжающий магнит). Программа: вибрационные испытания (имитация запуска), термовакуумные (имитация космической эксплуатации), EMC (радиационные и кондуктивные эмиссии), характеризация рассеянного магнитного поля, структурный анализ (NASA SSP-52005). Hēki прошла программу без деградации, снизив риск отказа в полёте.
Хронология: интеграция/тесты завершены октябрь 2024; проверки NASA; допуск к полёту Voyager Technologies (Houston) январь 2025; запуск на МКС сентябрь 2025 (NREP, слот 4, JEM-EF); миссия ≥15 недель, продлена до 25 недель; возвращена на Землю для постполётной оценки.

## Ключевые результаты
- **Вибрация:** тест по спектру GEVS workmanship (NASA GSFC-STD-7000B) по всем 3 осям; первый резонанс 88 Гц; запас 5 дБ над предсказанной нагрузкой на первом резонансе; два коротких неподдерживаемых участка HTS-ленты (резонансы в низких кГц) — беспокойство, но запас большой. Магнит и flux pump без механических проблем, функциональность подтверждена после теста.
- **Структурный анализ (SSP-52005):** положительные запасы по yield/ultimate для всех случаев (ускорение запуска, вращение, «kick»-нагрузки экипажа 125 lbf, болты); кроме пассивной стороны — уточнённый анализ с пластической деформацией по Neuber's Rule дал положительные запасы. Пиковое напряжение 143.9 МПа.
- **Тепло:** сброс до 100 Вт отходящего тепла; radiator на активной стороне (алюминизированный Teflon, максимальная площадь — вся пластина NREP), sink ~255 K (Земля) вместо ~3 K (открытый космос); суточный цикл ~100 мин; beta-угол −70°…+70°; две модели (external, internal); cryocooler модель эффективности vs T.
- **Термовакуум (HEART):** кастомный стенд с медной пластиной (Kapton, высокая emissivity), trim-heater на baseplate; cold soak ~255 K; functional тесты при baseplate 275 K и 300 K; в течение 3 недель; криогенные компоненты оставались в рабочих диапазонах; температуры в пределах нескольких градусов от модели.
- **Магнитное поле:** лимит ISS 3.16 Гс (0.316 мТл) @ 70 мм от внешней структуры NREP; компактный ферромагнитный экран (~120 мм диаметр, сталь); 3D FEM + Hall-датчики (z = 78/158 мм, r = 240 мм); хорошее согласие модель/измерение; **с экраном поле всё же превышало 3.16 Гс в некоторых направлениях при максимальном рабочем поле** → waiver + процедура с NASA/Voyager.
- **EMC (SSP-30237):** radiated emissions — в лимитах (100–200 МГц показаны); conducted emissions — в лимитах; пики на гармониках рабочей частоты криокулера.
- Один неожиданный результат: температурная чувствительность одного из двух радиационных детекторов (деградировавший пиксель) → маскировка пикселя в ПО.
- Hēki связана с проектом HTS-AF-MPD (applied-field magnetoplasmadynamic) двигателя — измерение тяги, магнитное экранирование заряженных частиц и re-entry нагрева.

## Теоретическая модель
- Вибрационный спектр: GEVS workmanship (GSFC-STD-7000B) vs IDD-спектры (Zotek foam, Pyrell 2"); первый резонанс 88 Гц, запас 5 дБ.
- Структурный анализ: NASA SSP-52005, факторы безопасности, Bolted Joint Fitting Factor; Neuber's Rule для пластической деформации (пассивная сторона).
- Тепловые модели: external (солнечное излучение, IR Земли, альбедо, отражения от ISS) и internal (криогенные компоненты, эффективность криокулера vs T); orbit-average тепловые потоки; beta-угол диапазон.
- Магнитное поле: 3D FEM + калиброванные Hall-зонды; лимит 3.16 Гс @ 70 мм.
- EMC: SSP-30237 Rev U.

## Параметры переменного поля (если применимо)
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | не указана (эта статья — квалификация, не накачка) | — |
| f | не указана | — |
| Направление | не указано | — |
| Геометрия | компактный HTS-магнит + flux pump + стальной экран ~120 мм | ISS payload |
| I_max | до «expected flight levels» и выше (при характеризации поля) | числа не даны |
| dI/dt | не указана | — |
| B_th | не указана | — |
| Потери | до 100 Вт отходящего тепла системы; криокулер сбрасывает | тепловой дизайн |

## Конструкция flux pump
- Индуктивный сверхпроводящий выпрямитель (flux pump), заряжающий HTS-магнит до поля.
- Интегрирован с коммерческим криокулером, полётным компьютером, кастомной авионикой, радиационными детекторами (HardPix, CTU Prague).
- Компактный ферромагнитный (стальной) экран ~120 мм вокруг стопки катушек магнита.
- Активная сторона (к Земле) — radiator из алюминизированного Teflon; пассивная — криогенные компоненты.
- НREP платформа: питание + связь; crew-инсталляция.

## Ограничения и замечания авторов
- Рассеянное поле с экраном превышало лимит 3.16 Гс в некоторых направлениях при максимальном поле → нужен waiver/процедура.
- Ориентация radiator фиксирована (к Земле, sink ~255 K) — не оптимальна, но компенсирована площадью и покрытием.
- Криокулер не смог достичь 20 K на полётной конфигурации (30 K в Iftikhar; здесь не указано, но cryocooler — коммерческий).
- Один радиационный детектор имел температурную чувствительность (деградировавший пиксель).
- Детали полётных операций и постполётной оценки — в следующих публикациях.

## Связь с нашим проектом
- Раздел 2.4 (космос): **главный первоисточник** — Hēki на ISS: требования (3.16 Гс @ 70 мм, SSP-30237, GEVS), тепловой дизайн (до 100 Вт, radiator к Земле), термовакуумная квалификация, магнитное экранирование.
- Раздел 2.4: связь с HTS-AF-MPD двигателем — применение HTS-магнита для магнитной тяги (космическая пропульсия).
- Раздел 2.5: тепловые требования к криогенной системе в космосе.
- Смежные: [3] Olatunji 2024 Superconductivity 12 100133 (уже в библиотеке!), [4] Mallett 2024 Superconductivity 12 100129 (тоже в библиотеке), [16] Strickland 2026 Superconductivity 17 100231, [14] Strickland 2025 IEEE TAS 35 4600107.

## Цитаты (дословные, с номером страницы/раздела)
> «Hēki is designed to advance the technology readiness level of two novel technologies: a high-temperature superconducting magnet and a 'flux pump'—an inductive superconducting rectifier which energizes the magnet to field.» (Abstract)
> «Hēki successfully completed this pre-launch test program without degradation in performance, reducing the risk of failure in flight and marking an important milestone toward commercialization of these technologies for space applications.» (Abstract)
> «the ability to shed up to 100 W of waste heat while maintaining all internal components within the allowable temperature ranges» (Section 3.1)
> «ISS safety requirements impose a DC magnetic stray field limit of 3.16 gauss (0.316 mT) at 70 mm from the exterior of the NREP structure» (Section 4.1)
> «even with the shield in place the field was found to exceed the 3.16 G limit in some directions at the planned maximum operational magnetic field» (Section 4.1)
