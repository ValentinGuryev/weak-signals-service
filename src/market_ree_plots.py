#!/usr/bin/env python3
"""Графики цен на оксиды РЗЭ (иттрий, европий) по госзакупкам РФ.

Источник: zakupki.gov.ru (НМЦК госзакупок), data/raw/market/ree_prices/zakupki_ree_oxides.json
Собирается скриптом src/zakupki_ree.py (лог: results/runtime/zakupki_ree.log).

ВАЖНО (честность данных):
- цены БЕЗ учёта чистоты (purity=None в данных) — разные лоты могут иметь разный grade;
- иттрий: одна точка 2023 (лот 0373100099923000138) — динамики нет;
- европий: две точки 2023 и 2025 (разные лоты) — рост +47.7% в рублях;
- это реальные цены госзакупок РФ, НЕ сравниваются с синтетическими датасетами.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
from pathlib import Path

ROOT = Path("/home/user/projects/Hackathon")
OUT_DIR = ROOT / "results" / "market"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SRC = ROOT / "data" / "raw" / "market" / "ree_prices" / "zakupki_ree_oxides.json"

# ==== Данные ====
d = json.loads(SRC.read_text(encoding="utf-8"))
items = d["items"]

def series(ree: str) -> dict:
    """Год -> средняя цена руб/кг по уникальным лотам (усредняем дубликаты одного лота)."""
    by_year = {}
    for it in items:
        if it.get("ree") != ree:
            continue
        by_year.setdefault(it["year"], []).append(it["price_per_kg"])
    return {y: sum(v) / len(v) for y, v in sorted(by_year.items())}

y_series = series("иттрий")     # {2023: 19771.84}
eu_series = series("европий")   # {2023: 99100.32, 2025: 146412.0}

# Сохранить чистые данные рядом с исходником
clean = {
    "source": "zakupki.gov.ru (НМЦК госзакупок)",
    "note": "Средние цены по уникальным лотам, руб/кг; чистота не указана в исходных данных (None)",
    "yttrium_Y2O3": y_series,
    "europium_Eu2O3": eu_series,
}
(ROOT / "data" / "raw" / "market" / "ree_prices" / "ree_series_clean.json").write_text(
    json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")

# ==== График ====
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=False)

def draw(ax, series, label, color, note=""):
    years = list(series.keys())
    prices = list(series.values())
    ax.plot(years, prices, 'o-', color=color, linewidth=2.5, markersize=9, zorder=3, label=label)
    for y, p in zip(years, prices):
        ax.annotate(f"{p:,.0f} ₽/кг", (y, p), textcoords="offset points",
                    xytext=(0, 10), ha='center', fontsize=10, color=color, fontweight='bold')
    ax.set_title(f"{label}\n{note}", fontsize=11)
    ax.set_xlabel("Год")
    ax.set_ylabel("руб/кг")
    ax.set_xlim(min(years) - 0.8, max(years) + 0.8)
    ax.grid(True, alpha=0.3, zorder=0)
    ax.legend(loc='upper left', fontsize=9)

draw(axes[0], eu_series, "Европий (Eu₂O₃)", "#d62728",
     "2023 → 2025: +47,7% (в рублях)")
draw(axes[1], y_series, "Иттрий (Y₂O₃)", "#1f77b4",
     "только 1 лот (2023) — динамики нет")

fig.suptitle("Оксиды РЗЭ — цены госзакупок РФ (zakupki.gov.ru), руб/кг\n"
             "Реальные НМЦК; чистота в исходных данных не указана",
             fontsize=12, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(OUT_DIR / "ree_prices.png", dpi=150)
plt.close(fig)
print("График → results/market/ree_prices.png")
print("Данные → data/raw/market/ree_prices/ree_series_clean.json")
print()
print("=== Таблица ===")
print(f"Европий: " + ", ".join(f"{y}: {p:,.0f} ₽/кг" for y, p in eu_series.items()))
print(f"Иттрий:  " + ", ".join(f"{y}: {p:,.0f} ₽/кг" for y, p in y_series.items()))
