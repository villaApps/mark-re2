"""ROI Analysis service for investment calculations."""

import os
from decimal import Decimal
from typing import Any

import boto3
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from src.models.analysis import (
    InvestmentStrategy,
    MonthlyExpenses,
    RentalIncome,
    ROIAnalysis,
    ROIInput,
    OpportunityFilter,
)
from src.models.property import Property
from src.utils.errors import DatabaseError, NotFoundError, ValidationError
from src.utils.id_generator import generate_analysis_id
from src.utils.logger import log_method

logger = Logger(child=True)

# Market data for Malta (approximate averages)
MALTA_MARKET_DATA = {
    "average_rental_yield": Decimal("4.5"),  # 4.5% average
    "average_price_per_sqm": Decimal("3500"),  # EUR per sqm
    "typical_occupancy_rate": Decimal("0.90"),
    "average_annual_appreciation": Decimal("0.03"),  # 3%
    "management_fee_rate": Decimal("0.10"),  # 10% of rent
    "maintenance_rate": Decimal("0.01"),  # 1% of property value annually
    "vacancy_reserve_months": Decimal("0.5"),  # Half month reserve
    "regional_rent_multipliers": {
        "sliema": Decimal("1.3"),
        "st_julians": Decimal("1.25"),
        "valletta": Decimal("1.2"),
        "gzira": Decimal("1.15"),
        "msida": Decimal("1.1"),
        "birkirkara": Decimal("1.0"),
        "mosta": Decimal("0.95"),
        "qormi": Decimal("0.90"),
        "zabbar": Decimal("0.85"),
    },
}


class AnalysisService:
    """Service for ROI analysis operations."""

    def __init__(self, table_name: str | None = None):
        self.table_name = table_name or os.environ.get("ANALYSIS_TABLE", "analysis-dev")
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.table_name)

    @log_method
    async def calculate_roi(self, property_obj: Property, inputs: ROIInput) -> ROIAnalysis:
        """Calculate ROI for a property."""
        # Validate inputs
        if inputs.monthly_rent is None:
            inputs.monthly_rent = await self._estimate_monthly_rent(property_obj)
        
        # Create rental income model
        rental_income = RentalIncome(
            monthly_rent=inputs.monthly_rent,
            occupancy_rate=inputs.occupancy_rate,
            annual_rent_increase=inputs.annual_rent_increase,
        )
        
        # Calculate monthly expenses if not provided
        if not inputs.monthly_expenses or inputs.monthly_expenses.total == 0:
            inputs.monthly_expenses = await self._estimate_expenses(
                property_obj, inputs, rental_income
            )
        
        # Create analysis
        analysis = ROIAnalysis(
            analysis_id=generate_analysis_id(property_obj.property_id),
            property_id=property_obj.property_id,
            strategy=inputs.strategy,
            purchase_price=property_obj.price,
            down_payment_percentage=inputs.down_payment_percentage,
            interest_rate=inputs.interest_rate,
            loan_term_years=inputs.loan_term_years,
            closing_costs=inputs.closing_costs,
            renovation_costs=inputs.renovation_costs,
            rental_income=rental_income,
            monthly_expenses=inputs.monthly_expenses,
            annual_appreciation_rate=inputs.annual_appreciation_rate,
        )
        
        return analysis

    @log_method
    async def save_analysis(self, analysis: ROIAnalysis) -> ROIAnalysis:
        """Save an analysis to DynamoDB."""
        try:
            item = analysis.to_dynamodb_item()
            dynamo_item = {
                "analysisId": item.pop("analysis_id"),
                **{self._to_dynamo_key(k): v for k, v in item.items() if v is not None},
            }
            
            self.table.put_item(Item=dynamo_item)
            logger.info(f"Saved analysis: {analysis.analysis_id}")
            return analysis
            
        except ClientError as e:
            logger.error(f"Failed to save analysis: {e}")
            raise DatabaseError(f"Failed to save analysis: {e}")

    @log_method
    async def get_analysis(self, analysis_id: str) -> ROIAnalysis:
        """Get an analysis by ID."""
        try:
            response = self.table.get_item(Key={"analysisId": analysis_id})
            
            if "Item" not in response:
                raise NotFoundError("Analysis", analysis_id)
            
            item = response["Item"]
            item["analysis_id"] = item.pop("analysisId", analysis_id)
            return ROIAnalysis.from_dynamodb_item(item)
            
        except NotFoundError:
            raise
        except ClientError as e:
            logger.error(f"Failed to get analysis: {e}")
            raise DatabaseError(f"Failed to get analysis: {e}")

    @log_method
    async def get_analyses_for_property(
        self,
        property_id: str,
        limit: int = 10,
    ) -> list[ROIAnalysis]:
        """Get all analyses for a property."""
        try:
            response = self.table.query(
                IndexName="PropertyIndex",
                KeyConditionExpression=Key("propertyId").eq(property_id),
                ScanIndexForward=False,  # Most recent first
                Limit=limit,
            )
            
            items = response.get("Items", [])
            analyses = []
            
            for item in items:
                item["analysis_id"] = item.pop("analysisId", "")
                item["property_id"] = property_id
                try:
                    analyses.append(ROIAnalysis.from_dynamodb_item(item))
                except Exception as e:
                    logger.warning(f"Failed to parse analysis: {e}")
            
            return analyses
            
        except ClientError as e:
            logger.error(f"Failed to get analyses for property: {e}")
            raise DatabaseError(f"Failed to get analyses for property: {e}")

    @log_method
    async def get_latest_analysis(self, property_id: str) -> ROIAnalysis | None:
        """Get the latest analysis for a property."""
        analyses = await self.get_analyses_for_property(property_id, limit=1)
        return analyses[0] if analyses else None

    @log_method
    async def get_top_opportunities(
        self,
        filters: OpportunityFilter | None = None,
    ) -> list[dict[str, Any]]:
        """Get top investment opportunities."""
        filters = filters or OpportunityFilter()
        
        try:
            # Query by ROI score using GSI
            scan_kwargs: dict[str, Any] = {
                "IndexName": "ROIScoreIndex",
                "ScanIndexForward": False,  # Highest scores first
                "Limit": filters.limit,
            }
            
            response = self.table.scan(**scan_kwargs)
            items = response.get("Items", [])
            
            opportunities = []
            for item in items:
                try:
                    item["analysis_id"] = item.pop("analysisId", "")
                    analysis = ROIAnalysis.from_dynamodb_item(item)
                    
                    # Apply filters
                    if filters.min_roi_score and analysis.roi_score:
                        if analysis.roi_score < filters.min_roi_score:
                            continue
                    
                    if filters.max_risk_level and analysis.risk_level:
                        if analysis.risk_level.value > filters.max_risk_level.value:
                            continue
                    
                    if filters.strategy and analysis.strategy != filters.strategy:
                        continue
                    
                    opportunities.append({
                        "analysis_id": analysis.analysis_id,
                        "property_id": analysis.property_id,
                        "roi_score": analysis.roi_score,
                        "roi_percentage": analysis.roi_percentage,
                        "risk_level": analysis.risk_level.value if analysis.risk_level else None,
                        "strategy": analysis.strategy.value,
                        "recommendation": analysis.recommendation,
                        "monthly_cash_flow": analysis.cash_flow.monthly_cash_flow if analysis.cash_flow else None,
                        "gross_rental_yield": analysis.gross_rental_yield,
                        "created_at": analysis.created_at.isoformat(),
                    })
                except Exception as e:
                    logger.warning(f"Failed to parse opportunity: {e}")
            
            return opportunities[:filters.limit]
            
        except ClientError as e:
            logger.error(f"Failed to get top opportunities: {e}")
            raise DatabaseError(f"Failed to get top opportunities: {e}")

    @log_method
    async def _estimate_monthly_rent(self, property: Property) -> Decimal:
        """Estimate monthly rent for a property."""
        # Base calculation on price and typical yield
        annual_yield = MALTA_MARKET_DATA["average_rental_yield"] / 100
        estimated_annual_rent = property.price * annual_yield
        estimated_monthly_rent = estimated_annual_rent / 12
        
        # Adjust for location
        location_multiplier = Decimal("1.0")
        if property.town:
            town_lower = property.town.lower()
            for region, multiplier in MALTA_MARKET_DATA["regional_rent_multipliers"].items():
                if region in town_lower:
                    location_multiplier = multiplier
                    break
        
        # Adjust for property characteristics
        bedroom_multiplier = Decimal("1.0")
        if property.bedrooms:
            if property.bedrooms >= 3:
                bedroom_multiplier = Decimal("1.2")
            elif property.bedrooms == 1:
                bedroom_multiplier = Decimal("0.85")
        
        area_multiplier = Decimal("1.0")
        if property.total_area_sqm:
            avg_area = Decimal("120")  # Average apartment size
            area_ratio = property.total_area_sqm / avg_area
            area_multiplier = Decimal("0.8") + (Decimal("0.2") * min(area_ratio, Decimal("2")))
        
        adjusted_rent = (
            estimated_monthly_rent *
            location_multiplier *
            bedroom_multiplier *
            area_multiplier
        )
        
        return max(adjusted_rent, Decimal("500"))  # Minimum 500 EUR

    @log_method
    async def _estimate_expenses(
        self,
        property: Property,
        inputs: ROIInput,
        rental_income: RentalIncome,
    ) -> MonthlyExpenses:
        """Estimate monthly expenses for a property."""
        # Calculate mortgage payment
        loan_amount = property.price * (1 - inputs.down_payment_percentage)
        monthly_rate = inputs.interest_rate / 12
        num_payments = inputs.loan_term_years * 12
        
        if monthly_rate > 0:
            mortgage_payment = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** num_payments
            ) / ((1 + monthly_rate) ** num_payments - 1)
        else:
            mortgage_payment = loan_amount / num_payments
        
        # Property tax (approximate for Malta)
        property_tax = property.price * Decimal("0.001") / 12  # ~0.1% annually
        
        # Insurance
        insurance = property.price * Decimal("0.002") / 12  # ~0.2% annually
        
        # Maintenance (1% of property value annually)
        maintenance = property.price * MALTA_MARKET_DATA["maintenance_rate"] / 12
        
        # Management fees (10% of rent)
        management_fees = rental_income.monthly_rent * MALTA_MARKET_DATA["management_fee_rate"]
        
        # Utilities (estimated)
        utilities = Decimal("100")  # Base estimate
        if property.total_area_sqm:
            utilities = Decimal("50") + (property.total_area_sqm * Decimal("0.5"))
        
        # Vacancy reserve
        vacancy_reserve = rental_income.monthly_rent * (
            1 - rental_income.occupancy_rate
        ) + (rental_income.monthly_rent * MALTA_MARKET_DATA["vacancy_reserve_months"] / 12)
        
        return MonthlyExpenses(
            mortgage_payment=mortgage_payment,
            property_tax=property_tax,
            insurance=insurance,
            maintenance=maintenance,
            management_fees=management_fees,
            utilities=utilities,
            vacancy_reserve=vacancy_reserve,
        )

    def _to_dynamo_key(self, key: str) -> str:
        """Convert snake_case to DynamoDB camelCase."""
        mapping = {
            "analysis_id": "analysisId",
            "property_id": "propertyId",
            "strategy": "strategy",
            "purchase_price": "purchasePrice",
            "down_payment_percentage": "downPaymentPercentage",
            "loan_amount": "loanAmount",
            "interest_rate": "interestRate",
            "loan_term_years": "loanTermYears",
            "closing_costs": "closingCosts",
            "renovation_costs": "renovationCosts",
            "down_payment": "downPayment",
            "closing_costs_amount": "closingCostsAmount",
            "total_investment": "totalInvestment",
            "rental_income": "rentalIncome",
            "monthly_expenses": "monthlyExpenses",
            "cash_flow": "cashFlow",
            "appreciation": "appreciation",
            "gross_rental_yield": "grossRentalYield",
            "net_rental_yield": "netRentalYield",
            "cap_rate": "capRate",
            "roi_percentage": "roiPercentage",
            "roi_score": "roiScore",
            "payback_period_years": "paybackPeriodYears",
            "break_even_months": "breakEvenMonths",
            "risk_level": "riskLevel",
            "market_trend": "marketTrend",
            "confidence_score": "confidenceScore",
            "recommendation": "recommendation",
            "key_factors": "keyFactors",
            "warnings": "warnings",
            "created_at": "createdAt",
            "updated_at": "updatedAt",
            "analysis_version": "analysisVersion",
        }
        return mapping.get(key, key)
