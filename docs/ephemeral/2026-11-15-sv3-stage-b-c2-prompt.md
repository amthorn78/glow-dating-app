# SV3 Stage B, correction B-C2 prompt — the exact-head review's findings: undo one step, D14 read as PostgreSQL reads, the block's direction stated, the tests and records

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 15 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 17, with its section "Stage B, correction B-C2 (Stage B's exact-head review; DM-75)".
- **Where the result goes:**
  - the session's changes in B-C2's owned paths, and its record, a new section `## Stage B, correction B-C2` at the end of `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.03 (confidence 0.86); rung probabilities low 0.00, medium 0.09, high 0.79, extra high 0.12, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.090, Opus 5.5 at high 0.790, Opus 5.5 at extra high 0.120, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-15T23:06:39Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs.
  - The brief's revision 17 applies DM-75's GG1, GG2, GG12, GG16, GG17, GG26 and GG27 as written, with GG3 in the carried-items file and GG4 in the P11 plan. DM-75 sets this prompt's place in the sequence (DM-75 section 10) and needs no further read if its words are applied as written.
  - This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification, and PR47's run and Codex's review of its head;
  - a bounded delta re-review of B-C2 against `470d97a` (a full exact-head review instead if B-C2's non-test lines in `services/api` exceed 60, or it changes a design);
  - Dev Manager 5's pre-merge read;
  - the merge.
- **Deletion condition:** prune after Stage B's PR (PR47) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **implementation session for SV3 Stage B's correction B-C2**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What B-C2 is.** The correction pass for the exact-head review of Stage B's code head `470d97a` (Stage B with correction B-C1). The review asked for changes, with no blocking finding. DM-75 ruled on each finding:
- **#1, the block's direction:** on the server only a block makes a match `restricted`, and Stage B serves the match's state to both participants, so the member who did not block can infer who blocked. It is **not fixed here**. It is D8's gap, carried to SV4 and sealed until P11. B-C2 corrects only the seven texts that say the direction stays hidden (item 1).
- **#2, undo can be chained:** undo becomes one step. The pass must be the actor's latest decision of any kind (item 2).
- **#3:** the plan-coverage test regains its protection (item 3).
- **#4 and #5:** D14's rule reads a statement as PostgreSQL does, and fails closed (items 4 and 5).
- **#6, #13 and #7:** limits and wording stated (items 6 and 7).
- **The nits:** records (item 8) and three tests (item 9).

B-C2 changes no model, migration, lock, version check, existing DTO, stale body, `glow_chat` writer, lock-scan rule or bound, contract package, workflow or dependency. The only behaviour it changes in `services/api` is undo's selection. There is no provider, deployed URL, real member, HDE call or stored credential.

**The brief, `docs/planning/sv3-eligibility-discovery-interactions.md`, revision 17, is the specification:**
- its section "Stage B, correction B-C2", items 1 to 10, its stop rule, its run of record and its review;
- D8's gap (GG1), D12's undo (GG12), D14's rule and reach (GG16, GG17);
- B-C2's owned paths, "Correction B-C2 only" (GG27).

Its text is Dev Manager 5's words (DM-75), checked against the code. Follow them exactly. Where this prompt summarizes the brief, the brief wins.

**DM-75's given words that B-C2 applies.** DM-75's report (`docs/continuity/dev-manager/reviews/2026-11-15-dm-75-sv3-stage-b-review-dispositions.md`) gives the exact old and new texts as pairs of quoted blocks:
- **B-C2's eighteen:** GG5 to GG11, GG13 to GG15 and GG18 to GG25 (its section 12, "Who applies what").
- **Apply each as written.** Its old passage must be found exactly once before the change, and its new text exactly once after. The manager checked each old passage once at `<START_SHA>`.
- **Stop if a pair cannot be applied.** If an old passage is not found exactly once, report it; do not reword it.
- **Leave the manager's pairs alone.** GG1 to GG4, GG12, GG16, GG17, GG26 and GG27 are already applied. So is #9, the CI policy's count, which is the manager's; do not change the CI policy.

**What came before.**
- **SV3's Stage A** (PR45, `8d83474`) and **B0** (PR46, `947576d`) are merged.
- **Stage B** (code head `5d58993`) and **correction B-C1** (the actor's own-versions read; code head `470d97a`) are built, verified and integrated. They are in PR47, whose runs and Codex's review are clean at `e75649d`. B-C1's run of record, 43727020292, passed all eight jobs: discovery 66/66, each suite's D14 record `PASS`.
- **The exact-head review of `470d97a`:** changes required, no blocking finding; seven should-fix findings and nine nits (the evidence record, "Exact-head review of Stage B").
- **DM-75** ruled on each (the same section's "Dispositions"). The brief is now at revision 17.

**Facts from the code** (at `470d97a`; the manager's reading at `<START_SHA>`, whose non-Markdown tree equals it):
- **Undo's selection** (`services/api/glow_discovery/interactions.py`, lines 413-425):
  - the row must be `passed` (`no_pass`);
  - `latest` is the newest of the actor's rows filtered `state="passed"`, ordered `-decided_at, -id` (`not_the_most_recent_pass` otherwise);
  - then the window check (`undo_window_ended`).

  Item 2 removes the `state="passed"` filter from `latest` and nothing else. `decided_at` is `clock_timestamp()` at each like, pass or undo, and non-null.
  - No test pins the internal reason `not_the_most_recent_pass`; DM-75 4.2 allows renaming it.
  - `settings.undo_off_and_on` asserts `undo_window_ended`.
- **The other cases that call undo:** `interactions.logs_no_private_value`, `interactions.pointer_order`, `own_versions.each_state_and_version` and `own_versions.recovery_like_after_undo`.
  - Each undoes either a pass that is its actor's latest decision, or a row that is not a pass.
  - So by the manager's reading their verdicts do not change under item 2. If one does, stop.
- **D14's rule** (`proofs/postgres-ordering/glow_ordering_proof/row_locks.py`, `refusal`):
  - it strips comments with a regular expression (`_COMMENT`, line 69) before anything else;
  - it returns `None` unless the text holds `FOR UPDATE` and names the account table;
  - it resolves `OF` names from `FROM` and `JOIN` matches (`_FROM_ITEM`), with no notion of scope.
- **What the suites send** (the manager's sweep, AM11-23):
  - no `DO` statement, `U&` string or identifier, or dollar-quoted string appears anywhere in `services/api` or `proofs/` source;
  - in run 43727020292, every suite's D14 line shows 0 statements taking `FOR UPDATE` that name the account table ("0 FOR UPDATE OF other tables only").

  So items 4 and 5 should refuse nothing the suites send. The run of record shows whether they do.
- **The existing row-lock offline tests keep their verdicts** (DM-75 6.2).
  - `test_an_of_naming_only_other_tables_passes` pins two statements that pass while naming the account table, or its alias, in another lock clause's `OF` list: `FOR SHARE OF "glow_persistence_appaccount"` and `FOR KEY SHARE OF T2`.
  - So item 5's "the account table appears only as such an item's table or a column's qualifier" must read a name in a lock clause's `OF` list as a reference to a binding, as a column's qualifier is.
  - If that reading cannot hold while each of item 5's forms fails, stop.
  - The review's own eight texts for #4 are not in the repository. Its kinds are in the record's #4: a literal, a dollar-quoted string, an `E''` string, a quoted alias, a nested comment, a `U&` identifier and a `DO` block with dynamic SQL. DM-75 section 2 lists its own forms. Write your own text of each kind, at least eight, covering DM-75 section 2's #4 forms.
- **The plan-coverage test** (`proofs/postgres-ordering/tests/test_discovery_offline.py`, `test_the_plan_covers_stage_as_and_stage_bs_acceptance_checks`, lines 372-404) pools `covered` over every case. The manager computed Stage A's own cases (those in neither `STAGE_B_CASES` nor `B_C1_CASES`) at `470d97a`: they still carry every one of Stage A's labels (1 to 6, 12 to 14, D2 to D8, D13, D14, D19 and DB04). So item 3's restored test passes at the start.
- **The cases item 9 extends:**
  - `settings.resurfacing_off_and_on` (`interaction_cases.py`, line 1111) reads only first pages;
  - `continue_page` (`glow_discovery/pages.py`, lines 333-334) applies resurfacing's cutoff on a cursor page;
  - the routes case is `routes.interaction_refusals_and_ownership` (line 1256);
  - the block case is `block.works_after_unmatch_and_while_paused` (line 1046), whose message is at line 1090.
- **The API's structural test** of `activate_reciprocal` that item 9 extends is `test_the_method_around_the_body_is_activate_matchs_with_one_import` (`services/api/tests/test_interactions_offline.py`, line 1377). It compares the nested `body`'s name, arguments and returns, but not its decorators.
- **No test reads the texts item 1, 7 or 8 change.**
  - `packages/contracts/tests/test_transition_contract.py` reads one sentence of the contract document ("explicit trusted test prerequisites"), which B-C2 does not change.
  - No generator writes the contract document's flow index.
- **The case count stays 66.** Item 2 and item 9 extend existing cases (DM-75 section 8). B-C2 adds no case.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - **write only B-C2's owned paths** (the brief's "Owned paths (the sessions)", "Correction B-C2 only", GG27):
    - in `services/api/glow_discovery/`: undo's latest-decision rule and the module docstring in `interactions.py`, `match_projection`'s docstring in `contract.py` and the module docstring in `interaction_views.py`, and nothing else in them;
    - in `services/api/tests/`: the structural test of `activate_reciprocal` and any test item 2 adds;
    - in the proof: `row_locks.py` (its reading, its resolution and its docstring) and its offline tests; `interaction_cases.py` (the cases and texts its section's items 1, 2, 7 and 9 name); and `tests/test_discovery_offline.py`'s plan-coverage test;
    - the proof README's D14 entry and SV3 paragraph;
    - the contract document's F08 to F13 server mapping, and its flow index's F08 and F13 rows;
    - the data model's `Block` row and undo row;
    - the P11 plan's DB05 line, migration 0011's note and its runs of record;
    - the evidence record.

    Nothing else changes in B-C2.
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (B-C2)"). Stop and report, with no further change, if any of these holds:
  - B-C2 needs a change outside its owned paths;
  - it needs a change to any of these: a model, a migration, a lock, a version check, an existing DTO, D8's single stale body, a `glow_chat` writer, the lock scan's rules or B0's bound, the contract package, the workflow, or a dependency;
  - a statement any suite sends fails D14's corrected rule;
  - a form items 4 and 5 name cannot be made to fail without refusing a statement the suites send, or without changing an existing row-lock offline test's verdict;
  - one of DM-75's eighteen pairs cannot be applied as written;
  - a case other than those item 10 names changes its verdict;
  - **an earlier test** (DD5; the section's item 10): the earlier tests B-C2 is expected to change are named here, with their reasons. Any other earlier test that no longer passes is a stop. Expected to change, each keeping what it protects:
    - **`settings.undo_off_and_on`** (item 2): it gains the one-step checks:
      - after undo B, undo A is refused;
      - after a like of B over its withdrawn row, undo A is still refused.

      Its window check keeps the backdated pass the actor's latest decision (each later row of the actor's backdated before it), so the pass is refused for its window only (`undo_window_ended`). Its existing checks otherwise stand.
    - **`settings.resurfacing_off_and_on`** (item 9, #16): it gains a second page fetched by cursor, reaching a resurfaced candidate there, with two resurfaced candidates and the page's `limit` (DM-75 section 8). Its existing checks stand.
    - **`routes.interaction_refusals_and_ownership`** (item 9, #15; item 7): its "another member's batch" check names an entry of another member's batch. Its docstring says what each route refuses, as GG22 and GG23 word it, and the case says what it checks on each route.
    - **`block.works_after_unmatch_and_while_paused`** (item 1): its docstring (GG7) and one message (GG8). Its assertions are unchanged.
    - **`test_the_plan_covers_stage_as_and_stage_bs_acceptance_checks`** (item 3): Stage A's checks and decisions computed over Stage A's own cases, and Stage B's and B-C1's over their own.
    - **`test_the_method_around_the_body_is_activate_matchs_with_one_import`** (item 9, #14): it also compares the nested `body`'s decorators.
    - **`test_row_locks_offline.py`:** only added to. Every existing test keeps its statements and verdicts.

    By the manager's reading at `<START_SHA>`, no other earlier test is expected to change. If any other earlier test fails, report which and why; do not change or delete it.
  - In each case, report it; do not narrow the brief's words to pass it. A reversal's temporary edit of code is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished; a newer push cancels the earlier run's application jobs. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
- **Network:**
  - PyPI and the npm registry, for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run.

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from the CI job's pinned image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.

  Local passes are "iteration, not evidence"; the run of record is CI's.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, code, token, session key or signing key, in any form;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - make test data that looks real: accounts, emails, names, birth facts, places and coordinates are synthetic and obviously so (`@example.invalid` addresses);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions;
  - run `migrate` or `makemigrations` other than through the proof's own commands against such a database, or under the static registry's dummy settings;
  - connect to HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`. `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"   # must print the line
git diff --quiet 470d97acbf1faff6e81f1e8d8c9b9f27d0131765 HEAD -- . ':!*.md' && echo "B-C1's code"   # must print the line: the start's non-Markdown tree equals 470d97a's
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering 'docs/testing/evidence/*sv3*' docs/architecture docs/testing/p11-deferred-acceptance.md   # must print nothing
grep -c -F 'Status: brief, revision 17,' docs/planning/sv3-eligibility-discovery-interactions.md   # must print 1
grep -c -E '^## Stage B, correction B-C2' docs/planning/sv3-eligibility-discovery-interactions.md   # must print 1
grep -c -E '^## Stage B, correction B-C2' docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md   # must print 0
test -f docs/continuity/dev-manager/reviews/2026-11-15-dm-75-sv3-stage-b-review-dispositions.md && echo "DM-75's report"   # must print the line
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the record already holds "Stage B, correction B-C2".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md` and `proofs/postgres-ordering/README.md` (above all D14's entry and the SV3 paragraph);
- the brief, revision 17: D8, D12, D14, "Stage B: interactions (DM-71)", "Stage B, correction B-C1" and "Stage B, correction B-C2", whole;
- DM-75's report, whole: its rulings, its conditions in section 6.2 and its eighteen pairs for B-C2;
- the evidence record: "Stage B (interactions)", "Stage B, correction B-C1", "Manager verification of B-C1" and "Exact-head review of Stage B" with its "Dispositions";
- the code, whole:
  - `services/api/glow_discovery/interactions.py` (undo, above all), `contract.py` (`match_projection`) and `interaction_views.py`;
  - `services/api/tests/test_interactions_offline.py`'s structural tests of `activate_reciprocal`;
  - the proof's `row_locks.py` and `tests/test_row_locks_offline.py`;
  - `interaction_cases.py`: the block, routes, resurfacing and undo cases, and the other four that call undo;
  - `discovery_cases.py` (the plan), `glow_discovery/pages.py` (`continue_page`) and `tests/test_discovery_offline.py`;
- the texts DM-75's pairs change: the contract document's F08 to F13 server mapping and its flow index, the data model's `Block` and undo rows, and the P11 plan's SV3 entry and migration notes.

## 3. What to do

Each test below comes with its reversal (D18): a temporary edit that must make the test fail, run, then undone, with the edit and the failing output recorded.

1. **The block's direction: the texts** (item 1; #1). Apply GG5 to GG11 as written:
   - the record's Stage B "Cannot" line;
   - the contract document's F10 and F13 bullet;
   - the block case's docstring and one message;
   - `match_projection`'s docstring;
   - `interactions.py`'s module docstring;
   - the data model's `Block` row (with #12).

   No behaviour changes, and the block case's assertions stay as they are (DM-75 3.4 condition 4).
2. **Undo, one step** (item 2; #2; D12 as GG12 words it). The pass undo withdraws must be the actor's latest decision: of all the actor's directional rows, in any state, the one with the latest `decided_at` (ties broken by ID). Otherwise `state_conflict`, with nothing written. The code change is the `latest` query's filter, and nothing else in undo.
   - **The case:** extend `settings.undo_off_and_on` as the stop rule's list says.
   - **Its reversal:** `470d97a`'s selection (`state="passed"` restored) fails the case. Run it locally under D4 if you can; otherwise show it with an offline test of the selection, and say which.
   - **The texts:** GG13 (the contract document), GG14 (the data model) and GG15 (`interactions.py`'s undo paragraph).
3. **The plan-coverage test** (item 3; #3; DD5).
   - Stage A's checks and decisions are computed over Stage A's own cases (those in neither `STAGE_B_CASES` nor `B_C1_CASES`), and Stage B's and B-C1's over their own.
   - **Its reversal:** the review's mutation, 14, D19 and DB04 stripped from Stage A's only carriers, fails it, as it fails at `947576d`.
   - **The record:** correct the record's claim that the rewritten test kept what it protects.
4. **D14 reads a statement as PostgreSQL does** (item 4; #4; DM-75 6.2 (a) to (c)).
   - **Before it judges,** `row_locks.refusal` masks:
     - every comment: `--` to the line's end, and `/* … */`, nested;
     - every string constant: `'…'` with `''`, `E'…'` with backslash escapes, `U&'…'`, and dollar-quoted strings, the tag empty or an identifier.
   - **A quoted identifier** (`"…"` with `""`) stays a name, so Django's `"glow_persistence_appaccount"` is still the account table.
   - **These fail by rule:**
     - a statement with an unterminated span or block comment;
     - a `DO` statement, whose dollar-quoted body runs as code;
     - a statement holding a `U&` quoted identifier.
   - **The tests:**
     - your texts of the review's kinds (above) each fail at B-C2's head, and each passes at `470d97a`. Where one you write is already refused at `470d97a` (as a plain `DO` block is), show that and say so;
     - each passes with `FOR NO KEY UPDATE` in place of `FOR UPDATE`, except the `DO` statement, which fails either way, by rule;
     - "Comments are read as spaces" gives way to GG18's words.
5. **D14 resolves `FOR UPDATE OF` without ambiguity** (item 5; #5; DM-75 6.2 (d)).
   - **An `OF` name counts** only where the statement binds it once, in any scope, as a table named in a plain `FROM` or `JOIN` item or that item's alias.
   - **The account table** appears only as such an item's table or a column's qualifier (the brief's words). By the manager's reading of DM-75 6.2, a name in another lock clause's `OF` list is a reference, as a qualifier is (see "Facts from the code"). If you read it otherwise, stop.
   - **Any other form fails:** a name bound twice, a comma item, a schema-qualified name, `ONLY`, `*`, a sub-query's or a function's alias, or the account table inside a sub-query.
   - **The tests:** the review's scope example, and one planted example of each form, fail at B-C2's head. Each that passes at `470d97a` is shown passing there.
   - **The existing tests:** every existing row-lock offline test keeps its verdict.
6. **D14's limits and counts, stated** (item 6; #6, #13). Apply GG18 to GG21 to the proof README's D14 entry. Then put the same, in the README's words, in `row_locks.py`'s docstring:
   - a statement a case's own execute wrapper sends through the driver while Django's `execute` runs on that thread is not recorded;
   - a statement such a wrapper rewrites is judged on the text before the rewrite;
   - the docstring's "whatever wrapper a case adds inside it" goes;
   - `psycopg.connect` is no longer listed as unseen;
   - the connection count counts a connection's Django wrapper and its psycopg connection as two.

   D14's recording is unchanged: which statements it records, from which source, and its summary line's form.
7. **The `GET` routes' texts** (item 7; #7).
   - **Apply** GG22 (`interaction_views.py`'s module docstring) and GG23 (the contract document's routes bullet).
   - **The record and the case:** the record's Stage B section and the routes case's docstring say the same, and the case says what it checks on each route.
   - **No route's behaviour changes.**
8. **The records** (item 8):
   - **#8:** the proof README's SV3 paragraph counts Stage B's 19 cases (59), then B-C1's 66;
   - **the revision citations:** the README's SV3 paragraph and the contract document's F08 to F13 paragraph name the brief's revision 17 where they named 15;
   - **#10 and migration 0011:** the P11 plan's DB05 (GG24), and migration 0011's note (GG25);
   - **#11:** the contract document's flow index gains `OwnInteractionVersions` in F08's and F13's rows, as `flows-v1.json` has;
   - **#12:** the data model's unblock keeps the row (in GG11);
   - **the block's 404:** the contract document's F13 server mapping records the block's `not_found` for a profile ID that never existed, as the review judged it: a signal of existence only, on random version 4 IDs, that reveals no state (DM-74 3.4).
9. **The tests** (item 9; #14, #15, #16), each with its reversal:
   - **#14:** the structural test of `activate_reciprocal` compares its nested `body`'s decorators. Reversal: a bypassing decorator on `body` fails it.
   - **#15:** the routes case's "another member's batch" check names an entry of another member's batch. Reversal: removing the batch-owner check (`pages._fresh`'s owner comparison, temporarily) fails it.
   - **#16:** `settings.resurfacing_off_and_on` reaches a resurfaced candidate on a page fetched by cursor. Reversal: a `NULL` cutoff in `continue_page` fails it.
10. **The local checks:**
    - **API,** in `services/api`:
      - set up: `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`;
      - then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `smoke.py`, `ruff check .`, `ruff format --check .`, `mypy` and `python -m glow_persistence.static_check`;
      - the Python contract tests: `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`, unchanged;
    - **the proof,** in `proofs/postgres-ordering`:
      - its venv and hash-locked install;
      - its offline tests under `env -i`, Ruff, `ruff format --check` and mypy;
      - the lock scan, `python -m glow_ordering_proof.account_lock_scan`, its output unchanged (52 calls, 0 joining, 7 account locks);
    - **a local database run,** if Docker allows it under D4's conditions: iteration, not evidence. Run the discovery suite at least, and item 2's reversal.
11. **The run of record.** Commit and push your code. Wait for the Foundation run on your last code commit to finish (the push rule), then read it with your GitHub tools:
    - every job's conclusion, and the gate's line (`Application checks passed`);
    - the API test count;
    - each suite's result and D14's line (`ROW LOCKS (D14): PASS`, none refused), and the scans;
    - the discovery suite: 66/66, and its phase duration against the job's 30-minute timeout;
    - whether a toolchain retry fired.

## 4. The record

Add a section `## Stage B, correction B-C2` at the end of `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, with:
- the start gate's results, the environment check (names only) and the toolchain versions;
- **DM-75's eighteen pairs:** each applied, with its target file, its old passage found once before and its new text once after;
- **undo:** the query before and after, and the case's new checks;
- **D14:** the reading and the resolution, described; a table of every text items 4 and 5 plant, with its verdict at `470d97a` and at B-C2's head, and its `FOR NO KEY UPDATE` variant's;
- **the tests:** a table with one row per test, giving the file, the test, the reversal and its failing output;
- **the earlier tests:** each named test's assertion before and after, and why;
- **commands:** every command you ran, with its result line. List local database runs as iteration, not evidence;
- **the run of record:** its ID, each job's result, the counts, D14's line in each suite, the discovery phase's duration, and whether a retry fired;
- **B-C2's non-test lines in `services/api`:** their count, added and removed, for the review's size rule;
- every deviation from the brief, and what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only B-C2's owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- DM-75's eighteen pairs, each applied or not;
- undo's change, and each test with its reversal's result;
- D14's reading and resolution, and the planted texts' verdicts before and after;
- the earlier tests, each before and after;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the counts, D14's line in each suite, the discovery phase's duration and whether a retry fired;
- B-C2's non-test lines in `services/api`;
- anything that met the stop rule, every deviation from the brief, and what you could not run.
