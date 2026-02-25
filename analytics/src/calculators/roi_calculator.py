"""ROI Calculator - Core investment return calculations.

This module provides pure, testable functions for calculating
real estate investment returns and metrics.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple

import numpy as np

from ..data.malta_market import (
    AGENCY_FEES_BUYER,
    NOTARY_FEES,
    REGISTRATION_FEES,
    calculate_stamp_duty_first_time,
    calculate_stamp_duty_second_time,
)
from ..models.analysis import (
    CashFlowBreakdown,
    PurchaseCostBreakdown,
    ROIAnalysis,
)
from ..models.investment import InvestmentScenario


# Precision for Decimal calculations
DECIMAL_PRECISION = Decimal("0.01")


def calculate_purchase_costs(
    property_price: Decimal,
    is_first_time: bool = True,
    include_agency_fees: bool = False,
) -> PurchaseCostBreakdown:
    """Calculate all purchase costs for a property in Malta.
    
    Args:
        property_price: The property purchase price
        is_first_time: Whether this is a first-time purchase (affects stamp duty)
        include_agency_fees: Whether to include buyer's agency fees
        
    Returns:
        PurchaseCostBreakdown with all cost components
        
    Example:
        >>> costs = calculate_purchase_costs(Decimal("300000"), is_first_time=True)
        >>> print(costs.total)
        19500.00
    """
    # Calculate stamp duty based on buyer type
    if is_first_time:
        stamp_duty = calculate_stamp_duty_first_time(property_price)
    else:
        stamp_duty = calculate_stamp_duty_second_time(property_price)
    
    # Calculate other fees
    notary_fees = (property_price * NOTARY_FEES).quantize(DECIMAL_PRECISION)
    registration_fees = (property_price * REGISTRATION_FEES).quantize(DECIMAL_PRECISION)
    agency_fees = (
        (property_price * AGENCY_FEES_BUYER).quantize(DECIMAL_PRECISION)
        if include_agency_fees
        else Decimal("0")
    )
    
    return PurchaseCostBreakdown(
        stamp_duty=stamp_duty.quantize(DECIMAL_PRECISION),
        notary_fees=notary_fees,
        registration_fees=registration_fees,
        agency_fees=agency_fees,
    )


def calculate_mortgage_payment(
    principal: Decimal,
    annual_rate: Decimal,
    years: int,
) -> Decimal:
    """Calculate monthly mortgage payment using standard amortization formula.
    
    Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
    Where:
        M = Monthly payment
        P = Principal (loan amount)
        r = Monthly interest rate
        n = Total number of payments
        
    Args:
        principal: The loan amount (principal)
        annual_rate: Annual interest rate (e.g., 0.035 for 3.5%)
        years: Loan term in years
        
    Returns:
        Monthly mortgage payment amount
        
    Raises:
        ValueError: If principal is negative or years is not positive
        
    Example:
        >>> payment = calculate_mortgage_payment(Decimal("240000"), Decimal("0.035"), 25)
        >>> print(payment)
        1201.58
    """
    if principal < Decimal("0"):
        raise ValueError("Principal cannot be negative")
    if years <= 0:
        raise ValueError("Loan term must be positive")
    
    # Handle zero interest rate case
    if annual_rate == Decimal("0"):
        num_payments = years * 12
        return (principal / Decimal(num_payments)).quantize(DECIMAL_PRECISION)
    
    # Convert to monthly rate and total payments
    monthly_rate = annual_rate / Decimal("12")
    num_payments = years * 12
    
    # Calculate using the amortization formula
    # Convert to float for the power operation, then back to Decimal
    monthly_rate_f = float(monthly_rate)
    num_payments_f = float(num_payments)
    principal_f = float(principal)
    
    # M = P * [r(1+r)^n] / [(1+r)^n - 1]
    factor = (1 + monthly_rate_f) ** num_payments_f
    payment_f = principal_f * (monthly_rate_f * factor) / (factor - 1)
    
    return Decimal(str(payment_f)).quantize(DECIMAL_PRECISION)


def calculate_total_interest(
    principal: Decimal,
    annual_rate: Decimal,
    years: int,
) -> Decimal:
    """Calculate total interest paid over the life of a loan.
    
    Args:
        principal: The loan amount
        annual_rate: Annual interest rate
        years: Loan term in years
        
    Returns:
        Total interest paid over the loan term
        
    Example:
        >>> interest = calculate_total_interest(Decimal("240000"), Decimal("0.035"), 25)
        >>> print(interest)
        120474.00
    """
    monthly_payment = calculate_mortgage_payment(principal, annual_rate, years)
    total_payments = monthly_payment * Decimal(years * 12)
    return (total_payments - principal).quantize(DECIMAL_PRECISION)


def calculate_cap_rate(
    net_operating_income: Decimal,
    purchase_price: Decimal,
) -> Decimal:
    """Calculate Capitalization Rate (Cap Rate).
    
    Cap Rate = Net Operating Income / Purchase Price
    
    This metric shows the unlevered return on a property, useful for
    comparing properties regardless of financing.
    
    Args:
        net_operating_income: Annual NOI (rental income minus operating expenses)
        purchase_price: Property purchase price
        
    Returns:
        Cap rate as a decimal (e.g., 0.055 for 5.5%)
        
    Raises:
        ValueError: If purchase price is zero or negative
        
    Example:
        >>> cap_rate = calculate_cap_rate(Decimal("15000"), Decimal("300000"))
        >>> print(cap_rate)
        0.0500
    """
    if purchase_price <= Decimal("0"):
        raise ValueError("Purchase price must be positive")
    
    return (net_operating_income / purchase_price).quantize(Decimal("0.0001"))


def calculate_cash_on_cash_return(
    annual_cash_flow: Decimal,
    cash_invested: Decimal,
) -> Decimal:
    """Calculate Cash-on-Cash Return.
    
    Cash-on-Cash = Annual Cash Flow / Cash Invested
    
    This shows the return on the actual cash invested, accounting for
    leverage from financing.
    
    Args:
        annual_cash_flow: Annual cash flow after all expenses and mortgage
        cash_invested: Total cash invested (down payment + closing costs)
        
    Returns:
        Cash-on-cash return as a decimal
        
    Raises:
        ValueError: If cash invested is zero or negative
        
    Example:
        >>> coc = calculate_cash_on_cash_return(Decimal("5000"), Decimal("75000"))
        >>> print(coc)
        0.0667
    """
    if cash_invested <= Decimal("0"):
        raise ValueError("Cash invested must be positive")
    
    return (annual_cash_flow / cash_invested).quantize(Decimal("0.0001"))


def calculate_price_to_rent_ratio(
    property_price: Decimal,
    monthly_rent: Decimal,
) -> Decimal:
    """Calculate Price-to-Rent Ratio.
    
    Ratio = Property Price / Annual Rent
    
    This metric helps identify potentially overvalued or undervalued markets.
    - Under 15: Potentially good for buying
    - 15-20: Neutral
    - Over 20: Potentially better to rent
    
    Args:
        property_price: Property purchase price
        monthly_rent: Monthly rental income
        
    Returns:
        Price-to-rent ratio
        
    Raises:
        ValueError: If monthly rent is zero or negative
        
    Example:
        >>> ratio = calculate_price_to_rent_ratio(Decimal("300000"), Decimal("1200"))
        >>> print(ratio)
        20.83
    """
    if monthly_rent <= Decimal("0"):
        raise ValueError("Monthly rent must be positive")
    
    annual_rent = monthly_rent * Decimal("12")
    return (property_price / annual_rent).quantize(DECIMAL_PRECISION)


def calculate_irr(
    cash_flows: List[Decimal],
    initial_investment: Decimal,
) -> Optional[Decimal]:
    """Calculate Internal Rate of Return (IRR).
    
    IRR is the discount rate that makes the net present value (NPV)
    of all cash flows equal to zero.
    
    Args:
        cash_flows: List of annual cash flows (positive for inflows)
        initial_investment: Initial investment amount (positive number)
        
    Returns:
        IRR as a decimal, or None if calculation fails
        
    Example:
        >>> irr = calculate_irr([5000, 5200, 5400, 5600, 100000], 75000)
        >>> print(irr)
        0.0892
    """
    if not cash_flows:
        return None
    
    # Build cash flow array: negative initial investment, then positive cash flows
    # numpy expects: [initial_investment] + cash_flows where initial is negative
    cf_array = [-float(initial_investment)] + [float(cf) for cf in cash_flows]
    
    try:
        irr_result = np.irr(cf_array)
        if np.isnan(irr_result) or np.isinf(irr_result):
            return None
        return Decimal(str(irr_result)).quantize(Decimal("0.0001"))
    except (ValueError, RuntimeError):
        return None


def calculate_gross_rental_yield(
    property_price: Decimal,
    monthly_rent: Decimal,
) -> Decimal:
    """Calculate Gross Rental Yield.
    
    Gross Yield = (Monthly Rent * 12) / Property Price
    
    This is a simple metric that doesn't account for expenses.
    
    Args:
        property_price: Property purchase price
        monthly_rent: Monthly rental income
        
    Returns:
        Gross rental yield as a decimal
        
    Raises:
        ValueError: If property price or rent is not positive
    """
    if property_price <= Decimal("0"):
        raise ValueError("Property price must be positive")
    if monthly_rent < Decimal("0"):
        raise ValueError("Monthly rent cannot be negative")
    
    annual_rent = monthly_rent * Decimal("12")
    return (annual_rent / property_price).quantize(Decimal("0.0001"))


def analyze_investment(
    scenario: InvestmentScenario,
    property_id: str = "PROP-001",
) -> Tuple[ROIAnalysis, PurchaseCostBreakdown, CashFlowBreakdown]:
    """Perform complete ROI analysis for an investment scenario.
    
    This is the main analysis function that calculates all metrics
    for a property investment opportunity.
    
    Args:
        scenario: InvestmentScenario with all input parameters
        property_id: Unique identifier for the property
        
    Returns:
        Tuple of (ROIAnalysis, PurchaseCostBreakdown, CashFlowBreakdown)
    """
    # Import here to avoid circular imports
    from .cash_flow import calculate_cash_flow
    from .projections import project_10_year_returns
    from ..scoring.opportunity_scorer import score_opportunity
    
    # Calculate purchase costs
    purchase_costs = calculate_purchase_costs(
        scenario.property_price,
        scenario.is_first_time_buyer,
        scenario.include_agency_fees,
    )
    
    # Calculate total cash invested
    total_cash_invested = scenario.down_payment_amount + purchase_costs.total
    
    # Calculate mortgage payment
    monthly_mortgage = calculate_mortgage_payment(
        scenario.loan_amount,
        scenario.loan_interest_rate,
        scenario.loan_term_years,
    )
    annual_mortgage = monthly_mortgage * Decimal("12")
    
    # Calculate total interest
    total_interest = calculate_total_interest(
        scenario.loan_amount,
        scenario.loan_interest_rate,
        scenario.loan_term_years,
    )
    
    # Calculate cash flow
    cash_flow = calculate_cash_flow(scenario, monthly_mortgage)
    
    # Calculate returns
    cap_rate = calculate_cap_rate(
        cash_flow.net_operating_income,
        scenario.property_price,
    )
    
    cash_on_cash = calculate_cash_on_cash_return(
        cash_flow.annual_cash_flow,
        total_cash_invested,
    )
    
    gross_yield = calculate_gross_rental_yield(
        scenario.property_price,
        scenario.monthly_rent,
    )
    
    net_yield = calculate_cap_rate(
        cash_flow.net_operating_income,
        scenario.property_price,
    )
    
    price_to_rent = calculate_price_to_rent_ratio(
        scenario.property_price,
        scenario.monthly_rent,
    )
    
    # Calculate 10-year projection
    projection = project_10_year_returns(scenario)
    irr_10_year = projection.irr if projection else None
    
    # Score the opportunity
    score_result = score_opportunity(
        cash_on_cash=cash_on_cash,
        cap_rate=cap_rate,
        monthly_cash_flow=cash_flow.monthly_cash_flow,
        area=scenario.property_area,
        price_to_rent=price_to_rent,
    )
    
    # Build ROI Analysis
    analysis = ROIAnalysis(
        property_id=property_id,
        scenario_name=scenario.scenario_name,
        property_price=scenario.property_price,
        area=scenario.property_area,
        total_purchase_cost=purchase_costs.total,
        closing_costs_breakdown=purchase_costs,
        total_cash_invested=total_cash_invested,
        loan_amount=scenario.loan_amount,
        monthly_mortgage_payment=monthly_mortgage,
        annual_mortgage_payment=annual_mortgage,
        total_interest_paid=total_interest,
        cash_flow=cash_flow,
        cap_rate=cap_rate,
        cash_on_cash_return=cash_on_cash,
        gross_rental_yield=gross_yield,
        net_rental_yield=net_yield,
        price_to_rent_ratio=price_to_rent,
        projection_10_year=projection,
        irr_10_year=irr_10_year,
        opportunity_score=score_result["score"],
        risk_level=score_result["risk_level"],
        recommendation=score_result["recommendation"],
    )
    
    return analysis, purchase_costs, cash_flow
