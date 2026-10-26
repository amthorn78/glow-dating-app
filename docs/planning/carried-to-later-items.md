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

## Carried to P08 (privacy lifecycle and conditional monetization)

- **The standing guard** (DM-30 1.1 and 1.2): deletion that removes an accepted message from a readable conversation triggers it. Its text is in the P11 plan, "Standing guard".
- **ADR 0003's condition (b)** (open for P07 and P08): as in P07's section; P08's deletion orchestration takes it if P07 has not.
- **The message spool's retention** (M05 finding 23): `MessageSubmission.text` is kept on every accepted submission. The retention decision, and deletion and export while it is kept, are in the P11 plan, "The message spool", and the privacy rules' spool row.

## Carried to P09.3a (the store, legal and safety requirements matrix)

- **CSAM detection and the reporting duty** (M05 E6; DM-31 item 5) are inside the matrix's scope as a requirement, not an option.
- **It is research with dated sources, not legal advice,** and it says so (DM-31, on N4). Whether to take legal advice is Nathan's.
- **Its prompt names an environment that can read public web sources** (DM-31 item 4; OD-40, OD-43); `Glow App - No Stream`'s network policy may not allow it.
- **Its countries** are the launch countries Nathan names, or the candidate list under comparison until he names them (N4).

## Carried to E7 (the OD-45 token cleanup), with E15's refusal lists

- **The epoch-bump question** (DM-31 item 4): whether a session-epoch bump still revokes provider tokens once no client token exists. It is a security-boundary question, so it goes to the Dev Manager before E7's brief settles it.
- **The refusal lists** (M05 finding 22, E15): a `PG*` prefix rule and the Railway, Redis and `STREAM_*` names, in the API and in the database proof together. ADR 0004's sentence changes again when the list widens.
- **The API README's lines** (M05 P-13): the dormant signer's descriptions and Stage C1's modules.
