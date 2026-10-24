# DM-21 — PR31's governing read: OD-45

- **Consultation:** DM-21, revision 1, from App Manager 7, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, branch `claude/dev-manager`.
- **Commit read:** `016e9fe7d94e5bec2d97f89da10ecac0b61ebfc9`, the head of `claude/magical-wozniak-yfmmx2` (draft PR31) when I fetched it. **This read covers `016e9fe`** (DM-03 G2).
- **Environment (names only):** `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are present, never read or used. No HDE name is present.
- **What I did not do:** I called no provider, database, HDE or Railway, and ran no repository code. The code passes B2-C4 and B2-C5 and their reviews are outside this read, as the consultation says.

## 1. What I read

**At `016e9fe`:**

- **The governing diff `050a37e..016e9fe`,** over the consultation's paths and the environment inventory: one added row, OD-45.
- **Every changed path in `050a37e..016e9fe`,** filtered for governing files:
  - any `AGENTS.md` or `CLAUDE.md`;
  - `.claude/`;
  - `docs/pf-canon`;
  - the manager workflow;
  - the charter;
  - the CI policy;
  - the register;
  - the environment inventory;
  - the start prompts.
- **The D8 message, revision 2.** Its body is identical to my DM-20 section 7, ignoring blank lines (checked with `diff`).
- **OD-45's homes:**
  - the brief's Status line (revision 11, carrying revision 9's sentence), D8, items 4 and 5, and "Nathan's answer" under "The client-token question (D8)";
  - ADR 0003's "Revisit when", and its decisions 1 to 4 for context;
  - the P11 plan's provider-configuration bullets.
- **The charter's line on Nathan's authority:** "Final authority on product, scope, spending, risk acceptance and process".
- **PR31's governing commits since `main` (`3272eed`),** per governing file, to check coverage (item 3).
- **DM-20 6.1's application in the architecture document's section 5,** at a glance: applied as written.

**Notion, read-only, 24 October:**

- the owner-direction register copy;
- *Implementation Control*;
- the Work Register's P06.2 row;
- *Dev Manager — reviews and approvals*.

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 OD-45's row | **Approved with condition 1.1:** its "State" cell in the words below. The quote and the date are right. Two of the three readings claim more than Nathan said |
| 2 OD-45's homes | **Approved with conditions 2.1 to 2.4.** The brief's Status line and D8 are approved as written |
| 3 Coverage | **Confirmed.** The OD-45 row is the only governing change since `050a37e`. With DM-16 to DM-21, every governing commit in PR31 has been read or confirmed as applied |
| 4 Notion | **No mismatch,** and one formatting nit |

- **What needs no further read:** the conditions applied as written (the charter's exception). PR31's governing Markdown then needs no further read before the merge.
- **What goes to Nathan:** no item. The conditions keep the record to his words and the charter.

## 3. Item 1 — OD-45's row: approved with condition 1.1

**The quote.**

- The row's quote is the same, character for character, as the consultation's, the brief's D8 and ADR 0003's: *"b, and I do think the stream architecture is still better than building our own, but I don't want features "snuck" in for sure"*. That includes the lower-case "stream" and the inner quotation marks.
- Nathan answered in App Manager 7's session, so I can check the quote only against the relayed text, not against his message itself.
- The date (24 October 2026) and the source (the message's revision 2, in DM-20's words) are right.

**The "State", reading by reading:**

- **"D8 is decided as option (b): the app holds no Stream credential."** His "b" supports it. So do the two sentences after it, which describe (b) as the message put it.
- **"Stream stays the provider … : Glow does not build its own message store."** The first half is a fair reading: his view that "the stream architecture is still better than building our own" answers the message's later question ("whether Stream is still worth its cost"). The second half turns a view into a prohibition he did not give, in words he did not use. It could also be read against what Glow already keeps, such as its accepted `MessageSubmission` rows (the brief's item 5). It should state his view as his view, and the design as option (b) was costed.
- **The three readings of "I don't want features 'snuck' in for sure":**
  - **The drift check is required.** Supported. The check is the only means of knowing that nothing was added, and his words raise it from DM-20's "hygiene" to a requirement. The row should name the check as the means (DM-17 item 6), so that a later change of means is not read as a change to his direction.
  - **A Stream addition is locked when it is detected.** This claims more than he said, and it contradicts how additions have been handled. D3's `lifecycle` sections were recorded in the 23 October baseline, not locked (DM-17), and D6's `blocklist_behavior` was accepted (DM-19). Some additions have no "locked" state at all. The reading his words support is that nothing Stream adds stays in effect for Glow without a recorded decision: it is turned off, or kept by a decision.
  - **A provider feature is turned on for Glow only by a recorded decision.** Supported. The row should also say whose decision it is when the feature changes what members see or what is done with their messages. That is a product decision, and the charter makes product and scope Nathan's. This applies the charter; it adds no new rule.
- **Does the row add a rule he has not directed?**
  - The prohibition on a message store does.
  - "Locked when detected", stated without the decision alternative, does.
  - "Before each deploy and on a schedule with an alert" is DM-17 item 6's approved design. It is fine when attributed to that design.

**1.1 The row's "State" cell reads as follows.** The ID, date, direction and home cells stay.

> In force. **D8 is decided as option (b): the app holds no Stream credential.** Glow's API serves conversation history and new messages to the app itself; every message still goes through Glow's server. **Stream stays the provider** behind Glow's server, as option (b) was costed (the provider keeps owning retained history); in Nathan's words, the Stream architecture is still better than building Glow's own. **No provider feature is "snuck" in:** a feature Stream adds takes effect for Glow only by a recorded decision. The means is the drift check that DM-17 item 6 approved, now required: it compares Stream's configuration with the last accepted record before each deploy and on a schedule, with an alert (its scope is in the P11 plan). A detected addition is turned off where the configuration targets name it, or kept only by a recorded decision, as D3 and D6 were; a feature that would change what members see, or what is done with their messages, is Nathan's to decide (the charter: product and scope are his). ADR 0003's D8 alternative is adopted; Stage C and the P11 plan change shape (the P06.2 brief's "The client-token question (D8)"); PF01 section 4's Chat row changes with Stage C's brief revision, for the Dev Manager's read. The socket or the lighter start (notifications plus polling) stays a technical choice for the brief, shown to Nathan in the P11 plan (DM-20 item 4)

## 4. Item 2 — OD-45's homes: approved with conditions

**Approved as written:**

- **The brief's Status line** (revision 9's sentence, carried in revision 11's line): "the app holds no Stream credential, Glow's API serves history and new messages, Stream stays the provider behind Glow's server, and no provider feature may reach members unannounced".
- **The brief's D8:** "the drift check is required so that no provider feature reaches members unannounced". Its note that the text below is the design before the decision is also right.
- **Items 4 and 5:** the token rules are marked superseded for the app and kept dormant, and Stage C changes shape. Both are consistent with DM-20's note.

**Conditions:**

- **2.1 The brief's "Nathan's answer" paragraph and the P11 plan's drift-check bullet take 1.1's reading of the response to a detected addition.** Both say "a detected (Stream) addition is locked". Each reads instead: "a detected addition is turned off where the configuration targets name it, or kept only by a recorded decision, as D3 and D6 were; a feature that would change what members see, or what is done with their messages, is Nathan's to decide (the charter)".
- **2.2 The P11 bullet states the scope of the required check.** It currently describes the drift check as "the chat target's generic coverage … with the Video and Feeds target".
  - Those targets check what they name. Since DM-17 2.3, what they do not name is seen only by the full comparison, and OD-45 is about features, not only grants.
  - The bullet adds: "Under OD-45 the check also compares Stream's whole configuration (every application key, and every channel type, call type, feed visibility and feed group, with their fields) with the last accepted record, as `full-view` and `compare-views` do. So an added settings key, section, type or feature is detected, not only a grant."
- **2.3 ADR 0003's "Decided" bullet: "under (b) the app receives no Stream data at all".**
  - This is loose. The app still shows message text and timestamps that Stream holds, served through Glow's API.
  - It reads: "under (b) the app holds no Stream credential or connection, and receives no Stream object or field: the message text and timestamps it shows reach it only through Glow's API, which forwards only the fields Glow names (decision 2 governs that endpoint)".
- **2.4 The brief's "Nathan's answer" paragraph: "(a) with its safeguards stays the fallback, and is Nathan's risk acceptance."** That was the position before his answer. It reads: "(a) with its safeguards was the fallback".

## 5. Item 3 — coverage: confirmed

**Since `050a37e`:** `git diff --name-only 050a37e 016e9fe`, filtered for governing paths (item 1 of section 1), prints only `docs/continuity/owner-directions.md`. Its diff is the OD-45 row and nothing else. The environment inventory, the start prompts and every `AGENTS.md` and `CLAUDE.md` are unchanged.

**Since `main` (`3272eed`), PR31's governing commits and the read that covers each:**

| Commit | Governing change | Covered by |
|---|---|---|
| `3120904` | OD-41: the register, the workflow's step 7, the CI policy | DM-16 (item 7, approved) |
| `2f62b1e` | the workflow's step 3, the TypeSafe sentence | DM-16 (7.1, 7.2) |
| `2542a06` | OD-42, and step 3 applying DM-16 | applied as written; DM-17 confirmed it |
| `5ae3c23` | the CI policy's timeout clause (DM-16 item 6) | DM-17 (its governing diff `2f62b1e..5ae3c23`) |
| `9371e24`, `d9f6c1e` | OD-43: the register, step 3, the environment inventory | DM-18 |
| `4bf973d` | OD-44's row | DM-18 |
| `34f494c` | step 5's push-filter bullet | DM-18 (6.1) |
| `4de03c1` | 6.1 and 7.1 applied; the environment inventory's clause | DM-19 (item 6, confirmed) |
| `51844a5` | OD-45's row | this read (1.1) |

**What follows:** with 1.1 applied as written, PR31's governing Markdown needs no further read. Any other governing change before the merge would need one.

## 6. Item 4 — Notion: no mismatch

- **The owner-direction register copy:** matched to `51844a5`. The register is unchanged from `51844a5` to `016e9fe`, and the copy's OD-45 row equals the repository's. After 1.1, the copy takes the new "State".
- ***Implementation Control*:** "Current status — 24 October 2026 (App Manager 7; P06.2: code reviewed; DM-21, the governing read of OD-45, with Nathan)", last matched to `016e9fe`. Its account matches the repository: B2-C5's re-review, records only, with the code fix carried to P11; the run of record 40054102314; DM-21; then Codex, the final run and the merge.
- **The Work Register's P06.2 row:** "In progress". It carries DM-20 (`ca806e3`, merge `855a92b`), OD-45, the review, B2-C4, B2-C5 and their re-reviews, as the record does. Next: DM-21, Codex, the final run, the checklist and the merge, then Stage C under OD-45.
- ***Dev Manager — reviews and approvals*:**
  - DM-20's row carries its verdicts and the disposition, "considered … at `fec4e6f` (merge `855a92b`)". Both commits are in the manager branch's history.
  - DM-21's row reads pending.
  - **Nit:** the review log's DM-21 row has six cells under a seven-column header, and Notion's shows an empty Disposition cell. That fills in when the disposition is recorded.

## 7. Where each condition goes

- **The owner-direction register:** 1.1 in OD-45's "State", then the Notion copy.
- **The brief, "Nathan's answer":** 2.1 and 2.4.
- **The P11 plan's drift-check bullet:** 2.1 and 2.2.
- **ADR 0003's "Decided" bullet:** 2.3.

Status: complete
