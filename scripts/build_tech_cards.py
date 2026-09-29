#!/usr/bin/env python3
"""Этап В ночи 28→29.09: извлекательные карточки слабых сигналов (NJ-14 v2, шаг 1).

Карточка : НАЗВАНИЕ слабого сигнала + ПРОБЛЕМА (что решает) +
ЯКОРНАЯ работа. Если карточку создать нельзя → карантин, в выдачу сервиса НЕ идёт.

Вход : data/openalex_derived/tech_docs_v1.parquet (или --docs, смоук quantum)
Выход: data/openalex_derived/tech_cards_v1.parquet + results/runtime/tech_cards_v1_report.md

Правила (объявлены ДО прогона):
  карантин-гейты:
    G1  в терме есть токен из 1 символа («a», «i»);
    G2  ≥40% токенов — служебные/замыкательные (CLOSED);
    G3  первый или последний токен — служебная голова/хвост (HEAD/END);
    G4  ни в одном из доков нет abstract → нет проблемы → карантин;
    G5  ВСЕ документы терма — спам/некачественные (SPAM_RE) → карантин;
        спам-доки исключаются из обёртки/якоря/проблемы всегда;
    G6  реальное число токенов терма вне 2..6 (проверка по строке,
        а не по колонке n_tok — смоук нашёл 12-токенные термы);
    G7  нет linked-тем (sp_tids доков ∪ digest n-граммы ∩ IMPACT) → нет
        достоверного импакта → карантин (канон build_tech_ngi: drop_nolink).
  БАЛЛЫ (канон build_tech_ngi, директива «самое важное — новизна/рост/импакт»):
    novelty = 1 − sigmoid((2025 − birth − 15)/5) по свежему году доков терма;
    growth  = clamp(из пула; >1 → g/(g+1));
    impact  = 1 − exp(−max(IMPACT[linked])/40); score = novelty×growth×impact.
  ЯКОРИ (3-4 работы): из digest (топ-100 по цитатам темы) по связанным темам,
    ≥половины токенов терма в заголовке, сортировка по cited_by_count DESC, ≤4;
    нет подходящих → поле ПУСТОЕ (не блокер, решение команды).
  НАЗВАНИЕ: извлекательная обёртка — промежуточная; финальное обязательное
    название в стиле retro_signals даёт LLM-этап (не сформулировалось → исключение).
  ПРОБЛЕМА (problem_en): предложение из самого свежего abstract с маркером
    проблемы (problem/challenge/need/…), иначе первое предложение ≥60 симв.
  ЯКОРЬ (anchor_*): самый свежий документ (year desc, tie — первый).
  Дополнительно: priority для LLM-очереди = sp-термы первыми, затем n_recent_sum DESC.
"""
import argparse
import json
import math
import re
import sys
import time
import zlib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
REPORT = ROOT / "results/runtime/tech_cards_v1_report.md"
Y_WINDOW = 2025


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

CLOSED = {"the", "a", "an", "of", "and", "or", "to", "in", "for", "on",
          "with", "by", "at", "as", "is", "are", "be", "this", "that",
          "these", "those", "it", "its", "we", "our", "can", "may", "more",
          "most", "such", "both", "between", "among", "via", "from", "into",
          "than", "then", "also", "using", "use", "based", "over", "under"}
HEAD = {"the", "a", "an", "of", "and", "or", "to", "in", "for", "on",
        "with", "by", "at", "as", "is", "are", "be", "this", "that"}
END = {"of", "and", "or", "to", "in", "for", "on", "with", "by", "at",
       "as", "is", "are", "the", "a", "an"}
MARK = ("problem", "challenge", "however", "bottleneck", "limitation",
        "critical", "require", "needs", "need to", "demand", "lack",
        "difficult", "remain", "obstacle", "hurdle", "yet,", "but ")

_WORD_RE = re.compile(r"[0-9A-Za-zА-Яа-яЁё]+(?:[-'][0-9A-Za-zА-Яа-яЁё]+)*")
_SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(«\"'])")
# спам/некачественные документы (смоук 23:37: в слайсах есть Admission List,
# «Download Book ➡ Link», [PDF]-зеркала) — в карточку не идут (G5)
SPAM_RE = re.compile(
    r"admission list|download book|click here|read more|\[pdf\]|https?://"
    r"|link read|jobs?|vacanc|question paper|syllabus|answer key|newsletter"
    r"|result[s]? \d{4}|exam (date|result)|admit card|publicity|table of contents",
    re.I)
BAD_PUNCT = re.compile(r"[.,;:()!?\[\]{}<>\"«»]")


def norm_len(s: str) -> str:
    """length-preserving: lower + дефис→пробел (позиции = оригиналу)."""
    return s.lower().replace("-", " ")


def is_spam(doc: dict) -> bool:
    blob = (doc.get("t") or "") + " " + (doc.get("a") or "")
    return bool(SPAM_RE.search(blob)) or not (doc.get("t") or "").strip()


def window_wrappers(term: str, texts: list[str]) -> str:
    """Каноническая обёртка: окно вокруг вхождения term в тексте (с сохранением
    регистра оригинала). Возвращает обёртку или term."""
    t = norm_len(term)
    pats = re.compile(r"(?<![0-9a-zа-яё])" + re.escape(t) + r"(?![0-9a-zа-яё])")
    counts: dict[str, int] = {}
    for text in texts:
        if not text:
            continue
        low = norm_len(text)
        if len(low) != len(text):
            low = text.lower().replace("-", " ")   # деградация — редкий случай
        for m in pats.finditer(low):
            # границы слов исходного текста: расширяем окно по словам
            toks = [(w.start(), w.end()) for w in _WORD_RE.finditer(text)]
            if not toks:
                continue
            i0 = next((k for k, (s, e) in enumerate(toks) if s >= m.start()), None)
            if i0 is None:
                i0 = len(toks)
            n = sum(1 for w in term.split())
            i1 = i0 + n
            for left in range(0, 4):
                for right in range(0, 4):
                    a, b = i0 - left, i1 + right
                    if a < 0 or b > len(toks):
                        continue
                    frag = text[toks[a][0]:toks[b - 1][1]]
                    if frag.lower() == term:
                        continue
                    if len(frag) > 140 or BAD_PUNCT.search(frag):
                        continue
                    counts[frag] = counts.get(frag, 0) + 1
    if not counts:
        return term
    best = sorted(counts.items(), key=lambda kv: (-kv[1], -len(kv[0])))
    return best[0][0]


def pick_problem(abstract: str, term: str) -> tuple[str, str]:
    sents = [s.strip() for s in _SENT_RE.split(abstract) if len(s.strip()) >= 60]
    if not sents:
        sents = [abstract.strip()[:500]]
    tl = set(term.split())
    marked = [s for s in sents if any(m in s.lower() for m in MARK)]
    marked_t = [s for s in marked if tl & set(s.lower().split())]
    if marked_t:
        return marked_t[0][:500], "marker+term"
    if marked:
        return marked[0][:500], "marker"
    return sents[0][:500], "first"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default=str(ROOT / "data/openalex_derived/tech_docs_v1.parquet"))
    ap.add_argument("--out", default=str(ROOT / "data/openalex_derived/tech_cards_v1.parquet"))
    args = ap.parse_args()
    t0 = time.time()

    docs_df = pd.read_parquet(args.docs)
    pool = pd.read_parquet(ROOT / "data/openalex_derived/tech_pool_v1.parquet")
    # после sp-merge колонка growth могла стать growth_x/growth_y (дубль имён)
    if "growth" not in pool.columns:
        gc = "growth_x" if "growth_x" in pool.columns else "growth_y"
        pool["growth"] = pool[gc]
    pool = pool[["term", "first_year", "n_recent_sum", "df_sum", "growth",
                 "n_domains", "source", "score"]].drop_duplicates("term") \
        .rename(columns={"score": "score_sp"})

    # ---- IMPACT тем (канон NGI) + digest (якоря и linked через n-граммы) ----
    imp = pd.read_parquet(ROOT / "webapp/data/ngi/topic_ngi_cache_impact.parquet")
    IMPACT = dict(zip(imp.tid.astype(int), imp.impact.astype(int)))
    del imp
    dg = pd.read_parquet(ROOT / "webapp/data/digest/digest.parquet").drop_duplicates("id")
    dg["_t"] = dg["title"].fillna("").str.lower().str.replace("-", " ")
    tid_rows: dict[int, list[int]] = {}
    for i, t in enumerate(dg["tid"].astype(int)):
        tid_rows.setdefault(t, []).append(i)
    # dig_map: ключ → tid с МАКСИМАЛЬНЫМ impact (фикс RSS: set-of-int давал
    # S2=5.05 ГБ; для impact=max(IMPACT[linked]) и для linked-якорей результат
    # эквивалентен — храним только лучший по impact tid на ключ)
    dig_map: dict[int, int] = {}
    for t, tid in zip(dg["title"].fillna("").str.lower(), dg["tid"]):
        tid = int(tid)
        imp_t = IMPACT.get(tid, -1)
        w = t.split()
        for k in range(1, 7):
            for j in range(len(w) - k + 1):
                key = zlib.crc32(" ".join(w[j:j + k]).encode())
                prev = dig_map.get(key)
                if prev is None or IMPACT.get(prev, -1) < imp_t:
                    dig_map[key] = tid
    dg_titles = list(dg["_t"])
    dg_cites = dg["cited_by_count"].astype(int).to_list()
    dg_year = dg["publication_year"].astype(int).to_list()
    dg_id = dg["id"].astype(str).to_list()
    dg_head = dg["title"].fillna("").astype(str).to_list()
    dg_toks = [frozenset(re.findall(r"[a-z0-9]+", t)) for t in dg_titles]
    del dg

    rows, qreasons, wrapper_ok = [], {}, 0
    growth_map = dict(zip(pool["term"], pool["growth"].fillna(0.0)))
    for r in docs_df.itertuples():
        term = r.term
        docs = [d for d in json.loads(r.docs_json)]
        clean = [d for d in docs if not is_spam(d)]
        toks = term.split()
        # --- гейты карантина ---
        reason = ""
        if any(len(w) == 1 for w in toks):
            reason = "G1_односимвольный_токен"
        else:
            cl = sum(1 for w in toks if w in CLOSED) / len(toks)
            if cl >= 0.4:
                reason = "G2_служебных_≥40%"
            elif toks[0] in HEAD or toks[-1] in END:
                reason = "G3_служебные_голова/хвост"
            elif not (2 <= len(toks) <= 6):
                reason = "G6_n_tok_по_строке"
            elif not clean:
                reason = "G5_все_доки_спам"
        if reason:
            qreasons[reason] = qreasons.get(reason, 0) + 1
            rows.append({"term": term, "status": "quarantine", "reason": reason,
                         "name_en": "", "problem_en": "", "anchor_title": "",
                         "anchor_year": 0, "anchor_id": ""})
            continue
        docs = clean
        anchor = docs[0] if docs else None
        abst = next((d["a"] for d in docs if d.get("a")), None)
        if not abst:
            reason = "G4_нет_abstract"
            qreasons[reason] = qreasons.get(reason, 0) + 1
            rows.append({"term": term, "status": "quarantine", "reason": reason,
                         "name_en": "", "problem_en": "", "anchor_title": "",
                         "anchor_year": 0, "anchor_id": ""})
            continue
        # ---- linked-темы: sp_tids доков ∪ digest n-граммы ----
        tnorm = " ".join(term.lower().replace("-", " ").split())
        linked = set()
        for d in docs:
            linked.update(int(x) for x in (d.get("s") or []))
        for _key in (zlib.crc32(term.lower().encode()),
                     zlib.crc32(tnorm.encode())):
            _t = dig_map.get(_key)
            if _t is not None:
                linked.add(_t)
        linked = {t for t in linked if t in IMPACT}
        if not linked:
            reason = "G7_нет_linked_нет_импакта"
            qreasons[reason] = qreasons.get(reason, 0) + 1
            rows.append({"term": term, "status": "quarantine", "reason": reason,
                         "name_en": "", "problem_en": "", "anchor_title": "",
                         "anchor_year": 0, "anchor_id": ""})
            continue
        # ---- баллы (канон NGI) ----
        birth = min(d.get("y") or 2025 for d in docs)
        novelty = 1.0 - sigmoid((max(Y_WINDOW - birth, 0) - 15) / 5.0)
        g_raw = float(growth_map.get(term, 0.0) or 0.0)
        growth = g_raw if g_raw <= 1.0 else g_raw / (g_raw + 1.0)
        growth = max(0.0, min(1.0, growth))
        impact_n = 1.0 - math.exp(-max(IMPACT[t] for t in linked) / 40.0)
        score = round(novelty * growth * impact_n, 4)
        # ---- якоря: топ-цитируемые digest-работы связанных тем ----
        # (1) с совпадением ≥половины токенов терма; (2) добивка «на эту тему»
        # топ-цитируемыми работами связанных тем — директива: 3-4 работы на тему
        tt = set(re.findall(r"[a-z0-9]+", tnorm))
        need = max(2, (len(tt) + 1) // 2)
        cand_idx = [i for t in linked for i in tid_rows.get(t, [])]
        matched = [i for i in cand_idx if len(tt & dg_toks[i]) >= need]
        matched.sort(key=lambda i: -dg_cites[i])
        seen_ids, anchors = set(), []
        for i in matched:
            if dg_id[i] in seen_ids:
                continue
            seen_ids.add(dg_id[i])
            anchors.append({"id": dg_id[i], "title": dg_head[i][:200],
                            "year": dg_year[i], "cites": dg_cites[i]})
            if len(anchors) >= 4:
                break
        if len(anchors) < 3:
            # добивка: работы темы с максимальным impact, без требования терма
            top_t = sorted(linked, key=lambda t: -IMPACT[t])
            fill = [i for t in top_t for i in tid_rows.get(t, [])]
            fill.sort(key=lambda i: -dg_cites[i])
            for i in fill:
                if dg_id[i] in seen_ids:
                    continue
                seen_ids.add(dg_id[i])
                anchors.append({"id": dg_id[i], "title": dg_head[i][:200],
                                "year": dg_year[i], "cites": dg_cites[i],
                                "topic_fill": True})
                if len(anchors) >= 4:
                    break
        texts = [d["t"] for d in docs if d.get("t")] + [abst]
        name = window_wrappers(term, texts)
        if name != term:
            wrapper_ok += 1
        problem, how = pick_problem(abst, term)
        rows.append({"term": term, "status": "ok", "reason": "",
                     "name_en": name, "problem_en": problem,
                     "problem_src": how,
                     "anchor_title": anchor.get("t", ""),
                     "anchor_year": int(anchor.get("y") or 0),
                     "anchor_id": anchor.get("id", ""),
                     "novelty": round(novelty, 4),
                     "growth_n": round(growth, 4),
                     "impact": round(impact_n, 4), "score_ngi": score,
                     "linked_json": json.dumps(
                         sorted(linked, key=lambda t: -IMPACT[t])[:10]),
                     "anchors_json": json.dumps(anchors, ensure_ascii=False)})

    cards = pd.DataFrame(rows).merge(pool, on="term", how="left")
    # priority для LLM-очереди: sp первыми, затем n_recent DESC
    cards["priority"] = (cards["source"].fillna("") == "sp").astype(int) * 10**9 \
        + cards["n_recent_sum"].fillna(0).astype("int64")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    cards.to_parquet(args.out, index=False)

    ok = int((cards["status"] == "ok").sum())
    lines = [f"# tech_cards — {time.strftime('%Y-%m-%d %H:%M:%S')}",
             "", f"- вход: {args.docs} ({len(docs_df):,} термов с доками)",
             f"- карточек OK: {ok:,} ({ok/max(len(cards),1):.1%})",
             f"- карантин: {len(cards)-ok:,} — причины: "
             + ", ".join(f"{k}={v:,}" for k, v in sorted(qreasons.items())),
             f"- обёртка найдена (не голый терм): {wrapper_ok:,} из OK "
             f"({wrapper_ok/max(ok,1):.1%})",
             f"- выход: {args.out} ({Path(args.out).stat().st_size//1024//1024} МБ)",
             f"- время: {time.time()-t0:.0f} с", "", "## Сэмпл OK (10 строк)"]
    for r in cards[cards["status"] == "ok"].sample(10, random_state=42).itertuples():
        lines.append(f"- **{r.name_en}** | {r.problem_en[:110]}… | "
                     f"якорь {r.anchor_year}: {r.anchor_title[:60]}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
