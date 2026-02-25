"""Tests for rental yield calculator functions."""

from decimal import Decimal

import pytest

from src.calculators.rental_yield import (
    calculate_break_even_rent,
    calculate_gross_rental_yield,
    calculate_net_rental_yield,
    calculate_yield_range,
    compare_yields,
    estimate_market_rent,
)
from src.data.malta_market import RENTAL_YIELDS


class TestCalculateGrossRentalYield:
    """Tests for calculate_gross_rental_yield function."""
    
    def test_standard_yield(self):
        """Test standard gross rental yield calculation."""
        price = Decimal("300000")
        monthly_rent = Decimal("1250")
        
        yield_rate = calculate_gross_rental_yield(price, monthly_rent)
        
        # Expected: (1,250 * 12) / 300,000 = 0.05 = 5%
        assert yield_rate == Decimal("0.0500")
    
    def test_high_yield(self):
        """Test high gross rental yield."""
        price = Decimal("200000")
        monthly_rent = Decimal("1200")
        
        yield_rate = calculate_gross_rental_yield(price, monthly_rent)
        
        # Expected: (1,200 * 12) / 200,000 = 0.072 = 7.2%
        assert yield_rate == Decimal("0.0720")
    
    def test_low_yield(self):
        """Test low gross rental yield."""
        price = Decimal("500000")
        monthly_rent = Decimal("1200")
        
        yield_rate = calculate_gross_rental_yield(price, monthly_rent)
        
        # Expected: (1,200 * 12) / 500,000 = 0.0288 = 2.88%
        assert yield_rate == Decimal("0.0288")
    
    def test_zero_price_raises_error(self):
        """Test that zero price raises ValueError."""
        with pytest.raises(ValueError, match="Property price must be positive"):
            calculate_gross_rental_yield(Decimal("0"), Decimal("1200"))
    
    def test_negative_price_raises_error(self):
        """Test that negative price raises ValueError."""
        with pytest.raises(ValueError, match="Property price must be positive"):
            calculate_gross_rental_yield(Decimal("-1000"), Decimal("1200"))
    
    def test_zero_rent(self):
        """Test with zero rent."""
        yield_rate = calculate_gross_rental_yield(Decimal("300000"), Decimal("0"))
        assert yield_rate == Decimal("0")
    
    def test_negative_rent_raises_error(self):
        """Test that negative rent raises ValueError."""
        with pytest.raises(ValueError, match="Monthly rent cannot be negative"):
            calculate_gross_rental_yield(Decimal("300000"), Decimal("-100"))


class TestCalculateNetRentalYield:
    """Tests for calculate_net_rental_yield function."""
    
    def test_standard_net_yield(self):
        """Test standard net rental yield calculation."""
        price = Decimal("300000")
        monthly_rent = Decimal("1250")
        
        yield_rate = calculate_net_rental_yield(price, monthly_rent)
        
        # Net yield should be less than gross yield
        gross_yield = calculate_gross_rental_yield(price, monthly_rent)
        assert yield_rate < gross_yield
        assert yield_rate > Decimal("0")
    
    def test_net_yield_with_vacancy(self):
        """Test net yield with different vacancy rates."""
        price = Decimal("300000")
        monthly_rent = Decimal("1250")
        
        yield_no_vacancy = calculate_net_rental_yield(price, monthly_rent, vacancy_rate=Decimal("0"))
        yield_with_vacancy = calculate_net_rental_yield(price, monthly_rent, vacancy_rate=Decimal("0.10"))
        
        # Higher vacancy should result in lower yield
        assert yield_with_vacancy < yield_no_vacancy
    
    def test_net_yield_with_higher_expenses(self):
        """Test net yield with higher operating expenses."""
        price = Decimal("300000")
        monthly_rent = Decimal("1250")
        
        yield_low_expenses = calculate_net_rental_yield(
            price, monthly_rent,
            property_management_percent=Decimal("0.05"),
        )
        yield_high_expenses = calculate_net_rental_yield(
            price, monthly_rent,
            property_management_percent=Decimal("0.15"),
        )
        
        # Higher expenses should result in lower yield
        assert yield_high_expenses < yield_low_expenses


class TestEstimateMarketRent:
    """Tests for estimate_market_rent function."""
    
    def test_estimate_by_area(self):
        """Test rent estimation using area-specific yield."""
        price = Decimal("300000")
        
        # Test for Sliema (4.5% yield)
        rent_sliema = estimate_market_rent(price, area="sliema")
        expected_sliema = (price * Decimal("0.045")) / Decimal("12")
        assert rent_sliema == expected_sliema.quantize(Decimal("0.01"))
        
        # Test for Birkirkara (5.8% yield)
        rent_birkirkara = estimate_market_rent(price, area="birkirkara")
        expected_birkirkara = (price * Decimal("0.058")) / Decimal("12")
        assert rent_birkirkara == expected_birkirkara.quantize(Decimal("0.01"))
    
    def test_estimate_by_target_yield(self):
        """Test rent estimation using target yield."""
        price = Decimal("300000")
        target_yield = Decimal("0.05")
        
        rent = estimate_market_rent(price, target_yield=target_yield)
        expected = (price * target_yield) / Decimal("12")
        
        assert rent == expected.quantize(Decimal("0.01"))
    
    def test_target_yield_overrides_area(self):
        """Test that target yield overrides area."""
        price = Decimal("300000")
        
        rent_area = estimate_market_rent(price, area="sliema")
        rent_override = estimate_market_rent(price, area="sliema", target_yield=Decimal("0.06"))
        
        # Override should give different result
        assert rent_override != rent_area
    
    def test_missing_area_and_yield_raises_error(self):
        """Test that missing both area and yield raises error."""
        with pytest.raises(ValueError, match="Either area or target_yield must be provided"):
            estimate_market_rent(Decimal("300000"))
    
    def test_unknown_area_uses_default(self):
        """Test that unknown area uses default yield."""
        price = Decimal("300000")
        
        # Should not raise error, uses default 5%
        rent = estimate_market_rent(price, area="unknown_area")
        expected = (price * Decimal("0.05")) / Decimal("12")
        
        assert rent == expected.quantize(Decimal("0.01"))


class TestCalculateYieldRange:
    """Tests for calculate_yield_range function."""
    
    def test_default_scenarios(self):
        """Test yield range with default vacancy scenarios."""
        price = Decimal("300000")
        monthly_rent = Decimal("1250")
        
        yields = calculate_yield_range(price, monthly_rent)
        
        # Should have 4 scenarios
        assert "0%" in yields
        assert "5%" in yields
        assert "10%" in yields
        assert "15%" in yields
        
        # Higher vacancy should result in lower yield
        assert yields["0%"] > yields["5%"]
        assert yields["5%"] > yields["10%"]
        assert yields["10%"] > yields["15%"]
    
    def test_custom_scenarios(self):
        """Test yield range with custom vacancy scenarios."""
        price = Decimal("300000")
        monthly_rent = Decimal("1250")
        custom_scenarios = [Decimal("0"), Decimal("0.20")]
        
        yields = calculate_yield_range(price, monthly_rent, vacancy_scenarios=custom_scenarios)
        
        assert "0%" in yields
        assert "20%" in yields
        assert len(yields) == 2


class TestCompareYields:
    """Tests for compare_yields function."""
    
    def test_meets_benchmark(self):
        """Test property that meets benchmark yield."""
        price = Decimal("300000")
        monthly_rent = Decimal("1250")  # 5% yield
        benchmark = Decimal("0.05")
        
        comparison = compare_yields(price, monthly_rent, benchmark)
        
        assert comparison["meets_benchmark"] is True
        assert comparison["difference"] == Decimal("0")
    
    def test_exceeds_benchmark(self):
        """Test property that exceeds benchmark yield."""
        price = Decimal("250000")
        monthly_rent = Decimal("1250")  # 6% yield
        benchmark = Decimal("0.05")
        
        comparison = compare_yields(price, monthly_rent, benchmark)
        
        assert comparison["meets_benchmark"] is True
        assert comparison["difference"] > Decimal("0")
    
    def test_below_benchmark(self):
        """Test property below benchmark yield."""
        price = Decimal("350000")
        monthly_rent = Decimal("1250")  # ~4.3% yield
        benchmark = Decimal("0.05")
        
        comparison = compare_yields(price, monthly_rent, benchmark)
        
        assert comparison["meets_benchmark"] is False
        assert comparison["difference"] < Decimal("0")


class TestCalculateBreakEvenRent:
    """Tests for calculate_break_even_rent function."""
    
    def test_standard_break_even(self):
        """Test standard break-even rent calculation."""
        price = Decimal("300000")
        target_yield = Decimal("0.05")
        
        rent = calculate_break_even_rent(price, target_yield=target_yield)
        
        # At 5% yield with 25% operating expenses
        # Required rent = (300,000 * 0.05 / 12) / (1 - 0.25) = 1,666.67
        assert rent > Decimal("1600")
        assert rent < Decimal("1700")
    
    def test_higher_target_yield(self):
        """Test break-even with higher target yield."""
        price = Decimal("300000")
        
        rent_5pct = calculate_break_even_rent(price, target_yield=Decimal("0.05"))
        rent_7pct = calculate_break_even_rent(price, target_yield=Decimal("0.07"))
        
        # Higher target yield requires higher rent
        assert rent_7pct > rent_5pct
    
    def test_zero_price_raises_error(self):
        """Test that zero price raises ValueError."""
        with pytest.raises(ValueError, match="Property price must be positive"):
            calculate_break_even_rent(Decimal("0"))
    
    def test_zero_yield_raises_error(self):
        """Test that zero yield raises ValueError."""
        with pytest.raises(ValueError, match="Target yield must be positive"):
            calculate_break_even_rent(Decimal("300000"), target_yield=Decimal("0"))
