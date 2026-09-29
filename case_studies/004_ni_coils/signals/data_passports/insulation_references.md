# Паспорт: insulation_references.json

- **Файл:** `data/raw/openalex/insulation_references.json`
- **Скрипт:** `src/openalex_insulation_refs.py`
- **Запрос:** OpenAlex /works filter=ids.openalex:<id>|..., select=id,references; батчи по 25; 125 работ изоляции (insulation_thermal+materials, ВСЕ,
включая пересекающиеся с NI — мосты)
- **Дата:** 
- **Записей:** 108 (с непустыми references)
- **Поля:** id -> [references...]
- **Цель:** B→A сторона перекрёстной проверки «изоляция цитирований» (NI-coils vs теплопроводная изоляция)
- **Бюджет:** OpenAlex, ~6 запросов (мягкие лимиты)
