"""Custom exception hierarchy for web scraper error handling."""


class ScraperError(Exception):
    """Base exception for all web scraper errors."""

    pass


class FetchError(ScraperError):
    """Raised when an HTTP request fails due to network, status code, or timeout errors."""

    pass


class ParseError(ScraperError):
    """Raised when HTML parsing fails to extract required content."""

    pass


class RobotsDeniedError(ScraperError):
    """Raised when access to a URL is disallowed by the target site's robots.txt policy."""

    pass
