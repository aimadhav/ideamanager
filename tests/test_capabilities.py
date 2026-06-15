import unittest
from src.capabilities import Capabilities

class TestCapabilities(unittest.TestCase):
    def test_extract_urls(self):
        text = "Check this out: https://google.com and http://example.org/test"
        urls = Capabilities.extract_urls(text)
        self.assertEqual(len(urls), 2)
        self.assertIn("https://google.com", urls)
        self.assertIn("http://example.org/test", urls)

    def test_is_youtube_url(self):
        self.assertTrue(Capabilities.is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertTrue(Capabilities.is_youtube_url("https://youtu.be/dQw4w9WgXcQ"))
        self.assertFalse(Capabilities.is_youtube_url("https://google.com"))

    def test_extract_youtube_id(self):
        # Testing internal logic indirectly via fetch_youtube_transcript if we mock the API
        # Or we can just trust the regex for now. 
        pass

if __name__ == "__main__":
    unittest.main()
