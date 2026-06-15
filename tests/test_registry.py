import unittest
import json
import os
from pathlib import Path
from src.registry import Registry

class TestRegistry(unittest.TestCase):
    def setUp(self):
        # Use a temporary registry file
        self.test_file = Path("test_registry.json")
        if self.test_file.exists():
            os.remove(self.test_file)
        
        # Monkey-patch the REGISTRY_FILE in the registry module
        import src.registry
        self.original_registry_file = src.registry.REGISTRY_FILE
        src.registry.REGISTRY_FILE = self.test_file
        
        self.reg = Registry()

    def tearDown(self):
        if self.test_file.exists():
            os.remove(self.test_file)
        import src.registry
        src.registry.REGISTRY_FILE = self.original_registry_file

    def test_ensure_registry_creates_file(self):
        self.assertTrue(self.test_file.exists())
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data, {"entities": {}})

    def test_add_entity(self):
        self.reg.add_entity("TestEntity", "test_folder", "Memories/test_folder/test_entity.md", "A test summary")
        entity = self.reg.find_entity("TestEntity")
        self.assertIsNotNone(entity)
        self.assertEqual(entity["entity_name"], "TestEntity")
        self.assertEqual(entity["folder"], "test_folder")
        self.assertEqual(entity["summary"], "A test summary")

    def test_find_entity_case_insensitive(self):
        self.reg.add_entity("TestEntity", "test_folder", "path.md")
        entity = self.reg.find_entity("testentity")
        self.assertIsNotNone(entity)
        self.assertEqual(entity["entity_name"], "TestEntity")

    def test_update_entity_timestamp(self):
        self.reg.add_entity("TestEntity", "test_folder", "path.md")
        old_timestamp = self.reg.find_entity("TestEntity")["last_updated"]
        # Small sleep to ensure timestamp changes if isoformat is granular enough
        import time
        time.sleep(0.01)
        self.reg.update_entity_timestamp("TestEntity")
        new_timestamp = self.reg.find_entity("TestEntity")["last_updated"]
        self.assertNotEqual(old_timestamp, new_timestamp)

    def test_get_all_entities_summary(self):
        self.reg.add_entity("Entity1", "folder1", "path1.md", "Summary 1")
        self.reg.add_entity("Entity2", "folder2", "path2.md", "Summary 2")
        summary = self.reg.get_all_entities_summary()
        self.assertIn("Entity1 (folder1) - Summary 1", summary)
        self.assertIn("Entity2 (folder2) - Summary 2", summary)

    def test_add_entity_special_chars(self):
        # Testing if it handles weird names (the registry itself doesn't sanitize, 
        # but ingestor does. Registry just stores what it's given)
        self.reg.add_entity("Entity! @#", "folder", "path.md")
        entity = self.reg.find_entity("entity! @#")
        self.assertIsNotNone(entity)

if __name__ == "__main__":
    unittest.main()
