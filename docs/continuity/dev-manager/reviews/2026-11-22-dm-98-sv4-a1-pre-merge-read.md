# DM-98 — SV4 A1's pre-merge read (PR58), with C2's delta review's E-1

- **Read at:** `13487ba30e7c2746cd4764ac2f35fc7c340e2c85` of `claude/magical-wozniak-yfmmx2`. It is PR58's head, and it was still the live branch's head when I fetched at 09:52 and again at 10:08 UTC. `main` is at `499ccbb`, PR58's base and its one merge base.
- **Requested by:** App Manager 13, relayed by Nathan ([the consultation](../../ephemeral/2026-11-22-dm-98-sv4-a1-pre-merge-read.md)). Nathan's relayed text equals the file's, with `<RECORDS_COMMIT>` filled in as `13487ba…`.
- **Written by:** Dev Manager 7, on 22 November 2026, from about 09:52 UTC.
- **What this is:** D-07's second read of SV4 A1 (OD-75). It also answers the one finding the manager says the fix-or-carry rule does not decide (E-1).
- **Last read before this:** my start note read `4618859`. The governing diff for this read runs from `499ccbb` (section 7).

## 1. The answers

| Item | Verdict |
|---|---|
| 1. E-1: carry, or a third correction | **(a), carry: approved with conditions AJ1 to AJ3.** The rule does decide it, once the review prompt's class is read inside D-07, as the workflow requires (section 3). The conditions make the carried entry, not the docstring, what the next writer of either field relies on |
| 1. Also asked: were the delta-review prompts' classes drawn within D-07? | **Not wholly.** Their docstring class and their record class leave out D-07's condition "that a decision or the merge would rest on". The record line has been in every SV4 review prompt since A0's. The manager logs it (section 3.4) |
| 2. The brief's revisions 4 to 7 | **Approved.** They widen owned paths and list earlier tests only, and each change I checked stayed inside them |
| 3. A1 as settled | **Approved with condition AJ4, which goes before the merge; AJ5 is recommended, not a condition.** Nothing in A1's code would stop me merging it. One living record is now false because of A1: the environment inventory says the API refuses "only" names that A1 now refuses (AJ4) |
| 4. C1 and C2 against their findings; the manager's D-07 calls | **Agreed.** One note: D1-1 went to C2 through the same wide class, and under D-07 alone it was a judgement call. C2's text is accurate, so nothing needs undoing |
| 5. Governing Markdown | **Confirmed: none changed** from `499ccbb` to `13487ba` |
| 6. Codex's P1 thread | **Agreed,** with one point of timing: resolve it after this read's disposition and before the merge |
| 7. What is carried or recorded only | **Each is in the right place,** with AR-4's entry changed by AJ1 and AJ2, and P07's entry by AJ3 |
| 8. Records since my start note | **Confirmed,** with one nit in the handoff (its "every session" sentence) |
| 9. Notion | **Five lines on Implementation Control and one Work Register property do not match `13487ba`** (section 11). The Dev Manager page and the register copy match |

- **The merge:** PR58 may merge once AJ1 to AJ4 are applied as given. They go in the batch that records this disposition, which is Markdown only. That batch's head then needs its passing PR run (all eleven jobs, with the gate's "Application checks passed") and Codex's completed review. After that, the P1 thread is resolved (item 6) and the checklist is filled (section 12).
- **AJ5** blocks nothing. It may go in the same batch or in the receipt's.
- **For Nathan:** nothing to decide. E-1 is a question of review procedure inside D-07, not a product or risk decision.

## 2. What I read and checked

- **The diff since my start note:** `git diff 4618859 13487ba` covers 18 files. Three are code: `services/api/glow_domain/chat_reads.py`, `services/api/tests/test_interactions_offline.py` and `services/api/tests/test_match_versions_offline.py`, all from C1 (`f69529c`) and C2 (`934da48`). The rest is Markdown: the record, the brief, the carried-items file, the handoff, the register, the review log, the mistakes log, the environment inventory, five prompts, DM-98's consultation, and my own start note and Dev Manager 6's handover (merged at `dfdca34`). **No non-Markdown path changed after `934da48`** (`git diff --name-only 934da48 13487ba` lists Markdown only).
- **The classification:** `main`'s `scripts/change_scope.py` (sha256 beginning `b564c62f4a076f51`, unchanged) was extracted outside the tree and run with `python3 -I --base 499ccbb… --head 13487ba… --merge-base`. It printed `"full": true`, reason `behavior-or-empty`, 74 paths, with one merge base, `499ccbb`.
- **Read whole:**
  - the SV4 record's sections "Exact-head review of A1", "A1-C1" and "A1-C2", each with its manager verification, delta review and disposition;
  - `services/api/tests/test_match_versions_offline.py` at `934da48`;
  - the three code diffs from `bc0675d` to `934da48`;
  - the brief's diff since `4618859`, its status line, its owned paths for A1-C1 and A1-C2, and its review plan;
  - the two delta-review prompts' correction-class paragraphs, A1's exact-head review prompt's (`ff2539b`) and A0's three (`499ccbb`);
  - the manager workflow's step 6 and PF02-R18 and R19;
  - the carried-items file's diff and its "Carried to SV4" and "Carried to P07" entries on the points at issue;
  - the handoff at `13487ba`;
  - the register's diff (OD-84);
  - the review log's diff (the Sessions rows and DM-98's row) and its open deferred rows;
  - the mistakes log's AM13-01 and AM13-02.
- **Read in the code** for A1's claims (section 5): `glow_chat/contact.py`'s `block` and `activate_reciprocal`; `glow_chat/reads.py`'s `readable`, `_causes` and `_authorize`; `glow_discovery/interactions.py`'s `interact` (its lock order); the migration `0013`; `glow_api/configuration_profiles.py`'s refusal lists and `forbidden_configuration`; the proof's copies in `environment.py`; and `glow_domain/notifications.py` (lines 13 to 18 and 928).
- **My own checks,** in the scratchpad, on exported trees (`git archive`). Each reads source with `ast` only, imports nothing from the candidate tree, and runs under `python3 -I`:
  - **The detector's blind spots in today's code.** I walked all 103 modules the detector scans, independently of its code. **One** shadowed definition exists: `FixtureInteractionService.policy_version`, a property whose getter (line 338) the setter (line 342) replaces. The getter names neither field. There is no `async def` at the walk's level. The classes nested in top-level classes are all Django `Meta` classes, and none writes either field: the two that mention the string `"version"` are unique constraints on `ConsentDecision` and `BirthInput`. The only module-level mention is the logging dictionary's `"version": 1` (`glow_api/telemetry.py`, line 168). So E-1, D1-1's forms and E-4 hide no writer at `934da48`.
  - **Code unchanged but for docstrings.** `ast.dump`, with every docstring removed, is equal from `bc0675d` to `934da48` for `chat_reads.py` and for `test_match_versions_offline.py`, and from `f69529c` to `934da48` for the latter (C2 alone).
- **GitHub, read only with `gh api` REST `GET`** (this session has no GitHub MCP tools):
  - PR58: open, not a draft, head `13487ba`, base `499ccbb`, `mergeable_state` clean.
  - PR run 45009459094 on `13487ba` (`pull_request`, attempt 1): all eleven jobs succeeded, and the gate's log line 94 reads "Application checks passed". In its API checks job (`refs/remotes/pull/58/merge`), `Ran 654 tests … OK (skipped=2)`: the two skips are the history tests, with their stated reason (log lines 1812 and 1814). The contract tests ran 53, OK.
  - PR runs 45007614603 (`045014d`) and 45002885670 (`ff17c61`): all eleven jobs succeeded.
  - Codex's summary comment (7031822500, updated 09:52:08 UTC): code review "completed" on `13487ba`, `has_any_findings: false`, `has_unresolved_findings: false`.
  - The P1 thread: review 6011084956 on `998116b` at 07:40:57 UTC, comment 4657212763, `original_line` 1389, now line 1382 at `13487ba`. `review_threads` shows it unresolved and not outdated.
  - `git ls-remote` at 09:59 UTC listed six branches (section 10).
- **The environment,** by `get_environment` (names only): `Glow App - No Stream`, network unrestricted, no environment variable of its own, a setup script (the toolchain), and one network secret, for `api.typesafe.ai`.
- **Not read or run:** the application's test suites (CI and three reviews ran them; I relied on their runs and logs); A1's whole diff line by line (the exact-head review read it, with nine reviewer agents and a verifier for each finding); the A0 sections of the record; the logs of the jobs other than API checks and the gate; the artifacts; Notion's uses table. No provider, database, HDE, Railway, Cloudflare or TypeSafe service was called.

## 3. Item 1 — E-1: carry, or a third correction

### 3.1 The finding, checked

- **E-1 holds in the code.** `functions()` (lines 60 to 70 at `934da48`) assigns `found[node.name]` and `found[f"{node.name}.{item.name}"]`, so a second definition of a name replaces the first. C2's passage says the detector reads "the `def` methods of top-level classes". Its list of what escapes leaves this case out. So does `functions()`' own docstring, "Every top-level function and method" (E-3).
- **It hides nothing today.** My independent walk (section 2) finds one such pair in the scanned code, `policy_version`, and it writes neither field. That agrees with the review and the manager. D6's acceptance check, "D6's equality test covers every writer of either version", holds at this head: the test pins `OrmContactPersistence.block` and `unmatch`, and they are the only writers. Four searches now say so: the exact-head review's, the manager's, the delta reviews', and mine.

### 3.2 The rule decides it: carry

The manager reads the rule as split. On one side, step 6 (a) says a defect "that falls in a correction class its review prompt names" is fixed. On the other, D-07 says "the reach of a static scan" is carried. But the workflow says which governs. Step 6's own paragraph, "What a correction pass is for", says that a correction pass is commissioned only for a defect in application behaviour, a defect at a security boundary, or *"a false claim that a decision or the merge would rest on. A review prompt's correction classes are drawn from those three."* The brief's review plan names the same: "a correction pass only for a defect D-07 names". PF02-R19 restates it in D-07's words. So a prompt's class cannot widen D-07. Where its words are wider, the class is read inside D-07, and E-1 is tested against D-07's third class:

- **The merge does not rest on the docstring.** It rests on D6's acceptance check, which rests on the searches. C2's passage itself says so: "the pinned set below is today's every writer by the A1 review's and the manager's searches of the code, not by the detector alone".
- **No decision rests on it, once AJ2 and AJ3 are applied.** The only later decision that could read the docstring's account of the detector's reach is a change that adds a writer of either field. Today the carried AR-4 entry tells A2 to "keep A2's writers to the forms it finds", and that does point A2 at the detector's account. AJ2 points it at the search instead, and AJ3 puts the same rule in front of the one other writer the records foresee, P07's staff path that ends a match (the brief's D12; DM-96's AG17).
- **So E-1 is "the reach of a static scan" and a record's wording that misleads no decision**, which the workflow carries: "written down in the evidence record as a limit and carried under rule (b)". The manager's recommendation is right, and so is the reason it gave: the merge and D6's check rest on the searches, not on the docstring.

### 3.3 Why a third correction would not converge

AR-2, D1-1 and E-1 are three passes on one docstring's account of a heuristic's reach, and the same review graded four more cases as nits (E-2 to E-5), with two more unlisted forms. Any list of what a heuristic misses will be incomplete, so each delta review can find the next case. A1-C3 would cost one more session, run, Codex pass and delta review, and it would hold A2 behind it under the one-item rule. It would not end the loop. Two things end it: the detector being made structural when it next changes, or no decision resting on the list. AJ2 does the second now and asks for the first at the next change.

### 3.4 Also asked: were the correction classes drawn within D-07?

**Not wholly.** Taking C1's and C2's delta-review prompts line by line:

- **"leaves a docstring claiming more than the code does, at the detector or the who-may-read boundary"** (C1's prompt; C2's has the detector only):
  - **The who-may-read half is within D-07.** It is a security boundary (who may read a conversation), and A2 and P11 wire against the port's docstring, so a decision rests on it. AR-3 was this case.
  - **The detector half is D-07's third class without its condition.** The detector is a test heuristic, not a security boundary. After C1 moved D6's basis onto the searches, a docstring's overclaim there met D-07 only through the carried entry's instruction to A2.
- **"makes a record claim more than the code, the tests or the runs show"** leaves out the same condition. It is not new. A0's exact-head review prompt and both A0 delta-review prompts (App Manager 12's, 19 November) carry the same line ("make a record claim more than the code, the tests or the runs show"). A1's exact-head review prompt (`ff2539b`) has "a false claim: a record, README, doc or test name that claims more than the code, the tests or the runs show".
- **Within D-07, on any fair reading:**
  - "lets a history test pass where it should fail, or fail on `main` after the merge": a failing test on `main` is a false claim the merge rests on, and OD-21 makes CI part of the current item;
  - "removes or loosens an earlier assertion" and "changes a path outside the passages": each would make the correction's own claim to the merge false.
- **What the manager logs:** that the two delta-review prompts drew a class wider than D-07, which breaks the workflow's step 6 ("drawn from those three") and PF02-R19. It should note that App Manager 12's SV4 prompts carried the same record line, so the entry is a repeat of a pattern, not a first.
- **A wording for the class in later prompts**, offered to the manager's next PF02 proposal (PF02 is governing, so its text comes to the Dev Manager's read in the usual way):

  > - a false claim that a decision or the merge would rest on (D-07): a docstring, record, README or test name that claims more than the code, the tests or the runs show, where that claim is what the decision, an acceptance check or the merge reads. Any other overclaim is recorded and carried.

- **The Notion summary** carries the same shortening: "a correction pass only for a defect in application behaviour, at a security boundary or a false claim". It is a likely source. Its correction is in section 11.

## 4. Item 2 — the brief's revisions 4 to 7

**Approved.** Each revision is the manager's and changes no design:

- **Revision 4** added `gapp-api-v1.schema.json` (`MatchProjection`'s description only), and the two proofs' READMEs (the sentences D4 and D7 make false), to A1's paths. D4 and D7 need each one.
- **Revision 5** added the two docstrings D4 makes false (`interactions.py`, lines 62 to 64; `contract.py`'s `match_projection`), and D11's three earlier tests, which A1's first session found.
- **Revision 6** added A1-C1's paths. C1's diff touches exactly those passages: `main_base()` removed, `A1_BASE` added, the two history tests renamed and reading `A1_BASE`, the class docstring, the comment above `MAIN_DEFINITION_DIGESTS`, the detector's two docstrings, and `chat_reads.py`'s one paragraph.
- **Revision 7** added A1-C2's paths. C2's diff touches only the module docstring's passage and `WriterDetectorTests`' docstring: the code is equal without docstrings (section 2).
- A1's accepted deviation (the Stream proof's README, lines 249 and 252, beside the owned line 250) is the right call. Left alone, both lines would state what D7 made false.

## 5. Item 3 — A1 as settled

**Approved.** What I checked in the code against the record's and the exact-head review's verdicts:

- **D3.**
  - `block` runs one queryset `update(retired_at=now)`. It covers the pair's unretired `liked` rows, both ways, after both account locks, with the database's clock, and it writes nothing else of a row.
  - `activate_reciprocal` requires `retired_at__isnull=True` on both rows.
  - SV3's `interact` takes `_lock_pair` before its eligibility check and before it writes its row. So a like and a block serialize on the same account locks. That is why AR-12's missing race case is a missing test, not a defect (section 9).
- **D4.** `block` stores `unmatched`, with the same `contact_version` and `version` advance, the same `save` and the same `contact_revoked` event.
- **D5.**
  - `_authorize` checks the match, the session, the epoch and the block in the send's order. It reads `chat.history` under its pointer after the row locks.
  - `readable()` serves a conversation that has causes only while the setting names the launch consent version and every cause reads `read_only`. Any other value fails closed.
  - `_causes` refuses a profile that is neither shown nor a cause (`removed`, or none) as `conversation_hidden`.
  - Every hidden cause refuses with the one reason `conversation_hidden`. An ended contact keeps `match_not_active`, so a block and an unmatch refuse alike.
- **D7.**
  - The grant and the signer are gone. `revoke_user_tokens` and `revocation_cutoff_sent` stay (the epoch revocation DM-96 kept).
  - `forbidden_configuration` refuses each name in `FORBIDDEN_INHERITED_NAMES`, and each name beginning `PG`, `POSTGRES_`, `REDIS` or `STREAM_`, by its presence and before any value is read. The proof's `environment.py` holds pinned copies.
- **The migration and the seal.**
  - `0013` is one `AddField`, `DateTimeField(null=True)`, after `0012_photo_check_seed`.
  - The 41 non-Markdown paths at `934da48` (A1's 40 and C1's `chat_reads.py`) include no settings, URL, WSGI, workflow, script, lock, requirements or package file, and no HDE port.
  - `identity_support.py` is untouched, so DM-50 1.2 stays carried. No open deferred row falls due at this merge.
- **The record A1 makes false: AJ4.**
  - The environment inventory's M05 finding-22 note says, in the present tense, "The API refuses only the exact names above". Since A1 the API also refuses the seven names and four prefixes. The note's dated observation (what `load_configuration` accepted on 26 October) stays true as history. The file is manager-owned and outside A1's paths, and no review listed it.
  - DM-97's AH5 corrected the same inventory for A0 in the batch before PR57 merged. AJ4 does the same here, and adds the consequence for integration that the record does not yet state: the database's and Stream's credentials reach the API only under names it is changed to read, never under libpq's, Railway's or Stream's own names (OD-18).
- **AJ5 (recommended)** puts that consequence beside the P11 plan's pool-settings item, where integration will look. The plan already has the runtime client pass Stream's pool settings explicitly, which agrees with the refusal. The plan does not yet say that the SDK can read none of its own `STREAM_*` settings from the API's environment.

## 6. Item 4 — the corrections against their findings, and the manager's D-07 calls

**Agreed.**

- **AR-1 into C1.**
  - Right: the first push run on `main` after the merge would have failed, and A1's record claimed less than its test did.
  - C1's fix compares with the fixed commit `499ccbb`, which is `main`'s own merge commit, so it stays in every full clone of `main`. The tests skip where it is absent (CI's depth-1 clones) and pass after the merge (the manager's simulation; the delta review's).
  - The digest test, which CI runs, still pins every definition.
  - This is also exactly what Codex's P1 asked for: "Compare both history tests against the fixed pre-A1 commit instead of the moving main merge base".
- **AR-2 into C1.** Right: "cannot miss one" was the claim D6's acceptance check could be read through.
- **AR-3 into C1.** Right: a false account of who may read a conversation, in the port A2 and P11 wire against. C1's paragraph matches `reads.py` condition by condition. N3's three omissions are all on the refusing side, so carrying them is right.
- **D1-1, with N1 and N2, into C2.** Agreed, with the note in section 1. It was taken under the prompt's wide class. Under D-07 alone it was a judgement call, since A2's reliance could have been routed through the carried entry, as AJ2 now does for every later gap. Taking N1 and N2 in the same lines cost nothing. C2's passage is accurate as far as it goes, so nothing needs undoing.
- **AR-4 to AR-16, N3 and E-2 to E-5 carried; N4 recorded.** Agreed. Each is the reach of a static scan, a test of behaviour whose code is right, or wording that misleads no decision once AJ2 is in place.

## 7. Item 5 — governing Markdown

**Confirmed: none changed** from `499ccbb` to `13487ba`.

- The consultation's command, `git diff --name-only 499ccbb 13487ba -- AGENTS.md CLAUDE.md '**/AGENTS.md' '**/CLAUDE.md' docs/pf-canon docs/planning/manager-workflow.md docs/planning/dev-manager.md docs/operations/ci-and-branch-policy.md`, printed nothing.
- My own sweep of every changed path found no `AGENTS.md` or `CLAUDE.md` at any level, nothing under `docs/pf-canon/` and no `.claude/` path. The only change to a start prompt is one history line in `docs/planning/start-prompts/next-manager.md`, which is not governing.

## 8. Item 6 — Codex's P1 thread

**Agreed**, with one point of timing.

- **The finding is answered.** C1 fixed it, the record's proofs and both delta reviews confirmed the fix, and Codex's own state on `13487ba` reads `has_unresolved_findings: false`.
- **The timing:** resolve the thread once this read's disposition is recorded, and before the merge rather than after it, so the PR's record at the merge shows no open thread. This is PR housekeeping within the manager's discretion (OD-09), and nothing is asked of Nathan (OD-58).
- **The receipt** names the thread (comment 4657212763, on `998116b`), the fix (C1, `f69529c`) and the two delta reviews that confirmed it.

## 9. Item 7 — what is carried or recorded only

**Each is in the right place, with three changes.**

- **AR-4's entry** takes AJ1 (E-1 is now carried, not pending) and AJ2 (the next writer repeats the search and is pinned).
- **P07's entry** takes AJ3 (D6's equality for a staff path that ends a match).
- **AR-12** is rightly a test for A2's chat suite: the account locks already order a like against a block (section 5).
- **The stale lines** from A1's record stay carried, `notifications.py` among them. Its lines 13 to 18 still state the composer's own checks correctly; only their identification with "the read rule of `chat_reads.py`" is stale. The next change to the composer is Stage B's, whose brief the Dev Manager reads.
- **The record-only items** (AR-6, AR-16, N4) stay record-only: each is wording in the record, corrected in its findings table, and no decision rests on it.
- **Nothing to fix before the merge** beyond AJ1 to AJ4.

## 10. Item 8 — records since my start note

**Confirmed,** with one nit.

- **OD-84** quotes Dev Manager 6's handover word for word, and names this session (`session_01Q789u3mBCcA1Fu21CMJKbS`, 07:50:00 UTC by `get_session`), its environment, `7b2c928` and `532e9d0`. The register's list of answers recorded in the Dev Manager's session adds OD-84.
- **The review log:**
  - Dev Manager 6's Sessions row ends "Handed over to Dev Manager 7 at `7b2c928` (OD-84)";
  - Dev Manager 7's row matches my start note, including its one Notion finding;
  - DM-98's row shows "Pending".
- **The handoff** routes correctly: Dev Manager 7, DM-98 waiting, six branches at 09:30 UTC. That matches `git ls-remote` at 09:59 (`main` `499ccbb`, the manager branch `13487ba`, `claude/dev-manager` `532e9d0`, A1's `a1651fb`, C1's `7b194aa`, C2's `02ebfc7`). It stays under 5 KB (4,548 bytes).
  - **The nit:** "the tools were missing in every session since 22 November" overstates. The record says C2's delta review's session "also offered GitHub MCP tools, which it did not use". Suggested words: "most sessions since 22 November have had no GitHub tools (C2's delta review's session had them)". The rule it states, the GitHub tools where present and otherwise `gh api` read only, is right.
- **Implementation Control's "Main" bullet** now names `499ccbb` (PR57) and PR58 open, as my start note asked. Its last clause is stale (section 11).
- **SV4's Work Register row** marks A1-C1's revision 1 "withdrawn before it ran (OD-83)", with both revisions linked.
- **The environment inventory's network note** matches my `get_environment`: unrestricted, no variable of its own, a setup script, one network secret for `api.typesafe.ai`.
- **AM13-01** is accurate against GitHub: review 6011084956 on `998116b` at 07:40:57 UTC, `original_line` 1389. It cites PF02-R57, which exists.
- **AM13-02** cites PF02-R68, which exists. I did not read the uses table it describes.

## 11. Item 9 — Notion (read only, between 10:00 and 10:07 UTC)

Each page was saved to a file and parsed with `python3 -I`. A match is stated only for the parts named. The repository wins (OD-27).

| Page | What I compared | Result |
|---|---|---|
| Implementation Control (`3e44590a05eb8118bf02f0dc0c3ea57c`, last edited 09:50:19 UTC) | The status heading and its stamp | "Last matched … at `13487ba`: SV4 A1-C2's delta review recorded; E-1 to DM-98", with C2's review and DM-98 as the record has them. **Match** |
| Implementation Control | "Dev Manager" | Dev Manager 7, OD-84, `7b2c928`, `532e9d0` merged at `dfdca34`, DM-98 to come. **Match** |
| Implementation Control | "Main" | `499ccbb` (PR57). **Match.** But its open-PR clause ends "with A1-C1 to come": at `13487ba` C1 and C2 are done and PR58 waits on DM-98. **Mismatch** (wording) |
| Implementation Control | "Branches" | Still App Manager 12's listing at 07:49 UTC: four branches, the manager branch at `4618859`, with no C1 or C2 branch. At `13487ba` there are six (the handoff; section 10). **Mismatch** |
| Implementation Control | "Mistakes log" | "AM12-01 to AM12-49, at `4618859`". The repository holds AM13-01 and AM13-02 at `13487ba`. **Mismatch** |
| Implementation Control | The procedure summary: its stamp | Links at `c33d1cf`. Since then one governing text changed: the CI policy, at A0's `3bf55de`, merged in PR57 at `499ccbb`. The summary's own rule ("moves its stamp when a governing text changes") and its history (it moved for earlier CI policy changes) call for a move. Its text states nothing about the job list, so only the stamp and its links need to move, to a commit at or after `499ccbb`. **Mismatch** (since PR57; not new to this item) |
| Implementation Control | The procedure summary: its D-07 sentence | "a correction pass only for a defect in application behaviour, at a security boundary or a false claim, anything else carried as a limit". The workflow says "a false claim that a decision or the merge would rest on". Suggested words: "a correction pass only for a defect in application behaviour, a defect at a security boundary, or a false claim that a decision or the merge would rest on; anything else, the reach of a static scan included, carried as a limit". **Mismatch** (section 3.4) |
| Dev Manager — reviews and approvals (`3e64590a05eb81e29903ca6fccd94268`, last edited 09:50:43 UTC) | Dev Manager 7's Sessions row; DM-98's row | As the review log has them; DM-98 pending, sent at `13487ba`. **Match** |
| Register copy (`3e64590a05eb81beaf78d6fa9d64a600`, last edited 08:03:53 UTC) | Its stamp; every row against `owner-directions.md` | Stamped at `52b0d13` (OD-84 added); the file is unchanged from `52b0d13` to `13487ba`. 84 rows each, OD-01 to OD-84. After normalizing links, markup and code spans, every row's quoted words are equal, and the only text differences in eight rows are the Notion checklist's descriptions in place of file names (and "Current handoff" for "The current handoff" in OD-83). **Match** |
| Work Register `SV4` (SQL on `"Work ID"`) | State, Owner Role, Next Action, Evidence | State "In progress"; Owner Role names App Manager 13 and Dev Manager 7; Next Action matches the record and the handoff at `13487ba`. **Match.** Nit: Evidence pins the brief and the record at `63aebb6`, which holds no A1-C2 section, and links neither C2's delta-review prompt nor DM-98's consultation. Not wrong at its commit, but it does not reach what E-1 rests on |

## 12. The merge

PR58 may merge when all of these hold:

1. AJ1 to AJ4 are applied as given, in the batch that records DM-98's disposition (Markdown only, so its non-Markdown paths still equal `934da48`'s);
2. that batch's head has its PR run, with all eleven jobs succeeding and the gate's "Application checks passed";
3. Codex's review has completed on that head, with any finding handled;
4. the P1 thread is resolved (item 6);
5. the pre-merge checklist names that run, A1's exact-head review with C1's and C2's delta reviews, Codex's summary on that head, and this read (DM-98) with its disposition.

A further non-Markdown change before the merge needs its own review and another read. AJ5 may go in the same batch or the receipt's. The Notion corrections (section 11) are the manager's next batch's.

## 13. The words

Each old passage below occurs exactly once in its file at `13487ba`. The pairs are applied in order, and each new passage then occurs exactly once (checked by script, section 14). AJ1 to AJ4 are conditions; AJ5 is recommended.

**AJ1 — the carried-items file, `docs/planning/carried-to-later-items.md`: E-1 carried, in AR-4's entry.**

> ```
> the earlier of two `def`s with one name, since `functions()` keys by name (E-1, unless DM-98 routes it to a correction; today `FixtureInteractionService.policy_version`'s getter, which writes neither field)
> ```

> ```
> the earlier of two `def`s with one name, since `functions()` keys by name (E-1, carried by DM-98; today `FixtureInteractionService.policy_version`'s getter, which writes neither field)
> ```

**AJ2 — the carried-items file, `docs/planning/carried-to-later-items.md`: what the next writer of either field does, in AR-4's entry.**

> ```
> Only `block` and `unmatch` write either field at A1's head; widen it, or keep A2's writers to the forms it finds, if A2 adds one;
> ```

> ```
> Only `block` and `unmatch` write either field at A1's head, by the searches of A1's exact-head review, the manager and DM-98, not by the detector alone (as the module's docstring says). A change that adds or changes a writer of either field (A2's, or P07's staff path, "Carried to P07") repeats that search at its own commit, listing every writer by file and line, and adds each new writer to `WRITERS`, so the detector must find it: either the detector is widened to reach it (for its function walk: every `def` and `async def` at any depth, none lost to a later definition of the same name) or the writer keeps to the forms and the functions the detector reads. A further gap in the docstring's account of the detector's reach is the reach of a static scan, recorded here and carried under D-07, not a correction of its own (DM-98);
> ```

**AJ3 — the carried-items file, `docs/planning/carried-to-later-items.md`: D6's equality for P07's staff path, in "Carried to P07".**

> ```
> - **From SV4's brief (DM-96; AG17):** a staff path that makes a match `restricted` keeps D4's sameness: it is served to both members as `unmatched`, so neither learns a block or a staff action from the match's state.
> ```

> ```
> - **From SV4's brief (DM-96; AG17):** a staff path that makes a match `restricted` keeps D4's sameness: it is served to both members as `unmatched`, so neither learns a block or a staff action from the match's state. **And D6's equality (SV4 A1; DM-98):** such a path ends contact, so it advances the match's `version` and `contact_version` together, by one each and saved in one `save`, as `block` and `unmatch` do; it is a writer of either field, so P07's prompt has its session repeat the search for every such writer and add it to `WRITERS` in `services/api/tests/test_match_versions_offline.py` ("Carried to SV4", AR-4).
> ```

**AJ4 — the environment inventory, `docs/operations/environment-inventory.md`: what the API refuses since SV4 A1.**

> ```
> [Added by M05, finding 22] The API refuses only the exact names above (`FORBIDDEN_CONNECTION_NAMES` in `services/api/glow_api/configuration_profiles.py`). On 26 October 2026, `load_configuration`
> ```

> ```
> [Added by M05, finding 22; updated by DM-98] Besides the exact names above (`FORBIDDEN_CONNECTION_NAMES` in `services/api/glow_api/configuration_profiles.py`), the API has refused since SV4 A1 (its brief's D7) seven more names and every name beginning `PG`, `POSTGRES_`, `REDIS` or `STREAM_` (`FORBIDDEN_INHERITED_NAMES` and `FORBIDDEN_INHERITED_PREFIXES`), by its presence, before any value is read; the disposable-database proof's environment check holds copies of both lists, pinned equal to the API's. So at integration the database's and Stream's credentials reach the API only under names it is changed to read, never under libpq's `PG*` names, Railway's database and Redis names or Stream's `STREAM_*` names (OD-18). Before SV4 A1, on 26 October 2026, `load_configuration`
> ```

**AJ5 (recommended) — the P11 plan, `docs/testing/p11-deferred-acceptance.md`: the refusal beside the pool-settings item.**

> ```
>   - **the runtime client passes every pool setting,** where the harness's `ServerApi` lets the SDK read five pool-setting names from the environment (a recorded limit of the proof).
> ```

> ```
>   - **the runtime client passes every pool setting,** where the harness's `ServerApi` lets the SDK read five pool-setting names from the environment (a recorded limit of the proof). Since SV4 A1 the API refuses, by its presence alone and before any value is read, every name beginning `STREAM_` (`glow_api/configuration_profiles.py`, `FORBIDDEN_INHERITED_PREFIXES`; M05's finding 22; DM-98), so the SDK can read none of its own settings from the API's environment, and Stream's credentials reach the runtime only under names the API is changed to read (the environment inventory).
> ```

## 14. Checks

| Check | Result |
|---|---|
| Environment, names only | None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET`. The container's `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE` and `AWS_SECRET_ACCESS_KEY` are present (OD-76), names only, never read |
| The commit read | `13487ba` on the live manager branch (`git merge-base --is-ancestor`), unchanged at 10:08 UTC |
| Classifier | `"full": true`, `behavior-or-empty`, one merge base `499ccbb`; policy sha256 begins `b564c62f4a076f51` |
| Governing Markdown | None changed from `499ccbb` (section 7) |
| Code after `934da48` | None (`git diff --name-only 934da48 13487ba`: Markdown only) |
| C1 and C2 change docstrings only where they say | `ast.dump` without docstrings equal (section 2) |
| The detector's blind spots today | One shadowed pair (`policy_version`), writing neither field; no `async def`; nested classes all `Meta`; no writer hidden (section 2) |
| PR58's run on `13487ba` | 45009459094: eleven jobs succeeded; "Application checks passed"; API `Ran 654 tests … OK (skipped=2)` |
| Codex on `13487ba` | Completed at 09:52:07 UTC, no findings; the P1 thread unresolved, not outdated |
| The words | Each old passage found once at `13487ba`; applied in order, each new passage found once (a script outside the tree, on the exported files) |
| Hygiene | No model identifier in this file; its last line is `Status: complete` |

Status: complete
