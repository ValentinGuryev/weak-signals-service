#!/usr/bin/env python3
"""Сбор закупок РФ на лазерные газовые смеси (KrF/ArF/XeCl, Kr/Ne/F2) с zakupki.gov.ru.

Этап 1: поиск по ключевым словам → собрать номера закупок (44-ФЗ и 223-ФЗ).
Этап 2: открыть карточку каждой закупки (printForm) → название, НМЦК, цена за единицу, объём.
Этап 3: сохранить в data/raw/market/excimer_prices/zakupki_laser_gas.json

Источник: zakupki.gov.ru (curl -k из-за самоподписанного сертификата).
"""
import json
import re
import subprocess
import time
import html
from pathlib import Path

ROOT = Path("/home/user/projects/Hackathon")
OUT = ROOT / "data" / "raw" / "market" / "excimer_prices" / "zakupki_laser_gas.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://zakupki.gov.ru"

QUERIES = ["KrF", "ArF", "XeCl", "газовая смесь лазерная", "криптон", "неон фтор",
           "эксимерный лазер газ", "лазерная газовая смесь", "фтористый водород",
           "криптон фтор", "фтор неон", "смесь для эксимерного", "лазерный газ",
           "KrF смесь", "газ для лазера", "эксимерная смесь"]

# Годы поиска (по 4-леткам, чтобы обойти лимит по датам)
YEAR_RANGES = [("01.01.2005", "31.12.2008"), ("01.01.2009", "31.12.2012"),
               ("01.01.2013", "31.12.2016"), ("01.01.2017", "31.12.2020"),
               ("01.01.2021", "31.12.2026")]

def curl(url: str, out: str, timeout: int = 30) -> int:
    subprocess.run(["curl", "-sk", "--max-time", str(timeout), "-A", UA, url, "-o", out],
                   capture_output=True)
    return Path(out).stat().st_size if Path(out).exists() else 0

def fetch(url: str, tmp: str) -> str:
    size = curl(url, tmp)
    if size < 1000:
        return ""
    return open(tmp, encoding="utf-8", errors="ignore").read()

def collect_numbers() -> dict:
    """Собрать номера закупок из всех поисковых запросов (по годам)."""
    nums = {}
    for q in QUERIES:
        qq = q.replace(" ", "+")
        for d_from, d_to in YEAR_RANGES:
            for page in range(1, 6):
                url = (f"{BASE}/epz/order/extendedsearch/results.html?searchString={qq}"
                       f"&fz44=on&fz223=on&publishDateFrom={d_from}&publishDateTo={d_to}&pageNumber={page}")
                tmp = f"/tmp/zak_ls_{abs(hash(q))%99999}_{d_from[:4]}_{page}.html"
                h = fetch(url, tmp)
                if not h:
                    break
                found = set(re.findall(r'(?:purchaseNoticeNumber|regNumber)=(\d+)', h))
                for n in found:
                    nums[n] = {"num": n, "query": q}
                print(f"  {q} [{d_from[:4]}] стр{page}: +{len(found)} (всего {len(nums)})")
                if len(found) < 10:
                    break
                time.sleep(0.7)
            time.sleep(1)
    return nums

def parse_card(html_text: str, num: str) -> dict:
    """Извлечь из карточки закупки: название, НМЦК, цена/ед, объём."""
    clean = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', html_text, flags=re.S)
    clean = re.sub(r'<[^>]+>', '\n', clean)
    clean = html.unescape(clean)
    lines = [l.strip() for l in clean.split('\n') if l.strip()]
    out = {"num": num, "title": "", "nmck": None, "unit_price": None, "volume": None,
           "unit": "", "date": None, "customer": ""}

    # Наименование объекта закупки → следующая непустая строка
    for i, l in enumerate(lines):
        if re.search(r'наименование объекта закупки', l, re.I) and i + 1 < len(lines):
            out["title"] = lines[i+1][:200]
            break
        if re.search(r'объект закупки', l, re.I) and i + 1 < len(lines):
            out["title"] = lines[i+1][:200]
            break

    # НМЦК
    for i, l in enumerate(lines):
        if re.search(r'(начальная \(максимальная\) цена|начальная цена)', l, re.I) and i + 1 < len(lines):
            m = re.search(r'([\d][\d\s.,]*\d)', lines[i+1])
            if m:
                out["nmck"] = m.group(1).replace(' ', '').replace(',', '.')
                break

    # Цена за единицу + объём (табличная строка: код | тип | ед | цена/ед | кол-во | сумма)
    for i, l in enumerate(lines):
        if re.match(r'^\d+$', l) and i + 3 < len(lines):
            # паттерн: ... | Литр | 29020.83 | 16 | 464333.28
            if re.search(r'(литр|баллон|штук|кубическ)', lines[i+1], re.I):
                out["unit"] = lines[i+1]
                m = re.search(r'([\d][\d\s.,]*\d)', lines[i+2])
                if m:
                    out["unit_price"] = m.group(1).replace(' ', '').replace(',', '.')
                m2 = re.search(r'([\d][\d\s.,]*\d)', lines[i+3])
                if m2:
                    out["volume"] = m2.group(1).replace(' ', '').replace(',', '.')
                break

    # Дата (подведения итогов / размещения)
    dm = re.search(r'(\d{2}\.\d{2}\.\d{4})', html_text)
    out["date"] = dm.group(1) if dm else None
    return out

def main() -> None:
    print("Этап 1: сбор номеров закупок")
    nums = collect_numbers()
    print(f"Всего номеров: {len(nums)}")

    print("\nЭтап 2: открытие карточек")
    results = []
    for n, meta in nums.items():
        # 44-ФЗ: regNumber; 223-ФЗ: purchaseNoticeNumber + guid
        if n.startswith("3"):  # 223-ФЗ
            # найдём guid из поисковой страницы (сохранённой)
            guid = None
            for q in QUERIES:
                qq = q.replace(" ", "+")
                for page in range(1, 6):
                    tmp = f"/tmp/zak_ls_{abs(hash(q))%99999}_{page}.html"
                    if Path(tmp).exists():
                        h = open(tmp, encoding="utf-8", errors="ignore").read()
                        m = re.search(rf'purchaseNoticeNumber={n}&(?:amp;)?purchaseNoticeGuid=([0-9a-f\-]{{36}})', h)
                        if not m:
                            m = re.search(rf'purchaseNoticeGuid=([0-9a-f\-]{{36}}).{{0,400}}purchaseNoticeNumber={n}', h, re.S)
                        if m:
                            guid = m.group(1)
                            break
                if guid:
                    break
            if guid:
                url = f"{BASE}/epz/order/notice/notice223/printForm/view.html?purchaseNoticeNumber={n}&purchaseNoticeGuid={guid}"
            else:
                # попробуем без guid
                url = f"{BASE}/epz/order/notice/notice223/printForm/view.html?purchaseNoticeNumber={n}"
        else:
            url = f"{BASE}/epz/order/notice/printForm/view.html?regNumber={n}"

        tmp = f"/tmp/zak_card_{n}.html"
        h = fetch(url, tmp)
        if not h:
            print(f"  {n}: пусто")
            continue
        card = parse_card(h, n)
        card.update(meta)
        # фильтр: только лазерные газы
        t = (card["title"] + " " + n).lower()
        if re.search(r'(krf|arf|xecl|эксимер|лазер|криптон|неон|фтор)', t):
            results.append(card)
            print(f"  {n} | {card['date']} | НМЦК {card['nmck']} | {card['title'][:70]}")
        time.sleep(0.7)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"source": "zakupki.gov.ru", "count": len(results), "items": results},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nСохранено релевантных: {len(results)} → {OUT}")

if __name__ == "__main__":
    main()
