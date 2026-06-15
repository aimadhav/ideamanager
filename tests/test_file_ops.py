import unittest
import os
import time
from pathlib import Path
from src.file_ops import read_inbox, clear_inbox, pop_inbox, append_to_file
from src.config import INBOX_FILE

class TestFileOps(unittest.TestCase):
    def setUp(self):
        # Backup existing inbox if it exists
        self.inbox_backup_path = Path("inbox_backup_test.txt")
        if INBOX_FILE.exists():
            import shutil
            shutil.copy(INBOX_FILE, self.inbox_backup_path)
        
        # Ensure clean state
        if INBOX_FILE.exists():
            os.remove(INBOX_FILE)

    def tearDown(self):
        # Restore original inbox
        if INBOX_FILE.exists():
            os.remove(INBOX_FILE)
        if self.inbox_backup_path.exists():
            import shutil
            shutil.move(self.inbox_backup_path, INBOX_FILE)

    def test_append_to_file(self):
        test_file = Path("test_append.txt")
        if test_file.exists(): os.remove(test_file)
        
        append_to_file(test_file, "Line 1")
        append_to_file(test_file, "Line 2")
        
        with open(test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertEqual(lines[0].strip(), "Line 1")
            self.assertEqual(lines[1].strip(), "Line 2")
        
        os.remove(test_file)

    def test_read_inbox_empty(self):
        self.assertEqual(read_inbox(), "")

    def test_read_inbox_with_content(self):
        with open(INBOX_FILE, 'w', encoding='utf-8') as f:
            f.write("Hello World")
        self.assertEqual(read_inbox(), "Hello World")

    def test_clear_inbox(self):
        with open(INBOX_FILE, 'w', encoding='utf-8') as f:
            f.write("Some data")
        self.assertTrue(clear_inbox())
        self.assertEqual(read_inbox(), "")

    def test_pop_inbox(self):
        content = "Line to pop"
        with open(INBOX_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = pop_inbox()
        self.assertEqual(result, content)
        self.assertEqual(read_inbox(), "")

    def test_pop_inbox_empty_or_whitespace(self):
        # Should return empty string and not touch file if just whitespace
        with open(INBOX_FILE, 'w', encoding='utf-8') as f:
            f.write("   \n   ")
        
        result = pop_inbox()
        self.assertEqual(result, "")

    def test_append_to_file_error(self):
        # Mocking open to raise an exception
        from unittest.mock import patch, mock_open
        with patch("builtins.open", side_effect=IOError("Disk Full")):
            result = append_to_file("any_path", "content")
            self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
