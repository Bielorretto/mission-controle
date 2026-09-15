# Mission Control — Transcript Input

> A Python module for importing meeting transcripts into Mission Control, with support for TXT and Markdown files.

## 🎯 Project Overview

**Mission Control** is a meeting-assistance project developed during a hackathon.

The goal is to transform meeting transcripts into structured information that can later be used by a local AI system and integrated into other services.

The overall pipeline is:

```text
Meeting Transcript
       ↓
Transcript Input
       ↓
Local AI Analysis
       ↓
MeetingAnalysis
       ↓
Grist
       ↓
Buzz
```

The **Transcript Input** component is the entry point of this pipeline.

Its role is to make sure that Mission Control can still process a meeting even when an external meeting service such as Google Meet is unavailable.

---

## 👨‍💻 My Contribution

As **Dev 6**, I developed the **Transcript Input** component.

My responsibilities for this part were:

- Designing a consistent `Transcript` representation.
- Implementing transcript loading from files.
- Supporting `.txt` and `.md` formats.
- Validating input files.
- Preserving French UTF-8 content and accents.
- Rejecting empty transcripts.
- Handling invalid or unsupported files.
- Creating realistic French demo transcripts.
- Writing automated tests with `pytest`.

The module exposes a simple interface:

```python
load_transcript(path) -> Transcript
```

This keeps the rest of the application independent from the way transcripts are stored.

---

# 🏗️ Architecture

The component is intentionally small and modular:

```text
mission_control/
└── transcript/
    ├── __init__.py
    ├── loader.py
    └── models.py
```

### `models.py`

Defines the data structure returned by the loader.

```python
@dataclass(frozen=True)
class Transcript:
    path: str
    content: str
    format: str
```

A transcript contains:

| Field | Description |
|---|---|
| `path` | Path of the source file |
| `content` | Full transcript content |
| `format` | Input format (`txt` or `md`) |

Using a dataclass avoids unnecessary boilerplate while making the expected structure explicit.

`frozen=True` makes the object immutable after creation, preventing accidental modifications during later processing.

---

# 📥 Transcript Loader

The main logic is implemented in:

```text
mission_control/transcript/loader.py
```

The public function is:

```python
load_transcript(path)
```

It performs several validation steps before returning a `Transcript`.

### 1. Validate the path

The loader first checks that the provided path exists.

```python
if not file_path.exists():
    raise FileNotFoundError(...)
```

This prevents the application from attempting to read a file that does not exist.

### 2. Validate that the path is a file

A valid path could technically point to a directory.

Therefore, the loader also checks:

```python
if not file_path.is_file():
    raise ValueError(...)
```

### 3. Validate the format

Mission Control currently supports:

```python
SUPPORTED_EXTENSIONS = {".txt", ".md"}
```

The extension is normalized using:

```python
extension = file_path.suffix.lower()
```

This means `.TXT` and `.txt` are treated consistently.

Unsupported formats are rejected instead of silently processed.

### 4. Read UTF-8 content

Transcripts are read using:

```python
content = file_path.read_text(encoding="utf-8")
```

Explicit UTF-8 handling is important because Mission Control is expected to process French meetings containing characters such as:

```text
é è ê ë à ç ù œ
```

### 5. Reject empty transcripts

An empty or whitespace-only transcript is not useful for the AI pipeline.

The loader therefore checks:

```python
if not content.strip():
    raise ValueError("Transcript is empty")
```

### 6. Return a consistent object

After validation, the loader returns:

```python
Transcript(
    path=str(file_path),
    content=content,
    format=extension[1:],
)
```

The rest of Mission Control therefore receives the same type of object regardless of whether the original file was TXT or Markdown.

---

# 🧪 Automated Testing

The component is tested with **pytest**.

The test suite covers:

- Valid TXT files
- Valid Markdown files
- French accents
- Empty files
- Missing files
- Unsupported extensions

Current result:

```text
6 passed
```

Example:

```python
def test_empty_transcript():
    with pytest.raises(ValueError, match="Transcript is empty"):
        load_transcript(DATA_DIR / "empty.txt")
```

This test verifies that invalid input is rejected with the expected error.

---

# 🇫🇷 French / UTF-8 Support

French text is an important requirement because meeting transcripts can contain names, accents and punctuation that must not be corrupted.

For example:

```text
Élodie présente l'état d'avancement du projet.
```

The loader explicitly uses UTF-8:

```python
read_text(encoding="utf-8")
```

This ensures that the original transcript is preserved before being passed to the AI analysis stage.

---

# 📄 Demo Transcripts

Three realistic French meeting transcripts are included:

```text
demo/
├── cybersecurity_meeting.txt
├── project_alpha.md
└── team_planning.txt
```

They simulate different types of meetings:

### Cybersecurity meeting

Contains:

- Participants
- Security vulnerabilities
- Decisions
- Assigned actions
- Deadlines
- Follow-up meeting

### Project Alpha

Contains:

- Project progress
- Performance issues
- Decisions
- Multiple actions
- Deadlines

### Team planning

Contains:

- Team planning
- Proposed tasks
- Decisions
- Assigned responsibilities
- Future meeting

These examples are designed to resemble the type of input that will later be processed by the local AI analysis component.

---

# 🔌 Integration With Mission Control

The important design decision is that the AI system does **not** need to know how the transcript was obtained.

For example:

```python
from mission_control.transcript import load_transcript

transcript = load_transcript("meeting.txt")

print(transcript.content)
```

The AI analysis layer can then consume:

```python
transcript.content
```

This creates a clean separation:

```text
File
 ↓
Transcript Loader
 ↓
Transcript
 ↓
AI Analysis
```

In the future, another input source could provide the transcript without changing the AI analysis layer.

For example:

```text
Google Meet
      ↓
      Transcript
      ↓
AI Analysis
```

or:

```text
meeting.md
      ↓
Transcript Loader
      ↓
AI Analysis
```

Both approaches can ultimately produce the same `Transcript` representation.

---

# 🧠 Design Principles

Several principles guided the implementation.

### Single responsibility

The loader is responsible for **loading and validating transcripts**.

It does not:

- Analyze meetings
- Generate summaries
- Extract decisions
- Communicate with Grist
- Communicate with Buzz
- Call external AI APIs

This keeps the component easy to understand and maintain.

### Explicit validation

Invalid inputs are rejected early.

This avoids pushing malformed data further into the application.

### Stable interface

The rest of Mission Control only needs:

```python
load_transcript(path)
```

The internal implementation can evolve without requiring changes to every consumer.

### No external dependency

The transcript loader relies on Python's standard library for file handling.

This makes it lightweight and easy to deploy.

---

# 📁 Project Structure

```text
mission-control/
│
├── mission_control/
│   └── transcript/
│       ├── __init__.py
│       ├── loader.py
│       └── models.py
│
├── tests/
│   ├── test_transcript.py
│   └── data/
│       ├── meeting.txt
│       ├── meeting.md
│       ├── empty.txt
│       └── meeting.pdf
│
├── demo/
│   ├── cybersecurity_meeting.txt
│   ├── project_alpha.md
│   └── team_planning.txt
│
├── pyproject.toml
└── README.md
```

---

# ⚙️ Installation

The project uses Python packaging through `pyproject.toml`.

Install the project and its test dependencies with:

```bash
python -m pip install -e ".[test]"
```

Then run:

```bash
pytest -v
```

Expected result:

```text
6 passed
```

---

# 🛠️ Technologies

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| `pathlib` | File and path management |
| `dataclasses` | Transcript data model |
| pytest | Automated testing |
| UTF-8 | French text support |

No external API is required for this component.

---

# 🚧 Current Scope

This component intentionally focuses only on transcript input.

It does not implement:

- Local AI analysis
- Meeting summaries
- Decision extraction
- Action extraction
- Grist integration
- Buzz integration
- Google Meet integration
- Docs integration
- Agenda functionality

Those responsibilities belong to other parts of Mission Control.

---

# 🚀 Possible Future Improvements

The current implementation provides the required MVP functionality while leaving room for future extensions.

Possible improvements include:

- Additional transcript formats
- Automatic format detection
- Streaming large transcripts
- More advanced input validation
- Transcript metadata extraction
- Integration with live meeting services
- Additional test cases

These extensions can be added without changing the fundamental `Transcript` interface.

---

# 📚 What I Learned

This part of the project gave me practical experience with:

- Python project structure
- Modules and packages
- Dataclasses
- Type hints
- File handling with `pathlib`
- UTF-8 text processing
- Input validation
- Exception handling
- Automated testing with pytest
- Designing a stable interface between components

More importantly, the project introduced me to an important software engineering principle:

> A component should have a clear responsibility and provide a predictable interface to the rest of the application.

---

# ✅ Definition of Done — Part A

The Transcript Input component satisfies the required objectives:

- [x] TXT transcript loading
- [x] Markdown transcript loading
- [x] Path validation
- [x] File validation
- [x] Empty transcript rejection
- [x] UTF-8/French text preservation
- [x] Consistent `Transcript` representation
- [x] Automated tests
- [x] French demo transcripts

---

# 👨‍💻 Contribution Summary

**Role:** Dev 6 — Transcript Input

**Main contribution:** Python transcript ingestion module

**Input formats:** `.txt`, `.md`

**Testing:** `pytest` — 6 tests passing

**Focus:** Reliable input validation, UTF-8 support and clean integration with the Mission Control pipeline.

---

## ⭐ Why This Component Matters

A meeting-analysis system is only as reliable as the data it receives.

The Transcript Input component provides a simple and controlled entry point into Mission Control:

```text
Untrusted file
     ↓
Validation
     ↓
UTF-8 content
     ↓
Transcript object
     ↓
AI analysis
```

By isolating this responsibility, the rest of the system can focus on understanding the meeting rather than dealing with file formats and invalid input.
