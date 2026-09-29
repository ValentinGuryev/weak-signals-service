#!/usr/bin/env python3
"""Докачка грантов SMES: NSF + CORDIS (кейс 005, грантовый сигнал).

Запросы (по решению команды):
  NSF:    "superconducting magnetic energy storage" (+ "SMES" если мало)
  CORDIS: "superconducting magnetic energy storage", "SMES"
Выход: data/raw/grants_foreign/{nsf_smes,cordis_smes}_results.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import PROJECT_ROOT

from grants_foreign import fetch_nsf as nsf_search
from grants_cordis import fetch_cordis as cordis_search

NSF_KW = ["superconducting magnetic energy storage", "SMES energy storage"]
CORDIS_KW = ["superconducting magnetic energy storage", "SMES"]


def main() -> None:
    # NSF
    nsf_rows = []
    for kw in NSF_KW:
        try:
            rows = nsf_search(kw, max_pages=4)
            for r in rows:
                r["query"] = kw
            nsf_rows.extend(rows)
            print(f"NSF '{kw}': {len(rows)}")
        except Exception as e:
            print(f"NSF '{kw}' ERR: {e}")
    out = PROJECT_ROOT / "data/raw/grants_foreign/nsf_smes_results.json"
    out.write_text(json.dumps({"method": "nsf API без ключа", "count": len(nsf_rows),
                               "grants": nsf_rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"NSF SMES сохранено: {len(nsf_rows)} -> {out}")

    # CORDIS
    cord_rows = []
    for kw in CORDIS_KW:
        try:
            rows = cordis_search(kw, num=20, max_pages=3)
            for r in rows:
                r["query"] = kw
            cord_rows.extend(rows)
            print(f"CORDIS '{kw}': {len(rows)}")
        except Exception as e:
            print(f"CORDIS '{kw}' ERR: {e}")
    out2 = PROJECT_ROOT / "data/raw/grants_foreign/cordis_smes_results.json"
    out2.write_text(json.dumps({"method": "CORDIS API", "count": len(cord_rows),
                                "projects": cord_rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"CORDIS SMES сохранено: {len(cord_rows)} -> {out2}")


if __name__ == "__main__":
    main()
