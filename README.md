# wa-eventkit

A lightweight Python library for receiving, authenticating, and parsing Meta WhatsApp Cloud API webhooks.

## About

Meta delivers WhatsApp events as deeply nested webhook payloads. wa-eventkit handles the infrastructure-facing parts—subscription verification, request-signature validation, payload traversal, normalization, and event dispatch—so applications can work with simple typed Python objects.

The library is application-independent. It has no database, ordering, CRM, chatbot, or business-domain assumptions. Use it in customer support systems, notification services, bots, workflow automations, analytics pipelines, or any Python application that needs WhatsApp webhook events.

> `wa-eventkit` is intentionally focused on webhook testing, security, debugging, and delivery reliability rather than becoming a complete WhatsApp messaging SDK.

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

- [Product comparison and roadmap](docs/ROADMAP.md)
- [Complete Meta and wa-eventkit setup guide](docs/META_SETUP.md)
- [Meta WhatsApp Cloud API documentation](https://developers.facebook.com/docs/whatsapp/cloud-api/)
- [Meta webhook documentation](https://developers.facebook.com/docs/graph-api/webhooks/)

## Installation

Install from GitHub until the first PyPI release:

~~~bash
pip install "wa-eventkit[fastapi] @ git+https://github.com/akashrane/wa-eventkit.git"
~~~

For development:

~~~bash
git clone https://github.com/akashrane/wa-eventkit.git
cd wa-eventkit
python -m venv .venv
pip install -e ".[fastapi,dev]"
~~~

## Quick Start

~~~python
import os

from fastapi import FastAPI

from wa_eventkit import Webhook
from wa_eventkit.adapters.fastapi import create_router

webhook = Webhook(
    verify_token=os.environ["WA_EVENTKIT_VERIFY_TOKEN"],
    app_secret=os.environ["WA_EVENTKIT_APP_SECRET"],
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
from wa_eventkit import parse_payload

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

wa-eventkit is currently alpha software. The first release focuses on securely receiving and normalizing webhook events. See the [roadmap](docs/ROADMAP.md) for planned testing, replay, deduplication, privacy, observability, and framework features.
