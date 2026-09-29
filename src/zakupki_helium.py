#!/usr/bin/env python3
"""Сбор цен на ГЕЛИЙ из госзакупок РФ (zakupki.gov.ru) — марки высокой чистоты.

Задача: цены на гелий ОДНОЙ марки (чистоты) в РФ за ~20 лет.
Марки (по приоритету, как просил автор): 6.0 (99.9999%), 5.5 (99.9995%),
5.0 (99.999%), марка А (99.995%) — НЕ ниже.

Метод:
1. Поиск по фразам: "гелий газообразный марки", "гелий высокой чистоты",
   "гелий марка 6", "гелий 99.99", "гелий жидкий".
2. Список → объекты закупки → отфильтровать те, где есть "гелий" + марка/чистота.
3. Карточка → извлечь позиции гелия: марка, чистота, баллон/литр, цена за единицу, кол-во.
4. Сохранить: data/raw/market/helium_prices/zakupki_helium.json
   + таблица (год, марка, цена/л, цена/баллон).

Источник: zakupki.gov.ru (wget --no-check-certificate, UA браузера, паузы 2-3 сек).
"""
import json
import re
import subprocess
import time
import html
from pathlib import Path

ROOT = Path("/home/user/projects/Hackathon")
OUT_DIR = ROOT / "data" / "raw" / "market" / "helium_prices"
OUT = OUT_DIR / "zakupki_helium.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://zakupki.gov.ru"

# Поисковые запросы (широкие — марка определится в карточке)
QUERIES = [
    "гелий газообразный", "гелий", "гелий в баллонах",
    "гелий жидкий", "поставка газов гелий", "газы в баллонах гелий",
    "гелий марки", "гелий высокой чистоты", "гелий 6.0", "гелий 99.999",
]

# Годы поиска: от 2005 до 2026. ПЛОТНО: отдельные годы для 2019-2026 (важна плотность),
# 4-летки для старых.
YEAR_RANGES = [("01.01.2005", "31.12.2008"), ("01.01.2009", "31.12.2012"),
               ("01.01.2013", "31.12.2016"), ("01.01.2017", "31.12.2018"),
               ("01.01.2019", "31.12.2019"), ("01.01.2020", "31.12.2020"),
               ("01.01.2021", "31.12.2021"), ("01.01.2022", "31.12.2022"),
               ("01.01.2023", "31.12.2023"), ("01.01.2024", "31.12.2024"),
               ("01.01.2025", "31.12.2025"), ("01.01.2026", "31.12.2026")]


def wget(url: str, out: str, timeout: int = 30) -> bool:
    r = subprocess.run(["wget", "-q", "--no-check-certificate", "--timeout", str(timeout),
                        "-U", UA, "-O", out, url], capture_output=True)
    return Path(out).exists() and Path(out).stat().st_size > 1000

def fetch(url: str, tmp: str) -> str:
    if wget(url, tmp):
        return open(tmp, encoding="utf-8", errors="ignore").read()
    return ""

def parse_list(html_text: str) -> list[dict]:
    """Парсинг списка: номер, объект, цена, заказчик, дата."""
    items = []
    blocks = re.split(r'<div class="search-registry-entry-block', html_text)
    for b in blocks[1:]:
        num = re.search(r'(?:purchaseNoticeNumber|regNumber)=(\d+)', b)
        if not num:
            continue
        om = re.search(r'body-title[^>]*>Объект закупки.*?body-value[^>]*>([^<]{3,300})<', b, re.S)
        obj = html.unescape(om.group(1)).strip() if om else ''
        pm = re.search(r'Начальная цена\s*</[^>]+>\s*<[^>]+>([\d\s\u00a0.,]+)\s*₽', b, re.S)
        price = pm.group(1).replace(' ', '').replace('\u00a0', '').replace(',', '.') if pm else None
        cm = re.search(r'body-title[^>]*>Заказчик.*?body-value[^>]*>([^<]{5,200})<', b, re.S)
        cust = html.unescape(cm.group(1)).strip() if cm else ''
        dm = re.search(r'body-title[^>]*>Размещено.*?body-value[^>]*>([\d.]+)', b, re.S)
        date = dm.group(1) if dm else None
        items.append({"num": num.group(1), "object": obj, "price": price,
                      "customer": cust, "date": date})
    return items

def parse_card(html_text: str, num: str) -> dict:
    """Из карточки: позиции гелия (марка, чистота, баллон, цена/ед, кол-во).
    Поддерживает ДВЕ структуры:
    - новая: 'Товар | ед | цена | кол-во | сумма' (табличная)
    - старая: 'Название | код | кол-во | ед | цена | сумма' (строковая)
    """
    clean = re.sub(r'<[^>]+>', '\n', re.sub(r'<script.*?</script>|<style.*?</style>', ' ', html_text, flags=re.S))
    clean = html.unescape(clean)
    lines = [l.strip() for l in clean.split('\n') if l.strip()]
    hel_positions = []
    for i, l in enumerate(lines):
        if 'гели' in l.lower() and len(l) < 130:
            # марка/чистота
            mm = re.search(r'(марк[аи]?\s*\d[.\d]*|марк[аи]?\s*[АБВ]|6\.0|5\.5|5\.0|99\.\d+|6n|5n)', l, re.I)
            mark = mm.group(1) if mm else None
            if mark and re.match(r'марк[аи]?\s*[ВГД]', mark, re.I):
                continue  # марки В/Г — ниже
            cm = re.search(r'(\d{2}\.\d{2}\.\d{4})', html_text)
            date = cm.group(1) if cm else None

            # === УНИВЕРСАЛЬНЫЙ парсер позиции: единица → числа вокруг ===
            # Структуры:
            #   2014: название | код | ЕД | кол-во | цена | сумма  (кол-во ПОСЛЕ ед)
            #   2023: название | код | кол-во | ЕД | цена | сумма  (кол-во ПЕРЕД ед)
            #   2026: название | ... | Товар | ЕД | цена            (кол-во нет)
            # Правило: если перед ЕД число → цена = 1-е число после;
            #          иначе кол-во = 1-е число после, цена = 2-е.
            price = None; unit = None; qty = None
            if i + 2 < len(lines):
                seg = lines[i+1:i+8]
                unit_idx = None
                for k, s in enumerate(seg):
                    if re.match(r'^(штук|литр|кубическ|м3|баллон|усл[\s.]*ед|шт)', s, re.I):
                        unit_idx = k
                        unit = s
                        break
                if unit_idx is not None:
                    nums_after = []
                    for s in seg[unit_idx+1:]:
                        if re.match(r'^[\d][\d\s.,]*\d$', s):
                            nums_after.append(s.replace(' ', '').replace(',', '.'))
                        else:
                            break
                    # кол-во перед единицей (целое без точек — НЕ код ОКПД2)
                    prev_qty = None
                    if unit_idx > 0 and re.match(r'^\d+$', seg[unit_idx-1]):
                        prev_qty = seg[unit_idx-1].replace(' ', '')
                    if prev_qty:
                        qty = prev_qty
                        if nums_after:
                            price = nums_after[0]
                    else:
                        if len(nums_after) >= 2:
                            qty = nums_after[0]
                            price = nums_after[1]
                        elif len(nums_after) == 1:
                            price = nums_after[0]

            # === новая структура: 'Товар | ед | цена | кол-во | сумма' ===
            if not price:
                for j in range(i, min(i+10, len(lines))):
                    if lines[j] in ('Товар', 'Услуга') and j+3 < len(lines):
                        unit = lines[j+1] if len(lines[j+1]) < 40 else None
                        m2 = re.search(r'([\d][\d\s.,]*\d)', lines[j+2])
                        if m2:
                            price = m2.group(1).replace(' ', '').replace(',', '.')
                        m3 = re.search(r'([\d][\d\s.,]*\d)', lines[j+3])
                        if m3:
                            qty = m3.group(1).replace(' ', '').replace(',', '.')
                        break
            hel_positions.append({
                "name": l[:120], "mark": mark, "unit": unit,
                "price": price, "qty": qty, "date": date,
            })
    # убрать дубли-характеристики (без марки и без цены)
    hel_positions = [p for p in hel_positions if (p["mark"] or p["price"])]
    return {"num": num, "helium_positions": hel_positions}

def main() -> None:
    all_items = {}
    # Поиск: каждый запрос × каждый годовой диапазон (для обхода лимита по датам)
    for q in QUERIES:
        qq = q.replace(" ", "+")
        for d_from, d_to in YEAR_RANGES:
            print(f"=== {q} [{d_from}..{d_to}] ===")
            for page in range(1, 4):
                url = (f"{BASE}/epz/order/extendedsearch/results.html?searchString={qq}"
                       f"&fz44=on&fz223=on&publishDateFrom={d_from}&publishDateTo={d_to}"
                       f"&pageNumber={page}")
                tmp = f"/tmp/zak_hel2_{abs(hash(q))%99999}_{d_from[:4]}_{page}.html"
                h = fetch(url, tmp)
                if not h:
                    print(f"  стр{page}: нет")
                    break
                items = parse_list(h)
                # релевантность: объект содержит газ/гелий (марка определится в карточке)
                rel = [it for it in items if any(w in (it["object"] + it["customer"]).lower()
                                                 for w in ["газ", "гели"])]
                print(f"  стр{page}: {len(items)} всего, {len(rel)} релевантных")
                for it in rel:
                    all_items[it["num"]] = it
                if len(items) < 10:
                    break
                time.sleep(2)
            time.sleep(2)
        time.sleep(3)

    # Этап 2: карточки релевантных
    print(f"\n=== Карточки ({len(all_items)}) ===")
    results = []
    for n, meta in all_items.items():
        # 44-ФЗ или 223-ФЗ
        if n.startswith("3"):
            # guid не обязателен для printForm 44-ФЗ; для 223 нужен
            if len(n) == 11:  # 223-ФЗ
                # поищем guid в сохранённых страницах
                guid = None
                for f in Path('/tmp').glob('zak_hel2_*.html'):
                    h = f.read_text(encoding='utf-8', errors='ignore')
                    m = re.search(rf'purchaseNoticeNumber={n}&(?:amp;)?purchaseNoticeGuid=([0-9a-f\-]{{36}})', h)
                    if m:
                        guid = m.group(1); break
                if guid:
                    url = f"{BASE}/epz/order/notice/notice223/printForm/view.html?purchaseNoticeNumber={n}&purchaseNoticeGuid={guid}"
                else:
                    print(f"  {n}: нет guid, пропуск")
                    continue
            else:
                url = f"{BASE}/epz/order/notice/printForm/view.html?regNumber={n}"
        else:
            url = f"{BASE}/epz/order/notice/printForm/view.html?regNumber={n}"
        tmp = f"/tmp/zak_hel_card_{n}.html"
        h = fetch(url, tmp)
        if not h:
            print(f"  {n}: пусто")
            continue
        card = parse_card(h, n)
        if card["helium_positions"]:
            card.update(meta)
            results.append(card)
            for p in card["helium_positions"]:
                print(f"  {n} | {p['date']} | марка {p['mark']} | {p['unit']} | {p['price']}₽/ед × {p['qty']} | {p['name'][:60]}")
        time.sleep(2)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"source": "zakupki.gov.ru", "query": "гелий марки 6.0/5.5/А (высокой чистоты)",
                               "count": len(results), "items": results},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== ИТОГО: {len(results)} закупок с позициями гелия → {OUT} ===")

if __name__ == "__main__":
    main()
