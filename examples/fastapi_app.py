"""Minimal FastAPI application that prints incoming messages."""

import os

from fastapi import FastAPI

from wa_eventkit import Webhook
from wa_eventkit.adapters.fastapi import create_router

webhook = Webhook(
    verify_token=os.environ["WA_EVENTKIT_VERIFY_TOKEN"],
    app_secret=os.environ["WA_EVENTKIT_APP_SECRET"],
)

app = FastAPI(title="wa-eventkit example")
app.include_router(create_router(webhook))


@webhook.on_message
def print_message(message):
    print(f"Message from {message.sender}: {message.text}")


@webhook.on_status
def print_status(status):
    print(f"Message {status.id}: {status.status}")
