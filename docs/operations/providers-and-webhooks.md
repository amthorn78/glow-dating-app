# Provider preparation and webhook boundaries

P03 prepares interfaces and configuration; no provider account, subscription,
callback, live credential or production adapter was activated. Public official
documentation below was checked on 23 September 2026. Documentation describes
published capabilities, not Nathan's account access, eligibility or billing.
Runtime production guards and P11 sequencing remain in force.

## Access and activation inventory

| Capability | Current preparation | Required before activation | Owning dependency / evidence |
|---|---|---|---|
| Cloudflare media | Plan selects Images/private R2 as appropriate; no live media adapter or webhook route | App-owned account/bucket/product, private delivery and upload grants, scoped server credentials, moderation/quarantine policy, purge rights, actual cost and domain access | A04/A05; P04 preparation; PV04/PV07 in P11B |
| Mail | No vendor selected or outbound transport implemented | Sender domain/admin access, verification/recovery mail provider, scoped server credentials, delivery/bounce rules and data terms | A04; P04; DB09/PV07 |
| Stream Chat | Conditional preference; pure signature verifier exists; no SDK account connection or callback route | Separate app identity/secret, permission and cost proof, server-controlled membership/send/revoke, privacy/history/deletion terms | A04/A05/A08; PV03 in P06 and repeated P11B |
| Expo push | Mobile uses Expo; no push credential or delivery adapter activated | EAS project and native app identities, APNs/FCM credentials, server access token and enhanced push security, device ownership/preferences, one notification delivery path | A04; P06; PV05/N01 |
| Monitoring | Local structured telemetry preparation; no external monitoring vendor chosen | Operator/alert destination, bounded retained fields, processor terms, access, retention and budget; no uncontrolled request/payload capture | A04/A05; P09 and R01 |
| RevenueCat | Conditional architecture only; purchase UI, billing adapter and webhook route remain disabled | Explicit A06 paid-scope decision, actual integration eligibility/budget, app/store products, server credentials, verified callbacks and reconciliation | A04/A06; PV08 only if paid scope is selected |
| HDE | Provisional app ports/fixtures only | Supported authorized contract/release, environment, output/cache/deletion rights and scoped credentials | A01/A07; PV01/PV02; no HDE changes under app authority |

These are required inputs, not a request to paste credentials into chat. Use the
provider and deployment platform's secure secret mechanisms. App service secrets
must remain service/environment scoped even when app and HDE occupy the same
Railway project. Do not read/copy protected HDE or shared resource credentials.
Public mobile values cannot carry server provider secrets. The
[configuration catalog](configuration.md) owns variable names, types, required
modes, scope and secret classification; this page owns provider prerequisites
and callback protocol limitations.

## Implemented Stream Chat signature check

[`glow_domain/webhooks.py`](../../services/api/glow_domain/webhooks.py) has no
network, database, SDK initialization or HTTP registration. It uses Python's
standard HMAC-SHA256 and constant-time comparison. `verify_stream_signature`
defaults to disabled. Setting its explicit `enabled` argument permits only the
pure check; it cannot enable a provider or callback endpoint.

The [official Stream overview](https://getstream.io/chat/docs/python/webhooks-overview/)
specifies `X-Signature`, raw body bytes and the application secret, with
`X-Api-Key` identifying the intended application. The
[official Python SDK](https://raw.githubusercontent.com/GetStream/stream-chat-python/master/stream_chat/base/client.py)
`verify_webhook` implementation confirms SHA256 and hexadecimal encoding. This
mutable upstream reference is research, not an installed SDK pin.

The verifier binds the API key to one explicit credential pair, requires one
lowercase hexadecimal signature and authenticates exact bytes without JSON
normalization. App-specific limits are a 1 MiB nonempty body, 256-byte printable
ASCII key, and 4096-byte secret ceiling; these are not advertised vendor quotas.
Errors/results contain fixed codes and retain no payload, key or signature.

Only identity encoding is supported. Stream's SDK also supports compressed
deliveries; that capability is deliberately unimplemented here. A future HTTP
adapter must enforce request-size limits before buffering, reject duplicate
signature/key headers, normalize the absence of Content-Encoding to identity,
and supply `request.body` before parsing. These transport controls are not
claimed from the pure function's checks alone.

The documented signature has no timestamp envelope. `X-Webhook-Id` is stable
across retries but is not part of the body HMAC; it must not become sole replay
proof. A replay of valid bytes remains cryptographically authentic. No in-memory
seen-set is presented as durable replay prevention.

`require_durable_webhook_admission` **always refuses**. Invalid input receives
`unverified_event`; authenticated input receives `durable_inbox_unavailable`.
Even a caller-constructed verification result grants no domain permission.
Future admission needs schema/type/environment/app/object checks and an atomic
inbox binding event identity, verified content digest, replay/order state and
domain effects. Unknown event fields/types must not execute commands. These
remain DB08/PV03/PV07 integration obligations, not P03 successes. A webhook
signature does not establish mutual-match or block authorization.

### Stream rotation preparation

[Stream's rotation guidance](https://support.getstream.io/hc/en-us/articles/31482202551191-How-do-I-safely-rotate-API-keys-in-my-Stream-application)
supports maintaining old/new application keys with their matching secrets during
client migration. This implementation accepts one configured pair per call and
does not invent a universal previous-secret fallback. Replacing that pair rejects
the retired signature. If later integration needs overlapping application keys,
record each allowed key and retirement deadline explicitly, select only from that
bounded server configuration, and validate vendor behavior before cutover. No
rotation, overlap or vendor token revocation was performed in P03.

## Other researched contracts remain unimplemented

| Provider contract | Verified public mechanism | P03 consequence |
|---|---|---|
| Cloudflare Images direct creator upload | Images uses Cloudflare Notifications for upload success/failure. The documented account prerequisite is at least one Pro-or-higher zone; actual eligibility is unverified. | Do not purchase/enable an account to complete this preparation. Prove selected upload/private delivery behavior in PV04. |
| Cloudflare Notifications generic webhook | Configured secret arrives in `cf-webhook-auth`; reject absent/wrong value. It is shared-header authentication, not a raw-body signature or signed timestamp. | No fabricated HMAC verifier or replay guarantee. No callback route. Future TLS, credential check, ownership/schema/reconciliation and durable admission are required. |
| Cloudflare R2 object events | Bucket changes are routed through Queues to a Worker or HTTP pull consumer. | Do not apply video Stream's `Webhook-Signature` algorithm to Images/R2. Queue activation and authenticated consumption remain separate future work. |
| Expo push | Tickets are followed by polled receipts; enhanced push security uses a server Bearer access token. A receipt confirms FCM/APNs handoff, not device receipt. | No inbound push-receipt webhook verifier. Native identity, transport, receipt polling and token rotation remain PV05/N01. |
| RevenueCat | Optional HMAC header `X-RevenueCat-Webhook-Signature` uses `t=<unix>,v1=<hex>`, signing timestamp + `.` + exact raw JSON using HMAC-SHA256. Configured Authorization is also supported. | Billing and concrete verifier remain disabled/unimplemented. Recheck exact enabled account contract before PV08; never reuse Stream's un-timestamped verifier. |

Sources:

- [Cloudflare Images upload webhooks](https://developers.cloudflare.com/images/storage/upload-images/configure-webhooks/).
- [Cloudflare Notifications authentication and destination controls](https://developers.cloudflare.com/notifications/get-started/configure-webhooks/).
- [Cloudflare R2 event notifications](https://developers.cloudflare.com/r2/buckets/event-notifications/).
- [Expo push sending, receipts and additional security](https://docs.expo.dev/push-notifications/sending-notifications/).
- [RevenueCat webhook authorization, HMAC and rotation](https://www.revenuecat.com/docs/integrations/webhooks).

RevenueCat refreshes signature timestamps on retries while event IDs remain the
same. Its 300-second timestamp-window example does not deduplicate business
events. Rotation immediately invalidates the old signing secret, so an indefinite
previous-secret fallback would contradict the documented lifecycle. Secrets are
only displayed on creation/rotation. No RevenueCat account eligibility, HMAC
toggle, secret or webhook was inspected or created.

For Cloudflare generic destinations the inspected dashboard guide describes
name editing or deletion, not seamless secret overlap. Before a future rotation,
confirm the current replacement/update operation and notification attachment
effects in that account; do not infer vendor rotation semantics from an app
credential container. On compromise, disable affected consumption, rotate/revoke
through the authorized provider operator, update only the app service secret,
test rejection of the retired credential, and reconcile missed events through
the durable inbox. Never log secret values or replay private payloads into logs.

## Reproduction and limits

From `services/api`, after installing the committed development lock:

```sh
python -m unittest tests.test_webhooks -v
ruff check glow_domain/webhooks.py tests/test_webhooks.py
ruff format --check glow_domain/webhooks.py tests/test_webhooks.py
mypy glow_domain/webhooks.py
```

Tests use synthetic credentials, a fixed HMAC-SHA256 vector, exact-byte mutation,
malformed/bounded input, wrong application identity, disabled configuration,
encoding refusal, credential replacement and replay/admission refusal. Sockets
are blocked during those tests. Tests prove neither provider registration nor
valid event schemas, real permission enforcement, persistence, delivery or
production readiness. The existing [deferred cases](../testing/p11-deferred-acceptance.md)
remain unexecuted until their named environments and dependencies are available.
