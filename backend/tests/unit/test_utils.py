"""Unit tests for utility modules."""

import pytest
from decimal import Decimal

from src.utils.errors import (
    PropertyAnalyzerError,
    ValidationError,
    NotFoundError,
    DatabaseError,
    ScraperError,
)
from src.utils.id_generator import (
    generate_id,
    generate_property_id,
    generate_analysis_id,
    generate_scraper_run_id,
    generate_correlation_id,
)
from src.utils.response import (
    create_response,
    create_error_response,
    create_paginated_response,
    DecimalEncoder,
)


@pytest.mark.unit
class TestErrors:
    """Tests for error classes."""

    def test_property_analyzer_error(self):
        """Test PropertyAnalyzerError."""
        error = PropertyAnalyzerError("Test error", details={"key": "value"})
        
        assert error.message == "Test error"
        assert error.details == {"key": "value"}
        assert error.status_code == 500
        assert error.error_code == "INTERNAL_ERROR"

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError(
            "Validation failed",
            field_errors={"price": "Must be positive"},
        )
        
        assert error.message == "Validation failed"
        assert error.field_errors == {"price": "Must be positive"}
        assert error.status_code == 400
        assert error.error_code == "VALIDATION_ERROR"

    def test_not_found_error(self):
        """Test NotFoundError."""
        error = NotFoundError("Property", "123")
        
        assert "Property" in error.message
        assert "123" in error.message
        assert error.resource_type == "Property"
        assert error.resource_id == "123"
        assert error.status_code == 404

    def test_database_error(self):
        """Test DatabaseError."""
        error = DatabaseError("Connection failed")
        
        assert error.message == "Connection failed"
        assert error.status_code == 500

    def test_scraper_error(self):
        """Test ScraperError."""
        error = ScraperError("Scrape failed", source="test_source")
        
        assert error.message == "Scrape failed"
        assert error.source == "test_source"
        assert error.status_code == 502

    def test_error_to_dict(self):
        """Test error serialization to dict."""
        error = PropertyAnalyzerError("Test", details={"foo": "bar"})
        error_dict = error.to_dict()
        
        assert error_dict["error_code"] == "INTERNAL_ERROR"
        assert error_dict["message"] == "Test"
        assert error_dict["details"] == {"foo": "bar"}


@pytest.mark.unit
class TestIdGenerator:
    """Tests for ID generator functions."""

    def test_generate_id(self):
        """Test generate_id."""
        id1 = generate_id()
        id2 = generate_id()
        
        assert len(id1) == 16
        assert len(id2) == 16
        assert id1 != id2  # Should be unique

    def test_generate_id_with_prefix(self):
        """Test generate_id with prefix."""
        id_val = generate_id("test")
        
        assert id_val.startswith("test_")
        assert len(id_val) > 16

    def test_generate_property_id_with_external(self):
        """Test generate_property_id with external ID."""
        id1 = generate_property_id("ext123", "source1")
        id2 = generate_property_id("ext123", "source1")
        
        # Should be deterministic
        assert id1 == id2
        assert id1.startswith("prop_")

    def test_generate_property_id_random(self):
        """Test generate_property_id without external ID."""
        id1 = generate_property_id()
        id2 = generate_property_id()
        
        assert id1.startswith("prop_")
        assert id1 != id2

    def test_generate_analysis_id(self):
        """Test generate_analysis_id."""
        analysis_id = generate_analysis_id("prop123")
        
        assert analysis_id.startswith("anl_")
        assert "prop123"[:8] in analysis_id

    def test_generate_scraper_run_id(self):
        """Test generate_scraper_run_id."""
        run_id = generate_scraper_run_id()
        
        assert run_id.startswith("scrap_")
        assert len(run_id) > 20

    def test_generate_correlation_id(self):
        """Test generate_correlation_id."""
        corr_id = generate_correlation_id()
        
        assert corr_id.startswith("corr_")
        assert len(corr_id) > 16


@pytest.mark.unit
class TestResponse:
    """Tests for response utilities."""

    def test_create_response_success(self):
        """Test creating a successful response."""
        response = create_response(200, data={"id": "123"}, message="Success")
        
        assert response["statusCode"] == 200
        assert "body" in response
        assert "headers" in response
        assert response["headers"]["Content-Type"] == "application/json"

    def test_create_response_with_decimal(self):
        """Test response with Decimal values."""
        response = create_response(200, data={"price": Decimal("450000")})
        
        import json
        body = json.loads(response["body"])
        assert body["data"]["price"] == 450000.0

    def test_create_error_response(self):
        """Test creating an error response."""
        error = ValidationError("Invalid input")
        response = create_error_response(error)
        
        assert response["statusCode"] == 400
        import json
        body = json.loads(response["body"])
        assert body["success"] is False
        assert "error_code" in body

    def test_create_error_response_generic(self):
        """Test creating error response from generic exception."""
        response = create_error_response(ValueError("Something went wrong"))
        
        assert response["statusCode"] == 500
        import json
        body = json.loads(response["body"])
        assert body["success"] is False

    def test_create_paginated_response(self):
        """Test creating a paginated response."""
        items = [{"id": i} for i in range(5)]
        response = create_paginated_response(items, total=20, page=1, page_size=5)
        
        assert response["statusCode"] == 200
        import json
        body = json.loads(response["body"])
        assert body["data"]["items"] == items
        assert body["data"]["total"] == 20
        assert body["data"]["total_pages"] == 4


@pytest.mark.unit
class TestDecimalEncoder:
    """Tests for DecimalEncoder."""

    def test_encode_decimal(self):
        """Test encoding Decimal values."""
        import json
        
        data = {"price": Decimal("450000.50")}
        encoded = json.dumps(data, cls=DecimalEncoder)
        
        assert "450000.5" in encoded

    def test_encode_set(self):
        """Test encoding set values."""
        import json
        
        data = {"tags": {"a", "b", "c"}}
        encoded = json.dumps(data, cls=DecimalEncoder)
        
        decoded = json.loads(encoded)
        assert set(decoded["tags"]) == {"a", "b", "c"}

    def test_encode_pydantic_model(self):
        """Test encoding Pydantic models."""
        from pydantic import BaseModel
        import json
        
        class TestModel(BaseModel):
            name: str
            value: int
        
        model = TestModel(name="test", value=42)
        encoded = json.dumps({"model": model}, cls=DecimalEncoder)
        
        decoded = json.loads(encoded)
        assert decoded["model"]["name"] == "test"
        assert decoded["model"]["value"] == 42
