import os
import time
from src.config import INBOX_FILE

def read_inbox(retries=3, delay=0.1):
    """Reads the inbox file safely."""
    for i in range(retries):
        try:
            if not INBOX_FILE.exists():
                return ""
            with open(INBOX_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except OSError:
            if i < retries - 1:
                time.sleep(delay)
                continue
    return ""

def clear_inbox(retries=3, delay=0.1):
    """Clears the inbox file safely."""
    for i in range(retries):
        try:
            with open(INBOX_FILE, 'w', encoding='utf-8') as f:
                f.write("")
            return True
        except OSError:
            if i < retries - 1:
                time.sleep(delay)
                continue
            return False
    return False

def pop_inbox(retries=5, delay=0.1):
    """Reads and clears the inbox file using a rename strategy to avoid race conditions."""
    processing_file = INBOX_FILE.with_name(f"inbox_processing_{int(time.time())}.txt")
    
    for i in range(retries):
        try:
            if not INBOX_FILE.exists():
                return ""
            
            # CLAIM THE FILE: Check if it has real content first
            with open(INBOX_FILE, 'r', encoding='utf-8') as check_f:
                if not check_f.read().strip():
                    return ""

            # Rename first to claim the file
            os.rename(INBOX_FILE, processing_file)

            
            # Immediately recreate the empty inbox file so the user can continue writing
            # We use a brief sleep or try loop to ensure OS releases the handle if needed
            try:
                with open(INBOX_FILE, 'w', encoding='utf-8') as f:
                    f.write("")
            except OSError:
                pass # If it fails, the user or next loop will create it, but we try best effort here

            with open(processing_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Delete the processing file
            os.remove(processing_file)
            
            return content
        except OSError:
            # If rename fails (file locked/missing), wait and retry
            if i < retries - 1:
                time.sleep(delay)
                continue
            return ""
    return ""

def append_to_file(filepath, content):
    """Appends content to a file with a newline."""
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(content + "\n")
        return True
    except Exception as e:
        print(f"Error writing to {filepath}: {e}")
        return False
