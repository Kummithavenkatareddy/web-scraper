"""HTTP client wrapper responsible exclusively for network communications."""

import requests
from web_scraper.config import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT
from web_scraper.exceptions import FetchError


class HTTPClient:
    """Thin wrapper around requests.Session to enforce timeouts, custom User-Agent headers,

    and domain exception handling.
    """

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: float = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        """Initialize the HTTP client.

        Args:
            user_agent: Custom User-Agent header string.
            timeout: Default request timeout in seconds.
            session: Optional pre-configured requests.Session for testing/injection.
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self._session = session or requests.Session()
        self._session.headers.update({"User-Agent": self.user_agent})

    def fetch(self, url: str, timeout: float | None = None) -> str:
        """Fetch HTML text from a target URL.

        Args:
            url: Target HTTP/HTTPS URL.
            timeout: Optional override for default request timeout.

        Returns:
            HTML page content as a string.

        Raises:
            FetchError: If the request fails, times out, returns an HTTP error code, or connection fails.
        """
        req_timeout = timeout if timeout is not None else self.timeout

        try:
            response = self._session.get(url, timeout=req_timeout)
            response.raise_for_status()
            if response.encoding is None or response.encoding.lower() == "iso-8859-1":
                response.encoding = response.apparent_encoding or "utf-8"
            return response.text
        except requests.Timeout as exc:
            raise FetchError(f"Request to '{url}' timed out after {req_timeout}s.") from exc
        except requests.ConnectionError as exc:
            raise FetchError(f"Failed to connect to '{url}'. Check network or URL.") from exc
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else "Unknown"
            raise FetchError(f"HTTP error {status_code} received from '{url}'.") from exc
        except requests.RequestException as exc:
            raise FetchError(f"An error occurred while fetching '{url}': {exc}") from exc

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> "HTTPClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
