# Паспорт данных: корпус кейса 012 (DC/AC-передача мощности)

- **Файл:** `data/raw/openalex/dc_cables_problem.json` — **34 200 работ** (очищен от мусора 2026-09-14).
- **Полная (неочищенная) версия:** `data/raw/openalex/dc_cables_problem.full_backup.json` (35 844).
- **Скрипты:** `src/dc_cables_problem_download.py` (базовый сбор, 26 запросов от проблемы),
  `src/dc_cables_problem_tor.py` (дособор через прокси+VPS, NEWNYM при 429, tmux `dccollect`).
- **Дата сбора:** …14. **QA-фильтр:** 2026-09-14 (`signals/corpus_qa.md`).
- **Запросы:** 7 групп таксономии от проблемы передачи мощности:
  HTS-DC, HTS-AC, CU-CRYO, CU-DC (XLPE/HVDC), GIL, URBAN, DATACENTER.
- **Поля:** id, doi, title, year, date, cited_by, abstract, authors, references, type, concepts, group.
  С абстрактами: 30 065 (87.9%) — достаточно для S2-семантики; references — для S3.
- **Состав (после очистки):**

| Группа | Работ | Доля |
|---|---|---|
| CU-DC (медь XLPE/HVDC) | 11 668 | 34.1% |
| URBAN (городские сети) | 7 328 | 21.4% |
| DATACENTER (ЦОД) | 5 629 | 16.5% |
| HTS-DC (ядро) | 3 883 | 11.4% |
| HTS-AC | 2 382 | 7.0% |
| GIL | 1 989 | 5.8% |
| CU-CRYO | 1 321 | 3.9% |

- **Как восстановить:** перезапуск `dc_cables_problem_download.py` (или `_tor.py` при 429);
  очистка — re-запуск regex-фильтра (см. corpus_qa.md).
- **Ограничения честности:** DATACENTER — драйвер-затравка (самый «собирательный» класс, ИИ-ЦОД
  появились после 2023); HTS-DC — ядро, но малый класс (~11%).