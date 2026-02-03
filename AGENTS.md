# Developer Documentation (AGENTS.md)

This document provides guidelines for AI agents and developers working on the `ideamanager` repository.

## 1. Environment Setup

### 1.1 Python Environment
Ensure you are running in a Python 3.10+ environment.

```bash
# Create venv
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 1.2 Dependencies
Install the required packages:
```bash
pip install -r requirements.txt
```

### 1.3 Node.js Environment (Phase 2)
For the WhatsApp Bridge:
```bash
cd src/whatsapp
npm install
```

### 1.4 Configuration (`.env`)
Create a `.env` file in the root directory. This file is `.gitignore`'d and must not be committed.

```ini
# Required for AI processing
GEMINI_API_KEY=your_api_key_here

# Required for WhatsApp (Phase 2)
WHATSAPP_GROUP_ID=123456789@g.us
```

## 2. Execution Commands

| Action | Command | Description |
| :--- | :--- | :--- |
| **Run System** | `python -m src.main` | Starts the background service (File Monitor + Worker). |
| **Run Bridge** | `node src/whatsapp/bridge.js` | Starts the WhatsApp listener (Phase 2). |
| **Run Tests** | `python -m unittest discover tests` | Runs all unit tests. |
| **Run Single Test** | `python -m unittest tests/test_ingestor.py` | Runs a specific test file. |
| **Start (Prod)** | `run_ideamanager.bat` | Starts both Python and Node.js processes silently. |

## 3. Project Structure

### `src/` (Core Logic)
*   **`main.py`**: Entry point. Handles threading, single-instance locking, and process orchestration.
*   **`ingestor.py`**: The "Brain". Reads from `inbox.txt` OR `data/inbox_buffer/`, orchestrates AI processing, and saves files.
*   **`ai_engine.py`**: Interface with Gemini API. Handles prompt engineering and JSON parsing.
*   **`capabilities.py`**: (Phase 2) The "Eyes". Fetches YouTube transcripts, scrapes URLs, and reads PDFs.
*   **`whatsapp/`**: (Phase 2) Node.js project for Baileys/WhatsApp connection.

### `data/` (Runtime Data)
*   `inbox_buffer/`: JSON files from WhatsApp waiting to be processed.
*   `attachments_buffer/`: Raw downloaded files (PDFs, Images).
*   `logs/`: Application logs (e.g., `ingestion.log`).
*   `whatsapp_auth/`: Baileys session credentials (DO NOT COMMIT).

### `Memories/` (Knowledge Base)
*   **Do not manually edit files here unless debugging.**
*   The system manages the folder structure based on AI routing.
*   `Library/`: Final home for downloaded PDFs/Docs.

## 4. Development Standards

### 4.1 Python Style
*   Follow **PEP 8**.
*   **Imports:** Absolute imports preferred (e.g., `from src.config import...`).
*   **Type Hints:** Use for all function arguments and returns.
*   **Docstrings:** Required for all classes and complex functions (Google Style).
*   **Path Handling:** ALWAYS use `pathlib.Path` objects from `src.config`. NEVER string concatenation for paths.

### 4.2 Node.js Style
*   Use ES6+ syntax (`const`/`let`, arrow functions).
*   Prefer `async/await` over callbacks.
*   Use `camelCase` for variables/functions.

### 4.3 Error Handling
*   **Retry Logic:** Network-dependent operations (AI API, Downloads) must implement exponential backoff.
*   **Fail-Safe:** If a single message fails, log it to `_errors.txt` and move on. Do NOT crash the main loop.

## 5. Critical Rules ("Do Nots")

1.  **NO Hardcoded Paths:** Always use `src.config` path variables (e.g., `DESKTOP_PATH`, `MEMORIES_DIR`).
2.  **NO Hardcoded Secrets:** API keys must only come from `os.environ`.
3.  **NO Overwrites:** The memory system is **append-only**. Never overwrite an existing markdown memory file; always append.
4.  **NO Blocking Main Thread:** Heavy processing (AI/Downloads) must happen in the `worker` thread, not the UI/Watchdog thread.
5.  **NO Interactive Shells:** Do not use `input()` or interactive CLI commands. This is a background service.

## 6. Testing Protocol
*   **Step-by-Step Verification:**
    1.  **Unit:** Test individual functions (e.g., `capabilities.fetch_youtube_transcript`).
    2.  **Integration:** Test the full pipeline using `inbox.txt` or a mock JSON in `inbox_buffer/`.
    3.  **End-to-End:** Send a real WhatsApp message and verify the final `.md` file in `Memories/`.
*   Mock external APIs (Gemini, WhatsApp) in tests to avoid usage costs.
