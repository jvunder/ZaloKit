"""Tests for ZaloKit exceptions module."""

import pytest

from zalokit.exceptions import (
    ZaloKitError,
    AuthenticationError,
    TokenExpiredError,
    InvalidTokenError,
    APIError,
    RateLimitError,
    ValidationError,
    NetworkError,
    TimeoutError,
    WebSocketError,
    MessageError,
    GroupError,
    ContactError,
)


class TestZaloKitError:
    """Tests for base ZaloKitError exception."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = ZaloKitError("Something went wrong")

        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.error_code is None
        assert error.details == {}

    def test_error_with_code(self):
        """Test error with error code."""
        error = ZaloKitError("Failed", error_code="ERR_001")

        assert str(error) == "[ERR_001] Failed"
        assert error.error_code == "ERR_001"

    def test_error_with_details(self):
        """Test error with details."""
        details = {"field": "email", "reason": "invalid"}
        error = ZaloKitError("Validation failed", details=details)

        assert error.details == details

    def test_error_to_dict(self):
        """Test error serialization."""
        error = ZaloKitError(
            "Test error",
            error_code="TEST_ERR",
            details={"key": "value"},
        )

        data = error.to_dict()

        assert data["error"] == "ZaloKitError"
        assert data["message"] == "Test error"
        assert data["error_code"] == "TEST_ERR"
        assert data["details"] == {"key": "value"}


class TestAuthenticationError:
    """Tests for AuthenticationError exception."""

    def test_default_message(self):
        """Test default error message."""
        error = AuthenticationError()

        assert "Authentication failed" in str(error)
        assert error.error_code == "AUTH_ERROR"

    def test_custom_message(self):
        """Test custom error message."""
        error = AuthenticationError("Invalid credentials")

        assert str(error) == "[AUTH_ERROR] Invalid credentials"


class TestTokenExpiredError:
    """Tests for TokenExpiredError exception."""

    def test_default_message(self):
        """Test default error message."""
        error = TokenExpiredError()

        assert "expired" in str(error).lower()
        assert error.error_code == "TOKEN_EXPIRED"

    def test_inheritance(self):
        """Test that TokenExpiredError inherits from AuthenticationError."""
        error = TokenExpiredError()

        assert isinstance(error, AuthenticationError)
        assert isinstance(error, ZaloKitError)


class TestInvalidTokenError:
    """Tests for InvalidTokenError exception."""

    def test_default_message(self):
        """Test default error message."""
        error = InvalidTokenError()

        assert "invalid" in str(error).lower()
        assert error.error_code == "INVALID_TOKEN"


class TestAPIError:
    """Tests for APIError exception."""

    def test_basic_api_error(self):
        """Test basic API error."""
        error = APIError("Request failed")

        assert "Request failed" in str(error)
        assert error.status_code is None

    def test_api_error_with_status_code(self):
        """Test API error with HTTP status code."""
        error = APIError("Not found", status_code=404)

        assert "404" in str(error)
        assert error.status_code == 404

    def test_api_error_with_all_fields(self):
        """Test API error with all fields."""
        error = APIError(
            "Server error",
            status_code=500,
            error_code="INTERNAL_ERROR",
            details={"trace_id": "abc123"},
        )

        assert error.status_code == 500
        assert error.error_code == "INTERNAL_ERROR"
        assert error.details["trace_id"] == "abc123"


class TestRateLimitError:
    """Tests for RateLimitError exception."""

    def test_default_message(self):
        """Test default error message."""
        error = RateLimitError()

        assert "rate limit" in str(error).lower()
        assert error.status_code == 429

    def test_with_retry_after(self):
        """Test error with retry_after."""
        error = RateLimitError(retry_after=60)

        assert error.retry_after == 60
        assert error.details["retry_after"] == 60

    def test_inheritance(self):
        """Test inheritance from APIError."""
        error = RateLimitError()

        assert isinstance(error, APIError)


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_basic_validation_error(self):
        """Test basic validation error."""
        error = ValidationError("Invalid input")

        assert "Invalid input" in str(error)
        assert error.error_code == "VALIDATION_ERROR"

    def test_validation_error_with_field(self):
        """Test validation error with field name."""
        error = ValidationError("Required field missing", field="email")

        assert error.field == "email"
        assert error.details["field"] == "email"


class TestNetworkError:
    """Tests for NetworkError exception."""

    def test_default_message(self):
        """Test default error message."""
        error = NetworkError()

        assert "network" in str(error).lower()
        assert error.error_code == "NETWORK_ERROR"

    def test_custom_message(self):
        """Test custom error message."""
        error = NetworkError("Connection refused")

        assert "Connection refused" in str(error)


class TestTimeoutError:
    """Tests for TimeoutError exception."""

    def test_default_message(self):
        """Test default error message."""
        error = TimeoutError()

        assert "timeout" in str(error).lower()
        assert error.error_code == "TIMEOUT"

    def test_with_timeout_value(self):
        """Test error with timeout value."""
        error = TimeoutError(timeout=30.0)

        assert error.timeout == 30.0
        assert error.details["timeout"] == 30.0

    def test_inheritance(self):
        """Test inheritance from NetworkError."""
        error = TimeoutError()

        assert isinstance(error, NetworkError)


class TestWebSocketError:
    """Tests for WebSocketError exception."""

    def test_default_message(self):
        """Test default error message."""
        error = WebSocketError()

        assert "websocket" in str(error).lower()
        assert error.error_code == "WEBSOCKET_ERROR"


class TestMessageError:
    """Tests for MessageError exception."""

    def test_basic_message_error(self):
        """Test basic message error."""
        error = MessageError("Failed to send")

        assert "Failed to send" in str(error)
        assert error.error_code == "MESSAGE_ERROR"

    def test_message_error_with_recipient(self):
        """Test message error with recipient ID."""
        error = MessageError("Delivery failed", recipient_id="user_123")

        assert error.recipient_id == "user_123"
        assert error.details["recipient_id"] == "user_123"


class TestGroupError:
    """Tests for GroupError exception."""

    def test_basic_group_error(self):
        """Test basic group error."""
        error = GroupError("Group not found")

        assert "Group not found" in str(error)
        assert error.error_code == "GROUP_ERROR"

    def test_group_error_with_id(self):
        """Test group error with group ID."""
        error = GroupError("Permission denied", group_id="group_456")

        assert error.group_id == "group_456"
        assert error.details["group_id"] == "group_456"


class TestContactError:
    """Tests for ContactError exception."""

    def test_basic_contact_error(self):
        """Test basic contact error."""
        error = ContactError("Contact not found")

        assert "Contact not found" in str(error)
        assert error.error_code == "CONTACT_ERROR"

    def test_contact_error_with_id(self):
        """Test contact error with contact ID."""
        error = ContactError("Cannot retrieve", contact_id="contact_789")

        assert error.contact_id == "contact_789"
        assert error.details["contact_id"] == "contact_789"


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_all_inherit_from_base(self):
        """Test all exceptions inherit from ZaloKitError."""
        exceptions = [
            AuthenticationError(),
            TokenExpiredError(),
            InvalidTokenError(),
            APIError("test"),
            RateLimitError(),
            ValidationError("test"),
            NetworkError(),
            TimeoutError(),
            WebSocketError(),
            MessageError("test"),
            GroupError("test"),
            ContactError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, ZaloKitError)

    def test_can_catch_by_base_class(self):
        """Test catching exceptions by base class."""
        try:
            raise TokenExpiredError()
        except ZaloKitError as e:
            assert "expired" in str(e).lower()

    def test_can_catch_specific_exception(self):
        """Test catching specific exceptions."""
        try:
            raise RateLimitError(retry_after=30)
        except RateLimitError as e:
            assert e.retry_after == 30
