import os
import sys
import time
import re
from datetime import datetime
from algorithm.keyword_expansion import expand_to_keywords, save_keywords


def validate_input(user_input: str) -> bool:
    _PHRASE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9' \-]*[A-Za-z0-9]$")
    if not isinstance(user_input, str):
        return False
    s = user_input.strip()
    if not s:
        return False

    if s[0] == ',' or s[-1] == ',':
        return False

    parts = s.split(',')
    for part in parts:
        p = part.strip()
        if not p:
            return False
        if not _PHRASE_RE.match(p):
            return False
    return True

def run_inference(user_input: str) -> str:
    def log(msg: str):
        print(f"[inference] {msg}")
        sys.stdout.flush()

    log("Starting inference…")
    phrases = [p.strip() for p in user_input.split(",")]
    keywords = expand_to_keywords(phrases, num_keywords=100)
    save_keywords(keywords, filepath="tmp/keywords.txt")

    log("→ Scraping Reddit")
    time.sleep(1)

    log("→ Compiling data")
    time.sleep(1)

    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    result_dir = os.path.join("static", "results", ts)
    os.makedirs(result_dir, exist_ok=True)

    log("→ Generating images")
    img_name = "image1.png"
    open(os.path.join(result_dir, img_name), "wb").close()
    time.sleep(0.5)

    log("→ Writing markdown")
    md = (
        f"# Results for “{user_input}”\n\n"
        f"![result image](/static/results/{ts}/{img_name})\n\n"
        "*(End of demo output.)*"
    )
    with open(os.path.join(result_dir, "output.md"), "w") as f:
        f.write(md)

    log("Inference complete ✔")
    return ts
