# Паспорт: ручные патенты (пачка )

**Файлы:** data/raw/patents/topics/{sc_qubits_manual,cryo_cmos_manual,ibad_mgo_manual,josephson_qec_manual,test_facilities_manual}.json (новые)
+ дополнены: flux_pump_lens_clean.json, rebco_joint_lens_clean.json, hts_tapes.json,
  hts_ac_cables_manual.json, uhf_nmr_manual.json, mgb2_mri.json, sc_bearings_manual.json, sc_motors.json
**Скрипт/запрос:** ручная загрузка автором PDF (Google Patents); разбор локально (pdftotext + OCR rapidocr)
**Дата:** 
**Записей:** 112 добавлений (90 PDF → 112 с учётом мульти-кейсов); лог results/runtime/manual_patents_processing_.md
**Остаток API-бюджета:** Lens не тратился
**Поля:** publication_number, title, abstract, assignee, priority_date, filing_date, source=google_patents_manual, cases
**Как восстановить:** PDF — на диске (patents.google.manual/, суффикс __<кейс>); JSON — пересборка из них не автоматизирована (записи вручную). Бэкап — автор.
