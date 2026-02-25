"""Rental yield calculations for property investments."""

from decimal import Decimal
from typing import Optional

from ..data.malta_market import (
    INSURANCE_ANNUAL,
    MAINTENANCE_RESERVE,
    PROPERTY_MANAGEMENT,
    get_rental_yield_for_area,
)


DECIMAL_PRECISION = Decimal("0.01")


def calculate_gross_rental_yield(
    property_price: Decimal,
    monthly_rent: Decimal,
) -> Decimal:
    """Calculate Gross Rental Yield.
    
    Gross Rental Yield = (Monthly Rent × 12) / Property Price
    
    This is the simplest yield calculation, showing the raw return
    before any expenses are deducted.
    
    Args:
        property_price: Property purchase price
        monthly_rent: Monthly rental income
        
    Returns:
        Gross rental yield as a decimal (e.g., 0.055 for 5.5%)
        
    Raises:
        ValueError: If property price is not positive or rent is negative
        
    Example:
        >>> yield_rate = calculate_gross_rental_yield(Decimal("300000"), Decimal("1250"))
        >>> print(yield_rate)
        0.0500
    """
    if property_price <= Decimal("0"):
        raise ValueError("Property price must be positive")
    if monthly_rent < Decimal("0"):
        raise ValueError("Monthly rent cannot be negative")
    
    annual_rent = monthly_rent * Decimal("12")
    return (annual_rent / property_price).quantize(Decimal("0.0001"))


def calculate_net_rental_yield(
    property_price: Decimal,
    monthly_rent: Decimal,
    vacancy_rate: Decimal = Decimal("0.05"),
    property_management_percent: Decimal = PROPERTY_MANAGEMENT,
    maintenance_reserve_percent: Decimal = MAINTENANCE_RESERVE,
    insurance_annual_percent: Decimal = INSURANCE_ANNUAL,
) -> Decimal:
    """Calculate Net Rental Yield.
    
    Net Rental Yield = (Annual Rent - Operating Expenses) / Property Price
    
    This provides a more realistic yield by accounting for common
    operating expenses.
    
    Args:
        property_price: Property purchase price
        monthly_rent: Monthly rental income
        vacancy_rate: Expected vacancy rate (default 5%)
        property_management_percent: Property management fee % (default 10%)
        maintenance_reserve_percent: Maintenance reserve % (default 5%)
        insurance_annual_percent: Annual insurance % of property value (default 0.3%)
        
    Returns:
        Net rental yield as a decimal
        
    Raises:
        ValueError: If property price is not positive
        
    Example:
        >>> net_yield = calculate_net_rental_yield(
        ...     Decimal("300000"),
        ...     Decimal("1250"),
        ...     vacancy_rate=Decimal("0.05"),
        ... )
        >>> print(net_yield)
        0.0385
    """
    if property_price <= Decimal("0"):
        raise ValueError("Property price must be positive")
    if monthly_rent < Decimal("0"):
        raise ValueError("Monthly rent cannot be negative")
    
    # Calculate annual figures
    annual_rent = monthly_rent * Decimal("12")
    
    # Account for vacancy
    effective_gross_income = annual_rent * (Decimal("1") - vacancy_rate)
    
    # Calculate operating expenses
    property_management = effective_gross_income * property_management_percent
    maintenance_reserve = effective_gross_income * maintenance_reserve_percent
    insurance = property_price * insurance_annual_percent
    
    # Net operating income
    noi = effective_gross_income - property_management - maintenance_reserve - insurance
    
    return (noi / property_price).quantize(Decimal("0.0001"))


def estimate_market_rent(
    property_price: Decimal,
    area: Optional[str] = None,
    target_yield: Optional[Decimal] = None,
) -> Decimal:
    """Estimate expected market rent based on property price and area.
    
    This function can estimate rent either:
    1. Using area-specific rental yields from market data
    2. Using a provided target yield
    
    Args:
        property_price: Property purchase price
        area: Area/locality in Malta (optional)
        target_yield: Target annual yield (optional, overrides area)
        
    Returns:
        Estimated monthly rent
        
    Raises:
        ValueError: If neither area nor target_yield is provided
        
    Example:
        >>> # Using area-specific yield
        >>> rent = estimate_market_rent(Decimal("300000"), area="sliema")
        >>> print(rent)
        1125.00
        
        >>> # Using target yield
        >>> rent = estimate_market_rent(Decimal("300000"), target_yield=Decimal("0.05"))
        >>> print(rent)
        1250.00
    """
    if property_price <= Decimal("0"):
        raise ValueError("Property price must be positive")
    
    # Determine the yield to use
    if target_yield is not None:
        yield_rate = target_yield
    elif area is not None:
        try:
            yield_rate = get_rental_yield_for_area(area)
        except ValueError:
            # If area not found, use a default yield
            yield_rate = Decimal("0.05")  # 5% default
    else:
        raise ValueError("Either area or target_yield must be provided")
    
    # Calculate monthly rent: (Price * Yield) / 12
    annual_rent = property_price * yield_rate
    monthly_rent = annual_rent / Decimal("12")
    
    return monthly_rent.quantize(DECIMAL_PRECISION)


def calculate_yield_range(
    property_price: Decimal,
    monthly_rent: Decimal,
    vacancy_scenarios: list[Decimal] = None,
) -> dict[str, Decimal]:
    """Calculate rental yield under different vacancy scenarios.
    
    Args:
        property_price: Property purchase price
        monthly_rent: Monthly rental income
        vacancy_scenarios: List of vacancy rates to test (default: 0%, 5%, 10%, 15%)
        
    Returns:
        Dictionary mapping vacancy rate to net yield
        
    Example:
        >>> yields = calculate_yield_range(Decimal("300000"), Decimal("1250"))
        >>> print(yields)
        {'0%': Decimal('0.0458'), '5%': Decimal('0.0435'), '10%': Decimal('0.0412'), '15%': Decimal('0.0389')}
    """
    if vacancy_scenarios is None:
        vacancy_scenarios = [
            Decimal("0"),
            Decimal("0.05"),
            Decimal("0.10"),
            Decimal("0.15"),
        ]
    
    results = {}
    for vacancy in vacancy_scenarios:
        net_yield = calculate_net_rental_yield(
            property_price,
            monthly_rent,
            vacancy_rate=vacancy,
        )
        key = f"{int(vacancy * 100)}%"
        results[key] = net_yield
    
    return results


def compare_yields(
    property_price: Decimal,
    monthly_rent: Decimal,
    benchmark_yield: Decimal = Decimal("0.05"),
) -> dict:
    """Compare property yield against a benchmark.
    
    Args:
        property_price: Property purchase price
        monthly_rent: Monthly rental income
        benchmark_yield: Benchmark yield to compare against (default 5%)
        
    Returns:
        Dictionary with comparison results
        
    Example:
        >>> comparison = compare_yields(Decimal("300000"), Decimal("1250"))
        >>> print(comparison['difference_pct'])
        0.0
    """
    gross_yield = calculate_gross_rental_yield(property_price, monthly_rent)
    net_yield = calculate_net_rental_yield(property_price, monthly_rent)
    
    difference = gross_yield - benchmark_yield
    difference_pct = (difference / benchmark_yield) * Decimal("100")
    
    return {
        "gross_yield": gross_yield,
        "net_yield": net_yield,
        "benchmark_yield": benchmark_yield,
        "difference": difference,
        "difference_pct": difference_pct,
        "meets_benchmark": gross_yield >= benchmark_yield,
    }


def calculate_break_even_rent(
    property_price: Decimal,
    operating_expense_ratio: Decimal = Decimal("0.25"),
    target_yield: Decimal = Decimal("0.05"),
) -> Decimal:
    """Calculate the rent needed to achieve a target yield.
    
    Args:
        property_price: Property purchase price
        operating_expense_ratio: Expected operating expenses as % of rent
        target_yield: Target annual yield
        
    Returns:
        Required monthly rent
        
    Example:
        >>> rent = calculate_break_even_rent(Decimal("300000"), target_yield=Decimal("0.05"))
        >>> print(rent)
        1666.67
    """
    if property_price <= Decimal("0"):
        raise ValueError("Property price must be positive")
    if target_yield <= Decimal("0"):
        raise ValueError("Target yield must be positive")
    
    # Target annual income = Price * Target Yield
    target_annual_income = property_price * target_yield
    
    # Account for operating expenses: NOI = Rent * (1 - OpEx%)
    # So: Rent = NOI / (1 - OpEx%)
    required_annual_rent = target_annual_income / (Decimal("1") - operating_expense_ratio)
    
    return (required_annual_rent / Decimal("12")).quantize(DECIMAL_PRECISION)
