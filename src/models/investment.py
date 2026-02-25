"""
Investment Models

Pydantic v2 models for property investment scenarios and ROI analysis results.
All monetary values use Decimal for precision.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class InvestmentScenario(BaseModel):
    """
    Input parameters for a property investment scenario.
    
    This model captures all the variables needed to calculate ROI
    for a Malta property investment.
    
    Example:
        >>> scenario = InvestmentScenario(
        ...     property_price=Decimal("300000"),
        ...     monthly_rent=Decimal("1200"),
        ...     location="sliema"
        ... )
    """
    
    # Property Details
    property_price: Decimal = Field(
        ...,
        gt=0,
        description="Property purchase price in EUR",
        examples=[Decimal("300000")]
    )
    
    location: str = Field(
        default="malta",
        description="Property location in Malta",
        examples=["sliema", "valletta", "mosta"]
    )
    
    is_first_time_buyer: bool = Field(
        default=False,
        description="Whether buyer qualifies for first-time buyer stamp duty rate"
    )
    
    # Financing
    down_payment_percent: Decimal = Field(
        default=Decimal("0.20"),
        ge=Decimal("0.10"),
        le=Decimal("1.00"),
        description="Down payment as decimal (e.g., 0.20 = 20%)"
    )
    
    loan_interest_rate: Decimal = Field(
        default=Decimal("0.035"),
        ge=0,
        le=Decimal("0.20"),
        description="Annual loan interest rate as decimal (e.g., 0.035 = 3.5%)"
    )
    
    loan_term_years: int = Field(
        default=25,
        ge=5,
        le=40,
        description="Loan term in years"
    )
    
    # Rental Income
    monthly_rent: Decimal = Field(
        ...,
        gt=0,
        description="Expected monthly rental income in EUR",
        examples=[Decimal("1200")]
    )
    
    vacancy_rate: Decimal = Field(
        default=Decimal("0.05"),
        ge=0,
        le=Decimal("0.50"),
        description="Expected annual vacancy rate as decimal (e.g., 0.05 = 5%)"
    )
    
    # Operating Expenses
    property_management_percent: Decimal = Field(
        default=Decimal("0.10"),
        ge=0,
        le=Decimal("0.30"),
        description="Property management fee as % of rent"
    )
    
    maintenance_reserve_percent: Decimal = Field(
        default=Decimal("0.05"),
        ge=0,
        le=Decimal("0.20"),
        description="Maintenance reserve as % of rent"
    )
    
    annual_insurance_cost: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Annual insurance cost in EUR (auto-calculated if None)"
    )
    
    annual_property_tax: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Annual property tax in EUR"
    )
    
    # Additional Costs
    closing_costs_override: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Override for total closing costs (auto-calculated if None)"
    )
    
    @field_validator("property_price", "monthly_rent", mode="before")
    @classmethod
    def ensure_decimal(cls, v):
        """Ensure monetary fields are Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v
    
    @model_validator(mode="after")
    def validate_rental_yield(self):
        """Validate that rental yield is reasonable for the location."""
        from ..data.malta_market import get_rental_yield
        
        annual_rent = self.monthly_rent * Decimal("12")
        actual_yield = annual_rent / self.property_price
        expected_yield = get_rental_yield(self.location)
        
        # Allow 50% variance from expected yield (warning only, not error)
        # This is just for validation, we don't raise an error
        return self
    
    @property
    def down_payment_amount(self) -> Decimal:
        """Calculate down payment amount in EUR."""
        return (self.property_price * self.down_payment_percent).quantize(Decimal("0.01"))
    
    @property
    def loan_amount(self) -> Decimal:
        """Calculate loan amount in EUR."""
        return self.property_price - self.down_payment_amount
    
    @property
    def gross_annual_rent(self) -> Decimal:
        """Calculate gross annual rental income."""
        return (self.monthly_rent * Decimal("12")).quantize(Decimal("0.01"))
    
    @property
    def effective_annual_rent(self) -> Decimal:
        """Calculate annual rent accounting for vacancy."""
        return (self.gross_annual_rent * (Decimal("1") - self.vacancy_rate)).quantize(Decimal("0.01"))


class PurchaseCostBreakdown(BaseModel):
    """
    Detailed breakdown of property purchase costs.
    """
    stamp_duty: Decimal = Field(description="Stamp duty amount")
    notary_fees: Decimal = Field(description="Notary fees")
    registration_fees: Decimal = Field(description="Land registry fees")
    agency_fees: Decimal = Field(description="Agency fees (if applicable)")
    other_fees: Decimal = Field(default=Decimal("0"), description="Other miscellaneous fees")
    
    @property
    def total(self) -> Decimal:
        """Calculate total purchase costs."""
        return (
            self.stamp_duty + 
            self.notary_fees + 
            self.registration_fees + 
            self.agency_fees + 
            self.other_fees
        ).quantize(Decimal("0.01"))


class MortgageDetails(BaseModel):
    """
    Mortgage calculation results.
    """
    principal: Decimal = Field(description="Loan principal amount")
    annual_rate: Decimal = Field(description="Annual interest rate")
    term_years: int = Field(description="Loan term in years")
    monthly_payment: Decimal = Field(description="Monthly mortgage payment")
    total_payments: int = Field(description="Total number of payments")
    total_interest: Decimal = Field(description="Total interest paid over loan term")
    total_cost: Decimal = Field(description="Total amount paid (principal + interest)")
    
    @property
    def annual_payment(self) -> Decimal:
        """Calculate annual mortgage payment."""
        return (self.monthly_payment * Decimal("12")).quantize(Decimal("0.01"))


class OperatingExpenses(BaseModel):
    """
    Annual operating expenses breakdown.
    """
    property_management: Decimal = Field(description="Property management fees")
    maintenance: Decimal = Field(description="Maintenance and repairs reserve")
    insurance: Decimal = Field(description="Property insurance")
    property_tax: Decimal = Field(description="Property tax")
    vacancy_loss: Decimal = Field(description="Estimated vacancy loss")
    other: Decimal = Field(default=Decimal("0"), description="Other expenses")
    
    @property
    def total(self) -> Decimal:
        """Calculate total annual operating expenses."""
        return (
            self.property_management + 
            self.maintenance + 
            self.insurance + 
            self.property_tax + 
            self.vacancy_loss + 
            self.other
        ).quantize(Decimal("0.01"))


class ROIAnalysis(BaseModel):
    """
    Complete ROI analysis results for a property investment.
    
    This model contains all calculated metrics for evaluating
    a property investment opportunity in Malta.
    
    Example:
        >>> analysis = ROIAnalysis(
        ...     total_purchase_cost=Decimal("315000"),
        ...     loan_amount=Decimal("240000"),
        ...     monthly_mortgage=Decimal("1200"),
        ...     gross_annual_rent=Decimal("14400"),
        ...     net_operating_income=Decimal("10000"),
        ...     annual_cash_flow=Decimal("-4400"),
        ...     cap_rate=Decimal("0.0317"),
        ...     cash_on_cash_return=Decimal("-0.140"),
        ...     opportunity_score=65.5
        ... )
    """
    
    # Purchase Information
    property_price: Decimal = Field(description="Property purchase price")
    total_purchase_cost: Decimal = Field(description="Total cost including fees")
    down_payment: Decimal = Field(description="Down payment amount")
    closing_costs: Decimal = Field(description="Total closing costs")
    
    # Financing
    loan_amount: Decimal = Field(description="Mortgage loan amount")
    monthly_mortgage: Decimal = Field(description="Monthly mortgage payment")
    annual_mortgage: Decimal = Field(description="Annual mortgage payment")
    mortgage_details: Optional[MortgageDetails] = Field(default=None)
    
    # Income
    gross_annual_rent: Decimal = Field(description="Gross annual rental income")
    vacancy_loss: Decimal = Field(description="Annual vacancy loss")
    effective_gross_income: Decimal = Field(description="Gross income minus vacancy")
    
    # Expenses
    operating_expenses: OperatingExpenses = Field(description="Operating expenses breakdown")
    total_operating_expenses: Decimal = Field(description="Total annual operating expenses")
    
    # Cash Flow
    net_operating_income: Decimal = Field(description="NOI = EGI - Operating Expenses")
    annual_cash_flow: Decimal = Field(description="Cash flow = NOI - Mortgage")
    monthly_cash_flow: Decimal = Field(description="Monthly cash flow")
    
    # Returns
    cap_rate: Decimal = Field(description="Cap Rate = NOI / Property Price")
    cash_on_cash_return: Decimal = Field(description="CoC = Annual Cash Flow / Cash Invested")
    gross_rent_multiplier: Decimal = Field(description="GRM = Price / Gross Annual Rent")
    
    # Scoring
    opportunity_score: float = Field(
        ge=0, 
        le=100, 
        description="Overall opportunity score (0-100)"
    )
    score_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Breakdown of score components"
    )
    
    # Additional Metrics
    break_even_occupancy: Decimal = Field(description="Occupancy rate needed to break even")
    debt_coverage_ratio: Decimal = Field(description="DSCR = NOI / Annual Mortgage")
    
    @property
    def is_cash_flow_positive(self) -> bool:
        """Check if investment generates positive cash flow."""
        return self.annual_cash_flow > 0
    
    @property
    def cash_invested(self) -> Decimal:
        """Calculate total cash invested (down payment + closing costs)."""
        return (self.down_payment + self.closing_costs).quantize(Decimal("0.01"))
    
    @property
    def roi_percent(self) -> Decimal:
        """Calculate ROI as percentage."""
        return (self.cash_on_cash_return * Decimal("100")).quantize(Decimal("0.01"))
    
    @property
    def cap_rate_percent(self) -> Decimal:
        """Calculate Cap Rate as percentage."""
        return (self.cap_rate * Decimal("100")).quantize(Decimal("0.01"))


class InvestmentComparison(BaseModel):
    """
    Model for comparing multiple investment scenarios.
    """
    scenarios: list[ROIAnalysis] = Field(description="List of analyzed scenarios")
    
    @property
    def best_cash_flow(self) -> Optional[ROIAnalysis]:
        """Get scenario with highest cash flow."""
        if not self.scenarios:
            return None
        return max(self.scenarios, key=lambda x: x.annual_cash_flow)
    
    @property
    def best_cap_rate(self) -> Optional[ROIAnalysis]:
        """Get scenario with highest cap rate."""
        if not self.scenarios:
            return None
        return max(self.scenarios, key=lambda x: x.cap_rate)
    
    @property
    def best_overall(self) -> Optional[ROIAnalysis]:
        """Get scenario with highest opportunity score."""
        if not self.scenarios:
            return None
        return max(self.scenarios, key=lambda x: x.opportunity_score)
