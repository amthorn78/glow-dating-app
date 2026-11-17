# SV3 Stage B, correction B-C2: bounded delta re-review prompt

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 2, 16 November 2026.** Revision 1 (at `b0386f8`) was not given: Codex's review of `e6fa3c1`, posted at 23:23 UTC and read only after it, found a defect in B-C1's version ledger. Revision 2 adds it to the scope ("Codex's finding on the ledger" and focus 9), with a new TypeSafe reading.
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 17, "Stage B, correction B-C2 (Stage B's exact-head review; DM-75)" and its paragraph "The review", under the five correction classes of "C4's review, and how the scan's line ends", which hold in every later review of SV3.
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta re-review of B-C2", with a disposition for each finding (a correction, or a stated limit or record), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.65 (confidence 0.72); rung probabilities low 0.00, medium 0.01, high 0.37, extra high 0.59, max 0.03, ultracode 0.00. Model probabilities Fable 5.1 0.02, Opus 5.5 0.98, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.007, Fable 5.1 at extra high 0.012, Fable 5.1 at max 0.001, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.010, Opus 5.5 at high 0.363, Opus 5.5 at extra high 0.578, Opus 5.5 at max 0.029, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-16T01:22:37Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 5's pre-merge read follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR47's head, which is this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after Stage B's PR (PR47) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **bounded delta code and security re-review of correction B-C2, in SV3's Stage B**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one correction against the code head the exact-head review read, within a scope the Dev Manager fixed, under classes that fix what can lead to another correction. This prompt is revision 2, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`, the head of [PR47](https://github.com/amthorn78/glow-dating-app/pull/47).

**What came before.**
- **SV3's Stage A** (PR45, `8d83474`) and **B0** (PR46, `947576d`) are merged.
- **Stage B** (likes and passes, the mutual match, unmatch and block, resurfacing, undo and rematch's refusal, and D14's record of the row locks the suites send) and **correction B-C1** (the actor's own-versions read) are built: code head `470d97a`.
- **The exact-head review of `470d97a`** asked for changes, with no blocking finding: seven should-fix findings and nine nits (the evidence record, "Exact-head review of Stage B").
- **DM-75** (Dev Manager 5, in `docs/continuity/dev-manager/reviews/`) ruled on each:
  - #1, a `restricted` match showing the blocked member who blocked: carried to SV4 and sealed until P11, its texts corrected;
  - #2, undo chained: one step, the pass the actor's latest decision of any kind;
  - #3 to #7 and the nits: fixed or stated in correction B-C2.

  The brief's revision 17 holds DM-75's words.
- **B-C2** (branch `claude/sleepy-newton-1g92x8`) built them: code head `4860b56`, records `423f34a` (the evidence record, "Stage B, correction B-C2").
- **Its run of record** is Foundation run 43780988590 on `4860b56` (push):
  - all eight jobs passed, and the gate printed `Application checks passed`;
  - API 628 tests; ordering 56/56, 115/115 and 62/62; identity 49/49; profile 69/69; discovery 66/66, its phase 162 s;
  - each suite's `ROW LOCKS (D14): PASS` with none refused.
- **The manager verified B-C2** (the evidence record, "Manager verification of B-C2"): the diff within the owned paths; the app files and the earlier tests by AST; DM-75's 27 texts; the run of record; local re-runs; two reversals of its own. It merged B-C2 into the manager branch at `4616214`.
- **Points for this review** (the manager's verification, "For the delta re-review and the Dev Manager"):
  - **The `U&` reading:** the brief (GG16) and the README (GG18) say a statement holding a `U&` quoted identifier fails. Item 4 requires each planted text to pass with `FOR NO KEY UPDATE`. The code fails such a statement only when it takes `FOR UPDATE`, and its docstring says so; the README keeps GG18's words.
  - **A `CREATE FUNCTION` or `CREATE PROCEDURE` body** is a dollar-quoted string constant, masked by item 4's words, which except only `DO`. `470d97a` refused such a body that takes `FOR UPDATE` on the account table; `4860b56` passes it. No suite creates a function, and the suites' own-objects check (`row_locks.OWN_OBJECTS`) fails any function, procedure, view or rule that exists when it runs.
  - **The session's own pre-push read:** at `581966e` it found four bypasses of its first reading (non-ASCII spaces before a dollar quote, an `E''` string continued across a line end, unreserved keywords as aliases, names over 63 bytes) and one false refusal (an aliased item's table name bound as well as its alias). It fixed each at `fb201a4` and planted them.
  - **Codex on PR47:** four P2 findings since the review, each the review's own: #1 (carried), #4, #2 and #5 (B-C2's items 4, 2 and 5). Their threads are named in the brief's "Sessions".
  - **Codex's fifth finding, on B-C1's ledger** (P2, on `e6fa3c1` at 23:23 UTC; [thread](https://github.com/amthorn78/glow-dating-app/pull/47#discussion_r4580718359)). `interaction_cases.py`'s `_as_a_client` records a command's own answer (`_Ledger.served_from`) before it checks the version the command sent (`_Ledger.check`), in both its wrappers (lines 2069 to 2073 for the routes, 2080 to 2081 for the direct calls, at `4860b56`). So a command that answers with the version it was sent, such as an unmatch of a match already `unmatched` (`no_change`, the version unchanged), satisfies the ledger by its own answer, even when the version came from the database. This is B-C1's code; B-C2 does not change it. The manager confirmed the order in the code.

**The code head under review is `4860b56`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `4860b56` (the start gate checks this). The baseline is `470d97a`, the head the exact-head review read; `main` is at `947576d`.

**Your scope** (the brief's "Stage B, correction B-C2", paragraph "The review"; nothing outside it):
- **Every path B-C2 touches,** as it stands at `4860b56` (code) and `423f34a` (records): `git diff f39bd0d 423f34a`.
- **D14's rule** (`row_locks.py`'s `judge` and `refusal`, items 4 and 5): plant the review's kinds of text for #4, DM-75 section 2's forms, item 5's forms, the review's scope example, Codex's two texts and the session's pre-push forms, by each rule's words and not its examples alone. Read each verdict at `4860b56` and at `470d97a`, with its `FOR NO KEY UPDATE` variant.
- **Undo** (item 2): the selection, the case and its reversal.
- **Items 3, 6, 7, 8 and 9:** the plan-coverage test, D14's stated limits and counts, the `GET` routes' texts, the records and the three tests, each with its reversal.
- **DM-75's eighteen given texts for B-C2** (GG5 to GG11, GG13 to GG15, GG18 to GG25), as written.
- **Codex's finding on the ledger** (`_Ledger` and the two wrappers of `_as_a_client`), though outside B-C2's diff: confirm it, give its class, find any other path by which a command's own answer, or a replay's, serves the version it sent, and give the words for the fix and its negative test (focus 9).
- **The runs:** 43780988590, the run of record, and PR47's pull-request run on this prompt's commit or its parent, if one has finished.
- **Out of scope:**
  - code B-C2 does not change;
  - Stage B's and B-C1's code outside B-C2's diff, which the exact-head review read, except the ledger (below);
  - #1's fix, which is SV4's (the carried-items file, "Carried to SV4");
  - OD-64, and the items carried to later phases.

**The size rule** (DM-75 section 10). This review is bounded because B-C2's non-test lines in `services/api` are 26 (17 added, 9 removed), under 60, and B-C2 changes no design. Count them yourself from the diff. If they exceed 60, or you find that B-C2 changes a design (a rule or a behaviour beyond DM-75's words), say so first: a full exact-head review applies instead, and the manager takes it to the Dev Manager.

**How findings are judged.**
- **For D14's rule,** the five correction classes (the brief's "C4's review, and how the scan's line ends"), read for D14's record and against `470d97a`. These, and only these, lead to another correction:
  1. a lock of an `AppAccount` row at the reviewed head, in `services/api` or the reference design, or in a statement a suite sends, that is not `FOR NO KEY UPDATE`, however it is written (blocking);
  2. a form one of items 4 and 5's rules names (DM-75 6.2 (a) to (d)) that the rule still passes;
  3. a regression: a form the rule refused at `470d97a` that the reviewed head passes, or a lock, a test or a case that passes there and not at the reviewed head. A planted form the reviewed head newly refuses (it fails closed) is not one; nor is a form the earlier head refused only through a pattern that a later item's words replace and exclude, which is a stated limit;
  4. a test or reversal of items 2 to 5 and 9 that passes where it should fail;
  5. a record (`row_locks.py`'s docstring, the README, the evidence record, the P11 plan, the contract document, the data model) that claims D14's rule, undo or a route refuses or sees more than it does. A record wrong about anything else is a record nit.

  Any other form the rule does not see is recorded, with its planted example, as a stated limit, not a correction class.
- **For undo, the cases and the texts,** the exact-head review's classes that apply. Each of these is a finding:
  - undo working outside D12's one-step rule as GG12 words it;
  - a test that passes where it should fail, or fails where the code is right;
  - a Dev Manager condition unmet;
  - a record that claims more than the code, the tests or the runs show.
- **For each finding,** name its class, or say it is a stated limit, a record nit, or a rule change for the Dev Manager.

**The focus:**
1. **D14's reading (item 4), as a security boundary.**
   - Can any text hide a `FOR UPDATE` naming the account table from the rule: a comment, a string constant of any kind (with escapes and continuations), a quoted identifier, a `DO` statement, a `U&` identifier, an unterminated span, PostgreSQL's whitespace, or a name's case or length?
   - Is the fast path sound? Can a statement it passes without the full reading fail the rule?
   - Does a quoted identifier stay a name, so that Django's quoted account table still counts?
2. **D14's resolution (item 5).**
   - Does an `OF` name count only where the statement binds it once, in any scope, in a plain `FROM` or `JOIN` item?
   - Does each other form fail: a name bound twice, a comma item, a schema-qualified name, `ONLY`, `*`, a sub-query's or a function's alias, or the account table inside a sub-query?
   - Is the reading of a name in another lock clause's `OF` list as a reference sound? It keeps the existing tests' `FOR SHARE OF "glow_persistence_appaccount"` and `FOR KEY SHARE OF T2` passing. Can it let a `FOR UPDATE` on the account table pass?
3. **Regressions against `470d97a`** (class 3).
   - List every planted form `470d97a` refused that `4860b56` passes, starting with the `CREATE FUNCTION` and `CREATE PROCEDURE` bodies.
   - For each, say whether it is class 3 or a stated limit under the exception, with its planted example and, for a stated limit, words for the README's "Limits".
   - Is any statement a suite sends refused now, or judged differently (writer, account, `FOR UPDATE`) from `470d97a`'s rule? Read the run's D14 lines.
4. **The `U&` reading and the records** (class 5): does the README's GG18 sentence, or any other record, claim the rule refuses more than it does, here or elsewhere? If so, give words.
5. **Undo, one step** (item 2).
   - Can an undo apply to any pass but the actor's latest decision of any kind? Check ties, a like or pass over a withdrawn row, rows seeded by the proofs with the field's default clock, and another member's rows.
   - Do the other four cases that call undo keep their verdicts in the run?
   - Run the reversal.
6. **The tests** (items 3 and 9). Does each fail against its reversal?
   - Does the plan-coverage test protect Stage A's labels by Stage A's own cases again?
   - Does the routes case's new precondition (the two members' account versions agree) make its batch check sound, or can it pass vacuously?
   - Does the resurfacing case's cursor page reach `continue_page`'s cutoff?
7. **The records.**
   - DM-75's eighteen texts as written.
   - The proof README's D14 entry and SV3 paragraph; `row_locks.py`'s docstring.
   - The contract document's routes bullet, F08 to F13 mapping, the block's `not_found` note and the flow index's F08 and F13 rows, against `flows-v1.json`.
   - The data model's two rows; the P11 plan's DB05 line, migration 0011's note and its run of record.
   - Every claim in the record's "Stage B, correction B-C2", and its three "corrected in B-C2" notes in the Stage B section.
8. **Nothing else changed:** from the diff, no path outside B-C2's owned paths (GG27), and no workflow, contract package, model, migration, lock file, dependency or `glow_chat` file.
9. **B-C1's ledger** (Codex's fifth finding). Does recording a command's own answer before checking its sent version let a version the device was never served pass (FF3's "every version a case sends comes from a command's own answer or from the read")?
   - Check the routes' wrapper and the direct one, a `no_change` answer, a replay, and a refused command.
   - Is it, under the exact-head review's classes, a test that passes where it should fail?
   - Does any case in the run send a version only its own answer served? Read the ledger's lines.
   - Give the fix's words (the check before the answer is recorded) and a negative test at the wrapper's level, with its reversal.

**Re-run, at least,** in a scratch copy of `4860b56`:
- **The checks:**
  - the API's `manage.py check`, its tests, Ruff, `ruff format --check` and mypy;
  - the proof's offline tests, Ruff, `ruff format --check` and mypy;
  - the lock scan, its output compared byte for byte with `470d97a`'s.
- **Offline reversals, at least six,** each against its test:
  - undo's `state="passed"` filter restored, against `UndoSelectionTests`;
  - one span kind's masking disabled in D14's reading (an `E''` string, a dollar quote or a nested comment), against its planted texts;
  - the `DO` rule disabled;
  - item 5's "bound once" or comma check disabled alone, against its forms;
  - the review's mutation of the plan-coverage test (14, D19 and DB04 stripped from Stage A's only carriers);
  - a bypassing decorator on `activate_reciprocal`'s nested `body`, against the structural test;
  - one of your own, against a claim you doubt.
- **Database reversals** (items 2 and 9: undo's selection, the routes case's batch-owner check, `continue_page`'s cutoff) are optional, under D4's conditions below. The session ran each locally; the record gives their results.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, thread resolutions, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI, for hash-locked installs in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`), if you choose a local run;
  - GitHub, through your tools, to read runs and PR47's threads.
- **Local database runs** are optional here and allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from that image, on loopback only; a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present; removed afterwards. Local passes are iteration, not evidence.
- **Never:**
  - dump the environment, or print a credential, password, token, session key or key;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE` (DM-57 and DM-58). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values. If any other `AWS_*` name is present, stop and report.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 947576d98b7c3103455a670c20fdba2734ff5053
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 4860b56c222db719f28010845ae32d15ecbf124a HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet 4860b56c222db719f28010845ae32d15ecbf124a origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after 4860b56"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Delta re-review of B-C2'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `4860b56`;
- this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree, run from the repository's root:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md` and `proofs/postgres-ordering/README.md` (above all D14's entry and the SV3 paragraph);
- the brief, revision 17: D8, D12, D14, "C4's review, and how the scan's line ends", "Stage B: interactions (DM-71)", "Stage B, correction B-C1" and "Stage B, correction B-C2", whole;
- DM-75's report, whole, above all sections 3 to 6 and 10;
- the evidence record: "Exact-head review of Stage B" with its "Dispositions", "Stage B, correction B-C2" and "Manager verification of B-C2";
- the diff `git diff 470d97acbf1faff6e81f1e8d8c9b9f27d0131765 4860b56c222db719f28010845ae32d15ecbf124a`, and, whole at `HEAD`:
  - `row_locks.py` and `tests/test_row_locks_offline.py`;
  - `services/api/glow_discovery/interactions.py`'s `undo`, and `services/api/tests/test_interactions_offline.py`'s `UndoSelectionTests` and `ReciprocalWriterTests`;
  - in `interaction_cases.py`, `_Ledger` and `_as_a_client`;
  - in `interaction_cases.py`, the four changed cases, `_account_versions`, and the four other cases that call undo;
  - `tests/test_discovery_offline.py`'s plan-coverage test, and `glow_discovery/pages.py`'s `continue_page` and `_fresh`.

**The run,** with your GitHub tools: 43780988590. Read every job's conclusion, the gate's line, and the Database proof checks job's suite, scan and D14 lines.

## 3. What to do

1. Review the delta against the focus, item by item, with focus 1 to 3 and 5 as security boundaries: what each rule stops, what it cannot see, and the test that proves it.
2. In a scratch copy of `4860b56`, re-run the checks and the offline reversals above, and any you doubt.
3. For each finding, give:
   - its severity (blocking, should fix, nit);
   - its file and line, and the evidence;
   - its class (1 to 5, or one of the exact-head review's classes for undo, the cases and the texts), or "stated limit", "record nit", or "rule change for the Dev Manager".

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 2, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the size rule's count, and whether a full review applies instead;
- **the verdict:** approve, approve with nits, or changes required. Changes are required only for a finding in a correction class;
- the findings, in a table: number, severity, class or "stated limit", "record nit" or "rule change for the Dev Manager", file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 9), a few lines each. Include:
  - your reading of the `U&` rule and of the `CREATE FUNCTION` and `CREATE PROCEDURE` bodies;
  - for each stated limit, its planted example and the words for the README;
  - whether each of Codex's threads for #2, #4 and #5 is answered at `4860b56`, and your reading of its fifth (the ledger);
- the reversals you re-ran, with their results;
- what you ran, and what you could not run or read.
