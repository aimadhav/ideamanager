import unittest
from pathlib import Path
import os
import shutil
import time
from src.registry import Registry
from src.file_ops import pop_inbox, append_to_file

class TestCoreLogic(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_temp")
        self.test_dir.mkdir(exist_ok=True)
        # Mocking Registry to use a temp file
        self.registry_file = self.test_dir / "test_registry.json"
        if self.registry_file.exists():
            os.remove(self.registry_file)
        
    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_registry_initialization(self):
        from src.registry import REGISTRY_FILE
        # Temporarily redirect registry file for testing if possible or just test logic
        reg = Registry()
        # Test basic structure
        data = reg._load()
        self.assertIn("entities", data)

    def test_safe_file_pop(self):
        """Tests the atomic pop_inbox logic to ensure no data loss/duplication."""
        from src.config import INBOX_FILE
        # Backup original
        backup_content = ""
        if INBOX_FILE.exists():
            with open(INBOX_FILE, 'r', encoding='utf-8') as f:
                backup_content = f.read()
        
        try:
            test_content = "Unique Test Message 123"
            with open(INBOX_FILE, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            result = pop_inbox()
            self.assertEqual(result, test_content)
            
            # Verify file is empty/recreated
            if INBOX_FILE.exists():
                with open(INBOX_FILE, 'r', encoding='utf-8') as f:
                    self.assertEqual(f.read().strip(), "")
        finally:
            # Restore
            with open(INBOX_FILE, 'w', encoding='utf-8') as f:
                f.write(backup_content)

if __name__ == "__main__":
    unittest.main()
