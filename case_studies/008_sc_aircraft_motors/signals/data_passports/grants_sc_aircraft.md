# Паспорт: гранты sc_aircraft_motors (кейс 008)

- **Файлы:** `data/raw/grants_foreign/cordis_sc_aircraft_v2.json` (18 проектов ЕС),
  `rnf_cards.json` (407, РФ — из них 4 прямых МАИ), `nsfc_results.json` (129, Китай)
- **Скрипт:** `src/grants_cordis_sc_aircraft.py` (CORDIS API, бесплатно)
- **Запросы CORDIS:** "superconducting motor" aircraft, "superconducting machine" aviation,
  cryogenic propulsion aircraft, ASuMED, HIVOMOT, FAME megawatt engines, "electric motor" aircraft propulsion
- **Дата:** 
- **Поля записей CORDIS:** id, rcn, title, acronym, programme, startDate, endDate, status, funding, countries
  (⚠️ даты/статус парсятся криво из API — для сигнала важно наличие/программа)
- **Метод РФ:** локальный поиск по rnf_cards.json (СП + авиа/мотор/крио)
- **Метод Китай:** локальный поиск по nsfc_results.json (超导 + 电机/飞机/航空/推进)
- **Ограничение:** NSFC-база собиралась по общим СП-ключам → прямых авиа-проектов не видно (артефакт канала);
  нужен живой NSFC-поиск «航空 超导 电机» (playwright, по команде)
- **Восстановление:** перезапуск скрипта CORDIS; РНФ/NSFC — локальные файлы
