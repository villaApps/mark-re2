"""
Unit tests for purchase costs calculator.

Tests all functions in the purchase_costs module with known values
to ensure accuracy of Malta property cost calculations.
"""

from decimal import Decimal
import pytest

from src.calculators.purchase_costs import (
    calculate_stamp_duty,
    calculate_notary_fees,
    calculate_registration_fees,
    calculate_agency_fees,
    calculate_purchase_costs,
    calculate_total_cash_needed,
)
from src.data.malta_market import (
    STAMP_DUTY_FIRST,
    STAMP_DUTY_REST,
    STAMP_DUTY_FIRST_THRESHOLD,
    NOTARY_FEES,
    AGENCY_FEES,
    REGISTRATION_FEES,
)


class TestStampDuty:
    """Tests for stamp duty calculations."""
    
    def test_first_time_buyer_below_threshold(self):
        """First-time buyer pays 3.5% on entire amount if below threshold."""
        price = Decimal("150000")
        duty = calculate_stamp_duty(price, is_first_time_buyer=True)
        expected = price * STAMP_DUTY_FIRST
        assert duty == expected.quantize(Decimal("0.01"))
        assert duty == Decimal("5250.00")
    
    def test_first_time_buyer_at_threshold(self):
        """First-time buyer at exact threshold."""
        price = STAMP_DUTY_FIRST_THRESHOLD
        duty = calculate_stamp_duty(price, is_first_time_buyer=True)
        expected = price * STAMP_DUTY_FIRST
        assert duty == expected.quantize(Decimal("0.01"))
        assert duty == Decimal("6125.00")
    
    def test_first_time_buyer_above_threshold(self):
        """First-time buyer pays 3.5% on first €175k, 5% on remainder."""
        price = Decimal("200000")
        duty = calculate_stamp_duty(price, is_first_time_buyer=True)
        # €175,000 * 3.5% + €25,000 * 5%
        expected = Decimal("6125.00") + Decimal("1250.00")
        assert duty == expected
        assert duty == Decimal("7375.00")
    
    def test_standard_buyer(self):
        """Standard buyer pays 5% on entire amount."""
        price = Decimal("200000")
        duty = calculate_stamp_duty(price, is_first_time_buyer=False)
        expected = price * STAMP_DUTY_REST
        assert duty == expected.quantize(Decimal("0.01"))
        assert duty == Decimal("10000.00")
    
    def test_standard_buyer_default(self):
        """Default is standard buyer (not first-time)."""
        price = Decimal("200000")
        duty_default = calculate_stamp_duty(price)
        duty_explicit = calculate_stamp_duty(price, is_first_time_buyer=False)
        assert duty_default == duty_explicit


class TestNotaryFees:
    """Tests for notary fee calculations."""
    
    def test_notary_fees_standard(self):
        """Notary fees are 1.5% of property price."""
        price = Decimal("300000")
        fees = calculate_notary_fees(price)
        expected = price * NOTARY_FEES
        assert fees == expected.quantize(Decimal("0.01"))
        assert fees == Decimal("4500.00")
    
    def test_notary_fees_small_property(self):
        """Notary fees for smaller property."""
        price = Decimal("150000")
        fees = calculate_notary_fees(price)
        assert fees == Decimal("2250.00")


class TestRegistrationFees:
    """Tests for registration fee calculations."""
    
    def test_registration_fees_standard(self):
        """Registration fees are 1% of property price."""
        price = Decimal("300000")
        fees = calculate_registration_fees(price)
        expected = price * REGISTRATION_FEES
        assert fees == expected.quantize(Decimal("0.01"))
        assert fees == Decimal("3000.00")
    
    def test_registration_fees_small_property(self):
        """Registration fees for smaller property."""
        price = Decimal("150000")
        fees = calculate_registration_fees(price)
        assert fees == Decimal("1500.00")


class TestAgencyFees:
    """Tests for agency fee calculations."""
    
    def test_agency_fees_buyer_pays(self):
        """Agency fees when buyer pays (1.5%)."""
        price = Decimal("300000")
        fees = calculate_agency_fees(price, buyer_pays=True)
        expected = price * AGENCY_FEES
        assert fees == expected.quantize(Decimal("0.01"))
        assert fees == Decimal("4500.00")
    
    def test_agency_fees_seller_pays(self):
        """Agency fees when seller pays (buyer pays 0)."""
        price = Decimal("300000")
        fees = calculate_agency_fees(price, buyer_pays=False)
        assert fees == Decimal("0.00")
    
    def test_agency_fees_default(self):
        """Default is seller pays (buyer pays 0)."""
        price = Decimal("300000")
        fees_default = calculate_agency_fees(price)
        fees_explicit = calculate_agency_fees(price, buyer_pays=False)
        assert fees_default == fees_explicit


class TestPurchaseCosts:
    """Tests for complete purchase cost calculations."""
    
    def test_purchase_costs_standard_buyer(self):
        """Complete purchase costs for standard buyer."""
        price = Decimal("300000")
        costs = calculate_purchase_costs(price, is_first_time_buyer=False)
        
        # Verify individual components
        assert costs.stamp_duty == Decimal("15000.00")  # 5%
        assert costs.notary_fees == Decimal("4500.00")  # 1.5%
        assert costs.registration_fees == Decimal("3000.00")  # 1%
        assert costs.agency_fees == Decimal("0.00")  # Seller pays
        
        # Verify total
        expected_total = Decimal("15000.00") + Decimal("4500.00") + Decimal("3000.00")
        assert costs.total == expected_total
        assert costs.total == Decimal("22500.00")
    
    def test_purchase_costs_first_time_buyer(self):
        """Complete purchase costs for first-time buyer."""
        price = Decimal("300000")
        costs = calculate_purchase_costs(price, is_first_time_buyer=True)
        
        # Stamp duty: €175k * 3.5% + €125k * 5% = €6,125 + €6,250 = €12,375
        assert costs.stamp_duty == Decimal("12375.00")
        assert costs.notary_fees == Decimal("4500.00")
        assert costs.registration_fees == Decimal("3000.00")
        
        expected_total = Decimal("12375.00") + Decimal("4500.00") + Decimal("3000.00")
        assert costs.total == expected_total
        assert costs.total == Decimal("19875.00")
    
    def test_purchase_costs_with_agency_fees(self):
        """Purchase costs when buyer pays agency fees."""
        price = Decimal("300000")
        costs = calculate_purchase_costs(
            price, 
            is_first_time_buyer=False, 
            buyer_pays_agency=True
        )
        
        assert costs.agency_fees == Decimal("4500.00")
        expected_total = Decimal("15000.00") + Decimal("4500.00") + Decimal("3000.00") + Decimal("4500.00")
        assert costs.total == expected_total
        assert costs.total == Decimal("27000.00")
    
    def test_purchase_costs_with_other_fees(self):
        """Purchase costs with additional miscellaneous fees."""
        price = Decimal("300000")
        other = Decimal("500")
        costs = calculate_purchase_costs(
            price, 
            is_first_time_buyer=False,
            other_fees=other
        )
        
        assert costs.other_fees == Decimal("500.00")
        expected_total = Decimal("22500.00") + Decimal("500.00")
        assert costs.total == expected_total


class TestTotalCashNeeded:
    """Tests for total cash needed calculation."""
    
    def test_total_cash_standard(self):
        """Total cash needed for standard purchase."""
        price = Decimal("300000")
        cash = calculate_total_cash_needed(
            price,
            down_payment_percent=Decimal("0.20"),
            is_first_time_buyer=False
        )
        
        # Down payment: 20% of €300k = €60k
        assert cash["down_payment"] == Decimal("60000.00")
        # Closing costs: €22.5k (from previous test)
        assert cash["closing_costs"] == Decimal("22500.00")
        # Total: €60k + €22.5k = €82.5k
        assert cash["total_cash"] == Decimal("82500.00")
    
    def test_total_cash_first_time_buyer(self):
        """Total cash needed for first-time buyer."""
        price = Decimal("300000")
        cash = calculate_total_cash_needed(
            price,
            down_payment_percent=Decimal("0.20"),
            is_first_time_buyer=True
        )
        
        # Down payment: €60k
        assert cash["down_payment"] == Decimal("60000.00")
        # Closing costs: €19.875k (reduced stamp duty)
        assert cash["closing_costs"] == Decimal("19875.00")
        # Total: €60k + €19.875k = €79.875k
        assert cash["total_cash"] == Decimal("79875.00")
    
    def test_total_cash_low_down_payment(self):
        """Total cash needed with minimum down payment."""
        price = Decimal("300000")
        cash = calculate_total_cash_needed(
            price,
            down_payment_percent=Decimal("0.10"),
            is_first_time_buyer=False
        )
        
        # Down payment: 10% of €300k = €30k
        assert cash["down_payment"] == Decimal("30000.00")
        assert cash["total_cash"] == Decimal("52500.00")


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_very_small_property_price(self):
        """Test with very small property price."""
        price = Decimal("50000")
        costs = calculate_purchase_costs(price, is_first_time_buyer=True)
        # Should still calculate correctly
        assert costs.stamp_duty == Decimal("1750.00")  # 3.5% of €50k
        assert costs.total > 0
    
    def test_large_property_price(self):
        """Test with large property price."""
        price = Decimal("1000000")
        costs = calculate_purchase_costs(price, is_first_time_buyer=False)
        # 5% stamp duty on €1M = €50k
        assert costs.stamp_duty == Decimal("50000.00")
        assert costs.total > 0
    
    def test_exact_threshold_calculation(self):
        """Test at exact €175,000 threshold."""
        price = Decimal("175000")
        
        # First-time buyer
        duty_first = calculate_stamp_duty(price, is_first_time_buyer=True)
        assert duty_first == Decimal("6125.00")  # 3.5% of €175k
        
        # Standard buyer
        duty_standard = calculate_stamp_duty(price, is_first_time_buyer=False)
        assert duty_standard == Decimal("8750.00")  # 5% of €175k
