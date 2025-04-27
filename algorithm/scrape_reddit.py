import os
import math
import time
import random
import datetime
import requests
import pandas as pd

SAMPLE_PER_MONTH = 1000
HITS_PER_PAGE = 1000
OUTPUT_CSV = os.path.join("tmp", "hn_raw_posts.csv")

API_URL = "https://hn.algolia.com/api/v1/search_by_date"


def fetch_hn_month(year: int, month: int, sample_size: int):
    start = int(datetime.datetime(year, month, 1).timestamp())
    end = int(datetime.datetime(year + (month==12), ((month % 12) + 1), 1).timestamp())

    pages_needed = math.ceil(sample_size / HITS_PER_PAGE)
    all_hits = []

    for page in range(pages_needed):
        params = {
            "tags": "(story,comment)",
            "hitsPerPage": HITS_PER_PAGE,
            "page": page,
            "numericFilters": f"created_at_i>={start},created_at_i<{end}"
        }
        resp = requests.get(API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        hits = data.get("hits", [])
        if not hits:
            break
        all_hits.extend(hits)
        time.sleep(0.5)

    if not all_hits:
        return pd.DataFrame()

    sampled = random.sample(all_hits, min(sample_size, len(all_hits)))
    return build_dataframe(sampled, year, month)



def build_dataframe(hits, year, month):
    """
    Build a pandas DataFrame with desired fields, extracting type and body.
    """
    rows = []
    for hit in hits:
        tags = hit.get("_tags", [])
        if "comment" in tags:
            item_type = "comment"
        elif "story" in tags:
            item_type = "story"
        else:
            item_type = "other"

        body = hit.get("comment_text") or hit.get("story_text") or ""

        rows.append({
            "year": year,
            "month": month,
            "id": hit.get("objectID"),
            "created_at": hit.get("created_at_i"),
            "type": item_type,
            "title": hit.get("title") or "",
            "url": hit.get("url") or "",
            "body": body,
            "score": hit.get("points") or 0,
            "num_comments": hit.get("num_comments") or 0
        })
    return pd.DataFrame(rows)


def main():
    today = datetime.date.today()
    dfs = []
    for i in range(24):
        year_offset, m_idx = divmod(today.month - 1 - i, 12)
        y = today.year + year_offset
        m = m_idx + 1
        print(f"→ Fetching {y}-{m:02d}…")
        try:
            df = fetch_hn_month(y, m, SAMPLE_PER_MONTH)
            print(f"   collected {len(df)} rows")
            dfs.append(df)
        except Exception as e:
            print(f"   Error: {e}")

    if dfs:
        result = pd.concat(dfs, ignore_index=True)
        os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
        result.to_csv(OUTPUT_CSV, index=False)
        print(f"✅ Saved raw HN posts to {OUTPUT_CSV}")
    else:
        print("❌ No data fetched; check your network or API limits.")


if __name__ == "__main__":
    main()
