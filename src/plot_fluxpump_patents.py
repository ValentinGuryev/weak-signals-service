#!/usr/bin/env python3
"""График: патенты flux pump по годам (Lens) + панель игроков.

Данные: data/raw/patents/topics/flux_pump_lens_clean.json (85 патентов, 61 в окне)
Показывает:
  - Верх: патенты по годам 2006-2026
  - Низ: топ-игроки + КЛЮЧЕВОЙ сигнал (гиганты = 0)
Выход: case_studies/003_flux_pump_space/plots/plot10_fluxpump_patents.png
"""
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw" / "patents" / "topics" / "flux_pump_lens_clean.json"
OUT = ROOT / "case_studies" / "003_flux_pump_space" / "plots" / "plot10_fluxpump_patents.png"

d = json.loads(SRC.read_text(encoding="utf-8"))
pats = d["patents"]
in_win = [p for p in pats if p.get("priority_date", "")[:4].isdigit()
          and 2006 <= int(p["priority_date"][:4]) <= 2026]

# Нормализация заявителей
def norm(a):
    a = a.upper()
    for key, name in [
        ("SICHUAN", "Sichuan Univ"), ("NORTH CHINA", "N China Elec Power"),
        ("VICTORIA", "Victoria Link (NZ)"), ("SIEMENS", "Siemens"),
        ("HUNAN", "Hunan Univ"), ("NORTHEASTERN", "Northeastern Univ"),
        ("FUTONG", "Futong Group"), ("HTS 110", "HTS 110 (NZ)"),
        ("HOFFMANN", "Hoffmann"), ("POOKE", "Pooke"), ("COOMBS", "Coombs"),
        ("KOREA ADVANCED", "KAIST"), ("CHANGWON", "Changwon"), ("KOREA BASIC", "KBSI"),
        ("JEJU", "Jeju"), ("SHANGHAI", "Shanghai Jiao Tong"),
        ("GRID LOGIC", "Grid Logic (US)"), ("EMERSON", "Emerson"),
        ("HOLCOMB", "Grid Logic (US)"), ("YUNNAN", "Yunnan Gexun"),
        ("WUHAN", "Wuhan Inst"), ("TEXAS", "UT Dallas"), ("KALS", "Kalsi"),
    ]:
        if key in a:
            return name
    return a.split(",")[0][:25] if a else "(нет)"

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), gridspec_kw={"height_ratios": [2, 1]})

# === Верх: патенты по годам ===
years = list(range(2006, 2027))
cnt = Counter(p["priority_date"][:4] for p in in_win)
vals = [cnt.get(str(y), 0) for y in years]
ax1.bar(years, vals, color="#1f77b4", alpha=0.85)

ax1.annotate(f"Пик 2021 ({cnt.get('2021',0)})\nвзрыв CN (Sichuan)",
             xy=(2021, cnt.get('2021',0)), xytext=(2012, 15),
             arrowprops=dict(arrowstyle="->", color="#1f77b4"), fontsize=9)
ax1.annotate(f"Вторая волна 2022 ({cnt.get('2022',0)})",
             xy=(2022, cnt.get('2022',0)), xytext=(2015, 10),
             arrowprops=dict(arrowstyle="->", color="#1f77b4"), fontsize=9)

ax1.set_xlabel("Год (priority date)")
ax1.set_ylabel("Число патентов flux pump")
ax1.set_title("Патенты flux pump по годам (2006-2026) — кейс 003")
ax1.set_xticks(range(2006, 2027, 1))
ax1.tick_params(axis='x', rotation=45)
ax1.grid(axis="y", alpha=0.3)

# === Низ: игроки (топ 8 + гиганты = 0) ===
players = Counter(norm(p["assignee"]) for p in in_win)
top = players.most_common(8)
names = [n for n, _ in top][::-1]
counts = [c for _, c in top][::-1]
colors = ["#d62728" if "Univ" in n or "Power" in n else "#1f77b4" for n in names]
ax2.barh(names, counts, color=colors, alpha=0.85)
ax2.set_xlabel("Число патентов (окно 2006-2026)")
ax2.set_title("Топ-игроки flux pump (красный = китайские университеты)")

# Ключевой сигнал: гиганты = 0
ax2.text(0.98, -0.12,
         "КЛЮЧЕВОЕ: Fujikura/Sumitomo/Toshiba/GA/AMSC/Hitachi = 0 патентов!\n"
         "Даже Coombs/Geng (пионеры науки) = 0. Flux pump — академическая/китайская тема.",
         transform=ax2.transAxes, ha="right", fontsize=9, color="#d62728",
         bbox=dict(boxstyle="round", facecolor="white", edgecolor="#d62728"))

fig.text(0.01, 0.01, f"Lens.org, {len(in_win)} патентов в окне (из {len(pats)}). "
         f"Гео: CN {sum(1 for p in in_win if p['publication_number'].startswith('CN'))}, "
         f"WO {sum(1 for p in in_win if p['publication_number'].startswith('WO'))}, "
         f"US {sum(1 for p in in_win if p['publication_number'].startswith('US'))}, "
         f"KR {sum(1 for p in in_win if p['publication_number'].startswith('KR'))}. 2026-08-31.",
         fontsize=8, style="italic", color="gray")

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT} (окно: {len(in_win)} патентов)")
