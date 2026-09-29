#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011 SRF: график первичного корпуса (S1a) — динамика публикаций.

Вход: data/raw/openalex/srf_corpus.json (7579 работ, 1962-2026)
Выход: case_studies/011_srf_cavities/plots/pubs_by_year.png
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/raw/openalex/srf_corpus.json"
OUT = ROOT / "case_studies/011_srf_cavities/plots/pubs_by_year.png"

d = json.loads(DATA.read_text(encoding="utf-8"))
ws = [w for w in d["works"] if w.get("year")]
yc = Counter(w["year"] for w in ws)
years = range(min(yc), max(yc) + 1)
counts = [yc.get(y, 0) for y in years]

# 3-летнее сглаживание (урок: «эхо» датировки arXiv → кварталы/сглаживание)
smooth = []
for i, y in enumerate(years):
    lo = max(0, i - 1)
    hi = min(len(years), i + 2)
    smooth.append(sum(counts[lo:hi]) / (hi - lo))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Панель A: по годам
ax1.bar([y for y in years], counts, color="#1f77b4", alpha=0.85)
ax1.axvline(2018, color="red", ls="--", lw=1.2)
ax1.text(2018.2, max(counts) * 0.93, "окно 2018", color="red", fontsize=9, rotation=90, va="top")
for y, lbl, dy in [(2013, "ILC TDR", 0.75), (2016, "LCLS-II стройка", 0.5), (2023, "LCLS-II запуск", 0.65)]:
    ax1.annotate(lbl, xy=(y, yc.get(y, 0)), xytext=(y - 2, yc.get(y, 0) + max(counts) * dy / 8),
                 fontsize=8, color="darkgreen")
ax1.set_title(f"Публикации по годам ({len(ws)} работ, OpenAlex)\nпик 2015-19 = строительство LCLS-II/ESS", fontsize=11)
ax1.set_xlabel("год"); ax1.set_ylabel("работ"); ax1.grid(alpha=0.3)

# Панель B: сглаженный тренд + ключевые вехи
ax2.plot(years, smooth, color="#2ca02c", lw=2, label="3-летнее сглаживание")
ax2.fill_between(years, smooth, alpha=0.15, color="#2ca02c")
for y, lbl in [(2013, "ILC TDR"), (2016, "LCLS-II/ESS\nстройка"), (2023, "LCLS-II\nзапуск")]:
    ax2.axvline(y, color="gray", ls=":", lw=1)
    ax2.text(y, max(smooth) * 0.95, lbl, fontsize=8, ha="center", color="gray")
ax2.set_title("Сглаженный тренд: подъём до 2015-19, плато/спад после запуска", fontsize=11)
ax2.set_xlabel("год"); ax2.set_ylabel("работ/год (сглаж.)"); ax2.grid(alpha=0.3)

fig.suptitle("S1a — Корпус SRF-резонаторов (кейс 011): сверхпроводящие ВЧ-полости", fontsize=13)
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("saved:", OUT)