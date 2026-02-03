import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from pypdf import PdfReader
from urllib.parse import urlparse, parse_qs
import re
import os

class Capabilities:
    """
    The 'Eyes' of the system. Handles external content fetching.
    """

    @staticmethod
    def extract_urls(text):
        """Finds all URLs in a text string."""
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        return url_pattern.findall(text)

    @staticmethod
    def is_youtube_url(url):
        """Checks if a URL is a YouTube link."""
        parsed = urlparse(url)
        return "youtube.com" in parsed.netloc or "youtu.be" in parsed.netloc

    @staticmethod
    def fetch_youtube_transcript(url):
        """
        Fetches the transcript of a YouTube video.
        Returns: (title, transcript_text) or (None, None)
        """
        try:
            video_id = None
            parsed = urlparse(url)
            
            if "youtu.be" in parsed.netloc:
                video_id = parsed.path.strip("/")
            elif "youtube.com" in parsed.netloc:
                query = parse_qs(parsed.query)
                video_id = query.get("v", [None])[0]

            if not video_id:
                return None, "Could not extract Video ID"

            # Get Transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            formatter = TextFormatter()
            transcript_text = formatter.format_transcript(transcript_list)
            
            # Try to get Title (simple scrape to avoid API key)
            try:
                r = requests.get(url)
                soup = BeautifulSoup(r.text, 'html.parser')
                title = soup.title.string.replace("- YouTube", "").strip()
            except:
                title = f"YouTube Video ({video_id})"

            return title, transcript_text

        except Exception as e:
            return None, f"Error fetching transcript: {str(e)}"

    @staticmethod
    def fetch_web_content(url):
        """
        Fetches the main text content of a web page.
        Returns: (title, text_content)
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            title = soup.title.string.strip() if soup.title else "No Title"
            
            # Get text
            text = soup.get_text(separator='\n')
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # Limit length to avoid token limits (approx 10k chars)
            return title, text[:15000]

        except Exception as e:
            return None, f"Error fetching web content: {str(e)}"

    @staticmethod
    def extract_pdf_text(filepath):
        """
        Extracts text from a local PDF file.
        """
        try:
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
