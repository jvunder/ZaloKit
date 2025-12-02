# ZaloKit

[![PyPI version](https://badge.fury.io/py/zalokit.svg)](https://badge.fury.io/py/zalokit)
[![Python Version](https://img.shields.io/pypi/pyversions/zalokit.svg)](https://pypi.org/project/zalokit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/jvunder/ZaloKit/actions/workflows/ci.yml/badge.svg)](https://github.com/jvunder/ZaloKit/actions/workflows/ci.yml)

A powerful and easy-to-use Python SDK for the Zalo API. ZaloKit provides a clean interface for sending messages, managing contacts, handling groups, and more.

[Tiếng Việt](README_VI.md)

## Features

- **Authentication**: Complete OAuth2 flow with automatic token refresh
- **Messaging**: Send text, images, files, stickers, and rich templates
- **Contacts**: Manage followers, tags, and user profiles
- **Groups**: Create groups, manage members, and send group messages
- **Type Safety**: Full type hints for better IDE support
- **Error Handling**: Comprehensive exception hierarchy
- **Logging**: Built-in logging for debugging

## Installation

### From PyPI (Recommended)

```bash
pip install zalokit
```

### From Source

```bash
git clone https://github.com/jvunder/ZaloKit.git
cd ZaloKit
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/jvunder/ZaloKit.git
cd ZaloKit
pip install -e ".[dev]"
```

## Quick Start

### 1. Initialize the Client

```python
from zalokit import ZaloClient

client = ZaloClient(
    app_id="your_app_id",
    app_secret="your_app_secret"
)
```

### 2. Authentication

#### Option A: OAuth2 Flow (Recommended)

```python
# Step 1: Get authorization URL
auth_url = client.get_authorization_url(
    redirect_uri="https://your-app.com/callback"
)
print(f"Visit this URL to authorize: {auth_url}")

# Step 2: After user authorizes, exchange code for token
token = client.authenticate(code="authorization_code_from_callback")
```

#### Option B: Direct Token Setup

```python
# If you already have an access token
client.set_access_token(
    access_token="your_access_token",
    refresh_token="your_refresh_token"  # Optional
)
```

### 3. Send Messages

```python
# Send text message
response = client.send_message(
    recipient_id="user_id",
    text="Hello from ZaloKit!"
)

if response.success:
    print(f"Message sent! ID: {response.message_id}")
else:
    print(f"Failed: {response.error}")

# Send image
client.send_image(
    recipient_id="user_id",
    image_path="/path/to/image.jpg"
)

# Send file
client.send_file(
    recipient_id="user_id",
    file_path="/path/to/document.pdf"
)
```

### 4. Manage Contacts

```python
# Get user profile
profile = client.get_user_profile("user_id")
print(f"Name: {profile.display_name}")

# Get all followers
followers = client.get_all_followers()
for follower in followers:
    print(f"Follower: {follower.display_name}")

# Tag a user
client.tag_user("user_id", "VIP")
```

### 5. Work with Groups

```python
# Create a group
group = client.create_group(
    name="My Group",
    member_ids=["user1", "user2", "user3"]
)

# Send group message
client.send_group_message(group.group_id, "Hello everyone!")

# Get all groups
groups = client.get_all_groups()
for g in groups:
    print(f"Group: {g.name} ({g.member_count} members)")
```

## Advanced Usage

### Token Management

```python
from zalokit import ZaloClient

def on_token_refresh(token_info):
    """Called when token is automatically refreshed"""
    print(f"New token: {token_info.access_token}")
    # Save to database, etc.

client = ZaloClient(
    app_id="your_app_id",
    app_secret="your_app_secret",
    token_storage_path="./tokens.json",  # Auto-save tokens
    on_token_refresh=on_token_refresh
)
```

### Error Handling

```python
from zalokit import ZaloClient
from zalokit.exceptions import (
    AuthenticationError,
    RateLimitError,
    MessageError,
    APIError
)

client = ZaloClient(app_id="...", app_secret="...")

try:
    client.send_message("user_id", "Hello!")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except MessageError as e:
    print(f"Message failed for {e.recipient_id}: {e}")
except APIError as e:
    print(f"API error [{e.error_code}]: {e}")
```

### Broadcast Messages

```python
recipient_ids = ["user1", "user2", "user3"]
results = client.broadcast_message(recipient_ids, "Hello everyone!")

for result in results:
    if result.success:
        print(f"Sent: {result.message_id}")
    else:
        print(f"Failed: {result.error}")
```

### Context Manager

```python
with ZaloClient(app_id="...", app_secret="...") as client:
    client.set_access_token("token")
    client.send_message("user_id", "Hello!")
# Resources automatically cleaned up
```

## API Reference

### ZaloClient

| Method | Description |
|--------|-------------|
| `send_message(recipient_id, text)` | Send text message |
| `send_image(recipient_id, image_path)` | Send image |
| `send_file(recipient_id, file_path)` | Send file |
| `send_sticker(recipient_id, sticker_id)` | Send sticker |
| `send_link(recipient_id, url, ...)` | Send link preview |
| `broadcast_message(recipient_ids, text)` | Send to multiple users |
| `get_user_profile(user_id)` | Get user profile |
| `get_followers(offset, count)` | Get followers list |
| `tag_user(user_id, tag_name)` | Assign tag to user |
| `create_group(name, member_ids)` | Create new group |
| `send_group_message(group_id, text)` | Send group message |

### Exceptions

| Exception | Description |
|-----------|-------------|
| `ZaloKitError` | Base exception |
| `AuthenticationError` | Authentication failed |
| `TokenExpiredError` | Access token expired |
| `APIError` | API request failed |
| `RateLimitError` | Rate limit exceeded |
| `ValidationError` | Input validation failed |
| `MessageError` | Message sending failed |
| `GroupError` | Group operation failed |
| `ContactError` | Contact operation failed |

## Configuration

### Environment Variables

```bash
export ZALO_APP_ID="your_app_id"
export ZALO_APP_SECRET="your_app_secret"
export ZALO_ACCESS_TOKEN="your_access_token"
```

```python
import os
from zalokit import ZaloClient

client = ZaloClient(
    app_id=os.environ["ZALO_APP_ID"],
    app_secret=os.environ["ZALO_APP_SECRET"],
    access_token=os.environ.get("ZALO_ACCESS_TOKEN")
)
```

## Requirements

- Python 3.8+
- requests
- websocket-client
- cryptography
- pydantic

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Documentation](https://jvunder.github.io/ZaloKit/)
- [PyPI Package](https://pypi.org/project/zalokit/)
- [GitHub Repository](https://github.com/jvunder/ZaloKit)
- [Issue Tracker](https://github.com/jvunder/ZaloKit/issues)
- [Zalo Developers](https://developers.zalo.me/)

## Acknowledgments

- Thanks to the Zalo team for providing the API
- Inspired by similar SDKs for other messaging platforms
