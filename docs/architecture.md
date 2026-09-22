# Architecture

## Current shape

PrepCanvas is a small local Streamlit application with deterministic domain logic and SQLite persistence.

```text
Streamlit UI
    │
    ├── catalog.py       synthetic demo content
    ├── coaching.py      diagnostic strategy selection
    ├── grading.py       deterministic answer scoring
    ├── readiness.py     transparent mastery heuristic
    └── storage.py       subjects, attempts, profiles
             │
          SQLite
```

## Data boundaries

Public, versioned data:

- packaged synthetic source document and derived demo subject;
- tests and expected outputs;
- product documentation.

Local, ignored data:

- user-created subjects;
- progress and answers;
- uploaded source materials;
- parsed source artifacts;
- secrets and provider configuration.

## Why deterministic first

The first public version works without an AI key. This makes setup reproducible, protects privacy, and keeps grading behavior testable. Later AI providers should implement explicit interfaces and return source citations; they should not replace the storage, readiness, or practice workflow.

## Readiness heuristic

For each topic, PrepCanvas weights newer answered attempts more strongly, uses up to five recent results, and applies an evidence factor that reaches 100% after three attempts. Overall readiness is the mean of topic mastery. A subject is marked ready only when the target score is reached and every topic has evidence.

## Planned ingestion boundary

Future source ingestion will produce a normalized subject package:

```text
subject metadata
topics[]
source references[]
learning notes[]
questions[]
rubrics[]
```

The UI and progress model should consume this normalized representation rather than depend on a particular institution's PDF layout.
