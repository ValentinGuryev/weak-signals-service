# Паспорт: JPA-резонаторный корпус (для S3-cross, кейс 007)

- **Файлы:** `data/raw/openalex/jpa_resonator_corpus.json` (386 работ), `jpa_resonator_full.json` (references, 386)
- **Скрипт:** `src/openalex_jpa_resonator.py` (сбор + докачка refs), `src/s3_cross_jtwpa.py` (анализ)
- **Запрос:** title_and_abstract.search "Josephson parametric amplifier" МИНУС traveling-wave (те в JTWPA-корпусе)
- **Дата:** 
- **Поля:** id, title, year, cited_by, authors, source; full: referenced_works
- **Бюджет:** OpenAlex — через SOCKS-прокси (127.0.0.1:9051), прямой IP исчерпал дневной лимит (~10 запросов + 8 пачек refs)
