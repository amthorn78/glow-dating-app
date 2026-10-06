# P06.2 Stage A review prompt — exact-head code and security review

- **Owner:** App Manager 6. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 6 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 2, and its "Sessions"; the [Stage A prompt](2026-10-05-p06-2-stage-a-implementation-prompt.md), revision 1.
- **Where the result goes:** the reviewer reports to Nathan; the manager records the review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage A", and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Fable 5.1, max.** Effort score 3.94 (confidence 0.95); rung probabilities low 0.00, medium 0.00, high 0.01, extra high 0.03, max 0.95, ultracode 0.01. Model probabilities Fable 5.1 0.98, Opus 5.5 0.02 (confidence 0.96). Sent 2026-10-06T00:44:55Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed; the prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29).
- **Deletion condition:** prune after Stage A's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stage A**, the first of three stages of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What Stage A built.** P06.DB proved, on a disposable PostgreSQL 17 database in the Foundation job "Database proof checks", a reference design that orders message-send authorizations against every revocation of contact (`proofs/postgres-ordering/`). Stage A carried that design into the app:

- a domain port, `glow_domain/chat.py`, and an ORM adapter, the new package `services/api/glow_chat` (`contact.py`), on `glow_persistence`'s models, with P06.2's extra checks: a paused or restricted profile and a withdrawn onboarding consent refuse a send;
- two new models and an additive, unapplied migration `0003` (`ChatIdentity`, an opaque provider user ID; `ChatReadCursor`);
- an outbox delivery path (`glow_chat/delivery.py`, `glow_chat/events.py`) with a provider port and a fixture provider only (`glow_domain/chat_provider*.py`), and token rules (`glow_domain/chat_tokens.py`);
- the race suite on two subjects, the reference design and the adapter, each with its own evidence reader and verdict, new oracle rules (O0, O9, O10, O5 narrowed), planted oracle controls, per-order counts, a delivery phase, and two new job steps: `dbshell` refused, and a second run on a used database refused;
- an API test that the runtime loads none of the adapter.

**No app runtime gains a database, real authentication or a live provider.** The adapter runs only under the proof's settings; P11 wires the runtime.

**The run of record** is PR29's pull-request run 37383940454 on `8bbad57`, whose code is byte-identical to Stage A's code head `3b92122`. Every job passed and the gate printed `Application checks passed`. Its database job is job 112012530140. The session's earlier push run 37372546600 on `3b92122` also passed its database job, but three jobs got no runner.

- **You review one exact head:** `e8eb5d370fe41e27658e5fa30eb857f05f514be0`, the merge that integrated Stage A.
  - Its first parent, `2cb2713`, is the manager branch before the merge. Its second parent, `1a7fd9a`, is the session's head. The code head is `3b9212236127638f9cd913927b3d382f1dca8202`, and the merge's code is byte-identical to it.
  - The merge brought 50 files: 14 under `services/api/`, 30 under `proofs/postgres-ordering/`, the workflow, and Markdown.
- **Your scope is Stage A's change:** the whole of `git diff HEAD^1 HEAD`. Read it against the code as it stands at `HEAD`, because a change can break code it did not touch. P06.DB's earlier reviews covered the reference design at `ea21ac8` and `369d03c`; re-read it where the adapter or the suite's new parts depend on it. Later commits are Markdown-only records, which you read at `<RECORDS_COMMIT>`.
- **The database run is not repeated here.** You start no database. The review is offline: the code, the offline tests, and the run of record's logs.
- **What comes after this review.** Report every finding with its severity. A correction pass comes before Stage A merges for any blocking finding, and for any should-fix finding that could:
  - let a send authorization commit after a revocation that invalidates it without the suite failing;
  - let a password, the marker or a connection value reach a log, an artifact or a file outside the job's temporary directory;
  - let the job, the proof or the adapter connect to anything but its own disposable database, or let the API runtime load the adapter or connect to any database;
  - make DB06's or DB09's mark claim more than the run shows;
  - let the provider receive a channel, member or user name, image or custom field, an invite, a call, a feed or an activity, or let provider text reach a stored row, a log or a user.

  Everything else goes into the records. For each finding, say whether it falls in one of those classes.
- Nathan started you manually and will relay your report to the manager (App Manager 6). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - Keep scratch work outside the repository, or in its ignored paths (`.venv/`, `.work/`).
- **Never:**
  - dump the environment;
  - start or connect to any database, whether a local cluster, a container, or the proof's settings pointed at anything, and never set a database's comment. Never connect to Stream, HDE, Railway or any other provider;
  - run `playwright install` or `eas`;
  - run `migrate` or the proof's `facts` and `run` commands yourself. The offline tests run commands only through `tests/command_harness.py`, whose fake server opens no connection; running the tests is allowed.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*`, `PROOF_DB_*` or `STREAM_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_|STREAM_)'` prints names only. If any is present, report its name first in your report, never read or use its value, and continue.
3. The pinned toolchain is in `$HOME/.local/bin`, including Python 3.12.14. Put `$HOME/.local/bin` first on PATH in every process you run, then record `command -v python3.12` and its version. Create any virtual environment with `python3.12`.
4. Run the API's and the proof's commands in a clean process environment, as `docs/operations/local-development.md` and the proof's README show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach e8eb5d370fe41e27658e5fa30eb857f05f514be0
git rev-parse HEAD                      # must print e8eb5d370fe41e27658e5fa30eb857f05f514be0
git rev-parse HEAD^2                    # must print 1a7fd9a9caa2837a225de0969059c31969d3d50f
git merge-base --all origin/main HEAD   # expected: one line, 3afffb30205563932ebd05d5d41cca6d569663a3
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stage A'   # must print 0: this review is not yet recorded
git diff --shortstat HEAD^1 HEAD        # expected: 50 files changed, 6203 insertions(+), 179 deletions(-)
git diff --quiet 3b9212236127638f9cd913927b3d382f1dca8202 HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
git diff --quiet HEAD 8bbad57741708e4767406d54a5592d38d6f7880d -- proofs .github services scripts apps packages && echo "the run's commit carries this code"
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
git diff --name-only "$base" "$head" | grep -v '\.md$' | grep -v -E '^(services/api/|proofs/postgres-ordering/|\.github/workflows/foundation\.yml$)'
```

- **The first run** is the head against `main`. Expected: `"full": true`. The last command must print nothing: every non-Markdown change is under `services/api/`, `proofs/postgres-ordering/` or is the workflow. Anything else is code this review would not cover: stop and report it.
- **The second run** is the manager branch before the merge against `main`. Expected: `ordinary-docs-only`, so all of PR29's code is Stage A's.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`, and `services/api/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md` (revision 2): items 1 to 4, D1 to D8, the owned paths and "Documents each stage updates";
- the Stage A prompt, `docs/ephemeral/2026-10-05-p06-2-stage-a-implementation-prompt.md`: what the session was asked to do, its rules and owned paths;
- the DM-13 report, `docs/continuity/dev-manager/reviews/2026-10-05-dm-13-p06-2-brief-read.md`, and the DM-12 report;
- the P06.DB brief, `docs/planning/p06-db-disposable-postgres-proof.md`: D1 to D6, item 6 and "Carried to P06.2";
- the evidence record, `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`, section "Stage A", whole;
- the whole of `git diff HEAD^1 HEAD`, and, whole, every file it adds under `services/api/` and `proofs/postgres-ordering/`;
- the `database` job of `.github/workflows/foundation.yml`, whole.

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the evidence record's "Manager verification of Stage A" (its five points for this review) and "Stage A run of record";
- the brief's "Sessions";
- `docs/testing/p11-deferred-acceptance.md`: "Early partial evidence", with the DB06 and DB09 entries.

**The run of record's logs:** the database job 112012530140, whole, and the gate's log line.

## 3. What to review

The focus areas are in order of risk.

1. **The adapter carries the design** (`glow_chat/contact.py`; P06.DB D5; the brief's D5).
   - Every writer: one `transaction.atomic()`, accounts locked lower then higher by primary key, then the match, then the session; every check in code on the locked rows; time from `clock_timestamp()` after the locks; a missing locked row a refusal; deletion the lifecycle transition.
   - The send reads a match's pair and a session's account before its locks. Confirm both are immutable, and that nothing a check uses is read before the locks.
   - 5.4: authorize, then deduplicate. Can a retry after a revocation get the old receipt? Can two identical racing requests yield two rows, or a unique-constraint error reach the caller?
   - The brief's D5 and DM-13 4.1: the pause, restriction and consent writers take the account lock first and bump the version of the row the send checks; the send reads that state under its account locks. Is the consent purpose's "latest" well defined (`order_by('-version')`), and can two decisions share a version?
   - Activation, block, unblock, unmatch, suspension and deletion: does any path leave contact open after a revocation, or reopen it (an unblock, a resume, an acceptance)?
   - **No fault switch** (DM-13 2.1): no branch, flag or hook in the adapter changes a lock, a check or a write. The probe only signals and waits.
   - `_run` turns every database error into a result. Can it hide a failure the suite should have seen?
2. **The suite proves the adapter, not only the reference** (`adapter.py`, `evidence.py`, `oracle.py`, `planted.py`, `cases.py`, `stress.py`).
   - Does each case and race really drive the adapter's code through the shared interface, with no path that falls back to the reference?
   - The adapter writes no proof-log row: its evidence is its own `MessageSubmission`s, outbox events and consent decisions, with the session taken from the harness's call rows. Could the oracle pass when the adapter's rows are wrong, or when a call row is missing (the session says such a submission fails closed)?
   - The new rules O0, O9 and O10, and O5 narrowed (carried items 4 and 5): each correct, each covered by a control that fails without it, and none hiding a violation of the earlier rules.
   - The reference keeps its 55 forced cases and ten controls unchanged; the CX2 boundary case makes 56. Confirm `reference.py` is unchanged and the controls still fail by their declared signals.
   - Per-order counts and the seeded delay (carried item 2): could the delay change what a race measures, or hide an order?
   - The tests for R3 and R4 (carried item 3), and the session's 21 fix reversals: is any part of the change untested?
3. **The refusals before any run** (carried items 1 and 6). The used-database refusal: which rows it reads, whether a used database can slip through. The `dbshell` refusal: it relies on Django resolving the command to the installed proof app before `django.core`; confirm in Django 5.2.17 and that no other command reaches a database unchecked. Making the proof package an installed app: does it change what `migrate` or `makemigrations` sees?
4. **Delivery** (`glow_chat/delivery.py`, `events.py`, the fixture provider).
   - One provider call per event, outside any transaction, with the identifiers committed with the event; a retry reuses them; nothing creates a second channel, message or member.
   - First in, first out, a retry stays at the head: can any event overtake an earlier one of the same channel or user, across the batched lease?
   - A message authorized before a revocation committed is delivered and the members removed after it (D6); a message whose channel's members were removed is never delivered.
   - No event carries a name, image or custom field, an invite, a call, a feed or an activity. Provider errors are kept only as Glow codes.
5. **The models and migration `0003`** (D7). Additive; `0001` and `0002` byte-identical; constraints and indexes sound; `makemigrations --check` passes in the API and in the proof; the provider IDs are `secrets.token_hex(16)`, never derived from an account or logged.
6. **The token rules** (`chat_tokens.py`; D6, DM-13 5.1): one hour; refused unless the session is valid, unexpired, at the account's epoch and the account active; per-user revocation at every epoch bump.
7. **The runtime stays sealed** (D2, DM-13 2.3): the API test really fails if the runtime imports the adapter, the models or a driver; the dummy backend and the connection refusal unchanged. The API's mypy now skips `glow_persistence`'s imports (`follow_imports = "skip"`): what does that leave unchecked in `glow_chat`?
8. **The workflow and the log** (the `database` job; job 112012530140).
   - Only the `database` job changed: the `dbshell` step, the run step's name, the used-database step. The marker and the passwords are read from the job's directory, never through `$GITHUB_ENV` or a step output.
   - From the log: no password or marker (look for strings of 32 or 48 hexadecimal characters; say what each `***` is); each forced wait observed with its holder, per subject; the ten reference controls and the planted controls met their declared signals; the oracle's figures per subject; the delivery phase; the refusals; the container's removal.
9. **The records** (the session's "Stage A" section and the manager's sections at `<RECORDS_COMMIT>`; `data-model.md`; `interactions-fixtures.md`; the P11 plan's entries). Does any statement claim more than the code and the run show? Check the figures against the log.
10. **The manager's five points** in "Manager verification of Stage A": agree or not with each.

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), the start gate's and the classifications' results;
- the environment check;
- a verdict: **approve**, or **changes required**, with the findings that require them;
- every finding, numbered, with its severity (blocking, should fix, nit), its file and line, what is wrong, why it matters, a suggested fix, and whether it falls in one of the correction classes above;
- for each focus area, what you checked and what you found, including what you confirmed;
- the offline checks you ran, with their exact results;
- limits of the review, and open questions.
