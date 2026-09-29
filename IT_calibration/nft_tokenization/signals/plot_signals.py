#!/usr/bin/env python
"""Визуализация сигналов кейса NFT/токенизация (4 слоя).

Запуск:  .venv/bin/python IT_calibration/nft_tokenization/signals/plot_signals.py
Вход:   raw/*.json (HN, GitHub, OpenAlex)
Выход:  plots/*.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

S = Path(__file__).resolve().parent
P = S / "plots"
R = S / "raw"
P.mkdir(exist_ok=True)

plt.rcParams.update({"figure.facecolor": "white", "axes.grid": True, "grid.alpha": 0.3,
                     "axes.axisbelow": True, "font.size": 10})


def load(name):
    return json.loads((R / name).read_text(encoding="utf-8"))


def num_series(d: dict, start=2016, end=2026):
    ys, vs = [], []
    for y in range(start, end + 1):
        v = d.get(str(y))
        if v is not None and not isinstance(v, str):
            ys.append(y); vs.append(v)
    return ys, vs


# ---------- 1. Attention (HN) ----------
hn = load("hn_attention_nft.json")
yrs, nft = num_series(hn["nft_exact_word"]["per_year"], 2017)
_, phr = num_series(hn["nft_phrase"]["per_year"], 2017)
fig, ax = plt.subplots(figsize=(9.5, 4.6))
ax.bar(yrs, nft, color="#9e3d22", alpha=0.9, label='word "nft" in title (stories/yr)')
ax.set_yscale("log")
ax.set_ylabel("stories per year (log)")
ax.set_xlabel("year")
ax.set_title("NFT — Attention layer (Hacker News, exact word in titles)\n"
             "peak 2021–22  →  −97% by 2025: V-shaped hype collapse")
ax.annotate("peak 717/713\n(2021–22)", xy=(2021.5, 713), xytext=(2019.4, 60),
            arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=8.5)
ax.annotate("−84% → 113\n(2023)", xy=(2023, 113), xytext=(2023.9, 25),
            arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=8.5)
ax.annotate("−97% → 18\n(2025); 11 (2026)", xy=(2025, 18), xytext=(2017.4, 260),
            arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=8.5)
ax2 = ax.twinx()
ax2.plot(yrs, phr, "o--", color="#2c6fb1", ms=3, lw=1,
         label='"non-fungible token" (formal term, titles)')
ax2.set_yscale("log"); ax2.set_ylabel("phrase hits / yr (log)")
ax.legend(loc="upper left", fontsize=8); ax2.legend(loc="upper right", fontsize=8)
fig.tight_layout(); fig.savefig(P / "hn_attention_nft.png", dpi=150); plt.close(fig)

# ---------- 2. Engineering (GitHub) ----------
gh = load("github_engineering_nft.json")
fig, ax = plt.subplots(figsize=(9.5, 4.6))
colors = {"erc721": "#762a83", "non_fungible_phrase": "#1b7837", "nft_marketplace": "#b2182b"}
labels = {"erc721": "erc721 (standard impl.)",
          "non_fungible_phrase": '"non-fungible token" (phrase)',
          "nft_marketplace": 'nft marketplace (apps)'}
for k, c in colors.items():
    yrs, vs = num_series(gh[k]["per_year_created"])
    ax.plot(yrs, vs, "o-", color=c, ms=4, lw=1.6, label=labels[k])
ax.set_yscale("log"); ax.set_xlabel("repo creation year"); ax.set_ylabel("repos created / yr (log)")
ax.set_title("NFT — Engineering layer (GitHub repos created per year)\n"
             "burst 2021–22 → decline, but code persists (no collapse)")
ax.annotate("burst ×390\n(2020→2022)", xy=(2022, 6188), xytext=(2016.6, 220),
            arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=8.5)
ax.annotate("residual floor:\nOpenSea seaport, Solana,\nutility-NFT", xy=(2024.5, 2679),
            xytext=(2018.2, 2600), arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=8.5)
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(P / "github_engineering_nft.png", dpi=150); plt.close(fig)

# ---------- 3. Science (OpenAlex) ----------
oa = load("openalex_nft_title_abstract.json")
oa_full = load("openalex_non_fungible_token_full.json")
fig, ax = plt.subplots(figsize=(9.5, 4.6))
yrs, vs = num_series(oa["per_year"], 2017)
ax.plot(yrs, vs, "o-", color="#762a83", ms=4, lw=1.6,
        label='title+abstract  "non-fungible token"  (canonical)')
yrs2, vs2 = num_series(oa_full["group_by_year"], 2016)
ax.plot(yrs2, vs2, "s--", color="#35978f", ms=3, lw=1.2,
        label='fulltext  "non-fungible token"  (control)')
ax.set_yscale("log"); ax.set_xlabel("publication year"); ax.set_ylabel("works / yr (log)")
ax.set_title("NFT — Science layer (OpenAlex)\n"
             "peak 2023 → plateau 2024–25 → mild decline 2026: science ECHO (not collapse)")
ax.annotate("peak 1089 (2023)\nplateau 1028/941", xy=(2023, 1089), xytext=(2017.3, 15),
            arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=8.5)
ax.annotate("market collapsed in 2022,\nscience kept plateau — echo signal", xy=(2024.5, 1028),
            xytext=(2018.6, 700), arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=8.5)
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(P / "openalex_science_nft.png", dpi=150); plt.close(fig)

# ---------- 4. Market timeline ----------
events = [
    ("2021-03", "OpenSea $23M\n(a16z)"),
    ("2021-07", "OpenSea\nvaluation $1.5B"),
    ("2022-01", "OpenSea $13.3B\n(Series C $300M)"),
    ("2022-05", "daily volume peak\n$2.7B (May 1)"),
    ("2022-05", "WSJ: market\n\"collapsing\" −92% sales"),
    ("2022-08", "volume −99%\n→ $9.34M/day"),
    ("2022-07", "OpenSea\nlayoffs 20%"),
    ("2023-09", "95% of NFTs\n= $0 value"),
    ("2024-08", "SEC Wells notice\n(tokens = securities)"),
    ("2025-02", "SEC closes case"),
    ("2025-10", "OpenSea pivots\n→ OS2 crypto aggregator"),
]
em, sel, top = [], [], []
for (m, lab) in events:
    em.append(m); sel.append(lab.split("\n")[0]); top.append(lab)
fig, ax = plt.subplots(figsize=(11.5, 5.2))
ax.set_xlim(0, 1); ax.set_ylim(0, len(events))
ax.axis("off")
ax.set_title("NFT — Market layer: timeline of hype and collapse (sources: WSJ/TechCrunch/Forbes/dappGambl, via Wikipedia)",
             fontsize=11, pad=18)
for i, (m, lab) in enumerate(events):
    y = len(events) - 1 - i
    ax.annotate(m, xy=(0.0, y), xytext=(0.005, y), fontsize=9, color="#555555", va="center")
    ax.annotate(lab, xy=(0.14, y), xytext=(0.145, y), fontsize=9.5, va="center",
                color="#b2182b" if ("%" in lab or "$0" in lab or "collaps" in lab) else "#222222")
ax.axvspan(0, 1, alpha=0.03, color="red")
fig.tight_layout(); fig.savefig(P / "nft_market_timeline.png", dpi=150); plt.close(fig)

# ---------- 5. Combined dashboard (3 panels + market inset) ----------
fig, axes = plt.subplots(1, 4, figsize=(21, 4.8))
# A. attention
yrs, nft = num_series(hn["nft_exact_word"]["per_year"], 2017)
axes[0].bar(yrs, nft, color="#b2182b", alpha=0.9)
axes[0].set_yscale("log"); axes[0].set_title("1. Attention (HN)\nstories/yr, exact word")
axes[0].set_xlabel("year"); axes[0].set_ylabel("count (log)")
# B. market snapshot
axm = axes[1]
axm.set_yscale("log")
axm.bar([2022], [2.7e3], color="#b2182b", width=0.45, label="peak $2.7B/day (05.2022)")
axm.bar([2022], [9.34], color="#f4a582", width=0.45, label="$9.34M/day (08.2022)")
axm.set_xticks([]); axm.set_ylim(1, 1e5)
axm.set_ylabel("daily volume, $M (log)")
axm.set_title("2. Market (OpenSea)\n−99% in 4 months")
axm.annotate("WSJ \"collapsing\"\n−92% sales", xy=(0.02, 0.96), xycoords="axes fraction",
             fontsize=7.5, ha="left", va="top")
axm.legend(fontsize=6.5, loc="lower center")
# C. engineering
yrs, mk = num_series(gh["nft_marketplace"]["per_year_created"])
axes[2].bar(yrs, mk, color="#1b7837", alpha=0.9)
axes[2].set_yscale("log"); axes[2].set_title("3. Engineering (GitHub)\nnft-marketplace repos created")
axes[2].set_xlabel("year")
# D. science
yrs, sc = num_series(oa["per_year"], 2017)
axes[3].bar(yrs, sc, color="#762a83", alpha=0.9)
axes[3].set_yscale("log"); axes[3].set_title("4. Science (OpenAlex)\ntitle+abstract, phrase")
axes[3].set_xlabel("year")
fig.suptitle("NFT / tokenization — four layers, one failed trend (window 2023 → 2026)\n"
             "market + attention collapsed; science plateaued (echo); engineering declined but persisted",
             fontsize=12, y=0.99)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(P / "nft_three_layers_combined.png", dpi=160)
print("saved:", "\n".join(str(p) + "  (" + str(round(p.stat().st_size / 1024)) + " KB)" for p in sorted(P.glob("*.png"))))