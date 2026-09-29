#!/usr/bin/env python3
"""TermTech — отбраковка очевидного мусора (слой выдачи, ПОСЛЕ frozen-конвейера).

Причина (пилот 25.09): топ по growth засорён техническим мусором abstract'ов:
XML/MathML-разметкой («xmlns a http», «math mrow», «c mi») и copyright-строками
изданств («american physical society 2024», «published by the american»).
Это НЕ технологии и НЕ ключевые слова — это артефакты восстановления текста
из abstract_inverted_index.

Правила (стандартные, сформулированы ДО просмотра выдачи; НЕ тюнинговались
на QA-запросах и НЕ содержат технологий из eval-списка):
  R1  маркировка/ссылки: любой токен из MARKUP_STOP (xmlns, http, w3.org,
      mathml, mrow, msub, …) → термин отбрасывается;
  R2  годы: токен-год 19xx/20xx → отбрасывается (год — не имя технологии);
  R3  boilerplate издательств: published/copyright/proceedings/society/
      institute/… → отбрасывается;
  R4  обрывки: все токены длиной ≤2 символа ИЛИ нет ни одного токена ≥3
      символов → отбрасывается («c mi», «e mi»);
  R5  числа: термин состоит только из цифр/разделителей → отбрасывается.
  R6  CSS/HTML-фрагменты: inline, span, div, class, style, block, css, br
      («display inline c» — классы вёрстки из HTML-abstract'ов);
  R7  affiliation/контакты авторов: correspondence, email, tel, these, authors,
      contributed, republic, affiliation + словослияния («republic of china
      email», «workcorrespondence»);
  R8  общая академическая фразеология (standard academic filler): valuable,
      insights, offering, findings, underscore, garnered, holds, provides,
      equally, significant + ast (звёздочка-сноска).
  R9  артефакты документа/вёрстки: подписи к рисункам (image, download,
      powerpoint, slide, resolution), метаданные архивов (collection,
      photograph, taken), домены/URL в токене, диапазоны годов (1932-1933),
      атрибуты directionality (dir, ltr, rtl), география-адрес (province);

Проверка целостности: recall маркеров eval-списка (§5 дизайна) ДОЛЖЕН остаться
12/14 — маркеры не содержат мусорных токенов; падение recall = фильтр сломан.

Выход:
  results/termtech/candidates_clean.parquet
  results/termtech/top_terms_clean.md
  results/termtech/filter_report.json   (сколько отсеяно по правилам + recall)

Запуск: .venv/bin/python scripts/termtech_filter.py
"""
import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INDIR = ROOT / "results/termtech"
sys.path.insert(0, str(ROOT / "scripts"))

# --- R1: разметка/ссылки (XML, MathML, LaTeX-окружение в abstract) ---
MARKUP_STOP = set("""
xmlns http https www w3 org com net edu
mathml math mrow mi mn msup msub mfrac mover munder mtd mtr mtable
mtext mspace mstyle merror mpadded mfenced menclose mglyph maction
annotation semantics xml ns xlink href svg g alttext
lt gt amp quot apos
""".split())

# --- R6: CSS/HTML-фрагменты вёрстки ---
CSS_STOP = set("""
inline span div class style block css br
""".split())

# --- R7: affiliation/контакты (авторские блоки в abstract) ---
AFFIL_STOP = set("""
correspondence email e-mail tel these authors contributed republic
affiliation address institution
""".split())

# подстрочные маркеры (словослияния: workcorrespondence, chinacorrespondence,
# 163.combackground, china 2department)
SUBSTR_BAD = ["correspondence", "xmlns", "insight", "garnered", "underscore",
              "department", "hospital", "affiliated", ".com", ".org",
              ".edu", ".net", ".cn"]

# --- R8: общая академическая фразеология ---
FILLER_STOP = set("""
valuable insights offering findings underscore underscored garnered holds
provides providing equally significant demonstrates highlighting underscores
reveals important across diverse transformative potential leveraging
comprehensive various several numerous underscoring emphasizing guidance
""".split())

# --- R9: артефакты документа (подписи, архивы, атрибуты вёрстки) ---
ARTIFACT_STOP = set("""
image images download downloads powerpoint slide slides resolution
supplementary document documents collection photograph photographs taken
website web page click link
ast dir ltr rtl province shanghai beijing
scriptlevel stretchy mml mo mtext fax lotte jacobi doan
equationequation multiscripts
""".split())
DOMAIN_RE = re.compile(r"^(https?://|www\.)|\.(edu|org|com|gov|net|io|cn|ru)$")
CSSLEN_RE = re.compile(r"^\d+(\.\d+)?(em|px|ex|pt|rem|%)$")
SINGLE_DIGIT_RE = re.compile(r"^[0-9]$")

# --- R3: boilerplate издательств/метаданных ---
BOILERPLATE_STOP = set("""
published publisher publishing copyright reserved
proceedings proceeding journal journals
institute association university department college school
society society's american physical review letters letter
volume vol pp doi arxiv preprint
licensed creative commons attribution
international conference symposium workshop
""".split())

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-+#.][a-z0-9]+)*")
YEAR_RE = re.compile(r"^(19|20)\d{2}([-–/.](19|20)?\d{2})?$")

# eval-список §5 дизайна (для проверки целостности фильтра)
EVAL_MARKERS = {
    "superconducting_diode": ["superconducting diode", "josephson diode",
                              "superconducting diode effect"],
    "snspd": ["superconducting nanowire single-photon detector",
              "nanowire single-photon", "snspd"],
    "jtwpa": ["josephson traveling-wave parametric amplifier",
              "traveling-wave parametric", "jtwpa"],
    "flux_pump": ["flux pump"],
    "ibad": ["ion-beam assisted deposition", "ibad"],
    "rce_dr": ["reactive co-evaporation", "rce dr"],
    "coated_conductor": ["coated conductor", "rebco tape", "2g hts"],
    "mgb2": ["mgb2", "magnesium diboride"],
    "smes": ["superconducting magnetic energy storage"],
    "ni_coils": ["no-insulation", "ni coil", "no insulating"],
    "corc": ["corc cable", "conductor on round core"],
    "sfcl": ["superconducting fault current limiter", "sfcl"],
    "hydrides": ["superconducting hydride", "hydrogen-rich superconduct"],
    "nb3sn": ["nb3sn", "niobium-tin"],
}


def norm(t: str) -> str:
    return re.sub(r"\s+", " ", str(t).strip().lower())


def reject_reason(term: str) -> str | None:
    toks = TOKEN_RE.findall(term.lower())
    if not toks:
        return "R5_empty"
    if all(t.isdigit() for t in toks):
        return "R5_numeric"
    if any(t in MARKUP_STOP for t in toks):
        return "R1_markup"
    if any(YEAR_RE.match(t) for t in toks):
        return "R2_year"
    if any(t in BOILERPLATE_STOP for t in toks):
        return "R3_boilerplate"
    if max(len(t) for t in toks) < 3:
        return "R4_stub"
    if any(t in CSS_STOP for t in toks):
        return "R6_css"
    if any(t in AFFIL_STOP for t in toks) or any(
            any(m in t for m in SUBSTR_BAD) for t in toks):
        return "R7_affil"
    if any(t in FILLER_STOP for t in toks):
        return "R8_filler"
    if (any(t in ARTIFACT_STOP for t in toks)
            or any(DOMAIN_RE.match(t) for t in toks)
            or any(CSSLEN_RE.match(t) for t in toks)
            or any(SINGLE_DIGIT_RE.match(t) for t in toks)):
        return "R9_artifact"
    return None


def recall(terms_norm: set[str]) -> dict:
    res = {}
    for name, markers in EVAL_MARKERS.items():
        found = None
        for m in markers:
            mn = norm(m)
            for t in terms_norm:
                if mn == t or f" {mn} " in f" {t} " or t.startswith(mn + " ") \
                        or t.endswith(" " + mn):
                    found = m
                    break
            if found:
                break
        res[name] = found
    return res


def main() -> int:
    global INDIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", default=None,
                    help="каталог с результатами termtech_mine (для доменных цепочек NJ-5..9)")
    args = ap.parse_args()
    if args.indir:
        INDIR = Path(args.indir)
    cand = pd.read_parquet(INDIR / "candidates.parquet")
    print(f"кандидатов до фильтра: {len(cand)}")

    reasons = cand["term"].map(reject_reason)
    keep = reasons.isna()
    rejected = cand[~keep].copy()
    rejected["reason"] = reasons[~keep]

    clean = cand[keep].copy()
    clean.to_parquet(INDIR / "candidates_clean.parquet", compression="zstd")

    # recall до/после
    before = recall({norm(t) for t in cand["term"]})
    after = recall({norm(t) for t in clean["term"]})
    n_before = sum(1 for v in before.values() if v)
    n_after = sum(1 for v in after.values() if v)

    by_reason = rejected["reason"].value_counts().to_dict()

    # топ-100 / emerging по ЧИСТЫМ кандидатам (те же правила §3)
    top = clean.sort_values("growth", ascending=False)
    em = clean[(clean["first_year"].fillna(9999) >= 2018)
               & (clean["n_recent"] >= 5)].sort_values("growth", ascending=False)

    lines = ["# TermTech — топ терминов ПОСЛЕ отбраковки мусора (filter v0.1)",
             "",
             f"До фильтра: {len(cand)} кандидатов; после: {len(clean)} "
             f"(отсеяно {len(cand) - len(clean)}, {100 * (len(cand) - len(clean)) / max(len(cand), 1):.1f}%)",
             f"Recall eval: {n_before}/14 → {n_after}/14 (маркерный тест целостности)",
             "",
             "## Топ-100 по growth", "",
             "| # | term | df | first_year | growth | kPMI |",
             "|---|---|---|---|---|---|"]
    for i, r in enumerate(top.head(100).itertuples(), 1):
        k = "" if pd.isna(r.kpmi) else f"{r.kpmi:.2f}"
        fy = "-" if pd.isna(r.first_year) else int(r.first_year)
        lines.append(f"| {i} | {r.term} | {r.df} | {fy} | {r.growth:.2f} | {k} |")
    lines += ["", "## Топ-40 emerging (first_year≥2018, n_recent≥5)", "",
              "| # | term | df | first_year | growth |",
              "|---|---|---|---|---|"]
    for i, r in enumerate(em.head(40).itertuples(), 1):
        fy = "-" if pd.isna(r.first_year) else int(r.first_year)
        lines.append(f"| {i} | {r.term} | {r.df} | {fy} | {r.growth:.2f} |")
    (INDIR / "top_terms_clean.md").write_text("\n".join(lines) + "\n")

    report = {
        "n_before": int(len(cand)), "n_after": int(len(clean)),
        "rejected": int(len(cand) - len(clean)),
        "rejected_by_rule": {k: int(v) for k, v in by_reason.items()},
        "recall_before": f"{n_before}/14", "recall_after": f"{n_after}/14",
        "recall_detail": {k: v for k, v in after.items()},
        "rules": "R1 markup, R2 year, R3 boilerplate, R4 stub, R5 numeric, "
                 "R6 css, R7 affil, R8 filler, R9 artifact "
                 "(scripts/termtech_filter.py, не тюнинговались на QA/eval)",
    }
    (INDIR / "filter_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1))
    print(json.dumps(report, ensure_ascii=False, indent=1))
    print(f"Выход: top_terms_clean.md, candidates_clean.parquet, filter_report.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
