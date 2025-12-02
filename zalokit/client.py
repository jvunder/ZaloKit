"""
ZaloKit Client Module.

This module provides the main ZaloClient class which serves as the
primary interface for interacting with the Zalo API.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from zalokit.auth import ZaloAuth, TokenInfo
from zalokit.messaging import MessagingAPI, MessageResponse
from zalokit.contacts import ContactsAPI, UserProfile
from zalokit.groups import GroupsAPI, Group
from zalokit.exceptions import (
    ZaloKitError,
    AuthenticationError,
    ValidationError,
)
from zalokit.utils import setup_logging

logger = logging.getLogger(__name__)


class ZaloClient:
    """
    Main client for interacting with Zalo API.

    This class provides a unified interface to all Zalo API functionalities
    including authentication, messaging, contacts, and groups.

    Example:
        ```python
        from zalokit import ZaloClient

        # Initialize client
        client = ZaloClient(
            app_id="your_app_id",
            app_secret="your_app_secret"
        )

        # Set access token (after OAuth flow)
        client.set_access_token("your_access_token")

        # Send a message
        client.send_message("user_id", "Hello from ZaloKit!")
        ```
    """

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        token_storage_path: Optional[str] = None,
        on_token_refresh: Optional[Callable[[TokenInfo], None]] = None,
        timeout: int = 30,
        log_level: int = logging.INFO,
    ):
        """
        Initialize ZaloClient.

        Args:
            app_id: Zalo application ID
            app_secret: Zalo application secret
            access_token: Optional pre-existing access token
            refresh_token: Optional pre-existing refresh token
            redirect_uri: OAuth redirect URI for authentication flow
            token_storage_path: Path to store/load tokens
            on_token_refresh: Callback when token is refreshed
            timeout: Request timeout in seconds
            log_level: Logging level
        """
        # Setup logging
        setup_logging(level=log_level)

        # Initialize authentication
        self._auth = ZaloAuth(
            app_id=app_id,
            app_secret=app_secret,
            redirect_uri=redirect_uri,
            token_storage_path=token_storage_path,
            on_token_refresh=on_token_refresh,
        )

        # Set tokens if provided
        if access_token:
            self._auth.set_access_token(access_token, refresh_token)

        # Initialize API modules
        self._messaging = MessagingAPI(self._auth, timeout=timeout)
        self._contacts = ContactsAPI(self._auth, timeout=timeout)
        self._groups = GroupsAPI(self._auth, timeout=timeout)

        self._timeout = timeout

        logger.info("ZaloClient initialized")

    # ==================== Authentication ====================

    @property
    def auth(self) -> ZaloAuth:
        """Get the authentication handler."""
        return self._auth

    @property
    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        return self._auth.is_authenticated

    def get_authorization_url(
        self,
        state: Optional[str] = None,
        code_challenge: Optional[str] = None,
    ) -> str:
        """
        Get OAuth authorization URL.

        Args:
            state: Optional state for CSRF protection
            code_challenge: Optional PKCE code challenge

        Returns:
            Authorization URL for user to visit
        """
        return self._auth.get_authorization_url(state, code_challenge)

    def authenticate(
        self,
        code: str,
        code_verifier: Optional[str] = None,
    ) -> TokenInfo:
        """
        Complete OAuth authentication with authorization code.

        Args:
            code: Authorization code from OAuth callback
            code_verifier: PKCE code verifier if used

        Returns:
            TokenInfo with access token
        """
        return self._auth.exchange_code_for_token(code, code_verifier)

    def set_access_token(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
    ) -> None:
        """
        Manually set access token.

        Args:
            access_token: Access token string
            refresh_token: Optional refresh token
        """
        self._auth.set_access_token(access_token, refresh_token)

    def refresh_token(self) -> TokenInfo:
        """
        Refresh the access token.

        Returns:
            New TokenInfo
        """
        return self._auth.refresh_access_token()

    # ==================== Messaging ====================

    @property
    def messaging(self) -> MessagingAPI:
        """Get the messaging API handler."""
        return self._messaging

    def send_message(
        self,
        recipient_id: str,
        text: str,
        quote_message_id: Optional[str] = None,
    ) -> MessageResponse:
        """
        Send a text message.

        Args:
            recipient_id: User ID to send message to
            text: Message text
            quote_message_id: Optional message ID to reply to

        Returns:
            MessageResponse with result
        """
        return self._messaging.send_text_message(
            recipient_id, text, quote_message_id
        )

    def send_image(
        self,
        recipient_id: str,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
        image_id: Optional[str] = None,
    ) -> MessageResponse:
        """
        Send an image message.

        Args:
            recipient_id: User ID
            image_path: Local image path
            image_url: Remote image URL
            image_id: Pre-uploaded image ID

        Returns:
            MessageResponse with result
        """
        return self._messaging.send_image(
            recipient_id, image_path, image_url, image_id
        )

    def send_file(self, recipient_id: str, file_path: str) -> MessageResponse:
        """
        Send a file attachment.

        Args:
            recipient_id: User ID
            file_path: Local file path

        Returns:
            MessageResponse with result
        """
        return self._messaging.send_file(recipient_id, file_path)

    def send_sticker(self, recipient_id: str, sticker_id: str) -> MessageResponse:
        """
        Send a sticker.

        Args:
            recipient_id: User ID
            sticker_id: Sticker ID

        Returns:
            MessageResponse with result
        """
        return self._messaging.send_sticker(recipient_id, sticker_id)

    def send_link(
        self,
        recipient_id: str,
        url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
    ) -> MessageResponse:
        """
        Send a link with preview.

        Args:
            recipient_id: User ID
            url: Link URL
            title: Optional title
            description: Optional description
            thumbnail_url: Optional thumbnail

        Returns:
            MessageResponse with result
        """
        return self._messaging.send_link(
            recipient_id, url, title, description, thumbnail_url
        )

    def broadcast_message(
        self,
        recipient_ids: List[str],
        text: str,
    ) -> List[MessageResponse]:
        """
        Broadcast message to multiple users.

        Args:
            recipient_ids: List of user IDs
            text: Message text

        Returns:
            List of MessageResponse for each recipient
        """
        return self._messaging.broadcast_text(recipient_ids, text)

    # ==================== Contacts ====================

    @property
    def contacts(self) -> ContactsAPI:
        """Get the contacts API handler."""
        return self._contacts

    def get_user_profile(self, user_id: str) -> UserProfile:
        """
        Get user profile.

        Args:
            user_id: User ID

        Returns:
            UserProfile object
        """
        return self._contacts.get_profile(user_id)

    def get_followers(
        self,
        offset: int = 0,
        count: int = 50,
        tag_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get followers list.

        Args:
            offset: Starting offset
            count: Number to retrieve
            tag_name: Optional tag filter

        Returns:
            Dictionary with followers and pagination
        """
        return self._contacts.get_followers(offset, count, tag_name)

    def get_all_followers(self, tag_name: Optional[str] = None) -> List[Any]:
        """
        Get all followers with automatic pagination.

        Args:
            tag_name: Optional tag filter

        Returns:
            List of all followers
        """
        return self._contacts.get_all_followers(tag_name)

    def tag_user(self, user_id: str, tag_name: str) -> bool:
        """
        Assign tag to a user.

        Args:
            user_id: User ID
            tag_name: Tag name

        Returns:
            True if successful
        """
        return self._contacts.assign_tag(user_id, tag_name)

    def untag_user(self, user_id: str, tag_name: str) -> bool:
        """
        Remove tag from a user.

        Args:
            user_id: User ID
            tag_name: Tag name

        Returns:
            True if successful
        """
        return self._contacts.remove_tag(user_id, tag_name)

    def is_user_active(self, user_id: str) -> bool:
        """
        Check if user is online/active.

        Args:
            user_id: User ID

        Returns:
            True if active
        """
        return self._contacts.is_user_active(user_id)

    # ==================== Groups ====================

    @property
    def groups(self) -> GroupsAPI:
        """Get the groups API handler."""
        return self._groups

    def create_group(
        self,
        name: str,
        member_ids: List[str],
        description: Optional[str] = None,
    ) -> Group:
        """
        Create a new group.

        Args:
            name: Group name
            member_ids: Initial member IDs (min 2)
            description: Optional description

        Returns:
            Created Group object
        """
        return self._groups.create_group(name, member_ids, description)

    def get_group(self, group_id: str) -> Group:
        """
        Get group information.

        Args:
            group_id: Group ID

        Returns:
            Group object
        """
        return self._groups.get_group(group_id)

    def get_groups(self, offset: int = 0, count: int = 20) -> Dict[str, Any]:
        """
        Get list of groups.

        Args:
            offset: Starting offset
            count: Number to retrieve

        Returns:
            Dictionary with groups and pagination
        """
        return self._groups.get_groups(offset, count)

    def get_all_groups(self) -> List[Group]:
        """
        Get all groups.

        Returns:
            List of all groups
        """
        return self._groups.get_all_groups()

    def add_group_members(self, group_id: str, member_ids: List[str]) -> bool:
        """
        Add members to a group.

        Args:
            group_id: Group ID
            member_ids: User IDs to add

        Returns:
            True if successful
        """
        return self._groups.add_members(group_id, member_ids)

    def remove_group_member(self, group_id: str, member_id: str) -> bool:
        """
        Remove a member from a group.

        Args:
            group_id: Group ID
            member_id: User ID to remove

        Returns:
            True if successful
        """
        return self._groups.remove_member(group_id, member_id)

    def send_group_message(self, group_id: str, text: str) -> Dict[str, Any]:
        """
        Send message to a group.

        Args:
            group_id: Group ID
            text: Message text

        Returns:
            Response with message ID
        """
        return self._groups.send_message(group_id, text)

    # ==================== Utility Methods ====================

    def close(self) -> None:
        """
        Close client and cleanup resources.
        """
        logger.info("ZaloClient closed")

    def __enter__(self) -> "ZaloClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        status = "authenticated" if self.is_authenticated else "not authenticated"
        return f"ZaloClient(status={status})"
