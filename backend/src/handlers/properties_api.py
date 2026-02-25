"""Properties API Lambda handler."""

import json
from typing import Any

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.models.property import PropertyFilter
from src.models.analysis import ROIInput
from src.services.property_service import PropertyService
from src.services.analysis_service import AnalysisService
from src.services.stats_service import StatsService
from src.utils.errors import PropertyAnalyzerError, ValidationError, NotFoundError
from src.utils.response import create_response, create_error_response
from src.utils.logger import log_handler

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()

# Initialize services
property_service = PropertyService()
analysis_service = AnalysisService()
stats_service = StatsService()


@app.get("/properties")
@tracer.capture_method
async def list_properties() -> dict[str, Any]:
    """List properties with filtering."""
    try:
        # Parse query parameters
        query_params = app.current_event.query_string_parameters or {}
        
        # Build filter from query params
        filter_data: dict[str, Any] = {}
        
        if "property_type" in query_params:
            filter_data["property_type"] = query_params["property_type"]
        if "min_price" in query_params:
            filter_data["min_price"] = float(query_params["min_price"])
        if "max_price" in query_params:
            filter_data["max_price"] = float(query_params["max_price"])
        if "location" in query_params:
            filter_data["location"] = query_params["location"]
        if "min_bedrooms" in query_params:
            filter_data["min_bedrooms"] = int(query_params["min_bedrooms"])
        if "max_bedrooms" in query_params:
            filter_data["max_bedrooms"] = int(query_params["max_bedrooms"])
        if "has_garage" in query_params:
            filter_data["has_garage"] = query_params["has_garage"].lower() == "true"
        if "has_garden" in query_params:
            filter_data["has_garden"] = query_params["has_garden"].lower() == "true"
        if "has_pool" in query_params:
            filter_data["has_pool"] = query_params["has_pool"].lower() == "true"
        if "min_roi_score" in query_params:
            filter_data["min_roi_score"] = float(query_params["min_roi_score"])
        if "sort_by" in query_params:
            filter_data["sort_by"] = query_params["sort_by"]
        if "sort_order" in query_params:
            filter_data["sort_order"] = query_params["sort_order"]
        if "page" in query_params:
            filter_data["page"] = int(query_params["page"])
        if "page_size" in query_params:
            filter_data["page_size"] = int(query_params["page_size"])
        
        filters = PropertyFilter(**filter_data)
        
        result = await property_service.list_properties(filters)
        
        return create_response(
            200,
            data={
                "items": [p.model_dump() for p in result.items],
                "total": result.total,
                "page": result.page,
                "page_size": result.page_size,
                "total_pages": result.total_pages,
                "has_next": result.has_next,
                "has_prev": result.has_prev,
            },
        )
        
    except ValidationError as e:
        return create_error_response(e)
    except Exception as e:
        logger.exception("Failed to list properties")
        return create_error_response(PropertyAnalyzerError(str(e)))


@app.get("/properties/<property_id>")
@tracer.capture_method
async def get_property(property_id: str) -> dict[str, Any]:
    """Get a single property by ID."""
    try:
        property_obj = await property_service.get_property(property_id)
        return create_response(200, data=property_obj.model_dump())
        
    except NotFoundError as e:
        return create_error_response(e)
    except Exception as e:
        logger.exception(f"Failed to get property: {property_id}")
        return create_error_response(PropertyAnalyzerError(str(e)))


@app.post("/properties/<property_id>/analyze")
@tracer.capture_method
async def trigger_analysis(property_id: str) -> dict[str, Any]:
    """Trigger ROI analysis for a property."""
    try:
        # Get the property
        property_obj = await property_service.get_property(property_id)
        
        # Parse request body
        body = app.current_event.json_body or {}
        
        # Create ROI input with defaults
        roi_input = ROIInput(
            property_id=property_id,
            strategy=body.get("strategy", "buy_to_let"),
            down_payment_percentage=body.get("down_payment_percentage", 0.20),
            interest_rate=body.get("interest_rate", 0.035),
            loan_term_years=body.get("loan_term_years", 25),
            monthly_rent=body.get("monthly_rent"),
            occupancy_rate=body.get("occupancy_rate", 0.90),
        )
        
        # Calculate ROI
        analysis = await analysis_service.calculate_roi(property_obj, roi_input)
        
        # Save analysis
        await analysis_service.save_analysis(analysis)
        
        # Update property ROI score
        if analysis.roi_score:
            await property_service.update_roi_score(property_id, analysis.roi_score)
        
        return create_response(
            200,
            data=analysis.model_dump(),
            message="Analysis completed successfully",
        )
        
    except NotFoundError as e:
        return create_error_response(e)
    except ValidationError as e:
        return create_error_response(e)
    except Exception as e:
        logger.exception(f"Failed to analyze property: {property_id}")
        return create_error_response(PropertyAnalyzerError(str(e)))


@app.get("/opportunities")
@tracer.capture_method
async def get_opportunities() -> dict[str, Any]:
    """Get top investment opportunities."""
    try:
        query_params = app.current_event.query_string_parameters or {}
        
        from src.models.analysis import OpportunityFilter
        
        filter_data: dict[str, Any] = {"limit": 20}
        
        if "min_roi_score" in query_params:
            filter_data["min_roi_score"] = float(query_params["min_roi_score"])
        if "limit" in query_params:
            filter_data["limit"] = int(query_params["limit"])
        if "strategy" in query_params:
            filter_data["strategy"] = query_params["strategy"]
        
        filters = OpportunityFilter(**filter_data)
        
        opportunities = await analysis_service.get_top_opportunities(filters)
        
        return create_response(200, data={"opportunities": opportunities})
        
    except Exception as e:
        logger.exception("Failed to get opportunities")
        return create_error_response(PropertyAnalyzerError(str(e)))


@app.get("/stats")
@tracer.capture_method
async def get_stats() -> dict[str, Any]:
    """Get market statistics."""
    try:
        query_params = app.current_event.query_string_parameters or {}
        location = query_params.get("location")
        
        if location:
            stats = await stats_service.get_location_statistics(location)
        else:
            stats = await stats_service.get_market_statistics()
        
        return create_response(200, data=stats)
        
    except Exception as e:
        logger.exception("Failed to get stats")
        return create_error_response(PropertyAnalyzerError(str(e)))


@app.exception_handler(PropertyAnalyzerError)
def handle_analyzer_error(ex: PropertyAnalyzerError) -> dict[str, Any]:
    """Handle custom analyzer errors."""
    return create_error_response(ex)


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@log_handler
def handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Lambda handler entry point."""
    return app.resolve(event, context)
