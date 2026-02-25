"""Scraper for Century 21 Malta (century21.com.mt)."""

from decimal import Decimal
from typing import Any, List, Optional

from bs4 import Tag

from src.models.property import Property, PropertyList, PropertyType
from src.parsers.html_parser import HTMLParser
from src.scrapers.base import ListingPageScraper, ScraperError
from src.utils.validators import clean_text, parse_area, parse_bedrooms, parse_bathrooms


class Century21Scraper(ListingPageScraper):
    """Scraper for Century 21 Malta real estate listings."""

    BASE_URL = "https://www.century21.com.mt"

    # Property type mapping for Century 21
    PROPERTY_TYPE_MAP = {
        PropertyType.APARTMENT: "apartment",
        PropertyType.HOUSE: "house",
        PropertyType.PENTHOUSE: "penthouse",
        PropertyType.MAISONETTE: "maisonette",
        PropertyType.VILLA: "villa",
        PropertyType.TOWNHOUSE: "townhouse",
        PropertyType.BUNGALOW: "bungalow",
        PropertyType.DUPLEX: "duplex",
        PropertyType.STUDIO: "studio",
        PropertyType.OFFICE: "office",
        PropertyType.SHOP: "shop",
        PropertyType.WAREHOUSE: "warehouse",
        PropertyType.LAND: "land",
        PropertyType.GARAGE: "garage",
    }

    def __init__(self, **kwargs: Any):
        """Initialize Century 21 scraper."""
        super().__init__(base_url=self.BASE_URL, **kwargs)

    def _build_search_url(
        self,
        location: Optional[str] = None,
        property_type: Optional[PropertyType] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        bedrooms: Optional[int] = None,
        is_rental: bool = False,
        page: int = 1,
    ) -> str:
        """Build search URL for Century 21 Malta."""
        listing_type = "rent" if is_rental else "sale"
        url = f"{self.base_url}/search/{listing_type}/"

        params = []

        if location:
            params.append(f"location={location.replace(' ', '-').lower()}")

        if property_type:
            type_value = self.PROPERTY_TYPE_MAP.get(property_type)
            if type_value:
                params.append(f"type={type_value}")

        if min_price:
            params.append(f"min_price={int(min_price)}")

        if max_price:
            params.append(f"max_price={int(max_price)}")

        if bedrooms:
            params.append(f"bedrooms={bedrooms}")

        if page > 1:
            params.append(f"page={page}")

        if params:
            url += "?" + "&".join(params)

        return url

    def _get_listing_containers(self, parser: HTMLParser) -> List[Tag]:
        """Get property listing containers from Century 21 page."""
        selectors = [
            ".property-card",
            ".property-item",
            ".listing-card",
            ".search-result",
            "[data-property-id]",
            ".property",
        ]

        for selector in selectors:
            containers = parser.find_all(selector)
            if containers:
                return containers

        # Fallback
        all_divs = parser.find_all("div")
        containers = []
        for div in all_divs:
            classes = div.get("class", [])
            if any(c and "property" in str(c).lower() for c in classes):
                containers.append(div)

        return containers

    def _parse_listing_element(self, element: Tag, base_url: str) -> Optional[Property]:
        """Parse a single Century 21 listing element into Property."""
        try:
            parser = HTMLParser(str(element), base_url=base_url)

            # Extract title
            title = ""
            title_selectors = [
                ".property-title",
                ".title",
                "h2",
                "h3",
                ".property-name",
            ]
            for selector in title_selectors:
                title_elem = parser.find(selector)
                if title_elem:
                    title = clean_text(title_elem.get_text())
                    break

            # Extract URL
            url = ""
            link_selectors = [
                "a.property-link",
                ".title a",
                "h2 a",
                "h3 a",
                "a[href*='/property/']",
            ]
            for selector in link_selectors:
                link_elem = parser.find(selector)
                if link_elem:
                    href = link_elem.get("href", "")
                    if href:
                        url = f"{base_url}{href}" if href.startswith("/") else href
                        break

            if not url:
                return None

            # Extract price
            price = Decimal("0")
            price_selectors = [
                ".price",
                ".property-price",
                ".listing-price",
                "[class*='price']",
            ]
            for selector in price_selectors:
                price_elem = parser.find(selector)
                if price_elem:
                    price_text = clean_text(price_elem.get_text())
                    parsed_price, _ = self._parse_price(price_text)
                    if parsed_price:
                        price = parsed_price
                        break

            # Extract location
            location = ""
            location_selectors = [
                ".location",
                ".locality",
                ".address",
                "[class*='location']",
            ]
            for selector in location_selectors:
                loc_elem = parser.find(selector)
                if loc_elem:
                    location = clean_text(loc_elem.get_text())
                    break

            # Extract bedrooms
            bedrooms = None
            bed_selectors = [
                ".bedrooms",
                ".beds",
                "[class*='bed']",
            ]
            for selector in bed_selectors:
                bed_elem = parser.find(selector)
                if bed_elem:
                    bed_text = clean_text(bed_elem.get_text())
                    bedrooms = parse_bedrooms(bed_text)
                    if bedrooms:
                        break

            # Extract bathrooms
            bathrooms = None
            bath_selectors = [
                ".bathrooms",
                ".baths",
                "[class*='bath']",
            ]
            for selector in bath_selectors:
                bath_elem = parser.find(selector)
                if bath_elem:
                    bath_text = clean_text(bath_elem.get_text())
                    bathrooms = parse_bathrooms(bath_text)
                    if bathrooms:
                        break

            # Extract area
            square_meters = None
            area_selectors = [
                ".area",
                ".sqm",
                ".square-meters",
                "[class*='area']",
                "[class*='sqm']",
            ]
            for selector in area_selectors:
                area_elem = parser.find(selector)
                if area_elem:
                    area_text = clean_text(area_elem.get_text())
                    square_meters = parse_area(area_text)
                    if square_meters:
                        break

            # Extract images
            images = parser.get_image_urls()

            # Generate ID
            prop_id = self._generate_id(url)

            # Detect property type
            prop_type = PropertyType.OTHER
            type_text = title.lower()
            for pt in PropertyType:
                if pt.value in type_text:
                    prop_type = pt
                    break

            return Property(
                id=prop_id,
                source=self.source_name,
                url=url,
                title=title,
                description=None,
                location=location or "Malta",
                property_type=prop_type,
                price=price,
                price_currency="EUR",
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                square_meters=square_meters,
                images=images,
            )

        except Exception:
            return None

    def _get_next_page_url(self, parser: HTMLParser) -> Optional[str]:
        """Get URL for next page if exists."""
        next_selectors = [
            ".pagination .next a",
            "a[rel='next']",
            ".next-page a",
            ".pagination a:last-child",
        ]

        for selector in next_selectors:
            next_elem = parser.find(selector)
            if next_elem:
                href = next_elem.get("href")
                if href:
                    return parser.get_absolute_url(selector)

        return None

    async def get_property(self, url: str) -> Optional[Property]:
        """Get detailed property information from Century 21."""
        try:
            html = await self._fetch(url)
            parser = HTMLParser(html, base_url=self.base_url)

            if parser.has_captcha() or parser.is_blocked():
                raise ScraperError("Access blocked or CAPTCHA detected", url)

            # Extract title
            title_selectors = ["h1.property-title", "h1", ".property-header h1"]
            title = ""
            for selector in title_selectors:
                title_elem = parser.find(selector)
                if title_elem:
                    title = clean_text(title_elem.get_text())
                    break

            # Extract price
            price_selectors = [".property-price", ".price", ".main-price"]
            price = Decimal("0")
            for selector in price_selectors:
                price_elem = parser.find(selector)
                if price_elem:
                    price_text = clean_text(price_elem.get_text())
                    parsed_price, _ = self._parse_price(price_text)
                    if parsed_price:
                        price = parsed_price
                        break

            # Extract location
            location_selectors = [".property-location", ".location", ".address"]
            location = ""
            for selector in location_selectors:
                loc_elem = parser.find(selector)
                if loc_elem:
                    location = clean_text(loc_elem.get_text())
                    break

            # Extract description
            desc_selectors = [
                ".property-description",
                ".description",
                ".property-details",
            ]
            description = None
            for selector in desc_selectors:
                desc_elem = parser.find(selector)
                if desc_elem:
                    description = clean_text(desc_elem.get_text())
                    break

            # Extract details
            details = parser.extract_property_details()

            # Extract images
            images = parser.get_image_urls()

            # Extract agent info
            agent_name = None
            agent_selectors = [".agent-name", ".consultant", "[class*='agent']"]
            for selector in agent_selectors:
                agent_elem = parser.find(selector)
                if agent_elem:
                    agent_name = clean_text(agent_elem.get_text())
                    break

            # Generate ID
            prop_id = self._generate_id(url)

            # Detect property type
            prop_type = PropertyType.OTHER
            type_text = (title + " " + (description or "")).lower()
            for pt in PropertyType:
                if pt.value in type_text:
                    prop_type = pt
                    break

            return Property(
                id=prop_id,
                source=self.source_name,
                url=url,
                title=title,
                description=description,
                location=location or "Malta",
                property_type=prop_type,
                price=price,
                price_currency="EUR",
                bedrooms=details.get("bedrooms"),
                bathrooms=details.get("bathrooms"),
                square_meters=details.get("square_meters"),
                images=images,
                agent_name=agent_name,
            )

        except ScraperError:
            raise
        except Exception as e:
            raise ScraperError(f"Error fetching property: {e}", url) from e

    async def get_all_listings(
        self,
        max_pages: int = 10,
        **kwargs: Any,
    ) -> PropertyList:
        """Get all listings across multiple pages."""
        all_properties = []
        page = 1

        while page <= max_pages:
            result = await self.get_listings(page=page, **kwargs)
            if not result.properties:
                break

            all_properties.extend(result.properties)

            # Check for next page
            url = self._build_search_url(page=page, **kwargs)
            html = await self._fetch(url)
            parser = HTMLParser(html, base_url=self.base_url)
            next_url = self._get_next_page_url(parser)

            if not next_url:
                break

            page += 1

        return PropertyList(
            properties=all_properties,
            total_count=len(all_properties),
            page=1,
            per_page=len(all_properties),
            source=self.source_name,
        )
