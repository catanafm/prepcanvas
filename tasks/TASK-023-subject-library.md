---
id: TASK-023
title: Add a subject library home screen
type: feature
status: backlog
priority: high
area: ui
created: 2026-09-24
---

## Context

Learners usually prepare for several exams over time. Study tools such as Anki, Quizlet, and Coursera open on a library of courses with progress and a clear "add" entry point, then drop into one course.

## Problem

The app opens straight into the demo subject. Subjects are switched in a sidebar dropdown, and creating one is hidden on the *Subjects* tab, so first-time users do not find it. There is no notion of a finished subject.

## Acceptance criteria

- [ ] The app opens on a *Library* screen with a short welcome and subject cards grouped into **In progress** and **Completed**
- [ ] Each card shows name, exam date countdown, readiness, topic coverage, and last activity, with a primary *Continue* action
- [ ] A prominent **+ New subject** card starts subject creation
- [ ] Subjects have a status (`active`, `completed`), changeable via *Mark as completed* / *Reopen*
- [ ] Inside a subject, a header shows the subject name and a way back to the library; the sidebar dropdown is removed
- [ ] The existing workspace pages keep working for the selected subject
- [ ] App tests cover library grouping, opening a subject, returning, and completing a subject
