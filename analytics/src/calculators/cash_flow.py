"""Cash flow calculations for property investments."""

from decimal import Decimal
from typing import Optional

from ..data.malta_market import (
    INSURANCE_ANNUAL,
    MAINTENANCE_RESERVE,
    PROPERTY_MANAGEMENT,
    PROPERTY_TAX,
)
from ..models.analysis import CashFlowBreakdown
from ..models.investment import InvestmentScenario


DECIMAL_PRECISION = Decimal("0.01")


def calculate_effective_gross_income(
    monthly_rent: Decimal,
    vacancy_rate: Decimal = Decimal("0.05"),
) -> Decimal:
    """Calculate Effective Gross Income (EGI).
    
    EGI = Gross Potential Income - Vacancy Loss
    
    This represents the actual expected rental income after accounting
    for periods when the property may be vacant.
    
    Args:
        monthly_rent: Monthly rental income
        vacancy_rate: Expected vacancy rate (default 5%)
        
    Returns:
        Annual effective gross income
        
    Raises:
        ValueError: If monthly rent is negative
        
    Example:
        >>> egi = calculate_effective_gross_income(Decimal("1200"), Decimal("0.05"))
        >>> print(egi)
        13680.00
    """
    if monthly_rent < Decimal("0"):
        raise ValueError("Monthly rent cannot be negative")
    if vacancy_rate < Decimal("0") or vacancy_rate > Decimal("1"):
        raise ValueError("Vacancy rate must be between 0 and 1")
    
    annual_rent = monthly_rent * Decimal("12")
    return (annual_rent * (Decimal("1") - vacancy_rate)).quantize(DECIMAL_PRECISION)


def calculate_operating_expenses(
    effective_gross_income: Decimal,
    property_value: Decimal,
    property_management_percent: Decimal = PROPERTY_MANAGEMENT,
    maintenance_reserve_percent: Decimal = MAINTENANCE_RESERVE,
    insurance_annual_percent: Decimal = INSURANCE_ANNUAL,
    property_tax_percent: Decimal = PROPERTY_TAX,
    other_expenses: Decimal = Decimal("0"),
) -> dict[str, Decimal]:
    """Calculate all operating expenses.
    
    Args:
        effective_gross_income: Annual EGI
        property_value: Property value (for insurance calculation)
        property_management_percent: Property management fee %
        maintenance_reserve_percent: Maintenance reserve %
        insurance_annual_percent: Annual insurance % of property value
        property_tax_percent: Property tax % (0% in Malta)
        other_expenses: Other operating expenses
        
    Returns:
        Dictionary with expense breakdown
        
    Example:
        >>> expenses = calculate_operating_expenses(
        ...     Decimal("13680"),
        ...     Decimal("300000"),
        ... )
        >>> print(expenses['total'])
        2952.00
    """
    if effective_gross_income < Decimal("0"):
        raise ValueError("Effective gross income cannot be negative")
    if property_value < Decimal("0"):
        raise ValueError("Property value cannot be negative")
    
    property_management = (effective_gross_income * property_management_percent).quantize(DECIMAL_PRECISION)
    maintenance_reserve = (effective_gross_income * maintenance_reserve_percent).quantize(DECIMAL_PRECISION)
    insurance = (property_value * insurance_annual_percent).quantize(DECIMAL_PRECISION)
    property_tax = (effective_gross_income * property_tax_percent).quantize(DECIMAL_PRECISION)
    
    total = (
        property_management +
        maintenance_reserve +
        insurance +
        property_tax +
        other_expenses
    )
    
    return {
        "property_management": property_management,
        "maintenance_reserve": maintenance_reserve,
        "insurance": insurance,
        "property_tax": property_tax,
        "other_expenses": other_expenses,
        "total": total,
    }


def calculate_net_operating_income(
    effective_gross_income: Decimal,
    operating_expenses: Decimal,
) -> Decimal:
    """Calculate Net Operating Income (NOI).
    
    NOI = Effective Gross Income - Operating Expenses
    
    This is a key metric representing the property's ability to
    generate income before financing costs.
    
    Args:
        effective_gross_income: Annual EGI
        operating_expenses: Total annual operating expenses
        
    Returns:
        Net operating income
        
    Example:
        >>> noi = calculate_net_operating_income(Decimal("13680"), Decimal("2952"))
        >>> print(noi)
        10728.00
    """
    return (effective_gross_income - operating_expenses).quantize(DECIMAL_PRECISION)


def calculate_cash_flow(
    scenario: InvestmentScenario,
    monthly_mortgage_payment: Optional[Decimal] = None,
) -> CashFlowBreakdown:
    """Calculate complete cash flow breakdown for an investment scenario.
    
    This is the main cash flow calculation function that computes all
    components of property cash flow.
    
    Args:
        scenario: InvestmentScenario with all inputs
        monthly_mortgage_payment: Pre-calculated mortgage payment (optional)
        
    Returns:
        CashFlowBreakdown with all cash flow components
        
    Example:
        >>> from ..models.investment import InvestmentScenario
        >>> scenario = InvestmentScenario(
        ...     property_price=Decimal("300000"),
        ...     monthly_rent=Decimal("1200"),
        ... )
        >>> cash_flow = calculate_cash_flow(scenario)
        >>> print(cash_flow.annual_cash_flow)
    """
    # Calculate gross potential income
    gross_annual_rent = scenario.monthly_rent * Decimal("12")
    
    # Calculate vacancy loss
    vacancy_loss = (gross_annual_rent * scenario.vacancy_rate).quantize(DECIMAL_PRECISION)
    
    # Calculate effective gross income
    effective_gross_income = calculate_effective_gross_income(
        scenario.monthly_rent,
        scenario.vacancy_rate,
    )
    
    # Calculate operating expenses
    expenses = calculate_operating_expenses(
        effective_gross_income=effective_gross_income,
        property_value=scenario.property_price,
        property_management_percent=scenario.property_management_percent,
        maintenance_reserve_percent=scenario.maintenance_reserve_percent,
        insurance_annual_percent=scenario.insurance_annual_percent,
        property_tax_percent=PROPERTY_TAX,
    )
    
    # Calculate NOI
    noi = calculate_net_operating_income(
        effective_gross_income,
        expenses["total"],
    )
    
    # Calculate mortgage payment if not provided
    if monthly_mortgage_payment is None:
        from .roi_calculator import calculate_mortgage_payment
        monthly_mortgage_payment = calculate_mortgage_payment(
            scenario.loan_amount,
            scenario.loan_interest_rate,
            scenario.loan_term_years,
        )
    
    annual_mortgage = monthly_mortgage_payment * Decimal("12")
    
    # Calculate cash flow
    annual_cash_flow = noi - annual_mortgage
    monthly_cash_flow = annual_cash_flow / Decimal("12")
    
    return CashFlowBreakdown(
        gross_annual_rent=gross_annual_rent,
        vacancy_loss=vacancy_loss,
        effective_gross_income=effective_gross_income,
        property_management=expenses["property_management"],
        maintenance_reserve=expenses["maintenance_reserve"],
        insurance=expenses["insurance"],
        property_tax=expenses["property_tax"],
        other_expenses=expenses["other_expenses"],
        net_operating_income=noi,
        annual_mortgage_payment=annual_mortgage,
        annual_cash_flow=annual_cash_flow.quantize(DECIMAL_PRECISION),
        monthly_cash_flow=monthly_cash_flow.quantize(DECIMAL_PRECISION),
    )


def calculate_debt_service_coverage_ratio(
    net_operating_income: Decimal,
    annual_mortgage_payment: Decimal,
) -> Decimal:
    """Calculate Debt Service Coverage Ratio (DSCR).
    
    DSCR = Net Operating Income / Annual Debt Service
    
    This ratio measures the property's ability to cover mortgage payments.
    - DSCR > 1.25: Generally considered good
    - DSCR < 1.0: Property doesn't generate enough income to cover mortgage
    
    Args:
        net_operating_income: Annual NOI
        annual_mortgage_payment: Annual mortgage payment (principal + interest)
        
    Returns:
        DSCR as a decimal
        
    Raises:
        ValueError: If mortgage payment is zero or negative
        
    Example:
        >>> dscr = calculate_debt_service_coverage_ratio(
        ...     Decimal("15000"),
        ...     Decimal("12000"),
        ... )
        >>> print(dscr)
        1.25
    """
    if annual_mortgage_payment <= Decimal("0"):
        raise ValueError("Annual mortgage payment must be positive")
    
    return (net_operating_income / annual_mortgage_payment).quantize(Decimal("0.01"))


def calculate_operating_expense_ratio(
    operating_expenses: Decimal,
    effective_gross_income: Decimal,
) -> Decimal:
    """Calculate Operating Expense Ratio (OER).
    
    OER = Operating Expenses / Effective Gross Income
    
    This shows what percentage of income is consumed by operating expenses.
    - Typical range: 25-50% for residential properties
    - Lower is generally better
    
    Args:
        operating_expenses: Total operating expenses
        effective_gross_income: Annual EGI
        
    Returns:
        OER as a decimal
        
    Raises:
        ValueError: If EGI is zero or negative
        
    Example:
        >>> oer = calculate_operating_expense_ratio(
        ...     Decimal("5000"),
        ...     Decimal("20000"),
        ... )
        >>> print(oer)
        0.25
    """
    if effective_gross_income <= Decimal("0"):
        raise ValueError("Effective gross income must be positive")
    
    return (operating_expenses / effective_gross_income).quantize(Decimal("0.0001"))


def project_cash_flow(
    monthly_rent: Decimal,
    property_value: Decimal,
    monthly_mortgage: Decimal,
    years: int = 10,
    annual_rent_growth: Decimal = Decimal("0.025"),
    annual_expense_growth: Decimal = Decimal("0.02"),
    vacancy_rate: Decimal = Decimal("0.05"),
) -> list[Decimal]:
    """Project cash flows over multiple years.
    
    Args:
        monthly_rent: Starting monthly rent
        property_value: Property value (for insurance)
        monthly_mortgage: Monthly mortgage payment (assumed constant)
        years: Number of years to project
        annual_rent_growth: Annual rent growth rate
        annual_expense_growth: Annual expense growth rate
        vacancy_rate: Vacancy rate
        
    Returns:
        List of annual cash flows for each year
        
    Example:
        >>> cash_flows = project_cash_flow(
        ...     Decimal("1200"),
        ...     Decimal("300000"),
        ...     Decimal("1000"),
        ...     years=5,
        ... )
        >>> print([float(cf) for cf in cash_flows])
    """
    cash_flows = []
    current_rent = monthly_rent
    
    for year in range(1, years + 1):
        # Calculate EGI
        egi = calculate_effective_gross_income(current_rent, vacancy_rate)
        
        # Calculate expenses with growth
        expenses = calculate_operating_expenses(
            egi,
            property_value,
        )
        # Add expense growth for subsequent years
        if year > 1:
            growth_factor = (Decimal("1") + annual_expense_growth) ** (year - 1)
            expenses["total"] = (expenses["total"] * growth_factor).quantize(DECIMAL_PRECISION)
        
        # Calculate NOI
        noi = calculate_net_operating_income(egi, expenses["total"])
        
        # Calculate cash flow
        annual_mortgage = monthly_mortgage * Decimal("12")
        cash_flow = noi - annual_mortgage
        cash_flows.append(cash_flow)
        
        # Grow rent for next year
        current_rent = (current_rent * (Decimal("1") + annual_rent_growth)).quantize(DECIMAL_PRECISION)
    
    return cash_flows
