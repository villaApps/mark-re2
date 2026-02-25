"""Lambda handlers for the Malta Property Analyzer."""

from src.handlers.properties_api import handler as properties_handler
from src.handlers.roi_api import handler as roi_handler
from src.handlers.scraper import handler as scraper_handler
from src.handlers.analyzer import handler as analyzer_handler
from src.handlers.stream_processor import handler as stream_handler

__all__ = [
    "properties_handler",
    "roi_handler",
    "scraper_handler",
    "analyzer_handler",
    "stream_handler",
]
