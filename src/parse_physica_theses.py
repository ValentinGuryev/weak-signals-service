#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Парсер сборников тезисов конференции ФизикА.СПб (2012-2025) - v4.

Форматы:
  A) Типографские PDF: секции-колонтитулы; заголовки тезисов крупным шрифтом.
  B) HTML-печать (2016b, 2017): текст потоком, секции одиночными строками,
     тезисы: Заголовок -> Авторы (Фамилия И.О.) -> аффилиация -> e-mail -> текст.

Выход: results/conference_analysis/PhysicA/physica_theses.csv
"""
import pymupdf, re, csv, os, logging
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(message)s')
DATA = 'data/raw/conferences/PhysicA'
OUTDIR = 'results/conference_analysis/PhysicA'
os.makedirs(OUTDIR, exist_ok=True)

KNOWN_SECTIONS = [
    'Астрономия и астрофизика','Астрономия, астрофизика и физика плазмы','Астрофизика',
    'Атомная физика и физика элементарных частиц','Атомная физика','Физика элементарных частиц',
    'Биофизика','Другие вопросы физики','Матфизика и численные методы','Оптика и спектроскопия',
    'Оптоэлектронные приборы','Поверхностные явления','Поверхность',
    'Приборы и материалы ТГц и СВЧ диапазона','Приборы и материалы ТГц и СВЧ',
    'Примеси и дефекты в твердом теле','Примеси и дефекты в полупроводниках',
    'Физика и технология преобразования энергии','Физика квантовых структур',
    'Физика плазмы, гидро- и аэродинамика','Физика плазмы','Гидро- и аэродинамика',
    'Аэро-, гидро-динамика','Физика ферроиков','Физика ферроиков и диэлектриков',
    'Наноструктурированные и тонкопленочные материалы',
    'Физика твердого тела и физика полупроводников',
    'Современные проблемы гидро и аэродинамики','Численные методы в физике',
    'Полупроводниковые лазеры','Полупроводниковые приборы и структуры',
    'Актуальные вопросы физики твердого тела и физики полупроводников',
    'Современная космология','Физика лазеров','POSTDEADLINE',
    'Nano-structured and thin film materials','Optics and Spectroscopy',
    'Astronomy and Astrophysics','Biophysics','Other problems of physics',
    'Physics of quantum structures','Solid state physics','Nuclear and elementary particle physics',
    'Plasma physics, hydrodynamics and aerodynamics','Surface phenomena','Mathematical physics',
    'Physics of ferroics','Physics and technology of energy conversion',
    'Impurities and defects in solids','Optoelectronic devices','Atomic physics',
    'Instruments and materials of THz and microwave range','International conference',
]
SECT_NORM = {re.sub(r'\s+',' ', s).strip().lower(): s for s in KNOWN_SECTIONS}
def norm(s): return re.sub(r'\s+',' ', s).strip().lower()
def canon_section(s):
    n = norm(s)
    if n in SECT_NORM: return SECT_NORM[n]
    for k,v in SECT_NORM.items():
        if n==k or (len(n)>8 and (n.startswith(k) or k.startswith(n))):
            return v
    return None

HEADER = {'2012':18.0,'2013':14.0,'2014':15.0,'2015':14.0,'2016a':12.0,'2018':12.0,
          '2019':12.0,'2020':14.0,'2021':14.0,'2022':14.0,'2023':13.9,'2024':14.0,'2025':14.0}
TEXT = {'2012':12.0,'2013':11.0,'2014':14.0,'2015':10.0,'2016a':10.0,'2018':10.0,
        '2019':10.0,'2020':10.0,'2021':10.0,'2022':10.0,'2023':10.0,'2024':10.0,'2025':10.0}

def parse_print_pdf(yr, fname):
    doc = pymupdf.open(f'{DATA}/{fname}')
    # карта секций по документу
    sec_pages = Counter()
    for pno in range(len(doc)):
        t = doc[pno].get_text()
        for l in [x.strip() for x in t.split('\n') if x.strip()][:5]:
            c = canon_section(l)
            if c:
                sec_pages[c]+=1; break
    toc_start = len(doc)
    for pno in range(len(doc)):
        if re.search(r'^\s*Содержание\s*$', doc[pno].get_text(), re.M):
            toc_start = pno; break
    hsize = HEADER[yr]; tsize = TEXT[yr]
    # порог: заголовок должен быть заметно больше текста
    hmin = hsize - 0.4  # строго
    theses=[]; cur=None; cur_sec=None
    for pno in range(toc_start):
        d = doc[pno].get_text('dict')
        lines=[]
        for b in d['blocks']:
            for l in b.get('lines',[]):
                txt=''.join(s['text'] for s in l['spans']).strip()
                if not txt: continue
                sz=round(max(s['size'] for s in l['spans']),1)
                bold=any('Bold' in s['font'] or 'bold' in s['font'] for s in l['spans'])
                lines.append([l['bbox'][1], sz, bold, txt])
        lines.sort(key=lambda x:x[0])
        # секция: первая строка-известная секция
        for idx in range(min(4,len(lines))):
            c = canon_section(lines[idx][3])
            if c and lines[idx][3] != (cur['title'] if cur else None):
                cur_sec = c
                break
        i=0
        while i < len(lines):
            y,sz,bold,txt = lines[i]
            # секция в потоке (колонтитул или заголовок секции)
            c = canon_section(txt)
            if c and (sz>=16 or i<2) and txt != (cur['title'] if cur else ''):
                cur_sec = c
                i+=1; continue
            if re.match(r'^\d+$', txt.strip()) or txt.strip() in ('Содержание','References','Литература'):
                i+=1; continue
            # заголовок тезиса: размер >= hmin (строго больше текста)
            is_head = sz >= hmin
            # исключить: секции, служебное, Список литературы (bold), номера
            skip = (canon_section(txt) or txt.strip() in ('Список литературы','Литература','References') 
                    or re.match(r'^[\d\s\.,\-—]+$', txt) or len(txt)<=2)
            if is_head and not skip:
                if cur is not None and len(cur['text'])>0:
                    theses.append(cur)
                cur={'year':yr,'file':fname,'section':cur_sec,'title':txt,'authors':'','email':'','text':'','lang':''}
                # многострочный заголовок (следующие строки с sz>=hmin)
                j=i+1
                while j<len(lines) and lines[j][1] >= hmin and not canon_section(lines[j][3]) and not re.match(r'^[\d\s\.,\-—]+$', lines[j][3]):
                    cur['title'] += ' ' + lines[j][3]
                    j+=1
                i=j; continue
            # авторы
            if cur is not None:
                if not cur['authors'] and sz <= tsize+0.6 and sz >= tsize-3.5 and re.search(r'[А-ЯЁA-Z]\.', txt) and not re.search(r'почта|mail|@',txt,re.I) and len(txt)<115 and not canon_section(txt):
                    cur['authors']=txt
                elif re.search(r'(e-?mail|Эл\.?\s*почта|Электронная почта)\s*[:.]', txt, re.I):
                    cur['email']=txt
                elif not canon_section(txt) and not re.match(r'^\d+$', txt.strip()):
                    cur['text'] += txt + ' '
            i+=1
    if cur is not None and len(cur['text'])>0:
        theses.append(cur)
    doc.close()
    return theses

def parse_html_pdf(yr, fname):
    doc = pymupdf.open(f'{DATA}/{fname}')
    text = '\n'.join(doc[p].get_text() for p in range(len(doc)))
    doc.close()
    lines=[]
    for l in text.split('\n'):
        l = re.sub(r'[ \t\xa0]+',' ', l).strip()
        if re.match(r'^\d{2}\.\d{2}\.\d{4}, \d{2}:\d{2}$', l): continue
        if re.match(r'^physica\.spb\.ru', l): continue
        if re.match(r'^\d+/\d+$', l): continue
        if l.startswith('Тезисы конференции ФизикА.СПб'): continue
        if re.match(r'^ББК|^Ф 50|^ISBN|^УДК', l): continue
        lines.append(l)
    theses=[]; cur=None; cur_sec=None
    i=0
    def is_authors(l):
        if len(l)>115 or len(l)<8: return False
        if re.search(r'почта|mail|@', l, re.I): return False
        # "Фамилия И.О.1[, Фамилия2]" - начинается с заглавной, содержит инициалы с точкой
        if re.match(r'^[А-ЯЁ][а-яё]+(\s+[А-ЯЁ][а-яё]+)*\s+[А-ЯЁ]\.\s?[А-ЯЁ]?\.?\s*\d*', l): return True
        if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s+[A-Z]\.\s?[A-Z]?\.?\s*\d*', l): return True
        return False
    while i < len(lines):
        l = lines[i]
        if not l: i+=1; continue
        c = canon_section(l)
        if c and len(l)<50:
            cur_sec = c; i+=1; continue
        if is_authors(l):
            if cur is None:
                # заголовок должен был идти раньше - берём предыдущую строку как заголовок?
                # такого быть не должно; начнём с пустым title
                cur={'year':yr,'file':fname,'section':cur_sec,'title':'','authors':l,'email':'','text':'','lang':''}
            else:
                cur['authors']=l
            i+=1; continue
        if re.search(r'(e-?mail|Эл\.?\s*почта|Электронная почта)\s*[:.]', l, re.I) and cur is not None:
            cur['email']=l; i+=1; continue
        # заголовок тезиса = строка перед авторами. Эвристика: если cur пуст (нет авторов/текста)
        # и след. строка - авторы, то это заголовок.
        if cur is not None and not cur['authors'] and not cur['text']:
            # возможно это продолжение заголовка
            nxt = lines[i+1] if i+1<len(lines) else ''
            if is_authors(nxt) or re.search(r'(e-?mail|почта)', nxt, re.I):
                cur['title'] = (cur['title']+' ' if cur['title'] else '') + l
                i+=1; continue
            else:
                cur['title'] = (cur['title']+' ' if cur['title'] else '') + l
                i+=1; continue
        if cur is not None:
            # конец тезиса? если текст уже есть и это новый заголовок (след. строка - авторы)
            nxt = lines[i+1] if i+1<len(lines) else ''
            if cur['text'] and len(cur['text'])>200 and (is_authors(l) or canon_section(nxt) or is_authors(nxt)):
                # l - либо начало нового (заголовок), либо хвост старого. Проверим: если l похоже на заголовок
                # (короткое, без точки в конце, след строка авторы) - новый тезис
                if is_authors(nxt) and len(l)<140 and not l.endswith('.'):
                    theses.append(cur)
                    cur={'year':yr,'file':fname,'section':cur_sec,'title':l,'authors':'','email':'','text':'','lang':''}
                    i+=1; continue
            cur['text'] += l + ' '
        else:
            cur={'year':yr,'file':fname,'section':cur_sec,'title':l,'authors':'','email':'','text':'','lang':''}
        i+=1
    if cur is not None and len(cur['text'])>0:
        theses.append(cur)
    return theses

FILES = [
 ('2012','physica_spb2012_thesises.pdf','print'),('2013','physica_spb2013_thesises.pdf','print'),
 ('2014','978-5-7422-4602-2.pdf','print'),('2015','Physica2015Thesises.pdf','print'),
 ('2016a','2016-physica-theses_fin-4_1_isbn.pdf','print'),
 ('2016b','Тезисы поданные на конференцию ФизикА.СПб 2016.pdf','html'),
 ('2017','Тезисы конференции ФизикА.СПб 2017.pdf','html'),
 ('2018','2018-physica-thesises.pdf','print'),('2019','Tesises2019.pdf','print'),
 ('2020','thesises-2020.pdf','print'),('2021','physicaspb-tesises-2021.pdf','print'),
 ('2022','thesises-2022.pdf','print'),('2023','theses2023final.pdf','print'),
 ('2024','theses2024.pdf','print'),('2025','theses2025.pdf','print')]

def main():
    all_theses=[]
    for yr,f,fmt in FILES:
        th = parse_print_pdf(yr,f) if fmt=='print' else parse_html_pdf(yr,f)
        logging.info(f'{yr}: {len(th)} тезисов')
        for t in th:
            cyr=sum(1 for ch in (t['title']+t['text'])[:300] if '\u0400'<=ch<='\u04FF')
            lat=sum(1 for ch in (t['title']+t['text'])[:300] if ch.isascii() and ch.isalpha())
            t['lang'] = 'ru' if cyr>=lat else 'en'
        all_theses.extend(th)
    with open(f'{OUTDIR}/physica_theses.csv','w',newline='',encoding='utf-8') as fp:
        w=csv.writer(fp)
        w.writerow(['year','file','section','title','authors','email','text','lang'])
        for t in all_theses:
            w.writerow([t['year'],t['file'],t['section'],t['title'],t['authors'],t['email'],t['text'],t['lang']])
    logging.info(f'ИТОГО: {len(all_theses)} -> {OUTDIR}/physica_theses.csv')
    by=Counter(t['year'] for t in all_theses)
    for y in sorted(by): logging.info(f'  {y}: {by[y]}')

if __name__=='__main__':
    main()
