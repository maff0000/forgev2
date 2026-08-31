import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as app_module  # noqa: E402
from app import app  # noqa: E402


def setup_function(_function):
    # Reset the module-level in-memory store between tests so they don't
    # leak state into each other.
    app_module._saved_note = None


def test_index_returns_200_with_form_markup():
    client = app.test_client()
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="note-input"' in html
    assert 'id="save-button"' in html
    assert "Save" in html


def test_save_returns_200_with_status_ok():
    client = app.test_client()
    response = client.post("/save", json={"note": "hello world"})

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_index_reflects_saved_note_after_save():
    client = app.test_client()
    client.post("/save", json={"note": "remember the milk"})

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "remember the milk" in html
