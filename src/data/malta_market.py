"""
Malta Property Market Constants

This module contains Malta-specific constants for property investment calculations.
All rates are expressed as decimals (e.g., 0.035 = 3.5%).

Sources:
- Stamp duty: Malta Inland Revenue Department
- Notary fees: Malta Notarial Council guidelines
- Agency fees: Malta real estate market standard
- Registration: Land Registry fees
"""

from decimal import Decimal

# =============================================================================
# PURCHASE COSTS
# =============================================================================

# Stamp Duty Rates
# First-time buyers get reduced rate on first €175,000
STAMP_DUTY_FIRST = Decimal("0.035")  # 3.5% for first-time buyers
STAMP_DUTY_REST = Decimal("0.05")    # 5% standard rate
STAMP_DUTY_FIRST_THRESHOLD = Decimal("175000")  # Threshold for first-time buyer rate

# Professional Fees
NOTARY_FEES = Decimal("0.015")       # 1.5% of property price
AGENCY_FEES = Decimal("0.015")       # 1.5% of property price (typically paid by seller)
REGISTRATION_FEES = Decimal("0.01")  # 1% Land Registry fee

# AIP (Acquisition of Immovable Property) Permit
# Non-Maltese/EU citizens may need AIP permit
AIP_PERMIT_FEE = Decimal("233")  # Fixed fee in EUR

# =============================================================================
# RENTAL MARKET DATA
# =============================================================================

# Average gross rental yields by location (as decimal)
# Data based on 2023-2024 Malta property market research
RENTAL_YIELDS: dict[str, Decimal] = {
    # Prime locations - lower yields, higher capital appreciation
    "sliema": Decimal("0.045"),       # 4.5% - Premium area
    "st_julians": Decimal("0.048"),   # 4.8% - Popular with expats
    "valletta": Decimal("0.050"),     # 5.0% - Capital city
    
    # Secondary locations - moderate yields
    "gzira": Decimal("0.052"),        # 5.2%
    "msida": Decimal("0.053"),        # 5.3%
    "ta_xbiex": Decimal("0.050"),     # 5.0%
    
    # Suburban locations - higher yields
    "mosta": Decimal("0.055"),        # 5.5%
    "birkirkara": Decimal("0.056"),   # 5.6%
    "qormi": Decimal("0.058"),        # 5.8%
    "zabbar": Decimal("0.060"),       # 6.0%
    
    # Northern locations
    "mellieha": Decimal("0.055"),     # 5.5%
    "bugibba": Decimal("0.060"),      # 6.0% - Tourist rental area
    "st_pauls_bay": Decimal("0.058"), # 5.8%
    
    # Southern locations
    "marsaskala": Decimal("0.057"),   # 5.7%
    "zejtun": Decimal("0.062"),       # 6.2%
    
    # Gozo
    "victoria_gozo": Decimal("0.065"), # 6.5% - Higher yields, seasonal
    "xaghra": Decimal("0.068"),        # 6.8%
    "marsalforn": Decimal("0.070"),    # 7.0% - Tourist area
}

# Default yield when location not specified
DEFAULT_RENTAL_YIELD = Decimal("0.055")  # 5.5%

# =============================================================================
# OPERATING EXPENSES
# =============================================================================

# Typical operating expense ratios (as decimal of gross rent)
PROPERTY_MANAGEMENT_FEE = Decimal("0.10")  # 10% of rent
MAINTENANCE_RESERVE = Decimal("0.05")      # 5% of rent for repairs
INSURANCE_ANNUAL_RATE = Decimal("0.002")   # 0.2% of property value

# Vacancy assumptions
DEFAULT_VACANCY_RATE = Decimal("0.05")     # 5% annual vacancy
HIGH_SEASONAL_VACANCY = Decimal("0.15")    # 15% for tourist areas

# =============================================================================
# FINANCING
# =============================================================================

# Typical mortgage terms in Malta
DEFAULT_LOAN_TERM = 25  # years
MAX_LOAN_TERM = 40      # years
MIN_DOWN_PAYMENT = Decimal("0.10")  # 10% minimum
DEFAULT_INTEREST_RATE = Decimal("0.035")  # 3.5% (current market rate)

# =============================================================================
# TAXATION
# =============================================================================

# Rental income tax (simplified)
# Malta has progressive rates, this is an effective average
EFFECTIVE_RENTAL_TAX_RATE = Decimal("0.15")  # 15% effective rate

# Capital Gains Tax
CAPITAL_GAINS_TAX = Decimal("0.08")  # 8% on property transfers
CAPITAL_GAINS_TAX_HELD_3YRS = Decimal("0.05")  # 5% if held 3+ years

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_rental_yield(location: str) -> Decimal:
    """
    Get the expected rental yield for a specific location.
    
    Args:
        location: Name of the location in Malta
        
    Returns:
        Expected gross rental yield as Decimal
        
    Example:
        >>> get_rental_yield("sliema")
        Decimal('0.045')
    """
    normalized_location = location.lower().strip()
    return RENTAL_YIELDS.get(normalized_location, DEFAULT_RENTAL_YIELD)


def estimate_monthly_rent(property_price: Decimal, location: str) -> Decimal:
    """
    Estimate monthly rent based on property price and location.
    
    Formula: (Property Price * Annual Yield) / 12
    
    Args:
        property_price: Property purchase price in EUR
        location: Location in Malta
        
    Returns:
        Estimated monthly rent in EUR
        
    Example:
        >>> estimate_monthly_rent(Decimal("300000"), "sliema")
        Decimal('1125.00')
    """
    annual_yield = get_rental_yield(location)
    annual_rent = property_price * annual_yield
    return (annual_rent / Decimal("12")).quantize(Decimal("0.01"))
