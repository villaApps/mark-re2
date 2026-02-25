"""
Pytest fixtures for Malta Property Analyzer tests.
"""

from decimal import Decimal
import pytest

from src.models.investment import InvestmentScenario


@pytest.fixture
def sample_property_price() -> Decimal:
    """Standard property price for testing."""
    return Decimal("300000")


@pytest.fixture
def sample_monthly_rent() -> Decimal:
    """Standard monthly rent for testing."""
    return Decimal("1400")


@pytest.fixture
def basic_scenario() -> InvestmentScenario:
    """Basic investment scenario for testing."""
    return InvestmentScenario(
        property_price=Decimal("300000"),
        monthly_rent=Decimal("1400"),
        location="mosta",
        down_payment_percent=Decimal("0.20"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
    )


@pytest.fixture
def first_time_buyer_scenario() -> InvestmentScenario:
    """Scenario for first-time buyer."""
    return InvestmentScenario(
        property_price=Decimal("250000"),
        monthly_rent=Decimal("1200"),
        location="mosta",
        is_first_time_buyer=True,
        down_payment_percent=Decimal("0.20"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
    )


@pytest.fixture
def premium_location_scenario() -> InvestmentScenario:
    """Scenario for premium location (Sliema)."""
    return InvestmentScenario(
        property_price=Decimal("450000"),
        monthly_rent=Decimal("1700"),
        location="sliema",
        down_payment_percent=Decimal("0.25"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
    )


@pytest.fixture
def high_yield_scenario() -> InvestmentScenario:
    """Scenario with high rental yield."""
    return InvestmentScenario(
        property_price=Decimal("200000"),
        monthly_rent=Decimal("1100"),
        location="zejtun",
        down_payment_percent=Decimal("0.20"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
    )


@pytest.fixture
def cash_buyer_scenario() -> InvestmentScenario:
    """Scenario with 100% down payment (cash buyer)."""
    return InvestmentScenario(
        property_price=Decimal("300000"),
        monthly_rent=Decimal("1400"),
        location="mosta",
        down_payment_percent=Decimal("1.00"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
    )


@pytest.fixture
def low_down_payment_scenario() -> InvestmentScenario:
    """Scenario with minimum down payment."""
    return InvestmentScenario(
        property_price=Decimal("300000"),
        monthly_rent=Decimal("1400"),
        location="mosta",
        down_payment_percent=Decimal("0.10"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
    )
