from __future__ import annotations
import base64, hashlib, hmac, os

PIN_ITERATIONS = 210_000

def validate_pin_format(pin: str) -> str:
    if not isinstance(pin, str) or len(pin) != 4 or not pin.isascii() or not pin.isdigit():
        raise ValueError("PIN_MUST_BE_FOUR_DIGITS")
    return pin

def hash_pin(pin: str, *, iterations: int = PIN_ITERATIONS, salt: bytes | None = None) -> str:
    validate_pin_format(pin)
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("ascii"), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )

def verify_pin(pin: str, encoded: str) -> bool:
    try:
        validate_pin_format(pin)
        algo, iterations, salt_b64, digest_b64 = encoded.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", pin.encode("ascii"), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False
