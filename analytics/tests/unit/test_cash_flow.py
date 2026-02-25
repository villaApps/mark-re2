"""Tests for cash flow calculator functions."""

from decimal import Decimal

import pytest

from src.calculators.cash_flow import (
    calculate_cash_flow,
    calculate_debt_service_coverage_ratio,
    calculate_effective_gross_income,
    calculate_net_operating_income,
    calculate_operating_expense_ratio,
    calculate_operating_expenses,
    project_cash_flow,
)
from src.models.investment import InvestmentScenario


class TestCalculateEffectiveGrossIncome:
    """Tests for calculate_effective_gross_income function."""
    
    def test_no_vacancy(self):
        """Test EGI with no vacancy."""
        monthly_rent = Decimal("1200")
        
        egi = calculate_effective_gross_income(monthly_rent, vacancy_rate=Decimal("0"))
        
        # Expected: 1,200 * 12 = 14,400
        assert egi == Decimal("14400.00")
    
    def test_with_vacancy(self):
        """Test EGI with 5% vacancy."""
        monthly_rent = Decimal("1200")
        
        egi = calculate_effective_gross_income(monthly_rent, vacancy_rate=Decimal("0.05"))
        
        # Expected: 14,400 * 0.95 = 13,680
        assert egi == Decimal("13680.00")
    
    def test_high_vacancy(self):
        """Test EGI with high vacancy."""
        monthly_rent = Decimal("1200")
        
        egi = calculate_effective_gross_income(monthly_rent, vacancy_rate=Decimal("0.15"))
        
        # Expected: 14,400 * 0.85 = 12,240
        assert egi == Decimal("12240.00")
    
    def test_negative_rent_raises_error(self):
        """Test that negative rent raises ValueError."""
        with pytest.raises(ValueError, match="Monthly rent cannot be negative"):
            calculate_effective_gross_income(Decimal("-100"), vacancy_rate=Decimal("0.05"))
    
    def test_invalid_vacancy_rate_raises_error(self):
        """Test that invalid vacancy rate raises ValueError."""
        with pytest.raises(ValueError, match="Vacancy rate must be between 0 and 1"):
            calculate_effective_gross_income(Decimal("1200"), vacancy_rate=Decimal("1.5"))


class TestCalculateOperatingExpenses:
    """Tests for calculate_operating_expenses function."""
    
    def test_standard_expenses(self):
        """Test standard operating expenses."""
        egi = Decimal("13680")
        property_value = Decimal("300000")
        
        expenses = calculate_operating_expenses(egi, property_value)
        
        # Property management: 10% of EGI = 1,368
        assert expenses["property_management"] == Decimal("1368.00")
        # Maintenance reserve: 5% of EGI = 684
        assert expenses["maintenance_reserve"] == Decimal("684.00")
        # Insurance: 0.3% of property value = 900
        assert expenses["insurance"] == Decimal("900.00")
        # Property tax: 0% (Malta has no property tax)
        assert expenses["property_tax"] == Decimal("0.00")
        
        # Total
        expected_total = Decimal("1368") + Decimal("684") + Decimal("900")
        assert expenses["total"] == expected_total
    
    def test_negative_egi_raises_error(self):
        """Test that negative EGI raises ValueError."""
        with pytest.raises(ValueError, match="Effective gross income cannot be negative"):
            calculate_operating_expenses(Decimal("-1000"), Decimal("300000"))
    
    def test_negative_property_value_raises_error(self):
        """Test that negative property value raises ValueError."""
        with pytest.raises(ValueError, match="Property value cannot be negative"):
            calculate_operating_expenses(Decimal("13680"), Decimal("-1000"))


class TestCalculateNetOperatingIncome:
    """Tests for calculate_net_operating_income function."""
    
    def test_positive_noi(self):
        """Test positive NOI calculation."""
        egi = Decimal("13680")
        expenses = Decimal("2952")
        
        noi = calculate_net_operating_income(egi, expenses)
        
        # Expected: 13,680 - 2,952 = 10,728
        assert noi == Decimal("10728.00")
    
    def test_zero_expenses(self):
        """Test NOI with zero expenses."""
        egi = Decimal("13680")
        expenses = Decimal("0")
        
        noi = calculate_net_operating_income(egi, expenses)
        
        assert noi == Decimal("13680.00")


class TestCalculateCashFlow:
    """Tests for calculate_cash_flow function."""
    
    def test_positive_cash_flow(self, sample_scenario):
        """Test positive cash flow scenario."""
        from src.calculators.roi_calculator import calculate_mortgage_payment
        
        monthly_mortgage = calculate_mortgage_payment(
            sample_scenario.loan_amount,
            sample_scenario.loan_interest_rate,
            sample_scenario.loan_term_years,
        )
        
        cash_flow = calculate_cash_flow(sample_scenario, monthly_mortgage)
        
        # Verify components
        assert cash_flow.gross_annual_rent == Decimal("14400.00")
        assert cash_flow.vacancy_loss == Decimal("720.00")  # 5% of 14,400
        assert cash_flow.effective_gross_income == Decimal("13680.00")
        assert cash_flow.net_operating_income > Decimal("0")
        
        # Cash flow should be calculated
        assert cash_flow.annual_cash_flow is not None
        assert cash_flow.monthly_cash_flow is not None
    
    def test_negative_cash_flow(self, cash_flow_negative_scenario):
        """Test negative cash flow scenario."""
        from src.calculators.roi_calculator import calculate_mortgage_payment
        
        monthly_mortgage = calculate_mortgage_payment(
            cash_flow_negative_scenario.loan_amount,
            cash_flow_negative_scenario.loan_interest_rate,
            cash_flow_negative_scenario.loan_term_years,
        )
        
        cash_flow = calculate_cash_flow(cash_flow_negative_scenario, monthly_mortgage)
        
        # This scenario should have negative cash flow
        assert cash_flow.is_cash_flow_positive is False
        assert cash_flow.annual_cash_flow < Decimal("0")
    
    def test_without_provided_mortgage(self, sample_scenario):
        """Test cash flow calculation without pre-calculated mortgage."""
        cash_flow = calculate_cash_flow(sample_scenario)
        
        # Should still calculate correctly
        assert cash_flow.gross_annual_rent == Decimal("14400.00")
        assert cash_flow.annual_mortgage_payment > Decimal("0")


class TestCalculateDebtServiceCoverageRatio:
    """Tests for calculate_debt_service_coverage_ratio function."""
    
    def test_strong_dscr(self):
        """Test strong DSCR (>1.25)."""
        noi = Decimal("20000")
        mortgage = Decimal("15000")
        
        dscr = calculate_debt_service_coverage_ratio(noi, mortgage)
        
        # Expected: 20,000 / 15,000 = 1.33
        assert dscr > Decimal("1.25")
        assert dscr < Decimal("1.35")
    
    def test_minimum_dscr(self):
        """Test minimum acceptable DSCR (1.25)."""
        noi = Decimal("18750")
        mortgage = Decimal("15000")
        
        dscr = calculate_debt_service_coverage_ratio(noi, mortgage)
        
        # Expected: 18,750 / 15,000 = 1.25
        assert dscr == Decimal("1.25")
    
    def test_weak_dscr(self):
        """Test weak DSCR (<1.0)."""
        noi = Decimal("12000")
        mortgage = Decimal("15000")
        
        dscr = calculate_debt_service_coverage_ratio(noi, mortgage)
        
        # Expected: 12,000 / 15,000 = 0.80
        assert dscr < Decimal("1.0")
    
    def test_zero_mortgage_raises_error(self):
        """Test that zero mortgage raises ValueError."""
        with pytest.raises(ValueError, match="Annual mortgage payment must be positive"):
            calculate_debt_service_coverage_ratio(Decimal("15000"), Decimal("0"))


class TestCalculateOperatingExpenseRatio:
    """Tests for calculate_operating_expense_ratio function."""
    
    def test_standard_oer(self):
        """Test standard OER calculation."""
        expenses = Decimal("3000")
        egi = Decimal("15000")
        
        oer = calculate_operating_expense_ratio(expenses, egi)
        
        # Expected: 3,000 / 15,000 = 0.20 = 20%
        assert oer == Decimal("0.2000")
    
    def test_high_oer(self):
        """Test high OER (concerning)."""
        expenses = Decimal("6000")
        egi = Decimal("15000")
        
        oer = calculate_operating_expense_ratio(expenses, egi)
        
        # Expected: 6,000 / 15,000 = 0.40 = 40%
        assert oer == Decimal("0.4000")
    
    def test_zero_egi_raises_error(self):
        """Test that zero EGI raises ValueError."""
        with pytest.raises(ValueError, match="Effective gross income must be positive"):
            calculate_operating_expense_ratio(Decimal("3000"), Decimal("0"))


class TestProjectCashFlow:
    """Tests for project_cash_flow function."""
    
    def test_standard_projection(self):
        """Test standard cash flow projection."""
        monthly_rent = Decimal("1200")
        property_value = Decimal("300000")
        monthly_mortgage = Decimal("1000")
        years = 5
        
        cash_flows = project_cash_flow(
            monthly_rent,
            property_value,
            monthly_mortgage,
            years=years,
        )
        
        # Should have 5 years of projections
        assert len(cash_flows) == 5
        
        # Cash flows should generally increase due to rent growth
        for cf in cash_flows:
            assert isinstance(cf, Decimal)
    
    def test_rent_growth_applied(self):
        """Test that rent growth is applied over time."""
        monthly_rent = Decimal("1200")
        property_value = Decimal("300000")
        monthly_mortgage = Decimal("1000")
        
        # Project with growth
        cash_flows_with_growth = project_cash_flow(
            monthly_rent,
            property_value,
            monthly_mortgage,
            years=5,
            annual_rent_growth=Decimal("0.025"),
        )
        
        # Project without growth
        cash_flows_no_growth = project_cash_flow(
            monthly_rent,
            property_value,
            monthly_mortgage,
            years=5,
            annual_rent_growth=Decimal("0"),
        )
        
        # With growth should have higher cash flows in later years
        assert cash_flows_with_growth[-1] > cash_flows_no_growth[-1]
