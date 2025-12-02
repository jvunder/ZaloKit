"""Tests for ZaloKit utilities module."""

import pytest
import time

from zalokit.utils import (
    generate_request_id,
    get_timestamp,
    get_iso_timestamp,
    parse_timestamp,
    validate_phone_number,
    normalize_phone_number,
    generate_signature,
    verify_signature,
    sanitize_message,
    chunk_list,
    format_file_size,
    safe_json_loads,
    mask_sensitive_data,
    RateLimiter,
)


class TestRequestId:
    """Tests for request ID generation."""

    def test_generate_request_id_format(self):
        """Test request ID is valid UUID format."""
        request_id = generate_request_id()

        # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        assert len(request_id) == 36
        assert request_id.count("-") == 4

    def test_generate_request_id_unique(self):
        """Test request IDs are unique."""
        ids = [generate_request_id() for _ in range(100)]

        assert len(set(ids)) == 100


class TestTimestamp:
    """Tests for timestamp functions."""

    def test_get_timestamp(self):
        """Test getting current timestamp."""
        ts = get_timestamp()

        # Should be in milliseconds
        assert ts > 1000000000000
        # Should be close to current time
        assert abs(ts - time.time() * 1000) < 1000

    def test_get_iso_timestamp(self):
        """Test getting ISO timestamp."""
        ts = get_iso_timestamp()

        # Should be ISO format
        assert "T" in ts
        assert len(ts) > 20

    def test_parse_timestamp_int(self):
        """Test parsing integer timestamp."""
        ts = 1700000000000  # In milliseconds
        dt = parse_timestamp(ts)

        assert dt.year == 2023
        assert dt.month == 11

    def test_parse_timestamp_string(self):
        """Test parsing ISO string timestamp."""
        ts = "2023-11-14T12:00:00+00:00"
        dt = parse_timestamp(ts)

        assert dt.year == 2023
        assert dt.month == 11
        assert dt.day == 14

    def test_parse_timestamp_invalid(self):
        """Test parsing invalid timestamp."""
        with pytest.raises(ValueError):
            parse_timestamp([1, 2, 3])


class TestPhoneValidation:
    """Tests for phone number validation."""

    def test_valid_vietnamese_phone_numbers(self):
        """Test valid Vietnamese phone numbers."""
        valid_numbers = [
            "0912345678",
            "0987654321",
            "0362345678",
            "0562345678",
            "0862345678",
            "84912345678",
            "+84912345678",
        ]

        for number in valid_numbers:
            assert validate_phone_number(number) is True, f"Failed for {number}"

    def test_invalid_phone_numbers(self):
        """Test invalid phone numbers."""
        invalid_numbers = [
            "123",
            "0123456789",  # Invalid prefix
            "091234567",   # Too short
            "09123456789", # Too long
            "abcdefghij",
        ]

        for number in invalid_numbers:
            assert validate_phone_number(number) is False, f"Should fail for {number}"

    def test_phone_number_with_formatting(self):
        """Test phone numbers with formatting."""
        assert validate_phone_number("091-234-5678") is True
        assert validate_phone_number("091 234 5678") is True
        assert validate_phone_number("091.234.5678") is True


class TestPhoneNormalization:
    """Tests for phone number normalization."""

    def test_normalize_with_country_code(self):
        """Test normalizing phone with country code."""
        assert normalize_phone_number("84912345678") == "0912345678"
        assert normalize_phone_number("+84912345678") == "0912345678"

    def test_normalize_local_number(self):
        """Test normalizing local number."""
        assert normalize_phone_number("0912345678") == "0912345678"

    def test_normalize_with_formatting(self):
        """Test normalizing formatted number."""
        assert normalize_phone_number("091-234-5678") == "0912345678"
        assert normalize_phone_number("091 234 5678") == "0912345678"


class TestSignature:
    """Tests for signature generation and verification."""

    def test_generate_signature(self):
        """Test signature generation."""
        data = "test_data"
        secret = "secret_key"

        signature = generate_signature(data, secret)

        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex length

    def test_generate_signature_bytes(self):
        """Test signature generation with bytes."""
        data = b"test_data"
        secret = "secret_key"

        signature = generate_signature(data, secret)

        assert isinstance(signature, str)

    def test_verify_signature_valid(self):
        """Test valid signature verification."""
        data = "test_data"
        secret = "secret_key"

        signature = generate_signature(data, secret)

        assert verify_signature(data, signature, secret) is True

    def test_verify_signature_invalid(self):
        """Test invalid signature verification."""
        data = "test_data"
        secret = "secret_key"

        assert verify_signature(data, "invalid_signature", secret) is False

    def test_signature_different_data(self):
        """Test signatures differ for different data."""
        secret = "secret_key"

        sig1 = generate_signature("data1", secret)
        sig2 = generate_signature("data2", secret)

        assert sig1 != sig2


class TestSanitizeMessage:
    """Tests for message sanitization."""

    def test_sanitize_removes_null_bytes(self):
        """Test removal of null bytes."""
        message = "Hello\x00World"

        result = sanitize_message(message)

        assert "\x00" not in result
        assert result == "Hello World"

    def test_sanitize_normalizes_whitespace(self):
        """Test whitespace normalization."""
        message = "Hello    World\n\nTest"

        result = sanitize_message(message)

        assert result == "Hello World Test"

    def test_sanitize_truncates_long_message(self):
        """Test truncation of long messages."""
        message = "A" * 3000

        result = sanitize_message(message, max_length=100)

        assert len(result) == 100
        assert result.endswith("...")

    def test_sanitize_preserves_short_message(self):
        """Test short messages are preserved."""
        message = "Hello World"

        result = sanitize_message(message)

        assert result == "Hello World"


class TestChunkList:
    """Tests for list chunking."""

    def test_chunk_even_split(self):
        """Test chunking with even split."""
        items = [1, 2, 3, 4, 5, 6]

        chunks = chunk_list(items, 2)

        assert chunks == [[1, 2], [3, 4], [5, 6]]

    def test_chunk_uneven_split(self):
        """Test chunking with uneven split."""
        items = [1, 2, 3, 4, 5]

        chunks = chunk_list(items, 2)

        assert chunks == [[1, 2], [3, 4], [5]]

    def test_chunk_larger_than_list(self):
        """Test chunk size larger than list."""
        items = [1, 2, 3]

        chunks = chunk_list(items, 10)

        assert chunks == [[1, 2, 3]]

    def test_chunk_empty_list(self):
        """Test chunking empty list."""
        chunks = chunk_list([], 5)

        assert chunks == []


class TestFormatFileSize:
    """Tests for file size formatting."""

    def test_format_bytes(self):
        """Test formatting bytes."""
        assert format_file_size(500) == "500.00 B"

    def test_format_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_file_size(1536) == "1.50 KB"

    def test_format_megabytes(self):
        """Test formatting megabytes."""
        assert format_file_size(1048576) == "1.00 MB"

    def test_format_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_file_size(1073741824) == "1.00 GB"


class TestSafeJsonLoads:
    """Tests for safe JSON parsing."""

    def test_valid_json_string(self):
        """Test parsing valid JSON string."""
        data = '{"key": "value"}'

        result = safe_json_loads(data)

        assert result == {"key": "value"}

    def test_valid_json_bytes(self):
        """Test parsing valid JSON bytes."""
        data = b'{"key": "value"}'

        result = safe_json_loads(data)

        assert result == {"key": "value"}

    def test_invalid_json(self):
        """Test parsing invalid JSON."""
        data = "not valid json"

        result = safe_json_loads(data, default={})

        assert result == {}

    def test_invalid_json_default_none(self):
        """Test parsing invalid JSON with None default."""
        data = "not valid json"

        result = safe_json_loads(data)

        assert result is None


class TestMaskSensitiveData:
    """Tests for sensitive data masking."""

    def test_mask_long_string(self):
        """Test masking long string."""
        data = "1234567890123456"

        result = mask_sensitive_data(data)

        assert result.startswith("1234")
        assert result.endswith("3456")
        assert "****" in result

    def test_mask_short_string(self):
        """Test masking short string."""
        data = "short"

        result = mask_sensitive_data(data)

        assert result == "*****"

    def test_mask_custom_visible_chars(self):
        """Test masking with custom visible characters."""
        data = "1234567890"

        result = mask_sensitive_data(data, visible_chars=2)

        assert result.startswith("12")
        assert result.endswith("90")


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_acquire_success(self):
        """Test successful token acquisition."""
        limiter = RateLimiter(rate=10.0, capacity=10)

        assert limiter.acquire(1) is True

    def test_acquire_exhausted(self):
        """Test acquisition when tokens exhausted."""
        limiter = RateLimiter(rate=0.0, capacity=2)

        assert limiter.acquire(1) is True
        assert limiter.acquire(1) is True
        assert limiter.acquire(1) is False

    def test_acquire_multiple_tokens(self):
        """Test acquiring multiple tokens."""
        limiter = RateLimiter(rate=10.0, capacity=10)

        assert limiter.acquire(5) is True
        assert limiter.acquire(5) is True
        assert limiter.acquire(1) is False

    def test_tokens_refill(self):
        """Test that tokens refill over time."""
        limiter = RateLimiter(rate=100.0, capacity=10)

        # Exhaust all tokens
        limiter.acquire(10)
        assert limiter.acquire(1) is False

        # Wait a bit for refill
        time.sleep(0.1)

        # Should have some tokens now
        assert limiter.acquire(1) is True
