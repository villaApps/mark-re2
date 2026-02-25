"""Simon Estates scraper for simonestates.com."""

import asyncio
from decimal import Decimal
from typing import List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from ..models.property import Property, PropertyType, ListingType
from .base import BaseScraper, ScraperError, ParseError


class SimonEstatesScraper(BaseScraper):
    """Scraper for Simon Estates Malta."""
    
    def __init__(self):
        """Initialize Simon Estates scraper."""
        super().__init__(
            base_url="https://www.simonestates.com",
            name="simon_estates",
            delay_seconds=2.0
        )
    
    async def scrape_listings(self, max_pages: int = 5) -> List[Property]:
        """Scrape property listings from Simon Estates.
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of Property objects
        """
        properties = []
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for page in range(1, max_pages + 1):
                try:
                    page_properties = await self._scrape_page(client, page)
                    if not page_properties:
                        break
                    properties.extend(page_properties)
                    await asyncio.sleep(self.delay_seconds)
                except Exception as e:
                    raise ScraperError(f"Failed to scrape page {page}: {e}")
        
        return properties
    
    async def _scrape_page(self, client: httpx.AsyncClient, page: int) -> List[Property]:
        """Scrape a single page of listings.
        
        Args:
            client: HTTP client
            page: Page number
            
        Returns:
            List of Property objects from this page
        """
        url = f"{self.base_url}/properties/page/{page}/"
        
        try:
            response = await client.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                }
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise ScraperError(f"HTTP error fetching {url}: {e}")
        
        soup = BeautifulSoup(response.text, "lxml")
        property_cards = soup.find_all("div", class_="property-card")
        
        if not property_cards:
            # Try alternative selectors
            property_cards = soup.find_all("article", class_=lambda x: x and "property" in x)
        
        properties = []
        for card in property_cards:
            try:
                prop = self._parse_property_card(card)
                if prop:
                    properties.append(prop)
            except Exception as e:
                # Log but continue with other properties
                print(f"Failed to parse property card: {e}")
                continue
        
        return properties
    
    def _parse_property_card(self, card: BeautifulSoup) -> Optional[Property]:
        """Parse a property card into a Property object.
        
        Args:
            card: BeautifulSoup element for property card
            
        Returns:
            Property object or None if parsing fails
        """
        try:
            # Extract URL
            link_elem = card.find("a", href=True)
            if not link_elem:
                return None
            
            relative_url = link_elem.get("href", "")
            url = urljoin(self.base_url, relative_url)
            
            # Extract title
            title_elem = card.find("h2") or card.find("h3") or card.find("h4")
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            # Extract price
            price_elem = card.find(class_=lambda x: x and "price" in str(x).lower())
            price = self._parse_price(price_elem.get_text(strip=True) if price_elem else "")
            
            if not price:
                return None
            
            # Extract location
            location_elem = card.find(class_=lambda x: x and "location" in str(x).lower())
            location = location_elem.get_text(strip=True) if location_elem else "Malta"
            
            # Extract features
            bedrooms = self._extract_number(card, ["bed", "bedroom"])
            bathrooms = self._extract_number(card, ["bath", "bathroom"])
            sqm = self._extract_number(card, ["sqm", "m2", "square"])
            
            # Extract images
            images = []
            img_elems = card.find_all("img")
            for img in img_elems:
                src = img.get("src") or img.get("data-src")
                if src:
                    images.append(urljoin(self.base_url, src))
            
            # Determine property type from title
            property_type = self._detect_property_type(title)
            
            return Property(
                id=self._generate_id(url),
                source=self.name,
                url=url,
                title=title,
                location=location,
                property_type=property_type,
                listing_type=ListingType.SALE,
                price=price,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                square_meters=sqm,
                images=images[:5],  # Limit to 5 images
            )
        
        except Exception as e:
            raise ParseError(f"Failed to parse property card: {e}")
    
    def _parse_price(self, text: str) -> Optional[Decimal]:
        """Parse price from text.
        
        Args:
            text: Price text like "€450,000" or "450000"
            
        Returns:
            Decimal price or None
        """
        import re
        
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[€$,\s]', '', text)
        
        # Extract numbers
        numbers = re.findall(r'\d+', cleaned)
        if numbers:
            try:
                return Decimal(''.join(numbers))
            except:
                pass
        
        return None
    
    def _extract_number(self, card: BeautifulSoup, keywords: List[str]) -> Optional[int]:
        """Extract a number from card based on keywords.
        
        Args:
            card: Property card element
            keywords: List of keywords to look for
            
        Returns:
            Extracted number or None
        """
        import re
        
        text = card.get_text()
        
        for keyword in keywords:
            # Look for patterns like "3 bed", "3 bedrooms", "3-bed"
            pattern = rf'(\d+)\s*{keyword}'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        return None
    
    def _detect_property_type(self, title: str) -> PropertyType:
        """Detect property type from title.
        
        Args:
            title: Property title
            
        Returns:
            PropertyType enum
        """
        title_lower = title.lower()
        
        if "penthouse" in title_lower:
            return PropertyType.PENTHOUSE
        elif "maisonette" in title_lower:
            return PropertyType.MAISONETTE
        elif "villa" in title_lower:
            return PropertyType.VILLA
        elif "townhouse" in title_lower:
            return PropertyType.TOWNHOUSE
        elif "studio" in title_lower:
            return PropertyType.STUDIO
        elif "duplex" in title_lower:
            return PropertyType.DUPLEX
        elif "apartment" in title_lower:
            return PropertyType.APARTMENT
        elif "house" in title_lower:
            return PropertyType.HOUSE
        else:
            return PropertyType.OTHER
    
    async def scrape_property(self, url: str) -> Property:
        """Scrape a single property detail page.
        
        Args:
            url: Property detail URL
            
        Returns:
            Property object
        """
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"
                        )
                    }
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                raise ScraperError(f"HTTP error fetching {url}: {e}")
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # Parse detail page (simplified for now)
            title_elem = soup.find("h1")
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            price_elem = soup.find(class_=lambda x: x and "price" in str(x).lower())
            price = self._parse_price(price_elem.get_text(strip=True) if price_elem else "")
            
            if not price:
                raise ParseError(f"Could not parse price from {url}")
            
            return Property(
                id=self._generate_id(url),
                source=self.name,
                url=url,
                title=title,
                location="Malta",
                property_type=self._detect_property_type(title),
                listing_type=ListingType.SALE,
                price=price,
            )
