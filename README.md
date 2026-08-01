# pywa-webhook

A lightweight Python library for receiving, authenticating, and parsing Meta WhatsApp Cloud API webhooks.

## About

Meta delivers WhatsApp events as deeply nested webhook payloads. pywa-webhook handles the infrastructure-facing parts—subscription verification, request-signature validation, payload traversal, normalization, and event dispatch—so applications can work with simple typed Python objects.

The library is application-independent. It has no database, ordering, CRM, chatbot, or business-domain assumptions. Use it in customer support systems, notification services, bots, workflow automations, analytics pipelines, or any Python application that needs WhatsApp webhook events.

### What it handles

- Meta webhook challenge verification
- X-Hub-Signature-256 validation with your Meta App Secret
- Text, media, location, button, interactive, and status events
- Sync and async handlers
- Framework-neutral parsing
- Optional FastAPI integration
- Raw Meta payload access when needed

### What it does not handle yet

- Sending WhatsApp messages
- Downloading media
- Creating message templates
- Managing Meta Business assets
- Storing messages in a database

## Documentation

- [Complete Meta and pywa-webhook setup guide](docs/META_SETUP.md)
- [Meta WhatsApp Cloud API documentation](https://developers.facebook.com/docs/whatsapp/cloud-api/)
- [Meta webhook documentation](https://developers.facebook.com/docs/graph-api/webhooks/)

## Installation

Install from GitHub until the first PyPI release:

~~~bash
pip install "pywa-webhook[fastapi] @ git+https://github.com/akashrane/pywa-webhook.git"
~~~

For development:

~~~bash
git clone https://github.com/akashrane/pywa-webhook.git
cd pywa-webhook
python -m venv .venv
pip install -e ".[fastapi,dev]"
~~~

## Quick Start

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
def receive_message(message):
    print(f"Message from {message.sender}: {message.text}")


@webhook.on_status
async def receive_status(status):
    print(f"Message {status.id}: {status.status}")
~~~

Run the application:

~~~bash
uvicorn examples.fastapi_app:app --host 0.0.0.0 --port 8000
~~~

Meta must be configured with a public HTTPS callback ending in /webhook. See the [complete setup guide](docs/META_SETUP.md) for app creation, credentials, local tunneling, webhook verification, subscriptions, production setup, and troubleshooting.

## Framework-Neutral Parsing

~~~python
from pywa_webhook import parse_payload

for event in parse_payload(meta_payload):
    if event.kind == "message":
        print(event.message.sender, event.message.text)
~~~

## Testing

~~~bash
pip install -e ".[dev]"
pytest
~~~

## Status

pywa-webhook is currently alpha software. The first release focuses on securely receiving and normalizing webhook events.
