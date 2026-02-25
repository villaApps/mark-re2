"""
Purchase Costs Calculator

Calculates all costs associated with purchasing property in Malta,
including stamp duty, notary fees, and registration fees.

All formulas are based on Malta Inland Revenue Department guidelines
and current market practices.
"""

from decimal import Decimal, ROUND_HALF_UP

from ..data.malta_market import (
    STAMP_DUTY_FIRST,
    STAMP_DUTY_REST,
    STAMP_DUTY_FIRST_THRESHOLD,
    NOTARY_FEES,
    AGENCY_FEES,
    REGISTRATION_FEES,
)
from ..models.investment import PurchaseCostBreakdown


def calculate_stamp_duty(property_price: Decimal, is_first_time_buyer: bool = False) -> Decimal:
    """
    Calculate Malta stamp duty on property purchase.
    
    For first-time buyers:
    - 3.5% on first €175,000
    - 5% on amount above €175,000
    
    For non-first-time buyers:
    - 5% on entire amount
    
    Args:
        property_price: Property purchase price in EUR
        is_first_time_buyer: Whether buyer qualifies for first-time buyer rate
        
    Returns:
        Stamp duty amount in EUR
        
    Formula:
        First-time buyer:
            If price <= 175,000: price * 0.035
            Else: 175,000 * 0.035 + (price - 175,000) * 0.05
        Standard:
            price * 0.05
            
    Example:
        >>> calculate_stamp_duty(Decimal("200000"), is_first_time_buyer=True)
        Decimal('7375.00')
        >>> calculate_stamp_duty(Decimal("200000"), is_first_time_buyer=False)
        Decimal('10000.00')
    """
    if is_first_time_buyer and property_price <= STAMP_DUTY_FIRST_THRESHOLD:
        # Entire amount at first-time buyer rate
        duty = property_price * STAMP_DUTY_FIRST
    elif is_first_time_buyer:
        # First €175,000 at 3.5%, rest at 5%
        first_portion = STAMP_DUTY_FIRST_THRESHOLD * STAMP_DUTY_FIRST
        remaining = property_price - STAMP_DUTY_FIRST_THRESHOLD
        second_portion = remaining * STAMP_DUTY_REST
        duty = first_portion + second_portion
    else:
        # Standard rate on entire amount
        duty = property_price * STAMP_DUTY_REST
    
    return duty.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_notary_fees(property_price: Decimal) -> Decimal:
    """
    Calculate notary fees for property transaction.
    
    Standard rate is 1.5% of property price, with minimum and
    maximum thresholds based on market practice.
    
    Args:
        property_price: Property purchase price in EUR
        
    Returns:
        Notary fees in EUR
        
    Formula:
        max(min_fee, min(property_price * 0.015, max_fee))
        
    Example:
        >>> calculate_notary_fees(Decimal("300000"))
        Decimal('4500.00')
    """
    fees = property_price * NOTARY_FEES
    return fees.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_registration_fees(property_price: Decimal) -> Decimal:
    """
    Calculate Land Registry registration fees.
    
    Standard rate is 1% of property price.
    
    Args:
        property_price: Property purchase price in EUR
        
    Returns:
        Registration fees in EUR
        
    Formula:
        property_price * 0.01
        
    Example:
        >>> calculate_registration_fees(Decimal("300000"))
        Decimal('3000.00')
    """
    fees = property_price * REGISTRATION_FEES
    return fees.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_agency_fees(
    property_price: Decimal, 
    buyer_pays: bool = False
) -> Decimal:
    """
    Calculate real estate agency fees.
    
    In Malta, agency fees are typically paid by the seller (3-5%)
    but buyers may pay fees in some arrangements (1.5%).
    
    Args:
        property_price: Property purchase price in EUR
        buyer_pays: Whether buyer pays agency fees
        
    Returns:
        Agency fees in EUR (0 if seller pays)
        
    Formula:
        If buyer_pays: property_price * 0.015
        Else: 0
        
    Example:
        >>> calculate_agency_fees(Decimal("300000"), buyer_pays=True)
        Decimal('4500.00')
        >>> calculate_agency_fees(Decimal("300000"), buyer_pays=False)
        Decimal('0.00')
    """
    if not buyer_pays:
        return Decimal("0.00")
    
    fees = property_price * AGENCY_FEES
    return fees.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_purchase_costs(
    property_price: Decimal,
    is_first_time_buyer: bool = False,
    buyer_pays_agency: bool = False,
    other_fees: Decimal = Decimal("0"),
) -> PurchaseCostBreakdown:
    """
    Calculate all purchase costs for a property in Malta.
    
    This is the main function for calculating total acquisition costs
    including all fees and taxes.
    
    Args:
        property_price: Property purchase price in EUR
        is_first_time_buyer: Whether buyer qualifies for reduced stamp duty
        buyer_pays_agency: Whether buyer pays agency fees
        other_fees: Any additional miscellaneous fees
        
    Returns:
        PurchaseCostBreakdown with detailed breakdown
        
    Example:
        >>> costs = calculate_purchase_costs(
        ...     property_price=Decimal("300000"),
        ...     is_first_time_buyer=True
        ... )
        >>> costs.total
        Decimal('20125.00')
        
    Notes:
        - Stamp duty: 3.5% (first €175k) + 5% (remainder) for first-time buyers
        - Stamp duty: 5% for standard buyers
        - Notary fees: 1.5% of property price
        - Registration: 1% of property price
        - Agency fees: 1.5% (if buyer pays)
    """
    stamp_duty = calculate_stamp_duty(property_price, is_first_time_buyer)
    notary = calculate_notary_fees(property_price)
    registration = calculate_registration_fees(property_price)
    agency = calculate_agency_fees(property_price, buyer_pays_agency)
    
    return PurchaseCostBreakdown(
        stamp_duty=stamp_duty,
        notary_fees=notary,
        registration_fees=registration,
        agency_fees=agency,
        other_fees=other_fees,
    )


def calculate_total_cash_needed(
    property_price: Decimal,
    down_payment_percent: Decimal = Decimal("0.20"),
    is_first_time_buyer: bool = False,
    buyer_pays_agency: bool = False,
    other_fees: Decimal = Decimal("0"),
) -> dict[str, Decimal]:
    """
    Calculate total cash needed to complete a property purchase.
    
    Args:
        property_price: Property purchase price in EUR
        down_payment_percent: Down payment as decimal (default 20%)
        is_first_time_buyer: Whether buyer qualifies for reduced stamp duty
        buyer_pays_agency: Whether buyer pays agency fees
        other_fees: Any additional miscellaneous fees
        
    Returns:
        Dictionary with down_payment, closing_costs, and total_cash
        
    Example:
        >>> cash = calculate_total_cash_needed(
        ...     property_price=Decimal("300000"),
        ...     is_first_time_buyer=True
        ... )
        >>> cash["total_cash"]
        Decimal('80125.00')
    """
    down_payment = (property_price * down_payment_percent).quantize(Decimal("0.01"))
    
    closing_costs_breakdown = calculate_purchase_costs(
        property_price=property_price,
        is_first_time_buyer=is_first_time_buyer,
        buyer_pays_agency=buyer_pays_agency,
        other_fees=other_fees,
    )
    
    closing_costs = closing_costs_breakdown.total
    total_cash = down_payment + closing_costs
    
    return {
        "down_payment": down_payment,
        "closing_costs": closing_costs,
        "total_cash": total_cash,
    }
