# ADR 0003: The chat display rule and "nothing outside Glow"

Date: 2026-09-25
Status: Accepted by Nathan.

- **The display rule as S15's answer** stands. It was conditional on the exact-head review of P06.1-I1 confirming finding S15 live, and the review confirmed it on 25 September 2026, finding no configuration that closes it ([evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), "Exact-head review of I1").
- **The principle** (decision 3) is in force regardless of the review (DM-03 G4).
- **The exceptions** (decision 4) are confirmed by Nathan (OD-16, 25 September 2026).
Work item: P06.1 — Prove chat-provider permissions and economics

## Context

P06.1-I1 proved Stream Chat's permission model against Nathan's development application 1729640; the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md) has the details. One bypass remained that configuration did not close:

- **S15.** A member's client can write up to 5 KB of free text as custom data on its own membership of its match channel (`updateMemberPartial`). The other member's client receives it in its ordinary channel query, inside the members list.
- Stream's documentation says realtime `member.updated` events carry member custom data to clients watching the channel. Neither I1's runs nor the exact-head review established that path, because the harness could not tell which event carried the text (the review's finding 4). P06.1-I2a maps the event types.
- No Stream permission governs that write. Removing `read-channel-members` hid only the separate members endpoint.

PF01 section 7 treats a provider's inability to enforce safety as a design blocker, so the design or the provider had to change before P06.2. The options put to Nathan are in the [P06.1 brief](../planning/p06-1-chat-provider-proof.md), under "S15: decided":

1. a display rule;
2. one channel per person;
3. clearing the data by webhook;
4. another provider.

## Decision

Nathan, 25 September 2026: *"I accept your recommendation on S15. There should never be any indication that there is anything happening outside Glow."*

1. **The display rule.** The app never displays Stream user or member data. Every name, photo and profile field comes from Glow's API. The app ignores member custom data and `member.updated` events. Stream's settings that copy member custom data into messages, typing events and mentions stay off.
2. **Server and operator consumers.** Stream member or user custom data is never forwarded into exports, staff or WordPress views, push content or analytics (DM-02 B1). Otherwise the hidden channel would reach a person through Glow itself.
3. **The principle, product-wide.** Users never see a sign that anything happens outside Glow. No provider's name, branding, identifiers, error text, notifications or data reaches them; everything they see comes from Glow's API, in Glow's own wording. The scope is Glow's in-app experience and every communication Glow sends: push, email, in-app errors, deep links and the links users share. [PF01](../pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md) section 7 records the principle.
4. **The exceptions.** Nathan confirmed them on 25 September 2026 (OD-16): *"Yes. S15 must allow legally required disclosures, licence notices, and essential system screens. Compliance takes priority. Please document these as narrow, explicit exceptions and make the resulting screens clear and usable. An optional product screen should not be classified as an exception merely because it is convenient to do so."*

   The list is exhaustive:
   - **legally required disclosures,** such as privacy policies, store privacy labels, processor lists, and data-export contents where the law requires recipients;
   - **licence notices;**
   - **essential system screens:** screens the operating system or store requires and Glow cannot replace, such as permission dialogs, store purchase sheets and platform sign-in flows if social login is adopted.

   Each exception has two requirements:
   - **a named basis:** the law, store policy or platform requirement that makes it necessary;
   - **usability:** the resulting screen is clear and usable wherever Glow controls its presentation.

   **Nathan's test:** an optional product screen is not an exception because it is convenient. For example, a provider's hosted chat or payment widget chosen for convenience does not qualify.

## Why the display rule, and its limits

- **What it relies on.** The rule relies on the recipient's app, which the writer cannot change. PF01's concern is a client the attacker controls. The residual channel needs two currently matched people who both run modified apps, and it gives them nothing they could not do outside Glow.
- **What it costs.** Nothing at the provider: one client rule, its test in P06.2, and the consumer rule above.
- **What it is not.** The rule is a user-experience and safety rule. It is not a provider-level control, and the development application's lockdown is not a production control.

## Conditions (DM-02 B7)

Each condition has its status after P06.1-I2a and I2b, whose exact-head reviews confirmed their findings on 27 September 2026. The [architecture document](../architecture/chat-provider-permissions.md), section 4, keeps the detail and names the review that confirmed each finding.

- **(a)** P06.1-I2a shows that member custom data cannot change anything Glow displays or forwards, and that revocation ends the write.
  - **Status: met per mechanism, not as a whole.**
    - *Removal* and *deactivation* end the write (404 code 16; both meet the history policy in I2b's run). The *hard delete* ends it with the conversation.
    - *Per-user token revocation* ends it for existing tokens, but a token issued afterwards works, so Glow's token endpoint must refuse the user.
    - A *channel ban*, a *hide* and a *freeze* do not end it.
    - That the data cannot change anything Glow displays or forwards rests on decisions 1 and 2, which P06.2 and P07 implement and test. The proof shows only that the data reaches the other member's client.
- **(b)** Deletion and export (PV07) include member custom data held at Stream.
  - **Status: open for P07 and P08.** The proof shows where the data lives, on the membership of the match channel. A hard delete removes the channel, so export must read the memberships first.
- **(c)** I1's configuration becomes a reviewed, reapplicable plan for the production application, in `docs/architecture/chat-provider-permissions.md` (P06.1-I2b).
  - **Status: met.** The plan is the document's section 5; the harness's `configure` and `configure --products video,feeds` are its executable form, and I2b's review confirmed it. The re-read after the Video and Feeds apply compared only the client roles' grants (the review's finding 2). P06.1-C4 extended the harness's comparison to every role and setting the committed products baseline records; it runs at the harness's next live use, and no live read has made it yet. Until one does, that the other roles and the settings are unchanged rests on Stream's documentation. The Dev Manager's close-out read chose no live read in P06.1 (DM-07 item 4 (a), 29 September 2026; the C4 review's nit 3): P06.2's first live step runs the full comparison before any other live command, and its result closes this caveat, or stops P06.2 if it differs.
- **(d)** One channel per person stays the recorded fallback if condition (a) fails. So does a provider-level closure, if Nathan wants one.
  - **Status: recorded,** in the document's section 7. Condition (a) is met per mechanism only, so the fallback stands until P06.2 shows that the display rule holds.

## Consequences

- **P06.2:**
  - the chat UI renders only Glow API data, with a test that proves it;
  - Stream user IDs are random and opaque, never derived from Glow's account IDs, names or emails, and never shown to users;
  - provider errors reach users only as Glow's own messages.
- **P06.3:** notification content comes only from Glow's server path, never from Stream's push.
- **P07 and P08:** staff views, exports and deletion follow the consumer rule and condition (b).
- **Later phases:** the principle applies to every provider surface, including media, mail, authentication and billing.

## Revisit when

- a later run or review narrows S15 or finds a configuration that closes it (the I1 review confirmed S15 on 25 September 2026);
- Stream support says that the undocumented `channel_hide_members_only` setting keeps member data from other members;
- P06.2 cannot show that the display rule holds, which brings in the fallback of condition (d); or Glow's unmatch or block path comes to rely on a channel ban, a hide or a freeze, none of which ends the write;
- Stream adds a setting that disables client writes to member custom data;
- a design change opens a path to the other member that a design constraint now closes, not the display rule: an invite, or a call, feed or activity the server creates for a user (the architecture document, sections 3 and 6);
- an exception's basis changes, or a new one is proposed; only Nathan adds to the list.
- **What the client reads goes to Nathan** (DM-13 7.1; the [P06.2 brief](../planning/p06-2-chat-integration.md), D8). P06.2 keeps the client token with `read-channel` under this rule. If any of these comes true, the alternative (no client token, with Glow serving history and realtime itself) goes to Nathan in OD-32's form before the next stage:
  - the mobile client cannot be kept from holding or rendering SDK state beyond Glow's own view model;
  - a client-reachable path appears that the display rule or a design constraint does not close;
  - unread or read state needs a grant beyond `read-channel`.
