# Carried to later items

This file holds what a later work item must take up when that item has no brief yet. Each section names the item, and each entry names its source. When the item's brief is written, the brief folds its section in and this file keeps a pointer to the brief. The item's Work Register row points here (the manager workflow, "Batching records"; DM-31 3.6, which closes the gap M05 finding 42 found: DM-02's items for P07 had no home and were nearly lost).

## From P09.3a's matrix: rules for every brief that takes a row (DM-37)

The [store, legal and safety requirements matrix](store-legal-safety-requirements.md) holds each requirement and gap; the sections below point to its gap IDs (G-01 to G-16) and rows. Every brief that takes a row:

- **rechecks the row on the day the brief is written** (DM-37 5.1), on any trigger in the matrix's section 10 (5.2), not only PF01 §7's points;
- **states the condition it assumes** (for example "UK links", "covered platform", "social media platform"), and never says Glow is, or would be, compliant: the matrix is a dated record, not an applicability finding (DM-37 1.1);
- **re-reads the original or plans for the stricter reading** of an UNCONFIRMED row or a quote read only through WebFetch; for example, UK-05's 48-hour duty is treated as in force (DM-37 1.2).

## Carried to P07 (safety, WordPress operations and support)

- **From DM-45 9.1** (the SV1 brief's D7): the interactions design keeps unmatch "reachable … for valid-session suspended or deletion-pending actors" (`interactions-fixtures.md`), and the mobile guard lets them open `/matches`, but neither `glow_chat`'s `open_session` nor SV1 gives such an actor a session. SV1 keeps that fail-closed default. P07's brief decides whether a suspended or deletion-pending member gets a restricted cleanup session, and puts it to Nathan if it changes what members can do. P07's moderation route also holds F01's `suspend` rule (from `active` only, role `moderator`, policy A05): `glow_chat`'s `suspend` checks only that the account is not being deleted.
- **WordPress for staff** (DM-02 B5; recorded as A4 under OD-19, "the Dev Manager's safeguards go to the P07 brief"): if WordPress stays for staff, the brief names its hosting, update policy, staff multi-factor authentication and plugin allowlist.
- **Stream's terms, section 6.2** (the customer's access and moderation duty; DM-07 item 5): Glow meets it with its own terms and moderation. Before the brief relies on that, it reads the clause in Stream's exact words.
- **The history read's policy question** (DM-22 3.1; the [P11 plan](../testing/p11-deferred-acceptance.md)): if P07 comes before P11 serves the reads, P07's brief takes the A05 question to Nathan in OD-32's form.
- **A second block writer's proof case** (M05 finding 25): three `glow_chat` revocation checks (`contact.py:490-498`, `reads.py:289-290`, `delivery.py:265`) cannot fail today, because a block always restricts the match through the adapter's own writers. P07's block writer, or WordPress's, makes them reachable, so a proof case with a direct block row lands before it.
- **ADR 0003's condition (b)**, open for P07 and P08: deletion and export (PV07) include member custom data held at Stream. It lives on the membership of the match channel, and a hard delete removes the channel, so export reads the memberships first. ADR 0003's decision 2 also binds P07's views: no Stream member or user custom data reaches exports, staff or WordPress views, push content or analytics (DM-02 B1).
- **The disposable WordPress** (DM-31 3.2, on P-5): the brief shows that the disposable WordPress P07's completion names runs in CI at no cost, or brings a fallback to the Dev Manager.
- **The standing guard** for an older page answered `stale_version` (DM-30 1.1 and 1.2): moderation that removes a message from a readable conversation triggers it. Its text is in the P11 plan, "Standing guard".
- **The open A05 questions go to Nathan before this brief** (OD-50; PF01 A05), each in OD-32's form, in three messages (DM-37 4.1 to 4.5): first, launch geography and language, age assurance, and where the business is established and whether it is an individual or a legal entity, **answered in OD-55** (a US legal entity; the US, all states, in English, for now; a self-entered birth date plus the stores' age signals); second, before SV2's brief, the preference taxonomy, resurfacing and rematch, and the history policy; third, before this brief, retention and moderation operators. The history read's question above is the second message's history policy.
- **From P09.3a's matrix** ([the matrix](store-legal-safety-requirements.md), section 8; DM-37 2.1 to 2.6):
  - **P07.1:** G-02 (CSAM detection choice, reporting routes, registrations and named contacts, report evidence, staff access); G-04's notices, pages, policies and filings (state dating-safety notices, Colorado's filing and report, 47 U.S.C. 230(d)'s notice); G-06 (the UK Online Safety Act documents), carried, conditional, to a UK launch, since the UK is not a launch country for now (OD-55); G-05's trigger: a CyberTipline or NCA report opens a hold (USF-04, UK-18), which P08.1 designs and P08.2 enforces (2.4).
  - **P07.2:** G-03 (intimate-image notice and removal, 48 hours) and G-15 (notices from non-users, statements of reasons) share one route for non-users, in the app and on the public site; P07's brief says which sub-item builds it (2.6). G-04's fraud-ban notices, from SV4's recipient records.
  - **P07's capacity plan** (R05 asks for it) names the 48-hour clock for one operator (2.5). PV04 covers photo detection; chat detection, if chosen, needs its own P11 case (2.6).
  - **Statutory notice text:** when a statute prescribes a notice's wording (UST-01 to UST-21), P07.1 takes the text from the statute, not from the matrix's quote (DM-37 1.2).
  - **The launch country is the US, all states, for now (OD-55):** the brief takes the matrix's store, US federal and US state rows; the UK and EU rows wait for a launch decision there.
  - **Before this brief:** P07's rows for the launch countries that are UNCONFIRMED, or rest on a source not read (Ofcom's and the ICO's guidance, New York's SAFE rule text, Connecticut's 2026 acts, New Jersey's current code), are re-read from their originals, by Nathan's CLI agent if the cloud still cannot reach them (OD-43); otherwise the brief carries them as UNCONFIRMED (DM-37 5.3). The UK's 6 and 12 November 2026 events (UK-22, UK-23) are read then, for a UK launch.
  - **PF01 §7's release gate** (1.17; DM-37 2.7) is in force before this brief: a request to publish, invite external testers or enable public traffic lists each binding row with its state.

## Carried to P08 (privacy lifecycle and conditional monetization)

- **From SV1** (the SV1 brief's D5): allauth's `UserSession` rows record each sign-in's IP address and user agent, and hold the session key. They are personal data; P08 sets their retention and their place in export and deletion.
- **The standing guard** (DM-30 1.1 and 1.2): deletion that removes an accepted message from a readable conversation triggers it. Its text is in the P11 plan, "Standing guard".
- **ADR 0003's condition (b)** (open for P07 and P08): as in P07's section; P08's deletion orchestration takes it if P07 has not.
- **The message spool's retention** (M05 finding 23): `MessageSubmission.text` is kept on every accepted submission. The retention decision, and deletion and export while it is kept, are in the P11 plan, "The message spool", and the privacy rules' spool row.
- **From P09.3a's matrix** ([the matrix](store-legal-safety-requirements.md), section 8; DM-37 2.1 to 2.6):
  - **P08.1:** G-05's hold design (P08.2 enforces it against deletion; the P11 plan's PV07 is extended to holds); G-09 (GDPR and UK GDPR representatives, the DSA's contact points and legal representative, the intake for authority orders), carried, conditional, to a UK or EU launch, since Glow is a US company launching in the US for now (OD-55), with a representative's cost in M07 then; G-11 (DPIA, records of processing, the DPO decision, automated decisions, transfers, breach procedure, UK complaints), with P09 keeping incident escalation. It reads SV4's G-12 classification.
  - **P08.3:** G-07 (consumer and subscription law), only if Nathan chooses a paid launch (A06); no PF01 line now.
- **A DPIA at a UK or EU launch** (DM-38 section 8): whether one is needed is read from the matrix's DPIA tests ("likely high risk", "large scale": EU-25, EU-46, EU-47), not from App Manager 8's follow-up reply under OD-55, which said one is needed "since orientation data, matching and age checks are high-risk". No decision rested on that reply, since the launch is the US only (OD-55).

## Carried to SV1 (the identity slice; OD-49)

- **The brief is written:** [`sv1-identity.md`](sv1-identity.md), revision 2 (9 November 2026), folds in each entry below (the threat model in its review plan; G-01 in D9; G-13 and G-14 in D13; G-04 in D8). DM-45 approved revision 1 with conditions; revision 2 applies them and is back with the Dev Manager as DM-46 (DM-45 1.1).
- **A written threat model** in SV1's exact-head review (DM-31 item 3), since Codex's security reviews are no longer available (OD-41).
- **Its brief goes to the Dev Manager:** django-allauth headless is a significant new dependency and sign-in is a security boundary (DM-31 item 3; the charter). The same holds for each slice's brief.
- **PF01's rules for every slice** (§8, "Server slices"): a disposable PostgreSQL in CI under P06.DB's rules, CI-generated credentials, the runtime guards kept, and the runtime sealed until P11.
- **From P09.3a's matrix** ([the matrix](store-legal-safety-requirements.md), section 8; DM-37 2.1, 2.2 and 3.2). SV1 keeps room for these and builds none of the owning briefs' work:
  - **G-01's age state:** the account's recorded age state. Nathan answered (OD-55): a self-entered birth date plus the stores' age signals where the law requires them; SV1 holds the age state behind a seam, so a stronger check can be added without rework (DM-37 3.2). G-01's umbrella row in the Work Register tracks the parts.
  - **G-13:** Google's Restore Credentials for apps with sign-in, from April 2027 (GP-36), as SV1's scope. **Not SV1's** (DM-45 13.1; the SV1 brief's D13): G-13 has a server part, a WebAuthn relying party that gives the new device a new session, and a native part. Both are carried to P09.2 below.
  - **G-14:** any review sign-in path for the stores' reviewers goes inside SV1's threat model; P09 owns the reviewer account.
  - **G-04:** Vermont's account-change notice.

## Carried to SV2 (profiles and media; OD-49)

- **From P09.3a's matrix** ([the matrix](store-legal-safety-requirements.md), section 8; DM-37 2.1):
  - **G-02's seam:** the media quarantine path keeps a place for a detection step, its report evidence and a hold; it builds none of them.
  - **G-10** (explicit consent for orientation-revealing fields, the lawful-basis map, disclosures, device-storage consent, a recorded no-sale rule), after Nathan's A05 answer on the preference taxonomy.

## Carried to SV3 (eligibility, discovery and interactions; OD-49)

- **From P09.3a's matrix** (DM-37 2.2): eligibility reads G-01's account age state. Without an answer on resurfacing and rematch, the brief keeps the recorded defaults and says so: no resurfacing or rematch (the interactions fixtures) (4.5).

## Carried to SV4 (chat's HTTP surface; OD-49)

- **From P09.3a's matrix** ([the matrix](store-legal-safety-requirements.md), section 8; DM-37 2.1 and 2.3):
  - **G-04's records:** who received (and responded to) a member's messages, kept after unmatch and block, for fraud-ban notices.
  - **G-05's hold:** a hold that survives deletion, which P08.1 designs.
  - **G-12** is carried, conditional, to an EU launch, since the EU is not a launch country for now (OD-55). At an EU launch it is the recorded classification of whether the chat is a number-independent interpersonal communications service. It decides whether ePrivacy's confidentiality rule covers what SV4 stores (EU-30), including the conversations OD-12 keeps for safety reports, and whether chat scanning needs Regulation 2026/1881's conditions (EU-26). P07.1 and P08.1 read it then.
  - **Without an answer on the history policy,** the brief keeps the recorded default and says so: reads refuse whatever refuses a send (the P11 plan) (4.5).
- **From P06.3** (DM-44 item 7): F12's HTTP surface, its ORM adapters and the notification triggers' wiring, with the decisions P06.3's brief lists in D9: the contract and model fields' mapping (`push_enabled`, a platform, a `none` device state, a `rotate` action, the registration's session, which registration a read describes); the triggers' events (a message's acceptance writes none today; `match_activated` is settled when the chat worker creates the channel); and the system `logout` event's source (`session_revoked`, `session_expired`).
- **From P06.3's exact-head review, F-4** (the P06.3 record, "Exact-head review of P06.3"): the in-memory composer's `_fixed` set and ledger grow without bound (`notifications.py`); the serving slice gives the ledger its real storage, a bound and a retention.
- **From DM-44's optional item (4.1), not taken in P06.3:** whether turning every kind off also revokes the installation's registration and discards its token, so that Glow holds no token it does not use. F12 allows it (`revoke`). It is decided where real tokens first exist, here or in P09.2.

## Carried to the second A05 message (before SV2's brief; DM-37 4.5)

- **The language** (DM-38 section 8, optional): OD-55 records English as the recommendation Nathan did not change, not as his answer; the second message confirms it in one line.

## Carried to the next change to how the chat screens hold or render chat data (DM-38 2.5)

- **Its trigger:** a change to how `apps/mobile/src/chat/screen.tsx` or `rows.ts` hold or render chat data, for example a list component, grouping, or a helper or control that takes messages (P07.2's report from chat is one candidate). Not P06.3 by name: P06.3 is notifications.
- **What that change does** (option (c)): it builds view models by explicit field copy, as `rows.ts` does for the list; its render check becomes "no contract type reaches the screen", with planted forms; it gets a full exact-head review. Its brief may propose another design to the Dev Manager.
- **The backstop** (DM-39 3.1): if the trigger is missed, (c) lands before P11 serves the chat reads, at the latest (the P11 plan, the chat section).
- **Every brief that touches `src/chat/screen.tsx` or `rows.ts`** says whether this trigger applies, P06.3's included (DM-39 3.2).
- **What (c)'s brief takes** (DM-39 1.3), from the P06.2-F record's "Correction C2" and DM-39 section 3: C2's 49 passing forms in nine classes (N1 to N9; N1's X2 an intermediate component with a narrower prop) as forms its check must refuse; the session's candidate's three rules with their measured results; that a narrower type built from the contract's own (`Pick<>`, `Omit<>`) keeps Glow's identity while one declared outside does not; and today's harmless controls (the candidate's five, F0's `FlatList` family) as forms its check must pass.
- **What (c)'s brief also takes** (DM-40 1.3, 1.4 and item 4), from the P06.2-F record's "Delta re-review of correction C3" and DM-40 section 3:
  - **forms its check must refuse:** the review's findings 1 to 4 (an object literal's method shorthand and its JSX-prop, overloaded-interface, class-instance and `rows.ts` variants; a contextually typed parameter's destructuring default; a destructuring target in a `for…of` head; the source check's text-match misses) and O5 (a reflective global through a union-typed key); DM-40's F1c (an accessor), F1d (a class instance), G2 (an untyped literal given later) and G3 (a class field);
  - **the refusals no planted form pins** (the test comment's brackets), which its planted forms cover;
  - **three code fixes, noted and not made** (DM-40 1.4): exempt only a destructuring pattern typed as Glow's data; refuse a `for…of` head whose target is a literal; compare an object literal's method against its contextual property type;
  - **forms by class and ID,** with the duplicate IDs named (C2's `R3` and `R6`) and C2's 49th form placed in N4 or N5 (the record, "Correction C4").
- **What (c)'s brief also takes** (DM-42 1.3), from the P06.2-F record's "Review of C4 and repair pass C5" and DM-42 section 1: forms its check must refuse, F1 (a function expression with a declared `this` parameter), F2 (a parameter after a rest parameter of the contextual signature) and F3 (a declared `this` against a signature with no parameter in the first place), and T1 from the record's "Correction C6" (a declared `this` against a signature whose only parameter is a rest parameter: `const both: (...entries: ConversationMessage[]) => string = function (this: void, first: Loose) { return first.name ?? ''; }`, then `both(message)`), and from the record's "Delta review of correction C6": TU1 (a tuple rest, F2's class) and F-1's R1, R3 and R4 (at a rest parameter's place the inline rule compares with the rest's array type, not its element, so `(first: { at: string; length?: number })` against `(...entries: ConversationMessage[]) => string` passes), with H1, a harmless `(first: ConversationMessage)` at a rest place that the same comparison refuses; and from the record's "Delta review of correction C7", forms that pass as C7's words give: X9 (T1's form reading `first.name`), X5 (a tuple rest with R1's annotation), X2 (a union of two rest members), X4 (a `readonly` rest), X13 (`toString`, an array member's name) and X14 (R4 as a function expression); with the fix noted and not made: "pair a declared `this` with the contextual signature's `this`, and each later parameter through `parameterAt`, as the by-reference rule does".
- **Why:** the render-rule check after P06.2-F's C2 treats a value as Glow's data only while its type declares a field in a `GLOW_DATA` file; data held inside another value (a group or section, a list's render-item wrapper, a view-model object, a closure or a container) is a named limit that an ordinary refactor reaches, and a harmless `FlatList` over Glow's data fails it (P06.2-F record, "Delta re-review of correction C1"; DM-38 section 4).

## Carried to P06.3 (notifications)

- **From P09.3a's matrix** (DM-37 3.1): the brief rechecks AP-50, AP-51 and GP-51, all planned. **Done** on 8 November 2026: all three confirmed in the sources' own words ([recheck record](../testing/evidence/2026-11-08-p06-3-matrix-recheck.md)); the brief is [`p06-3-notifications.md`](p06-3-notifications.md).

## Carried to P09 (security, native quality and release preparation)

- **G-13, Restore Credentials, both parts, before April 2027** (DM-45 13.1; GP-36): Android's guide asks for a WebAuthn relying party server: the app registers a restore key after sign-in, and on a new device the server verifies its assertion and issues a new session. Raw authentication tokens stay out of the app's backup, and the restore key is deleted when the member signs out or the server ends the session. P09.2's brief names the server part's owner (through a maintained library; PF01 §4: no custom token cryptography) and builds the native part.
- **From P09.3a's matrix** ([the matrix](store-legal-safety-requirements.md), section 8; DM-37 2.1 and 2.2):
  - **G-01's store parts:** the native age signals in P09.2 (Apple's Declared Age Range, Google's Play Age Signals); Restrict Minor Access in Play Console (GP-11).
  - **G-14:** the reviewer account for both stores, which no fixture adapter or test-account privilege can turn into access to real users (PF01 P12).
  - **G-16:** EU monthly active recipients on request, UK monthly users against the thresholds, and evidence of micro or small status, in the observability scope.
  - **G-11's incident escalation** stays with P09.
- **From P06.3's exact-head review, F-5** (the P06.3 record, "Exact-head review of P06.3"): `NotificationStore.setKind` awaits `permission.request()` with no catch (`apps/mobile/src/notifications/store.ts`). P09.2's real permission seam handles a rejection, so that `busy` is reset and the member can try again; the fixture seam never rejects.
- **From C1's delta review of P06.3, N-1** (the P06.3 record, "Delta review of correction C1"): the notifications import scan's `SPECIFIER` (`apps/mobile/src/notifications/fixture-scope.test.ts`) accepts `'` and `"` but not backticks, as `src/chat/no-provider.test.ts` does, so ``import(`x`)`` and ``require(`x`)`` pass it, and its self-test's title says it reads every import form. When P09.2 adds `expo-notifications` behind the seam and rewrites this guard, the scan also takes backtick specifiers, and its self-test names the forms it reads.

## Carried to P09.3a (the store, legal and safety requirements matrix)

- **Folded into its brief,** [P09.3a](p09-3a-requirements-matrix.md): CSAM in scope as a requirement, not legal advice, an environment that reads the web, and the candidate countries (DM-31 items 3 to 5; OD-50).

## Carried to P06.2-T (M05's E7, the OD-45 token cleanup), with E15's refusal lists

- **The epoch-bump question** (DM-31 item 4): whether a session-epoch bump still revokes provider tokens once no client token exists. It is a security-boundary question, so it goes to the Dev Manager before P06.2-T's brief settles it.
- **The refusal lists** (M05 finding 22, E15): a `PG*` prefix rule and the Railway, Redis and `STREAM_*` names, in the API and in the database proof together. ADR 0004's sentence changes again when the list widens.
- **The API README's lines** (M05 P-13): the dormant signer's descriptions and Stage C1's modules.
- **The pin test's gap** (M05 finding 13; DM-32 1.11): `services/api/tests/test_toolchain_pins.py` does not read `proofs/stream-chat/package.json`, so a changed Node or npm pin there passes it. The test reads it, with a reversal that fails it. The bootstrap script's "both package.json files" wording stays with the M02 brief's hardening item, since a Setup-script change needs Nathan to paste it.

## Carried to the next change to the branch cleanup (M04's exact-head review)

Due with the first change to `scripts/branch_cleanup.py` after M04 merges ([the M04 record](../testing/evidence/2026-10-26-m04-branch-hygiene.md), "Exact-head review of M04"):

- **F4:** the git credential helper answers `get` for any host. It answers only when git's input names `host=github.com`, with a test.
- **F6:** four guards with no failing reversal get tests: the token mask in `diagnostic()`, the strict UTF-8 decode and the SHA check in `read_heads()`, and the non-printable escaping in `cell()`.
- **The re-review's nit 1:** F2's redirect test asserts `Refused` with its reason (`assertRaisesRegex(branch_cleanup.Refused, "HTTPError")`).
- **DM-33's log line** (item 2): print `deleting <name> at <head>` to the log just before each push, so that even a run killed during a push names that branch.

## Carried from DM-34's optional items (the CI policy's next change; the manager's next Notion batch)

- **The CI policy's gate sentence** (DM-34 3.1): in "Documentation and agent-review policy", "require the gate as well when enforceable repository controls become available" reads as if no control were available; under OD-52 they are, and Nathan chose none. The report's wording: "require the gate as well only if Nathan chooses enforced controls (OD-52 chose none), after the change DM-33 6.2 names". Due with the CI policy's next change.
- **The superseded copy in Notion** (DM-34 section 5): Implementation Control's "Superseded: the full copy of the procedure" moves to a child page. It is most of the page, and it was the copy that drifted (M05 finding 30).

## Carried to P06.2-F (E11, the mobile hardening; from M06's exact-head review)

- **Folded into its brief,** [P06.2-F](p06-2-f-mobile-hardening.md), item 7, which chooses account entry, with the reset's generic error, as the landing (DM-36 section 6); done in its code head `3db50d8`, with both assertions. The entries below stay until the item closes.

- **The failed-reset landing** (finding 6): on SDK 58 a member whose reset fails lands on account entry with the generic error, where SDK 57 fell back to recovery (Router 58 renders a redirect for a failed guard). E11 decides the landing, for example a failure branch in `reset-password.tsx` that sends the member to `/recovery`. Not `redirectTo="/recovery"`, which would race the reset's own `router.replace('/account')`. A change that alters what a guard allows goes to the Dev Manager.
- **Two assertions for that landing** (finding 5): the failure's alert is visible on account entry, and `page.getByTestId('screen-reset-password')` has a count of 0 without the visible filter, so the screen is shown unmounted, not just hidden (`rendered/onboarding.spec.ts:76-77` at `524d42f`).
- **E11's brief states the landing it chooses,** with these two assertions pinning it (DM-36 section 6).

## Carried to M07 (the costed list of completion's accounts and services; OD-50)

- **What it is** (M05 E3; PF01 A04): before P09 and P11B, a list of each account and service completion needs (Apple and Google developer accounts, Railway app services, the Stream production plan, Cloudflare, mail and push), each with its published price rechecked and dated.
- **Research only:** no account is created and nothing is spent before Nathan approves its line, when its phase needs it; OD-12's $0 stands until then (DM-31, on N2).
- **The Stream line** depends on the Maker application, pending since 25 September 2026 (OD-22; confirmed pending in OD-50).
- **Its environment** must read public price pages (OD-40, OD-43), as the matrix's must.
- **GitHub Actions minutes** (OD-51): the repository is public for now only for budget reasons, and Nathan intends to make it private again. Private, it gets GitHub Free's 2,000 Actions minutes a month, then $0.006 a minute on Linux, and CI is blocked once they are used if no payment method is on file (GitHub's documentation, read on 26 October 2026). October's use was past 2,000 minutes (DM-32 3.4's estimate). So the list carries an Actions line, priced from the month's measured use, with the cheaper options beside it: fewer runs, or a paid plan.
- **From P09.3a's matrix** ([the matrix](store-legal-safety-requirements.md), section 8; DM-37 2.5 and 5.4):
  - **G-08:** the store and regulator account decisions (individual or organization, trader status, Android developer verification, Google's 12-tester closed test, the ICO fee), for Nathan to decide before any account is created.
  - **G-02's lines:** a detection-service line, and the registrations and named contacts (NCMEC, the NCA, Google's child-safety contact), as lines in M07's list, which A04 already names.
  - **OD-55's legal entity:** a US legal entity holds the store accounts and the service; its formation, and a D-U-N-S number for Apple's organization enrolment, are lines before those accounts (AP-57; G-08).
  - **G-09:** a representative service's cost, only for a later UK or EU launch (OD-55).
  - **Before Nathan approves an account's line,** that account's rows are rechecked: opening an account starts store deadlines, for example Google's trader declaration on account creation, and by 1 February 2027 at the latest (GP-59).
