import os
import re
import sqlite3
import sys
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path
from uuid import uuid4

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from prepcanvas.catalog import diagnostic_questions as select_diagnostic_questions
from prepcanvas.catalog import get_topic, load_demo_subject
from prepcanvas.coaching import recommend_strategy
from prepcanvas.grading import grade_question, grade_questions
from prepcanvas.library import exam_countdown, group_subjects, last_activity
from prepcanvas.readiness import calculate_readiness, next_best_action
from prepcanvas.storage import StudyStore


st.set_page_config(page_title="PrepCanvas", page_icon="◉", layout="wide")

st.markdown(
    """
    <style>
    :root { --ink:#17211b; --muted:#66736b; --accent:#2f6b4f; --soft:#edf4ef; --warm:#f6f1e8; }
    .stApp { background: #fbfcfa; color: var(--ink); }
    [data-testid="stSidebar"] { background: #17211b; }
    [data-testid="stSidebar"] * { color: #f7faf7 !important; }
    [data-testid="stSidebar"] button { background:transparent; border:1px solid #4d6b5a; }
    [data-testid="stSidebar"] button:hover { border-color:#f7faf7; }
    .st-key-page [role="radiogroup"] { gap:.4rem; flex-wrap:wrap; margin-bottom:.5rem; }
    .st-key-page label[data-baseweb="radio"] { margin:0; padding:.35rem .9rem; border:1px solid #d5e1d9; border-radius:999px; background:white; cursor:pointer; }
    .st-key-page label[data-baseweb="radio"] > div:first-child { display:none; }
    .st-key-page label[data-baseweb="radio"]:has(input:checked) { background:var(--accent); border-color:var(--accent); }
    .st-key-page label[data-baseweb="radio"]:has(input:checked) p { color:white; }
    .welcome { margin:0 0 1.25rem; }
    .welcome h1 { margin:0 0 .25rem; }
    .welcome p { color:var(--muted); margin:0; }
    .card-title { font-weight:700; font-size:1.1rem; margin:0 0 .15rem; }
    .card-meta { color:var(--muted); font-size:.85rem; margin:.1rem 0; }
    .card-stats { display:flex; gap:1.25rem; margin:.6rem 0 .2rem; }
    .card-stats b { display:block; font-size:1.35rem; }
    .card-stats span { color:var(--muted); font-size:.75rem; }
    .badge { display:inline-block; background:var(--warm); color:#8a5a1c; border-radius:999px; padding:.1rem .5rem; font-size:.7rem; font-weight:700; margin-left:.4rem; vertical-align:middle; }
    .subject-bar { color:var(--muted); font-size:.85rem; }
    .metrics { display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:.75rem; margin:0 0 1rem; }
    .metrics.three { grid-template-columns:repeat(3, minmax(0, 1fr)); }
    .metric { background:white; border:1px solid #e1e8e3; padding:.9rem 1rem; border-radius:16px; min-width:0; }
    .metric .label { color:var(--muted); font-size:.85rem; }
    .metric .value { font-size:2rem; line-height:1.2; margin-top:.2rem; }
    .metric .hint { color:var(--muted); font-size:.75rem; margin-top:.3rem; }
    @media (max-width: 640px) {
      [data-testid="stMainBlockContainer"] { padding-top:1.5rem; }
      .metrics { grid-template-columns:repeat(2, minmax(0, 1fr)); gap:.5rem; }
      .metrics.three { gap:.5rem; }
      .metric { padding:.7rem .8rem; }
      .metric .value { font-size:1.5rem; }
      .hero { padding:1.2rem 1.25rem; }
      .hero h1 { font-size:1.75rem !important; line-height:1.2; }
    }
    .hero { padding:1.6rem 1.8rem; border-radius:24px; color:white; background:linear-gradient(125deg,#183f2d,#4d8064); margin-bottom:1.2rem; }
    .hero h1 { margin:0; font-size:2.5rem; }
    .hero p { max-width:720px; color:#e5f0e9; font-size:1.05rem; }
    .eyebrow { text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:700; opacity:.78; }
    .panel { background:white; border:1px solid #e1e8e3; border-radius:18px; padding:1.15rem 1.25rem; margin:.5rem 0 1rem; }
    .source { color:#68756d; font-size:.82rem; }
    .tag { display:inline-block; background:#edf4ef; color:#285a43; border-radius:999px; padding:.28rem .65rem; margin:.15rem .25rem .15rem 0; font-size:.8rem; font-weight:600; }
    .next-action { background:#f6f1e8; border-left:5px solid #c98b38; border-radius:12px; padding:1rem 1.2rem; margin-bottom:1.25rem; }
    [data-testid="stMainBlockContainer"] { padding-top:2.5rem; }
    .activity { display:flex; justify-content:space-between; gap:1rem; padding:.55rem 0; border-bottom:1px solid #e1e8e3; }
    .activity .what { min-width:0; }
    .activity .meta { color:var(--muted); font-size:.8rem; }
    .activity .score { font-weight:700; white-space:nowrap; }
    div.stButton > button, div.stFormSubmitButton > button { border-radius:999px; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_store(path: str) -> StudyStore:
    return StudyStore(Path(path))


default_database_path = ROOT_DIR / "data" / "local" / "prepcanvas.sqlite3"
store = get_store(str(os.environ.get("PREPCANVAS_DB_PATH", default_database_path)))
demo = load_demo_subject()
store.seed_demo_subject(demo)


def merged_subject(record: dict) -> dict:
    if record["id"] == demo["id"]:
        return {**demo, **record, "topics": demo["topics"], "questions": demo["questions"]}
    return {**record, "topics": [], "questions": []}


def material_label(key: str) -> str:
    return {
        "workbook": "Workbook",
        "practice_tests": "Practice tests",
        "sample_answers": "Sample answers",
        "notes": "Notes",
        "transcripts": "Session transcripts",
        "other": "Other materials",
    }.get(key, key.replace("_", " ").title())


def render_source(source: str):
    st.markdown(f'<div class="source">Source: {escape(source)}</div>', unsafe_allow_html=True)


def render_metrics(items: list):
    """Render metric cards as a grid: one row on desktop, two columns on phones."""
    cards = "".join(
        '<div class="metric">'
        f'<div class="label">{escape(label)}</div>'
        f'<div class="value">{escape(str(value))}</div>'
        + (f'<div class="hint">{escape(hint)}</div>' if hint else "")
        + "</div>"
        for label, value, hint in items
    )
    layout = "metrics three" if len(items) == 3 else "metrics"
    st.markdown(f'<div class="{layout}">{cards}</div>', unsafe_allow_html=True)


def render_topic_explanation(topic: dict, expandable_trap: bool = True):
    st.markdown(
        '<div class="panel"><div class="eyebrow">Core idea</div>'
        f'<h3>{escape(topic["title"])}</h3>{escape(topic["summary"])}</div>',
        unsafe_allow_html=True,
    )
    concepts = "".join(
        f'<span class="tag">{escape(item)}</span>'
        for item in topic["key_concepts"]
    )
    st.markdown(concepts, unsafe_allow_html=True)
    st.subheader("See it in context")
    st.write(topic["worked_example"])
    if expandable_trap:
        with st.expander("Reveal a common trap"):
            st.write(topic["common_mistake"])
    else:
        st.markdown("**Common trap**")
        st.write(topic["common_mistake"])


def render_feedback(question: dict, result: dict):
    if result["score"] == result["max_score"]:
        st.success(f'Correct · {result["score"]}/{result["max_score"]}')
    elif result["score"]:
        st.warning(f'Partly correct · {result["score"]}/{result["max_score"]}')
    else:
        st.error(f'Not yet · {result["score"]}/{result["max_score"]}')
    st.write(result["feedback"])
    if result["matched_points"]:
        st.write("**What you covered:** " + "; ".join(result["matched_points"]))
    if result["missing_points"] and question["type"] == "short_answer":
        st.write("**Add next time:** " + "; ".join(result["missing_points"]))
        st.write("**Model answer:** " + question["model_answer"])
    render_source(question["source"])


PAGES = ["Overview", "Diagnostic", "Learn", "Practice", "Mock exam", "Progress", "Settings"]


def open_subject(subject_id: str):
    st.session_state["subject_id"] = subject_id
    st.session_state["page"] = PAGES[0]
    st.session_state["view"] = "library"


def open_library(view: str = "library"):
    st.session_state["subject_id"] = None
    st.session_state["view"] = view


def render_subject_card(item: dict):
    record = merged_subject(item)
    item_attempts = store.list_attempts(item["id"])
    item_readiness = calculate_readiness(record, item_attempts)
    badge = '<span class="badge">Sample</span>' if item["is_demo"] else ""
    has_content = bool(record["topics"])
    stats = (
        f'<div class="card-stats"><div><b>{item_readiness["score"]}%</b><span>Readiness</span></div>'
        f'<div><b>{item_readiness["coverage"]}%</b><span>Topic coverage</span></div></div>'
        if has_content
        else '<div class="card-meta">Study content arrives with material upload.</div>'
    )
    with st.container(border=True):
        st.markdown(
            f'<div class="card-title">{escape(item["name"])}{badge}</div>'
            f'<div class="card-meta">{escape(exam_countdown(item.get("exam_date"), date.today()))} · '
            f'{escape(last_activity(item_attempts, datetime.now(timezone.utc)))}</div>{stats}',
            unsafe_allow_html=True,
        )
        label = "Continue" if item_attempts else "Open"
        st.button(label, key=f'open_{item["id"]}', type="primary", on_click=open_subject, args=(item["id"],))


def render_library(records: list):
    groups = group_subjects(records)
    summary = f'{len(groups["active"])} in progress · {len(groups["completed"])} completed'
    st.markdown(
        '<div class="welcome"><h1>Welcome to PrepCanvas</h1>'
        f"<p>Pick up where you left off, or add a subject for your next exam. {summary}.</p></div>",
        unsafe_allow_html=True,
    )
    st.subheader("In progress")
    columns = st.columns(3)
    with columns[0]:
        with st.container(border=True):
            st.markdown(
                '<div class="card-title">+ New subject</div>'
                '<div class="card-meta">Set an exam date and target, then record which materials you have.</div>',
                unsafe_allow_html=True,
            )
            st.button("New subject", key="new_subject", on_click=open_library, args=("new",))
    for index, item in enumerate(groups["active"], start=1):
        with columns[index % 3]:
            render_subject_card(item)
    if groups["completed"]:
        st.subheader("Completed")
        columns = st.columns(3)
        for index, item in enumerate(groups["completed"]):
            with columns[index % 3]:
                render_subject_card(item)


def render_new_subject(records: list):
    st.button("← All subjects", key="back_from_new", on_click=open_library)
    st.title("New subject")
    st.write(
        "Set up the subject now. Uploading and processing your own materials is planned for a later "
        "release; until then, the sample subject shows the full study flow."
    )
    with st.form("new_subject_form"):
        name = st.text_input("Subject name")
        exam_date = st.date_input("Exam date", value=None)
        target_score = st.slider("Target score", 50, 100, 80)
        st.write("Available materials")
        material_columns = st.columns(3)
        materials = {
            "workbook": material_columns[0].checkbox("Workbook"),
            "practice_tests": material_columns[1].checkbox("Practice tests"),
            "sample_answers": material_columns[2].checkbox("Sample answers"),
            "notes": material_columns[0].checkbox("Notes"),
            "transcripts": material_columns[1].checkbox("Session transcripts"),
            "other": material_columns[2].checkbox("Other materials"),
        }
        create_submitted = st.form_submit_button("Create subject", type="primary")
    if create_submitted:
        cleaned_name = name.strip()
        if not cleaned_name:
            st.warning("Enter a subject name before creating it.")
        elif any(item["name"].casefold() == cleaned_name.casefold() for item in records):
            st.error("A subject with this name already exists.")
        else:
            subject_id = re.sub(r"[^a-z0-9]+", "-", cleaned_name.lower()).strip("-")
            if not subject_id:
                subject_id = f"subject-{uuid4().hex[:8]}"
            if store.get_subject(subject_id):
                subject_id = f"{subject_id}-{uuid4().hex[:8]}"
            try:
                store.create_subject(
                    subject_id,
                    cleaned_name,
                    exam_date.isoformat() if exam_date else "",
                    target_score,
                    materials,
                )
                open_subject(subject_id)
                st.session_state["flash"] = (
                    f"Subject “{cleaned_name}” created. Material upload arrives in a later release; "
                    "until then, the sample subject shows the full study flow."
                )
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("Could not create the subject because its identifier already exists. Try again.")


if "flash" in st.session_state:
    st.toast(st.session_state.pop("flash"), icon="✅")

records = store.list_subjects()
subject_lookup = {item["id"]: item for item in records}

st.sidebar.markdown("## ◉ PrepCanvas")
st.sidebar.caption("Local-first exam preparation")
st.sidebar.button("All subjects", key="sidebar_library", on_click=open_library, width="stretch")

selected_id = st.session_state.get("subject_id")
if selected_id not in subject_lookup:
    if st.session_state.get("view") == "new":
        render_new_subject(records)
    else:
        render_library(records)
    st.stop()

# Inside a subject: a way back to the library, then the workspace switcher,
# which sits above the content so it stays reachable on phones.
back_column, name_column = st.columns([1, 4], vertical_alignment="center")
back_column.button("← All subjects", key="back_to_library", on_click=open_library)
name_column.markdown(
    f'<div class="subject-bar">{escape(subject_lookup[selected_id]["name"])}</div>', unsafe_allow_html=True
)
page = st.radio("Workspace", PAGES, key="page", horizontal=True, label_visibility="collapsed")

subject = merged_subject(subject_lookup[selected_id])
attempts = store.list_attempts(selected_id)
readiness = calculate_readiness(subject, attempts)
profile = store.get_profile(selected_id)


if page == "Overview":
    st.markdown(
        f"""
        <div class="hero">
          <div class="eyebrow">Your study command center</div>
          <h1>{escape(subject['name'])}</h1>
          <p>{escape(subject['description'] or 'Add materials and build a focused route to exam readiness.')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if readiness["is_ready"]:
        session_value, session_help = "Ready", "Target reached"
    elif readiness["estimated_sessions"] is None:
        session_value, session_help = "—", "Answer every topic first"
    else:
        session_value, session_help = f'≈ {readiness["estimated_sessions"]}', "Rough heuristic"
    render_metrics(
        [
            ("Readiness", f'{readiness["score"]}%', None),
            ("Topic coverage", f'{readiness["coverage"]}%', None),
            ("Target", f'{readiness["target"]}%', None),
            ("Est. sessions", session_value, session_help),
        ]
    )

    st.markdown(
        f'<div class="next-action"><b>Next best action</b><br>{escape(next_best_action(subject, readiness))}</div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("Topic map")
        if not subject["topics"]:
            st.info(
                "Your exam date, target, and material list are saved. Uploading and processing materials is planned "
                "for a later release; until then, switch to the demo subject in the sidebar to try every step."
            )
        for topic in subject["topics"]:
            mastery = readiness["topics"][topic["id"]]
            st.markdown(f"**{escape(topic['title'])}** · {mastery['mastery']}% mastery")
            st.progress(mastery["mastery"] / 100)
            st.caption(f'{mastery["evidence"]} of {mastery["questions"]} questions answered')
    with right:
        st.subheader("Coaching setup")
        if profile:
            st.markdown(
                f'<div class="panel"><b>{escape(profile["strategy_name"])}</b><br>'
                f'{escape(profile["description"])}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="panel"><b>No learning profile yet</b><br>Take the short diagnostic so PrepCanvas can choose a starting approach.</div>', unsafe_allow_html=True)
        st.subheader("Available materials")
        tags = "".join(
            f'<span class="tag">{material_label(key)}</span>'
            for key, available in subject["materials"].items()
            if available
        )
        st.markdown(tags or "No materials selected yet.", unsafe_allow_html=True)

elif page == "Diagnostic":
    st.title("Find your starting point")
    st.write("A short knowledge check plus your confidence level determines the first coaching strategy.")
    diagnostic_questions = select_diagnostic_questions(subject)
    if not diagnostic_questions:
        st.info("Add content to this subject before running a diagnostic. The synthetic demo subject is ready to use.")
    else:
        with st.form("diagnostic_form"):
            diagnostic_answers = {}
            for question in diagnostic_questions:
                st.markdown(f'**{question["prompt"]}**')
                diagnostic_answers[question["id"]] = st.radio(
                    "Choose one",
                    question["options"],
                    index=None,
                    key=f'diagnostic_{question["id"]}',
                    label_visibility="collapsed",
                )
            confidence = st.slider("How confident do you feel about this subject?", 1, 5, 3)
            diagnostic_submitted = st.form_submit_button("Build my learning profile", type="primary")
        if diagnostic_submitted:
            unanswered = [question for question in diagnostic_questions if not diagnostic_answers.get(question["id"])]
            if unanswered:
                st.warning("Answer every diagnostic question before building your learning profile.")
            else:
                graded = grade_questions(diagnostic_questions, diagnostic_answers)
                ratio = graded["score"] / graded["max_score"] if graded["max_score"] else 0
                strategy = recommend_strategy(ratio, confidence)
                for result in graded["results"]:
                    store.save_attempt(selected_id, "diagnostic", result, confidence)
                store.save_profile(selected_id, strategy, ratio, confidence)
                st.success(f'Your starting strategy: {strategy["name"]}')
                st.write(strategy["description"])
                st.write(f'Diagnostic score: {graded["score"]}/{graded["max_score"]}')

elif page == "Learn":
    st.title("Coach a topic")
    if not subject["topics"]:
        st.info("Learning content will appear after source materials are processed.")
    else:
        topic_id = st.selectbox(
            "Topic",
            [topic["id"] for topic in subject["topics"]],
            format_func=lambda value: get_topic(subject, value)["title"],
        )
        topic = get_topic(subject, topic_id)
        strategy_id = profile["strategy_id"] if profile else "guided_foundations"
        if profile:
            st.caption(f'Current strategy: {profile["strategy_name"]}')
        else:
            st.info("Using guided foundations by default. Complete the diagnostic to personalize the sequence.")
        if strategy_id == "guided_foundations":
            render_topic_explanation(topic)
        elif strategy_id == "coach_and_recall":
            st.info("Active recall first: attempt the checkpoint before reviewing the explanation.")
        else:
            st.info("Exam simulation: answer without hints, then open the review material if needed.")
        st.subheader("Coach's checkpoint")
        st.info(topic["coach_question"])
        topic_questions = [q for q in subject["questions"] if q["topic_id"] == topic_id and q["type"] == "short_answer"]
        submitted = False
        if topic_questions:
            question = topic_questions[0]
            with st.form(f'coach_{topic_id}'):
                answer = st.text_area(question["prompt"], height=130)
                submitted = st.form_submit_button("Check my understanding", type="primary")
            if submitted:
                if not answer.strip():
                    st.warning("Write an answer before checking your understanding.")
                else:
                    result = grade_question(question, answer)
                    store.save_attempt(selected_id, "coaching", result)
                    render_feedback(question, result)
        if strategy_id != "guided_foundations":
            with st.expander("Review the explanation and example", expanded=submitted):
                render_topic_explanation(topic, expandable_trap=False)
        render_source(topic["source"])

elif page == "Practice":
    st.title("Targeted practice")
    if not subject["questions"]:
        st.info("Practice questions will appear after source materials are processed.")
    else:
        topic_options = ["all"] + [topic["id"] for topic in subject["topics"]]
        chosen_topic = st.selectbox(
            "Focus",
            topic_options,
            format_func=lambda value: "All topics" if value == "all" else get_topic(subject, value)["title"],
        )
        questions = subject["questions"] if chosen_topic == "all" else [q for q in subject["questions"] if q["topic_id"] == chosen_topic]
        question_id = st.selectbox(
            "Question",
            [q["id"] for q in questions],
            format_func=lambda value: next(q for q in questions if q["id"] == value)["prompt"],
        )
        question = next(q for q in questions if q["id"] == question_id)
        with st.form(f'practice_{question_id}'):
            if question["type"] == "multiple_choice":
                answer = st.radio("Your answer", question["options"], index=None)
            else:
                answer = st.text_area("Your answer", height=150)
            submitted = st.form_submit_button("Check answer", type="primary")
        if submitted:
            if not answer or not str(answer).strip():
                st.warning("Choose or write an answer before submitting.")
            else:
                result = grade_question(question, answer)
                store.save_attempt(selected_id, "practice", result)
                render_feedback(question, result)

elif page == "Mock exam":
    st.title("Mock exam")
    st.write("Feedback stays hidden until the full attempt is submitted.")
    if not subject["questions"]:
        st.info("A mock exam will be available after questions are added.")
    else:
        with st.form("mock_exam"):
            exam_answers = {}
            for index, question in enumerate(subject["questions"], start=1):
                st.markdown(f'**{index}. {question["prompt"]}** · {question["points"]} pt')
                if question["type"] == "multiple_choice":
                    exam_answers[question["id"]] = st.radio(
                        "Answer",
                        question["options"],
                        index=None,
                        key=f'exam_{question["id"]}',
                        label_visibility="collapsed",
                    )
                else:
                    exam_answers[question["id"]] = st.text_area(
                        "Answer",
                        key=f'exam_{question["id"]}',
                        label_visibility="collapsed",
                    )
            exam_submitted = st.form_submit_button("Submit mock exam", type="primary")
        if exam_submitted:
            unanswered = [
                question
                for question in subject["questions"]
                if not exam_answers.get(question["id"]) or not str(exam_answers[question["id"]]).strip()
            ]
            if unanswered:
                st.warning(f"Answer all questions before submitting the mock exam ({len(unanswered)} remaining).")
            else:
                graded = grade_questions(subject["questions"], exam_answers)
                for result in graded["results"]:
                    store.save_attempt(selected_id, "mock_exam", result)
                percentage = round(graded["score"] / graded["max_score"] * 100) if graded["max_score"] else 0
                st.header(f'{percentage}% · {graded["score"]}/{graded["max_score"]}')
                for question, result in zip(subject["questions"], graded["results"]):
                    with st.expander(f'{question["prompt"]} · {result["score"]}/{result["max_score"]}'):
                        render_feedback(question, result)

elif page == "Progress":
    st.title("Progress")
    if not attempts:
        st.info("Complete the diagnostic or a practice question to start tracking progress.")
    else:
        render_metrics(
            [
                ("Readiness", f'{readiness["score"]}%', None),
                ("Coverage", f'{readiness["coverage"]}%', None),
                ("Saved answers", len(attempts), None),
            ]
        )
        chart_data = {
            topic["title"]: readiness["topics"].get(topic["id"], {}).get("mastery", 0)
            for topic in subject["topics"]
        }
        if chart_data:
            st.subheader("Mastery by topic")
            for topic_name, mastery in chart_data.items():
                st.markdown(f"**{topic_name}** · {mastery}%")
                st.progress(mastery / 100)
        st.subheader("Recent activity")
        topic_titles = {topic["id"]: topic["title"] for topic in subject["topics"]}
        prompts = {question["id"]: question["prompt"] for question in subject["questions"]}
        rows = []
        for row in attempts[:12]:
            ratio = round(row["score"] / row["max_score"] * 100) if row["max_score"] else 0
            answered_at = datetime.fromisoformat(row["created_at"]).astimezone().strftime("%d %b, %H:%M")
            what = prompts.get(row["question_id"], "Answer")
            meta = " · ".join(
                part
                for part in (topic_titles.get(row["topic_id"]), row["mode"].replace("_", " ").capitalize(), answered_at)
                if part
            )
            rows.append(
                f'<div class="activity"><div class="what">{escape(what)}<div class="meta">{escape(meta)}</div></div>'
                f'<div class="score">{ratio}%</div></div>'
            )
        st.markdown("".join(rows), unsafe_allow_html=True)
        st.caption("Readiness is a transparent heuristic based on recent topic evidence. It is not a guaranteed exam result.")

else:
    st.title("Subject settings")
    item = subject_lookup[selected_id]
    exam_label = exam_countdown(item.get("exam_date"), date.today())
    selected_materials = [material_label(key) for key, value in item["materials"].items() if value]
    st.markdown(
        f'<div class="panel"><b>{escape(item["name"])}</b><br>{escape(exam_label)} · target {item["target_score"]}%<br>'
        f'<span class="source">{escape(", ".join(selected_materials) or "No materials recorded")}</span></div>',
        unsafe_allow_html=True,
    )

    st.subheader("Status")
    if item.get("status") == "completed":
        st.write("This subject is in your **Completed** list.")
        if st.button("Reopen subject", key="reopen_subject"):
            store.set_status(selected_id, "active")
            st.session_state["flash"] = f'“{item["name"]}” is back in progress.'
            st.rerun()
    else:
        st.write("Finished with this exam? Move the subject to your **Completed** list; its progress is kept.")
        if st.button("Mark as completed", key="complete_subject"):
            store.set_status(selected_id, "completed")
            st.session_state["flash"] = f'“{item["name"]}” moved to Completed.'
            open_library()
            st.rerun()

    st.subheader("Manage data")
    removes = "its saved answers and coaching profile" if item["is_demo"] else "the subject and all of its progress"
    confirmed = st.checkbox(f"I understand this permanently removes {removes}.", key=f'confirm_{item["id"]}')
    reset_column, delete_column = st.columns(2)
    if reset_column.button("Reset progress", key=f'reset_{item["id"]}', disabled=not confirmed):
        store.reset_progress(item["id"])
        st.session_state["flash"] = f'Progress for “{item["name"]}” was reset.'
        st.rerun()
    if not item["is_demo"] and delete_column.button(
        "Delete subject", key=f'delete_{item["id"]}', type="primary", disabled=not confirmed
    ):
        store.delete_subject(item["id"])
        open_library()
        st.session_state["flash"] = f'Subject “{item["name"]}” was deleted.'
        st.rerun()
