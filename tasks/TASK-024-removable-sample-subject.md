---
id: TASK-024
title: Treat the demo as a removable sample subject
type: feature
status: backlog
priority: high
area: storage
created: 2026-09-24
---

## Context

Tools such as Notion and Todoist ship sample content that users can remove once they have their own, and restore when they want to explore again.

## Problem

The demo subject is re-seeded on every start and cannot be deleted, so a learner with real subjects keeps seeing it.

## Acceptance criteria

- [ ] The demo is labelled *Sample* in the library
- [ ] The sample can be removed (with its progress) and stays removed across restarts
- [ ] An *Add sample subject* action restores it
- [ ] With no subjects at all, the library shows an empty state with *Create your first subject* and *Explore the sample subject*
- [ ] Storage and app tests cover removal, persistence, and restore
