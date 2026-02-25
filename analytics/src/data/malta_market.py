"""Malta-specific property market constants and data.

This module contains all Malta-specific financial constants for property investment
analysis, including purchase costs, rental yields, and operating expenses.
"""

from decimal import Decimal
from typing import Dict, Optional

# =============================================================================
# PURCHASE COSTS (% of property price)
# =============================================================================

# Stamp Duty - First Time Buyers
# 3.5% on first €150,000, 5% on remainder
STAMP_DUTY_FIRST_TIME = Decimal("0.035")  # 3.5%
STAMP_DUTY_FIRST_TIME_REMAINDER = Decimal("0.05")  # 5%
STAMP_DUTY_FIRST_TIME_THRESHOLD = Decimal("150000")  # €150,000 threshold

# Stamp Duty - Second/Subsequent Property
STAMP_DUTY_SECOND_TIME = Decimal("0.05")  # 5% flat rate

# Notary Fees (typically 1-2%, average ~1.5%)
NOTARY_FEES = Decimal("0.015")  # 1.5%

# Agency Fees (when buying, sometimes paid by buyer)
AGENCY_FEES_BUYER = Decimal("0.015")  # 1.5%

# Registration Fees (approximate)
REGISTRATION_FEES = Decimal("0.01")  # 1%

# =============================================================================
# RENTAL MARKET - Annual Yields by Area
# =============================================================================

# Annual rental yields by area (as decimal, e.g., 0.045 = 4.5%)
RENTAL_YIELDS: Dict[str, Decimal] = {
    # Prime coastal areas (lower yields, higher appreciation)
    "sliema": Decimal("0.045"),           # 4.5% - Premium area
    "st_julians": Decimal("0.048"),       # 4.8% - Nightlife/tourism hub
    "valletta": Decimal("0.050"),         # 5.0% - Capital city
    "gzira": Decimal("0.046"),            # 4.6% - Central location
    "msida": Decimal("0.047"),            # 4.7% - Near university
    "ta_xbiex": Decimal("0.044"),         # 4.4% - Upscale marina area
    "pieta": Decimal("0.048"),            # 4.8% - Central, near hospital
    
    # Central areas (balanced yields)
    "birkirkara": Decimal("0.058"),       # 5.8% - Most populous
    "mosta": Decimal("0.055"),            # 5.5% - Large town
    "naxxar": Decimal("0.054"),           # 5.4% - Growing area
    "lija": Decimal("0.056"),             # 5.6% - Central
    "balzan": Decimal("0.053"),           # 5.3% - Residential
    "attard": Decimal("0.052"),           # 5.2% - Residential
    "iklin": Decimal("0.055"),            # 5.5% - Residential
    "swieqi": Decimal("0.050"),           # 5.0% - Upscale residential
    "pembroke": Decimal("0.051"),         # 5.1% - Near St Julian's
    "santa_venera": Decimal("0.057"),     # 5.7% - Affordable central
    "hamrun": Decimal("0.060"),           # 6.0% - Affordable
    "qormi": Decimal("0.059"),            # 5.9% - Large town
    "zabbar": Decimal("0.058"),           # 5.8% - South eastern
    "fgura": Decimal("0.059"),            # 5.9% - South eastern
    "paola": Decimal("0.061"),            # 6.1% - Affordable
    "marsa": Decimal("0.062"),            # 6.2% - Industrial/residential
    
    # Northern areas (tourism, holiday rentals)
    "mellieha": Decimal("0.040"),         # 4.0% - Holiday homes, low yield
    "st_pauls_bay": Decimal("0.052"),     # 5.2% - Mixed residential/tourism
    "bugibba": Decimal("0.053"),          # 5.3% - Tourism area
    "qawra": Decimal("0.054"),            # 5.4% - Tourism area
    "xemxija": Decimal("0.051"),          # 5.1% - Residential
    "manikata": Decimal("0.045"),         # 4.5% - Rural, low volume
    
    # Southern areas (higher yields, lower prices)
    "birzebbuga": Decimal("0.060"),       # 6.0% - Affordable coastal
    "marsaskala": Decimal("0.057"),       # 5.7% - Growing area
    "marsaxlokk": Decimal("0.055"),       # 5.5% - Fishing village
    "zurrieq": Decimal("0.058"),          # 5.8% - Large village
    "safi": Decimal("0.059"),             # 5.9% - Small village
    "mqabba": Decimal("0.060"),           # 6.0% - Affordable
    "qrendi": Decimal("0.058"),           # 5.8% - Rural
    "siggiewi": Decimal("0.056"),         # 5.6% - Rural
    "dingli": Decimal("0.054"),           # 5.4% - Rural
    "rabat": Decimal("0.055"),            # 5.5% - Historic
    "mdina": Decimal("0.048"),            # 4.8% - Historic, limited supply
    "zebbug": Decimal("0.057"),           # 5.7% - South central
    "senglea": Decimal("0.055"),          # 5.5% - Three cities
    "cospicua": Decimal("0.056"),         # 5.6% - Three cities
    "vittoriosa": Decimal("0.054"),       # 5.4% - Three cities
    "kalkara": Decimal("0.057"),          # 5.7% - Three cities area
    "xghajra": Decimal("0.058"),          # 5.8% - Eastern coast
    "zejtun": Decimal("0.059"),           # 5.9% - South eastern
    "ghaxaq": Decimal("0.060"),           # 6.0% - South
    "gudja": Decimal("0.058"),            # 5.8% - Near airport
    "luqa": Decimal("0.059"),             # 5.9% - Near airport
    
    # Gozo (different market dynamics)
    "victoria": Decimal("0.050"),         # 5.0% - Gozo capital
    "xewkija": Decimal("0.052"),          # 5.2% - Central Gozo
    "nadur": Decimal("0.048"),            # 4.8% - Residential Gozo
    "xlendi": Decimal("0.045"),           # 4.5% - Tourist area
    "marsalforn": Decimal("0.046"),       # 4.6% - Tourist area
    "mgarr": Decimal("0.051"),            # 5.1% - Ferry port area
    "sannat": Decimal("0.049"),           # 4.9% - Residential
    "ghajnsielem": Decimal("0.050"),      # 5.0% - Near ferry
    "xaghra": Decimal("0.047"),           # 4.7% - Residential
}

# =============================================================================
# OPERATING EXPENSES (% of rental income or property value)
# =============================================================================

# Property Management Fees (typically 8-12% of rental income)
PROPERTY_MANAGEMENT = Decimal("0.10")  # 10%

# Maintenance Reserve (annual budget for repairs)
MAINTENANCE_RESERVE = Decimal("0.05")  # 5% of rental income

# Insurance (building insurance, typically 0.2-0.5% of property value annually)
INSURANCE_ANNUAL = Decimal("0.003")  # 0.3% of property value

# Property Tax - Malta has NO annual property tax
PROPERTY_TAX = Decimal("0.00")  # 0%

# Ground Rent (if applicable, for properties on government land)
# This varies widely, typically €50-€500 annually
TYPICAL_GROUND_RENT = Decimal("200")  # €200 average

# =============================================================================
# LOCATION DESIRABILITY SCORES (0-100)
# =============================================================================

# Used for opportunity scoring - higher = more desirable
LOCATION_DESIRABILITY: Dict[str, int] = {
    # Prime areas (highest desirability)
    "sliema": 95,
    "st_julians": 93,
    "valletta": 90,
    "ta_xbiex": 88,
    "swieqi": 85,
    "pembroke": 82,
    "mdina": 85,
    
    # Very desirable central areas
    "gzira": 80,
    "msida": 78,
    "pieta": 76,
    "iklin": 75,
    "balzan": 74,
    "attard": 73,
    "naxxar": 72,
    "lija": 71,
    
    # Good residential areas
    "mosta": 70,
    "birkirkara": 68,
    "santa_venera": 65,
    "qormi": 63,
    "zabbar": 62,
    "fgura": 61,
    
    # Northern coastal/tourism areas
    "mellieha": 75,
    "st_pauls_bay": 70,
    "bugibba": 65,
    "qawra": 64,
    "xemxija": 68,
    "manikata": 72,
    
    # Affordable areas
    "hamrun": 55,
    "paola": 52,
    "marsa": 50,
    
    # Southern coastal
    "marsaskala": 68,
    "birzebbuga": 60,
    "marsaxlokk": 70,
    
    # Three Cities (historic, growing popularity)
    "vittoriosa": 75,
    "senglea": 72,
    "cospicua": 70,
    "kalkara": 68,
    
    # Rural/southern villages
    "zurrieq": 58,
    "safi": 55,
    "mqabba": 54,
    "qrendi": 56,
    "siggiewi": 60,
    "dingli": 62,
    "rabat": 65,
    "zebbug": 57,
    "zejtun": 56,
    "ghaxaq": 54,
    "gudja": 55,
    "luqa": 53,
    "xghajra": 58,
    
    # Gozo
    "victoria": 70,
    "xewkija": 62,
    "nadur": 68,
    "xlendi": 72,
    "marsalforn": 70,
    "mgarr": 65,
    "sannat": 64,
    "ghajnsielem": 66,
    "xaghra": 63,
}

# =============================================================================
# MARKET TRENDS
# =============================================================================

# Historical annual property appreciation (conservative estimate)
HISTORICAL_APPRECIATION = Decimal("0.03")  # 3% annually

# Inflation rate for projections
INFLATION_RATE = Decimal("0.025")  # 2.5%

# =============================================================================
# FINANCING PARAMETERS
# =============================================================================

# Typical mortgage interest rate (varies by lender and LTV)
TYPICAL_INTEREST_RATE = Decimal("0.035")  # 3.5%

# Typical loan term
TYPICAL_LOAN_TERM = 25  # years

# Minimum down payment for non-residents
MIN_DOWN_PAYMENT = Decimal("0.20")  # 20%

# Maximum LTV for residents
MAX_LTV_RESIDENT = Decimal("0.80")  # 80%

# Maximum LTV for non-residents
MAX_LTV_NON_RESIDENT = Decimal("0.80")  # 80%

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_rental_yield_for_area(area: str) -> Decimal:
    """Get the expected annual rental yield for a specific area.
    
    Args:
        area: Name of the area/locality in Malta
        
    Returns:
        Expected annual rental yield as a Decimal (e.g., 0.055 for 5.5%)
        
    Raises:
        ValueError: If the area is not found in the database
    """
    area_normalized = area.lower().strip().replace(" ", "_")
    if area_normalized not in RENTAL_YIELDS:
        raise ValueError(
            f"Unknown area: {area}. "
            f"Available areas: {', '.join(sorted(RENTAL_YIELDS.keys()))}"
        )
    return RENTAL_YIELDS[area_normalized]


def get_location_score(area: str) -> int:
    """Get the desirability score for a specific area.
    
    Args:
        area: Name of the area/locality in Malta
        
    Returns:
        Desirability score from 0-100
        
    Raises:
        ValueError: If the area is not found in the database
    """
    area_normalized = area.lower().strip().replace(" ", "_")
    if area_normalized not in LOCATION_DESIRABILITY:
        raise ValueError(
            f"Unknown area: {area}. "
            f"Available areas: {', '.join(sorted(LOCATION_DESIRABILITY.keys()))}"
        )
    return LOCATION_DESIRABILITY[area_normalized]


def calculate_stamp_duty_first_time(property_price: Decimal) -> Decimal:
    """Calculate stamp duty for first-time buyers.
    
    First €150,000 at 3.5%, remainder at 5%
    
    Args:
        property_price: Total property price
        
    Returns:
        Total stamp duty amount
    """
    if property_price <= STAMP_DUTY_FIRST_TIME_THRESHOLD:
        return property_price * STAMP_DUTY_FIRST_TIME
    else:
        first_portion = STAMP_DUTY_FIRST_TIME_THRESHOLD * STAMP_DUTY_FIRST_TIME
        remainder = (property_price - STAMP_DUTY_FIRST_TIME_THRESHOLD) * STAMP_DUTY_FIRST_TIME_REMAINDER
        return first_portion + remainder


def calculate_stamp_duty_second_time(property_price: Decimal) -> Decimal:
    """Calculate stamp duty for second/subsequent property purchases.
    
    Flat 5% rate
    
    Args:
        property_price: Total property price
        
    Returns:
        Total stamp duty amount
    """
    return property_price * STAMP_DUTY_SECOND_TIME


def calculate_total_purchase_cost_percentage(
    is_first_time: bool = True,
    include_agency_fees: bool = False
) -> Decimal:
    """Calculate total purchase costs as a percentage of property price.
    
    Args:
        is_first_time: Whether this is a first-time purchase
        include_agency_fees: Whether to include buyer's agency fees
        
    Returns:
        Total purchase cost percentage
    """
    # Use average property price of €300k for stamp duty calculation
    avg_price = Decimal("300000")
    
    if is_first_time:
        stamp_duty = calculate_stamp_duty_first_time(avg_price) / avg_price
    else:
        stamp_duty = calculate_stamp_duty_second_time(avg_price) / avg_price
    
    total = stamp_duty + NOTARY_FEES + REGISTRATION_FEES
    
    if include_agency_fees:
        total += AGENCY_FEES_BUYER
    
    return total


def get_all_areas() -> list[str]:
    """Get a list of all available areas in the database.
    
    Returns:
        Sorted list of area names
    """
    return sorted(RENTAL_YIELDS.keys())


def get_high_yield_areas(min_yield: Decimal = Decimal("0.055")) -> Dict[str, Decimal]:
    """Get areas with rental yields above a threshold.
    
    Args:
        min_yield: Minimum yield threshold (default 5.5%)
        
    Returns:
        Dictionary of area names to yields
    """
    return {
        area: yield_val 
        for area, yield_val in RENTAL_YIELDS.items() 
        if yield_val >= min_yield
    }


def get_prime_areas() -> Dict[str, Decimal]:
    """Get prime/desirable areas (score >= 80).
    
    Returns:
        Dictionary of prime area names to yields
    """
    return {
        area: RENTAL_YIELDS[area]
        for area in LOCATION_DESIRABILITY
        if LOCATION_DESIRABILITY[area] >= 80 and area in RENTAL_YIELDS
    }
