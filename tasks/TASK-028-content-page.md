---
id: TASK-028
title: Guide a new subject from creation to study content on a Content page
type: feature
status: done
priority: high
area: ui
created: 2026-09-25
---

## Context

Creating a subject used to end in a dead end: metadata was saved and every screen said that upload comes later. The learner needs to see what exists, what is missing, and where to go next.

## Problem

No place to add materials, no way to get content in, no explanation of the AI step, and material checkboxes that recorded nothing useful.

## Acceptance criteria

- [x] Creating a subject asks only for name, exam date, and target, writes `brief.json` for the agent, and opens the Content page
- [x] The Content page has three steps: Materials (TASK-012), Build (coding agent command with a copy button, chat prompt with package import, by hand), and Check (package missing / invalid with every issue / valid with summary, warnings, and a review of every topic and question)
- [x] The Overview of a subject without content shows a setup checklist with a button to the Content page; Diagnostic, Learn, Practice, and Mock exam link there instead of showing a placeholder
- [x] Library cards say what a subject without content needs next
- [x] The privacy statement is explicit: PrepCanvas sends nothing; the chosen assistant receives the materials under the learner's account
- [x] README, architecture, and roadmap describe the flow; covered by smoke tests
