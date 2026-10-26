# Carried to later items

This file holds what a later work item must take up when that item has no brief yet. Each section names the item, and each entry names its source. When the item's brief is written, the brief folds its section in and this file keeps a pointer to the brief. The item's Work Register row points here (the manager workflow, "Batching records"; DM-31 3.6, which closes the gap M05 finding 42 found: DM-02's items for P07 had no home and were nearly lost).

## Carried to P07 (safety, WordPress operations and support)

- **WordPress for staff** (DM-02 B5; recorded as A4 under OD-19, "the Dev Manager's safeguards go to the P07 brief"): if WordPress stays for staff, the brief names its hosting, update policy, staff multi-factor authentication and plugin allowlist.
- **Stream's terms, section 6.2** (the customer's access and moderation duty; DM-07 item 5): Glow meets it with its own terms and moderation. Before the brief relies on that, it reads the clause in Stream's exact words.
- **The history read's policy question** (DM-22 3.1; the [P11 plan](../testing/p11-deferred-acceptance.md)): if P07 comes before P11 serves the reads, P07's brief takes the A05 question to Nathan in OD-32's form.
- **A second block writer's proof case** (M05 finding 25): three `glow_chat` revocation checks (`contact.py:490-498`, `reads.py:289-290`, `delivery.py:265`) cannot fail today, because a block always restricts the match through the adapter's own writers. P07's block writer, or WordPress's, makes them reachable, so a proof case with a direct block row lands before it.
- **ADR 0003's condition (b)**, open for P07 and P08: deletion and export (PV07) include member custom data held at Stream. It lives on the membership of the match channel, and a hard delete removes the channel, so export reads the memberships first. ADR 0003's decision 2 also binds P07's views: no Stream member or user custom data reaches exports, staff or WordPress views, push content or analytics (DM-02 B1).
- **The disposable WordPress** (DM-31 3.2, on P-5): the brief shows that the disposable WordPress P07's completion names runs in CI at no cost, or brings a fallback to the Dev Manager.
- **The standing guard** for an older page answered `stale_version` (DM-30 1.1 and 1.2): moderation that removes a message from a readable conversation triggers it. Its text is in the P11 plan, "Standing guard".
- **The open A05 questions go to Nathan before this brief** (OD-50; PF01 A05), each in OD-32's form: launch geography (from the matrix's candidate list), age assurance, the preference taxonomy, resurfacing and rematch, the history policy, retention and moderation operators. The history read's question above is one of them.

## Carried to P08 (privacy lifecycle and conditional monetization)

- **The standing guard** (DM-30 1.1 and 1.2): deletion that removes an accepted message from a readable conversation triggers it. Its text is in the P11 plan, "Standing guard".
- **ADR 0003's condition (b)** (open for P07 and P08): as in P07's section; P08's deletion orchestration takes it if P07 has not.
- **The message spool's retention** (M05 finding 23): `MessageSubmission.text` is kept on every accepted submission. The retention decision, and deletion and export while it is kept, are in the P11 plan, "The message spool", and the privacy rules' spool row.

## Carried to SV1 (the identity slice; OD-49)

- **A written threat model** in SV1's exact-head review (DM-31 item 3), since Codex's security reviews are no longer available (OD-41).
- **Its brief goes to the Dev Manager:** django-allauth headless is a significant new dependency and sign-in is a security boundary (DM-31 item 3; the charter). The same holds for each slice's brief.
- **PF01's rules for every slice** (§8, "Server slices"): a disposable PostgreSQL in CI under P06.DB's rules, CI-generated credentials, the runtime guards kept, and the runtime sealed until P11.

## Carried to P09.3a (the store, legal and safety requirements matrix)

- **CSAM detection and the reporting duty** (M05 E6; DM-31 item 5) are inside the matrix's scope as a requirement, not an option.
- **It is research with dated sources, not legal advice,** and it says so (DM-31, on N4). Whether to take legal advice is Nathan's.
- **Its prompt names an environment that can read public web sources** (DM-31 item 4; OD-40, OD-43); `Glow App - No Stream`'s network policy may not allow it.
- **Its countries:** the candidate list Nathan chose, the US, the UK and the EU (OD-50, N4 (b)). He names the launch countries from it before P07's brief.

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

## Carried to M07 (the costed list of completion's accounts and services; OD-50)

- **What it is** (M05 E3; PF01 A04): before P09 and P11B, a list of each account and service completion needs (Apple and Google developer accounts, Railway app services, the Stream production plan, Cloudflare, mail and push), each with its published price rechecked and dated.
- **Research only:** no account is created and nothing is spent before Nathan approves its line, when its phase needs it; OD-12's $0 stands until then (DM-31, on N2).
- **The Stream line** depends on the Maker application, pending since 25 September 2026 (OD-22; confirmed pending in OD-50).
- **Its environment** must read public price pages (OD-40, OD-43), as the matrix's must.
- **GitHub Actions minutes** (OD-51): the repository is public for now only for budget reasons, and Nathan intends to make it private again. Private, it gets GitHub Free's 2,000 Actions minutes a month, then $0.006 a minute on Linux, and CI is blocked once they are used if no payment method is on file (GitHub's documentation, read on 26 October 2026). October's use was past 2,000 minutes (DM-32 3.4's estimate). So the list carries an Actions line, priced from the month's measured use, with the cheaper options beside it: fewer runs, or a paid plan.
