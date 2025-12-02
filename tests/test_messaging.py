"""Tests for ZaloKit messaging module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
from pathlib import Path

from zalokit.messaging import (
    MessagingAPI,
    Message,
    MessageResponse,
    MessageType,
    AttachmentType,
)
from zalokit.exceptions import ValidationError, MessageError, RateLimitError, APIError


class TestMessageTypes:
    """Tests for message type enums."""

    def test_message_type_values(self):
        """Test MessageType enum values."""
        assert MessageType.TEXT.value == "text"
        assert MessageType.IMAGE.value == "image"
        assert MessageType.FILE.value == "file"
        assert MessageType.STICKER.value == "sticker"

    def test_attachment_type_values(self):
        """Test AttachmentType enum values."""
        assert AttachmentType.IMAGE.value == "image"
        assert AttachmentType.FILE.value == "file"
        assert AttachmentType.VIDEO.value == "video"


class TestMessage:
    """Tests for Message dataclass."""

    def test_message_creation(self):
        """Test Message creation."""
        message = Message(
            message_id="msg_123",
            sender_id="sender_001",
            recipient_id="recipient_002",
            message_type=MessageType.TEXT,
            content="Hello!",
        )

        assert message.message_id == "msg_123"
        assert message.sender_id == "sender_001"
        assert message.recipient_id == "recipient_002"
        assert message.message_type == MessageType.TEXT
        assert message.content == "Hello!"
        assert message.attachments == []
        assert message.metadata == {}

    def test_message_to_dict(self):
        """Test Message serialization."""
        message = Message(
            message_id="msg_123",
            sender_id="sender_001",
            recipient_id="recipient_002",
            message_type=MessageType.TEXT,
            content="Hello!",
            timestamp=1000000,
        )

        data = message.to_dict()

        assert data["message_id"] == "msg_123"
        assert data["message_type"] == "text"
        assert data["timestamp"] == 1000000


class TestMessageResponse:
    """Tests for MessageResponse dataclass."""

    def test_success_response(self):
        """Test successful message response."""
        response = MessageResponse(
            success=True,
            message_id="msg_123",
        )

        assert response.success is True
        assert response.message_id == "msg_123"
        assert response.error is None

    def test_error_response(self):
        """Test error message response."""
        response = MessageResponse(
            success=False,
            error="Message delivery failed",
            error_code="DELIVERY_FAILED",
        )

        assert response.success is False
        assert response.error == "Message delivery failed"
        assert response.error_code == "DELIVERY_FAILED"

    def test_from_api_response_success(self):
        """Test creating response from successful API response."""
        api_response = {
            "error": 0,
            "data": {"message_id": "msg_456"},
        }

        response = MessageResponse.from_api_response(api_response)

        assert response.success is True
        assert response.message_id == "msg_456"

    def test_from_api_response_error(self):
        """Test creating response from error API response."""
        api_response = {
            "error": -201,
            "message": "Invalid token",
        }

        response = MessageResponse.from_api_response(api_response)

        assert response.success is False
        assert response.error == "Invalid token"
        assert response.error_code == "-201"


class TestMessagingAPI:
    """Tests for MessagingAPI class."""

    @pytest.fixture
    def mock_auth(self):
        """Create mock auth."""
        auth = Mock()
        auth.get_auth_header.return_value = {"Authorization": "Bearer test_token"}
        return auth

    @pytest.fixture
    def messaging_api(self, mock_auth):
        """Create MessagingAPI instance."""
        return MessagingAPI(mock_auth, timeout=30)

    def test_send_text_message_validation_no_recipient(self, messaging_api):
        """Test validation error for missing recipient."""
        with pytest.raises(ValidationError) as exc_info:
            messaging_api.send_text_message("", "Hello!")

        assert "recipient_id" in str(exc_info.value)

    def test_send_text_message_validation_no_text(self, messaging_api):
        """Test validation error for missing text."""
        with pytest.raises(ValidationError) as exc_info:
            messaging_api.send_text_message("user_123", "")

        assert "text" in str(exc_info.value)

    @patch("zalokit.messaging.requests.Session")
    def test_send_text_message_success(self, mock_session_class, mock_auth):
        """Test successful text message sending."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "error": 0,
            "data": {"message_id": "msg_success"},
        }
        mock_session.post.return_value = mock_response

        api = MessagingAPI(mock_auth, timeout=30)
        response = api.send_text_message("user_123", "Hello!")

        assert response.success is True
        assert response.message_id == "msg_success"

    @patch("zalokit.messaging.requests.Session")
    def test_send_text_message_rate_limit(self, mock_session_class, mock_auth):
        """Test rate limit handling."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {"error": -1, "message": "Rate limit"}
        mock_session.post.return_value = mock_response

        api = MessagingAPI(mock_auth, timeout=30)

        with pytest.raises(RateLimitError) as exc_info:
            api.send_text_message("user_123", "Hello!")

        assert exc_info.value.retry_after == 60

    def test_send_image_validation_no_source(self, messaging_api):
        """Test validation error when no image source provided."""
        with pytest.raises(ValidationError):
            messaging_api.send_image("user_123")

    def test_send_file_validation_no_path(self, messaging_api):
        """Test validation error for missing file path."""
        with pytest.raises(ValidationError) as exc_info:
            messaging_api.send_file("user_123", "")

        assert "file_path" in str(exc_info.value)

    def test_send_file_validation_file_not_found(self, messaging_api):
        """Test validation error for non-existent file."""
        with pytest.raises(ValidationError) as exc_info:
            messaging_api.send_file("user_123", "/nonexistent/file.pdf")

        assert "not found" in str(exc_info.value).lower()

    def test_send_sticker_validation_no_recipient(self, messaging_api):
        """Test validation error for missing recipient in sticker."""
        with pytest.raises(ValidationError) as exc_info:
            messaging_api.send_sticker("", "sticker_123")

        assert "recipient_id" in str(exc_info.value)

    def test_send_sticker_validation_no_sticker_id(self, messaging_api):
        """Test validation error for missing sticker ID."""
        with pytest.raises(ValidationError) as exc_info:
            messaging_api.send_sticker("user_123", "")

        assert "sticker_id" in str(exc_info.value)

    def test_send_link_validation_no_url(self, messaging_api):
        """Test validation error for missing URL in link."""
        with pytest.raises(ValidationError) as exc_info:
            messaging_api.send_link("user_123", "")

        assert "url" in str(exc_info.value)

    def test_send_template_validation_no_template(self, messaging_api):
        """Test validation error for missing template."""
        with pytest.raises(ValidationError) as exc_info:
            messaging_api.send_template("user_123", {})

        assert "template" in str(exc_info.value)

    @patch("zalokit.messaging.requests.Session")
    def test_broadcast_text_multiple_recipients(self, mock_session_class, mock_auth):
        """Test broadcasting to multiple recipients."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "error": 0,
            "data": {"message_id": "msg_broadcast"},
        }
        mock_session.post.return_value = mock_response

        api = MessagingAPI(mock_auth, timeout=30)
        results = api.broadcast_text(["user_1", "user_2", "user_3"], "Hello all!")

        assert len(results) == 3
        assert all(r.success for r in results)

    @patch("zalokit.messaging.requests.Session")
    def test_broadcast_text_partial_failure(self, mock_session_class, mock_auth):
        """Test broadcasting with some failures."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # First call succeeds, second fails
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "error": 0,
            "data": {"message_id": "msg_1"},
        }

        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 400
        mock_response_fail.json.return_value = {
            "error": -1,
            "message": "User not found",
        }

        mock_session.post.side_effect = [mock_response_success, mock_response_fail]

        api = MessagingAPI(mock_auth, timeout=30)
        results = api.broadcast_text(["user_1", "user_2"], "Hello!")

        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False
