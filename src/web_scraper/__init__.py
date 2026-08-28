"""Web Scraper package."""

from web_scraper.config import ScraperConfig
from web_scraper.exceptions import FetchError, ParseError, RobotsDeniedError, ScraperError
from web_scraper.http_client import HTTPClient
from web_scraper.models import Book
from web_scraper.parser import parse_books, parse_next_page_url
from web_scraper.scraper import WebScraper

__all__ = [
    "Book",
    "ScraperConfig",
    "ScraperError",
    "FetchError",
    "ParseError",
    "RobotsDeniedError",
    "HTTPClient",
    "WebScraper",
    "parse_books",
    "parse_next_page_url",
]
