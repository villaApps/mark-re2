"""Malta Property Investment Analytics Engine.

A comprehensive ROI analysis engine for evaluating property investment
opportunities in Malta.

Example:
    >>> from src.models.investment import InvestmentScenario
    >>> from src.calculators.roi_calculator import analyze_investment
    
    >>> scenario = InvestmentScenario(
    ...     property_price=Decimal("300000"),
    ...     monthly_rent=Decimal("1200"),
    ...     property_area="sliema",
    ... )
    >>> analysis = analyze_investment(scenario, property_id="PROP-001")
    >>> print(f"Cap Rate: {analysis.cap_rate}")
    >>> print(f"Cash-on-Cash: {analysis.cash_on_cash_return}")
    >>> print(f"Opportunity Score: {analysis.opportunity_score}")
"""

__version__ = "1.0.0"
__author__ = "Malta Property Analytics Team"

from . import calculators
from . import data
from . import models
from . import scoring

__all__ = [
    "calculators",
    "data",
    "models",
    "scoring",
]
