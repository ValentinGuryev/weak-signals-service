#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Очистка и унификация таблицы тезисов PhysicA."""
import pandas as pd, re, os

OUTDIR = 'results/conference_analysis/PhysicA'
df = pd.read_csv(f'{OUTDIR}/physica_theses.csv', dtype=str).fillna('')

# 1) Удалить мусор (обложки, служебные страницы)
junk_pat = re.compile(r'Тезисы докладов|ФизикА|ББК|ISBN|международной конференции|международной молод|'
                      r'Российская молодежная|Организатор|Спонсор|Содержание|Сокращённ|Сокращенн|'
                      r'Заметки|ПРОГРАММА|программа|Октябрь|Санкт-Петербург.*\d|УДК', re.I)
# title мусорный, если короткий и похож на обложку
def is_junk(r):
    t = r['title'].strip()
    if junk_pat.search(t) and len(t) < 130:
        return True
    # секция из обложки, пустой текст
    if len(r['text']) < 100 and len(t) < 60 and not r['authors']:
        return True
    return False
before = len(df)
df = df[~df.apply(is_junk, axis=1)].copy()

# 2) Унификация секций: EN -> RU канон
sec_map = {
 'Nano-structured and thin film materials':'Наноструктурированные и тонкопленочные материалы',
 'Optics and Spectroscopy':'Оптика и спектроскопия',
 'Astronomy and Astrophysics':'Астрономия и астрофизика',
 'Biophysics':'Биофизика',
 'Other problems of physics':'Другие вопросы физики',
 'Physics of quantum structures':'Физика квантовых структур',
 'Nuclear and elementary particle physics':'Атомная физика и физика элементарных частиц',
 'Plasma physics, hydrodynamics and aerodynamics':'Физика плазмы, гидро- и аэродинамика',
 'Surface phenomena':'Поверхностные явления',
 'Mathematical physics':'Матфизика и численные методы',
 'Physics of ferroics':'Физика ферроиков',
 'Physics and technology of energy conversion':'Физика и технология преобразования энергии',
 'Impurities and defects in solids':'Примеси и дефекты в твердом теле',
 'Optoelectronic devices':'Оптоэлектронные приборы',
 'Atomic physics':'Атомная физика и физика элементарных частиц',
 'Instruments and materials of THz and microwave range':'Приборы и материалы ТГц и СВЧ диапазона',
 'Solid state physics':'Физика твердого тела и физика полупроводников',
 'Физика плазмы':'Физика плазмы, гидро- и аэродинамика',
 'Аэро-, гидро-динамика':'Физика плазмы, гидро- и аэродинамика',
 'Гидро- и аэродинамика':'Физика плазмы, гидро- и аэродинамика',
 'Физика ферроиков и диэлектриков':'Физика ферроиков',
 'Поверхность':'Поверхностные явления',
 'Примеси и дефекты в полупроводниках':'Примеси и дефекты в твердом теле',
 'Современная космология':'Астрономия и астрофизика',
 'Современные проблемы гидро и аэродинамики':'Физика плазмы, гидро- и аэродинамика',
}
def norm_section(s):
    s = s.strip()
    if s in sec_map: return sec_map[s]
    # POSTDEADLINE оставить как есть (это доп. сессии)
    return s
df['section'] = df['section'].apply(norm_section)
# убрать пустые секции, заменить на 'Не указана'
df['section'] = df['section'].replace('', 'Не указана')

# 3) Почистить поля
df['text'] = df['text'].str.replace(r'\s+', ' ', regex=True).str.strip()
df['title'] = df['title'].str.replace(r'\s+', ' ', regex=True).str.strip()
df['authors'] = df['authors'].str.replace(r'\s+', ' ', regex=True).str.strip()
# 2016a/2016b -> 2016 (два файла одной конференции)
df['year'] = df['year'].str.replace(r'[ab]','',regex=True).astype(int)

# 4) Дубликаты (один доклад в RU и EN версиях)? Дедuп по нормализованному title+year
df['title_key'] = df['title'].str.lower().str.replace(r'[^a-zа-яё0-9]','',regex=True)
# оставляем первый из дублей (RU предпочтительно)
df = df.sort_values(['year','title_key','lang']).drop_duplicates(subset=['year','title_key'], keep='first')
df = df.drop(columns=['title_key']).reset_index(drop=True)

df.to_csv(f'{OUTDIR}/physica_theses_clean.csv', index=False, encoding='utf-8')
print(f'Было {before}, стало {len(df)}')
print('\nСекции после унификации:')
print(df['section'].value_counts().head(20).to_string())
print('\nПо годам:')
print(df.groupby('year').size().to_string())
