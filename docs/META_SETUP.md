# Meta WhatsApp Cloud API Setup Guide

This guide explains how to connect pywa-webhook to a Meta WhatsApp Cloud API application, receive WhatsApp messages, and print them in a Python terminal.

Meta's dashboard labels and navigation can change. If a menu name differs, use the equivalent WhatsApp or Webhooks section shown for your app.

## 1. Understand the Credentials

WhatsApp Cloud API uses several values that are easy to confuse.

| Value | Who creates it | Used by pywa-webhook | Purpose |
| --- | --- | --- | --- |
| Verify token | You | Yes | A private string Meta sends during callback verification |
| App Secret | Meta | Yes | Validates X-Hub-Signature-256 on POST requests |
| Access token | Meta | No, not for receiving | Authorizes Graph API calls that send messages |
| Phone Number ID | Meta | Available in events | Identifies the WhatsApp sending number |
| WhatsApp Business Account ID | Meta | Not required for basic receiving | Identifies the WhatsApp Business Account |
| App ID | Meta | Not required for basic receiving | Identifies the Meta application |

Receiving webhook messages does not require an access token inside pywa-webhook. The package needs the Verify Token and App Secret. An access token is needed when your application sends messages or calls protected Graph API endpoints.

Never commit any token or App Secret to Git.

## 2. Prerequisites

You need:

- A Meta developer account
- Access to a Meta Business portfolio for production use
- Python 3.10 or newer
- A public HTTPS URL for the webhook
- A WhatsApp-enabled Meta application
- A test recipient phone number while the app is in development

For local testing, an HTTPS tunnel such as ngrok or Cloudflare Tunnel can expose your local server.

## 3. Create the Meta Application

1. Open [Meta for Developers](https://developers.facebook.com/).
2. Select My Apps.
3. Select Create App.
4. Choose an app type or use case that supports WhatsApp.
5. Enter an app name and contact email.
6. Associate the appropriate Business portfolio when Meta requests it.
7. Finish creating the application.
8. From the app dashboard, add the WhatsApp product if it is not already present.

After WhatsApp is added, Meta normally provides an API Setup page containing a temporary access token, test phone number, Phone Number ID, and WhatsApp Business Account ID.

## 4. Configure the Test Number

Meta provides a test WhatsApp number during development.

1. Open WhatsApp > API Setup in the app dashboard.
2. Locate the test From number.
3. Add your personal WhatsApp number as an allowed recipient.
4. Complete the recipient verification process if prompted.
5. Use Meta's test-message control to confirm that the test number can send to your phone.

The temporary access token shown on this page is for Graph API testing and normally expires. It is not used by pywa-webhook to receive messages.

## 5. Find the App Secret

1. Open the Meta application.
2. Navigate to App settings > Basic.
3. Locate App Secret.
4. Select Show and complete any requested account verification.
5. Copy the secret into a password manager or secret manager.

Set it locally:

~~~bash
export WHATSAPP_APP_SECRET="your-meta-app-secret"
~~~

PowerShell:

~~~powershell
$env:WHATSAPP_APP_SECRET = "your-meta-app-secret"
~~~

The FastAPI adapter uses this value to validate the X-Hub-Signature-256 request header. This confirms that the POST body was signed with your Meta App Secret.

If the App Secret is exposed, reset it in Meta and update every deployment that uses it.

## 6. Choose a Verify Token

The Verify Token is not supplied by Meta. You create it. It should be long, random, and private.

Example generation:

~~~bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
~~~

Set the generated value:

~~~bash
export WHATSAPP_VERIFY_TOKEN="your-generated-value"
~~~

PowerShell:

~~~powershell
$env:WHATSAPP_VERIFY_TOKEN = "your-generated-value"
~~~

You must enter this exact same value in the Meta webhook configuration. It is used only for the GET verification challenge; it is not an access token.

## 7. Install pywa-webhook

Until a PyPI release is available:

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install "pywa-webhook[fastapi] @ git+https://github.com/akashrane/pywa-webhook.git"
~~~

PowerShell activation:

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install "pywa-webhook[fastapi] @ git+https://github.com/akashrane/pywa-webhook.git"
~~~

## 8. Create the Python Application

Create app.py:

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
    print("--- New WhatsApp message ---")
    print("ID:", message.id)
    print("From:", message.sender)
    print("Name:", message.profile_name)
    print("Type:", message.type)
    print("Text:", message.text)


@webhook.on_status
def receive_status(status):
    print(
        f"Message {status.id} changed to {status.status} "
        f"for {status.recipient}"
    )
~~~

Start it:

~~~bash
uvicorn app:app --host 0.0.0.0 --port 8000
~~~

The application now exposes:

~~~text
GET  http://localhost:8000/webhook
POST http://localhost:8000/webhook
~~~

GET handles Meta's verification challenge. POST verifies signed requests, parses events, and dispatches your handlers.

## 9. Expose the Local Server

Meta cannot send webhooks directly to localhost. It requires a public HTTPS URL.

Example with ngrok:

~~~bash
ngrok http 8000
~~~

ngrok returns a URL similar to:

~~~text
https://example-subdomain.ngrok-free.app
~~~

Your callback URL is:

~~~text
https://example-subdomain.ngrok-free.app/webhook
~~~

Keep both uvicorn and the tunnel running. Free tunnel URLs may change when restarted; update Meta whenever the URL changes.

For production, use a stable HTTPS domain rather than a development tunnel.

## 10. Configure the Meta Webhook

1. Open your Meta application.
2. Navigate to WhatsApp > Configuration.
3. Find the Webhook section.
4. Select Edit or Configure.
5. Enter the public callback URL ending in /webhook.
6. Enter the exact WHATSAPP_VERIFY_TOKEN value.
7. Select Verify and Save.
8. Subscribe the webhook to the messages field.

During verification, Meta sends a GET request similar to:

~~~text
/webhook?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...
~~~

pywa-webhook compares hub.verify_token with your configured Verify Token and returns hub.challenge as plain text. A mismatch returns HTTP 403.

The messages subscription delivers both incoming message events and delivery-status events associated with WhatsApp messages.

## 11. Test Incoming Messages

1. Confirm uvicorn is running.
2. Confirm the HTTPS tunnel is running.
3. Confirm Meta shows the callback as verified.
4. Confirm the messages field is subscribed.
5. Send a WhatsApp message from an allowed recipient to Meta's test number.

Expected terminal output:

~~~text
--- New WhatsApp message ---
ID: wamid...
From: 15551234567
Name: Example User
Type: text
Text: Hello
~~~

Meta may send status-only payloads as messages move through sent, delivered, read, or failed states. These are dispatched through on_status instead of on_message.

## 12. Work with Different Message Types

Text:

~~~python
@webhook.on_message
def handle(message):
    if message.type == "text":
        print(message.text)
~~~

Media:

~~~python
@webhook.on_message
def handle(message):
    if message.type in {"image", "video", "audio", "document", "sticker"}:
        print("Media ID:", message.media_id)
        print("Caption:", message.caption)
~~~

Location:

~~~python
@webhook.on_message
def handle(message):
    if message.type == "location":
        print(message.latitude, message.longitude)
~~~

Buttons and interactive replies are normalized into message.text when a useful title, text, payload, or ID is present.

For fields not yet normalized, inspect:

~~~python
print(message.raw)
~~~

## 13. Signature Verification

For every webhook POST, the FastAPI adapter reads the exact raw request bytes and validates X-Hub-Signature-256 using HMAC-SHA256 and your App Secret.

Do not parse and re-serialize the JSON before verification. Even harmless formatting differences change the signature.

Framework-neutral applications can validate manually:

~~~python
from pywa_webhook import verify_signature

verify_signature(
    raw_body,
    request_headers.get("X-Hub-Signature-256"),
    app_secret,
)
~~~

Invalid or missing signatures raise InvalidSignatureError. The FastAPI adapter converts this to HTTP 401.

Signature checking can be disabled for isolated unit tests:

~~~python
webhook = WhatsAppWebhook(
    verify_token="test-token",
    verify_signatures=False,
)
~~~

Do not disable it in a public deployment.

## 14. Temporary and Production Access Tokens

pywa-webhook does not currently send messages, so an access token is not required for the package's receiving workflow.

If another part of your application sends Graph API messages:

- Temporary access tokens are useful for initial testing and expire.
- Production applications should use the token mechanism recommended for their Meta Business setup, commonly a system user token.
- Grant only permissions required by the application.
- Common WhatsApp permissions include whatsapp_business_messaging and, for management operations, whatsapp_business_management.
- Store production tokens in a secret manager.
- Never put access tokens in frontend code, query strings, screenshots, logs, or Git history.

A typical production-token setup uses Meta Business Settings to create or select a system user, assign the application and WhatsApp assets, and generate a token with the required permissions. Meta's exact screens and approval requirements may vary by account and business status.

## 15. Production Checklist

Before production:

- Use a stable HTTPS domain.
- Keep signature verification enabled.
- Store secrets in a managed secret store.
- Use separate development and production credentials.
- Restrict logs so message content and phone numbers are not exposed unnecessarily.
- Return HTTP 200 quickly and move slow work to a queue or background worker.
- Make handlers idempotent because webhook events can be delivered more than once.
- Deduplicate events using message.id or status identifiers.
- Monitor handler failures and webhook response latency.
- Complete Meta business verification and app-review requirements when applicable.
- Configure the real business phone number instead of the Meta test number.
- Review Meta's current platform and data-handling requirements.

## 16. Troubleshooting

### Meta says the callback could not be verified

Check:

- The URL is public HTTPS and ends in /webhook.
- uvicorn and the tunnel are running.
- Meta and WHATSAPP_VERIFY_TOKEN use exactly the same value.
- The tunnel forwards to port 8000.
- No proxy removes the hub query parameters.

A token mismatch returns HTTP 403.

### POST requests return HTTP 401

The signature does not match.

Check:

- WHATSAPP_APP_SECRET belongs to the same Meta app.
- The proxy has not changed the request body.
- The exact raw body is used for validation.
- The x-hub-signature-256 header reaches the application.

### Verification succeeds but messages do not arrive

Check:

- The messages field is subscribed.
- The recipient is allowed for the test number.
- You are messaging the correct WhatsApp number.
- The callback URL did not change after restarting the tunnel.
- The app and WhatsApp Business Account assets are connected correctly.
- The server logs do not show parsing or handler errors.

### Messages arrive more than once

Webhook delivery is at-least-once in practice. Store processed message IDs and make your handlers idempotent.

### message.text is None

The event may be media, location, reaction, status, or another non-text type. Inspect message.type and message.raw.

## 17. Official References

- [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api/)
- [WhatsApp Cloud API Get Started](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started)
- [WhatsApp Cloud API Webhooks](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/)
- [Graph API Webhooks](https://developers.facebook.com/docs/graph-api/webhooks/)
- [Meta App Dashboard](https://developers.facebook.com/apps/)
