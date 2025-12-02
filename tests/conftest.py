"""Pytest configuration and fixtures for ZaloKit tests."""

import pytest
from unittest.mock import Mock, MagicMock

from zalokit import ZaloClient, ZaloAuth
from zalokit.auth import TokenInfo


@pytest.fixture
def mock_token_info():
    """Create a mock TokenInfo object."""
    return TokenInfo(
        access_token="test_access_token_12345",
        refresh_token="test_refresh_token_67890",
        expires_in=3600,
    )


@pytest.fixture
def mock_auth(mock_token_info):
    """Create a mock ZaloAuth instance."""
    auth = Mock(spec=ZaloAuth)
    auth.app_id = "test_app_id"
    auth.app_secret = "test_app_secret"
    auth.is_authenticated = True
    auth._token = mock_token_info
    auth.get_access_token.return_value = mock_token_info.access_token
    auth.get_auth_header.return_value = {
        "Authorization": f"Bearer {mock_token_info.access_token}"
    }
    return auth


@pytest.fixture
def mock_client(mock_auth):
    """Create a mock ZaloClient instance."""
    client = Mock(spec=ZaloClient)
    client._auth = mock_auth
    client.is_authenticated = True
    return client


@pytest.fixture
def zalo_auth():
    """Create a real ZaloAuth instance for testing."""
    return ZaloAuth(
        app_id="test_app_id",
        app_secret="test_app_secret",
        redirect_uri="https://example.com/callback",
    )


@pytest.fixture
def zalo_client():
    """Create a real ZaloClient instance for testing."""
    return ZaloClient(
        app_id="test_app_id",
        app_secret="test_app_secret",
    )


@pytest.fixture
def sample_user_profile():
    """Sample user profile data from API."""
    return {
        "user_id": "1234567890",
        "display_name": "Test User",
        "avatar": "https://example.com/avatar.jpg",
        "avatars": {
            "120": "https://example.com/avatar_120.jpg",
            "240": "https://example.com/avatar_240.jpg",
        },
        "user_gender": 1,
        "birthday": "01/01/1990",
        "is_follower": True,
        "is_following": False,
    }


@pytest.fixture
def sample_message_response():
    """Sample message response from API."""
    return {
        "error": 0,
        "message": "Success",
        "data": {
            "message_id": "msg_123456789",
        },
    }


@pytest.fixture
def sample_error_response():
    """Sample error response from API."""
    return {
        "error": -201,
        "message": "Invalid access token",
    }


@pytest.fixture
def sample_group_data():
    """Sample group data from API."""
    return {
        "group_id": "group_123456",
        "name": "Test Group",
        "description": "A test group",
        "member_count": 5,
        "is_admin": True,
        "admins": ["user_1", "user_2"],
    }


@pytest.fixture
def sample_follower_list():
    """Sample followers list from API."""
    return {
        "error": 0,
        "data": {
            "total": 2,
            "followers": [
                {
                    "user_id": "user_001",
                    "display_name": "Follower One",
                    "avatar": "https://example.com/avatar1.jpg",
                },
                {
                    "user_id": "user_002",
                    "display_name": "Follower Two",
                    "avatar": "https://example.com/avatar2.jpg",
                },
            ],
        },
    }
