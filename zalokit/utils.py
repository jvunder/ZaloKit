"""
ZaloKit Utilities Module.

This module provides utility functions and helpers used throughout the SDK.
"""

import hashlib
import hmac
import json
import logging
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from functools import wraps

logger = logging.getLogger(__name__)


def generate_request_id() -> str:
    """Generate a unique request ID for tracking API calls."""
    return str(uuid.uuid4())


def get_timestamp() -> int:
    """Get current Unix timestamp in milliseconds."""
    return int(time.time() * 1000)


def get_iso_timestamp() -> str:
    """Get current timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def parse_timestamp(timestamp: Union[int, str]) -> datetime:
    """
    Parse a timestamp into a datetime object.

    Args:
        timestamp: Unix timestamp (milliseconds) or ISO 8601 string

    Returns:
        datetime object in UTC
    """
    if isinstance(timestamp, int):
        # Assume milliseconds
        return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    elif isinstance(timestamp, str):
        # Try ISO format
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    else:
        raise ValueError(f"Invalid timestamp format: {timestamp}")


def validate_phone_number(phone: str) -> bool:
    """
    Validate Vietnamese phone number format.

    Args:
        phone: Phone number string

    Returns:
        True if valid, False otherwise
    """
    # Remove spaces, dashes, and dots
    cleaned = re.sub(r"[\s\-\.]", "", phone)

    # Vietnamese phone patterns
    patterns = [
        r"^0[3589]\d{8}$",  # Mobile: 03x, 05x, 08x, 09x
        r"^84[3589]\d{8}$",  # With country code (84)
        r"^\+84[3589]\d{8}$",  # With +84
    ]

    return any(re.match(pattern, cleaned) for pattern in patterns)


def normalize_phone_number(phone: str, country_code: str = "84") -> str:
    """
    Normalize phone number to standard format.

    Args:
        phone: Phone number string
        country_code: Country code (default: 84 for Vietnam)

    Returns:
        Normalized phone number
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r"[^\d+]", "", phone)

    # Remove leading + if present
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]

    # Remove country code if present
    if cleaned.startswith(country_code):
        cleaned = "0" + cleaned[len(country_code) :]

    return cleaned


def generate_signature(
    data: Union[str, bytes], secret_key: str, algorithm: str = "sha256"
) -> str:
    """
    Generate HMAC signature for data.

    Args:
        data: Data to sign
        secret_key: Secret key for signing
        algorithm: Hash algorithm (default: sha256)

    Returns:
        Hex-encoded signature
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    secret = secret_key.encode("utf-8")
    hash_func = getattr(hashlib, algorithm)
    signature = hmac.new(secret, data, hash_func)

    return signature.hexdigest()


def verify_signature(
    data: Union[str, bytes],
    signature: str,
    secret_key: str,
    algorithm: str = "sha256",
) -> bool:
    """
    Verify HMAC signature.

    Args:
        data: Original data
        signature: Signature to verify
        secret_key: Secret key used for signing
        algorithm: Hash algorithm (default: sha256)

    Returns:
        True if signature is valid, False otherwise
    """
    expected = generate_signature(data, secret_key, algorithm)
    return hmac.compare_digest(expected, signature)


def sanitize_message(message: str, max_length: int = 2000) -> str:
    """
    Sanitize and truncate message content.

    Args:
        message: Original message
        max_length: Maximum allowed length

    Returns:
        Sanitized message
    """
    # Remove null bytes
    message = message.replace("\x00", "")

    # Normalize whitespace
    message = " ".join(message.split())

    # Truncate if necessary
    if len(message) > max_length:
        message = message[: max_length - 3] + "..."

    return message


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        items: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}"
                        )
                        raise

                    delay = min(
                        base_delay * (exponential_base ** (retries - 1)), max_delay
                    )
                    logger.warning(
                        f"Retry {retries}/{max_retries} for {func.__name__} "
                        f"after {delay:.2f}s. Error: {e}"
                    )
                    time.sleep(delay)

        return wrapper

    return decorator


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def safe_json_loads(data: Union[str, bytes], default: Any = None) -> Any:
    """
    Safely parse JSON data.

    Args:
        data: JSON string or bytes
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    try:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data, showing only first and last few characters.

    Args:
        data: Sensitive data string
        visible_chars: Number of characters to show at each end

    Returns:
        Masked string
    """
    if len(data) <= visible_chars * 2:
        return "*" * len(data)

    return data[:visible_chars] + "*" * (len(data) - visible_chars * 2) + data[-visible_chars:]


class RateLimiter:
    """Simple rate limiter implementation using token bucket algorithm."""

    def __init__(self, rate: float, capacity: int):
        """
        Initialize rate limiter.

        Args:
            rate: Tokens per second
            capacity: Maximum tokens (burst capacity)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()

    def acquire(self, tokens: int = 1) -> bool:
        """
        Attempt to acquire tokens.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens acquired, False otherwise
        """
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def wait_for_token(self, tokens: int = 1) -> float:
        """
        Wait until tokens are available.

        Args:
            tokens: Number of tokens needed

        Returns:
            Time waited in seconds
        """
        start = time.time()
        while not self.acquire(tokens):
            time.sleep(0.1)
        return time.time() - start


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Setup logging for ZaloKit.

    Args:
        level: Logging level
        format_string: Custom format string
        log_file: Optional log file path

    Returns:
        Configured logger
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)

    # Get ZaloKit logger
    zalokit_logger = logging.getLogger("zalokit")
    zalokit_logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    zalokit_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        zalokit_logger.addHandler(file_handler)

    return zalokit_logger
