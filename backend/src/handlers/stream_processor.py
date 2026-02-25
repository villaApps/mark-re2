"""DynamoDB Stream Processor Lambda handler."""

import asyncio
import json
import os
from decimal import Decimal
from typing import Any

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.models.analysis import InvestmentStrategy, ROIInput
from src.models.property import Property
from src.services.analysis_service import AnalysisService
from src.services.property_service import PropertyService
from src.utils.logger import log_handler

logger = Logger()
tracer = Tracer()

# Initialize services
analysis_service = AnalysisService()
property_service = PropertyService()

# EventBridge client
events_client = boto3.client("events")
event_bus_name = os.environ.get("EVENT_BUS_NAME", "property-events-dev")


async def process_new_property(property_data: dict[str, Any]) -> None:
    """Process a newly inserted property."""
    try:
        # Convert to Property model
        property_data["property_id"] = property_data.pop("propertyId", "")
        property_obj = Property.from_dynamodb_item(property_data)
        
        logger.info(f"Processing new property: {property_obj.property_id}")
        
        # Automatically trigger ROI analysis for new properties
        roi_input = ROIInput(
            property_id=property_obj.property_id,
            strategy=InvestmentStrategy.BUY_TO_LET,
        )
        
        analysis = await analysis_service.calculate_roi(property_obj, roi_input)
        await analysis_service.save_analysis(analysis)
        
        # Update property with ROI score
        if analysis.roi_score:
            await property_service.update_roi_score(
                property_obj.property_id,
                analysis.roi_score,
            )
        
        logger.info(f"Auto-analyzed new property: {property_obj.property_id}")
        
    except Exception as e:
        logger.exception(f"Failed to process new property: {e}")
        raise


async def process_price_change(
    old_image: dict[str, Any],
    new_image: dict[str, Any],
) -> None:
    """Process a price change in a property."""
    try:
        old_price = old_image.get("price", 0)
        new_price = new_image.get("price", 0)
        
        if old_price == new_price:
            return
        
        property_id = new_image.get("propertyId", "")
        price_change_pct = ((new_price - old_price) / old_price * 100) if old_price else 0
        
        logger.info(
            f"Price change detected for {property_id}: "
            f"{old_price} -> {new_price} ({price_change_pct:+.1f}%)"
        )
        
        # Re-analyze property with new price
        new_image["property_id"] = property_id
        property_obj = Property.from_dynamodb_item(new_image)
        
        roi_input = ROIInput(
            property_id=property_id,
            strategy=InvestmentStrategy.BUY_TO_LET,
        )
        
        analysis = await analysis_service.calculate_roi(property_obj, roi_input)
        await analysis_service.save_analysis(analysis)
        
        # Update property with new ROI score
        if analysis.roi_score:
            await property_service.update_roi_score(property_id, analysis.roi_score)
        
        # Publish price change event
        try:
            events_client.put_events(
                Entries=[
                    {
                        "Source": "malta.property.stream",
                        "DetailType": "PriceChange",
                        "Detail": json.dumps({
                            "propertyId": property_id,
                            "oldPrice": old_price,
                            "newPrice": new_price,
                            "changePercentage": float(price_change_pct),
                            "newRoiScore": float(analysis.roi_score) if analysis.roi_score else None,
                        }),
                        "EventBusName": event_bus_name,
                    }
                ]
            )
        except Exception as e:
            logger.warning(f"Failed to publish price change event: {e}")
        
    except Exception as e:
        logger.exception(f"Failed to process price change: {e}")
        raise


async def process_record(record: dict[str, Any]) -> None:
    """Process a single DynamoDB stream record."""
    event_name = record.get("eventName", "")
    
    if event_name == "INSERT":
        new_image = record.get("dynamodb", {}).get("NewImage", {})
        if new_image:
            # Convert DynamoDB format to plain dict
            new_image = _unmarshal_dynamodb_image(new_image)
            await process_new_property(new_image)
    
    elif event_name == "MODIFY":
        old_image = record.get("dynamodb", {}).get("OldImage", {})
        new_image = record.get("dynamodb", {}).get("NewImage", {})
        
        if old_image and new_image:
            old_image = _unmarshal_dynamodb_image(old_image)
            new_image = _unmarshal_dynamodb_image(new_image)
            
            # Check if price changed
            if old_image.get("price") != new_image.get("price"):
                await process_price_change(old_image, new_image)


def _unmarshal_dynamodb_image(image: dict[str, Any]) -> dict[str, Any]:
    """Convert DynamoDB stream image format to plain dict."""
    result = {}
    
    for key, value in image.items():
        if "S" in value:
            result[key] = value["S"]
        elif "N" in value:
            result[key] = float(value["N"])
        elif "BOOL" in value:
            result[key] = value["BOOL"]
        elif "NULL" in value:
            result[key] = None
        elif "L" in value:
            result[key] = [_unmarshal_dynamodb_value(v) for v in value["L"]]
        elif "M" in value:
            result[key] = _unmarshal_dynamodb_image(value["M"])
        else:
            result[key] = value
    
    return result


def _unmarshal_dynamodb_value(value: dict[str, Any]) -> Any:
    """Unmarshal a single DynamoDB value."""
    if "S" in value:
        return value["S"]
    elif "N" in value:
        return float(value["N"])
    elif "BOOL" in value:
        return value["BOOL"]
    elif "NULL" in value:
        return None
    elif "L" in value:
        return [_unmarshal_dynamodb_value(v) for v in value["L"]]
    elif "M" in value:
        return _unmarshal_dynamodb_image(value["M"])
    return value


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@log_handler
async def handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Lambda handler entry point for stream processor."""
    logger.info("Stream processor handler invoked", extra={
        "record_count": len(event.get("Records", [])),
    })
    
    records = event.get("Records", [])
    processed_count = 0
    error_count = 0
    
    for record in records:
        try:
            await process_record(record)
            processed_count += 1
        except Exception as e:
            logger.exception(f"Failed to process record: {e}")
            error_count += 1
    
    logger.info(
        f"Stream processing complete: {processed_count} processed, {error_count} errors"
    )
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "success": True,
            "processed_count": processed_count,
            "error_count": error_count,
        }),
    }


# Wrapper for synchronous Lambda invocation
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Synchronous entry point for Lambda."""
    return asyncio.run(handler(event, context))
