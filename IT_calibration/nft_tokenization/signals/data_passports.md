# Паспорта данных кейса NFT (2026-09-15)

Паспорта по §4.5 внутренний контракт. Все базы — локальные, коммитятся в git (малые JSON).

## 1. HN внимание — `raw/hn_attention_nft.json`

- **Скрипт:** сниппет ниже (одноразовый; воспроизводим).
- **Запросы:** HN Algolia `search_by_date`, `tags=story`, `restrictSearchableAttributes=title`,
  `advancedSyntax=true`, `typoTolerance=false`, фразы `"nft"` и `"non-fungible token"`, 2017–2026.
- **Дата:** 2026-09-15 · **число запросов:** ~22 (free, без квоты).
- **Поля:** год → nbHits (число историй). + серия-контроль `"metaverse"` (валидация методики с документом).
- **Восстановление:** повторный вызов API (методика в комментарии к скрипту).

```python
import time, urllib.request, urllib.parse, json
def hn_year(q, y):
    p = {"query": q, "tags": "story",
         "numericFilters": f"created_at_i>={int(time.mktime(time.strptime(f'{y}-01-01','%Y-%m-%d')))},created_at_i<{int(time.mktime(time.strptime(f'{y+1}-01-01','%Y-%m-%d')))}",
         "hitsPerPage": "0", "restrictSearchableAttributes": "title",
         "advancedSyntax": "true", "typoTolerance": "false"}
    u = "https://hn.algolia.com/api/v1/search_by_date?" + urllib.parse.urlencode(p)
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"research-it-calib"}), timeout=30) as r:
        return json.loads(r.read().decode())["nbHits"]
```

## 2. GitHub инженерия — `raw/github_engineering_nft.json`

- **Скрипт:** вызов Search API, `created:YYYY-01-01..YYYY-12-31`, 3 запроса (`erc721 in:name,description,topics`,
  `"non-fungible token" in:name,description,topics`, `"nft" marketplace in:name,description,topics`), 2016–2026.
- **Дата:** 2026-09-15 · **число запросов:** ~37 (free, rate 10/min — паузы 6.3–12 с; 2 ошибки 403 дозаполнены).
- **Поля:** год → total_count; top_repos (поля name/stars/desc/created) для валидации.
- **Восстановление:** повторный вызов с паузой ≥6.5 с между запросами.

## 3. OpenAlex наука — `raw/openalex_nft_title_abstract.json`, `raw/openalex_non_fungible_token_full.json`

- **Запросы:** `works?mailto=...&filter=title_and_abstract.search:"non-fungible token"&group_by=publication_year&per_page=100`
  (канон) и `search="non-fungible token"` (контроль fulltext).
- **Дата:** 2026-09-15 · **число запросов:** 2 (free; rate-limit по частоте — паузы 1.5 с).
- **Поля:** год → count.
- **Восстановление:** повторный вызов (нотис: 2026 неполный год, счёт по 15.09.2026).

## 4. Рынок — факты в `market_signal.md`

- Источники: Wikipedia (Non-fungible token, OpenSea) с цитатами WSJ/TechCrunch/Forbes/dappGambl.
- Восстановление: ссылки в таблицах `market_signal.md`.

## Итого расход API-бюджета
- Lens.org: **0** (по решению: патенты отложены до сброса 30.09).
- Google Patents: 0. Платных: 0.
## 5. USPTO патенты — `raw/uspto_nft_patents.json`

- **Канал:** MCP patent-client-agents → **USPTO PPUBS** (бесплатный полнотекстовый поиск US-патентов;
  впервые доступен после закрытия Lens 2026-09-16). Ранее слой был `deferred_until_lens`.
- **Запросы (2026-09-20):** `"non-fungible token"` и `"digital asset tokenization"`, юрисдикция US,
  пагинация до 100/страница. ~5 вызовов PPUBS (бесплатно, без квоты).
- **Поля:** publication_number, title, pub, filing, applicant, cc (класс), rel (core/infra/noise), fam.
- **Число записей:** 32 публикации → 27 семей (L2-дедуп: assignee+смысл; Tulip ×3, HIWAVE ×2×2, Templum ×2).
- **Восстановление:** повторный поиск через MCP patentclient + дедуп L2.
- ⚠️ PPSUBS полнотекст → 9/32 шум (фраза случайно в тексте); считать только core+infra по титулу.
