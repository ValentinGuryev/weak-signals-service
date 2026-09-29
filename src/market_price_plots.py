#!/usr/bin/env python3
"""Графики цен: гелий (с точкой Китая) + газовая смесь Kr/Ne/F2 для эксимерного лазера.

Источники:
- Гелий (USD/м³, рынок США): оцифрованные USGS 2000-2022 + референсные точки
  (2024 ~$8 RSEE, 2026 ~$12). Китай: 2015 $3.73/м³ nongovernment (NGI B 2025).
- KrF-смесь (руб/л, госзакупки РФ): НМЦК госзакупок KrF-смеси для эксимерных
  лазеров (CL7100 248 нм, ~16 л в баллоне):
    2016: 210 000 руб/баллон (ИММиКН ЮФУ)
    2017: 175 000 руб/баллон (Premix KrF)
    2018: 210 000 руб/баллон (ИММиКН ЮФУ CL7100)
    2025: 464 333 руб/баллон = 29 020.83 руб/л (Курчатовский, 16 л, Ne 95.1%)
  Смесь: Ne 95% + Kr 3% + F2 ~2% (стандарт KrF).
  Пересчёт в USD/л по среднегодовому курсу.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
from pathlib import Path

ROOT = Path("/home/user/projects/Hackathon")
OUT_DIR = ROOT / "results" / "market"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ============ 1. ГЕЛИЙ ============
# Одна кривая (рынок США, розничная оценочная, USD/м³)
hel_years = [2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,
             2013,2014,2015,2019,2022,2024,2026]
hel_prices = [1.59,1.57,1.59,1.96,2.19,2.15,2.41,2.84,3.41,3.97,4.46,5.18,5.76,
              6.07,7.23,7.22,7.60,7.63,10.0,12.0]
# Китай: 2015 $3.73/м³ (nongovernment, NGI B 2025) — убрано с графика по решению автора
# (данные сохранены в knоwledge base / helium_prices_manual.md)
cn_years = []
cn_prices = []

fig, ax = plt.subplots(figsize=(13, 6))
ax.plot(hel_years, hel_prices, 'o-', color='#1f77b4', linewidth=2.5, markersize=6, zorder=3, label='США (оценочная розничная)')
# Точка Китая — убрана (решение команды)
if cn_years:
    ax.plot(cn_years, cn_prices, 's', color='#d62728', markersize=11, zorder=5, label='Китай (2015, негос. потребители, $3.73/м³)')
    ax.annotate('Китай 2015: $3.73/м³\n(негос. потребители)', xy=(2015, 3.73), xytext=(2017, 3.0),
                fontsize=9, color='#d62728', arrowprops=dict(arrowstyle='->', color='#d62728', lw=1.2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='mistyrose', edgecolor='#d62728', alpha=0.9))
# Диапазон извлечения
ax.axhspan(9, 13, color='gray', alpha=0.10, zorder=0)
ax.text(1998.2, 13.4, 'Извлечение из газа: $9-27/м³', fontsize=7.5, color='dimgray')
# Подписи ключевых точек США
for y, p in zip(hel_years, hel_prices):
    if y in (2000, 2005, 2010, 2015, 2022, 2024, 2026):
        ax.annotate(f'${p:.1f}', (y, p), textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, color='#1f77b4')
ax.set_title('Цены на гелий (USD/м³, 2000-2026) — оценочная розничная цена\nСША (кривая)', fontsize=11)
ax.set_xlabel('Год')
ax.set_ylabel('USD/м³')
ax.set_ylim(0, 17)
ax.set_xlim(1998, 2028)
ax.grid(True, alpha=0.3, zorder=0)
ax.legend(loc='upper left', fontsize=9)
plt.subplots_adjust(top=0.90, bottom=0.08, left=0.07, right=0.97)
plt.savefig(OUT_DIR / "helium_price.png", dpi=150)
plt.close(fig)
print("Гелий → results/market/helium_price.png")

# ============ 2. KrF-смесь (Kr/Ne/F2) ============
# Данные из госзакупок РФ (НМЦК, руб/баллон ~16л)
krf_data = [
    {"year": 2016, "rub_balloon": 210000, "org": "ИММиКН ЮФУ", "note": "1 баллон (16л)"},
    {"year": 2017, "rub_balloon": 175000, "org": "Premix KrF", "note": "1 баллон (16л)"},
    {"year": 2018, "rub_balloon": 210000, "org": "ИММиКН ЮФУ CL7100", "note": "1 баллон (16л)"},
    {"year": 2025, "rub_balloon": 464333, "org": "Курчатовский CL7100", "note": "1 баллон 16л, 29 020.83 руб/л, Ne 95.1%"},
]
# Курс USD/руб по годам (среднегодовой)
usd_rate = {2016: 67.0, 2017: 58.3, 2018: 62.7, 2025: 95.0}
# Пересчёт: руб/л → USD/л
for d in krf_data:
    d["rub_per_l"] = d["rub_balloon"] / 16.0
    d["usd_per_l"] = d["rub_per_l"] / usd_rate[d["year"]]

# Сохранить данные
with open(ROOT / "data" / "raw" / "market" / "excimer_prices" / "krf_prices.json", "w", encoding="utf-8") as f:
    json.dump({"gas": "KrF (Kr/Ne/F2)", "wavelength": "248 nm", "source": "zakupki.gov.ru (НМЦК госзакупок)",
               "note": "1 баллон ~16 л; 2025: Ne 95.1% (Курчатовский); руб/л → USD/л по курсу",
               "data": krf_data}, f, ensure_ascii=False, indent=2)

years_k = [d["year"] for d in krf_data]
usd_k = [d["usd_per_l"] for d in krf_data]
rub_k = [d["rub_per_l"] for d in krf_data]

fig2, ax2 = plt.subplots(figsize=(13, 6))
ax2.plot(years_k, usd_k, 'o-', color='#2ca02c', linewidth=2.5, markersize=8, zorder=3, label='KrF-смесь (USD/л)')
for y, u, r, d in zip(years_k, usd_k, rub_k, krf_data):
    ax2.annotate(f'${u:.0f}/л\n({r:,.0f} руб/л)', (y, u), textcoords="offset points", xytext=(0, 8),
                 ha='center', fontsize=8, color='#2ca02c')
    ax2.annotate(f"{d['org']}", (y, u), textcoords="offset points", xytext=(0, -30),
                 ha='center', fontsize=7, color='dimgray')
ax2.set_title('Газовая смесь Kr/Ne/F2 для эксимерного лазера (KrF, 248 нм)\nЦены госзакупок РФ (zakupki.gov.ru), USD/л, 1 баллон ~16 л', fontsize=11)
ax2.set_xlabel('Год')
ax2.set_ylabel('USD/л')
ax2.set_xlim(2014.5, 2026.5)
ax2.grid(True, alpha=0.3, zorder=0)
ax2.legend(loc='upper left', fontsize=9)
plt.subplots_adjust(top=0.88, bottom=0.12, left=0.07, right=0.97)
plt.savefig(OUT_DIR / "krf_laser_gas_price.png", dpi=150)
plt.close(fig2)
print("KrF-смесь → results/market/krf_laser_gas_price.png")
print("Данные → data/raw/market/excimer_prices/krf_prices.json")
print()
print("=== Таблица KrF ===")
for d in krf_data:
    print(f"{d['year']}: {d['rub_balloon']:,} руб/баллон = {d['rub_per_l']:,.0f} руб/л = ${d['usd_per_l']:.0f}/л | {d['org']}")
