# Implementation Plan: Phase 1a (The Mechanical Skeleton)

**Goal:** Build the core loop: Write → Save → Disappear → Store (Safe Fallback). No AI involved yet.

## Context
This system monitors a local text file (`inbox.txt`) on the user's Desktop. When the user saves the file, the system automatically:
1.  Reads the content.
2.  Backs it up to a raw history file.
3.  Clears the `inbox.txt` file (making it ready for the next thought).
4.  (Temporary) Appends the content to `Memories/Unsorted.md` since AI is disabled in this phase.

## Tasks

- [x] **1. Project Scaffolding**
    - [x] Create directory structure: `src`, `data/raw`, `data/logs`, `Memories`.
    - [x] Create `requirements.txt` (dependencies: `watchdog`, `python-dotenv`).
    - [x] Create `.env` template.

- [x] **2. Environment Setup**
    - [x] Install dependencies via pip.
    - [x] Create dummy `inbox.txt` on Desktop if missing.

- [x] **3. Core Logic Implementation**
    - [x] `src/config.py`: Define absolute paths for Inbox, Memories, and Data.
    - [x] `src/file_ops.py`: Helper functions for atomic read/write and safe clearing.
    - [x] `src/ingestor.py`: The "Dumb" processor.
    - [x] `src/monitor.py`: Watchdog observer.

- [x] **4. Entry Point**
    - [x] `src/main.py`: Sets up the observer and keeps the script running.

- [x] **5. Verification**
    - [x] Run `src/main.py`.
    - [x] Manually write to `inbox.txt` and Save.
    - [x] Verify `inbox.txt` is empty.
    - [x] Verify content exists in `Memories/Unsorted.md`.

## Phase 1a Status: COMPLETE
The system is now running.
- **To Start:** Double-click `run.bat` in `C:\Users\madha\Desktop\ideamanger\`.
- **To Use:** Write in `inbox.txt` on your Desktop and Save.
- **Output:** Check `ideamanger/Memories/Unsorted.md`.

## Phase 1b Status: COMPLETE
The system effectively uses Gemini 2.0 Flash to organize thoughts.
- **AI Routing:** Verified. "Python" idea -> `Memories/Tools/Python.md`.
- **Registry:** Verified. `_memories_index.json` tracks entities.
- **Commands:** Verified. `@append` works.

## Phase 1c: Robustness & Ambiguity (The "Human-in-the-Loop")

**Goal:** Handle edge cases where AI is unsure, preventing wrong filing.

### Tasks

- [ ] **1. Implement Ambiguity Handling**
    - [ ] Update `src/ai_engine.py` prompt to encourage "ambiguous" output for vague inputs.
    - [ ] Update `src/ingestor.py` to write to `_decisions.txt` in a structured format (as per Spec Section 7.3).
    - [ ] Create `src/decision_handler.py` to monitor `_decisions.txt` for user replies (DECISION: 1).

- [ ] **2. Command Expansion**
    - [ ] Support `#fix` (Grammar check).
    - [ ] Support `#expand` (Idea expansion).
    - [ ] Support `#research` (Web search - optional).

- [ ] **3. Startup & Reliability**
    - [ ] Ensure `run.bat` starts on boot (User instruction).
    - [ ] Add logging to `data/logs/ingestion.log`.

## Phase 2: WhatsApp Integration (Future)
- [ ] Twilio/Meta API setup.
- [ ] Webhook listener.


