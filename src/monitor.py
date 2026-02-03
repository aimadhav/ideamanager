import time
import os
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.config import INBOX_FILE, DESKTOP_PATH, INBOX_BUFFER_DIR

class BufferHandler(FileSystemEventHandler):
    """Watches the WhatsApp buffer for new JSON files."""
    def __init__(self, processing_queue):
        self.queue = processing_queue

    def on_created(self, event):
        from src.config import LOGS_DIR
        from src.file_ops import append_to_file
        from datetime import datetime
        log_file = LOGS_DIR / "ingestion.log"

        if event.is_directory:
            return
        if event.src_path.endswith(".json"):
            append_to_file(log_file, f"[{datetime.now()}] [MONITOR] Detected new file via Watchdog: {event.src_path}")
            print(f"Detected new buffer file: {event.src_path}")
            self.queue.put("PROCESS")

class InboxHandler(FileSystemEventHandler):
    def __init__(self, processing_queue):
        self.last_modified = 0
        self.debounce_seconds = 1.0
        self.queue = processing_queue

    def on_modified(self, event):
        # Watchdog returns paths with mixed slashes sometimes, normalize to string check
        if not event.src_path.endswith("inbox.txt"):
            return

        current_time = time.time()
        if current_time - self.last_modified < self.debounce_seconds:
            return
        
        self.last_modified = current_time
        print(f"Detected change in {event.src_path}. Queuing job.")
        
        # Add job to queue
        self.queue.put("PROCESS")

def start_monitoring(processing_queue):
    """Starts the directory observer AND a polling fallback."""
    print(f"Monitoring {DESKTOP_PATH} for changes to inbox.txt...")
    print(f"Monitoring {INBOX_BUFFER_DIR} for WhatsApp messages...")
    
    observer = Observer()
    
    # 1. Watch Desktop (Inbox)
    inbox_handler = InboxHandler(processing_queue)
    observer.schedule(inbox_handler, str(DESKTOP_PATH), recursive=False)
    
    # 2. Watch Buffer
    buffer_handler = BufferHandler(processing_queue)
    observer.schedule(buffer_handler, str(INBOX_BUFFER_DIR), recursive=False)

    observer.start()
    
    # 3. Initial Sweep
    print("Performing initial buffer sweep...")
    processing_queue.put("PROCESS")
    
    try:
        from src.file_ops import append_to_file
        from src.config import LOGS_DIR
        from datetime import datetime
        log_file = LOGS_DIR / "ingestion.log"

        while True:
            time.sleep(10)
            # POLLING FALLBACK: Check if buffer has files that watchdog missed
            if any(entry.endswith('.json') for entry in os.listdir(INBOX_BUFFER_DIR)):
                append_to_file(log_file, f"[{datetime.now()}] [MONITOR] Files found via Polling Fallback")
                processing_queue.put("PROCESS")
                
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()
