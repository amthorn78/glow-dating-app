# SV4 A1 exact-head review prompt — the rules, with a written threat model

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 20 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 5, "Review plan" (an exact-head code and security review of each stage, with a written threat model for A1 and A2).
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Exact-head review of A1", with a disposition for each finding (a correction before the merge, or carried), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.98 (confidence 0.90); rung probabilities low 0.00, medium 0.00, high 0.08, extra high 0.85, max 0.07, ultracode 0.00. Model probabilities Fable 5.1 0.14, Opus 5.5 0.86, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.81). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.011, Fable 5.1 at extra high 0.119, Fable 5.1 at max 0.010, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.069, Opus 5.5 at extra high 0.731, Opus 5.5 at max 0.060, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-20T06:02:40Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. The Dev Manager's pre-merge read of A1 follows this review (D-07).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present.
- **It runs alone** (OD-29), after Codex's review of PR58's head (manager workflow, step 6). A full review of A1's code, not a delta review.
- **Deletion condition:** prune after A1's pull request (PR58) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head review of SV4 A1**, the rules chat's routes will serve, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head in full, with a written threat model. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **SV4's brief,** revision 5 (`docs/planning/sv4-chat-notifications.md`). Its D3 to D7 set A1: a block retires the pair's earlier likes (D3; M09's C-01); a block ends an active match as an unmatch does, so its direction is not served (D4; C-02, DM-75); the history read, the list and the read cursor follow OD-60's rule through `chat.history` (D5; C-08); the send's expected version is the match's version (D6); the dormant token-signing code is removed, with the refusal lists (D7; P06.2-T, M05 finding 22). Much of it is the Dev Manager's words (DM-96, AG1 to AG21; `docs/continuity/dev-manager/reviews/2026-11-19-dm-96-sv4-stage-a-brief.md`). Revisions 3 to 5 are the manager's, for the Dev Manager's pre-merge read.
- **The implementation** (branch `claude/sleepy-mendel-0kqgw9`, code head `bc0675d`, records head `a1651fb`; the evidence record `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, section "A1"): run of record 44679608400, all eleven jobs passed. Its first session (from the prompt's revision 1) stopped before any change at its stop rule; the second, from revision 2, built A1. The manager verified it ("Manager verification of A1") and took it into the manager branch by fast-forward. PR58 carries it into `main`, which is at `499ccbb` (PR57, SV4 A0).

**The code head under review is `bc0675d`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `bc0675d` (the start gate checks this).

**Your scope:**
- **The code:** `git diff 499ccbbec758ed4ef34a93ad19fa8df454fb095c bc0675de3c6a4411f1d72845c69f8dc4e5706463`, its 40 non-Markdown paths, read in full at `bc0675d`, each changed module whole, beside its version at `499ccbb`:
  - the API: `glow_chat/contact.py`, `reads.py`; `glow_discovery/interactions.py`, `contract.py`; `glow_domain/chat.py`, `chat_tokens.py`, `chat_provider_stream.py`; `glow_api/configuration_profiles.py`; `glow_persistence/models.py` and `migrations/0013_interaction_retired_at.py`; the tests changed and added under `services/api/tests/`;
  - the ordering proof: `glow_ordering_proof/` (the cases, the read phase, the reference design, the adapter, the interface, `dbreads.py`, `delivery_phase.py`, `environment.py`) and its tests;
  - the Stream proof: `glow_stream_proof/conformance.py` and its tests;
  - the contracts: `packages/contracts/production/flows-v1.json`, `gapp-api-v1.schema.json`, `tests/test_transition_contract.py`, and the two generated files in `apps/mobile/src/contracts/generated/`.
- **The Markdown, as claims about the code:** `docs/architecture/production-contracts.md`, `docs/architecture/data-model.md`, `docs/adr/0004-app-database-placement.md`, `services/api/README.md`, `proofs/postgres-ordering/README.md`, `proofs/stream-chat/README.md`, and the evidence record's section "A1" with "Manager verification of A1", whole.
- **The runs:** 44679608400 (the run of record) and the PR run on PR58's head (event `pull_request`), once it has finished.
- **Out of scope:** chat's routes and contract additions (A2's D8 to D10), notifications (Stage B), and the mobile app, which A1 does not change beyond the two generated files. Report only where A1's change affects them.

**The threat model.** Write it in your report:
- **Assets:**
  - a conversation's history, its list entry and its read cursor, which only a member the read rule admits may read;
  - a block's direction, and the fact that a block (not an unmatch) ended a match, which the member who did not block must not learn from any state, version, answer, refusal or listing;
  - a like made before a block, which must never count toward a match, and must still read the same to its own actor;
  - `chat.history`'s settings and their consent limit, which decide whether a cause reads read-only or hidden;
  - the API's fixture guards, which refuse inherited connection and provider names by presence before any value is read;
  - the provider-token surface, which D7 removes, and the epoch revocation, which stays (DM-96);
  - the proofs' evidence: the ordering suite's comparison of the reference design and the app's adapter, the read phase, the discovery suite, and the Stream proof's conformance.
- **Actors:**
  - a member reading a conversation, listing conversations or moving a read cursor, in any state the brief names (paused, incomplete, restricted, removed, suspended, deleted, consent withdrawn, blocked, unmatched, signed out, expired);
  - the other member of the pair, in each of those states, and the member who blocked;
  - a concurrent writer: a block, an unmatch, a pause, a restriction, a suspension, a consent withdrawal, a sign-out, or a publication of `chat.history`;
  - an inherited environment variable in a runner or a future host;
  - a later change that depends on A1 (A2, Stage B, integration).
- **Entry points:** `glow_chat.contact`'s `block`, `unblock`, `unmatch`, `activate_reciprocal` and send; `glow_discovery.interactions`' `interact` and `read_own_versions`; `glow_chat.reads`' history read, list and cursor; `configuration_profiles.forbidden_configuration`; the proofs' cases and harnesses.

For each threat, give the code that stops it and the test or run that proves it. The focus:
1. **D3, the retired likes.** `block` sets `retired_at` on every unretired `liked` row between the pair, both ways, under both account locks with the database's clock, and writes nothing else of a row. Both reciprocity checks require it null. Search every reader of a `liked` `DirectionalInteraction` row at `bc0675d` (activation, discovery's predicates and pages, the own-versions read, notifications, the proofs' oracles) and say whether any still counts a retired like, or reveals `retired_at`, or answers differently for it in a way that tells either member of the block. Say whether a later like after a block and unblock is recorded with no match and never refused for the retired like, and whether the first like reads the same state and version to its actor before and after.
2. **D4, a block's direction.** `block` stores `unmatched` with the same contact and version advance and the same `contact_revoked` event. On each surface the brief's D4 lists (the send, each read, the list, discovery's exclusion, the own-versions read, a later block by the member who was blocked, the blocker's later unblock and unmatch), say whether what the member who did not block is served (state, version, answers to their own commands and reads, refusals, events they can observe) is the same after a block as after an unmatch. Search every writer and reader of `restricted` at `bc0675d` and say whether any server path still writes it or treats it apart. F10's new row, `MatchProjection`'s description, and the reference design's change.
3. **D5, the reads.**
   - The rule against the brief's D5, condition by condition: the reader's session and account, the match, a block either way, the other account's states, each cause (`own_pause`, `other_pause` with SV2's `incomplete`, `restriction`, a `removed` profile hidden, `suspension`, `withdrawn_consent`), and the consent limit failing closed on any version but the launch one.
   - **One refusal, never naming the cause:** every hidden cause refuses with `conversation_hidden`; say whether the order of the checks, a refusal's reason, its timing, the list's omissions or a cursor's answer lets a reader tell which cause hid a conversation, or that the other member blocked, paused, was restricted or suspended. Say what reaches the served layer (`glow_domain.chat_projections`).
   - **The lock order:** `chat.history`'s pointer is taken `FOR SHARE` through `settings_store.read_shared` after the row locks (SV2's D19). Say whether a read and a publication of the setting, or a read and any writer, can deadlock or cross, and whether the `_Pointers` transaction shim gives the store what its D19 check needs. Say what a setting the store cannot resolve does to a read.
   - **Read-only:** the page, the list entry and the cursor's move are served; the send still refuses. The read's protocol (shared locks in the send's order, the clock after the locks, the check before and after the provider call, no read inside a caller's transaction) is unchanged. `final_check_first_lock`'s suspension variant.
4. **D6, the version equality.** The offline test's detection of every writer of a match's `version` or `contact_version`: say whether a writer could escape it (another module, raw SQL, a queryset update, a bulk operation, a migration).
5. **D7, the token surface.**
   - The grant, the signer, the `granted` outcome, `IAT_BACKDATE_SECONDS`, the ordering suite's seven token cases and the Stream proof's ten signer rows are gone, with the code only they used; the epoch revocation (`revoke_user_tokens`, `revocation_cutoff_sent`) stays and is still proven where it was.
   - **The refusal lists:** `FORBIDDEN_INHERITED_NAMES` and `FORBIDDEN_INHERITED_PREFIXES` (`PG`, `POSTGRES_`, `REDIS`, `STREAM_`), checked in the same presence step as `FORBIDDEN_CONNECTION_NAMES`, before any value is read. Say whether a prefix refuses a name the API reads (every `GLOW_*` name), or one a later profile needs (`configuration_profiles.py`'s slots), and whether a Railway or Stream name M05 meant escapes them. You may read Railway's and Stream's public documentation pages on their variables, read only. The proof's copy and its equality test.
   - The Stream proof's remaining rows and verdict coverage (`ConformanceVerdictTest`), and whether its offline tests or `checks/run_plan.py` still reach anything removed.
6. **The earlier tests.** Each changed test is one A1's prompt, revision 2, listed under "Earlier tests" (at `docs/ephemeral/2026-11-20-sv4-a1-rules-prompt.md` on the manager branch), changed only as its reason requires. `ReciprocalWriterTests`' rewrite (SV3's digests kept, A1's pinned, `MAIN_MODULE_DIGEST` removed): say whether it still guards what SV3's class guarded. The retirements, the plan counts (`56 + 25 + 27`, read 66, discovery 70) and each new test: say whether any is vacuous, and whether each reversal the record names fails its test.
7. **The migration:** `0013` adds one nullable field and nothing else; the models match it.
8. **The seal and the boundary:** A1 adds no route, served URL, provider call, credential, dependency or pin; the runtime's settings and URL configuration are unchanged; HDE's ports and adapters are untouched (OD-80).
9. **The records:** every claim in the docs, the READMEs and the record's section "A1" holds against the code and the runs.
10. **The lines outside A1's owned paths** that A1 made stale (the record's "Limits and deviations"; carried by the manager): say, for each, whether it is a defect D-07 names (application behaviour, a security boundary, or a false claim) or a record to carry, and whether any other such line exists.

**Re-run, at least,** in a scratch copy of `bc0675d`, each package in a virtual environment installed from its own lock with `pip install --require-hashes`, under `env -i`:
- **The API:** `GLOW_ENV=test python manage.py check && GLOW_ENV=test python manage.py test tests`; `ruff check .`, `ruff format --check .` and `mypy`; `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests`; `GLOW_ENV=test python manage.py makemigrations --check --dry-run`.
- **The ordering proof:** its offline tests, `ruff` and `mypy`.
- **The Stream proof:** after `npm ci --ignore-scripts` in `proofs/stream-chat`, its offline tests, `ruff`, `mypy` and `python checks/run_plan.py` (never its live commands).
- **The contracts:** after `npm ci --ignore-scripts` in `packages/contracts`, `node scripts/generate.mjs --check`.
- **Reversals, offline, on copies,** each restored afterwards:
  - `reads.readable` made to return true whatever the setting says: a read-rule test fails;
  - one inherited prefix removed from the API's constants, and from the proof's copy: a refusal test fails each way;
  - a third writer of a match's `version` added in a scratch module the detector scans: the D6 test fails;
  - `retired_at__isnull=True` removed from `activate_reciprocal`'s check: an offline test fails, or say that only the database case catches it.
- **The database suites, informational:** the discovery suite's A1 cases and the read phase on a throwaway PostgreSQL under P06.DB's D4, if Docker allows.

**What comes after this review: the correction classes** (D-07; the manager workflow). Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that is:
- a defect in application behaviour: a retired like that still counts, a block still told apart from an unmatch on any surface, a read admitted or refused against D5's rule, a refusal that names a cause, a deadlock or a crossing, a refusal list that refuses a name the API reads;
- at a security boundary: a reader who should be refused who is served, a credential or connection value read before its refusal, a token path left reachable, a seal or HDE boundary crossed;
- a false claim: a record, README, doc or test name that claims more than the code, the tests or the runs show.

A missing test is a correction only when the behaviour is at a security boundary or an acceptance check rests on it. Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches. Read GitHub only through your GitHub tools; use `gh` for nothing but a search.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI and the npm registry, for hash-locked installs from the existing locks in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the workflow pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, through your tools, to read runs; Railway's and Stream's public documentation pages on their variables, to read only.

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from that image, on loopback only; a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present; removed afterwards. Migrations reach that database only through the proof's own commands; never run `manage.py migrate` yourself.
- **Never:**
  - dump the environment, or print a credential, password, marker, token, session key or key;
  - read, print or use the value of any `AWS_*` variable (section 1);
  - call any provider or HDE; in `proofs/stream-chat/`, run only its offline tests and `checks/run_plan.py`, never its live commands;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`); the cloud container sets them (OD-76). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 499ccbbec758ed4ef34a93ad19fa8df454fb095c
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet bc0675de3c6a4411f1d72845c69f8dc4e5706463 HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet bc0675de3c6a4411f1d72845c69f8dc4e5706463 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after bc0675d"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-19-sv4-chat-notifications.md | grep -c -E '^#+ Exact-head review of A1'   # must print 0
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, a non-Markdown path changed there after `bc0675d`, or this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Run it from the checkout (the policy file outside it). Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 5: D1, D3 to D15, "Owned paths" (A1), "Exclusions", "Acceptance checks", "Review plan", and the revision history in its status line;
- DM-96's report, sections 4 to 8, 11 and 14;
- A1's prompt, revision 2 (`docs/ephemeral/2026-11-20-sv4-a1-rules-prompt.md`), its "Earlier tests" above all;
- M05's finding 22 (`docs/testing/evidence/2026-10-25-m05-project-review.md`, from line 189);
- SV2's D2 and D19 (`docs/planning/sv2-profiles-media.md`);
- the evidence record's section "A1", whole, with "Manager verification of A1";
- every file in the code diff, whole, beside its version at `499ccbb`.

**The runs,** with your GitHub tools: 44679608400 and the PR run on PR58's head, if it has finished: every job's conclusion and duration, and the gate's line.

## 3. What to do

1. Write the threat model, then review the change against the focus, item by item.
2. In a scratch copy of `bc0675d`: re-run the checks and the reversals above, and any you doubt; run the database cases locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the threat model, each threat with its stopping code and its test or run;
- the focus, item by item, with your verdict on each;
- every finding, with its severity, file and line, evidence and correction class;
- the checks and reversals you re-ran, each with its exact result, and any local run;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.
