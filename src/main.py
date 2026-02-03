import threading
import queue
import time
import socket
import sys
from src.config import SINGLE_INSTANCE_PORT
from src.monitor import start_monitoring
from src.ingestor import process_inbox

def get_lock(port=SINGLE_INSTANCE_PORT):
    """
    Enforces a single instance of the application by binding to a local TCP port.
    Returns the socket object which must be kept alive.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        return s
    except socket.error:
        print("Another instance is already running. Exiting.")
        sys.exit(1)

def worker(q):
    from src.config import LOGS_DIR
    from src.file_ops import append_to_file
    from datetime import datetime
    log_file = LOGS_DIR / "ingestion.log"

    while True:
        task = q.get()
        if task == "PROCESS":
            append_to_file(log_file, f"[{datetime.now()}] [WORKER] Received PROCESS task")
            print("Worker: Processing Inbox...")
            # We add a small sleep to ensure file write is complete
            time.sleep(0.5) 
            try:
                process_inbox()
                append_to_file(log_file, f"[{datetime.now()}] [WORKER] Finished processing inbox")
            except Exception as e:
                append_to_file(log_file, f"[{datetime.now()}] [WORKER ERROR] {e}")
                print(f"Worker Error: {e}")
            q.task_done()

if __name__ == "__main__":
    # 1. Single Instance Guard
    # We assign it to a variable so it doesn't get garbage collected/closed
    instance_lock = get_lock()
    
    print("Ideamanager System Starting (Queue Mode)...")
    
    # Create Queue
    job_queue = queue.Queue()
    
    # Start Worker Thread
    t = threading.Thread(target=worker, args=(job_queue,), daemon=True)
    t.start()
    
    # Initial Sweep
    job_queue.put("PROCESS")

    # Start Monitor (with restart logic)
    while True:
        try:
            start_monitoring(job_queue)
        except Exception as e:
            print(f"Main Monitor Error: {e}")
            print("Restarting monitor in 5 seconds...")
            time.sleep(5)
