"""
ZaloKit - A Python SDK for Zalo API integration.

This library provides an easy-to-use interface for interacting with
Zalo's messaging platform, including sending messages, managing contacts,
and handling group conversations.
"""

__version__ = "0.1.0"
__author__ = "ZaloKit Contributors"
__license__ = "MIT"

from zalokit.client import ZaloClient
from zalokit.auth import ZaloAuth
from zalokit.messaging import MessagingAPI
from zalokit.contacts import ContactsAPI
from zalokit.groups import GroupsAPI
from zalokit.exceptions import (
    ZaloKitError,
    AuthenticationError,
    APIError,
    RateLimitError,
    ValidationError,
)

__all__ = [
    "ZaloClient",
    "ZaloAuth",
    "MessagingAPI",
    "ContactsAPI",
    "GroupsAPI",
    "ZaloKitError",
    "AuthenticationError",
    "APIError",
    "RateLimitError",
    "ValidationError",
]
