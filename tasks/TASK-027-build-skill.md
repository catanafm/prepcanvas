---
id: TASK-027
title: Ship an Agent Skill that builds subject packages with the learner's own assistant
type: feature
status: done
priority: high
area: ai
created: 2026-09-25
---

## Context

Turning a workbook, a mock exam, and its answers into topics, questions, and rubrics needs a capable model. API keys and metered tokens would make the project expensive to use and to demo. Learners already pay for, or have free access to, a coding agent or a chat assistant; the repository should let them use it.

## Acceptance criteria

- [x] `.claude/skills/prepcanvas-build/SKILL.md` follows the Agent Skills format and instructs any CLI agent to read the materials, design topics, write source and generated questions with rubrics, write `package.json`, and run the validator until it passes
- [x] `AGENTS.md` points to the skill, so agents without skill support (and Codex, which reads `AGENTS.md`) find it
- [x] `docs/subject-package.md` is the single schema document used by the skill, the chat prompt, and the validator's documentation
- [x] `python -m prepcanvas prompt <subject-id>` prints a self-contained prompt with the brief, the material list, and the schema for chat assistants
- [x] The skill never copies private material into the repository and tells the agent so

## Notes

Policy note for the README: local CLI agents run under the learner's own subscription; vendors change subscription rules and quotas, so the docs avoid hard numbers.
