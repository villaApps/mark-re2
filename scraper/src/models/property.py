"""Property data models using Pydantic v2."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class PropertyType(str, Enum):
    """Types of properties."""
    APARTMENT = "apartment"
    HOUSE = "house"
    PENTHOUSE = "penthouse"
    MAISONETTE = "maisonette"
    VILLA = "villa"
    TOWNHOUSE = "townhouse"
    STUDIO = "studio"
    DUPLEX = "duplex"
    OTHER = "other"


class ListingType(str, Enum):
    """Type of listing."""
    SALE = "sale"
    RENT = "rent"


class Property(BaseModel):
    """Property listing model."""
    
    id: str = Field(..., description="Unique property ID")
    source: str = Field(..., description="Source website name")
    url: str = Field(..., description="Property listing URL")
    
    # Basic info
    title: str = Field(..., description="Property title")
    description: Optional[str] = Field(None, description="Property description")
    location: str = Field(..., description="Location/area in Malta")
    
    # Property details
    property_type: PropertyType = Field(..., description="Type of property")
    listing_type: ListingType = Field(default=ListingType.SALE, description="Sale or rent")
    
    # Pricing
    price: Decimal = Field(..., description="Price in EUR")
    price_currency: str = Field(default="EUR", description="Currency code")
    
    # Features
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms", ge=0)
    bathrooms: Optional[int] = Field(None, description="Number of bathrooms", ge=0)
    square_meters: Optional[float] = Field(None, description="Property size in sqm", gt=0)
    
    # Rental specific
    monthly_rent: Optional[Decimal] = Field(None, description="Monthly rent if rental listing")
    
    # Media
    images: List[str] = Field(default_factory=list, description="Image URLs")
    
    # Metadata
    listed_date: Optional[datetime] = Field(None, description="When property was listed")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, description="When property was scraped")
    
    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, v):
        """Ensure price is positive Decimal."""
        if isinstance(v, (int, float, str)):
            v = Decimal(str(v))
        if v <= 0:
            raise ValueError("Price must be positive")
        return v
    
    @field_validator("images", mode="before")
    @classmethod
    def validate_images(cls, v):
        """Ensure images is a list."""
        if v is None:
            return []
        return v
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat(),
        }
