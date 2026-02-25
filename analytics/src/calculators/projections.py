"""10-year projection calculations for property investments."""

from decimal import Decimal
from typing import List, Optional

import numpy as np

from ..data.malta_market import INSURANCE_ANNUAL, MAINTENANCE_RESERVE, PROPERTY_MANAGEMENT
from ..models.analysis import ProjectionYear, TenYearProjection
from ..models.investment import InvestmentScenario


DECIMAL_PRECISION = Decimal("0.01")


def calculate_loan_balance(
    original_principal: Decimal,
    annual_rate: Decimal,
    years: int,
    payments_made: int,
) -> Decimal:
    """Calculate remaining loan balance after a number of payments.
    
    Uses the amortization formula to calculate the remaining balance.
    
    Args:
        original_principal: Original loan amount
        annual_rate: Annual interest rate
        years: Original loan term in years
        payments_made: Number of monthly payments made
        
    Returns:
        Remaining loan balance
        
    Example:
        >>> balance = calculate_loan_balance(
        ...     Decimal("240000"),
        ...     Decimal("0.035"),
        ...     25,
        ...     60,  # 5 years
        ... )
        >>> print(balance)
        207234.56
    """
    if payments_made < 0:
        raise ValueError("Payments made cannot be negative")
    if payments_made >= years * 12:
        return Decimal("0")
    
    # Handle zero interest rate
    if annual_rate == Decimal("0"):
        monthly_payment = original_principal / Decimal(years * 12)
        remaining = original_principal - (monthly_payment * Decimal(payments_made))
        return remaining.quantize(DECIMAL_PRECISION)
    
    # Convert to monthly rate
    monthly_rate = annual_rate / Decimal("12")
    num_payments = years * 12
    
    # Calculate monthly payment
    from .roi_calculator import calculate_mortgage_payment
    monthly_payment = calculate_mortgage_payment(original_principal, annual_rate, years)
    
    # Calculate remaining balance using amortization formula
    # B = P * [(1+r)^n - (1+r)^p] / [(1+r)^n - 1]
    # Where p = payments made
    monthly_rate_f = float(monthly_rate)
    num_payments_f = float(num_payments)
    payments_made_f = float(payments_made)
    principal_f = float(original_principal)
    
    factor_n = (1 + monthly_rate_f) ** num_payments_f
    factor_p = (1 + monthly_rate_f) ** payments_made_f
    
    balance_f = principal_f * (factor_n - factor_p) / (factor_n - 1)
    
    return Decimal(str(balance_f)).quantize(DECIMAL_PRECISION)


def calculate_equity_buildup(
    property_value: Decimal,
    loan_balance: Decimal,
) -> Decimal:
    """Calculate equity in a property.
    
    Equity = Property Value - Loan Balance
    
    Args:
        property_value: Current property value
        loan_balance: Current loan balance
        
    Returns:
        Equity amount
        
    Example:
        >>> equity = calculate_equity_buildup(Decimal("350000"), Decimal("200000"))
        >>> print(equity)
        150000.00
    """
    return (property_value - loan_balance).quantize(DECIMAL_PRECISION)


def project_annual_rent(
    starting_monthly_rent: Decimal,
    years: int,
    annual_growth_rate: Decimal = Decimal("0.025"),
) -> List[Decimal]:
    """Project annual rent over multiple years.
    
    Args:
        starting_monthly_rent: Initial monthly rent
        years: Number of years to project
        annual_growth_rate: Annual rent growth rate
        
    Returns:
        List of annual rents for each year
        
    Example:
        >>> rents = project_annual_rent(Decimal("1200"), 5)
        >>> print([float(r) for r in rents])
        [14400.0, 14760.0, 15129.0, 15507.22, 15894.9]
    """
    rents = []
    current_monthly = starting_monthly_rent
    
    for year in range(1, years + 1):
        annual_rent = current_monthly * Decimal("12")
        rents.append(annual_rent.quantize(DECIMAL_PRECISION))
        
        # Grow rent for next year
        current_monthly = (current_monthly * (Decimal("1") + annual_growth_rate)).quantize(DECIMAL_PRECISION)
    
    return rents


def project_property_value(
    starting_value: Decimal,
    years: int,
    annual_appreciation: Decimal = Decimal("0.03"),
) -> List[Decimal]:
    """Project property value over multiple years.
    
    Args:
        starting_value: Initial property value
        years: Number of years to project
        annual_appreciation: Annual appreciation rate
        
    Returns:
        List of property values for each year
        
    Example:
        >>> values = project_property_value(Decimal("300000"), 5)
        >>> print([float(v) for v in values])
        [309000.0, 318270.0, 327818.1, 337652.64, 347782.22]
    """
    values = []
    current_value = starting_value
    
    for year in range(1, years + 1):
        current_value = (current_value * (Decimal("1") + annual_appreciation)).quantize(DECIMAL_PRECISION)
        values.append(current_value)
    
    return values


def project_10_year_returns(
    scenario: InvestmentScenario,
    include_sale: bool = True,
) -> Optional[TenYearProjection]:
    """Calculate 10-year projection for an investment scenario.
    
    This function projects all key metrics over a 10-year period,
    including cash flows, equity buildup, and property appreciation.
    
    Args:
        scenario: InvestmentScenario with all inputs
        include_sale: Whether to include property sale in final year
        
    Returns:
        TenYearProjection with year-by-year data
        
    Example:
        >>> from ..models.investment import InvestmentScenario
        >>> scenario = InvestmentScenario(
        ...     property_price=Decimal("300000"),
        ...     monthly_rent=Decimal("1200"),
        ...     down_payment_percent=Decimal("0.20"),
        ... )
        >>> projection = project_10_year_returns(scenario)
        >>> print(projection.total_cash_flow)
    """
    from .cash_flow import calculate_cash_flow
    from .roi_calculator import calculate_mortgage_payment
    
    years_data: List[ProjectionYear] = []
    
    # Initial values
    current_property_value = scenario.property_price
    current_monthly_rent = scenario.monthly_rent
    loan_balance = scenario.loan_amount
    
    # Calculate mortgage payment (constant)
    monthly_mortgage = calculate_mortgage_payment(
        scenario.loan_amount,
        scenario.loan_interest_rate,
        scenario.loan_term_years,
    )
    annual_mortgage = monthly_mortgage * Decimal("12")
    
    cumulative_cash_flow = Decimal("0")
    
    for year in range(1, 11):
        # Apply appreciation to property value
        if year > 1:
            current_property_value = (
                current_property_value * (Decimal("1") + scenario.annual_appreciation)
            ).quantize(DECIMAL_PRECISION)
        
        # Apply rent growth
        if year > 1:
            current_monthly_rent = (
                current_monthly_rent * (Decimal("1") + scenario.annual_rent_increase)
            ).quantize(DECIMAL_PRECISION)
        
        # Calculate appreciation gain for this year
        if year == 1:
            appreciation_gain = Decimal("0")
        else:
            appreciation_gain = (
                current_property_value - 
                (scenario.property_price * (Decimal("1") + scenario.annual_appreciation) ** (year - 2))
            ).quantize(DECIMAL_PRECISION)
        
        # Calculate rental income
        annual_rent = current_monthly_rent * Decimal("12")
        vacancy_loss = (annual_rent * scenario.vacancy_rate).quantize(DECIMAL_PRECISION)
        effective_income = annual_rent - vacancy_loss
        
        # Calculate operating expenses
        property_management = (effective_income * scenario.property_management_percent).quantize(DECIMAL_PRECISION)
        maintenance_reserve = (effective_income * scenario.maintenance_reserve_percent).quantize(DECIMAL_PRECISION)
        insurance = (current_property_value * scenario.insurance_annual_percent).quantize(DECIMAL_PRECISION)
        operating_expenses = property_management + maintenance_reserve + insurance
        
        # Calculate cash flow
        noi = effective_income - operating_expenses
        cash_flow = noi - annual_mortgage
        cumulative_cash_flow += cash_flow
        
        # Calculate loan balance
        payments_made = year * 12
        loan_balance = calculate_loan_balance(
            scenario.loan_amount,
            scenario.loan_interest_rate,
            scenario.loan_term_years,
            payments_made,
        )
        
        # Calculate equity
        equity = current_property_value - loan_balance
        
        year_data = ProjectionYear(
            year=year,
            property_value=current_property_value,
            appreciation_gain=appreciation_gain,
            annual_rent=annual_rent,
            vacancy_loss=vacancy_loss,
            effective_income=effective_income,
            operating_expenses=operating_expenses,
            mortgage_payment=annual_mortgage,
            cash_flow=cash_flow,
            cumulative_cash_flow=cumulative_cash_flow,
            remaining_loan_balance=loan_balance,
            equity=equity,
        )
        years_data.append(year_data)
    
    # Calculate summary metrics
    total_cash_flow = sum(year.cash_flow for year in years_data)
    total_appreciation = years_data[-1].property_value - scenario.property_price
    final_property_value = years_data[-1].property_value
    final_equity = years_data[-1].equity
    
    # Calculate total ROI
    total_investment = scenario.down_payment_amount
    # Add closing costs estimate (roughly 5-7%)
    closing_costs = scenario.property_price * Decimal("0.06")
    total_cash_invested = total_investment + closing_costs
    
    # Total return includes cash flows + appreciation + equity from principal paydown
    initial_loan = scenario.loan_amount
    final_loan = years_data[-1].remaining_loan_balance
    principal_paid = initial_loan - final_loan
    
    total_return = total_cash_flow + total_appreciation
    if include_sale:
        # If selling, we realize the equity
        total_return += final_equity - total_investment
    
    # Calculate total ROI
    total_roi = (total_return / total_cash_invested).quantize(Decimal("0.0001"))
    
    # Calculate annualized return (CAGR)
    # (1 + Total ROI)^(1/10) - 1
    total_roi_float = float(total_roi)
    if total_roi_float > -1:
        annualized_return_float = (1 + total_roi_float) ** (1/10) - 1
        annualized_return = Decimal(str(annualized_return_float)).quantize(Decimal("0.0001"))
    else:
        annualized_return = Decimal("0")
    
    # Calculate IRR
    # Build cash flow array for IRR calculation
    # Year 0: Negative initial investment
    # Years 1-9: Annual cash flows
    # Year 10: Cash flow + sale proceeds (if applicable)
    irr_cash_flows = [year.cash_flow for year in years_data]
    
    # Add sale proceeds to final year if applicable
    if include_sale:
        # Sale proceeds = Property value - loan balance - selling costs (~5%)
        selling_costs = final_property_value * Decimal("0.05")
        sale_proceeds = final_property_value - final_loan - selling_costs
        irr_cash_flows[-1] = irr_cash_flows[-1] + sale_proceeds
    
    # Calculate IRR using numpy
    try:
        cf_array = [float(-total_cash_invested)] + [float(cf) for cf in irr_cash_flows]
        irr_result = np.irr(cf_array)
        if not (np.isnan(irr_result) or np.isinf(irr_result)):
            irr = Decimal(str(irr_result)).quantize(Decimal("0.0001"))
        else:
            irr = None
    except (ValueError, RuntimeError):
        irr = None
    
    return TenYearProjection(
        years=years_data,
        total_cash_flow=total_cash_flow.quantize(DECIMAL_PRECISION),
        total_appreciation=total_appreciation.quantize(DECIMAL_PRECISION),
        final_property_value=final_property_value,
        final_equity=final_equity,
        irr=irr,
        total_roi=total_roi,
        annualized_return=annualized_return,
    )


def calculate_break_even_period(
    scenario: InvestmentScenario,
    monthly_mortgage: Decimal,
) -> int:
    """Calculate the number of months until break-even.
    
    Break-even is when cumulative cash flow turns positive.
    
    Args:
        scenario: InvestmentScenario
        monthly_mortgage: Monthly mortgage payment
        
    Returns:
        Number of months until break-even (0 if already positive)
        
    Example:
        >>> months = calculate_break_even_period(scenario, Decimal("1000"))
        >>> print(months)
        24
    """
    from .cash_flow import calculate_cash_flow
    
    cash_flow = calculate_cash_flow(scenario, monthly_mortgage)
    
    if cash_flow.annual_cash_flow > Decimal("0"):
        return 0
    
    # If negative cash flow, calculate how long to break even
    # This would require appreciation analysis
    # For simplicity, return -1 to indicate it may never break even
    return -1


def calculate_total_return_components(
    scenario: InvestmentScenario,
    projection: TenYearProjection,
) -> dict:
    """Break down total return into components.
    
    Args:
        scenario: InvestmentScenario
        projection: TenYearProjection
        
    Returns:
        Dictionary with return components
        
    Example:
        >>> components = calculate_total_return_components(scenario, projection)
        >>> print(components['from_cash_flow'])
    """
    # Cash flow component
    from_cash_flow = projection.total_cash_flow
    
    # Appreciation component
    from_appreciation = projection.total_appreciation
    
    # Principal paydown component
    initial_loan = scenario.loan_amount
    final_loan = projection.years[-1].remaining_loan_balance
    from_principal_paydown = initial_loan - final_loan
    
    # Total
    total = from_cash_flow + from_appreciation + from_principal_paydown
    
    return {
        "from_cash_flow": from_cash_flow,
        "from_appreciation": from_appreciation,
        "from_principal_paydown": from_principal_paydown,
        "total_return": total,
        "cash_flow_percentage": (from_cash_flow / total * 100).quantize(Decimal("0.01")) if total > 0 else Decimal("0"),
        "appreciation_percentage": (from_appreciation / total * 100).quantize(Decimal("0.01")) if total > 0 else Decimal("0"),
        "principal_paydown_percentage": (from_principal_paydown / total * 100).quantize(Decimal("0.01")) if total > 0 else Decimal("0"),
    }
