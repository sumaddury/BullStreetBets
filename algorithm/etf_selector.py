
import os
import json
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

REPORT_JSON    = "tmp/spike_report.json"
ETF_CSV        = "tmp/etf_list_us_canada_final.csv"
KEYWORDS_FILE  = "tmp/keywords.txt"
TOP_N          = 10

def load_json(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Report JSON not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_keywords(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Keywords file not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        kws = [line.strip() for line in f if line.strip()]
    return " ".join(kws)

def load_etfs(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"ETF CSV not found at {path}")
    etfs = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = f"{row.get('Name','')} {row.get('Sector','')}".strip()
            etfs.append({
                "ticker": row.get("Ticker",""),
                "text": text
            })
    return etfs

def main():
    report = load_json(REPORT_JSON)

    query_text = load_keywords(KEYWORDS_FILE)

    etfs = load_etfs(ETF_CSV)
    texts = [e["text"] for e in etfs]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(texts + [query_text])
    query_vec = tfidf_matrix[-1]
    etf_vecs  = tfidf_matrix[:-1]

    sims = cosine_similarity(query_vec, etf_vecs)[0]

    top_idxs = sims.argsort()[::-1][:TOP_N]
    top_tickers = [etfs[i]["ticker"] for i in top_idxs if sims[i] > 0]

    report["relevant_etfs"] = ",".join(top_tickers)

    save_json(report, REPORT_JSON)

    print(f"→ Appended relevant_etfs='{report['relevant_etfs']}' to {REPORT_JSON}")

if __name__ == "__main__":
    main()
