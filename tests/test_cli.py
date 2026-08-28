"""Unit tests for CLI parsing, formatting, and file exports (tests/test_cli.py)."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from web_scraper.cli import (
    build_parser,
    format_csv,
    format_json,
    format_table,
    main,
)
from web_scraper.exceptions import FetchError, RobotsDeniedError
from web_scraper.models import Book


class TestCLI(unittest.TestCase):
    """Test suite for CLI argument parser, formatters, and file execution."""

    def setUp(self) -> None:
        self.sample_books = [
            Book(
                title="Book One",
                price="£10.00",
                availability="In stock",
                url="https://example.com/b1",
                rating="Five",
                category="Fiction",
            ),
            Book(
                title="Book Two",
                price="£20.00",
                availability="In stock",
                url="https://example.com/b2",
                rating="Three",
                category="Non-Fiction",
            ),
        ]

    def test_build_parser_defaults(self) -> None:
        """Verify default CLI parser values."""
        parser = build_parser()
        args = parser.parse_args([])
        self.assertEqual(args.url, "https://books.toscrape.com/")
        self.assertEqual(args.max_pages, 1)
        self.assertEqual(args.delay, 1.0)
        self.assertEqual(args.timeout, 10.0)
        self.assertEqual(args.format, "table")
        self.assertIsNone(args.output)

    def test_build_parser_custom_args(self) -> None:
        """Verify explicit argument parsing."""
        parser = build_parser()
        args = parser.parse_args([
            "https://custom.site/",
            "--max-pages", "3",
            "--delay", "0.5",
            "--timeout", "15",
            "--format", "json",
            "--output", "out.json",
        ])
        self.assertEqual(args.url, "https://custom.site/")
        self.assertEqual(args.max_pages, 3)
        self.assertEqual(args.delay, 0.5)
        self.assertEqual(args.timeout, 15.0)
        self.assertEqual(args.format, "json")
        self.assertEqual(args.output, "out.json")

    def test_format_json(self) -> None:
        """Verify JSON output structure."""
        json_str = format_json(self.sample_books)
        data = json.loads(json_str)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["title"], "Book One")
        self.assertEqual(data[1]["price"], "£20.00")

    def test_format_csv(self) -> None:
        """Verify CSV output header and rows."""
        csv_str = format_csv(self.sample_books)
        lines = csv_str.strip().splitlines()
        self.assertEqual(lines[0], "title,price,availability,rating,category,url")
        self.assertIn("Book One", lines[1])
        self.assertIn("Book Two", lines[2])

    def test_format_table(self) -> None:
        """Verify table output includes headers and formatted rows."""
        table_str = format_table(self.sample_books)
        self.assertIn("Title", table_str)
        self.assertIn("Book One", table_str)
        self.assertIn("Book Two", table_str)

    @patch("web_scraper.cli.WebScraper")
    def test_main_stdout_execution(self, mock_scraper_cls: MagicMock) -> None:
        """Verify CLI main execution printing to stdout."""
        mock_instance = MagicMock()
        mock_instance.scrape.return_value = self.sample_books
        mock_scraper_cls.return_value = mock_instance

        with patch("sys.stdout") as mock_stdout:
            exit_code = main(["--format", "json"])
            self.assertEqual(exit_code, 0)
            mock_instance.scrape.assert_called_once()

    @patch("web_scraper.cli.WebScraper")
    def test_main_output_file_writing(self, mock_scraper_cls: MagicMock) -> None:
        """Verify CLI writes formatted output to specified file."""
        mock_instance = MagicMock()
        mock_instance.scrape.return_value = self.sample_books
        mock_scraper_cls.return_value = mock_instance

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = Path(tmp_dir) / "output.json"
            exit_code = main(["--format", "json", "--output", str(out_file)])
            self.assertEqual(exit_code, 0)
            self.assertTrue(out_file.exists())
            written_data = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(len(written_data), 2)

    @patch("web_scraper.cli.WebScraper")
    def test_main_error_handling(self, mock_scraper_cls: MagicMock) -> None:
        """Verify domain errors are caught cleanly without raw tracebacks."""
        mock_instance = MagicMock()
        mock_instance.scrape.side_effect = RobotsDeniedError("Access forbidden")
        mock_scraper_cls.return_value = mock_instance

        with patch("sys.stderr") as mock_stderr:
            exit_code = main([])
            self.assertEqual(exit_code, 1)

    def test_main_invalid_args(self) -> None:
        """Verify invalid CLI arguments return non-zero exit code."""
        self.assertEqual(main(["--max-pages", "0"]), 1)
        self.assertEqual(main(["--delay", "-1"]), 1)
        self.assertEqual(main(["--timeout", "0"]), 1)


if __name__ == "__main__":
    unittest.main()
