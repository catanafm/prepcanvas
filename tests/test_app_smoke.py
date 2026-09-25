import json

from streamlit.testing.v1 import AppTest

from prepcanvas.catalog import load_demo_subject
from prepcanvas.storage import StudyStore


DEMO_ID = "sustainable-business-demo"


def start(tmp_path, monkeypatch, name="app.sqlite3"):
    database = tmp_path / name
    monkeypatch.setenv("PREPCANVAS_DB_PATH", str(database))
    monkeypatch.setenv("PREPCANVAS_PRIVATE_DIR", str(tmp_path / "private"))
    return database, AppTest.from_file("app/streamlit_app.py", default_timeout=10).run()


def write_package(tmp_path, subject_id, package):
    folder = tmp_path / "private" / "subjects" / subject_id
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "package.json").write_text(json.dumps({**package, "id": subject_id}), encoding="utf-8")
    return folder


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
    for page in ["Content", "Diagnostic", "Learn", "Practice", "Mock exam", "Progress", "Settings", "Overview"]:
        open_page(app, page)
        assert len(app.exception) == 0, f"{page} failed to render"


def test_tabs_put_study_modes_before_setup_pages(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch)
    open_subject(app)
    tabs = next(radio for radio in app.radio if radio.key == "page").options
    assert tabs == ["Overview", "Learn", "Practice", "Mock exam", "Progress", "Diagnostic", "Content", "Settings"]


def test_every_screen_renders_for_a_subject_without_content(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")
    for page in ["Overview", "Diagnostic", "Learn", "Practice", "Mock exam", "Progress", "Settings", "Content"]:
        open_page(app, page)
        assert len(app.exception) == 0, f"{page} failed to render"
        if page in {"Diagnostic", "Learn", "Practice", "Mock exam"}:
            assert button(app, "needs_content").label == "Set up study content"


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

    assert any("6 remaining" in warning.value for warning in app.warning)
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


def test_created_subject_opens_on_the_content_page_with_a_brief(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")

    assert len(app.exception) == 0
    assert app.toast[0].value.startswith("Subject “Statistics 101” created.")
    assert "add your materials" in app.toast[0].value
    assert any("Statistics 101" in item.value for item in app.markdown if 'class="subject-bar"' in item.value)
    assert next(radio for radio in app.radio if radio.key == "page").value == "Content"
    assert [item.value for item in app.subheader] == ["1 · Materials", "2 · Build the study content", "3 · Check the result"]
    assert any("No package yet" in info.value for info in app.info)
    brief = json.loads((tmp_path / "private" / "subjects" / "statistics-101" / "brief.json").read_text(encoding="utf-8"))
    assert brief["name"] == "Statistics 101" and brief["target_score"] == 80

    open_page(app, "Progress")
    assert len(app.toast) == 0


def test_overview_without_content_shows_the_setup_checklist(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")
    open_page(app, "Overview")
    panel = next(item.value for item in app.markdown if "Set up study content" in item.value)
    assert "1 · Materials: no files yet" in panel
    assert "2 · Study content: no package.json yet" in panel
    assert button(app, "open_content").label == "Open Content"
    button(app, "open_content").click().run()
    assert next(radio for radio in app.radio if radio.key == "page").value == "Content"


def test_user_subject_with_a_valid_package_is_fully_studyable(tmp_path, monkeypatch, demo_subject):
    write_package(tmp_path, "statistics-101", demo_subject)
    _, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")
    assert any("Study content loaded: 4 topics · 12 questions" in item.value for item in app.success)
    assert button(app, "start_diagnostic")

    open_page(app, "Overview")
    assert any("Systems thinking** · 0% mastery" in item.value for item in app.markdown)

    open_page(app, "Diagnostic")
    for radio in app.radio:
        if radio.key.startswith("diagnostic_"):
            radio.set_value(radio.options[0]).run()
    next(item for item in app.button if item.label == "Build my learning profile").click().run()
    assert any("Your starting strategy" in item.value for item in app.success)

    open_page(app, "Progress")
    assert len(app.exception) == 0
    assert any("Saved answers" in item.value and ">4<" in item.value for item in app.markdown)


def test_invalid_package_is_explained_on_the_content_page(tmp_path, monkeypatch, demo_subject):
    demo_subject["questions"][0]["correct_answer"] = "not an option"
    write_package(tmp_path, "statistics-101", demo_subject)
    _, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")
    assert len(app.exception) == 0
    assert any("could not be loaded" in item.value for item in app.error)
    assert any("$.questions[0].correct_answer" in item.value for item in app.error)
    button(app, "back_to_library").click().run()
    assert any("Study content has errors" in item.value for item in app.markdown)


def exam_widgets(app):
    return [radio for radio in app.radio if radio.key.startswith("exam_")] + list(app.text_area)


def test_mock_exam_offers_the_original_exam_a_variant_or_everything(tmp_path, monkeypatch, demo_subject):
    for question in demo_subject["questions"]:
        if question["topic_id"] == "carbon-basics":
            question["origin"] = "generated"
    write_package(tmp_path, "statistics-101", demo_subject)
    _, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")
    open_page(app, "Mock exam")
    exam_set = next(radio for radio in app.radio if radio.key == "mock_exam_set")
    assert exam_set.options == ["Original practice exam", "Numbered variant from the question pool", "Every question"]
    assert exam_set.value == "source"
    assert len(exam_widgets(app)) == 9
    exam_set.set_value("variant").run()
    assert len(exam_widgets(app)) == 6
    assert any("4 multiple choice · 2 short answer · 8 points" in item.value for item in app.caption)
    assert next(item for item in app.number_input if item.key == "mock_variant").value == 1
    next(radio for radio in app.radio if radio.key == "mock_exam_set").set_value("all").run()
    assert len(exam_widgets(app)) == 12


def sit_variant(app):
    for radio in app.radio:
        if radio.key.startswith("exam_"):
            radio.set_value(radio.options[0]).run()
    for area in app.text_area:
        area.input("An answer that earns nothing").run()
    next(item for item in app.button if item.label == "Submit mock exam").click().run()


def test_variant_sittings_are_recorded_and_the_next_new_variant_is_offered(tmp_path, monkeypatch):
    database, app = start(tmp_path, monkeypatch)
    open_subject(app)
    open_page(app, "Mock exam")
    assert next(radio for radio in app.radio if radio.key == "mock_exam_set").value == "variant"
    assert any("Variant 1 is new to you" in item.value for item in app.caption)
    sit_variant(app)
    assert len(app.exception) == 0
    assert app.header[0].value.startswith("Variant 1 · ")
    app.run()  # the sitting count above the form refreshes on the next interaction
    assert any("You have sat variant 1 1 time(s). Variant 2 is the next new one." in item.value for item in app.caption)

    sittings = StudyStore(database).list_sittings(DEMO_ID)
    assert len(sittings) == 1 and sittings[0]["exam_variant"] == 1 and sittings[0]["questions"] == 6

    button(app, "next_variant").click().run()
    assert next(item for item in app.number_input if item.key == "mock_variant").value == 2
    assert any("Variant 2 is new to you" in item.value for item in app.caption)

    open_page(app, "Progress")
    sittings_markup = next(item.value for item in app.markdown if "Variant 1" in item.value and 'class="activity"' in item.value)
    assert "6 questions" in sittings_markup


def test_export_is_offered_for_user_subjects_only(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch)
    create_subject(app, "Statistics 101")
    open_page(app, "Settings")
    button(app, "prepare_export").click().run()
    assert len(app.exception) == 0
    assert any(item.label == "Download subject archive" for item in app.get("download_button"))
    button(app, "back_to_library").click().run()
    assert any("Import a subject from another computer" in item.label for item in app.expander)
    open_subject(app)
    open_page(app, "Settings")
    assert not any(item.key == "prepare_export" for item in app.button)


def test_sample_subject_content_page_is_read_only(tmp_path, monkeypatch):
    _, app = start(tmp_path, monkeypatch)
    open_subject(app)
    open_page(app, "Content")
    assert any("Sample content: 4 topics" in item.value for item in app.success)
    assert app.subheader == [] or not any("Materials" in item.value for item in app.subheader)


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
