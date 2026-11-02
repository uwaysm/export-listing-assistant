from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_demo_runs_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run(timeout=20)
    assert not app.exception
    assert len(app.tabs) == 3
    assert "Kensington Pride" in app.subheader[2].value
    app.main.radio[0].set_value("Side by side").run()
    assert not app.exception
    assert len(app.tabs) == 0


def test_live_mode_without_key_is_disabled(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("ENABLE_LIVE_GENERATION", "false")
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Live generation").run()
    assert not app.exception
    assert app.button[0].disabled
    assert len(app.tabs) == 0


def test_live_generation_and_failed_regeneration_clear_stale_output(monkeypatch):
    from export_listing.examples import demo_drafts
    from export_listing.generator import GenerationError
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key-for-test")
    monkeypatch.setenv("ENABLE_LIVE_GENERATION", "true")
    monkeypatch.setattr("export_listing.generator.generate", lambda *args: demo_drafts())
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Live generation").run()
    app.button[0].click().run()
    assert not app.exception
    assert len(app.tabs) == 3

    def fail(*args):
        raise GenerationError("Test generation failed")

    monkeypatch.setattr("export_listing.generator.generate", fail)
    app.button[0].click().run()
    assert not app.exception
    assert len(app.tabs) == 0
    assert "Test generation failed" in app.error[0].value
