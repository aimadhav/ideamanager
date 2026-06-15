import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.ingestor import _enrich_content, _finalize_item

class TestIngestorLogic(unittest.TestCase):
    
    @patch('src.ingestor.Capabilities')
    def test_enrich_content_links(self, mock_caps):
        # Mocking extract_urls to return a list of URLs
        mock_caps.extract_urls.return_value = ["https://youtube.com/watch?v=123"]
        mock_caps.is_youtube_url.return_value = True
        mock_caps.fetch_youtube_transcript.return_value = ("Video Title", "Transcript content")
        
        text = "Check this video: https://youtube.com/watch?v=123"
        result = _enrich_content(text)
        
        self.assertIn("YOUTUBE TRANSCRIPT: Video Title", result)
        self.assertIn("Transcript content", result)

    @patch('src.ingestor.registry')
    @patch('src.ingestor.ai')
    @patch('src.ingestor.append_to_file')
    def test_finalize_item_append(self, mock_append, mock_ai, mock_registry):
        # Mock AI output
        mock_ai.process_thought.return_value = {
            "action": "append",
            "entity": "TestEntity",
            "folder": "test_folder",
            "refined_content": "Cleaned thought",
            "summary": "Updating test entity"
        }
        
        _finalize_item("Original thought")
        
        # Verify append_to_file was called with the right path
        # Note: In _finalize_item, the path is MEMORIES_DIR / safe_folder / safe_entity.md
        self.assertTrue(mock_append.called)
        args, _ = mock_append.call_args
        # Entity "TestEntity" -> safe_entity "testentity"
        self.assertIn("testentity.md", str(args[0]).lower())
        self.assertIn("Cleaned thought", args[1])

if __name__ == "__main__":
    unittest.main()
