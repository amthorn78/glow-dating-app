# P06.2 Stage C1 review prompt — the exact-head review of C1

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 13: "Stage C under OD-45", points a to k, with DM-22's conditions; D5, D6 and D8 as decided (OD-45).
- **Where the result goes:**
  - The reviewer reports to Nathan.
  - The manager records the review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage C1", and in the brief's "Sessions".
  - A correction pass follows if the review asks for one.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.70 (confidence 0.81); rung probabilities low 0.00, medium 0.00, high 0.00, extra high 0.29, max 0.71, ultracode 0.00. Model probabilities Fable 5.1 0.88, Opus 5.5 0.12, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.84). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.255, Fable 5.1 at max 0.625, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.000, Opus 5.5 at extra high 0.035, Opus 5.5 at max 0.085, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T14:01:54Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed. The prompt authorizes no credential use and no live provider action. This session is the only security reading of C1 (OD-41), so section 3 names the security focus.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29).
- **Deletion condition:** prune after Stage C1's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stage C1**, the server half of Stage C of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. You review C1 at one exact head. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.** Stage B2 merged on 24 October (PR31, `3572c41`).

- **Nathan decided D8 as option (b)** (OD-45):
  - the app holds no Stream credential;
  - Glow's API serves history and new messages;
  - Stream stays the provider behind Glow's server.
- **Stage C runs in two parts** (the brief's "Stage C under OD-45"), each merged before the next:
  - **C1** (this one) is the server half and the contracts;
  - **C2** is the mobile interface.
- **The Dev Manager read C1's design and prompt** in DM-22 and approved them with conditions. The brief's revision 13 and C1's prompt revision 2 apply those conditions as written.
- **C1 is the draft PR32,** from the manager branch `claude/magical-wozniak-yfmmx2` into `main`.
  - **Code:** `91c3945`.
  - **What it adds:**
    - the provider port's seventh operation, `read_message_texts`, in the fixture and the Stream adapters;
    - the history read, the conversation list and the read-cursor command (`services/api/glow_chat/reads.py`, with `glow_domain/chat_reads.py`);
    - the server's projections (`glow_domain/chat_projections.py`);
    - the proof's read phase (`proofs/postgres-ordering/glow_ordering_proof/read_phase.py`): 58 cases and two planted read controls;
    - seven production DTOs, with `ChannelEntitlement` losing `channel_ref`;
    - the shared corpus, from 373 to 586 cases;
    - the regenerated validators;
    - one line in the harness's test helper.

**The run of record** is the session's push run 40064952123 on `91c3945`. All eight jobs passed, and the database job took 7 min 34 s of its 30-minute timeout. The head's code is byte-identical to `91c3945`'s.

- **You review one exact head:** `<RECORDS_COMMIT>`.
- **Your scope is PR32's whole code change:** `git diff origin/main...HEAD` over every non-Markdown path, read against the code at `HEAD`. That is 29 files, about 16,800 lines added.
  - Two files hold most of those lines: the generated `validators.js` (about 12,900 changed lines) and the corpus (about 4,700). You check them by regenerating and by running them, not line by line.
  - The hand-written code is about 3,500 lines.
  - Read the Markdown records too, for their claims, not as code.
- **Split the reading by area if the head is too large for one reading** (DM-22 item 1's note). Subagents are fine. Say how you split it.
- **The review is offline:** the code, the offline tests, a disposable database you start yourself if your sandbox allows one, and the run's logs. You call no provider.
- **What comes after this review.** Report every finding with its severity. A correction pass takes every blocking finding. It also takes any should-fix finding that could do any of these:
  - let a history read, the list or a cursor move succeed after a revocation committed before its final check;
  - let a safety action wait on the provider;
  - let provider text, a provider ID or any other provider field reach a DTO, a log, a stored row or a user;
  - show a text Glow did not send;
  - let a message accepted late never reach the reader, or never count as unread (DM-22 2.2);
  - let a forced case or a planted control pass where it should fail;
  - let the API runtime import the reads, the projections or the adapter, or connect to any database;
  - make a record claim more than the code, the tests or the runs show;
  - leave a DM-22 condition unmet.

  Everything else goes into the records. For each finding, say whether it falls in one of those classes.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Reversals and scratch work go in a copy outside the repository, never the checkout** (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Never:**
  - dump the environment, or print a password, a marker or a connection value;
  - call Stream, or run any harness command that reaches it;
  - connect to any database other than a disposable one you start for this review (P06.DB brief, D4), and never to HDE, Railway or any other provider;
  - run `playwright install`, `eas`, or Django's `migrate` against anything but your own disposable database.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*`, `PROOF_DB_*` or `STREAM_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_|STREAM_)'` prints names only.
   - If a `STREAM_*` name is present, stop and report: this session must start in `Glow App - No Stream`.
   - If another is present, report its name first, never read or use its value, and continue.
3. **The toolchain.** The pinned toolchain is in `$HOME/.local/bin`: Python 3.12.14, Node 24.19.0 and npm 11.9.0.
   - Put `$HOME/.local/bin` first on PATH in every process you run.
   - Record `command -v python3.12` and its version.
   - Create any virtual environment with `python3.12`, outside the checkout.
4. **A clean process environment.** Run each component's commands in one, as `docs/operations/local-development.md` and the READMEs show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only that component's own variables. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <RECORDS_COMMIT>
git rev-parse HEAD                      # must print <RECORDS_COMMIT>
git merge-base --all origin/main HEAD   # expected: one line, 3572c41d8c401cc0c54430a9e364c2c1c58b5963
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stage C1'   # must print 0
git diff --quiet 91c39457a9657cc8c4bf8b1964ec822fb6506491 HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
git diff --shortstat origin/main...HEAD -- proofs .github services scripts apps packages   # expected: 29 files changed, 16788 insertions(+), 4836 deletions(-)
```

If any check fails, stop and report. The checks on `origin/claude/magical-wozniak-yfmmx2` read the live manager branch. The prompt is stale if:
- this prompt's commit is not on that branch;
- code landed after it;
- or this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree and full SHAs:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
git diff --name-only origin/main...HEAD | grep -v '\.md$' | grep -v -E '^(services/api/|proofs/postgres-ordering/|proofs/stream-chat/tests/test_conformance\.py$|packages/contracts/|apps/mobile/src/contracts/generated/)'
```

- **Expected:** `"full": true`.
- **The last command must print nothing.** Every non-Markdown change must be under one of these five paths:
  - `services/api/`;
  - `proofs/postgres-ordering/`;
  - the harness's one test file;
  - `packages/contracts/`;
  - the generated contracts.

  Anything else is code this review would not cover: stop and report it.

**Then read, completely, at `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md`, `proofs/postgres-ordering/README.md` and `packages/contracts/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`: "What P06.2 delivers", D5, D6, D8 (as decided) and "Stage C under OD-45", whole;
- the DM-22 report, `docs/continuity/dev-manager/reviews/2026-10-24-dm-22-p06-2-stage-c-read.md`, whole;
- C1's prompt, `docs/ephemeral/2026-10-24-p06-2-stage-c1-implementation-prompt.md`, revision 2;
- the evidence record's sections "Stage C1" and "Manager verification of Stage C1";
- ADR 0003, decisions 1 to 3 and "Revisit when";
- `docs/architecture/production-contracts.md` (F11, and the section the session added) and `docs/architecture/data-model.md`, "Chat contact and the outbox";
- **the whole hand-written code diff,** read whole at `HEAD`:
  - `services/api/glow_chat/reads.py`, with `contact.py` for the send's checks and helpers it reuses;
  - `services/api/glow_chat/delivery.py`, for `delivered_at` and `sequence`;
  - `glow_domain/chat_reads.py`, `chat_projections.py`, `chat.py`, `chat_provider.py`, `chat_provider_fixtures.py` and `chat_provider_stream.py`;
  - the tests under `services/api/tests/` that the change adds or edits;
  - in the proof: `read_phase.py`, `results.py`, `cases.py`, `interface.py`, `__main__.py` and their tests;
  - in the contracts: the schema, `flows-v1.json`, `openapi.json`, `tests/test_transition_contract.py`, and the corpus's new cases.

**The run's logs:** run 40064952123 on `91c3945`. Read its database job (the read phase's lines, the waits, the controls and the verdict), its mobile job (the generation check and the corpus) and its gate. Read enough to confirm the claims below, and say what you read.

## 3. What to review

1. **The safety order** (DM-22 3.2; the evidence record's "What the exact-head review must know"):
   - the first check's transaction ends before the provider call;
   - the call runs outside any transaction;
   - the final check takes the same shared locks again in a new transaction;
   - only then is the page returned;
   - a refused first check calls nothing.

   Are the planted controls (`read_phase.py`) the adapter's own steps in another order, as the session says? Could the adapter's code take a path that skips the final check, and would the suite notice?
2. **The checks** (point c; D5). Check that:
   - the reads make exactly the send's checks, with the send's helpers and in the send's lock order;
   - the list locks every account in UUID order, then every match, then the session.

   Can the list or a read deadlock against a send, a revocation or another read? If one can, is the deadlock mapped to a retryable Glow code, never a page? The interim rule (DM-22 3.1) is built as stated: confirm it, but do not ask for it to be softened.
3. **The text** (DM-22 2.1, 2.3 to 2.5):
   - the digest check through the send's own `request_digest`;
   - the `regular` and deleted filter in both adapters;
   - an ID answered twice;
   - a provider error failing the read, never giving an all-"unavailable" page;
   - a read writing nothing;
   - no message text in any log line, with the log-capture test.

   **The Stream adapter's call** never passes `member_custom_include` and reads only each message's ID and text. Can any other provider field reach the page?
4. **The order** (DM-22 2.2): the manager's observation 1 in "Manager verification of Stage C1".
   - `delivered_at` is read inside the delivery's transaction, before its commit. Can two deliveries of one channel's messages commit out of `delivered_at` order, so that a polling reader passes a message that then never appears and never counts as unread?
   - **Say which of 2.2's two cases the code meets:** an order that follows acceptance, or per-channel delivery order.
     - If it is the second, say so plainly. The manager then records P11's "Per-channel order across retries" as a requirement for the history read, without its "or records the case".
     - If it meets neither, it is a finding in the correction classes.
   - Check `read.order_follows_acceptance`: does it show what 2.2 asks?
5. **The read phase** (point c; DM-22 3.2 and 3.3):
   - **The cases:** sixteen revocations, three forced cases each, plus `read.block_during_provider_call` and nine named cases, for 58 in all.
   - **The waits:** each forced wait is observed where the case requires one. `read_waits` passes on "no wait observed": is that the right signal for "the reader holds no lock across the call"?
   - **The controls:** each fails by its declared signal.
   - **Unchanged:** `reference.py` and its ten controls.
6. **The contracts** (point f; DM-22 6.1 to 6.4):
   - no DTO can carry a provider ID, timestamp, error text or other provider field, and the corpus shows it through both validators;
   - `channel_ref` is gone from `ChannelEntitlement` and every consumer;
   - the latest-message marker is computed over visible rows only (6.1);
   - "unavailable" is one state with no reason (6.2);
   - the unread count follows 6.3;
   - the page cursor is opaque and bound to its match (6.4);
   - the generated outputs match a fresh `npm run generate`.
7. **The session's recorded choices** (the evidence record's "Choices for the review"). Judge each:
   - **`ReadCursorIntent` without `CommandMeta`,** against the production contracts' rule that every mutating intent carries an idempotency key and an expected version. If it should carry one, that is a contract change for the correction pass, before C2.
   - **F11's `read` transition.**
   - **`ConversationSummary.state`'s `closed`,** which nothing emits.
   - **One check** for a page with no accepted message.
   - **Own failed submissions' spool text.**
   - **The error mapping.**
   - **The order case** calling `OutboxDelivery._deliver` directly.
8. **The sealed runtime** (D2 2.3): the API runtime imports none of `glow_chat`, `chat_reads`, `chat_projections` or the adapters, and the extended test shows it.
9. **The records:**
   - the evidence record's "Stage C1";
   - the production contracts' and the data model's changes;
   - the two READMEs.

   Does any statement claim more than the code, the tests or the runs show? Judge the session's finding C1-X1 (the production contracts' older sentence on direct SDK bypass under OD-45) and say whether the correction pass should take it.
10. **The offline checks,** run at `HEAD` in a clean environment:
    - **the API:** hash-locked installs and `pip check`; `manage.py check` and its tests (361 at the run of record); Ruff; mypy; the static check with `makemigrations --check --dry-run`; the sealed-runtime test;
    - **the proof:** its tests (157); Ruff; mypy;
    - **the harness:** its tests (648);
    - **the contracts:** `npm run generate` with no diff, `npm run check` (586 corpus cases), and the Python contract tests (39);
    - **the mobile app:** `npm run check` (516).
    - **The database:** if your sandbox can run a disposable database (P06.DB brief, D4), run the read phase and say which database and version. If it cannot, say so; the run's logs then carry the database evidence.

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), and the start gate's and the classification's results;
- the environment check;
- how you split the reading, if you did;
- a verdict: **approve**, or **changes required**, with the findings that require them;
- every finding, numbered, with:
  - its severity (blocking, should fix, nit);
  - its file and line;
  - what is wrong, why it matters, and a suggested fix;
  - whether it falls in one of the correction classes above;
- for each focus area, what you checked and what you found, and for item 4, which of 2.2's cases the code meets;
- the offline checks you ran, with their exact results;
- limits of the review, and open questions.
