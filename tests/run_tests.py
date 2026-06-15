import unittest
import sys
import os
from unittest.mock import MagicMock

# Mock dependencies that might be missing in the environment
try:
    import dotenv
except ImportError:
    print("Mocking dotenv")
    sys.modules['dotenv'] = MagicMock()

try:
    import google.generativeai
except ImportError:
    print("Mocking google.generativeai")
    sys.modules['google.generativeai'] = MagicMock()

try:
    import youtube_transcript_api
    import youtube_transcript_api.formatters
except ImportError:
    print("Mocking youtube_transcript_api")
    m = MagicMock()
    sys.modules['youtube_transcript_api'] = m
    sys.modules['youtube_transcript_api.formatters'] = m

try:
    import google
    import google.generativeai
    import google.api_core
    import google.api_core.exceptions
except ImportError:
    print("Mocking google")
    m = MagicMock()
    sys.modules['google'] = m
    sys.modules['google.generativeai'] = m
    sys.modules['google.api_core'] = m
    sys.modules['google.api_core.exceptions'] = m

try:
    import pypdf
except ImportError:
    print("Mocking pypdf")
    sys.modules['pypdf'] = MagicMock()

try:
    import watchdog
    import watchdog.observers
    import watchdog.events
except ImportError:
    print("Mocking watchdog")
    m = MagicMock()
    sys.modules['watchdog'] = m
    sys.modules['watchdog.observers'] = m
    sys.modules['watchdog.events'] = m

try:
    import requests
except ImportError:
    print("Mocking requests")
    sys.modules['requests'] = MagicMock()

try:
    import bs4
except ImportError:
    print("Mocking bs4")
    m = MagicMock()
    sys.modules['bs4'] = m
    sys.modules['BeautifulSoup'] = m

# Set PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

def run():
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    run()
