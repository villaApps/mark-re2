"""Analysis results models."""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class PurchaseCostBreakdown(BaseModel):
    """Detailed breakdown of purchase costs."""
    
    stamp_duty: Decimal = Field(..., description="Stamp duty amount")
    notary_fees: Decimal = Field(..., description="Notary fees")
    registration_fees: Decimal = Field(..., description="Registration fees")
    agency_fees: Decimal = Field(..., description="Agency fees (if applicable)")
    other_costs: Decimal = Field(default=Decimal("0"), description="Other miscellaneous costs")
    
    @field_validator("stamp_duty", "notary_fees", "registration_fees", "agency_fees", "other_costs", mode="before")
    @classmethod
    def convert_to_decimal(cls, v):
        """Convert numeric values to Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v
    
    @property
    def total(self) -> Decimal:
        """Calculate total purchase costs."""
        return (
            self.stamp_duty + 
            self.notary_fees + 
            self.registration_fees + 
            self.agency_fees + 
            self.other_costs
        )


class CashFlowBreakdown(BaseModel):
    """Detailed cash flow breakdown."""
    
    # Income
    gross_annual_rent: Decimal = Field(..., description="Total annual rent before vacancy")
    vacancy_loss: Decimal = Field(..., description="Estimated vacancy loss")
    effective_gross_income: Decimal = Field(..., description="Rent after vacancy")
    
    # Operating Expenses
    property_management: Decimal = Field(..., description="Property management fees")
    maintenance_reserve: Decimal = Field(..., description="Maintenance reserve")
    insurance: Decimal = Field(..., description="Annual insurance cost")
    property_tax: Decimal = Field(default=Decimal("0"), description="Property tax (0 in Malta)")
    other_expenses: Decimal = Field(default=Decimal("0"), description="Other operating expenses")
    
    # Net Operating Income
    net_operating_income: Decimal = Field(..., description="NOI = EGI - Operating Expenses")
    
    # Financing
    annual_mortgage_payment: Decimal = Field(..., description="Total annual mortgage payments")
    
    # Cash Flow
    annual_cash_flow: Decimal = Field(..., description="NOI - Mortgage Payments")
    monthly_cash_flow: Decimal = Field(..., description="Annual cash flow / 12")
    
    @field_validator(
        "gross_annual_rent", "vacancy_loss", "effective_gross_income",
        "property_management", "maintenance_reserve", "insurance",
        "property_tax", "other_expenses", "net_operating_income",
        "annual_mortgage_payment", "annual_cash_flow", "monthly_cash_flow",
        mode="before"
    )
    @classmethod
    def convert_to_decimal(cls, v):
        """Convert numeric values to Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v
    
    @property
    def total_operating_expenses(self) -> Decimal:
        """Calculate total operating expenses."""
        return (
            self.property_management +
            self.maintenance_reserve +
            self.insurance +
            self.property_tax +
            self.other_expenses
        )
    
    @property
    def operating_expense_ratio(self) -> Decimal:
        """Calculate operating expense ratio (OER)."""
        if self.effective_gross_income == Decimal("0"):
            return Decimal("0")
        return self.total_operating_expenses / self.effective_gross_income
    
    @property
    def is_cash_flow_positive(self) -> bool:
        """Check if cash flow is positive."""
        return self.annual_cash_flow > Decimal("0")


class ProjectionYear(BaseModel):
    """Single year projection data."""
    
    year: int = Field(..., description="Year number (1-10)")
    
    # Property Value
    property_value: Decimal = Field(..., description="Projected property value")
    appreciation_gain: Decimal = Field(..., description="Gain from appreciation")
    
    # Rental Income
    annual_rent: Decimal = Field(..., description="Projected annual rent")
    vacancy_loss: Decimal = Field(..., description="Projected vacancy loss")
    effective_income: Decimal = Field(..., description="Effective gross income")
    
    # Expenses
    operating_expenses: Decimal = Field(..., description="Total operating expenses")
    mortgage_payment: Decimal = Field(..., description="Annual mortgage payment")
    
    # Cash Flow
    cash_flow: Decimal = Field(..., description="Annual cash flow")
    cumulative_cash_flow: Decimal = Field(..., description="Cumulative cash flow to date")
    
    # Equity
    remaining_loan_balance: Decimal = Field(..., description="Remaining loan balance")
    equity: Decimal = Field(..., description="Property value - loan balance")
    
    @field_validator(
        "property_value", "appreciation_gain", "annual_rent", "vacancy_loss",
        "effective_income", "operating_expenses", "mortgage_payment",
        "cash_flow", "cumulative_cash_flow", "remaining_loan_balance", "equity",
        mode="before"
    )
    @classmethod
    def convert_to_decimal(cls, v):
        """Convert numeric values to Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v


class TenYearProjection(BaseModel):
    """10-year investment projection."""
    
    years: List[ProjectionYear] = Field(..., description="Year-by-year projections")
    
    # Summary Metrics
    total_cash_flow: Decimal = Field(..., description="Total cash flow over 10 years")
    total_appreciation: Decimal = Field(..., description="Total appreciation gain")
    final_property_value: Decimal = Field(..., description="Property value at year 10")
    final_equity: Decimal = Field(..., description="Equity at year 10")
    
    # Returns
    irr: Optional[Decimal] = Field(None, description="Internal Rate of Return")
    total_roi: Decimal = Field(..., description="Total return on investment")
    annualized_return: Decimal = Field(..., description="Annualized return percentage")
    
    @field_validator(
        "total_cash_flow", "total_appreciation", "final_property_value",
        "final_equity", "irr", "total_roi", "annualized_return",
        mode="before"
    )
    @classmethod
    def convert_to_decimal(cls, v):
        """Convert numeric values to Decimal."""
        if v is None:
            return v
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v


class ROIAnalysis(BaseModel):
    """Complete ROI analysis for a property investment.
    
    This model contains all the calculated metrics for evaluating
    a property investment opportunity in Malta.
    """
    
    # Identification
    property_id: str = Field(..., description="Unique property identifier")
    scenario_name: Optional[str] = Field(None, description="Name of the investment scenario")
    
    # Input Summary
    property_price: Decimal = Field(..., description="Property purchase price")
    area: Optional[str] = Field(None, description="Property area/locality")
    
    # Purchase Costs
    total_purchase_cost: Decimal = Field(..., description="Total cash needed to purchase")
    closing_costs_breakdown: PurchaseCostBreakdown = Field(..., description="Detailed closing costs")
    total_cash_invested: Decimal = Field(..., description="Down payment + closing costs")
    
    # Financing
    loan_amount: Decimal = Field(..., description="Total loan amount")
    monthly_mortgage_payment: Decimal = Field(..., description="Monthly mortgage payment")
    annual_mortgage_payment: Decimal = Field(..., description="Annual mortgage payment")
    total_interest_paid: Decimal = Field(..., description="Total interest over loan term")
    
    # Cash Flow
    cash_flow: CashFlowBreakdown = Field(..., description="Detailed cash flow breakdown")
    
    # Returns - Key Metrics
    cap_rate: Decimal = Field(..., description="Capitalization Rate (NOI / Purchase Price)")
    cash_on_cash_return: Decimal = Field(..., description="Cash-on-Cash Return (Annual CF / Cash Invested)")
    gross_rental_yield: Decimal = Field(..., description="Gross Rental Yield (Annual Rent / Price)")
    net_rental_yield: Decimal = Field(..., description="Net Rental Yield (NOI / Price)")
    
    # Price-to-Rent Ratio
    price_to_rent_ratio: Decimal = Field(..., description="Property Price / Annual Rent")
    
    # Projections
    projection_10_year: Optional[TenYearProjection] = Field(None, description="10-year projection")
    irr_10_year: Optional[Decimal] = Field(None, description="10-year IRR")
    
    # Scoring
    opportunity_score: float = Field(..., description="Opportunity score (0-100)", ge=0, le=100)
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    recommendation: str = Field(..., description="Investment recommendation")
    
    # Metadata
    calculated_at: datetime = Field(default_factory=datetime, description="Calculation timestamp")
    
    @field_validator(
        "property_price", "total_purchase_cost", "total_cash_invested",
        "loan_amount", "monthly_mortgage_payment", "annual_mortgage_payment",
        "total_interest_paid", "cap_rate", "cash_on_cash_return",
        "gross_rental_yield", "net_rental_yield", "price_to_rent_ratio",
        "irr_10_year",
        mode="before"
    )
    @classmethod
    def convert_to_decimal(cls, v):
        """Convert numeric values to Decimal."""
        if v is None:
            return v
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v
    
    @property
    def is_good_investment(self) -> bool:
        """Quick check if this appears to be a good investment."""
        return (
            self.opportunity_score >= 60 and
            self.cash_flow.is_cash_flow_positive and
            self.cash_on_cash_return >= Decimal("0.05")  # 5%+
        )
    
    @property
    def monthly_cash_flow(self) -> Decimal:
        """Get monthly cash flow."""
        return self.cash_flow.monthly_cash_flow
    
    @property
    def annual_cash_flow(self) -> Decimal:
        """Get annual cash flow."""
        return self.cash_flow.annual_cash_flow
    
    @property
    def net_operating_income(self) -> Decimal:
        """Get net operating income."""
        return self.cash_flow.net_operating_income
    
    def to_summary_dict(self) -> Dict:
        """Convert to a summary dictionary for display."""
        return {
            "property_id": self.property_id,
            "property_price": float(self.property_price),
            "total_cash_needed": float(self.total_cash_invested),
            "monthly_cash_flow": float(self.monthly_cash_flow),
            "annual_cash_flow": float(self.annual_cash_flow),
            "cap_rate": float(self.cap_rate) * 100,  # As percentage
            "cash_on_cash": float(self.cash_on_cash_return) * 100,  # As percentage
            "gross_yield": float(self.gross_rental_yield) * 100,  # As percentage
            "opportunity_score": self.opportunity_score,
            "risk_level": self.risk_level,
            "recommendation": self.recommendation,
        }
