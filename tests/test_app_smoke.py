from streamlit.testing.v1 import AppTest

from prepcanvas.catalog import load_demo_subject
from prepcanvas.storage import StudyStore


def open_page(app, page):
    next(radio for radio in app.radio if radio.key == "page").set_value(page).run()


def test_every_primary_screen_renders_without_exceptions(tmp_path, monkeypatch):
    monkeypatch.setenv("PREPCANVAS_DB_PATH", str(tmp_path / "app-smoke.sqlite3"))
    app = AppTest.from_file("app/streamlit_app.py", default_timeout=10).run()

    assert len(app.exception) == 0
    for page in ["Diagnostic", "Learn", "Practice", "Mock exam", "Progress", "Subjects", "Overview"]:
        open_page(app, page)
        assert len(app.exception) == 0, f"{page} failed to render"


def test_blank_mock_exam_is_not_saved_as_evidence(tmp_path, monkeypatch):
    database = tmp_path / "blank-mock.sqlite3"
    monkeypatch.setenv("PREPCANVAS_DB_PATH", str(database))
    app = AppTest.from_file("app/streamlit_app.py", default_timeout=10).run()
    open_page(app, "Mock exam")
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
    open_page(app, "Learn")
    assert any("Active recall first" in info.value for info in app.info)


def test_overview_counts_distinct_questions_per_topic(tmp_path, monkeypatch):
    database = tmp_path / "evidence.sqlite3"
    monkeypatch.setenv("PREPCANVAS_DB_PATH", str(database))
    store = StudyStore(database)
    subject = load_demo_subject()
    store.seed_demo_subject(subject)
    for _ in range(3):
        store.save_attempt(
            subject["id"],
            "practice",
            {"topic_id": "systems-thinking", "question_id": "sys-1", "score": 1, "max_score": 1},
        )

    app = AppTest.from_file("app/streamlit_app.py", default_timeout=10).run()
    captions = [caption.value for caption in app.caption]
    assert "1 of 3 questions answered" in captions
    assert any("Systems thinking** · 33% mastery" in item.value for item in app.markdown)


def test_created_subject_is_confirmed_and_selected(tmp_path, monkeypatch):
    monkeypatch.setenv("PREPCANVAS_DB_PATH", str(tmp_path / "create.sqlite3"))
    app = AppTest.from_file("app/streamlit_app.py", default_timeout=10).run()
    open_page(app, "Subjects")
    app.text_input[0].input("Statistics 101").run()
    next(button for button in app.button if button.label == "Create subject").click().run()

    assert len(app.exception) == 0
    assert [toast.value for toast in app.toast] == ["Subject “Statistics 101” created and selected."]
    assert app.sidebar.selectbox[0].value == "statistics-101"

    open_page(app, "Overview")
    assert len(app.toast) == 0
    assert app.sidebar.selectbox[0].value == "statistics-101"


def create_subject(app, name):
    open_page(app, "Subjects")
    app.text_input[0].input(name).run()
    next(button for button in app.button if button.label == "Create subject").click().run()


def button(app, key):
    return next(item for item in app.button if item.key == key)


def test_destructive_actions_require_confirmation(tmp_path, monkeypatch):
    monkeypatch.setenv("PREPCANVAS_DB_PATH", str(tmp_path / "manage.sqlite3"))
    app = AppTest.from_file("app/streamlit_app.py", default_timeout=10).run()
    create_subject(app, "Statistics 101")

    assert button(app, "delete_statistics-101").disabled
    assert button(app, "reset_statistics-101").disabled
    assert not any(item.key == "delete_sustainable-business-demo" for item in app.button)


def test_deleting_the_selected_subject_falls_back_to_the_demo(tmp_path, monkeypatch):
    database = tmp_path / "delete.sqlite3"
    monkeypatch.setenv("PREPCANVAS_DB_PATH", str(database))
    app = AppTest.from_file("app/streamlit_app.py", default_timeout=10).run()
    create_subject(app, "Statistics 101")
    assert app.sidebar.selectbox[0].value == "statistics-101"

    app.checkbox(key="confirm_statistics-101").check().run()
    button(app, "delete_statistics-101").click().run()

    assert len(app.exception) == 0
    assert app.sidebar.selectbox[0].value == "sustainable-business-demo"
    assert "Statistics 101" not in app.sidebar.selectbox[0].options
    assert [toast.value for toast in app.toast] == ["Subject “Statistics 101” was deleted."]
    assert StudyStore(database).get_subject("statistics-101") is None


def test_resetting_demo_progress_clears_saved_answers(tmp_path, monkeypatch):
    database = tmp_path / "reset.sqlite3"
    monkeypatch.setenv("PREPCANVAS_DB_PATH", str(database))
    store = StudyStore(database)
    subject = load_demo_subject()
    store.seed_demo_subject(subject)
    store.save_attempt(subject["id"], "practice", {"topic_id": "systems-thinking", "question_id": "sys-1", "score": 1, "max_score": 1})

    app = AppTest.from_file("app/streamlit_app.py", default_timeout=10).run()
    open_page(app, "Subjects")
    app.checkbox(key=f'confirm_{subject["id"]}').check().run()
    button(app, f'reset_{subject["id"]}').click().run()

    assert len(app.exception) == 0
    assert StudyStore(database).list_attempts(subject["id"]) == []
    assert StudyStore(database).get_subject(subject["id"]) is not None
