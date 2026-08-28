"""Unit tests for the HTML parser module (tests/test_parser.py)."""

import unittest
from pathlib import Path
from web_scraper.parser import parse_books, parse_next_page_url

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "books_page.html"
BASE_URL = "https://books.toscrape.com/"


class TestParser(unittest.TestCase):
    """Test suite for HTML parsing and data extraction logic."""

    @classmethod
    def setUpClass(cls) -> None:
        with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
            cls.fixture_html = f.read()

    def test_parse_books_count_and_order(self) -> None:
        """Verify the parser extracts all books preserving original DOM order."""
        books = parse_books(self.fixture_html, BASE_URL)
        self.assertEqual(len(books), 3)

        self.assertEqual(books[0].title, "A Light in the Attic")
        self.assertEqual(books[1].title, "Tipping the Velvet")
        self.assertEqual(books[2].title, "Soumission")

    def test_parse_book_fields(self) -> None:
        """Verify detailed attributes of extracted Book objects."""
        books = parse_books(self.fixture_html, BASE_URL)
        book1 = books[0]
        book2 = books[1]

        self.assertEqual(book1.title, "A Light in the Attic")
        self.assertEqual(book1.price, "£51.77")
        self.assertEqual(book1.availability, "In stock")
        self.assertEqual(book1.rating, 3)
        self.assertEqual(
            book1.url,
            "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        )
        self.assertEqual(book2.rating, 1)

    def test_missing_rating(self) -> None:
        """Verify that a book missing star rating class defaults rating to None."""
        books = parse_books(self.fixture_html, BASE_URL)
        book3 = books[2]
        self.assertIsNone(book3.rating)

    def test_whitespace_normalization(self) -> None:
        """Verify title and availability whitespace is cleaned."""
        books = parse_books(self.fixture_html, BASE_URL)
        book3 = books[2]
        self.assertEqual(book3.title, "Soumission")
        self.assertEqual(book3.availability, "In stock")

    def test_relative_url_conversion(self) -> None:
        """Verify relative URLs are converted to raw absolute URLs without markdown markup."""
        books = parse_books(self.fixture_html, BASE_URL)
        for book in books:
            self.assertTrue(book.url.startswith("https://books.toscrape.com/"))
            self.assertNotIn("[", book.url)
            self.assertNotIn("]", book.url)

    def test_empty_html(self) -> None:
        """Verify passing empty or whitespace HTML returns an empty list."""
        self.assertEqual(parse_books("", BASE_URL), [])
        self.assertEqual(parse_books("   ", BASE_URL), [])

    def test_malformed_html(self) -> None:
        """Verify parsing handles incomplete or malformed HTML gracefully."""
        malformed = "<article class='product_pod'><h3><a href='b1.html'>Partial Book</a>"
        books = parse_books(malformed, BASE_URL)
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, "Partial Book")

    def test_parse_next_page_url(self) -> None:
        """Verify extraction of absolute pagination link."""
        next_url = parse_next_page_url(self.fixture_html, BASE_URL)
        self.assertEqual(next_url, "https://books.toscrape.com/catalogue/page-2.html")

    def test_parse_next_page_url_none(self) -> None:
        """Verify next_page_url returns None when pagination link is absent."""
        no_next_html = "<html><body><p>No pagination here</p></body></html>"
        self.assertIsNone(parse_next_page_url(no_next_html, BASE_URL))
        self.assertIsNone(parse_next_page_url("", BASE_URL))


if __name__ == "__main__":
    unittest.main()
