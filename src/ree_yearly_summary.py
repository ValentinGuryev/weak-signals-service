#!/usr/bin/env python3
"""Итоговые данные по оксидам РЗЭ (SMM, 2014-2026): сводная таблица + CSV.

Источники: снапшоты Wayback (2014-2021, 2024c) — обычный сорт (grade='std').

Изменения v2 (2026-08-20, фикс артефактов сортов):
- Используем ТОЛЬКО обычный сорт (grade='std'). Раньше y2026 брался из ручного
  среза с ПЕРЕПУТАННЫМИ сортами (La=обычный 5500, Ce=высокочистый 14250) → ложное Ce/La=2.59.
- Добавлен год 2024 (снапшот 2024c): La=4000, Ce=7300 (обычный сорт) — честная точка.
- Мусор за логином (2023-2026 SPA) исключён автоматически: таких снапшотов нет в JSON.
- Yb/Lu/Ho/Er — только там, где есть данные (Ho/Er с 2016, Yb/Lu только 2024).
"""
import json, csv
from pathlib import Path
from collections import defaultdict

ROOT = Path("/home/user/projects/Hackathon")
SRC = ROOT / "data" / "raw" / "market" / "ree_prices" / "smm_ree_all.json"
OUT_CSV = ROOT / "data" / "raw" / "market" / "ree_prices" / "smm_ree_yearly.csv"
OUT_CSV_USD = ROOT / "data" / "raw" / "market" / "ree_prices" / "smm_ree_yearly_usd.csv"

# Среднегодовые курсы CNY/USD (юаней за 1 доллар) — как в plot_ree_all.py
RATES = {2014: 6.14, 2015: 6.23, 2016: 6.64, 2017: 6.76, 2018: 6.62,
         2019: 6.91, 2020: 6.90, 2021: 6.45, 2022: 6.73, 2023: 7.08,
         2024: 7.24, 2025: 7.19, 2026: 7.10}

d = json.loads(SRC.read_text(encoding="utf-8"))
snapshots = d["snapshots"]

# Только содержательные снапшоты (2014-2021, 2024c) и ТОЛЬКО обычный сорт
GOOD = {l for l, s in snapshots.items() if s["year"] in (2014, 2015, 2016, 2019, 2020, 2021, 2024)}

# усреднение по (элемент, год) — только spot, grade='std'
agg = defaultdict(list)
for l in sorted(GOOD):
    y = snapshots[l]["year"]
    for it in snapshots[l]["items"]:
        if it["type"] == "spot" and it.get("grade", "std") == "std":
            agg[(it["element"], y)].append(it["price_avg"])

UNIT = {
    'La': 'yuan/tonne', 'Ce': 'yuan/tonne', 'Pr': 'yuan/tonne', 'Nd': 'yuan/tonne',
    'Sm': 'yuan/tonne', 'Gd': 'yuan/tonne', 'Er': 'yuan/tonne', 'Y': 'yuan/tonne',
    'Ho': 'yuan/tonne', 'Yb': 'yuan/tonne',
    'Eu': 'yuan/kg', 'Tb': 'yuan/kg', 'Dy': 'yuan/kg', 'Lu': 'yuan/kg',
}
YEARS = [2014, 2015, 2016, 2019, 2020, 2021, 2024]

els = ['La', 'Ce', 'Pr', 'Nd', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Y', 'Yb', 'Lu']
FORMULA = {'La':'La2O3','Ce':'CeO2','Pr':'Pr6O11','Nd':'Nd2O3','Sm':'Sm2O3','Eu':'Eu2O3',
           'Gd':'Gd2O3','Tb':'Tb4O7','Dy':'Dy2O3','Ho':'Ho2O3','Er':'Er2O3','Y':'Y2O3',
           'Yb':'Yb2O3','Lu':'Lu2O3'}

def median(vals):
    return sorted(vals)[len(vals)//2] if vals else None

# CNY CSV
with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['element', 'formula', 'unit'] + [f'y{y}' for y in YEARS])
    for el in els:
        row = [el, FORMULA[el], UNIT[el]]
        for y in YEARS:
            v = median(agg.get((el, y), []))
            row.append('' if v is None else round(v))
        w.writerow(row)

# USD CSV (CNY → USD по курсу года)
with open(OUT_CSV_USD, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['element', 'formula', 'unit_usd'] + [f'y{y}' for y in YEARS])
    for el in els:
        row = [el, FORMULA[el], 'USD/tonne' if UNIT[el] == 'yuan/tonne' else 'USD/kg']
        for y in YEARS:
            v = median(agg.get((el, y), []))
            row.append('' if v is None else round(v / RATES.get(y, 7.0), 2))
        w.writerow(row)

print(f"CSV (CNY) → {OUT_CSV}")
print(f"CSV (USD) → {OUT_CSV_USD}")
print("\n=== Итоговая таблица (медиана по году, юани, обычный сорт) ===")
print(f"{'Эл':4s} " + ' '.join(f'{y:>9d}' for y in YEARS))
for el in els:
    vals = [median(agg.get((el, y), [])) for y in YEARS]
    print(f"{el:4s} " + ' '.join(('{v:>9,.0f}'.format(v=v) if v else ' ' * 9) for v in vals))
