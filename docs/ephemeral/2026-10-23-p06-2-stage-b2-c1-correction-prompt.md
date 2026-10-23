# P06.2 Stage B2-C1 prompt — Stream's additions corrected, then B2's live rows

- **Owner:** App Manager 6. Nathan starts this session manually, in the **`Glow app`** environment (OD-36), and relays its report.
- **Revision 1, 23 October 2026.** It goes to the Dev Manager first (DM-17): it authorizes the Stream secret and live configuration changes at application 1729640, so the Dev Manager reads it before Nathan runs it (the [charter](../planning/dev-manager.md)).
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 5: "B2's live run stopped" (D1 to D4, points i to vi), "B2's design points" a to h with DM-16's conditions, and B2-C1's owned paths.
  - Inputs: the evidence record's "Stage B2" and "Manager verification of Stage B2"; the [Stage B2 prompt](2026-10-22-p06-2-stage-b2-implementation-prompt.md), revision 2, whose item 7 this pass completes; the [harness README](../../proofs/stream-chat/README.md); ADR 0003's condition (c); the DM-16 and DM-17 reports.
- **Where the result goes:** the session's code and tests, the new products baseline, and its section "Stage B2-C1" in the evidence record; the Foundation run on its last code commit is the run of record for the offline code; the live run is recorded from the session's own output. The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.97 (confidence 0.97); rung probabilities low 0.00, medium 0.00, high 0.01, extra high 0.01, max 0.97, ultracode 0.01. Model probabilities Fable 5.1 0.90, Opus 5.5 0.10, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.87). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.009, Fable 5.1 at extra high 0.009, Fable 5.1 at max 0.873, Fable 5.1 at ultracode 0.009, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.001, Opus 5.5 at extra high 0.001, Opus 5.5 at max 0.097, Opus 5.5 at ultracode 0.001, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-23T15:50:05Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** DM-17, before Nathan runs it.
- **Environment** (OD-36): `Glow app`, which holds `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET`. The session checks their names only and never prints, logs or copies their values; only the harness's credential loader reads them.
- **It runs alone** (OD-29). An exact-head review of B2 and B2-C1 together follows, then Codex's code review (OD-41).
- **Deletion condition:** prune after Stage B2's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session P06.2 Stage B2-C1**, which returns Stream's development application to the proof's targets and then runs Stage B2's live rows, for P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stage B2 (code head `e97f90d`, integrated into the manager branch at `957dccb`) added the Stream adapter on the chat provider port (`services/api/glow_domain/chat_provider_stream.py`), the client token's signer, and the harness's `conformance` command with 46 rows (`proofs/stream-chat/glow_stream_proof/conformance.py`). Its offline checks and its run of record passed. Its first live command, the read-only `baseline`, found 8 differences from the chat target and 7 from the Video and Feeds lockdown target, so it stopped there and nothing at Stream was changed. The differences are Stream's additions since the lockdown of 27 September (the brief's D1 to D4):

- **D1:** `glow-match`'s `channel_member` also holds `schedule-message`;
- **D2:** a new Video call type `agent` whose `user` and `guest` roles hold Stream's default grants;
- **D3:** `agent` is not in the committed products baseline, and the four known call types carry a new `lifecycle` settings section;
- **D4:** a new default chat channel type `agent`, with client grants, which the chat target does not inspect, since it names only five default types.

**What B2-C1 does.** You widen the chat target so that every channel type other than `glow-match` must hold no grant, record a new products baseline, apply the chat target and the Video and Feeds lockdown once each, confirm both counts are 0, and then run B2's live rows from its item 7.2. **No app runtime gains a database, real authentication or a live provider.**

- Nathan started you manually and will relay your report to the manager (App Manager 6). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 6);
  - push only your own session branch. Each push runs the Foundation workflow on your branch; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any `STREAM_*` value, a token, a signature or a marker, in any form;
  - call any Stream application but 1729640, or any Stream product but Chat, except the read-only Video and Feeds reads and the one Video `PUT` that item 4.4 plans; create a call, a feed, an activity or an invite;
  - run `restore --apply`, a second `configure --apply`, a second `configure --products video,feeds --apply`, or any other command that changes the application's settings, roles, grants or channel or call types;
  - connect to any database, HDE, Railway or any other provider;
  - run `playwright install` or `eas`;
  - add or change a dependency anywhere.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **The three `STREAM_*` names must be present:** `compgen -e | grep -E '^STREAM_'` prints names only. Expected: `STREAM_API_KEY`, `STREAM_API_SECRET`, `STREAM_APP_ID`. If any is missing, stop and report: this session must start in `Glow app`. Never read their values yourself; the harness's credential loader does.
3. No `PG*` or `PROOF_DB_*` name should be set; report any name present, never its value.
4. **No `.env` file:** `ls -a . services/api proofs/stream-chat | grep -x '\.env'` must print nothing. If one exists, report it without reading it, and stop.
5. The pinned toolchain is in `$HOME/.local/bin`: Node 24.19.0, npm 11.9.0 and Python 3.12.14. Put `$HOME/.local/bin` first on PATH, then record `command -v python3.12` and its version.
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

- root `AGENTS.md` and `CLAUDE.md`, and `proofs/stream-chat/README.md`, whole;
- the P06.2 brief (revision 5), whole, and the DM-16 and DM-17 reports in `docs/continuity/dev-manager/reviews/`;
- ADR 0003's "Conditions", and the chat-provider architecture document, section 5;
- the evidence record's "Stage B2" and "Manager verification of Stage B2";
- in `proofs/stream-chat/`: `glow_stream_proof/configuration.py`, `products.py`, `baseline.py`, `cli.py` (the `baseline`, `configure`, `configure --products`, `record-products-baseline`, `verify-clean`, `cleanup` and `conformance` commands), `guard.py`'s configure scope, `conformance.py`, and the tests and fakes that model the two baselines.

## 3. The work, offline first

Each code change gets a test that fails without it, with its reversal made in a scratch copy outside the checkout (`git status` clean afterwards; DM-14 item 6).

1. **The chat target's coverage** (brief point i).
   - `configuration.verify` reports a difference for any grant held by any role in any channel type other than `glow-match`, not only in the five default types, which must still exist.
   - `configure`'s plan empties every such type the snapshot shows, with the same request shape as the five default types' (its `automod`, `automod_behavior` and `max_message_length` from the snapshot, every role's grants `[]`).
   - `restore` leaves untouched a channel type that the pre-proof baseline (`baseline/application-1729640-2026-09-25.json`) does not hold, and the README says so.
   - The offline fakes gain a sixth, non-default channel type with client grants, so the tests show it is a difference, is planned and verifies once locked.
2. **The products baseline's file name** (brief point ii): `products` reads the baseline the session records in item 4.2, through one constant, with the fakes and tests updated to model it. The committed `baseline/video-feeds-1729640-2026-09-27.json` and `baseline/application-1729640-2026-09-25.json` stay byte-identical. Commit item 1 first; item 2's code goes in the same commit as the new baseline file (item 4.2), so that no commit names a file that does not exist.
3. **Offline checks pass** (section 5, items 1 to 4) before any live command.

## 4. The live run, in this order

The command form is Stage B2's (section 1, item 6). Record each command's exact result lines.

1. **`baseline`** (read-only). With item 1's coverage, its differences must be exactly B2's 8 chat and 7 Video and Feeds lines, as Stage B2's record lists them, plus one chat line for each role of the chat type `agent` that holds a grant. **Any other difference, or any of these changed, stops the session:** record it and report. From the same snapshot, list every field of `glow-match` that `MATCH_FEATURES` does not name, with its value; if one turns on a content feature or a client write, report it first and stop before item 4.2.
2. **The new products baseline** (D3): `record-products-baseline --snapshot <that snapshot>` writes `baseline/video-feeds-1729640-<today>.json`. Record its diff against `video-feeds-1729640-2026-09-27.json` whole: it must be the call type `agent` and a `lifecycle` section on each of `audio_room`, `default`, `development` and `livestream`, and nothing else; otherwise stop. Scan the file as every record is scanned (no identifier, token or secret). Commit it with item 2's code before any apply; you may push it then, and the apply need not wait for its Foundation run.
3. **The chat target** (D1, D4):
   1. `configure` (dry run). For each planned request, show from the snapshot that it either re-sends values the snapshot already holds or corrects D1 (`glow-match`'s `channel_member`: `read-channel` alone) or D4 (the chat type `agent`: every role's grants `[]`). Anything else stops the session before the apply.
   2. `configure --apply`, once. Its chat differences after (the lines without the `video/feeds: ` prefix) must be `[]`; the Video and Feeds lines that remain must be D2's two. Otherwise stop: no second apply, no restore.
4. **The Video and Feeds lockdown** (D2):
   1. `configure --products video,feeds` (dry run). The plan must be exactly one `PUT /api/v2/video/calltypes/agent` naming `user` and `guest` with `[]`, and nothing for Feeds; otherwise stop.
   2. `configure --products video,feeds --apply`, once. Its differences after must be `[]`. Otherwise stop.
5. **`baseline`:** both counts 0. Otherwise stop.
6. **B2's live run from its item 7.2, unchanged:** `verify-clean`; `conformance` with its 46 rows (`--accept-dashboard-user` as B2's command takes it); `cleanup --apply` if the run did not clean up, then `verify-clean`; the closing `baseline`, both counts 0. B2's rules hold as its prompt states them:
   - **the rerun rule** (DM-16 1.3): one rerun of `conformance` only when the first run stopped on something other than a charge or limit signal, its cleanup and `verify-clean` passed, the cause is recorded, and the fix, if any, is offline, in section 6's rerun paths, with its checks passing; otherwise, and after a second stop, stop and report;
   - **the blocking rule** (DM-16 5.2): a code that differs from the fixture's for F3 and CX6's causes (rows C4, R8, D10 and V13) blocks B2's merge until it is dispositioned; report it first;
   - **every other difference** between Stream's outcome and the fixture's is a finding, reported, not fixed silently; R7's answer (a send by a removed member) is recorded either way.
- **Budget and stops:** the harness's guardrails as they are. A charge or limit signal stops the session at once, deleting nothing, and you report it; a rate limit only: wait as the README says. Record the API calls each command used.

**Not in B2-C1:** any change to B2's adapter, signer or command except a fix under the rerun rule; any role or scope beyond D1, D2 and D4; the `admin` and resource roles; the dashboard user; the committed baselines; Feeds; the mobile app; any dependency.

**Rules for every change:** no weakened check, guard, deny-list or budget; no credential, token or signature in any file, log line, record or report; the harness's other commands and their results unchanged.

**Findings outside this work:** report each with its class. Fix it here only if it could let a credential leak, let a request reach Stream outside the guard or the configure scope, or let the configuration commands change anything beyond D1, D2 and D4.

**A departure** from any of the above that you find necessary: stop before making it and report it; it goes to the Dev Manager.

## 5. Checks

Report the exact commands and results.

1. `git diff --check <START_SHA> HEAD` and `git diff --name-only <START_SHA> HEAD`: only owned paths changed.
2. Classification with the trusted policy from `main`, outside the tree: `base=$(git rev-parse origin/main); d=$(mktemp -d); git show "$base:scripts/change_scope.py" > "$d/change_scope.py"; python3 -I "$d/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base`. Expected: full scope.
3. Hash-locked installs and `pip check` for the API and the harness; `npm ci` for the harness's client, with `npm audit`'s advisory named (package, severity, advisory ID; no change).
4. The offline checks: the API's tests (329 at the start), the harness's tests (605 at the start), Ruff, mypy, the static check with `makemigrations --check --dry-run`, the sealed-runtime and pin tests, the harness's `node --check` and its run-plan count.
5. **The live run:** each command's exact result lines; item 4.1's differences and `glow-match`'s unnamed fields; the new baseline's diff; each dry-run plan with its check; each apply's differences after; every `baseline` run's two counts; each conformance row's result; each mapping with its row; the API calls used; `verify-clean`'s results; whether a rerun was used, and why. No value of any `STREAM_*` variable, token or signature in what you record.
6. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs), the database job's duration, and the gate's line `Application checks passed`. Push nothing more until that run has finished (AM5-14). CI has no Stream secret; it runs the offline checks only.
7. A secret scan over your whole diff, the new baseline and your record.

## 6. Owned paths, push and records

- **You may change:**
  - `proofs/stream-chat/**`: `glow_stream_proof/configuration.py` (item 1), `products.py` (the baseline's file name, item 2), the new `baseline/video-feeds-1729640-<today>.json` written by `record-products-baseline`, their tests and fakes, and the README. Not the guard, the deny-lists, the budget, the stop signals, cleanup's rules, the committed baselines or any dependency file;
  - **for a fix under the rerun rule only:** `services/api/glow_domain/chat_provider_stream.py` and `services/api/tests/test_chat_provider_stream.py`; `proofs/stream-chat/glow_stream_proof/conformance.py`, `cli.py`'s `conformance` command, and their tests;
  - the evidence record: a new section "Stage B2-C1" after the existing sections, which stay byte-identical.
- **Nothing else.** Report any other change you think is needed, before making it.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage B2-C1":** the prompt's revision and start SHA, your head, your branch and the run of record; items 1 and 2, each done (`file:line` and its test) or left (the reason); the live run, step by step, with section 5 item 5's contents; the conformance rows' results, row by row; each mapping with its row; the API calls used; every check with its exact results; deviations and limits; what the exact-head review must know.

## 7. Report

Your final message is the report Nathan relays: the prompt revision (revision 1, from `<START_SHA>`); the environment check (names only, the `.env` check included); your branch, head SHA and changed paths; first, whether the session stopped and where, and any code that differs from the fixture's for the causes in F3 and CX6's rows; items 1 and 2; every `baseline` run's counts; the applies' results; the conformance rows' results; the API calls used; every check with its exact results, and the run of record's details; deviations, departures you stopped at, findings outside the work with their class, and limits.
