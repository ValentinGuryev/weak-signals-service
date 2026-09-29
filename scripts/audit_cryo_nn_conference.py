"""Local lexical audit, NOT a count of computing talks. No network access.
Run: .venv/bin/python scripts/audit_cryo_nn_conference.py
Input PDFs are never modified. Derived JSON/CSV/plot are overwritten on rerun.
"""
from __future__ import annotations

import csv
import hashlib
import json
import logging
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/raw/conferences/Наноконференция_Новгород'
SIGNALS = ROOT / 'case_studies/cryo_sc_computing/signals'
OUTPUT = ROOT / 'data/raw/conferences/cases/087_cryo_nn_lexical_audit.json'
TOKEN = re.compile(r'[A-Za-zА-Яа-яЁё]+')
TERMS = {
    'sc': r'сверхпровод.*', 'josephson': r'джозефсон.*',
    'cryo': r'криоген.*', 'sfq': r'(?:sfq|rsfq|esfq|ersfq)',
    'cryotron': r'криотрон.*', 'quantum': r'квантов.*',
}


def analyze(text: str) -> dict:
    counts = Counter(TOKEN.findall(text.lower()))
    words = sum(counts.values())
    hits = {key: sum(n for t, n in counts.items() if re.fullmatch(pattern, t))
            for key, pattern in TERMS.items()}
    return {'words': words, 'hits': hits}


def main() -> None:
    # Token boundaries and nested SFQ names must not produce duplicate hits.
    test = analyze('RSFQ SFQ eSFQ ERSFQ XS FQ криогенный криоген криотрон')
    assert test['hits']['sfq'] == 4 and test['hits']['cryo'] == 2
    assert test['hits']['cryotron'] == 1
    files = []
    cache = ROOT / 'data/cache/cryo_nn_lexical'
    cache.mkdir(parents=True, exist_ok=True)
    inputs = sorted(SOURCE.glob('*.pdf'))
    if not inputs:
        raise FileNotFoundError(SOURCE)
    for pdf in inputs:
        with pdf.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        record = {'file': str(pdf.relative_to(ROOT)), 'sha256': digest,
                  'year': int(pdf.name[:4]), 'status': 'error'}
        target = cache / f'{pdf.stem}_{digest[:16]}.txt'
        try:
            # Always re-extract: never reuse a partial file from an earlier failure.
            process = subprocess.run(['pdftotext', '-enc', 'UTF-8', str(pdf), str(target)],
                                     capture_output=True, text=True, timeout=180)
            record['returncode'] = process.returncode
            record['stderr'] = process.stderr
            if process.returncode == 0 and target.exists():
                text = target.read_text(encoding='utf-8')
                record.update(analyze(text))
                pages = text.split('\f')
                if pages and not pages[-1].strip():
                    pages.pop()
                record['extracted_pages'] = len(pages)
                record['pages_under_100_letters'] = sum(
                    len(re.findall(r'[A-Za-zА-Яа-яЁё]', p)) < 100 for p in pages)
                record['status'] = 'ok' if record['words'] else 'empty'
        except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
            record['stderr'] = str(exc)
        if record['status'] != 'ok':
            logging.warning('%s: %s', pdf.name, record['status'])
        files.append(record)
    years = []
    for year in range(min(f['year'] for f in files), max(f['year'] for f in files) + 1):
        present = [f for f in files if f['year'] == year]
        good = [f for f in present if f['status'] == 'ok']
        words = sum(f['words'] for f in good)
        row = {'year': year, 'files_present': len(present), 'files_read': len(good),
               'words': words or None}
        for key in TERMS:
            hits = sum(f['hits'][key] for f in good) if words else None
            row[key + '_hits'] = hits
            row[key + '_per_1000'] = 1000 * hits / words if words else None
        years.append(row)
    data = {'created_utc': datetime.now(timezone.utc).isoformat(),
            'tool': subprocess.run(['pdftotext', '-v'], capture_output=True, text=True).stderr.strip(),
            'script': str(Path(__file__).relative_to(ROOT)),
            'token_regex': TOKEN.pattern, 'term_fullmatch_regex': TERMS,
            'scope': 'Full extracted text incl. TOC/references/sponsors; NOT unique talks.',
            'files': files, 'years': years}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    table = SIGNALS / 'conference_lexical_audit.csv'
    with table.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(years[0]))
        writer.writeheader()
        writer.writerows(years)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    for ax, keys in zip(axes, [('cryo', 'sfq', 'cryotron'), ('sc', 'quantum')]):
        for key in keys:
            values = [r[key + '_per_1000'] if r[key + '_per_1000'] is not None else float('nan')
                      for r in years]
            ax.plot([r['year'] for r in years], values, marker='.', label=key)
        for year in [2009, 2014]:
            ax.axvspan(year - .3, year + .3, color='orange', alpha=.2)
        ax.axvspan(2016, 2019, color='gray', alpha=.15)
        ax.axvline(2024.5, color='gray', linestyle='--')
        ax.set_ylabel('Occurrences / 1,000 tokens')
        ax.grid(alpha=.2)
        ax.legend(loc='upper left')
    axes[0].set_title('Lexical audit only — not computing talks or adoption')
    axes[1].set_xticks(range(2005, 2027, 2))
    fig.text(.02, .015, 'Orange: failed volume; grey: no usable year. Dashed: format change to abstracts (2025).', fontsize=9)
    fig.tight_layout(rect=(0, .045, 1, 1))
    plot = SIGNALS / 'plots/conference_lexical_audit.png'
    plot.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot, dpi=140)
    plt.close(fig)
    assert sum(r['words'] or 0 for r in years) == sum(f['words'] for f in files if f['status'] == 'ok')
    logging.info('Files %s, usable %s; wrote JSON, CSV, plot. Assertions passed.', len(files),
                 sum(f['status'] == 'ok' for f in files))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    main()
