"""Opportunity scoring and risk assessment for property investments.

This module provides scoring algorithms to evaluate and rank
property investment opportunities in Malta.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional

from ..data.malta_market import get_location_score as get_market_location_score


# Scoring weights (must sum to 1.0)
WEIGHTS = {
    "cash_on_cash": 0.30,      # 30% - Most important
    "cap_rate": 0.25,          # 25%
    "cash_flow": 0.20,         # 20%
    "location": 0.15,          # 15%
    "price_to_rent": 0.10,     # 10%
}

# Benchmark values for scoring
BENCHMARKS = {
    # Cash-on-cash return benchmarks
    "coc_excellent": Decimal("0.10"),   # 10%+
    "coc_good": Decimal("0.07"),        # 7%+
    "coc_fair": Decimal("0.05"),        # 5%+
    "coc_poor": Decimal("0.03"),        # 3%+
    
    # Cap rate benchmarks
    "cap_excellent": Decimal("0.07"),   # 7%+
    "cap_good": Decimal("0.055"),       # 5.5%+
    "cap_fair": Decimal("0.045"),       # 4.5%+
    "cap_poor": Decimal("0.035"),       # 3.5%+
    
    # Price-to-rent ratio benchmarks (lower is better)
    "ptr_excellent": Decimal("15"),     # < 15
    "ptr_good": Decimal("18"),          # < 18
    "ptr_fair": Decimal("22"),          # < 22
    "ptr_poor": Decimal("25"),          # < 25
}


@dataclass
class OpportunityScoreResult:
    """Result of opportunity scoring."""
    
    score: float  # 0-100
    risk_level: str  # low, medium, high
    recommendation: str
    component_scores: Dict[str, float]
    raw_metrics: Dict[str, Decimal]


def calculate_cash_on_cash_score(cash_on_cash_return: Decimal) -> float:
    """Calculate score for cash-on-cash return (0-100).
    
    Scoring:
    - 10%+: 100 points (excellent)
    - 7-10%: 80-100 points (good)
    - 5-7%: 60-80 points (fair)
    - 3-5%: 40-60 points (poor)
    - <3%: 0-40 points (very poor)
    
    Args:
        cash_on_cash_return: Cash-on-cash return as decimal
        
    Returns:
        Score from 0-100
        
    Example:
        >>> score = calculate_cash_on_cash_score(Decimal("0.085"))
        >>> print(score)
        90.0
    """
    coc = cash_on_cash_return
    
    if coc >= BENCHMARKS["coc_excellent"]:
        return 100.0
    elif coc >= BENCHMARKS["coc_good"]:
        # 7-10%: Scale 80-100
        range_size = BENCHMARKS["coc_excellent"] - BENCHMARKS["coc_good"]
        position = coc - BENCHMARKS["coc_good"]
        return 80.0 + float(position / range_size) * 20.0
    elif coc >= BENCHMARKS["coc_fair"]:
        # 5-7%: Scale 60-80
        range_size = BENCHMARKS["coc_good"] - BENCHMARKS["coc_fair"]
        position = coc - BENCHMARKS["coc_fair"]
        return 60.0 + float(position / range_size) * 20.0
    elif coc >= BENCHMARKS["coc_poor"]:
        # 3-5%: Scale 40-60
        range_size = BENCHMARKS["coc_fair"] - BENCHMARKS["coc_poor"]
        position = coc - BENCHMARKS["coc_poor"]
        return 40.0 + float(position / range_size) * 20.0
    elif coc > Decimal("0"):
        # 0-3%: Scale 0-40
        range_size = BENCHMARKS["coc_poor"]
        position = coc
        return float(position / range_size) * 40.0
    else:
        # Negative return
        return 0.0


def calculate_cap_rate_score(cap_rate: Decimal) -> float:
    """Calculate score for cap rate (0-100).
    
    Scoring:
    - 7%+: 100 points
    - 5.5-7%: 80-100 points
    - 4.5-5.5%: 60-80 points
    - 3.5-4.5%: 40-60 points
    - <3.5%: 0-40 points
    
    Args:
        cap_rate: Cap rate as decimal
        
    Returns:
        Score from 0-100
        
    Example:
        >>> score = calculate_cap_rate_score(Decimal("0.06"))
        >>> print(score)
        88.89
    """
    cap = cap_rate
    
    if cap >= BENCHMARKS["cap_excellent"]:
        return 100.0
    elif cap >= BENCHMARKS["cap_good"]:
        range_size = BENCHMARKS["cap_excellent"] - BENCHMARKS["cap_good"]
        position = cap - BENCHMARKS["cap_good"]
        return 80.0 + float(position / range_size) * 20.0
    elif cap >= BENCHMARKS["cap_fair"]:
        range_size = BENCHMARKS["cap_good"] - BENCHMARKS["cap_fair"]
        position = cap - BENCHMARKS["cap_fair"]
        return 60.0 + float(position / range_size) * 20.0
    elif cap >= BENCHMARKS["cap_poor"]:
        range_size = BENCHMARKS["cap_fair"] - BENCHMARKS["cap_poor"]
        position = cap - BENCHMARKS["cap_poor"]
        return 40.0 + float(position / range_size) * 20.0
    elif cap > Decimal("0"):
        range_size = BENCHMARKS["cap_poor"]
        position = cap
        return float(position / range_size) * 40.0
    else:
        return 0.0


def calculate_cash_flow_score(monthly_cash_flow: Decimal) -> float:
    """Calculate score for cash flow positivity (0-100).
    
    Scoring:
    - €500+/month: 100 points
    - €200-500/month: 80-100 points
    - €0-200/month: 60-80 points
    - €-200-0/month: 40-60 points
    - €-500 to -200/month: 20-40 points
    - <-€500/month: 0-20 points
    
    Args:
        monthly_cash_flow: Monthly cash flow in EUR
        
    Returns:
        Score from 0-100
        
    Example:
        >>> score = calculate_cash_flow_score(Decimal("350"))
        >>> print(score)
        90.0
    """
    cf = monthly_cash_flow
    
    if cf >= Decimal("500"):
        return 100.0
    elif cf >= Decimal("200"):
        # €200-500: Scale 80-100
        return 80.0 + float((cf - Decimal("200")) / Decimal("300")) * 20.0
    elif cf >= Decimal("0"):
        # €0-200: Scale 60-80
        return 60.0 + float(cf / Decimal("200")) * 20.0
    elif cf >= Decimal("-200"):
        # €-200-0: Scale 40-60
        return 40.0 + float((cf + Decimal("200")) / Decimal("200")) * 20.0
    elif cf >= Decimal("-500"):
        # €-500 to -200: Scale 20-40
        return 20.0 + float((cf + Decimal("500")) / Decimal("300")) * 20.0
    else:
        # <-€500: Scale 0-20
        # Assume -€1000 is worst case (0 points)
        worst_case = Decimal("-1000")
        if cf <= worst_case:
            return 0.0
        return float((cf - worst_case) / Decimal("500")) * 20.0


def calculate_location_score(area: Optional[str]) -> float:
    """Calculate score for location desirability (0-100).
    
    Uses Malta market data for location desirability scores.
    
    Args:
        area: Area/locality name in Malta
        
    Returns:
        Score from 0-100
        
    Example:
        >>> score = calculate_location_score("sliema")
        >>> print(score)
        95.0
    """
    if area is None:
        # Default score if area not specified
        return 50.0
    
    try:
        desirability = get_market_location_score(area)
        return float(desirability)
    except ValueError:
        # Area not found in database
        return 50.0


def calculate_price_to_rent_score(price_to_rent: Decimal) -> float:
    """Calculate score for price-to-rent ratio (0-100).
    
    Lower ratio is better (property is cheaper relative to rent).
    
    Scoring:
    - <15: 100 points (excellent)
    - 15-18: 80-100 points (good)
    - 18-22: 60-80 points (fair)
    - 22-25: 40-60 points (poor)
    - >25: 0-40 points (very poor)
    
    Args:
        price_to_rent: Price-to-rent ratio
        
    Returns:
        Score from 0-100
        
    Example:
        >>> score = calculate_price_to_rent_score(Decimal("18"))
        >>> print(score)
        80.0
    """
    ptr = price_to_rent
    
    if ptr <= BENCHMARKS["ptr_excellent"]:
        return 100.0
    elif ptr <= BENCHMARKS["ptr_good"]:
        # 15-18: Scale 80-100 (inverted)
        range_size = BENCHMARKS["ptr_good"] - BENCHMARKS["ptr_excellent"]
        position = BENCHMARKS["ptr_good"] - ptr
        return 80.0 + float(position / range_size) * 20.0
    elif ptr <= BENCHMARKS["ptr_fair"]:
        # 18-22: Scale 60-80 (inverted)
        range_size = BENCHMARKS["ptr_fair"] - BENCHMARKS["ptr_good"]
        position = BENCHMARKS["ptr_fair"] - ptr
        return 60.0 + float(position / range_size) * 20.0
    elif ptr <= BENCHMARKS["ptr_poor"]:
        # 22-25: Scale 40-60 (inverted)
        range_size = BENCHMARKS["ptr_poor"] - BENCHMARKS["ptr_fair"]
        position = BENCHMARKS["ptr_poor"] - ptr
        return 40.0 + float(position / range_size) * 20.0
    else:
        # >25: Scale 0-40 (inverted)
        # Assume 35 is worst case (0 points)
        worst_case = Decimal("35")
        if ptr >= worst_case:
            return 0.0
        return float((worst_case - ptr) / Decimal("10")) * 40.0


def classify_risk_level(
    cash_on_cash: Decimal,
    cap_rate: Decimal,
    monthly_cash_flow: Decimal,
    score: float,
) -> str:
    """Classify investment risk level based on metrics.
    
    Risk classification:
    - Low: Score >= 70, positive cash flow, CoC >= 7%, Cap Rate >= 5%
    - Medium: Score 40-69, or mixed signals
    - High: Score < 40, negative cash flow, or poor returns
    
    Args:
        cash_on_cash: Cash-on-cash return
        cap_rate: Cap rate
        monthly_cash_flow: Monthly cash flow
        score: Overall opportunity score
        
    Returns:
        Risk level: "low", "medium", or "high"
        
    Example:
        >>> risk = classify_risk_level(Decimal("0.08"), Decimal("0.055"), Decimal("300"), 75.0)
        >>> print(risk)
        low
    """
    # High risk conditions
    if score < 40:
        return "high"
    if monthly_cash_flow < Decimal("-200"):
        return "high"
    if cash_on_cash < Decimal("0.02") and cap_rate < Decimal("0.035"):
        return "high"
    
    # Low risk conditions
    if score >= 70:
        if monthly_cash_flow > Decimal("0"):
            if cash_on_cash >= Decimal("0.07") and cap_rate >= Decimal("0.05"):
                return "low"
    
    # Default to medium
    return "medium"


def get_recommendation(score: float, risk_level: str) -> str:
    """Get investment recommendation based on score and risk.
    
    Recommendations:
    - Score 80-100: "Excellent Opportunity"
    - Score 60-79: "Good Opportunity"
    - Score 40-59: "Fair - Consider Carefully"
    - Score <40: "Poor - Not Recommended"
    
    Args:
        score: Overall opportunity score (0-100)
        risk_level: Risk classification
        
    Returns:
        Recommendation string
        
    Example:
        >>> rec = get_recommendation(85.0, "low")
        >>> print(rec)
        Excellent Opportunity
    """
    if score >= 80:
        if risk_level == "low":
            return "Excellent Opportunity - Strong Buy"
        else:
            return "Excellent Opportunity - Moderate Risk"
    elif score >= 60:
        if risk_level == "low":
            return "Good Opportunity - Consider Buying"
        elif risk_level == "medium":
            return "Good Opportunity - Moderate Risk"
        else:
            return "Good Metrics but High Risk - Proceed with Caution"
    elif score >= 40:
        if risk_level == "low":
            return "Fair - Worth Considering"
        else:
            return "Fair - Higher Risk, Negotiate Price"
    else:
        return "Poor - Not Recommended"


def score_opportunity(
    cash_on_cash: Decimal,
    cap_rate: Decimal,
    monthly_cash_flow: Decimal,
    area: Optional[str] = None,
    price_to_rent: Optional[Decimal] = None,
) -> Dict:
    """Calculate overall opportunity score for a property investment.
    
    This is the main scoring function that combines all metrics into
    a single score from 0-100.
    
    Weights:
    - Cash-on-cash return: 30%
    - Cap rate: 25%
    - Cash flow: 20%
    - Location: 15%
    - Price-to-rent ratio: 10%
    
    Args:
        cash_on_cash: Cash-on-cash return as decimal
        cap_rate: Cap rate as decimal
        monthly_cash_flow: Monthly cash flow in EUR
        area: Area/locality name (optional)
        price_to_rent: Price-to-rent ratio (optional)
        
    Returns:
        Dictionary with score, risk level, recommendation, and component scores
        
    Example:
        >>> result = score_opportunity(
        ...     Decimal("0.085"),
        ...     Decimal("0.055"),
        ...     Decimal("350"),
        ...     area="sliema",
        ...     price_to_rent=Decimal("18"),
        ... )
        >>> print(result['score'])
        85.5
    """
    # Calculate component scores
    coc_score = calculate_cash_on_cash_score(cash_on_cash)
    cap_score = calculate_cap_rate_score(cap_rate)
    cf_score = calculate_cash_flow_score(monthly_cash_flow)
    loc_score = calculate_location_score(area)
    
    # Use default price-to-rent score if not provided
    if price_to_rent is not None:
        ptr_score = calculate_price_to_rent_score(price_to_rent)
    else:
        ptr_score = 50.0  # Neutral score
    
    # Calculate weighted overall score
    overall_score = (
        coc_score * WEIGHTS["cash_on_cash"] +
        cap_score * WEIGHTS["cap_rate"] +
        cf_score * WEIGHTS["cash_flow"] +
        loc_score * WEIGHTS["location"] +
        ptr_score * WEIGHTS["price_to_rent"]
    )
    
    # Round to 1 decimal place
    overall_score = round(overall_score, 1)
    
    # Classify risk
    risk_level = classify_risk_level(
        cash_on_cash,
        cap_rate,
        monthly_cash_flow,
        overall_score,
    )
    
    # Get recommendation
    recommendation = get_recommendation(overall_score, risk_level)
    
    return {
        "score": overall_score,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "component_scores": {
            "cash_on_cash": round(coc_score, 1),
            "cap_rate": round(cap_score, 1),
            "cash_flow": round(cf_score, 1),
            "location": round(loc_score, 1),
            "price_to_rent": round(ptr_score, 1),
        },
        "raw_metrics": {
            "cash_on_cash": cash_on_cash,
            "cap_rate": cap_rate,
            "monthly_cash_flow": monthly_cash_flow,
            "price_to_rent": price_to_rent or Decimal("0"),
        },
    }


def rank_opportunities(
    opportunities: list[Dict],
) -> list[Dict]:
    """Rank multiple investment opportunities by score.
    
    Args:
        opportunities: List of opportunity dictionaries with metrics
        
    Returns:
        List of opportunities sorted by score (highest first)
        
    Example:
        >>> opportunities = [
        ...     {"property_id": "A", "cash_on_cash": Decimal("0.08"), ...},
        ...     {"property_id": "B", "cash_on_cash": Decimal("0.06"), ...},
        ... ]
        >>> ranked = rank_opportunities(opportunities)
    """
    scored_opportunities = []
    
    for opp in opportunities:
        score_result = score_opportunity(
            cash_on_cash=opp.get("cash_on_cash", Decimal("0")),
            cap_rate=opp.get("cap_rate", Decimal("0")),
            monthly_cash_flow=opp.get("monthly_cash_flow", Decimal("0")),
            area=opp.get("area"),
            price_to_rent=opp.get("price_to_rent"),
        )
        scored_opportunities.append({
            **opp,
            **score_result,
        })
    
    # Sort by score descending
    return sorted(scored_opportunities, key=lambda x: x["score"], reverse=True)
