"""Meta webhook signature validation."""

import hashlib
import hmac

from .exceptions import InvalidSignatureError


def verify_signature(body: bytes, signature: str | None, app_secret: str) -> bool:
    """Validate a Meta X-Hub-Signature-256 header."""

    if not app_secret:
        raise InvalidSignatureError("An app secret is required.")
    if not signature or not signature.startswith("sha256="):
        raise InvalidSignatureError("Missing or malformed X-Hub-Signature-256.")

    expected = hmac.new(
        app_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    supplied = signature.removeprefix("sha256=")

    if not hmac.compare_digest(expected, supplied):
        raise InvalidSignatureError("Webhook signature does not match.")
    return True
