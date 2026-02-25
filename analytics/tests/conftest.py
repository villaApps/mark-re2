"""Pytest configuration and shared fixtures."""

from decimal import Decimal

import pytest

from src.models.investment import InvestmentScenario


@pytest.fixture
def sample_property_price():
    """Sample property price for testing."""
    return Decimal("300000")


@pytest.fixture
def sample_monthly_rent():
    """Sample monthly rent for testing."""
    return Decimal("1200")


@pytest.fixture
def sample_scenario():
    """Sample investment scenario for testing."""
    return InvestmentScenario(
        property_price=Decimal("300000"),
        monthly_rent=Decimal("1200"),
        property_area="sliema",
        down_payment_percent=Decimal("0.20"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
        annual_appreciation=Decimal("0.03"),
        scenario_name="Test Scenario",
    )


@pytest.fixture
def high_yield_scenario():
    """High-yield investment scenario for testing."""
    return InvestmentScenario(
        property_price=Decimal("200000"),
        monthly_rent=Decimal("1000"),
        property_area="birkirkara",
        down_payment_percent=Decimal("0.20"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
        annual_appreciation=Decimal("0.03"),
        scenario_name="High Yield Test",
    )


@pytest.fixture
def cash_flow_negative_scenario():
    """Negative cash flow scenario for testing edge cases."""
    return InvestmentScenario(
        property_price=Decimal("500000"),
        monthly_rent=Decimal("1200"),
        property_area="mellieha",
        down_payment_percent=Decimal("0.20"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
        annual_appreciation=Decimal("0.03"),
        scenario_name="Negative Cash Flow Test",
    )


@pytest.fixture
def first_time_buyer_scenario():
    """First-time buyer scenario for testing stamp duty."""
    return InvestmentScenario(
        property_price=Decimal("150000"),
        monthly_rent=Decimal("700"),
        property_area="mosta",
        is_first_time_buyer=True,
        down_payment_percent=Decimal("0.20"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
        annual_appreciation=Decimal("0.03"),
        scenario_name="First Time Buyer Test",
    )


@pytest.fixture
def second_time_buyer_scenario():
    """Second-time buyer scenario for testing stamp duty."""
    return InvestmentScenario(
        property_price=Decimal("300000"),
        monthly_rent=Decimal("1200"),
        property_area="sliema",
        is_first_time_buyer=False,
        down_payment_percent=Decimal("0.20"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
        annual_appreciation=Decimal("0.03"),
        scenario_name="Second Time Buyer Test",
    )


@pytest.fixture
def zero_interest_scenario():
    """Zero interest rate scenario for edge case testing."""
    return InvestmentScenario(
        property_price=Decimal("300000"),
        monthly_rent=Decimal("1200"),
        down_payment_percent=Decimal("0.20"),
        loan_interest_rate=Decimal("0"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
        annual_appreciation=Decimal("0.03"),
        scenario_name="Zero Interest Test",
    )


@pytest.fixture
def expensive_property_scenario():
    """Expensive property scenario for testing stamp duty tiers."""
    return InvestmentScenario(
        property_price=Decimal("500000"),
        monthly_rent=Decimal("2000"),
        property_area="sliema",
        is_first_time_buyer=True,
        down_payment_percent=Decimal("0.20"),
        loan_interest_rate=Decimal("0.035"),
        loan_term_years=25,
        vacancy_rate=Decimal("0.05"),
        annual_appreciation=Decimal("0.03"),
        scenario_name="Expensive Property Test",
    )
