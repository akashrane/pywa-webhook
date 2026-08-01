"""FastAPI integration for pywa-webhook."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Query, Request, Response

from ..exceptions import InvalidPayloadError, InvalidSignatureError
from ..webhook import WhatsAppWebhook


def create_router(
    webhook: WhatsAppWebhook,
    *,
    path: str = "/webhook",
) -> APIRouter:
    """Create a FastAPI router exposing Meta GET and POST webhook routes."""

    router = APIRouter()

    @router.get(path)
    async def verify_webhook(
        mode: str | None = Query(default=None, alias="hub.mode"),
        token: str | None = Query(default=None, alias="hub.verify_token"),
        challenge: str | None = Query(default=None, alias="hub.challenge"),
    ) -> Response:
        try:
            verified_challenge = webhook.verify_challenge(
                mode=mode,
                token=token,
                challenge=challenge,
            )
        except (PermissionError, ValueError) as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        return Response(content=verified_challenge, media_type="text/plain")

    @router.post(path)
    async def receive_webhook(request: Request) -> dict[str, str]:
        body = await request.body()
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as error:
            raise HTTPException(status_code=400, detail="Invalid JSON.") from error

        try:
            events = webhook.parse(
                payload,
                body=body,
                signature=request.headers.get("x-hub-signature-256"),
            )
        except InvalidSignatureError as error:
            raise HTTPException(status_code=401, detail=str(error)) from error
        except InvalidPayloadError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        await webhook.dispatch(events)
        return {"status": "received"}

    return router
