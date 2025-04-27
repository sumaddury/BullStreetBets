import os
import time
import random
import math
import datetime
import requests
import pandas as pd

SAMPLE_PER_WEEK = 1000
WEEKS_PER_MONTH = 4
HITS_PER_PAGE = 1000
OUTPUT_CSV = os.path.join("tmp", "hn_raw_posts.csv")
API_URL = "https://hn.algolia.com/api/v1/search_by_date"


def fetch_hn_month(year: int, month: int):
    """
    Fetch up to SAMPLE_PER_WEEK hits for each of WEEKS_PER_MONTH segments in the given month.
    """
    start_dt = datetime.datetime(year, month, 1)
    if month == 12:
        next_month_dt = datetime.datetime(year + 1, 1, 1)
    else:
        next_month_dt = datetime.datetime(year, month + 1, 1)

    total_days = (next_month_dt - start_dt).days
    segment_days = math.ceil(total_days / WEEKS_PER_MONTH)
    all_hits = []

    for i in range(WEEKS_PER_MONTH):
        seg_start = start_dt + datetime.timedelta(days=i * segment_days)
        seg_end = seg_start + datetime.timedelta(days=segment_days)
        if seg_end > next_month_dt:
            seg_end = next_month_dt

        start_ts = int(seg_start.timestamp())
        end_ts = int(seg_end.timestamp())

        params = {
            "tags": "(story,comment)",
            "hitsPerPage": HITS_PER_PAGE,
            "page": 0,
            "numericFilters": f"created_at_i>={start_ts},created_at_i<{end_ts}"
        }
        resp = requests.get(API_URL, params=params)
        resp.raise_for_status()
        hits = resp.json().get("hits", [])

        if len(hits) > SAMPLE_PER_WEEK:
            hits = random.sample(hits, SAMPLE_PER_WEEK)

        all_hits.extend(hits)
        time.sleep(0.5)

    if not all_hits:
        return pd.DataFrame()

    return build_dataframe(all_hits, year, month)


def build_dataframe(hits, year, month):
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
            df = fetch_hn_month(y, m)
            print(f"   collected {len(df)} rows")
            dfs.append(df)
        except Exception as e:
            print(f"   Error: {e}")

    if dfs:
        result = pd.concat(dfs, ignore_index=True)
        os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
        result.to_csv(OUTPUT_CSV, index=False)
        print(f"Saved raw HN posts to {OUTPUT_CSV}")
    else:
        print("No data fetched; check your network or API limits.")


if __name__ == "__main__":
    main()
