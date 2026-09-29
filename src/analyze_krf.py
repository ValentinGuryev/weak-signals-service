#!/usr/bin/env python3
"""Анализ цен на газовые смеси для эксимерных лазеров (KrF/ArF) из госзакупок РФ.

Вход: data/raw/market/excimer_prices/zakupki_laser_gas.json
Выход:
- results/market/krf_laser_gas_price.png — график цены за БАЛЛОН по годам
- data/raw/market/excimer_prices/krf_clean.json — отфильтрованные смеси

ВАЖНО: НМЦК = начальная (макс.) цена ВСЕЙ закупки. Для сравнения нормализуем
к цене за БАЛЛОН (÷ количество, где известно):
- Микроскан Визум 2023-24: 3 баллона → ÷3
- CL7020 2025: 1 баллон (16 л, 29020 руб/л)
- Выброс 2017 (2+ ед) исключён.
"""
import json
import re
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/home/user/projects/Hackathon")
SRC = ROOT / "data" / "raw" / "market" / "excimer_prices" / "zakupki_laser_gas.json"
OUT = ROOT / "data" / "raw" / "market" / "excimer_prices" / "krf_clean.json"
IMG = ROOT / "results" / "market" / "krf_laser_gas_price.png"

def is_gas_mix(title: str) -> bool:
    t = title.lower()
    # смесь для лазера
    if 'смес' in t and re.search(r'лазер|эксимер|krf|arf|офтальм|xecl', t):
        return True
    return False

def mix_type(title: str) -> str:
    """Тип смеси по названию → ХИМ. СОСТАВ."""
    tl = title.lower()
    if 'микроскан' in tl or 'визум' in tl:
        # Офтальмологический эксимерный лазер ArF 193 нм (Микроскан Визум)
        return 'ArF: Ne+Ar+F2 (Микроскан Визум)'
    if 'cl7020' in tl or 'cl7100' in tl:
        # KrF 248 нм: Ne 95.1% + Kr 2.9% + F2 2% (из карточки Курчатовского 2025)
        return 'KrF: Ne95+Kr3+F2 (CL7020/7100)'
    if 'фтораргон' in tl or 'arf' in tl:
        return 'ArF: фтораргон'
    if 'криптон' in tl:
        return 'KrF: криптоновая'
    return 'KrF/ArF (не уточнено)'

# Цвета по типам
TYPE_COLORS = {
    'ArF: Ne+Ar+F2 (Микроскан Визум)': '#1f77b4',
    'KrF: Ne95+Kr3+F2 (CL7020/7100)': '#d62728',
    'ArF: фтораргон': '#2ca02c',
    'KrF: криптоновая': '#9467bd',
    'KrF/ArF (не уточнено)': '#ff7f0e',
}

# Исключаемые выбросы (объём заведомо >1 баллона / доп. условия)
# 0373100047417000510 (2017): 2+ ед (945482 руб/ед × 2 = 1.89M) — двойной объём
EXCLUDE = {"0373100047417000510"}

# Нормализация: НМЦК → цена за БАЛЛОН (÷ количество единиц)
# Из карточек: Микроскан Визум 2023-24 = 3 баллона; остальные = 1 баллон
QTY = {
    "0373100047423000476": 3,  # 2023 Микроскан Визум (проверено: кол-во 3)
    "0373100047424001696": 3,  # 2024 Микроскан Визум (проверено: 2 шт + 1 шт)
}

def main() -> None:
    if not SRC.exists():
        print(f"Нет данных: {SRC}")
        return
    d = json.loads(SRC.read_text(encoding="utf-8"))
    items = d["items"]
    print(f"Всего закупок: {len(items)}")

    rows = []
    for it in items:
        if it.get("num") in EXCLUDE:
            continue  # выброс (объём >1 ед)
        title = it.get("title", "") or it.get("object", "")
        if not is_gas_mix(title):
            continue
        date = it.get("date", "")
        m = re.search(r'(\d{4})', date)
        year = int(m.group(1)) if m else None
        price = it.get("price") or it.get("nmck")
        if not year or not price:
            continue
        rows.append({"num": it.get("num"), "year": year, "date": date,
                     "title": title[:80], "nmck": float(price),
                     "per_balloon": float(price) / QTY.get(it.get("num"), 1),
                     "type": mix_type(title)})

    rows.sort(key=lambda r: (r["year"], r["nmck"]))
    OUT.write_text(json.dumps({"note": "Смеси для эксимерных лазеров, НМЦК госзакупок РФ",
                               "count": len(rows), "rows": rows},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Смесей для лазеров: {len(rows)} → {OUT}")

    # по годам: медиана цены за баллон
    by_year = {}
    for r in rows:
        by_year.setdefault(r["year"], []).append(r["per_balloon"])
    print("\n=== Цена за баллон (НМЦК ÷ кол-во) по годам (руб) ===")
    for y in sorted(by_year):
        vals = by_year[y]
        from statistics import median
        print(f"  {y}: n={len(vals)}, медиана={median(vals):,.0f}, min={min(vals):,.0f}, max={max(vals):,.0f}")

    # график: точки по типу (цвет), медиана по типу
    # Показываем только типы с ≥2 разными годами (одиночные точки не дают динамики)
    fig, ax = plt.subplots(figsize=(14, 7))
    for typ in TYPE_COLORS:
        pts = [r for r in rows if r["type"] == typ]
        if not pts:
            continue
        n_years = len(set(r["year"] for r in pts))
        if n_years < 2:
            print(f"  (пропущен {typ}: только {n_years} год — нет динамики)")
            continue  # одиночные точки убираем
        xs = [r["year"] for r in pts]
        ys = [r["per_balloon"] / 1e6 for r in pts]
        ax.scatter(xs, ys, alpha=0.7, color=TYPE_COLORS[typ], s=50, label=typ)
        # медиана по типу
        ty = {}
        for r in pts:
            ty.setdefault(r["year"], []).append(r["per_balloon"])
        yrs = sorted(ty)
        meds = [median(ty[y]) / 1e6 for y in yrs]
        if len(yrs) > 1:
            ax.plot(yrs, meds, '--', color=TYPE_COLORS[typ], linewidth=1.5, alpha=0.6)
        for y, v in zip(yrs, meds):
            ax.annotate(f'{v:.2f}', (y, v), textcoords="offset points", xytext=(0, 7), fontsize=7, color=TYPE_COLORS[typ])
    ax.set_title('Газовые смеси для эксимерных лазеров — госзакупки РФ\nЦена за БАЛЛОН (НМЦК ÷ кол-во), млн руб, по типу смеси', fontsize=11)
    ax.set_xlabel('Год')
    ax.set_ylabel('Цена за баллон, млн руб')
    ax.set_ylim(0, None)  # ось от нуля (иначе ложное ощущение динамики)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(IMG, dpi=150)
    print(f"\nГрафик → {IMG}")

if __name__ == "__main__":
    main()
