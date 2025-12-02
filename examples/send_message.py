#!/usr/bin/env python3
"""
Example: Send messages using ZaloKit.

This script demonstrates how to send various types of messages
using the ZaloKit SDK.

Usage:
    python send_message.py

Make sure to set environment variables:
    - ZALO_APP_ID
    - ZALO_APP_SECRET
    - ZALO_ACCESS_TOKEN
    - ZALO_RECIPIENT_ID
"""

import os
import sys

from zalokit import ZaloClient
from zalokit.exceptions import (
    AuthenticationError,
    MessageError,
    RateLimitError,
    ZaloKitError,
)


def get_client() -> ZaloClient:
    """Create and configure ZaloClient from environment variables."""
    app_id = os.environ.get("ZALO_APP_ID")
    app_secret = os.environ.get("ZALO_APP_SECRET")
    access_token = os.environ.get("ZALO_ACCESS_TOKEN")

    if not all([app_id, app_secret, access_token]):
        print("Error: Missing required environment variables.")
        print("Please set: ZALO_APP_ID, ZALO_APP_SECRET, ZALO_ACCESS_TOKEN")
        sys.exit(1)

    return ZaloClient(
        app_id=app_id,
        app_secret=app_secret,
        access_token=access_token,
    )


def send_text_message(client: ZaloClient, recipient_id: str) -> None:
    """Send a simple text message."""
    print(f"\n--- Sending text message to {recipient_id} ---")

    try:
        response = client.send_message(
            recipient_id=recipient_id,
            text="Hello from ZaloKit! This is a test message.",
        )

        if response.success:
            print(f"Message sent successfully!")
            print(f"Message ID: {response.message_id}")
        else:
            print(f"Failed to send message: {response.error}")

    except MessageError as e:
        print(f"Message error: {e}")
    except RateLimitError as e:
        print(f"Rate limited. Try again in {e.retry_after} seconds.")
    except ZaloKitError as e:
        print(f"Error: {e}")


def send_image_message(client: ZaloClient, recipient_id: str, image_url: str) -> None:
    """Send an image message."""
    print(f"\n--- Sending image to {recipient_id} ---")

    try:
        response = client.send_image(
            recipient_id=recipient_id,
            image_url=image_url,
        )

        if response.success:
            print(f"Image sent successfully!")
            print(f"Message ID: {response.message_id}")
        else:
            print(f"Failed to send image: {response.error}")

    except ZaloKitError as e:
        print(f"Error: {e}")


def send_link_message(client: ZaloClient, recipient_id: str) -> None:
    """Send a link with preview."""
    print(f"\n--- Sending link to {recipient_id} ---")

    try:
        response = client.send_link(
            recipient_id=recipient_id,
            url="https://github.com/jvunder/ZaloKit",
            title="ZaloKit - Python SDK for Zalo",
            description="A powerful and easy-to-use Python SDK for the Zalo API",
        )

        if response.success:
            print(f"Link sent successfully!")
            print(f"Message ID: {response.message_id}")
        else:
            print(f"Failed to send link: {response.error}")

    except ZaloKitError as e:
        print(f"Error: {e}")


def send_buttons_message(client: ZaloClient, recipient_id: str) -> None:
    """Send a message with interactive buttons."""
    print(f"\n--- Sending buttons message to {recipient_id} ---")

    buttons = [
        {
            "title": "Visit Website",
            "type": "oa.open.url",
            "payload": {"url": "https://github.com/jvunder/ZaloKit"},
        },
        {
            "title": "Contact Us",
            "type": "oa.query.show",
            "payload": {"data": "contact"},
        },
    ]

    try:
        response = client.messaging.send_buttons(
            recipient_id=recipient_id,
            text="What would you like to do?",
            buttons=buttons,
        )

        if response.success:
            print(f"Buttons message sent successfully!")
            print(f"Message ID: {response.message_id}")
        else:
            print(f"Failed to send buttons: {response.error}")

    except ZaloKitError as e:
        print(f"Error: {e}")


def broadcast_message(client: ZaloClient, recipient_ids: list) -> None:
    """Broadcast a message to multiple users."""
    print(f"\n--- Broadcasting message to {len(recipient_ids)} recipients ---")

    try:
        results = client.broadcast_message(
            recipient_ids=recipient_ids,
            text="Hello everyone! This is a broadcast message from ZaloKit.",
        )

        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count

        print(f"Broadcast complete: {success_count} sent, {fail_count} failed")

        for i, result in enumerate(results):
            status = "OK" if result.success else f"FAILED: {result.error}"
            print(f"  - Recipient {recipient_ids[i]}: {status}")

    except ZaloKitError as e:
        print(f"Error: {e}")


def main():
    """Main function to demonstrate messaging capabilities."""
    print("=" * 50)
    print("ZaloKit - Message Sending Example")
    print("=" * 50)

    # Get recipient ID from environment
    recipient_id = os.environ.get("ZALO_RECIPIENT_ID")
    if not recipient_id:
        print("Warning: ZALO_RECIPIENT_ID not set. Using placeholder.")
        recipient_id = "placeholder_user_id"

    # Create client
    client = get_client()
    print(f"\nClient created: {client}")
    print(f"Authenticated: {client.is_authenticated}")

    # Demonstrate different message types
    send_text_message(client, recipient_id)

    # Uncomment to test other message types
    # send_image_message(
    #     client, recipient_id,
    #     "https://example.com/image.jpg"
    # )
    # send_link_message(client, recipient_id)
    # send_buttons_message(client, recipient_id)
    # broadcast_message(client, [recipient_id, "another_user_id"])

    print("\n" + "=" * 50)
    print("Example complete!")


if __name__ == "__main__":
    main()
