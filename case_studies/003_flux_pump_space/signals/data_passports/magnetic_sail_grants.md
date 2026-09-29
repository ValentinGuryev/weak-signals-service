# Паспорт: гранты и публикации магнитного паруса ()

**Файлы:**
- data/raw/grants_foreign/kaken_magnetic_sail.json — 11 KAKEN-грантов (Япония), ключи 磁気セイル/磁気プラズマセイル
- data/raw/openalex/magnetic_sail_sc_corpus.json — 42 публикации «парус+СП» (title_and_abstract.search)
**Канал:** KAKEN API (kaken.nii.ac.jp/en/search), OpenAlex через SOCKS-прокси 127.0.0.1:9051
**Дата:** . **Записей:** 11 грантов + 42 публикации.
**Поля KAKEN:** grant_number, title, pi, institution, category, period, status, url.
**Поля корпуса:** id, doi, title, year, cites, authors, insts, venue, abstract_inverted_index.
**Как восстановить:** запросы выше; ~30 запросов KAKEN + ~10 OpenAlex (VPS).
**Ограничения:** NSF/CORDIS проверены (0 MPS); NSFC недоступен (playwright: нет libasound, нет root);
РНФ — SPA, ручной поиск «Комбаев» на rscf.ru.
