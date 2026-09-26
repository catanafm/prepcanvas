import os
import random
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
from prepcanvas.exams import available_sets, describe, exam_questions, next_variant
from prepcanvas.grading import grade_question, grade_questions
from prepcanvas.library import exam_countdown, group_subjects, last_activity
from prepcanvas.packages import MATERIAL_SUFFIXES, SubjectFiles, content_summary
from prepcanvas.practice import next_question, question_status, random_question, remaining
from prepcanvas.prompts import SKILL_NAME, agent_request, chat_prompt, display_path
from prepcanvas.readiness import calculate_readiness, next_best_action
from prepcanvas.storage import StudyStore
from prepcanvas.transfer import ArchiveError, SubjectExists, export_subject, import_subject, inspect_archive


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
    .side-subject { margin:1.25rem 0 .5rem; padding-top:1rem; border-top:1px solid #4d6b5a; }
    .side-subject b { font-size:1.05rem; }
    .side-subject .meta { font-size:.8rem; opacity:.75; margin-top:.2rem; }
    .side-stats { display:flex; gap:1.25rem; margin:.6rem 0; }
    .side-stats b { display:block; font-size:1.3rem; }
    .side-stats span { font-size:.72rem; opacity:.75; }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_store(path: str) -> StudyStore:
    # Created on every run on purpose: a cached instance would outlive code reloads and
    # miss methods added in a newer version. Opening SQLite here costs milliseconds.
    return StudyStore(Path(path))


default_database_path = ROOT_DIR / "data" / "local" / "prepcanvas.sqlite3"
store = get_store(str(os.environ.get("PREPCANVAS_DB_PATH", default_database_path)))
files = SubjectFiles(Path(os.environ.get("PREPCANVAS_PRIVATE_DIR", ROOT_DIR / "data" / "private")))
demo = load_demo_subject()
store.ensure_sample_subject(demo)


def load_content(record: dict) -> dict:
    """The study content of a subject: the bundled sample, or the validated private package."""
    if record["id"] == demo["id"]:
        return {"state": "sample", "package": demo, "issues": [], "path": None}
    return files.load_package(record["id"])


def merged_subject(record: dict, content: dict = None) -> dict:
    """Subject metadata from the database plus topics and questions from its package."""
    package = (content or load_content(record))["package"]
    if package is None:
        return {**record, "topics": [], "questions": [], "sources": []}
    merged = {
        **package,
        **record,
        "topics": package["topics"],
        "questions": package["questions"],
        "sources": package.get("sources", []),
    }
    if not merged.get("description"):
        merged["description"] = package.get("description", "")
    return merged


def material_names(item: dict, subject: dict) -> list:
    """What the subject was, or will be, built from: sample sources or uploaded files."""
    if item["is_demo"]:
        return [source["title"] for source in subject.get("sources", [])]
    return [material["name"] for material in files.list_materials(item["id"])]


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


# Ordered by how often a learner needs them: study modes first, one-off setup pages last.
PAGES = ["Overview", "Learn", "Practice", "Mock exam", "Progress", "Diagnostic", "Content", "Settings"]


def open_subject(subject_id: str):
    st.session_state["subject_id"] = subject_id
    st.session_state["page"] = PAGES[0]
    st.session_state["view"] = "library"


def open_library(view: str = "library"):
    st.session_state["subject_id"] = None
    st.session_state["view"] = view


def go_to_page(page: str):
    st.session_state["page"] = page


def render_subject_card(item: dict):
    content = load_content(item)
    record = merged_subject(item, content)
    item_attempts = store.list_attempts(item["id"])
    item_readiness = calculate_readiness(record, item_attempts)
    badge = '<span class="badge">Sample</span>' if item["is_demo"] else ""
    has_content = bool(record["topics"])
    stats = (
        f'<div class="card-stats"><div><b>{item_readiness["score"]}%</b><span>Readiness</span></div>'
        f'<div><b>{item_readiness["coverage"]}%</b><span>Topic coverage</span></div></div>'
        if has_content
        else f'<div class="card-meta">{escape(content_hint(item, content))}</div>'
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


def content_hint(item: dict, content: dict) -> str:
    """One line that tells a learner what a subject without content needs next."""
    if content["state"] == "invalid":
        return "Study content has errors. Open Content to see them."
    if files.list_materials(item["id"]):
        return "Materials added. Build the study content next."
    return "No study content yet. Add materials to get started."


def restore_sample():
    store.restore_sample_subject(demo)
    open_subject(demo["id"])
    st.session_state["flash"] = "Sample subject added. Explore every step with synthetic content."


def render_empty_library():
    st.markdown(
        '<div class="welcome"><h1>Welcome to PrepCanvas</h1>'
        "<p>Plan and practise for your exams in one private workspace on this computer.</p></div>",
        unsafe_allow_html=True,
    )
    create_column, sample_column = st.columns(2)
    with create_column:
        with st.container(border=True):
            st.markdown(
                '<div class="card-title">Create your first subject</div>'
                '<div class="card-meta">Set an exam date and target, then build study content from your own materials.</div>',
                unsafe_allow_html=True,
            )
            st.button("Create your first subject", key="new_subject", type="primary", on_click=open_library, args=("new",))
    with sample_column:
        with st.container(border=True):
            st.markdown(
                '<div class="card-title">Explore the sample subject</div>'
                '<div class="card-meta">Try the diagnostic, coaching, practice, and mock exam with synthetic content.</div>',
                unsafe_allow_html=True,
            )
            st.button("Explore the sample subject", key="add_sample", on_click=restore_sample)


def render_library(records: list):
    if not records:
        render_empty_library()
        return
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
                '<div class="card-meta">Set an exam date and target, then build study content from your own materials.</div>',
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
    if store.sample_removed():
        st.caption("Want to see how PrepCanvas works with ready-made content?")
        st.button("Add sample subject", key="add_sample", type="tertiary", on_click=restore_sample)
    render_import()


def render_import():
    """Restore a subject exported from another computer."""
    with st.expander("Import a subject from another computer"):
        st.caption("Choose a subject archive exported from PrepCanvas Settings. Materials, content, and progress come with it.")
        with st.form("import_form", clear_on_submit=True):
            upload = st.file_uploader("Subject archive", type=["zip"])
            replace = st.checkbox("Replace a subject with the same id, including its progress")
            submitted = st.form_submit_button("Import subject")
        if submitted:
            if upload is None:
                st.warning("Choose an archive first.")
                return
            data = upload.getvalue()
            try:
                summary = inspect_archive(data)
                subject_id = import_subject(store, files, data, replace=replace)
            except ArchiveError as error:
                st.error(str(error))
            except SubjectExists as error:
                st.error(f"A subject with id “{error}” already exists. Tick the replace option to overwrite it, including its progress.")
            else:
                open_subject(subject_id)
                st.session_state["flash"] = (
                    f'Imported “{summary["name"]}”: {summary["materials"]} material file(s), '
                    f'{"study content" if summary["has_package"] else "no content yet"}, {summary["attempts"]} saved answers.'
                )
                st.rerun()


def render_new_subject(records: list):
    st.button("← All subjects", key="back_from_new", on_click=open_library)
    st.title("New subject")
    st.write(
        "Name the subject and set your goal. In the next step you add your materials and build the study "
        "content, topics, questions, and rubrics, with your own AI assistant. Everything stays on this computer."
    )
    with st.form("new_subject_form"):
        name = st.text_input("Subject name")
        exam_date = st.date_input("Exam date", value=None)
        target_score = st.slider("Target score", 50, 100, 80)
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
                    {},
                )
                files.write_brief(store.get_subject(subject_id))
                open_subject(subject_id)
                go_to_page("Content")
                st.session_state["flash"] = (
                    f"Subject “{cleaned_name}” created. Next: add your materials and build its study content."
                )
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("Could not create the subject because its identifier already exists. Try again.")


def render_needs_content(reason: str):
    st.info(f"{reason} This subject has none yet.")
    st.button("Set up study content", key="needs_content", type="primary", on_click=go_to_page, args=("Content",))


def package_summary_line(content: dict) -> str:
    if content["state"] == "valid":
        summary = content_summary(content["package"])
        return (
            f'{summary["topics"]} topics · {summary["questions"]} questions '
            f'({summary["source"]} from your materials, {summary["generated"]} generated)'
        )
    if content["state"] == "invalid":
        errors = sum(1 for issue in content["issues"] if issue["level"] == "error")
        return f"package.json has {errors} error(s) and is not loaded"
    return "no package.json yet"


def render_setup_checklist(item: dict, content: dict):
    """Overview panel for a subject without content: what exists, what is missing, where to go."""
    materials = files.list_materials(item["id"])
    materials_line = f'{len(materials)} file(s) added' if materials else "no files yet"
    if content["state"] == "invalid":
        next_step = "Open Content to see the validation errors and fix the package."
    elif materials:
        next_step = "Build the study content with your AI assistant, then check it on the Content page."
    else:
        next_step = "Add your workbook, practice exam, answer key, or notes on the Content page."
    st.markdown(
        '<div class="panel"><b>Set up study content</b><br>'
        f'<span class="source">1 · Materials: {escape(materials_line)}<br>'
        f'2 · Study content: {escape(package_summary_line(content))}<br>'
        f'3 · Study: diagnostic, learning, practice, and mock exam unlock once the content loads</span><br><br>'
        f'{escape(next_step)}</div>',
        unsafe_allow_html=True,
    )
    st.button("Open Content", key="open_content", type="primary", on_click=go_to_page, args=("Content",))


def render_issues(issues: list):
    for issue in issues:
        line = f'`{issue["path"]}` {issue["message"]}'
        if issue["level"] == "error":
            st.error(line)
        else:
            st.warning(line)


def render_content_review(subject: dict):
    """Read-only review of every topic and question, so the learner can spot mistakes before studying."""
    with st.expander("Review topics and questions"):
        for topic in subject["topics"]:
            st.markdown(f'**{escape(topic["title"])}** · {escape(topic["source"])}')
            st.caption(", ".join(topic["key_concepts"]))
            for question in (q for q in subject["questions"] if q["topic_id"] == topic["id"]):
                kind = "Multiple choice" if question["type"] == "multiple_choice" else "Short answer"
                origin = "from materials" if question.get("origin") == "source" else "generated"
                st.markdown(
                    f'- {escape(question["prompt"])}  \n'
                    f'  <span class="source">{kind} · {question["points"]} pt · {origin} · {escape(question["source"])}</span>',
                    unsafe_allow_html=True,
                )


def render_materials_section(item: dict):
    st.subheader("1 · Materials")
    st.caption(
        f"Files are stored in {display_path(files.materials_dir(item['id']))} on this computer. PrepCanvas itself never uploads them anywhere."
    )
    with st.form("materials_form", clear_on_submit=True):
        uploads = st.file_uploader(
            "Add your workbook, practice exam, answer key, or notes",
            type=[suffix.lstrip(".") for suffix in MATERIAL_SUFFIXES],
            accept_multiple_files=True,
        )
        add_submitted = st.form_submit_button("Add files")
    if add_submitted:
        saved, problems = [], []
        for upload in uploads or []:
            try:
                saved.append(files.save_material(item["id"], upload.name, upload.getvalue()).name)
            except ValueError as error:
                problems.append(str(error))
        for problem in problems:
            st.error(problem)
        if saved:
            st.session_state["flash"] = f'Added {len(saved)} file(s): {", ".join(saved)}.'
            st.rerun()
        elif not problems:
            st.warning("Choose at least one file first.")
    materials = files.list_materials(item["id"])
    if not materials:
        st.info("No files yet. PDF, TXT, Markdown, and DOCX files up to 25 MB each are accepted.")
    for material in materials:
        name_column, remove_column = st.columns([5, 1], vertical_alignment="center")
        name_column.markdown(f'{escape(material["name"])} <span class="source">· {material["bytes"] // 1024} KB</span>', unsafe_allow_html=True)
        if remove_column.button("Remove", key=f'remove_{material["name"]}', type="tertiary"):
            files.remove_material(item["id"], material["name"])
            st.rerun()
    return materials


def render_build_section(item: dict, materials: list, content: dict):
    st.subheader("2 · Build the study content")
    st.write(
        "An AI assistant reads your materials and writes `package.json`: topics, questions taken from your practice "
        "exam, similar new questions, and rubrics. Use whichever assistant you already have; no API key is needed."
    )
    st.caption(
        "Privacy: PrepCanvas sends nothing. The assistant you choose receives your materials under your own account, "
        "so pick one whose data handling you accept."
    )
    agent_tab, chat_tab, manual_tab = st.tabs(["Coding agent in a terminal", "Chat assistant", "By hand"])
    with agent_tab:
        st.markdown(
            "1. Open a terminal in the PrepCanvas folder.\n"
            "2. Start your agent: `claude`, `codex`, `gemini`, or any agent that reads `AGENTS.md`.\n"
            "3. Ask it to build the subject:"
        )
        st.code(agent_request(item["id"], files.subject_dir(item["id"])), language="text")
        st.markdown(
            f"The `{SKILL_NAME}` skill in this repository tells the agent how to read the materials, write the package, "
            "and run the validator until it passes. When it is done, return here and press **Check again**."
        )
    with chat_tab:
        brief = files.read_brief(item["id"])
        if brief is None:
            files.write_brief(item)
            brief = files.read_brief(item["id"])
        st.markdown(
            "1. Attach your materials to a new chat in ChatGPT, Claude, Gemini, or another assistant.\n"
            "2. Paste this prompt. It contains the full package schema.\n"
            "3. Save the JSON reply as `package.json` and import it below."
        )
        with st.expander("Show the prompt"):
            st.code(chat_prompt(brief, materials, files.subject_dir(item["id"])), language="markdown")
        with st.form("package_form", clear_on_submit=True):
            package_upload = st.file_uploader("Import package.json", type=["json"])
            import_submitted = st.form_submit_button("Import package")
        if import_submitted:
            if package_upload is None:
                st.warning("Choose the package.json file first.")
            else:
                files.save_package(item["id"], package_upload.getvalue())
                st.session_state["flash"] = "Package imported. Check the validation result below."
                st.rerun()
    with manual_tab:
        st.markdown(
            f"Write `{display_path(files.package_path(item['id']))}` yourself, following "
            "[docs/subject-package.md](https://github.com/catanafm/prepcanvas/blob/main/docs/subject-package.md), "
            "and validate it with:"
        )
        st.code(f"PYTHONPATH=src python -m prepcanvas validate {display_path(files.package_path(item['id']))}", language="bash")


def render_result_section(item: dict, subject: dict, content: dict):
    st.subheader("3 · Check the result")
    st.button("Check again", key="check_content")
    if content["state"] == "missing":
        st.info(f"No package yet. It is expected at {display_path(files.package_path(item['id']))}.")
        return
    if content["state"] == "invalid":
        st.error("The package could not be loaded. Fix these issues, or ask your assistant to, and check again.")
        render_issues(content["issues"])
        return
    st.success(f'Study content loaded: {package_summary_line(content)}.')
    if content["issues"]:
        st.caption("Warnings do not block studying, but fixing them gives better diagnostics and readiness estimates.")
        render_issues(content["issues"])
    render_content_review(subject)
    st.button("Start with the diagnostic", key="start_diagnostic", type="primary", on_click=go_to_page, args=("Diagnostic",))


def render_content_page(item: dict, subject: dict, content: dict):
    st.title("Study content")
    if item["is_demo"]:
        st.write(
            "The sample subject ships with synthetic content built from one synthetic workbook. Your own subjects "
            "get their content from a package you build with your AI assistant from your own materials."
        )
        st.success(f"Sample content: {package_summary_line({**content, 'state': 'valid'})}.")
        render_content_review(subject)
        return
    st.write(
        "Study content is built once, outside the app, from your own materials. After that, everything in PrepCanvas "
        "works locally: grading, readiness, and coaching need no AI at all."
    )
    materials = render_materials_section(item)
    if content["state"] == "valid":
        with st.expander("Rebuild or extend the content"):
            render_build_section(item, materials, content)
    else:
        render_build_section(item, materials, content)
    render_result_section(item, subject, content)


EXAM_SET_LABELS = {
    "source": "Original practice exam",
    "variant": "Numbered variant from the question pool",
    "all": "Every question",
}


def set_variant(value: int):
    st.session_state["mock_variant"] = value


def select_exam(subject: dict, sittings: list) -> tuple:
    """Let the learner pick the original exam, a numbered variant, or everything; returns (set, variant, questions)."""
    sets = available_sets(subject)
    if len(sets) == 1:
        exam_set = sets[0]
    else:
        exam_set = st.radio("Exam set", sets, format_func=EXAM_SET_LABELS.get, horizontal=True, key="mock_exam_set")
    variant = None
    if exam_set == "variant":
        sat = sorted({row["exam_variant"] for row in sittings if row["exam_set"] == "variant"})
        st.session_state.setdefault("mock_variant", next_variant(sat))
        number_column, next_column, random_column = st.columns([1, 1, 1], vertical_alignment="bottom")
        variant = number_column.number_input("Variant", 1, 99, key="mock_variant")
        next_column.button("Next new variant", key="next_variant", on_click=set_variant, args=(next_variant(sat),))
        random_column.button("Random variant", key="random_variant", on_click=set_variant, args=(random.randint(1, 99),))
        if variant in sat:
            times = sum(1 for row in sittings if row["exam_set"] == "variant" and row["exam_variant"] == variant)
            st.caption(f"You have sat variant {variant} {times} time(s). Variant {next_variant(sat)} is the next new one.")
        else:
            st.caption(f"Variant {variant} is new to you. Variants share a question pool, so some questions recur.")
    questions = exam_questions(subject, exam_set, variant or 1)
    st.caption(describe(questions))
    return exam_set, variant, questions


def sitting_label(row: dict) -> str:
    if row["exam_set"] == "variant":
        return f'Variant {row["exam_variant"]}'
    return EXAM_SET_LABELS.get(row["exam_set"] or "", "Mock exam")


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

content = load_content(subject_lookup[selected_id])
subject = merged_subject(subject_lookup[selected_id], content)
attempts = store.list_attempts(selected_id)
readiness = calculate_readiness(subject, attempts)
profile = store.get_profile(selected_id)

st.sidebar.markdown(
    f'<div class="side-subject"><div class="eyebrow">Subject</div><b>{escape(subject["name"])}</b>'
    f'<div class="meta">{escape(exam_countdown(subject.get("exam_date"), date.today()))} · '
    f'{escape(last_activity(attempts, datetime.now(timezone.utc)))}</div>'
    f'<div class="side-stats"><div><b>{readiness["score"]}%</b><span>Readiness</span></div>'
    f'<div><b>{readiness["coverage"]}%</b><span>Coverage</span></div>'
    f'<div><b>{readiness["target"]}%</b><span>Target</span></div></div></div>',
    unsafe_allow_html=True,
)


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
            render_setup_checklist(subject_lookup[selected_id], content)
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
        st.subheader("Materials")
        tags = "".join(f'<span class="tag">{escape(name)}</span>' for name in material_names(subject_lookup[selected_id], subject))
        st.markdown(tags or "No materials yet. Add them on the Content page.", unsafe_allow_html=True)

elif page == "Content":
    render_content_page(subject_lookup[selected_id], subject, content)

elif page == "Diagnostic":
    st.title("Find your starting point")
    st.write("A short knowledge check plus your confidence level determines the first coaching strategy.")
    diagnostic_questions = select_diagnostic_questions(subject)
    if not diagnostic_questions:
        render_needs_content("The diagnostic uses the multiple-choice questions of your study content.")
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
        render_needs_content("Topic explanations come from your study content.")
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
        render_needs_content("Practice questions come from your study content.")
    else:
        topic_options = ["all"] + [topic["id"] for topic in subject["topics"]]
        chosen_topic = st.selectbox(
            "Focus",
            topic_options,
            format_func=lambda value: "All topics" if value == "all" else get_topic(subject, value)["title"],
            key="practice_focus",
            on_change=lambda: st.session_state.pop("practice_question", None),
        )
        questions = subject["questions"] if chosen_topic == "all" else [q for q in subject["questions"] if q["topic_id"] == chosen_topic]
        known = {q["id"] for q in questions}
        if st.session_state.get("practice_question") not in known:
            st.session_state["practice_question"] = next_question(questions, attempts)["id"]
        question = next(q for q in questions if q["id"] == st.session_state["practice_question"])
        position = next(index for index, q in enumerate(questions, start=1) if q["id"] == question["id"])
        st.markdown(
            f'**Question {position} of {len(questions)}** · {escape(question_status(question, attempts))} · '
            f'{remaining(questions, attempts)} still unanswered in this focus'
        )
        st.markdown(f'<div class="panel">{escape(question["prompt"])}</div>', unsafe_allow_html=True)
        with st.form(f'practice_{question["id"]}'):
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
        next_column, random_column = st.columns([1, 1])
        next_column.button(
            "Next question",
            key="next_question",
            type="primary" if submitted else "secondary",
            on_click=lambda: st.session_state.update(
                practice_question=next_question(questions, store.list_attempts(selected_id), question["id"])["id"]
            ),
        )
        random_column.button(
            "Random question",
            key="random_question",
            on_click=lambda: st.session_state.update(practice_question=random_question(questions, question["id"])["id"]),
        )

elif page == "Mock exam":
    st.title("Mock exam")
    st.write("Feedback stays hidden until the full attempt is submitted.")
    if not subject["questions"]:
        render_needs_content("The mock exam uses the questions of your study content.")
    else:
        sittings = store.list_sittings(selected_id)
        exam_set, variant, exam_set_questions = select_exam(subject, sittings)
        exam_key = f"{exam_set}_{variant or 0}"
        with st.form(f"mock_exam_{exam_key}"):
            exam_answers = {}
            for index, question in enumerate(exam_set_questions, start=1):
                st.markdown(f'**{index}. {question["prompt"]}** · {question["points"]} pt')
                if question["type"] == "multiple_choice":
                    exam_answers[question["id"]] = st.radio(
                        "Answer",
                        question["options"],
                        index=None,
                        key=f'exam_{exam_key}_{question["id"]}',
                        label_visibility="collapsed",
                    )
                else:
                    exam_answers[question["id"]] = st.text_area(
                        "Answer",
                        key=f'exam_{exam_key}_{question["id"]}',
                        label_visibility="collapsed",
                    )
            exam_submitted = st.form_submit_button("Submit mock exam", type="primary")
        if exam_submitted:
            unanswered = [
                question
                for question in exam_set_questions
                if not exam_answers.get(question["id"]) or not str(exam_answers[question["id"]]).strip()
            ]
            if unanswered:
                st.warning(f"Answer all questions before submitting the mock exam ({len(unanswered)} remaining).")
            else:
                graded = grade_questions(exam_set_questions, exam_answers)
                sitting = uuid4().hex
                for result in graded["results"]:
                    store.save_attempt(
                        selected_id, "mock_exam", result, sitting=sitting, exam_set=exam_set, exam_variant=variant
                    )
                percentage = round(graded["score"] / graded["max_score"] * 100) if graded["max_score"] else 0
                label = f"Variant {variant}" if exam_set == "variant" else EXAM_SET_LABELS[exam_set]
                st.header(f'{label} · {percentage}% · {graded["score"]}/{graded["max_score"]}')
                for question, result in zip(exam_set_questions, graded["results"]):
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
        sittings = store.list_sittings(selected_id)
        if sittings:
            st.subheader("Mock exam sittings")
            rows = []
            for row in sittings[:12]:
                ratio = round(row["score"] / row["max_score"] * 100) if row["max_score"] else 0
                sat_at = datetime.fromisoformat(row["created_at"]).astimezone().strftime("%d %b, %H:%M")
                rows.append(
                    f'<div class="activity"><div class="what">{escape(sitting_label(row))}'
                    f'<div class="meta">{escape(sat_at)} · {row["questions"]} questions · {row["score"]}/{row["max_score"]}</div></div>'
                    f'<div class="score">{ratio}%</div></div>'
                )
            st.markdown("".join(rows), unsafe_allow_html=True)
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
    selected_materials = material_names(item, subject)
    st.markdown(
        f'<div class="panel"><b>{escape(item["name"])}</b><br>{escape(exam_label)} · target {item["target_score"]}%<br>'
        f'<span class="source">{escape(", ".join(selected_materials) or "No materials yet")}</span></div>',
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

    if not item["is_demo"]:
        st.subheader("Move to another computer")
        st.write(
            "Export this subject as one archive with its materials, study content, and progress, then import it "
            "from the library on the other computer."
        )
        if st.button("Prepare export", key="prepare_export"):
            st.session_state["export"] = (item["id"], export_subject(store, files, item["id"]))
        if st.session_state.get("export", (None,))[0] == item["id"]:
            st.download_button(
                "Download subject archive",
                data=st.session_state["export"][1],
                file_name=f'{item["id"]}-prepcanvas.zip',
                mime="application/zip",
                key="download_export",
            )

    st.subheader("Manage data")
    removes = "its saved answers and coaching profile, or the sample itself" if item["is_demo"] else "the subject and all of its progress"
    if not item["is_demo"]:
        st.caption(
            f"Deleting the subject keeps its materials and package in {display_path(files.subject_dir(item['id']))} so nothing you "
            "uploaded is lost; remove that folder yourself if you no longer need it."
        )
    confirmed = st.checkbox(f"I understand this permanently removes {removes}.", key=f'confirm_{item["id"]}')
    reset_column, delete_column = st.columns(2)
    if reset_column.button("Reset progress", key=f'reset_{item["id"]}', disabled=not confirmed):
        store.reset_progress(item["id"])
        st.session_state["flash"] = f'Progress for “{item["name"]}” was reset.'
        st.rerun()
    if item["is_demo"]:
        if delete_column.button("Remove sample subject", key="remove_sample", type="primary", disabled=not confirmed):
            store.remove_sample_subject(item["id"])
            open_library()
            st.session_state["flash"] = "Sample subject removed. You can add it back from the library."
            st.rerun()
    elif delete_column.button("Delete subject", key=f'delete_{item["id"]}', type="primary", disabled=not confirmed):
        store.delete_subject(item["id"])
        open_library()
        st.session_state["flash"] = f'Subject “{item["name"]}” was deleted.'
        st.rerun()
