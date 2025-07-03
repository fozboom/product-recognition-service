import logging
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

# Get logger with a specific name that matches the one in logging_config.yaml
logger = logging.getLogger("src.product_recognition_service.url_processor")


class URLProcessor:
    """
    A class to fetch, process, and save web content from a URL.

    This class handles fetching HTML from a URL, extracting clean text content,
    and saving both the raw HTML and the extracted text to specified directories.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def __init__(self, url: str, html_output_dir: Path | None = None, text_output_dir: Path | None = None):
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise ValueError("A valid URL starting with http:// or https:// is required.")
        logger.debug(f"Processing URL: {url}")
        self.url = url
        self.html_output_dir = html_output_dir
        self.text_output_dir = text_output_dir
        self.text_content: str | None = None

        self.file_name_base = self._url_to_filename_base()

        if self.html_output_dir:
            self.html_output_dir.mkdir(parents=True, exist_ok=True)
        if self.text_output_dir:
            self.text_output_dir.mkdir(parents=True, exist_ok=True)

    def _url_to_filename_base(self) -> str:
        """Converts the URL to a safe and valid base filename (without extension)."""
        filename = self.url.replace("https://", "").replace("http://", "").replace("/", "_")
        filename = re.sub(r'[\\/*?:"<>|]', "", filename)

        return filename[:150]

    def _fetch_html(self) -> str | None:
        """Fetches the HTML content from the URL."""

        with httpx.Client(
            headers=self.headers,
            follow_redirects=True,
            timeout=httpx.Timeout(30.0, connect=10.0),
        ) as client:
            r = client.get(self.url)
            r.raise_for_status()  # raises on 4xx/5xx

            logger.debug(f"Successfully fetched {self.url}")

            return r.text

    @staticmethod
    def _extract_text_from_html(html: str) -> str:
        """Extracts and cleans visible text from HTML content."""
        soup = BeautifulSoup(html, "lxml")
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return text

    def _save_content_to_file(self, content: str, output_path: Path) -> None:
        """Saves the given content to a file."""
        try:
            output_path.write_text(content, encoding="utf-8")
            logger.info(f"Successfully saved content to {output_path}")
        except IOError as e:
            logger.error(f"Error writing to file {output_path}: {e}")

    def process(self) -> bool:
        """
        Fetch data from url, save HTML, extract text, save text.

        Returns:
            True if the entire process was successful, False otherwise.
        """
        html_content = self._fetch_html()
        if not html_content:
            return False

        if self.html_output_dir:
            html_file_path = self.html_output_dir / f"{self.file_name_base}.html"
            self._save_content_to_file(html_content, html_file_path)

        if self.text_output_dir:
            self.text_content = self._extract_text_from_html(html_content)

            text_with_source = f"{self.text_content}\n\nSource URL: {self.url}"
            text_file_path = self.text_output_dir / f"{self.file_name_base}.txt"
            self._save_content_to_file(text_with_source, text_file_path)

        return True

    def extract_text_from_url(self) -> str:
        """
        Extracts text from a URL.
        """
        html = self._fetch_html()
        if not html:
            return ""
        return self._extract_text_from_html(html)
