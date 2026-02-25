"""HTML parsing utilities for property extraction."""

import json
import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from src.utils.validators import (
    clean_text,
    detect_property_type,
    extract_year_built,
    normalize_location,
    parse_area,
    parse_bathrooms,
    parse_bedrooms,
    parse_price,
)


class ParseError(Exception):
    """Exception raised for parsing errors."""

    pass


class Extractor:
    """Utility class for extracting data from HTML elements."""

    @staticmethod
    def text(element: Optional[Tag], default: str = "") -> str:
        """Extract text from element.

        Args:
            element: BeautifulSoup Tag element
            default: Default value if element is None

        Returns:
            Extracted and cleaned text
        """
        if element is None:
            return default
        return clean_text(element.get_text())

    @staticmethod
    def attr(element: Optional[Tag], attr: str, default: str = "") -> str:
        """Extract attribute from element.

        Args:
            element: BeautifulSoup Tag element
            attr: Attribute name
            default: Default value if element or attribute is missing

        Returns:
            Attribute value
        """
        if element is None:
            return default
        return element.get(attr, default)

    @staticmethod
    def int_text(element: Optional[Tag], default: Optional[int] = None) -> Optional[int]:
        """Extract integer from element text.

        Args:
            element: BeautifulSoup Tag element
            default: Default value if extraction fails

        Returns:
            Extracted integer or default
        """
        text = Extractor.text(element)
        if not text:
            return default

        # Extract first number
        match = re.search(r'\d+', text.replace(',', ''))
        if match:
            try:
                return int(match.group())
            except ValueError:
                pass
        return default

    @staticmethod
    def float_text(element: Optional[Tag], default: Optional[float] = None) -> Optional[float]:
        """Extract float from element text.

        Args:
            element: BeautifulSoup Tag element
            default: Default value if extraction fails

        Returns:
            Extracted float or default
        """
        text = Extractor.text(element)
        if not text:
            return default

        # Extract first decimal number
        match = re.search(r'[\d,]+\.?\d*', text.replace(',', ''))
        if match:
            try:
                return float(match.group())
            except ValueError:
                pass
        return default


class HTMLParser:
    """Parser for HTML content with property extraction capabilities."""

    def __init__(self, html: str, base_url: str = ""):
        """Initialize parser with HTML content.

        Args:
            html: Raw HTML string
            base_url: Base URL for resolving relative links
        """
        self.html = html
        self.base_url = base_url
        self.soup = BeautifulSoup(html, 'lxml')
        self.extractor = Extractor()

    def find(
        self,
        selector: str,
        attrs: Optional[Dict[str, str]] = None,
    ) -> Optional[Tag]:
        """Find single element by selector.

        Args:
            selector: CSS selector or tag name
            attrs: Additional attributes to match

        Returns:
            Found element or None
        """
        try:
            if attrs:
                return self.soup.find(selector, attrs=attrs)
            return self.soup.select_one(selector)
        except Exception:
            return None

    def find_all(
        self,
        selector: str,
        attrs: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
    ) -> List[Tag]:
        """Find all elements matching selector.

        Args:
            selector: CSS selector or tag name
            attrs: Additional attributes to match
            limit: Maximum number of results

        Returns:
            List of matching elements
        """
        try:
            if attrs:
                return self.soup.find_all(selector, attrs=attrs, limit=limit)
            return self.soup.select(selector, limit=limit)
        except Exception:
            return []

    def get_text(self, selector: str, default: str = "") -> str:
        """Get text from element matching selector.

        Args:
            selector: CSS selector
            default: Default value if not found

        Returns:
            Extracted text
        """
        element = self.find(selector)
        return self.extractor.text(element, default)

    def get_attr(self, selector: str, attr: str, default: str = "") -> str:
        """Get attribute from element matching selector.

        Args:
            selector: CSS selector
            attr: Attribute name
            default: Default value if not found

        Returns:
            Attribute value
        """
        element = self.find(selector)
        return self.extractor.attr(element, attr, default)

    def get_absolute_url(self, selector: str, attr: str = "href") -> str:
        """Get absolute URL from element.

        Args:
            selector: CSS selector
            attr: Attribute containing URL

        Returns:
            Absolute URL
        """
        relative_url = self.get_attr(selector, attr)
        if not relative_url:
            return ""
        return urljoin(self.base_url, relative_url)

    def get_image_urls(self, selector: str = "img") -> List[str]:
        """Extract image URLs from page.

        Args:
            selector: CSS selector for images

        Returns:
            List of absolute image URLs
        """
        images = self.find_all(selector)
        urls = []
        for img in images:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                absolute = urljoin(self.base_url, src)
                urls.append(absolute)
        return urls

    def extract_json_ld(self) -> List[Dict[str, Any]]:
        """Extract JSON-LD structured data from page.

        Returns:
            List of JSON-LD objects
        """
        scripts = self.find_all('script', {'type': 'application/ld+json'})
        data = []
        for script in scripts:
            try:
                if script.string:
                    json_data = json.loads(script.string)
                    data.append(json_data)
            except json.JSONDecodeError:
                continue
        return data

    def extract_microdata(self, itemtype: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract microdata from page.

        Args:
            itemtype: Filter by specific itemtype (e.g., 'http://schema.org/Product')

        Returns:
            List of microdata objects
        """
        if itemtype:
            elements = self.find_all(attrs={'itemtype': itemtype})
        else:
            elements = self.find_all(attrs={'itemscope': True})

        data = []
        for element in elements:
            item_data = {'@type': element.get('itemtype', '').split('/')[-1]}
            props = element.find_all(attrs={'itemprop': True})
            for prop in props:
                prop_name = prop.get('itemprop')
                if prop_name:
                    item_data[prop_name] = clean_text(prop.get_text())
            data.append(item_data)
        return data

    def extract_open_graph(self) -> Dict[str, str]:
        """Extract Open Graph metadata from page.

        Returns:
            Dictionary of Open Graph properties
        """
        og_tags = self.find_all('meta', attrs={'property': re.compile(r'^og:')})
        data = {}
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if prop and content:
                data[prop] = content
        return data

    def extract_meta_tags(self) -> Dict[str, str]:
        """Extract all meta tags from page.

        Returns:
            Dictionary of meta tag name/content pairs
        """
        meta_tags = self.find_all('meta')
        data = {}
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                data[name] = content
        return data

    def extract_price_info(self, selectors: Optional[List[str]] = None) -> tuple:
        """Extract price information from page.

        Args:
            selectors: List of CSS selectors to try for price

        Returns:
            Tuple of (price, currency) or (None, None)
        """
        default_selectors = [
            '.price',
            '.property-price',
            '[class*="price"]',
            '.amount',
            '.listing-price',
        ]

        selectors = selectors or default_selectors

        for selector in selectors:
            element = self.find(selector)
            if element:
                text = self.extractor.text(element)
                price, currency = parse_price(text)
                if price is not None:
                    return price, currency

        return None, None

    def extract_property_details(self) -> Dict[str, Any]:
        """Extract common property details from page.

        Returns:
            Dictionary of extracted details
        """
        details = {}

        # Get all text content for analysis
        full_text = self.soup.get_text()

        # Extract bedrooms
        details['bedrooms'] = parse_bedrooms(full_text)

        # Extract bathrooms
        details['bathrooms'] = parse_bathrooms(full_text)

        # Extract area
        area_selectors = [
            '.area',
            '.sqm',
            '.square-meters',
            '[class*="area"]',
            '[class*="sqm"]',
        ]
        for selector in area_selectors:
            element = self.find(selector)
            if element:
                area = parse_area(self.extractor.text(element))
                if area:
                    details['square_meters'] = area
                    break

        # Extract property type
        details['property_type'] = detect_property_type(full_text)

        # Extract year built
        details['year_built'] = extract_year_built(full_text)

        # Extract location
        location_selectors = [
            '.location',
            '.address',
            '.locality',
            '[class*="location"]',
        ]
        for selector in location_selectors:
            element = self.find(selector)
            if element:
                location = normalize_location(self.extractor.text(element))
                if location:
                    details['location'] = location
                    break

        return details

    def extract_property_listings(
        self,
        container_selector: str,
        title_selector: str = '.title',
        price_selector: str = '.price',
        link_selector: str = 'a',
    ) -> List[Dict[str, Any]]:
        """Extract property listings from a list page.

        Args:
            container_selector: CSS selector for listing containers
            title_selector: CSS selector for title within container
            price_selector: CSS selector for price within container
            link_selector: CSS selector for link within container

        Returns:
            List of property listing dictionaries
        """
        listings = []
        containers = self.find_all(container_selector)

        for container in containers:
            listing = {}

            # Extract title
            title_elem = container.select_one(title_selector)
            if title_elem:
                listing['title'] = self.extractor.text(title_elem)

            # Extract price
            price_elem = container.select_one(price_selector)
            if price_elem:
                price_text = self.extractor.text(price_elem)
                price, currency = parse_price(price_text)
                if price:
                    listing['price'] = price
                    listing['price_currency'] = currency

            # Extract link
            link_elem = container.select_one(link_selector)
            if link_elem:
                href = link_elem.get('href', '')
                if href:
                    listing['url'] = urljoin(self.base_url, href)

            # Extract details from container text
            container_text = container.get_text()
            bedrooms = parse_bedrooms(container_text)
            if bedrooms:
                listing['bedrooms'] = bedrooms

            bathrooms = parse_bathrooms(container_text)
            if bathrooms:
                listing['bathrooms'] = bathrooms

            prop_type = detect_property_type(container_text)
            if prop_type:
                listing['property_type'] = prop_type

            if listing:
                listings.append(listing)

        return listings

    def get_pagination_links(self, selector: str = '.pagination a') -> List[str]:
        """Extract pagination links from page.

        Args:
            selector: CSS selector for pagination links

        Returns:
            List of absolute page URLs
        """
        links = self.find_all(selector)
        urls = []
        for link in links:
            href = link.get('href')
            if href:
                absolute = urljoin(self.base_url, href)
                # Avoid duplicates
                if absolute not in urls:
                    urls.append(absolute)
        return urls

    def has_captcha(self) -> bool:
        """Check if page contains CAPTCHA challenge.

        Returns:
            True if CAPTCHA detected
        """
        captcha_indicators = [
            'captcha',
            'recaptcha',
            'g-recaptcha',
            'i\'m not a robot',
            'security check',
            'verify you are human',
        ]

        page_text = self.soup.get_text().lower()
        page_html = str(self.soup).lower()

        for indicator in captcha_indicators:
            if indicator in page_text or indicator in page_html:
                return True

        return False

    def is_blocked(self) -> bool:
        """Check if access is blocked.

        Returns:
            True if blocked
        """
        block_indicators = [
            'access denied',
            '403 forbidden',
            'blocked',
            'rate limit exceeded',
            'too many requests',
            'ip blocked',
        ]

        page_text = self.soup.get_text().lower()

        for indicator in block_indicators:
            if indicator in page_text:
                return True

        # Check for common block status codes in title
        title = self.soup.find('title')
        if title:
            title_text = title.get_text().lower()
            if any(code in title_text for code in ['403', '429', '503']):
                return True

        return False
