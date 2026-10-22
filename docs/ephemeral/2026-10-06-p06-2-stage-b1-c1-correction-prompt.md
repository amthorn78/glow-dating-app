# P06.2 Stage B1-C1 prompt — correction pass on Stage B1's exact-head review

- **Owner:** App Manager 6. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 6 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 3, "B1's design points" (DM-15's conditions); the [Stage B1 prompt](2026-10-06-p06-2-stage-b1-implementation-prompt.md), revision 1.
  - Input: the evidence record's "Exact-head review of Stage B1", findings R1 to R5, with the manager's dispositions.
- **Where the result goes:** the session's code and tests, its section "Stage B1-C1" in the evidence record; the Foundation run on its last code commit is the run of record; the manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Opus 5.5, high.** Effort score 2.14 (confidence 0.79); rung probabilities low 0.00, medium 0.09, high 0.70, extra high 0.21, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.99 (confidence 0.99). Sent 2026-10-06T12:12:59Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed. The pass meets a DM-15 condition as written (3.5) and changes no design; it authorizes no credential, provider call or dependency.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29). An exact-head review of the corrected head follows.
- **Deletion condition:** prune after Stage B1's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session P06.2 Stage B1-C1**, a small offline pass on Stage B1 of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stage B1 (code head `cab71b9`, integrated into the manager branch at `e614d8a`) made the eight changes Stage A's reviews carried: provisioning before the channel, a reconciliation mark, the grant's transaction, activation's checks and three nits, in `services/api/glow_chat/` and the race suite in `proofs/postgres-ordering/`. Its exact-head review approved it with one should-fix finding and four nits (the evidence record, "Exact-head review of Stage B1"). R1 is a test the Dev Manager's DM-15 condition 3.5 requires and B1 did not write, so it is corrected before B1 merges; the nits ride with it.

- Nathan started you manually and will relay your report to the manager (App Manager 6). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. Each push runs the Foundation workflow on your branch; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo or log the proof database's passwords or the run's marker, in any form;
  - connect to any database other than a disposable one that you or the job start for this proof (P06.DB brief, D4). Never connect to Stream, HDE, Railway or any other provider;
  - run `playwright install` or `eas`;
  - run Django's `migrate` anywhere but against a disposable proof database, from the proof's own settings;
  - add a dependency anywhere, or import `getstream`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report to Nathan: this session must start in `Glow App - No Stream`.
3. No `PG*` or `PROOF_DB_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_)'`. If any is present, report its name first, never read or use its value, and run every proof command in a clean process environment that lacks it.
4. The pinned toolchain is in `$HOME/.local/bin`, including Python 3.12.14. Put `$HOME/.local/bin` first on PATH, then record `command -v python3.12` and its version. Create any virtual environment with `python3.12`.
5. Run the API's and the proof's commands in a clean process environment, as `docs/operations/local-development.md` and the proof's README show. Installs get the proxy and CA variables by reference, never printed.
6. **What a local database can use** (P06.DB brief, D4): record whether `docker info` succeeds (its exit status only), and `command -v initdb pg_ctl postgres pg_isready psql`.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/ proofs/ .github/ docs/architecture/ docs/operations/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage B1-C1'   # must print 0
```

If code or this pass's section has already landed on the live manager branch, this prompt is stale: stop and report (AM5-15). If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md` and `proofs/postgres-ordering/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`, "B1's design points";
- the DM-15 report, `docs/continuity/dev-manager/reviews/2026-10-06-dm-15-p06-2-stage-b-split-read.md`, item 3;
- the evidence record, `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: "Stage B1" and "Exact-head review of Stage B1", whole;
- `services/api/glow_chat/contact.py` and `delivery.py`, and the proof's `cases.py`, `adapter.py` and `delivery_phase.py`.

## 3. The work

Each item gets a test that fails without it and passes with it, or, for R5, a reversal that now fails on the comparison it names.

1. **R1, a second match for an already-provisioned account** (DM-15 3.5, as written: "An identity that already exists from an earlier match gets no second provisioning event; its earlier event precedes the new channel by `available_at`, since both writers lock that account. A test covers a second match for an already-provisioned account"). Add a case on the adapter's subject, in the database job (a delivery-phase case or an adapter case; say which and why): account A is matched with B, A's identity is provisioned (`active`); A is then matched with a new account C. Show from the database that over both activations exactly one `identity_created` exists for A, that the second activation writes provisioning for C only, and that the new channel's delivery is preceded only by C's provisioning and succeeds. Its reversal (an activation that provisions every member again) must fail the case.
2. **R2.** Drop the explicit `before_commit` signal in the grant's body (`contact.py:361`), so `_run` signals it once, as for every other writer. Show the probe fires once on the granted path.
3. **R3.** In `delivery.py`, the `contact_revoked` branches that dead-letter for a missing match, missing identities or a missing channel reference (`:293`), and the `PROVIDER_REJECTED` plans of the revocation and provisioning events (`:197`, `:217`, `:243`, `:289`, and any other, such as `:369`, that concerns a row), pass the binding's or identity's mark as their dead-letter action instead of `_nothing`, so every dead-lettered revocation marks its row (F3's rule). Where a branch has no row to mark, say so and leave it. Offline or database tests for the branches you change.
4. **R4.** In your own evidence section "Stage B1", correct the sentence in "What the exact-head review must know" that says `sequence` orders "within one `available_at` and across clock skew between writers": delete "and across clock skew between writers", and mark the edit as B1-C1's (R4). This is the only change to the existing record.
5. **R5.** Make F1 point 5's app-clock reversal fail on the issue-time comparison, not on the expiry check: a skew shorter than the cases' sessions (for example two minutes), or token cases with longer sessions. Keep the hour's skew case too if it adds coverage. Show the reversal's failure reason in your report.

**Not in C1:** anything else. `reference.py`, its cases and controls, migrations `0001` to `0003`, the harness, the workflow and every dependency file stay unchanged. A finding outside this work is reported with its class, and fixed here only if it could let a send, an activation or a grant commit after a revocation without the suite failing, or let a password, the marker or a connection value leak, or let anything connect beyond its disposable database.

**Rules:** reversals in a scratch copy outside the repository, never the checkout, with `git status` clean afterwards (DM-14 item 6); evidence from the database; no weakened check; no password or marker anywhere; no dependency change.

**Local runs** (P06.DB brief, D4): a throwaway database in your sandbox if one is available, otherwise CI; iteration, not evidence.

## 4. Checks

Report the exact commands and results.

1. `git diff --check <START_SHA> HEAD` and `git diff --name-only <START_SHA> HEAD`: only owned paths changed.
2. Classification with the trusted policy from `main`, outside the tree: `base=$(git rev-parse origin/main); d=$(mktemp -d); git show "$base:scripts/change_scope.py" > "$d/change_scope.py"; python3 -I "$d/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base`. Expected: full scope.
3. Hash-locked installs and `pip check` for the API and the proof.
4. The offline checks: the API's and the proof's tests with counts (at the start: 289 and 150), Ruff check and format, mypy, the static check with `makemigrations --check --dry-run`, the sealed-runtime test, the pin tests.
5. `reference.py`, `0001`, `0002` and `0003` unchanged against `<START_SHA>`.
6. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs), and the gate's line `Application checks passed`. Push nothing more until that run has finished (AM5-14). From the database job's log: the new case or cases with their results, the adapter's case count, the oracle's figures per subject, the delivery phase's checks, the controls, the refusals, the container's removal, and no password, marker or `***` where either would be.
7. A secret scan over your diff.

## 5. Owned paths, push and records

- **You may change:** `services/api/glow_chat/**` and `services/api/tests/**`; `proofs/postgres-ordering/**`, except its dependency files and `glow_ordering_proof/reference.py`; the evidence record: the one sentence of item 4, and a new section "Stage B1-C1" after the existing sections, which otherwise stay byte-identical.
- **Nothing else.** Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage B1-C1":** the prompt's revision and start SHA, your head, your branch and the run of record; R1 to R5, each done (`file:line` and its test or reversal) or left (the reason); the run's results; local runs, marked "iteration, not evidence"; every check with its exact results; deviations and limits; what the exact-head review must know.

## 6. Report

Your final message is the report Nathan relays: the prompt revision (revision 1, from `<START_SHA>`); the environment check; your branch, head SHA and changed paths; R1 to R5, done or left; every check with its exact results, and the run of record's details; deviations, findings outside the work with their class, and limits.
