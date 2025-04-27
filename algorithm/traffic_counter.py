import csv
import re
import calendar
from collections import defaultdict
from datetime import datetime

DATA_CSV = 'tmp/hn_raw_posts.csv'
KEYWORDS_FILE = 'tmp/keywords.txt'
THRESHOLD = 2
STORY_WEIGHT = 1.0
COMMENT_WEIGHT = 0.4
OUTPUT_CSV = 'tmp/traffic_avg_per_day.csv'


def load_keywords(path: str):
    """Load keywords and compile into regex patterns"""
    with open(path, 'r', encoding='utf-8') as f:
        kws = [line.strip() for line in f if line.strip()]
    return [re.compile(r"\b" + re.escape(kw) + r"\b", flags=re.IGNORECASE)
            for kw in kws]


def compute_weighted_counts_and_days(data_csv: str, patterns: list):
    """Read data_csv and return two dicts:
    1) counts[(year,month)] = weighted count
    2) days_seen[(year,month)] = max day-of-month observed in data
    """
    counts = defaultdict(float)
    days_seen = defaultdict(int)
    with open(data_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                year = int(row['year'])
                month = int(row['month'])
                ts = int(row['created_at'])
            except (KeyError, ValueError):
                continue
            dt = datetime.fromtimestamp(ts)
            if dt.year == year and dt.month == month:
                days_seen[(year, month)] = max(days_seen[(year, month)], dt.day)
            text = row.get('body', '') or ''
            occ = sum(len(p.findall(text)) for p in patterns)
            if occ < THRESHOLD:
                continue
            post_type = row.get('type', '').strip().lower()
            if post_type == 'story':
                counts[(year, month)] += STORY_WEIGHT
            elif post_type == 'comment':
                counts[(year, month)] += COMMENT_WEIGHT
    return counts, days_seen


def main():
    patterns = load_keywords(KEYWORDS_FILE)
    counts, days_seen = compute_weighted_counts_and_days(DATA_CSV, patterns)

    months = sorted(counts.keys())
    if not months:
        return
    last_month = months[-1]

    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['year', 'month', 'avg_per_day'])
        for ym in months:
            year, month = ym
            weighted = counts[ym]
            if ym == last_month:
                days = days_seen.get(ym, calendar.monthrange(year, month)[1])
            else:
                days = calendar.monthrange(year, month)[1]
            avg = weighted / days if days else 0.0
            writer.writerow([year, month, f"{avg:.4f}"])

if __name__ == '__main__':
    main()
