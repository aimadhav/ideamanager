import threading
import queue
import time
import socket
import sys
from src.monitor import start_monitoring
from src.ingestor import process_inbox

def get_lock(port=65432):
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
    while True:
        task = q.get()
        if task == "PROCESS":
            print("Worker: Processing Inbox...")
            # We add a small sleep to ensure file write is complete
            time.sleep(0.5) 
            try:
                process_inbox()
            except Exception as e:
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
    
    # Start Monitor (blocks main thread)
    start_monitoring(job_queue)
