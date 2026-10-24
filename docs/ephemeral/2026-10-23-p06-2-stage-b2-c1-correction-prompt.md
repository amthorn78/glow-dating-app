# P06.2 Stage B2-C1 prompt — Stream's additions corrected, then B2's live rows

- **Owner:** App Manager 7 (revision 1 by App Manager 6). Nathan starts this session manually, in the **`Glow app`** environment (OD-36), and relays its report.
- **Revision 2, 23 October 2026.** Revision 1 went to the Dev Manager (DM-17), which approved it with conditions; revision 1 does not run. Revision 2 applies DM-17's conditions as written, each marked with its number, so it needs no further read (DM-03 G2). Two means of applying them are listed in the review log's DM-17 disposition: the full view in item 3, which 2.1 and 2.3 need because the written snapshot withholds most application keys by design, and the recording of a credential-like value as its type and digest, the existing credential rule applied to 2.1's listing.
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 5 with DM-17's conditions: "B2's live run stopped" (D1 to D4, points i to vi), "B2's design points" a to h with DM-16's conditions, and B2-C1's owned paths.
  - Inputs: the evidence record's "Stage B2" and "Manager verification of Stage B2"; the [Stage B2 prompt](2026-10-22-p06-2-stage-b2-implementation-prompt.md), revision 2, whose item 7 this pass completes; the [harness README](../../proofs/stream-chat/README.md); ADR 0003's condition (c); the DM-16 and DM-17 reports.
- **Where the result goes:** the session's code and tests, the new products baseline, and its section "Stage B2-C1" in the evidence record; the Foundation run on its last code commit is the run of record for the offline code; the live run is recorded from the session's own output. The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.61 (confidence 0.75); rung probabilities low 0.00, medium 0.00, high 0.08, extra high 0.22, max 0.70, ultracode 0.00. Model probabilities Fable 5.1 0.50, Opus 5.5 0.50, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.33). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.040, Fable 5.1 at extra high 0.110, Fable 5.1 at max 0.350, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.040, Opus 5.5 at extra high 0.110, Opus 5.5 at max 0.350, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: model near tie between Fable 5.1 and Opus 5.5. Sent 2026-10-23T17:32:04Z. Nathan picks the cell.
  - Revision 1's reading (Fable 5.1 at max, sent 2026-10-23T15:50:05Z) is superseded; revision 1 did not run.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** DM-17 ([report](../continuity/dev-manager/reviews/2026-10-23-dm-17-p06-2-stage-b2-drift-read.md), `0ab61e4`), of revision 1; revision 2 applies it as written.
- **Environment** (OD-36): `Glow app`, which holds `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET`. The session checks their names only and never prints, logs or copies their values; only the harness's credential loader reads them.
- **It runs alone** (OD-29). An exact-head review of B2 and B2-C1 together follows, then Codex's code review (OD-41).
- **Deletion condition:** prune after Stage B2's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session P06.2 Stage B2-C1**, which returns Stream's development application to the proof's targets and then runs Stage B2's live rows, for P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 2, from commit `<START_SHA>`.

**What exists.** Stage B2 (code head `e97f90d`, integrated into the manager branch at `957dccb`) added the Stream adapter on the chat provider port (`services/api/glow_domain/chat_provider_stream.py`), the client token's signer, and the harness's `conformance` command with 46 rows (`proofs/stream-chat/glow_stream_proof/conformance.py`). Its offline checks and its run of record passed. Its first live command, the read-only `baseline`, found 8 differences from the chat target and 7 from the Video and Feeds lockdown target, so it stopped there and nothing at Stream was changed. The differences are Stream's additions since the lockdown of 27 September (the brief's D1 to D4), and the Dev Manager approved their disposition (DM-17 item 1):

- **D1:** `glow-match`'s `channel_member` also holds `schedule-message`: remove it;
- **D2:** a new Video call type `agent` whose `user` and `guest` roles hold Stream's default grants: empty them;
- **D3:** `agent` is not in the committed products baseline, and the four known call types carry a new `lifecycle` settings section: re-baseline, keeping the pre-lockdown client grants (item 2);
- **D4:** a new default chat channel type `agent`, with client grants, which the chat target does not inspect, since it names only five default types: lock it, and cover every channel type.

**What B2-C1 does.** Offline, you widen the chat target so that every channel type other than `glow-match` must hold no grant, prepare the merged products baseline, add a read-only full view of the configuration with an offline comparison, and align the API's development lock with the harness's. Live, you record the new products baseline, apply the chat target and the Video and Feeds lockdown once each with a full comparison around each apply, confirm both counts are 0, and then run B2's live rows from its item 7.2. **No app runtime gains a database, real authentication or a live provider.**

- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 6);
  - push only your own session branch. Each push runs the Foundation workflow on your branch; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any `STREAM_*` value, a token, a signature, a marker or any other credential, in any form;
  - call any Stream application but 1729640, or any Stream product but Chat, except the read-only Video and Feeds reads and the one Video `PUT` that item 4.4 plans; create a call, a feed, an activity or an invite;
  - run `restore --apply`, a second `configure --apply`, a second `configure --products video,feeds --apply`, or any other command that changes the application's settings, roles, grants or channel or call types;
  - connect to any database, HDE, Railway or any other provider;
  - run `playwright install` or `eas`;
  - add a dependency anywhere, or change a version except item 4's alignment (DM-17 3.3).

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **The three `STREAM_*` names must be present:** `compgen -e | grep -E '^STREAM_'` prints names only. Expected: `STREAM_API_KEY`, `STREAM_API_SECRET`, `STREAM_APP_ID`. If any is missing, stop and report: this session must start in `Glow app`. Never read their values yourself; the harness's credential loader does.
3. No `PG*` or `PROOF_DB_*` name should be set; report any name present, never its value.
4. **No `.env` file:** `ls -a . services/api proofs/stream-chat | grep -x '\.env'` must print nothing. If one exists, report it without reading it, and stop.
5. The pinned toolchain is in `$HOME/.local/bin`: Node 24.19.0, npm 11.9.0 and Python 3.12.14. Put `$HOME/.local/bin` first on PATH, then record `command -v python3.12` and its version. The API README's lock command names uv 0.12.17, which the pinned toolchain lacks; as Stage B2 did, install uv 0.12.17 into a scratch virtual environment outside the checkout for item 4 only, record its path and version, and commit nothing of it.
6. Run every command in a clean process environment, as `docs/operations/local-development.md` and the harness's README show, in the form Stage B2's record shows for its live command (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, the three `STREAM_*` names by reference only to the harness's live commands, and the proxy and CA variables by reference).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/ proofs/ .github/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage B2-C1'   # must print 0
```

If code or this pass's section has already landed on the live manager branch, this prompt is stale: stop and report (AM5-15). If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`, `services/api/AGENTS.md` if present, `services/api/README.md` and `proofs/stream-chat/README.md`, whole;
- the P06.2 brief (revision 5 with DM-17's conditions), whole, and the DM-16 and DM-17 reports in `docs/continuity/dev-manager/reviews/`;
- ADR 0003's "Conditions", and the chat-provider architecture document, section 5;
- the evidence record's "Stage B2" and "Manager verification of Stage B2";
- in `proofs/stream-chat/`: `glow_stream_proof/configuration.py`, `products.py`, `baseline.py`, `workdir.py`, `cli.py` (the `baseline`, `configure`, `configure --products`, `record-products-baseline`, `restore`, `verify-clean`, `cleanup` and `conformance` commands), `guard.py`'s configure scope, `conformance.py`, the committed `baseline/video-feeds-1729640-2026-09-27.json`, and the tests and fakes that model the two baselines;
- `services/api/tests/test_dependency_pins.py`, `services/api/requirements-dev.in`, both API locks, `proofs/stream-chat/requirements.lock` and `services/api/dependency-inventory.json`.

## 3. The work, offline first

Each code change gets a test that fails without it, with its reversal made in a scratch copy outside the checkout (`git status` clean afterwards; DM-14 item 6).

1. **The chat target's coverage** (brief point i).
   - `configuration.verify` reports a difference for any grant held by any role in any channel type other than `glow-match`, not only in the five default types, which must still exist.
   - `configure`'s plan empties every such type the snapshot shows, with the same request shape as the five default types' (its `automod`, `automod_behavior` and `max_message_length` from the snapshot, every role's grants `[]`).
   - `restore` leaves untouched a channel type that the pre-proof baseline (`baseline/application-1729640-2026-09-25.json`) does not hold, and the README says so.
   - The offline fakes gain a sixth, non-default channel type with client grants, so the tests show it is a difference, is planned and verifies once locked.
2. **The merged products baseline** (brief point ii; DM-17 1.1 and 2.2).
   - `record-products-baseline` writes a record that takes, **for every scope the 27 September file holds** (each call type and feed visibility), the client roles' grants (`user`, `guest`, `anonymous`) from `baseline/video-feeds-1729640-2026-09-27.json` unchanged, and everything else from the fresh snapshot. A scope the 27 September file does not hold (`agent`) takes its client grants as read from the snapshot, before its lockdown. The merge lives in `products.py`'s record function or in `cli.py`'s `record-products-baseline`, whichever you choose; record which, and why.
   - The file then still means "each scope's grants before the lockdown". `verify` ignores client roles in `baseline_differences`, so the merge changes no verification; a test shows that too.
   - An offline test shows the merge on the fakes: a snapshot whose known scopes hold empty client grants and a new scope with client grants gives a record whose known scopes carry the old file's client grants and whose new scope carries the snapshot's.
   - `products` reads the new baseline through its one constant (`PRODUCTS_BASELINE`), with the fakes and tests updated to model it. The README names the new file. The committed `baseline/video-feeds-1729640-2026-09-27.json` and `baseline/application-1729640-2026-09-25.json` stay byte-identical and are kept.
   - Commit item 1 first. Item 2's code goes in the same commit as the new baseline file (item 4.2 of section 4), so that no commit names a file that does not exist.
3. **The full view and its comparison** (DM-17 2.1 and 2.3). The written `baseline` snapshot keeps only the application settings the target names (`APP_SETTING_KEYS`) and withholds the rest by design, so 2.1's listing and 2.3's comparison need a fuller read:
   - **a read-only command** (for example `full-view`) that reads, through the harness's `ServerApi` under its guard and with GETs only, the application (`/api/v2/app`: every settings key and the `.app` grants), every chat channel type, and every Video call type and Feeds visibility and feed group (the reads `baseline` already makes), and writes one JSON file to `.work/` through `workdir`'s checked writer. A test shows it sends nothing but GETs.
   - **Credential-like values are never written** (the standing credential rule, applied to 2.1): a value under a key whose name contains `key`, `secret`, `token`, `password`, `credential`, `certificate`, `private` or `url`, or anywhere under push, SQS, SNS or webhook configuration, is written as its JSON type, whether it is empty, and the SHA-256 of its canonical JSON, never the value. A change is still seen; the value is not. The list of such keys is a constant, tested, and recorded whole in your section.
   - **an offline comparison** of two full views: every field compared, value and type, with only named volatile fields left aside (for example `created_at` and `updated_at`), each name in one constant and in your record. Its output lists each changed path with its before and after (or digest). Tests on the fakes show a change in an unnamed field is reported and a change in a named volatile field is not.
4. **The lock alignment** (DM-17 5.1 and 3.3), offline, before any live command, so the live rows run under the lock the API merges.
   - Regenerate `services/api/requirements-dev.lock` with the API README's command (uv 0.12.17, `--python-version 3.12 --generate-hashes --no-header`), adding the harness's `proofs/stream-chat/requirements.lock` as a constraint, so that every package the two locks share resolves to the harness's version with the same hashes. `tzdata`, which only the API holds, stays as resolved. Record the exact command. Never edit a lock by hand. If a shared package resolves to the harness's version with a different set of hashes, or a shared package cannot take the harness's version, stop and report before any live command.
   - Expected movement: the nine packages Stage B2 reported at later versions (certifi, charset-normalizer, ijson, pydantic, pydantic-core, pydantic-settings, pyee, python-dateutil, python-dotenv) move to the harness's versions; nothing else moves. Record the before and after of every package that moves.
   - Regenerate `services/api/dependency-inventory.json` from the installed metadata, as Stage B2 did.
   - Extend `services/api/tests/test_dependency_pins.py` from three packages to **every package the two locks share**: the same version and the same set of hashes, each as a subtest; the report-only method gives way to this check. Its reversal: a lock naming another version of one shared package fails.
   - `services/api/requirements.lock`, `requirements-dev.in`, `pyproject.toml` and the README stay unchanged. Report whether the README's documented lock command, run as written, still reproduces the lock; don't change it.
5. **Offline checks pass** (section 5, items 1 to 4) before any live command.

## 4. The live run, in this order

The command form is Stage B2's (section 1, item 6). Record each command's exact result lines.

1. **`baseline`** (read-only), then **`full-view`** (read-only); call the view **V0**.
   - With item 1's coverage, `baseline`'s differences must be exactly B2's 8 chat and 7 Video and Feeds lines, as Stage B2's record lists them, plus one chat line for each role of the chat type `agent` that holds a grant. **Any other difference, or any of these changed, stops the session:** record it and report.
   - From the same snapshot, list every field of `glow-match` that `MATCH_FEATURES` does not name, with its value.
   - **From V0, list every application settings key that the 25 September record (`app_settings`) and the target do not name, with its value** (a credential-like value as item 3 writes it) (DM-17 2.1).
   - If a field of `glow-match` or an application key turns on a content feature or a client write, report it first and stop before item 4.2.
2. **The new products baseline** (D3; DM-17 1.1): `record-products-baseline --snapshot <item 4.1's snapshot>` writes `baseline/video-feeds-1729640-<today>.json`, merged as section 3 item 2 says. Record its diff against `video-feeds-1729640-2026-09-27.json` whole: it must be the call type `agent` and a `lifecycle` section on each of `audio_room`, `default`, `development` and `livestream`, and nothing else; otherwise stop. Scan the file as every record is scanned (no identifier, token or secret). Commit it with item 2's code before any apply; you may push it then, and the apply need not wait for its Foundation run.
3. **The chat target** (D1, D4):
   1. `configure` (dry run). For each planned request, show from the snapshot that it either re-sends values the snapshot already holds or corrects D1 (`glow-match`'s `channel_member`: `read-channel` alone) or D4 (the chat type `agent`: every role's grants `[]`). Anything else stops the session before the apply.
   2. `configure --apply`, once. **It runs outside the guard** (`cmd_configure`'s own comment), as on 25 September: it re-sends the application `PATCH`, the default types and `glow-match`. That is accepted for this one reviewed command with the dry-run check above and the comparison below (DM-17 2.4); a differential chat apply under a guard is P11's. Its chat differences after (the lines without the `video/feeds: ` prefix) must be `[]`; the Video and Feeds lines that remain must be D2's two. Otherwise stop: no second apply, no restore.
   3. `full-view`: **V1**. Compare V0 with V1 (item 3's comparison). **The only changes allowed are D1 and D4** (DM-17 2.3). Anything else is reported first, before any further command.
4. **The Video and Feeds lockdown** (D2):
   1. `configure --products video,feeds` (dry run). The plan must be exactly one `PUT /api/v2/video/calltypes/agent` naming `user` and `guest` with `[]`, and nothing for Feeds; otherwise stop.
   2. `configure --products video,feeds --apply`, once. Its differences after must be `[]`. Otherwise stop.
   3. `full-view`: **V2**. Compare V1 with V2. **The only change allowed is D2.** Anything else is reported first, before any further command.
5. **`baseline`:** both counts 0. Otherwise stop.
6. **B2's live run from its item 7.2, unchanged:** `verify-clean`; `conformance` with its 46 rows (`--accept-dashboard-user` as B2's command takes it); `cleanup --apply` if the run did not clean up, then `verify-clean`; the closing `baseline`, both counts 0. B2's rules hold as its prompt states them:
   - **the rerun rule** (DM-16 1.3): one rerun of `conformance` only when the first run stopped on something other than a charge or limit signal, its cleanup and `verify-clean` passed, the cause is recorded, and the fix, if any, is offline, in section 6's rerun paths, with its checks passing; otherwise, and after a second stop, stop and report;
   - **the blocking rule** (DM-16 5.2): a code that differs from the fixture's for F3 and CX6's causes (rows C4, R8, D10 and V13) blocks B2's merge until it is dispositioned; report it first;
   - **every other difference** between Stream's outcome and the fixture's is a finding, reported, not fixed silently; R7's answer (a send by a removed member) is recorded either way.
- **A half-applied state is reported, not repaired** (DM-17 3.4). If an apply fails part-way, stop with its record. Run `full-view` once (read-only) and compare it with the view before that apply. Report which requests were applied (the `configure` record's applied steps), the failure, and that comparison. Run nothing else: the development application's state is then a new decision, not this session's.
- **Budget and stops:** the harness's guardrails as they are. A charge or limit signal stops the session at once, deleting nothing, and you report it; a rate limit only: wait as the README says. Record the API calls each command used.

**Not in B2-C1:** any change to B2's adapter, signer or command except a fix under the rerun rule; any role or scope beyond D1, D2 and D4; the `admin` and resource roles; the dashboard user; the committed baselines; Feeds; the mobile app; any dependency or version beyond item 4's alignment.

**Rules for every change:** no weakened check, guard, deny-list or budget; no credential, token or signature in any file, log line, record or report; the harness's other commands and their results unchanged.

**Findings outside this work:** report each with its class. Fix it here only if it could let a credential leak, let a request reach Stream outside the guard or the configure scope, or let the configuration commands change anything beyond D1, D2 and D4.

**A departure** from any of the above that you find necessary: stop before making it and report it; it goes to the Dev Manager.

## 5. Checks

Report the exact commands and results.

1. `git diff --check <START_SHA> HEAD` and `git diff --name-only <START_SHA> HEAD`: only owned paths changed.
2. Classification with the trusted policy from `main`, outside the tree: `base=$(git rev-parse origin/main); d=$(mktemp -d); git show "$base:scripts/change_scope.py" > "$d/change_scope.py"; python3 -I "$d/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base`. Expected: full scope.
3. Hash-locked installs and `pip check` for the API (with the aligned lock) and the harness; `npm ci` for the harness's client, with `npm audit`'s advisory named (package, severity, advisory ID; no change).
4. The offline checks: the API's tests (329 at the start), the harness's tests (605 at the start), Ruff, mypy, the static check with `makemigrations --check --dry-run`, the sealed-runtime and pin tests, the harness's `node --check` and its run-plan count.
5. **The live run:** each command's exact result lines; item 4.1's differences, `glow-match`'s unnamed fields and the application's unnamed keys; the new baseline's diff; each dry-run plan with its check; each apply's differences after; both comparisons (V0 with V1, V1 with V2) whole; every `baseline` run's two counts; each conformance row's result; each mapping with its row; the API calls used; `verify-clean`'s results; whether a rerun was used, and why. No value of any `STREAM_*` variable, token, signature or other credential in what you record.
6. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs), the database job's duration, and the gate's line `Application checks passed`. Push nothing more until that run has finished (AM5-14). CI has no Stream secret; it runs the offline checks only.
7. A secret scan over your whole diff, the new baseline, every `.work/` file you cite and your record.

## 6. Owned paths, push and records

- **You may change:**
  - `proofs/stream-chat/**`: `glow_stream_proof/configuration.py` (item 1); `products.py` (the baseline's constant and, if you put it there, the merge; item 2); `cli.py`'s `record-products-baseline` (if the merge goes there) and the new read-only command (item 3); a new module for the full view and its comparison (item 3); the new `baseline/video-feeds-1729640-<today>.json` written by `record-products-baseline`; their tests and fakes; the README. Not the guard, the deny-lists, the budget, the stop signals, cleanup's rules, the committed baselines, the other commands or any dependency file;
  - **for the lock alignment only** (item 4; DM-17 3.3): `services/api/requirements-dev.lock`, `services/api/dependency-inventory.json` and `services/api/tests/test_dependency_pins.py`;
  - **for a fix under the rerun rule only:** `services/api/glow_domain/chat_provider_stream.py` and `services/api/tests/test_chat_provider_stream.py`; `proofs/stream-chat/glow_stream_proof/conformance.py`, `cli.py`'s `conformance` command, and their tests;
  - the evidence record: a new section "Stage B2-C1" after the existing sections, which stay byte-identical.
- **Nothing else.** Report any other change you think is needed, before making it.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage B2-C1":** the prompt's revision and start SHA, your head, your branch and the run of record; items 1 to 4, each done (`file:line` and its test) or left (the reason), with item 2's choice of home and item 3's two constants; the lock command and every package that moved; the live run, step by step, with section 5 item 5's contents; the conformance rows' results, row by row; each mapping with its row; the API calls used; every check with its exact results; deviations and limits; what the exact-head review must know.

## 7. Report

Your final message is the report Nathan relays: the prompt revision (revision 2, from `<START_SHA>`); the environment check (names only, the `.env` check included); your branch, head SHA and changed paths; first, whether the session stopped and where, and any code that differs from the fixture's for the causes in F3 and CX6's rows; items 1 to 4, with every package the alignment moved; the application's and `glow-match`'s unnamed fields; every `baseline` run's counts; the applies' results and both comparisons; the conformance rows' results; the API calls used; every check with its exact results, and the run of record's details; deviations, departures you stopped at, findings outside the work with their class, and limits.
