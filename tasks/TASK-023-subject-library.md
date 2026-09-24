---
id: TASK-023
title: Add a subject library home screen
type: feature
status: done
priority: high
area: ui
created: 2026-09-24
---

## Context

Learners usually prepare for several exams over time. Study tools such as Anki, Quizlet, and Coursera open on a library of courses with progress and a clear "add" entry point, then drop into one course.

## Problem

The app opens straight into the demo subject. Subjects are switched in a sidebar dropdown, and creating one is hidden on the *Subjects* tab, so first-time users do not find it. There is no notion of a finished subject.

## Acceptance criteria

- [x] The app opens on a *Library* screen with a short welcome and subject cards grouped into **In progress** and **Completed**
- [x] Each card shows name, exam date countdown, readiness, topic coverage, and last activity, with a primary *Continue* action
- [x] A prominent **+ New subject** card starts subject creation
- [x] Subjects have a status (`active`, `completed`), changeable via *Mark as completed* / *Reopen*
- [x] Inside a subject, a header shows the subject name and a way back to the library; the sidebar dropdown is removed
- [x] The existing workspace pages keep working for the selected subject
- [x] App tests cover library grouping, opening a subject, returning, and completing a subject

## Notes

Resolution: the app opens on a library with a welcome line, an **In progress** grid that starts with a *+ New subject* card, and a **Completed** grid when needed. Cards show exam countdown, last activity, readiness, and coverage (or a note that study content arrives with material upload), with *Continue* / *Open*. Inside a subject, *← All subjects* returns to the library and the former *Subjects* tab became per-subject *Settings* (status, reset, delete). Subject status is a new `subjects.status` column added by migration. Pure helpers live in `prepcanvas.library` and are unit tested. Navigation uses button callbacks so switching subjects always lands on *Overview*.
