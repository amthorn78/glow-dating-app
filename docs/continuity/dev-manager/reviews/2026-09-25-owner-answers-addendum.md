# Addendum: Nathan's answers to the two follow-up questions

- **Source:** Nathan Amthor, in the Dev Manager session on 25 September 2026. He was answering the two questions at the end of [the owner-answers report](2026-09-25-owner-answers-to-dm-01-dm-02.md), which was pushed at `574ee0e`. That report stays as written; this file adds to it.
- **Consultation ID:** none. This is owner input.

## Answers, word for word

1. **The Stream secret (A5):** *"I don't know technically enough, this a question to explore with the app manager sessions"*
2. **The HDE and integration owners (A7):** *"there is only one human involved in any of this, me"*

## What follows

### A5 — The Stream secret goes to the primary manager to explore

- **Nathan's instruction.** He is not choosing an option. He asks the app manager sessions to explore the question.
- **What the primary manager should bring back.** A recommendation in plain terms that Nathan can accept or reject without technical knowledge:
  - what each option protects;
  - what it costs Nathan in clicks per session;
  - what could go wrong.
- **The inputs the primary manager already has:** the three options in A5, and the constraint Nathan set, "the simplest setup that protects the secret". A separate environment is acceptable only if nothing simpler is safe.
- **What it may verify:**
  - whether one cloud environment can give a variable to only some sessions. I could not confirm this;
  - the GitHub plan facts, but only if CI ever needs the secret. It does not today.
- **Until it is decided, the current setup stands.** Every session in the `Glow app` environment can read the development secret. The impact is low: a development application holding synthetic data only.
- **Timing:**
  - This does not block the I1 review, which needs the secret in its session anyway.
  - It should be settled before P06.1-I2a, the next live session after the review.
  - The rotation of the development secret at P06.1's close stands in any case.
- **Documents:** the P06.1 brief or the current handoff (a next action for the primary manager), and `docs/operations/environment-inventory.md` once decided.

### A7 — One person holds every role

- **The roles.** Nathan is the Product Owner, the HDE owner and the dating app's integration owner. The request to "obtain a date from the HDE owner" is therefore a scheduling decision Nathan makes for himself. No other person can supply the date.
- **The practical path, within D08's protection of HDE:**
  1. **The primary manager** writes the contract-requirements document from PF01 §5 "Before live integration" and A07. This is application-side and ordinary documentation. It lists what the app needs:
     - the supported interface and version;
     - the release or environment;
     - the authorized access;
     - idempotency, rate limits, retries and errors;
     - output and cache rights;
     - deletion obligations;
     - throughput and granularity.
  2. **Nathan** takes it to HDE's own process, outside this repository and outside the app sessions' authority, and sets a delivery date there. HDE's own sessions and canon produce the versioned contract.
  3. **On delivery,** the app records its receipt (version, HDE release or commit, environment, access described by name only, date), with HDE's text governed by HDE. That is as A7 describes.
- **Until Nathan sets a date,** A01 and A07 stay Blocked with "date not yet set", and P11B's live HDE checks stay gated. No other work waits on this.
- **One consequence worth recording now (for P07, not a question today):** PF01 assumes named people for several operating duties:
  - moderation;
  - urgent escalation;
  - child-safety duties;
  - support;
  - appeals.

  With one human, all of them fall to Nathan (A05, R05). The P07 brief should plan for that capacity explicitly: what can be automated, what response times one person can meet, and what must be in place before launch. It should not assume a team.
- **Documents:**
  - **The owner-direction register:** a row recording that Nathan holds every human role;
  - **A01, A05 and A07 in PF01 §10:** the owner named;
  - **R05:** the single-operator note;
  - **A new file:** the contract-requirements document, `docs/planning/hde-contract-request.md` or similar;
  - **The current handoff:** the next actions.

## Questions for Nathan

None now. The Stream-secret question returns to Nathan as the primary manager's recommendation. The HDE date is his to set once the requirements document exists.

Status: complete
