---
id: TASK-024
title: Treat the demo as a removable sample subject
type: feature
status: done
priority: high
area: storage
created: 2026-09-24
---

## Context

Tools such as Notion and Todoist ship sample content that users can remove once they have their own, and restore when they want to explore again.

## Problem

The demo subject is re-seeded on every start and cannot be deleted, so a learner with real subjects keeps seeing it.

## Acceptance criteria

- [x] The demo is labelled *Sample* in the library
- [x] The sample can be removed (with its progress) and stays removed across restarts
- [x] An *Add sample subject* action restores it
- [x] With no subjects at all, the library shows an empty state with *Create your first subject* and *Explore the sample subject*
- [x] Storage and app tests cover removal, persistence, and restore

## Notes

Resolution: a new `app_settings` table stores `sample_removed`. `StudyStore.ensure_sample_subject` seeds the sample only when it has not been removed; `remove_sample_subject` deletes it with its progress; `restore_sample_subject` brings it back fresh. The sample's *Settings* page offers *Remove sample subject* behind the same confirmation as other destructive actions. The library shows *Add sample subject* when it is removed, and an empty state with *Create your first subject* and *Explore the sample subject* when there are no subjects.
