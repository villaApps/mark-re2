"""Property service for CRUD operations."""

import os
from decimal import Decimal
from typing import Any

import boto3
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

from src.models.property import Property, PropertyCreate, PropertyFilter, PropertyUpdate
from src.models.common import PaginatedResponse
from src.utils.errors import DatabaseError, NotFoundError, ValidationError
from src.utils.id_generator import generate_property_id
from src.utils.logger import log_method

logger = Logger(child=True)


class PropertyService:
    """Service for property operations."""

    def __init__(self, table_name: str | None = None):
        self.table_name = table_name or os.environ.get("PROPERTIES_TABLE", "properties-dev")
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.table_name)

    @log_method
    async def get_property(self, property_id: str) -> Property:
        """Get a property by ID."""
        try:
            response = self.table.get_item(Key={"propertyId": property_id})
            
            if "Item" not in response:
                raise NotFoundError("Property", property_id)
            
            item = response["Item"]
            # Convert DynamoDB format to model format
            item["property_id"] = item.pop("propertyId", property_id)
            return Property.from_dynamodb_item(item)
            
        except NotFoundError:
            raise
        except ClientError as e:
            logger.error(f"Failed to get property: {e}")
            raise DatabaseError(f"Failed to get property: {e}")

    @log_method
    async def list_properties(
        self,
        filters: PropertyFilter | None = None,
    ) -> PaginatedResponse[Property]:
        """List properties with optional filtering."""
        filters = filters or PropertyFilter()
        
        try:
            # Build scan filter expression
            filter_expression = None
            
            if filters.status:
                filter_expression = Attr("status").eq(filters.status.value)
            
            if filters.property_type:
                expr = Attr("propertyType").eq(filters.property_type.value)
                filter_expression = expr if filter_expression is None else filter_expression & expr
            
            if filters.min_price is not None:
                expr = Attr("price").gte(float(filters.min_price))
                filter_expression = expr if filter_expression is None else filter_expression & expr
            
            if filters.max_price is not None:
                expr = Attr("price").lte(float(filters.max_price))
                filter_expression = expr if filter_expression is None else filter_expression & expr
            
            if filters.location:
                expr = Attr("town").contains(filters.location) | Attr("region").contains(filters.location)
                filter_expression = expr if filter_expression is None else filter_expression & expr
            
            if filters.min_bedrooms is not None:
                expr = Attr("bedrooms").gte(filters.min_bedrooms)
                filter_expression = expr if filter_expression is None else filter_expression & expr
            
            if filters.max_bedrooms is not None:
                expr = Attr("bedrooms").lte(filters.max_bedrooms)
                filter_expression = expr if filter_expression is None else filter_expression & expr
            
            if filters.min_bathrooms is not None:
                expr = Attr("bathrooms").gte(filters.min_bathrooms)
                filter_expression = expr if filter_expression is None else filter_expression & expr
            
            if filters.has_garage is not None:
                expr = Attr("hasGarage").eq(filters.has_garage)
                filter_expression = expr if filter_expression is None else filter_expression & expr
            
            if filters.has_garden is not None:
                expr = Attr("hasGarden").eq(filters.has_garden)
                filter_expression = expr if filter_expression is None else filter_expression & expr
            
            if filters.has_pool is not None:
                expr = Attr("hasPool").eq(filters.has_pool)
                filter_expression = expr if filter_expression is None else filter_expression & expr
            
            if filters.min_roi_score is not None:
                expr = Attr("roiScore").gte(float(filters.min_roi_score))
                filter_expression = expr if filter_expression is None else filter_expression & expr
            
            # Execute scan
            scan_kwargs: dict[str, Any] = {}
            if filter_expression:
                scan_kwargs["FilterExpression"] = filter_expression
            
            response = self.table.scan(**scan_kwargs)
            items = response.get("Items", [])
            
            # Convert to Property objects
            properties = []
            for item in items:
                item["property_id"] = item.pop("propertyId", "")
                try:
                    properties.append(Property.from_dynamodb_item(item))
                except Exception as e:
                    logger.warning(f"Failed to parse property: {e}")
            
            # Sort results
            sort_key = filters.sort_by
            reverse = filters.sort_order == "desc"
            
            if sort_key == "price":
                properties.sort(key=lambda p: p.price if p.price else Decimal("0"), reverse=reverse)
            elif sort_key == "roi_score":
                properties.sort(key=lambda p: p.roi_score if p.roi_score else Decimal("0"), reverse=reverse)
            elif sort_key == "price_per_sqm":
                properties.sort(key=lambda p: p.price_per_sqm if p.price_per_sqm else Decimal("0"), reverse=reverse)
            else:  # created_at
                properties.sort(key=lambda p: p.created_at, reverse=reverse)
            
            # Paginate
            total = len(properties)
            start_idx = (filters.page - 1) * filters.page_size
            end_idx = start_idx + filters.page_size
            paginated_properties = properties[start_idx:end_idx]
            
            return PaginatedResponse.create(
                items=paginated_properties,
                total=total,
                page=filters.page,
                page_size=filters.page_size,
            )
            
        except ClientError as e:
            logger.error(f"Failed to list properties: {e}")
            raise DatabaseError(f"Failed to list properties: {e}")

    @log_method
    async def create_property(self, data: PropertyCreate) -> Property:
        """Create a new property."""
        try:
            # Generate property ID
            property_id = generate_property_id(data.external_id, data.source_name)
            
            # Check if property already exists
            try:
                existing = await self.get_property(property_id)
                if existing:
                    logger.info(f"Property {property_id} already exists, updating")
                    return await self.update_property(property_id, data.model_dump())
            except NotFoundError:
                pass
            
            # Create property
            property_data = data.model_dump()
            property_data["property_id"] = property_id
            
            property_obj = Property(**property_data)
            
            # Save to DynamoDB
            item = property_obj.to_dynamodb_item()
            # Convert to DynamoDB format
            dynamo_item = {
                "propertyId": item.pop("property_id"),
                **{self._to_dynamo_key(k): v for k, v in item.items() if v is not None},
            }
            
            self.table.put_item(Item=dynamo_item)
            
            logger.info(f"Created property: {property_id}")
            return property_obj
            
        except ClientError as e:
            logger.error(f"Failed to create property: {e}")
            raise DatabaseError(f"Failed to create property: {e}")

    @log_method
    async def update_property(
        self,
        property_id: str,
        data: dict[str, Any],
    ) -> Property:
        """Update an existing property."""
        try:
            # Check if property exists
            existing = await self.get_property(property_id)
            if not existing:
                raise NotFoundError("Property", property_id)
            
            # Build update expression
            update_parts = []
            expression_values = {}
            expression_names = {}
            
            for key, value in data.items():
                if value is not None:
                    dynamo_key = self._to_dynamo_key(key)
                    update_parts.append(f"#{key} = :{key}")
                    expression_names[f"#{key}"] = dynamo_key
                    expression_values[f":{key}"] = value
            
            if not update_parts:
                return existing
            
            update_expression = "SET " + ", ".join(update_parts) + ", #updatedAt = :updatedAt"
            expression_names["#updatedAt"] = "updatedAt"
            expression_values[":updatedAt"] = __import__("datetime").datetime.utcnow().isoformat()
            
            response = self.table.update_item(
                Key={"propertyId": property_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_values,
                ReturnValues="ALL_NEW",
            )
            
            item = response["Attributes"]
            item["property_id"] = item.pop("propertyId", property_id)
            
            logger.info(f"Updated property: {property_id}")
            return Property.from_dynamodb_item(item)
            
        except NotFoundError:
            raise
        except ClientError as e:
            logger.error(f"Failed to update property: {e}")
            raise DatabaseError(f"Failed to update property: {e}")

    @log_method
    async def delete_property(self, property_id: str) -> None:
        """Delete a property."""
        try:
            self.table.delete_item(Key={"propertyId": property_id})
            logger.info(f"Deleted property: {property_id}")
        except ClientError as e:
            logger.error(f"Failed to delete property: {e}")
            raise DatabaseError(f"Failed to delete property: {e}")

    @log_method
    async def get_properties_by_location(
        self,
        location: str,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[Property]:
        """Get properties by location using GSI."""
        try:
            response = self.table.query(
                IndexName="LocationIndex",
                KeyConditionExpression=Key("location").eq(location),
                ScanIndexForward=False,  # Most recent first
            )
            
            items = response.get("Items", [])
            properties = []
            
            for item in items:
                item["property_id"] = item.pop("propertyId", "")
                try:
                    properties.append(Property.from_dynamodb_item(item))
                except Exception as e:
                    logger.warning(f"Failed to parse property: {e}")
            
            total = len(properties)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            return PaginatedResponse.create(
                items=properties[start_idx:end_idx],
                total=total,
                page=page,
                page_size=page_size,
            )
            
        except ClientError as e:
            logger.error(f"Failed to get properties by location: {e}")
            raise DatabaseError(f"Failed to get properties by location: {e}")

    @log_method
    async def update_roi_score(self, property_id: str, roi_score: Decimal) -> None:
        """Update the ROI score for a property."""
        try:
            self.table.update_item(
                Key={"propertyId": property_id},
                UpdateExpression="SET roiScore = :roiScore, analysisCount = if_not_exists(analysisCount, :zero) + :inc, updatedAt = :updatedAt",
                ExpressionAttributeValues={
                    ":roiScore": float(roi_score),
                    ":zero": 0,
                    ":inc": 1,
                    ":updatedAt": __import__("datetime").datetime.utcnow().isoformat(),
                },
            )
            logger.info(f"Updated ROI score for property: {property_id}")
        except ClientError as e:
            logger.error(f"Failed to update ROI score: {e}")
            raise DatabaseError(f"Failed to update ROI score: {e}")

    def _to_dynamo_key(self, key: str) -> str:
        """Convert snake_case to DynamoDB camelCase."""
        # Simple mapping for common fields
        mapping = {
            "property_id": "propertyId",
            "external_id": "externalId",
            "source_url": "sourceUrl",
            "source_name": "sourceName",
            "property_type": "propertyType",
            "price_per_sqm": "pricePerSqm",
            "price_range": "priceRange",
            "original_price": "originalPrice",
            "total_rooms": "totalRooms",
            "internal_area_sqm": "internalAreaSqm",
            "external_area_sqm": "externalAreaSqm",
            "total_area_sqm": "totalAreaSqm",
            "floor_number": "floorNumber",
            "total_floors": "totalFloors",
            "year_built": "yearBuilt",
            "has_garage": "hasGarage",
            "has_garden": "hasGarden",
            "has_pool": "hasPool",
            "has_elevator": "hasElevator",
            "is_furnished": "isFurnished",
            "has_air_conditioning": "hasAirConditioning",
            "has_heating": "hasHeating",
            "floor_plans": "floorPlans",
            "virtual_tour_url": "virtualTourUrl",
            "created_at": "createdAt",
            "updated_at": "updatedAt",
            "scraped_at": "scrapedAt",
            "is_active": "isActive",
            "view_count": "viewCount",
            "roi_score": "roiScore",
            "analysis_count": "analysisCount",
        }
        return mapping.get(key, key)
