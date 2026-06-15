# IdeaManager: AI-Powered Autonomous Knowledge Pipeline

IdeaManager is a **local-first, background-service memory pipeline** designed to convert ephemeral inputs (WhatsApp messages, desktop notes) into a structured, permanent Knowledge Base. It operates autonomously, using AI to categorize, summarize, and file information without user intervention.

## 🚀 The Vision
The core goal is **Zero-Friction Ingestion**. Instead of manually organizing notes or filing PDFs, the user sends content to a dedicated WhatsApp group or saves a line in a desktop `inbox.txt`. IdeaManager handles the rest: OCR, link expansion, AI categorization, and long-term storage.

---

## 🛠️ Architecture & Core Principles

### 1. Multi-Sensory Ingestion
- **WhatsApp Bridge (Node.js):** Uses the `Baileys` library to link as a companion device. It monitors a specific Group ID and downloads text, images, and documents into a local buffer.
- **Desktop Monitor (Python/Watchdog):** Watches a local `inbox.txt` on the Desktop. Any save event triggers the pipeline.

### 2. The Neural Pipeline (Python)
Once content enters the buffer, the Python "Brain" takes over:
- **Link Expansion:** Automatically fetches YouTube transcripts or scrapes web article content to provide the AI with full context.
- **OCR/Document Analysis:** Extracting text snippets from PDFs to allow the AI to understand file contents.
- **AI Routing:** Uses Gemini/DeepSeek to analyze the "thought" and decide whether to create a new category (Entity) or append to an existing one in the `Memories/` directory.

### 3. Concurrency & Reliability (Race Condition Management)
Handling rapid, asynchronous inputs from multiple sources (WhatsApp + Desktop) requires robust concurrency management:
- **Producer-Consumer Pattern:** The `monitor.py` (Watchdog) acts as a producer, pushing "PROCESS" signals into a thread-safe `queue.Queue`.
- **Dedicated Worker Thread:** A single worker thread consumes these signals sequentially. This prevents the "Double-Processing" race condition where two events might try to read/wipe the same file simultaneously.
- **Atomic File Operations:** The system uses "Pop" logic—reading the content and clearing the source file immediately to ensure no message is processed twice.
- **Single Instance Guard:** Uses TCP port binding (`SINGLE_INSTANCE_PORT`) to ensure only one instance of the "Brain" is running at any time, preventing database (Registry) corruption.

---

## 📈 Challenges Faced & Solutions

### **The "Rapid-Fire" Problem**
*   **Issue:** When a user sends 5 WhatsApp messages in 2 seconds, the monitor might trigger 5 simultaneous processing threads, leading to file access conflicts and duplicate AI calls.
*   **Solution:** Implemented a **Global Job Queue**. The monitor only signals the queue. The sequential worker ensures each "burst" is handled one-by-one, maintaining data integrity.

### **The "History Sync" Storm**
*   **Issue:** On startup, the WhatsApp bridge receives a burst of "missed" messages from the server.
*   **Solution:** State-tracking in `whatsapp_state.json`. The bridge ignores any message ID it has already buffered, and the Python ingestor processes the buffer in chronological order.

### **API Fragility**
*   **Issue:** Network downtime or AI API rate limits.
*   **Solution:** Offline-first buffering. Content stays in the `data/inbox_buffer/` until the AI confirms a successful process. If the API fails, the task stays in the queue or retries on the next sweep.

---

## 💻 Tech Stack
- **Languages:** Python (Brain), Node.js (WhatsApp Bridge).
- **Libraries:** `@whiskeysockets/baileys` (WA), `Watchdog` (FS Monitoring), `Google Generative AI` (Brain), `BeautifulSoup/yt-transcript` (Expansion).
- **Database:** Local Markdown files + `_memories_index.json` (Registry).

---

## 🔧 Setup
1.  **Environment:** Copy `.env.example` to `.env` and add your API keys.
2.  **WhatsApp Auth:** Run `node src/whatsapp/get_groups.js` to link your device and find your target Group ID.
3.  **Run:** Execute `run.bat` to launch both the Bridge and the Brain.

---

## 🧪 Testing
The project includes a suite of tests to verify core logic:
- `tests/test_capabilities_manual.py`: Manual verification of OCR and Link expansion.
- *More automated tests under development in `tests/`.*

---
*Developed with a focus on **Software Engineering Principles**: Separation of Concerns, Atomic Operations, and Local-First Privacy.*
