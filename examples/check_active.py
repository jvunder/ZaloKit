#!/usr/bin/env python3
"""
Example: Check user activity status using ZaloKit.

This script demonstrates how to check if users are active/online
and retrieve user profile information.

Usage:
    python check_active.py

Make sure to set environment variables:
    - ZALO_APP_ID
    - ZALO_APP_SECRET
    - ZALO_ACCESS_TOKEN
"""

import os
import sys
from datetime import datetime

from zalokit import ZaloClient
from zalokit.exceptions import ContactError, ZaloKitError


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


def check_user_profile(client: ZaloClient, user_id: str) -> None:
    """Get and display user profile information."""
    print(f"\n--- User Profile: {user_id} ---")

    try:
        profile = client.get_user_profile(user_id)

        print(f"User ID: {profile.user_id}")
        print(f"Display Name: {profile.display_name}")
        print(f"Avatar: {profile.avatar or 'Not available'}")
        print(f"Gender: {profile.gender.value}")
        print(f"Birthday: {profile.birthday or 'Not shared'}")
        print(f"Is Follower: {profile.is_follower}")
        print(f"Is Following: {profile.is_following}")

        if profile.tags:
            print(f"Tags: {', '.join(profile.tags)}")

        if profile.notes:
            print(f"Notes: {profile.notes}")

    except ContactError as e:
        print(f"Contact error: {e}")
    except ZaloKitError as e:
        print(f"Error retrieving profile: {e}")


def check_user_active(client: ZaloClient, user_id: str) -> None:
    """Check if a user is currently active/online."""
    print(f"\n--- Checking Activity Status: {user_id} ---")

    try:
        is_active = client.is_user_active(user_id)

        status = "ONLINE" if is_active else "OFFLINE"
        print(f"User Status: {status}")
        print(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except ZaloKitError as e:
        print(f"Error checking status: {e}")
        print("Note: Activity status may not be available for all users.")


def list_followers(client: ZaloClient, limit: int = 10) -> None:
    """List followers with their activity status."""
    print(f"\n--- Listing Followers (limit: {limit}) ---")

    try:
        result = client.get_followers(offset=0, count=limit)

        total = result.get("total", 0)
        followers = result.get("followers", [])

        print(f"Total followers: {total}")
        print(f"Showing: {len(followers)}")
        print("-" * 40)

        for follower in followers:
            print(f"  - {follower.display_name} (ID: {follower.user_id})")

            # Check activity status
            is_active = client.is_user_active(follower.user_id)
            status = "Online" if is_active else "Offline"
            print(f"    Status: {status}")

    except ZaloKitError as e:
        print(f"Error listing followers: {e}")


def get_all_followers_summary(client: ZaloClient) -> None:
    """Get summary of all followers."""
    print("\n--- All Followers Summary ---")

    try:
        all_followers = client.get_all_followers()

        print(f"Total followers: {len(all_followers)}")

        # Count by tags if available
        tagged = {}
        untagged = 0

        for follower in all_followers:
            profile = client.get_user_profile(follower.user_id)
            if profile.tags:
                for tag in profile.tags:
                    tagged[tag] = tagged.get(tag, 0) + 1
            else:
                untagged += 1

        if tagged:
            print("\nFollowers by tag:")
            for tag, count in sorted(tagged.items()):
                print(f"  - {tag}: {count}")

        print(f"\nUntagged followers: {untagged}")

    except ZaloKitError as e:
        print(f"Error: {e}")


def check_recent_conversations(client: ZaloClient, limit: int = 5) -> None:
    """Check recent conversation partners."""
    print(f"\n--- Recent Conversations (limit: {limit}) ---")

    try:
        result = client.contacts.get_recent_chat(offset=0, count=limit)

        conversations = result.get("data", [])

        if not conversations:
            print("No recent conversations found.")
            return

        print(f"Found {len(conversations)} recent conversations:")

        for conv in conversations:
            user_id = conv.get("user_id", "Unknown")
            last_msg_time = conv.get("last_message_time", "Unknown")
            print(f"  - User: {user_id}")
            print(f"    Last message: {last_msg_time}")

    except ZaloKitError as e:
        print(f"Error: {e}")


def main():
    """Main function to demonstrate activity checking."""
    print("=" * 50)
    print("ZaloKit - User Activity Check Example")
    print("=" * 50)

    # Create client
    client = get_client()
    print(f"\nClient created: {client}")
    print(f"Authenticated: {client.is_authenticated}")

    # Get user ID from environment or use placeholder
    user_id = os.environ.get("ZALO_USER_ID")
    if not user_id:
        print("\nWarning: ZALO_USER_ID not set.")
        print("Set this environment variable to check a specific user.")
        user_id = "placeholder_user_id"

    # Demonstrate features
    check_user_profile(client, user_id)
    check_user_active(client, user_id)

    # List followers
    list_followers(client, limit=5)

    # Check recent conversations
    check_recent_conversations(client, limit=5)

    print("\n" + "=" * 50)
    print("Example complete!")


if __name__ == "__main__":
    main()
