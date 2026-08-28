# Architecture Documentation (`ARCHITECTURE.md`)

This document details the architectural design, component responsibilities, data flow, error handling taxonomy, and CSS selector design for `web-scraper`.

---

## 1. Architectural Philosophy

The `web-scraper` application is structured around a **Layered Architecture**. Each component has a single, well-defined responsibility with strict boundary isolation:

1. **Isolation of Parsing from Networking**: The HTML parser (`parser.py`) is completely decoupled from HTTP communication (`http_client.py`). It accepts HTML text input and returns structured models. This decoupling enables fast, 100% offline unit testing without mocking network interfaces in parsing tests.
2. **Centralized Configuration**: All operational parameters (timeouts, User-Agent strings, default URLs, delays) are centralized in `config.py` via `ScraperConfig`.
3. **Domain Exception Mapping**: Raw library exceptions (e.g. `requests.Timeout`, `requests.ConnectionError`) are caught at component boundaries and mapped into domain-specific exceptions (`FetchError`, `RobotsDeniedError`, `ParseError`).
4. **Single-threaded Sequential Execution**: To maintain predictability and ethical compliance, page requests are executed sequentially with explicit rate-limiting pauses between iterations.

---

## 2. Component Layout & Responsibilities

```text
┌─────────────────────────────────────────────────────────────┐
│                       CLI Layer                             │
│                  (cli.py & main.py)                         │
│  - Parses CLI arguments (url, max-pages, delay, format)    │
│  - Formats output (table, json, csv)                        │
│  - Suppresses tracebacks for standard user errors           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               v
┌─────────────────────────────────────────────────────────────┐
│                    Orchestration Layer                      │
│                        (scraper.py)                         │
│  - Checks robots.txt policy compliance                       │
│  - Coordinates page fetch & pagination loop                 │
│  - Enforces max_pages limit and rate delay (time.sleep)     │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
                v                             v
┌──────────────────────────────┐  ┌───────────────────────────┐
│          HTTP Layer          │  │       Parser Layer        │
│       (http_client.py)       │  │        (parser.py)        │
│  - Enforces HTTP timeouts    │  │  - Parses HTML string     │
│  - Sets custom User-Agent    │  │  - Applies CSS selectors  │
│  - Wraps network errors      │  │  - Resolves absolute URLs │
└──────────────────────────────┘  └─────────────┬─────────────┘
                                                │
                                                v
                                  ┌───────────────────────────┐
                                  │        Model Layer        │
                                  │        (models.py)        │
                                  │  - Immutable Book class   │
                                  └───────────────────────────┘
```

### Module Breakdown

| Module | Responsibility | Key Symbols |
|---|---|---|
| [`models.py`](file:///c:/Users/kvred/projects/COGNIFYZ/LEVEL%203/TASK%201/web-scraper/src/web_scraper/models.py) | Defines application domain entities | `@dataclass(frozen=True) class Book` |
| [`config.py`](file:///c:/Users/kvred/projects/COGNIFYZ/LEVEL%203/TASK%201/web-scraper/src/web_scraper/config.py) | Holds scraper default options & configurations | `ScraperConfig` |
| [`exceptions.py`](file:///c:/Users/kvred/projects/COGNIFYZ/LEVEL%203/TASK%201/web-scraper/src/web_scraper/exceptions.py) | Application exception hierarchy | `ScraperError`, `FetchError`, `RobotsDeniedError`, `ParseError` |
| [`http_client.py`](file:///c:/Users/kvred/projects/COGNIFYZ/LEVEL%203/TASK%201/web-scraper/src/web_scraper/http_client.py) | Handles network GET requests safely | `HTTPClient` |
| [`parser.py`](file:///c:/Users/kvred/projects/COGNIFYZ/LEVEL%203/TASK%201/web-scraper/src/web_scraper/parser.py) | Pure HTML text parsing & selector extraction | `parse_books()`, `parse_next_page_url()` |
| [`scraper.py`](file:///c:/Users/kvred/projects/COGNIFYZ/LEVEL%203/TASK%201/web-scraper/src/web_scraper/scraper.py) | Workflow manager & crawl controller | `WebScraper` |
| [`cli.py`](file:///c:/Users/kvred/projects/COGNIFYZ/LEVEL%203/TASK%201/web-scraper/src/web_scraper/cli.py) | User CLI interface & output formatters | `main()`, `format_table()`, `format_json()`, `format_csv()` |
| [`main.py`](file:///c:/Users/kvred/projects/COGNIFYZ/LEVEL%203/TASK%201/web-scraper/src/web_scraper/main.py) | Entrypoint script for `python -m web_scraper` | `main()` |

---

## 3. Data Flow & Pagination Workflow

```text
[CLI User] -> Executes CLI -> [ScraperConfig] initialized
                                    │
                                    v
                         [WebScraper.scrape()]
                                    │
                                    v
                    Check robots.txt compliance
                                    │
                         ┌──────────┴──────────┐
                     Disallowed             Allowed
                         │                     │
                         v                     v
                 Raise RobotsDeniedError    Fetch Page 1 HTML
                                               │
                                               v
                                        parse_books(html)
                                               │
                                               v
                                     Extract Book dataclasses
                                               │
                                               v
                                    parse_next_page_url(html)
                                               │
                                     ┌─────────┴─────────┐
                             Has Next Page           No Next Page
                                     │                     │
                        pages_scraped < max_pages?         │
                            ┌────────┴────────┐            │
                          True              False          │
                            │                 │            │
                            v                 └──────┬─────┘
                     time.sleep(delay)               │
                            │                        │
                      Fetch Next Page                │
                       (Loop back)                   │
                                                     v
                                          Return Aggregated Books
                                                     │
                                                     v
                                         Format Output & Display/Save
```

---

## 4. Robots.txt Compliance Policy

Before fetching catalog HTML, `WebScraper.check_robots_txt(url)` performs an automated policy check:

1. Derives the `robots.txt` URL from the target URL's scheme and netloc (`https://domain/robots.txt`).
2. Fetches the `robots.txt` body using `HTTPClient`.
3. Passes the contents to `urllib.robotparser.RobotFileParser`.
4. Evaluates `can_fetch(user_agent, target_url)`.
5. If denied, halts execution immediately with `RobotsDeniedError`.
6. If `robots.txt` returns HTTP 404 or fails to fetch, standard Web Robots conventions apply (allowing access by default).

---

## 5. CSS Selectors Design Rationale

Brittle, deeply nested selectors (such as `body > div:nth-child(2) > div > div > article`) break easily whenever minor layout edits occur.

`web_scraper` uses semantic, class-based CSS selectors targeted at robust HTML nodes:

- **Book Product Container**: `article.product_pod`
  - Targets each individual book card on catalog pages.
- **Title Anchor**: `h3 a`
  - Extracts the full title string from `title` attribute or inner link text.
- **Product Relative URL**: `h3 a[href]`
  - Converted to absolute URL using `urllib.parse.urljoin(base_url, href)`.
- **Price**: `.price_color`
  - Selects price text (e.g. `£51.77`).
- **Stock Availability**: `.availability`
  - Strips inner icon HTML and normalizes whitespace into clean strings (e.g. `In stock`).
- **Star Rating**: `.star-rating`
  - Maps rating level from CSS class names to numeric integers (e.g. `star-rating Three` -> `3`).
- **Next Page Anchor**: `ul.pager li.next a[href]`
  - Resolves next page URL for pagination crawling.

---

## 6. Error Handling Strategy

All internal errors are categorized into an explicit domain hierarchy:

```text
Exception
  └── ScraperError (Base domain exception)
       ├── FetchError (Network failures, HTTP 4xx/5xx status, connection timeouts)
       ├── ParseError (HTML parsing failures)
       └── RobotsDeniedError (Target page disallowed by robots.txt)
```

The CLI layer catches all `ScraperError` exceptions and displays clean, informative terminal error messages without printing raw Python tracebacks to end users.
