"""Property scrapers for Malta real estate websites."""

from .base import BaseScraper, ScraperError
from .simon_estates import SimonEstatesScraper

__all__ = ["BaseScraper", "ScraperError", "SimonEstatesScraper"]
