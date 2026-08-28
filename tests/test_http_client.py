"""Unit tests for the HTTP client wrapper (tests/test_http_client.py)."""

import unittest
from unittest.mock import MagicMock, patch
import requests

from web_scraper.exceptions import FetchError
from web_scraper.http_client import HTTPClient


class TestHTTPClient(unittest.TestCase):
    """Test suite for HTTP communication and exception mapping."""

    def setUp(self) -> None:
        self.mock_session = MagicMock(spec=requests.Session)
        self.mock_session.headers = {}
        self.client = HTTPClient(
            user_agent="TestUserAgent/1.0",
            timeout=5.0,
            session=self.mock_session,
        )

    def test_user_agent_header_configured(self) -> None:
        """Verify User-Agent header is registered on session."""
        self.assertEqual(self.mock_session.headers.get("User-Agent"), "TestUserAgent/1.0")

    def test_fetch_success(self) -> None:
        """Verify successful HTTP fetch returns response body."""
        mock_response = MagicMock()
        mock_response.text = "<html>Success</html>"
        self.mock_session.get.return_value = mock_response

        content = self.client.fetch("https://example.com/test")
        self.assertEqual(content, "<html>Success</html>")
        self.mock_session.get.assert_called_once_with("https://example.com/test", timeout=5.0)

    def test_fetch_timeout(self) -> None:
        """Verify Timeout exception is wrapped in FetchError."""
        self.mock_session.get.side_effect = requests.Timeout("Connection timed out")

        with self.assertRaises(FetchError) as ctx:
            self.client.fetch("https://example.com/timeout")

        self.assertIn("timed out", str(ctx.exception))

    def test_fetch_connection_error(self) -> None:
        """Verify ConnectionError exception is wrapped in FetchError."""
        self.mock_session.get.side_effect = requests.ConnectionError("DNS failure")

        with self.assertRaises(FetchError) as ctx:
            self.client.fetch("https://example.com/connerror")

        self.assertIn("Failed to connect", str(ctx.exception))

    def test_fetch_http_error(self) -> None:
        """Verify HTTP 404/500 errors raise FetchError."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_http_err = requests.HTTPError("404 Client Error", response=mock_response)
        self.mock_session.get.side_effect = mock_http_err

        with self.assertRaises(FetchError) as ctx:
            self.client.fetch("https://example.com/404")

        self.assertIn("HTTP error 404", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
