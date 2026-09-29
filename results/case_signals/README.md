# case_signals — данные сигналов по кейсам (S2: семантика, S4: экономика)

> **Назначение:** результаты экспериментов по операционализации сигналов S2 (семантический
> сдвиг «фундаментальное → прикладное») и S4 (экономика: цены сверхпроводников, снятие предела),
> плюс фазы трендов (S1/S3). Это **вход для таблицы фич** (Фаза B), НЕ финальные фичи.
> **Статус:** экспериментальные данные, сгенерированы скриптами `src/` (см. таблицу ниже).
> **Обновлено:** 2026-08.

---

## Структура

```
case_signals/
├── README.md                          # этот файл — индекс
├── PLAN_SEMANTIC_V2.md                # ПЛАН улучшения анализатора S2 (баги + литература)
│
│   ── S2: семантический сдвиг «фундаментальное vs прикладное» ──
├── semantic_v2_ibad.json              # S2 по SNF-докладам IBAD (2008–2025, 3-летние бины)
├── semantic_v2_control.json           # S2 по контрольным темам (cables, fusion, mri, mgb2, cryogenics)
├── ibad_abstracts_discrimination.json # S2-дискриминатор по абстрактам OpenAlex IBAD (1991–2026)
├── discrimination_verdicts.json       # золотой стандарт: вердикты по 9 ключевым IBAD-статьям
├── wordshift_trends_snf_ibad_tapes.json # слов. сдвиг (частоты + тренд) — SNF IBAD-ленты
├── wordshift_trends_snf_cables.json     # слов. сдвиг — SNF кабели (контроль)
├── wordshift_trends_snf_fusion.json     # слов. сдвиг — SNF термояд (контроль)
├── wordshift_trends_openalex.json       # слов. сдвиг — OpenAlex IBAD
│
│   ── S4: экономика / цены / снятие предела ──
├── snf_price_scan.json                # скан 701 SNF-PDF на цены ($/kA·m, €/kAm, контексты)
├── snf_price_graphs.json              # извлечённые цены + контексты (NbTi $1, YBCO $400→25, MgB2 $5)
│
│   ── S1/S3: фазы тренда ──
└── trend_phases.json                  # фазы тренда по ядрам кластера IBAD (зарождение/развитие/состоялся)
```

---

## Связь с методологией и сигналами

| Сигнал (METHODOLOGY §4a) | Файлы | Что даёт для фич |
|---|---|---|
| **S2 — семантическое поле** («открытие» → «инжиниринг») | `semantic_v2_*.json`, `ibad_abstracts_discrimination.json`, `wordshift_trends_*.json`, `discrimination_verdicts.json` | `appl_share`, `fund_share`, `delta_mean` (прикладная−лабораторная лексика на 1000 слов) по периодам; слов. тренды (`monotonic`, `trend`, `freqs`); золотой стандарт для валидации |
| **S4 — снятие предела** (рекорд/экономика) | `snf_price_scan.json`, `snf_price_graphs.json` | цены $/kA·m по годам (NbTi $1, MgB2 $5, YBCO $400→25), контексты — кейс-примеры; идеальность = функция/затраты |
| **S1 — пересечение баз** | `trend_phases.json` | фазы (зарождение/развитие/состоялся) по цитатной динамике ядер кластера |

---

## Генерация (какой скрипт → какой файл)

| Файл | Скрипт | Статус |
|---|---|---|
| `semantic_v2_ibad.json`, `semantic_v2_control.json` | `src/semantic_shift_v2.py` | работает, но см. PLAN (баги v1) |
| `ibad_abstracts_discrimination.json` | `src/openalex_ibad_discriminate.py` | работает |
| `discrimination_verdicts.json` | ручной золотой стандарт (автор) | ✅ эталон |
| `wordshift_trends_*.json` | `src/wordshift_trends.py` | работает |
| `trend_phases.json` | `src/trend_phases.py` | работает |
| `snf_price_scan.json`, `snf_price_graphs.json` | скрипты сканирования SNF (см. `src/` ninja/scan) | работает |
| (валидация S2) | `src/semantic_train_eval.py`, `src/semantic_gold_eval.py` | отладка классификатора |

> ⚠️ `src/semantic_shift_ibad.py` — старый анализатор v1; его замена описана в `PLAN_SEMANTIC_V2.md`.

---

## Как переиспользовать (в таблицу фич, Фаза B)

1. **S2:** `semantic_v2_ibad.json` + `semantic_v2_control.json` — брать `delta_mean`/`appl_share` по последнему периоду как фичу «стадия зрелости»; контроль (cables/fusion) — бейзлайн «нормы».
2. **S2 (слов. сдвиг):** `wordshift_trends_*.json` → `trends` (monotonic/trend/freqs) + `ranked` — топ растущих/падающих терминов.
3. **S4:** `snf_price_graphs.json` — цены по годам для фичи «идеальность (функция/затраты)» и гипотезы H7 (падение $/kA·m перед прорывом).
4. **S1/S3:** `trend_phases.json` — фаза тренда как стратификатор/фича.

---

## Связь с другими документами
- Методология: `methodology/METHODOLOGY.md` (§4a сигналы, §5 фичи).
- Кейс IBAD: `case_studies/001_ibad_mgo/` (сигналы в `signals/`).
- Разбор слабых сигналов (Ebadi): `results/implementation_examples/ebadi_weak_signal_analysis.md` (DoV/DoD — дополнение к wordshift).
