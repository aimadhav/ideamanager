# Phase 2: The WhatsApp Neural Bridge - Detailed Implementation Plan

## 1. System Architecture
The system decouples **Message Fetching** (Node.js/Baileys) from **Processing/Intelligence** (Python). This ensures robust offline handling and separation of concerns.

### 1.1 The "Bridge" (Node.js)
*   **Role:** Acts as the sensory organ. It sees, hears, and downloads.
*   **Library:** `@whiskeysockets/baileys` (Unofficial, runs locally, no API costs).
*   **Identity:** Connects as a "Companion Device" (linked via QR code to your main phone).
*   **Scope:** Listens **ONLY** to a specific WhatsApp Group ID (configured in `.env`).

### 1.2 The "Buffer" (File System)
A shared folder structure acting as the handshake zone.
*   `data/inbox_buffer/`: JSON files containing message metadata + text.
*   `data/attachments_buffer/`: Raw downloaded files (PDFs, Images, etc.).

### 1.3 The "Brain" (Python)
*   **Watcher:** Monitors `data/inbox_buffer/`.
*   **Expander:** Fetches external content (YouTube transcripts, Web text, PDF OCR).
*   **Archivist:** Moves files to permanent storage and generates AI summaries.

---

## 2. Workflow & Logic

### 2.1 The "Catch-Up" Loop (Offline Handling)
**Scenario:** PC is off. You send 5 messages (3 text, 1 PDF, 1 YouTube Link) to the group.
1.  **PC Boots:** Node.js Bridge starts.
2.  **History Sync:** Baileys connects and receives the "history" event containing the 5 missed messages.
3.  **Deduplication:**
    *   The Bridge checks `data/whatsapp_state.json` (stores last processed `messageTimestamp` or `id`).
    *   It filters out messages *older* than the last checkpoint.
4.  **Batch Processing:**
    *   It processes them **sequentially** (oldest to newest) to preserve context.
    *   For the PDF: Downloads it -> Writes `msg_4.json` pointing to the file.
    *   For the Text: Writes `msg_1.json`, `msg_2.json`, etc.

### 2.2 Differentiating Messages
**Problem:** How does the AI know if 3 messages are separate thoughts or one long thought?
**Strategy:** "Time-Based Grouping" (Implemented in Python Ingestor)
*   If messages arrive within a short window (e.g., < 60 seconds) from the same source, they can be concatenated into a single "Context Block" before sending to the AI.
*   *Correction for Phase 2 MVP:* We will treat each message as a distinct "Input Unit" initially to ensure atomic reliability. If you paste a long text in 3 parts, the AI will likely treat them as 3 entries unless we implement advanced context windows.
*   **Edge Case:** "Reply" context. If Message B is a reply to Message A, Baileys provides the `quotedMessage`. We will include this in the JSON so the AI sees: "Context: [Quoted Text] -> Input: [New Text]".

---

## 3. Handling Specific Content Types

### 3.1 YouTube Links
*   **Trigger:** Regex detects `youtube.com` or `youtu.be`.
*   **Action:**
    1.  Python uses `youtube_transcript_api` to fetch the transcript.
    2.  If transcript fails (no captions), it falls back to `pytube` (or `yt-dlp`) to get the Description + Title.
    3.  **AI Prompt:** "Analyze this video transcript. Summarize the key arguments. Save to `Memories/WatchList`."

### 3.2 Web Articles
*   **Trigger:** Regex detects `http/https`.
*   **Action:**
    1.  Python requests the URL.
    2.  `BeautifulSoup` extracts `<p>` tags and main content (stripping nav/ads).
    3.  **AI Prompt:** "Summarize this article. Save to `Memories/Library/Articles`."

### 3.3 Files (PDFs/Docs)
*   **Trigger:** Message has `message.documentMessage`.
*   **Action:**
    1.  Bridge downloads to `data/attachments_buffer/temp_123.pdf`.
    2.  Python moves it to `Memories/Library/[Year]/[Month]/RealName.pdf`.
    3.  Python uses `pypdf` to extract text.
    4.  **AI Prompt:** "Here is the text from 'contract.pdf'. Summarize it. Link to the local file at `Memories/Library/...`."

---

## 4. Directory Structure Updates

```text
ideamanager/
├── data/
│   ├── inbox_buffer/         (JSONs: wa_timestamp_id.json)
│   ├── attachments_buffer/   (Temp downloads)
│   ├── whatsapp_state.json   (Last processed ID)
│   └── whatsapp_auth/        (Baileys credentials)
├── src/
│   ├── whatsapp/
│   │   ├── bridge.js         (The Node.js Process)
│   │   └── package.json
│   ├── capabilities.py       (PDF/YouTube tools)
│   └── ingestor.py           (Updated to read JSONs)
```

---

## 5. Edge Cases & Guardrails

| Edge Case | Solution |
| :--- | :--- |
| **Duplicate Messages** | Use `message.key.id` as the filename suffix (`wa_170992_3EB0X.json`). File system prevents duplicates. |
| **Huge Files (>50MB)** | Bridge checks file size. If >50MB, it downloads but *skips* text extraction (too slow), sending only metadata to AI ("User sent a large file: [Path]"). |
| **Corrupt Downloads** | If download fails, Bridge retries 3 times. If dead, logs error and sends text notification to AI ("Failed to download attachment"). |
| **Process Crash** | Use a "Supervisor" (PM2 or Python Watchdog) to ensure `bridge.js` is always running. |
| **Mixed Content** | (Image + Caption). The JSON includes `text: "caption"` AND `attachment: "path"`. AI considers both. |

---

## 6. Implementation Steps

1.  **Setup Node.js:** Initialize `src/whatsapp` and install Baileys.
2.  **Tooling:** Create `get_group_id.js` script to help user config.
3.  **Bridge Logic:** Write `bridge.js` (Download -> JSON Write).
4.  **Python Logic:** Update `ingestor.py` (JSON Read -> Expand -> AI).
5.  **Bat Script:** Update `run.bat` to launch `node src/whatsapp/bridge.js` alongside Python.
