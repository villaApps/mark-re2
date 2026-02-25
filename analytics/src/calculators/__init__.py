"""Financial calculators for property investment analysis."""

from .roi_calculator import (
    calculate_purchase_costs,
    calculate_mortgage_payment,
    calculate_total_interest,
    calculate_cap_rate,
    calculate_cash_on_cash_return,
    calculate_price_to_rent_ratio,
    calculate_irr,
    analyze_investment,
)

from .rental_yield import (
    calculate_gross_rental_yield,
    calculate_net_rental_yield,
    estimate_market_rent,
)

from .cash_flow import (
    calculate_cash_flow,
    calculate_net_operating_income,
    calculate_operating_expenses,
    calculate_effective_gross_income,
)

from .projections import (
    project_10_year_returns,
    calculate_loan_balance,
    calculate_equity_buildup,
    project_annual_rent,
)

__all__ = [
    # ROI Calculator
    "calculate_purchase_costs",
    "calculate_mortgage_payment",
    "calculate_total_interest",
    "calculate_cap_rate",
    "calculate_cash_on_cash_return",
    "calculate_price_to_rent_ratio",
    "calculate_irr",
    "analyze_investment",
    
    # Rental Yield
    "calculate_gross_rental_yield",
    "calculate_net_rental_yield",
    "estimate_market_rent",
    
    # Cash Flow
    "calculate_cash_flow",
    "calculate_net_operating_income",
    "calculate_operating_expenses",
    "calculate_effective_gross_income",
    
    # Projections
    "project_10_year_returns",
    "calculate_loan_balance",
    "calculate_equity_buildup",
    "project_annual_rent",
]
