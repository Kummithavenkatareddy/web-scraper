# Development Guide (`DEVELOPMENT.md`)

This guide explains how to set up the development environment, run test suites, perform manual verification, extend parsers, and follow the project's recommended Git workflow.

---

## 1. Environment Setup

### Requirements

- **Python**: Version 3.10, 3.11, or 3.12.
- **Package Manager**: `pip` (standard with Python).

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/web-scraper.git
   cd web-scraper
   ```

2. **Create a virtual environment**:

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

## 2. Running Unit Tests

The test suite is located in `tests/` and runs entirely **offline** without internet access.

Run the unit tests via Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests -v
```

### Individual Test Modules

To run tests for a specific component:

```bash
# Test HTML Parser
python -m unittest tests/test_parser.py -v

# Test HTTP Client
python -m unittest tests/test_http_client.py -v

# Test Scraper Orchestrator
python -m unittest tests/test_scraper.py -v

# Test CLI & Formatters
python -m unittest tests/test_cli.py -v
```

---

## 3. Manual Verification Procedures

Verify that the CLI works as expected against live scraping targets:

### Step 1: Help Command
```bash
python -m web_scraper --help
```

### Step 2: Single-Page Scraping (Default Table Output)
```bash
python -m web_scraper https://books.toscrape.com/ --max-pages 1
```

### Step 3: Multi-Page Pagination with Delay
```bash
python -m web_scraper https://books.toscrape.com/ --max-pages 2 --delay 1.0
```

### Step 4: JSON Export
```bash
python -m web_scraper https://books.toscrape.com/ --format json --output books.json
```

Verify output file content:
- **Windows PowerShell**: `Get-Content books.json`
- **Linux / macOS**: `cat books.json`

### Step 5: Clean Up Test Artifacts
Remove any temporary `.json` or `.csv` files created during manual testing before committing:
```bash
rm books.json
```

---

## 4. Extending Parsers / CSS Selectors

If target HTML structure changes or a new scraping target is added:

1. **Inspect Target HTML**: Open target web pages in developer tools to identify stable container and field selectors.
2. **Update `src/web_scraper/parser.py`**:
   - Update CSS selector strings inside `parse_books()`.
   - Update field normalization rules.
3. **Update Test Fixture**: Update `tests/fixtures/books_page.html` with representative target HTML.
4. **Update Unit Tests**: Update expectations in `tests/test_parser.py`.

---

## 5. Debugging Failed Requests

If live network requests fail during development:

1. **Timeout Issues**: Increase timeout parameter (`--timeout 20`).
2. **Robots.txt Denial**: Verify if the path is prohibited in the site's `robots.txt` file.
3. **User-Agent Blocking**: Ensure your custom User-Agent string is clear and descriptive.

---

## 6. Recommended Git Workflow

Follow conventional commit guidelines:

- `feat:` for new features (e.g. `feat: build configurable web scraper`)
- `fix:` for bug fixes
- `docs:` for documentation updates
- `test:` for test additions or updates

### Recommended Initial Commit
```bash
git add .
git commit -m "feat: build configurable web scraper"
```
