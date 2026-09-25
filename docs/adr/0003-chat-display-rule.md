# ADR 0003: The chat display rule and "nothing outside Glow"

Date: 2026-09-25
Status: Accepted by Nathan. Conditional on the exact-head review of P06.1-I1 confirming finding S15 live. The carve-outs below await Nathan's confirmation.
Work item: P06.1 — Prove chat-provider permissions and economics

## Context

P06.1-I1 proved Stream Chat's permission model against Nathan's development application 1729640; the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md) has the details. One bypass remained that configuration did not close:

- **S15.** A member's client can write up to 5 KB of free text as custom data on its own membership of its match channel (`updateMemberPartial`). The other member's client receives it in its ordinary channel query and in realtime `member.updated` events.
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
4. **Proposed carve-outs, awaiting Nathan's confirmation** (DM-02 question 1):
   - legally required disclosures, such as privacy policies, store privacy labels, processor lists, and data-export contents where the law requires recipients;
   - licence notices;
   - system screens the platform mandates, such as permission dialogs, store purchase sheets and platform sign-in flows.

   Until Nathan confirms, no session hides a legally required disclosure or treats a mandated system screen as a defect.

## Why the display rule, and its limits

- **What it relies on.** The rule relies on the recipient's app, which the writer cannot change. PF01's concern is a client the attacker controls. The residual channel needs two currently matched people who both run modified apps, and it gives them nothing they could not do outside Glow.
- **What it costs.** Nothing at the provider: one client rule, its test in P06.2, and the consumer rule above.
- **What it is not.** The rule is a user-experience and safety rule. It is not a provider-level control, and the development application's lockdown is not a production control.

## Conditions (DM-02 B7)

- **(a)** P06.1-I2a shows that member custom data cannot change anything Glow displays or forwards, and that revocation ends the write.
- **(b)** Deletion and export (PV07) include member custom data held at Stream.
- **(c)** I1's configuration becomes a reviewed, reapplicable plan for the production application, in `docs/architecture/chat-provider-permissions.md` (P06.1-I2b).
- **(d)** One channel per person stays the recorded fallback if condition (a) fails. So does a provider-level closure, if Nathan wants one.

## Consequences

- **P06.2:**
  - the chat UI renders only Glow API data, with a test that proves it;
  - Stream user IDs are random and opaque, never derived from Glow's account IDs, names or emails, and never shown to users;
  - provider errors reach users only as Glow's own messages.
- **P06.3:** notification content comes only from Glow's server path, never from Stream's push.
- **P07 and P08:** staff views, exports and deletion follow the consumer rule and condition (b).
- **Later phases:** the principle applies to every provider surface, including media, mail, authentication and billing.

## Revisit when

- the exact-head review narrows S15 or finds a configuration that closes it;
- P06.1-I2a fails condition (a);
- Stream adds a setting that disables client writes to member custom data;
- Nathan decides the carve-outs.
