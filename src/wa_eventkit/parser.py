"""Parse Meta WhatsApp webhook payloads into normalized events."""

from __future__ import annotations

from typing import Any

from .exceptions import InvalidPayloadError
from .models import Message, StatusUpdate, WebhookEvent


def parse_payload(payload: dict[str, Any]) -> list[WebhookEvent]:
    """Parse all messages and status updates contained in a Meta payload."""

    if not isinstance(payload, dict):
        raise InvalidPayloadError("Webhook payload must be a JSON object.")
    if payload.get("object") != "whatsapp_business_account":
        raise InvalidPayloadError("Payload is not a WhatsApp Business webhook.")

    events: list[WebhookEvent] = []
    entries = payload.get("entry", [])
    if not isinstance(entries, list):
        raise InvalidPayloadError("Payload entry must be a list.")

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        changes = entry.get("changes", [])
        if not isinstance(changes, list):
            continue

        for change in changes:
            if not isinstance(change, dict):
                continue
            value = change.get("value", {})
            if not isinstance(value, dict):
                continue

            metadata = value.get("metadata", {})
            metadata = metadata if isinstance(metadata, dict) else {}
            contacts = value.get("contacts", [])
            contacts = contacts if isinstance(contacts, list) else []

            messages = value.get("messages", [])
            if isinstance(messages, list):
                for item in messages:
                    if isinstance(item, dict):
                        message = Message.from_meta(
                            item,
                            metadata=metadata,
                            contacts=contacts,
                        )
                        events.append(
                            WebhookEvent(
                                kind="message",
                                message=message,
                                raw=change,
                            )
                        )

            statuses = value.get("statuses", [])
            if isinstance(statuses, list):
                for item in statuses:
                    if isinstance(item, dict):
                        status = StatusUpdate.from_meta(item)
                        events.append(
                            WebhookEvent(
                                kind="status",
                                status=status,
                                raw=change,
                            )
                        )

    return events
