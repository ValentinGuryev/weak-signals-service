#!/usr/bin/env python3
"""Мини-прототип пайплайна «снапшот OpenAlex → направления исследований».
Работает на выборке 2.3 ГБ (part_0000 восьми партиций) — только для проверки архитектуры.
Полный прогон — тем же кодом на всех 2374 файлах.
"""
import duckdb, json, time, glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

S = "/mnt/c/oa_tmp/small"
W = "/mnt/c/oa_tmp/s*.gz"

con = duckdb.connect()
con.execute("SET threads=12; SET memory_limit='5GB'")

def load_taxonomy():
    con.execute(f"CREATE OR REPLACE TABLE topics AS SELECT id, display_name, description, keywords, subfield.id AS subfield_id, field.id AS field_id, domain.id AS domain_id, works_count, cited_by_count FROM read_json_auto('{S}/topics.gz', format='newline_delimited')")
    con.execute(f"CREATE OR REPLACE TABLE subfields AS SELECT id, display_name, field.id AS field_id FROM read_json_auto('{S}/subfields.gz', format='newline_delimited')")
    con.execute(f"CREATE OR REPLACE TABLE fields AS SELECT id, display_name, domain.id AS domain_id FROM read_json_auto('{S}/fields.gz', format='newline_delimited')")
    con.execute(f"CREATE OR REPLACE TABLE domains AS SELECT id, display_name FROM read_json_auto('{S}/domains.gz', format='newline_delimited')")

def build_derived():
    pat = ",".join(f"'{f}'" for f in sorted(glob.glob(W)))
    con.execute(f"""
    CREATE OR REPLACE TABLE works AS
    SELECT
      id, title, abstract_inverted_index, publication_year, language, type,
      cited_by_count,
      (SELECT list(array_element.id) FROM (SELECT unnest(coalesce(topics, [])) AS array_element) t) AS topic_ids,
      primary_topic.id AS primary_topic_id,
      is_retracted, is_paratext
    FROM read_json_auto([{pat}], format='newline_delimited')
    WHERE publication_year >= 2016
    """)
    n = con.execute("SELECT count(*) FROM works").fetchone()[0]
    con.execute("CREATE OR REPLACE TABLE work_text AS SELECT id, title, abstract_inverted_index FROM works")
    con.execute("CREATE OR REPLACE TABLE work_stats AS SELECT id, publication_year, language, type, cited_by_count, topic_ids, primary_topic_id, is_retracted, is_paratext FROM works")
    return n

def match_query(query, k_top=30):
    df = con.execute("SELECT id, display_name, coalesce(description,'') AS descr, coalesce(keywords,'[]') AS kw FROM topics").df()
    import ast
    df["text"] = df["display_name"] + " " + df["descr"] + " " + df["kw"].apply(lambda s: " ".join(ast.literal_eval(s)))
    vec = TfidfVectorizer(ngram_range=(1,2), stop_words="english", max_features=20000)
    X = vec.fit_transform(df["text"].tolist() + [query])
    sim = cosine_similarity(X[-1:], X[:-1])[0]
    idx = sim.argsort()[::-1]
    return [(df.iloc[i]["id"], df.iloc[i]["display_name"], float(sim[i])) for i in idx[:k_top] if sim[i] > 0]

def analyze_topics(top_ids):
    """Работы с любой из тем → таблица направлений: размер, цитирования, динамика."""
    tids = ",".join(f"'{t}'" for t in top_ids)
    df = con.execute(f"""
      WITH w AS (SELECT * FROM work_stats WHERE list_has_any(topic_ids, [{tids}])),
           per AS (
             SELECT w.id, unnest(w.topic_ids) AS tid, w.publication_year, w.cited_by_count
             FROM w
           )
      SELECT t.id AS topic_id, t.display_name AS topic_name,
             count(DISTINCT per.id)      AS n_works,
             sum(per.cited_by_count)     AS n_cites,
             min(per.publication_year)   AS y_min,
             max(per.publication_year)   AS y_max
      FROM per JOIN topics t ON per.tid = t.id
      GROUP BY 1,2 ORDER BY n_works DESC
    """).df()
    return df

if __name__ == "__main__":
    t0 = time.time()
    load_taxonomy()
    n = build_derived()
    print(f"[build] works 2016+ в выборке: {n:,}  ({time.time()-t0:.0f}s)")

    t0 = time.time()
    top = match_query("защита систем искусственного интеллекта adversarial machine learning")
    print(f"[match] топ-12 тем по запросу ({time.time()-t0:.0f}s):")
    for tid, name, s in top[:12]:
        print(f"  {tid:>10}  {name[:64]:<64} {s:.3f}")

    t0 = time.time()
    tids = [t[0] for t in top[:15]]
    d = analyze_topics(tids)
    print(f"\n[analyze] направления (топ-12 из {len(d)}) ({time.time()-t0:.0f}s):")
    for _, r in d.head(12).iterrows():
        print(f"  {r['topic_id']:>12}  {r['topic_name'][:58]:<58} works={r['n_works']:>6} cites={r['n_cites']:>8} {r['y_min']}-{r['y_max']}")