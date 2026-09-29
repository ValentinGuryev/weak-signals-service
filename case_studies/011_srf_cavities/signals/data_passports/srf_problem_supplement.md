# Паспорт: дополнение корпуса проблемными формулировками (кейс 011, S1a-supplement)

- **Файл:** `data/raw/openalex/srf_problem_supplement.json` — **12444 работ** ().
  Объединённый корпус с `srf_corpus.json` (7579) = **19999 работ** (дедуп по id).
- **Скрипт:** `src/srf_problem_download.py` (v2, MERGE-идемпотентный), ценз-счётчики — `src/srf_problem_census.py`.
- **Метод:** OpenAlex `title_and_abstract.search`, полные записи (abstract+authors+references+concepts),
  cursor-пагинация per-page=200, дедуп по id против корпуса, ранняя остановка на перекрытых запросах,
  backoff 30/60/120с на 429 (потребовался: 2 прогона частично падали в rate-limit).

## Запросы (формулировки ОТ ПРОБЛЕМЫ, ни разу не использованные в исходном сборе)

| Класс | Запрос | Новых работ |
|---|---|---|
| **NC-альтернативы** | "normal conducting" AND (linac/accelerator/cavity/structure) | 1329 |
| | "copper" AND ("accelerating structure" OR "RF cavity") | 368 |
| | "CLIC" AND (collider/accelerator/structure) | 2570 |
| | "two-beam accelerator" | 227 |
| | "high gradient" AND (linac/accelerator/cavity) | 1568 |
| | "accelerating gradient" | 3269 |
| **Новые технологии ускорения** | "dielectric laser acceleration" OR "dielectric laser accelerator" | 296 |
| | "dielectric wakefield" | 162 |
| | "THz" AND (accelerator/linac) AND (structure/cavity) | 355 |
| | "plasma wakefield acceleration" | 766 |
| | "laser wakefield acceleration" | 1438 |
| **Материальные дыры (ценз)** | "MgB2" AND (radiofrequency/SRF/RF cavity) | 14 |
| | "NbN" AND (SRF/superconducting RF/RF cavity) | 13 |
| | "NbTiN" AND (cavity/SRF/radiofrequency) | 64 |
| | "SIS multilayer" | 5 |

## Почему именно эти запросы (шаги 1-2 GUIDE)
1. Ценз-счётчики поля: MgB2∨NbN∨NbTiN∨SIS в SRF-контексте (добавлено 96 работ — закрыты дыры знаменателя);
2. Не-сверхпроводящие альтернативы проблемы «высокоградиентное ускорение частиц»:
   - NC-полости/структуры (медь, CLIC, two-beam) — прямой конкурент SRF,
   - DLA / диэлектрический кильватер / THz-структуры — RF-структуры нового типа,
   - плазменный / лазерный кильватер — бескавитиевые подходы к той же проблеме (компактные ускорители).
3. Запросы "high gradient"/"accelerating gradient" — от проблемы (градиент), не от материала.

## Исключено из знаменателя (сознательно)
- **"Nb3Sn wire" (3732)** — магниты/провода (ITER, HL-LHC), НЕ полости → чужой домен, сигнал загрязнит;
- **"energy efficiency accel" (6782)** — шумовой (energy efficiency в др. смыслах);
- **ERL/ILC/FCC/CEPC/XFEL/cryomodule** — приложения SRF, уже покрыты исходным корпусом (проверено: ранняя остановка).

## Расход API (OpenAlex, free)
- Census: 19 (поле) + 27 (проблемные формулировки) = 46 запросов-счётчиков (разведка counts).
- Докачка: 3 прогона × 15 запросов × до 25 страниц, с дедупом; итого ~200 страничных запросов
  (+ повторы на 429 с backoff 30/60/120с). Free-лимит OpenAlex, квотных API не тратил.
- Лимиты: соблюдался backoff; записи стандартные (title/year/abstract/authors/references/concepts).

## Как восстановить
`.venv/bin/python src/srf_problem_download.py` (merge) + `src/plot_pubs_share_011.py` (график).
Исходный `srf_corpus.json` НЕ тронут.