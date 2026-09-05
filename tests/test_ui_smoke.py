from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_renders_without_exceptions() -> None:
    app_path = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    app = AppTest.from_file(str(app_path)).run(timeout=30)

    assert not app.exception
    assert app.title[0].value == (
        "Cloud Resource Usage Forecasting and VM Optimization Dashboard"
    )
    assert app.button[0].label == "Run Forecast"
    assert app.button[1].disabled

    app.button[0].click().run(timeout=60)
    assert not app.exception
    assert not app.button[1].disabled

    app.button[1].click().run(timeout=60)
    assert not app.exception
    assert "7. Scaling Recommendation" in [header.value for header in app.header]
