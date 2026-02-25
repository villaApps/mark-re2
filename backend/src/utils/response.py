"""API response utilities."""

import json
from decimal import Decimal
from typing import Any

from pydantic import BaseModel

from src.utils.errors import PropertyAnalyzerError


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


def create_response(
    status_code: int,
    data: Any = None,
    message: str | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Create a standardized API Gateway response."""
    response_body: dict[str, Any] = {
        "success": 200 <= status_code < 300,
    }
    
    if data is not None:
        response_body["data"] = data
    if message is not None:
        response_body["message"] = message
    
    response_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    }
    
    if headers:
        response_headers.update(headers)
    
    return {
        "statusCode": status_code,
        "headers": response_headers,
        "body": json.dumps(response_body, cls=DecimalEncoder),
    }


def create_error_response(
    error: PropertyAnalyzerError | Exception,
    status_code: int | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    """Create an error response."""
    if isinstance(error, PropertyAnalyzerError):
        code = error.status_code
        body: dict[str, Any] = {
            "success": False,
            "error_code": error.error_code,
            "message": error.message,
        }
        body.update(error.to_dict())
    else:
        code = status_code or 500
        body = {
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": str(error) or "An unexpected error occurred",
        }
    
    if request_id:
        body["request_id"] = request_id
    
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, cls=DecimalEncoder),
    }


def create_paginated_response(
    items: list[Any],
    total: int,
    page: int,
    page_size: int,
    status_code: int = 200,
) -> dict[str, Any]:
    """Create a paginated response."""
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    data = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }
    
    return create_response(status_code, data=data)
