"""Data module for Malta market constants."""

from .malta_market import (
    STAMP_DUTY_FIRST,
    STAMP_DUTY_REST,
    NOTARY_FEES,
    AGENCY_FEES,
    REGISTRATION_FEES,
    RENTAL_YIELDS,
    DEFAULT_RENTAL_YIELD,
    get_rental_yield,
    estimate_monthly_rent,
)

__all__ = [
    "STAMP_DUTY_FIRST",
    "STAMP_DUTY_REST",
    "NOTARY_FEES",
    "AGENCY_FEES",
    "REGISTRATION_FEES",
    "RENTAL_YIELDS",
    "DEFAULT_RENTAL_YIELD",
    "get_rental_yield",
    "estimate_monthly_rent",
]
