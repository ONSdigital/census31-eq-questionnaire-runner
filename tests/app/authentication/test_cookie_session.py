import hashlib

from app.authentication.cookie_session import SHA256SecureCookieSessionInterface


def test_digest_method_returns_sha256_hash_object():
    result = SHA256SecureCookieSessionInterface.digest_method(b"test-data")
    assert result.name == hashlib.sha256(b"test-data").name


def test_digest_method_default_empty_bytes():
    result = SHA256SecureCookieSessionInterface.digest_method()
    assert result.digest_size == hashlib.sha256().digest_size
