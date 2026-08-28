"""Unit tests for WebScraper orchestration, pagination, robots.txt, and delay (tests/test_scraper.py)."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from web_scraper.config import ScraperConfig
from web_scraper.exceptions import FetchError, RobotsDeniedError
from web_scraper.http_client import HTTPClient
from web_scraper.scraper import WebScraper

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "books_page.html"


class TestWebScraper(unittest.TestCase):
    """Test suite for WebScraper crawling workflow."""

    @classmethod
    def setUpClass(cls) -> None:
        with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
            cls.fixture_html = f.read()

        # HTML for page 2 (no further pagination)
        cls.page2_html = """
        <html>
        <body>
            <article class="product_pod">
                <h3><a href="book_p2.html" title="Page 2 Book">Page 2 Book</a></h3>
                <div class="product_price">
                    <p class="price_color">£15.00</p>
                    <p class="instock availability">In stock</p>
                </div>
            </article>
        </body>
        </html>
        """

    def setUp(self) -> None:
        self.mock_http_client = MagicMock(spec=HTTPClient)

    @patch("web_scraper.scraper.WebScraper.check_robots_txt")
    def test_single_page_scrape(self, mock_check_robots: MagicMock) -> None:
        """Verify scraper stops after max_pages=1 despite next page link."""
        self.mock_http_client.fetch.return_value = self.fixture_html
        config = ScraperConfig(
            target_url="https://books.toscrape.com/",
            max_pages=1,
            delay=0,
        )
        scraper = WebScraper(config=config, http_client=self.mock_http_client)

        books = scraper.scrape()
        self.assertEqual(len(books), 3)
        self.mock_http_client.fetch.assert_called_once_with("https://books.toscrape.com/")
        mock_check_robots.assert_called_once_with("https://books.toscrape.com/")

    @patch("time.sleep")
    @patch("web_scraper.scraper.WebScraper.check_robots_txt")
    def test_multi_page_scrape(self, mock_check_robots: MagicMock, mock_sleep: MagicMock) -> None:
        """Verify scraper crawls page 1 and page 2 up to max_pages=2."""
        self.mock_http_client.fetch.side_effect = [self.fixture_html, self.page2_html]
        config = ScraperConfig(
            target_url="https://books.toscrape.com/",
            max_pages=2,
            delay=1.5,
        )
        scraper = WebScraper(config=config, http_client=self.mock_http_client)

        books = scraper.scrape()
        self.assertEqual(len(books), 4)  # 3 from page 1 + 1 from page 2
        self.assertEqual(self.mock_http_client.fetch.call_count, 2)
        mock_sleep.assert_called_once_with(1.5)

    @patch("web_scraper.scraper.RobotFileParser")
    def test_check_robots_txt_disallowed(self, mock_rfp_class: MagicMock) -> None:
        """Verify RobotsDeniedError is raised when robots.txt forbids target URL."""
        mock_rfp = MagicMock()
        mock_rfp.can_fetch.return_value = False
        mock_rfp_class.return_value = mock_rfp
        self.mock_http_client.fetch.return_value = "User-agent: *\nDisallow: /"

        config = ScraperConfig(target_url="https://books.toscrape.com/secret")
        scraper = WebScraper(config=config, http_client=self.mock_http_client)

        with self.assertRaises(RobotsDeniedError):
            scraper.check_robots_txt("https://books.toscrape.com/secret")

    @patch("web_scraper.scraper.WebScraper.check_robots_txt")
    def test_fetch_error_bubbles_up(self, mock_check_robots: MagicMock) -> None:
        """Verify FetchError raised during scraping bubbles up to caller."""
        self.mock_http_client.fetch.side_effect = FetchError("Network unreachable")
        config = ScraperConfig(target_url="https://books.toscrape.com/")
        scraper = WebScraper(config=config, http_client=self.mock_http_client)

        with self.assertRaises(FetchError):
            scraper.scrape()


if __name__ == "__main__":
    unittest.main()
