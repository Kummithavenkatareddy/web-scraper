# Web Scraper Examples

This directory provides usage examples and output demonstrations for `web-scraper`.

---

## Example 1: Basic Table Rendering

Execute basic single-page scrape against [Books to Scrape](https://books.toscrape.com/):

```bash
python -m web_scraper https://books.toscrape.com/ --max-pages 1
```

### Sample Terminal Output

```text
# | Title                               | Price  | Availability | Rating | URL
--+-------------------------------------+--------+--------------+--------+-------------------------------------------------------------------------
1 | A Light in the Attic                | £51.77 | In stock     | Three  | https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
2 | Tipping the Velvet                  | £53.74 | In stock     | One    | https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html
3 | Soumission                          | £50.10 | In stock     | One    | https://books.toscrape.com/catalogue/soumission_998/index.html
```

---

## Example 2: Multi-Page Pagination with Delay

Crawl 2 catalog pages with a 1.0-second delay between requests:

```bash
python -m web_scraper https://books.toscrape.com/ --max-pages 2 --delay 1.0
```

---

## Example 3: JSON File Export

Scrape books and export structured JSON data to `scraped_books.json`:

```bash
python -m web_scraper https://books.toscrape.com/ --format json --output scraped_books.json
```

### Sample Output File (`scraped_books.json`)

```json
[
  {
    "title": "A Light in the Attic",
    "price": "£51.77",
    "availability": "In stock",
    "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "rating": "Three",
    "category": null
  },
  {
    "title": "Tipping the Velvet",
    "price": "£53.74",
    "availability": "In stock",
    "url": "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
    "rating": "One",
    "category": null
  }
]
```

---

## Example 4: CSV File Export

Scrape books and export CSV format to `scraped_books.csv`:

```bash
python -m web_scraper https://books.toscrape.com/ --format csv --output scraped_books.csv
```

### Sample CSV Output

```csv
title,price,availability,rating,category,url
A Light in the Attic,£51.77,In stock,Three,,https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
Tipping the Velvet,£53.74,In stock,One,,https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html
```
