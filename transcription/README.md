# Mission Control — Transcript Input & Meeting Reports

## Overview

This module provides the transcript input and meeting report generation layer for **Mission Control**.

The goal is to keep the Mission Control pipeline functional even when external meeting services such as Google Meet are unavailable.

The implemented flow is:

```text
Transcript file
      │
      ▼
load_transcript()
      │
      ▼
Transcript
      │
      ▼
Local AI analysis
      │
      ▼
MeetingAnalysis
      │
      ▼
generate_markdown_report()
      │
      ▼
Markdown meeting report
```

The transcript loader and report generator are independent from the AI implementation and from external meeting providers.

---

## Implemented Features

### 1. Transcript Input

The transcript loader supports:

- `.txt` files
- `.md` Markdown files
- UTF-8 encoded content
- French and other Unicode characters
- Empty-file validation
- Missing-file validation
- Unsupported-format validation
- File-path validation

Main API:

```python
from mission_control.transcript import load_transcript

transcript = load_transcript("demo/project_alpha.md")
```

The loader returns a consistent `Transcript` object:

```python
Transcript(
    path="demo/project_alpha.md",
    content="...",
    format="md",
)
```

This provides a clean interface for the rest of the Mission Control pipeline.

---

## 2. MeetingAnalysis Model

The analysis layer defines the structured result expected from the Local AI analysis step.

The shared `MeetingAnalysis` contract contains:

- Meeting ID
- Meeting title
- Detected language
- Summary
- Decisions
- Actions
- Assignees
- Due dates
- Action status

Example:

```python
MeetingAnalysis(
    meeting_id="meeting-2026-09-15-001",
    title="Project Alpha",
    language="en",
    summary="Meeting summary...",
    decisions=[
        Decision(
            description="Use option B."
        )
    ],
    actions=[
        Action(
            id="action-001",
            description="Prepare the presentation",
            assignee="Celine",
            due_date="2026-09-18",
            status="todo",
        )
    ],
)
```

Unknown information is represented with `None`.

The system does **not** invent missing assignees or deadlines.

---

## 3. Markdown Meeting Reports

A structured `MeetingAnalysis` can be converted into a clean Markdown report.

```python
from mission_control.report import generate_markdown_report

report = generate_markdown_report(analysis)
```

The generated report contains:

```text
# Meeting Title

Meeting metadata

## Summary

...

## Decisions

- ...

## Actions

| Action | Assignee | Due date | Status |
|---|---|---|---|
| ... | ... | ... | ... |
```

Reports can also be saved directly to disk:

```python
from mission_control.report import save_markdown_report

save_markdown_report(
    analysis,
    "demo/reports/project_alpha_demo_report.md",
)
```

Missing action information is handled safely:

- Unknown assignee → `Unknown`
- Missing due date → `Not specified`
- No decisions → `No decisions recorded.`
- No actions → `No actions recorded.`

---

## 4. Demo Transcripts

Three realistic demo transcripts are included:

```text
demo/
├── cybersecurity_meeting.txt
├── project_alpha.md
└── team_planning.txt
```

The demo transcripts are intentionally written in **English** for the hackathon demonstration.

French/UTF-8 handling is tested separately with:

```text
tests/data/french_accents.txt
```

Example content:

```text
Équipe cybersécurité — réunion
Céline présente l'état d'avancement.
La réunion est très productive et terminée à 17h.
```

This verifies that the loader preserves Unicode and French accents correctly.

---

## 5. Test Coverage

The project currently contains **10 automated tests**.

### Transcript tests

The test suite verifies:

- Valid TXT loading
- Valid Markdown loading
- French accents preservation
- Empty transcript rejection
- Missing file rejection
- Unsupported extension rejection

### Report tests

The test suite verifies:

- Markdown report generation
- Missing action information
- Empty decisions/actions
- Saving reports to disk

Run the complete test suite with:

```bash
cd transcription
python -m pytest -v
```

Current result:

```text
10 passed
```

---

## 6. End-to-End Demo

The complete implemented workflow can be demonstrated with:

```text
project_alpha.md
       ↓
load_transcript()
       ↓
Transcript
       ↓
MeetingAnalysis
       ↓
generate_markdown_report()
       ↓
project_alpha_demo_report.md
```

The `MeetingAnalysis` used in the local demonstration is a simulated analysis result.

In the complete Mission Control architecture, this object is produced by the **Local AI analysis layer**.

This separation keeps the transcript and reporting components independent from the AI provider.

---

## Project Structure

```text
transcription/
├── demo/
│   ├── cybersecurity_meeting.txt
│   ├── project_alpha.md
│   ├── team_planning.txt
│   └── reports/
│       └── project_alpha_demo_report.md
│
├── mission_control/
│   ├── __init__.py
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── models.py
│   │
│   └── transcript/
│       ├── __init__.py
│       ├── loader.py
│       └── models.py
│
│   └── report.py
│
├── tests/
│   ├── data/
│   │   ├── empty.txt
│   │   ├── french_accents.txt
│   │   ├── meeting.md
│   │   ├── meeting.pdf
│   │   └── meeting.txt
│   │
│   ├── test_report.py
│   └── test_transcript.py
│
├── pyproject.toml
└── README.md
```

---

## Design Principles

### Stable MVP first

The core Mission Control workflow must not depend on an external meeting provider.

Transcript files provide a reliable fallback input when Meet or another meeting service is unavailable.

### Separation of responsibilities

Each component has a single responsibility:

```text
Transcript Loader
    → Reads and validates transcript files

MeetingAnalysis Models
    → Represents structured AI analysis results

Report Generator
    → Converts analysis into human-readable Markdown
```

The Local AI layer can therefore evolve independently.

### No invented information

The analysis contract explicitly allows unknown information.

For example:

```python
assignee=None
due_date=None
```

is preferable to guessing information that was not present in the transcript.

### UTF-8 by default

Transcript files are read using UTF-8 to preserve multilingual content and characters such as:

```text
é è ê à ç ù œ É
```

---

## External Integrations

External meeting and document services are intentionally **not required for the stable MVP**.

The implemented components can operate entirely from local transcript files.

Potential integrations such as La Suite Docs or Google Meet can consume the existing interfaces later without changing the core transcript-loading logic.

This makes the module usable even when external APIs are unavailable.

---

## Definition of Done

### Required

- [x] TXT transcript loading
- [x] Markdown transcript loading
- [x] UTF-8/French character preservation
- [x] Empty-file validation
- [x] Missing-file validation
- [x] Unsupported-extension validation
- [x] Realistic English demo transcripts
- [x] Structured `MeetingAnalysis` model
- [x] Markdown meeting report generation
- [x] Automated tests
- [x] End-to-end demonstration

### Optional integrations

- [ ] Import generated reports into La Suite Docs
- [ ] External meeting provider integration

These integrations are not required for the stable Mission Control MVP.

---

## Quick Start

```bash
cd transcription

python -m pytest -v
```

To load a transcript:

```python
from mission_control.transcript import load_transcript

transcript = load_transcript("demo/project_alpha.md")

print(transcript.content)
```

To generate a report:

```python
from mission_control.report import generate_markdown_report

markdown = generate_markdown_report(analysis)

print(markdown)
```

To save it:

```python
from mission_control.report import save_markdown_report

save_markdown_report(
    analysis,
    "demo/reports/project_alpha_demo_report.md",
)
```

---

## Status

**Mission Control — Transcript Input & Meeting Reports: MVP implemented and tested.**

Test status:

```text
10 passed
```

The module is ready to be connected to the Local AI analysis layer and the rest of the Mission Control pipeline.
