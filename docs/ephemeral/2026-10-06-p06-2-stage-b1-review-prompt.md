# P06.2 Stage B1 review prompt — exact-head code and security review

- **Owner:** App Manager 6. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 6 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 3, and its "Sessions"; the [Stage B1 prompt](2026-10-06-p06-2-stage-b1-implementation-prompt.md), revision 1.
- **Where the result goes:** the reviewer reports to Nathan; the manager records the review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage B1", and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Fable 5.1, max.** Effort score 3.70 (confidence 0.80); rung probabilities low 0.00, medium 0.00, high 0.01, extra high 0.28, max 0.71, ultracode 0.00. Model probabilities Fable 5.1 0.94, Opus 5.5 0.06 (confidence 0.88). Sent 2026-10-06T04:15:46Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed; the prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29).
- **Deletion condition:** prune after Stage B1's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stage B1**, the offline half of Stage B of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.** Stage A merged on 6 October (`02072f4`): a chat contact adapter (`services/api/glow_chat/contact.py`) carrying P06.DB's transaction design, outbox delivery to a fixture provider, token rules, migration `0003`, and P06.DB's race suite on two subjects, the reference design and the adapter. Its reviews carried eight items to Stage B (F1 to F5, CX4 to CX6). Stage B was split (brief revision 3): B1, offline, makes those eight changes; B2, live, adds Stream later. The Dev Manager's DM-15 set the conditions B1 had to meet.

**What Stage B1 built:**

- a provisioning event per new chat identity, delivered before the channel, ordered by a database-assigned `OutboxEvent.sequence` (`glow_persistence/fields.py`'s `SequenceField`), with identities `pending` until the provider's receipt (CX4; DM-15 3.1 to 3.5);
- a reconciliation mark (`reconcile_code`) on bindings and identities, set when a revocation or provisioning dead-letters; a revocation of a marked or failed binding still removes (F3, CX6; DM-15 4.1 to 4.5); migration `0003` amended, not a new `0004`;
- the grant's transaction in the adapter (`grant_token`): account then session `FOR SHARE`, `clock_timestamp()` under the locks; the cut-off sent at the next whole second (F1; DM-15 5.1, 5.2);
- activation's profile and consent checks under its account locks (CX5), and the nits F2, F4 and F5;
- 33 new adapter cases (114 in all; the reference keeps 56), oracle rule O11 with two planted controls, four new delivery cases;
- in `proofs/stream-chat/`, offline: the C5 review's nits 2 and 3 and a request-header allowlist.

**No app runtime gains a database, real authentication or a live provider**, and nothing called Stream.

**The run of record** is the session's push run 37410705342 on `cab71b9`: all eight jobs passed, and the gate printed `Application checks passed`. Its database job is job 112098441694.

- **You review one exact head:** `e614d8a12c39884045023dbb71c615ea40899674`, the merge that integrated Stage B1.
  - Its first parent, `8f34dc4`, is the manager branch before the merge. Its second parent, `e6a5c0d`, is the session's head. The code head is `cab71b9a25bb4af2c88b3959efb0851bdd319eb0`, and the merge's code is byte-identical to it.
  - The merge brought 36 files: 14 non-Markdown under `services/api/`, 11 under `proofs/postgres-ordering/`, 5 under `proofs/stream-chat/`, and Markdown.
- **Your scope is Stage B1's change:** the whole of `git diff HEAD^1 HEAD`. Read it against the code as it stands at `HEAD`, because a change can break code it did not touch. Stage A's review covered the adapter at `e8eb5d3`; re-read it where B1's changes depend on it. Later commits are Markdown-only records, which you read at `<RECORDS_COMMIT>`.
- **The database run is not repeated here.** You start no database. The review is offline: the code, the offline tests, and the run of record's logs.
- **What comes after this review.** Report every finding with its severity. A correction pass comes before Stage B1 merges for any blocking finding, and for any should-fix finding that could:
  - let a send authorization or an activation commit after a revocation, pause, restriction or withdrawal that invalidates it without the suite failing;
  - let a token be granted at an old epoch, or for an identity the provider does not have, or survive a revocation it should not;
  - let a channel be created before both members are provisioned, or a revocation be recorded without its provider call;
  - let a password, the marker or a connection value reach a log, an artifact or a file outside the job's temporary directory;
  - let the job, the proof or the adapter connect to anything but its own disposable database, or let the API runtime load the adapter or connect to any database;
  - make DB06's or DB09's mark claim more than the run shows;
  - let the provider receive a channel, member or user name, image or custom field, an invite, a call, a feed or an activity, or let provider text reach a stored row, a log or a user;
  - let the harness send a request it would not have sent before B1.

  Everything else goes into the records. For each finding, say whether it falls in one of those classes.
- Nathan started you manually and will relay your report to the manager (App Manager 6). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Reversals and scratch work in a copy outside the repository, never the checkout** (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Never:**
  - dump the environment;
  - start or connect to any database, whether a local cluster, a container, or the proof's settings pointed at anything, and never set a database's comment. Never connect to Stream, HDE, Railway or any other provider, and never run a harness command that sends a request;
  - run `playwright install` or `eas`;
  - run `migrate` or the proof's `facts` and `run` commands yourself. The offline tests run commands only through `tests/command_harness.py`, whose fake server opens no connection; running the tests is allowed.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*`, `PROOF_DB_*` or `STREAM_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_|STREAM_)'` prints names only. If a `STREAM_*` name is present, stop and report: this session must start in `Glow App - No Stream`. If another is present, report its name first, never read or use its value, and continue.
3. The pinned toolchain is in `$HOME/.local/bin`, including Python 3.12.14 and Node 24.19.0. Put `$HOME/.local/bin` first on PATH in every process you run, then record `command -v python3.12` and its version. Create any virtual environment with `python3.12`.
4. Run the API's, the proof's and the harness's commands in a clean process environment, as `docs/operations/local-development.md` and each README show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach e614d8a12c39884045023dbb71c615ea40899674
git rev-parse HEAD                      # must print e614d8a12c39884045023dbb71c615ea40899674
git rev-parse HEAD^2                    # must print e6a5c0d96a9f71b63d8e7aa365efd8e6e18ece83
git merge-base --all origin/main HEAD   # expected: one line, 02072f4dcb0c20dd45dee9bc02e75323d0a2aec7
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stage B1'   # must print 0: this review is not yet recorded
git diff --shortstat HEAD^1 HEAD        # expected: 36 files changed, 2769 insertions(+), 252 deletions(-)
git diff --quiet cab71b9a25bb4af2c88b3959efb0851bdd319eb0 HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
```

If any check fails, stop and report. The three checks on `origin/claude/magical-wozniak-yfmmx2` read the live manager branch: if this prompt's commit is not on it, if code landed after that commit, or if this review is already recorded, the prompt is stale.

Classify three times, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree, every run uses the same policy file, and every SHA is a full one (a short SHA fails closed):

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$(git rev-parse HEAD^1)" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only "$base" "$head" | grep -v '\.md$' | grep -v -E '^(services/api/|proofs/postgres-ordering/|proofs/stream-chat/)'
```

- **The first run** is the head against `main`. Expected: `"full": true`. The last command must print nothing: every non-Markdown change is under `services/api/`, `proofs/postgres-ordering/` or `proofs/stream-chat/`. Anything else is code this review would not cover: stop and report it.
- **The second run** is the manager branch before the merge against `main`. Expected: `ordinary-docs-only`, so all of the code is Stage B1's.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md`, `proofs/postgres-ordering/README.md` and `proofs/stream-chat/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md` (revision 3): D1 to D7, the owned paths, "Carried to Stage B and P11" and "B1's design points";
- the Stage B1 prompt, `docs/ephemeral/2026-10-06-p06-2-stage-b1-implementation-prompt.md`: what the session was asked to do, its rules and owned paths;
- the DM-14 and DM-15 reports, `docs/continuity/dev-manager/reviews/2026-10-06-dm-14-p06-2-stage-a-governing-read.md` and `2026-10-06-dm-15-p06-2-stage-b-split-read.md`;
- the evidence record, `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: "Exact-head review of Stage A", "Codex's review of PR29", "Codex's second code review, of `9f6f6ab`", and "Stage B1", whole;
- `docs/architecture/data-model.md`, "Chat contact and the outbox", and `docs/operations/migration-plan.md`;
- the whole of `git diff HEAD^1 HEAD`, and, whole, every file it adds;
- the `database` job of `.github/workflows/foundation.yml` (unchanged by B1).

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the evidence record's "Manager verification of Stage B1" (its five points for this review);
- the brief's "Sessions".

**The run of record's logs:** the database job 112098441694, whole, and the gate's log line.

## 3. What to review

The focus areas are in order of risk.

1. **The grant** (`contact.py`'s `grant_token`; F1; DM-14 item 3; DM-15 5.1).
   - One transaction: the account row, then the session row, `FOR SHARE`, in the send's order; `clock_timestamp()` under those locks; every check of `grant_chat_token` on the locked rows. Can a grant read an old epoch after a bump commits, or interleave with the send, a sign-out or a bump into a deadlock?
   - A `pending`, deactivated or missing identity is refused `no_chat_identity`.
   - The forced cases both ways, with the app's clock skewed ahead. The manager's point 2: does any test fail if the issue time came from the app's clock while the session stays valid?
   - The cut-off: the exact time stored; the next whole second, strictly, sent to the port, with the zero-microsecond case.
2. **Provisioning and the order key** (CX4; DM-15 3.1 to 3.5).
   - `SequenceField` (`glow_persistence/fields.py`): the manager's point 1. Is it assigned by the database on every insert path, never by the app, and read back correctly? Does it change anything for `0001`'s table beyond the new column?
   - Delivery by `(available_at, sequence)`: within one transaction, the provisioning events come before the channel's; across writers, can a channel event overtake its members' provisioning? The manager's point 3.
   - An identity is provisioned only on the provider's receipt; a channel whose member is not provisioned dead-letters `member_unavailable` without a call; a second match for a provisioned account writes no second provisioning; provisioning carries `user_id` only and is idempotent; the fixture refuses a channel naming an unknown member.
   - A lost provisioning response marks the identity, and a later deactivation or revocation still calls (a user the provider lacks counts as done).
3. **The mark and revocation's delivery** (F3, CX6; DM-15 4.5). The manager's point 4. A message is never delivered into a marked binding; every revocation plan for a marked or failed binding still calls the provider, and `channel_unavailable` counts as removed for that plan only; the binding ends `revoked` with the mark's reason. Is the mark always a Glow code, never provider text?
4. **Activation's checks** (CX5; DM-15 6.1, 6.3). The send's profile and consent checks run on rows read under activation's account locks; the forced cases both ways for a pause and a withdrawal; is the restriction's writer really the pause's (`test_restriction_shares_the_pause_writer` reads the source)? `activate_match`'s docstring says it is not F09's activation.
5. **The nits** (F2, F4, F5). The re-checks after the locks; the deadlock mapping's test; the self-block refused before any lock or write. The manager's point 5: do the F2 cases, which move keys from a harness transaction, or the token cases, which provision by a fixture write, hide an adapter path?
6. **The suite** (DM-15 6.2, 6.3). O11: correct, scoped to the adapter, and caught by its two planted controls; any other new rule with its control. `reference.py`, its 56 cases and ten controls unchanged. The 33 new cases and four new delivery cases: does each test what it names? Is any part of the change untested? The session's 34 fix reversals: spot-check some in a scratch copy.
7. **Migration `0003`** (DM-15 4.1 to 4.4). Amended by the autodetector, with no `RunSQL` or `RunPython`; `0001` and `0002` byte-identical; the test asserts the exact operation list; `makemigrations --check --dry-run` passes; the migration plan records `0003` and the amendment rule. Is the claim that `0003` was applied only to disposable databases well founded?
8. **The harness** (`proofs/stream-chat/`; the C5 review's nits 2 and 3). The nit 2 test and its reversal; `finish()`'s chaining; the header allowlist: pinned to the locked SDK and axios, checked before any request leaves, the earlier refusals unchanged. Can any request leave that would not have left before B1, or does the allowlist refuse one the harness's run plan needs?
9. **The runtime stays sealed** and **no dependency changed**: the sealed-runtime test; no change to any dependency file; no `getstream` import.
10. **The log and the records.** From job 112098441694: each held case with its holder, per subject, the new cases named; O11's controls; the oracle's figures; the delivery phase; the refusals; the container's removal; no password or marker (say what each `***` is; look for strings of 32 or 48 hexadecimal characters). Does any statement in the session's "Stage B1" section, the data model, the migration plan or the READMEs claim more than the code and the run show? Check the figures against the log.
11. **The manager's five points** in "Manager verification of Stage B1": agree or not with each.

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), the start gate's and the classifications' results;
- the environment check;
- a verdict: **approve**, or **changes required**, with the findings that require them;
- every finding, numbered, with its severity (blocking, should fix, nit), its file and line, what is wrong, why it matters, a suggested fix, and whether it falls in one of the correction classes above;
- for each focus area, what you checked and what you found, including what you confirmed;
- the offline checks you ran, with their exact results;
- limits of the review, and open questions.
