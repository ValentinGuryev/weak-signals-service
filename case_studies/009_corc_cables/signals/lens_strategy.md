# Lens-стратегия: CORC-патенты по грантополучателям (кейс 009)

> **Дата:** . **Бюджет:** ~24 + 7 вызовов (остаток ~423/1000 на ).
> **Цель:** покрыть «грантовое поле» CORC через патенты финансируемых игроков (ACT=DOE SBIR,
> CERN, KIT, ВНИИКП/Курчатовский, Китай=NSFC/CRAFT) + география + импакт.

---

## 1. Итоговая стратегия (13 запросов, `src/lens_corc_grants.py`)

| # | Запрос | Зачем | Результат |
|---|---|---|---|
| A1 | title="CORC" | ядро по аббревиатуре | 31 (с фарм-мусором) |
| A2 | "conductor on round core" (t/a) | синоним без аббр. | 1 |
| B1-B6 | assignee/inventor ACT, CERN, KIT, ВНИИКП, Курчатовский | грантополучатели | **0 — assignee-фильтр сломан** |
| C1 | jurisdiction=CN + CORC | Китай (NSFC/CRAFT) | 32 |
| C2 | jurisdiction=US + CORC | США (DOE) | 36 |
| C3 | JP/KR/EP/WO + CORC | остальная география | 23 |
| D1 | CORC top-cited | импакт | 25 |
| D2 | CORC + legal_status | судьба | **HTTP 400 — поля нет** |

**Итог:** 116 патентов (93 осн. + 23 ACT-семейства докачкой). Чистых CORC ~57.

## 2. Критические уроки (что НЕ работает в Lens)

1. **`biblio.legal_status` — НЕ существует** → HTTP 400 «Unrecognized fields».
2. **Фильтр `applicants`/`applicant_name`/`assignee` match/match_phrase — 0** для многословных
   («Advanced Conductor Technologies»). Работает только простой match по одному токену
   (университеты в lens_academy_check: «Cambridge», «Tokyo»).
3. **`inventors` match_phrase — 0** (van der Laan, ten Kate). Поле не индексируется как phrase.
4. **`sort: [{"priority_date":...}]` — HTTP 400** («Mismatched input for fields - [sort, priority_date]»).
5. **title="CORC" ловит фарм-мусор** (WYETH/Merck/GSK — «CORC»=акроним) → нужен СП-контекст.
6. **ACT-семейства без «CORC» в abstract** (series-connected, quench, power cable, machine) —
   fielded-поиск по термину их НЕ ловит. Обход: title-фразы по известным номерам из Google-данных.
7. **СП-контекст на сервере** (must: superconducting/cable/wire/magnet...) хорошо режет фарму — приём
   работает (recall R0-R2: total 38 CORC без фармы).

## 3. Что РАБОТАЕТ

| Приём | Статус |
|---|---|
| title/abstract match_phrase по термину | ✅ |
| jurisdiction-фильтр (match по CN/US/JP...) | ✅ |
| СП-контекст must (superconduct/cable/...) | ✅ режет мусор серверно |
| cited_by (biblio.cited_by) | ✅ (импакт) |
| offset-пагинация (size 100) | ✅ (lens_patents цикл) |
| title-фразы по известным номерам (докачка семейств) | ✅ обход сломанного assignee |

## 4. Рекомендации на будущее (для др. кейсов)

1. **Для компаний:** НЕ полагаться на assignee-фильтр — собирать через термин в title/abstract +
   добивать по известным номерам/семействам (Google-данные → Lens-номера).
2. **Один запрос = union-count:** `should`-ветки + СП-контекст, size=100 — экономия (recall 4 вызова
   вместо 24).
3. **legal_status/судьбу патента** в Lens получить нельзя — судить по cited_by/публикациям.
4. **Фарм-аббревиатуры** («CORC») — всегда СП-контекст серверно, не пост-фильтр.

## Артефакты
- Скрипты: `src/lens_corc_grants.py` (+ recall-heredoc'и).
- Данные: `data/raw/patents/cases/009_corc_grants.json` (116), `009_corc_recall.json` (43).
- Бюджет-лог: `results/runtime/api_budget.md` (2026-09-09, ~31 вызов, →~423).
