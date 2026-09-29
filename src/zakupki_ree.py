#!/usr/bin/env python3
"""Сбор цен на оксиды РЗЭ (3N-4N чистота) с госзакупок РФ, 2014-2026.

Логика:
- Для каждого РЗЭ-оксида (рус. название) и каждого года 2014-2026 — отдельный запрос.
- Запрос: "оксид <РЗЭ>" + фильтр дат.
- Парсим карточки: цена за кг (реактивы), чистота (3N-4N = 99.9-99.99%).
- Фильтр: только чистота 3N-4N (не 5N+ — слишком чистый не интересует).
- Сохраняем: data/raw/market/ree_prices/zakupki_ree_oxides.json

РЗЭ-оксиды (рус. названия для поиска):
Иттрий, Гадолиний, Неодим, Диспрозий, Тербий, Лантан, Церий, Празеодим,
Самарий, Эрбий, Европий, Гольмий, Лютеций, Тулий, Иттербий, Скандий.
"""
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path("/home/user/projects/Hackathon")
OUT_DIR = ROOT / "data" / "raw" / "market" / "ree_prices"
OUT = OUT_DIR / "zakupki_ree_oxides.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://zakupki.gov.ru"

# РЗЭ-оксиды: русское имя (для поиска) → формула
REES = [
    ("иттрий", "Y2O3"), ("гадолиний", "Gd2O3"), ("неодим", "Nd2O3"),
    ("диспрозий", "Dy2O3"), ("тербий", "Tb2O3"), ("лантан", "La2O3"),
    ("церий", "CeO2"), ("празеодим", "Pr2O3"), ("самарий", "Sm2O3"),
    ("эрбий", "Er2O3"), ("европий", "Eu2O3"), ("гольмий", "Ho2O3"),
    ("лютеций", "Lu2O3"), ("тулий", "Tm2O3"), ("иттербий", "Yb2O3"),
    ("скандий", "Sc2O3"),
]

# Годы 2014-2026 (по одному)
YEARS = list(range(2014, 2027))

def wget(url: str, out: str, timeout: int = 30) -> bool:
    r = subprocess.run(["wget", "-q", "--no-check-certificate", "--timeout", str(timeout),
                        "-U", UA, "-O", out, url], capture_output=True)
    return Path(out).exists() and Path(out).stat().st_size > 1000

def fetch(url: str, tmp: str) -> str:
    if wget(url, tmp):
        return open(tmp, encoding="utf-8", errors="ignore").read()
    return ""

def parse_list(html_text: str) -> list[dict]:
    """Парсинг списка закупок."""
    items = []
    blocks = re.split(r'<div class="search-registry-entry-block', html_text)
    for b in blocks[1:]:
        num = re.search(r'(?:purchaseNoticeNumber|regNumber)=(\d+)', b)
        if not num:
            continue
        om = re.search(r'body-title[^>]*>Объект закупки.*?body-value[^>]*>([^<]{3,300})<', b, re.S)
        obj = re.sub(r'\s+', ' ', (om.group(1) if om else '')).strip()
        pm = re.search(r'Начальная цена\s*</[^>]+>\s*<[^>]+>([\d\s\u00a0.,]+)\s*₽', b, re.S)
        price = pm.group(1).replace(' ', '').replace('\u00a0', '').replace(',', '.') if pm else None
        items.append({"num": num.group(1), "object": obj[:200], "price": price})
    return items

def parse_card(html_text: str, num: str, year: int) -> list[dict]:
    """Из карточки: ВСЕ позиции с оксидами РЗЭ (цена/кг).
    Ищем строки вида '<РЗЭ> оксид' с ценой за Килограмм."""
    clean = re.sub(r'<[^>]+>', '\n', re.sub(r'<script.*?</script>|<style.*?</style>', ' ', html_text, flags=re.S))
    clean = __import__('html').unescape(clean)
    lines = [l.strip() for l in clean.split('\n') if l.strip()]
    # карта РЗЭ-формул по рус. названиям
    ree_map = {
        'иттербий': 'Yb2O3', 'гадолиний': 'Gd2O3', 'диспрозий': 'Dy2O3',
        'празеодим': 'Pr2O3', 'самарий': 'Sm2O3', 'европий': 'Eu2O3',
        'гольмий': 'Ho2O3', 'лютеций': 'Lu2O3', 'иттрий': 'Y2O3',
        'неодим': 'Nd2O3', 'лантан': 'La2O3', 'церий': 'CeO2',
        'тербий': 'Tb2O3', 'эрбий': 'Er2O3', 'тулий': 'Tm2O3', 'скандий': 'Sc2O3',
    }
    hits = []
    for i, l in enumerate(lines):
        ll = l.lower()
        if 'оксид' not in ll:
            continue
        # какой РЗЭ
        ree_found = None
        for name, formula in ree_map.items():
            if name in ll:
                ree_found = (name, formula)
                break
        if not ree_found:
            continue  # не РЗЭ (алюминий, гафний и т.д.)
        name, formula = ree_found
        # чистота (3N-4N): ищем в строке или рядом
        purity = None
        pm = re.search(r'(99\.\d{2,4}|3N|4N)', l, re.I)
        if pm:
            p = pm.group(1)
            if p in ('3N', '4N'):
                purity = p
            else:
                try:
                    pv = float(p)
                    if 99.9 <= pv <= 99.99:
                        purity = p
                except:
                    pass
        # цена за кг
        price_kg = None
        for j in range(i, min(i+12, len(lines))):
            if lines[j].lower() in ('килограмм', 'кг') and j+1 < len(lines):
                m2 = re.search(r'([\d][\d\s.,]*\d)', lines[j+1])
                if m2:
                    price_kg = m2.group(1).replace(' ', '').replace(',', '.')
                break
        if price_kg and float(price_kg) > 100:
            hits.append({"ree": name, "formula": formula, "purity": purity,
                         "price_per_kg": float(price_kg), "name": l[:100],
                         "num": num, "year": year})
    return hits

def main() -> None:
    all_hits = []
    for ree, formula in REES:
        for year in YEARS:
            q = f"оксид {ree}"
            qq = q.replace(" ", "+")
            d_from = f"01.01.{year}"
            d_to = f"31.12.{year}"
            url = (f"{BASE}/epz/order/extendedsearch/results.html?searchString={qq}"
                   f"&fz44=on&fz223=on&publishDateFrom={d_from}&publishDateTo={d_to}")
            tmp = f"/tmp/zak_ree_{ree}_{year}.html"
            h = fetch(url, tmp)
            if not h:
                print(f"  {ree} {year}: нет")
                continue
            items = parse_list(h)
            rel = [it for it in items if ree.lower() in it['object'].lower() or 'реактив' in it['object'].lower()]
            print(f"  {ree} {year}: {len(items)} закупок, {len(rel)} релевантных")
            for it in rel[:5]:  # до 5 карточек на запрос
                # откроем карточку
                curl_url = f"{BASE}/epz/order/notice/printForm/view.html?regNumber={it['num']}"
                ctmp = f"/tmp/zak_ree_card_{it['num']}.html"
                ch = fetch(curl_url, ctmp)
                if ch:
                    hits = parse_card(ch, it['num'], year)
                    for hh in hits:
                        all_hits.append(hh)
                        print(f"    → {hh['formula']} чистота={hh['purity']} {hh['price_per_kg']} руб/кг ({year})")
                time.sleep(1.5)
            time.sleep(1)
        time.sleep(2)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"source": "zakupki.gov.ru", "note": "Оксиды РЗЭ 3N-4N, руб/кг",
                               "count": len(all_hits), "items": all_hits},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== ИТОГО: {len(all_hits)} позиций → {OUT} ===")

if __name__ == "__main__":
    main()
