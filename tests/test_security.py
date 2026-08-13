import hashlib
import hmac

import pytest

from wa_eventkit import InvalidSignatureError, verify_signature


def test_accepts_valid_signature():
    body = b'{"object":"whatsapp_business_account"}'
    secret = "app-secret"
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    assert verify_signature(body, f"sha256={digest}", secret)


def test_rejects_invalid_signature():
    with pytest.raises(InvalidSignatureError):
        verify_signature(b"payload", "sha256=incorrect", "app-secret")
