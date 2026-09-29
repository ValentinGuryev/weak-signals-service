#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кластеризация тезисов PhysicA методом BERTopic.
1. Эмбеддинги: paraphrase-multilingual-MiniLM-L12-v2 (документ = title + первые 300 симв текста).
2. UMAP -> HDBSCAN -> темы + c-TF-IDF.
Результат: physica_topics.csv (id, тема, документы), physica_doc_topics.csv.
"""
import pandas as pd, numpy as np, time, os, logging, pickle
logging.basicConfig(level=logging.INFO, format='%(message)s')
OUT='results/conference_analysis/PhysicA'
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(f'{OUT}/physica_theses_prepared.csv', dtype=str).fillna('')
docs = [(r['title'] + '. ' + r['text_clean'])[:400] for _,r in df.iterrows()]
df['doc_short'] = docs
logging.info(f'Документов: {len(df)}')

from sentence_transformers import SentenceTransformer
emb_path = f'{OUT}/embeddings.npy'
if os.path.exists(emb_path):
    emb = np.load(emb_path)
    logging.info(f'Эмбеддинги загружены: {emb.shape}')
else:
    t0=time.time()
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    emb = model.encode(docs, batch_size=64, show_progress_bar=True)
    np.save(emb_path, emb)
    logging.info(f'Эмбеддинги: {emb.shape} за {(time.time()-t0)/60:.1f} мин')

from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN

# Умеренная кластеризация: не слишком мелко, но и не сливать всё
umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
hdbscan_model = HDBSCAN(min_cluster_size=12, min_samples=5, metric='euclidean', cluster_selection_method='eom')
topic_model = BERTopic(embedding_model=None,  # эмбеддинги уже посчитаны
                       umap_model=umap_model, hdbscan_model=hdbscan_model,
                       min_topic_size=12, calculate_probabilities=False, verbose=True)
t0=time.time()
topics, probs = topic_model.fit_transform(docs, embeddings=emb)
logging.info(f'Кластеризация за {(time.time()-t0)/60:.1f} мин')
df['topic'] = topics
df.to_csv(f'{OUT}/physica_doc_topics.csv', index=False, encoding='utf-8')

# Сводка тем
topic_info = topic_model.get_topic_info()
topic_info.to_csv(f'{OUT}/physica_topics.csv', index=False, encoding='utf-8')
n_topics = len(topic_info[topic_info.Topic != -1])
logging.info(f'Тем: {n_topics} (+ шум {-1}: {(topics==-1).sum()})')
# топ-10 тем
for _,r in topic_info[topic_info.Topic!=-1].head(15).iterrows():
    print(f"  Тема {r['Topic']}: {r['Count']} док. | {str(r['Name'])[:90]}")
topic_model.save(f'{OUT}/bertopic_model')
with open(f'{OUT}/doc_short.pkl','wb') as f: pickle.dump(docs, f)
