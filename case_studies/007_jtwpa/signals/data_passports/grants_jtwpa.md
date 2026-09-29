# Паспорт: грантовые базы JTWPA (кейс 007)

- **Файлы:**
  - `data/raw/grants_foreign/cordis_jtwpa_results.json` — CORDIS (121 запись, 20 реальных проектов)
  - `data/raw/grants_foreign/nsf_jtwpa_results.json` — NSF (131 грант, релевантных 2)
  - РНФ: `data/raw/rnf/rnf_cards.json` (общая база 407; JTWPA-прямых 2: 21-42-04421, 26-72-10142)
- **Скрипты:** `src/grants_cordis_jtwpa.py`, `src/grants_nsf_jtwpa.py`
- **Запросы:** CORDIS — 10 терминов (TWPA/JTWPA/Josephson param amp/kinetic inductance/DARTWARS/qubit readout/...);
  NSF — 10 терминов; РНФ — локальный поиск по ключевым словам (бегущей волны/параметрич./JTWPA)
- **Дата:** 
- **Поля:** CORDIS: id/acronym/title/programme/start/end/teaser/country/contentType/url;
  NSF: id/title/org/pi/amount/year/start/abstract/url
- **Бюджет:** CORDIS — бесплатно без ключа (~10 запросов); NSF — бесплатно без ключа (~10);
  РНФ — локальные данные
- **Дополнение ():** `kaken_jtwpa_live.json` — 9 японских KAKEN-проектов по усилителям
  (найдены ЖИВЫМ поиском kaken.nii.ac.jp; старая kaken_results.json их не содержала — узкие запросы).
  Урок: «0 в базе ≠ 0 в реальности».
