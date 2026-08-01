# pywa-webhook

A lightweight, framework-friendly Python library for receiving, verifying, and parsing [Meta WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api/) webhooks.

The package is independent of any application or database. It turns Meta's nested webhook payloads into typed Python objects and lets your code decide what to do next.

## Features

- Meta webhook challenge verification
- X-Hub-Signature-256 validation using your Meta App Secret
- Normalized text, media, location, button, interactive, and status events
- Sync and async event handlers
- Framework-neutral parsing and dispatch
- Optional FastAPI adapter
- Zero runtime dependencies for the core package
- Typed package with Python 3.10+ support

## Installation

Until the first PyPI release, install directly from GitHub:

~~~bash
pip install "pywa-webhook[fastapi] @ git+https://github.com/akashrane/pywa-webhook.git"
~~~

For local development:

~~~bash
git clone https://github.com/akashrane/pywa-webhook.git
cd pywa-webhook
python -m venv .venv
pip install -e ".[fastapi,dev]"
~~~

## FastAPI Example

~~~python
import os

from fastapi import FastAPI

from pywa_webhook import WhatsAppWebhook
from pywa_webhook.adapters.fastapi import create_router

webhook = WhatsAppWebhook(
    verify_token=os.environ["WHATSAPP_VERIFY_TOKEN"],
    app_secret=os.environ["WHATSAPP_APP_SECRET"],
)

app = FastAPI()
app.include_router(create_router(webhook))


@webhook.on_message
def print_message(message):
    print(f"Message from {message.sender}: {message.text}")


@webhook.on_status
async def print_status(status):
    print(f"Message {status.id}: {status.status}")
~~~

Run it with:

~~~bash
export WHATSAPP_VERIFY_TOKEN="choose-a-private-verification-token"
export WHATSAPP_APP_SECRET="your-meta-app-secret"
uvicorn examples.fastapi_app:app --host 0.0.0.0 --port 8000
~~~

On PowerShell:

~~~powershell
$env:WHATSAPP_VERIFY_TOKEN = "choose-a-private-verification-token"
$env:WHATSAPP_APP_SECRET = "your-meta-app-secret"
uvicorn examples.fastapi_app:app --host 0.0.0.0 --port 8000
~~~

Your webhook endpoint is:

~~~text
GET  /webhook
POST /webhook
~~~

For local Meta testing, expose port 8000 through an HTTPS tunnel and configure the resulting URL as your Meta callback URL.

## Framework-Neutral Usage

You can use the parser without FastAPI:

~~~python
from pywa_webhook import parse_payload

events = parse_payload(meta_payload)

for event in events:
    if event.kind == "message":
        print(event.message.sender, event.message.text)
~~~

To validate the request signature separately:

~~~python
from pywa_webhook import verify_signature

verify_signature(
    raw_request_body,
    request_headers.get("X-Hub-Signature-256"),
    app_secret,
)
~~~

Signature validation must use the exact raw request bytes received from Meta.

## Message Object

Incoming messages are normalized into a Message dataclass with commonly used fields:

~~~python
message.id
message.sender
message.recipient
message.timestamp
message.type
message.text
message.profile_name
message.phone_number_id
message.media_id
message.caption
message.latitude
message.longitude
message.raw
~~~

The original Meta message object is always available through message.raw.

## Meta Configuration

In the Meta developer dashboard:

1. Create or select a Meta app with WhatsApp enabled.
2. Configure the callback URL as your public HTTPS webhook URL.
3. Enter the same verification token used by WhatsAppWebhook.
4. Subscribe to the messages webhook field.
5. Store your Meta App Secret in an environment variable or secret manager.

The verification token is chosen by you. The App Secret comes from your Meta app settings. Do not commit either value.

## Testing

~~~bash
pip install -e ".[dev]"
pytest
~~~

## Project Status

pywa-webhook is currently an alpha project. The first release focuses on securely receiving and normalizing webhook events. Sending WhatsApp messages may be added as a separate client in a future release.

## Contributing

Issues and pull requests are welcome. Please include tests for behavior changes.
