"""Scraper orchestration engine managing crawling, pagination, robots.txt, and rate limiting."""

import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from web_scraper.config import ScraperConfig
from web_scraper.exceptions import FetchError, RobotsDeniedError
from web_scraper.http_client import HTTPClient
from web_scraper.models import Book
from web_scraper.parser import parse_books, parse_next_page_url


class WebScraper:
    """Orchestrates structured web scraping workflows across single or multiple pages."""

    def __init__(
        self,
        config: ScraperConfig | None = None,
        http_client: HTTPClient | None = None,
    ) -> None:
        """Initialize scraper with configuration and optional HTTP client dependency injection.

        Args:
            config: Scraper configuration options.
            http_client: Custom or mocked HTTP client instance.
        """
        self.config = config or ScraperConfig()
        self.http_client = http_client or HTTPClient(
            user_agent=self.config.user_agent,
            timeout=self.config.timeout,
        )

    def check_robots_txt(self, url: str) -> None:
        """Check if target URL is allowed by the site's robots.txt policy.

        Args:
            url: Target URL to check.

        Raises:
            RobotsDeniedError: If the URL is explicitly disallowed for the user agent.
        """
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return

        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rfp = RobotFileParser()
        rfp.set_url(robots_url)

        try:
            robots_txt = self.http_client.fetch(robots_url)
            rfp.parse(robots_txt.splitlines())
        except FetchError:
            # If robots.txt is 404 or unreachable, default to allowing fetch per standard guidelines
            return

        if not rfp.can_fetch(self.config.user_agent, url):
            raise RobotsDeniedError(
                f"Access to '{url}' is disallowed by robots.txt for User-Agent '{self.config.user_agent}'."
            )

    def scrape(self) -> list[Book]:
        """Execute web scraping workflow according to configured max_pages and delay.

        Returns:
            List of aggregated Book items scraped across pages.

        Raises:
            RobotsDeniedError: If disallowed by robots.txt.
            FetchError: If network request fails.
        """
        target_url = self.config.target_url
        self.check_robots_txt(target_url)

        scraped_books: list[Book] = []
        current_url: str | None = target_url
        pages_scraped = 0

        while current_url and pages_scraped < self.config.max_pages:
            html = self.http_client.fetch(current_url)
            page_books = parse_books(html, current_url)
            scraped_books.extend(page_books)
            pages_scraped += 1

            next_url = parse_next_page_url(html, current_url)
            if next_url and pages_scraped < self.config.max_pages:
                if self.config.delay > 0:
                    time.sleep(self.config.delay)
                current_url = next_url
            else:
                current_url = None

        return scraped_books
