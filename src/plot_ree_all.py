#!/usr/bin/env python3
"""Графики динамики цен оксидов РЗЭ (2014-2026) в USD.

- Перевод CNY→USD по среднегодовым курсам (разные годы — разный курс).
- Усреднение точек за один год (медиана) → одна точка на год.
- Убраны элементы без динамики (Yb, Lu — только одна точка 2026).
- Оси Y от нуля; панели tonne-графика в общем масштабе (×10⁶ USD/т).
- Графики не выходят за 2026 год.
- Сводный график: Gd, Y, Eu в USD/кг (сопоставимые масштабы).

Источники: снапшоты SMM (Wayback 2014-2021) + текущий срез 2026-08-19.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json, csv
from pathlib import Path
from collections import defaultdict

ROOT = Path("/home/user/projects/Hackathon")
OUT_DIR = ROOT / "results" / "market"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SRC = ROOT / "data" / "raw" / "market" / "ree_prices" / "smm_ree_all.json"

# Среднегодовые курсы CNY/USD (юаней за 1 доллар)
RATES = {2014: 6.14, 2015: 6.23, 2016: 6.64, 2017: 6.76, 2018: 6.62,
         2019: 6.91, 2020: 6.90, 2021: 6.45, 2022: 6.73, 2023: 7.08,
         2024: 7.24, 2025: 7.19, 2026: 7.10}

UNIT_BY_EL = {
    'La': 'yuan/tonne', 'Ce': 'yuan/tonne', 'Pr': 'yuan/tonne', 'Nd': 'yuan/tonne',
    'Sm': 'yuan/tonne', 'Gd': 'yuan/tonne', 'Er': 'yuan/tonne', 'Y': 'yuan/tonne',
    'Ho': 'yuan/tonne', 'Yb': 'yuan/tonne',
    'Eu': 'yuan/kg', 'Tb': 'yuan/kg', 'Dy': 'yuan/kg', 'Lu': 'yuan/kg',
}
FORMULA = {'La':'La2O3','Ce':'CeO2','Pr':'Pr6O11','Nd':'Nd2O3','Sm':'Sm2O3','Eu':'Eu2O3',
           'Gd':'Gd2O3','Tb':'Tb4O7','Dy':'Dy2O3','Ho':'Ho2O3','Er':'Er2O3','Y':'Y2O3',
           'Yb':'Yb2O3','Lu':'Lu2O3'}

d = json.loads(SRC.read_text(encoding="utf-8"))
snapshots = d["snapshots"]

# Содержательные снапшоты (2014-2021, 2024c); только обычный сорт (grade='std')
GOOD = {l for l, s in snapshots.items() if s["year"] in (2014, 2015, 2016, 2019, 2020, 2021, 2024)}

# Собрать (элемент, год) -> список цен CNY (только spot, grade='std')
agg = defaultdict(list)
for label in sorted(GOOD):
    year = snapshots[label]["year"]
    for it in snapshots[label]["items"]:
        if it["type"] == "spot" and it.get("grade", "std") == "std":
            agg[(it["element"], year)].append(it["price_avg"])

def to_usd(cny: float, unit: str, year: int) -> float:
    """CNY → USD по курсу года. yuan/tonne → USD/tonne; yuan/kg → USD/kg."""
    rate = RATES.get(year, 7.0)
    return cny / rate

# Итоговые серии: элемент -> [(год, цена_usd, unit)]
series = {}
for (el, year), prices in agg.items():
    med = sorted(prices)[len(prices)//2]
    unit = UNIT_BY_EL[el]
    series.setdefault(el, []).append((year, to_usd(med, unit, year), unit))

for el in series:
    series[el].sort(key=lambda x: x[0])

# Сохранить USD-данные в CSV
ORDER = ['La','Ce','Pr','Nd','Sm','Eu','Gd','Tb','Dy','Ho','Er','Y','Yb','Lu']
usd_csv = ROOT / "data" / "raw" / "market" / "ree_prices" / "smm_ree_yearly_usd.csv"
YEARS_CSV = [2014, 2015, 2016, 2019, 2020, 2021, 2024]
with open(usd_csv, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['element', 'formula', 'unit_usd'] + [f'y{y}' for y in YEARS_CSV])
    for el in ORDER:
        if el not in series:
            continue
        unit = series[el][0][2]
        row = [el, FORMULA[el], 'USD/kg' if unit == 'yuan/kg' else 'USD/tonne']
        for y in YEARS_CSV:
            vals = [p for yr, p, u in series[el] if int(yr) == y]
            row.append(round(sorted(vals)[len(vals)//2], 2) if vals else '')
        w.writerow(row)
print(f"USD CSV → {usd_csv}")

# ---------- ГРАФИК 1: оксиды в USD/т (две панели, РАЗНЫЕ масштабы) ----------
# элементы за тонну, без Yb (одна точка)
# дешёвые и дорогие
cheap = ['La', 'Ce', 'Sm', 'Y', 'Er']
expensive = ['Pr', 'Nd', 'Gd', 'Ho']

# СВОИ ylim для каждой панели (чтобы видно было динамику)
YMAX_CHEAP = 60_000   # недорогие: 0..60k USD/т (макс у Er ~50k, чтобы динамика была видна)
# дорогие: по максимуму серий на панели
all_exp = [p for el in expensive for yr, p, u in series[el] if el in series]
YMAX_EXP = max(all_exp) * 1.08

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
colors = plt.cm.tab10.colors
fmt = plt.FuncFormatter(lambda x, p: f'{x/1e6:.2f}')

for ax, els, title, ymax in [(axes[0], cheap, "Недорогие оксиды (USD/т)", YMAX_CHEAP),
                              (axes[1], expensive, "Дорогие оксиды (USD/т)", YMAX_EXP)]:
    for i, el in enumerate(els):
        if el not in series:
            continue
        xs = [p[0] for p in series[el]]
        ys = [p[1] for p in series[el]]
        ax.plot(xs, ys, 'o-', color=colors[i % 10], linewidth=2, markersize=6, label=el)
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("Год")
    ax.set_ylabel("USD/т  (×10⁶)")
    ax.set_xlim(2013.5, 2026.5)
    ax.set_ylim(0, ymax)  # от нуля, СВОЙ диапазон на панель
    ax.yaxis.set_major_formatter(fmt)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)

fig.suptitle("Цены оксидов РЗЭ — SMM (Shanghai Metals Market), 2014-2024, USD/т\n"
             "Каждая панель — свой вертикальный масштаб (0..60k / по данным); обычный сорт, усреднение по годам",
             fontsize=12, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(OUT_DIR / "ree_smm_all_tonne.png", dpi=150)
plt.close(fig)

# ---------- ГРАФИК 2: оксиды в USD/кг (Eu, Tb, Dy; без Lu) ----------
kg_els = [e for e in ORDER if e in series and series[e][0][2] == 'yuan/kg' and e != 'Lu']
fig, ax = plt.subplots(figsize=(12, 6))
for i, el in enumerate(kg_els):
    xs = [p[0] for p in series[el]]
    ys = [p[1] for p in series[el]]
    ax.plot(xs, ys, 'o-', color=colors[i % 10], linewidth=2.2, markersize=7, label=el)
ax.set_title("Оксиды РЗЭ — SMM 2014-2024, USD/кг (Eu, Tb, Dy)", fontsize=12)
ax.set_xlabel("Год"); ax.set_ylabel("USD/кг")
ax.set_xlim(2013.5, 2026.5)
ax.set_ylim(0, max(p for el in kg_els for _, p, _ in series[el]) * 1.08)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(OUT_DIR / "ree_smm_all_kg.png", dpi=150)
plt.close(fig)

# ---------- ГРАФИК 3: сводный Gd, Y, Eu + Nd (все в USD/кг, лог-шкала) ----------
# Gd, Y, Nd в USD/т → /1000 → USD/кг; Eu уже USD/кг
fig, ax = plt.subplots(figsize=(12, 6))

for el, color, ls in [('Gd', '#2ca02c', '-'), ('Y', '#1f77b4', '-'),
                         ('Eu', '#d62728', '-'), ('Nd', '#9467bd', '--')]:
    pts = []
    for yr, p, u in series[el]:
        if u == 'yuan/tonne':
            pts.append((yr, p / 1000))  # USD/т → USD/кг
        else:
            pts.append((yr, p))
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    ax.plot(xs, ys, ls, color=color, linewidth=2.5, markersize=7, label=el)

ax.set_yscale('log')
ax.set_title("Динамика цен Gd, Y, Eu, Nd — 2014-2024 (USD/кг, лог-шкала)\n"
             "Gd/Y/Eu/Nd — SMM (оксиды), Nd пунктиром; обычный сорт", fontsize=12)
ax.set_xlabel("Год"); ax.set_ylabel("USD/кг (логарифмическая)")
ax.set_xlim(2013.5, 2026.5)
ax.set_ylim(1, 1000)
ax.grid(True, alpha=0.3, which='both')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(OUT_DIR / "ree_gd_y_eu_usd.png", dpi=150)
plt.close(fig)

print("Графики → results/market/ree_smm_all_tonne.png, ree_smm_all_kg.png, ree_gd_y_eu_usd.png")

# ---------- Таблица USD ----------
print("\n=== Динамика в USD (медианы по годам) ===")
for el in ORDER:
    if el not in series:
        continue
    unit = series[el][0][2]
    ustr = 'USD/т' if unit == 'yuan/tonne' else 'USD/кг'
    by_year = defaultdict(list)
    for yr, p, u in series[el]:
        by_year[int(yr)].append(p)
    s = f"{el} ({ustr}): " + ", ".join(f"{y}:{sorted(v)[len(v)//2]:,.0f}" if ustr=='USD/т' else f"{y}:{sorted(v)[len(v)//2]:,.1f}" for y, v in sorted(by_year.items()))
    print(" ", s)
