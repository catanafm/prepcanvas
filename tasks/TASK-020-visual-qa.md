---
id: TASK-020
title: Complete visual QA across every screen and fix findings
type: fix
status: done
priority: medium
area: ui
created: 2026-09-24
---

## Context

TASK-006 checked Overview, Practice, and Subjects. Diagnostic, Learn, Mock exam, and Progress were not reviewed at desktop and phone widths, and a few presentation issues were noticed along the way.

## Problem

- The hero heading keeps its desktop size on phones; the mobile style is overridden by Streamlit's heading rules.
- After creating a subject, the confirmation does not say what to do next, and new subjects cannot be studied until ingestion exists.
- Source labels show a repository file path (`src/prepcanvas/demo_data/...`) instead of a readable source name.
- Progress: on phones three metrics wrap as 2 + 1, and *Recent activity* lists only a UTC timestamp, mode, and percentage, without saying which question was answered.
- Large empty space above the navigation, and no gap between *Next best action* and *Topic map*.

## Acceptance criteria

- [x] All seven screens are captured at 1280 px and 390 px and reviewed; findings are recorded in this task
- [x] The hero heading scales down on phones
- [x] Subject creation feedback explains the next step without implying that ingestion works
- [x] Source labels read as human-friendly names
- [x] `scripts/capture_media.py --qa DIR` reproduces the review captures

## Notes

Review captured with `scripts/capture_media.py --qa DIR` (seeded synthetic progress, 1280 px and 390 px, full-page).

| Screen | Desktop | Phone | Action |
|---|---|---|---|
| Overview | OK | Tall hero heading; no gap after next action; empty band above navigation | Heading scales to 1.75rem, spacing added, top padding reduced |
| Diagnostic | OK | OK | — |
| Learn | Source shows file path | Source path wraps over three lines | Source labels renamed to "Sustainable Business workbook (synthetic) · Topic" |
| Practice | OK | OK | — |
| Mock exam | OK | OK | — |
| Progress | Activity lacks context | Metrics wrap 2 + 1; activity lacks context | Three metrics stay in one row; activity shows question, topic, mode, local time, and score |
| Subjects | OK | OK | Creation toast and new-subject overview now explain that material upload comes later and point to the demo |

README media are regenerated in TASK-021 so they reflect these fixes.
