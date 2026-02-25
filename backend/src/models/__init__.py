"""Pydantic models for the Malta Property Analyzer."""

from src.models.property import Property, PropertyCreate, PropertyUpdate, PropertyFilter
from src.models.analysis import ROIAnalysis, ROIInput, OpportunityFilter
from src.models.scraper import ScraperRun, ScraperResult
from src.models.common import ApiResponse, PaginatedResponse, Location

__all__ = [
    "Property",
    "PropertyCreate",
    "PropertyUpdate",
    "PropertyFilter",
    "ROIAnalysis",
    "ROIInput",
    "OpportunityFilter",
    "ScraperRun",
    "ScraperResult",
    "ApiResponse",
    "PaginatedResponse",
    "Location",
]
