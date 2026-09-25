---
id: TASK-035
title: Export a subject with its progress and import it on another computer
type: feature
status: in-progress
priority: medium
area: storage
created: 2026-09-25
---

## Context

Progress lives in `data/local/prepcanvas.sqlite3`, materials and the package in `data/private/subjects/<id>/`. Studying on a second computer today means copying both folders by hand.

## Acceptance criteria

- [ ] Settings offers *Export subject*: one zip with the subject record, coaching profile, attempts, `package.json`, `brief.json`, and the materials
- [ ] The library offers *Import subject* from such a zip; an existing subject with the same id is not overwritten without an explicit choice
- [ ] Round trip keeps readiness, progress history, and content identical; covered by tests with synthetic data
- [ ] README explains the export/import route and the synced-folder alternative with its SQLite caveat
