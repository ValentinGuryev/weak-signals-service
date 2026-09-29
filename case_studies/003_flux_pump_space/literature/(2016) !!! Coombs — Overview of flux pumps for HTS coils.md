# Coombs — An Overview of Flux Pumps for HTS Coils (2016)

## [Библиография]
Авторы: T.A. Coombs (Senior Member, IEEE), J. Geng, L. Fu, K. Matsuda (University of Cambridge, Electrical Engineering Division)
Название: An Overview of Flux Pumps for HTS Coils
Журнал: IEEE Transactions on Applied Superconductivity 27(4), 2016 (ASC2016-5LOr1A-04A)
Год: 2016
DOI: 10.1109/TASC.2016.2645130
Тип: рецензируемый обзор

## Релевантность проекту: 5/5
**Ключевой обзор Coombs (Кембридж)** — систематизация HTS flux pumps: travelling wave (LTWFP, RTWFP), switched transformer-rectifier (ESTRFP, HSTRFP, DCSTRFP), variable resistance rectifier (SRTRFP, ACSTRFP); общая модель (уравнения 1–2); сравнение типов и применений. Прямой ответ на вопрос 2.3 (какие типы) и 2.1 (физика). Дополняет Coombs 2019 (перспектива) и Wang 2022 (обзор).

## Суть работы
Обзор HTS flux pumps для катушек из coated conductor (CC). Мотивация: персистентный режим CC-катушек, компенсация спада тока (flux creep, AC-потери). Три категории: (1) Travelling wave (бегущая волна; первый предложен Coombs [9,10]): H(t,x) = A·sin(2π(ft − x/λ)); генерируется тепловым/оптическим способом, линейными катушками, концентрическими катушками, вращающимися магнитами; два основных типа — LTWFP (линейные электромагниты; Lin и co-workers первыми с YBCO CC без нормального пятна) и RTWFP (вращающиеся магниты; Hoffmann [11,23,24]); (2) Switched transformer-rectifier (трансформатор + сверхпроводящие переключатели): ESTRFP (MOSFET, до 500 Гц, но on-state сопротивление), HSTRFP (тепловые переключатели Nb3Sn/YBCO, медленные), DCSTRFP (DC-полевые переключатели MgB2, быстрее тепловых); (3) Variable resistance rectifier (без переключателей S1/S2, сопротивление в HTS-ленте): SRTRFP (self-regulating, асимметричный ток, только half-wave), ACSTRFP (AC-полевые переключатели, Geng & Coombs). Общая модель (рис. 8): V1(t)+V2(t) = −dΦ/dt (ур. 1); VAVG = (1/T)∫(R2/(R1+R2))·(−dΦ/dt)dt (ур. 2). Применения: NMR (microampere pump, Walsh 2 Тл/2.5 ч/18 ppm), HTS-ротор (VUW exciter, through-wall).

## Ключевые результаты
- **RTWFP**: эквивалентная схема V_oc + R_eff; R_eff ≫ R_соединений (динамическое сопротивление — лимит насыщения [26]); V ∝ f (частота вращения); полярность — направление/полярность магнитов; V и ток насыщения падают с полем [28]; ширина ленты влияет на ток насыщения [27].
- **LTWFP**: первый linear electro-magnetic с YBCO CC без нормального пятна (Lin [20-22]); поведение не точно предсказуемо (оптимизация trial-and-error), излишние потери.
- **ESTRFP**: MOSFET до 500 Гц, быстрая зарядка, высокая эффективность, но on-state сопротивление → постоянные потери в quasi-persistent режиме.
- **HSTRFP**: тепловые переключатели (Nb3Sn, YBCO), медленные → низкие частоты.
- **DCSTRFP**: MgB2-переключатели, DC-поле управляет Jc (сильная полевая зависимость Jc у HTS); полная волна, быстрее тепловых.
- **SRTRFP**: асимметричный i2 (положительный пик > Ic, отрицательный < Ic); без переключателя; только half-wave; V-I крутой (сложное управление).
- **ACSTRFP**: high-frequency AC-поле при одном направлении тока → flux flow; точное управление потоком за цикл → высокая стабильность поля; требует длинную ленту для больших R.
- **Walsh [23]**: RTWFP зарядил 0.4H NMR-магнит до 2 Тл за 2.5 ч; вариация поля 18 ppm при поддержании.
- **VUW**: brushless exciter для HTS-ротора [45-47]; through-wall operation [48] — flux pump вне криостата.
- **Общая модель**: DC-напряжение = интеграл движения потока через R2(t); R1, R2 могут быть flux flow или обычным сопротивлением (утечка).

## Теоретическая модель
- Бегущая волна: H(t,x) = A·sin(2π(ft − x/λ)); A, f, λ — амплитуда, частота, длина волны.
- Общая эквивалентная схема (рис. 8): v1(t)+v2(t) = −dΦ/dt (ур. 1); VAVG = (1/T)∫₀ᵀ (R2(t)/(R1(t)+R2(t)))·(−dΦ/dt)dt (ур. 2).
- Flux flow: нелинейная E-J кривая ВТСП; переключатели работают в flux flow области.

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | поле бегущей волны A (амплитуда) | H(t,x)=A·sin(2π(ft−x/λ)) |
| f | ESTRFP до 500 Гц; HSTRFP низкие; RTWFP ~Гц–десятки Гц | |
| Направление | перпендикулярно ленте (traveling wave) | |
| Геометрия | одиночная YBCO-лента; линейные катушки; вращающиеся магниты | |
| I_max | ~100 А (RTWFP); NMR 2 Тл/2.5 ч | |
| Потери | R_eff ≫ R_соединений (динамическое сопротивление); on-state MOSFET | |

## Конструкция flux pump
Все три категории: LTWFP (пары полюсов над/под лентой), RTWFP (диск с магнитами), ESTRFP (MOSFET), HSTRFP (Nb3Sn/YBCO тепловые), DCSTRFP (MgB2), SRTRFP (асимметричный ток), ACSTRFP (AC-поле).

## Ограничения и замечания авторов
- RTWFP: мотор — не гибкое управление, шум; постоянная скорость для поддержания поля; потери растут с током.
- LTWFP: поведение не предсказуемо точно, trial-and-error оптимизация.
- ESTRFP: on-state сопротивление (постоянные потери); для высокомощных/частотных.
- SRTRFP: только half-wave; крутая V-I (сложно управлять); переключатели на высоком токе.
- ACSTRFP: оптимизированный LTWFP; высокая стабильность; нужна длинная лента.
- Variable resistance rectifier — самые перспективные (сопротивление независимо от индукции, iB не зависит от iL → минимальные потери).

## Связь с нашим проектом
- Раздел 2.3 (конструкции): полная классификация типов с преимуществами/недостатками.
- Раздел 2.1 (физика): общая модель (ур. 1-2), flux flow, динамическое сопротивление.
- Раздел 2.2 (параметры): частота (до 500 Гц), поле ∝ A, форма волны.
- Раздел 2.4: через-wall excitation (VUW) — космический контекст.
- Дополняет: Coombs 2019 (перспектива), Wang 2022 (обзор), Zhai 2019.

## Цитаты (дословные, с номером страницы/раздела)
> «The effective resistance observed is much larger than the joint resistances... Jiang and co-workers proposed that dynamic resistance contributes most to the effective resistance and is the limiting factor of saturation current» (Sec. II-C, p. 2)
> «The magnitude of the voltage observed is proportional to rotating frequency, and the polarity is related to rotating direction and the polarity of the magnets» (Sec. II-C, p. 2)
> «the travelling wave and the variable resistance type rectifier pumps do not require either switches or the generation of a normal spot and can be reduced to the same equivalent circuit» (Sec. VI-B, p. 4)
