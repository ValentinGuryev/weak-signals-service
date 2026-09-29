# Wang — Electromotive force and magnetization process of a superconducting traveling-wave flux pump (2023)

## [Библиография]
Авторы: Wei Wang, Jiafu Wei, Chenghuai Wu, Guangtong Ma, Hong Li, Hanxin Ye, Yuntian Zhang (Sichuan University; Southwest Jiaotong University)
Название: Electromotive force and magnetization process of a superconducting traveling-wave flux pump
Источник: arXiv:2306.02545 (2023) (препринт)
Год: 2023
DOI: нет (препринт arXiv:2306.02545)
Тип: препринт (arXiv)

## Релевантность проекту: 5/5
**КЛЮЧЕВАЯ ТЕОРИЯ: e.m.f. travelling wave flux pump = motional e.m.f. (v×B), НЕ индукция** — эксперименты с DC-bias: B_bias = 0 → I_pump = 0; B_bias > 0 → отрицательный; B_bias < 0 → положительный; при B_d = B_a: ±69 А (размах 138 А); непрерывная регулировка током B_bias; adaptive control для точного контроля. Продолжение Wang 2018 (макроскопическое сцепление), «four-quadrant control». Прямой ответ на 2.1 (физика) и 2.2 (DC-bias, амплитуда). Дополняет Wang 2018, Wang 2022.

## Суть работы
Экспериментальное доказательство происхождения e.m.f. travelling wave flux pump: **motional e.m.f. (v×B, Lorentz), а не индуцированное (−∂t·A)**. Linear-motor flux pump (AC + DC катушки, независимо): три случая с одинаковым AC (одинаковое −∂t·A), разным B_bias: (I) B_bias = 0 → I_pump = 0; (II) B_bias > 0 → I_pump < 0; (III) B_bias < 0 → I_pump > 0. При B_d = B_a: ±69 А (симметрично, размах 138 А). Выход непрерывно регулируется B_bias (линейно от 0 до B_a) — «four-quadrant» регулировка. H-formulation модель (постоянный Jc) подтверждает. Вывод: e.m.f. — из моционального члена (Lorentz), «exceptions to the flux rule» (Фейнман), но без движущегося магнита.

## Три случая (эксперимент)
- **By(x,t) = Ba·sin(kx+ωt) + B_bias** (ур. 3).
- Case (I): B_bias = 0 → By1 = Ba·sin(k0x+ω0t) (ур. 4) → **I_pump = 0 А**.
- Case (II): B_bias = +Bd → By2 = Ba·sin(k0x+ω0t) + Bd (ур. 5) → **I_pump < 0**.
- Case (III): B_bias = −Bd → By3 = Ba·sin(k0x+ω0t) − Bd (ур. 6) → **I_pump > 0**.
- **B_d = B_a**: I_pump = ±69 А (размах 138 А).
- Одинаковое −∂t·A во всех трёх → e.m.f. не от индукции.

## Ключевые результаты
- **e.m.f. = motional (v×B)**, не индукция (−∂t·A): три случая с одинаковым AC дают разный DC.
- **B_bias = 0 → I_pump = 0**; B_bias > 0 → I_pump < 0; B_bias < 0 → I_pump > 0.
- **При B_d = B_a**: I_pump = ±69 А (размах 138 А).
- **Непрерывная регулировка**: выход линейно растёт с B_bias (0 → B_a); мгновенный отклик.
- **«Four-quadrant»**: контроль B_bias и направления волны → полное управление выходом.
- **Adaptive control [35]**: точный контроль выходного DC-тока.
- **Модель**: H-formulation + E-J (постоянный Jc) — воспроизводит.
- **Поле**: By(x,t) = Ba·sin(kx+ωt) + B_bias (ур. 3).
- «Exceptions to the flux rule» (Фейнман), но без движущегося магнита.
- Моциональный e.m.f. из Lorentz: v×B.
- T-A formulation [29] — тоже игнорирует motional (критика).

## Теоретическая модель
- e.m.f. = −∂t·A (индукция) + v×B (моциональный) (ур. 2).
- Бегущая волна: By(x,t) = Ba·sin(kx+ωt) + B_bias (ур. 3).
- Контролируемый flux flow (H-formulation + E-J, постоянный Jc).
- v = λ·f (скорость волны).
- Макро-манипулирование вихрями (поляризация DC-bias).

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | Ba (амплитуда AC волны) | |
| B_dc (bias) | 0 → B_a; регулировка выхода | |
| λ (длина волны) | короткая (сцепление) | |
| f | скорость волны v = λf | |
| Направление | перпендикулярно ленте | |
| I_max | ±69 А (при B_d = B_a) | |

## Конструкция flux pump
Linear-motor flux pump: отдельные AC и DC катушки (независимое управление); закрытый YBCO-контур (Hall-датчик); H-formulation модель; adaptive control.

## Ограничения и замечания авторов
- e.m.f. — моциональный (не индукция) — уточнение физики.
- «Four-quadrant» контроль — точная регулировка (для MRI и т.д.).
- H-formulation/T-A игнорируют motional — ограничение.
- Продолжение теории макроскопического сцепления (Wang 2018).

## Связь с нашим проектом
- Раздел 2.1 (физика): происхождение e.m.f. (motional v×B).
- Раздел 2.2 (DC-bias): регулировка выхода B_bias; амплитуда.
- Раздел 2.3 (конструкции): linear-motor; four-quadrant; adaptive control.
- Дополняет: Wang 2018, Wang 2022 (обзор), Coombs 2016.

## Цитаты (дословные, с номером страницы/раздела)
> «the e.m.f. of the travelling wave flux pump is the direct result of the motional e.m.f. (v×B) rather than the induced e.m.f. (−∂t A)» (Sec. II-A, p. 2)
> «in the case Bd = Ba, Case (II) obtains I_pump = −69 A, while Case (III) obtains I_pump = 69 A... this static field Bbias had surprisingly caused a variation of output current up to 138 A» (Sec. II-A, p. 2)
> «by controlling the DC bias magnetic field, we realize the continuous regulation of the DC output of a flux pump as well as the reverse regulation» (Sec. II-A, p. 3)
> «the output DC current is accurately controlled, to be compared to a conventional... by using adaptive control» (Sec. I, p. 2)
