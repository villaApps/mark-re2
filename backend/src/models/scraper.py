"""Scraper models for the Malta Property Analyzer."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ScraperStatus(str, Enum):
    """Status of a scraper run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class ScraperSource(str, Enum):
    """Source websites for scraping."""

    SIMONESTATES = "simonestates"
    FRANKSALT = "franksalt"
    REMax = "remax"
    DHALIA = "dhalia"
    BELAIR = "belair"
    CENTURY21 = "century21"


class ScrapedProperty(BaseModel):
    """A property scraped from a source."""

    external_id: str = Field(..., description="ID from source website")
    source: ScraperSource = Field(..., description="Source website")
    source_url: str = Field(..., description="URL of the listing")
    title: str = Field(..., description="Property title")
    price: float = Field(..., gt=0, description="Price in EUR")
    location: str | None = Field(None, description="Location string")
    bedrooms: int | None = Field(None, ge=0, description="Number of bedrooms")
    bathrooms: int | None = Field(None, ge=0, description="Number of bathrooms")
    area_sqm: float | None = Field(None, gt=0, description="Area in square meters")
    property_type: str | None = Field(None, description="Type of property")
    description: str | None = Field(None, description="Property description")
    images: list[str] = Field(default_factory=list, description="Image URLs")
    features: list[str] = Field(default_factory=list, description="Property features")


class ScraperRun(BaseModel):
    """Record of a scraper execution."""

    run_id: str = Field(..., description="Unique run identifier")
    status: ScraperStatus = Field(default=ScraperStatus.PENDING)
    sources: list[ScraperSource] = Field(default_factory=list)
    
    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float | None = None
    
    # Results
    total_properties_found: int = Field(0, ge=0)
    total_properties_new: int = Field(0, ge=0)
    total_properties_updated: int = Field(0, ge=0)
    total_properties_failed: int = Field(0, ge=0)
    
    # Per-source results
    source_results: dict[str, dict[str, Any]] = Field(default_factory=dict)
    
    # Errors
    errors: list[dict[str, Any]] = Field(default_factory=list)
    error_message: str | None = None
    
    # Metadata
    triggered_by: str = Field(default="schedule", description="manual, schedule, or event")
    correlation_id: str | None = None
    expires_at: int | None = Field(None, description="TTL timestamp for cleanup")

    def mark_started(self) -> None:
        """Mark the scraper run as started."""
        self.status = ScraperStatus.RUNNING
        self.started_at = datetime.utcnow()

    def mark_completed(self) -> None:
        """Mark the scraper run as completed."""
        self.status = ScraperStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

    def mark_failed(self, error_message: str) -> None:
        """Mark the scraper run as failed."""
        self.status = ScraperStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

    def add_error(self, source: str, error: str, details: dict[str, Any] | None = None) -> None:
        """Add an error to the run record."""
        error_entry: dict[str, Any] = {
            "source": source,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if details:
            error_entry["details"] = details
        self.errors.append(error_entry)
        self.total_properties_failed += 1

    def to_dynamodb_item(self) -> dict[str, Any]:
        """Convert to DynamoDB item format."""
        data = self.model_dump()
        
        # Convert datetime to ISO strings
        for key in ["started_at", "completed_at"]:
            if data.get(key) is not None:
                data[key] = data[key].isoformat()
        
        # Convert enums
        data["status"] = data["status"].value
        data["sources"] = [s.value for s in data["sources"]]
        
        return data

    @classmethod
    def from_dynamodb_item(cls, item: dict[str, Any]) -> "ScraperRun":
        """Create ScraperRun from DynamoDB item."""
        # Convert ISO strings to datetime
        for key in ["started_at", "completed_at"]:
            if key in item and item[key] is not None:
                item[key] = datetime.fromisoformat(item[key])
        
        # Convert enums
        if "status" in item:
            item["status"] = ScraperStatus(item["status"])
        if "sources" in item:
            item["sources"] = [ScraperSource(s) for s in item["sources"]]
        
        return cls(**item)


class ScraperResult(BaseModel):
    """Result of a scraper operation."""

    success: bool
    source: ScraperSource
    properties: list[ScrapedProperty] = Field(default_factory=list)
    properties_count: int = 0
    new_count: int = 0
    updated_count: int = 0
    error: str | None = None
    duration_seconds: float | None = None
