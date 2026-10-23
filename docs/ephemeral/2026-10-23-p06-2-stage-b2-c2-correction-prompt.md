# P06.2 Stage B2-C2 prompt — the live correction after B2-C1, then B2's live rows

- **Owner:** App Manager 7. Nathan starts this session manually, in the **`Glow app`** environment (OD-36), and relays its report.
- **Revision 2, 23 October 2026.** Revision 1 went to the Dev Manager (DM-18), which approved it with conditions; revision 1 does not run. Revision 2 applies DM-18's conditions as written, each marked with its number, so it needs no further read (DM-03 G2).
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 6 with DM-18's conditions: D5, "B2-C1's live run stopped, and B2-C2" (points i to vii), "B2's live run stopped" (D1 to D5, points i to vi, with DM-17's conditions), "B2's design points" a to h with DM-16's conditions, and B2-C2's owned paths.
  - Inputs: the evidence record's "Stage B2", "Manager verification of Stage B2", "Stage B2-C1" and "Manager verification of Stage B2-C1"; the [Stage B2 prompt](2026-10-22-p06-2-stage-b2-implementation-prompt.md), revision 2, whose item 7 this pass completes; the [B2-C1 prompt](2026-10-23-p06-2-stage-b2-c1-correction-prompt.md), revision 2, whose section 4 this pass runs with the changes below; the [harness README](../../proofs/stream-chat/README.md); ADR 0003's condition (c); the DM-16, DM-17 and DM-18 reports.
- **Where the result goes:** the session's code and tests, the new products baseline, and its section "Stage B2-C2" in the evidence record; the run of record is the Foundation run on its last code commit if its branch is under the workflow's push filter, otherwise PR31's run on the manager-branch head that integrates it; the live run is recorded from the session's own output. The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 3.44 (confidence 0.61); rung probabilities low 0.00, medium 0.01, high 0.13, extra high 0.29, max 0.57, ultracode 0.00. Model probabilities Fable 5.1 0.45, Opus 5.5 0.55, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.40). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.005, Fable 5.1 at high 0.059, Fable 5.1 at extra high 0.131, Fable 5.1 at max 0.257, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.006, Opus 5.5 at high 0.072, Opus 5.5 at extra high 0.160, Opus 5.5 at max 0.314, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between extra high and max; model near tie between Opus 5.5 and Fable 5.1. Sent 2026-10-23T20:23:37Z. Nathan picks the cell.
  - Revision 1's reading (Opus 5.5 at extra high, sent 2026-10-23T19:16:47Z) is superseded; revision 1 did not run.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** DM-18 ([report](../continuity/dev-manager/reviews/2026-10-23-dm-18-p06-2-stage-b2-c2-read.md), `f0a43c9`), of revision 1; revision 2 applies it as written.
- **Environment** (OD-36): `Glow app`, which holds `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET`. The session checks their names only and never prints, logs or copies their values; only the harness's credential loader reads them.
- **It runs alone** (OD-29). An exact-head review of B2, B2-C1 and B2-C2 together follows, then Codex's code review (OD-41).
- **Deletion condition:** prune after Stage B2's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session P06.2 Stage B2-C2**, which returns Stream's development application to the proof's targets and then runs Stage B2's live rows, for P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 2, from commit `<START_SHA>`.

**What exists.** Stage B2 (code head `e97f90d`) added the Stream adapter on the chat provider port (`services/api/glow_domain/chat_provider_stream.py`), the client token's signer, and the harness's `conformance` command with 46 rows. Its first live command, the read-only `baseline`, found Stream's additions since the lockdown of 27 September (D1 to D4), so it stopped. The correction pass B2-C1 (code head `2f54538`, integrated at `9e24ca1`) then did its offline work: the chat target covers every channel type other than `glow-match`; `products.merged_baseline_record` merges a new products baseline with the 27 September one; the read-only `full-view` and the offline `compare-views` commands; the API's development lock aligned with the harness's. Its first live command, `baseline`, found B2's lines, the chat type `agent`'s lines its coverage expects, and three lines for a **fifth addition, the Video call type `audio_call`** (D5: `user` 33, `guest` 6), so it stopped too; nothing at Stream was changed. The dispositions (the brief's D1 to D5):

- **D1:** `glow-match`'s `channel_member` also holds `schedule-message`: remove it;
- **D2 and D5:** the Video call types `agent` and `audio_call`, whose `user` and `guest` roles hold Stream's default grants: empty them;
- **D3:** the new call types and a new `lifecycle` settings section on the four known call types: re-baseline, keeping the 27 September client grants (B2-C1's merge);
- **D4:** the default chat channel type `agent`, with client grants: lock it (B2-C1's coverage).

**What B2-C2 does.** You take two read-only views and compare them, check the differences by class (section 3), record the merged products baseline and switch to it, apply the chat target and the Video and Feeds lockdown once each with a full comparison around each apply, confirm both counts are 0, and then run B2's live rows from its item 7.2. **No app runtime gains a database, real authentication or a live provider.**

- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 7);
  - push only your own session branch. **The Foundation workflow runs on a push only for `main`, `app-builder-1/**`, `app-planner-1/**` and `claude/**`.** If your branch's name is outside those, no run starts: say so in your report, and the manager's integration run is the run of record. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any `STREAM_*` value, a token, a signature, a marker or any other credential, in any form;
  - call any Stream application but 1729640, or any Stream product but Chat, except the read-only Video and Feeds reads and the Video and Feeds `PUT`s that section 4 item 5.1 plans; create a call, a feed, an activity or an invite;
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
6. Run every command in a clean process environment, in the form Stage B2-C1's record shows for its live command (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, the three `STREAM_*` names by reference only to the harness's live commands, and the proxy and CA variables by reference).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/ proofs/ .github/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage B2-C2'   # must print 0
```

If code or this pass's section has already landed on the live manager branch, this prompt is stale: stop and report (AM5-15). If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md` and `proofs/stream-chat/README.md`, whole;
- the P06.2 brief (revision 6 with DM-18's conditions), whole, and the DM-16, DM-17 and DM-18 reports in `docs/continuity/dev-manager/reviews/`;
- ADR 0003's "Conditions", and the chat-provider architecture document, section 5;
- the evidence record's "Stage B2", "Manager verification of Stage B2", "Stage B2-C1" (B2-C1's 4.1 differences, its two listings and its `audio_call` entry are this pass's reference) and "Manager verification of Stage B2-C1";
- in `proofs/stream-chat/`: `glow_stream_proof/configuration.py`, `products.py`, `full_view.py`, `baseline.py`, `cli.py` (the `baseline`, `full-view`, `compare-views`, `configure`, `configure --products`, `record-products-baseline`, `verify-clean`, `cleanup` and `conformance` commands), `guard.py`'s configure scope, `conformance.py`, both committed baselines, and the tests and fakes that model the products baseline.

## 3. The difference classes (the brief's B2-C2 point i)

At the first `baseline` (section 4 item 1), every difference must belong to one of these four classes. **List every line with its class, and mark each line that is new since B2-C1's record** (DM-18 2.1).

1. **B2's lines:** the 8 chat and 7 Video and Feeds lines Stage B2's record lists, unchanged.
2. **A chat channel type other than `glow-match` with a grant:** a line `<type> grants for <role> not empty: […]` for any type other than `glow-match` (the chat type `agent`'s nine lines in B2-C1's record are of this class). `configure --apply` empties them.
3. **A Video call type or Feeds visibility the committed baseline does not hold:** its line "not in the committed baseline" and its client roles' lines "grants for user / guest / anonymous not empty" (`agent` and `audio_call` in B2-C1's record). The products apply empties the client roles; the merged baseline records the scope as read.
4. **A settings section added to a call type the committed baseline holds:** a line "settings differ from the committed baseline at <section> (not in the baseline)" (`lifecycle` on the four known call types). The merged baseline records it. **Each added section is listed with its value** (DM-18 2.3). A section that acts without any client request stops the session before section 4 item 4: one that records, transcribes, broadcasts, rings, notifies, or sends to a URL by itself. `lifecycle` (`reusable` or `single_use`) does none of these.

**Anything else stops the session before section 4 item 4**, with the line reported first: for example a grant added to `glow-match` beyond D1, a change to a known call type's or visibility's non-client grants or existing settings, a feed group change, an application setting against the 25 September record, or a missing type. A line that belongs to a class but was not in B2-C1's record (a new type or scope since 18:28 UTC on 23 October) is allowed and is listed as new. **A class-2 or class-3 scope whose `created_at` differs from B2-C1's record is listed with both stamps** (DM-18 2.4): Stream may re-create its default types.

## 4. The live run, in this order

The command form is Stage B2-C1's (section 1, item 6). Record each command's exact result lines. B2-C1's code is in place; this pass adds code only where section 6 says.

1. **`baseline`** (read-only), then **`full-view`**: **V0a**. Check every `baseline` difference against section 3's classes; anything else stops.
2. **Wait at least 60 seconds, then `full-view` again: V0b.** `compare-views --before V0a --after V0b`. A field that changed with no apply between the two reads is handled in one of three ways:
   - **a volatile name, the narrowest possible** (DM-18 3.2): a name joins `full_view.VOLATILE_FIELDS` only if both hold: its V0a and V0b values are read-time values (a time that moved forward, or a counter that grew), and it occurs nowhere in either committed baseline or among the fields the targets name. Add it offline with a test that shows both (a change in it is not reported, and the name occurs in neither baseline nor any targeted field), commit it, run the harness's tests, re-run `compare-views` on the same two files (nothing reported), and name the field and its path in your record. `VOLATILE_FIELDS` matches by name at any depth, so a common name (for example `count` or `limit`) would hide configuration everywhere: such a name stops the session instead;
   - **a list in a different order, pre-approved** (DM-18 3.3): if the only difference between V0a and V0b is the order of a list whose items are otherwise identical (the role list is the likely case), make the comparison key that list's items by `name` (or `id`), offline in `full_view.py`, with a test; re-run `compare-views` on the same files (nothing reported) and record it;
   - **anything else:** report it first and stop before any apply.
3. **The listings against B2-C1's** (DM-17 2.1; DM-18 2.2). From V0b, list every application settings key that the 25 September record and the target do not name, and from the `baseline` snapshot every field of `glow-match` that `MATCH_FEATURES` does not name, each with its value (a credential-like value as section 5 item 5 says). Mark each key or field that is not in B2-C1's listing or whose value differs from it. If one of those turns on a content feature or a client write, report it first and stop before item 4. **From V0b, also compare these with B2-C1's record:**
   - the role list (17 names);
   - each role's `.app` grant count (`admin` 47, `anonymous` 0, `global_admin` 44, `global_moderator` 39, `global_read_only` 5, `guest` 0, `moderator` 42, `user` 0);
   - the names of the channel types, call types, feed visibilities and feed groups.

   **A new or missing role, a changed `.app` grant, or a new or missing feed group stops the session before item 4.** A new channel type, call type or feed visibility is listed, marked new, and takes its class (section 3).
4. **The new products baseline** (D3, D5; DM-17 1.1): `record-products-baseline --snapshot <item 1's snapshot>` writes `baseline/video-feeds-1729640-<today>.json` through `products.merged_baseline_record`. Record its diff against `video-feeds-1729640-2026-09-27.json` whole: it must be the class-3 scopes as read and the class-4 sections, and nothing else; otherwise stop. Then, in the same commit as the new file: `products.PRODUCTS_BASELINE` names it; the fakes and tests that model the committed baseline model the new one; the README names it. The 27 September file and `baseline/application-1729640-2026-09-25.json` stay byte-identical and are kept. Run the harness's tests (all pass), scan the file as every record is scanned (no identifier, token or secret), commit and push; the apply need not wait for a Foundation run.
5. **The chat target** (D1 and the class-2 types):
   1. `configure` (dry run). For each planned request, show from the snapshot that it either re-sends values the snapshot already holds or corrects D1 (`glow-match`'s `channel_member`: `read-channel` alone) or a class-2 type (every role's grants `[]`). Anything else stops the session before the apply.
   2. `configure --apply`, once. It runs **outside the guard** (`cmd_configure`'s own comment), as on 25 September: it re-sends the application `PATCH`, the default types and `glow-match`. That is accepted for this one reviewed command with the dry-run check above and the comparison below (DM-17 2.4). Its chat differences after (the lines without the `video/feeds: ` prefix) must be `[]`; the Video and Feeds lines that remain must be only class 3's client-role lines. Otherwise stop: no second apply, no restore.
   3. `full-view`: **V1**. `compare-views --before V0b --after V1`. **The only changes allowed are D1 and the class-2 types' grants** (DM-17 2.3). Anything else is reported first, **and the session stops** (DM-18 3.1): no further apply, no restore and no conformance run. Stopping here leaves Video and Feeds as they are.
6. **The Video and Feeds lockdown** (D2, D5):
   1. `configure --products video,feeds` (dry run). The plan must be exactly one `PUT` per call type or feed visibility whose client-role lines item 1 listed, each naming only `user`, `guest` or `anonymous` with `[]`, and nothing else; otherwise stop.
   2. `configure --products video,feeds --apply`, once. Its differences after must be `[]`. Otherwise stop.
   3. `full-view`: **V2**. `compare-views --before V1 --after V2`. **The only changes allowed are those `PUT`s' client roles.** Anything else is reported first, **and the session stops** (DM-18 3.1): no restore and no conformance run. **Record from V2 the `created_at` and `updated_at` of every class-2 and class-3 scope** (DM-18 3.5).
7. **`baseline`:** both counts 0. Otherwise stop.
8. **B2's live run from its item 7.2, unchanged:** `verify-clean`; `conformance` with its 46 rows (`--accept-dashboard-user` as B2's command takes it); `cleanup --apply` if the run did not clean up, then `verify-clean`; the closing `baseline`, both counts 0. **With the closing `baseline`, record the `created_at` and `updated_at` of every class-2 and class-3 scope** (DM-18 3.5), from its snapshot or, where the snapshot does not hold them, from a `full-view` taken with it. **If a scope locked in this session reads grants again at the closing `baseline`,** that is the closing count's difference: the session stops and reports it with the stamps (a lock that does not hold against Stream's own re-creation). B2's rules hold as its prompt states them:
   - **the rerun rule** (DM-16 1.3): one rerun of `conformance` only when the first run stopped on something other than a charge or limit signal, its cleanup and `verify-clean` passed, the cause is recorded, and the fix, if any, is offline, in section 7's rerun paths, with its checks passing; otherwise, and after a second stop, stop and report;
   - **the blocking rule** (DM-16 5.2): a code that differs from the fixture's for F3 and CX6's causes (rows C4, R8, D10 and V13) blocks B2's merge until it is dispositioned; report it first;
   - **every other difference** between Stream's outcome and the fixture's is a finding, reported, not fixed silently; R7's answer (a send by a removed member) is recorded either way.
- **A half-applied state is reported, not repaired** (DM-17 3.4). If an apply fails part-way, stop with its record. Run `full-view` once (read-only) and compare it with the view before that apply. Report which requests were applied (the `configure` record's applied steps), the failure, and that comparison. Run nothing else: the development application's state is then a new decision, not this session's.
- **Budget and stops:** the harness's guardrails as they are. A charge or limit signal stops the session at once, deleting nothing, and you report it; a rate limit only: wait as the README says. Record the API calls each command used.

**Not in B2-C2:** any change to B2's adapter, signer or command except a fix under the rerun rule; any change to B2-C1's code except section 6's; any role or scope beyond D1, D2, D5 and the class-2 and class-3 scopes; the `admin` and resource roles in Video and Feeds; the dashboard user; the committed baselines; Feeds' groups; the mobile app; any dependency.

**Rules for every change:** no weakened check, guard, deny-list or budget; no credential, token or signature in any file, log line, record or report; the harness's other commands and their results unchanged.

**Findings outside this work:** report each with its class. Fix it here only if it could let a credential leak, let a request reach Stream outside the guard or the configure scope, or let the configuration commands change anything beyond the planned scopes.

**A departure** from any of the above that you find necessary: stop before making it and report it; it goes to the Dev Manager.

## 5. Checks

Report the exact commands and results.

1. `git diff --check <START_SHA> HEAD` and `git diff --name-only <START_SHA> HEAD`: only owned paths changed.
2. Classification with the trusted policy from `main`, outside the tree: `base=$(git rev-parse origin/main); d=$(mktemp -d); git show "$base:scripts/change_scope.py" > "$d/change_scope.py"; python3 -I "$d/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base`. Expected: full scope.
3. Hash-locked installs and `pip check` for the API and the harness; `npm ci` for the harness's client, with `npm audit`'s advisory named (package, severity, advisory ID; no change).
4. The offline checks: the API's tests (328 at the start), the harness's tests (632 at the start), Ruff, mypy, the static check with `makemigrations --check --dry-run`, the sealed-runtime and pin tests, the harness's `node --check` and its run-plan count.
5. **The live run:** each command's exact result lines; item 1's differences, each with its class and new lines marked, class-4 sections with their values, and re-created scopes with both stamps; the V0a–V0b comparison and any volatile name or list key added; item 3's listings, role list, `.app` grant counts and name lists with their marks; the new baseline's diff; each dry-run plan with its check; each apply's differences after; the comparisons V0b–V1 and V1–V2 whole; the stamps of item 6.3 and the closing `baseline`; every `baseline` run's two counts; each conformance row's result; each mapping with its row; the API calls used; `verify-clean`'s results; whether a rerun was used, and why. No value of any `STREAM_*` variable, token, signature or other credential in what you record. **No digest of a non-empty withheld value in the record** (DM-18 3.4): write such a value as "withheld, non-empty", and a change as "changed" or "unchanged"; an empty one as "empty". The digests stay in the `.work` files, which git ignores.
6. **The run of record:** if your branch is under the workflow's push filter, the Foundation run on your last code commit (its run ID, each job's conclusion, eight jobs, the database job's duration, and the gate's line `Application checks passed`), and push nothing more until it has finished (AM5-14); otherwise say that no run started, and why.
7. A secret scan over your whole diff, the new baseline, every `.work/` file you cite and your record.

## 6. Code in this pass

1. **B2-C1's item 2, completed** (section 4 item 4): `PRODUCTS_BASELINE`'s switch, the fakes and tests, the README's file name, in the commit that adds the new baseline file.
2. **A volatile name or a list key**, only under section 4 item 2's first two cases (DM-18 3.2, 3.3), each with its test.
3. **The pin test's docstring:** `services/api/tests/test_dependency_pins.py` says `tzdata` "stays as resolved"; it left the lock in B2-C1 (only `python-dateutil` 3.0.0 required it). Correct the sentence; no code change.
4. **A fix under the rerun rule only**, in section 7's rerun paths.

Each code change gets a test that fails without it, with its reversal made in a scratch copy outside the checkout (`git status` clean afterwards; DM-14 item 6), except the docstring.

## 7. Owned paths, push and records

- **You may change:**
  - `proofs/stream-chat/**`: `glow_stream_proof/products.py` (`PRODUCTS_BASELINE`), `glow_stream_proof/full_view.py` (`VOLATILE_FIELDS`, or the comparison keying one list's items by `name` or `id`, under section 4 item 2 only), the new `baseline/video-feeds-1729640-<today>.json` written by `record-products-baseline`, the tests and fakes that model the committed baseline or the volatile names, and the README. Not the guard, the deny-lists, the budget, the stop signals, cleanup's rules, the committed baselines, the other commands or any dependency file;
  - `services/api/tests/test_dependency_pins.py`: its docstring only;
  - **for a fix under the rerun rule only:** `services/api/glow_domain/chat_provider_stream.py` and `services/api/tests/test_chat_provider_stream.py`; `proofs/stream-chat/glow_stream_proof/conformance.py`, `cli.py`'s `conformance` command, and their tests;
  - the evidence record: a new section "Stage B2-C2" after the existing sections, which stay byte-identical.
- **Nothing else.** Report any other change you think is needed, before making it.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage B2-C2":** the prompt's revision and start SHA, your head, your branch and the run of record (or why none started); section 6's items, each done (`file:line` and its test) or not needed; the live run, step by step, with section 5 item 5's contents; the conformance rows' results, row by row; each mapping with its row; the API calls used; every check with its exact results; deviations and limits; what the exact-head review must know.

## 8. Report

Your final message is the report Nathan relays: the prompt revision (revision 2, from `<START_SHA>`); the environment check (names only, the `.env` check included); your branch, head SHA and changed paths; first, whether the session stopped and where, and any code that differs from the fixture's for the causes in F3 and CX6's rows; item 1's differences by class, with any new line marked and any re-created scope's stamps; the V0a–V0b comparison; the listings' marks, the role list, the `.app` grant counts and the name lists; the stamps after the applies and at the close; every `baseline` run's counts; the applies' results and both comparisons; the conformance rows' results; the API calls used; every check with its exact results, and the run of record (or why none started); deviations, departures you stopped at, findings outside the work with their class, and limits.
