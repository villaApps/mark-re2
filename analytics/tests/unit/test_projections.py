"""Tests for projections calculator functions."""

from decimal import Decimal

import pytest

from src.calculators.projections import (
    calculate_break_even_period,
    calculate_equity_buildup,
    calculate_loan_balance,
    calculate_total_return_components,
    project_10_year_returns,
    project_annual_rent,
    project_property_value,
)
from src.models.investment import InvestmentScenario


class TestCalculateLoanBalance:
    """Tests for calculate_loan_balance function."""
    
    def test_initial_balance(self):
        """Test balance at start of loan."""
        principal = Decimal("240000")
        rate = Decimal("0.035")
        years = 25
        
        balance = calculate_loan_balance(principal, rate, years, 0)
        
        # At start, balance equals principal
        assert balance == principal
    
    def test_after_one_year(self):
        """Test balance after one year of payments."""
        principal = Decimal("240000")
        rate = Decimal("0.035")
        years = 25
        
        balance = calculate_loan_balance(principal, rate, years, 12)
        
        # Balance should be less than principal
        assert balance < principal
        # Should have paid off some principal
        assert balance > Decimal("230000")
    
    def test_after_five_years(self):
        """Test balance after five years."""
        principal = Decimal("240000")
        rate = Decimal("0.035")
        years = 25
        
        balance = calculate_loan_balance(principal, rate, years, 60)
        
        # Should have paid off significant principal
        assert balance < Decimal("210000")
        assert balance > Decimal("190000")
    
    def test_at_end_of_loan(self):
        """Test balance at end of loan term."""
        principal = Decimal("240000")
        rate = Decimal("0.035")
        years = 25
        
        balance = calculate_loan_balance(principal, rate, years, 300)
        
        # Should be fully paid off
        assert balance == Decimal("0")
    
    def test_beyond_loan_term(self):
        """Test balance beyond loan term."""
        principal = Decimal("240000")
        rate = Decimal("0.035")
        years = 25
        
        balance = calculate_loan_balance(principal, rate, years, 400)
        
        # Should still be zero
        assert balance == Decimal("0")
    
    def test_zero_interest(self):
        """Test balance with zero interest."""
        principal = Decimal("240000")
        rate = Decimal("0")
        years = 25
        
        balance = calculate_loan_balance(principal, rate, years, 60)
        
        # Simple linear amortization
        expected = principal - (principal / Decimal("300")) * Decimal("60")
        assert balance == expected.quantize(Decimal("0.01"))
    
    def test_negative_payments_raises_error(self):
        """Test that negative payments made raises ValueError."""
        with pytest.raises(ValueError, match="Payments made cannot be negative"):
            calculate_loan_balance(Decimal("240000"), Decimal("0.035"), 25, -1)


class TestCalculateEquityBuildup:
    """Tests for calculate_equity_buildup function."""
    
    def test_positive_equity(self):
        """Test positive equity calculation."""
        property_value = Decimal("350000")
        loan_balance = Decimal("200000")
        
        equity = calculate_equity_buildup(property_value, loan_balance)
        
        # Expected: 350,000 - 200,000 = 150,000
        assert equity == Decimal("150000.00")
    
    def test_high_equity(self):
        """Test high equity scenario."""
        property_value = Decimal("400000")
        loan_balance = Decimal("50000")
        
        equity = calculate_equity_buildup(property_value, loan_balance)
        
        # Expected: 400,000 - 50,000 = 350,000
        assert equity == Decimal("350000.00")
    
    def test_low_equity(self):
        """Test low equity scenario."""
        property_value = Decimal("300000")
        loan_balance = Decimal("280000")
        
        equity = calculate_equity_buildup(property_value, loan_balance)
        
        # Expected: 300,000 - 280,000 = 20,000
        assert equity == Decimal("20000.00")


class TestProjectAnnualRent:
    """Tests for project_annual_rent function."""
    
    def test_standard_projection(self):
        """Test standard rent projection."""
        starting_rent = Decimal("1200")
        years = 5
        growth_rate = Decimal("0.025")
        
        rents = project_annual_rent(starting_rent, years, growth_rate)
        
        # Should have 5 years
        assert len(rents) == 5
        
        # First year
        assert rents[0] == Decimal("14400.00")  # 1,200 * 12
        
        # Rents should increase each year
        for i in range(1, len(rents)):
            assert rents[i] > rents[i-1]
    
    def test_zero_growth(self):
        """Test rent projection with zero growth."""
        starting_rent = Decimal("1200")
        years = 5
        growth_rate = Decimal("0")
        
        rents = project_annual_rent(starting_rent, years, growth_rate)
        
        # All rents should be the same
        for rent in rents:
            assert rent == Decimal("14400.00")
    
    def test_high_growth(self):
        """Test rent projection with high growth."""
        starting_rent = Decimal("1200")
        years = 5
        growth_rate = Decimal("0.05")
        
        rents_low_growth = project_annual_rent(starting_rent, years, Decimal("0.025"))
        rents_high_growth = project_annual_rent(starting_rent, years, growth_rate)
        
        # High growth should result in higher rents
        assert rents_high_growth[-1] > rents_low_growth[-1]


class TestProjectPropertyValue:
    """Tests for project_property_value function."""
    
    def test_standard_appreciation(self):
        """Test standard property value appreciation."""
        starting_value = Decimal("300000")
        years = 5
        appreciation = Decimal("0.03")
        
        values = project_property_value(starting_value, years, appreciation)
        
        # Should have 5 years
        assert len(values) == 5
        
        # Year 1: 300,000 * 1.03 = 309,000
        assert values[0] == Decimal("309000.00")
        
        # Values should increase each year
        for i in range(1, len(values)):
            assert values[i] > values[i-1]
    
    def test_zero_appreciation(self):
        """Test with zero appreciation."""
        starting_value = Decimal("300000")
        years = 5
        appreciation = Decimal("0")
        
        values = project_property_value(starting_value, years, appreciation)
        
        # All values should be the same
        for value in values:
            assert value == Decimal("300000.00")
    
    def test_high_appreciation(self):
        """Test with high appreciation."""
        starting_value = Decimal("300000")
        years = 10
        appreciation = Decimal("0.05")
        
        values = project_property_value(starting_value, years, appreciation)
        
        # After 10 years at 5%, value should be significantly higher
        assert values[-1] > Decimal("450000")


class TestProject10YearReturns:
    """Tests for project_10_year_returns function."""
    
    def test_standard_projection(self, sample_scenario):
        """Test standard 10-year projection."""
        projection = project_10_year_returns(sample_scenario)
        
        # Should have 10 years of data
        assert len(projection.years) == 10
        
        # Verify year numbers
        for i, year in enumerate(projection.years):
            assert year.year == i + 1
        
        # Should have summary metrics
        assert projection.total_cash_flow is not None
        assert projection.total_appreciation is not None
        assert projection.final_property_value is not None
        assert projection.final_equity is not None
        
        # Property value should appreciate
        assert projection.final_property_value > sample_scenario.property_price
        
        # Equity should increase
        assert projection.final_equity > sample_scenario.down_payment_amount
    
    def test_cash_flow_accumulation(self, sample_scenario):
        """Test that cash flows accumulate correctly."""
        projection = project_10_year_returns(sample_scenario)
        
        # Cumulative cash flow should increase each year
        for i in range(1, len(projection.years)):
            assert projection.years[i].cumulative_cash_flow >= projection.years[i-1].cumulative_cash_flow
    
    def test_loan_balance_decreases(self, sample_scenario):
        """Test that loan balance decreases over time."""
        projection = project_10_year_returns(sample_scenario)
        
        # Loan balance should decrease each year
        for i in range(1, len(projection.years)):
            assert projection.years[i].remaining_loan_balance < projection.years[i-1].remaining_loan_balance
    
    def test_equity_increases(self, sample_scenario):
        """Test that equity increases over time."""
        projection = project_10_year_returns(sample_scenario)
        
        # Equity should increase each year
        for i in range(1, len(projection.years)):
            assert projection.years[i].equity > projection.years[i-1].equity
    
    def test_irr_calculation(self, sample_scenario):
        """Test IRR calculation."""
        projection = project_10_year_returns(sample_scenario)
        
        # Should have an IRR value
        assert projection.irr is not None
        
        # IRR should be reasonable (between -20% and +50%)
        assert projection.irr > Decimal("-0.20")
        assert projection.irr < Decimal("0.50")
    
    def test_total_roi_calculation(self, sample_scenario):
        """Test total ROI calculation."""
        projection = project_10_year_returns(sample_scenario)
        
        # Total ROI should be calculated
        assert projection.total_roi is not None
        
        # Annualized return should be calculated
        assert projection.annualized_return is not None


class TestCalculateTotalReturnComponents:
    """Tests for calculate_total_return_components function."""
    
    def test_component_breakdown(self, sample_scenario):
        """Test breakdown of return components."""
        projection = project_10_year_returns(sample_scenario)
        
        components = calculate_total_return_components(sample_scenario, projection)
        
        # Should have all components
        assert "from_cash_flow" in components
        assert "from_appreciation" in components
        assert "from_principal_paydown" in components
        assert "total_return" in components
        
        # Total should equal sum of components
        expected_total = (
            components["from_cash_flow"] +
            components["from_appreciation"] +
            components["from_principal_paydown"]
        )
        assert components["total_return"] == expected_total
        
        # Percentages should sum to 100
        total_pct = (
            components["cash_flow_percentage"] +
            components["appreciation_percentage"] +
            components["principal_paydown_percentage"]
        )
        assert abs(total_pct - Decimal("100")) < Decimal("0.01")
