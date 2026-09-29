#!/usr/bin/env python3
"""Анализ цен на гелий из госзакупок РФ: газ высокой чистоты (6N/99.9999%), по годам.

Вход: data/raw/market/helium_prices/zakupki_helium.json
Выход:
- results/market/helium_rf_prices.png — график (медиана 6N газ/баллон по годам)
- data/raw/market/helium_prices/helium_rf_clean.json — очищенная таблица

Метод: фильтр марка 6N/6.0/99.9999% (газ, БЕЗ жидкого); медиана по году.
"""
import json
import re
from statistics import median
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/home/user/projects/Hackathon")
SRC = ROOT / "data" / "raw" / "market" / "helium_prices" / "zakupki_helium.json"
OUT = ROOT / "data" / "raw" / "market" / "helium_prices" / "helium_rf_clean.json"
IMG = ROOT / "results" / "market" / "helium_rf_prices.png"


def classify(name: str) -> str | None:
    """Тип газообразного гелия: '6N' (99.9999%) или 'марка А' (99.995%).
    Жидкий — НЕ включаем."""
    n = name.lower()
    if 'жидк' in n:
        return None  # жидкий убран
    if re.search(r'6\.0|6,0|6n|99,9999|99\.9999|особой чистоты', n):
        return '6N'
    if re.search(r'марк[аи]?\s*["«]?а|99\.99[56]|высокой чистоты', n):
        return 'марка А'
    return None


MIN_PRICE = 1000  # фильтр мусора (цены <1000 руб/баллон — ошибки парсинга)

# Исключения-выбросы (решение команды):
# - 6N 2026: год целиком (цены аномально низкие)
# - марка А 2019: точки 22 461 (29.12.2019), 23 500, 25 200 — выбросы «высокой чистоты»
EXCLUDE_YEARS = {(2026, '6N')}
EXCLUDE_PRICES = {(2019, 'марка А', 22460.66), (2019, 'марка А', 23500.00), (2019, 'марка А', 25200.00)}


def price_per_liter(price: float, unit: str, is_gas: bool) -> float:
    """Нормализация к руб/литр. Баллон 40л ≈ газ; 'Штука' для газа = баллон (обычно 40л)."""
    u = (unit or '').lower()
    if 'литр' in u or 'кубический дециметр' in u:
        return price
    if 'кубический метр' in u:
        return price / 1000.0  # м³ → литр
    if 'штук' in u:  # баллон
        # гелий в баллоне: 40 л стандарт; цена за баллон → за литр (газа под давлением ~150-200 атм)
        # но объём газа в баллоне ≈ 40л × ~150 атм ≈ 6000 л газа; жидкого эквивалента нет.
        # Для газообразного: 1 баллон 40л при 150 атм ≈ 6 м³ газа. Цена/м³ = price/6.
        if is_gas:
            return price / 6.0  # ≈ руб/м³ газа → /1000 = руб/л
    return price


def main() -> None:
    if not SRC.exists():
        print(f"Нет данных: {SRC}")
        return
    data = json.loads(SRC.read_text(encoding="utf-8"))
    items = data.get("items", [])
    print(f"Закупок с позициями: {len(items)}")

    rows = []
    for it in items:
        for p in it.get("helium_positions", []):
            name = p.get("name", "")
            price = p.get("price")
            if not price or not classify(name):
                continue
            date = p.get("date") or ""
            m = re.search(r'(\d{4})', date)
            year = int(m.group(1)) if m else None
            if not year:
                continue
            kind = classify(name)
            unit = p.get("unit", "")
            rows.append({
                "num": it.get("num"), "year": year, "date": date, "kind": kind,
                "name": name[:100], "unit": unit, "price": float(price),
                "customer": it.get("customer", "")[:50],
            })

    rows.sort(key=lambda r: (r["year"], r["kind"]))
    OUT.write_text(json.dumps({"note": "Гелий газообразный: 6N (99.9999%) + марка А (99.995%), из госзакупок РФ",
                               "count": len(rows), "rows": rows},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Позиций газ. гелия: {len(rows)} → {OUT}")

    # Медиана по году и типу (газ в баллонах)
    gas_balloon = {}  # (year, kind) -> [цены за баллон]
    gas_m3 = {}       # (year, kind) -> [цены за м³]
    for r in rows:
        if float(r["price"]) < MIN_PRICE:
            continue  # мусор (ошибки парсинга)
        # исключения-выбросы
        if (r["year"], r["kind"]) in EXCLUDE_YEARS:
            continue
        if (r["year"], r["kind"], round(float(r["price"]), 2)) in EXCLUDE_PRICES:
            continue
        u = (r["unit"] or '').lower()
        key = (r["year"], r["kind"])
        if 'штук' in u or 'шт' in u or 'усл' in u:
            gas_balloon.setdefault(key, []).append(float(r["price"]))
        elif 'кубический метр' in u:
            gas_m3.setdefault(key, []).append(float(r["price"]))

    print("\n=== Гелий газ (руб/баллон, медиана по году и типу) ===")
    for (y, kind) in sorted(gas_balloon):
        vals = gas_balloon[(y, kind)]
        print(f"  {y} {kind}: n={len(vals)}, медиана={median(vals):,.0f}, min={min(vals):,.0f}, max={max(vals):,.0f}")

    # График (газ в баллонах): 6N и марка А разными цветами
    fig, ax = plt.subplots(figsize=(13, 6))
    for kind, color in [('6N', '#1f77b4'), ('марка А', '#ff7f0e')]:
        pts = [(y, median(vals)) for (y, k), vals in sorted(gas_balloon.items()) if k == kind]
        if not pts:
            continue
        ys = [p[0] for p in pts]
        meds = [p[1] for p in pts]
        ax.plot(ys, meds, 'o-', color=color, linewidth=2.5, label=f'{kind} газ, медиана руб/баллон')
        for y, v in zip(ys, meds):
            ax.annotate(f'{v:,.0f}', (y, v), textcoords="offset points", xytext=(0, 8), fontsize=9, color=color)
    ax.set_title('Гелий газообразный в РФ из госзакупок: 6N (99.9999%) и марка А (99.995%)\nмедиана руб/баллон по году', fontsize=11)
    ax.set_xlabel('Год')
    ax.set_ylabel('руб/баллон')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(IMG, dpi=150)
    print(f"\nГрафик → {IMG}")


if __name__ == "__main__":
    main()
