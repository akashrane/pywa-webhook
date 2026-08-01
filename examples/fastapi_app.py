"""Minimal FastAPI application that prints incoming messages."""

import os

from fastapi import FastAPI

from pywa_webhook import WhatsAppWebhook
from pywa_webhook.adapters.fastapi import create_router

webhook = WhatsAppWebhook(
    verify_token=os.environ["WHATSAPP_VERIFY_TOKEN"],
    app_secret=os.environ["WHATSAPP_APP_SECRET"],
)

app = FastAPI(title="pywa-webhook example")
app.include_router(create_router(webhook))


@webhook.on_message
def print_message(message):
    print(f"Message from {message.sender}: {message.text}")


@webhook.on_status
def print_status(status):
    print(f"Message {status.id}: {status.status}")
