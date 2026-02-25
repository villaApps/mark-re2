"""ROI API Lambda handler."""

from typing import Any

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.models.analysis import ROIInput
from src.services.property_service import PropertyService
from src.services.analysis_service import AnalysisService
from src.utils.errors import PropertyAnalyzerError, NotFoundError, ValidationError
from src.utils.response import create_response, create_error_response
from src.utils.logger import log_handler

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()

# Initialize services
property_service = PropertyService()
analysis_service = AnalysisService()


@app.get("/properties/<property_id>/roi")
@tracer.capture_method
async def get_property_roi(property_id: str) -> dict[str, Any]:
    """Get ROI analysis for a property."""
    try:
        # Get the property
        property_obj = await property_service.get_property(property_id)
        
        # Get the latest analysis
        analysis = await analysis_service.get_latest_analysis(property_id)
        
        if not analysis:
            return create_response(
                404,
                error="No ROI analysis found for this property",
                message="Run analysis first using POST /properties/{id}/analyze",
            )
        
        return create_response(200, data={
            "property": property_obj.model_dump(),
            "analysis": analysis.model_dump(),
        })
        
    except NotFoundError as e:
        return create_error_response(e)
    except Exception as e:
        logger.exception(f"Failed to get ROI for property: {property_id}")
        return create_error_response(PropertyAnalyzerError(str(e)))


@app.post("/roi/calculate")
@tracer.capture_method
async def calculate_roi() -> dict[str, Any]:
    """Calculate ROI for a property without saving."""
    try:
        body = app.current_event.json_body or {}
        
        # Validate required fields
        if "property_id" not in body:
            raise ValidationError("property_id is required")
        
        property_id = body["property_id"]
        
        # Get the property
        property_obj = await property_service.get_property(property_id)
        
        # Create ROI input
        roi_input = ROIInput(
            property_id=property_id,
            strategy=body.get("strategy", "buy_to_let"),
            down_payment_percentage=body.get("down_payment_percentage", 0.20),
            interest_rate=body.get("interest_rate", 0.035),
            loan_term_years=body.get("loan_term_years", 25),
            closing_costs=body.get("closing_costs", 0.05),
            renovation_costs=body.get("renovation_costs", 0),
            monthly_rent=body.get("monthly_rent"),
            occupancy_rate=body.get("occupancy_rate", 0.90),
            annual_rent_increase=body.get("annual_rent_increase", 0.03),
            annual_appreciation_rate=body.get("annual_appreciation_rate", 0.03),
        )
        
        # Calculate ROI
        analysis = await analysis_service.calculate_roi(property_obj, roi_input)
        
        return create_response(
            200,
            data={
                "property_id": property_id,
                "analysis": analysis.model_dump(),
            },
            message="ROI calculation completed",
        )
        
    except NotFoundError as e:
        return create_error_response(e)
    except ValidationError as e:
        return create_error_response(e)
    except Exception as e:
        logger.exception("Failed to calculate ROI")
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
