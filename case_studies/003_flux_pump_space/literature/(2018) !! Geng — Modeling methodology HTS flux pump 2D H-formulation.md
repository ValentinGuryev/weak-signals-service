# Geng — Modeling methodology for an HTS flux pump using 2D H-formulation (2018)

## [Библиография]
Авторы: Jianzhao Geng, T.A. Coombs (Department of Engineering, University of Cambridge)
Название: Modeling methodology for an HTS flux pump using 2D H-formulation
Журнал: Superconductor Science and Technology 31, 125015 (2018)
Год: 2018
DOI: 10.1088/1361-6668/aae4bc
Тип: рецензируемая статья (SUST, Accepted Manuscript версия)

## Релевантность проекту: 4/5
**FEM-моделирование transformer-rectifier flux pump (H-formulation)** — методология Geng для dynamic-resistance-switched pump: 2D FEM в COMSOL, H-formulation, E-J power law. Ключевое: симуляция показывает движение потока через сверхпроводник «сдвигом электрической центральной линии» — уникальная природа намагничивания ВТСП. Заполняет раздел 11 (моделирование FEM) и 2.1 (физика). Дополняет Wang 2022 (обзор, раздел 3.1.5) и Geng 2015 (механизм).

## Суть работы
Методология моделирования HTS flux pump (transformer-rectifier, switched by dynamic resistance) в 2D H-formulation (COMSOL). Показано, как flux pumping возникает в сверхпроводнике: движение потока через сверхпроводник путём сдвига электрической центральной линии — уникальное свойство намагничивания ВТСП (тип-II). Результаты симуляции сверены с экспериментом. Мотивация: два способа работы HTS flux pump — (1) превышение локального критического тока (индукцией тока или снижением Jc полем), (2) динамическое сопротивление (переменное поле на проводящем ток сверхпроводнике).

## Ключевые результаты
- 2D H-formulation FEM в COMSOL для transformer-rectifier flux pump (dynamic resistance switch).
- Симуляция воспроизводит эксперимент (верифицировано).
- **Уникальное наблюдение**: движение потока через сверхпроводник сдвигом электрической центральной линии — природа намагничивания ВТСП.
- Два способа работы HTS flux pump: (1) превышение Ic (индукцией или полем), (2) dynamic resistance (переменное поле + DC-ток).
- Полезно для понимания физики flux pumps.

## Теоретическая модель
- 2D H-formulation (COMSOL): уравнения Максвелла в H-переменной; E-J power law для нелинейной резистивности.
- Динамическое сопротивление: DC-ток + перпендикулярное переменное поле → вихри перераспределяются → flux motion.

## Параметры переменного поля
| Параметр | Значение | Примечание |
|----------|----------|------------|
| B_ac | переменное поле (dynamic resistance) | |
| f | не приведена явно | |
| Направление | перпендикулярно ленте | |
| Геометрия | transformer-rectifier (bridge + load) | |
| Потери | dynamic resistance (модель) | |

## Конструкция flux pump
Transformer-rectifier HTS flux pump switched by dynamic resistance (как Geng 2015); 2D FEM модель.

## Ограничения и замечания авторов
- 2D (осевая/плоская симметрия) — ограничение для 3D-эффектов.
- E-J power law — приближение.
- Accepted Manuscript версия (до финальной публикации).

## Связь с нашим проектом
- Раздел 11 (моделирование FEM): H-formulation методология.
- Раздел 2.1 (физика): flux motion, электрическая центральная линия.
- Раздел 2.3: transformer-rectifier с dynamic resistance.
- Дополняет: Wang 2022 (обзор, §3.1.5), Geng 2015 (механизм), Geng 2016 (self-switching).

## Цитаты (дословные, с номером страницы/раздела)
> «The simulation will give a clear picture of how flux pumping occurs in the superconductor. It will show flux motion across a superconductor by shifting the electric central line, which is a unique nature of magnetization of High-Tc Superconductors» (Abstract, p. 1)
> «The first [8] is to exceed the local critical current... The second [7] is to take advantage of dynamic resistance effect» (Sec. 1, p. 2)
