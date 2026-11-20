# SV4 A1 prompt — the rules: the block's likes and direction, the reads, the send's version, the token code removed

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 2, 20 November 2026.** Revision 1's session (from `1d55ec4`) stopped at its stop rule before any change: its search at its commit found three earlier tests the list omitted (S1, the migration leaf; S2, the discovery suite's case count; S3, the read phase's first-lock case for a suspension), and points revision 2 names. Revision 2 names each, from the brief's revision 5.
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 5 (DM-96's AG1 to AG21 applied as given; revisions 3 to 5 are the manager's: revision 4 adds three paths to A1's owned paths, which D4 and D7 need and the list omitted; revision 5 adds two docstrings D4 makes false).
- **Where the result goes:**
  - the session's changes in A1's owned paths, and its section "A1" in the SV4 record, `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.80 (confidence 0.77); rung probabilities low 0.00, medium 0.02, high 0.24, extra high 0.67, max 0.07, ultracode 0.00. Model probabilities Fable 5.1 0.10, Opus 5.5 0.90, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.87). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.002, Fable 5.1 at high 0.024, Fable 5.1 at extra high 0.067, Fable 5.1 at max 0.007, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.018, Opus 5.5 at high 0.216, Opus 5.5 at extra high 0.603, Opus 5.5 at max 0.063, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-20T03:33:50Z. Nathan picks the cell.
- **The Dev Manager's read:** done for the brief (DM-96; D-07's first read). This prompt authorizes no credential use and no live provider action, so it needs no read of its own (the charter, "Read before it takes effect"). The Dev Manager reads A1, with the brief's revisions 4 and 5, before A1 merges (D-07).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present.
- **It runs alone** (OD-29). Then, in order: the manager's verification; the pull request and Codex's review of its head; an exact-head code and security review with a written threat model (who may read a conversation; what a member learns of a block; the token surface removed); corrections only for a defect D-07 names; the Dev Manager's pre-merge read; the merge after its run, Codex's summary on the final head and its checklist.
- **Deletion condition:** prune after A1's pull request merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **implementation session for SV4 A1**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 2, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What A1 is.** The second of SV4 Stage A's three sessions: the rules chat's routes (A2) will serve, with no new route. A1 covers:
- **D3, a block retires the pair's earlier likes** (M09's C-01): a nullable `retired_at` on `DirectionalInteraction` (migration `0013`), set by `glow_chat`'s `block` on every `liked` row between the pair; both reciprocity checks require it null;
- **D4, a block's direction is not served** (C-02; DM-75): `block` ends an active match as an unmatch does, storing `unmatched`; F10 gains the transition `block` from `active` to `unmatched`;
- **D5, the reads follow OD-60's rule** (C-08): the history read, the list and the read cursor check the read rule, then each cause reads its value in `chat.history`, read-only at launch;
- **D6, the send's expected version**: a test pins that `MatchProjection.version` equals the send's `contact_version` for every writer of either;
- **D7, the token code removed** (P06.2-T), with the refusal lists, the API README's lines and the persistence docstring.

There is no provider call, deployed URL, real member, HDE call or stored credential. The runtime stays sealed.

**The brief, `docs/planning/sv4-chat-notifications.md`, revision 5, is the specification:** D1, D3 to D7, D11's bullets for D3 to D7 and "Mobile", D12's "Taken in Stage A", D13 to D15, A1's owned paths, the exclusions, the acceptance checks and the review plan. Much of its text is the Dev Manager's words (DM-96, AG1 to AG21). Follow them exactly. Where this prompt summarizes the brief, the brief wins. Where this prompt adds to the brief, it says so; those additions come from the manager's search at this prompt's commit (PF02-R14), and the brief's revisions 4 and 5 record them.

**What came before.**
- **A0 merged** with PR57 at `499ccbb` (20 November 2026): each database suite now runs in its own job (ordering, identity, profile, discovery), each with its own PostgreSQL, credentials, marker and decoy database; `main`'s push run 44657225220 passed all eleven jobs. A0 changed no application code.
- **SV3** (PR45, PR47) built discovery, interactions and the match read; SV2 built the settings store and `chat.history`'s launch default; P06.2 built `glow_chat` (contact, reads, delivery) and the token grant A1 removes.
- **Revision 1's session** (branch `claude/loving-planck-2atn59`, local only, never pushed) stopped before any change, with three stops and a list of points; revision 2 answers each below. Nothing of it is on GitHub, and you start afresh from this prompt's commit.
- **`main` is at `499ccbb`.** The manager branch has changed only Markdown since.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only A1's owned paths (the brief, revision 5):
    - `services/api/glow_chat/contact.py`, `reads.py`;
    - `services/api/glow_discovery/interactions.py` (`interact`'s reciprocity check and its write of `retired_at`, and the module docstring's sentence on D8's gap, lines 62 to 64, only; revision 5);
    - `services/api/glow_discovery/contract.py` (`match_projection`'s docstring, lines 255 and 256, only; revision 5);
    - `services/api/glow_persistence/models.py` (the docstring; `DirectionalInteraction.retired_at`) and `services/api/glow_persistence/migrations/0013_*.py`;
    - `services/api/glow_domain/chat.py`, `chat_tokens.py`, `chat_provider_stream.py`;
    - `services/api/glow_api/configuration_profiles.py` (the refusal list only);
    - `services/api/README.md`;
    - the offline tests D7 and D11 name (listed below under "Earlier tests"), and new tests;
    - `proofs/postgres-ordering/glow_ordering_proof/` (the cases D3 to D7 and D11 name, D3's and D4's new cases in the discovery suite, `discovery_cases.py`'s `CASE_COUNT`; `reference.py`'s block (D4); `environment.py`'s refusal list; the helpers only the removed code uses), and `proofs/postgres-ordering/tests/` (the tests listed below, and new ones);
    - `proofs/postgres-ordering/README.md` (its sentences on B1's token cases and on the rules A1 changes, only; revision 4);
    - `proofs/stream-chat/glow_stream_proof/conformance.py`, its tests and `proofs/stream-chat/README.md`'s paragraph on the conformance rows, only as D7 requires (revision 4 adds the README);
    - `packages/contracts/production/flows-v1.json` (D4's transition) and `packages/contracts/production/gapp-api-v1.schema.json` (`MatchProjection`'s `description`, only; revision 4), and the generated outputs, through `npm run generate`; `packages/contracts/tests/test_transition_contract.py` (its frozen F10 table);
    - `docs/architecture/production-contracts.md`, `docs/architecture/data-model.md`, `docs/adr/0004-app-database-placement.md` (D7's sentence);
    - the record;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only, through your GitHub tools: no pull request, comment, review, re-run, workflow dispatch or setting. Use `gh` for nothing but a search. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **an owned path:** the work needs a path outside the list above, including `.github/`, `scripts/`, `glow_api/` beyond the refusal list, any `apps/mobile` file other than those `npm run generate` writes in `apps/mobile/src/contracts/generated/`, another migration, an environment template or a `requirements` file;
  - **the reference design** (D3): the new write changes anything the ordering suite compares between P06.DB's reference design and the app's adapter, beyond D4's `unmatched` (which both subjects take);
  - **a product decision** (D3, D4; DM-75): the design would change D8's rule, F13's private projection, or what either member can do;
  - **the Stream proof** (D7): after the token rows below are retired, its offline tests or `checks/run_plan.py` still need the signer;
  - **a refusal rule** (D7) that would refuse a name the API itself reads (every `GLOW_*` name in `configuration_profiles.py`, `GLOW_RAILWAY_*` among them);
  - **a dependency:** a new Python or npm package, or a changed pin (D13); the `pyjwt` pin stays, since SV1 needs the package;
  - **the timeout:** a database job no longer fits its `timeout-minutes`;
  - **an earlier test:** a test not named in "Earlier tests" below would have to change in what it asserts, or any test would be weakened or deleted beyond the retirements named there. Report which and why; do not change it.
  - In each case, report it; do not narrow the brief's words to pass it. A reversal's temporary edit is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report. The manager's PR run is then the run of record.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
- **Network:**
  - **PyPI and the npm registry:** for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only;
  - **Docker Hub:** only to pull the PostgreSQL image the workflow pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run (below).

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from the pinned image, on loopback only; a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present; removed afterwards. Migrations reach that database only through the proof's own commands; never run `manage.py migrate` yourself. Local passes are "iteration, not evidence"; the run of record is CI's. `manage.py makemigrations` against the dummy backend, to write `0013`, opens no connection and is allowed.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, marker, token or key, in any form;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - call any provider or HDE; in `proofs/stream-chat/`, run only its offline tests and `checks/run_plan.py`, never its live commands;
  - connect to any database but a throwaway one you started under D4's conditions;
  - connect to HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script in your own environment;
  - weaken or delete a test to make the suite pass, beyond the retirements "Earlier tests" names.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`); the cloud container sets them (OD-76). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH (`scripts/bootstrap-toolchain.sh`). Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git merge-base --is-ancestor 499ccbbec758ed4ef34a93ad19fa8df454fb095c HEAD && echo "PR57's merge present"
git diff --quiet 499ccbbec758ed4ef34a93ad19fa8df454fb095c HEAD -- . ':!*.md' && echo "main's code"
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs packages apps docs/architecture docs/adr docs/planning/sv4-chat-notifications.md   # must print nothing
grep -c '^## A1' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md   # must print 0
ls services/api/glow_persistence/migrations | grep -c '^0013'                  # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, the live branch has changed an owned path or the brief since it, or A1's record or migration already exists.

**Then read, completely:**
- **The instructions:** root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`; `apps/mobile/AGENTS.md` (you change only generated files there).
- **The brief,** revision 4: D1, D3 to D15, "Owned paths", "Exclusions", "Acceptance checks" and "Review plan", and the revision history in its status line.
- **The Dev Manager's report** DM-96 (`docs/continuity/dev-manager/reviews/2026-11-19-dm-96-sv4-stage-a-brief.md`), sections 4 to 8 and 11, and section 14's words for D3 to D7.
- **M05's finding 22** (`docs/testing/evidence/2026-10-25-m05-project-review.md`, from line 189): the names the API accepted.
- **SV2's D19** (`docs/planning/sv2-profiles-media.md`): the pointer order a read of a setting follows.
- **The code you change,** whole: `glow_chat/contact.py`, `reads.py`; `glow_discovery/interactions.py` (`interact`, `read_own_versions`, `_match_projection`, `unmatch`); `glow_domain/chat.py`, `chat_tokens.py`, `chat_provider_stream.py`; `glow_profiles/settings_store.py` (`read_shared`, which you call and do not change); `glow_domain/profile_settings.py` (`chat.history`); and every earlier test below.

## 3. What to do

1. **D3, the block retires the pair's earlier likes.** As the brief's D3 says: `retired_at` (nullable) on `DirectionalInteraction`, one additive migration `0013`; `block` sets it, under its two account locks with the database's clock, on every `liked` row between the pair in both directions, in the same transaction, changing nothing else of the row; both reciprocity checks require it null on both rows (`activate_reciprocal`'s, and `interact`'s own check before it calls `activate_reciprocal`); no read of the actor's own row returns it; a pass, or a like that replaces a pass, writes it null. The two database cases D3 names, each with its reversal, and in each the first like reads the same state and version in its actor's own-versions read before and after the block. They go in the discovery suite (`interaction_cases.py`), the only suite that serves SV3's like and the own-versions read (S2): a named list of A1's cases after B-C1's, labelled with SV4's checks (for example "SV4-A1", "D3"), never with Stage A's or Stage B's checks; `CASE_COUNT` and the plan tests change as "Earlier tests" says. A test beside the existing migration pins in `services/api/tests/test_model_definitions.py` pins `0013` as generated (0001 to 0012 stay unchanged), and the one leaf the suite asserts becomes `0013` (S1).
2. **D4, a block ends an active match as an unmatch does.** `block` stores `unmatched`, with the same contact and version advance and the same `contact_revoked` event it writes today. F10 gains the transition (`block`, `active` to `unmatched`, `participant`, no eligibility, no policy); no row is removed. `MatchProjection` gains a `description` in `gapp-api-v1.schema.json` saying the server serves `restricted` to no member; `production-contracts.md`'s F10 and F13 paragraph and `data-model.md`'s `Match` row say a block ends an active match as an unmatch does, its cause kept in the `Block` rows. P06.DB's reference design's block (`reference.py`, line 366) changes with it. Show D4's sameness on every surface the brief lists (the send, each read, the list, discovery's exclusion, the own-versions read, a later block by the member who was blocked, the blocker's later unblock and unmatch), each with a reversal. The surfaces only the discovery suite serves get new cases in A1's list there; `block.works_after_unmatch_and_while_paused` changes only its expectations. `interactions.py`'s module docstring (lines 62 to 64) and `contract.py`'s `match_projection` docstring (lines 255 and 256) say D8's gap is closed: no command makes a match `restricted`, and a block ends it as `unmatched`. Run `npm run generate` (after `npm ci --ignore-scripts` in `packages/contracts`) and commit what it writes; record whether it changed anything.
3. **D5, the reads.** The read rule and the cause mapping exactly as the brief's D5 says, for the history read, the list and the read cursor. Read `chat.history` through `glow_profiles.settings_store.read_shared`, after the row locks, in SV2's D19 order; `reads.py` names no pointer model or table (`services/api/tests/test_profile_pointer_order.py`). Fail closed on the consent version: while the setting names `consent.onboarding.v1`, each cause reads its value; once it names any other, every cause reads `hidden`. Every hidden cause refuses with one internal reason that names no cause; the existing refusals (the block, the unmatch, the deletion, the sign-out, the expiry) keep their reasons, and the served layer maps every one to `not_found`, as `chat_projections.error_for` does today. Read-only serves the history page and the list, moves the read cursor, and refuses the send as today. Cases: each cause read-only at launch; each hidden when its setting says so; the consent limit; the block, unmatch, deletion, sign-out and expiry keep their refusal; each with a reversal. In `read.final_check_first_lock` (S3), the variant where a suspension of the lower member holds its first lock while the higher member reads now expects the read served read-only, its lock wait still observed; the lower member's own read stays refused, and `FIRST_LOCK_WRITERS` does not change. The read's protocol (shared locks in the send's order, the clock after the locks, the check before and after the provider call, no read inside a caller's transaction) does not change.
4. **D6, the send's expected version.** A test pins that `MatchProjection.version` equals the match's `contact_version` for every writer of either (today the block and the unmatch, `contact.py` lines 693 to 694 and 779 to 780), with a reversal. The contract says a match's version changes only when contact ends (`production-contracts.md`).
5. **D7, the token code removed,** as the brief's D7 lists it, keeping `_lock_shared` (the reads use it), `revocation_cutoff_sent` and `revoke_user_tokens` (the epoch revocation stays; DM-96). **Added by this prompt's search** (the brief's list is incomplete; revision 4):
   - `ContactResult.grant` and its `TokenGrant` import (`glow_domain/chat.py`, lines 25 and 127) and the outcome `granted` (line 33), with the proof's copy of the outcome (`proofs/postgres-ordering/glow_ordering_proof/interface.py`, line 37) and its docstring (lines 17 and 18);
   - `IAT_BACKDATE_SECONDS` (`chat_provider_stream.py`, line 111), used only by the signer;
   - the ordering suite's seven token cases (`cases.py`, `B1_TOKEN_CASES`, from line 1599, with the helpers only they use, from line 1441; `B1_CASES` at line 1781 then holds the activation and named cases), the adapter's grant (`adapter.py`, lines 56 to 59 and 181 to 183) and the delivery phase's refused grant (`delivery_phase.py`, lines 591 to 594, and its line 637's words);
   - **the Stream proof's token rows are history** (the brief's D7): retire from `conformance.py` the rows that need Glow's signer, T1 and T2 (`rows_signer`), R3, D3, D7, V5, V6, V7, V8 and V12, with `_grant` and `_sign` (lines 429 to 462) and every helper only the retired rows use (`_token_check`, from line 464, among them), and keep every other row (V3 and V4, the revocation and its read-back, among them). The rows' P06.2 records stand as history. Its tests follow: the row count (46), the recorded set (`M5`, `R7`, `V7`), the verdict counts, the peak connections, and each test that names or forces a retired row. `ConformanceVerdictTest` keeps each verdict's coverage on a row that stays; where no remaining row can produce a verdict, record that as a limit. `checks/run_plan.py` needs no change (it measures through the tests' conformance run). `README.md`'s row paragraph (line 250) follows.
   - **The dead code with them,** each removed only after a search at your head shows no other user, and each recorded: `TokenRefusal` (`chat_tokens.py`); the adapter fixture's `provision_identity` (`adapter.py`, line 219, and its docstring's mentions); `dbreads.identity_row` and `event_times`; `AFTER_REVOCATION_MARGIN_SECONDS` (`conformance.py`, line 68) and the tests' `no_revocation_wait`; the `INSERTED` constant (`test_interactions_offline.py`, lines 1108 to 1113) if only `ReciprocalWriterTests` uses it; and the imports the retirements leave unused (Ruff's F401).
   
   **The refusal lists** (M05 finding 22): in the API's fixture guards and the proof's environment check together, as a constant of its own beside `FORBIDDEN_CONNECTION_NAMES` (which, and its two exact pins, do not change), checked in the same presence step before any value is read, refuse by presence a `PG` prefix, the names M05 found accepted (`DATABASE_PUBLIC_URL`, `PGPASSFILE`, `PGSERVICE`, `POSTGRES_PASSWORD`, `REDIS_PUBLIC_URL`, `REDISPASSWORD`, `STREAM_API_SECRET`) and the families they stand for (Railway's database and Redis names, and a `STREAM_` prefix), each refused before any value is read, with a test per name in both places. The proof's copies still equal the API's, the new constant's included (`proofs/postgres-ordering/tests/test_settings_refusals.py`). ADR 0004's line 34 drops its "(other names … are not refused until the hardening item lands)". The API README's lines on the dormant signer and Stage C1's modules (M05 P-13), and the persistence docstring (R-23), as the brief says.
6. **The earlier tests** (below). Change each only as its reason requires, keeping what it guards. Record each changed test with its reason.
7. **The record,** section "A1" of `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`:
   - this prompt's revision and commit;
   - the start gate's and the environment check's results;
   - what was built, by D-number;
   - each earlier test changed, with its reason, and each retirement;
   - each new case and each reversal with its failing output;
   - each database job's duration on the run of record, with each suite's case count before and after;
   - the limits.

**Earlier tests** (the brief's D11 and D7, repeated by the manager at revision 1's commit and completed from revision 1's session's search; PF02-R14). These may change, and no others:
- **D3:**
  - `services/api/tests/test_interactions_offline.py`: `ReciprocalWriterTests` (from line 1343) and its digests (`MAIN_DEFINITION_DIGESTS` and `MAIN_MODULE_DIGEST`, lines 1203 to 1295), which pin `glow_chat/contact.py` as SV3 left it. D3, D4 and D7 each change `contact.py`; rewrite the class against your own head and record why. `StructureTests` (from line 722) must pass unchanged;
  - `services/api/tests/test_model_definitions.py`: gains the `0013` test; in `test_sv2_stage_a_migrations_follow_0004`, the leaf assertion (line 323) becomes `0013` and its comment (lines 319 to 321) names `0013` (S1; as SV2-R's `f4703a1` did for `0012`); no other existing test changes;
  - `proofs/postgres-ordering/tests/test_discovery_offline.py`: `DiscoveryPlanTests` (S2). `test_the_case_count_is_pinned` (lines 716 to 725) is re-pinned, with `plan()[59:66]` equal to `B_C1_CASES` and A1's list after it; `test_the_plan_covers_stage_as_and_stage_bs_acceptance_checks` (lines 671 to 714) keeps A1's cases out of Stage A's set and checks A1's own labels; `discovery_cases.py`'s `CASE_COUNT` (line 61) follows.
- **D4:**
  - `proofs/postgres-ordering/glow_ordering_proof/reference.py`, line 366, and the six ordering cases that expect `restricted` at version 2 (`cases.py`, lines 360, 758, 847, 861, 878 and 910), which then expect `unmatched`;
  - `interaction_cases.py`, `block.works_after_unmatch_and_while_paused` (lines 1046 to 1109; its expectations at lines 1082, 1089 and 1099);
  - `packages/contracts/tests/test_transition_contract.py`: the frozen F10 table (lines 911 to 918) gains the row. Its lines 697 to 707 read one sentence of `production-contracts.md`, which stays as it is.
- **D5:**
  - `proofs/postgres-ordering/glow_ordering_proof/read_phase.py`: the forced cases (`FORCED`, from line 1116, over `REVOCATIONS_READ`, line 1226) for the seven revocations whose read becomes read-only (the high account's suspension, both pauses, both restrictions, both consent withdrawals), and the list case "listed while the other is paused" (lines 1099 and 1100);
  - `read_phase.py`'s `final_check_first_lock` (lines 629 to 685; S3): the one variant above;
  - `proofs/postgres-ordering/tests/test_read_phase.py`: `ReadPlanTests` (from line 57), which counts the plan; `FirstLockReadersTests` and `ReadControlTests` must pass unchanged;
  - the block, unmatch, deletion, sign-out and expiry cases keep their refusal.
- **D7:**
  - `services/api/tests/test_chat_domain.py`: line 63 (the port's method names), line 79 (the outcomes, `granted` among them), `TokenRuleTests` (lines 228 to 290) retired; `RevocationCutoffTests` (lines 292 to 320) stay;
  - `services/api/tests/test_chat_adapter_offline.py`: `test_r2_the_grant_signals_before_commit_once` (from line 148) and `test_the_adapter_has_no_switch_and_the_grant_is_on_the_port` (from line 294);
  - `services/api/tests/test_chat_provider_stream.py`: the imports (lines 53, 56, 57 and 59), `SignerTests` (lines 1284 to 1348) retired, and the seal test's import list (line 1362);
  - `services/api/tests/test_chat_sealed_runtime.py` and `services/api/tests/test_identity_sealed_runtime.py`: each `test_the_connection_refusal_is_unchanged` (`FORBIDDEN_AT_P06_2`, from line 33; `FORBIDDEN_AT_SV1`, line 154) must pass unchanged, since the new names live in their own constant; the import check at lines 158 to 161 must pass unchanged;
  - `proofs/postgres-ordering/tests/test_case_plan.py`: `test_the_adapter_plan_adds_b1` (from line 84) is rewritten to `56 + 25 + 27`, without the seven token names, still pinning the 24 activation cases and the F2 and F5 cases; `test_the_token_cases_skew_is_shorter_than_their_sessions` (from line 117) is retired with the cases;
  - `proofs/postgres-ordering/tests/test_settings_refusals.py`: gains the new names; its rule does not change;
  - `proofs/stream-chat/tests/test_conformance.py`: lines 343 to 349 (the rows and the recorded set), 413 (the peak connections), 430, 619 and 803 (the verdict counts), 855, `test_the_signer_rows` (from line 435) retired, `ConformanceVerdictTest` (from line 446), `test_a_failing_row_exits_one_after_cleanup` (from line 825, which forces R3's failure today; it forces a row that stays), `no_revocation_wait` (lines 56 to 58, and its uses at 122, 647 and 774), and any other test naming a retired row; and `tests/test_run_plan.py` (lines 97 to 101), as above. `test_the_adapter_imports_only_the_port_the_token_module_and_the_sdk` (line 139) must pass unchanged;
  - imports a retirement leaves unused: `timedelta` (`test_chat_domain.py`, line 8), `time` and `jwt` (`test_chat_provider_stream.py`, lines 29 and 36), if unused after it.
- **Mobile:** none. The fixture adapter looks up F10's rows while it runs (`apps/mobile/src/interactions/fixture-adapter.ts`, lines 39 to 42 and 204); D4 removes none. P05.3's fixture commands (`glow_domain.interactions`) and their tests stay as they are.

Before you start, repeat the search at your own commit: every test that reads, imports or digests a module you change, or names a removed function, constant, outcome, case or row. If it finds one not named here, stop and report.

## 4. Checks, then the report

- **The trusted classifier,** from `main` (`499ccbb`), extracted outside your checkout and run from it with `python3 -I` and full SHAs: `python3 -I <trusted copy>/change_scope.py --base 499ccbbec758ed4ef34a93ad19fa8df454fb095c --head <your code head> --merge-base` prints `"full": true` (reason `behavior-or-empty`).
- **The diff:** `git diff --name-only <START_SHA> <your head>` lists only A1's owned paths.
- **The removed names are gone:** `grep -rn` over `services/api`, `proofs` and `packages` finds none of `grant_token`, `grant_chat_token`, `TokenGrant`, `TokenAccount`, `TokenSession`, `TOKEN_LIFETIME`, `NO_CHAT_IDENTITY`, `token_claims` (outside the Stream proof's own `token_claims` fields in `proof_run.py` and `mechanisms.py`), `sign_chat_token` or `IAT_BACKDATE_SECONDS`; `import jwt` is gone from `chat_provider_stream.py`.
- **The migrations match the models** (`manage.py makemigrations --check --dry-run` against the dummy backend), and `0013` is additive.
- **The generated outputs equal `npm run generate`'s** (`npm run check` in `packages/contracts`).
- **The run of record,** on your last code commit: every job passed, each database job within its timeout, the gate printed "Application checks passed", and the Stream proof's job passed.
- **Every offline test** of `services/api`, `proofs/postgres-ordering`, `proofs/stream-chat` and `packages/contracts` passes locally in a clean environment, and in the run; Ruff and mypy pass in each.

Your final message, which Nathan relays:
- your branch and head (code head and records head);
- the record's path;
- the run of record's link and result, with each database job's duration and each suite's case count;
- what you built, by D-number;
- each earlier test changed or retired, with its reason;
- each acceptance check with its evidence;
- every stop, limit and deviation.
