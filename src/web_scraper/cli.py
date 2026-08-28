"""Command line interface (CLI) for running the web scraper application."""

import argparse
import csv
import io
import json
import sys
from pathlib import Path

from web_scraper.config import (
    ALLOWED_OUTPUT_FORMATS,
    DEFAULT_DELAY,
    DEFAULT_MAX_PAGES,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_TARGET_URL,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    ScraperConfig,
)
from web_scraper.exceptions import ScraperError
from web_scraper.models import Book
from web_scraper.scraper import WebScraper


def format_table(books: list[Book]) -> str:
    """Format books list as a clean ASCII text table.

    Args:
        books: List of scraped Book objects.

    Returns:
        Formatted multi-line text table string.
    """
    if not books:
        return "No books scraped."

    headers = ["#", "Title", "Price", "Availability", "Rating", "URL"]
    rows: list[list[str]] = []

    for idx, book in enumerate(books, start=1):
        # Truncate very long titles for neat terminal rendering
        title_disp = (book.title[:37] + "...") if len(book.title) > 40 else book.title
        rating_disp = book.rating or "N/A"
        rows.append([
            str(idx),
            title_disp,
            book.price,
            book.availability,
            rating_disp,
            book.url,
        ])

    # Compute column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(val))

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    separator_line = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    row_lines = [
        " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
        for row in rows
    ]

    return "\n".join([header_line, separator_line] + row_lines)


def format_json(books: list[Book]) -> str:
    """Format books list as a JSON string.

    Args:
        books: List of scraped Book objects.

    Returns:
        JSON array string.
    """
    data = [book.to_dict() for book in books]
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_csv(books: list[Book]) -> str:
    """Format books list as a CSV string.

    Args:
        books: List of scraped Book objects.

    Returns:
        CSV formatted text string.
    """
    if not books:
        return ""

    output = io.StringIO()
    fieldnames = ["title", "price", "availability", "rating", "category", "url"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for book in books:
        writer.writerow(book.to_dict())
    return output.getvalue()


def format_output(books: list[Book], fmt: str) -> str:
    """Format books according to specified format string.

    Args:
        books: List of scraped Book objects.
        fmt: Target format ('table', 'json', 'csv').

    Returns:
        Formatted text output.
    """
    fmt_lower = fmt.lower()
    if fmt_lower == "json":
        return format_json(books)
    elif fmt_lower == "csv":
        return format_csv(books)
    else:
        return format_table(books)


def build_parser() -> argparse.ArgumentParser:
    """Construct command-line argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="web-scraper",
        description="Extract structured book catalog data from scraping-friendly websites.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "url",
        nargs="?",
        default=DEFAULT_TARGET_URL,
        help="Target web page URL to scrape.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help="Maximum number of pagination pages to crawl.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help="Delay in seconds between consecutive HTTP requests.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="HTTP request timeout in seconds.",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=ALLOWED_OUTPUT_FORMATS,
        default=DEFAULT_OUTPUT_FORMAT,
        help="Output data format (table, json, csv).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Optional file path to save output (e.g. books.json).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main CLI entrypoint.

    Args:
        argv: Optional list of command-line arguments.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.max_pages < 1:
        print("Error: --max-pages must be at least 1.", file=sys.stderr)
        return 1

    if args.delay < 0:
        print("Error: --delay cannot be negative.", file=sys.stderr)
        return 1

    if args.timeout <= 0:
        print("Error: --timeout must be greater than 0.", file=sys.stderr)
        return 1

    config = ScraperConfig(
        target_url=args.url,
        max_pages=args.max_pages,
        delay=args.delay,
        timeout=args.timeout,
        output_format=args.format,
        output_file=args.output,
    )

    try:
        scraper = WebScraper(config=config)
        books = scraper.scrape()
        formatted_result = format_output(books, config.output_format)

        if config.output_file:
            output_path = Path(config.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(formatted_result, encoding="utf-8")
            print(f"Successfully scraped {len(books)} books. Saved output to '{config.output_file}'.")
        else:
            print(formatted_result)

        return 0

    except ScraperError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Unexpected Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
