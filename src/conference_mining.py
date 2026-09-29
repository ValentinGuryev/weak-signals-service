#!/usr/bin/env python3
"""Выгрузка статей конференций по прикладной сверхпроводимости (IEEE TAS, IOP JPCS)
с ключевыми словами провала/успеха для калибровки ретро-кейсов.

Логика:
- Источники: IEEE TAS (S119074828), J.Phys.Conf.Ser (S4390939671), + arXiv отдельно.
- Поиск по abstract.search: lessons learned, discontinued, decommissioned, failed,
  unsuccessful, terminated, cancelled, abandoned + success, milestone, commissioned.
- Сохраняем: title, year, authors, abstract (если есть), DOI, source, keywords-матчи.
"""
import json, time, urllib.request, urllib.parse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "data" / "raw" / "conferences"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "ieee_tas": "S119074828",       # IEEE Transactions on Applied Superconductivity
    "iop_jpcs": "S4390939671",      # Journal of Physics: Conference Series (EuCAS)
    "ieee_tasc_prev": "S4363608361", # 1986 ASC
}

KEYWORDS_FAIL = [
    # провал/остановка
    "lesson learned", "lessons learned", "discontinued", "decommissioned",
    "terminated", "cancelled", "abandoned", "unsuccessful", "failed project",
    "end of life", "shut down", "shutdown", "withdrawn", "not completed",
    "cost overrun", "schedule delay", "technical challenge",
]

KEYWORDS_SUCCESS = [
    # опыт эксплуатации (прямая идея пользователя)
    "operational experience", "operation experience", "in operation since",
    "operating since", "successfully operated", "successful operation",
    "commissioning and operation", "long-term operation", "long-term reliability",
    # полевые/сетевые испытания
    "field demonstration", "field test results", "grid-connected",
    "grid connection", "commercial deployment", "commercial operation",
    # экономика/готовность
    "cost-effective", "economically viable", "return on investment",
    "payback period", "technology readiness", "in service",
]

KEYWORDS = KEYWORDS_FAIL + KEYWORDS_SUCCESS

def get(url: str, retries: int = 4) -> dict:
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "hackathon-research/1.0 (mailto:test@example.com)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            code = getattr(e, "code", None)
            if code == 429:
                wait = 300 * (i + 1)  # 5-20 мин, чтобы не триггерить блокировку
                print(f"  [429] жду {wait}s...")
                time.sleep(wait)
                continue
            if i == retries - 1:
                raise
            time.sleep(5 * (i + 1))

def search(source_id: str, keyword: str, per_page: int = 200) -> list:
    """Поиск по абстракту + пагинация."""
    kw = urllib.parse.quote(keyword)
    results = []
    page = 1
    while True:
        url = (f"https://api.openalex.org/works?"
               f"filter=primary_location.source.id:{source_id},abstract.search:{kw}"
               f"&per-page={per_page}&page={page}&mailto=test@example.com")
        try:
            d = get(url)
        except Exception as e:
            print(f"  [err] {keyword} page {page}: {str(e)[:60]}")
            break
        batch = d.get("results", [])
        if not batch:
            break
        results.extend(batch)
        meta = d.get("meta", {})
        if page >= meta.get("count", 0) // per_page + 1 or len(batch) < per_page:
            break
        page += 1
        time.sleep(0.3)
    return results

def main() -> None:
    all_hits = {}   # (source, keyword) -> [works]
    summary = {}
    seen = {}  # дедупликация на лету (по DOI/id+title)

    def save_progress():
        """Сохранить текущий прогресс (защита от потери при сбое)."""
        out = []
        for key, rec in seen.items():
            w = rec["work"]
            out.append({
                "source": rec["source"],
                "keywords": rec["keywords"],
                "title": w.get("title"),
                "year": w.get("publication_year"),
                "doi": w.get("doi"),
                "authors": [a.get("author", {}).get("display_name") for a in w.get("authorships", [])][:10],
                "abstract": w.get("abstract_inverted_index") and _invert(w["abstract_inverted_index"]) or None,
                "url": w.get("id"),
                "cited_by": w.get("cited_by_count"),
            })
        (OUT_DIR / "conference_hits.json").write_text(
            json.dumps({"summary": summary, "total": len(out), "items": out}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        return len(out)

    for src_name, src_id in SOURCES.items():
        summary[src_name] = {}
        for kw in KEYWORDS:
            print(f"=== {src_name} | '{kw}' ===")
            try:
                hits = search(src_id, kw, per_page=100)
            except Exception as e:
                print(f"  ERR {str(e)[:60]}")
                continue
            summary[src_name][kw] = len(hits)
            print(f"  -> {len(hits)} статей")
            key = (src_name, kw)
            all_hits[key] = hits
            for w in hits:
                doi = w.get("doi")
                dkey = doi or (w.get("id"), w.get("title"))
                if dkey not in seen:
                    seen[dkey] = {"source": src_name, "keywords": [kw], "work": w}
                else:
                    if kw not in seen[dkey]["keywords"]:
                        seen[dkey]["keywords"].append(kw)
            total_now = save_progress()
            print(f"  [прогресс] уникальных: {total_now}")
            time.sleep(1.5)  # анти-rate-limit

    total = save_progress()
    print(f"\n=== ИТОГО: {total} уникальных статей ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

def _invert(inv: dict) -> str:
    """OpenAlex abstract_inverted_index -> текст."""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))

if __name__ == "__main__":
    main()
