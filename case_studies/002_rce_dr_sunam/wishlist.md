# Wishlist — кейс RCE-DR (SuNAM)

> **Правило (внутренний контракт §4.2a):** только документы, которых у нас НЕТ в библиотеке.
> Скачанные → в `literature/`, строки вычищаются. Данные в `data/raw/` — не включаются.
>
> **Формат записи (правило ):** ПОЛНАЯ библиография — авторы (полный список),
> год, журнал, полное название, DOI. Один DOI без авторов/названия — НЕДОПУСТИМО.
>
> **Статусы:** 📥 = скачать; ⛔ = заблокировано (нет доступа); 🔶 = найти (неизвестно).

## К скачиванию — TLAG-барьеры (кейс 002, ветвь TLAG)

| # | Полная библиография | Статус | Почему нужен |
|---|---------------------|--------|--------------|
| 1 | Saltarelli L., Sanchez-Rodriguez D., Gupta K., Kethamkuzhi A., Farjas J., Molins E., Yáñez R., Ricart S., Obradors X., Puig T. — **Metal Propionate Solutions for High-Throughput Liquid-Assisted Manufacturing of Superconducting REBa₂Cu₃O₇₋δ (RE = Y, Gd, Sm, and Yb) Films**. ACS Appl. Mater. Interfaces 2024, 16, 54199-54214. DOI: 10.1021/acsami.4c11685 | ✅ ЕСТЬ (literature/) | — |
| 2 | Saltarelli L., Moreno García D., Soler L., Pach E., Gupta K., Aguilar J., Solano E., et al., Puig T. — **Role of Liquid Composition in the Transient Liquid Assisted Growth of Superconducting YBa₂Cu₃O₇₋δ Films**. Advanced Materials 2025. DOI: 10.1002/adma.202510660 | ✅ ЕСТЬ (literature/) | — |
| 3 | Queraltó A., Sieger M., Gupta K., Meledin A., Barusco P., Saltarelli L., de Palau M., Granados X., Obradors X., Puig T. — **Transient liquid assisted growth of superconducting YBa₂Cu₃O₇₋ₓ films based on pulsed laser deposition**. Supercond. Sci. Technol. 2023, 36, 025003. DOI: 10.1088/1361-6668/acaad3 | ✅ ЕСТЬ (literature/) | — |
| 4 | Oh S.S., Kim H.S., Ha H.S., Ko R.K., Ha D.W., Lee H., Moon S.H., Yoo S.I. — **Progress in R&D for REBCO CCs by reactive co-evaporation**. Prog. Supercond. Cryog. 2013, 15(4), 1-5. DOI: 10.9714/psac.2013.15.4.001 | ✅ ЕСТЬ (literature/) | — |
| 5 | Saltarelli L., Gupta K., Rasi S., Kethamkuzhi A., Queraltó A., Garcia D., Gutierrez J., Farjas J., Roura-Grabulosa P., Ricart S., Obradors X., Puig T. — **Chemical and Microstructural Nanoscale Homogeneity in Superconducting YBa₂Cu₃O₇₋ₓ Films Derived from Metal-Propionate Fluorine-free Solutions**. ACS Appl. Mater. Interfaces 2022, 14, 48582-48597. DOI: 10.1021/acsami.2c11414 | ✅ ЕСТЬ (literature/) | — |
| 6 | Kethamkuzhi A., Saltarelli L., Gupta K., Torres C., Garcia D., et al., Puig T. — **Exploring the overdoping effects in Transient Liquid Assisted Grown YBa₂Cu₃O₇₋δ superconducting films**. Sci. Rep. 2026. DOI: 10.1038/s41598-026-41613-0 | 📥 | Свежая (2026) — overdoping TLAG, пиннинг (продолжение барьера №3) |
| 7 | Ghiara E., Wu Z., Voulhoux M., Mola Bertran O., Bertini V., et al. — **High-Throughput Screening of REBCO Superconducting Thin Films Fabricated Via Combinatorial Inkjet Printing and TLAG Process**. Adv. Mater. Technol. 2026. DOI: 10.1002/admt.202502441 | 📥 | Свежая (2026) — инкджет+TLAG, HTS-скрининг (масштабирование) |
| 8 | Obradors X., Puig T., Ricart S., Palau A., Coll M., Gutiérrez J., Farjas J., Bartolomé E. — **Progress in superconducting REBa₂Cu₃O₇ (RE = rare earth) coated conductors derived from fluorinated solutions**. Supercond. Sci. Technol. 2024. DOI: 10.1088/1361-6668/ad36eb | 📥 | Обзор CSD (фторированные прекурсоры) — контекст TLAG-CSD |
| 9 | Zhou ..., Cai ..., et al. — **китайский TLAG (Colloids Surf. A 2024)**. DOI: 10.1016/j.colsurfa.2024.135106 | 🔶 уточнить авторов | Китай подхватил TLAG — R&D (верификация) |
| 10 | Puig T., et al. — **обзор TLAG в Nature Reviews Physics**. DOI: 10.1038/s42254-023-00663-3 | 🔶 проверить DOI | Обзор механизма TLAG (цитируется в ISS 2023) |
| 11 | Banchewski J., et al. — **TLAG-CSD свойства** («to be published» в 2023). | 🔶 найти | Свойства TLAG-CSD (пиннинг) |

## Документы для верификации «докупили PLD» (найти)

| # | Полная библиография | Статус | Почему |
|---|---------------------|--------|--------|
| 12 | SuNAM — новости/презентации о PLD-линии | 2016-2020 | 🔶 | Подтвердить факт «докупили PLD» |
| 13 | SuNAM — годовой отчёт / производственные данные | 2018-2024 | 🔶 | Объёмы RCE-DR vs PLD |

## Уже есть в проекте (НЕ wishlist — вычищено 2026-08-31)

> Эти документы ЕСТЬ в проекте — по правилу §4.2a они в wishlist не включаются.
> Удалены из wishlist (вычищено 2026-08-31):
> - **Lee et al. 2014 — RCE-DR (SuST 27 044018)** — в `literature/lee2014.pdf`
> - **Soler et al. 2020 — TLAG (Nat Comm, 10.1038/s41467-019-13791-1)** — в literature/
> - **Oh et al. 2013 — PSAC (10.9714/psac.2013.15.4.001)** — в literature/
> - **Saltarelli et al. 2022 ACS AMI (10.1021/acsami.2c11414)** — в literature/
> - **Saltarelli et al. 2024 ACS AMI (10.1021/acsami.4c11685)** — в literature/
> - **Saltarelli et al. 2025 Adv Mater (10.1002/adma.202510660)** — в literature/
> - **Queraltó et al. 2023 SUST (10.1088/1361-6668/acaad3)** — в literature/
> - SuNAM — Recent Progress of 2G superconducting wire (SNF, ~2013)
> - SuNAM — Developed New Process Named RCE-DR (SNF, ~2014)
> - SuNAM — CC Development for NMR/MRI (CCA 2021)
> - SuNAM NM-5 CCA 2021 (полный доклад, `(2021) [CCA] Invited presentation NM-5`)
> - TLAG доклады Puig (2023 ART/ISS/CCA, 2025 CCA) — в SNF
