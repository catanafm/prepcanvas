# Project purpose

PrepCanvas is a local-first, source-grounded exam preparation companion.

# Product constraints

- Keep user materials, answers, and progress local by default.
- Never commit private source documents, transcripts, generated source artifacts, or local databases.
- Ground learning feedback in the selected subject's sources.
- Keep deterministic workflows functional without an AI provider.
- Present readiness as a transparent heuristic, not a guaranteed result.
- Use synthetic content for public demos and tests.

# Technical constraints

- Python and Streamlit
- SQLite persistence
- small modules with focused tests
- English product UI and documentation
- optional AI providers behind explicit interfaces in later iterations

# UX priorities

1. Show the next best study action.
2. Explain before testing when the learner needs foundations.
3. Use immediate feedback in learning and practice modes.
4. Delay feedback until submission in mock-exam mode.
5. Show progress by topic and distinguish mastery from evidence volume.
