"""Opportunity scoring and risk assessment."""

from .opportunity_scorer import (
    score_opportunity,
    calculate_cash_on_cash_score,
    calculate_cap_rate_score,
    calculate_cash_flow_score,
    calculate_location_score,
    calculate_price_to_rent_score,
    classify_risk_level,
    get_recommendation,
    OpportunityScoreResult,
)

__all__ = [
    "score_opportunity",
    "calculate_cash_on_cash_score",
    "calculate_cap_rate_score",
    "calculate_cash_flow_score",
    "calculate_location_score",
    "calculate_price_to_rent_score",
    "classify_risk_level",
    "get_recommendation",
    "OpportunityScoreResult",
]
