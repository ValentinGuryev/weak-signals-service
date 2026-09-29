#!/usr/bin/env python3
"""Семантический анализатор S2 v2: разделение «фундаментальное vs прикладное» по IBAD.

Реализация плана results/case_signals/PLAN_SEMANTIC_V2.md (2026-08-28).
Заменяет грубый regex-анализатор src/semantic_shift_ibad.py.

Что исправлено (по списку багов из плана):
1. word boundaries \\b + Porter-стемминг (nltk) — «tapered»≠«tape», «wireless»≠«wire»,
   «powerful/powered»≠«power», «systematic»≠«system».
2. Многословные паттерны (current density, temperature dependence) работают
   на исходном тексте, НЕ в word-цикле.
3. Сбалансированные словари (равное число корней, подбор по частотности).
4. Пер-документная агрегация (среднее по докладам, а не по словам) + дисперсия.
5. Бутстрап → доверительные интервалы для Δ по периодам.
6. Чистка текста: вырезаем шапку форума, footer, keywords, acknowledgements,
   список литературы (REFERENCES/References), DOI-блоки.
7. Контрольная группа: не-IBAD теги SNF (cables, fusion, mri, mgb2, cryogenics) —
   проверяем, что сдвиг специфичен для IBAD, а не глобальный.

Выход: печать в консоль + results/case_signals/semantic_v2_ibad.json
       + results/case_signals/semantic_v2_control.json
"""
from __future__ import annotations

import json
import random
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

try:
    from nltk.stem import PorterStemmer
    _STEM = PorterStemmer().stem
except Exception:
    _STEM = lambda w: w.lower()  # fallback без стемминга

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNF_DIRS = [
    PROJECT_ROOT / "data" / "raw" / "conferences" / "snf_ieeecsc" / "downloads_renamed",
    PROJECT_ROOT / "data" / "raw" / "conferences" / "snf_ieeecsc" / "downloads_renamed_v2",
]
TOPICS = PROJECT_ROOT / "results" / "snf_index" / "topics_map.json"

OUT_IBAD = PROJECT_ROOT / "results" / "case_signals" / "semantic_v2_ibad.json"
OUT_CTRL = PROJECT_ROOT / "results" / "case_signals" / "semantic_v2_control.json"

# ============ ЧИСТКА ТЕКСТА ============
# Шапка/футер форума: разные варианты ESNF/SNF
FORUM_HEADER = re.compile(
    r"(IEEE CSC\s*&\s*ESAS SUPERCONDUCTIVITY NEWS FORUM|IEEE/CSC\s*&\s*ESAS European Superconductivity News Forum|"
    r"European Superconductivity News Forum|SUPERCONDUCTIVITY NEWS FORUM|Superconductivity News Forum|"
    r"ESNF|IEEE CSC\s*&\s*ESAS).*?(?=\n\s*\n|Abstract|Introduction|\bABSTRACT\b|\bAbstract—\b)",
    re.S | re.I)
# Footer: «... Issue No. ... Presentation given at ...» / «17th Issue of ESNF»
FORUM_FOOTER = re.compile(
    r"(IEEE CSC\s*&\s*ESAS SUPERCONDUCTIVITY NEWS FORUM|European Superconductivity News Forum|"
    r"SUPERCONDUCTIVITY NEWS FORUM|\d+th Issue of .*?ESNF|ESNF.*?Presentation given at).*?(?:\n|$)",
    re.S | re.I)
# «Issue No. 53, July 2023» / «No. 6, October 2008» в любом месте
ISSUE_LINE = re.compile(r"(Issue No\. \d+[^\n]*|No\. \d+, [A-Z][a-z]+ \d{4}[^\n]*|\d+th Issue of[^\n]*)")
# «The published version ... appeared in IEEE TAS 19, No. 3...»
PUB_VERSION = re.compile(r"The published version of this manuscript[^\n]*")
# Keywords / Index Terms
KEYWORDS = re.compile(r"\bKeywords?\b[^\n]*|Index Terms[^\n]*", re.I)
# Лицензия ESNF (футер) — «promotional purposes, creating new collective works...»
LICENSE = re.compile(r"promotional purposes[^\n]*|creating new collective works[^\n]*|"
                     r"for resale or redistribution[^\n]*|republish[^\n]*")
# Обложки/титулы журналов: «19, No. 3, Part 2, 1055 - 1068 (2009)»
JOURNAL_FOOT = re.compile(r"\d{1,2}, No\. \d, Part \d, \d+ - \d+ \(\d{4}\)")
# IEEE TAS-обложки в SNF: «... No. 3, Part 2, ... (2009)» как заголовок страницы
TAS_HEADER = re.compile(r"IEEE Transactions on Applied Superconductivity[^\n]*|IEEE TRANSACTIONS ON APPLIED SUPERCONDUCTIVITY[^\n]*")
# «Power Hardware-in-the-Loop...», «Abstract—» остатки
ABSTRACT_MARK = re.compile(r"\bAbstract—?\b")
# Acknowledgements / A part of this work...
ACK = re.compile(r"\bAcknowledg(e)?ments?\b.*|A part of this work.*|This work (was )?(is )?(partially )?supported by.*|"
                 r"This work is based on results.*|subsidized by.*|funded by.*|supported by.*", re.I | re.S)
# References
REFS = re.compile(r"^\s*(References|REFERENCES)\s*$.*", re.M | re.S)
DOI = re.compile(r"\b(doi|dx\.doi\.org|https?://)\S*", re.I)
EMAIL = re.compile(r"\S+@\S+")
MULTISPACE = re.compile(r"\s+")

# Стоп-слова (частотные, не несут семантики инж/фунд)
STOP = set("""a an and the or of to in for on with by from as at is are was were be been being
it its this that these those i we you he she they them their our your my me us
not no nor but so if then than when where which who whom what how why
about into over under between through during before after above below
can could would should may might must shall will do does did done
also only just very more most much many some any each every both few
such same other another new old one two three four five first second
there here out up down off again once here there
""".split())


def clean_text(text: str) -> str:
    """Вырезать служебные блоки ESNF, оставить только научный текст."""
    t = text
    t = FORUM_HEADER.sub(" ", t)
    t = FORUM_FOOTER.sub(" ", t)
    t = ISSUE_LINE.sub(" ", t)
    t = PUB_VERSION.sub(" ", t)
    t = KEYWORDS.sub(" ", t)
    t = LICENSE.sub(" ", t)
    t = JOURNAL_FOOT.sub(" ", t)
    t = TAS_HEADER.sub(" ", t)
    t = ABSTRACT_MARK.sub(" ", t)
    t = ACK.sub(" ", t)
    t = REFS.sub(" ", t)
    t = DOI.sub(" ", t)
    t = EMAIL.sub(" ", t)
    t = MULTISPACE.sub(" ", t)
    return t


def split_paragraphs(text: str) -> list[str]:
    """Разбить на абзацы (по границам предложений), длина > 40 символов."""
    text = MULTISPACE.sub(" ", text)
    paras = [p.strip() for p in re.split(r"(?<=[.!?])\s+(?=[A-ZА-Я0-9])", text) if len(p.strip()) > 40]
    return paras


def tokens(text: str) -> list[str]:
    """Стеммированные токены (без стоп-слов)."""
    words = re.findall(r"[A-Za-z][A-Za-z\-']{2,}", text.lower())
    return [_STEM(w) for w in words if w not in STOP]


# ============ СЛОВАРИ (сбалансированные, word boundaries, стемминг) ============
# Прикладное / инжиниринг: производство, оптимизация, интеграция, коммерциализация.
# ВАЖНО: только УЗКИЕ производственные термины. Широкие (process, cost, optim, quality,
# control, line, system, power, rate, energy) убраны из одиночных корней — они ловят
# научный процесс/качество/стоимость в фундаментальных текстах. Производственный смысл
# дают ТОЛЬКО многословные паттерны (MULTI_ENG) и узкие корни ниже.
ENG_ROOTS = [
    "product", "manufactur", "fabricat", "industri", "commerci", "reel", "r2r",
    "throughput", "scale", "mass", "yield", "length", "continu", "autom",
    "inline", "online", "prototyp", "pilot", "equip",
]
# Фундаментальное / эффект-открытие: демонстрация, рекорд, новизна, механизм.
# Убраны: лабораторные метрики (sample, measured, tape, wire, film, layer, substrate,
# coil, voltage, resistance), «улучшение свойств» (enhance/improve/increase — это скорее
# оптимизация = прикладное), «critical current» (объект измерения, не маркер эффекта).
EFF_ROOTS = [
    "demonstr", "discover", "record", "breakthrough", "achiev", "possib",
    "potenti", "promis", "novel", "remark", "superior", "mechan", "theoret",
    "fundament", "basic", "insight", "understand", "phenomen", "surprising",
    "unexpect", "first", "new", "unique", "reveal", "elucid", "uncover",
]

# Строим regex по корням: \b(prod|manufac...)[a-z]*\b — с учётом стемминга.
def roots_regex(roots: list[str]) -> re.Pattern:
    # корни уже в стеммированной форме; паттерн: \b root [a-z']* \b
    return re.compile(r"\b(?:" + "|".join(re.escape(r) for r in roots) + r")[a-z']*\b", re.I)


ENG_RE = roots_regex(ENG_ROOTS)
EFF_RE = roots_regex(EFF_ROOTS)

# Точные стеммированные корни (наборы), сравниваем с токенами текста.
# Важно: корни стеммированы Porter'ом, поэтому "tapered"→"taper" НЕ совпадёт с "tape",
# "wireless"→"wireless" НЕ совпадёт с "wire", "systematic"→"systemat" НЕ совпадёт с "system".
ENG_STEMS = {_STEM(r) for r in ENG_ROOTS}
EFF_STEMS = {_STEM(r) for r in EFF_ROOTS}
# многословные паттерны (на исходном тексте, не токены)
# ВАЖНО: critical current — объект измерения, НЕ маркер эффекта; убран.
MULTI_EFF = re.compile(r"current density|flux pinning|transition temperature|"
                       r"vortex motion|first time|never before", re.I)
MULTI_ENG = re.compile(r"reel[- ]to[- ]reel|mass production|long length|scale[- ]?up|in-line|on-line|"
                       r"\bR2R\b|quality control|cost reduction|production line|production process|"
                       r"manufacturing process|industrial production|commercial production|process optimization|"
                       r"process control|production cost|manufacturing cost|pilot[- ]scale|mass[- ]produc|"
                       r"preparation process|fabrication process|long[- ]tape|long[- ]length|length fabrication|"
                       r"long[- ]tape fabrication|continuous preparation|long tape|"
                       r"buffer[- ]layer preparation|preparation of (buffer|template|IBAD)|production of long|"
                       r"template production|buffer preparation|production of (IBAD|MgO)|manufacturing of (tape|conductor)|"
                       r"deposition of (long|wide|meter|100|200|500|800|830)[^.]{0,30}(tape|conductor)|\d+[- ]?m (long|tape|length)|"
                       r"continuous processing|moving (metal )?tape|for (coated conductor|HTS|tape) fabrication|"
                       r"fabrication of (coated conductor|tape|HTS)|for (production|manufacturing) of (tape|conductor)|"
                       r"substrate preparation|industrial (production|scale|fabrication)|on (moving|metal) tape|"
                       r"commercial (tape|conductor|production)|for (commercial|industrial) use", re.I)
# Достижение/результат В ПРОИЗВОДСТВЕННОМ контексте (объект ленты/шаблона/буфера):
# «achieved uniform Jc on 830-m tape», «demonstrated on commercial tape» — прикладное достижение,
# а не фундаментальное открытие.
MULTI_ENG_ACHIEVE = re.compile(
    r"(achiev|demonstrat|obtain|produc)[^.]{0,80}(tape|coated conductor|IBAD|template|buffer|long length|\d+[ ]?m long)",
    re.I | re.S)
MULTI_ENG_ACHIEVE2 = re.compile(
    r"(tape|coated conductor|IBAD|template|buffer)[^.]{0,60}(achiev|demonstrat|produc|fabricat)[^.]{0,40}",
    re.I | re.S)


def classify_paragraph(p: str) -> str:
    """Классифицировать абзац: 'eng' | 'eff' | 'neu' (по стеммированным токенам).

    Правило перевеса: если и eng, и eff маркеры — сравниваем их количество.
    """
    toks = set(tokens(p))
    e_set = toks & ENG_STEMS
    f_set = toks & EFF_STEMS
    e = len(e_set) + (2 if MULTI_ENG.search(p) else 0)
    f = len(f_set) + (2 if MULTI_EFF.search(p) else 0)
    # Достижение в производственном контексте → перевешивает eff (прикладное достижение)
    if MULTI_ENG_ACHIEVE.search(p) or MULTI_ENG_ACHIEVE2.search(p):
        e += 2
    if e > f and e > 0:
        return "eng"
    if f > e and f > 0:
        return "eff"
    return "neu"


# Пороги дискриминации документа (эмпирические, настроены на золотом стандарте):
# - eng% > APPLIED_ENG_MIN → явно прикладной (плотный производственный контекст)
# - eff% > eng% × EFF_RATIO и eff% > EFF_MIN → явно фундаментальный (доминирует открытие/механизм)
# - иначе → mixed (слабый сигнал; для ранних статей 1991-1997 = фундаментальный контекст)
APPLIED_ENG_MIN = 15.0   # eng-абзацев ≥ 15% → applied
EFF_RATIO = 1.5          # eff > eng × 1.5 → fundamental
EFF_MIN = 5.0            # и eff ≥ 5%

# Коррекция mixed по заголовку/аннотации (первые 900 символов):
# авторы сами заявляют цель — производственную или научную.
PROD_HEAD = re.compile(
    r"production|manufactur|coated conductor|reel[\s-]?to[\s-]?reel|long (tape|length)|"
    r"commercial|pilot|industrial|fabrication|buffer layer for|optimiz|for (YBCO|HTS|2G|applications)|"
    r"large[- ]scale application|tape[- ]shaped", re.I)
FUND_HEAD = re.compile(
    r"mechanism|in-plane (textured|aligned)|biaxially aligned|nucleation|comparison with|"
    r"first (report|observation|demonstration)|reveal|elucidate|theory|model of|"
    r"deposited on polycrystalline|thin films deposited", re.I)


def classify_document(text: str) -> dict:
    """Дискриминация документа: 'applied' | 'fundamental' | 'mixed' + метрики.

    Используется для целых статей (а не абзацев). Возвращает подробный результат.
    Порядок: (1) по абзацам (eng%/eff%), (2) mixed → коррекция по заголовку/аннотации.

    АБСТРАКТ-РЕЖИМ: если текст короткий (<3000 символов — абстракт, не полный текст),
    применяем БОЛЕЕ СТРОГИЕ пороги и взвешивание: одиночный eng-корень (fabricat,
    manufactur, continu, length, scale, commerci) НЕ даёт applied без производственной
    фразы (MULTI_ENG) — на коротких текстах эти слова встречаются в лабораторном смысле
    («manufacturing method», «continuous film», «small scale»).
    """
    clean = clean_text(text)
    paras = split_paragraphs(clean)
    if not paras:
        return {"verdict": "no_text", "n": 0}
    is_abstract = len(clean) < 3000
    c = Counter(classify_paragraph(p) for p in paras)
    n = len(paras)
    eng_p = 100 * c["eng"] / n
    eff_p = 100 * c["eff"] / n
    if is_abstract:
        # Абстракт: нужен плотный производственный сигнал (multi-фразы), одиночные
        # eng-корни (fabricat/manufactur/continu/length/scale/commerci) — лабораторные.
        multi_hits = sum(1 for p in paras if MULTI_ENG.search(p))
        multi_p = 100 * multi_hits / n
        # applied только при сильном производственном сигнале: multi-фразы ≥ 20%
        # ИЛИ eng% ≥ 40% (очень плотный), И при этом eff не доминирует
        if multi_p >= 20 and eff_p < 30:
            verdict = "applied"
        elif eng_p >= 40 and eff_p < 30:
            verdict = "applied"
        elif eff_p > eng_p * EFF_RATIO and eff_p >= EFF_MIN:
            verdict = "fundamental"
        else:
            verdict = "mixed"
    else:
        # Полный текст: прежняя логика
        if eng_p >= APPLIED_ENG_MIN:
            verdict = "applied"
        elif eff_p > eng_p * EFF_RATIO and eff_p >= EFF_MIN:
            verdict = "fundamental"
        else:
            verdict = "mixed"
    # Коррекция mixed по заголовку/аннотации (только для полных текстов — у абстрактов
    # заголовок уже включён в первый абзац, двойной учёт исказит)
    if verdict == "mixed" and not is_abstract:
        head = clean[:900]
        prod = bool(PROD_HEAD.search(head))
        fund = bool(FUND_HEAD.search(head))
        if prod and not fund:
            verdict = "applied"
        elif fund and not prod:
            verdict = "fundamental"
    return {
        "verdict": verdict, "n": n, "is_abstract": is_abstract,
        "eng": c["eng"], "eff": c["eff"], "neu": c["neu"],
        "eng_p": eng_p, "eff_p": eff_p, "neu_p": 100 * c["neu"] / n,
    }


# ============ ИЗВЛЕЧЕНИЕ ============
def find_snf(name: str) -> Path | None:
    for d in SNF_DIRS:
        p = d / name
        if p.exists():
            return p
    return None


def extract_text(pdf: Path) -> str:
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
        out = tf.name
    try:
        subprocess.run(["pdftotext", str(pdf), out], check=True, timeout=60,
                       capture_output=True)
        return open(out, encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""
    finally:
        Path(out).unlink(missing_ok=True)


# ============ АНАЛИЗ ============
def analyze_doc(text: str) -> dict | None:
    """Один доклад → (n_eng, n_eff, n_neu, appl_per_1000, lab_per_1000)."""
    clean = clean_text(text)
    if len(clean) < 300:
        return None
    paras = split_paragraphs(clean)
    if not paras:
        return None
    cnt = Counter(classify_paragraph(p) for p in paras)
    toks = tokens(clean)
    n = len(toks)
    appl = sum(1 for t in toks if t in ENG_STEMS)
    lab = sum(1 for t in toks if t in EFF_STEMS)
    return {
        "n_paras": len(paras),
        "eng": cnt["eng"], "eff": cnt["eff"], "neu": cnt["neu"],
        "words": n,
        "appl": appl, "lab": lab,
        "appl_per_1000": 1000 * appl / n if n else 0,
        "lab_per_1000": 1000 * lab / n if n else 0,
    }


def year_from_name(name: str) -> int | None:
    m = re.match(r"\((\d{4})\)", name)
    return int(m.group(1)) if m else None


PERIODS = {"2008-2010": (2008, 2010), "2011-2013": (2011, 2013),
           "2014-2016": (2014, 2016), "2017-2019": (2017, 2019),
           "2020-2022": (2020, 2022), "2023-2025": (2023, 2025)}


def period_of(year: int) -> str | None:
    for p, (a, b) in PERIODS.items():
        if a <= year <= b:
            return p
    return None


def analyze_tag(tag: str, files: list[str]) -> dict:
    """Анализ всех докладов тега по периодам (пер-документная агрегация + бутстрап).

    v2.2: каждый документ получает бинарный вердикт (applied/fundamental/mixed)
    через classify_document (с коррекцией по заголовку). Агрегируем долю прикладных
    и фундаментальных по периодам + eng%/eff% + Δappl−lab‰.
    """
    docs_by_period: dict[str, list[dict]] = {p: [] for p in PERIODS}
    failed = 0
    for name in files:
        year = year_from_name(name)
        if not year:
            continue
        p = period_of(year)
        if not p:
            continue
        pdf = find_snf(name)
        if not pdf:
            failed += 1
            continue
        txt = extract_text(pdf)
        r = analyze_doc(txt)
        if not r:
            failed += 1
            continue
        # бинарный вердикт документа (улучшенный дискриминатор)
        v = classify_document(txt)
        r["verdict"] = v["verdict"]
        docs_by_period[p].append(r)

    # Пер-документная агрегация + бутстрап (1000 итераций, 95% ДИ)
    out = {}
    for p in PERIODS:
        docs = docs_by_period[p]
        if not docs:
            out[p] = {"n": 0}
            continue
        eng_share = [d["eng"] / d["n_paras"] for d in docs]
        eff_share = [d["eff"] / d["n_paras"] for d in docs]
        appl_per = [d["appl_per_1000"] for d in docs]
        lab_per = [d["lab_per_1000"] for d in docs]

        def boot(xs):
            vals = []
            for _ in range(1000):
                sample = [random.choice(xs) for _ in xs]
                vals.append(sum(sample) / len(sample))
            vals.sort()
            return vals[25], vals[975]

        delta = [a - l for a, l in zip(appl_per, lab_per)]
        delta_ci = boot(delta)
        eng_ci = boot(eng_share)
        eff_ci = boot(eff_share)
        # доля прикладных/фундаментальных документов (бинарный вердикт)
        n_appl = sum(1 for d in docs if d["verdict"] == "applied")
        n_fund = sum(1 for d in docs if d["verdict"] == "fundamental")
        n_mix = sum(1 for d in docs if d["verdict"] == "mixed")
        out[p] = {
            "n": len(docs),
            "n_appl": n_appl, "n_fund": n_fund, "n_mix": n_mix,
            "appl_share": n_appl / len(docs),
            "fund_share": n_fund / len(docs),
            "eng_share_mean": sum(eng_share) / len(eng_share),
            "eng_share_ci": eng_ci,
            "eff_share_mean": sum(eff_share) / len(eff_share),
            "eff_share_ci": eff_ci,
            "appl_per_1000_mean": sum(appl_per) / len(appl_per),
            "lab_per_1000_mean": sum(lab_per) / len(lab_per),
            "delta_mean": sum(delta) / len(delta),
            "delta_ci": delta_ci,
            "words_total": sum(d["words"] for d in docs),
        }
    out["_meta"] = {"failed_extract": failed, "tag": tag, "total_docs": len(files)}
    return out


def print_report(tag: str, res: dict) -> None:
    print(f"\n=== SNF v2: семантический сдвиг по тегу '{tag}' (пер-документно, бутстрап 95% ДИ) ===")
    print(f"{'период':<10} {'докл':>4} {'прикл%':>7} {'фунд%':>7} {'смеш%':>6} {'инж%':>7} {'эфф%':>7} {'Δ‰':>6}")
    for p in PERIODS:
        d = res[p]
        if not d.get("n"):
            print(f"{p:<10} {'—':>4}")
            continue
        eng = 100 * d["eng_share_mean"]
        eff = 100 * d["eff_share_mean"]
        dm = d["delta_mean"]
        print(f"{p:<10} {d['n']:>4} {100*d['appl_share']:>6.1f}% {100*d['fund_share']:>6.1f}% {100*d['n_mix']/d['n']:>5.1f}% "
              f"{eng:>6.1f}% {eff:>6.1f}% {dm:>+5.1f}")
    print(f"(не извлечено: {res['_meta']['failed_extract']} / всего {res['_meta']['total_docs']})")


def main() -> None:
    random.seed(42)
    with open(TOPICS) as f:
        tm = json.load(f)

    ibad = tm.get("ibad_tapes", [])
    print(f"Докладов в теге ibad_tapes: {len(ibad)}")
    res_ibad = analyze_tag("ibad_tapes", ibad)
    print_report("ibad_tapes", res_ibad)
    OUT_IBAD.parent.mkdir(parents=True, exist_ok=True)
    OUT_IBAD.write_text(json.dumps(res_ibad, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT_IBAD}")

    # Контрольные группы (не-IBAD теги) — проверить специфичность сдвига
    ctrl_tags = ["cables", "fusion", "mri", "mgb2", "cryogenics"]
    ctrl = {}
    for tag in ctrl_tags:
        files = tm.get(tag, [])
        if not files:
            continue
        print(f"\n--- Контрольная группа: {tag} ({len(files)} докладов) ---")
        res = analyze_tag(tag, files)
        ctrl[tag] = res
        print_report(tag, res)
    OUT_CTRL.parent.mkdir(parents=True, exist_ok=True)
    OUT_CTRL.write_text(json.dumps(ctrl, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT_CTRL}")


if __name__ == "__main__":
    main()
