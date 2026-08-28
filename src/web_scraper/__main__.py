"""Package main entrypoint enabling 'python -m web_scraper' execution."""

import sys
from web_scraper.cli import main

if __name__ == "__main__":
    sys.exit(main())
