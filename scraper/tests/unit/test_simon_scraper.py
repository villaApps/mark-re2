"""Tests for Simon Estates scraper."""

import pytest
import respx
from decimal import Decimal
from httpx import Response

from src.scrapers.simon_estates import SimonEstatesScraper
from src.scrapers.base import ScraperError, ParseError
from src.models.property import PropertyType, ListingType


class TestSimonEstatesScraper:
    """Tests for SimonEstatesScraper."""
    
    @pytest.fixture
    def scraper(self):
        """Create scraper instance."""
        return SimonEstatesScraper()
    
    @respx.mock
    async def test_scrape_listings_success(self, scraper, sample_html_listing):
        """Test successful scraping of listings."""
        # Mock the listing page
        route = respx.get("https://www.simonestates.com/properties/page/1/").mock(
            return_value=Response(200, text=sample_html_listing)
        )
        
        # Mock subsequent pages as empty
        respx.get("https://www.simonestates.com/properties/page/2/").mock(
            return_value=Response(200, text="<html><body></body></html>")
        )
        
        properties = await scraper.scrape_listings(max_pages=1)
        
        assert len(properties) == 2
        assert route.called
        
        # Check first property
        prop = properties[0]
        assert prop.source == "simon_estates"
        assert prop.title == "Modern Apartment in Sliema"
        assert prop.price == Decimal("450000")
        assert prop.location == "Sliema"
        assert prop.property_type == PropertyType.APARTMENT
        assert prop.listing_type == ListingType.SALE
    
    @respx.mock
    async def test_scrape_listings_http_error(self, scraper):
        """Test handling of HTTP error."""
        respx.get("https://www.simonestates.com/properties/page/1/").mock(
            return_value=Response(500, text="Server Error")
        )
        
        with pytest.raises(ScraperError) as exc_info:
            await scraper.scrape_listings(max_pages=1)
        
        assert "HTTP error" in str(exc_info.value)
    
    @respx.mock
    async def test_scrape_listings_empty_page(self, scraper):
        """Test handling of empty page."""
        respx.get("https://www.simonestates.com/properties/page/1/").mock(
            return_value=Response(200, text="<html><body></body></html>")
        )
        
        properties = await scraper.scrape_listings(max_pages=1)
        
        assert len(properties) == 0
    
    @respx.mock
    async def test_scrape_property_success(self, scraper, sample_html_detail):
        """Test successful scraping of property detail."""
        url = "https://www.simonestates.com/property/123"
        respx.get(url).mock(return_value=Response(200, text=sample_html_detail))
        
        prop = await scraper.scrape_property(url)
        
        assert prop.id is not None
        assert prop.source == "simon_estates"
        assert prop.url == url
        assert prop.title == "Luxury Villa in Mellieha"
        assert prop.price == Decimal("850000")
    
    @respx.mock
    async def test_scrape_property_no_price(self, scraper):
        """Test handling of property page without price."""
        html = "<html><body><h1>Test Property</h1></body></html>"
        url = "https://www.simonestates.com/property/123"
        respx.get(url).mock(return_value=Response(200, text=html))
        
        with pytest.raises(ParseError) as exc_info:
            await scraper.scrape_property(url)
        
        assert "Could not parse price" in str(exc_info.value)
    
    def test_parse_price_with_euro_symbol(self, scraper):
        """Test parsing price with euro symbol."""
        assert scraper._parse_price("€450,000") == Decimal("450000")
    
    def test_parse_price_without_symbol(self, scraper):
        """Test parsing price without symbol."""
        assert scraper._parse_price("450000") == Decimal("450000")
    
    def test_parse_price_with_spaces(self, scraper):
        """Test parsing price with spaces."""
        assert scraper._parse_price("€ 450 000") == Decimal("450000")
    
    def test_parse_price_invalid(self, scraper):
        """Test parsing invalid price."""
        assert scraper._parse_price("Contact for price") is None
    
    def test_detect_property_type_apartment(self, scraper):
        """Test detecting apartment type."""
        assert scraper._detect_property_type("Nice Apartment in Sliema") == PropertyType.APARTMENT
    
    def test_detect_property_type_penthouse(self, scraper):
        """Test detecting penthouse type."""
        assert scraper._detect_property_type("Luxury Penthouse") == PropertyType.PENTHOUSE
    
    def test_detect_property_type_villa(self, scraper):
        """Test detecting villa type."""
        assert scraper._detect_property_type("Beautiful Villa") == PropertyType.VILLA
    
    def test_detect_property_type_unknown(self, scraper):
        """Test detecting unknown type."""
        assert scraper._detect_property_type("Some Property") == PropertyType.OTHER
    
    def test_generate_id_consistency(self, scraper):
        """Test ID generation is consistent."""
        url = "https://example.com/property/123"
        id1 = scraper._generate_id(url)
        id2 = scraper._generate_id(url)
        assert id1 == id2
        assert len(id1) == 12
    
    def test_generate_id_uniqueness(self, scraper):
        """Test ID generation produces unique IDs for different URLs."""
        id1 = scraper._generate_id("https://example.com/1")
        id2 = scraper._generate_id("https://example.com/2")
        assert id1 != id2
