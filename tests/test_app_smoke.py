from streamlit.testing.v1 import AppTest

from prepcanvas.catalog import load_demo_subject
from prepcanvas.storage import StudyStore


DEMO_ID = "sustainable-business-demo"


def start(tmp_path, monkeypatch, name="app.sqlite3"):
    database = tmp_path / name
    monkeypatch.setenv("PREPCANVAS_DB_PATH", str(database))
    return database, AppTest.from_file("app/streamlit_app.py", default_timeout=10).run()


def button(app, key):
    return next(item for item in app.button if item.key == key)


def open_subject(app, subject_id=DEMO_ID):
    button(app, f"open_{subject_id}").click().run()


def open_page(app, page):
    next(radio for radio in app.radio if radio.key == "page").set_value(page).run()


def create_subject(app, name):
    button(app, "new_subject").click().run()
    app.text_input[0].input(name).run()
    next(item for item in app.button if item.label == "Create subject").click().run()


def seeded_store(database):
    store = StudyStore(database)
    subject = load_demo_subject()
    store.seed_demo_subject(subject)
    return store, subject


def test_app_opens_on_the_subject_library(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch)
    assert len(app.exception) == 0
    assert any("Welcome to PrepCanvas" in item.value for item in app.markdown)
    assert [item.value for item in app.subheader] == ["In progress"]
    assert button(app, "new_subject")
    assert button(app, f"open_{DEMO_ID}").label == "Open"


def test_every_primary_screen_renders_without_exceptions(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch)
    open_subject(app)
    assert len(app.exception) == 0
    for page in ["Diagnostic", "Learn", "Practice", "Mock exam", "Progress", "Settings", "Overview"]:
        open_page(app, page)
        assert len(app.exception) == 0, f"{page} failed to render"


def test_back_to_library_and_into_another_subject_resets_the_page(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")
    button(app, "back_to_library").click().run()
    open_subject(app)
    open_page(app, "Progress")
    button(app, "back_to_library").click().run()
    open_subject(app, "statistics-101")
    assert next(radio for radio in app.radio if radio.key == "page").value == "Overview"


def test_blank_mock_exam_is_not_saved_as_evidence(tmp_path, monkeypatch):
    database, app = start(tmp_path, monkeypatch)
    open_subject(app)
    open_page(app, "Mock exam")
    next(item for item in app.button if item.label == "Submit mock exam").click().run()

    assert any("12 remaining" in warning.value for warning in app.warning)
    assert StudyStore(database).list_attempts(DEMO_ID) == []


def test_learning_sequence_uses_saved_coaching_strategy(tmp_path, monkeypatch):
    database = tmp_path / "strategy.sqlite3"
    store, subject = seeded_store(database)
    store.save_profile(
        subject["id"],
        {"id": "coach_and_recall", "name": "Coach + active recall", "description": "Recall before review."},
        0.6,
        3,
    )
    _, app = start(tmp_path, monkeypatch, "strategy.sqlite3")
    open_subject(app)
    open_page(app, "Learn")
    assert any("Active recall first" in info.value for info in app.info)


def test_overview_counts_distinct_questions_per_topic(tmp_path, monkeypatch):
    store, subject = seeded_store(tmp_path / "evidence.sqlite3")
    for _ in range(3):
        store.save_attempt(
            subject["id"],
            "practice",
            {"topic_id": "systems-thinking", "question_id": "sys-1", "score": 1, "max_score": 1},
        )
    _, app = start(tmp_path, monkeypatch, "evidence.sqlite3")
    assert button(app, f"open_{DEMO_ID}").label == "Continue"
    open_subject(app)
    assert "1 of 3 questions answered" in [caption.value for caption in app.caption]
    assert any("Systems thinking** · 33% mastery" in item.value for item in app.markdown)


def test_created_subject_is_confirmed_and_opened(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")

    assert len(app.exception) == 0
    assert app.toast[0].value.startswith("Subject “Statistics 101” created.")
    assert "later release" in app.toast[0].value
    assert any("Statistics 101" in item.value for item in app.markdown if 'class="subject-bar"' in item.value)

    open_page(app, "Progress")
    assert len(app.toast) == 0


def test_completed_subjects_move_to_their_own_group_and_can_reopen(tmp_path, monkeypatch):
    database, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")
    open_page(app, "Settings")
    button(app, "complete_subject").click().run()

    assert [item.value for item in app.subheader] == ["In progress", "Completed"]
    assert StudyStore(database).get_subject("statistics-101")["status"] == "completed"

    open_subject(app, "statistics-101")
    open_page(app, "Settings")
    button(app, "reopen_subject").click().run()
    assert StudyStore(database).get_subject("statistics-101")["status"] == "active"


def test_destructive_actions_require_confirmation(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")
    open_page(app, "Settings")

    assert button(app, "delete_statistics-101").disabled
    assert button(app, "reset_statistics-101").disabled


def remove_sample(app):
    open_subject(app)
    open_page(app, "Settings")
    assert not any(item.key == f"delete_{DEMO_ID}" for item in app.button)
    app.checkbox(key=f"confirm_{DEMO_ID}").check().run()
    button(app, "remove_sample").click().run()


def test_removing_the_sample_leaves_an_empty_library_with_two_starting_points(tmp_path, monkeypatch):
    database, app = start(tmp_path, monkeypatch)
    remove_sample(app)

    assert len(app.exception) == 0
    assert [toast.value for toast in app.toast] == ["Sample subject removed. You can add it back from the library."]
    assert button(app, "new_subject").label == "Create your first subject"
    assert button(app, "add_sample").label == "Explore the sample subject"
    assert StudyStore(database).get_subject(DEMO_ID) is None


def test_removed_sample_stays_removed_after_a_restart(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch, "restart.sqlite3")
    remove_sample(app)
    _, restarted = start(tmp_path, monkeypatch, "restart.sqlite3")
    assert not any(item.key == f"open_{DEMO_ID}" for item in restarted.button)


def test_sample_can_be_added_back_from_the_library(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")
    button(app, "back_to_library").click().run()
    remove_sample(app)

    assert button(app, "add_sample").label == "Add sample subject"
    button(app, "add_sample").click().run()
    assert len(app.exception) == 0
    assert any("Sustainable Business Fundamentals" in item.value for item in app.markdown if 'class="subject-bar"' in item.value)


def test_deleting_a_subject_returns_to_the_library(tmp_path, monkeypatch):
    database, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")
    open_page(app, "Settings")
    app.checkbox(key="confirm_statistics-101").check().run()
    button(app, "delete_statistics-101").click().run()

    assert len(app.exception) == 0
    assert any("Welcome to PrepCanvas" in item.value for item in app.markdown)
    assert not any(item.key == "open_statistics-101" for item in app.button)
    assert [toast.value for toast in app.toast] == ["Subject “Statistics 101” was deleted."]
    assert StudyStore(database).get_subject("statistics-101") is None


def test_resetting_demo_progress_clears_saved_answers(tmp_path, monkeypatch):
    database = tmp_path / "reset.sqlite3"
    store, subject = seeded_store(database)
    store.save_attempt(subject["id"], "practice", {"topic_id": "systems-thinking", "question_id": "sys-1", "score": 1, "max_score": 1})

    _, app = start(tmp_path, monkeypatch, "reset.sqlite3")
    open_subject(app)
    open_page(app, "Settings")
    app.checkbox(key=f'confirm_{subject["id"]}').check().run()
    button(app, f'reset_{subject["id"]}').click().run()

    assert len(app.exception) == 0
    assert StudyStore(database).list_attempts(subject["id"]) == []
    assert StudyStore(database).get_subject(subject["id"]) is not None


def test_recent_activity_names_the_question_and_topic(tmp_path, monkeypatch):
    store, subject = seeded_store(tmp_path / "activity.sqlite3")
    store.save_attempt(subject["id"], "mock_exam", {"topic_id": "systems-thinking", "question_id": "sys-1", "score": 1, "max_score": 1})

    _, app = start(tmp_path, monkeypatch, "activity.sqlite3")
    open_subject(app)
    open_page(app, "Progress")
    activity = next(item.value for item in app.markdown if 'class="activity"' in item.value)
    assert "Which question best reflects systems thinking?" in activity
    assert "Systems thinking · Mock exam ·" in activity
    assert "100%" in activity
