"""Central configuration and default settings for the web scraper."""

from dataclasses import dataclass

DEFAULT_TARGET_URL: str = "https://books.toscrape.com/"
DEFAULT_TIMEOUT: float = 10.0
DEFAULT_USER_AGENT: str = "Mozilla/5.0 (compatible; WebScraperEducational/1.0)"
DEFAULT_MAX_PAGES: int = 1
DEFAULT_DELAY: float = 1.0
DEFAULT_OUTPUT_FORMAT: str = "table"
ALLOWED_OUTPUT_FORMATS: tuple[str, ...] = ("table", "json", "csv")


@dataclass(frozen=True)
class ScraperConfig:
    """Runtime configuration container for scraper parameters.

    Attributes:
        target_url: Base or starting URL to scrape.
        timeout: HTTP request timeout in seconds.
        user_agent: Custom User-Agent header string.
        max_pages: Maximum number of pagination pages to scrape.
        delay: Time delay in seconds between consecutive page requests.
        output_format: Display or export format ('table', 'json', 'csv').
        output_file: Optional file path to write scraped results.
    """

    target_url: str = DEFAULT_TARGET_URL
    timeout: float = DEFAULT_TIMEOUT
    user_agent: str = DEFAULT_USER_AGENT
    max_pages: int = DEFAULT_MAX_PAGES
    delay: float = DEFAULT_DELAY
    output_format: str = DEFAULT_OUTPUT_FORMAT
    output_file: str | None = None
