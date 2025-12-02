#!/usr/bin/env python3
"""
ZaloKit Interactive Bot Demo
A production-ready bot for Zalo using ZaloKit SDK
"""

from zalokit import ZaloClient
from zalokit.exceptions import ZaloKitError
import os
import time
from datetime import datetime
from typing import Dict, Callable, Optional


class InteractiveZaloBot:
    """Interactive Zalo Bot with command system and auto-responses"""

    def __init__(self, client: ZaloClient):
        self.client = client
        self.commands: Dict[str, Callable] = {}
        self.users: Dict[str, Dict] = {}
        self.stats: Dict[str, int] = {"messages": 0, "commands": 0}
        self._register_commands()

    def _register_commands(self):
        """Register bot commands"""
        self.register_command("help", self.cmd_help)
        self.register_command("ping", self.cmd_ping)
        self.register_command("info", self.cmd_info)
        self.register_command("echo", self.cmd_echo)
        self.register_command("profile", self.cmd_profile)
        self.register_command("time", self.cmd_time)
        self.register_command("weather", self.cmd_weather)
        self.register_command("calc", self.cmd_calc)

    def register_command(self, name: str, handler: Callable):
        """Register a command handler"""
        self.commands[name.lower()] = handler

    # Command Handlers
    def cmd_help(self, user_id: str, args: str) -> str:
        """Show available commands"""
        lines = ["📋 Available Commands:"]
        commands_info = {
            "help": "Show this help message",
            "ping": "Check bot status",
            "info": "Show bot information",
            "echo": "Echo your message",
            "profile": "Get your profile",
            "time": "Show current time",
            "weather": "Get weather info (mock)",
            "calc": "Calculate expression"
        }
        for cmd, desc in commands_info.items():
            lines.append(f"  /{cmd} - {desc}")
        return "\n".join(lines)

    def cmd_ping(self, user_id: str, args: str) -> str:
        """Check bot status"""
        return "🏓 Pong! Bot is running!"

    def cmd_info(self, user_id: str, args: str) -> str:
        """Bot information"""
        return (
            f"🤖 ZaloKit Demo Bot\n"
            f"Version: 1.0.0\n"
            f"Status: Running ✅\n"
            f"Users: {len(self.users)}\n"
            f"Commands: {len(self.commands)}\n"
            f"Messages: {self.stats['messages']}\n"
            f"Commands executed: {self.stats['commands']}"
        )

    def cmd_echo(self, user_id: str, args: str) -> str:
        """Echo user message"""
        if not args:
            return "Usage: /echo <message>"
        return f"🔊 {args}"

    def cmd_profile(self, user_id: str, args: str) -> str:
        """Get user profile"""
        try:
            profile = self.client.get_user_profile(user_id)
            return (
                f"👤 Profile:\n"
                f"Name: {profile.display_name}\n"
                f"ID: {profile.user_id}"
            )
        except ZaloKitError as e:
            return f"❌ Could not retrieve profile: {e}"
        except Exception:
            return "❌ Error retrieving profile (demo mode)"

    def cmd_time(self, user_id: str, args: str) -> str:
        """Current time"""
        now = datetime.now()
        return (
            f"⏰ Current Time\n"
            f"Time: {now.strftime('%H:%M:%S')}\n"
            f"Date: {now.strftime('%Y-%m-%d')}\n"
            f"Day: {now.strftime('%A')}"
        )

    def cmd_weather(self, user_id: str, args: str) -> str:
        """Weather info (mock)"""
        city = args.strip() if args else "Hanoi"

        # Mock weather data
        weather_data = {
            "hanoi": ("Hanoi", "28°C", "Sunny ☀️"),
            "saigon": ("Ho Chi Minh", "32°C", "Partly Cloudy 🌤️"),
            "danang": ("Da Nang", "30°C", "Cloudy ☁️"),
        }

        city_lower = city.lower()
        if city_lower in weather_data:
            name, temp, condition = weather_data[city_lower]
            return f"🌤️ Weather in {name}\n{temp}, {condition}"

        return f"🌤️ Weather in {city}\n28°C, Sunny ☀️ (mock data)"

    def cmd_calc(self, user_id: str, args: str) -> str:
        """Simple calculator"""
        if not args:
            return "Usage: /calc <expression>\nExample: /calc 5*10+2"

        try:
            # Safe evaluation - only allow numbers and basic operators
            allowed_chars = set("0123456789+-*/() .")
            if not all(c in allowed_chars for c in args):
                return "❌ Only numbers and operators (+, -, *, /, parentheses) are allowed"

            result = eval(args)
            return f"🧮 {args} = {result}"
        except ZeroDivisionError:
            return "❌ Error: Division by zero"
        except Exception as e:
            return f"❌ Invalid expression: {e}"

    def process_message(self, user_id: str, message: str) -> Optional[str]:
        """Process incoming message"""
        message = message.strip()

        if not message:
            return None

        # Track user
        if user_id not in self.users:
            self.users[user_id] = {"name": "User", "count": 0, "first_seen": datetime.now()}
        self.users[user_id]["count"] += 1
        self.stats["messages"] += 1

        # Handle commands
        if message.startswith("/"):
            self.stats["commands"] += 1
            return self._handle_command(user_id, message)

        # Handle regular messages
        return self._handle_regular_message(message)

    def _handle_command(self, user_id: str, message: str) -> str:
        """Handle command messages"""
        parts = message[1:].split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd in self.commands:
            try:
                return self.commands[cmd](user_id, args)
            except Exception as e:
                return f"❌ Error executing command: {e}"

        return f"❌ Unknown command: /{cmd}\nType /help to see available commands"

    def _handle_regular_message(self, message: str) -> str:
        """Handle regular text messages with keyword detection"""
        msg_lower = message.lower()

        # Greetings
        if any(word in msg_lower for word in ["hello", "hi", "hey", "xin chào", "chào"]):
            return "👋 Hi there! How can I help?\nType /help to see what I can do!"

        # Thanks
        if any(word in msg_lower for word in ["thanks", "thank you", "cảm ơn", "cám ơn"]):
            return "😊 You're welcome! Happy to help!"

        # Goodbye
        if any(word in msg_lower for word in ["bye", "goodbye", "see you", "tạm biệt"]):
            return "👋 Goodbye! Have a great day!"

        # How are you
        if any(phrase in msg_lower for phrase in ["how are you", "what's up", "bạn khỏe không", "thế nào"]):
            return "🤖 I'm doing great! Thanks for asking.\nHow can I assist you today?"

        # Help requests
        if any(word in msg_lower for word in ["help", "giúp", "hỗ trợ"]):
            return "💡 I can help you with various commands!\nType /help to see all available commands."

        # Default response
        return "💬 I received your message! Type /help to see what I can do!"

    def send_response(self, user_id: str, response: str) -> bool:
        """Send response to user"""
        try:
            result = self.client.send_message(user_id, response)
            return result.success
        except ZaloKitError as e:
            print(f"Error sending message: {e}")
            return False

    def run_interactive(self):
        """Run bot in interactive mode for testing"""
        print("\n" + "="*60)
        print("🤖 ZaloKit Interactive Bot Demo")
        print("="*60)
        print("\n📋 Available Commands:")
        print("  /help     - Show all commands")
        print("  /ping     - Check bot status")
        print("  /profile  - Get your profile")
        print("  /echo     - Echo your message")
        print("  /time     - Show current time")
        print("  /weather  - Get weather info")
        print("  /calc     - Calculate expressions")
        print("  /info     - Bot information")
        print("\n💬 Or just type naturally and I'll respond!")
        print("   Try: 'hello', 'thanks', 'help me', etc.")
        print("\n⌨️  Type 'quit' to exit\n")
        print("="*60 + "\n")

        test_user = "demo_user_001"

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Goodbye! Thanks for trying ZaloKit Bot Demo!")
                    break

                if not user_input:
                    continue

                response = self.process_message(test_user, user_input)
                if response:
                    print(f"Bot: {response}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for trying ZaloKit Bot Demo!")
                break
            except Exception as e:
                print(f"Error: {e}\n")


def main():
    """Main entry point"""
    print("\n🚀 Starting ZaloKit Bot Demo...\n")

    # Setup client
    app_id = os.environ.get("ZALO_APP_ID", "demo")
    app_secret = os.environ.get("ZALO_APP_SECRET", "demo")
    access_token = os.environ.get("ZALO_ACCESS_TOKEN", "demo")

    if app_id == "demo":
        print("⚠️  Running in DEMO mode (no actual Zalo connection)")
        print("   Set environment variables for production use:")
        print("   - ZALO_APP_ID")
        print("   - ZALO_APP_SECRET")
        print("   - ZALO_ACCESS_TOKEN\n")

    client = ZaloClient(
        app_id=app_id,
        app_secret=app_secret,
        access_token=access_token
    )

    # Create and run bot
    bot = InteractiveZaloBot(client)
    bot.run_interactive()


if __name__ == "__main__":
    main()
