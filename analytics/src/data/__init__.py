"""Malta property market data and constants."""

from .malta_market import (
    # Purchase costs
    STAMP_DUTY_FIRST_TIME,
    STAMP_DUTY_SECOND_TIME,
    STAMP_DUTY_FIRST_TIME_THRESHOLD,
    NOTARY_FEES,
    AGENCY_FEES_BUYER,
    REGISTRATION_FEES,
    
    # Rental yields by area
    RENTAL_YIELDS,
    
    # Operating expenses
    PROPERTY_MANAGEMENT,
    MAINTENANCE_RESERVE,
    INSURANCE_ANNUAL,
    PROPERTY_TAX,
    
    # Location desirability scores
    LOCATION_DESIRABILITY,
    
    # Market trends
    HISTORICAL_APPRECIATION,
    INFLATION_RATE,
    
    # Financing
    TYPICAL_INTEREST_RATE,
    TYPICAL_LOAN_TERM,
    MIN_DOWN_PAYMENT,
    
    # Helper functions
    get_rental_yield_for_area,
    get_location_score,
    calculate_total_purchase_cost_percentage,
)

__all__ = [
    "STAMP_DUTY_FIRST_TIME",
    "STAMP_DUTY_SECOND_TIME",
    "STAMP_DUTY_FIRST_TIME_THRESHOLD",
    "NOTARY_FEES",
    "AGENCY_FEES_BUYER",
    "REGISTRATION_FEES",
    "RENTAL_YIELDS",
    "PROPERTY_MANAGEMENT",
    "MAINTENANCE_RESERVE",
    "INSURANCE_ANNUAL",
    "PROPERTY_TAX",
    "LOCATION_DESIRABILITY",
    "HISTORICAL_APPRECIATION",
    "INFLATION_RATE",
    "TYPICAL_INTEREST_RATE",
    "TYPICAL_LOAN_TERM",
    "MIN_DOWN_PAYMENT",
    "get_rental_yield_for_area",
    "get_location_score",
    "calculate_total_purchase_cost_percentage",
]
