import pytest


@pytest.fixture
def text_payload():
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "business-account-id",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15551234567",
                                "phone_number_id": "phone-number-id",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Ada"},
                                    "wa_id": "15557654321",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "15557654321",
                                    "id": "wamid.message-id",
                                    "timestamp": "1735689600",
                                    "text": {"body": "Hello from WhatsApp"},
                                    "type": "text",
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }
