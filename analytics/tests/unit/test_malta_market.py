"""Tests for Malta market data module."""

from decimal import Decimal

import pytest

from src.data.malta_market import (
    RENTAL_YIELDS,
    LOCATION_DESIRABILITY,
    calculate_stamp_duty_first_time,
    calculate_stamp_duty_second_time,
    calculate_total_purchase_cost_percentage,
    get_all_areas,
    get_high_yield_areas,
    get_location_score,
    get_prime_areas,
    get_rental_yield_for_area,
)


class TestStampDutyCalculations:
    """Tests for stamp duty calculations."""
    
    def test_first_time_below_threshold(self):
        """Test first-time buyer stamp duty below €150k."""
        price = Decimal("100000")
        duty = calculate_stamp_duty_first_time(price)
        
        # 3.5% of €100,000 = €3,500
        assert duty == Decimal("3500")
    
    def test_first_time_at_threshold(self):
        """Test first-time buyer stamp duty at exactly €150k."""
        price = Decimal("150000")
        duty = calculate_stamp_duty_first_time(price)
        
        # 3.5% of €150,000 = €5,250
        assert duty == Decimal("5250")
    
    def test_first_time_above_threshold(self):
        """Test first-time buyer stamp duty above €150k."""
        price = Decimal("300000")
        duty = calculate_stamp_duty_first_time(price)
        
        # 3.5% of €150,000 + 5% of €150,000 = €5,250 + €7,500 = €12,750
        assert duty == Decimal("12750")
    
    def test_second_time_buyer(self):
        """Test second-time buyer stamp duty (flat 5%)."""
        price = Decimal("300000")
        duty = calculate_stamp_duty_second_time(price)
        
        # 5% of €300,000 = €15,000
        assert duty == Decimal("15000")
    
    def test_second_time_more_expensive(self):
        """Verify second-time buyer pays more stamp duty."""
        price = Decimal("300000")
        
        first_time = calculate_stamp_duty_first_time(price)
        second_time = calculate_stamp_duty_second_time(price)
        
        assert second_time > first_time


class TestGetRentalYieldForArea:
    """Tests for get_rental_yield_for_area function."""
    
    def test_prime_area(self):
        """Test getting yield for prime area."""
        yield_rate = get_rental_yield_for_area("sliema")
        assert yield_rate == Decimal("0.045")
    
    def test_high_yield_area(self):
        """Test getting yield for high-yield area."""
        yield_rate = get_rental_yield_for_area("birkirkara")
        assert yield_rate == Decimal("0.058")
    
    def test_low_yield_area(self):
        """Test getting yield for low-yield area (holiday destination)."""
        yield_rate = get_rental_yield_for_area("mellieha")
        assert yield_rate == Decimal("0.040")
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        yield_lower = get_rental_yield_for_area("sliema")
        yield_upper = get_rental_yield_for_area("SLIEMA")
        yield_mixed = get_rental_yield_for_area("Sliema")
        
        assert yield_lower == yield_upper == yield_mixed
    
    def test_unknown_area_raises_error(self):
        """Test that unknown area raises ValueError."""
        with pytest.raises(ValueError, match="Unknown area"):
            get_rental_yield_for_area("unknown_city")


class TestGetLocationScore:
    """Tests for get_location_score function."""
    
    def test_prime_location(self):
        """Test getting score for prime location."""
        score = get_location_score("sliema")
        assert score == 95
    
    def test_good_location(self):
        """Test getting score for good location."""
        score = get_location_score("mosta")
        assert score == 70
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        score_lower = get_location_score("sliema")
        score_upper = get_location_score("SLIEMA")
        
        assert score_lower == score_upper
    
    def test_unknown_area_raises_error(self):
        """Test that unknown area raises ValueError."""
        with pytest.raises(ValueError, match="Unknown area"):
            get_location_score("unknown_city")


class TestGetAllAreas:
    """Tests for get_all_areas function."""
    
    def test_returns_sorted_list(self):
        """Test that function returns sorted list."""
        areas = get_all_areas()
        
        # Should be a list
        assert isinstance(areas, list)
        # Should be sorted
        assert areas == sorted(areas)
        # Should contain known areas
        assert "sliema" in areas
        assert "valletta" in areas


class TestGetHighYieldAreas:
    """Tests for get_high_yield_areas function."""
    
    def test_default_threshold(self):
        """Test getting areas with default threshold (5.5%)."""
        areas = get_high_yield_areas()
        
        # Should return a dictionary
        assert isinstance(areas, dict)
        
        # All yields should be >= 5.5%
        for area, yield_rate in areas.items():
            assert yield_rate >= Decimal("0.055")
    
    def test_custom_threshold(self):
        """Test getting areas with custom threshold."""
        areas = get_high_yield_areas(min_yield=Decimal("0.06"))
        
        # All yields should be >= 6%
        for area, yield_rate in areas.items():
            assert yield_rate >= Decimal("0.06")
    
    def test_high_threshold(self):
        """Test with very high threshold."""
        areas = get_high_yield_areas(min_yield=Decimal("0.10"))
        
        # Should return empty or very few areas
        assert isinstance(areas, dict)


class TestGetPrimeAreas:
    """Tests for get_prime_areas function."""
    
    def test_returns_prime_areas(self):
        """Test that function returns prime areas only."""
        areas = get_prime_areas()
        
        # Should return a dictionary
        assert isinstance(areas, dict)
        
        # All areas should have location score >= 80
        for area in areas:
            assert LOCATION_DESIRABILITY[area] >= 80


class TestCalculateTotalPurchaseCostPercentage:
    """Tests for calculate_total_purchase_cost_percentage function."""
    
    def test_first_time_buyer(self):
        """Test for first-time buyer."""
        pct = calculate_total_purchase_cost_percentage(is_first_time=True)
        
        # Should be around 5-6% (stamp duty + notary + registration)
        assert pct > Decimal("0.04")
        assert pct < Decimal("0.07")
    
    def test_second_time_buyer(self):
        """Test for second-time buyer."""
        pct = calculate_total_purchase_cost_percentage(is_first_time=False)
        
        # Should be higher than first-time buyer
        pct_first = calculate_total_purchase_cost_percentage(is_first_time=True)
        assert pct > pct_first
    
    def test_with_agency_fees(self):
        """Test including agency fees."""
        pct_without = calculate_total_purchase_cost_percentage(include_agency_fees=False)
        pct_with = calculate_total_purchase_cost_percentage(include_agency_fees=True)
        
        # With agency fees should be higher
        assert pct_with > pct_without


class TestRentalYieldsData:
    """Tests for rental yields data consistency."""
    
    def test_all_yields_in_valid_range(self):
        """Test that all yields are in valid range (1-15%)."""
        for area, yield_rate in RENTAL_YIELDS.items():
            assert yield_rate >= Decimal("0.01"), f"{area} yield too low"
            assert yield_rate <= Decimal("0.15"), f"{area} yield too high"
    
    def test_prime_areas_have_lower_yields(self):
        """Test that prime areas generally have lower yields."""
        sliema_yield = RENTAL_YIELDS["sliema"]
        birkirkara_yield = RENTAL_YIELDS["birkirkara"]
        
        # Prime area should have lower yield than affordable area
        assert sliema_yield < birkirkara_yield


class TestLocationDesirabilityData:
    """Tests for location desirability data consistency."""
    
    def test_all_scores_in_valid_range(self):
        """Test that all scores are in valid range (0-100)."""
        for area, score in LOCATION_DESIRABILITY.items():
            assert score >= 0, f"{area} score too low"
            assert score <= 100, f"{area} score too high"
    
    def test_prime_areas_have_high_scores(self):
        """Test that prime areas have high desirability scores."""
        assert LOCATION_DESIRABILITY["sliema"] >= 90
        assert LOCATION_DESIRABILITY["st_julians"] >= 90
        assert LOCATION_DESIRABILITY["valletta"] >= 85
