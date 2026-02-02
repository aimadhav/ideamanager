import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base Project Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Paths
user_profile = os.environ.get("USERPROFILE")
if not user_profile:
    # Fallback for some windows environments or non-standard setups
    user_profile = os.path.expanduser("~")

DESKTOP_PATH = Path(user_profile) / "Desktop"
INBOX_FILE = DESKTOP_PATH / "inbox.txt"

MEMORIES_DIR = BASE_DIR / "Memories"
DATA_DIR = BASE_DIR / "data"
RAW_HISTORY_FILE = DATA_DIR / "raw" / "history.txt"
LOGS_DIR = DATA_DIR / "logs"

# Ensure directories exist
MEMORIES_DIR.mkdir(parents=True, exist_ok=True)
RAW_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
