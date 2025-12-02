# Quick Start Guide

This guide will help you get started with ZaloKit in just a few minutes.

## Prerequisites

Before you begin, make sure you have:

- Python 3.8 or higher
- A Zalo Official Account (OA)
- App credentials from [Zalo Developers](https://developers.zalo.me/)

## Installation

Install ZaloKit using pip:

```bash
pip install zalokit
```

Or install from source:

```bash
git clone https://github.com/jvunder/ZaloKit.git
cd ZaloKit
pip install -e .
```

## Getting Your Credentials

1. Go to [Zalo Developers Console](https://developers.zalo.me/)
2. Create a new application or select an existing one
3. Note down your **App ID** and **App Secret**
4. Configure your OAuth redirect URI

## Authentication

### Option 1: OAuth2 Flow (Recommended)

```python
from zalokit import ZaloClient

# Initialize client
client = ZaloClient(
    app_id="your_app_id",
    app_secret="your_app_secret",
    redirect_uri="https://your-app.com/callback"
)

# Step 1: Get authorization URL
auth_url = client.get_authorization_url(state="random_state")
print(f"Visit this URL: {auth_url}")

# Step 2: User authorizes and you receive a code at your redirect URI

# Step 3: Exchange code for token
token = client.authenticate(code="code_from_callback")
print(f"Access token: {token.access_token}")
```

### Option 2: Direct Token Setup

If you already have an access token:

```python
from zalokit import ZaloClient

client = ZaloClient(
    app_id="your_app_id",
    app_secret="your_app_secret",
    access_token="your_access_token",
    refresh_token="your_refresh_token"  # Optional but recommended
)
```

## Sending Messages

### Text Message

```python
response = client.send_message(
    recipient_id="user_id",
    text="Hello from ZaloKit!"
)

if response.success:
    print(f"Sent! Message ID: {response.message_id}")
else:
    print(f"Failed: {response.error}")
```

### Image Message

```python
# From local file
response = client.send_image(
    recipient_id="user_id",
    image_path="/path/to/image.jpg"
)

# From URL
response = client.send_image(
    recipient_id="user_id",
    image_url="https://example.com/image.jpg"
)
```

### File Attachment

```python
response = client.send_file(
    recipient_id="user_id",
    file_path="/path/to/document.pdf"
)
```

## Getting User Information

```python
# Get user profile
profile = client.get_user_profile("user_id")
print(f"Name: {profile.display_name}")
print(f"Avatar: {profile.avatar}")

# Check if user is active
is_active = client.is_user_active("user_id")
print(f"Online: {is_active}")
```

## Managing Followers

```python
# Get followers list
result = client.get_followers(offset=0, count=50)
for follower in result["followers"]:
    print(f"- {follower.display_name}")

# Get all followers (with pagination)
all_followers = client.get_all_followers()
print(f"Total followers: {len(all_followers)}")

# Tag a user
client.tag_user("user_id", "VIP")
```

## Working with Groups

```python
# Create a group
group = client.create_group(
    name="My Group",
    member_ids=["user1", "user2", "user3"]
)

# Send group message
client.send_group_message(group.group_id, "Hello everyone!")

# Add members
client.add_group_members(group.group_id, ["user4", "user5"])
```

## Error Handling

```python
from zalokit import ZaloClient
from zalokit.exceptions import (
    AuthenticationError,
    RateLimitError,
    MessageError,
    ZaloKitError
)

client = ZaloClient(app_id="...", app_secret="...")

try:
    client.send_message("user_id", "Hello!")
except AuthenticationError:
    print("Authentication failed - check your credentials")
except RateLimitError as e:
    print(f"Rate limited - retry after {e.retry_after} seconds")
except MessageError as e:
    print(f"Message failed: {e}")
except ZaloKitError as e:
    print(f"General error: {e}")
```

## Environment Variables

For security, store credentials in environment variables:

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

## Token Persistence

Save tokens automatically:

```python
client = ZaloClient(
    app_id="your_app_id",
    app_secret="your_app_secret",
    token_storage_path="./tokens.json"  # Tokens saved/loaded automatically
)
```

## Next Steps

- Read the [Messaging Guide](messaging.md) for advanced messaging features
- Learn about [Contacts Management](contacts.md)
- Explore [Group Operations](groups.md)
- Check out [Example Scripts](examples/basic.md)
