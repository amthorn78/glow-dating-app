# P06.1-I1 review prompt — exact-head code and security review

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), sections "P06.1-I1 result" and "Review plan". Evidence: [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md).
- **Recommended reasoning level: max, with ultracode.** Before the reading, the manager committed to max, or ultracode if the scorer flagged it. TypeSafe v4 reads extra high and flags ultracode. Nathan picks; without ultracode, run max in one session. Details are in the brief's "Reasoning levels".
- **Deletion condition:** prune after P06.1 closes and the brief and evidence record hold the accepted review result.

**Manager:** before giving this prompt to Nathan, replace `<REVIEW_HEAD>` with the exact head SHA of `claude/stoic-carson-66gdig` to be reviewed.

---

You are the **review session for P06.1-I1** of the Glow dating app, private repository `amthorn78/glow-dating-app`. The head you review holds P06.1-I1's work and the manager's records. P06.1-I1 was the first implementation session of P06.1, the chat-provider permissions proof: a sandbox harness in `proofs/stream-chat/` and its live results against Nathan's development Stream application 1729640, with synthetic users only.

- Nathan started you manually and will relay your report to the manager (App Manager 3). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes or PR comments.
  - Keep scratch work outside the repository, or in its ignored paths (`.venv/`, `node_modules/`, `.work/`).
  - In the Stream application, change nothing beyond what section 4 allows.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are set for application 1729640: `for n in STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n}" ] && echo "$n set" || echo "$n MISSING"; done`. Use them only for section 4. Never print, copy, log or write the secret or a full token.
3. Record `command -v node npm npx python3.12` and their versions. Expected: v24.19.0, 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`.
4. Never dump the environment. Never connect to a database, HDE or Railway. Never run `playwright install`, `eas` or `migrate`. The only provider you may call is Stream, application 1729640, as section 4 allows.
5. In a clean process environment, network installs need the proxy and CA variables passed through by reference, never printed. See "Claude Code cloud sessions" in `docs/operations/local-development.md` and the harness README.

## 2. Start gate

```bash
git fetch origin claude/stoic-carson-66gdig main
git switch --detach <REVIEW_HEAD>
git rev-parse HEAD                      # must print <REVIEW_HEAD>
git merge-base --all origin/main HEAD   # expected: one line, 0f45e648099b415217938c25d7369164c0101def
```

If any check fails, stop and report.

Classify first, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. If it reports `ordinary-docs-only`, stop and report that.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`;
- the I1 prompt, `docs/ephemeral/2026-09-25-p06-1-i1-implementation-prompt.md`: what the session was asked to do;
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, and `proofs/stream-chat/README.md`;
- in `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md`: section 7's "Chat and notifications" paragraph and section 8's P06;
- flows F10, F11 and F13 in `docs/architecture/production-contracts.md`;
- the whole of `git diff origin/main...HEAD`.

## 3. What to review

Review the complete diff. The focus areas are in order of risk.

1. **Credentials and tokens.**
   - The secret must never leave the server process. Check the client environment's allowlist (`client_bridge.py`), the runner's refusal (`client/runner.cjs`) and every subprocess the harness starts.
   - No secret or full token may reach standard output or error, `.work/` files, the evidence, exceptions or tracebacks. Check the redactor and the leak check (`redaction.py`, `workdir.py`), every error path (exception messages, the client's stderr tail, SDK error objects, library logging) and the requests the runner records. Stream's WebSocket URL carries the user token as a query parameter.
   - The committed baseline JSON and the evidence must hold no credential, token or personal data. The Stream dashboard user's identifier and name fields must not appear.
2. **Safety of live actions against the application.**
   - Preflight must refuse any data the run did not create. Nathan's direction during I1 accepted exactly one pre-existing user, the Stream dashboard administrator (see the evidence's "Stop condition"). Check that `--accept-dashboard-user` accepts that user and nothing wider.
   - Cleanup (`ProofRun.cleanup` and `cleanup --apply`) must delete only proof data. Check the prefix matching, the handling of the `deleted-user-1729640-…` system user, a partial cleanup, and a guardrail stop that skips cleanup.
   - Configuration (`configuration.py`): whether `apply_plan`, `verify` and `restore_plan` do what the README and the evidence say. Would the untested restore really return the recorded baseline? Consider Stream's grant semantics (`[]`, `null`, roles a request does not name) and features a type update might reset. What does the emptied admin role affect?
   - Temporary changes inside a run (channel `config_overrides`, the type-level custom-events and polls toggles, guest creation) must always be restored, including when a case raises. Could a crash leave one in place?
   - Guardrails: counting before sending, the session ledger, the runner's per-command cap and the charge-signal stop.
3. **Validity of the proof: silent passes.**
   - Does every verdict follow the brief's matrix quality rule? Check `matrix.classify`, the verdict functions and each procedure case in `proof_run.py`. A refusal counts only as an attributable 401 or 403 with Stream's code. The positive control must be the same request made by an authorized principal. A 400 or 404 never counts.
   - Where could a HOLDS be wrong? Consider:
     - a control that differs from its case in a way that matters;
     - "filtered, not refused" results, where target data might be present in another shape;
     - "accepted, not applied" results;
     - the feature-phase cases S2, S5, S6, S7 and S12, which switch a feature on to get an attributable refusal;
     - RT2 and RT3 (what B actually receives), and T4 (identity claims).
   - Do the evidence tables match the harness's logic and outcomes? I1's `.work/` output is not in the repository, so check the code paths that produce each row.
   - Coverage: compare the matrix with the I1 prompt's list (its section 4.1, item 6). Report required cases that are missing or weaker than required. Report client-reachable Stream endpoints the matrix did not try that could put content in front of the other member, or read outside the match.
4. **S15, the reported design blocker.** A member writes free-text custom data on its own membership (`updateMemberPartial`), and the other member receives it in its channel query and in `member.updated` events. The evidence says no configuration closes it.
   - Confirm or refute that from Stream's current documentation, the installed SDK sources and, if needed, section 4. Is there any setting, permission, grant, channel-type option or channel-level override that stops a member's own membership update, or keeps member custom data out of the other member's view? Include the application settings `member_custom_on_messages_enabled`, `member_custom_on_typing_events_enabled` and `member_custom_on_mentioned_users_enabled`.
   - Report anything that closes or narrows S15, with its documentation page.
   - The design response is Nathan's decision, which the manager puts to him separately. Your task is whether the finding is real and whether configuration can close it.
5. **Evidence and documentation.** Find claims the code or the results do not support, contradictions with the brief, and gaps in "Deviations" and "Limits". This is a full-scope review: never skip a finding because its file ends in `.md`.
6. **Dependencies.** Check:
   - the hash-pinned Python locks and the npm lock's sources and integrity;
   - `npm ci --ignore-scripts` (`stream-chat` declares an install script, which it skips);
   - the `ws` and `https-proxy-agent` pins, and the runner's module-cache substitution of `isomorphic-ws`: is it robust, and does anything weaken TLS?
   - `allowServerSideConnect`.
7. **Scope.** Only `proofs/stream-chat/**`, the evidence record and manager-owned Markdown changed. There is no application runtime, CI, configuration or `.env.example` change, and no `GLOW_*` variable.

**Out of scope:**

- the design response to S15;
- P06.1-I2's topics: revocation, history, outage and economics;
- the known intermittent rendered-suite failures;
- anything in HDE.

## 4. Live confirmation (optional)

You may confirm S15, and anything else your review needs, with the harness's live run. Follow the README's commands and these rules:

- **Before any run,** run `verify-clean` and the dry-run `configure`. The expected result is no proof users, no channels, one other user (the dashboard user) and "differences before: []". If the application holds anything else, for example a `deleted-user-…` user, a leftover proof user or any channel, or the configuration differs, do no live run and report.
- **At most two runs**, each `run --accept-dashboard-user --only <case ids>`, within the brief's per-session guardrails: 20 synthetic users, 30 channels, 10 concurrent connections and 5,000 API calls. The harness counts them. Each run also sets up four users and two channels, and runs the authorized path and the reconnect check.
- **One place, one at a time.** Run every live command from a single checkout, one after another, never from parallel agents or separate worktrees. Then the harness's session ledger counts every call, and no cleanup can touch another run.
- **Never** run `configure --apply` or `restore --apply`. Use `cleanup --apply` only to remove your own runs' leftovers. Finish with `verify-clean`.
- Stop at once if anything suggests a charge, an upgrade or an exceeded limit.
- The secret and full tokens must never appear in any output. Report the run prefix, the UTC start and end times, the cases, the results, the usage and the cleanup result.

## 5. Checks to run

Report the exact commands and results.

1. `git diff --check origin/main...HEAD`.
2. The classification above.
3. The installs from the locks, in clean processes, with the README's commands.
4. The offline unit tests, Ruff (check and format), mypy and `node --check client/runner.cjs`, with the README's commands.
5. A secret scan over the whole diff, and over any output your live runs produce.
6. The live confirmation, if you ran it.
7. Anything else you judge necessary.

The manager reads hosted CI on the reviewed head, so you need not wait for it.

## 6. Report

Your final message is the report Nathan relays:

- the head you reviewed (`git rev-parse HEAD`) and the classification output;
- **verdict:** "approve" (the I1 head is a sound base for P06.1-I2) or "changes required";
- **S15:** confirmed, refuted or narrowed, with the documentation, source or live evidence;
- **findings,** most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario and a suggested fix;
- the areas you reviewed with no findings;
- every check you ran, with its exact result, and each live run as section 4 asks;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. Change nothing in the repository, on GitHub or in Notion.
