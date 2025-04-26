import os
from datetime import datetime

def validate_input(user_input: str) -> bool:
    # replace with your real validation logic
    return bool(user_input and user_input.strip())

def run_inference(user_input: str) -> str:
    """
    - Creates a timestamped folder under static/results/
    - Writes out output.md (referencing its image)
    - Touches a dummy image file (replace with real generation)
    Returns the folder name.
    """
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    result_dir = os.path.join("static", "results", ts)
    os.makedirs(result_dir, exist_ok=True)

    # --- create a dummy image placeholder ---
    img_name = "image1.png"
    open(os.path.join(result_dir, img_name), "wb").close()

    # --- write markdown referencing the image via absolute static path ---
    md = (
        f"# Results for “{user_input}”\n\n"
        f"![result image](/static/results/{ts}/{img_name})\n\n"
        "*(That’s your algorithm’s markdown output.)*"
    )
    with open(os.path.join(result_dir, "output.md"), "w") as f:
        f.write(md)

    return ts
