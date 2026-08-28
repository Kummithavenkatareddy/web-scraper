# Web Scraper

A professional, modular, educational Python web scraping repository built to extract structured data from web pages cleanly and ethically.

Targeted primarily at scraping-friendly sandbox environments like [Books to Scrape](https://books.toscrape.com/), this project demonstrates modern Python software engineering principles: clean layered architecture, robust error handling, `robots.txt` policy adherence, rate limiting, multi-format exports, CLI capabilities, and fully isolated offline unit tests.

---

## Key Features

- **HTTP Networking**: Robust GET requests powered by `requests` with explicit timeouts and custom User-Agent headers.
- **HTML Parsing**: Robust extraction using `beautifulsoup4` and semantic CSS selectors (`article.product_pod`, `.price_color`, `.availability`, `.star-rating`).
- **Structured Data Models**: Encapsulates scraped books into immutable Python `@dataclass` objects.
- **Ethical Crawling**: Automated `robots.txt` policy verification via `urllib.robotparser`.
- **Pagination & Rate Limiting**: Multi-page traversal with configurable `--max-pages` and request `--delay` throttles.
- **Flexible Output Formats**: Supports interactive terminal `table`, `json`, and `csv` rendering.
- **File Export**: Direct export capability to files (`--output books.json`).
- **Clean CLI**: User-friendly command-line interface powered by `argparse` with graceful error suppression.
- **Comprehensive Unit Testing**: 100% offline test suite using HTML fixtures and mocks.

---

## Extracted Fields

For every target book product, the scraper extracts:

- **Title**: Book title string.
- **Price**: Currency-formatted price (e.g. `£51.77`).
- **Availability**: Stock availability status (e.g. `In stock`).
- **Product URL**: Fully resolved absolute URL (e.g. `https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html`).
- **Rating**: Numeric star rating from 1 to 5 if available (e.g. `3`, `5`, or `None` if missing).

---

## Requirements

- Python **3.10** or higher
- `requests >= 2.28.0`
- `beautifulsoup4 >= 4.11.0`

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/web-scraper.git
   cd web-scraper
   ```

2. **Create and activate a virtual environment**:

   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```

   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install the package in editable mode**:
   ```bash
   python -m pip install -e .
   ```

---

## Usage

You can run the scraper directly via the installed CLI executable (`web-scraper`) or via Python module execution (`python -m web_scraper`).

### Basic Scraping (Default Target)

Scrape the default target ([books.toscrape.com](https://books.toscrape.com/)) with default single-page table output:

```bash
python -m web_scraper
```

### Multi-page Pagination with Rate Delay

Crawl up to 3 pages with a 1.5-second delay between requests:

```bash
python -m web_scraper https://books.toscrape.com/ --max-pages 3 --delay 1.5
```

### Exporting to JSON or CSV

Display results as formatted JSON in the terminal:

```bash
python -m web_scraper https://books.toscrape.com/ --format json
```

Save results directly to a file:

```bash
python -m web_scraper https://books.toscrape.com/ --format json --output books.json
```

Save results as a CSV file:

```bash
python -m web_scraper https://books.toscrape.com/ --format csv --output books.csv
```

### CLI Command Options

```text
usage: web-scraper [-h] [--max-pages MAX_PAGES] [--delay DELAY] [--timeout TIMEOUT]
                   [--format {table,json,csv}] [--output OUTPUT]
                   [url]

Extract structured book catalog data from scraping-friendly websites.

positional arguments:
  url                   Target web page URL to scrape. (default: https://books.toscrape.com/)

options:
  -h, --help            show this help message and exit
  --max-pages MAX_PAGES
                        Maximum number of pagination pages to crawl. (default: 1)
  --delay DELAY         Delay in seconds between consecutive HTTP requests. (default: 1.0)
  --timeout TIMEOUT     HTTP request timeout in seconds. (default: 10.0)
  --format {table,json,csv}, -f {table,json,csv}
                        Output data format (table, json, csv). (default: table)
  --output OUTPUT, -o OUTPUT
                        Optional file path to save output (e.g. books.json). (default: None)
```

---

## Sample Output

### Terminal Table Output

```text
#  | Title                                    | Price  | Availability | Rating | URL
---+------------------------------------------+--------+--------------+--------+-----------------------------------------
1  | A Light in the Attic                     | £51.77 | In stock     | 3/5    | https://books.toscrape.com/catalogue/...
2  | Tipping the Velvet                       | £53.74 | In stock     | 1/5    | https://books.toscrape.com/catalogue/...
3  | Soumission                               | £50.10 | In stock     | 1/5    | https://books.toscrape.com/catalogue/...
```

### JSON Output

```json
[
  {
    "title": "A Light in the Attic",
    "price": "£51.77",
    "availability": "In stock",
    "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "rating": 3
  }
]
```

---

## Architecture Overview

The application follows a clean layered separation of concerns:

```text
┌──────────────┐
│     CLI      │  (cli.py & main.py)
└──────┬───────┘
       │
       v
┌──────────────┐
│   Scraper    │  (scraper.py - Orchestration, Pagination & Rate Limiting)
└──────┬───────┘
       │
       ├───────────────────────┐
       v                       v
┌─────────────┐         ┌─────────────┐
│ HTTP Client │         │   Parser    │  (parser.py - BeautifulSoup HTML parsing)
└─────────────┘         └──────┬──────┘
                               │
                               v
                        ┌───────────┐
                        │  Models   │  (models.py - Book dataclass)
                        └───────────┘
```

For detailed architectural decisions, data flow documentation, and error taxonomy, see [ARCHITECTURE.md](file:///c:/Users/kvred/projects/COGNIFYZ/LEVEL%203/TASK%201/web-scraper/ARCHITECTURE.md).

---

## Running Automated Tests

The unit test suite is designed to run **100% offline** without requesting external network resources.

Run all tests using Python's standard `unittest` runner:

```bash
python -m unittest discover -s tests -v
```

---

## Ethical Scraping & Responsible Usage

This project adheres strictly to ethical web scraping best practices:

1. **Target Selection**: Designed for educational practice against authorized test sandboxes ([books.toscrape.com](https://books.toscrape.com/)).
2. **Robots.txt Adherence**: Automatically checks target `robots.txt` files prior to crawling.
3. **Throttling & Rate Limiting**: Defaults to a 1.0-second pause between pagination requests to avoid server strain.
4. **Explicit Timeouts**: Every HTTP request enforces a mandatory timeout to prevent hanging connections.
5. **Transparent User-Agent**: Uses an explicit, honest User-Agent header string (`Mozilla/5.0 (compatible; WebScraperEducational/1.0)`).
6. **No Anti-Bot Evasion**: Does not attempt to bypass CAPTCHAs, bypass paywalls, rotate IP addresses, or evade anti-scraping protections.

---

## License

Distributed under the [MIT License](file:///c:/Users/kvred/projects/COGNIFYZ/LEVEL%203/TASK%201/web-scraper/LICENSE).
