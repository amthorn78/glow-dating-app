# P06.2 Stage B2-C4 prompt — correction pass on Stage B2's exact-head review

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 10: "B2's exact-head review, and B2-C4", and point i's 1.2 and 1.3 in "B2's live rows, and what they leave".
  - Inputs: the evidence record's "Exact-head review of Stage B2", findings B2R1 to B2R9 with the manager's dispositions; the [DM-20 report](../continuity/dev-manager/reviews/2026-10-23-dm-20-p06-2-b2-live-rows-and-d8.md), items 1 and 3.
- **Where the result goes:** the session's code and tests, and its section "Stage B2-C4" in the evidence record. The run of record is the Foundation run on its last code commit if its branch is under the workflow's push filter; otherwise it is PR31's run on the manager-branch head that integrates it (AM7-02). The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.88 (confidence 0.85); rung probabilities low 0.00, medium 0.17, high 0.78, extra high 0.05, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.168, Opus 5.5 at high 0.772, Opus 5.5 at extra high 0.050, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.002, Sonnet 5.5 at high 0.008, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T01:00:57Z. Nathan picks the cell.
  - **Nathan's pick:** Opus 5.5 at high, TypeSafe's reading (24 October).
- **The Dev Manager's read:** none needed. The pass applies DM-20 1.2 and 1.3 as written and the review's findings the manager sends to it. It authorizes no credential use, provider call, dependency or design change.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29). An exact-head re-review of the corrected head follows, then Codex's code review of the final head (OD-41).
- **Deletion condition:** prune after Stage B2's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session P06.2 Stage B2-C4**, an offline pass on Stage B2 of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stage B2 and its three correction passes are the draft PR31, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`.

- **B2's code:**
  - the Stream adapter on the chat provider port, `services/api/glow_domain/chat_provider_stream.py`;
  - the client token's signer;
  - the harness's `conformance` command, with 46 rows, in `proofs/stream-chat/glow_stream_proof/conformance.py`.
- **The live rows:** B2-C1 to B2-C3 corrected Stream's configuration additions, and B2-C3 ran the 46 rows live on 23 October: 42 PASS, 2 RECORDED, 2 DIFFERENCE.
- **D10, dispositioned by the Dev Manager (DM-20 item 1).** Rows C4, M5, D10 and V13 share one identifier, and M5's accepted send left that user at Stream. So D10 and V13 did not exercise "a user Stream does not have" live.
  - Their identifiers are corrected here (DM-20 1.2).
  - M5 becomes a recorded row (1.3).
- **The exact-head review** of B2 to B2-C3, at `51844a5`, approved, with one should-fix finding and eight nits (the evidence record, "Exact-head review of Stage B2"). The manager sends five of them here.
- **The code at your start** is byte-identical to `ebdc690`'s, the code of the run of record, Foundation run 40025252591.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. If your branch is under the workflow's push filter (`claude/**`), each push runs the Foundation workflow on it; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token, signature or marker, in any form;
  - call Stream, or run any harness command that reaches it (`baseline`, `full-view`, `configure`, `restore`, `verify-clean`, `cleanup`, `run`, `conformance`). The harness's offline tests use fakes and are allowed;
  - start or connect to any database; connect to HDE, Railway or any other provider;
  - run `playwright install`, `eas` or `migrate`;
  - add or change a dependency, a version or a lock file.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. No `PG*` or `PROOF_DB_*` name should be set (`compgen -e | grep -E '^(PG|PROOF_DB_)'`). If one is present, report its name, never read or use its value, and continue.
4. **No `.env` file:** `ls -a . services/api proofs/stream-chat | grep -x '\.env'` must print nothing. If one exists, report it without reading it, and stop.
5. **The toolchain:**
   - The pinned toolchain is in `$HOME/.local/bin`: Python 3.12.14, Node 24.19.0 and npm 11.9.0. Put `$HOME/.local/bin` first on PATH in every process you run, then record `command -v python3.12` and its version. Create any virtual environment with `python3.12`, outside the checkout.
   - **uv, for item 6's check only:** the API README's lock command names uv 0.12.17, which the pinned toolchain lacks. As B2-C1 did, install uv 0.12.17 into a scratch virtual environment outside the checkout, record its path and version, and commit nothing of it.
6. Run the API's and the harness's commands in a clean process environment: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API, as `docs/operations/local-development.md` and the READMEs show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/ proofs/ .github/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage B2-C4'   # must print 0
git diff --quiet ebdc690b3341cd81e60d92b9526f9f1d12c37f24 HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
```

If code or this pass's section has already landed on the live manager branch, this prompt is stale: stop and report (AM5-15). If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md` and `proofs/stream-chat/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`:
  - "B2's design points";
  - "B2's live rows, and what they leave" (point i's 1.1 to 1.3 and point ii);
  - "B2's exact-head review, and B2-C4";
- the DM-16 report's items 4.1, 4.4, 4.7 and 5.2, and the DM-20 report's items 1 and 3, in `docs/continuity/dev-manager/reviews/`;
- the evidence record, `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: the rows table of "Stage B2-C3", and "Exact-head review of Stage B2", whole;
- `services/api/glow_domain/chat_provider_stream.py` and `services/api/tests/test_chat_provider_stream.py`;
- in `proofs/stream-chat/`:
  - `glow_stream_proof/conformance.py`;
  - in `glow_stream_proof/proof_run.py`: `_generic`, `_TABLE_NAMES`, `results` and `_delete_users`;
  - `checks/run_plan.py`;
  - `tests/test_conformance.py` and `tests/test_run_plan.py`, with the fakes they use.

## 3. The work

**For each item:**
- write a test that fails without the change and passes with it;
- show the failure with a reversal in a scratch copy outside the repository.

Item 6 is shown by its command instead.

1. **DM-20 1.2, the identifiers.** As written:

   > C4, D10 and V13 each get an identifier that no other row names, and M5 gets its own. A test in the harness fails if any two of those rows share an identifier.

   - C4's, D10's and V13's identifiers name users the run never creates: none goes through `_new_user`, and no earlier row sends one.
   - Name the keys you choose.
   - Every other row's identifiers, verdicts and order stay as they are.
2. **DM-20 1.3, M5 a recorded row, with B2R3.** As written:

   > M5 becomes a recorded row in the same correction, as R7 is (DM-16 4.7). … The run records M5's identifier as a user its send may create, so the cleanup deletes that user by record, not only by the prefix search that found it this time.

   - **The verdict:** M5 is RECORDED whatever Stream answers (`recorded=True`, as R7). Its expected value stays the fixture's.
   - **B2R3, the ledger:** before the send, the run reserves M5's sender in the ledger and records it as a run user, as `_new_user` does.
   - **Cleanup needs no change.** `_delete_users` already leaves out a recorded user that a complete listing does not show.
     - Show with a test on the fakes that M5's sender is deleted by record when the send creates it.
     - Show that nothing is reported as found by prefix but not recorded.
   - **The budget:** `checks/run_plan.py`'s conformance count moves from 4 to 5 users, and `b2_total_with_reserve` from 8 to 10 users, within the cap. Update `tests/test_run_plan.py`'s pins.
   - **The blocking rows stay** C4, R8, D10 and V13.
3. **B2R1, the exception context.**
   - **Where:** `_guarded` (`chat_provider_stream.py:134-140`) and `send_message`'s handler (`:239-243`).
   - **The change:** raise the mapped error after the `except` block, not inside it, so that both its `__cause__` and its `__context__` are `None`. Do the same for any other `raise` inside an `except` clause in the module.
   - **What stays unchanged:** the mapping, the codes, the caught tuple and `_reports_existing`.
   - **The tests:** extend the boundary tests to assert `__context__ is None` and `__cause__ is None`, for every operation and both hooks (the test at `tests/test_chat_provider_stream.py:748` and its siblings).
   - **The reversal:** the raise moved back inside the clause, with `from None` kept, must fail them.
   - **The docstring:** make the module's sentence on the chain say what the code now does.
4. **B2R2, the results' identifiers.**
   - **The change:** in `conformance.py`'s `results()`, replace every identifier of the run with `{key}` (every value of `self.ids`, longest first), before the redactor runs. This applies in each row's detail, in the run's notes, and in any other part of the results that carries one.
   - **What stays unchanged:** `proof_run.py` and the other commands' records.
   - **The test:** on a fake run, no row's detail and no note in the results contains the random part (the 32 hexadecimal characters) of any of the run's identifiers.
5. **B2R4, a short error body.**
   - **The docstring:** one sentence in the module docstring's boundary paragraph. A non-2xx body that the SDK cannot parse into its `APIError` (for example, one with `code` and `message` only) raises the SDK's own `KeyError` before a `StreamApiException` exists. That `KeyError` propagates unmapped, as the undecodable 2xx body's does (DM-16 4.1), and delivery keeps it as a retryable `provider_unavailable`.
   - **The test:** modelled on the 2xx one, on the recorded transport.
   - **No change to the boundary.**
6. **B2R7, the README's lock command.**
   - **The change:** in `services/api/README.md`, the development-lock line names `--constraint ../../proofs/stream-chat/requirements.lock`. Add one sentence: the development lock is compiled in place, so uv keeps its other pins as preferences, and the 30 shared packages keep the harness's versions and hashes, which the pin test holds.
   - **The check:** with uv 0.12.17 from your scratch environment, run the README's new command on a scratch copy of `services/api` that holds the committed lock. The result must be byte-identical to the committed `requirements-dev.lock`.
   - **If it is not:** change no lock file. Leave the item and report the difference.
   - **The harness README:** in `proofs/stream-chat/README.md`, change the conformance description to match: three RECORDED rows, M5's new verdict, and the budget's 5 users.

**Not in B2-C4:**
- B2R5, B2R6, B2R8, B2R9 and `getstream`'s licence in the inventory, which are recorded;
- the signer and `delivery.py`;
- the guard, the deny-lists, the budget's caps and cleanup's rules;
- `proof_run.py`, the baselines and the workflow;
- every dependency and lock file.

**A finding outside this work:** report it with its class. Fix it here only if it could:
- let a credential, token or signature reach a log line, a record, a test recording or a file outside the git-ignored working directories;
- let a request reach Stream outside the guard;
- let provider text reach a Glow code or a user.

**Rules:**
- reversals in a scratch copy outside the repository, never the checkout, with `git status` clean afterwards (DM-14 item 6);
- no weakened check, guard, deny-list or budget;
- no credential anywhere;
- no live command.

**A departure** from any of the above that you find necessary: stop before making it, and report it.

## 4. Checks

Report the exact commands and results.

1. `git diff --check <START_SHA> HEAD` and `git diff --name-only <START_SHA> HEAD`: only owned paths changed.
2. **Classification,** with the trusted policy from `main`, outside the tree. Expected: full scope.

   ```bash
   base=$(git rev-parse origin/main); d=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$d/change_scope.py"
   python3 -I "$d/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```
3. **Installs:** hash-locked installs and `pip check` for the API and the harness; `npm ci` for the harness's client, with `npm audit`'s advisory named (package, severity, advisory ID; no change).
4. **The offline checks:**
   - the API's tests (328 at the start) and the harness's tests (638 at the start), with their counts;
   - Ruff check and format, and mypy;
   - the static check, with `makemigrations --check --dry-run`;
   - the sealed-runtime and pin tests;
   - `node --check` on the harness's client files;
   - `checks/run_plan.py`'s result, with the new count.
5. **Item 6's command:** the uv command, its path and version, and the byte comparison.
6. **The run of record:**
   - **If your branch is under the workflow's push filter:** the Foundation run on your last code commit, with its run ID, each job's conclusion (eight jobs), the database job's duration, and the gate's line `Application checks passed`. Push nothing more until it has finished (AM5-14).
   - **Otherwise:** say that no run started, and why.
7. A secret scan over your whole diff and your record.

## 5. Owned paths, push and records

- **You may change:**
  - `services/api/glow_domain/chat_provider_stream.py` and `services/api/tests/test_chat_provider_stream.py`;
  - `services/api/README.md`: the development-lock command and its sentence only;
  - in `proofs/stream-chat/`:
    - `glow_stream_proof/conformance.py`;
    - `checks/run_plan.py`: the conformance count only, never its caps, its ledger's addition or its wording;
    - `tests/**`;
    - `README.md`: the conformance description only;
  - the evidence record: a new section "Stage B2-C4" after the existing sections, which stay byte-identical.
- **Nothing else.** Report any other change you think is needed, before making it.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage B2-C4"** records:
  - the prompt's revision and start SHA, your head, your branch and the run of record;
  - items 1 to 6, each done (with `file:line`, its test and its reversal) or left (with the reason), and the identifier keys item 1 chose;
  - every check with its exact results;
  - deviations and limits;
  - what the exact-head re-review must know.

## 6. Report

Your final message is the report Nathan relays. It covers:
- the prompt revision (revision 1, from `<START_SHA>`);
- the environment check (names only, the `.env` check included);
- your branch, head SHA and changed paths;
- items 1 to 6, done or left, with item 1's keys;
- every check with its exact results, and the run of record's details;
- deviations, departures you stopped at, findings outside the work with their class, and limits.
