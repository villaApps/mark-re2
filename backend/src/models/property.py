"""Property models for the Malta Property Analyzer."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from src.models.common import Location


class PropertyType(str, Enum):
    """Types of properties in Malta."""

    APARTMENT = "apartment"
    MAISONETTE = "maisonette"
    PENTHOUSE = "penthouse"
    TOWNHOUSE = "townhouse"
    VILLA = "villa"
    BUNGALOW = "bungalow"
    FARMHOUSE = "farmhouse"
    STUDIO = "studio"
    DUPLEX = "duplex"
    TRIPLEX = "triplex"
    OFFICE = "office"
    SHOP = "shop"
    WAREHOUSE = "warehouse"
    LAND = "land"


class PropertyStatus(str, Enum):
    """Status of a property listing."""

    FOR_SALE = "for_sale"
    FOR_RENT = "for_rent"
    SOLD = "sold"
    RENTED = "rented"
    UNDER_OFFER = "under_offer"
    RESERVED = "reserved"


class PriceRange(str, Enum):
    """Price range categories for filtering."""

    UNDER_100K = "under_100k"
    RANGE_100K_200K = "100k_200k"
    RANGE_200K_300K = "200k_300k"
    RANGE_300K_500K = "300k_500k"
    RANGE_500K_750K = "500k_750k"
    RANGE_750K_1M = "750k_1m"
    OVER_1M = "over_1m"


class Property(BaseModel):
    """Property model representing a real estate listing."""

    property_id: str = Field(..., description="Unique property identifier")
    external_id: str | None = Field(None, description="ID from source website")
    source_url: str | None = Field(None, description="URL of the listing")
    source_name: str | None = Field(None, description="Name of the source website")

    # Basic info
    title: str = Field(..., min_length=1, max_length=500, description="Property title")
    description: str | None = Field(None, description="Property description")
    property_type: PropertyType = Field(..., description="Type of property")
    status: PropertyStatus = Field(default=PropertyStatus.FOR_SALE, description="Listing status")

    # Pricing
    price: Decimal = Field(..., gt=0, description="Price in EUR")
    price_per_sqm: Decimal | None = Field(None, ge=0, description="Price per square meter")
    price_range: PriceRange | None = Field(None, description="Price range category")
    original_price: Decimal | None = Field(None, gt=0, description="Original price if reduced")

    # Location
    location: Location | None = Field(None, description="Property location")
    region: str | None = Field(None, description="Region in Malta")
    town: str | None = Field(None, description="Town/village name")

    # Physical characteristics
    bedrooms: int | None = Field(None, ge=0, description="Number of bedrooms")
    bathrooms: int | None = Field(None, ge=0, description="Number of bathrooms")
    total_rooms: int | None = Field(None, ge=0, description="Total number of rooms")
    internal_area_sqm: Decimal | None = Field(None, gt=0, description="Internal area in sqm")
    external_area_sqm: Decimal | None = Field(None, ge=0, description="External area in sqm")
    total_area_sqm: Decimal | None = Field(None, gt=0, description="Total area in sqm")
    floor_number: int | None = Field(None, description="Floor number")
    total_floors: int | None = Field(None, ge=1, description="Total floors in building")
    year_built: int | None = Field(None, ge=1800, le=2100, description="Year built")
    condition: str | None = Field(None, description="Property condition")

    # Features
    features: list[str] = Field(default_factory=list, description="List of features")
    has_garage: bool = Field(False, description="Has garage/parking")
    has_garden: bool = Field(False, description="Has garden")
    has_pool: bool = Field(False, description="Has pool")
    has_elevator: bool = Field(False, description="Has elevator")
    is_furnished: bool | None = Field(None, description="Is furnished")
    has_air_conditioning: bool = Field(False, description="Has AC")
    has_heating: bool = Field(False, description="Has heating")

    # Media
    images: list[str] = Field(default_factory=list, description="Image URLs")
    floor_plans: list[str] = Field(default_factory=list, description="Floor plan URLs")
    virtual_tour_url: str | None = Field(None, description="Virtual tour URL")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    scraped_at: datetime | None = Field(None, description="When the data was scraped")
    is_active: bool = Field(True, description="Whether the listing is active")
    view_count: int = Field(0, ge=0, description="Number of views")

    # Analysis
    roi_score: Decimal | None = Field(None, ge=0, le=100, description="ROI score (0-100)")
    analysis_count: int = Field(0, ge=0, description="Number of analyses performed")

    @field_validator("price_range", mode="before")
    @classmethod
    def calculate_price_range(cls, v: Any, info: Any) -> PriceRange:
        """Calculate price range from price if not provided."""
        if v is not None:
            return v
        
        price_data = info.data.get("price")
        if price_data is None:
            return None
        
        price = float(price_data)
        if price < 100_000:
            return PriceRange.UNDER_100K
        elif price < 200_000:
            return PriceRange.RANGE_100K_200K
        elif price < 300_000:
            return PriceRange.RANGE_200K_300K
        elif price < 500_000:
            return PriceRange.RANGE_300K_500K
        elif price < 750_000:
            return PriceRange.RANGE_500K_750K
        elif price < 1_000_000:
            return PriceRange.RANGE_750K_1M
        else:
            return PriceRange.OVER_1M

    @model_validator(mode="after")
    def calculate_total_area(self) -> "Property":
        """Calculate total area if not provided."""
        if self.total_area_sqm is None:
            internal = self.internal_area_sqm or Decimal("0")
            external = self.external_area_sqm or Decimal("0")
            if internal > 0 or external > 0:
                self.total_area_sqm = internal + external
        return self

    @model_validator(mode="after")
    def calculate_price_per_sqm(self) -> "Property":
        """Calculate price per sqm if not provided."""
        if self.price_per_sqm is None and self.total_area_sqm and self.total_area_sqm > 0:
            self.price_per_sqm = Decimal(str(self.price)) / self.total_area_sqm
        return self

    def to_dynamodb_item(self) -> dict[str, Any]:
        """Convert to DynamoDB item format."""
        data = self.model_dump()
        # Convert Decimal to float for DynamoDB
        for key in ["price", "price_per_sqm", "original_price", "internal_area_sqm", 
                    "external_area_sqm", "total_area_sqm", "roi_score"]:
            if data.get(key) is not None:
                data[key] = float(data[key])
        # Convert datetime to ISO string
        for key in ["created_at", "updated_at", "scraped_at"]:
            if data.get(key) is not None:
                data[key] = data[key].isoformat()
        # Convert enums to strings
        data["property_type"] = data["property_type"].value
        data["status"] = data["status"].value
        if data.get("price_range"):
            data["price_range"] = data["price_range"].value
        # Convert location
        if data.get("location"):
            data["location"] = {
                "latitude": data["location"]["latitude"],
                "longitude": data["location"]["longitude"],
                "address": data["location"].get("address"),
                "locality": data["location"].get("locality"),
            }
        return data

    @classmethod
    def from_dynamodb_item(cls, item: dict[str, Any]) -> "Property":
        """Create Property from DynamoDB item."""
        # Convert float back to Decimal
        for key in ["price", "price_per_sqm", "original_price", "internal_area_sqm",
                    "external_area_sqm", "total_area_sqm", "roi_score"]:
            if key in item and item[key] is not None:
                item[key] = Decimal(str(item[key]))
        # Convert ISO strings back to datetime
        for key in ["created_at", "updated_at", "scraped_at"]:
            if key in item and item[key] is not None:
                item[key] = datetime.fromisoformat(item[key])
        # Convert string enums back
        if "property_type" in item:
            item["property_type"] = PropertyType(item["property_type"])
        if "status" in item:
            item["status"] = PropertyStatus(item["status"])
        if "price_range" in item and item["price_range"]:
            item["price_range"] = PriceRange(item["price_range"])
        return cls(**item)


class PropertyCreate(BaseModel):
    """Model for creating a new property."""

    external_id: str | None = None
    source_url: str | None = None
    source_name: str | None = None
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    property_type: PropertyType
    status: PropertyStatus = PropertyStatus.FOR_SALE
    price: Decimal = Field(..., gt=0)
    location: Location | None = None
    region: str | None = None
    town: str | None = None
    bedrooms: int | None = Field(None, ge=0)
    bathrooms: int | None = Field(None, ge=0)
    total_rooms: int | None = Field(None, ge=0)
    internal_area_sqm: Decimal | None = Field(None, gt=0)
    external_area_sqm: Decimal | None = Field(None, ge=0)
    floor_number: int | None = None
    total_floors: int | None = Field(None, ge=1)
    year_built: int | None = Field(None, ge=1800, le=2100)
    condition: str | None = None
    features: list[str] = Field(default_factory=list)
    has_garage: bool = False
    has_garden: bool = False
    has_pool: bool = False
    has_elevator: bool = False
    is_furnished: bool | None = None
    has_air_conditioning: bool = False
    has_heating: bool = False
    images: list[str] = Field(default_factory=list)


class PropertyUpdate(BaseModel):
    """Model for updating an existing property."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    status: PropertyStatus | None = None
    price: Decimal | None = Field(None, gt=0)
    location: Location | None = None
    bedrooms: int | None = Field(None, ge=0)
    bathrooms: int | None = Field(None, ge=0)
    internal_area_sqm: Decimal | None = Field(None, gt=0)
    external_area_sqm: Decimal | None = Field(None, ge=0)
    features: list[str] | None = None
    has_garage: bool | None = None
    has_garden: bool | None = None
    has_pool: bool | None = None
    is_furnished: bool | None = None
    images: list[str] | None = None
    is_active: bool | None = None


class PropertyFilter(BaseModel):
    """Filter model for property queries."""

    property_type: PropertyType | None = None
    status: PropertyStatus | None = PropertyStatus.FOR_SALE
    min_price: Decimal | None = Field(None, ge=0)
    max_price: Decimal | None = Field(None, ge=0)
    location: str | None = None
    region: str | None = None
    town: str | None = None
    min_bedrooms: int | None = Field(None, ge=0)
    max_bedrooms: int | None = Field(None, ge=0)
    min_bathrooms: int | None = Field(None, ge=0)
    min_area_sqm: Decimal | None = Field(None, ge=0)
    max_area_sqm: Decimal | None = Field(None, ge=0)
    has_garage: bool | None = None
    has_garden: bool | None = None
    has_pool: bool | None = None
    features: list[str] = Field(default_factory=list)
    min_roi_score: Decimal | None = Field(None, ge=0, le=100)
    sort_by: str = Field(default="created_at", pattern="^(price|created_at|roi_score|price_per_sqm)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
