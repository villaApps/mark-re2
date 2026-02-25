"""Market data and property listing models."""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class PropertyListing(BaseModel):
    """Property listing from market data."""
    
    property_id: str = Field(..., description="Unique property identifier")
    
    # Basic Info
    title: Optional[str] = Field(None, description="Property listing title")
    description: Optional[str] = Field(None, description="Property description")
    property_type: str = Field(..., description="Type: apartment, house, penthouse, etc.")
    
    # Location
    area: str = Field(..., description="Area/locality in Malta")
    address: Optional[str] = Field(None, description="Full address")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    
    # Pricing
    listing_price: Decimal = Field(..., description="Listed price")
    price_per_sqm: Optional[Decimal] = Field(None, description="Price per square meter")
    
    # Property Details
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms", ge=0)
    bathrooms: Optional[int] = Field(None, description="Number of bathrooms", ge=0)
    sqm_internal: Optional[Decimal] = Field(None, description="Internal area in sqm", ge=0)
    sqm_external: Optional[Decimal] = Field(None, description="External area in sqm", ge=0)
    floor: Optional[str] = Field(None, description="Floor level")
    has_elevator: bool = Field(default=False, description="Building has elevator")
    has_garage: bool = Field(default=False, description="Property includes garage")
    year_built: Optional[int] = Field(None, description="Year property was built")
    condition: Optional[str] = Field(None, description="Property condition")
    
    # Features
    features: List[str] = Field(default_factory=list, description="Property features")
    
    # Listing Info
    listing_date: Optional[datetime] = Field(None, description="When listed")
    listing_agent: Optional[str] = Field(None, description="Listing agent/agency")
    listing_url: Optional[str] = Field(None, description="URL to listing")
    
    # Market Data
    estimated_rent: Optional[Decimal] = Field(None, description="Estimated monthly rent")
    days_on_market: Optional[int] = Field(None, description="Days since listing")
    
    @field_validator("listing_price", "price_per_sqm", "sqm_internal", "sqm_external", "estimated_rent", mode="before")
    @classmethod
    def convert_to_decimal(cls, v):
        """Convert numeric values to Decimal."""
        if v is None:
            return v
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v
    
    @property
    def total_sqm(self) -> Optional[Decimal]:
        """Calculate total area."""
        if self.sqm_internal is None:
            return self.sqm_external
        if self.sqm_external is None:
            return self.sqm_internal
        return self.sqm_internal + self.sqm_external
    
    @property
    def estimated_gross_yield(self) -> Optional[Decimal]:
        """Calculate estimated gross rental yield."""
        if self.estimated_rent is None or self.estimated_rent == 0:
            return None
        annual_rent = self.estimated_rent * Decimal("12")
        return annual_rent / self.listing_price


class MarketConditions(BaseModel):
    """Current market conditions for analysis context."""
    
    # Interest Rates
    average_mortgage_rate: Decimal = Field(
        default=Decimal("0.035"),
        description="Current average mortgage interest rate"
    )
    rate_trend: str = Field(
        default="stable",
        description="Rate trend: rising, falling, stable"
    )
    
    # Market Activity
    market_temperature: str = Field(
        default="balanced",
        description="Market temperature: hot, warm, balanced, cool, cold"
    )
    average_days_on_market: int = Field(
        default=60,
        description="Average days properties stay on market"
    )
    
    # Price Trends
    price_growth_yoy: Decimal = Field(
        default=Decimal("0.03"),
        description="Year-over-year price growth"
    )
    price_growth_forecast: Decimal = Field(
        default=Decimal("0.025"),
        description="Forecasted price growth"
    )
    
    # Rental Market
    rental_growth_yoy: Decimal = Field(
        default=Decimal("0.025"),
        description="Year-over-year rental growth"
    )
    average_vacancy_rate: Decimal = Field(
        default=Decimal("0.05"),
        description="Average market vacancy rate"
    )
    
    # Area-Specific Data
    area_price_per_sqm: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Average price per sqm by area"
    )
    area_rent_per_sqm: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Average rent per sqm by area"
    )
    
    # Economic Indicators
    inflation_rate: Decimal = Field(
        default=Decimal("0.025"),
        description="Current inflation rate"
    )
    unemployment_rate: Decimal = Field(
        default=Decimal("0.03"),
        description="Unemployment rate"
    )
    
    # Timestamp
    data_date: datetime = Field(
        default_factory=datetime.now,
        description="When this data was collected"
    )
    
    @field_validator(
        "average_mortgage_rate", "price_growth_yoy", "price_growth_forecast",
        "rental_growth_yoy", "average_vacancy_rate", "inflation_rate",
        "unemployment_rate",
        mode="before"
    )
    @classmethod
    def convert_to_decimal(cls, v):
        """Convert numeric values to Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v
    
    def get_area_price_per_sqm(self, area: str) -> Optional[Decimal]:
        """Get average price per sqm for a specific area."""
        area_normalized = area.lower().strip().replace(" ", "_")
        return self.area_price_per_sqm.get(area_normalized)
    
    def get_area_rent_per_sqm(self, area: str) -> Optional[Decimal]:
        """Get average rent per sqm for a specific area."""
        area_normalized = area.lower().strip().replace(" ", "_")
        return self.area_rent_per_sqm.get(area_normalized)
