# Shen — Review of the AC loss computation for HTS using the H-formulation (2020)

## [Библиография]
Авторы: Boyang Shen, Francesco Grilli, Tim Coombs (University of Cambridge; Karlsruhe Institute of Technology)
Название: Review of the AC loss computation for HTS using the H-formulation
Журнал: Superconductor Science and Technology 33, 033002 (2020)
Год: 2020
DOI: 10.1088/1361-6668/ab66d3 (arXiv:1908.02176)
Тип: рецензируемый обзор (SUST)

## Релевантность проекту: 4/5
**Обзор FEM-моделирования AC-потерь (H-formulation)** — стандарт для расчёта потерь в HTS-лентах/кабелях/обмотках: уравнения, стратегии (multi-scale, homogenization), применения (ленты, кабели, магниты), плюсы/минусы. Заполняет раздел 11 (моделирование) и 2.5 (потери). Дополняет Geng 2018 (H-formulation flux pump), Lahtinen 2019.

## Суть работы
Обзор FEM-модели (H-formulation уравнений Максвелла) для расчёта AC-потерь в HTS: ленты, кабели, обмотки. Используется десятками групп по всему миру. Часть 1: обзор модели, стратегии для большого числа лент (multi-scale, homogenization). Часть 2: применения (от отдельных лент до сложных кабелей и крупных обмоток). Раздел: численная реализация (плюсы/минусы). Выводы. Мотивация: AC-потери — важный лимит для силовых применений (кабели, ограничители тока, генераторы).

## Ключевые результаты
- **H-formulation**: FEM-модель Максвелла в H-переменной для AC-потерь.
- **Стратегии**: multi-scale, homogenization (большое число лент).
- **Применения**: отдельные ленты, кабели (CORC, Roebel), обмотки магнитов.
- **Численная реализация**: плюсы/минусы описаны.
- Используется десятками групп (стандарт).
- Важно для: кабели, ограничители тока, генераторы/моторы, магниты.

## Теоретическая модель
- H-formulation: ∂(μ0μrH)/∂t + ∇×(ρ∇×H) = 0; E-J power law (нелинейная резистивность).
- AC-потери: гистерезисные (лента), связывание (кабель), eddy (матрица).

## Параметры (моделирование)
| Параметр | Значение | Примечание |
|----------|----------|------------|
| Модель | 2D/3D H-formulation FEM | |
| Применения | ленты, кабели, обмотки | |
| Стратегии | multi-scale, homogenization | |
| Потери | AC (гистерезис, coupling, eddy) | |

## Связь с нашим проектом
- Раздел 11 (моделирование): стандарт FEM для AC-потерь.
- Раздел 2.5 (потери): AC-потери в лентах (flux pump контекст).
- Дополняет: Geng 2018 (H-formulation flux pump), Lahtinen 2019 (семантика), Wang 2022 (обзор).

## Цитаты (дословные, с номером страницы/раздела)
> «This article presents a review of the finite-element method (FEM) model based on the H formulation of Maxwell's equations used to calculate AC losses in high-temperature superconductor (HTS) tapes, cables and windings» (Abstract, p. 1)
> «This model... has been in use in tens of research groups around the world» (Abstract, p. 1)
> «Modeling strategies to tackle large number of HTS tapes, such as multi-scale and homogenization methods, are also introduced» (Abstract, p. 1)
