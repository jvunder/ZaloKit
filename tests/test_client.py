"""Tests for ZaloKit client module."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from zalokit import ZaloClient
from zalokit.auth import ZaloAuth, TokenInfo
from zalokit.messaging import MessagingAPI, MessageResponse
from zalokit.contacts import ContactsAPI
from zalokit.groups import GroupsAPI
from zalokit.exceptions import AuthenticationError, ValidationError


class TestZaloClient:
    """Tests for ZaloClient class."""

    def test_client_initialization(self):
        """Test ZaloClient initialization."""
        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
        )

        assert client._auth is not None
        assert client._messaging is not None
        assert client._contacts is not None
        assert client._groups is not None
        assert client.is_authenticated is False

    def test_client_initialization_with_token(self):
        """Test ZaloClient initialization with access token."""
        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_token",
        )

        assert client.is_authenticated is True

    def test_client_set_access_token(self):
        """Test setting access token."""
        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
        )

        client.set_access_token("new_token", "new_refresh")

        assert client.is_authenticated is True

    def test_client_auth_property(self):
        """Test auth property returns ZaloAuth instance."""
        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
        )

        assert isinstance(client.auth, ZaloAuth)

    def test_client_messaging_property(self):
        """Test messaging property returns MessagingAPI instance."""
        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
        )

        assert isinstance(client.messaging, MessagingAPI)

    def test_client_contacts_property(self):
        """Test contacts property returns ContactsAPI instance."""
        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
        )

        assert isinstance(client.contacts, ContactsAPI)

    def test_client_groups_property(self):
        """Test groups property returns GroupsAPI instance."""
        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
        )

        assert isinstance(client.groups, GroupsAPI)

    def test_client_get_authorization_url(self):
        """Test getting authorization URL."""
        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            redirect_uri="https://example.com/callback",
        )

        url = client.get_authorization_url(state="test_state")

        assert "oauth.zaloapp.com" in url
        assert "test_app_id" in url
        assert "test_state" in url

    def test_client_context_manager(self):
        """Test ZaloClient as context manager."""
        with ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
        ) as client:
            assert client is not None

    def test_client_repr_not_authenticated(self):
        """Test string representation when not authenticated."""
        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
        )

        repr_str = repr(client)

        assert "ZaloClient" in repr_str
        assert "not authenticated" in repr_str

    def test_client_repr_authenticated(self):
        """Test string representation when authenticated."""
        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_token",
        )

        repr_str = repr(client)

        assert "ZaloClient" in repr_str
        assert "authenticated" in repr_str


class TestZaloClientMessaging:
    """Tests for ZaloClient messaging methods."""

    @patch.object(MessagingAPI, "send_text_message")
    def test_send_message(self, mock_send):
        """Test sending a text message."""
        mock_send.return_value = MessageResponse(
            success=True,
            message_id="msg_123",
        )

        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_token",
        )

        response = client.send_message("user_123", "Hello!")

        assert response.success is True
        assert response.message_id == "msg_123"
        mock_send.assert_called_once_with("user_123", "Hello!", None)

    @patch.object(MessagingAPI, "send_image")
    def test_send_image(self, mock_send):
        """Test sending an image."""
        mock_send.return_value = MessageResponse(success=True, message_id="img_123")

        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_token",
        )

        response = client.send_image("user_123", image_path="/path/to/image.jpg")

        assert response.success is True
        mock_send.assert_called_once()

    @patch.object(MessagingAPI, "send_file")
    def test_send_file(self, mock_send):
        """Test sending a file."""
        mock_send.return_value = MessageResponse(success=True, message_id="file_123")

        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_token",
        )

        response = client.send_file("user_123", "/path/to/doc.pdf")

        assert response.success is True
        mock_send.assert_called_once_with("user_123", "/path/to/doc.pdf")

    @patch.object(MessagingAPI, "broadcast_text")
    def test_broadcast_message(self, mock_broadcast):
        """Test broadcasting message to multiple users."""
        mock_broadcast.return_value = [
            MessageResponse(success=True, message_id="msg_1"),
            MessageResponse(success=True, message_id="msg_2"),
        ]

        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_token",
        )

        responses = client.broadcast_message(["user_1", "user_2"], "Hello all!")

        assert len(responses) == 2
        assert all(r.success for r in responses)


class TestZaloClientContacts:
    """Tests for ZaloClient contacts methods."""

    @patch.object(ContactsAPI, "get_profile")
    def test_get_user_profile(self, mock_get_profile):
        """Test getting user profile."""
        from zalokit.contacts import UserProfile, Gender

        mock_get_profile.return_value = UserProfile(
            user_id="user_123",
            display_name="Test User",
            gender=Gender.MALE,
        )

        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_token",
        )

        profile = client.get_user_profile("user_123")

        assert profile.user_id == "user_123"
        assert profile.display_name == "Test User"
        mock_get_profile.assert_called_once_with("user_123")

    @patch.object(ContactsAPI, "get_followers")
    def test_get_followers(self, mock_get_followers):
        """Test getting followers."""
        mock_get_followers.return_value = {
            "followers": [],
            "total": 0,
            "offset": 0,
            "count": 0,
        }

        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_token",
        )

        result = client.get_followers(offset=0, count=10)

        assert "followers" in result
        mock_get_followers.assert_called_once_with(0, 10, None)

    @patch.object(ContactsAPI, "assign_tag")
    def test_tag_user(self, mock_tag):
        """Test tagging a user."""
        mock_tag.return_value = True

        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_token",
        )

        result = client.tag_user("user_123", "VIP")

        assert result is True
        mock_tag.assert_called_once_with("user_123", "VIP")


class TestZaloClientGroups:
    """Tests for ZaloClient groups methods."""

    @patch.object(GroupsAPI, "create_group")
    def test_create_group(self, mock_create):
        """Test creating a group."""
        from zalokit.groups import Group

        mock_create.return_value = Group(
            group_id="group_123",
            name="Test Group",
        )

        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_token",
        )

        group = client.create_group("Test Group", ["user_1", "user_2"])

        assert group.group_id == "group_123"
        assert group.name == "Test Group"
        mock_create.assert_called_once()

    @patch.object(GroupsAPI, "send_message")
    def test_send_group_message(self, mock_send):
        """Test sending group message."""
        mock_send.return_value = {"message_id": "gmsg_123"}

        client = ZaloClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_token",
        )

        result = client.send_group_message("group_123", "Hello group!")

        assert "message_id" in result
        mock_send.assert_called_once_with("group_123", "Hello group!")
