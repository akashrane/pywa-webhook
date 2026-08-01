import pytest

from pywa_webhook import InvalidPayloadError, parse_payload


def test_parses_text_message(text_payload):
    events = parse_payload(text_payload)

    assert len(events) == 1
    assert events[0].kind == "message"
    assert events[0].message is not None
    assert events[0].message.sender == "15557654321"
    assert events[0].message.recipient == "15551234567"
    assert events[0].message.profile_name == "Ada"
    assert events[0].message.text == "Hello from WhatsApp"


def test_rejects_non_whatsapp_payload():
    with pytest.raises(InvalidPayloadError):
        parse_payload({"object": "page"})
