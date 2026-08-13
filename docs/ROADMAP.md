# Product Roadmap

## Product Direction

The project will focus on one promise:

> The easiest way to test, debug, secure, and reliably process Meta WhatsApp webhooks in Python.

It will remain application-independent and will not initially compete with complete WhatsApp SDKs that send messages, create templates, manage business accounts, or build bots.

The project name is **wa-eventkit**, selected to clearly distinguish it from complete WhatsApp SDKs and the established PyWa framework.

## How We Are Different

| Area | Meta documentation | Full WhatsApp SDKs | Current project | Planned improvement |
| --- | --- | --- | --- | --- |
| Purpose | Defines the WhatsApp platform and raw APIs | Complete messaging and bot framework | Basic webhook receiver | Focused webhook development and reliability toolkit |
| Incoming messages | Raw nested JSON | Parsed events | Basic typed parsing | Complete normalized event coverage |
| Sending messages | Graph API documentation | Usually supported | Not supported | Remains out of initial scope |
| Verification | Developer implements challenge handling | Usually supported | Supported | Diagnostics and configuration checks |
| Request security | Developer implements HMAC validation | Usually supported | Signature validation | Secret rotation and replay protection |
| Local development | Meta test endpoint | Framework-specific server | Manual FastAPI setup | One-command development console |
| Payload testing | Documentation examples | Varies | Small fixtures | Complete payload factory library |
| Recording and replay | Manual | Not usually a primary feature | Not supported | Built-in event recording and replay |
| Duplicate delivery | Meta warns about retries | Application responsibility | Not handled | Memory and Redis deduplication |
| Fast acknowledgement | Developer responsibility | Framework dependent | Handlers run before response | Immediate acknowledgement and queued processing |
| Unknown events | Raw JSON | Varies | Usually ignored | Preserve and dispatch safely |
| Frameworks | Generic HTTP documentation | Usually limited integrations | FastAPI | FastAPI, Flask, Django, ASGI, WSGI, and serverless |
| Multi-business routing | WABA and phone webhook overrides | Often part of large SDKs | Not supported | Lightweight tenant and phone routing |
| Privacy | Developer responsibility | Varies | Basic output | Redacted structured logging |
| Monitoring | Developer responsibility | Varies | Not supported | Metrics and lifecycle hooks |
| CLI | None for Python applications | Varies | None | Inspect, generate, sign, record, replay, and diagnose |
| Dependencies | Not applicable | Often broad | Lightweight | Dependency-free core remains a goal |

## Key Differentiators

1. Test webhook applications without Meta credentials.
2. Generate realistic webhook payloads.
3. Record, redact, and replay real events.
4. Prevent duplicate event processing.
5. Acknowledge Meta immediately and process asynchronously.
6. Provide privacy-safe structured logs.
7. Preserve and report unknown Meta event types.
8. Diagnose configuration with one CLI command.
9. Support multiple Python frameworks without coupling the core parser.
10. Track Meta payload compatibility over time.

## Planned Event Coverage

### Message events

- [x] Text messages
- [x] Common media metadata
- [x] Locations
- [x] Buttons and interactive replies
- [x] Delivery status events
- [ ] Contacts
- [ ] Reactions
- [ ] System messages
- [ ] Referral and advertisement metadata
- [ ] Message-level errors
- [ ] Complete media metadata
- [ ] Unsupported and unknown message wrappers

### Platform events

- [ ] Calls
- [ ] Account alerts
- [ ] Account review updates
- [ ] Account updates
- [ ] Business capability updates
- [ ] Template component updates
- [ ] Template quality updates
- [ ] Template status updates
- [ ] Phone-number name updates
- [ ] Phone-number quality updates
- [ ] Security events
- [ ] User marketing preferences
- [ ] Payment configuration updates
- [ ] WhatsApp Business app message echoes
- [ ] History synchronization events

## Planned Developer API

~~~python
from wa_eventkit import Webhook

webhook = Webhook.from_env()


@webhook.on_message
async def receive(message):
    print(message.sender, message.text)


@webhook.on_status
async def status_changed(status):
    print(status.id, status.state)


@webhook.on_unknown
async def unknown(event):
    print(event.field, event.raw)
~~~

The distribution name is `wa-eventkit`, the Python import is `wa_eventkit`, and the planned CLI command is `wa-eventkit`.

## CLI Plan

Primary command:

~~~bash
wa-eventkit dev
~~~

Planned commands:

~~~bash
wa-eventkit doctor
wa-eventkit generate text
wa-eventkit generate image
wa-eventkit inspect payload.json
wa-eventkit replay payload.json
wa-eventkit sign payload.json
~~~

### Development server goals

- Start a local webhook endpoint.
- Print raw and normalized events.
- Display verification and signature status.
- Save received events optionally.
- Redact personal information when recording.
- Replay recorded events.
- Generate valid sample signatures.
- Offer clear HTTPS tunnel instructions.

## Testing Toolkit

Planned factories:

~~~python
from wa_eventkit.testing import text_message

payload = text_message(
    sender="15551234567",
    text="Where is my order?",
)
~~~

The testing package will provide:

- Text, image, document, audio, video, location, reaction, and interactive events
- Delivery and failure status events
- Account and template events
- Valid signature generation
- Invalid signature fixtures
- FastAPI, Flask, and Django test helpers
- Payload mutation for edge cases
- Official-style sample payloads
- Oversized and malformed payload tests

## Delivery Reliability

Meta can retry failed webhook notifications and may deliver duplicates. Planned reliability features include:

### Deduplication

~~~python
webhook = Webhook(
    deduplicator=MemoryDeduplicator(),
)
~~~

Production adapters may include Redis and a custom deduplicator protocol.

### Immediate acknowledgement

The intended request flow is:

1. Validate the signature.
2. Enforce request-size limits.
3. Parse and identify the event.
4. Store or enqueue the event.
5. Return HTTP 200.
6. Run application handlers outside the request lifecycle.

### Queue adapters

- [ ] In-memory background queue
- [ ] FastAPI background tasks
- [ ] Celery
- [ ] Redis Queue
- [ ] Dramatiq
- [ ] Custom queue protocol

### Failure handling

- [ ] Handler timeouts
- [ ] Error hooks
- [ ] Dead-letter hooks
- [ ] Retry policies
- [ ] Processing attempt metadata
- [ ] Idempotency helpers

## Security and Privacy

Planned security improvements:

- [x] HMAC-SHA256 request-signature validation
- [x] Signature checking enabled by default
- [ ] Multiple active secrets during rotation
- [ ] Replay protection
- [ ] Request timestamp policies where applicable
- [ ] Configurable payload-size limit
- [ ] Sensitive-field redaction
- [ ] Safe production logging defaults
- [ ] Security audit command
- [ ] mTLS deployment guidance

Raw payload logging will be opt-in for production configurations.

## Observability

Planned hooks:

~~~python
@webhook.on_error
def handle_error(error, event):
    ...


@webhook.on_duplicate
def handle_duplicate(event):
    ...
~~~

Planned metrics:

- Events received
- Events parsed
- Invalid signatures
- Parse failures
- Unknown event types
- Duplicate events
- Handler failures
- Handler duration
- Payload size
- Queue delay

## Framework Roadmap

| Priority | Integration | Status |
| ---: | --- | --- |
| 1 | FastAPI | Initial adapter available |
| 2 | Flask | Planned |
| 3 | Django | Planned |
| 4 | Starlette and generic ASGI | Planned |
| 5 | Generic WSGI | Planned |
| 6 | AWS Lambda and API Gateway | Planned |
| 7 | Azure Functions | Planned |
| 8 | Google Cloud Functions | Planned |

## Multi-Tenant Routing

Planned routing API:

~~~python
@webhook.route(phone_number_id="123456")
def store_one(event):
    ...


@webhook.tenant_resolver
def resolve_tenant(event):
    return event.phone_number_id
~~~

Multi-tenant support should allow:

- Separate secrets per tenant
- Separate handlers and queues
- WABA-level routing
- Phone-number-level routing
- Tenant-aware metrics
- Tenant-specific logging and redaction policies

## Release Plan

### 0.2.0 — Foundation

- [x] Finalize a distinct project and package name
- [ ] Expand common message types
- [ ] Add unknown-event handling
- [ ] Improve event models and validation errors
- [ ] Add Flask support
- [ ] Expand sample-payload coverage

### 0.3.0 — Developer Experience

- [ ] Add the development CLI
- [ ] Add payload factories
- [ ] Add signature-generation helpers
- [ ] Add event inspection
- [ ] Add recording and replay
- [ ] Add the doctor command

### 0.4.0 — Production Reliability

- [ ] Add immediate acknowledgement
- [ ] Add deduplication interfaces
- [ ] Add Redis deduplication
- [ ] Add queue interfaces
- [ ] Add structured logging
- [ ] Add privacy redaction
- [ ] Add metrics and error hooks

### 0.5.0 — Platform Coverage

- [ ] Add call events
- [ ] Add account and capability events
- [ ] Add template events
- [ ] Add phone quality and security events
- [ ] Add multi-WABA routing
- [ ] Add serverless adapters

### 1.0.0 — Stable Release

- [ ] Stabilize the public event API
- [ ] Publish the package to PyPI
- [ ] Publish complete documentation with screenshots
- [ ] Add a Meta compatibility matrix
- [ ] Publish performance benchmarks
- [ ] Complete security and deployment guides
- [ ] Document migration and deprecation policies

## Deliberately Out of Scope Before 1.0

- Sending WhatsApp messages
- Template creation and management
- WhatsApp Flows builders
- Group management
- Calling clients
- Business-account management
- AI chatbot orchestration

These capabilities are already addressed by larger WhatsApp SDKs. The project will first make webhook testing and processing excellent.

## References

- [Meta WhatsApp Business Platform](https://developers.facebook.com/documentation/business-messaging/whatsapp/overview)
- [Meta webhook documentation](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview)
- [Meta getting-started guide](https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started)
