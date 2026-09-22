from streamlit.testing.v1 import AppTest

from prepcanvas.catalog import load_demo_subject
from prepcanvas.storage import StudyStore


def test_every_primary_screen_renders_without_exceptions(tmp_path, monkeypatch):
    monkeypatch.setenv("PREPCANVAS_DB_PATH", str(tmp_path / "app-smoke.sqlite3"))
    app = AppTest.from_file("app/streamlit_app.py", default_timeout=10).run()

    assert len(app.exception) == 0
    for page in ["Diagnostic", "Learn", "Practice", "Mock exam", "Progress", "Subjects", "Overview"]:
        app.sidebar.radio[0].set_value(page).run()
        assert len(app.exception) == 0, f"{page} failed to render"


def test_blank_mock_exam_is_not_saved_as_evidence(tmp_path, monkeypatch):
    database = tmp_path / "blank-mock.sqlite3"
    monkeypatch.setenv("PREPCANVAS_DB_PATH", str(database))
    app = AppTest.from_file("app/streamlit_app.py", default_timeout=10).run()
    app.sidebar.radio[0].set_value("Mock exam").run()
    next(button for button in app.button if button.label == "Submit mock exam").click().run()

    assert any("12 remaining" in warning.value for warning in app.warning)
    assert StudyStore(database).list_attempts("sustainable-business-demo") == []


def test_learning_sequence_uses_saved_coaching_strategy(tmp_path, monkeypatch):
    database = tmp_path / "strategy.sqlite3"
    monkeypatch.setenv("PREPCANVAS_DB_PATH", str(database))
    store = StudyStore(database)
    subject = load_demo_subject()
    store.seed_demo_subject(subject)
    store.save_profile(
        subject["id"],
        {
            "id": "coach_and_recall",
            "name": "Coach + active recall",
            "description": "Recall before review.",
        },
        0.6,
        3,
    )

    app = AppTest.from_file("app/streamlit_app.py", default_timeout=10).run()
    app.sidebar.radio[0].set_value("Learn").run()
    assert any("Active recall first" in info.value for info in app.info)
