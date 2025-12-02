"""
ZaloKit Contacts Module.

This module provides functionality for managing contacts and user profiles
through the Zalo platform.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import requests

from zalokit.exceptions import APIError, ContactError, ValidationError
from zalokit.utils import generate_request_id, validate_phone_number

logger = logging.getLogger(__name__)


class Gender(Enum):
    """User gender enum."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


@dataclass
class UserProfile:
    """Represents a Zalo user profile."""

    user_id: str
    display_name: str
    avatar: Optional[str] = None
    avatar_small: Optional[str] = None
    cover: Optional[str] = None
    gender: Gender = Gender.UNKNOWN
    birthday: Optional[str] = None
    phone: Optional[str] = None
    is_follower: bool = False
    is_following: bool = False
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    shared_info: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "avatar": self.avatar,
            "avatar_small": self.avatar_small,
            "cover": self.cover,
            "gender": self.gender.value,
            "birthday": self.birthday,
            "phone": self.phone,
            "is_follower": self.is_follower,
            "is_following": self.is_following,
            "tags": self.tags,
            "notes": self.notes,
            "shared_info": self.shared_info,
        }

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "UserProfile":
        """Create UserProfile from API response."""
        gender_map = {
            1: Gender.MALE,
            2: Gender.FEMALE,
            0: Gender.OTHER,
        }

        return cls(
            user_id=data.get("user_id", ""),
            display_name=data.get("display_name", data.get("name", "")),
            avatar=data.get("avatar", data.get("avatars", {}).get("240")),
            avatar_small=data.get("avatars", {}).get("120"),
            cover=data.get("cover"),
            gender=gender_map.get(data.get("user_gender"), Gender.UNKNOWN),
            birthday=data.get("birthday"),
            phone=data.get("phone"),
            is_follower=data.get("is_follower", False),
            is_following=data.get("is_following", False),
            tags=data.get("tags_and_notes_info", {}).get("tag_names", []),
            notes=data.get("tags_and_notes_info", {}).get("notes"),
            shared_info=data.get("shared_info", {}),
        )


@dataclass
class FollowerInfo:
    """Represents follower information."""

    user_id: str
    display_name: str
    avatar: Optional[str] = None
    followed_at: Optional[int] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "FollowerInfo":
        """Create FollowerInfo from API response."""
        return cls(
            user_id=data.get("user_id", ""),
            display_name=data.get("display_name", ""),
            avatar=data.get("avatar"),
            followed_at=data.get("followed_at"),
        )


class ContactsAPI:
    """
    Handles contact and user profile operations.

    This class provides methods for:
    - Getting user profiles
    - Managing followers
    - Tagging and organizing contacts
    - Searching users
    """

    BASE_URL = "https://openapi.zalo.me/v3.0/oa"

    def __init__(self, auth, timeout: int = 30):
        """
        Initialize ContactsAPI.

        Args:
            auth: ZaloAuth instance for authentication
            timeout: Request timeout in seconds
        """
        self.auth = auth
        self.timeout = timeout
        self._session = requests.Session()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make authenticated API request."""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self.auth.get_auth_header()
        request_id = generate_request_id()

        logger.debug(f"API Request [{request_id}]: {method} {endpoint}")

        try:
            if method == "GET":
                response = self._session.get(
                    url, headers=headers, params=data, timeout=self.timeout
                )
            elif method == "POST":
                headers["Content-Type"] = "application/json"
                response = self._session.post(
                    url, headers=headers, json=data, timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            result = response.json()

            if result.get("error") != 0:
                raise APIError(
                    message=result.get("message", "API request failed"),
                    status_code=response.status_code,
                    error_code=str(result.get("error")),
                )

            return result

        except requests.RequestException as e:
            logger.error(f"API Request [{request_id}] failed: {e}")
            raise APIError(f"Network error: {e}")

    def get_profile(self, user_id: str) -> UserProfile:
        """
        Get user profile by ID.

        Args:
            user_id: Zalo user ID

        Returns:
            UserProfile object

        Raises:
            ContactError: If profile cannot be retrieved
        """
        if not user_id:
            raise ValidationError("user_id is required", field="user_id")

        try:
            response = self._make_request("GET", "user/detail", {"user_id": user_id})
            return UserProfile.from_api_response(response.get("data", {}))
        except APIError as e:
            raise ContactError(str(e), contact_id=user_id)

    def get_followers(
        self,
        offset: int = 0,
        count: int = 50,
        tag_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get list of followers.

        Args:
            offset: Starting offset for pagination
            count: Number of followers to retrieve (max 50)
            tag_name: Optional tag to filter by

        Returns:
            Dictionary with followers list and pagination info
        """
        count = min(count, 50)  # Max 50 per request

        params = {"offset": offset, "count": count}
        if tag_name:
            params["tag_name"] = tag_name

        response = self._make_request("GET", "follower/getlist", params)
        data = response.get("data", {})

        followers = [
            FollowerInfo.from_api_response(f) for f in data.get("followers", [])
        ]

        return {
            "followers": followers,
            "total": data.get("total", 0),
            "offset": offset,
            "count": len(followers),
        }

    def get_all_followers(self, tag_name: Optional[str] = None) -> List[FollowerInfo]:
        """
        Get all followers with automatic pagination.

        Args:
            tag_name: Optional tag to filter by

        Returns:
            List of all followers
        """
        all_followers = []
        offset = 0

        while True:
            result = self.get_followers(offset=offset, count=50, tag_name=tag_name)
            all_followers.extend(result["followers"])

            if len(result["followers"]) < 50:
                break

            offset += 50

        return all_followers

    def get_recent_chat(
        self,
        offset: int = 0,
        count: int = 10,
    ) -> Dict[str, Any]:
        """
        Get recent chat users.

        Args:
            offset: Starting offset
            count: Number of users to retrieve

        Returns:
            Dictionary with recent users list
        """
        response = self._make_request(
            "GET", "conversation/list", {"offset": offset, "count": count}
        )
        return response.get("data", {})

    def assign_tag(self, user_id: str, tag_name: str) -> bool:
        """
        Assign a tag to a user.

        Args:
            user_id: User ID to tag
            tag_name: Tag name to assign

        Returns:
            True if successful
        """
        if not user_id:
            raise ValidationError("user_id is required", field="user_id")
        if not tag_name:
            raise ValidationError("tag_name is required", field="tag_name")

        data = {"user_id": user_id, "tag_name": tag_name}
        self._make_request("POST", "tag/tagfollower", data)
        return True

    def remove_tag(self, user_id: str, tag_name: str) -> bool:
        """
        Remove a tag from a user.

        Args:
            user_id: User ID to untag
            tag_name: Tag name to remove

        Returns:
            True if successful
        """
        if not user_id:
            raise ValidationError("user_id is required", field="user_id")
        if not tag_name:
            raise ValidationError("tag_name is required", field="tag_name")

        data = {"user_id": user_id, "tag_name": tag_name}
        self._make_request("POST", "tag/rmfollowerfromtag", data)
        return True

    def get_tags(self) -> List[Dict[str, Any]]:
        """
        Get all available tags.

        Returns:
            List of tag information
        """
        response = self._make_request("GET", "tag/getlist")
        return response.get("data", {}).get("tags", [])

    def create_tag(self, tag_name: str) -> bool:
        """
        Create a new tag.

        Args:
            tag_name: Name of tag to create

        Returns:
            True if successful
        """
        if not tag_name:
            raise ValidationError("tag_name is required", field="tag_name")

        self._make_request("POST", "tag/create", {"tag_name": tag_name})
        return True

    def delete_tag(self, tag_name: str) -> bool:
        """
        Delete a tag.

        Args:
            tag_name: Name of tag to delete

        Returns:
            True if successful
        """
        if not tag_name:
            raise ValidationError("tag_name is required", field="tag_name")

        self._make_request("POST", "tag/delete", {"tag_name": tag_name})
        return True

    def update_notes(self, user_id: str, notes: str) -> bool:
        """
        Update notes for a user.

        Args:
            user_id: User ID
            notes: Notes content

        Returns:
            True if successful
        """
        if not user_id:
            raise ValidationError("user_id is required", field="user_id")

        self._make_request(
            "POST", "tag/updatenote", {"user_id": user_id, "note": notes}
        )
        return True

    def send_follow_request(self, phone: str) -> Dict[str, Any]:
        """
        Send a follow request to a user by phone number.

        Args:
            phone: Phone number of user to follow

        Returns:
            Response with request status
        """
        if not validate_phone_number(phone):
            raise ValidationError("Invalid phone number format", field="phone")

        return self._make_request("POST", "follow/request", {"phone": phone})

    def get_conversation(
        self,
        user_id: str,
        offset: int = 0,
        count: int = 10,
    ) -> Dict[str, Any]:
        """
        Get conversation history with a user.

        Args:
            user_id: User ID
            offset: Starting offset
            count: Number of messages to retrieve

        Returns:
            Conversation data
        """
        if not user_id:
            raise ValidationError("user_id is required", field="user_id")

        return self._make_request(
            "GET",
            "conversation",
            {"user_id": user_id, "offset": offset, "count": count},
        )

    def is_user_active(self, user_id: str) -> bool:
        """
        Check if a user is currently active (online).

        Note: This may not be available for all users depending on privacy settings.

        Args:
            user_id: User ID to check

        Returns:
            True if user is active, False otherwise
        """
        try:
            profile = self.get_profile(user_id)
            return profile.shared_info.get("is_active", False)
        except Exception:
            return False

    def search_users(
        self,
        query: str,
        limit: int = 10,
    ) -> List[UserProfile]:
        """
        Search for users by name or phone.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of matching user profiles
        """
        if not query or len(query) < 2:
            raise ValidationError("Query must be at least 2 characters", field="query")

        # This is a placeholder - actual implementation depends on API availability
        logger.warning("User search API may have limited availability")
        return []
