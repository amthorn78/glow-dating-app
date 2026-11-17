# DM-74 — SV3 Stage B: Codex's finding on PR47 (no read gives a client the directional version), before the exact-head review

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `6fa1b2c23bbc72ec2ce9e7ac7565634687db48b3` of `claude/magical-wozniak-yfmmx2`, which this read covers.
  - **The code** is Stage B's, `5d58993`, integrated by fast-forward. No non-Markdown path differs between `5d58993` and `6fa1b2c`.
  - **Since my last read (`1b331b2`):**
    - DM-73's records (`550e74f`), and Stage B's prompt, revision 2 (`2d8f28a`);
    - Stage B's commits on `claude/brave-brown-o90q6i`, from the merge into `29fad40` (`6544c2d`) to its records (`291edef`);
    - your verification (`622a4f4`), PR47 and Codex (`2316957`), and the PR's runs with this consultation (`6fa1b2c`).
  - **One governing path changed:** the CI policy's Database proof checks paragraph gains Stage B's sentence. As the consultation says, I read it at the pre-merge read, not now.
  - **Remote heads at 13:37 UTC** (`git ls-remote`):
    - `main` `947576d`, and the manager branch at `6fa1b2c`;
    - `claude/dev-manager` `7d219d0`;
    - Stage B's session branch at `291edef`.
- **Written:** 15 November 2026, finished at 13:43 UTC by the clock.
- **Boundaries kept:**
  - Environment names only: `DATABASE_URL`, `HD_API_KEY` and `GEO_API_KEY` are absent, and so are the `STREAM_*` and `PG*` names; the three AWS names are present, as recorded before. I read no value.
  - No provider, database, HDE, Railway, Cloudflare or TypeSafe call. No application code run, no test suite run, no database.
  - **What I ran,** with `python3`, from scripts kept outside the export: the scripts that check DM-73's words as applied and verify this report's words. Everything else was read, from git and the files.
  - Notion was read, not changed. I wrote only this file.

## 1. What I read

- **The consultation** (revision 1), and Codex's finding as quoted there and in the record.
- **The code at `5d58993`:**
  - in `glow_discovery/interactions.py`:
    - the like and pass (from `_account_of_profile` to the version check at line 307);
    - the block and unblock (line 518);
    - `_interaction_projection`, `_block_projection` and `read_match`;
  - `contract.card()`, and `interaction_urls.py`'s five routes;
  - the proof's `interaction_cases._version()`.
- **The contract's version rule:** `production-contracts.md` (lines 197 and 287), and `interactions-fixtures.md`'s "Version, digest and replay boundary".
- **The ordering suite's `cases.all_cases`,** to see where the F2 named cases run.
- **The brief's revision 15:** D13, the owned paths, the review plan, and the sections for B0 and Stage B.
- **The handoff, the review log's rows, and Notion,** read-only (section 7).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. Codex's finding | **(a), fixed in Stage B before the exact-head review, as correction B-C1, in shape (a1):** one owner-only read of the actor's own directional row and own block, each state and version. Words: FF1 (D13), FF2 (owned paths), FF3 (B-C1's section), FF6 (the review's focus) (section 3) |
| 2. The F2 cases' wording | **Narrow the brief's words** (FF4, FF5). The error is mine: those cases run on the adapter subject only (section 4) |
| 3. The sequence | **Agree, under (a),** with B-C1's start gate (section 5) |
| DM-73's EE1 to EE10 | **Confirmed as applied.** EE10 was then rewritten by Stage B's records, as item 2 intended (section 6) |
| 4. Notion | **No mismatch** (section 7) |

**How to apply:**
- **Where each condition goes:** FF1 to FF6, the brief's revision 16 (yours). B-C1's prompt then takes FF3's section as its given words.
- **The words are Markdown records, given exactly;** line breaks may move.
- **Verified by script** (`apply74.py`, outside the export):
  - each of the six old passages occurs exactly once in the brief at `6fa1b2c`;
  - the pairs apply to a copy, in order, and each new text then occurs once;
  - the report holds no model identifier.
- **No further read is needed** before B-C1's prompt if FF1 to FF6 are applied as written. A departure comes back first.

## 3. Item 1 — Codex's finding: (a), in shape (a1)

### 3.1 Confirmed

**The like and pass:** `interactions.py:307` compares `CommandMeta.expected_version` with the actor's directional row, `0` for its absence, before anything else is judged. That is the contract's rule ("zero for its absence", `production-contracts.md:197`; P05's "Version, digest and replay boundary").

**The block and unblock** do the same with the actor's directional block (line 518).

**Where a client can get a version:**
- Only from its own command's answer: `InteractionOutcome`, the undo outcome and `BlockOutcome` each carry the row's version.
- No read does:
  - `contract.card()` gives the profile ID, the profile and the details;
  - of the five routes, the only read is `GET api/v1/matches/<uuid:match_id>`;
  - every stale cause answers one 409 body with no version (D8).

**The proof hides the gap:** `interaction_cases._version()` reads the row through the ORM.

### 3.2 Why fix it now, not carry or decline it

**The block case is reachable at launch, and it is a safety action.**
- After a member unblocks someone, the block row is `removed` with a version above zero.
- On a new phone, after a reinstall, or after losing a response, a client has no way to learn that version. Its block of that member is refused `stale_version` every time.
- No setting gates this. A member who cannot block someone is the failure F13 exists to prevent ("block works after unmatch and while paused").

**(b) would carry a safety gap past the merge.** (c) would make the contract depend on something clients cannot always do:
- a second device has no answers to keep;
- a replay recovers a lost answer only with the same key and intent, which a new device does not have.

**The like, pass and undo case** waits on settings that are off at launch, and would by itself be a fair carry. It needs the same read, so B-C1 fixes both.

### 3.3 Why (a1), not (a2)

- **(a2)** puts the version on a new card, which covers resurfacing and undo only. A blocked member is never on a card, so the block would still need a read of its own.
- **(a1)** is one owner-only read that covers all three.

### 3.4 What the read must be (D8, D13)

**Additive (D13):**
- a new route and a new DTO in F08's and F13's registry entries;
- every existing DTO, each version check and D8's single stale body unchanged.

**Its answer depends only on the actor's own rows:**
- **Where the actor has none,** it is the same 200 body (`none` and `0`, twice) whether the profile exists or not, and whatever its state: not visible, paused, restricted, removed, excluded, or blocking the actor.
- **Where the actor has a row,** it is that row, whatever the other member's state.
- **No row whose actor is the other member is ever read.** So the other member's like, which D9 says the target never sees, and their block stay hidden.
- **It is never a 404 for a profile ID that does not exist.**

**Like the match read:**
- one transaction holding the actor's account row `FOR SHARE`;
- served `Cache-Control: no-store`;
- for the actor only.

**What the proof must model:** it must take its versions as a client would. `_version()` reads the route, never the ORM, so the gap Codex found cannot be hidden again.

**One point for the exact-head review's threat model, not a ruling:**
- Stage B's block answers 404 `target_not_found` for a profile ID that does not exist (line 506), before its locks.
- With `expected_version` set wrong, it answers 409 for an existing profile and 404 for a missing one, and changes nothing either way.
- The review judges it against D8. The new read must not add a second such answer.

### 3.5 Its words

- **FF1** adds the read to D13.
- **FF2** gives B-C1's owned paths.
- **FF3** gives B-C1's section: items, stop rule, run of record and review.
- **FF6** adds the read to the review plan's Stage B focus.

## 4. Item 2 — The F2 named cases: narrow the words

- **The words were mine (DM-73's EE1 and EE6), and wrong.**
  - `f2_session_account_changed_under_wait` and `f2_match_pair_changed_under_wait` are P06.2 B1's.
  - `cases.all_cases` carries B1's cases only for the adapter subject (`all_cases(d5=True)`).
  - Your consultation had said "the adapter subject's named cases".
- **Stage B compared them where they run,** and the control on both subjects. That is what the words should have said.
- **The record's note is not enough:** the brief is the living text, and its next reader is B-C1's prompt. FF4 and FF5 narrow EE1 and EE6.

## 5. Item 3 — The sequence: agree, under (a)

1. this answer;
2. the brief's revision 16, with FF1 to FF6;
3. B-C1's prompt, with its TypeSafe reading. Its start gate checks that the start commit's non-Markdown tree equals `5d58993`'s;
4. B-C1, then your verification;
5. PR47's run and Codex on its head;
6. the exact-head review of `5d58993` with B-C1, with its threat model;
7. my pre-merge read: the CI policy's paragraph, the data model's and the contract's rewritten texts, and any governing Markdown;
8. the merge.

## 6. DM-73's EE1 to EE10, as applied

At `6fa1b2c`, whitespace normalised:
- **EE1 to EE9:** each once.
  - EE1 and EE6 keep their anchors, as insertions do;
  - EE2 to EE5 and EE7 to EE9 have their old passages gone.
- **EE10:** applied at `550e74f`, present once there. Stage B's records (`291edef`) then rewrote that limit as item 2 required.
  - The suites now record psycopg's own cursor methods, `callproc` among them.
  - What remains unseen is stated: a statement below psycopg's cursors, with its planted example, and an asynchronous connection.

**The review log's rows:**
- DM-73's row (EE1 to EE10) can close.
- A new row: FF1 to FF6 as applied, confirmed at my next consultation.

## 7. Item 4 — Notion (read-only, at about 13:40 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control | The status heading and stamp | **Match:** "15 November 2026 (App Manager 11; Stage B integrated, PR47 open; DM-74 on Codex's finding)", the handoff's title; matched at `6fa1b2c` |
| Implementation Control | "Next items" | **Match:** Stage B built from revision 2, verified and integrated; PR47 open; DM-74 with Dev Manager 5 |
| Implementation Control | "Main"; "Branches" | **Match:** `947576d`, with PR47 open; four branches, as `git ls-remote` shows: `claude/dev-manager` at `7d219d0`, and Stage B's at `291edef` |
| Implementation Control | "Dev Manager"; "Mistakes log"; standing directions | **Match:** Dev Manager 5; AM11-01 to AM11-24 at `1b331b2`, the log's last change; OD-01 to OD-65 |
| Dev Manager — reviews and approvals | DM-73's and DM-74's rows | **Match:** DM-73 considered (EE1 to EE10 applied at `550e74f`); DM-74 pending |
| Register copy | Rows | **Match:** 65 rows. The register is unchanged since `829f90c`; the copy's one pinned-link difference (OD-64) is as DM-71 reported |
| Work Register `SV3` | State, next action, evidence | **Match:** "In progress"; Stage B integrated, PR47 open; DM-74 at `6fa1b2c`; evidence pinned at `6fa1b2c` |

## 8. The words

**FF1 (yours: the brief's revision 16: D13, the actor's own versions):**

> ```
> each as an added DTO or value and named in the report (DM-60).
> ```

> ```
> each as an added DTO or value and named in the report (DM-60).
>   - **The actor's own versions** (DM-74; Codex on PR47): F08's like, pass and undo, and F13's block and unblock, compare `CommandMeta.expected_version` with the actor's own row, `0` for its absence, and a client that has lost its own command answers, or a second device, had no read that returns that version. An owner-only read does: for a target profile ID, the actor's own directional row's state and version, and the actor's own block's state and version, each `none` and `0` where the actor has no row. Its answer depends only on the actor's own rows: where the actor has none, it is the same 200 body whether the profile exists or not and whatever its state; where the actor has a row, it is that row, whatever the other member's state; and no row whose actor is the other member is ever read. It is a new route and a new DTO in F08's and F13's registry entries; every existing DTO, each version check and D8's single stale body stay as they are.
> ```

**FF2 (yours: the brief's revision 16: B-C1's owned paths):**

> ```
> its runs of record only. Nothing else changes in B0.
> ```

> ```
> its runs of record only. Nothing else changes in B0.
> - **Correction B-C1 only** (DM-74): the own-versions read in `services/api/glow_discovery/interactions.py`, `interaction_views.py`, `interaction_urls.py` and `contract.py`, and nothing else in them, with its tests in `services/api/tests/`; D13's contract addition for it (the production schema, `openapi.json`'s DTOs, the corpus, `flows-v1.json`'s F08 and F13 entries, `packages/contracts/README.md` and the contract tests), and the generated outputs as `npm run generate` writes them; in the proof, `interaction_cases.py` and the discovery suite's case list, count and offline tests; the contract document's F08 and F13 server mapping; the proof README's SV3 paragraph; the evidence record; and the P11 plan's SV3 entry, its runs of record only. Nothing else changes in B-C1.
> ```

**FF3 (yours: the brief's revision 16: B-C1's section, before "Sessions"):**

> ```
> ## Sessions
> ```

> ```
> ## Stage B, correction B-C1 (Codex on PR47; DM-74)
>
> B-C1 corrects Stage B before its exact-head review, which then reads Stage B's code head `5d58993` and B-C1 together, as Stage A's review read C1. Its one finding is Codex's on PR47 (P2, `glow_discovery/interactions.py`; the record, "PR47 and Codex on its head"), with the block's same case the manager found: a client that has lost its own command answers, or a second device, cannot learn the version that F08's like, pass and undo, or F13's block and unblock, compare with `CommandMeta.expected_version`, since no read returns it. Resurfacing and undo are off at launch; a block after an unblock is not. B-C1 changes no model, migration, lock, version check, existing DTO, stale body, `glow_chat` writer, lock-scan rule or bound, workflow or dependency.
>
> 1. **The own-versions read** (D13; DM-74). A `GET` route for a target profile ID (proposed `api/v1/interactions/<uuid:profile_id>`), for the actor only, through SV1's `GlowActorAuthentication`, served `Cache-Control: no-store`. In one transaction holding the actor's account row `FOR SHARE`, as the match read does, it reads the actor's own directional row toward that profile's account and the actor's own block of it, and answers a new DTO: the profile ID as asked; the directional row's state (`none`, `liked`, `passed` or `withdrawn`) and version; and the block's state (`none`, `active` or `removed`) and version; each `none` and `0` where the actor has no row. Its answer depends only on the actor's own rows: where the actor has none, it is the same 200 body whether the profile exists or not and whatever its state (not visible, paused, restricted, removed, excluded, or blocking the actor), and never a 404; where the actor has a row, it is that row, whatever the other member's state; and no row whose actor is the other member is ever read, so the other member's like, pass or block is never shown. Its tests: each state and version after a like, a pass, an undo, a resurfaced like, a block and an unblock; the alike cases, byte-identical; the other member's like and block not shown; and recovery from no state, each with the version the read gives: with resurfacing on, a like of a passed candidate who resurfaces; with undo on, a like after a withdrawn pass; and a block after an unblock. Each recovery's reversal: with the read's version replaced by `0`, the command is refused `stale_version`.
> 2. **The proof takes its versions as a client does** (Codex: "the discovery proof masks this gap"): `interaction_cases._version()` reads the new route, not the ORM, and every expected version a case sends comes from a command's own answer or from the read, which a test asserts. Item 1's recovery cases are discovery cases too.
> 3. **The earlier tests it changes** (DD5): the API's `test_the_page_route_and_stage_bs_action_routes_are_served_and_no_other`, the proof's `test_the_routes_are_the_apis` and the discovery case `match.no_route_creates_a_match` each gain the read's route in the exact set they pin; the proof's `test_the_case_count_is_pinned` is re-pinned with B-C1's cases named; and the contract tests gain the DTO. Any other earlier test that no longer passes is a stop.
> 4. **The records:** the contract document's F08 and F13 server mapping states the read and its answer; the proof README's SV3 paragraph gains a sentence on B-C1, in its words; the record gains a section for B-C1; and the P11 plan's SV3 entry gains B-C1's run of record.
>
> **The stop rule (B-C1):** stop and report if B-C1 needs a change outside its owned paths, or to a model, a migration, a lock, a version check, an existing DTO, D8's single stale body, a `glow_chat` writer, the lock scan's rules or B0's bound, the workflow or a dependency; if the read cannot give the same answer for every profile the actor has no row with, whatever that profile's state; or if a case other than those item 3 names changes its verdict.
>
> **B-C1's run of record:** a push run on its code head, with all eight jobs passing, each suite's D14 record `PASS`, and the discovery phase's duration within the job's 30 minutes, read from GitHub.
>
> **The review:** Stage B's exact-head code and security review then reads `5d58993` and B-C1 together, with its threat model; its focus gains the read: owner-only, the same answer whatever the target's state, never the other member's rows, and no version recovered any other way (DM-74). The manager's verification comes first, then PR47's run and Codex on its head, then the review, and the Dev Manager's pre-merge read after it.
>
> ## Sessions
> ```

**FF4 (yours: the brief's revision 16: D14, the F2 cases' subject):**

> ```
> and shows, on both subjects, each named case's wait and verdict and the control's failure unchanged; if any changes, it stops and reports (DM-73).
> ```

> ```
> and shows each named case's wait and verdict unchanged on the adapter subject, where P06.2 B1's cases run, and the control's failure unchanged on both subjects; if any changes, it stops and reports (DM-73, DM-74).
> ```

**FF5 (yours: the brief's revision 16: Stage B's item 5, the same):**

> ```
> so each wait should hold: on both subjects, `f2_session_account_changed_under_wait` and `f2_match_pair_changed_under_wait` each show the arriver's wait and their verdict unchanged, and `oracle.send_after_account_revocation` still fails as intended.
> ```

> ```
> so each wait should hold: on the adapter subject, where P06.2 B1's cases run, `f2_session_account_changed_under_wait` and `f2_match_pair_changed_under_wait` each show the arriver's wait and their verdict unchanged, and, on both subjects, `oracle.send_after_account_revocation` still fails as intended (DM-74).
> ```

**FF6 (yours: the brief's revision 16: the review plan, Stage B's focus):**

> ```
> unmatch and block through `glow_chat`, and rematch's fixed limit;
> ```

> ```
> unmatch and block through `glow_chat`, rematch's fixed limit, and the own-versions read (DM-74): owner-only, the same answer whatever the target's state, and never the other member's rows;
> ```

## 9. Where each item goes

- **The brief's revision 16 (yours):** FF1 to FF6, and a Sessions line for DM-74's answer.
- **B-C1's prompt:** FF3's section as its given words, with its TypeSafe reading and the start gate in section 5.
- **The review log:**
  - DM-74's dispositions, naming `6fa1b2c` as the commit this read covered;
  - DM-73's deferred row closed;
  - a new row for FF1 to FF6.
- **Notion:** the status after DM-74.

Status: complete
