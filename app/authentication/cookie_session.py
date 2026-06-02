import hashlib
from typing import Any

from flask.sessions import SecureCookieSessionInterface


class SHA256SecureCookieSessionInterface(SecureCookieSessionInterface):
    @staticmethod
    def digest_method(data: bytes = b"") -> Any:
        return hashlib.sha256(data)
