#!/usr/bin/env python3
"""
traffic_counter.py

Step 3: Keyword Traffic Counting
Reads a single CSV of posts, groups by year and month, and computes a weighted count
based on keyword occurrences in the `body` field:
- A story increments by STORY_WEIGHT
- A comment increments by COMMENT_WEIGHT
Only posts with at least THRESHOLD keyword occurrences are counted.
"""

import csv
import re
from collections import defaultdict

# === Configuration ===
# Path to the CSV containing all posts (fields: year,month,type,body,...)
DATA_CSV = 'tmp/hn_raw_posts.csv'
# Path to the keywords file
KEYWORDS_FILE = 'tmp/keywords.txt'
# Minimum total keyword occurrences per post (threshold for counting)
THRESHOLD = 2
# Weight for story-type posts (>= THRESHOLD occurrences)
STORY_WEIGHT = 1.0
# Weight for comment-type posts (>= THRESHOLD occurrences)
# Based on relative significance, choose a value in (0,1)
COMMENT_WEIGHT = 0.4
# Path to the output CSV for monthly weighted counts
OUTPUT_CSV = 'tmp/traffic_counts_weighted.csv'


def load_keywords(path: str):
    """Load keywords and compile into regex patterns"""
    with open(path, 'r', encoding='utf-8') as f:
        kws = [line.strip() for line in f if line.strip()]
    return [re.compile(r"\b" + re.escape(kw) + r"\b", flags=re.IGNORECASE)
            for kw in kws]


def compute_weighted_counts(data_csv: str, patterns: list):
    """Read data_csv and return dict mapping (year, month) to weighted count"""
    counts = defaultdict(float)
    with open(data_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # extract year, month, type, and text
            try:
                year = int(row['year'])
                month = int(row['month'])
            except (KeyError, ValueError):
                continue  # skip malformed rows
            text = row.get('body', '') or ''
            # count occurrences
            occ = sum(len(p.findall(text)) for p in patterns)
            if occ < THRESHOLD:
                continue
            post_type = row.get('type', '').strip().lower()
            if post_type == 'story':
                counts[(year, month)] += STORY_WEIGHT
            elif post_type == 'comment':
                counts[(year, month)] += COMMENT_WEIGHT
            # ignore other types
    return counts


def main():
    patterns = load_keywords(KEYWORDS_FILE)
    weighted_counts = compute_weighted_counts(DATA_CSV, patterns)

    # Write results sorted by year, month
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['year', 'month', 'weighted_count'])
        for (year, month) in sorted(weighted_counts):
            wc = weighted_counts[(year, month)]
            writer.writerow([year, month, f"{wc:.2f}"])


if __name__ == '__main__':
    main()
