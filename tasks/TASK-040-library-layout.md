---
id: TASK-040
title: Put subjects first in the library and give the cards one height
type: fix
status: done
priority: medium
area: ui
created: 2026-09-28
---

## Problem

The first card in the library is *+ New subject*, although creating a subject is rare and opening one is what every session starts with. Cards also differ in height depending on their text, so a row looks ragged.

## Acceptance criteria

- [x] *New subject* is a button in the library header, not a card in the grid
- [x] Subjects are ordered by last activity, most recent first; never-studied subjects follow, soonest exam first
- [x] Cards in a row share one height: fixed-height title, meta, and stats areas, button at the bottom
- [x] Covered by tests
