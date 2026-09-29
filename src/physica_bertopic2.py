#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BERTopic: обучение + сокращение до ~30 тем + сохранение (v2)."""
import pandas as pd, numpy as np, os, pickle, logging, json
logging.basicConfig(level=logging.INFO, format='%(message)s')
OUT='results/conference_analysis/PhysicA'
df = pd.read_csv(f'{OUT}/physica_theses_prepared.csv', dtype=str).fillna('')
docs = [(r['title'] + '. ' + r['text_clean'])[:400] for _,r in df.iterrows()]
emb = np.load(f'{OUT}/embeddings.npy')
print('Док-в:', len(docs), '| эмбеддинги:', emb.shape)

from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
hdbscan_model = HDBSCAN(min_cluster_size=12, min_samples=5, metric='euclidean', cluster_selection_method='eom')
model = BERTopic(umap_model=umap_model, hdbscan_model=hdbscan_model, min_topic_size=12, verbose=False)
topics, probs = model.fit_transform(docs, embeddings=emb)
print('Тем до reduce:', len(set(topics)) - (1 if -1 in topics else 0), 'шум:', list(topics).count(-1))
df['topic_full'] = topics

# reduce до ~30
model.reduce_topics(docs, nr_topics=30)
topics30 = model.topics_
df['topic'] = topics30
n_real = len(set(topics30) - {-1})
print('После reduce: тем', n_real, 'шум:', list(topics30).count(-1))
df.to_csv(f'{OUT}/physica_doc_topics.csv', index=False, encoding='utf-8')
ti = model.get_topic_info()
ti.to_csv(f'{OUT}/physica_topics30.csv', index=False, encoding='utf-8')
# сохранить модель через pickle (надёжнее)
with open(f'{OUT}/bertopic_model30.pkl','wb') as f:
    pickle.dump(model, f)
# имена тем
print('\nИтоговые темы:')
for _,r in ti[ti.Topic!=-1].sort_values('Count',ascending=False).iterrows():
    print(f"  #{int(r['Topic']):3d} ({int(r['Count']):4d}): {str(r['Name'])[:95]}")
