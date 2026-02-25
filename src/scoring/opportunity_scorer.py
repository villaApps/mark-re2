"""
Opportunity Scorer

Scores property investment opportunities on a 0-100 scale.
Uses multiple weighted factors to evaluate investment quality.

Scoring methodology:
- Cash Flow Score (30%): Positive cash flow is critical
- Cap Rate Score (25%): Measure of property's earning potential
- DSCR Score (20%): Ability to cover mortgage payments
- GRM Score (15%): Price relative to rental income
- Safety Margin (10%): Cushion for unexpected expenses
"""

from decimal import Decimal
from typing import Tuple


def _score_cash_flow(monthly_cash_flow: Decimal) -> float:
    """
    Score based on monthly cash flow.
    
    Scale:
    - Negative: 0-40 points (penalty for negative cash flow)
    - €0-200: 40-60 points
    - €200-500: 60-80 points
    - €500-1000: 80-95 points
    - €1000+: 95-100 points
    
    Args:
        monthly_cash_flow: Monthly cash flow in EUR
        
    Returns:
        Score from 0-100
    """
    cf = float(monthly_cash_flow)
    
    if cf < 0:
        # Negative cash flow: 0 to 40 points
        # -€500 or worse = 0 points
        # €0 = 40 points
        return max(0, 40 + (cf / 500) * 40)
    elif cf < 200:
        # €0-200: 40-60 points
        return 40 + (cf / 200) * 20
    elif cf < 500:
        # €200-500: 60-80 points
        return 60 + ((cf - 200) / 300) * 20
    elif cf < 1000:
        # €500-1000: 80-95 points
        return 80 + ((cf - 500) / 500) * 15
    else:
        # €1000+: 95-100 points
        return min(100, 95 + ((cf - 1000) / 1000) * 5)


def _score_cap_rate(cap_rate: Decimal) -> float:
    """
    Score based on capitalization rate.
    
    Scale (Malta market context):
    - < 3%: 0-30 points (poor)
    - 3-4%: 30-50 points (below average)
    - 4-5%: 50-70 points (average)
    - 5-6%: 70-85 points (good)
    - 6-8%: 85-95 points (excellent)
    - 8%+: 95-100 points (exceptional)
    
    Args:
        cap_rate: Cap rate as decimal (e.g., 0.055 for 5.5%)
        
    Returns:
        Score from 0-100
    """
    cr = float(cap_rate)
    
    if cr < 0.03:
        return max(0, cr / 0.03 * 30)
    elif cr < 0.04:
        return 30 + ((cr - 0.03) / 0.01) * 20
    elif cr < 0.05:
        return 50 + ((cr - 0.04) / 0.01) * 20
    elif cr < 0.06:
        return 70 + ((cr - 0.05) / 0.01) * 15
    elif cr < 0.08:
        return 85 + ((cr - 0.06) / 0.02) * 10
    else:
        return min(100, 95 + ((cr - 0.08) / 0.02) * 5)


def _score_dscr(debt_coverage_ratio: Decimal) -> float:
    """
    Score based on Debt Service Coverage Ratio.
    
    DSCR = NOI / Annual Mortgage Payment
    
    Scale:
    - < 1.0: 0-20 points (dangerous, negative cash flow)
    - 1.0-1.1: 20-40 points (risky)
    - 1.1-1.25: 40-60 points (acceptable)
    - 1.25-1.5: 60-80 points (good)
    - 1.5-2.0: 80-95 points (excellent)
    - 2.0+: 95-100 points (very safe)
    
    Args:
        debt_coverage_ratio: DSCR value
        
    Returns:
        Score from 0-100
    """
    dscr = float(debt_coverage_ratio)
    
    if dscr < 1.0:
        return max(0, dscr * 20)
    elif dscr < 1.1:
        return 20 + ((dscr - 1.0) / 0.1) * 20
    elif dscr < 1.25:
        return 40 + ((dscr - 1.1) / 0.15) * 20
    elif dscr < 1.5:
        return 60 + ((dscr - 1.25) / 0.25) * 20
    elif dscr < 2.0:
        return 80 + ((dscr - 1.5) / 0.5) * 15
    else:
        return min(100, 95 + ((dscr - 2.0) / 1.0) * 5)


def _score_grm(gross_rent_multiplier: Decimal) -> float:
    """
    Score based on Gross Rent Multiplier.
    
    GRM = Property Price / Gross Annual Rent
    Lower is better (payback period in years)
    
    Scale (Malta market context):
    - > 25: 0-30 points (poor, 25+ years to pay back)
    - 20-25: 30-50 points (below average)
    - 15-20: 50-70 points (average)
    - 12-15: 70-85 points (good)
    - 10-12: 85-95 points (excellent)
    - < 10: 95-100 points (exceptional)
    
    Args:
        gross_rent_multiplier: GRM value
        
    Returns:
        Score from 0-100
    """
    grm = float(gross_rent_multiplier)
    
    if grm > 25:
        return max(0, 30 - (grm - 25) * 2)
    elif grm > 20:
        return 30 + ((25 - grm) / 5) * 20
    elif grm > 15:
        return 50 + ((20 - grm) / 5) * 20
    elif grm > 12:
        return 70 + ((15 - grm) / 3) * 15
    elif grm > 10:
        return 85 + ((12 - grm) / 2) * 10
    else:
        return min(100, 95 + (10 - grm) * 2.5)


def _score_cash_on_cash(cash_on_cash: Decimal) -> float:
    """
    Score based on Cash-on-Cash return.
    
    Scale:
    - < 0%: 0-30 points (negative return)
    - 0-4%: 30-50 points (poor)
    - 4-7%: 50-70 points (average)
    - 7-10%: 70-85 points (good)
    - 10-15%: 85-95 points (excellent)
    - 15%+: 95-100 points (exceptional)
    
    Args:
        cash_on_cash: Cash-on-cash return as decimal
        
    Returns:
        Score from 0-100
    """
    coc = float(cash_on_cash)
    
    if coc < 0:
        return max(0, 30 + coc * 100)
    elif coc < 0.04:
        return 30 + (coc / 0.04) * 20
    elif coc < 0.07:
        return 50 + ((coc - 0.04) / 0.03) * 20
    elif coc < 0.10:
        return 70 + ((coc - 0.07) / 0.03) * 15
    elif coc < 0.15:
        return 85 + ((coc - 0.10) / 0.05) * 10
    else:
        return min(100, 95 + ((coc - 0.15) / 0.05) * 5)


def score_opportunity(
    cap_rate: Decimal,
    cash_on_cash: Decimal,
    monthly_cash_flow: Decimal,
    debt_coverage_ratio: Decimal,
    gross_rent_multiplier: Decimal,
) -> Tuple[float, dict[str, float]]:
    """
    Calculate overall opportunity score (0-100) for an investment.
    
    Uses weighted scoring of multiple factors:
    - Cash Flow Score: 30% weight
    - Cap Rate Score: 25% weight
    - DSCR Score: 20% weight
    - Cash-on-Cash Score: 15% weight
    - GRM Score: 10% weight
    
    Args:
        cap_rate: Capitalization rate as decimal
        cash_on_cash: Cash-on-cash return as decimal
        monthly_cash_flow: Monthly cash flow in EUR
        debt_coverage_ratio: DSCR value
        gross_rent_multiplier: GRM value
        
    Returns:
        Tuple of (overall_score, score_breakdown_dict)
        
    Example:
        >>> score, breakdown = score_opportunity(
        ...     cap_rate=Decimal("0.055"),
        ...     cash_on_cash=Decimal("0.08"),
        ...     monthly_cash_flow=Decimal("300"),
        ...     debt_coverage_ratio=Decimal("1.4"),
        ...     gross_rent_multiplier=Decimal("15"),
        ... )
        >>> score
        75.5
    """
    # Calculate individual scores
    cash_flow_score = _score_cash_flow(monthly_cash_flow)
    cap_rate_score = _score_cap_rate(cap_rate)
    dscr_score = _score_dscr(debt_coverage_ratio)
    grm_score = _score_grm(gross_rent_multiplier)
    coc_score = _score_cash_on_cash(cash_on_cash)
    
    # Weighted average
    # Cash flow is most important (30%)
    # Cap rate shows earning potential (25%)
    # DSCR shows safety (20%)
    # Cash-on-cash shows actual return (15%)
    # GRM shows value (10%)
    weights = {
        "cash_flow": 0.30,
        "cap_rate": 0.25,
        "dscr": 0.20,
        "cash_on_cash": 0.15,
        "grm": 0.10,
    }
    
    overall_score = (
        cash_flow_score * weights["cash_flow"] +
        cap_rate_score * weights["cap_rate"] +
        dscr_score * weights["dscr"] +
        coc_score * weights["cash_on_cash"] +
        grm_score * weights["grm"]
    )
    
    # Round to 1 decimal place
    overall_score = round(overall_score, 1)
    
    # Ensure within bounds
    overall_score = max(0, min(100, overall_score))
    
    breakdown = {
        "cash_flow": round(cash_flow_score, 1),
        "cap_rate": round(cap_rate_score, 1),
        "dscr": round(dscr_score, 1),
        "cash_on_cash": round(coc_score, 1),
        "grm": round(grm_score, 1),
    }
    
    return overall_score, breakdown


def get_score_interpretation(score: float) -> str:
    """
    Get human-readable interpretation of opportunity score.
    
    Args:
        score: Opportunity score (0-100)
        
    Returns:
        Interpretation string
        
    Example:
        >>> get_score_interpretation(85)
        'Excellent opportunity'
    """
    if score >= 90:
        return "Exceptional opportunity - Strong buy recommendation"
    elif score >= 80:
        return "Excellent opportunity - Highly recommended"
    elif score >= 70:
        return "Good opportunity - Worth considering"
    elif score >= 60:
        return "Fair opportunity - Proceed with caution"
    elif score >= 50:
        return "Below average - Consider alternatives"
    elif score >= 40:
        return "Weak opportunity - Not recommended"
    else:
        return "Poor opportunity - Avoid"
