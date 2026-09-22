import os
import re
import sqlite3
import sys
from html import escape
from pathlib import Path
from uuid import uuid4

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from prepcanvas.catalog import get_topic, load_demo_subject
from prepcanvas.coaching import recommend_strategy
from prepcanvas.grading import grade_question, grade_questions
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
    [data-testid="stSidebar"] div[data-baseweb="select"] * { color: #17211b !important; }
    [data-testid="stMetric"] { background:white; border:1px solid #e1e8e3; padding:1rem; border-radius:16px; }
    .hero { padding:1.6rem 1.8rem; border-radius:24px; color:white; background:linear-gradient(125deg,#183f2d,#4d8064); margin-bottom:1.2rem; }
    .hero h1 { margin:0; font-size:2.5rem; }
    .hero p { max-width:720px; color:#e5f0e9; font-size:1.05rem; }
    .eyebrow { text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:700; opacity:.78; }
    .panel { background:white; border:1px solid #e1e8e3; border-radius:18px; padding:1.15rem 1.25rem; margin:.5rem 0 1rem; }
    .source { color:#68756d; font-size:.82rem; }
    .tag { display:inline-block; background:#edf4ef; color:#285a43; border-radius:999px; padding:.28rem .65rem; margin:.15rem .25rem .15rem 0; font-size:.8rem; font-weight:600; }
    .next-action { background:#f6f1e8; border-left:5px solid #c98b38; border-radius:12px; padding:1rem 1.2rem; }
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


records = store.list_subjects()
subject_lookup = {item["id"]: item for item in records}

st.sidebar.markdown("## ◉ PrepCanvas")
st.sidebar.caption("Local-first exam preparation")
selected_id = st.sidebar.selectbox(
    "Subject",
    options=list(subject_lookup),
    format_func=lambda value: subject_lookup[value]["name"],
)
page = st.sidebar.radio(
    "Workspace",
    ["Overview", "Diagnostic", "Learn", "Practice", "Mock exam", "Progress", "Subjects"],
)

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
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Readiness", f'{readiness["score"]}%')
    col2.metric("Topic coverage", f'{readiness["coverage"]}%')
    col3.metric("Target", f'{readiness["target"]}%')
    session_value = "Ready" if readiness["is_ready"] else f'≈ {readiness["estimated_sessions"]}'
    col4.metric("Focused sessions", session_value, help="A rough heuristic, not a guarantee.")

    st.markdown(
        f'<div class="next-action"><b>Next best action</b><br>{escape(next_best_action(subject, readiness))}</div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("Topic map")
        if not subject["topics"]:
            st.info("This subject is ready for materials, but content ingestion is not part of the first public demo yet.")
        for topic in subject["topics"]:
            mastery = readiness["topics"].get(topic["id"], {"mastery": 0, "evidence": 0})
            st.markdown(f"**{escape(topic['title'])}** · {mastery['mastery']}% mastery")
            st.progress(mastery["mastery"] / 100)
            st.caption(f'{mastery["evidence"]} recent evidence points')
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
    if not subject["questions"]:
        st.info("Add content to this subject before running a diagnostic. The synthetic demo subject is ready to use.")
    else:
        diagnostic_questions = [
            next(q for q in subject["questions"] if q["topic_id"] == topic["id"] and q["type"] == "multiple_choice")
            for topic in subject["topics"]
        ]
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
        col1, col2, col3 = st.columns(3)
        col1.metric("Readiness", f'{readiness["score"]}%')
        col2.metric("Coverage", f'{readiness["coverage"]}%')
        col3.metric("Saved answers", len(attempts))
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
        for row in attempts[:12]:
            ratio = round(row["score"] / row["max_score"] * 100) if row["max_score"] else 0
            st.write(f'{row["created_at"][:16].replace("T", " ")} · {row["mode"].replace("_", " ").title()} · {ratio}%')
        st.caption("Readiness is a transparent heuristic based on recent topic evidence. It is not a guaranteed exam result.")

else:
    st.title("Subjects and materials")
    st.write("Create a subject and record which source types are available. File ingestion comes in the next product iteration.")
    with st.form("new_subject"):
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
                st.success("Subject created. Select it from the sidebar.")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("Could not create the subject because its identifier already exists. Try again.")

    st.subheader("Current subjects")
    for item in records:
        demo_label = " · demo" if item["is_demo"] else ""
        st.markdown(f'**{item["name"]}**{demo_label}')
        selected_materials = [material_label(key) for key, value in item["materials"].items() if value]
        st.caption(", ".join(selected_materials) or "No materials selected")
