#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011: wordshift-семантика Nb3Sn-SRF подмножества по периодам (S2).

Метод — как в кейсе 007 (wordshift_jtwpa.py): частота маркера на 1000 слов абстрактов
по периодам. Периоды: <=2012 | 2013-15 | 2016-18 | 2019-21 | 2022-26 (окно 2018 — центр).

Данные: data/raw/openalex/srf_nb3sn_subset.json (327 работ, title+абстракт, из SRF-корпуса)
        + контроль Nb bulk (1229 работ с niobium в title, без Nb3Sn) из srf_corpus.json.
Выход: печать таблиц; JSON-тренды и график пишутся в case_studies/011_srf_cavities/.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent

PERIODS = [("<=2012", 0, 2012), ("2013-15", 2013, 2015), ("2016-18", 2016, 2018),
           ("2019-21", 2019, 2021), ("2022-26", 2022, 2026)]

MARKERS = {
    # терминология техн.
    "term_nb3sn": r"\bNb\s*3\s*Sn\b",
    "term_niot": r"niobium[\s-]tin\b|niobium stannide",
    # материал / процесс
    "mat_tin": r"\btin\b",
    "mat_coat": r"coat(ed|ing)?\b",
    "mat_film": r"\bfilms?\b",
    "mat_layer": r"\blayers?\b",
    "mat_vdp": r"vapo(u)?r diffusion",
    # физика предела Nb
    "phys_superheat": r"superheat(ing)?",
    "phys_hc1": r"lower critical field|\bHc1\b|Hc\s*1",
    "phys_rs": r"surface resistance|residual resistance",
    "phys_q0": r"quality factor|\bQ0\b|\bQ\s*0\b",
    "phys_grad": r"gradient",
    "phys_flux": r"flux expulsion",
    "phys_emit": r"multipacto?r|field emission",
    "phys_bcs": r"\bBCS\b",
    # крио-экономика
    "cryo_42": r"4[.,]\s*2\s*K\b",
    "cryo_2k": r"2[.,]\s*0?\s*K\b|2 K\b",
    "cryo_plant": r"cryoplan?t|cryogenic (plant|system)",
    "cryo_eff": r"cryogenic efficien|\bCOP\b",
    "cryo_cool": r"cryocooler",
    # применения / драйверы
    "app_xfel": r"\bXFEL\b|European X-ray",
    "app_ilc": r"\bILC\b|International Linear Collider",
    "app_fcc": r"\bFCC\b",
    "app_collider": r"collider",
    "app_compact": r"compact",
    "app_med": r"medical|radiotherapy|isotope",
    "app_cryomod": r"cryomodule",
    "app_linac": r"linac",
    # альтернативы не-СП
    "alt_nc": r"normal-conducting|normal conducting|\bcopper\b",
    "alt_clic": r"\bCLIC\b",
    "alt_plasma": r"plasma wakefield|plasma acceleration",
    "alt_ws": r"wakefield",
    "alt_thz": r"\bTHz\b",
    "alt_diel": r"dielectric laser|dielectric wakefield",
    # институции-сообщество
    "inst_cornell": r"Cornell",
    "inst_jlab": r"Jefferson|JLab",
    "inst_cern": r"\bCERN\b",
    "inst_fermi": r"Fermilab|Fermi National|FNAL",
    "inst_keksrf": r"\bKEK\b|High Energy Accelerator Research",
}


def load():
    cr = json.loads((ROOT / "data/raw/openalex/srf_corpus.json").read_text(encoding="utf-8"))
    allw = [w for w in cr["works"] if w.get("year")]
    pat3 = re.compile(r"nb\s*3\s*sn|niobium[\s-]?tin|niob[\s-]?tin|\bb3sn\b", re.I)
    patnb = re.compile(r"\bniobium\b|\bNb\b", re.I)
    nb3sn = []
    nb_ctrl = []
    for w in allw:
        txt = (w.get("title") or "") + " " + (w.get("abstract") or "")
        ttl = (w.get("title") or "")
        if pat3.search(ttl):
            nb3sn.append(w)
        elif patnb.search(ttl) and not pat3.search(ttl):
            nb_ctrl.append(w)
    return nb3sn, nb_ctrl


def freq_by_period(works):
    """маркер -> период -> (слов, вхождений)"""
    total_words = Counter()
    hits = {m: Counter() for m in MARKERS}
    for w in works:
        y = w.get("year")
        if not y:
            continue
        per = next(p for p, a, b in PERIODS if a <= y <= b)
        ab = w.get("abstract") or ""
        if not ab:
            continue
        total_words[per] += len(ab.split())
        lab = ab.lower()
        for m, pat in MARKERS.items():
            hits[m][per] += len(re.findall(pat, lab))
    return total_words, hits


def main():
    nb3sn, nb_ctrl = load()
    print(f"Nb3Sn подмножество: {len(nb3sn)} работ; контроль Nb: {len(nb_ctrl)}")
    for name, ws in (("Nb3Sn", nb3sn), ("Nb-control", nb_ctrl)):
        tw, hits = freq_by_period(ws)
        print(f"\n===== {name}: частота на 1000 слов по периодам =====")
        hdr = "маркер".ljust(14) + "".join(p.ljust(11) for p, _, _ in PERIODS)
        print(hdr)
        for m in MARKERS:
            vals = []
            for per, a, b in PERIODS:
                tot = tw.get(per, 0)
                h = hits[m].get(per, 0)
                vals.append(1000.0 * h / tot if tot else 0.0)
            if max(vals) < 0.05:  # редкие — не печатать
                continue
            row = m.ljust(14) + "".join(f"{v:11.2f}" for v in vals)
            print(row)
    # сохранить тренды JSON (Nb3Sn)
    tw, hits = freq_by_period(nb3sn)
    out = {"periods": [p for p, _, _ in PERIODS],
           "markers": {m: {p: (1000.0 * hits[m].get(p, 0) / tw.get(p, 1))
                           for p, _, _ in PERIODS} for m in MARKERS}}
    op = ROOT / "results/case_signals/wordshift_trends_nb3sn_srf.json"
    op.parent.mkdir(parents=True, exist_ok=True)
    op.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nsaved:", op)


if __name__ == "__main__":
    main()