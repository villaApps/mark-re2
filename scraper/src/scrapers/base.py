"""Base scraper class with common functionality."""

from abc import ABC, abstractmethod
from typing import List

from ..models.property import Property


class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class RateLimitError(ScraperError):
    """Raised when rate limit is exceeded."""
    pass


class ParseError(ScraperError):
    """Raised when parsing fails."""
    pass


class BaseScraper(ABC):
    """Abstract base class for property scrapers."""
    
    def __init__(self, base_url: str, name: str, delay_seconds: float = 2.0):
        """Initialize scraper.
        
        Args:
            base_url: Base URL of the website
            name: Name of the scraper/source
            delay_seconds: Delay between requests
        """
        self.base_url = base_url.rstrip("/")
        self.name = name
        self.delay_seconds = delay_seconds
    
    @abstractmethod
    async def scrape_listings(self, max_pages: int = 5) -> List[Property]:
        """Scrape property listings.
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of Property objects
            
        Raises:
            ScraperError: If scraping fails
        """
        pass
    
    @abstractmethod
    async def scrape_property(self, url: str) -> Property:
        """Scrape a single property detail page.
        
        Args:
            url: Property detail URL
            
        Returns:
            Property object
            
        Raises:
            ScraperError: If scraping fails
        """
        pass
    
    def _generate_id(self, url: str) -> str:
        """Generate unique ID from URL.
        
        Args:
            url: Property URL
            
        Returns:
            Unique ID string
        """
        import hashlib
        return hashlib.md5(f"{self.name}:{url}".encode()).hexdigest()[:12]
