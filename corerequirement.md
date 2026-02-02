# Personal Memory Ingestion System — Requirements (Phase 1)

## 1. Purpose

Build a **local-first, always-on personal memory ingestion system** that allows the user to:
- write thoughts freely in a desktop text file
- have those thoughts automatically cleaned, organized, and stored
- use simple text-based commands (hashtags / @) to instruct AI
- never lose ideas
- avoid manual organization
- postpone retrieval/search to later phases

This system is NOT a notes app, NOT a chatbot UI, and NOT a cloud-only service.

---

## 2. Core User Interaction

### 2.1 Writing Interface (Inbox)

- The user writes in a **plain text file** located on the **Desktop**.
- Example filename:
  - `inbox.txt`
- The file must:
  - be writable using any text editor
  - require zero setup or UI
  - work offline

### 2.2 Inbox Is a Temporary Buffer

- `inbox.txt` is **not storage**.
- It is a **temporary input buffer**.

#### Required behavior:
- When the user saves the file:
  - all content is consumed by the system
  - content is stored elsewhere
  - the inbox file is **automatically cleared**
- When the user reopens `inbox.txt`:
  - it must always be **empty**
  - no previous text should remain

---

## 3. Background Execution

- The system must run as a **background process**.
- It must:
  - start automatically when the laptop boots
  - not require the user to run CMD / terminal
  - not require manual triggers
- The system runs **only when the laptop is ON**.
- Sleep, restart, or crashes must not cause data loss.

---

## 4. Text-Based AI Commands (VERY IMPORTANT)

The user must be able to control AI behavior **directly from the text file** using simple markers.

### 4.1 Supported Command Syntax

The system must recognize:

#### Hashtags
- `#fix` → fix grammar and clarity
- `#expand` → expand or elaborate the idea
- `#research` → do light research (if internet available)
- `#raw` → store without AI modification
user can use either sign this sign goes as a command to ai rather than a text ai shoould have gauradrailss that if user says something in normal text ai should not believe it as a command
#### At-sign (@)
- `@append <entity>` → force append to a specific file
- `@new <entity>` → force creation of a new file
- `@umbrella <folder>` → hint umbrella category

### 4.2 Command Rules

- Commands are **optional**
- If no commands are present:
  - AI makes a best-effort decision silently
- Commands override AI judgment
- Commands must not appear in final stored content unless explicitly desired (very important)

---

## 5. Organization Model (Deterministic, Not Fuzzy)

### 5.1 Folder Rules (Umbrellas)

- Broad categories map to **folders**
- Examples:
  - `Apps/`
  - `Projects/`
  - `Concepts/`
  - `People/`

### 5.2 File Rules (Entities)

- Each **real-world entity** has exactly **one file**
- Examples:
  - `Apps/Grammarly.md`
  - `Apps/Duolingo.md`
- Different apps → different files
- Same app → same file

### 5.3 Append vs Create Logic

- If the content is about an **existing entity**:
  - content must be **appended** to that file
- If the content is about a **new entity under an existing umbrella**:
  - a **new file** must be created
- The system must **never** create duplicate files for the same entity.

---

## 6. AI Decision Making

- AI is allowed and expected to:
  - identify the entity being discussed
  - decide append vs new file
  - clean, expand, or research content based on commands
- Low-cost, fast AI models are acceptable and preferred.
- Internet access:
  - is optional
  - must not block ingestion
- If internet is unavailable:
  - raw content must still be saved
  - AI processing may be deferred

---

## 7. Human-in-the-Loop (Uncertainty Handling)

### 7.1 Default Behavior

- AI should act **silently** if confidence is high.
- No popups.
- No interruptions.

### 7.2 Uncertainty Resolution

- If AI is unsure:
  - it must write a question to a **separate text file**
- Example:
  - `_decisions.txt`

### 7.3 Decision File Rules

- `_decisions.txt` is where AI communicates with the user.
- AI may ask:
  - which file to append to giving options always give options
  - whether to create a new file
- The user responds by typing in the same file.
- After resolution:
  - the system processes the decision
  - clears the resolved section

---

## 8. Data Safety & Storage

### 8.1 Raw Preservation

- Every input must be stored in raw form.
- Raw inputs must never be deleted or overwritten.

### 8.2 Append-Only Storage

- Processed files grow by **appending**
- Existing content must never be rewritten automatically

---

## 9. Explicit Non-Requirements (What This System Is NOT)

The system must NOT include:

- Search or retrieval UI (Phase 3)
- Dashboards or analytics
- Popups or modal dialogs
- Chat interfaces
- Manual folder management
- Deep folder hierarchies
- Cloud-only dependency
- Forced internet requirement
- Automatic deletion of stored content

---

## 10. Phase Boundaries

### Phase 1 (This Document)
- Desktop TXT ingestion
- AI-assisted organization
- Deterministic append/create logic
- Separate decision file
- Local-first reliability

### Phase 2 (Later)
- WhatsApp ingestion
- Message backlog handling
- Same pipeline as TXT

### Phase 3 (Later)
- Retrieval
- Search
- Memory resurfacing
- Optional UI enhancements

---

## 11. Success Criteria (Phase 1)

- The inbox file is always clean after save
- No ideas are lost
- Same entity always maps to the same file
- Writing remains frictionless
- AI assistance feels invisible, not intrusive

## 12. User Workflows (Concrete, End-to-End)

This section describes how the system should *feel* to use from the user’s perspective.
These are NOT implementation details — they define expected behavior.

---

### Workflow 1: Writing a New App Idea (No Ambiguity)

**Scenario**
The user has a new idea for an app they have never written about before.

**Steps**
1. User opens `Desktop/inbox.txt`
2. User writes:


idea: an app that helps students revise using spaced repetition
#expand



3. User presses **Save**
4. System behavior:
- Reads the content
- Clears `inbox.txt`
- Uses AI to expand the idea
- Detects umbrella category = `Apps`
- Detects this is a **new entity**
- Creates a new file:
  ```
  Memories/Apps/Spaced_Repetition_App.md
  ```
- Appends expanded content with timestamp


**User experience**
- User comes back to `inbox.txt` → it is empty
- No popups
- No questions
- Idea is safely stored


---


### Workflow 2: Writing Again About an Existing App (Append Case)


**Scenario**
The user already has `Apps/Grammarly.md`.
They think of a new idea related to Grammarly.


**Steps**
1. User opens `Desktop/inbox.txt`
2. User writes:



Grammarly should support voice-based corrections
#fix



3. User presses **Save**
4. System behavior:
- Reads content
- Clears `inbox.txt`
- Uses AI to fix grammar
- Identifies entity = **Grammarly**
- Appends content to:
  ```
  Memories/Apps/Grammarly.md
  ```
- Adds timestamped section


**User experience**
- No new file is created
- Grammarly thoughts accumulate in one place
- Inbox remains clean


---


### Workflow 3: Ambiguous Case (Human-in-the-loop)


**Scenario**
The user writes something that could belong to multiple entities or a new one.


**Steps**
1. User writes in `inbox.txt`:



This could be integrated into a writing tool for developers



2. User presses **Save**
3. System behavior:
- Reads content
- Clears `inbox.txt`
- AI detects ambiguity:
  - Could be `Grammarly`
  - Could be a new app
- System does NOT guess blindly
- Writes to `_decisions.txt`:


  ```
  [Pending Decision – 2026-02-02 14:05]


  New thought:
  "This could be integrated into a writing tool for developers"


  Possible actions:
  1) Append to Apps/Grammarly.md
  2) Create new app file


  Reply with:
  DECISION: 1
  or
  DECISION: 2
  ```


4. User later opens `_decisions.txt`
5. User types:

DECISION: 1

6. User saves the file
7. System appends content accordingly and clears the resolved block


**User experience**
- No interruption during thinking
- Decisions are resolved asynchronously
- User stays in control when needed


---


## 13. AI & API Configuration Requirements


### 13.1 AI Usage Policy


- The system is allowed and expected to use external AI APIs.
- models like deepseek or geminin flash 
- Examples include:
- Gemini Flash–class models
- AI is used for:
- entity detection
- append vs new-file decisions
- grammar fixing
- idea expansion
- light research if asked 


AI must **not** be a hard dependency for ingestion.


---


### 13.2 Environment Configuration


- All AI credentials must be loaded from a `.env` file.
- No API keys may be hardcoded.


#### Example `.env` variables (illustrative):



AI_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-flash



- The system must:
  - fail gracefully if API is unavailable
  - continue storing raw input locally
  - retry or defer AI processing later


---


### 13.3 Offline Behavior


- If internet or AI API is unavailable:
  - inbox content is still consumed
  - inbox is still cleared
  - raw content is stored
  - AI processing is marked as pending


No idea may be dropped due to AI failure.


---


## 14. Final UX Principle (Non-Negotiable)


- Writing must feel **instant and safe**
- AI must feel **invisible**
- Organization must feel **automatic**
- Control must be available **only when needed**


If the system ever makes the user hesitate before writing,
it has failed its core purpose.

This is written in the same .md spec style so you can append it to your existing REQUIREMENTS.md.

## 15. Explicit Clarifications & Missing Decisions


This section documents **important clarifications, open questions, and edge cases**
that must be acknowledged to avoid silent failures or future redesigns.


---


## 16. Command Markers (Hashtags / @) — Clarified Behavior


### 16.1 Non-Dependency Rule (VERY IMPORTANT)


- The system must **NOT rely solely** on hashtags (`#`) or at-signs (`@`) to function.
- These markers are:
  - **explicit overrides**
  - **strong hints**
  - **optional**


### 16.2 Decision Priority Order


When processing content, the system must follow this order:


1. **Explicit commands present**  
   → obey them strictly  
   (e.g. `@append Grammarly`, `@new AppName`)


2. **No explicit commands present**  
   → AI must decide autonomously using:
   - known entities
   - existing file registry
   - content understanding


3. **AI uncertainty**  
   → escalate to `_decisions.txt`


### 16.3 Explicit Means Explicit


- If a hashtag or `@` is ambiguous, malformed, or unclear:
  - the system must **ignore it**
  - fall back to AI reasoning
- Only **clear, explicit commands** are binding.


---


## 17. Entity Registry & File Index (MANDATORY)


To ensure deterministic behavior, the system must maintain a **central registry file**
that represents the current “known world” of stored knowledge.


This registry is **not user-facing**, but critical for correctness.


---


### 17.1 Registry File Purpose


The registry must allow the system to answer:


- What files already exist?
- What real-world entity does each file represent?
- What umbrella folder does it belong to?
- What is this file *about* (briefly)?


This prevents:
- duplicate files
- inconsistent naming
- AI guessing blindly


---


### 17.2 Registry File Format (Example)


File name:

_memories_index.json



Example structure:


```json
{
  "entities": {
    "grammarly": {
      "entity_name": "Grammarly",
      "type": "app",
      "folder": "Apps",
      "file": "Apps/Grammarly.md",
      "summary": "AI-powered writing assistant for grammar, clarity, and tone",
      "aliases": ["grammar tool", "writing assistant"],
      "created_at": "2026-01-12T10:32:00Z",
      "last_updated": "2026-02-02T14:10:00Z"
    },
    "duolingo": {
      "entity_name": "Duolingo",
      "type": "app",
      "folder": "Apps",
      "file": "Apps/Duolingo.md",
      "summary": "Gamified language learning application",
      "aliases": [],
      "created_at": "2026-01-20T09:11:00Z",
      "last_updated": "2026-01-28T18:45:00Z"
    }
  }
}
17.3 Registry Update Rules

The registry must be updated when:

a new file/entity is created

a file is appended to (update last_updated)

an entity summary is refined

Registry updates must be:

atomic

append-safe

The registry is the primary source of truth, not folder scanning alone.

18. File-Level Summaries (Lightweight, Bounded)
18.1 Summary Purpose

Each entity file must have a short, bounded summary used for:

AI routing decisions

ambiguity resolution

future retrieval (Phase 3)

This summary is not the full content.

18.2 Summary Storage Options (Either Is Acceptable)

Stored:

in the registry JSON (preferred) use this

or as a small header block inside the file

Example inside a file:

---
entity: Grammarly
type: app
summary: AI-powered writing assistant for grammar and tone
---

Summaries must:

be concise

be updateable

never grow unbounded

19. Major Unanswered Questions (To Be Decided Later)

These are explicitly not decided yet, but must be acknowledged.

Entity Renaming

What happens if you want to rename Grammarly.md? most users wont they will write that in commands.txt a file like decesion.txt

How are aliases updated?

Entity Merging

If two files later turn out to be the same entity, can they merge? yes 

If yes, how is history preserved? idk you think

Deletion Policy

Can entities ever be deleted?

Or only archived? can be delted 

Versioning

Do we keep old summaries? not the delted  ones

Do we track changes to entity meaning over time?

Conflicting AI Decisions

If AI previously chose wrong silently, how is correction handled?

These are intentionally postponed.

20. Critical Edge Cases (Must Be Handled Gracefully)
20.1 Empty or Noise Input

If the user saves inbox.txt with:

empty content

whitespace only

The system must:

do nothing

not create files

not log errors

20.2 Multiple Ideas in One Save

If the inbox contains multiple distinct ideas:

the system may:

split them (if confident)

or treat them as one entry

If splitting is uncertain:

do NOT guess aggressively

store as a single raw entry

20.3 Rapid Saves

If the user saves multiple times quickly:

ingestion must be idempotent

no duplicate entries may be created

20.4 Partial Failures

If AI succeeds but file write fails:

raw content must still be preserved

If file write succeeds but registry update fails:

system must retry registry sync

20.5 Misclassification Risk

Wrong append is worse than asking.

Therefore:

low-confidence AI decisions must escalate

silent actions require high confidence

21. Logging & Audit Trail
21.1 Processing Log

The system must maintain a log file for debugging and trust.

Example:

_logs/ingestion.log

Log entries may include:

timestamp

source (inbox / WhatsApp later)

entity chosen

action taken (append / new / pending)

AI confidence score (if available)

Logs are:

append-only

non-user-facing

never required for normal use

22. Final Non-Negotiable Rule (Reinforced)

Hashtags and @ are hints, not crutches.

The system must work correctly even if the user writes plain English only. bur command would be folloerd by # or @ ONLY

If the system depends on perfect tagging, it has failed its purpose.



---

