"""
ZaloKit Exceptions Module.

This module defines all custom exceptions used throughout the ZaloKit SDK.
"""

from typing import Optional, Dict, Any


class ZaloKitError(Exception):
    """Base exception for all ZaloKit errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary representation."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class AuthenticationError(ZaloKitError):
    """Raised when authentication fails or credentials are invalid."""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: Optional[str] = "AUTH_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)


class TokenExpiredError(AuthenticationError):
    """Raised when the access token has expired."""

    def __init__(
        self,
        message: str = "Access token has expired",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "TOKEN_EXPIRED", details)


class InvalidTokenError(AuthenticationError):
    """Raised when the access token is invalid."""

    def __init__(
        self,
        message: str = "Invalid access token",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "INVALID_TOKEN", details)


class APIError(ZaloKitError):
    """Raised when an API request fails."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = "API_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        super().__init__(message, error_code, details)

    def __str__(self) -> str:
        base = super().__str__()
        if self.status_code:
            return f"{base} (HTTP {self.status_code})"
        return base


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.retry_after = retry_after
        details = details or {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, 429, "RATE_LIMIT", details)


class ValidationError(ZaloKitError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.field = field
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", details)


class NetworkError(ZaloKitError):
    """Raised when a network-related error occurs."""

    def __init__(
        self,
        message: str = "Network error occurred",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "NETWORK_ERROR", details)


class TimeoutError(NetworkError):
    """Raised when a request times out."""

    def __init__(
        self,
        message: str = "Request timed out",
        timeout: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.timeout = timeout
        details = details or {}
        if timeout:
            details["timeout"] = timeout
        super().__init__(message, details)
        self.error_code = "TIMEOUT"


class WebSocketError(ZaloKitError):
    """Raised when a WebSocket-related error occurs."""

    def __init__(
        self,
        message: str = "WebSocket error occurred",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "WEBSOCKET_ERROR", details)


class MessageError(ZaloKitError):
    """Raised when message sending or receiving fails."""

    def __init__(
        self,
        message: str,
        recipient_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.recipient_id = recipient_id
        details = details or {}
        if recipient_id:
            details["recipient_id"] = recipient_id
        super().__init__(message, "MESSAGE_ERROR", details)


class GroupError(ZaloKitError):
    """Raised when group operations fail."""

    def __init__(
        self,
        message: str,
        group_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.group_id = group_id
        details = details or {}
        if group_id:
            details["group_id"] = group_id
        super().__init__(message, "GROUP_ERROR", details)


class ContactError(ZaloKitError):
    """Raised when contact operations fail."""

    def __init__(
        self,
        message: str,
        contact_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.contact_id = contact_id
        details = details or {}
        if contact_id:
            details["contact_id"] = contact_id
        super().__init__(message, "CONTACT_ERROR", details)
