# Zhai — Research progress of contactless magnetization technology: HTS flux pumps (MT26)

## [Библиография]
Авторы: Yujia Zhai (Member, IEEE), Ziwei Tan, Xinyi Liu, Boyang Shen, T. A. Coombs, Feng Wang (Hunan University; University of Cambridge; Hunan Institute of Engineering)
Название: Research progress of contactless magnetization technology: HTS flux pumps
Конференция: MT26 (26th International Conference on Magnet Technology), paper MT26-Mon-Af-Po1.19-09 (poster), 2019
Год: 2019 (MT26, Ванкувер; конференционная статья)
DOI: нет (конференционный poster-abstract)
Тип: конференционная статья (poster, MT26)

## Релевантность проекту: 3/5
Компактный обзор-классификация HTS flux pumps с акцентом на физику: TAFP (термически-активированные), travelling wave (rotating/linear/circular), switched transformer-rectifier (AC field switch, dynamic resistance switch, self-switching). Даёт сводную таблицу типов с «merits and drawbacks» (табл. 1) и рекорд >2 kA у self-switching (Geng 2020). Для разделов 2.3 (классификация) и 2.1 (физика). Численно беден — в основном качественный.

## Суть работы
Классифицирует HTS flux pumps по типу и описывает физику каждого:
1) **TAFP (Thermally Actuated Flux Pump)** — первый предложен Coombs (Cambridge) [1]: термомагнитный материал (редкоземельный Gd, позже феррит — оптимизация Zhai [3]) между YBCO и постоянным магнитом; тепловые волны меняют проницаемость → бегущая магнитная волна → намагничивание. Без переключателей и без нормального пятна. Самый примитивный прототип travelling wave.
2) **Travelling wave flux pumps** — волна B(x,t) = A·sin(2π(x/λ − ft)) (ур. 1); поле перпендикулярно сверхпроводнику:
   - Rotating magnets (Hoffman [7]): магниты на диске (N наружу), вращение → DC-напряжение на 2G-ленте. Эквивалентная схема: V_oc + R_eff; R_eff > R_соединений; насыщение ограничено динамическим сопротивлением (в 10² раз выше R_соединений) [9]. Параметры: зазор [10], частота [11], ширина статора [12], геометрия магнита [13]; through-wall excitation [14]; 10 MW ветрогенератор [15,16]. Механизм: сильное поле протягивает поток, слабое — выталкивает; экранирующий ток следует за магнитом → выпрямление [17].
   - Linear-type (Matsuda [6]): 6 медных катушек с железными сердечниками, последовательное переключение → бегущая волна; рабочие частоты/амплитуды/формы изучены. Меньше вибраций и шума, проще, может работать без изменения амплитуды.
   - Circular-type (CTMFP, Wang [18]): коаксиальные обмотки, круговая бегущая волна на YBCO-плёнке ϕ50 мм; открыт макроскопический эффект магнитного сцепления (кластеры вихрей ~миллионы, следуют за полюсами; требуется короткая длина волны и сильное поле).
3) **Switched transformer-rectifier pumps** (тип LTSFP с двумя переключателями S1, S2):
   - AC Field Switch Based [24,25,26]: высокочастотное AC-поле на ленту при положительном токе → flux flow; первый HTSFP с ясным количественным механизмом.
   - Dynamic Resistance Switch Based (Geng [33]): transformer + магнитные переключатели + load; 1 Гц синус; **квази-персистентный ток >1 kA** — рекорд в HTS-магните на тот момент.
   - Self-switching (Geng [34]): асимметричная форма тока в primary; без высокочастотного переключателя; **максимальный выход >2 kA** — самый высокий для HTSFP.
4) Табл. 1 — сводка: TAFP (нет переключателей, медленное тепловое управление, низкая частота, высокие потери); Rotating (негибкое управление, шум, вибрация); Linear (стабильный, контролируемый, но трудно полностью предсказать); Circular (высокая скорость, магнитное сцепление); AC Field Switch (полная волна, высокая стабильность); Dynamic Resistance Switch (высокая эффективность, малые потери и флуктуации поля); Self-switching (нет переключателя, сверхвысокий ток).

## Ключевые результаты
- Рекорды: dynamic resistance switch → **>1 kA** [33]; self-switching → **>2 kA** [34].
- R_eff (dynamo) в ~10² раз больше R_соединений → определяет ток насыщения [9].
- Механизм dynamo: «сильное поле тащит поток через ленту, слабое выталкивает; за счёт неоднородности — чистый поток за проход» [7]; экранирующий ток меняет путь вперёд/назад → выпрямление [17].
- Сircular-type: длина волны должна быть короткой, амплитуда высокой для эффективного сцепления; миллионы вихрей на полюс [18].

## Теоретическая модель
- Бегущая волна: B(x,t) = A·sin(2π(x/λ − ft)) (ур. 1); A, f, λ — амплитуда, частота, длина волны.
- Классический Фарадей + Bean model дают только AC-выход; DC-выход требует зависимости ρ от J, поля и скорости его изменения (Geng [30]).
- Магнитное сцепление: кластеры вихрей, неоднородность поля → энергия сцепления (Wang [18]).

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | «сильное» поле — тащит поток | качественно [7] |
| f | изучены частоты (rotating, linear) | [11],[6] |
| Направление | перпендикулярно ленте | рис. 2 [6] |
| Геометрия | одиночная лента; circular YBCO-плёнка ϕ50 мм | |
| I_max | >1 kA (dyn. resistance); >2 kA (self-switching) | [33],[34] |
| B_th | не приведено | |
| Потери | TAFP: высокие потери; переключатели — значительные потери | табл. 1 |

## Конструкция flux pump
Все классы: TAFP (Gd/феррит), rotating magnets (диск с NdFeB), linear (6 катушек с Fe-сердечником), circular (коаксиальные обмотки, YBCO-плёнка), transformer-rectifier (AC field switch / dynamic resistance switch / self-switching). 2G-ленты, YBCO-катушки.

## Ограничения и замечания авторов
- Физика HTSFP «нечёткая», магнитная динамика потока требует дальнейших исследований.
- Переключатели в transformer-rectifier дают потери; power electronics имеют высокое сопротивление в открытом состоянии → быстрая утечка потока.
- TAFP: медленное тепловое управление, низкая частота, высокие потери.
- Rotating: шум, вибрация, негибкое управление.
- Linear: трудно полностью предсказать.

## Связь с нашим проектом
- Раздел 2.1 (физика): механизм выпрямления (экранирующий ток), макроскопическое магнитное сцепление, необходимость нелинейного ρ.
- Раздел 2.3 (конструкции): полная классификация с merits/drawbacks (табл. 1).
- Раздел 2.5 (потери): переключатели, потери TAFP.
- Дополняет Wang 2022 (обзор) и Coombs 2019 (перспектива) — качественная таблица сравнения типов.

## Цитаты (дословные, с номером страницы/раздела)
> «the saturation current is limited by the dynamic resistance which is two orders higher than the joint resistance in the circuit» (Sec. III-A, p. 2)
> «when the magnets go across the sheet, flux will be dragged across the wire if the magnetic field is strong, while flux will be expelled by the wire if the field is weak» (Sec. III-A, p. 2)
> «the change in resistivity occurs in type II superconductors as a result of flux flow, and finally a DC voltage is induced in the flux pump system» (Sec. IV-B, p. 4)
