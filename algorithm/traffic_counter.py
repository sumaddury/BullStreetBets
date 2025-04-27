import csv
import re
from collections import defaultdict

DATA_CSV = 'tmp/hn_raw_posts.csv'
KEYWORDS_FILE = 'tmp/keywords.txt'
THRESHOLD = 2
STORY_WEIGHT = 1.0
COMMENT_WEIGHT = 0.4
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
            try:
                year = int(row['year'])
                month = int(row['month'])
            except (KeyError, ValueError):
                continue
            text = row.get('body', '') or ''
            occ = sum(len(p.findall(text)) for p in patterns)
            if occ < THRESHOLD:
                continue
            post_type = row.get('type', '').strip().lower()
            if post_type == 'story':
                counts[(year, month)] += STORY_WEIGHT
            elif post_type == 'comment':
                counts[(year, month)] += COMMENT_WEIGHT
    return counts


def main():
    patterns = load_keywords(KEYWORDS_FILE)
    weighted_counts = compute_weighted_counts(DATA_CSV, patterns)

    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['year', 'month', 'weighted_count'])
        for (year, month) in sorted(weighted_counts):
            wc = weighted_counts[(year, month)]
            writer.writerow([year, month, f"{wc:.2f}"])


if __name__ == '__main__':
    main()
