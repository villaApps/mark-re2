"""Analyzer Lambda handler - triggered by EventBridge after scraper completes."""

import asyncio
import json
import os
import sys
from decimal import Decimal
from typing import Any

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

# Add layer path for shared modules
sys.path.insert(0, "/opt/python")

# Import from analytics module (shared layer)
try:
    from analytics.src.calculators.roi_calculator import analyze_investment
    from analytics.src.calculators.rental_yield import calculate_gross_rental_yield
    from analytics.src.calculators.cash_flow import calculate_cash_flow
    from analytics.src.models.investment import InvestmentScenario
    from analytics.src.scoring.opportunity_scorer import score_opportunity
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    logger.warning("Analytics module not available in layer, using fallback implementation")

from src.models.analysis import InvestmentStrategy, ROIInput, ROIAnalysis
from src.models.property import PropertyFilter
from src.services.property_service import PropertyService
from src.services.analysis_service import AnalysisService
from src.utils.errors import PropertyAnalyzerError
from src.utils.logger import log_handler, LoggerContext
from src.utils.id_generator import generate_correlation_id

logger = Logger()
tracer = Tracer()

# Initialize services
property_service = PropertyService()
analysis_service = AnalysisService()

# EventBridge client
events_client = boto3.client("events")
event_bus_name = os.environ.get("EVENT_BUS_NAME", "property-events-dev")


def create_investment_scenario(property_obj: Any, monthly_rent: Decimal | None = None) -> Any:
    """Create an InvestmentScenario from a property object."""
    # Estimate monthly rent if not provided
    if monthly_rent is None:
        # Base calculation: 4.5% annual yield
        annual_yield = Decimal("0.045")
        estimated_annual_rent = property_obj.price * annual_yield
        monthly_rent = estimated_annual_rent / Decimal("12")

        # Adjust for location
        location_multiplier = Decimal("1.0")
        if property_obj.town:
            town_lower = property_obj.town.lower()
            multipliers = {
                "sliema": Decimal("1.3"),
                "st_julians": Decimal("1.25"),
                "valletta": Decimal("1.2"),
                "gzira": Decimal("1.15"),
                "msida": Decimal("1.1"),
            }
            for region, mult in multipliers.items():
                if region in town_lower:
                    location_multiplier = mult
                    break

        # Adjust for bedrooms
        bedroom_multiplier = Decimal("1.0")
        if property_obj.bedrooms:
            if property_obj.bedrooms >= 3:
                bedroom_multiplier = Decimal("1.2")
            elif property_obj.bedrooms == 1:
                bedroom_multiplier = Decimal("0.85")

        monthly_rent = monthly_rent * location_multiplier * bedroom_multiplier
        monthly_rent = max(monthly_rent, Decimal("500"))  # Minimum 500 EUR

    return InvestmentScenario(
        property_price=property_obj.price,
        property_area=property_obj.town,
        is_first_time_buyer=True,
        down_payment_percent=Decimal("0.20"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        monthly_rent=monthly_rent,
        vacancy_rate=Decimal("0.05"),
        property_management_percent=Decimal("0.10"),
        maintenance_reserve_percent=Decimal("0.05"),
        insurance_annual_percent=Decimal("0.003"),
        annual_appreciation=Decimal("0.03"),
        annual_rent_increase=Decimal("0.025"),
    )


async def analyze_single_property(
    property_obj: Any,
    use_analytics_module: bool = True,
) -> ROIAnalysis | None:
    """Analyze a single property using analytics module if available."""
    if not ANALYTICS_AVAILABLE or not use_analytics_module:
        # Fallback to service implementation
        roi_input = ROIInput(
            property_id=property_obj.property_id,
            strategy=InvestmentStrategy.BUY_TO_LET,
        )
        return await analysis_service.calculate_roi(property_obj, roi_input)

    try:
        # Create investment scenario from property
        scenario = create_investment_scenario(property_obj)

        # Use analytics module for complete analysis
        analysis_result, purchase_costs, cash_flow = analyze_investment(
            scenario,
            property_id=property_obj.property_id,
        )

        # Convert analytics result to backend ROIAnalysis model
        from datetime import datetime

        roi_analysis = ROIAnalysis(
            analysis_id=analysis_result.analysis_id if hasattr(analysis_result, "analysis_id") else f"anl_{property_obj.property_id}_{int(datetime.utcnow().timestamp())}",
            property_id=property_obj.property_id,
            strategy=InvestmentStrategy.BUY_TO_LET,
            purchase_price=property_obj.price,
            down_payment_percentage=Decimal("0.20"),
            interest_rate=Decimal("0.035"),
            loan_term_years=25,
            closing_costs=purchase_costs.total / property_obj.price if hasattr(purchase_costs, "total") else Decimal("0.05"),
            renovation_costs=Decimal("0"),
            rental_income={
                "monthly_rent": scenario.monthly_rent,
                "occupancy_rate": scenario.vacancy_rate,
                "annual_rent_increase": scenario.annual_rent_increase,
            },
            monthly_expenses={
                "mortgage_payment": cash_flow.monthly_mortgage_payment if hasattr(cash_flow, "monthly_mortgage_payment") else Decimal("0"),
                "property_tax": cash_flow.property_tax if hasattr(cash_flow, "property_tax") else Decimal("0"),
                "insurance": cash_flow.insurance if hasattr(cash_flow, "insurance") else Decimal("0"),
                "maintenance": cash_flow.maintenance if hasattr(cash_flow, "maintenance") else Decimal("0"),
                "management_fees": cash_flow.management_fees if hasattr(cash_flow, "management_fees") else Decimal("0"),
                "utilities": cash_flow.utilities if hasattr(cash_flow, "utilities") else Decimal("0"),
                "vacancy_reserve": cash_flow.vacancy_reserve if hasattr(cash_flow, "vacancy_reserve") else Decimal("0"),
            },
            annual_appreciation_rate=scenario.annual_appreciation,
        )

        # Set calculated fields
        roi_analysis.roi_score = analysis_result.opportunity_score if hasattr(analysis_result, "opportunity_score") else None
        roi_analysis.roi_percentage = analysis_result.cash_on_cash_return * 100 if hasattr(analysis_result, "cash_on_cash_return") else None
        roi_analysis.gross_rental_yield = analysis_result.gross_rental_yield * 100 if hasattr(analysis_result, "gross_rental_yield") else None
        roi_analysis.net_rental_yield = analysis_result.net_rental_yield * 100 if hasattr(analysis_result, "net_rental_yield") else None
        roi_analysis.cap_rate = analysis_result.cap_rate * 100 if hasattr(analysis_result, "cap_rate") else None

        return roi_analysis

    except Exception as e:
        logger.warning(f"Analytics module failed for {property_obj.property_id}: {e}")
        # Fallback to service implementation
        roi_input = ROIInput(
            property_id=property_obj.property_id,
            strategy=InvestmentStrategy.BUY_TO_LET,
        )
        return await analysis_service.calculate_roi(property_obj, roi_input)


async def analyze_properties_without_roi(limit: int = 100) -> dict[str, Any]:
    """Analyze properties that don't have ROI calculations yet."""
    # Get properties without ROI scores
    filters = PropertyFilter(
        min_roi_score=Decimal("0"),
        page=1,
        page_size=limit,
    )

    result = await property_service.list_properties(filters)

    analyzed_count = 0
    errors = []

    for property_obj in result.items:
        try:
            # Skip if already has ROI
            if property_obj.roi_score and property_obj.roi_score > 0:
                continue

            # Analyze property using analytics module
            analysis = await analyze_single_property(property_obj)

            if analysis:
                # Save analysis
                await analysis_service.save_analysis(analysis)

                # Update property ROI score
                if analysis.roi_score:
                    await property_service.update_roi_score(
                        property_obj.property_id,
                        analysis.roi_score,
                    )

                analyzed_count += 1

        except Exception as e:
            logger.warning(f"Failed to analyze property {property_obj.property_id}: {e}")
            errors.append({
                "property_id": property_obj.property_id,
                "error": str(e),
            })

    return {
        "analyzed_count": analyzed_count,
        "errors": errors,
    }


async def reanalyze_top_properties(limit: int = 50) -> dict[str, Any]:
    """Re-analyze top properties with latest market data."""
    # Get top properties by current ROI score
    filters = PropertyFilter(
        min_roi_score=Decimal("50"),
        sort_by="roi_score",
        sort_order="desc",
        page=1,
        page_size=limit,
    )

    result = await property_service.list_properties(filters)

    reanalyzed_count = 0
    errors = []

    for property_obj in result.items:
        try:
            # Re-analyze property using analytics module
            analysis = await analyze_single_property(property_obj)

            if analysis:
                # Save analysis
                await analysis_service.save_analysis(analysis)

                # Update property ROI score
                if analysis.roi_score:
                    await property_service.update_roi_score(
                        property_obj.property_id,
                        analysis.roi_score,
                    )

                reanalyzed_count += 1

        except Exception as e:
            logger.warning(f"Failed to reanalyze property {property_obj.property_id}: {e}")
            errors.append({
                "property_id": property_obj.property_id,
                "error": str(e),
            })

    return {
        "reanalyzed_count": reanalyzed_count,
        "errors": errors,
    }


async def publish_analysis_complete_event(
    analyzed_count: int,
    reanalyzed_count: int,
) -> None:
    """Publish EventBridge event when analysis completes."""
    try:
        event_detail = {
            "analyzedCount": analyzed_count,
            "reanalyzedCount": reanalyzed_count,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }
        
        events_client.put_events(
            Entries=[
                {
                    "Source": "malta.property.analyzer",
                    "DetailType": "AnalysisComplete",
                    "Detail": json.dumps(event_detail),
                    "EventBusName": event_bus_name,
                }
            ]
        )
        
        logger.info("Published AnalysisComplete event")
        
    except Exception as e:
        logger.exception("Failed to publish AnalysisComplete event")


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@log_handler
async def handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Lambda handler entry point for analyzer."""
    correlation_id = generate_correlation_id()
    
    with LoggerContext("analyzer", correlation_id=correlation_id):
        logger.info("Analyzer handler invoked", extra={"event": event})
        
        try:
            # Analyze properties without ROI
            new_results = await analyze_properties_without_roi(limit=100)
            
            # Re-analyze top properties
            reanalyze_results = await reanalyze_top_properties(limit=50)
            
            # Publish completion event
            await publish_analysis_complete_event(
                new_results["analyzed_count"],
                reanalyze_results["reanalyzed_count"],
            )
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "success": True,
                    "newlyAnalyzed": new_results["analyzed_count"],
                    "reanalyzed": reanalyze_results["reanalyzed_count"],
                    "totalErrors": len(new_results["errors"]) + len(reanalyze_results["errors"]),
                }),
            }
            
        except Exception as e:
            logger.exception("Analyzer failed")
            
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "success": False,
                    "error": str(e),
                }),
            }


# Wrapper for synchronous Lambda invocation
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Synchronous entry point for Lambda."""
    return asyncio.run(handler(event, context))
