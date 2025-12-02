"""Tests for ZaloKit authentication module."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from zalokit.auth import ZaloAuth, TokenInfo
from zalokit.exceptions import (
    AuthenticationError,
    TokenExpiredError,
    InvalidTokenError,
    ValidationError,
)


class TestTokenInfo:
    """Tests for TokenInfo dataclass."""

    def test_token_info_creation(self):
        """Test TokenInfo creation with required fields."""
        token = TokenInfo(access_token="test_token")

        assert token.access_token == "test_token"
        assert token.refresh_token is None
        assert token.expires_in == 3600
        assert token.token_type == "Bearer"

    def test_token_info_with_all_fields(self):
        """Test TokenInfo creation with all fields."""
        token = TokenInfo(
            access_token="access_123",
            refresh_token="refresh_456",
            expires_in=7200,
            token_type="Bearer",
            created_at=1000000,
        )

        assert token.access_token == "access_123"
        assert token.refresh_token == "refresh_456"
        assert token.expires_in == 7200
        assert token.created_at == 1000000

    def test_token_expiration_calculation(self):
        """Test token expiration timestamp calculation."""
        token = TokenInfo(
            access_token="test",
            expires_in=3600,
            created_at=1000000,
        )

        assert token.expires_at == 1000000 + (3600 * 1000)

    def test_token_is_expired(self):
        """Test token expiration check."""
        # Create token that expired in the past
        token = TokenInfo(
            access_token="test",
            expires_in=1,
            created_at=0,  # Very old timestamp
        )

        assert token.is_expired is True

    def test_token_to_dict(self):
        """Test token serialization to dictionary."""
        token = TokenInfo(
            access_token="access_123",
            refresh_token="refresh_456",
            expires_in=3600,
            created_at=1000000,
        )

        data = token.to_dict()

        assert data["access_token"] == "access_123"
        assert data["refresh_token"] == "refresh_456"
        assert data["expires_in"] == 3600
        assert data["created_at"] == 1000000

    def test_token_from_dict(self):
        """Test token creation from dictionary."""
        data = {
            "access_token": "access_123",
            "refresh_token": "refresh_456",
            "expires_in": 7200,
            "created_at": 2000000,
        }

        token = TokenInfo.from_dict(data)

        assert token.access_token == "access_123"
        assert token.refresh_token == "refresh_456"
        assert token.expires_in == 7200
        assert token.created_at == 2000000


class TestZaloAuth:
    """Tests for ZaloAuth class."""

    def test_init_with_valid_credentials(self):
        """Test ZaloAuth initialization with valid credentials."""
        auth = ZaloAuth(
            app_id="test_app_id",
            app_secret="test_app_secret",
        )

        assert auth.app_id == "test_app_id"
        assert auth.app_secret == "test_app_secret"
        assert auth.is_authenticated is False

    def test_init_with_invalid_app_id(self):
        """Test ZaloAuth initialization with invalid app_id."""
        with pytest.raises(ValidationError) as exc_info:
            ZaloAuth(app_id="", app_secret="valid_secret")

        assert "app_id" in str(exc_info.value)

    def test_init_with_invalid_app_secret(self):
        """Test ZaloAuth initialization with invalid app_secret."""
        with pytest.raises(ValidationError) as exc_info:
            ZaloAuth(app_id="valid_id", app_secret="")

        assert "app_secret" in str(exc_info.value)

    def test_get_authorization_url(self):
        """Test authorization URL generation."""
        auth = ZaloAuth(
            app_id="test_app",
            app_secret="test_secret",
            redirect_uri="https://example.com/callback",
        )

        url = auth.get_authorization_url(state="test_state")

        assert "oauth.zaloapp.com" in url
        assert "app_id=test_app" in url
        assert "redirect_uri=" in url
        assert "state=test_state" in url

    def test_get_authorization_url_without_redirect_uri(self):
        """Test authorization URL generation without redirect_uri."""
        auth = ZaloAuth(app_id="test_app", app_secret="test_secret")

        with pytest.raises(ValidationError) as exc_info:
            auth.get_authorization_url()

        assert "redirect_uri" in str(exc_info.value)

    def test_set_access_token(self):
        """Test manually setting access token."""
        auth = ZaloAuth(app_id="test_app", app_secret="test_secret")

        auth.set_access_token("manual_token", "manual_refresh")

        assert auth.is_authenticated is True
        assert auth._token.access_token == "manual_token"
        assert auth._token.refresh_token == "manual_refresh"

    def test_get_access_token_not_authenticated(self):
        """Test getting access token when not authenticated."""
        auth = ZaloAuth(app_id="test_app", app_secret="test_secret")

        with pytest.raises(AuthenticationError):
            auth.get_access_token()

    def test_get_auth_header(self):
        """Test getting authorization header."""
        auth = ZaloAuth(app_id="test_app", app_secret="test_secret")
        auth.set_access_token("test_token")

        header = auth.get_auth_header()

        assert header["Authorization"] == "Bearer test_token"

    def test_token_storage(self):
        """Test token storage to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            token_path = Path(tmpdir) / "tokens.json"

            auth = ZaloAuth(
                app_id="test_app",
                app_secret="test_secret",
                token_storage_path=str(token_path),
            )

            auth.set_access_token("stored_token", "stored_refresh")

            # Verify file was created
            assert token_path.exists()

            # Verify content
            data = json.loads(token_path.read_text())
            assert data["access_token"] == "stored_token"
            assert data["refresh_token"] == "stored_refresh"

    def test_token_loading(self):
        """Test token loading from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            token_path = Path(tmpdir) / "tokens.json"

            # Create token file
            token_data = {
                "access_token": "loaded_token",
                "refresh_token": "loaded_refresh",
                "expires_in": 3600,
                "created_at": 9999999999999,  # Far future
            }
            token_path.write_text(json.dumps(token_data))

            # Create auth and verify token was loaded
            auth = ZaloAuth(
                app_id="test_app",
                app_secret="test_secret",
                token_storage_path=str(token_path),
            )

            assert auth._token is not None
            assert auth._token.access_token == "loaded_token"

    def test_revoke_token(self):
        """Test token revocation."""
        auth = ZaloAuth(app_id="test_app", app_secret="test_secret")
        auth.set_access_token("test_token")

        result = auth.revoke_token()

        assert result is True
        assert auth._token is None
        assert auth.is_authenticated is False

    def test_repr(self):
        """Test string representation."""
        auth = ZaloAuth(app_id="test_app_id_12345", app_secret="test_secret")

        repr_str = repr(auth)

        assert "ZaloAuth" in repr_str
        assert "not authenticated" in repr_str


class TestZaloAuthWithMocking:
    """Tests for ZaloAuth with mocked HTTP requests."""

    @patch("zalokit.auth.requests.Session")
    def test_exchange_code_for_token_success(self, mock_session_class):
        """Test successful code exchange for token."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
        }
        mock_session.post.return_value = mock_response

        auth = ZaloAuth(
            app_id="test_app",
            app_secret="test_secret",
            redirect_uri="https://example.com/callback",
        )

        token = auth.exchange_code_for_token("auth_code_123")

        assert token.access_token == "new_access_token"
        assert token.refresh_token == "new_refresh_token"
        assert auth.is_authenticated is True

    @patch("zalokit.auth.requests.Session")
    def test_exchange_code_for_token_error(self, mock_session_class):
        """Test failed code exchange."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Invalid authorization code",
        }
        mock_session.post.return_value = mock_response

        auth = ZaloAuth(
            app_id="test_app",
            app_secret="test_secret",
            redirect_uri="https://example.com/callback",
        )

        with pytest.raises(AuthenticationError) as exc_info:
            auth.exchange_code_for_token("invalid_code")

        assert "Invalid authorization code" in str(exc_info.value)

    @patch("zalokit.auth.requests.Session")
    def test_refresh_access_token_success(self, mock_session_class):
        """Test successful token refresh."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "refreshed_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
        }
        mock_session.post.return_value = mock_response

        auth = ZaloAuth(app_id="test_app", app_secret="test_secret")
        auth.set_access_token("old_token", "old_refresh_token")

        token = auth.refresh_access_token()

        assert token.access_token == "refreshed_access_token"

    def test_refresh_access_token_no_refresh_token(self):
        """Test token refresh without refresh token."""
        auth = ZaloAuth(app_id="test_app", app_secret="test_secret")
        auth.set_access_token("access_only")  # No refresh token

        with pytest.raises(AuthenticationError) as exc_info:
            auth.refresh_access_token()

        assert "No refresh token" in str(exc_info.value)
