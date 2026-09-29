# SNF-доклады по RCE/TLAG — сравнение с OpenAlex-корпусом

> **Дата:** . Источник: `data/raw/conferences/snf_ieeecsc/downloads_renamed[_v2]`
> **Вывод:** OpenAlex НЕ индексирует SNF (конференционные презентации IEEE-CSC/ESAS).
> SNF — уникальный источник докладов, которых нет в OpenAlex.

## Сводка

| Источник | RCE/SuNAM | TLAG | Всего |
|---|---|---|---|
| SNF-доклады (уникальные) | 6 | 8 | 14 |
| OpenAlex-корпус (title+abstract) | 51 | 31 | 82 |
| **SNF-докладов НЕТ в OpenAlex** | **3** | **6** | **9** |

## SNF-доклады RCE/SuNAM (6)

| Год | Доклад | В OpenAlex? |
|---|---|---|
| 2013 | SuNAM Developed New Process Named RCE-DR (Moon, EUCAS) | статья Lee 2014 SuST (есть) |
| 2014 | Recent Progress of 2G superconducting wire in SuNAM | ❌ НЕТ |
| 2016 | Recent progress on SuNAM Coated Conductor Development (CCA) | ❌ НЕТ |
| 2021 | SuNAM Coated Conductor Development for NMR/MRI (CCA) | ❌ НЕТ |
| — | RCE-DR Novel Process for Coated Conductor Fabrication | статья Lee 2014 (есть) |
| — | Recent progress in REBCO coated conductors via RCE-DR | частично (Oh 2013) |

## SNF-доклады TLAG (8)

| Год | Доклад | В OpenAlex? |
|---|---|---|
| 2021 | Materials Opportunities to Boost HTS-CC: TLAG (Puig, CCA) | ❌ НЕТ |
| 2022 | Ultrafast transient liquid assisted growth of YBCO (ASC) | статья Soler 2020 (есть) |
| 2023 | TLAG, A Method to Increase Coated Conductors (ART) | ❌ НЕТ |
| 2023 | Ultrafast TLAG of YBa2Cu3O7 (ASC) | частично |
| 2023 | TLAG method for increasing CC throughput (ISS) | ❌ НЕТ |
| 2024 | **Impact of High Growth Rates on TLAG (ASC)** — Kethamkuzhi, Mola, Gupta, Vlad, Torres, Pach, Ghiara, Saltarelli, Rasi, Banchewski | ❌ НЕТ (свежий!) |
| 2025 | Progress and Opportunities of TLAG (CCA, Puig) | ❌ НЕТ |
| — | Transient Liquid Assisted Growth (TLAG) | ❌ НЕТ |

## Почему это важно

1. **SNF-доклады дают свежую инфу** (2024 ASC TLAG — авторы Kethamkuzhi et al., «Impact of High Growth Rates on TLAG» — нет в OpenAlex)
2. **Конференционные презентации не попадают в OpenAlex** (нет DOI/журнальной версии)
3. **Полная картина метода = OpenAlex (статьи) + SNF (доклады) + патенты**
4. Для графика: SNF-доклады добавляют пики в годы конференций (2013, 2016, 2021-2025)

## Действие

- SNF-доклады УЖЕ в `data/raw/conferences/snf_ieeecsc/` (скачаны ранее)
- Выжимки для ключевых: 2013 EUCAS RCE-DR, 2021 CCA TLAG, 2024 ASC TLAG — в процессе
- Для полного графика можно добавить SNF-доклады отдельной серией (пунктир)
