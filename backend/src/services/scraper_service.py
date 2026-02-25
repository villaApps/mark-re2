"""Scraper service for property data collection."""

import json
import os
from datetime import datetime, timedelta
from typing import Any

import boto3
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError

from src.models.property import Property, PropertyCreate, PropertyType, PropertyStatus
from src.models.scraper import ScraperRun, ScraperSource, ScraperStatus, ScrapedProperty, ScraperResult
from src.utils.errors import DatabaseError, ScraperError
from src.utils.id_generator import generate_scraper_run_id
from src.utils.logger import log_method

logger = Logger(child=True)


class ScraperService:
    """Service for scraper operations."""

    def __init__(
        self,
        table_name: str | None = None,
        bucket_name: str | None = None,
    ):
        self.table_name = table_name or os.environ.get("SCRAPER_RUNS_TABLE", "scraper-runs-dev")
        self.bucket_name = bucket_name or os.environ.get("RAW_DATA_BUCKET", "")
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.table_name)
        self.s3 = boto3.client("s3") if self.bucket_name else None

    @log_method
    async def create_run(
        self,
        sources: list[ScraperSource],
        triggered_by: str = "schedule",
    ) -> ScraperRun:
        """Create a new scraper run record."""
        run = ScraperRun(
            run_id=generate_scraper_run_id(),
            sources=sources,
            status=ScraperStatus.PENDING,
            triggered_by=triggered_by,
            expires_at=int((datetime.utcnow() + timedelta(days=90)).timestamp()),
        )
        
        try:
            self.table.put_item(Item=run.to_dynamodb_item())
            logger.info(f"Created scraper run: {run.run_id}")
            return run
        except ClientError as e:
            logger.error(f"Failed to create scraper run: {e}")
            raise DatabaseError(f"Failed to create scraper run: {e}")

    @log_method
    async def start_run(self, run_id: str) -> ScraperRun:
        """Mark a scraper run as started."""
        try:
            response = self.table.update_item(
                Key={"runId": run_id},
                UpdateExpression="SET #status = :status, startedAt = :startedAt",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": ScraperStatus.RUNNING.value,
                    ":startedAt": datetime.utcnow().isoformat(),
                },
                ReturnValues="ALL_NEW",
            )
            
            item = response["Attributes"]
            item["run_id"] = item.pop("runId", run_id)
            return ScraperRun.from_dynamodb_item(item)
            
        except ClientError as e:
            logger.error(f"Failed to start scraper run: {e}")
            raise DatabaseError(f"Failed to start scraper run: {e}")

    @log_method
    async def complete_run(
        self,
        run_id: str,
        results: list[ScraperResult],
    ) -> ScraperRun:
        """Mark a scraper run as completed."""
        total_found = sum(r.properties_count for r in results)
        total_new = sum(r.new_count for r in results)
        total_updated = sum(r.updated_count for r in results)
        
        source_results = {
            r.source.value: {
                "success": r.success,
                "count": r.properties_count,
                "new": r.new_count,
                "updated": r.updated_count,
                "error": r.error,
                "duration_seconds": r.duration_seconds,
            }
            for r in results
        }
        
        try:
            response = self.table.update_item(
                Key={"runId": run_id},
                UpdateExpression="""
                    SET #status = :status,
                        completedAt = :completedAt,
                        totalPropertiesFound = :totalFound,
                        totalPropertiesNew = :totalNew,
                        totalPropertiesUpdated = :totalUpdated,
                        sourceResults = :sourceResults,
                        durationSeconds = :duration
                """,
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": ScraperStatus.COMPLETED.value,
                    ":completedAt": datetime.utcnow().isoformat(),
                    ":totalFound": total_found,
                    ":totalNew": total_new,
                    ":totalUpdated": total_updated,
                    ":sourceResults": source_results,
                    ":duration": self._calculate_duration(run_id),
                },
                ReturnValues="ALL_NEW",
            )
            
            item = response["Attributes"]
            item["run_id"] = item.pop("runId", run_id)
            logger.info(f"Completed scraper run: {run_id}")
            return ScraperRun.from_dynamodb_item(item)
            
        except ClientError as e:
            logger.error(f"Failed to complete scraper run: {e}")
            raise DatabaseError(f"Failed to complete scraper run: {e}")

    @log_method
    async def fail_run(self, run_id: str, error_message: str) -> ScraperRun:
        """Mark a scraper run as failed."""
        try:
            response = self.table.update_item(
                Key={"runId": run_id},
                UpdateExpression="""
                    SET #status = :status,
                        completedAt = :completedAt,
                        errorMessage = :errorMessage,
                        durationSeconds = :duration
                """,
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": ScraperStatus.FAILED.value,
                    ":completedAt": datetime.utcnow().isoformat(),
                    ":errorMessage": error_message,
                    ":duration": self._calculate_duration(run_id),
                },
                ReturnValues="ALL_NEW",
            )
            
            item = response["Attributes"]
            item["run_id"] = item.pop("runId", run_id)
            logger.error(f"Failed scraper run: {run_id} - {error_message}")
            return ScraperRun.from_dynamodb_item(item)
            
        except ClientError as e:
            logger.error(f"Failed to mark scraper run as failed: {e}")
            raise DatabaseError(f"Failed to mark scraper run as failed: {e}")

    @log_method
    async def get_run(self, run_id: str) -> ScraperRun:
        """Get a scraper run by ID."""
        try:
            response = self.table.get_item(Key={"runId": run_id})
            
            if "Item" not in response:
                raise DatabaseError(f"Scraper run not found: {run_id}")
            
            item = response["Item"]
            item["run_id"] = item.pop("runId", run_id)
            return ScraperRun.from_dynamodb_item(item)
            
        except ClientError as e:
            logger.error(f"Failed to get scraper run: {e}")
            raise DatabaseError(f"Failed to get scraper run: {e}")

    @log_method
    async def get_recent_runs(self, limit: int = 10) -> list[ScraperRun]:
        """Get recent scraper runs."""
        try:
            response = self.table.scan(
                IndexName="StatusIndex",
                Limit=limit,
                ScanIndexForward=False,
            )
            
            items = response.get("Items", [])
            runs = []
            
            for item in items:
                item["run_id"] = item.pop("runId", "")
                try:
                    runs.append(ScraperRun.from_dynamodb_item(item))
                except Exception as e:
                    logger.warning(f"Failed to parse scraper run: {e}")
            
            return sorted(
                runs,
                key=lambda r: r.started_at or datetime.min,
                reverse=True,
            )[:limit]
            
        except ClientError as e:
            logger.error(f"Failed to get recent scraper runs: {e}")
            raise DatabaseError(f"Failed to get recent scraper runs: {e}")

    @log_method
    async def add_run_error(
        self,
        run_id: str,
        source: str,
        error: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Add an error to a scraper run."""
        try:
            error_entry = {
                "source": source,
                "error": error,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details or {},
            }
            
            self.table.update_item(
                Key={"runId": run_id},
                UpdateExpression="""
                    SET errors = list_append(if_not_exists(errors, :emptyList), :error),
                        totalPropertiesFailed = if_not_exists(totalPropertiesFailed, :zero) + :inc
                """,
                ExpressionAttributeValues={
                    ":error": [error_entry],
                    ":emptyList": [],
                    ":zero": 0,
                    ":inc": 1,
                },
            )
            
        except ClientError as e:
            logger.error(f"Failed to add run error: {e}")

    @log_method
    async def save_raw_data(
        self,
        run_id: str,
        source: ScraperSource,
        data: list[dict[str, Any]],
    ) -> str:
        """Save raw scraped data to S3."""
        if not self.s3 or not self.bucket_name:
            logger.warning("S3 not configured, skipping raw data save")
            return ""
        
        try:
            key = f"raw/{run_id}/{source.value}/{datetime.utcnow().isoformat()}.json"
            
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(data, default=str),
                ContentType="application/json",
            )
            
            logger.info(f"Saved raw data to s3://{self.bucket_name}/{key}")
            return key
            
        except ClientError as e:
            logger.error(f"Failed to save raw data: {e}")
            return ""

    @log_method
    async def scrape_source(self, source: ScraperSource) -> ScraperResult:
        """Scrape a single source."""
        import asyncio
        start_time = datetime.utcnow()
        
        try:
            # This is a placeholder - actual scraping would be implemented here
            # For now, return an empty result
            logger.info(f"Scraping source: {source.value}")
            
            # Simulate scraping delay
            await asyncio.sleep(0.1)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return ScraperResult(
                success=True,
                source=source,
                properties=[],
                properties_count=0,
                new_count=0,
                updated_count=0,
                duration_seconds=duration,
            )
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Failed to scrape {source.value}: {e}")
            
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

    def _calculate_duration(self, run_id: str) -> float:
        """Calculate duration for a run."""
        try:
            response = self.table.get_item(Key={"runId": run_id})
            item = response.get("Item", {})
            
            started_at = item.get("startedAt")
            if started_at:
                start = datetime.fromisoformat(started_at)
                return (datetime.utcnow() - start).total_seconds()
        except Exception:
            pass
        return 0.0

    def _scraped_property_to_create(self, scraped: ScrapedProperty) -> PropertyCreate:
        """Convert a scraped property to PropertyCreate."""
        # Map property type string to enum
        property_type = PropertyType.APARTMENT
        type_lower = (scraped.property_type or "").lower()
        for pt in PropertyType:
            if pt.value in type_lower:
                property_type = pt
                break
        
        return PropertyCreate(
            external_id=scraped.external_id,
            source_url=scraped.source_url,
            source_name=scraped.source.value,
            title=scraped.title,
            description=scraped.description,
            property_type=property_type,
            status=PropertyStatus.FOR_SALE,
            price=__import__("decimal").Decimal(str(scraped.price)),
            location=None,  # Would parse from scraped.location
            town=scraped.location,
            bedrooms=scraped.bedrooms,
            bathrooms=scraped.bathrooms,
            internal_area_sqm=__import__("decimal").Decimal(str(scraped.area_sqm)) if scraped.area_sqm else None,
            features=scraped.features,
            images=scraped.images,
        )
