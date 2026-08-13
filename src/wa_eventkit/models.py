"""Normalized webhook event models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal


@dataclass(frozen=True, slots=True)
class Message:
    """A normalized incoming WhatsApp message."""

    id: str
    sender: str
    recipient: str | None
    timestamp: datetime
    type: str
    text: str | None = None
    profile_name: str | None = None
    phone_number_id: str | None = None
    media_id: str | None = None
    caption: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_meta(
        cls,
        data: dict[str, Any],
        *,
        metadata: dict[str, Any],
        contacts: list[dict[str, Any]],
    ) -> "Message":
        message_type = str(data.get("type", "unknown"))
        content = data.get(message_type)
        content = content if isinstance(content, dict) else {}
        contact = contacts[0] if contacts else {}
        profile = contact.get("profile")
        profile = profile if isinstance(profile, dict) else {}

        try:
            timestamp = datetime.fromtimestamp(
                int(data.get("timestamp", "0")), tz=timezone.utc
            )
        except (TypeError, ValueError, OSError):
            timestamp = datetime.fromtimestamp(0, tz=timezone.utc)

        media_id = None
        if message_type in {"audio", "document", "image", "sticker", "video"}:
            media_id = content.get("id")

        text = None
        if message_type == "text":
            text = content.get("body")
        elif message_type in {"button", "interactive"}:
            text = _interactive_text(message_type, content)

        location = content if message_type == "location" else {}

        return cls(
            id=str(data.get("id", "")),
            sender=str(data.get("from", "")),
            recipient=metadata.get("display_phone_number"),
            timestamp=timestamp,
            type=message_type,
            text=text,
            profile_name=profile.get("name"),
            phone_number_id=metadata.get("phone_number_id"),
            media_id=media_id,
            caption=content.get("caption"),
            latitude=location.get("latitude"),
            longitude=location.get("longitude"),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class StatusUpdate:
    """A normalized outbound message delivery status."""

    id: str
    status: str
    recipient: str | None
    timestamp: datetime
    conversation_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_meta(cls, data: dict[str, Any]) -> "StatusUpdate":
        conversation = data.get("conversation")
        conversation = conversation if isinstance(conversation, dict) else {}
        try:
            timestamp = datetime.fromtimestamp(
                int(data.get("timestamp", "0")), tz=timezone.utc
            )
        except (TypeError, ValueError, OSError):
            timestamp = datetime.fromtimestamp(0, tz=timezone.utc)

        return cls(
            id=str(data.get("id", "")),
            status=str(data.get("status", "unknown")),
            recipient=data.get("recipient_id"),
            timestamp=timestamp,
            conversation_id=conversation.get("id"),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class WebhookEvent:
    """A normalized event emitted from one webhook change."""

    kind: Literal["message", "status"]
    message: Message | None = None
    status: StatusUpdate | None = None
    raw: dict[str, Any] = field(default_factory=dict)


def _interactive_text(message_type: str, content: dict[str, Any]) -> str | None:
    if message_type == "button":
        return content.get("text") or content.get("payload")

    interactive_type = content.get("type")
    reply = content.get(f"{interactive_type}_reply")
    if isinstance(reply, dict):
        return reply.get("title") or reply.get("id")
    return None
