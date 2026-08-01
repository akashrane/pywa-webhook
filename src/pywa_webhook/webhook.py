"""Framework-neutral webhook coordinator."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from .models import Message, StatusUpdate, WebhookEvent
from .parser import parse_payload
from .security import verify_signature

HandlerResult = TypeVar("HandlerResult")
MessageHandler = Callable[[Message], HandlerResult | Awaitable[HandlerResult]]
StatusHandler = Callable[
    [StatusUpdate], HandlerResult | Awaitable[HandlerResult]
]


class WhatsAppWebhook:
    """Verify Meta requests, parse events, and dispatch registered handlers."""

    def __init__(
        self,
        *,
        verify_token: str,
        app_secret: str | None = None,
        verify_signatures: bool = True,
    ) -> None:
        if not verify_token:
            raise ValueError("verify_token must not be empty.")
        if verify_signatures and not app_secret:
            raise ValueError(
                "app_secret is required when signature verification is enabled."
            )

        self.verify_token = verify_token
        self.app_secret = app_secret
        self.verify_signatures = verify_signatures
        self._message_handlers: list[MessageHandler[Any]] = []
        self._status_handlers: list[StatusHandler[Any]] = []

    def verify_challenge(
        self,
        *,
        mode: str | None,
        token: str | None,
        challenge: str | None,
    ) -> str:
        """Validate Meta's webhook subscription challenge."""

        if mode != "subscribe" or token != self.verify_token:
            raise PermissionError("Webhook verification failed.")
        if challenge is None:
            raise ValueError("Webhook challenge is missing.")
        return challenge

    def parse(
        self,
        payload: dict[str, Any],
        *,
        body: bytes | None = None,
        signature: str | None = None,
    ) -> list[WebhookEvent]:
        """Verify and parse one webhook request."""

        if self.verify_signatures:
            if body is None:
                raise ValueError("Raw request body is required for verification.")
            verify_signature(body, signature, self.app_secret or "")
        return parse_payload(payload)

    def on_message(self, handler: MessageHandler[Any]) -> MessageHandler[Any]:
        """Register a message handler; usable as a decorator."""

        self._message_handlers.append(handler)
        return handler

    def on_status(self, handler: StatusHandler[Any]) -> StatusHandler[Any]:
        """Register a delivery-status handler; usable as a decorator."""

        self._status_handlers.append(handler)
        return handler

    async def dispatch(self, events: list[WebhookEvent]) -> None:
        """Dispatch normalized events to sync or async handlers."""

        for event in events:
            if event.kind == "message" and event.message is not None:
                await self._run_handlers(self._message_handlers, event.message)
            elif event.kind == "status" and event.status is not None:
                await self._run_handlers(self._status_handlers, event.status)

    @staticmethod
    async def _run_handlers(
        handlers: list[Callable[[Any], Any]],
        event: Message | StatusUpdate,
    ) -> None:
        for handler in handlers:
            result = handler(event)
            if inspect.isawaitable(result):
                await result
