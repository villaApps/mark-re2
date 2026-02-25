"""Statistics service for market data aggregation."""

import os
from decimal import Decimal
from typing import Any

import boto3
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from src.utils.errors import DatabaseError
from src.utils.logger import log_method

logger = Logger(child=True)


class StatsService:
    """Service for market statistics and aggregations."""

    def __init__(self, table_name: str | None = None):
        self.table_name = table_name or os.environ.get("PROPERTIES_TABLE", "properties-dev")
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.table_name)

    @log_method
    async def get_market_statistics(self) -> dict[str, Any]:
        """Get overall market statistics."""
        try:
            # Scan all active properties
            response = self.table.scan(
                FilterExpression=Attr("isActive").eq(True)
            )
            items = response.get("Items", [])
            
            # Handle pagination
            while "LastEvaluatedKey" in response:
                response = self.table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                    FilterExpression=Attr("isActive").eq(True)
                )
                items.extend(response.get("Items", []))
            
            if not items:
                return self._empty_stats()
            
            # Calculate statistics
            prices = [item.get("price", 0) for item in items if item.get("price")]
            prices_per_sqm = [item.get("pricePerSqm", 0) for item in items if item.get("pricePerSqm")]
            bedrooms = [item.get("bedrooms", 0) for item in items if item.get("bedrooms")]
            areas = [item.get("totalAreaSqm", 0) for item in items if item.get("totalAreaSqm")]
            roi_scores = [item.get("roiScore", 0) for item in items if item.get("roiScore")]
            
            # Property type distribution
            property_types: dict[str, int] = {}
            for item in items:
                pt = item.get("propertyType", "unknown")
                property_types[pt] = property_types.get(pt, 0) + 1
            
            # Location distribution (top 10)
            locations: dict[str, int] = {}
            for item in items:
                town = item.get("town") or item.get("region") or "Unknown"
                locations[town] = locations.get(town, 0) + 1
            
            top_locations = dict(
                sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]
            )
            
            # Price range distribution
            price_ranges = {
                "under_100k": 0,
                "100k_200k": 0,
                "200k_300k": 0,
                "300k_500k": 0,
                "500k_750k": 0,
                "750k_1m": 0,
                "over_1m": 0,
            }
            for price in prices:
                if price < 100000:
                    price_ranges["under_100k"] += 1
                elif price < 200000:
                    price_ranges["100k_200k"] += 1
                elif price < 300000:
                    price_ranges["200k_300k"] += 1
                elif price < 500000:
                    price_ranges["300k_500k"] += 1
                elif price < 750000:
                    price_ranges["500k_750k"] += 1
                elif price < 1000000:
                    price_ranges["750k_1m"] += 1
                else:
                    price_ranges["over_1m"] += 1
            
            return {
                "total_properties": len(items),
                "price_statistics": {
                    "average": round(sum(prices) / len(prices), 2) if prices else 0,
                    "median": round(self._median(prices), 2) if prices else 0,
                    "min": round(min(prices), 2) if prices else 0,
                    "max": round(max(prices), 2) if prices else 0,
                },
                "price_per_sqm_statistics": {
                    "average": round(sum(prices_per_sqm) / len(prices_per_sqm), 2) if prices_per_sqm else 0,
                    "median": round(self._median(prices_per_sqm), 2) if prices_per_sqm else 0,
                    "min": round(min(prices_per_sqm), 2) if prices_per_sqm else 0,
                    "max": round(max(prices_per_sqm), 2) if prices_per_sqm else 0,
                },
                "area_statistics": {
                    "average": round(sum(areas) / len(areas), 2) if areas else 0,
                    "median": round(self._median(areas), 2) if areas else 0,
                },
                "bedroom_statistics": {
                    "average": round(sum(bedrooms) / len(bedrooms), 1) if bedrooms else 0,
                    "distribution": self._distribution(bedrooms) if bedrooms else {},
                },
                "roi_statistics": {
                    "average": round(sum(roi_scores) / len(roi_scores), 2) if roi_scores else 0,
                    "median": round(self._median(roi_scores), 2) if roi_scores else 0,
                    "properties_with_roi": len(roi_scores),
                    "high_roi_properties": len([s for s in roi_scores if s >= 70]),
                },
                "property_type_distribution": property_types,
                "top_locations": top_locations,
                "price_range_distribution": price_ranges,
                "generated_at": __import__("datetime").datetime.utcnow().isoformat(),
            }
            
        except ClientError as e:
            logger.error(f"Failed to get market statistics: {e}")
            raise DatabaseError(f"Failed to get market statistics: {e}")

    @log_method
    async def get_location_statistics(self, location: str) -> dict[str, Any]:
        """Get statistics for a specific location."""
        try:
            # Query by location using GSI
            response = self.table.query(
                IndexName="LocationIndex",
                KeyConditionExpression="location = :location",
                ExpressionAttributeValues={":location": location},
                FilterExpression=Attr("isActive").eq(True),
            )
            
            items = response.get("Items", [])
            
            if not items:
                return {
                    "location": location,
                    "total_properties": 0,
                    "message": "No properties found for this location",
                }
            
            prices = [item.get("price", 0) for item in items if item.get("price")]
            prices_per_sqm = [item.get("pricePerSqm", 0) for item in items if item.get("pricePerSqm")]
            
            property_types: dict[str, int] = {}
            for item in items:
                pt = item.get("propertyType", "unknown")
                property_types[pt] = property_types.get(pt, 0) + 1
            
            return {
                "location": location,
                "total_properties": len(items),
                "price_statistics": {
                    "average": round(sum(prices) / len(prices), 2) if prices else 0,
                    "median": round(self._median(prices), 2) if prices else 0,
                    "min": round(min(prices), 2) if prices else 0,
                    "max": round(max(prices), 2) if prices else 0,
                },
                "price_per_sqm_statistics": {
                    "average": round(sum(prices_per_sqm) / len(prices_per_sqm), 2) if prices_per_sqm else 0,
                    "median": round(self._median(prices_per_sqm), 2) if prices_per_sqm else 0,
                },
                "property_type_distribution": property_types,
                "generated_at": __import__("datetime").datetime.utcnow().isoformat(),
            }
            
        except ClientError as e:
            logger.error(f"Failed to get location statistics: {e}")
            raise DatabaseError(f"Failed to get location statistics: {e}")

    @log_method
    async def get_price_trends(self, days: int = 30) -> dict[str, Any]:
        """Get price trends over time."""
        # This would typically query historical data
        # For now, return a placeholder
        return {
            "period_days": days,
            "trend": "stable",
            "price_change_percentage": 0.0,
            "message": "Price trends feature coming soon",
        }

    def _empty_stats(self) -> dict[str, Any]:
        """Return empty statistics structure."""
        return {
            "total_properties": 0,
            "price_statistics": {},
            "price_per_sqm_statistics": {},
            "area_statistics": {},
            "bedroom_statistics": {},
            "roi_statistics": {},
            "property_type_distribution": {},
            "top_locations": {},
            "price_range_distribution": {},
            "generated_at": __import__("datetime").datetime.utcnow().isoformat(),
        }

    def _median(self, values: list[float]) -> float:
        """Calculate median of a list of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        return sorted_values[n // 2]

    def _distribution(self, values: list[int]) -> dict[str, int]:
        """Calculate distribution of values."""
        dist: dict[str, int] = {}
        for v in values:
            key = str(v)
            dist[key] = dist.get(key, 0) + 1
        return dist
