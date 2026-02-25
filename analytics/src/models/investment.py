"""Investment scenario and financing models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class FinancingDetails(BaseModel):
    """Mortgage financing details for a property investment."""
    
    loan_amount: Decimal = Field(
        ...,
        description="Total loan amount",
        ge=Decimal("0"),
    )
    interest_rate_annual: Decimal = Field(
        default=Decimal("0.035"),
        description="Annual interest rate (e.g., 0.035 for 3.5%)",
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    term_years: int = Field(
        default=25,
        description="Loan term in years",
        ge=1,
        le=40,
    )
    is_interest_only: bool = Field(
        default=False,
        description="Whether the loan is interest-only",
    )
    
    @field_validator("loan_amount", "interest_rate_annual", mode="before")
    @classmethod
    def convert_to_decimal(cls, v):
        """Convert numeric values to Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v
    
    @property
    def monthly_interest_rate(self) -> Decimal:
        """Calculate monthly interest rate."""
        return self.interest_rate_annual / Decimal("12")
    
    @property
    def number_of_payments(self) -> int:
        """Calculate total number of payments."""
        return self.term_years * 12


class InvestmentScenario(BaseModel):
    """Complete investment scenario for property analysis.
    
    This model captures all the inputs needed to analyze a property
    investment opportunity in Malta.
    """
    
    # Property Details
    property_price: Decimal = Field(
        ...,
        description="Property purchase price in EUR",
        gt=Decimal("0"),
    )
    property_area: Optional[str] = Field(
        default=None,
        description="Area/locality in Malta (e.g., 'sliema', 'valletta')",
    )
    is_first_time_buyer: bool = Field(
        default=True,
        description="Whether this is a first-time property purchase",
    )
    
    # Financing
    down_payment_percent: Decimal = Field(
        default=Decimal("0.20"),
        description="Down payment as percentage of property price (e.g., 0.20 for 20%)",
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    loan_interest_rate: Decimal = Field(
        default=Decimal("0.035"),
        description="Annual loan interest rate (e.g., 0.035 for 3.5%)",
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    loan_term_years: int = Field(
        default=25,
        description="Loan term in years",
        ge=1,
        le=40,
    )
    
    # Rental Income
    monthly_rent: Decimal = Field(
        ...,
        description="Expected monthly rental income in EUR",
        ge=Decimal("0"),
    )
    vacancy_rate: Decimal = Field(
        default=Decimal("0.05"),
        description="Expected vacancy rate (e.g., 0.05 for 5%)",
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    
    # Operating Expenses
    property_management_percent: Decimal = Field(
        default=Decimal("0.10"),
        description="Property management fee as % of rental income",
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    maintenance_reserve_percent: Decimal = Field(
        default=Decimal("0.05"),
        description="Maintenance reserve as % of rental income",
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    insurance_annual_percent: Decimal = Field(
        default=Decimal("0.003"),
        description="Annual insurance as % of property value",
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    
    # Market Assumptions
    annual_appreciation: Decimal = Field(
        default=Decimal("0.03"),
        description="Expected annual property appreciation (e.g., 0.03 for 3%)",
        ge=Decimal("-0.5"),
        le=Decimal("0.5"),
    )
    annual_rent_increase: Decimal = Field(
        default=Decimal("0.025"),
        description="Expected annual rent increase (e.g., 0.025 for 2.5%)",
        ge=Decimal("-0.5"),
        le=Decimal("0.5"),
    )
    
    # Purchase Costs Override (optional)
    custom_stamp_duty: Optional[Decimal] = Field(
        default=None,
        description="Custom stamp duty amount (overrides calculation)",
        ge=Decimal("0"),
    )
    include_agency_fees: bool = Field(
        default=False,
        description="Whether to include buyer agency fees",
    )
    
    # Metadata
    scenario_name: Optional[str] = Field(
        default=None,
        description="Optional name for this scenario",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When this scenario was created",
    )
    
    @field_validator(
        "property_price", "down_payment_percent", "loan_interest_rate",
        "monthly_rent", "vacancy_rate", "property_management_percent",
        "maintenance_reserve_percent", "insurance_annual_percent",
        "annual_appreciation", "annual_rent_increase", "custom_stamp_duty",
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
    
    @model_validator(mode="after")
    def validate_scenario(self):
        """Validate the entire scenario for consistency."""
        # Check that down payment + loan = property price
        loan_pct = Decimal("1") - self.down_payment_percent
        loan_amount = self.property_price * loan_pct
        
        if loan_amount < Decimal("0"):
            raise ValueError("Loan amount cannot be negative")
        
        # Check that rent makes sense for the property price
        if self.monthly_rent > Decimal("0"):
            annual_rent = self.monthly_rent * Decimal("12")
            gross_yield = annual_rent / self.property_price
            if gross_yield > Decimal("0.20"):  # 20% yield is suspiciously high
                # This is a warning, not an error
                pass
        
        return self
    
    @property
    def down_payment_amount(self) -> Decimal:
        """Calculate down payment amount."""
        return self.property_price * self.down_payment_percent
    
    @property
    def loan_amount(self) -> Decimal:
        """Calculate loan amount."""
        return self.property_price - self.down_payment_amount
    
    @property
    def annual_rent(self) -> Decimal:
        """Calculate annual rental income."""
        return self.monthly_rent * Decimal("12")
    
    @property
    def effective_gross_income(self) -> Decimal:
        """Calculate effective gross income (accounting for vacancy)."""
        return self.annual_rent * (Decimal("1") - self.vacancy_rate)
    
    def get_financing_details(self) -> FinancingDetails:
        """Get financing details as a separate model."""
        return FinancingDetails(
            loan_amount=self.loan_amount,
            interest_rate_annual=self.loan_interest_rate,
            term_years=self.loan_term_years,
        )
    
    def copy_with_adjustments(
        self,
        property_price: Optional[Decimal] = None,
        monthly_rent: Optional[Decimal] = None,
        down_payment_percent: Optional[Decimal] = None,
        loan_interest_rate: Optional[Decimal] = None,
        scenario_name: Optional[str] = None,
    ) -> "InvestmentScenario":
        """Create a copy of this scenario with specified adjustments.
        
        Args:
            property_price: New property price (or None to keep current)
            monthly_rent: New monthly rent (or None to keep current)
            down_payment_percent: New down payment % (or None to keep current)
            loan_interest_rate: New interest rate (or None to keep current)
            scenario_name: New scenario name (or None to keep current)
            
        Returns:
            New InvestmentScenario with adjustments applied
        """
        data = self.model_dump()
        
        if property_price is not None:
            data["property_price"] = property_price
        if monthly_rent is not None:
            data["monthly_rent"] = monthly_rent
        if down_payment_percent is not None:
            data["down_payment_percent"] = down_payment_percent
        if loan_interest_rate is not None:
            data["loan_interest_rate"] = loan_interest_rate
        if scenario_name is not None:
            data["scenario_name"] = scenario_name
        
        data["created_at"] = datetime.now()
        
        return InvestmentScenario(**data)
