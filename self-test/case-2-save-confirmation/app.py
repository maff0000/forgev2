"""Forge self-test case 2: a minimal note-saving feature.

One route (`/`) that renders a page with a text input and a "Save"
button. One route (`POST /save`) that accepts a JSON body and persists
the note text in a plain module-level Python variable — no database,
no file, no session. `GET /` renders whatever is currently held in
that variable, which is what makes a page reload after a save show
the previously saved note.
"""
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Plain module-level in-memory store. Not a database, not a file, not a
# session — sufficient only to prove save-then-reload within one running
# process, per the PID.
_saved_note = None


@app.route("/")
def index():
    return render_template("index.html", saved_note=_saved_note)


@app.route("/save", methods=["POST"])
def save():
    global _saved_note
    data = request.get_json(silent=True) or {}
    _saved_note = data.get("note")
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
