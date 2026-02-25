"""Tests for property models."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models.property import Property, PropertyType, ListingType


class TestProperty:
    """Tests for Property model."""
    
    def test_create_valid_property(self):
        """Test creating a valid property."""
        prop = Property(
            id="test123",
            source="test",
            url="https://example.com/123",
            title="Test Property",
            location="Sliema",
            property_type=PropertyType.APARTMENT,
            price=Decimal("450000"),
        )
        
        assert prop.id == "test123"
        assert prop.source == "test"
        assert prop.title == "Test Property"
        assert prop.price == Decimal("450000")
        assert prop.price_currency == "EUR"
        assert prop.listing_type == ListingType.SALE
    
    def test_property_with_all_fields(self):
        """Test property with all optional fields."""
        prop = Property(
            id="test456",
            source="test",
            url="https://example.com/456",
            title="Full Property",
            description="A nice property",
            location="Valletta",
            property_type=PropertyType.PENTHOUSE,
            listing_type=ListingType.RENT,
            price=Decimal("2500"),
            bedrooms=3,
            bathrooms=2,
            square_meters=120.5,
            monthly_rent=Decimal("2500"),
            images=["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
        )
        
        assert prop.bedrooms == 3
        assert prop.bathrooms == 2
        assert prop.square_meters == 120.5
        assert len(prop.images) == 2
    
    def test_price_validation_string(self):
        """Test price validation with string input."""
        prop = Property(
            id="test",
            source="test",
            url="https://example.com",
            title="Test",
            location="Malta",
            property_type=PropertyType.APARTMENT,
            price="500000",  # String input
        )
        assert prop.price == Decimal("500000")
    
    def test_price_validation_int(self):
        """Test price validation with int input."""
        prop = Property(
            id="test",
            source="test",
            url="https://example.com",
            title="Test",
            location="Malta",
            property_type=PropertyType.APARTMENT,
            price=500000,  # Int input
        )
        assert prop.price == Decimal("500000")
    
    def test_price_validation_zero_fails(self):
        """Test that zero price fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            Property(
                id="test",
                source="test",
                url="https://example.com",
                title="Test",
                location="Malta",
                property_type=PropertyType.APARTMENT,
                price=0,
            )
        assert "Price must be positive" in str(exc_info.value)
    
    def test_price_validation_negative_fails(self):
        """Test that negative price fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            Property(
                id="test",
                source="test",
                url="https://example.com",
                title="Test",
                location="Malta",
                property_type=PropertyType.APARTMENT,
                price=-100,
            )
        assert "Price must be positive" in str(exc_info.value)
    
    def test_images_default_empty_list(self):
        """Test that images defaults to empty list."""
        prop = Property(
            id="test",
            source="test",
            url="https://example.com",
            title="Test",
            location="Malta",
            property_type=PropertyType.APARTMENT,
            price=100000,
        )
        assert prop.images == []
    
    def test_property_type_enum(self):
        """Test property type enum values."""
        assert PropertyType.APARTMENT.value == "apartment"
        assert PropertyType.HOUSE.value == "house"
        assert PropertyType.PENTHOUSE.value == "penthouse"
    
    def test_listing_type_enum(self):
        """Test listing type enum values."""
        assert ListingType.SALE.value == "sale"
        assert ListingType.RENT.value == "rent"
