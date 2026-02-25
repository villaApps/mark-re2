"""Custom exceptions for the Malta Property Analyzer."""

from typing import Any


class PropertyAnalyzerError(Exception):
    """Base exception for the property analyzer."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        original_error: Exception | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.original_error = original_error

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API response."""
        result: dict[str, Any] = {
            "error_code": self.error_code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


class ValidationError(PropertyAnalyzerError):
    """Raised when input validation fails."""

    status_code = 400
    error_code = "VALIDATION_ERROR"

    def __init__(
        self,
        message: str = "Validation failed",
        field_errors: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.field_errors = field_errors or {}

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        if self.field_errors:
            result["field_errors"] = self.field_errors
        return result


class NotFoundError(PropertyAnalyzerError):
    """Raised when a requested resource is not found."""

    status_code = 404
    error_code = "NOT_FOUND"

    def __init__(self, resource_type: str, resource_id: str, **kwargs: Any):
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id


class DatabaseError(PropertyAnalyzerError):
    """Raised when a database operation fails."""

    status_code = 500
    error_code = "DATABASE_ERROR"

    def __init__(self, message: str = "Database operation failed", **kwargs: Any):
        super().__init__(message, **kwargs)


class ScraperError(PropertyAnalyzerError):
    """Raised when a scraper operation fails."""

    status_code = 502
    error_code = "SCRAPER_ERROR"

    def __init__(
        self,
        message: str = "Scraper operation failed",
        source: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.source = source


class AnalysisError(PropertyAnalyzerError):
    """Raised when an analysis operation fails."""

    status_code = 500
    error_code = "ANALYSIS_ERROR"

    def __init__(self, message: str = "Analysis operation failed", **kwargs: Any):
        super().__init__(message, **kwargs)


class RateLimitError(PropertyAnalyzerError):
    """Raised when rate limit is exceeded."""

    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60, **kwargs: Any):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class AuthenticationError(PropertyAnalyzerError):
    """Raised when authentication fails."""

    status_code = 401
    error_code = "AUTHENTICATION_ERROR"

    def __init__(self, message: str = "Authentication failed", **kwargs: Any):
        super().__init__(message, **kwargs)


class AuthorizationError(PropertyAnalyzerError):
    """Raised when authorization fails."""

    status_code = 403
    error_code = "AUTHORIZATION_ERROR"

    def __init__(self, message: str = "Not authorized to perform this action", **kwargs: Any):
        super().__init__(message, **kwargs)
