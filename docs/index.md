# ZaloKit

A powerful and easy-to-use Python SDK for the Zalo API.

## Overview

ZaloKit provides a clean, Pythonic interface for interacting with Zalo's messaging platform. Whether you're building a chatbot, integrating Zalo messaging into your application, or automating communications, ZaloKit makes it simple.

## Features

- **Complete OAuth2 Support**: Full authentication flow with automatic token refresh
- **Messaging API**: Send text, images, files, stickers, and rich templates
- **Contacts Management**: Manage followers, tags, and user profiles
- **Group Operations**: Create groups, manage members, and send group messages
- **Type Hints**: Full type annotation support for better IDE integration
- **Comprehensive Error Handling**: Clear exception hierarchy for easy debugging
- **Built-in Logging**: Debug your applications with detailed logging

## Quick Example

```python
from zalokit import ZaloClient

# Initialize client
client = ZaloClient(
    app_id="your_app_id",
    app_secret="your_app_secret",
    access_token="your_access_token"
)

# Send a message
response = client.send_message(
    recipient_id="user_id",
    text="Hello from ZaloKit!"
)

if response.success:
    print(f"Message sent! ID: {response.message_id}")
```

## Installation

```bash
pip install zalokit
```

## Why ZaloKit?

### Simple and Intuitive

ZaloKit is designed to be easy to use. Common operations can be done in just a few lines of code.

### Production Ready

With comprehensive error handling, automatic token refresh, and rate limiting support, ZaloKit is ready for production use.

### Well Documented

Every method is documented with clear examples and type hints.

### Actively Maintained

ZaloKit is actively maintained and keeps up with the latest Zalo API changes.

## Getting Started

1. [Install ZaloKit](quickstart.md#installation)
2. [Set up authentication](quickstart.md#authentication)
3. [Send your first message](quickstart.md#sending-messages)

## Getting Help

- [GitHub Issues](https://github.com/jvunder/ZaloKit/issues)
- [Documentation](https://jvunder.github.io/ZaloKit/)

## License

ZaloKit is released under the MIT License. See [LICENSE](https://github.com/jvunder/ZaloKit/blob/main/LICENSE) for details.
