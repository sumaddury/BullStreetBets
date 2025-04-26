import os
import sys
import time
from datetime import datetime

def validate_input(user_input: str) -> bool:
    return bool(user_input and user_input.strip())

def run_inference(user_input: str) -> str:
    def log(msg: str):
        print(f"[inference] {msg}")
        sys.stdout.flush()

    log("Starting inference…")
    log("→ Scraping Reddit")
    time.sleep(1)  # simulate work

    log("→ Compiling data")
    time.sleep(1)

    # create timestamped result folder
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
