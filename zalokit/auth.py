"""
ZaloKit Authentication Module.

This module handles all authentication-related operations including
OAuth2 flow, token management, and credential storage.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Optional, Any

import requests

from zalokit.exceptions import (
    AuthenticationError,
    TokenExpiredError,
    InvalidTokenError,
    ValidationError,
)
from zalokit.utils import generate_request_id, get_timestamp, mask_sensitive_data

logger = logging.getLogger(__name__)


@dataclass
class TokenInfo:
    """Represents OAuth token information."""

    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int = 3600
    token_type: str = "Bearer"
    created_at: int = field(default_factory=get_timestamp)

    @property
    def expires_at(self) -> int:
        """Calculate token expiration timestamp."""
        return self.created_at + (self.expires_in * 1000)

    @property
    def is_expired(self) -> bool:
        """Check if token has expired."""
        # Add 60 second buffer
        return get_timestamp() >= (self.expires_at - 60000)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_in": self.expires_in,
            "token_type": self.token_type,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenInfo":
        """Create TokenInfo from dictionary."""
        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in", 3600),
            token_type=data.get("token_type", "Bearer"),
            created_at=data.get("created_at", get_timestamp()),
        )


class ZaloAuth:
    """
    Handles Zalo OAuth2 authentication flow.

    This class manages the complete OAuth2 authentication lifecycle including:
    - Authorization URL generation
    - Token exchange
    - Token refresh
    - Token storage and retrieval
    """

    OAUTH_BASE_URL = "https://oauth.zaloapp.com/v4"
    OPENAPI_BASE_URL = "https://openapi.zalo.me/v2.0"

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        redirect_uri: Optional[str] = None,
        token_storage_path: Optional[str] = None,
        on_token_refresh: Optional[Callable[[TokenInfo], None]] = None,
    ):
        """
        Initialize ZaloAuth.

        Args:
            app_id: Zalo application ID
            app_secret: Zalo application secret
            redirect_uri: OAuth redirect URI
            token_storage_path: Path to store tokens (optional)
            on_token_refresh: Callback when token is refreshed
        """
        self._validate_credentials(app_id, app_secret)

        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.token_storage_path = token_storage_path
        self.on_token_refresh = on_token_refresh

        self._token: Optional[TokenInfo] = None
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "ZaloKit/0.1.0",
            }
        )

        # Try to load existing token
        if token_storage_path:
            self._load_token()

    def _validate_credentials(self, app_id: str, app_secret: str) -> None:
        """Validate app credentials."""
        if not app_id or not isinstance(app_id, str):
            raise ValidationError("Invalid app_id", field="app_id")
        if not app_secret or not isinstance(app_secret, str):
            raise ValidationError("Invalid app_secret", field="app_secret")

    def get_authorization_url(
        self,
        state: Optional[str] = None,
        code_challenge: Optional[str] = None,
        code_challenge_method: str = "S256",
    ) -> str:
        """
        Generate OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection
            code_challenge: PKCE code challenge (recommended)
            code_challenge_method: PKCE method (S256 or plain)

        Returns:
            Authorization URL for user to visit
        """
        if not self.redirect_uri:
            raise ValidationError("redirect_uri is required", field="redirect_uri")

        params = {
            "app_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "state": state or generate_request_id(),
        }

        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = code_challenge_method

        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.OAUTH_BASE_URL}/permission?{query}"

    def exchange_code_for_token(
        self,
        code: str,
        code_verifier: Optional[str] = None,
    ) -> TokenInfo:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback
            code_verifier: PKCE code verifier (if code_challenge was used)

        Returns:
            TokenInfo object with access token

        Raises:
            AuthenticationError: If token exchange fails
        """
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret,
            "code": code,
            "grant_type": "authorization_code",
        }

        if code_verifier:
            data["code_verifier"] = code_verifier

        logger.info("Exchanging authorization code for token")
        response = self._make_token_request(data)

        self._token = TokenInfo(
            access_token=response["access_token"],
            refresh_token=response.get("refresh_token"),
            expires_in=response.get("expires_in", 3600),
        )

        self._save_token()
        logger.info("Successfully obtained access token")
        return self._token

    def refresh_access_token(self, refresh_token: Optional[str] = None) -> TokenInfo:
        """
        Refresh the access token.

        Args:
            refresh_token: Refresh token (uses stored one if not provided)

        Returns:
            New TokenInfo object

        Raises:
            AuthenticationError: If token refresh fails
        """
        token = refresh_token or (self._token.refresh_token if self._token else None)

        if not token:
            raise AuthenticationError("No refresh token available")

        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret,
            "refresh_token": token,
            "grant_type": "refresh_token",
        }

        logger.info("Refreshing access token")
        response = self._make_token_request(data)

        self._token = TokenInfo(
            access_token=response["access_token"],
            refresh_token=response.get("refresh_token", token),
            expires_in=response.get("expires_in", 3600),
        )

        self._save_token()

        if self.on_token_refresh:
            self.on_token_refresh(self._token)

        logger.info("Successfully refreshed access token")
        return self._token

    def _make_token_request(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Make token request to OAuth server."""
        try:
            response = self._session.post(
                f"{self.OAUTH_BASE_URL}/access_token",
                data=data,
                timeout=30,
            )

            result = response.json()

            if "error" in result:
                error_code = result.get("error")
                error_msg = result.get("error_description", "Token request failed")

                if error_code == "invalid_token":
                    raise InvalidTokenError(error_msg)
                elif error_code == "expired_token":
                    raise TokenExpiredError(error_msg)
                else:
                    raise AuthenticationError(error_msg, error_code=error_code)

            return result

        except requests.RequestException as e:
            logger.error(f"Token request failed: {e}")
            raise AuthenticationError(f"Network error during authentication: {e}")

    def get_access_token(self, auto_refresh: bool = True) -> str:
        """
        Get current access token, refreshing if necessary.

        Args:
            auto_refresh: Automatically refresh if expired

        Returns:
            Access token string

        Raises:
            AuthenticationError: If no valid token available
        """
        if not self._token:
            raise AuthenticationError("Not authenticated. Call exchange_code_for_token first.")

        if self._token.is_expired:
            if auto_refresh and self._token.refresh_token:
                self.refresh_access_token()
            else:
                raise TokenExpiredError()

        return self._token.access_token

    def set_access_token(self, access_token: str, refresh_token: Optional[str] = None) -> None:
        """
        Manually set access token.

        Args:
            access_token: Access token string
            refresh_token: Optional refresh token
        """
        self._token = TokenInfo(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        self._save_token()
        logger.info("Access token set manually")

    @property
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with valid token."""
        return self._token is not None and not self._token.is_expired

    @property
    def token_info(self) -> Optional[TokenInfo]:
        """Get current token information."""
        return self._token

    def _save_token(self) -> None:
        """Save token to storage."""
        if not self.token_storage_path or not self._token:
            return

        try:
            path = Path(self.token_storage_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self._token.to_dict(), indent=2))
            logger.debug(f"Token saved to {self.token_storage_path}")
        except Exception as e:
            logger.warning(f"Failed to save token: {e}")

    def _load_token(self) -> None:
        """Load token from storage."""
        if not self.token_storage_path:
            return

        try:
            path = Path(self.token_storage_path)
            if path.exists():
                data = json.loads(path.read_text())
                self._token = TokenInfo.from_dict(data)
                logger.debug(f"Token loaded from {self.token_storage_path}")
        except Exception as e:
            logger.warning(f"Failed to load token: {e}")

    def revoke_token(self) -> bool:
        """
        Revoke current access token.

        Returns:
            True if successful, False otherwise
        """
        if not self._token:
            return True

        try:
            # Note: Implement actual revocation endpoint if available
            logger.info("Revoking access token")
            self._token = None
            if self.token_storage_path:
                Path(self.token_storage_path).unlink(missing_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to revoke token: {e}")
            return False

    def get_auth_header(self) -> Dict[str, str]:
        """
        Get authorization header for API requests.

        Returns:
            Dictionary with Authorization header
        """
        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

    def __repr__(self) -> str:
        token_status = "authenticated" if self.is_authenticated else "not authenticated"
        return f"ZaloAuth(app_id={mask_sensitive_data(self.app_id)}, status={token_status})"
