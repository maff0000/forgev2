"""Forge self-test case 1: a minimal toggle page.

One route (`/`) that renders a page with a "Show details" button and a
details panel that is hidden on load and toggles via the native HTML
`hidden` attribute on click.
"""
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
