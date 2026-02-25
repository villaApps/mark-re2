"""Tests for ROI calculator functions."""

from decimal import Decimal

import pytest

from src.calculators.roi_calculator import (
    calculate_cap_rate,
    calculate_cash_on_cash_return,
    calculate_gross_rental_yield,
    calculate_irr,
    calculate_mortgage_payment,
    calculate_price_to_rent_ratio,
    calculate_purchase_costs,
    calculate_total_interest,
)
from src.data.malta_market import (
    AGENCY_FEES_BUYER,
    NOTARY_FEES,
    REGISTRATION_FEES,
    calculate_stamp_duty_first_time,
    calculate_stamp_duty_second_time,
)


class TestCalculatePurchaseCosts:
    """Tests for calculate_purchase_costs function."""
    
    def test_first_time_buyer_below_threshold(self):
        """Test purchase costs for first-time buyer below €150k threshold."""
        price = Decimal("100000")
        costs = calculate_purchase_costs(price, is_first_time=True)
        
        # Stamp duty: 3.5% of €100,000 = €3,500
        expected_stamp_duty = Decimal("3500")
        # Notary: 1.5% of €100,000 = €1,500
        expected_notary = Decimal("1500")
        # Registration: 1% of €100,000 = €1,000
        expected_registration = Decimal("1000")
        
        assert costs.stamp_duty == expected_stamp_duty
        assert costs.notary_fees == expected_notary
        assert costs.registration_fees == expected_registration
        assert costs.agency_fees == Decimal("0")
        assert costs.total == expected_stamp_duty + expected_notary + expected_registration
    
    def test_first_time_buyer_above_threshold(self):
        """Test purchase costs for first-time buyer above €150k threshold."""
        price = Decimal("300000")
        costs = calculate_purchase_costs(price, is_first_time=True)
        
        # Stamp duty: 3.5% of €150,000 + 5% of €150,000 = €5,250 + €7,500 = €12,750
        expected_stamp_duty = Decimal("12750")
        # Notary: 1.5% of €300,000 = €4,500
        expected_notary = Decimal("4500")
        # Registration: 1% of €300,000 = €3,000
        expected_registration = Decimal("3000")
        
        assert costs.stamp_duty == expected_stamp_duty
        assert costs.notary_fees == expected_notary
        assert costs.registration_fees == expected_registration
        assert costs.total == expected_stamp_duty + expected_notary + expected_registration
    
    def test_second_time_buyer(self):
        """Test purchase costs for second-time buyer (flat 5% stamp duty)."""
        price = Decimal("300000")
        costs = calculate_purchase_costs(price, is_first_time=False)
        
        # Stamp duty: 5% of €300,000 = €15,000
        expected_stamp_duty = Decimal("15000")
        
        assert costs.stamp_duty == expected_stamp_duty
        assert costs.total > calculate_purchase_costs(price, is_first_time=True).total
    
    def test_with_agency_fees(self):
        """Test purchase costs including agency fees."""
        price = Decimal("300000")
        costs = calculate_purchase_costs(price, is_first_time=True, include_agency_fees=True)
        
        # Agency fees: 1.5% of €300,000 = €4,500
        expected_agency = Decimal("4500")
        
        assert costs.agency_fees == expected_agency
        assert costs.total == (
            costs.stamp_duty + costs.notary_fees + 
            costs.registration_fees + costs.agency_fees
        )
    
    def test_exact_threshold(self):
        """Test purchase costs at exactly €150,000 threshold."""
        price = Decimal("150000")
        costs = calculate_purchase_costs(price, is_first_time=True)
        
        # At exactly €150,000, all should be at 3.5%
        expected_stamp_duty = Decimal("5250")  # 3.5% of 150,000
        
        assert costs.stamp_duty == expected_stamp_duty


class TestCalculateMortgagePayment:
    """Tests for calculate_mortgage_payment function."""
    
    def test_standard_mortgage(self):
        """Test standard 25-year mortgage at 3.5%."""
        principal = Decimal("240000")  # 80% of 300k
        rate = Decimal("0.035")
        years = 25
        
        payment = calculate_mortgage_payment(principal, rate, years)
        
        # Expected monthly payment ~€1,201.58
        assert payment > Decimal("1200")
        assert payment < Decimal("1210")
    
    def test_zero_interest(self):
        """Test mortgage with zero interest rate."""
        principal = Decimal("240000")
        rate = Decimal("0")
        years = 25
        
        payment = calculate_mortgage_payment(principal, rate, years)
        
        # Should be simple division: 240,000 / (25 * 12) = 800
        expected = Decimal("800")
        assert payment == expected
    
    def test_shorter_term(self):
        """Test 15-year mortgage."""
        principal = Decimal("240000")
        rate = Decimal("0.035")
        years = 15
        
        payment_15 = calculate_mortgage_payment(principal, rate, years)
        payment_25 = calculate_mortgage_payment(principal, rate, 25)
        
        # Shorter term should have higher monthly payment
        assert payment_15 > payment_25
    
    def test_higher_rate(self):
        """Test mortgage with higher interest rate."""
        principal = Decimal("240000")
        years = 25
        
        payment_low = calculate_mortgage_payment(principal, Decimal("0.03"), years)
        payment_high = calculate_mortgage_payment(principal, Decimal("0.05"), years)
        
        # Higher rate should have higher monthly payment
        assert payment_high > payment_low
    
    def test_negative_principal_raises_error(self):
        """Test that negative principal raises ValueError."""
        with pytest.raises(ValueError, match="Principal cannot be negative"):
            calculate_mortgage_payment(Decimal("-1000"), Decimal("0.035"), 25)
    
    def test_zero_years_raises_error(self):
        """Test that zero years raises ValueError."""
        with pytest.raises(ValueError, match="Loan term must be positive"):
            calculate_mortgage_payment(Decimal("100000"), Decimal("0.035"), 0)


class TestCalculateTotalInterest:
    """Tests for calculate_total_interest function."""
    
    def test_standard_loan(self):
        """Test total interest for standard loan."""
        principal = Decimal("240000")
        rate = Decimal("0.035")
        years = 25
        
        total_interest = calculate_total_interest(principal, rate, years)
        
        # Total interest should be positive
        assert total_interest > Decimal("0")
        # Total interest should be less than principal for reasonable rates
        assert total_interest < principal
    
    def test_zero_interest(self):
        """Test total interest with zero rate."""
        principal = Decimal("240000")
        rate = Decimal("0")
        years = 25
        
        total_interest = calculate_total_interest(principal, rate, years)
        
        # Zero interest means zero total interest
        assert total_interest == Decimal("0")


class TestCalculateCapRate:
    """Tests for calculate_cap_rate function."""
    
    def test_standard_calculation(self):
        """Test standard cap rate calculation."""
        noi = Decimal("15000")
        price = Decimal("300000")
        
        cap_rate = calculate_cap_rate(noi, price)
        
        # Expected: 15,000 / 300,000 = 0.05 = 5%
        assert cap_rate == Decimal("0.0500")
    
    def test_high_cap_rate(self):
        """Test high cap rate property."""
        noi = Decimal("21000")
        price = Decimal("300000")
        
        cap_rate = calculate_cap_rate(noi, price)
        
        # Expected: 21,000 / 300,000 = 0.07 = 7%
        assert cap_rate == Decimal("0.0700")
    
    def test_zero_price_raises_error(self):
        """Test that zero price raises ValueError."""
        with pytest.raises(ValueError, match="Purchase price must be positive"):
            calculate_cap_rate(Decimal("15000"), Decimal("0"))
    
    def test_negative_price_raises_error(self):
        """Test that negative price raises ValueError."""
        with pytest.raises(ValueError, match="Purchase price must be positive"):
            calculate_cap_rate(Decimal("15000"), Decimal("-1000"))


class TestCalculateCashOnCashReturn:
    """Tests for calculate_cash_on_cash_return function."""
    
    def test_positive_return(self):
        """Test positive cash-on-cash return."""
        annual_cf = Decimal("5000")
        cash_invested = Decimal("75000")
        
        coc = calculate_cash_on_cash_return(annual_cf, cash_invested)
        
        # Expected: 5,000 / 75,000 = 0.0667 = 6.67%
        assert coc > Decimal("0.066")
        assert coc < Decimal("0.067")
    
    def test_high_return(self):
        """Test high cash-on-cash return."""
        annual_cf = Decimal("10000")
        cash_invested = Decimal("75000")
        
        coc = calculate_cash_on_cash_return(annual_cf, cash_invested)
        
        # Expected: 10,000 / 75,000 = 0.1333 = 13.33%
        assert coc > Decimal("0.13")
        assert coc < Decimal("0.14")
    
    def test_zero_cash_invested_raises_error(self):
        """Test that zero cash invested raises ValueError."""
        with pytest.raises(ValueError, match="Cash invested must be positive"):
            calculate_cash_on_cash_return(Decimal("5000"), Decimal("0"))


class TestCalculatePriceToRentRatio:
    """Tests for calculate_price_to_rent_ratio function."""
    
    def test_standard_ratio(self):
        """Test standard price-to-rent ratio."""
        price = Decimal("300000")
        monthly_rent = Decimal("1200")
        
        ratio = calculate_price_to_rent_ratio(price, monthly_rent)
        
        # Expected: 300,000 / (1,200 * 12) = 300,000 / 14,400 = 20.83
        assert ratio > Decimal("20")
        assert ratio < Decimal("21")
    
    def test_low_ratio(self):
        """Test low price-to-rent ratio (good for buying)."""
        price = Decimal("200000")
        monthly_rent = Decimal("1200")
        
        ratio = calculate_price_to_rent_ratio(price, monthly_rent)
        
        # Expected: 200,000 / 14,400 = 13.89
        assert ratio < Decimal("15")
    
    def test_high_ratio(self):
        """Test high price-to-rent ratio (better to rent)."""
        price = Decimal("500000")
        monthly_rent = Decimal("1200")
        
        ratio = calculate_price_to_rent_ratio(price, monthly_rent)
        
        # Expected: 500,000 / 14,400 = 34.72
        assert ratio > Decimal("30")
    
    def test_zero_rent_raises_error(self):
        """Test that zero rent raises ValueError."""
        with pytest.raises(ValueError, match="Monthly rent must be positive"):
            calculate_price_to_rent_ratio(Decimal("300000"), Decimal("0"))


class TestCalculateIRR:
    """Tests for calculate_irr function."""
    
    def test_simple_irr(self):
        """Test simple IRR calculation."""
        initial_investment = Decimal("100000")
        cash_flows = [
            Decimal("10000"),
            Decimal("10000"),
            Decimal("10000"),
            Decimal("110000"),  # Includes sale
        ]
        
        irr = calculate_irr(cash_flows, initial_investment)
        
        # Should be around 10%
        assert irr is not None
        assert irr > Decimal("0.08")
        assert irr < Decimal("0.12")
    
    def test_empty_cash_flows(self):
        """Test IRR with empty cash flows."""
        irr = calculate_irr([], Decimal("100000"))
        assert irr is None
    
    def test_negative_irr(self):
        """Test IRR with negative returns."""
        initial_investment = Decimal("100000")
        cash_flows = [
            Decimal("5000"),
            Decimal("5000"),
            Decimal("5000"),
            Decimal("80000"),  # Loss on sale
        ]
        
        irr = calculate_irr(cash_flows, initial_investment)
        
        # Should be negative
        assert irr is not None
        assert irr < Decimal("0")


class TestCalculateGrossRentalYield:
    """Tests for calculate_gross_rental_yield function."""
    
    def test_standard_yield(self):
        """Test standard gross rental yield."""
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
    
    def test_zero_price_raises_error(self):
        """Test that zero price raises ValueError."""
        with pytest.raises(ValueError, match="Property price must be positive"):
            calculate_gross_rental_yield(Decimal("0"), Decimal("1200"))
    
    def test_zero_rent(self):
        """Test with zero rent (should return zero yield)."""
        yield_rate = calculate_gross_rental_yield(Decimal("300000"), Decimal("0"))
        assert yield_rate == Decimal("0")
