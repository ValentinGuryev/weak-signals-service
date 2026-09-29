# Кейс 010: СП-генераторы для ветроэнергетики (EcoSwing)

> **Статус:** ✅ ЗАКРЫТ (). **Метка:** ❌ НЕ состоялся к 2026 (демо было, коммерции нет).
> **Роль:** калибровочный (глубокий) — negative-пример «спонсируемое демо без коммерции».

## Сигнал ~2018 (что обещали)
- Офшорные 10-20 MW турбины: вес/размер генератора растёт с мощностью, КПД/магниты — в пределе.
  СП-генератор: больше МВт/кг, выше КПД, компактнее, потенциально без редких земель.
- Обещания: Abrahamsen 2010 — ~1200 СП-турбин = 10% офшорного рынка ЕС к 2030; IEA 2017 — market
  maturity 2030. **Ни одно не сбылось.**

## Вердикт
**❌ Не стоило / НЕ состоялся:** единственное в мире полноразмерное демо (EcoSwing, 3.6 MW direct-drive,
TRL 7, поле 2018-2019, €10.6M вклад ЕС) было инженерной вехой, но **0 коммерческих установок к 2026**.
Все каналы сошлись на V-образном обрыве после 2019.

## Почему (механизм)
1. **ЕС оплатил ДЕМО, не R&D-рынок** (топик LCE-03-2014); грант-конвейер (UpWind→INNWIND→EcoSwing)
   оборвался после 2019.
2. **Грантополучатели НЕ патентовали** (EcoSwing/SUPRAPOWER/KEPCO/AMSC = 0 патентов); патенты — у GE
   (6 изобр., 2018-19), MIT+CFS (3, 2021!), китайских ТНК/вузов (Dongfang, Hunan, Nanjing).
3. **Семантика остыла:** пик инженерной лексики 2015-19, экономическая лексика (cost/scale) УБЫВАЛА —
   тема не прошла гейт «инжиниринг → рынок»; дрейф в водород/microgrid.
4. **Азиатские программы** (KEPCO 10MW floating, Япония New Sunshine/feasibility) — конферентно/грантово,
   тоже без внедрения.

## Исход 2026 (документально)
- **«…has achieved full commercialization for MRI and NMR applications… many challenges still remain…
  which will in turn pave the way for the commercialization»** — Song et al. 2026 (SuST Roadmap,
  DOI: 10.1088/1361-6668/ae8b31): СП коммерциализирована только в MRI/NMR, не в энергетике.
- **Shah et al. 2025 (SuST review, DOI из выжимки): СП-генераторы для ветра «not commercially viable»**.
- **Thönelt et al. 2026 (IPEC-Nagasaki): доклад о «Partly Superconducting … Generator *Prototype*»** —
  в 2026 тема живёт в прототипах, не в продуктах.

## Шумиха (честно)
- СМИ 2018-2020: «World's First Full-Scale MW-Class SC Generator» (заголовки команды EcoSwing) —
  веха ДЕМО, не коммерции; в SNF-индексе EcoSwing-команда отсутствует (журнальная жизнь).
- AMSC «10 MW класс» (2011, NIST ATP) — 0 патентов, 0 продаж ветро-СП.

## Сигналы (детали в `signals/`)
`grant_signal.md` · `conference_signal.md` · `patent_signal.md` · `semantic_s2.md` ·
`problem_competitors.md` · `s3_cross_competitor.md` · `roadmap_signal.md` · `assembly.md` (единый нарратив).

## Данные
Корпус OpenAlex 1560 релев.; гранты (CORDIS/NSF/РНФ/KAKEN); патенты Lens 192 зап. / 87 релев. /
48 изобр. (`data/raw/patents/cases/010_sc_wind.json`); SNF-индекс; паспорта — `signals/data_passports/`.

## Артефакты
- `plots/`: pubs_by_year, s3_*, plot_grants_signal, plot_s2_semantic_shift, plot_patent_signal.
- `assembly.md` — единый нарратив кейса.