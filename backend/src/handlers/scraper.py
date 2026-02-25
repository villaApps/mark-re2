"""Scraper Lambda handler - triggered by EventBridge schedule."""

import asyncio
import json
import os
import sys
from datetime import datetime
from decimal import Decimal
from typing import Any

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

# Add layer path for shared modules
sys.path.insert(0, "/opt/python")

# Import from scraper module (shared layer)
try:
    from scraper.src.scrapers.simon_estates import SimonEstatesScraper
    from scraper.src.scrapers.frank_salt import FrankSaltScraper
    from scraper.src.scrapers.remax import RemaxScraper
    from scraper.src.scrapers.dhalia import DhaliaScraper
    from scraper.src.models.property import Property as ScraperProperty
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    logger.warning("Scraper module not available in layer, using fallback implementation")

from src.models.scraper import ScraperSource, ScraperResult
from src.models.property import PropertyCreate, PropertyType, PropertyStatus
from src.services.scraper_service import ScraperService
from src.services.property_service import PropertyService
from src.utils.errors import ScraperError, PropertyAnalyzerError
from src.utils.logger import log_handler, LoggerContext
from src.utils.id_generator import generate_correlation_id

logger = Logger()
tracer = Tracer()

# Initialize services
scraper_service = ScraperService()
property_service = PropertyService()

# EventBridge client for publishing events
events_client = boto3.client("events")
event_bus_name = os.environ.get("EVENT_BUS_NAME", "property-events-dev")

# Scraper mapping
SCRAPER_MAP = {
    ScraperSource.SIMONESTATES: "SimonEstatesScraper",
    ScraperSource.FRANKSALT: "FrankSaltScraper",
    ScraperSource.REMax: "RemaxScraper",
    ScraperSource.DHALIA: "DhaliaScraper",
}


def convert_scraper_property_to_create(
    scraper_prop: Any,
    source: ScraperSource,
) -> PropertyCreate:
    """Convert a scraper Property model to backend PropertyCreate model."""
    # Map property type string to enum
    property_type = PropertyType.APARTMENT
    type_lower = (scraper_prop.property_type or "").lower()
    for pt in PropertyType:
        if pt.value in type_lower:
            property_type = pt
            break

    # Parse location
    location = None
    if hasattr(scraper_prop, "location") and scraper_prop.location:
        from src.models.common import Location
        location = Location(
            address=scraper_prop.location,
            locality=scraper_prop.location.split(",")[0].strip() if "," in scraper_prop.location else scraper_prop.location,
        )

    return PropertyCreate(
        external_id=scraper_prop.id,
        source_url=scraper_prop.url,
        source_name=source.value,
        title=scraper_prop.title,
        description=getattr(scraper_prop, "description", None),
        property_type=property_type,
        status=PropertyStatus.FOR_SALE,
        price=Decimal(str(scraper_prop.price)),
        location=location,
        town=location.locality if location else None,
        bedrooms=scraper_prop.bedrooms,
        bathrooms=scraper_prop.bathrooms,
        internal_area_sqm=Decimal(str(scraper_prop.square_meters)) if scraper_prop.square_meters else None,
        images=scraper_prop.images or [],
    )


async def scrape_source_with_module(
    source: ScraperSource,
    run_id: str,
) -> ScraperResult:
    """Scrape a single source using the scraper module."""
    import time
    start_time = time.time()

    scraper_class_name = SCRAPER_MAP.get(source)
    if not scraper_class_name or not SCRAPER_AVAILABLE:
        # Fallback to service implementation
        return await scraper_service.scrape_source(source)

    try:
        # Get scraper class from globals
        scraper_class = globals().get(scraper_class_name)
        if not scraper_class:
            raise ScraperError(f"Scraper class not found: {scraper_class_name}")

        properties = []
        new_count = 0
        updated_count = 0

        async with scraper_class() as scraper:
            # Scrape listings from the source
            scraped_properties = await scraper.scrape_listings(max_pages=5)
            logger.info(f"Scraped {len(scraped_properties)} properties from {source.value}")

            # Save raw data to S3
            raw_data = [p.model_dump() for p in scraped_properties]
            await scraper_service.save_raw_data(run_id, source, raw_data)

            # Convert and save each property
            for scraper_prop in scraped_properties:
                try:
                    property_create = convert_scraper_property_to_create(scraper_prop, source)
                    existing_property = None

                    try:
                        existing_property = await property_service.get_property(
                            f"{source.value}_{scraper_prop.id}"
                        )
                    except Exception:
                        pass

                    if existing_property:
                        # Update existing property
                        await property_service.update_property(
                            existing_property.property_id,
                            property_create.model_dump(exclude_unset=True),
                        )
                        updated_count += 1
                    else:
                        # Create new property
                        await property_service.create_property(property_create)
                        new_count += 1

                    properties.append(scraper_prop)

                except Exception as e:
                    logger.warning(f"Failed to process property {scraper_prop.id}: {e}")
                    await scraper_service.add_run_error(run_id, source.value, str(e), {"property_id": scraper_prop.id})

        duration = time.time() - start_time

        return ScraperResult(
            success=True,
            source=source,
            properties=properties,
            properties_count=len(properties),
            new_count=new_count,
            updated_count=updated_count,
            duration_seconds=duration,
        )

    except Exception as e:
        duration = time.time() - start_time
        logger.exception(f"Failed to scrape {source.value}")
        return ScraperResult(
            success=False,
            source=source,
            properties=[],
            properties_count=0,
            new_count=0,
            updated_count=0,
            error=str(e),
            duration_seconds=duration,
        )


async def scrape_all_sources(run_id: str) -> list[ScraperResult]:
    """Scrape all configured sources."""
    sources = [
        ScraperSource.SIMONESTATES,
        ScraperSource.FRANKSALT,
        ScraperSource.REMax,
        ScraperSource.DHALIA,
    ]

    results = []

    for source in sources:
        try:
            logger.info(f"Starting scrape for source: {source.value}")
            result = await scrape_source_with_module(source, run_id)
            results.append(result)

            if not result.success:
                await scraper_service.add_run_error(
                    run_id,
                    source.value,
                    result.error or "Unknown error",
                )

        except Exception as e:
            logger.exception(f"Failed to scrape {source.value}")
            await scraper_service.add_run_error(run_id, source.value, str(e))
            results.append(ScraperResult(
                success=False,
                source=source,
                error=str(e),
            ))

    return results


async def publish_scraper_complete_event(run_id: str, results: list[ScraperResult]) -> None:
    """Publish EventBridge event when scraper completes."""
    try:
        total_properties = sum(r.properties_count for r in results)
        successful_sources = sum(1 for r in results if r.success)
        
        event_detail = {
            "runId": run_id,
            "totalProperties": total_properties,
            "successfulSources": successful_sources,
            "totalSources": len(results),
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }
        
        response = events_client.put_events(
            Entries=[
                {
                    "Source": "malta.property.scraper",
                    "DetailType": "ScraperComplete",
                    "Detail": json.dumps(event_detail),
                    "EventBusName": event_bus_name,
                }
            ]
        )
        
        logger.info(f"Published ScraperComplete event: {response}")
        
    except Exception as e:
        logger.exception("Failed to publish ScraperComplete event")
        # Don't raise - event publishing failure shouldn't fail the scraper


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@log_handler
async def handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Lambda handler entry point for scheduled scraper."""
    correlation_id = generate_correlation_id()
    
    with LoggerContext("scraper", correlation_id=correlation_id):
        logger.info("Scraper handler invoked", extra={"event": event})
        
        # Determine trigger source
        trigger_source = event.get("source", "schedule")
        
        # Create scraper run record
        sources = [
            ScraperSource.SIMONESTATES,
            ScraperSource.FRANKSALT,
            ScraperSource.REMax,
            ScraperSource.DHALIA,
        ]
        
        run = await scraper_service.create_run(sources, triggered_by=trigger_source)
        run_id = run.run_id
        
        logger.append_keys(run_id=run_id)
        logger.info(f"Created scraper run: {run_id}")
        
        try:
            # Mark run as started
            await scraper_service.start_run(run_id)
            
            # Scrape all sources
            results = await scrape_all_sources(run_id)
            
            # Mark run as completed
            completed_run = await scraper_service.complete_run(run_id, results)
            
            # Publish completion event
            await publish_scraper_complete_event(run_id, results)
            
            # Return summary
            total_new = sum(r.new_count for r in results)
            total_updated = sum(r.updated_count for r in results)
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "success": True,
                    "runId": run_id,
                    "totalProperties": completed_run.total_properties_found,
                    "newProperties": total_new,
                    "updatedProperties": total_updated,
                    "sourceResults": [
                        {
                            "source": r.source.value,
                            "success": r.success,
                            "count": r.properties_count,
                            "error": r.error,
                        }
                        for r in results
                    ],
                }),
            }
            
        except Exception as e:
            logger.exception("Scraper failed")
            await scraper_service.fail_run(run_id, str(e))
            
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "success": False,
                    "runId": run_id,
                    "error": str(e),
                }),
            }


# Wrapper for synchronous Lambda invocation
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Synchronous entry point for Lambda."""
    return asyncio.run(handler(event, context))
