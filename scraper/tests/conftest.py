"""Pytest fixtures for scraper tests."""

import pytest
from decimal import Decimal

from src.models.property import Property, PropertyType, ListingType


@pytest.fixture
def sample_property():
    """Return a sample property for testing."""
    return Property(
        id="test123",
        source="test_source",
        url="https://example.com/property/123",
        title="Test Apartment in Sliema",
        description="A beautiful test apartment",
        location="Sliema",
        property_type=PropertyType.APARTMENT,
        listing_type=ListingType.SALE,
        price=Decimal("450000"),
        bedrooms=2,
        bathrooms=1,
        square_meters=85.0,
        images=["https://example.com/img1.jpg"],
    )


@pytest.fixture
def sample_html_listing():
    """Return sample HTML for property listing page."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Properties</title></head>
    <body>
        <div class="property-card">
            <a href="/property/123">
                <img src="/img/123.jpg" data-src="/img/123.jpg">
                <h3>Modern Apartment in Sliema</h3>
                <span class="price">€450,000</span>
                <span class="location">Sliema</span>
                <span class="features">2 bed, 1 bath, 85 sqm</span>
            </a>
        </div>
        <div class="property-card">
            <a href="/property/456">
                <img src="/img/456.jpg">
                <h3>Penthouse in St Julians</h3>
                <span class="price">€750,000</span>
                <span class="location">St Julians</span>
                <span class="features">3 bed, 2 bath, 120 sqm</span>
            </a>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_detail():
    """Return sample HTML for property detail page."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Property Detail</title></head>
    <body>
        <h1>Luxury Villa in Mellieha</h1>
        <div class="price">€850,000</div>
        <div class="location">Mellieha</div>
        <div class="description">Beautiful villa with pool</div>
        <div class="features">
            <span>4 bedrooms</span>
            <span>3 bathrooms</span>
            <span>250 sqm</span>
        </div>
    </body>
    </html>
    """
