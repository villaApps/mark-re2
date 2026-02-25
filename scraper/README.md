# Malta Property Scraper

Property scraper for Malta real estate websites.

## Supported Websites

- Simon Estates (simonestates.com)

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```python
import asyncio
from src.scrapers.simon_estates import SimonEstatesScraper

async def main():
    scraper = SimonEstatesScraper()
    properties = await scraper.scrape_listings(max_pages=3)
    
    for prop in properties:
        print(f"{prop.title}: €{prop.price}")

asyncio.run(main())
```

## Testing

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_simon_scraper.py -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

## Project Structure

```
scraper/
├── src/
│   ├── models/
│   │   └── property.py       # Pydantic property models
│   ├── scrapers/
│   │   ├── base.py           # Abstract base scraper
│   │   └── simon_estates.py  # Simon Estates scraper
│   └── utils/
│       └── rate_limiter.py   # Async rate limiter
└── tests/
    └── unit/
        ├── test_models.py
        ├── test_simon_scraper.py
        └── test_rate_limiter.py
```

## Development

### Adding a New Scraper

1. Create a new file in `src/scrapers/`
2. Inherit from `BaseScraper`
3. Implement `scrape_listings()` and `scrape_property()`
4. Add tests in `tests/unit/`

### Code Quality

```bash
# Format code
black src tests

# Lint
ruff src tests

# Type check
mypy src
```

## License

MIT
