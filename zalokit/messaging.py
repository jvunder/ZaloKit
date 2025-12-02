"""
ZaloKit Messaging Module.

This module provides functionality for sending and receiving messages
through the Zalo platform.
"""

import logging
import mimetypes
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests

from zalokit.exceptions import (
    APIError,
    MessageError,
    ValidationError,
    RateLimitError,
)
from zalokit.utils import (
    generate_request_id,
    get_timestamp,
    sanitize_message,
    format_file_size,
)

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Supported message types."""

    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    STICKER = "sticker"
    GIF = "gif"
    LINK = "link"
    TEMPLATE = "template"
    REQUEST_USER_INFO = "request_user_info"


class AttachmentType(Enum):
    """Supported attachment types."""

    IMAGE = "image"
    FILE = "file"
    GIF = "gif"
    AUDIO = "audio"
    VIDEO = "video"


@dataclass
class Message:
    """Represents a message."""

    message_id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType
    content: str
    timestamp: int = field(default_factory=get_timestamp)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "attachments": self.attachments,
            "metadata": self.metadata,
        }


@dataclass
class MessageResponse:
    """Response from sending a message."""

    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "MessageResponse":
        """Create from API response."""
        if response.get("error") == 0:
            return cls(
                success=True,
                message_id=response.get("data", {}).get("message_id"),
            )
        return cls(
            success=False,
            error=response.get("message", "Unknown error"),
            error_code=str(response.get("error")),
        )


class MessagingAPI:
    """
    Handles messaging operations with Zalo API.

    This class provides methods for:
    - Sending text messages
    - Sending media (images, files, stickers)
    - Sending interactive templates
    - Managing message status
    """

    BASE_URL = "https://openapi.zalo.me/v3.0/oa"

    def __init__(self, auth, timeout: int = 30):
        """
        Initialize MessagingAPI.

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
        files: Optional[Dict[str, Any]] = None,
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
                if files:
                    response = self._session.post(
                        url, headers=headers, data=data, files=files, timeout=self.timeout
                    )
                else:
                    headers["Content-Type"] = "application/json"
                    response = self._session.post(
                        url, headers=headers, json=data, timeout=self.timeout
                    )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            result = response.json()

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise RateLimitError(retry_after=retry_after)

            # Handle API errors
            if result.get("error") != 0:
                raise APIError(
                    message=result.get("message", "API request failed"),
                    status_code=response.status_code,
                    error_code=str(result.get("error")),
                    details=result,
                )

            logger.debug(f"API Response [{request_id}]: Success")
            return result

        except requests.RequestException as e:
            logger.error(f"API Request [{request_id}] failed: {e}")
            raise APIError(f"Network error: {e}")

    def send_text_message(
        self,
        recipient_id: str,
        text: str,
        quote_message_id: Optional[str] = None,
    ) -> MessageResponse:
        """
        Send a text message.

        Args:
            recipient_id: User ID to send message to
            text: Message text content
            quote_message_id: Optional message ID to quote/reply to

        Returns:
            MessageResponse with result

        Raises:
            ValidationError: If parameters are invalid
            MessageError: If sending fails
        """
        if not recipient_id:
            raise ValidationError("recipient_id is required", field="recipient_id")
        if not text:
            raise ValidationError("text is required", field="text")

        text = sanitize_message(text)

        data = {
            "recipient": {"user_id": recipient_id},
            "message": {"text": text},
        }

        if quote_message_id:
            data["message"]["quote_message_id"] = quote_message_id

        try:
            response = self._make_request("POST", "message/text", data)
            return MessageResponse.from_api_response(response)
        except APIError as e:
            raise MessageError(str(e), recipient_id=recipient_id)

    def send_image(
        self,
        recipient_id: str,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
        image_id: Optional[str] = None,
        caption: Optional[str] = None,
    ) -> MessageResponse:
        """
        Send an image message.

        Args:
            recipient_id: User ID to send image to
            image_path: Local path to image file
            image_url: URL of image
            image_id: Previously uploaded image ID
            caption: Optional caption for image

        Returns:
            MessageResponse with result
        """
        if not recipient_id:
            raise ValidationError("recipient_id is required", field="recipient_id")

        if not any([image_path, image_url, image_id]):
            raise ValidationError("One of image_path, image_url, or image_id is required")

        data = {"recipient": {"user_id": recipient_id}}

        if image_id:
            data["message"] = {"attachment": {"type": "template", "payload": {"template_type": "media", "elements": [{"media_type": "image", "attachment_id": image_id}]}}}
        elif image_url:
            data["message"] = {"attachment": {"type": "image", "payload": {"url": image_url}}}
        elif image_path:
            # Upload image first
            upload_response = self.upload_image(image_path)
            if not upload_response.get("data", {}).get("attachment_id"):
                raise MessageError("Failed to upload image", recipient_id=recipient_id)
            attachment_id = upload_response["data"]["attachment_id"]
            data["message"] = {"attachment": {"type": "template", "payload": {"template_type": "media", "elements": [{"media_type": "image", "attachment_id": attachment_id}]}}}

        response = self._make_request("POST", "message/attachment", data)
        return MessageResponse.from_api_response(response)

    def send_file(
        self,
        recipient_id: str,
        file_path: str,
    ) -> MessageResponse:
        """
        Send a file attachment.

        Args:
            recipient_id: User ID to send file to
            file_path: Local path to file

        Returns:
            MessageResponse with result
        """
        if not recipient_id:
            raise ValidationError("recipient_id is required", field="recipient_id")
        if not file_path:
            raise ValidationError("file_path is required", field="file_path")

        path = Path(file_path)
        if not path.exists():
            raise ValidationError(f"File not found: {file_path}", field="file_path")

        # Upload file first
        upload_response = self.upload_file(file_path)
        if not upload_response.get("data", {}).get("token"):
            raise MessageError("Failed to upload file", recipient_id=recipient_id)

        file_token = upload_response["data"]["token"]

        data = {
            "recipient": {"user_id": recipient_id},
            "message": {
                "attachment": {
                    "type": "file",
                    "payload": {"token": file_token},
                }
            },
        }

        response = self._make_request("POST", "message/attachment", data)
        return MessageResponse.from_api_response(response)

    def send_sticker(
        self,
        recipient_id: str,
        sticker_id: str,
    ) -> MessageResponse:
        """
        Send a sticker.

        Args:
            recipient_id: User ID to send sticker to
            sticker_id: ID of sticker to send

        Returns:
            MessageResponse with result
        """
        if not recipient_id:
            raise ValidationError("recipient_id is required", field="recipient_id")
        if not sticker_id:
            raise ValidationError("sticker_id is required", field="sticker_id")

        data = {
            "recipient": {"user_id": recipient_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "media",
                        "elements": [{"media_type": "sticker", "attachment_id": sticker_id}],
                    },
                }
            },
        }

        response = self._make_request("POST", "message/attachment", data)
        return MessageResponse.from_api_response(response)

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
            recipient_id: User ID to send link to
            url: Link URL
            title: Optional link title
            description: Optional link description
            thumbnail_url: Optional thumbnail image URL

        Returns:
            MessageResponse with result
        """
        if not recipient_id:
            raise ValidationError("recipient_id is required", field="recipient_id")
        if not url:
            raise ValidationError("url is required", field="url")

        element = {
            "type": "banner",
            "default_action": {"type": "oa.open.url", "url": url},
        }

        if thumbnail_url:
            element["image_url"] = thumbnail_url

        data = {
            "recipient": {"user_id": recipient_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "list",
                        "elements": [element],
                    },
                }
            },
        }

        response = self._make_request("POST", "message/attachment", data)
        return MessageResponse.from_api_response(response)

    def send_template(
        self,
        recipient_id: str,
        template: Dict[str, Any],
    ) -> MessageResponse:
        """
        Send a custom template message.

        Args:
            recipient_id: User ID to send template to
            template: Template configuration dictionary

        Returns:
            MessageResponse with result
        """
        if not recipient_id:
            raise ValidationError("recipient_id is required", field="recipient_id")
        if not template:
            raise ValidationError("template is required", field="template")

        data = {
            "recipient": {"user_id": recipient_id},
            "message": {"attachment": {"type": "template", "payload": template}},
        }

        response = self._make_request("POST", "message/attachment", data)
        return MessageResponse.from_api_response(response)

    def send_buttons(
        self,
        recipient_id: str,
        text: str,
        buttons: List[Dict[str, Any]],
    ) -> MessageResponse:
        """
        Send a message with interactive buttons.

        Args:
            recipient_id: User ID to send to
            text: Message text
            buttons: List of button configurations

        Returns:
            MessageResponse with result
        """
        template = {
            "template_type": "button",
            "text": sanitize_message(text),
            "buttons": buttons,
        }

        return self.send_template(recipient_id, template)

    def upload_image(self, image_path: str) -> Dict[str, Any]:
        """
        Upload an image to Zalo servers.

        Args:
            image_path: Local path to image file

        Returns:
            Upload response with attachment_id
        """
        path = Path(image_path)
        if not path.exists():
            raise ValidationError(f"Image not found: {image_path}", field="image_path")

        mime_type = mimetypes.guess_type(str(path))[0] or "image/jpeg"

        with open(path, "rb") as f:
            files = {"file": (path.name, f, mime_type)}
            return self._make_request("POST", "upload/image", files=files)

    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a file to Zalo servers.

        Args:
            file_path: Local path to file

        Returns:
            Upload response with file token
        """
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(f"File not found: {file_path}", field="file_path")

        mime_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"

        with open(path, "rb") as f:
            files = {"file": (path.name, f, mime_type)}
            return self._make_request("POST", "upload/file", files=files)

    def broadcast_text(
        self,
        recipient_ids: List[str],
        text: str,
    ) -> List[MessageResponse]:
        """
        Broadcast text message to multiple recipients.

        Args:
            recipient_ids: List of user IDs
            text: Message text

        Returns:
            List of MessageResponse for each recipient
        """
        results = []
        for recipient_id in recipient_ids:
            try:
                result = self.send_text_message(recipient_id, text)
                results.append(result)
            except Exception as e:
                results.append(MessageResponse(success=False, error=str(e)))
        return results

    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get delivery status of a message.

        Args:
            message_id: Message ID to check

        Returns:
            Message status information
        """
        return self._make_request("GET", "message/status", {"message_id": message_id})
