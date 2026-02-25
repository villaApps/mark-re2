"""
Unit tests for ROI calculator.

Tests mortgage calculations, cash flow analysis, and return metrics.
"""

from decimal import Decimal
import pytest

from src.calculators.roi_calculator import (
    calculate_mortgage,
    calculate_operating_expenses,
    calculate_roi,
    compare_scenarios,
)
from src.models.investment import InvestmentScenario


class TestMortgageCalculation:
    """Tests for mortgage payment calculations."""
    
    def test_mortgage_standard_case(self):
        """Standard mortgage calculation."""
        mortgage = calculate_mortgage(
            principal=Decimal("240000"),
            annual_rate=Decimal("0.035"),
            years=25
        )
        
        assert mortgage.principal == Decimal("240000.00")
        assert mortgage.annual_rate == Decimal("0.035")
        assert mortgage.term_years == 25
        assert mortgage.total_payments == 300
        
        # Monthly payment should be around €1,201.58
        assert mortgage.monthly_payment > Decimal("1100")
        assert mortgage.monthly_payment < Decimal("1300")
        
        # Total cost should be more than principal
        assert mortgage.total_cost > mortgage.principal
        assert mortgage.total_interest > 0
    
    def test_mortgage_zero_interest(self):
        """Mortgage with 0% interest."""
        mortgage = calculate_mortgage(
            principal=Decimal("240000"),
            annual_rate=Decimal("0"),
            years=25
        )
        
        # With 0% interest, monthly payment = principal / months
        expected_monthly = Decimal("240000") / Decimal("300")
        assert mortgage.monthly_payment == expected_monthly.quantize(Decimal("0.01"))
        assert mortgage.total_interest == Decimal("0.00")
        assert mortgage.total_cost == mortgage.principal
    
    def test_mortgage_shorter_term(self):
        """Mortgage with shorter term has higher payments but less interest."""
        mortgage_15 = calculate_mortgage(
            principal=Decimal("240000"),
            annual_rate=Decimal("0.035"),
            years=15
        )
        mortgage_25 = calculate_mortgage(
            principal=Decimal("240000"),
            annual_rate=Decimal("0.035"),
            years=25
        )
        
        # 15-year has higher monthly payment
        assert mortgage_15.monthly_payment > mortgage_25.monthly_payment
        # But less total interest
        assert mortgage_15.total_interest < mortgage_25.total_interest
    
    def test_mortgage_higher_rate(self):
        """Higher interest rate increases payments."""
        mortgage_low = calculate_mortgage(
            principal=Decimal("240000"),
            annual_rate=Decimal("0.03"),
            years=25
        )
        mortgage_high = calculate_mortgage(
            principal=Decimal("240000"),
            annual_rate=Decimal("0.05"),
            years=25
        )
        
        assert mortgage_high.monthly_payment > mortgage_low.monthly_payment
        assert mortgage_high.total_interest > mortgage_low.total_interest
    
    def test_mortgage_invalid_inputs(self):
        """Test validation of invalid inputs."""
        with pytest.raises(ValueError, match="Principal must be positive"):
            calculate_mortgage(Decimal("0"), Decimal("0.035"), 25)
        
        with pytest.raises(ValueError, match="Principal must be positive"):
            calculate_mortgage(Decimal("-100000"), Decimal("0.035"), 25)
        
        with pytest.raises(ValueError, match="Interest rate cannot be negative"):
            calculate_mortgage(Decimal("100000"), Decimal("-0.01"), 25)
        
        with pytest.raises(ValueError, match="Loan term must be positive"):
            calculate_mortgage(Decimal("100000"), Decimal("0.035"), 0)


class TestOperatingExpenses:
    """Tests for operating expense calculations."""
    
    def test_operating_expenses_basic(self, basic_scenario):
        """Basic operating expenses calculation."""
        expenses = calculate_operating_expenses(basic_scenario)
        
        # Gross annual rent: €1,400 * 12 = €16,800
        assert basic_scenario.gross_annual_rent == Decimal("16800.00")
        
        # Property management: 10% of €16,800 = €1,680
        assert expenses.property_management == Decimal("1680.00")
        
        # Maintenance: 5% of €16,800 = €840
        assert expenses.maintenance == Decimal("840.00")
        
        # Insurance: 0.2% of €300,000 = €600
        assert expenses.insurance == Decimal("600.00")
        
        # Vacancy loss: 5% of €16,800 = €840
        assert expenses.vacancy_loss == Decimal("840.00")
        
        # Total should be sum of all
        expected_total = Decimal("1680.00") + Decimal("840.00") + Decimal("600.00") + Decimal("840.00")
        assert expenses.total == expected_total
    
    def test_operating_expenses_custom_rates(self):
        """Operating expenses with custom rates."""
        scenario = InvestmentScenario(
            property_price=Decimal("300000"),
            monthly_rent=Decimal("1400"),
            location="mosta",
            property_management_percent=Decimal("0.15"),  # 15%
            maintenance_reserve_percent=Decimal("0.10"),  # 10%
            annual_insurance_cost=Decimal("800"),
            vacancy_rate=Decimal("0.10"),  # 10%
        )
        
        expenses = calculate_operating_expenses(scenario)
        
        # Property management: 15% of €16,800 = €2,520
        assert expenses.property_management == Decimal("2520.00")
        
        # Maintenance: 10% of €16,800 = €1,680
        assert expenses.maintenance == Decimal("1680.00")
        
        # Insurance: Custom €800
        assert expenses.insurance == Decimal("800.00")
        
        # Vacancy: 10% of €16,800 = €1,680
        assert expenses.vacancy_loss == Decimal("1680.00")


class TestROICalculation:
    """Tests for complete ROI analysis."""
    
    def test_roi_basic_scenario(self, basic_scenario):
        """Complete ROI analysis for basic scenario."""
        analysis = calculate_roi(basic_scenario)
        
        # Verify purchase info
        assert analysis.property_price == Decimal("300000")
        assert analysis.down_payment == Decimal("60000.00")  # 20%
        assert analysis.loan_amount == Decimal("240000.00")
        
        # Verify closing costs are calculated
        assert analysis.closing_costs > 0
        assert analysis.total_purchase_cost > analysis.property_price
        
        # Verify mortgage is calculated
        assert analysis.monthly_mortgage > 0
        assert analysis.annual_mortgage > 0
        
        # Verify income
        assert analysis.gross_annual_rent == Decimal("16800.00")
        assert analysis.vacancy_loss > 0
        assert analysis.effective_gross_income < analysis.gross_annual_rent
        
        # Verify operating expenses
        assert analysis.total_operating_expenses > 0
        assert analysis.operating_expenses is not None
        
        # Verify NOI
        assert analysis.net_operating_income > 0
        
        # Verify cash flow
        assert analysis.annual_cash_flow is not None
        assert analysis.monthly_cash_flow is not None
        
        # Verify return metrics
        assert analysis.cap_rate > 0
        assert analysis.cash_on_cash_return is not None
        assert analysis.gross_rent_multiplier > 0
        
        # Verify scoring
        assert 0 <= analysis.opportunity_score <= 100
        assert len(analysis.score_breakdown) > 0
        
        # Verify DSCR
        assert analysis.debt_coverage_ratio > 0
        
        # Verify break-even
        assert analysis.break_even_occupancy > 0
    
    def test_roi_cash_buyer(self, cash_buyer_scenario):
        """ROI analysis for cash buyer (no mortgage)."""
        analysis = calculate_roi(cash_buyer_scenario)
        
        # No loan
        assert analysis.loan_amount == Decimal("0.00")
        assert analysis.monthly_mortgage == Decimal("0.00")
        assert analysis.annual_mortgage == Decimal("0.00")
        
        # Cash invested is full price plus closing costs
        assert analysis.down_payment == Decimal("300000.00")
        
        # Cash flow equals NOI (no mortgage)
        assert analysis.annual_cash_flow == analysis.net_operating_income
        
        # DSCR should be very high (no mortgage payments)
        assert analysis.debt_coverage_ratio > 100
    
    def test_roi_first_time_buyer(self, first_time_buyer_scenario):
        """ROI analysis for first-time buyer."""
        analysis = calculate_roi(first_time_buyer_scenario)
        
        # Should have reduced stamp duty
        # Property price €250k, first €175k at 3.5%, rest at 5%
        # €175k * 3.5% + €75k * 5% = €6,125 + €3,750 = €9,875
        assert analysis.closing_costs < Decimal("15000.00")  # Less than standard
        
        # Total purchase cost should reflect savings
        expected_price = Decimal("250000")
        assert analysis.property_price == expected_price
    
    def test_roi_cap_rate_calculation(self):
        """Verify cap rate is calculated correctly."""
        # Create scenario with known values
        scenario = InvestmentScenario(
            property_price=Decimal("300000"),
            monthly_rent=Decimal("1500"),  # €18,000 annual
            location="mosta",
            vacancy_rate=Decimal("0"),  # No vacancy for simplicity
            property_management_percent=Decimal("0"),  # No management
            maintenance_reserve_percent=Decimal("0"),  # No maintenance
            annual_insurance_cost=Decimal("0"),  # No insurance
            down_payment_percent=Decimal("1.00"),  # Cash buyer
        )
        
        analysis = calculate_roi(scenario)
        
        # With no expenses, NOI = Gross Rent
        # Cap Rate = NOI / Price = €18,000 / €300,000 = 6%
        expected_cap_rate = Decimal("0.06")
        assert abs(analysis.cap_rate - expected_cap_rate) < Decimal("0.001")
    
    def test_roi_cash_on_cash_calculation(self):
        """Verify cash-on-cash return is calculated correctly."""
        scenario = InvestmentScenario(
            property_price=Decimal("300000"),
            monthly_rent=Decimal("1500"),
            location="mosta",
            down_payment_percent=Decimal("0.20"),  # 20% down
            vacancy_rate=Decimal("0"),
            property_management_percent=Decimal("0"),
            maintenance_reserve_percent=Decimal("0"),
            annual_insurance_cost=Decimal("0"),
            loan_interest_rate=Decimal("0"),  # 0% interest for simplicity
        )
        
        analysis = calculate_roi(scenario)
        
        # Cash invested: 20% of €300k = €60k + closing costs
        # With 0% interest, mortgage payment = €240k / 300 months = €800/month
        # Annual cash flow = €18,000 - (€800 * 12) = €18,000 - €9,600 = €8,400
        # CoC = €8,400 / (€60k + closing costs)
        
        assert analysis.cash_on_cash_return > 0
    
    def test_roi_grm_calculation(self):
        """Verify GRM is calculated correctly."""
        scenario = InvestmentScenario(
            property_price=Decimal("300000"),
            monthly_rent=Decimal("1500"),  # €18,000 annual
            location="mosta",
        )
        
        analysis = calculate_roi(scenario)
        
        # GRM = Price / Gross Annual Rent = €300,000 / €18,000 = 16.67
        expected_grm = Decimal("16.67")
        assert abs(analysis.gross_rent_multiplier - expected_grm) < Decimal("0.1")


class TestCompareScenarios:
    """Tests for scenario comparison."""
    
    def test_compare_multiple_scenarios(self):
        """Compare multiple investment scenarios."""
        scenarios = [
            InvestmentScenario(
                property_price=Decimal("200000"),
                monthly_rent=Decimal("1100"),
                location="zejtun",
            ),
            InvestmentScenario(
                property_price=Decimal("300000"),
                monthly_rent=Decimal("1400"),
                location="mosta",
            ),
            InvestmentScenario(
                property_price=Decimal("450000"),
                monthly_rent=Decimal("1700"),
                location="sliema",
            ),
        ]
        
        results = compare_scenarios(scenarios)
        
        # Should return same number of results
        assert len(results) == len(scenarios)
        
        # Results should be sorted by opportunity score (highest first)
        for i in range(len(results) - 1):
            assert results[i].opportunity_score >= results[i + 1].opportunity_score
    
    def test_compare_empty_list(self):
        """Compare empty list of scenarios."""
        results = compare_scenarios([])
        assert results == []


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_very_low_rent(self):
        """Scenario with very low rent relative to price."""
        scenario = InvestmentScenario(
            property_price=Decimal("500000"),
            monthly_rent=Decimal("1000"),  # Very low yield
            location="sliema",
        )
        
        analysis = calculate_roi(scenario)
        
        # Should still calculate without errors
        assert analysis.cap_rate > 0
        assert analysis.opportunity_score >= 0
    
    def test_high_vacancy_rate(self):
        """Scenario with high vacancy rate."""
        scenario = InvestmentScenario(
            property_price=Decimal("300000"),
            monthly_rent=Decimal("1400"),
            location="mosta",
            vacancy_rate=Decimal("0.30"),  # 30% vacancy
        )
        
        analysis = calculate_roi(scenario)
        
        # High vacancy should reduce cash flow
        assert analysis.vacancy_loss > Decimal("4000")
        assert analysis.effective_gross_income < analysis.gross_annual_rent * Decimal("0.8")
