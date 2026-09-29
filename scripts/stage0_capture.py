#!/usr/bin/env python3
"""Этап 0 (ночь 28→29.09): заморозка baseline живой выдачи VPS ДО правок.

Что делает:
  1. Гоняет контрольный набор запросов (6 приёмочных + 4 авторских) по
     http://85.137.95.74/api/query, сохраняет сырые JSON.
  2. Для каждой строки TECHS/TOPICS считает ПРОЗРАЧНЫЕ маркеры мусора
     (без изменения сервиса — чистая диагностика) и предварительный вердикт.
  3. Пишет человекочитаемый отчёт results/runtime/stage0_20260928/report.md
     — его смотрит автор глазами.

Правила вердикта (записаны ДО прогона, в шапке отчёта):
  TECHS:  🗑 = GENERIC-фраза ИЛИ GARBAGE_RE-матч ИЛИ bridge==0
                (ни одна linked-тема терма не входит в топ-15 тем запроса);
          ⚠  = lex==0 (ни один токен запроса не найден в терме);
          ок = иначе.
  TOPICS: 🗑 = GARBAGE_RE-матч ИЛИ (t_hit==0 И screen==0);
          ⚠  = ровно одно из (t_hit==0, screen==0);
          ок = иначе.
  t_hit — токены запроса (RU/EN) в name+name_ru; screen — Оценка NGI.
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from rank_directions_ngi import GARBAGE_RE  # noqa: E402
from build_tech_ngi import (GENERIC_PHRASES, GENERIC_MODS_EXACT,  # noqa: E402
                            GENERIC_MODS_SUFFIX, is_snippet)
import pandas as pd  # noqa: E402

BASE = "http://85.137.95.74"
# ночь 29.09: З1-замер нужно снимать с ЛОКАЛЬНОГО сервера (новые флаги №17)
# ДО деплоя — добавлен --base/--out, дефолты = канонический вид.
_ap = argparse.ArgumentParser()
_ap.add_argument("--base", default=BASE, help="базовый URL API (дефолт = VPS)")
_ap.add_argument("--out", default=None, help="каталог отчёта (дефолт канон)")
_cli = _ap.parse_args()
BASE = _cli.base
OUT = Path(_cli.out) if _cli.out else ROOT / "results" / "runtime" / "stage0_20260928"
OUT.mkdir(parents=True, exist_ok=True)

# Контрольный набор: 6 приёмочных (qa_demo_accept) + 4 запроса автора/дежурных
QUERIES = [
    "Защита ИИ",
    "Edge",
    "Индустриальный ИИ",
    "Инфраструктура ИИ",
    "Роботы",
    "Финтех",
    "прикладная сверхпроводимость",
    "защита AI",
    "Сверхпроводимость",
    "Фармацевтика",
]

TOKEN_RE = re.compile(r"[a-zа-яё0-9]{2,}", re.I)
STOP = set("""
выдай темы по защите года году и о на для от с к как при что это эти или же не нет
да все очень более самый можно нужно через про между
a an the and or of to in for on with from by at as is are be been being this that
these those it its our your their can could may might will would should must not no
do does did study paper analysis research method methods using use used data results
result new two three one artificial intelligence models model based
""".split())


def qtokens(q: str) -> list[str]:
    out, seen = [], set()
    for t in TOKEN_RE.findall(q.lower()):
        if t in STOP or t.isdigit() or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def fetch(q: str) -> dict:
    url = BASE + "/api/query?q=" + urllib.parse.quote(q)
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if attempt == 2:
                raise
            print(f"  retry after {e}", flush=True)
            time.sleep(3)


def main() -> None:
    TOPICS_DF = pd.read_parquet(ROOT / "webapp/data/taxonomy/topics.parquet")
    TID2NAME = {int(str(v).rstrip("/").split("T")[-1]): str(d)
                for v, d in zip(TOPICS_DF["id"], TOPICS_DF["display_name"])}

    lines: list[str] = []
    lines.append("# Этап 0 — baseline живой выдачи VPS (ДО правок, ночь 28→29.09)")
    lines.append(f"\nСнято: {time.strftime('%Y-%m-%d %H:%M:%S')}; {BASE}; "
                 f"контрольных запросов: {len(QUERIES)}")
    lines.append("""
## Правила предварительного вердикта (объявлены ДО прогона)

**TECHS (форма «Зарождающиеся технологии»):**
- 🗑 **кандидат в мусор** = `GENERIC_PHRASES` / `MOD` (модификатор
  «X-based/driven/advanced», коллокации Медведева) / `SNIP` (фрагмент >5 слов
  или обрывок) / `GARBAGE_RE` ИЛИ **bridge==0** — ни одна из linked-тем терма
  (топ-3 по `linked_json`) не входит в топ-15 тем того же ответа;
- ⚠ **спорно** = lex==0 — ни один токен запроса (RU/EN) не найден в терме;
- **ок** = иначе.

**TOPICS (форма «Темы»):**
- 🗑 = `GARBAGE_RE` матчит имя ИЛИ (t_hit==0 И screen==0);
- ⚠ = ровно одно из (t_hit==0, screen==0);
- **ок** = иначе.
- t_hit — токены запроса в name + name_ru; screen — Оценка NGI (новизна×рост×воздействие).

Маркеры: `lex` — токены запроса в терме; `bridge` — доля linked-тем в топ-15 ответа;
`GR` — GARBAGE_RE; `GEN` — GENERIC-фраза; `no-screen` — Оценка 0.00.
Это ДИАГНОСТИКА, сервис не меняется.
""")

    for n, q in enumerate(QUERIES, 1):
        print(f"[{n}/{len(QUERIES)}] {q}", flush=True)
        d = fetch(q)
        slug = re.sub(r"[^a-z0-9]+", "_", q.lower())[:40]
        (OUT / f"capture_{n:02d}_{slug}.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1))
        qt = qtokens(q)
        top_tids = [t["tid"] for t in d.get("topics", [])]
        lines.append(f"\n---\n## {n}. «{q}»  (tокены: {qt}; ms={d.get('retrieval',{}).get('ms')})")

        # ---- TECHS ----
        lines.append("\n### TECHS (топ-15)\n")
        lines.append("| # | term | rel | оценка | nov/gro/imp | birth | n_rec | lex | bridge | маркеры | вердикт |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for i, t in enumerate(d.get("techs", [])[:15], 1):
            tl = t["term"].lower()
            ttok = set(TOKEN_RE.findall(tl))
            lex = sorted({x for x in qt if x in ttok})
            linked = t.get("topics", [])
            bridge = sum(1 for L in linked if L["tid"] in top_tids)
            marks, verdict = [], "ок"
            if tl in GENERIC_PHRASES:
                marks.append("GEN")
            if any(tok in GENERIC_MODS_EXACT or
                   tok.endswith(GENERIC_MODS_SUFFIX) for tok in ttok):
                marks.append("MOD")
            if is_snippet(t["term"]):
                marks.append("SNIP")
            if GARBAGE_RE.search(t["term"]):
                marks.append("GR")
            if bridge == 0:
                marks.append("bridge=0")
            if not lex:
                marks.append("lex=0")
            if ("GEN" in marks or "GR" in marks or "MOD" in marks or
                    "SNIP" in marks or bridge == 0):
                verdict = "🗑"
            elif not lex:
                verdict = "⚠"
            lines.append(
                f"| {i} | {t['term']} | {t['rel']:.3f} | {t['score']:.2f} | "
                f"{t['novelty']:.2f}/{t['growth']:.2f}/{t['impact']:.2f} | "
                f"{t['birth']} | {t['n_recent']} | {','.join(lex) or '—'} | "
                f"{bridge}/{len(linked)} | {','.join(marks) or '—'} | {verdict} |")

        # ---- TOPICS ----
        lines.append("\n### TOPICS (топ-15)\n")
        lines.append("| # | name / name_ru | screen | rel | birth | t_hit | маркеры | вердикт |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for i, t in enumerate(d.get("topics", [])[:15], 1):
            blob = f"{t.get('name','')} {t.get('name_ru','')}".lower()
            thit = sorted({x for x in qt if x in blob})
            marks, verdict = [], "ок"
            gr = bool(GARBAGE_RE.search(t.get("name", "")))
            if gr:
                marks.append("GR")
            if not thit:
                marks.append("t_hit=0")
            if float(t.get("screen", 0)) == 0:
                marks.append("no-screen")
            if gr or (not thit and float(t.get("screen", 0)) == 0):
                verdict = "🗑"
            elif (not thit) or float(t.get("screen", 0)) == 0:
                verdict = "⚠"
            lines.append(
                f"| {i} | {t.get('name','')} / {t.get('name_ru','')} | "
                f"{t.get('screen',0):.3f} | {float(t.get('rel',0)):.3f} | "
                f"{t.get('birth','—')} | {','.join(thit) or '—'} | "
                f"{','.join(marks) or '—'} | {verdict} |")

        # ---- сводка ----
        tech_v = sum(1 for L in lines[-40:] if L.endswith("| 🗑 |"))
        lines.append(f"\n_Сводка по запросу: см. маркеры/вердикты выше; "
                     f"retro2026: {[r['item'] for r in d.get('retro2026', [])]}_")

    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"DONE -> {OUT / 'report.md'}", flush=True)


if __name__ == "__main__":
    main()
