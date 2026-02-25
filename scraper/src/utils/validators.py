"""Validation and parsing utilities for property data."""

import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple


def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_phone(phone: str) -> bool:
    """Validate phone number format (Malta/international).

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return False
    # Remove common separators
    cleaned = re.sub(r'[\s\-\.\(\)]', '', phone.strip())
    # Malta numbers: +356 XXXX XXXX or 00356 XXXX XXXX or XXXX XXXX
    # International: +XX... or 00XX...
    pattern = r'^(\+356|00356)?\d{8}$|^(\+|00)\d{10,15}$'
    return bool(re.match(pattern, cleaned))


def clean_phone(phone: str) -> Optional[str]:
    """Clean and format phone number.

    Args:
        phone: Raw phone number string

    Returns:
        Cleaned phone number or None if invalid
    """
    if not phone:
        return None
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone.strip())
    # Ensure Malta numbers have country code
    if len(cleaned) == 8 and not cleaned.startswith('+'):
        cleaned = '+356' + cleaned
    elif cleaned.startswith('00356'):
        cleaned = '+356' + cleaned[5:]
    return cleaned if validate_phone(cleaned) else None


def parse_price(price_str: str) -> Tuple[Optional[Decimal], Optional[str]]:
    """Parse price string to Decimal and currency.

    Args:
        price_str: Price string (e.g., "€450,000", "EUR 450000", "450k")

    Returns:
        Tuple of (price as Decimal, currency code) or (None, None) if parsing fails
    """
    if not price_str:
        return None, None

    price_str = price_str.strip().upper()

    # Detect currency
    currency = "EUR"  # Default for Malta
    if "EUR" in price_str or "€" in price_str:
        currency = "EUR"
    elif "USD" in price_str or "$" in price_str:
        currency = "USD"
    elif "GBP" in price_str or "£" in price_str:
        currency = "GBP"

    # Remove currency symbols and text
    cleaned = re.sub(r'[€$£]|EUR|USD|GBP', '', price_str, flags=re.IGNORECASE)

    # Handle 'k' suffix (thousands)
    multiplier = 1
    if 'K' in cleaned:
        multiplier = 1000
        cleaned = cleaned.replace('K', '')
    elif 'M' in cleaned and not re.search(r'\d\s*M', cleaned):
        # Handle 'M' for millions (but not "sqm")
        multiplier = 1000000
        cleaned = cleaned.replace('M', '')

    # Remove all non-numeric characters except decimal point
    cleaned = re.sub(r'[^\d.]', '', cleaned)

    # Handle multiple decimal points (keep first)
    parts = cleaned.split('.')
    if len(parts) > 2:
        cleaned = parts[0] + '.' + ''.join(parts[1:])

    try:
        if cleaned:
            price = Decimal(cleaned) * multiplier
            return price, currency
    except InvalidOperation:
        pass

    return None, None


def parse_area(area_str: str) -> Optional[float]:
    """Parse area/size string to square meters.

    Args:
        area_str: Area string (e.g., "150 sqm", "1,500 sq ft", "150m2")

    Returns:
        Area in square meters or None if parsing fails
    """
    if not area_str:
        return None

    area_str = area_str.strip().lower()

    # Extract number
    match = re.search(r'([\d,]+\.?\d*)', area_str)
    if not match:
        return None

    try:
        value = float(match.group(1).replace(',', ''))
    except ValueError:
        return None

    # Detect unit and convert to sqm
    if 'sqm' in area_str or 'm2' in area_str or 'm²' in area_str or 'sq m' in area_str:
        return value
    elif 'sqft' in area_str or 'sq ft' in area_str or 'ft2' in area_str or 'ft²' in area_str:
        # Convert sq ft to sqm (1 sq ft = 0.092903 sqm)
        return round(value * 0.092903, 2)
    elif 'sqyd' in area_str or 'sq yd' in area_str or 'yd2' in area_str:
        # Convert sq yards to sqm (1 sq yd = 0.836127 sqm)
        return round(value * 0.836127, 2)

    # Default to sqm if no unit specified
    return value


def clean_text(text: str, preserve_newlines: bool = False) -> str:
    """Clean text by removing extra whitespace and special characters.

    Args:
        text: Raw text string
        preserve_newlines: Whether to preserve newline characters

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    text = text.strip()

    if not preserve_newlines:
        # Replace newlines with spaces
        text = text.replace('\n', ' ').replace('\r', ' ')

    # Remove extra whitespace
    text = ' '.join(text.split())

    # Remove zero-width characters
    text = text.replace('\u200b', '').replace('\ufeff', '')

    return text


def parse_bedrooms(text: str) -> Optional[int]:
    """Extract bedroom count from text.

    Args:
        text: Text containing bedroom info (e.g., "3 bedrooms", "3-bed")

    Returns:
        Number of bedrooms or None
    """
    if not text:
        return None

    text = text.lower()

    # Common patterns
    patterns = [
        r'(\d+)\s*(?:bed|bedroom|br)',
        r'(?:bed|bedroom)s?\s*[:\-]?\s*(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue

    return None


def parse_bathrooms(text: str) -> Optional[int]:
    """Extract bathroom count from text.

    Args:
        text: Text containing bathroom info (e.g., "2 bathrooms", "2 bath")

    Returns:
        Number of bathrooms or None
    """
    if not text:
        return None

    text = text.lower()

    patterns = [
        r'(\d+)\s*(?:bath|bathroom|ba)',
        r'(?:bath|bathroom)s?\s*[:\-]?\s*(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue

    return None


def detect_property_type(text: str) -> Optional[str]:
    """Detect property type from text.

    Args:
        text: Text describing property

    Returns:
        Property type string or None
    """
    if not text:
        return None

    text = text.lower()

    type_patterns = {
        'penthouse': ['penthouse', 'penthse'],
        'apartment': ['apartment', 'apt', 'flat'],
        'maisonette': ['maisonette', 'maisonete'],
        'villa': ['villa', 'detached villa'],
        'townhouse': ['townhouse', 'town house', 'terraced house'],
        'bungalow': ['bungalow', 'bongalo'],
        'duplex': ['duplex', 'duplex apartment'],
        'studio': ['studio', 'studio apartment', 'bedsitter'],
        'house': ['house', 'residence', 'home'],
        'office': ['office', 'commercial office'],
        'shop': ['shop', 'retail', 'store'],
        'warehouse': ['warehouse', 'industrial', 'factory'],
        'land': ['land', 'plot', 'site'],
        'garage': ['garage', 'parking', 'car space'],
    }

    for prop_type, keywords in type_patterns.items():
        for keyword in keywords:
            if keyword in text:
                return prop_type

    return None


def normalize_location(location: str) -> str:
    """Normalize location string.

    Args:
        location: Raw location string

    Returns:
        Normalized location
    """
    if not location:
        return ""

    # Common Malta localities for normalization
    malta_localities = {
        'sliema': 'Sliema',
        'st julians': 'St. Julian\'s',
        'st. julians': 'St. Julian\'s',
        'valletta': 'Valletta',
        'gzira': 'Gzira',
        'msida': 'Msida',
        'ta xbiex': 'Ta\' Xbiex',
        "ta' xbiex": 'Ta\' Xbiex',
        'st pauls bay': 'St. Paul\'s Bay',
        'st. pauls bay': 'St. Paul\'s Bay',
        'bugibba': 'Bugibba',
        'qawra': 'Qawra',
        'mellieha': 'Mellieha',
        'mosta': 'Mosta',
        'naxxar': 'Naxxar',
        'birkirkara': 'Birkirkara',
        'hamrun': 'Hamrun',
        'qormi': 'Qormi',
        'zabbar': 'Zabbar',
        'fgura': 'Fgura',
        'marsaskala': 'Marsaskala',
        'marsaxlokk': 'Marsaxlokk',
        'mdina': 'Mdina',
        'rabat': 'Rabat',
        'gozo': 'Gozo',
        'victoria': 'Victoria',
        'xaghra': 'Xaghra',
        'xewkija': 'Xewkija',
    }

    location_lower = location.lower().strip()

    for key, value in malta_localities.items():
        if key in location_lower:
            return value

    # Title case for unknown locations
    return location.strip().title()


def extract_year_built(text: str) -> Optional[int]:
    """Extract year built from text.

    Args:
        text: Text containing year information

    Returns:
        Year as integer or None
    """
    if not text:
        return None

    text = text.lower()

    # Patterns for year built
    patterns = [
        r'(?:built|construction|year)\s*[:\-]?\s*(\d{4})',
        r'\b(19\d{2}|20\d{2})\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                year = int(match.group(1))
                if 1800 <= year <= 2100:
                    return year
            except ValueError:
                continue

    return None
