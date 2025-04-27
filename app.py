from flask import Flask, render_template, request, redirect, url_for, flash
import markdown as md_lib
from algorithm.inference import validate_input, run_inference

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-random-string"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form.get("user_input", "")
        if not validate_input(text):
            flash("❌ Usage: Must be a non-empty string. Cannot start or end with a comma. \\" \
            "Phrases are separated by single commas (no “,,”). \\" \
            "After splitting on commas, each phrase (trimmed) must be non-empty. \\" \
            "Each phrase may only contain letters, digits, spaces, apostrophes ('), and hyphens (-). \\")
            return redirect(url_for("index"))

        try:
            folder = run_inference(text)
            return redirect(url_for("show_result", folder=folder))
        except Exception as e:
            flash(f"❌ Error: {e}")
            return redirect(url_for("index"))

    return render_template("index.html")

@app.route("/result/<folder>")
def show_result(folder):
    md_path = f"{app.static_folder}/results/{folder}/output.md"
    try:
        raw = open(md_path).read()
        html = md_lib.markdown(raw, extensions=["fenced_code", "tables"])
    except FileNotFoundError:
        flash("❌ Result not found.")
        return redirect(url_for("index"))

    return render_template("result.html", content=html)

if __name__ == "__main__":
    app.run(debug=True)
