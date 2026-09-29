# -*- coding: utf-8 -*-
"""H32 (Kastrin 2020): сдвиг методологии области co-occurrence -> semantic по корпусу SRF/Nb3Sn.
Внешний позитивный контроль для S2. Локальные данные, 0 API. ASCII-only.
"""
import json
import os
import re

ROOT = '/home/user/projects/Hackathon'
CORPUS = os.path.join(ROOT, 'data/raw/openalex/srf_corpus.json')
OUT = os.path.join(ROOT, 'results/h32_stats.json')

PERIODS = [
    ('P1 <=1999', 0, 1999),
    ('P2 2000-09', 2000, 2009),
    ('P3 2010-14', 2010, 2014),
    ('P4 2015-19', 2015, 2019),
    ('P5 2020-26', 2020, 2026),
]

FAMILIES = {
    'old_cooc': ['co-occurrence', 'cooccurrence', 'co-word', 'coword',
                 'co-citation', 'cocitation', 'bibliographic coupling',
                 'association rule', 'dictionary based', 'thesaurus'],
    'semantic': ['semantic', 'semantics', 'embedding', 'word2vec',
                 'sentence-transformer', 'semantic similarity',
                 'topic model', 'topic modeling', 'topic modelling'],
    'llm': ['large language model', 'llm', 'transformer', 'bert',
            'gpt', 'chatgpt', 'deep learning', 'neural network',
            'machine learning'],
}


def make_regex(words):
    parts = [re.escape(w) for w in words]
    return re.compile(r'\b(?:' + '|'.join(parts) + r')(?:s)?\b', re.IGNORECASE)


def load_works(path):
    d = json.load(open(path))
    works = d.get('works')
    if not works:
        for k, v in d.items():
            if isinstance(v, list) and v and isinstance(v[0], dict) and 'title' in v[0]:
                works = v
                break
    return works or []


def main():
    works = load_works(CORPUS)
    regs = {k: make_regex(v) for k, v in FAMILIES.items()}
    rows = []
    for label, y0, y1 in PERIODS:
        pool = [w for w in works
                if isinstance(w.get('year'), int) and y0 <= w['year'] <= y1
                and w.get('abstract')]
        n_total = sum(1 for w in works if isinstance(w.get('year'), int) and y0 <= w['year'] <= y1)
        n_abs = len(pool)
        words_total = 0
        counts = {k: 0 for k in FAMILIES}
        docs_hit = {k: 0 for k in FAMILIES}
        for w in pool:
            ab = w['abstract']
            if not isinstance(ab, str):
                continue
            tokens = ab.lower().split()
            words_total += len(tokens)
            text = ' '.join(tokens)
            for k, rx in regs.items():
                m = rx.findall(text)
                counts[k] += len(m)
                if m:
                    docs_hit[k] += 1
        row = {'period': label, 'n_total': n_total, 'n_abs': n_abs,
               'words': words_total}
        for k in FAMILIES:
            row[k + '_raw'] = counts[k]
            row[k + '_per1kabs'] = round(1000.0 * counts[k] / n_abs, 2) if n_abs else 0.0
            row[k + '_per1kwords'] = round(1000.0 * counts[k] / words_total, 3) if words_total else 0.0
            row[k + '_docs'] = docs_hit[k]
        old = row['old_cooc_raw']
        sem = row['semantic_raw']
        row['sem_share_of_oldplus'] = round(sem / (old + sem), 3) if (old + sem) else None
        rows.append(row)
    hdr = ['period', 'n_total', 'n_abs', 'words',
           'old_cooc_raw', 'old_cooc_per1kabs',
           'semantic_raw', 'semantic_per1kabs',
           'llm_raw', 'llm_per1kabs',
           'sem_share_of_oldplus', 'semantic_docs', 'old_cooc_docs']
    print(';'.join(hdr))
    for r in rows:
        print(';'.join(str(r[k]) for k in hdr))
    json.dump({'rows': rows}, open(OUT, 'w'), indent=1)
    print('JSON ->', OUT)


if __name__ == '__main__':
    main()