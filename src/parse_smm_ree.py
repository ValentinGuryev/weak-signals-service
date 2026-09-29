#!/usr/bin/env python3
"""Парсер цен оксидов РЗЭ из снапшотов SMM (Wayback Machine), v5.

Форматы:
- 2014-2016 smm.cn/metals/rare_earth (GBK): таблица ячеек
  ['氧化铕', 'Eu2O3/TREO 99.95-99.99%', '4200-4500']  <- цена в 3-й ячейке
  ['氧化钇', 'Y2O3/TREO 99.995-99.999%', '5.5万-6万']
  таблица годовых средних: ['氧化钇', '57857.14', '-6.75%']
- 2016-2017 hq.smm.cn/xt: строки "氧化铕 370-390 380 0 全国"
- 2019-2021 таблицы с единицей: ['氧化铕', '...99.95-99.99%', '195-215', '205', '0', '元/千克', '09-22']
- 2022-2026: SPA (пропуск) + страницы-заглушки с логином («未登录»), где цен нет

Изменения v4 → v5 (исправление артефактов сортов):
1. Сорта: различаем «氧化镧» (обычный) и «高纯氧化镧» (высокочистый). Поле `grade`.
   Раньше find_price брал ПЕРВУЮ цену из ячеек — для «高纯» строк захватывалась цена обычного,
   а для обычных могла попасть цена высокочистого (когда обычная < 5000 и отбрасывалась valid()).
2. Мусор 2023-2026: страницы SMM за логином («未登录», цены скрыты). Валидные цены
   (2014-2021, 2024c) — это диапазоны вида "3800-4200" или "17000-19000". Парсер больше
   НЕ принимает одиночные числа 4-17 юаней/кг (это артефакт: «涨跌»/другие колонки).
3. valid(): обычный La может стоить 3000-5000 юаней/т (2024) — не отбрасывать.
4. Ключ записи включает grade — больше не сливаем сорта в один элемент.
"""
import re, html, glob, json
from pathlib import Path

ROOT = Path("/home/user/projects/Hackathon")
SNAP = ROOT / "data" / "raw" / "market" / "smm_snapshots"
OUT = ROOT / "data" / "raw" / "market" / "ree_prices" / "smm_ree_all.json"

REES_CN = {
    '氧化镧': ('La2O3', 'La'), '氧化铈': ('CeO2', 'Ce'), '氧化镨': ('Pr6O11', 'Pr'),
    '氧化钕': ('Nd2O3', 'Nd'), '氧化钐': ('Sm2O3', 'Sm'), '氧化铕': ('Eu2O3', 'Eu'),
    '氧化钆': ('Gd2O3', 'Gd'), '氧化铽': ('Tb4O7', 'Tb'), '氧化镝': ('Dy2O3', 'Dy'),
    '氧化钬': ('Ho2O3', 'Ho'), '氧化铒': ('Er2O3', 'Er'), '氧化铥': ('Tm2O3', 'Tm'),
    '氧化镱': ('Yb2O3', 'Yb'), '氧化镥': ('Lu2O3', 'Lu'), '氧化钇': ('Y2O3', 'Y'),
}

def decode(raw: bytes) -> str:
    for enc in ('utf-8', 'gbk', 'gb18030'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode('utf-8', errors='ignore')

def to_num(s: str) -> float:
    s = s.replace(',', '').replace(' ', '')
    if s.endswith('万'):
        return float(s[:-1]) * 10000
    return float(s)

# жёсткая карта единиц по элементу (проверено по 2014-2021 снапшотам)
UNIT_BY_EL = {
    'La': 'yuan/tonne', 'Ce': 'yuan/tonne', 'Pr': 'yuan/tonne', 'Nd': 'yuan/tonne',
    'Sm': 'yuan/tonne', 'Gd': 'yuan/tonne', 'Er': 'yuan/tonne', 'Y': 'yuan/tonne',
    'Ho': 'yuan/tonne',
    'Eu': 'yuan/kg', 'Tb': 'yuan/kg', 'Dy': 'yuan/kg',
    'Tm': 'yuan/kg', 'Yb': 'yuan/kg', 'Lu': 'yuan/kg',
}

def unit_for(en: str, avg: float) -> str:
    u = UNIT_BY_EL.get(en)
    if u:
        return u
    return 'yuan/kg' if avg < 20000 else 'yuan/tonne'

# Реальные минимумы цен (юань/т, обычный сорт): La падал до 4000 (2024), Ce до 7000 (2024)
# Eu/Tb/Dy — в юань/кг, минимумы единичные (Eu 24, Tb 395, Dy 183).
MIN_BY_EL_TONNE = {
    'La': 3000, 'Ce': 5000, 'Pr': 30000, 'Nd': 30000, 'Sm': 5000,
    'Gd': 5000, 'Er': 10000, 'Y': 1500, 'Ho': 20000, 'Yb': 30000,
}
MIN_BY_EL_KG = {'Eu': 10, 'Tb': 100, 'Dy': 50, 'Tm': 50, 'Yb': 300, 'Lu': 300}

def valid(avg: float, unit: str, en: str) -> bool:
    if unit == 'yuan/kg':
        lo = MIN_BY_EL_KG.get(en, 10)
        return lo <= avg <= 20000
    lo = MIN_BY_EL_TONNE.get(en, 5000)
    return lo <= avg <= 5000000

def find_price(cells: list[str]) -> tuple | None:
    """Ищем цену: диапазон 'a-b' или 'a万-b万' в ячейках, исключая те, где есть '%'."""
    for c in cells:
        if '%' in c:
            continue
        pm = re.search(r'(\d[\d.,]*万?)\s*[-–—]\s*(\d[\d.,]*万?)(?:\s*元/(?:吨|千克|公斤))?', c)
        if pm:
            try:
                lo, hi = to_num(pm.group(1)), to_num(pm.group(2))
                return (lo, hi, (lo + hi) / 2)
            except ValueError:
                continue
    return None

def parse_file(fname: Path) -> list[dict]:
    raw = open(fname, 'rb').read()
    txt = decode(raw)
    results = []
    tables = re.findall(r'<table[^>]*>(.*?)</table>', txt, re.S)

    # Страницы за логином (2023-2026 SMM SPA): цены скрыты, есть только «未登录».
    # На таких страницах реальных цен НЕТ — не парсим их вообще (иначе мусор 4-17 юань/кг).
    login_blocked = '未登录' in txt and '价格' in txt

    def cell_text(c):
        return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html.unescape(c))).strip()

    def rows_of(t):
        out = []
        for r in re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S):
            cells = [cell_text(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)]
            cells = [c for c in cells if c]
            if cells:
                out.append(cells)
        return out

    # 1) Таблицы (spot)
    for t in tables:
        for cells in rows_of(t):
            if any('未登录' in c for c in cells):
                continue  # цена скрыта за логином
            for cn, (formula, en) in REES_CN.items():
                if cn not in cells[0]:
                    continue
                grade = 'high' if '高纯' in cells[0] else 'std'
                # единица
                unit = None
                for c in cells:
                    um = re.search(r'元/(吨|千克|公斤)', c)
                    if um:
                        unit = 'yuan/kg' if um.group(1) == '千克' else 'yuan/tonne'
                        break
                fp = find_price(cells[1:])  # после названия
                if not fp:
                    continue
                lo, hi, avg = fp
                if unit is None:
                    unit = unit_for(en, avg)
                if valid(avg, unit, en):
                    results.append({'element': en, 'formula': formula, 'grade': grade,
                                    'price_avg': round(avg, 2), 'price_lo': round(lo, 2), 'price_hi': round(hi, 2),
                                    'unit': unit, 'type': 'spot'})
                break

    # 2) Годовые средние: ['氧化钇', '57857.14', '-6.75%'] — 2-я ячейка число
    for t in tables:
        for cells in rows_of(t):
            if len(cells) < 2 or any('未登录' in c for c in cells):
                continue
            for cn, (formula, en) in REES_CN.items():
                if cn in cells[0]:
                    grade = 'high' if '高纯' in cells[0] else 'std'
                    pm = re.search(r'(\d[\d.,]*万?)', cells[1])
                    if pm and '%' not in cells[1]:
                        try:
                            avg = to_num(pm.group(1))
                        except ValueError:
                            continue
                        if not any(r2['element'] == en and r2['price_avg'] == round(avg, 2) and r2['grade'] == grade
                                   for r2 in results):
                            unit = unit_for(en, avg)
                            if valid(avg, unit, en):
                                results.append({'element': en, 'formula': formula, 'grade': grade,
                                                'price_avg': round(avg, 2), 'price_lo': round(avg, 2),
                                                'price_hi': round(avg, 2), 'unit': unit, 'type': 'yearly_avg'})
                    break

    # 3) Текстовый формат: "氧化铕 370-390 380 0 全国"
    if not results and not login_blocked:
        lines = [l.strip() for l in re.sub(r'<[^>]+>', '\n', txt).split('\n') if l.strip()]
        for i, l in enumerate(lines):
            for cn, (formula, en) in REES_CN.items():
                if cn in l:
                    grade = 'high' if '高纯' in l else 'std'
                    pm = re.search(r'(\d[\d.,]*万?)\s*[-–—]\s*(\d[\d.,]*万?)', l)
                    if pm:
                        try:
                            lo, hi = to_num(pm.group(1)), to_num(pm.group(2))
                            avg = (lo + hi) / 2
                        except ValueError:
                            continue
                        unit = unit_for(en, avg)
                        if valid(avg, unit, en):
                            results.append({'element': en, 'formula': formula, 'grade': grade,
                                            'price_avg': round(avg,2), 'price_lo': round(lo,2), 'price_hi': round(hi,2),
                                            'unit': unit, 'type': 'spot'})
                    break
    return results

all_data = {}
for f in sorted(SNAP.glob('*.html')):
    label = f.stem
    year = int(label[:4])
    res = parse_file(f)
    if res:
        seen = set()
        uniq = []
        for r in res:
            key = (r['element'], r['type'], r['grade'], round(r['price_avg'], 1))
            if key in seen:
                continue
            seen.add(key)
            uniq.append(r)
        all_data[label] = {'year': year, 'items': uniq}
        g = lambda r: f"{r['element']}={r['price_avg']:.0f}{'kg' if r['unit']=='yuan/kg' else 't'}{'H' if r['grade']=='high' else ''}{'*' if r['type']=='yearly_avg' else ''}"
        print(f"{label}: {len(uniq)} | " + ", ".join(g(r) for r in uniq[:12]))

OUT.write_text(json.dumps({"source": "SMM via Wayback", "snapshots": all_data},
                          ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nСохранено → {OUT}")
