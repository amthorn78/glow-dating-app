# Private media provider and native selection mapping

Research for **AP1-P04.3-001**, checked 23 September 2026 against the official
sources linked below. This is integration preparation under GAPP-PF01. It does
not activate a provider, settle account eligibility or approve launch policy.
The fixture adapter's events are synthetic; no provider callback is registered.

## Native selection and image display

The inspected mobile manifest pins Expo **57.0.24**, React Native **0.86.3** and
React **19.2.3**. Matching documentation was available. The
[SDK 57 ImagePicker reference](https://docs.expo.dev/versions/v57.0.0/sdk/imagepicker/)
recommends `expo-image-picker ~57.0.19`; the
[SDK 57 package manifest](https://github.com/expo/expo/blob/sdk-57/packages/expo-image-picker/package.json)
declares version `57.0.19`, MIT and `expo-image-loader ~57.0.1`. These upstream
branch references are research; the committed application lock is the installed
version authority. Use Expo's resolver and the existing compatibility check.

Prefer a narrow picker adapter using `launchImageLibraryAsync` for images only.
Read `canceled` and `assets`; treat filename, MIME, asset ID, byte count and
dimensions as untrusted hints. IDs/names can be absent under limited access.
`accessPrivileges` distinguishes all/limited/none where supported. Modern system
photo selection need not request broad library access. Disable unused camera and
microphone permissions in the config plugin; its default Android microphone
permission is unnecessary here. `exif: false` omits returned metadata, not proof
of stripping embedded metadata. Web selection requires a user press and may not
report cancellation, so explicit cancellation must invalidate pending work.
Android `getPendingResultAsync` can recover picker results, but the app must still
validate the original session/selection identity before adoption.

The [Expo documentation index](https://docs.expo.dev/llms.txt),
[SDK 57 Image reference](https://docs.expo.dev/versions/v57.0.0/sdk/image/) and
[React Native 0.86 Image reference](https://reactnative.dev/docs/0.86/image)
were also inspected. Expo Image recommends `~57.0.5`, but a second image
dependency is unnecessary for bounded bundled synthetic previews: React Native
Image supports local sources, fixed dimensions and accessibility labels. Image
display/cache behavior is not decoding validation or authorization. Use a safe
placeholder for private/unverified originals and clear retained presentation when
authority changes. Native picker permissions, activity recovery, device layout
and screen readers remain **N01**; browser fixtures are not device proof.

## Cloudflare mapping

| Concern | Observed official mechanism | Application consequence |
|---|---|---|
| Direct upload | [Images direct creator upload](https://developers.cloudflare.com/images/storage/upload-images/direct-creator-upload/) issues a one-use upload URL without exposing the server API credential. The request can require signed delivery. Unused URLs default to 30 minutes; configurable expiry is 2 minutes–6 hours. | Keep the app asset identity and opaque grant reference distinct from the provider image ID and upload URL. Use provider-generated IDs: custom IDs cannot use private signed delivery. The app may expire/revoke a grant earlier; that does not prove immediate revocation of an already issued provider URL. Reconcile any late private bytes. |
| Delivery | [Private Images delivery](https://developers.cloudflare.com/images/optimization/hosted-images/serve-private-images/) uses expiring server-generated signed URLs. A variant configured for always-public access bypasses the signed-image requirement. | Prohibit public-bypass variants. Only current approved variants are eligible for app-authorized delivery. Never expose the signing key. Signed URL possession/expiry alone does not establish current viewer eligibility or instantaneous revocation. Verify delivery/cache revocation behavior before activation. |
| Images upload notifications | [Images notifications](https://developers.cloudflare.com/images/storage/upload-images/configure-webhooks/) report direct creator upload success/failure through Cloudflare Notifications. Documentation requires an account with at least one Pro-or-higher zone. | Verify actual account eligibility later; do not purchase or enable anything for P04.3. An upload notice is not decoding, moderation or purge evidence. |
| Generic notification destination | [Notifications webhook configuration](https://developers.cloudflare.com/notifications/get-started/configure-webhooks/) sends the configured secret in `cf-webhook-auth`; absent or wrong values must be rejected. | This is shared-header authentication, not a body HMAC, signed timestamp or replay guarantee. Future admission also needs bounded parsing, exact account/object/attempt reconciliation and durable replay control. Do not reuse a video Stream signature protocol. |
| R2 events | [R2 event notifications](https://developers.cloudflare.com/r2/buckets/event-notifications/) send bucket changes to Queues, consumed through a Worker or HTTP pull. Object-delete events omit size and ETag. | This is a separate authenticated queue integration, not an Images webhook contract. Match app-owned bucket/object and removal identity; do not assume a unique event digest or ordered/exactly-once delivery from these fields. |
| Images deletion | [Delete Images](https://developers.cloudflare.com/images/storage/manage-images/delete-images/) documents authenticated deletion and `success: true` after deletion from the account. | Remove app delivery eligibility immediately, then retain `removal_pending` until the matching adapter acknowledgment/reconciliation. The cited page does not prove device-cache or backup erasure, a completion deadline, or an Images purge webhook. These require actual processor evidence. |

## Integration path and deferred proof

These are application design consequences, not vendor promises. Keep original
bytes private; validate actual encoded content and processing bounds before
creating a sanitized variant; moderate that variant before authorizing delivery.
An Images-based direct upload could supply private originals and variants. Private
R2 may instead be appropriate for controlled quarantine/processing. Final choice,
processing controls, credentials, cost and retention remain unverified. The app
must not send a signed URL merely because a provider upload succeeded.

The future adapter maps provider-owned identities to the app's current owner,
asset, upload/removal attempt and policy. Use a durable inbox/outbox and
reconciliation for ambiguous outcomes; retain pending deletion after timeout or
failure. Same-session memory and fabricated actor events cannot establish a
provider transaction or durable replay protection.

**PV04** retains actual private storage, safe decoding, metadata removal,
moderation, authorized delivery and purge proof. **PV07** retains processor
deletion/export. **DB07/DB08** retain durable outbox/inbox, replay and recovery.
**N01** retains native selection/permission/accessibility proof. See
[P11 deferred acceptance](../testing/p11-deferred-acceptance.md) and
[provider preparation](../operations/providers-and-webhooks.md). No live account,
storage bucket, endpoint, database or Railway resource was accessed or changed
for this research.
