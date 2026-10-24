# P06.2 Stage B2 review prompt — one exact-head review of B2, B2-C1, B2-C2 and B2-C3

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 9: "B2's design points" a to h with DM-16's conditions; "B2's live run stopped" and its successors through "B2's live rows, and what they leave" (points i to iv, with DM-20's conditions); D8 as decided (OD-45).
- **Where the result goes:** the reviewer reports to Nathan; the manager records the review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage B2", and in the brief's "Sessions". The correction pass that follows (DM-20 7.1) takes DM-20's 1.2 and 1.3 and whatever this review asks for.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.60 (confidence 0.74); rung probabilities low 0.00, medium 0.00, high 0.02, extra high 0.35, max 0.63, ultracode 0.00. Model probabilities Fable 5.1 0.84, Opus 5.5 0.16, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.79). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.017, Fable 5.1 at extra high 0.294, Fable 5.1 at max 0.529, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.003, Opus 5.5 at extra high 0.056, Opus 5.5 at max 0.101, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T00:09:21Z. Nathan picks the cell.
  - **Nathan's pick:** Fable 5.1 at max, TypeSafe's reading (24 October).
- **The Dev Manager's read:** none needed; the prompt authorizes no credential use and no live provider action. It names DM-16 1.5's security focus areas, since this session is the only security reading of B2 (OD-41).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29).
- **Deletion condition:** prune after Stage B2's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stage B2**, the live half of Stage B of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. You review B2 and its three correction passes together, at one exact head. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.** Stage B1 merged on 22 October (PR30, `3272eed`). Stage B2 and its corrections are the draft PR31, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`:

- **B2** (code head `e97f90d`): the Stream adapter on the chat provider port (`services/api/glow_domain/chat_provider_stream.py`), the client token's signer, `getstream` 6.1.0 and `pyjwt` 2.15.0 in the API's development scope only, the sealed-runtime test extended, the harness's `conformance` command (46 rows), and the database job's timeout from 20 to 30 minutes. Its first live command found Stream's additions since 27 September and stopped.
- **B2-C1** (code head `2f54538`): the chat target covers every channel type other than `glow-match`; `products.merged_baseline_record`; the read-only `full-view` command and the offline `compare-views`; the API's development lock aligned with the harness's.
- **B2-C2** (code head `ebdc690`): `full_view.KEYED_LISTS` (the geofences by `name`), the merged products baseline of 23 October in force, and a docstring. Its live run locked the chat target.
- **B2-C3** (records only, `9dbcda8`): the Video and Feeds lockdown, then B2's 46 live rows. Result: 42 PASS, 2 RECORDED (R7, V7), 2 DIFFERENCE (M5, D10).
- **The Dev Manager read each pass first** (DM-16 to DM-20).
  - **D10 is dispositioned** (DM-20 item 1, option (b)). **D10 and V13 did not exercise "a user Stream does not have" live:** rows C4, M5, D10 and V13 share one identifier, and M5's accepted send created that user at Stream. The evidence for their cause is C4's live read (the same `_users` read, by ID, deactivated users included) and the offline test `test_deactivation_and_revocation_never_create_a_user`. V13 also showed live that a revocation for a deactivated user is refused, so no cut-off is set.
  - The rows' identifiers are corrected, and M5 becomes a recorded row, in the correction pass after this review (DM-20 1.2, 1.3).
- **Nathan decided D8 on 24 October (OD-45):** the app holds no Stream credential. The signer and the token rules stay in the code, dormant, until a later cleanup. Whether to remove them is not this review's question.

**The run of record for the head's code** is B2-C2's push run 40025252591 on `ebdc690`: all eight jobs passed, and the gate printed `Application checks passed`. The head's code is byte-identical to `ebdc690`'s. B2's own run is 39971426724 on `e97f90d`, and B2-C1's is PR31's run 40010499562 on `34f494c`.

- **You review one exact head:** `<RECORDS_COMMIT>`.
- **Your scope is PR31's whole code change:** `git diff origin/main...HEAD` over every non-Markdown path (26 files, about 10,700 lines added; one of them is a 4,995-line baseline file written by the harness), read against the code at `HEAD`. B1's code was reviewed at its own head; re-read it where B2 depends on it. Read the Markdown records too, for claims, not as code.
- **The review is offline:** the code, the offline tests, and the runs' logs. You start no database and call no provider.
- **What comes after this review.** Report every finding with its severity. The correction pass after this review takes every blocking finding. It also takes any should-fix finding that could:
  - let a credential, token, signature or other secret reach a log line, a record, a test recording, an artifact or a file outside git-ignored working directories;
  - let a request reach Stream outside the harness's guard or its configure scope, or let a configuration command change anything beyond its planned scopes;
  - let the API runtime import the adapter, the SDK or `pyjwt`, or load a Stream credential;
  - let a provider write undo a removal, a deactivation or a revocation, lower a held cut-off, or add a member to a channel Stream already has;
  - let provider text, or a provider field other than an identifier, reach a Glow code or a user;
  - make a record claim more than the code, the tests or the runs show;
  - leave a DM-16 to DM-20 condition unmet.

  Everything else goes into the records. For each finding, say whether it falls in one of those classes.
- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Reversals and scratch work in a copy outside the repository, never the checkout** (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Never:**
  - dump the environment;
  - call Stream, or run any harness command that reaches it (`baseline`, `full-view`, `configure`, `restore`, `verify-clean`, `cleanup`, `run`, `conformance`); the harness's offline tests use fakes and are allowed, as is `compare-views` on files you make yourself;
  - start or connect to any database; connect to HDE, Railway or any other provider;
  - run `playwright install`, `eas` or `migrate`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*`, `PROOF_DB_*` or `STREAM_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_|STREAM_)'` prints names only. If a `STREAM_*` name is present, stop and report: this session must start in `Glow App - No Stream`. If another is present, report its name first, never read or use its value, and continue.
3. The pinned toolchain is in `$HOME/.local/bin`, including Python 3.12.14, Node 24.19.0 and npm 11.9.0. Put `$HOME/.local/bin` first on PATH in every process you run, then record `command -v python3.12` and its version. Create any virtual environment with `python3.12`.
4. Run the API's and the harness's commands in a clean process environment (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API), as `docs/operations/local-development.md` and the READMEs show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <RECORDS_COMMIT>
git rev-parse HEAD                      # must print <RECORDS_COMMIT>
git merge-base --all origin/main HEAD   # expected: one line, 3272eed3d6b07d3215c6c667000082b6254eea69
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stage B2'   # must print 0: this review is not yet recorded
git diff --quiet ebdc690b3341cd81e60d92b9526f9f1d12c37f24 HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
git diff --shortstat origin/main...HEAD -- proofs .github services scripts apps packages   # expected: 26 files changed, 10733 insertions(+), 73 deletions(-)
```

If any check fails, stop and report. The checks on `origin/claude/magical-wozniak-yfmmx2` read the live manager branch: if this prompt's commit is not on it, if code landed after it, or if this review is already recorded, the prompt is stale.

Classify, as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree and full SHAs:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
git diff --name-only origin/main...HEAD | grep -v '\.md$' | grep -v -E '^(services/api/|proofs/stream-chat/|\.github/workflows/foundation\.yml$)'
```

Expected: `"full": true`. The last command must print nothing: every non-Markdown change is under `services/api/`, `proofs/stream-chat/` or the one workflow. Anything else is code this review would not cover: stop and report it.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md` and `proofs/stream-chat/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`: D2, D5, D6, D8 (as decided), "B2's design points", and every section from "B2's live run stopped" to "The client-token question (D8)";
- the Dev Manager's reports DM-16 to DM-20 in `docs/continuity/dev-manager/reviews/`. Read DM-16 whole; for DM-17 to DM-20, read their verdicts and conditions;
- the evidence record's sections "Stage B2" to "Manager verification of Stage B2-C3", whole;
- the architecture document `docs/architecture/chat-provider-permissions.md`, sections 4, 5 and 8; ADR 0003's "Conditions" and "Revisit when";
- **the whole code diff** `git diff origin/main...HEAD` over every non-Markdown path. Read these whole at `HEAD`:
  - `services/api/glow_domain/chat_provider_stream.py`, with `chat_provider.py`, `chat_tokens.py` and `chat_provider_fixtures.py` for the port, the grant and the fixture it is measured against;
  - `services/api/glow_chat/delivery.py`;
  - in the harness: `glow_stream_proof/conformance.py`, `full_view.py`, `products.py`, `configuration.py`, `credentials.py`, `guard.py`, `server_api.py`, `redaction.py`, `workdir.py`, and `cli.py`'s commands that B2 to B2-C2 added or changed.

**The runs' logs:** run 40025252591 on `ebdc690` (the run of record: its Stream proof job, its database job and its gate), and the API checks job of run 39971426724. Read enough to confirm the claims below; say what you read.

## 3. What to review

1. **DM-16 1.5's security focus areas** (this review is the only security reading of B2, OD-41):
   1. **the new resolved set and its hashes:** `services/api/requirements-dev.in` and `requirements-dev.lock`, `dependency-inventory.json`, and `tests/test_dependency_pins.py`. Check:
      - every package `getstream` and `pyjwt` bring in is hash-pinned, in the development scope only, and absent from `requirements.lock`;
      - the pin test fails when a shared package leaves the harness's version or hash;
      - B2-C1's alignment (nine shared packages moved; `tzdata` dropped as an orphan) leaves nothing unpinned;
   2. **every path the secret takes, the signer included:**
      - the harness's credential loader and `ServerApi`;
      - the adapter's injected client;
      - `sign_chat_token`, which uses `client.api_secret`;
      - the full view's withholding of credential-like values (`CREDENTIAL_KEY_PARTS`, digests in git-ignored files only, DM-18 3.4);
      - the redactor;
      - `workdir`'s checked writer.

      Can a secret, token or signature reach a log line, an exception text, a record or a test recording?
   3. **the adapter's exception boundary** (DM-16 4.1): one tuple of the SDK's and `httpx`'s errors; `_send_error` is the only reader of Stream's text, in memory. Can any provider text reach a Glow code, a log or a user? Does any exception outside the tuple escape as something other than a mapped code?
   4. **the recorded transport's contents** (4.2): the adapter tests' recordings and fakes hold no credential and no real identifier;
   5. **the guard's coverage of each new request** (4.3), shown in code and tests: every request `conformance`, `full-view` and the products apply can send. In particular:
      - `full-view` sends GET and HEAD only;
      - the products apply sends only `grants` naming client roles with `[]`;
      - `configure --apply` runs outside the guard by design (DM-17 2.4; `cmd_configure`'s comment). Is that the only unguarded path?
2. **The manager's five points** in the evidence record's "Manager verification of Stage B2". Agree or not with each:
   1. the creator: `glow-match` grants no owner-scoped permission to any role, so making the first member the creator gives it nothing beyond membership;
   2. the read-first paths (4.4): no write path can reach Stream for an existing object, and a revocation never lowers a held cut-off;
   3. the `KeyError` the SDK raises on an undecodable 2xx body: delivery (`glow_chat/delivery.py`) keeps it as a retryable Glow code, and the retry meets the existing object;
   4. the fixture's `ok` against the adapter's `already` for an earlier cut-off: delivery treats both as delivered;
   5. the two locks: B2-C1 aligned them. Is any difference left between what the live rows ran under (the harness's lock) and the API's development lock?
3. **D10's disposition** (DM-20 1.1). Confirm in the code that:
   - C4's live read is the same call `deactivate_user` and `revoke_user_tokens` begin with;
   - the offline test covers the branch after it.

   Does anything else in the adapter, delivery or the records depend on D10 or V13 having exercised their cause live? Record the identifier correction (1.2) and M5's move to a recorded row (1.3) as the correction pass's, not as new findings.
4. **The two findings DM-20 item 3 leaves to you:**
   - the conformance results replace only the run prefix in identifiers (`_generic` and `_TABLE_NAMES`), so the random part of a synthetic user's ID stays in the git-ignored results. Should the correction pass fix it, with a test that no row's detail keeps a run identifier's random part?
   - `checks/run_plan.py` adds the checkout's session ledger to every plan, so it reads "DOES NOT FIT" after a live run in the same checkout. Only its wording may change; never the caps or the ledger's addition.
5. **The conformance command and its rows:**
   - each of the 46 rows tests what its name says, apart from D10 and V13 above;
   - the verdicts (PASS, RECORDED, DIFFERENCE) follow the fixture as DM-16 4.x defines;
   - the run checks the configuration itself before its first changing request (DM-16 1.1);
   - the rerun rule and the blocking rule are as DM-16 1.3 and 5.2 state;
   - cleanup deletes only what the run created, by record and by prefix.
6. **B2-C1's and B2-C2's harness code:**
   - `configuration.py`'s coverage of every channel type other than `glow-match`;
   - `merged_baseline_record` (DM-17 1.1): scopes the earlier baseline holds keep its client grants;
   - `full_view.py`'s comparison: `VOLATILE_FIELDS` matches by name at any depth, so check that no configuration field hides behind `created_at`, `updated_at` or `duration`; `KEYED_LISTS` keys one path and falls back to position;
   - `PRODUCTS_BASELINE` and the 23 October baseline file: its difference from the 27 September file is exactly six paths, and its test holds that.
7. **M5 and R7** (DM-20 item 2): no adapter change. Is there any path by which Glow's delivery could send for a sender Stream does not hold, given the order in `delivery.py` and the adapter's `create_channel` read?
8. **The workflow:** the database job's `timeout-minutes` 20 to 30, and nothing else. The CI policy's sentence on it (DM-16 6.1).
9. **The records:** the evidence record's sections for B2 to B2-C3 and the brief's revision 8 and 9 sections. Does any statement claim more than the code, the tests or the runs show? Check the conformance rows table and the mappings against `conformance.py` and the adapter.
10. **The offline checks,** run at `HEAD` in a clean environment:
    - the API: hash-locked installs and `pip check`; `manage.py check` and its tests (328); Ruff; mypy; the static check with `makemigrations --check --dry-run`; the sealed-runtime, pin and toolchain tests;
    - the harness: hash-locked install and `pip check`; its tests (638); Ruff; mypy; `node --check` on its client files;
    - `npm audit`'s advisory, named.

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), the start gate's and the classification's results;
- the environment check;
- a verdict: **approve**, or **changes required**, with the findings that require them;
- every finding, numbered, with:
  - its severity (blocking, should fix, nit);
  - its file and line;
  - what is wrong, why it matters, and a suggested fix;
  - whether it falls in one of the correction classes above;
- for each focus area, what you checked and what you found;
- the offline checks you ran, with their exact results;
- limits of the review, and open questions.
