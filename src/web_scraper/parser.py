"""HTML parsing module using BeautifulSoup for extracting structured book data."""

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from web_scraper.models import Book


RATING_MAP = {
    "One": 1,
    "1": 1,
    "Two": 2,
    "2": 2,
    "Three": 3,
    "3": 3,
    "Four": 4,
    "4": 4,
    "Five": 5,
    "5": 5,
}


def parse_books(html: str, base_url: str) -> list[Book]:
    """Parse HTML text and extract structured Book entities.

    Args:
        html: Raw HTML content of a book catalog page.
        base_url: Base URL used to resolve relative product URLs into absolute URLs.

    Returns:
        List of extracted Book objects preserving catalog page order.
    """
    if not html or not html.strip():
        return []

    soup = BeautifulSoup(html, "html.parser")
    book_pods = soup.select("article.product_pod")
    books: list[Book] = []

    for pod in book_pods:
        # Extract title and product URL from h3 > a
        title_anchor = pod.select_one("h3 a")
        if not title_anchor:
            continue

        title = title_anchor.get("title") or title_anchor.get_text(strip=True)
        raw_href = title_anchor.get("href", "")
        product_url = urljoin(base_url, raw_href) if raw_href else base_url

        # Extract price
        price_elem = pod.select_one(".price_color")
        price = price_elem.get_text(strip=True) if price_elem else "N/A"

        # Extract availability status
        availability_elem = pod.select_one(".availability")
        availability = " ".join(availability_elem.get_text().split()) if availability_elem else "Unknown"

        # Extract numeric star rating from class attribute (e.g. 'star-rating Three' -> 3)
        rating: int | None = None
        rating_elem = pod.select_one(".star-rating")
        if rating_elem and rating_elem.has_attr("class"):
            classes = rating_elem["class"]
            rating_classes = [c for c in classes if c != "star-rating"]
            if rating_classes:
                rating = RATING_MAP.get(rating_classes[0], None)

        book = Book(
            title=title,
            price=price,
            availability=availability,
            url=product_url,
            rating=rating,
        )
        books.append(book)

    return books


def parse_next_page_url(html: str, base_url: str) -> str | None:
    """Extract next page URL from catalog pagination links.

    Args:
        html: Raw HTML content of catalog page.
        base_url: Current page URL used for joining relative links.

    Returns:
        Absolute URL to the next page, or None if no next page exists.
    """
    if not html or not html.strip():
        return None

    soup = BeautifulSoup(html, "html.parser")
    next_anchor = soup.select_one("ul.pager li.next a")
    if next_anchor and next_anchor.has_attr("href"):
        relative_href = next_anchor["href"]
        return urljoin(base_url, relative_href)

    return None
