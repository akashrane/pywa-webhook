"""Exceptions raised by pywa-webhook."""


class PywaWebhookError(Exception):
    """Base exception for the package."""


class InvalidSignatureError(PywaWebhookError):
    """Raised when a webhook signature cannot be validated."""


class InvalidPayloadError(PywaWebhookError):
    """Raised when a payload is not a supported Meta webhook payload."""
