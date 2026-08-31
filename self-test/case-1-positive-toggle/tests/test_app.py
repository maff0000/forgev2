import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app  # noqa: E402


def test_index_returns_200():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_index_contains_button_and_hidden_panel():
    client = app.test_client()
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert 'id="toggle-button"' in html
    assert "Show details" in html
    assert 'id="details-panel"' in html
    # The panel must carry the native `hidden` attribute on initial render.
    assert "details-panel" in html
    assert 'hidden' in html

    # More precise check: the details-panel element itself carries `hidden`.
    panel_start = html.index('id="details-panel"')
    # Look in a small window around the id for the hidden attribute,
    # covering both `<div id="details-panel" hidden>` orderings.
    window = html[max(0, panel_start - 100): panel_start + 100]
    assert "hidden" in window
