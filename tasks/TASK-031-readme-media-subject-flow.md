---
id: TASK-031
title: Refresh README media for the subject flow
type: docs
status: backlog
priority: medium
area: docs
created: 2026-09-25
---

## Context

README screenshots and the GIF still show the previous creation form. The Content page and setup checklist are the new first impression.

## Acceptance criteria

- [ ] `scripts/capture_media.py` captures the Content page of a synthetic user subject (materials list, build instructions, validation result) in addition to the existing screens
- [ ] README shows the flow from creation to a loaded package with synthetic content only
- [ ] The demo GIF starts from the library and includes the Content page

## Review update — 2026-09-29

Complete after the reliability fixes and before the next release. The review used code and Streamlit AppTest; it did not perform browser visual or accessibility QA.

- [ ] Check the current library, Content recovery, practice, exam timer/results, and import flow at desktop and phone widths
- [ ] Verify keyboard navigation, feedback visibility, and usable error messages on the synthetic subject flow
- [ ] Record tested viewport sizes and resolve findings before recapturing media
