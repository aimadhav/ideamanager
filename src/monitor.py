import time
import os
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.config import INBOX_FILE, DESKTOP_PATH

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
    """Starts the directory observer."""
    print(f"Monitoring {DESKTOP_PATH} for changes to inbox.txt...")
    
    event_handler = InboxHandler(processing_queue)
    observer = Observer()
    observer.schedule(event_handler, str(DESKTOP_PATH), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()
