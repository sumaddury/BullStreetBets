import os
import sys
import time
import re
import json
from datetime import datetime
from algorithm.keyword_expansion import expand_to_keywords, save_keywords


def validate_input(user_input: str) -> bool:
    _PHRASE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9' \-]*[A-Za-z0-9]$")
    if not isinstance(user_input, str):
        return False
    s = user_input.strip()
    if not s or s[0] == ',' or s[-1] == ',':
        return False
    for part in s.split(','):
        p = part.strip()
        if not p or not _PHRASE_RE.match(p):
            return False
    return True


def run_inference(user_input: str) -> str:
    """
    Full pipeline:
    1) Expand keywords
    2) Scrape Reddit
    3) Count & normalize traffic
    4) Detect spikes
    5) Write a Markdown report embedding the JSON stats and static spike_plot.png
    """
    def log(msg: str):
        print(f"[inference] {msg}")
        sys.stdout.flush()

    log("Building Keywords...")
    phrases = [p.strip() for p in user_input.split(",")]
    keywords = expand_to_keywords(phrases, num_keywords=100)
    save_keywords(keywords, filepath="tmp/keywords.txt")

    log("Scraping Reddit...")
    os.system("python3 algorithm/scrape_reddit.py")

    log("Counting Traffic...")
    os.system("python3 algorithm/traffic_counter.py")

    log("Analyze Time Series...")
    os.system("python3 algorithm/spike_detector.py")

    log("Pulling ETFs...")
    os.system("python3 algorithm/scrape_etfs.py")
    os.system("python3 algorithm/etf_selector.py")

    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    result_dir = os.path.join("static", "results", ts)
    os.makedirs(result_dir, exist_ok=True)

    src_json = os.path.join("tmp", "spike_report.json")
    dst_json = os.path.join(result_dir, "spike_report.json")
    os.replace(src_json, dst_json)

    with open(dst_json, 'r', encoding='utf-8') as f:
        report = json.load(f)

    md_lines = [f"# Traffic Spike Analysis for “{user_input}”", ""]
    md_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_lines.append("")
    md_lines.append("| Parameter        | Value      |")
    md_lines.append("|:-----------------|-----------:|")
    for key in ['year','month','latest_rate','beta','mean','stdev','variance','median','min','max','threshold','recommendation', 'relevant_etfs']:
        md_lines.append(f"| {key} | {report.get(key)} |")
    md_lines.append("")
    md_lines.append("## Spike Plot")
    md_lines.append("")
    # Reference static spike_plot.png directly
    md_lines.append("![Spike Plot](/static/spike_plot.png)")
    md_content = "\n".join(md_lines)

    # Write markdown
    with open(os.path.join(result_dir, 'output.md'), 'w', encoding='utf-8') as f:
        f.write(md_content)

    log("Inference complete ✔")
    return ts
