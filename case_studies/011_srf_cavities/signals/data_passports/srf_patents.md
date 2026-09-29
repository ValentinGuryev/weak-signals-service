# Паспорт данных: патенты SRF-резонаторов (кейс 011, S1b)

- **Файл:** `data/raw/patents/cases/011_srf_cavities.json` (106 raw → 79 уник. → 61 релев. → 39 изобретений).
- **Скрипт:** `src/lens_srf.py` (API lens.org/patent/search, Bearer).
- **Запросы (, 6 логических):**
  - A1 "superconducting RF cavity"/"SRF cavity"/"SRF cavities" (35);
  - A2 "niobium cavity"/"niobium SRF" (30);
  - A3 "superconducting accelerator cavity"/"superconducting accelerating cavity" (67, взято 40);
  - B1 "Nb3Sn cavity"/"Nb3Sn SRF"/"niobium-tin cavity" (0 — патенты на Nb3Sn полости НЕ найдены; Nb3Sn силён в магнитах, не полостях);
  - B2 "superconducting RF" + accelerator/linac (1);
  - C1 SRF + Fermilab/JLab/KEK/CERN/Cornell (0 — assignee-верификация через текст, урок 008: 0 не значит «нет»).
- **Дедуп:** уровень 1 = jurisdiction_doc_number (unique 79); семейный (assignee+смысл) — Mitsubishi 2010 (переводы DE/EN/FR→1), Siemens 1970-71 (CA/GB/US→1), JLab/Fermilab/IMP по годам.
- **Поля:** publication_number, title, abstract, assignee, inventors, cited_by, year, relevant, invention_id.
- **Алиасы:** «Texas Wind Tower» = гидроформовка SRF (релевантен); Huainan/Heifei — китайская EBW-оснастка (релевантна).
- **Лимиты:** 6 запросов Lens (остаток по headers: 146/мес, сброс 2026-09-30).
- **Как восстановить:** `.venv/bin/python src/lens_srf.py`.

**Уточнение (, новое видение — тренд Nb3Sn):** из 79 уник. патентов Nb3Sn-специфичных — **5**
(IMP CAS ×3: 2020/2021/2023; China Nonferrous Metals TIANJIN 2024; Rey C.M. US 2018) — все про техпроцесс
покрытия/термообработки/оборудования, НЕ продукт. Остальные 54 релев. — Nb-полости (JLab, Mitsubishi,
Fermilab, Siemens) = зрелый контроль. Подграф-фильтр: `nb\s*3\s*sn|niobium[\s-]?tin|b3sn` в title/abstract.
График: `plots/patents_nb3sn_by_year.png` (тренд 5 vs контроль 54). Сигнал: `signals/patent_signal.md`.
