#!/usr/bin/env python3
"""
Example: Simple Zalo Bot using ZaloKit.

This script demonstrates how to build a simple bot that responds
to messages and commands using the ZaloKit SDK.

Usage:
    python bot_example.py

Make sure to set environment variables:
    - ZALO_APP_ID
    - ZALO_APP_SECRET
    - ZALO_ACCESS_TOKEN

Note: This is a simplified example. For a production bot, you would
typically use webhooks to receive messages in real-time.
"""

import os
import sys
import time
from typing import Callable, Dict, Optional

from zalokit import ZaloClient
from zalokit.exceptions import ZaloKitError


class ZaloBot:
    """
    A simple Zalo bot implementation.

    This bot demonstrates:
    - Command handling
    - Auto-responses
    - User tracking
    - Message logging
    """

    def __init__(self, client: ZaloClient):
        """Initialize the bot with a ZaloClient."""
        self.client = client
        self.commands: Dict[str, Callable] = {}
        self.known_users: Dict[str, str] = {}  # user_id -> display_name
        self.message_count = 0

        # Register default commands
        self._register_default_commands()

    def _register_default_commands(self) -> None:
        """Register default bot commands."""
        self.register_command("help", self.cmd_help, "Show available commands")
        self.register_command("ping", self.cmd_ping, "Check if bot is alive")
        self.register_command("info", self.cmd_info, "Get bot information")
        self.register_command("echo", self.cmd_echo, "Echo your message")
        self.register_command("profile", self.cmd_profile, "Get your profile info")

    def register_command(
        self,
        name: str,
        handler: Callable,
        description: str = "",
    ) -> None:
        """Register a command handler."""
        self.commands[name.lower()] = {
            "handler": handler,
            "description": description,
        }

    def cmd_help(self, user_id: str, args: str) -> str:
        """Show available commands."""
        lines = ["Available commands:"]
        for name, info in self.commands.items():
            desc = info.get("description", "No description")
            lines.append(f"  /{name} - {desc}")
        return "\n".join(lines)

    def cmd_ping(self, user_id: str, args: str) -> str:
        """Check if bot is alive."""
        return "Pong! Bot is running."

    def cmd_info(self, user_id: str, args: str) -> str:
        """Get bot information."""
        return (
            "ZaloKit Demo Bot\n"
            f"Messages processed: {self.message_count}\n"
            f"Known users: {len(self.known_users)}\n"
            f"Commands available: {len(self.commands)}"
        )

    def cmd_echo(self, user_id: str, args: str) -> str:
        """Echo the user's message."""
        if not args:
            return "Usage: /echo <message>"
        return f"You said: {args}"

    def cmd_profile(self, user_id: str, args: str) -> str:
        """Get user's profile information."""
        try:
            profile = self.client.get_user_profile(user_id)
            return (
                f"Your Profile:\n"
                f"  Name: {profile.display_name}\n"
                f"  ID: {profile.user_id}\n"
                f"  Gender: {profile.gender.value}\n"
                f"  Follower: {'Yes' if profile.is_follower else 'No'}"
            )
        except ZaloKitError as e:
            return f"Could not get profile: {e}"

    def process_message(self, user_id: str, message: str) -> Optional[str]:
        """
        Process an incoming message and return a response.

        Args:
            user_id: The sender's user ID
            message: The message content

        Returns:
            Response message or None
        """
        self.message_count += 1
        message = message.strip()

        # Track user
        if user_id not in self.known_users:
            try:
                profile = self.client.get_user_profile(user_id)
                self.known_users[user_id] = profile.display_name
                print(f"New user: {profile.display_name} ({user_id})")
            except ZaloKitError:
                self.known_users[user_id] = "Unknown"

        # Check for commands
        if message.startswith("/"):
            return self._handle_command(user_id, message)

        # Default response for non-commands
        return self._handle_regular_message(user_id, message)

    def _handle_command(self, user_id: str, message: str) -> str:
        """Handle a command message."""
        parts = message[1:].split(maxsplit=1)  # Remove leading /
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if command in self.commands:
            handler = self.commands[command]["handler"]
            return handler(user_id, args)
        else:
            return f"Unknown command: /{command}\nType /help for available commands."

    def _handle_regular_message(self, user_id: str, message: str) -> str:
        """Handle a regular (non-command) message."""
        # Keyword-based responses
        message_lower = message.lower()

        if any(word in message_lower for word in ["hello", "hi", "hey", "xin chào"]):
            name = self.known_users.get(user_id, "there")
            return f"Hello {name}! How can I help you today?"

        if any(word in message_lower for word in ["thanks", "thank you", "cảm ơn"]):
            return "You're welcome! Happy to help!"

        if any(word in message_lower for word in ["bye", "goodbye", "tạm biệt"]):
            return "Goodbye! Have a great day!"

        # Default response
        return (
            "I received your message. Type /help to see what I can do!\n"
            "Or try saying 'hello' to start a conversation."
        )

    def send_response(self, user_id: str, response: str) -> bool:
        """Send a response message to a user."""
        try:
            result = self.client.send_message(user_id, response)
            return result.success
        except ZaloKitError as e:
            print(f"Error sending response: {e}")
            return False

    def run_interactive(self) -> None:
        """
        Run the bot in interactive mode (for testing).

        This simulates receiving messages from a user.
        """
        print("\n" + "=" * 50)
        print("ZaloKit Demo Bot - Interactive Mode")
        print("=" * 50)
        print("\nThis is a simulation mode for testing.")
        print("Enter messages as if you were a user.")
        print("Type 'quit' to exit.\n")

        test_user_id = "test_user_001"

        while True:
            try:
                user_input = input(f"[User {test_user_id}]: ").strip()

                if user_input.lower() == "quit":
                    print("Goodbye!")
                    break

                if not user_input:
                    continue

                response = self.process_message(test_user_id, user_input)

                if response:
                    print(f"[Bot]: {response}")
                    print()

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                break


def get_client() -> ZaloClient:
    """Create and configure ZaloClient from environment variables."""
    app_id = os.environ.get("ZALO_APP_ID")
    app_secret = os.environ.get("ZALO_APP_SECRET")
    access_token = os.environ.get("ZALO_ACCESS_TOKEN")

    if not all([app_id, app_secret]):
        print("Warning: ZALO_APP_ID or ZALO_APP_SECRET not set.")
        print("Running in demo mode with mock client.")

        # Create a mock client for demo purposes
        return ZaloClient(
            app_id="demo_app_id",
            app_secret="demo_app_secret",
        )

    return ZaloClient(
        app_id=app_id,
        app_secret=app_secret,
        access_token=access_token,
    )


def main():
    """Main function to run the bot."""
    print("=" * 50)
    print("ZaloKit - Bot Example")
    print("=" * 50)

    # Create client
    client = get_client()

    # Create and run bot
    bot = ZaloBot(client)

    # Add custom command
    def cmd_time(user_id: str, args: str) -> str:
        """Get current server time."""
        from datetime import datetime
        return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    bot.register_command("time", cmd_time, "Get current server time")

    # Run in interactive mode for testing
    bot.run_interactive()


if __name__ == "__main__":
    main()
