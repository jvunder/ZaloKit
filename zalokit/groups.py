"""
ZaloKit Groups Module.

This module provides functionality for managing group conversations
and group operations through the Zalo platform.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import requests

from zalokit.exceptions import APIError, GroupError, ValidationError
from zalokit.utils import generate_request_id, sanitize_message

logger = logging.getLogger(__name__)


class GroupRole(Enum):
    """Group member roles."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class GroupType(Enum):
    """Group types."""

    NORMAL = "normal"
    BROADCAST = "broadcast"


@dataclass
class GroupMember:
    """Represents a group member."""

    user_id: str
    display_name: str
    avatar: Optional[str] = None
    role: GroupRole = GroupRole.MEMBER
    joined_at: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "avatar": self.avatar,
            "role": self.role.value,
            "joined_at": self.joined_at,
        }

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "GroupMember":
        """Create from API response."""
        role_map = {
            "owner": GroupRole.OWNER,
            "admin": GroupRole.ADMIN,
            "-1": GroupRole.OWNER,
            "0": GroupRole.ADMIN,
            "1": GroupRole.MEMBER,
        }

        return cls(
            user_id=data.get("user_id", ""),
            display_name=data.get("display_name", data.get("name", "")),
            avatar=data.get("avatar"),
            role=role_map.get(str(data.get("role", "1")), GroupRole.MEMBER),
            joined_at=data.get("joined_at"),
        )


@dataclass
class Group:
    """Represents a Zalo group."""

    group_id: str
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    cover: Optional[str] = None
    group_type: GroupType = GroupType.NORMAL
    member_count: int = 0
    created_at: Optional[int] = None
    is_admin: bool = False
    admins: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "group_id": self.group_id,
            "name": self.name,
            "description": self.description,
            "avatar": self.avatar,
            "cover": self.cover,
            "group_type": self.group_type.value,
            "member_count": self.member_count,
            "created_at": self.created_at,
            "is_admin": self.is_admin,
            "admins": self.admins,
        }

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Group":
        """Create from API response."""
        return cls(
            group_id=data.get("group_id", data.get("id", "")),
            name=data.get("name", ""),
            description=data.get("description"),
            avatar=data.get("avatar"),
            cover=data.get("cover"),
            member_count=data.get("member_count", data.get("total_member", 0)),
            created_at=data.get("created_at"),
            is_admin=data.get("is_admin", False),
            admins=data.get("admins", []),
        )


class GroupsAPI:
    """
    Handles group operations with Zalo API.

    This class provides methods for:
    - Creating and managing groups
    - Adding/removing members
    - Sending group messages
    - Managing group settings
    """

    BASE_URL = "https://openapi.zalo.me/v2.0/oa"

    def __init__(self, auth, timeout: int = 30):
        """
        Initialize GroupsAPI.

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

    def create_group(
        self,
        name: str,
        member_ids: List[str],
        description: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> Group:
        """
        Create a new group.

        Args:
            name: Group name
            member_ids: List of user IDs to add as members
            description: Optional group description
            avatar_url: Optional group avatar URL

        Returns:
            Created Group object

        Raises:
            ValidationError: If parameters are invalid
            GroupError: If creation fails
        """
        if not name:
            raise ValidationError("name is required", field="name")
        if not member_ids or len(member_ids) < 2:
            raise ValidationError(
                "At least 2 members required", field="member_ids"
            )

        data = {
            "name": sanitize_message(name, max_length=100),
            "member_ids": member_ids,
        }

        if description:
            data["description"] = sanitize_message(description, max_length=500)
        if avatar_url:
            data["avatar"] = avatar_url

        try:
            response = self._make_request("POST", "group/create", data)
            return Group.from_api_response(response.get("data", {}))
        except APIError as e:
            raise GroupError(str(e))

    def get_group(self, group_id: str) -> Group:
        """
        Get group information.

        Args:
            group_id: Group ID

        Returns:
            Group object
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")

        try:
            response = self._make_request("GET", "group/getinfo", {"group_id": group_id})
            return Group.from_api_response(response.get("data", {}))
        except APIError as e:
            raise GroupError(str(e), group_id=group_id)

    def get_groups(self, offset: int = 0, count: int = 20) -> Dict[str, Any]:
        """
        Get list of groups.

        Args:
            offset: Starting offset
            count: Number of groups to retrieve

        Returns:
            Dictionary with groups list and pagination info
        """
        response = self._make_request(
            "GET", "group/getlist", {"offset": offset, "count": count}
        )
        data = response.get("data", {})

        groups = [Group.from_api_response(g) for g in data.get("groups", [])]

        return {
            "groups": groups,
            "total": data.get("total", 0),
            "offset": offset,
            "count": len(groups),
        }

    def get_all_groups(self) -> List[Group]:
        """
        Get all groups with automatic pagination.

        Returns:
            List of all groups
        """
        all_groups = []
        offset = 0

        while True:
            result = self.get_groups(offset=offset, count=20)
            all_groups.extend(result["groups"])

            if len(result["groups"]) < 20:
                break

            offset += 20

        return all_groups

    def get_members(
        self,
        group_id: str,
        offset: int = 0,
        count: int = 50,
    ) -> Dict[str, Any]:
        """
        Get group members.

        Args:
            group_id: Group ID
            offset: Starting offset
            count: Number of members to retrieve

        Returns:
            Dictionary with members list and pagination info
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")

        response = self._make_request(
            "GET",
            "group/getmembers",
            {"group_id": group_id, "offset": offset, "count": count},
        )
        data = response.get("data", {})

        members = [GroupMember.from_api_response(m) for m in data.get("members", [])]

        return {
            "members": members,
            "total": data.get("total", 0),
            "offset": offset,
            "count": len(members),
        }

    def add_members(self, group_id: str, member_ids: List[str]) -> bool:
        """
        Add members to a group.

        Args:
            group_id: Group ID
            member_ids: List of user IDs to add

        Returns:
            True if successful
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")
        if not member_ids:
            raise ValidationError("member_ids is required", field="member_ids")

        try:
            self._make_request(
                "POST",
                "group/addmember",
                {"group_id": group_id, "member_ids": member_ids},
            )
            return True
        except APIError as e:
            raise GroupError(str(e), group_id=group_id)

    def remove_member(self, group_id: str, member_id: str) -> bool:
        """
        Remove a member from a group.

        Args:
            group_id: Group ID
            member_id: User ID to remove

        Returns:
            True if successful
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")
        if not member_id:
            raise ValidationError("member_id is required", field="member_id")

        try:
            self._make_request(
                "POST",
                "group/removemember",
                {"group_id": group_id, "member_id": member_id},
            )
            return True
        except APIError as e:
            raise GroupError(str(e), group_id=group_id)

    def leave_group(self, group_id: str) -> bool:
        """
        Leave a group.

        Args:
            group_id: Group ID

        Returns:
            True if successful
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")

        try:
            self._make_request("POST", "group/leave", {"group_id": group_id})
            return True
        except APIError as e:
            raise GroupError(str(e), group_id=group_id)

    def update_group(
        self,
        group_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> bool:
        """
        Update group information.

        Args:
            group_id: Group ID
            name: New group name
            description: New description
            avatar_url: New avatar URL

        Returns:
            True if successful
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")

        data = {"group_id": group_id}

        if name:
            data["name"] = sanitize_message(name, max_length=100)
        if description:
            data["description"] = sanitize_message(description, max_length=500)
        if avatar_url:
            data["avatar"] = avatar_url

        try:
            self._make_request("POST", "group/update", data)
            return True
        except APIError as e:
            raise GroupError(str(e), group_id=group_id)

    def set_admin(self, group_id: str, member_id: str, is_admin: bool = True) -> bool:
        """
        Set or remove admin role for a member.

        Args:
            group_id: Group ID
            member_id: User ID
            is_admin: True to make admin, False to remove admin

        Returns:
            True if successful
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")
        if not member_id:
            raise ValidationError("member_id is required", field="member_id")

        endpoint = "group/addadmin" if is_admin else "group/removeadmin"

        try:
            self._make_request(
                "POST", endpoint, {"group_id": group_id, "member_id": member_id}
            )
            return True
        except APIError as e:
            raise GroupError(str(e), group_id=group_id)

    def send_message(
        self,
        group_id: str,
        text: str,
    ) -> Dict[str, Any]:
        """
        Send a text message to a group.

        Args:
            group_id: Group ID
            text: Message text

        Returns:
            Response with message ID
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")
        if not text:
            raise ValidationError("text is required", field="text")

        try:
            return self._make_request(
                "POST",
                "group/message",
                {"group_id": group_id, "message": {"text": sanitize_message(text)}},
            )
        except APIError as e:
            raise GroupError(str(e), group_id=group_id)

    def get_pending_requests(self, group_id: str) -> List[Dict[str, Any]]:
        """
        Get pending join requests for a group.

        Args:
            group_id: Group ID

        Returns:
            List of pending requests
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")

        response = self._make_request(
            "GET", "group/getpendingrequests", {"group_id": group_id}
        )
        return response.get("data", {}).get("requests", [])

    def approve_request(self, group_id: str, user_id: str) -> bool:
        """
        Approve a join request.

        Args:
            group_id: Group ID
            user_id: User ID to approve

        Returns:
            True if successful
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")
        if not user_id:
            raise ValidationError("user_id is required", field="user_id")

        try:
            self._make_request(
                "POST",
                "group/approverequest",
                {"group_id": group_id, "user_id": user_id},
            )
            return True
        except APIError as e:
            raise GroupError(str(e), group_id=group_id)

    def reject_request(self, group_id: str, user_id: str) -> bool:
        """
        Reject a join request.

        Args:
            group_id: Group ID
            user_id: User ID to reject

        Returns:
            True if successful
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")
        if not user_id:
            raise ValidationError("user_id is required", field="user_id")

        try:
            self._make_request(
                "POST",
                "group/rejectrequest",
                {"group_id": group_id, "user_id": user_id},
            )
            return True
        except APIError as e:
            raise GroupError(str(e), group_id=group_id)

    def pin_message(self, group_id: str, message_id: str) -> bool:
        """
        Pin a message in a group.

        Args:
            group_id: Group ID
            message_id: Message ID to pin

        Returns:
            True if successful
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")
        if not message_id:
            raise ValidationError("message_id is required", field="message_id")

        try:
            self._make_request(
                "POST",
                "group/pinmessage",
                {"group_id": group_id, "message_id": message_id},
            )
            return True
        except APIError as e:
            raise GroupError(str(e), group_id=group_id)

    def unpin_message(self, group_id: str, message_id: str) -> bool:
        """
        Unpin a message in a group.

        Args:
            group_id: Group ID
            message_id: Message ID to unpin

        Returns:
            True if successful
        """
        if not group_id:
            raise ValidationError("group_id is required", field="group_id")
        if not message_id:
            raise ValidationError("message_id is required", field="message_id")

        try:
            self._make_request(
                "POST",
                "group/unpinmessage",
                {"group_id": group_id, "message_id": message_id},
            )
            return True
        except APIError as e:
            raise GroupError(str(e), group_id=group_id)
