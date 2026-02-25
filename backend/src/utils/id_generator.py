"""ID generation utilities."""

import uuid
from datetime import datetime


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique_id = uuid.uuid4().hex[:16]
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id


def generate_property_id(external_id: str | None = None, source: str | None = None) -> str:
    """Generate a property ID.
    
    If external_id and source are provided, creates a deterministic ID.
    Otherwise, generates a random UUID-based ID.
    """
    if external_id and source:
        # Create deterministic ID from external_id and source
        import hashlib
        combined = f"{source}:{external_id}"
        hash_value = hashlib.sha256(combined.encode()).hexdigest()[:16]
        return f"prop_{hash_value}"
    return generate_id("prop")


def generate_analysis_id(property_id: str) -> str:
    """Generate an analysis ID based on property ID and timestamp."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_suffix = uuid.uuid4().hex[:8]
    return f"anl_{property_id[:8]}_{timestamp}_{unique_suffix}"


def generate_scraper_run_id() -> str:
    """Generate a scraper run ID."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_suffix = uuid.uuid4().hex[:8]
    return f"scrap_{timestamp}_{unique_suffix}"


def generate_correlation_id() -> str:
    """Generate a correlation ID for request tracing."""
    return f"corr_{uuid.uuid4().hex[:16]}"
