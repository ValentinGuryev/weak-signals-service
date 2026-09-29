#!/usr/bin/env python3
"""Докачка метаданных внешних целей (OpenAlex) для s3_external_diversity.

Внешние ссылки ранних работ (рождение темы): flux pump 2010-11 vs joint 2017-18.
Нужны: title, publication_year, primary_location (журнал), concepts (для области).
OpenAlex: бесплатный, батчи по 50 (filter=openalex_id|...), мягкие лимиты.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDS = json.loads(Path("/tmp/ext_ids.json").read_text())
OUT = ROOT / "data/raw/openalex" / "s3_external_meta.json"

BASE = "https://api.openalex.org/works"


def fetch_batch(ids: list[str]) -> list[dict]:
    filt = "|".join(ids)
    url = f"{BASE}?filter=ids.openalex:{filt}&per-page=50&select=id,title,publication_year,primary_location,concepts,topics"
    req = urllib.request.Request(url, headers={"User-Agent": "hackathon-research mailto:test@example.com"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    return data.get("results", [])


def main() -> None:
    # загрузим уже скачанное (если есть) для продолжения
    done: dict[str, dict] = {}
    if OUT.exists():
        done = json.loads(OUT.read_text())
        print(f"уже есть: {len(done)}")

    todo = [i for i in IDS if i not in done]
    print(f"докачать: {len(todo)} работ")

    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        try:
            results = fetch_batch(batch)
            for w in results:
                wid = w["id"].split("/")[-1]
                done[wid] = {
                    "title": w.get("title"),
                    "year": w.get("publication_year"),
                    "venue": (w.get("primary_location") or {}).get("source", {}).get("display_name")
                    if (w.get("primary_location") or {}).get("source") else None,
                    "concepts": [c["display_name"] for c in (w.get("concepts") or [])[:5]],
                    "topics": [(t.get("display_name") or (t.get("subfield") or {}).get("display_name"))
                               for t in (w.get("topics") or [])[:2]],
                }
            print(f"  батч {i//50+1}/{(len(todo)+49)//50}: +{len(results)} (всего {len(done)})")
        except Exception as e:
            print(f"  ошибка на батче {i//50+1}: {e}")
        time.sleep(0.5)  # вежливость

    OUT.write_text(json.dumps(done, ensure_ascii=False, indent=1))
    print(f"\nсохранено: {OUT}, всего {len(done)}")


if __name__ == "__main__":
    main()
