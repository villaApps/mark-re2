"""ROI Analysis models for the Malta Property Analyzer."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class InvestmentStrategy(str, Enum):
    """Investment strategy types."""

    BUY_TO_LET = "buy_to_let"
    FLIP = "flip"
    HOLIDAY_RENTAL = "holiday_rental"
    LONG_TERM_RENTAL = "long_term_rental"
    COMMERCIAL = "commercial"


class RiskLevel(str, Enum):
    """Risk level for investment."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MarketTrend(str, Enum):
    """Market trend direction."""

    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"


class MonthlyExpenses(BaseModel):
    """Monthly expense breakdown."""

    mortgage_payment: Decimal = Field(Decimal("0"), ge=0)
    property_tax: Decimal = Field(Decimal("0"), ge=0)
    insurance: Decimal = Field(Decimal("0"), ge=0)
    maintenance: Decimal = Field(Decimal("0"), ge=0)
    management_fees: Decimal = Field(Decimal("0"), ge=0)
    utilities: Decimal = Field(Decimal("0"), ge=0)
    vacancy_reserve: Decimal = Field(Decimal("0"), ge=0)
    other: Decimal = Field(Decimal("0"), ge=0)

    @property
    def total(self) -> Decimal:
        """Calculate total monthly expenses."""
        return (
            self.mortgage_payment
            + self.property_tax
            + self.insurance
            + self.maintenance
            + self.management_fees
            + self.utilities
            + self.vacancy_reserve
            + self.other
        )


class RentalIncome(BaseModel):
    """Rental income projections."""

    monthly_rent: Decimal = Field(..., gt=0)
    occupancy_rate: Decimal = Field(Decimal("0.90"), ge=0, le=1)
    annual_rent_increase: Decimal = Field(Decimal("0.03"), ge=0, le=0.5)

    @property
    def effective_monthly_income(self) -> Decimal:
        """Calculate effective monthly income considering occupancy."""
        return self.monthly_rent * self.occupancy_rate

    @property
    def annual_income(self) -> Decimal:
        """Calculate annual rental income."""
        return self.effective_monthly_income * 12


class CashFlowAnalysis(BaseModel):
    """Cash flow analysis results."""

    monthly_income: Decimal
    monthly_expenses: Decimal
    monthly_cash_flow: Decimal
    annual_cash_flow: Decimal
    cash_on_cash_return: Decimal


class AppreciationProjection(BaseModel):
    """Property appreciation projections."""

    annual_appreciation_rate: Decimal = Field(Decimal("0.03"), ge=0, le=0.5)
    projected_value_1yr: Decimal
    projected_value_5yr: Decimal
    projected_value_10yr: Decimal
    total_appreciation_10yr: Decimal


class ROIAnalysis(BaseModel):
    """Complete ROI analysis for a property."""

    analysis_id: str = Field(..., description="Unique analysis identifier")
    property_id: str = Field(..., description="Associated property ID")
    
    # Input parameters
    strategy: InvestmentStrategy = Field(default=InvestmentStrategy.BUY_TO_LET)
    purchase_price: Decimal = Field(..., gt=0)
    down_payment_percentage: Decimal = Field(Decimal("0.20"), ge=0, le=1)
    loan_amount: Decimal | None = None
    interest_rate: Decimal = Field(Decimal("0.035"), ge=0, le=0.5)
    loan_term_years: int = Field(25, ge=5, le=40)
    closing_costs: Decimal = Field(Decimal("0.05"), ge=0, le=0.5)
    renovation_costs: Decimal = Field(Decimal("0"), ge=0)
    
    # Financial calculations
    down_payment: Decimal | None = None
    closing_costs_amount: Decimal | None = None
    total_investment: Decimal | None = None
    
    # Income and expenses
    rental_income: RentalIncome
    monthly_expenses: MonthlyExpenses
    
    # Results
    cash_flow: CashFlowAnalysis | None = None
    appreciation: AppreciationProjection | None = None
    
    # ROI metrics
    gross_rental_yield: Decimal | None = None
    net_rental_yield: Decimal | None = None
    cap_rate: Decimal | None = None
    roi_percentage: Decimal | None = Field(None, ge=-100, le=1000)
    roi_score: Decimal | None = Field(None, ge=0, le=100)
    payback_period_years: Decimal | None = None
    break_even_months: int | None = None
    
    # Risk assessment
    risk_level: RiskLevel | None = None
    market_trend: MarketTrend = MarketTrend.STABLE
    confidence_score: Decimal = Field(Decimal("0.5"), ge=0, le=1)
    
    # Recommendations
    recommendation: str | None = None
    key_factors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_version: str = "1.0"

    @field_validator("loan_amount", mode="before")
    @classmethod
    def calculate_loan_amount(cls, v: Any, info: Any) -> Decimal:
        """Calculate loan amount from purchase price and down payment."""
        if v is not None:
            return v
        data = info.data
        purchase_price = data.get("purchase_price", Decimal("0"))
        down_payment_pct = data.get("down_payment_percentage", Decimal("0.20"))
        return purchase_price * (1 - down_payment_pct)

    @model_validator(mode="after")
    def calculate_investment_amounts(self) -> "ROIAnalysis":
        """Calculate investment-related amounts."""
        if self.down_payment is None:
            self.down_payment = self.purchase_price * self.down_payment_percentage
        if self.closing_costs_amount is None:
            self.closing_costs_amount = self.purchase_price * self.closing_costs
        if self.total_investment is None:
            self.total_investment = (
                self.down_payment + self.closing_costs_amount + self.renovation_costs
            )
        return self

    @model_validator(mode="after")
    def calculate_cash_flow(self) -> "ROIAnalysis":
        """Calculate cash flow metrics."""
        monthly_income = self.rental_income.effective_monthly_income
        monthly_exp = self.monthly_expenses.total
        
        self.cash_flow = CashFlowAnalysis(
            monthly_income=monthly_income,
            monthly_expenses=monthly_exp,
            monthly_cash_flow=monthly_income - monthly_exp,
            annual_cash_flow=(monthly_income - monthly_exp) * 12,
            cash_on_cash_return=Decimal("0"),
        )
        
        if self.total_investment and self.total_investment > 0:
            annual_cf = self.cash_flow.annual_cash_flow
            self.cash_flow.cash_on_cash_return = (annual_cf / self.total_investment) * 100
        
        return self

    @model_validator(mode="after")
    def calculate_roi_metrics(self) -> "ROIAnalysis":
        """Calculate ROI metrics."""
        # Gross rental yield
        if self.purchase_price > 0:
            annual_rent = self.rental_income.annual_income
            self.gross_rental_yield = (annual_rent / self.purchase_price) * 100
        
        # Net rental yield
        annual_expenses = self.monthly_expenses.total * 12
        if self.purchase_price > 0:
            net_income = self.rental_income.annual_income - annual_expenses
            self.net_rental_yield = (net_income / self.purchase_price) * 100
        
        # Cap rate (using purchase price as property value)
        if self.purchase_price > 0:
            noi = self.rental_income.annual_income - annual_expenses + self.monthly_expenses.mortgage_payment * 12
            self.cap_rate = (noi / self.purchase_price) * 100
        
        # Overall ROI
        if self.cash_flow and self.total_investment and self.total_investment > 0:
            annual_return = self.cash_flow.annual_cash_flow
            self.roi_percentage = (annual_return / self.total_investment) * 100
        
        # ROI Score (0-100)
        if self.roi_percentage is not None:
            # Normalize ROI to 0-100 scale
            # Assuming 15%+ ROI is excellent (100), 0% is poor (0)
            score = min(max(self.roi_percentage / Decimal("0.15"), Decimal("0")), Decimal("100"))
            self.roi_score = score
        
        # Payback period
        if self.cash_flow and self.cash_flow.annual_cash_flow > 0:
            self.payback_period_years = self.total_investment / self.cash_flow.annual_cash_flow
        
        # Break-even months
        if self.cash_flow and self.cash_flow.monthly_cash_flow > 0:
            self.break_even_months = int(self.total_investment / self.cash_flow.monthly_cash_flow)
        
        return self

    @model_validator(mode="after")
    def calculate_appreciation(self) -> "ROIAnalysis":
        """Calculate appreciation projections."""
        rate = self.annual_appreciation_rate
        self.appreciation = AppreciationProjection(
            annual_appreciation_rate=rate,
            projected_value_1yr=self.purchase_price * (1 + rate),
            projected_value_5yr=self.purchase_price * ((1 + rate) ** 5),
            projected_value_10yr=self.purchase_price * ((1 + rate) ** 10),
            total_appreciation_10yr=self.purchase_price * (((1 + rate) ** 10) - 1),
        )
        return self

    @model_validator(mode="after")
    def assess_risk(self) -> "ROIAnalysis":
        """Assess investment risk level."""
        risk_factors = 0
        
        # Cash flow risk
        if self.cash_flow and self.cash_flow.monthly_cash_flow < 0:
            risk_factors += 2
        
        # ROI risk
        if self.roi_percentage is not None and self.roi_percentage < 5:
            risk_factors += 1
        
        # Market risk
        if self.market_trend == MarketTrend.DECLINING:
            risk_factors += 2
        
        # Confidence risk
        if self.confidence_score < Decimal("0.3"):
            risk_factors += 1
        
        # Assign risk level
        if risk_factors >= 4:
            self.risk_level = RiskLevel.VERY_HIGH
        elif risk_factors >= 3:
            self.risk_level = RiskLevel.HIGH
        elif risk_factors >= 1:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW
        
        return self

    @model_validator(mode="after")
    def generate_recommendation(self) -> "ROIAnalysis":
        """Generate investment recommendation."""
        if self.roi_score is None:
            self.recommendation = "Insufficient data for recommendation"
            return self
        
        if self.roi_score >= 80 and self.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
            self.recommendation = "Strong Buy - Excellent investment opportunity"
        elif self.roi_score >= 60 and self.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
            self.recommendation = "Buy - Good investment opportunity"
        elif self.roi_score >= 40:
            self.recommendation = "Consider - Moderate investment potential"
        elif self.roi_score >= 20:
            self.recommendation = "Hold - Limited investment potential"
        else:
            self.recommendation = "Avoid - Poor investment opportunity"
        
        # Add key factors
        self.key_factors = []
        if self.gross_rental_yield and self.gross_rental_yield > Decimal("5"):
            self.key_factors.append(f"Strong rental yield: {self.gross_rental_yield:.1f}%")
        if self.cap_rate and self.cap_rate > Decimal("4"):
            self.key_factors.append(f"Good cap rate: {self.cap_rate:.1f}%")
        if self.cash_flow and self.cash_flow.monthly_cash_flow > 0:
            self.key_factors.append("Positive monthly cash flow")
        
        return self

    def to_dynamodb_item(self) -> dict[str, Any]:
        """Convert to DynamoDB item format."""
        data = self.model_dump()
        
        # Convert Decimal to float
        decimal_fields = [
            "purchase_price", "down_payment_percentage", "loan_amount", "interest_rate",
            "closing_costs", "renovation_costs", "down_payment", "closing_costs_amount",
            "total_investment", "gross_rental_yield", "net_rental_yield", "cap_rate",
            "roi_percentage", "roi_score", "payback_period_years", "confidence_score",
        ]
        for field in decimal_fields:
            if data.get(field) is not None:
                data[field] = float(data[field])
        
        # Convert datetime
        for key in ["created_at", "updated_at"]:
            if data.get(key) is not None:
                data[key] = data[key].isoformat()
        
        # Convert enums
        data["strategy"] = data["strategy"].value
        data["market_trend"] = data["market_trend"].value
        if data.get("risk_level"):
            data["risk_level"] = data["risk_level"].value
        
        return data

    @classmethod
    def from_dynamodb_item(cls, item: dict[str, Any]) -> "ROIAnalysis":
        """Create ROIAnalysis from DynamoDB item."""
        # Convert float to Decimal
        decimal_fields = [
            "purchase_price", "down_payment_percentage", "loan_amount", "interest_rate",
            "closing_costs", "renovation_costs", "down_payment", "closing_costs_amount",
            "total_investment", "gross_rental_yield", "net_rental_yield", "cap_rate",
            "roi_percentage", "roi_score", "payback_period_years", "confidence_score",
        ]
        for field in decimal_fields:
            if field in item and item[field] is not None:
                item[field] = Decimal(str(item[field]))
        
        # Convert datetime
        for key in ["created_at", "updated_at"]:
            if key in item and item[key] is not None:
                item[key] = datetime.fromisoformat(item[key])
        
        # Convert enums
        if "strategy" in item:
            item["strategy"] = InvestmentStrategy(item["strategy"])
        if "market_trend" in item:
            item["market_trend"] = MarketTrend(item["market_trend"])
        if "risk_level" in item and item["risk_level"]:
            item["risk_level"] = RiskLevel(item["risk_level"])
        
        return cls(**item)


class ROIInput(BaseModel):
    """Input model for ROI calculation."""

    property_id: str
    strategy: InvestmentStrategy = InvestmentStrategy.BUY_TO_LET
    down_payment_percentage: Decimal = Field(Decimal("0.20"), ge=0, le=1)
    interest_rate: Decimal = Field(Decimal("0.035"), ge=0, le=0.5)
    loan_term_years: int = Field(25, ge=5, le=40)
    closing_costs: Decimal = Field(Decimal("0.05"), ge=0, le=0.5)
    renovation_costs: Decimal = Field(Decimal("0"), ge=0)
    monthly_rent: Decimal | None = Field(None, gt=0)
    occupancy_rate: Decimal = Field(Decimal("0.90"), ge=0, le=1)
    annual_rent_increase: Decimal = Field(Decimal("0.03"), ge=0, le=0.5)
    annual_appreciation_rate: Decimal = Field(Decimal("0.03"), ge=0, le=0.5)
    monthly_expenses: MonthlyExpenses = Field(default_factory=MonthlyExpenses)


class OpportunityFilter(BaseModel):
    """Filter for investment opportunities."""

    min_roi_score: Decimal = Field(Decimal("60"), ge=0, le=100)
    max_risk_level: RiskLevel | None = None
    strategy: InvestmentStrategy | None = None
    location: str | None = None
    min_price: Decimal | None = Field(None, ge=0)
    max_price: Decimal | None = Field(None, ge=0)
    property_type: str | None = None
    limit: int = Field(default=20, ge=1, le=100)
