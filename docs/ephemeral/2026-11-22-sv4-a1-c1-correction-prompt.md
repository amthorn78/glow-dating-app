# SV4 A1-C1 prompt — the correction: the history tests on `main`, the version detector's claim, the read port's rule

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 2, 22 November 2026** (App Manager 13, OD-83). Revision 1 ([`998116b`](https://github.com/amthorn78/glow-dating-app/blob/998116b/docs/ephemeral/2026-11-22-sv4-a1-c1-correction-prompt.md)) was withdrawn before it ran: it told the session to read GitHub only with `gh api`. Revision 2 names no single route: the session reads GitHub with the GitHub tools where it has them, otherwise with `gh api` REST `GET` calls. It also names App Manager 13 as the manager, adds Codex's P1 thread on PR58 (the same defect as AR-1), and carries a new reading. The work is unchanged.
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 6. **The findings:** the SV4 record's section "Exact-head review of A1" (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`), with its disposition table.
- **Where the result goes:**
  - the session's changes to the three files below, and its section "A1-C1" in the same record, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.71 (confidence 0.81); rung probabilities low 0.00, medium 0.29, high 0.71, extra high 0.00, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.97, Sonnet 5.5 0.03, Haiku 5.5 0.00 (confidence 0.96). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.281, Opus 5.5 at high 0.689, Opus 5.5 at extra high 0.000, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.009, Sonnet 5.5 at high 0.021, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-22T07:54:49Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. This prompt authorizes no credential use and no live provider action (the charter, "Read before it takes effect"). Under D-07 the correction goes on the list for the Dev Manager's pre-merge read of A1.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read-only; this work needs nothing from it (OD-74).
- **It runs alone** (OD-29). Then, in order: the manager's verification; PR58's run and Codex's review of its new head; a delta review of C1 (the manager workflow, "A small correction gets a delta re-review"); the Dev Manager's pre-merge read of A1; the merge.
- **Deletion condition:** prune after A1's pull request (PR58) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **correction session A1-C1** for SV4 A1, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 2, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **A1** (code head `bc0675d`; the record's section "A1") built the rules chat's routes will serve: a block retires the pair's earlier likes (D3) and ends a match as an unmatch does (D4); the reads follow OD-60's rule through `chat.history` (D5); the send's expected version is the match's (D6); the token code is removed (D7). PR58 carries it into `main`, which is at `499ccbb` (PR57, SV4 A0).
- **A1's exact-head review** (the record's section "Exact-head review of A1") found the application's behaviour right on every item, and asked for changes:
  - **AR-1, blocking.** Two tests of `ReciprocalWriterTests` compare `glow_chat/contact.py` with `main`'s merge base and assert that it differs by A1's edits. Once A1 is on `main`, they compare A1 with itself and fail. `main`'s push runs check out a local `main` (`git checkout --progress --force -B main refs/remotes/origin/main`, in run 44657225220's API checks job), so the first push run after PR58's merge would fail the API checks job and the gate. PR runs and session-branch runs skip the two tests, so no run so far shows it. The manager reproduced it: with a local `main` at `bc0675d`, the class gives `FAILED (failures=2)`; with `main` at `499ccbb`, `OK`.
  - **AR-2, should fix (a false claim).** `test_match_versions_offline.py`'s docstrings say every form a writer could take is found, "so the pinned set above cannot miss one". The review reproduced 22 forms the detector misses.
  - **AR-3, should fix (a false claim at the who-may-read boundary).** `glow_domain/chat_reads.py`'s module docstring still states the read rule D5 replaced, which A2 and P11 will wire against.
- **Codex's review of PR58** (head `4618859`, 22 November 2026) left one unresolved P1 thread on `test_interactions_offline.py` line 1389, "Pin the history comparisons to the pre-A1 revision": the same defect as AR-1. Your fix answers it; you do not reply to it or resolve it.
- **The manager's disposition** (the same section's table): AR-1, AR-2 and AR-3 are fixed now, by you. The detector's reach (AR-4) and the nits (AR-5 to AR-16) are recorded or carried; you do not take them up.

**This correction changes tests and docstrings only.** No application behaviour, workflow, setting, contract, README or proof changes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only these paths:
    - `services/api/tests/test_interactions_offline.py`: `main_base()`; `ReciprocalWriterTests`' docstring and its two history tests, `test_every_writer_at_mains_base_is_unchanged_but_a1s` and `test_block_differs_from_mains_by_d3s_statement_and_d4s_value`; a new constant for A1's base; the comment above `MAIN_DEFINITION_DIGESTS`, only where it describes what the comparison reads;
    - `services/api/tests/test_match_versions_offline.py`: its module docstring (lines 8 to 15) and `WriterDetectorTests`' docstring (lines 231 and 232), only;
    - `services/api/glow_domain/chat_reads.py`: its module docstring's paragraph "Whatever refuses a send refuses a read" (lines 10 to 16), only (the brief, revision 6);
    - the record, section "A1-C1" only;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: use the GitHub tools where your session has them, otherwise `gh api` REST `GET` calls, and say in the report which you used. No pull request, comment, review, thread resolution, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **a path:** the work needs any path or passage outside the list above: `.github/workflows/foundation.yml` (its `fetch-depth` above all), any other test, `glow_chat/`, the contracts, a proof, a README;
  - **an earlier test:** a test not named above would have to change, or either history test would lose an assertion it makes today;
  - **the rule's text:** `chat_reads.py`'s paragraph would have to state a rule that `glow_chat/reads.py` does not apply, or leave out one it does;
  - **a proof or a reversal:** a result in section 3 differs from the one it names.
  - In each case, report it; do not narrow this prompt's words to pass it. A reversal's temporary edit is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it.
- **Network:** PyPI only, for `pip install --require-hashes` from the API's existing lock. No database runs: every check here is offline.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, marker, token or key;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - call any provider or HDE, connect to any database, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`); the cloud container sets them (OD-76). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`. Record `python3.12 --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API, as the workflow sets it).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet bc0675de3c6a4411f1d72845c69f8dc4e5706463 HEAD -- . ':!*.md' && echo "A1's code head"
git diff --quiet bc0675de3c6a4411f1d72845c69f8dc4e5706463 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after bc0675d"
git cat-file -e '499ccbbec758ed4ef34a93ad19fa8df454fb095c^{commit}' && echo "A1's base is in this checkout"
grep -c -E '^#+ Exact-head review of A1' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md   # must print 1
grep -c -E '^#+ A1-C1' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md                     # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, a non-Markdown path changed there after `bc0675d`, or a C1 section already exists.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`;
- the record's sections "A1" (its "Earlier tests changed, and why" and "Limits and deviations" above all), "Manager verification of A1" and "Exact-head review of A1", whole;
- the brief, revision 6: D5, D6, D11's A1 bullet, "Owned paths" (A1-C1), "Acceptance checks";
- `services/api/tests/test_interactions_offline.py`, from `git()` (line 1166) to the end of `ReciprocalWriterTests`, with the constants it uses (`CONTACT_IN_REPO`, `RETIRED`, `A1_CHANGED`, `A1_REMOVED`, `A1_DEFINITION_DIGESTS`, `A1_MODULE_DIGEST`);
- `services/api/tests/test_match_versions_offline.py`, whole;
- `services/api/glow_domain/chat_reads.py`'s module docstring, and `services/api/glow_chat/reads.py`'s module docstring, `readable`, `_history` and `_causes`.

## 3. What to do

1. **AR-1, the history tests.** The two history tests compare `contact.py` at `HEAD` with `contact.py` at A1's base, `499ccbb`, never with `main` or `origin/main`, so their result does not depend on whether A1 is on `main`.
   - Pin the base as a constant holding the full SHA `499ccbbec758ed4ef34a93ad19fa8df454fb095c`, with a comment naming it (PR57's merge, A1's base).
   - Each test reads the file with `git show <base>:services/api/glow_chat/contact.py`, and skips, saying why, where that commit is not in the checkout. That is every CI job's shallow clone; `fetch-depth` does not change.
   - Every assertion each test makes today stays, against the base.
   - Remove `main_base()` if nothing else uses it (the manager's search at `<START_SHA>` found only these two tests).
   - Rename both tests to name A1's base, not `main`'s. `ReciprocalWriterTests`' docstring and the comment above `MAIN_DEFINITION_DIGESTS` say what the class compares with, and that CI runs the digest test while the history tests run wherever the base is present.

   **Proofs,** each in a scratch clone outside the checkout (`git clone --no-local`), with its output recorded:
   - (a) **A1 on `main`:** with a local `main` at `bc0675d` and the clone at your head, `ReciprocalWriterTests` passes with both history tests run (`-v`, each `... ok`). The same set-up at `bc0675d` itself gives `FAILED (failures=2)`.
   - (b) **Before the merge:** with a local `main` at `499ccbb`, the class passes, both history tests run.
   - (c) **CI's clone:** in a `git clone --depth 1` of your head, both history tests skip with their reason, and the rest of the class passes.

   **Reversals,** each with `499ccbb` present, on a copy of `contact.py`, restored afterwards. Each fails a history test (record its name and assertion line; the digest test failing too is expected):
   - (r1) A1's `retired_at` statement removed from `block`;
   - (r2) one statement added to `unblock`, a definition A1 leaves alone.

2. **AR-2, the detector's claim.** `test_match_versions_offline.py`'s module docstring (lines 8 to 15) and `WriterDetectorTests`' docstring (lines 231 and 232) claim only what the detector finds.
   - Keep the list of forms it finds, and that `WriterDetectorTests` shows each is found.
   - Say that other forms escape it, naming at least those the review reproduced:
     - a related manager's `update` or `aupdate`;
     - a `Match(..., version=...)` or a `bulk_create`;
     - SQL text whose table name is built at runtime or held in a constant;
     - a match obtained through a helper such as `glow_discovery.interactions._pair_match`;
     - a `save()` override or a signal;
     - `Match` imported under another name.
   - Say that the pinned set is today's every writer by the A1 review's and the manager's searches, not by the detector alone, and that the detector's reach is carried (the carried-items file; the review's AR-4).
   - Remove "cannot miss one", and every other sentence that claims the detector is complete.
   - No assertion, detector or test changes; the module's test count and results are unchanged.

3. **AR-3, the read port's rule.** In `chat_reads.py`, replace the paragraph "Whatever refuses a send refuses a read" (lines 10 to 16) with the rule `glow_chat.reads` applies (its module docstring; the brief's D5):
   - the reader's valid, current session of an `active` account;
   - the match `active`, with no block either way;
   - the other account `active` or `suspended`; a deletion works as an unmatch;
   - then each cause reads its value in `chat.history`: read-only at launch, hidden as the setting says, the consent limit failing closed;
   - every hidden cause refuses with one reason that names no cause.

   The paragraph names no grant (the shared locks are the send's) and no open history question (OD-60 answered it; D5). It may point to `glow_chat.reads`' docstring instead of repeating it. It makes no claim about the served codes beyond naming `glow_domain.chat_projections.error_for` as the mapping. Nothing else in the module changes.

## 4. Checks, then the report

- **The trusted classifier,** from `main` (`499ccbb`), extracted outside your checkout and run with `python3 -I` and full SHAs: `python3 -I <trusted copy>/change_scope.py --base 499ccbbec758ed4ef34a93ad19fa8df454fb095c --head <your code head> --merge-base` prints `"full": true` (reason `behavior-or-empty`).
- **The diff:** `git diff --name-only <START_SHA> <your head>` lists only the three files and the record. In `chat_reads.py` and `test_match_versions_offline.py`, `git diff` touches only the passages named above, and `ast.dump` of each module with its docstrings removed is unchanged (record the comparison).
- **The API's checks,** in a clean environment, after `pip install --require-hashes -r requirements-dev.lock` in `services/api`: `GLOW_ENV=test python manage.py check`, `GLOW_ENV=test python manage.py test tests`, `ruff check .`, `ruff format --check .` and `mypy` pass. Record the test count and skips before and after.
- **Every proof and reversal** in section 3, with its output, `contact.py` restored byte for byte (`git status` clean).
- **The run of record,** on your last code commit: every job passed, and the gate printed "Application checks passed".

**The record,** section "A1-C1":
- this prompt's revision and commit; the start gate's and the environment check's results;
- each change, by item, with the tests' old and new names;
- the proofs and the reversals, with their outputs;
- the counts and the run of record;
- what C1 changes in section "A1": its limit on `ReciprocalWriterTests` (line 1093) now holds, because the history tests compare with A1's base, so a later change to `contact.py` fails them and A1's merge does not. The detector's forms in line 917 stand, with the forms it misses now in the docstrings.

Your final message, which Nathan relays:
- your branch and head;
- the record's path;
- the run of record's link and result;
- what you changed, by item;
- every proof's and reversal's result;
- every stop, limit and deviation.
