# -*- coding: utf-8 -*-
"""H26 (4sigma anomalies, Mints 2024) + H12 (rare + acceleration, Menning 2026).
Local canonical series, window <=2018, no look-ahead. No API.
"""
import json
import math
import os

ROOT = '/home/user/projects/Hackathon'
SER = os.path.join(ROOT, 'results/ESCORE_RECALC_series.json')
SMES = os.path.join(ROOT, 'data/raw/openalex/smes_vs_bess_counts.json')
OUT = os.path.join(ROOT, 'results/h26_h12_stats.json')

LABEL = {
    '003_flux_pump': 1, '003_joint_control': 0, '004_ni_coils': 1,
    '005_smes': 0, '002_rce_dr_sunam': 0, '007_jtwpa': 2,
    '001_ibad_mgo': 1, '006_snspd': 1, '008_sc_aircraft_motors': 0,
}
ORDER = ['003_flux_pump', '003_joint_control', '004_ni_coils', '005_smes',
         '002_rce_dr_sunam', '007_jtwpa', '001_ibad_mgo', '006_snspd',
         '008_sc_aircraft_motors']


def load_series(path):
    raw = json.load(open(path))
    cont = raw.get('case', raw)
    out = {}
    for cid, blob in cont.items():
        if not isinstance(blob, dict):
            continue
        yr = blob.get('year')
        if not isinstance(yr, dict):
            continue
        out[cid] = {int(y): int(n) for y, n in yr.items()}
    return out


def win_upto(serie, end):
    return {y: n for y, n in serie.items() if y <= end}


def baseline(win, zthr=2.0):
    vals = list(win.values())
    mu = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - mu) ** 2 for v in vals) / len(vals))
    for _ in range(10):
        keep = []
        for v in vals:
            if sd > 0 and abs(v - mu) / sd < zthr:
                keep.append(v)
        if not keep:
            keep = vals[:]
        mu2 = sum(keep) / len(keep)
        sd2 = math.sqrt(sum((v - mu2) ** 2 for v in keep) / len(keep))
        if sd2 == 0:
            break
        mu = mu2
        sd = sd2
    return mu, sd


def signature(win, mu, sd):
    zs = {}
    for y, n in win.items():
        if sd > 0:
            zs[y] = (n - mu) / sd
        else:
            zs[y] = 0.0
    zmax = max(zs.values())
    ge3 = [y for y, z in zs.items() if z >= 3.0]
    ge4 = [y for y, z in zs.items() if z >= 4.0]
    best = 0
    run = 0
    prev = None
    for y in sorted(win):
        if zs[y] >= 3.0:
            if prev is not None and y == prev + 1:
                run += 1
            else:
                run = 1
            if run > best:
                best = run
        else:
            run = 0
        prev = y
    peak = max(win, key=win.get)
    return {
        'zmax': round(zmax, 2),
        'n_ge3': len(ge3),
        'n_ge4': len(ge4),
        'run3': best,
        'first_ge3': ge3[0] if ge3 else None,
        'peak': peak,
    }


def w3w2(serie):
    def span(a, b):
        return sum(serie.get(y, 0) for y in range(a, b + 1))
    w2 = span(2017, 2019)
    w3 = span(2020, 2022)
    g = None
    denom = span(2014, 2015)
    num = span(2016, 2018)
    if denom:
        g = round(num / denom, 2)
    elif num:
        g = 1.0
    return {'w3w2': round(w3 / w2, 2) if w2 else None, 'g': g}


def menning(win):
    n1718 = sum(win.get(y, 0) for y in (2017, 2018))
    n1516 = sum(win.get(y, 0) for y in (2015, 2016))
    n1318 = sum(win.get(y, 0) for y in range(2013, 2019))
    level = round(sum(win.get(y, 0) for y in (2016, 2017, 2018)) / 3.0, 1)
    return {
        'level': level,
        'accel': round(n1718 / n1516 - 1.0, 2) if n1516 else None,
        'recency': round(n1718 / n1318, 2) if n1318 else None,
    }


def shares(class_counts, end=2018):
    norm = {k: {int(y): v for y, v in d.items()} for k, d in class_counts.items()}
    years = sorted({y for d in norm.values() for y in d if y <= end})
    rows = {}
    for y in years:
        tot = sum(d.get(y, 0) for d in norm.values())
        rows[y] = {k: round(d.get(y, 0) / tot, 3) if tot else 0.0
                   for k, d in norm.items()}
    return rows


def main():
    series = load_series(SER)
    rows = []
    for cid in ORDER:
        if cid not in series:
            continue
        win = win_upto(series[cid], 2018)
        mu, sd = baseline(win)
        sg = signature(win, mu, sd)
        mn = menning(win)
        ww = w3w2(series[cid])
        row = {'case': cid, 'label': LABEL[cid]}
        for d in (sg, ww, mn):
            for k, v in d.items():
                row[k] = v
        rows.append(row)
    hdr = ['case', 'label', 'zmax', 'n_ge3', 'n_ge4', 'run3', 'first_ge3',
           'peak', 'w3w2', 'g', 'level', 'accel', 'recency']
    print(';'.join(hdr))
    for r in rows:
        print(';'.join(str(r[k]) for k in hdr))
    sm = json.load(open(SMES))
    sh = shares(sm['counts'])
    print('=== CLASS SHARES (storage, <=2018) ===')
    for y in sorted(sh):
        bits = [str(y)]
        for k in ['SMES', 'BESS', 'Li-ion', 'Supercap']:
            bits.append('{}={:.3f}'.format(k, sh[y][k]))
        print(' '.join(bits))
    payload = {'rows': rows,
               'class_shares': {str(y): sh[y] for y in sorted(sh)}}
    json.dump(payload, open(OUT, 'w'), indent=1)
    print('JSON ->', OUT)


if __name__ == '__main__':
    main()