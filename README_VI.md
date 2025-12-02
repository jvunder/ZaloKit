# ZaloKit

[![PyPI version](https://badge.fury.io/py/zalokit.svg)](https://badge.fury.io/py/zalokit)
[![Python Version](https://img.shields.io/pypi/pyversions/zalokit.svg)](https://pypi.org/project/zalokit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/jvunder/ZaloKit/actions/workflows/ci.yml/badge.svg)](https://github.com/jvunder/ZaloKit/actions/workflows/ci.yml)

SDK Python mạnh mẽ và dễ sử dụng cho Zalo API. ZaloKit cung cấp giao diện sạch sẽ để gửi tin nhắn, quản lý danh bạ, xử lý nhóm và nhiều hơn nữa.

[English](README.md)

## Tính năng

- **Xác thực**: Luồng OAuth2 hoàn chỉnh với tự động làm mới token
- **Tin nhắn**: Gửi văn bản, hình ảnh, file, sticker và template phong phú
- **Danh bạ**: Quản lý người theo dõi, tag và hồ sơ người dùng
- **Nhóm**: Tạo nhóm, quản lý thành viên và gửi tin nhắn nhóm
- **Type Safety**: Hỗ trợ type hints đầy đủ cho IDE
- **Xử lý lỗi**: Hệ thống exception toàn diện
- **Logging**: Tích hợp logging để debug

## Cài đặt

### Từ PyPI (Khuyến nghị)

```bash
pip install zalokit
```

### Từ mã nguồn

```bash
git clone https://github.com/jvunder/ZaloKit.git
cd ZaloKit
pip install -e .
```

### Cài đặt cho phát triển

```bash
git clone https://github.com/jvunder/ZaloKit.git
cd ZaloKit
pip install -e ".[dev]"
```

## Bắt đầu nhanh

### 1. Khởi tạo Client

```python
from zalokit import ZaloClient

client = ZaloClient(
    app_id="your_app_id",
    app_secret="your_app_secret"
)
```

### 2. Xác thực

#### Cách A: Luồng OAuth2 (Khuyến nghị)

```python
# Bước 1: Lấy URL xác thực
auth_url = client.get_authorization_url(
    redirect_uri="https://your-app.com/callback"
)
print(f"Truy cập URL này để xác thực: {auth_url}")

# Bước 2: Sau khi người dùng xác thực, đổi code lấy token
token = client.authenticate(code="authorization_code_from_callback")
```

#### Cách B: Thiết lập Token trực tiếp

```python
# Nếu bạn đã có access token
client.set_access_token(
    access_token="your_access_token",
    refresh_token="your_refresh_token"  # Tùy chọn
)
```

### 3. Gửi tin nhắn

```python
# Gửi tin nhắn văn bản
response = client.send_message(
    recipient_id="user_id",
    text="Xin chào từ ZaloKit!"
)

if response.success:
    print(f"Tin nhắn đã gửi! ID: {response.message_id}")
else:
    print(f"Thất bại: {response.error}")

# Gửi hình ảnh
client.send_image(
    recipient_id="user_id",
    image_path="/path/to/image.jpg"
)

# Gửi file
client.send_file(
    recipient_id="user_id",
    file_path="/path/to/document.pdf"
)
```

### 4. Quản lý danh bạ

```python
# Lấy hồ sơ người dùng
profile = client.get_user_profile("user_id")
print(f"Tên: {profile.display_name}")

# Lấy tất cả người theo dõi
followers = client.get_all_followers()
for follower in followers:
    print(f"Người theo dõi: {follower.display_name}")

# Gán tag cho người dùng
client.tag_user("user_id", "VIP")
```

### 5. Làm việc với nhóm

```python
# Tạo nhóm
group = client.create_group(
    name="Nhóm của tôi",
    member_ids=["user1", "user2", "user3"]
)

# Gửi tin nhắn nhóm
client.send_group_message(group.group_id, "Xin chào mọi người!")

# Lấy tất cả nhóm
groups = client.get_all_groups()
for g in groups:
    print(f"Nhóm: {g.name} ({g.member_count} thành viên)")
```

## Sử dụng nâng cao

### Quản lý Token

```python
from zalokit import ZaloClient

def on_token_refresh(token_info):
    """Được gọi khi token tự động làm mới"""
    print(f"Token mới: {token_info.access_token}")
    # Lưu vào database, v.v.

client = ZaloClient(
    app_id="your_app_id",
    app_secret="your_app_secret",
    token_storage_path="./tokens.json",  # Tự động lưu token
    on_token_refresh=on_token_refresh
)
```

### Xử lý lỗi

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
    client.send_message("user_id", "Xin chào!")
except AuthenticationError as e:
    print(f"Xác thực thất bại: {e}")
except RateLimitError as e:
    print(f"Vượt giới hạn. Thử lại sau {e.retry_after} giây")
except MessageError as e:
    print(f"Gửi tin thất bại cho {e.recipient_id}: {e}")
except APIError as e:
    print(f"Lỗi API [{e.error_code}]: {e}")
```

### Gửi tin nhắn hàng loạt

```python
recipient_ids = ["user1", "user2", "user3"]
results = client.broadcast_message(recipient_ids, "Xin chào mọi người!")

for result in results:
    if result.success:
        print(f"Đã gửi: {result.message_id}")
    else:
        print(f"Thất bại: {result.error}")
```

### Context Manager

```python
with ZaloClient(app_id="...", app_secret="...") as client:
    client.set_access_token("token")
    client.send_message("user_id", "Xin chào!")
# Tài nguyên tự động được giải phóng
```

## Tham khảo API

### ZaloClient

| Phương thức | Mô tả |
|-------------|-------|
| `send_message(recipient_id, text)` | Gửi tin nhắn văn bản |
| `send_image(recipient_id, image_path)` | Gửi hình ảnh |
| `send_file(recipient_id, file_path)` | Gửi file |
| `send_sticker(recipient_id, sticker_id)` | Gửi sticker |
| `send_link(recipient_id, url, ...)` | Gửi preview link |
| `broadcast_message(recipient_ids, text)` | Gửi cho nhiều người |
| `get_user_profile(user_id)` | Lấy hồ sơ người dùng |
| `get_followers(offset, count)` | Lấy danh sách người theo dõi |
| `tag_user(user_id, tag_name)` | Gán tag cho người dùng |
| `create_group(name, member_ids)` | Tạo nhóm mới |
| `send_group_message(group_id, text)` | Gửi tin nhắn nhóm |

### Exceptions

| Exception | Mô tả |
|-----------|-------|
| `ZaloKitError` | Exception cơ sở |
| `AuthenticationError` | Xác thực thất bại |
| `TokenExpiredError` | Token đã hết hạn |
| `APIError` | Yêu cầu API thất bại |
| `RateLimitError` | Vượt giới hạn tần suất |
| `ValidationError` | Lỗi xác thực đầu vào |
| `MessageError` | Gửi tin nhắn thất bại |
| `GroupError` | Thao tác nhóm thất bại |
| `ContactError` | Thao tác danh bạ thất bại |

## Cấu hình

### Biến môi trường

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

## Yêu cầu

- Python 3.8+
- requests
- websocket-client
- cryptography
- pydantic

## Đóng góp

Chúng tôi hoan nghênh đóng góp! Hãy thoải mái gửi Pull Request.

1. Fork repository
2. Tạo nhánh tính năng (`git checkout -b feature/tinh-nang-moi`)
3. Commit thay đổi (`git commit -m 'Thêm tính năng mới'`)
4. Push lên nhánh (`git push origin feature/tinh-nang-moi`)
5. Mở Pull Request

## Giấy phép

Dự án này được cấp phép theo Giấy phép MIT - xem file [LICENSE](LICENSE) để biết chi tiết.

## Liên kết

- [Tài liệu](https://jvunder.github.io/ZaloKit/)
- [PyPI Package](https://pypi.org/project/zalokit/)
- [GitHub Repository](https://github.com/jvunder/ZaloKit)
- [Báo cáo lỗi](https://github.com/jvunder/ZaloKit/issues)
- [Zalo Developers](https://developers.zalo.me/)

## Lời cảm ơn

- Cảm ơn đội ngũ Zalo đã cung cấp API
- Lấy cảm hứng từ các SDK tương tự cho các nền tảng nhắn tin khác
