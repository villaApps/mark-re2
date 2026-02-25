"""
ROI Calculator

Main calculator for property investment ROI analysis.
Includes mortgage calculations, cash flow analysis, and return metrics.

All formulas follow standard real estate investment practices.
"""

from decimal import Decimal, ROUND_HALF_UP
from math import pow

from ..models.investment import (
    InvestmentScenario,
    ROIAnalysis,
    MortgageDetails,
    OperatingExpenses,
    PurchaseCostBreakdown,
)
from ..data.malta_market import INSURANCE_ANNUAL_RATE
from .purchase_costs import calculate_purchase_costs


def calculate_mortgage(
    principal: Decimal,
    annual_rate: Decimal,
    years: int,
) -> MortgageDetails:
    """
    Calculate mortgage details using standard amortization formula.
    
    Uses the formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
    Where:
        M = Monthly payment
        P = Principal loan amount
        r = Monthly interest rate (annual / 12)
        n = Total number of payments (years * 12)
    
    Args:
        principal: Loan principal amount in EUR
        annual_rate: Annual interest rate as decimal (e.g., 0.035 for 3.5%)
        years: Loan term in years
        
    Returns:
        MortgageDetails with full payment breakdown
        
    Example:
        >>> mortgage = calculate_mortgage(
        ...     principal=Decimal("240000"),
        ...     annual_rate=Decimal("0.035"),
        ...     years=25
        ... )
        >>> mortgage.monthly_payment
        Decimal('1201.58')
    """
    if principal <= 0:
        raise ValueError("Principal must be positive")
    if annual_rate < 0:
        raise ValueError("Interest rate cannot be negative")
    if years <= 0:
        raise ValueError("Loan term must be positive")
    
    total_payments = years * 12
    
    # Handle zero interest rate case
    if annual_rate == 0:
        monthly_payment = principal / Decimal(total_payments)
        total_cost = principal
        total_interest = Decimal("0")
    else:
        # Convert to monthly rate
        monthly_rate = annual_rate / Decimal("12")
        
        # Convert to float for pow calculation, then back to Decimal
        r = float(monthly_rate)
        n = total_payments
        
        # Calculate monthly payment using amortization formula
        # M = P * [r(1+r)^n] / [(1+r)^n - 1]
        factor = pow(1 + r, n)
        monthly_payment_float = float(principal) * (r * factor) / (factor - 1)
        monthly_payment = Decimal(str(monthly_payment_float))
        
        # Calculate totals
        total_cost = monthly_payment * Decimal(total_payments)
        total_interest = total_cost - principal
    
    return MortgageDetails(
        principal=principal.quantize(Decimal("0.01")),
        annual_rate=annual_rate,
        term_years=years,
        monthly_payment=monthly_payment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        total_payments=total_payments,
        total_interest=total_interest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        total_cost=total_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
    )


def calculate_operating_expenses(
    scenario: InvestmentScenario,
) -> OperatingExpenses:
    """
    Calculate annual operating expenses for a rental property.
    
    Args:
        scenario: Investment scenario with expense parameters
        
    Returns:
        OperatingExpenses breakdown
        
    Formula:
        Property Management = Gross Rent * management_percent
        Maintenance = Gross Rent * maintenance_percent
        Insurance = Property Price * 0.002 (or override)
        Vacancy Loss = Gross Rent * vacancy_rate
    """
    gross_annual_rent = scenario.gross_annual_rent
    
    # Property management fee
    property_management = (
        gross_annual_rent * scenario.property_management_percent
    ).quantize(Decimal("0.01"))
    
    # Maintenance reserve
    maintenance = (
        gross_annual_rent * scenario.maintenance_reserve_percent
    ).quantize(Decimal("0.01"))
    
    # Insurance (use override or calculate)
    if scenario.annual_insurance_cost is not None:
        insurance = scenario.annual_insurance_cost
    else:
        insurance = (
            scenario.property_price * INSURANCE_ANNUAL_RATE
        ).quantize(Decimal("0.01"))
    
    # Vacancy loss
    vacancy_loss = (
        gross_annual_rent * scenario.vacancy_rate
    ).quantize(Decimal("0.01"))
    
    return OperatingExpenses(
        property_management=property_management,
        maintenance=maintenance,
        insurance=insurance,
        property_tax=scenario.annual_property_tax,
        vacancy_loss=vacancy_loss,
        other=Decimal("0"),
    )


def calculate_roi(scenario: InvestmentScenario) -> ROIAnalysis:
    """
    Perform complete ROI analysis for a property investment scenario.
    
    This is the main analysis function that calculates all investment
    metrics including cash flow, returns, and opportunity scoring.
    
    Args:
        scenario: InvestmentScenario with all input parameters
        
    Returns:
        ROIAnalysis with complete investment metrics
        
    Formulas:
        Cap Rate = NOI / Property Price
        Cash-on-Cash = Annual Cash Flow / Cash Invested
        GRM = Property Price / Gross Annual Rent
        DSCR = NOI / Annual Mortgage Payment
        
    Example:
        >>> scenario = InvestmentScenario(
        ...     property_price=Decimal("300000"),
        ...     monthly_rent=Decimal("1400"),
        ...     location="mosta"
        ... )
        >>> analysis = calculate_roi(scenario)
        >>> analysis.cap_rate
        Decimal('0.048')
    """
    # Calculate purchase costs
    purchase_costs = calculate_purchase_costs(
        property_price=scenario.property_price,
        is_first_time_buyer=scenario.is_first_time_buyer,
    )
    closing_costs = purchase_costs.total
    
    # Calculate down payment and loan
    down_payment = scenario.down_payment_amount
    loan_amount = scenario.loan_amount
    
    # Total purchase cost
    total_purchase_cost = scenario.property_price + closing_costs
    
    # Calculate mortgage (skip if cash buyer)
    if loan_amount > 0:
        mortgage = calculate_mortgage(
            principal=loan_amount,
            annual_rate=scenario.loan_interest_rate,
            years=scenario.loan_term_years,
        )
        monthly_mortgage = mortgage.monthly_payment
        annual_mortgage = mortgage.annual_payment
    else:
        # Cash buyer - no mortgage
        mortgage = None
        monthly_mortgage = Decimal("0.00")
        annual_mortgage = Decimal("0.00")
    
    # Calculate rental income
    gross_annual_rent = scenario.gross_annual_rent
    vacancy_loss = gross_annual_rent * scenario.vacancy_rate
    effective_gross_income = gross_annual_rent - vacancy_loss
    
    # Calculate operating expenses
    operating_expenses = calculate_operating_expenses(scenario)
    total_operating_expenses = operating_expenses.total
    
    # Calculate NOI (Net Operating Income)
    net_operating_income = effective_gross_income - total_operating_expenses
    
    # Calculate cash flow
    annual_cash_flow = net_operating_income - annual_mortgage
    monthly_cash_flow = annual_cash_flow / Decimal("12")
    
    # Calculate return metrics
    # Cap Rate = NOI / Property Price
    cap_rate = (net_operating_income / scenario.property_price).quantize(Decimal("0.0001"))
    
    # Cash-on-Cash Return = Annual Cash Flow / Cash Invested
    cash_invested = down_payment + closing_costs
    if cash_invested > 0:
        cash_on_cash = (annual_cash_flow / cash_invested).quantize(Decimal("0.0001"))
    else:
        cash_on_cash = Decimal("0")
    
    # Gross Rent Multiplier = Price / Gross Annual Rent
    gross_rent_multiplier = (
        scenario.property_price / gross_annual_rent
    ).quantize(Decimal("0.01"))
    
    # Debt Coverage Ratio = NOI / Annual Mortgage
    if annual_mortgage > 0:
        debt_coverage_ratio = (net_operating_income / annual_mortgage).quantize(Decimal("0.01"))
    else:
        debt_coverage_ratio = Decimal("999.99")  # No mortgage = infinite coverage
    
    # Break-even occupancy
    # At break-even: EGI - OpEx = Mortgage
    # (Gross Rent * Occupancy) - OpEx = Mortgage
    # Occupancy = (Mortgage + OpEx) / Gross Rent
    if gross_annual_rent > 0:
        break_even_occupancy = (
            (annual_mortgage + total_operating_expenses) / gross_annual_rent
        ).quantize(Decimal("0.0001"))
    else:
        break_even_occupancy = Decimal("1")
    
    # Calculate opportunity score
    from ..scoring.opportunity_scorer import score_opportunity
    score, score_breakdown = score_opportunity(
        cap_rate=cap_rate,
        cash_on_cash=cash_on_cash,
        monthly_cash_flow=monthly_cash_flow,
        debt_coverage_ratio=debt_coverage_ratio,
        gross_rent_multiplier=gross_rent_multiplier,
    )
    
    return ROIAnalysis(
        property_price=scenario.property_price,
        total_purchase_cost=total_purchase_cost,
        down_payment=down_payment,
        closing_costs=closing_costs,
        loan_amount=loan_amount,
        monthly_mortgage=monthly_mortgage,
        annual_mortgage=annual_mortgage,
        mortgage_details=mortgage,
        gross_annual_rent=gross_annual_rent,
        vacancy_loss=vacancy_loss,
        effective_gross_income=effective_gross_income,
        operating_expenses=operating_expenses,
        total_operating_expenses=total_operating_expenses,
        net_operating_income=net_operating_income,
        annual_cash_flow=annual_cash_flow,
        monthly_cash_flow=monthly_cash_flow.quantize(Decimal("0.01")),
        cap_rate=cap_rate,
        cash_on_cash_return=cash_on_cash,
        gross_rent_multiplier=gross_rent_multiplier,
        opportunity_score=score,
        score_breakdown=score_breakdown,
        break_even_occupancy=break_even_occupancy,
        debt_coverage_ratio=debt_coverage_ratio,
    )


def compare_scenarios(scenarios: list[InvestmentScenario]) -> list[ROIAnalysis]:
    """
    Analyze and compare multiple investment scenarios.
    
    Args:
        scenarios: List of investment scenarios to compare
        
    Returns:
        List of ROIAnalysis results, sorted by opportunity score
        
    Example:
        >>> scenarios = [
        ...     InvestmentScenario(property_price=300000, monthly_rent=1400, location="mosta"),
        ...     InvestmentScenario(property_price=350000, monthly_rent=1600, location="sliema"),
        ... ]
        >>> results = compare_scenarios(scenarios)
    """
    results = [calculate_roi(s) for s in scenarios]
    return sorted(results, key=lambda x: x.opportunity_score, reverse=True)
