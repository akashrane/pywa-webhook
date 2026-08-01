import asyncio

import pytest

from pywa_webhook import WhatsAppWebhook, parse_payload


def test_verifies_challenge():
    webhook = WhatsAppWebhook(
        verify_token="verify-me",
        verify_signatures=False,
    )

    result = webhook.verify_challenge(
        mode="subscribe",
        token="verify-me",
        challenge="12345",
    )

    assert result == "12345"


def test_rejects_wrong_verification_token():
    webhook = WhatsAppWebhook(
        verify_token="verify-me",
        verify_signatures=False,
    )

    with pytest.raises(PermissionError):
        webhook.verify_challenge(
            mode="subscribe",
            token="wrong",
            challenge="12345",
        )


def test_dispatches_message(text_payload):
    webhook = WhatsAppWebhook(
        verify_token="verify-me",
        verify_signatures=False,
    )
    received = []

    @webhook.on_message
    def handler(message):
        received.append(message.text)

    asyncio.run(webhook.dispatch(parse_payload(text_payload)))

    assert received == ["Hello from WhatsApp"]
