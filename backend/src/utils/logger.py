"""Logging utilities using AWS Lambda Powertools."""

import functools
import uuid
from contextvars import ContextVar
from typing import Any, Callable, TypeVar

from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths

# Context variable for request ID
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

# Create the main logger
logger = Logger(service="malta-property-analyzer")

F = TypeVar("F", bound=Callable[..., Any])


def get_logger(component: str | None = None) -> Logger:
    """Get a logger instance with optional component name."""
    if component:
        return Logger(service="malta-property-analyzer", child=True)
    return logger


class LoggerContext:
    """Context manager for logging with request context."""

    def __init__(self, operation: str, **context: Any):
        self.operation = operation
        self.context = context
        self.request_id = str(uuid.uuid4())
        self.token = None

    def __enter__(self) -> "LoggerContext":
        self.token = request_id_var.set(self.request_id)
        logger.append_keys(
            request_id=self.request_id,
            operation=self.operation,
            **self.context,
        )
        logger.info(f"Starting operation: {self.operation}")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_val:
            logger.exception(f"Operation failed: {self.operation}")
        else:
            logger.info(f"Operation completed: {self.operation}")
        
        logger.remove_keys(list(self.context.keys()) + ["request_id", "operation"])
        if self.token:
            request_id_var.reset(self.token)


def log_handler(func: F) -> F:
    """Decorator to log Lambda handler entry/exit with correlation ID."""

    @functools.wraps(func)
    def wrapper(event: dict[str, Any], context: Any) -> Any:
        request_id = context.aws_request_id if hasattr(context, "aws_request_id") else str(uuid.uuid4())
        
        with logger.append_keys(request_id=request_id, handler=func.__name__):
            logger.info(
                "Lambda handler invoked",
                extra={
                    "event_source": event.get("source"),
                    "http_method": event.get("httpMethod"),
                    "path": event.get("path"),
                    "path_parameters": event.get("pathParameters"),
                    "query_parameters": event.get("queryStringParameters"),
                },
            )
            
            try:
                result = func(event, context)
                logger.info("Lambda handler completed successfully")
                return result
            except Exception as e:
                logger.exception("Lambda handler failed")
                raise

    return wrapper  # type: ignore[return-value]


def log_method(func: F) -> F:
    """Decorator to log method calls."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        method_name = func.__name__
        class_name = args[0].__class__.__name__ if args else "Unknown"
        
        logger.debug(
            f"Calling {class_name}.{method_name}",
            extra={
                "class": class_name,
                "method": method_name,
                "args_count": len(args) - 1 if args else 0,
                "kwargs_keys": list(kwargs.keys()),
            },
        )
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{class_name}.{method_name} completed successfully")
            return result
        except Exception as e:
            logger.exception(f"{class_name}.{method_name} failed")
            raise

    return wrapper  # type: ignore[return-value]


def get_correlation_id() -> str | None:
    """Get the current correlation ID."""
    return request_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID."""
    request_id_var.set(correlation_id)
    logger.append_keys(correlation_id=correlation_id)
