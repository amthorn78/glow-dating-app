# DM-03 — Governing Markdown read, dispositions and the revised I1 review prompt

- **Consultation:** DM-03, from App Manager 3. It arrived as a scheduled message at 09:32 UTC on 25 September 2026.
- **Reviewer:** Dev Manager 1, branch `claude/dev-manager`.
- **Commit read:** `fa4dc5f78e80bd9994796bfc41d07a79c90d0991`, which was the head of `claude/stoic-carson-66gdig` when I fetched it. It builds on my `0f55891` through `c893022`. I compared it with `68b4ab9`, the manager head before the batch.

## 1. What I read and ran

**Commands:**

| Command | Result |
|---|---|
| `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done` | Printed nothing |
| `git fetch origin claude/stoic-carson-66gdig main`; `git rev-parse origin/claude/stoic-carson-66gdig` | `fa4dc5f78e80bd9994796bfc41d07a79c90d0991` |
| `git log --oneline 68b4ab9..fa4dc5f` | `fa4dc5f`, `c893022`, `0f55891` |
| `git merge-base --is-ancestor 0f55891 fa4dc5f` | Yes |
| `git diff 0f55891 fa4dc5f -- docs/continuity/dev-manager/reviews/` | Empty: my DM-01 and DM-02 reports arrived unchanged |
| The trusted policy from `origin/main` (`git show $base:scripts/change_scope.py` into a temporary directory), then `python3 -I … --base 9ff600fe… --head fa4dc5f…` | `{"full": false, "reason": "ordinary-docs-only", …}`: everything after I1's code head is Markdown |
| The same policy, `--base $(git rev-parse origin/main) --head fa4dc5f… --merge-base` | `{"full": true, "reason": "behavior-or-empty", …}`: PR26 as a whole is full scope, as expected |
| `git show fa4dc5f:docs/continuity/current-handoff.md \| wc -c` | 4262 bytes, under the 5 KB target |
| `git show 9ff600fe…:proofs/stream-chat/glow_stream_proof/cli.py` and `…/proof_run.py` | Read: `cmd_run`, `cmd_verify_clean`, `cmd_cleanup`, `ProofRun.preflight`, `run_matrix` and `_proc_member_custom`, to judge the live actions the prompt authorizes |

**Read completely at `fa4dc5f`:**

- the item-1 diff (`AGENTS.md`, PF00, PF01, the manager workflow, the charter and the CI policy);
- the review log;
- the I1 review prompt, revision 2;
- ADR 0003 and the owner-direction register;
- the current handoff;
- the diffs of `docs/README.md`, `docs/ephemeral/README.md`, the Claude handoff, `docs/operations/local-development.md`, the mistakes log and the P06.1 brief;
- the rename diffs of both start prompts.

I did not read the archived handoff `docs/continuity/history/m02-p06-1-handoff.md` line by line. I made no provider, database, HDE or Railway call, and I did not run the review prompt.

## 2. Summary verdict

The batch applies DM-01 and DM-02 faithfully, and it measurably reduces duplication.

- **Governing changes:** they say what the dispositions say. One is written as in force while its disposition says it awaits Nathan (G1).
- **The revised I1 review prompt:** safe and sufficient to confirm or refute S15. Before Nathan runs it, it needs two small additions to its close-out: a configuration re-check and the Stream system user.
- **One real inconsistency:** the brief both grants and excludes `.github/`. Fix it before the I2b prompt is written.

## 3. Findings

### Governing Markdown (item 1)

**G1 — The Dev Manager read is written as in force, but its disposition says "pending Nathan" — *before PR26 merges***

- **Evidence:**
  - `AGENTS.md` ("Code Review Rules", first bullet), the CI policy ("A Dev Manager read for governing Markdown"), the charter ("Read before it takes effect") and workflow steps 3 and 7 all state the rule without qualification.
  - The review log disposes of P1 as "Accepted, pending Nathan's answer to DM-01 question 2".
- **Assessment:** the rule has a basis in Nathan's direction (OD-15: *"incorporate the Dev Manager into the workflow wherever independent review or approval would materially reduce project risk"*), so adopting it is within the manager's remit. The governing texts and the disposition must still agree.
- **Recommendation:** choose one.
  - **(a)** Cite OD-15 as the authority in the charter's "Read before it takes effect", and record P1 as accepted, with DM-01 question 2 asking Nathan to confirm or withdraw it.
  - **(b)** Mark the rule "pending Nathan's confirmation" in each place it appears.

  I recommend (a). The rule costs little, and it is already in use (this read).

**G2 — The read is not tied to a commit — *before PR26 merges***

- **Evidence:** "the Dev Manager reads it before its PR merges" (`AGENTS.md`, the charter). Nothing says which commit was read, or what happens when governing Markdown changes after the read. Applying this report will change governing files again.
- **Risk:** a read of `fa4dc5f` could be taken as covering governing text written later.
- **Recommendation:**
  - The review log's disposition names the commit the Dev Manager read.
  - Governing changes after that commit need another read before the merge.
  - **The exception:** changes that only apply a Dev Manager finding's own text or instruction. The manager lists those in the disposition, and the next consultation or close-out read confirms them.

  This avoids a loop after every consultation.

**G3 — PF01 §7 lacks the interim safeguard ADR 0003 has — *soon***

- **Evidence:** ADR 0003, decision 4: *"Until Nathan confirms, no session hides a legally required disclosure or treats a mandated system screen as a defect."* PF01 §7's "Product presentation" lists the carve-outs as proposed but omits that sentence. PF01 is what sessions read first.
- **Recommendation:** add the sentence to PF01 §7's "Carve-outs" bullet.

**G4 — Only the display rule is conditional, not Nathan's principle — *soon***

- **Evidence:**
  - ADR 0003's status reads "Accepted by Nathan. Conditional on the exact-head review … confirming finding S15 live."
  - Register row OD-14 says "In force; conditional on the I1 review confirming S15".
  - PF01 §7 correctly states the principle without that condition.
- **Risk:** a reader could conclude that "nothing outside Glow" lapses if the review refutes S15. Only the choice of the display rule, as S15's answer, depends on the review. Nathan's principle stands regardless.
- **Recommendation:** split the wording in the ADR's status and in OD-14. The display rule, as S15's answer, is conditional. The principle is in force, with carve-outs pending.

**Checked with no finding:**

- PF00 1.8 and PF01 1.9 remove status from the canon, as P3 asked, and change no authority, scope or HDE boundary.
- The charter's relay steps 3 and 4, its continuity paragraph and its meaning of `approved` match my item-4 conditions.
- The workflow's new lines (P2 batching, P4, P6 (c) and (d), P7 checklist, P8) match the dispositions.
- **New procedural rules** go slightly beyond my findings but within the manager's workflow discretion (OD-09):
  - the "Writing to Notion" checklist (its `$` escape is not tied to a logged mistake);
  - the CI policy's "Dependency drift" line;
  - "no conditional level commitments".

  None adds an owner-level rule.

### Dispositions (item 2)

**D1 — The dispositions reflect my findings faithfully — *no action***

Every finding and condition has a disposition. Each referral matches a question I asked. The two changes and the refinement:

- **P2, batching instead of a records branch: accepted.**
  - The constraint is real: a cloud session pushes only its own branch.
  - An alternative I considered is opening the code PR from the implementer's branch and keeping the manager branch as a records PR. It fails once correction sessions push new branches.
  - Batching plus "name the code head" plus "state the prompt revision received" achieves P2's purpose. It still costs one full PR run per batch. That is acceptable.
- **P8, a summary row for every mistake: accepted.** It is faithful to Nathan's *"track your mistakes"* (OD-11). My wording ("one summary row") did not intend to drop rows.
- **B4, the backup refinement: accepted as a correction to my DM-02.**
  - I did not verify it either (Limits).
  - If Railway backs up volumes, as the manager says, then a separate logical database gives separate ownership, grants, logical dumps (`pg_dump`, `pg_restore`) and drops. It does **not** separate platform restores.
  - DB13 requires restoring an actual backup. If restore independence matters, only a separate PostgreSQL service in the same project gives it.
  - So Nathan's DM-02 question 3 now has a clearer trade-off:
    - same database: least isolation;
    - separate logical database: logical isolation, shared platform restore;
    - separate service: full restore separation, one more service to run.
  - I no longer recommend option 2 over option 3 outright. If restore independence (DB13) is a requirement, choose option 3; otherwise option 2 is the minimum.
  - Please relay this refinement with the question. It is not a new question.
- **P1:** see G1.

### The revised I1 review prompt (item 3)

I checked the prompt against the harness code at `9ff600f`, which is what the reviewer will run.

**Safeguards already in place:**

- `ProofRun.preflight` re-verifies the whole configuration and refuses to start (`RunStopped`, with no cleanup) if:
  - any user is present that has neither the run prefix nor the dashboard administrator's role and flag;
  - any channel exists;
  - the configuration differs.
- `cmd_run` sets `cleanup_needed` only after preflight passes, and cleans up on any exception except a stop that says "stopping at once".
- `_proc_member_custom` changes only a channel-level `config_overrides` on the run's own channel AB, and clears it in a `finally`. AB is deleted at cleanup either way.
- `--only S15` limits the matrix to S15. The reconnect check and the four-user, two-channel setup always run, so two runs use at most 8 users and 4 channels, well inside the 20 and 30 guardrails.
- The prompt:
  - requires a clean `verify-clean` and an empty dry-run `configure` before any run;
  - forbids `configure --apply` and `restore --apply`;
  - requires one checkout, one command at a time;
  - stops on any charge signal;
  - asks for a secret scan of the output.

**R1 — Nothing re-checks the configuration after the runs — *before Nathan runs the prompt***

- **Evidence:**
  - The prompt ends with `verify-clean` only (section 4, "Never" bullet). `verify-clean` checks users and channels, not configuration.
  - Optional run 2 may choose any cases. Some cases change application- or type-level settings temporarily: G1 toggles `guest_user_creation_disabled`, and S10 and S12 toggle type features.
  - If the process is killed mid-case, those `finally` blocks never run.
- **Risk:** a setting could be left relaxed, for example guest creation enabled, while `verify-clean` reports clean. I2a's preflight would then stop, or worse, run on a configuration nobody recorded.
- **Recommendation:** add to section 4: "After the last run, run `verify-clean` **and** the dry-run `configure` again. Report both outputs. If `configure` reports any difference, do not fix it: report it, and the manager decides."

  Optionally, also limit run 2 to cases that change no application- or type-level setting. With R1 in place, that is not required.

**R2 — `cleanup --apply` leaves Stream's system user behind — *before Nathan runs the prompt***

- **Evidence:**
  - `cmd_cleanup` hard-deletes users and channels whose IDs contain `p061i1-`. It does not remove the `deleted-user-1729640-…` user that Stream creates on a hard delete; only `ProofRun.cleanup` does.
  - The prompt allows `cleanup --apply` for leftovers. `preflight` then treats the system user as "a user this proof did not create" and refuses the next run, which is I2a's.
- **Risk:** after a manual cleanup, the application is not clean, and the reviewer has no instruction for the one user it may not touch by its own reading of the prompt.
- **Recommendation:** add to section 4, choosing one:
  - "If a `deleted-user-1729640-…` user remains after `cleanup --apply`, report it and leave it; the manager arranges its removal."
  - Or explicitly permit deleting exactly that user ID with the harness's API, and require reporting it.

  I prefer the first. It keeps the reviewer's writes to what the prompt names.

**R3 — Code running live for the first time — *consider***

- **Evidence:** the fixes after I1's final run have not been exercised live (the evidence record, "Deviations"): prefix matching anywhere in an ID, the guest filters and the R9 control. The review's runs will be the first to exercise them.
- **Recommendation:** one line in section 4: "These runs are the first live use of the fixes listed in the evidence record's 'Deviations'. Report whether cleanup and verify-clean behaved as intended."

**Sufficiency for S15:** yes.

- The procedure writes a unique marker, reads B's three views (channel query, members query and events) in the locked configuration, and repeats the write with `read-channel-members` granted on AB as the positive control.
- The prompt also asks for a documentation and SDK check of the three `member_custom_on_*` settings and of any closing configuration.
- That confirms or refutes the finding as stated.
- What happens after revocation or removal is I2a's, as the prompt says.

**Other checks on the prompt:**

- Naming the code head `9ff600f`, reading the records at `<RECORDS_COMMIT>`, and the second classification run are sound. At `fa4dc5f` the second run prints `ordinary-docs-only`, as I verified.
- The `<RECORDS_COMMIT>` placeholder must be filled with the commit that holds the **final** prompt text, after R1 and R2. Section 6 asks the reviewer to report that commit, so any divergence becomes visible.
- The TypeSafe header shows a reading taken for revision 1. That is harmless, and consistent with P8.
- **I found no path** by which the prompt lets a live action exceed the brief's guardrails, or touch data the run did not create.
  - Preflight refuses foreign users and channels, and the prompt forbids configuration writes.
  - Both cleanup paths delete only IDs that contain `p061i1-`.
  - The residual risks are the leftovers in R1 and R2, not overreach.

### Everything else in the batch (item 4)

**E1 — The brief grants `.github/` to I2b and also excludes it — *before the I2b prompt is written***

- **Evidence:** in the P06.1 brief's "Brief — P06.1", "Owned paths" now gives I2b "one new job … in `.github/workflows/foundation.yml`". "Exclusions" still lists `.github/`.
- **Recommendation:** change "Exclusions" to "`.github/`, except the one Foundation job P06.1-I2b owns".

**E2 — Local development cites the frozen handoff as the full inventory — *soon***

- **Evidence:** `docs/operations/local-development.md` says "The full inventory is in [the handoff](../continuity/claude-code-handoff.md#environment-variable-inventory)". That packet is now frozen and "no longer kept current".
- **Recommendation:** point it to `docs/operations/environment-inventory.md`, or move the variable inventory there. Either way, one living home.

**E3 — The Dev Manager start prompt is specific to DM-01 and DM-02 — *consider***

- **Evidence:** `docs/planning/start-prompts/dev-manager.md` still holds DM-01 and DM-02 as its consultation, a reading list written "for these reviews", and the fixed branch `claude/stoic-carson-66gdig`.
- **Recommendation:** before it is next used, turn it into a generic start procedure with a `<CONSULTATION>` block and a `<MANAGER_BRANCH>` placeholder. The first session's text stays available at `3888e8f`, as its header already says.

**E4 — Stale role names in the canon — *consider***

- **Evidence:**
  - PF01's "Execution model" line still says "App Planner 1 prepares the transition".
  - PF00's "Current session authority" still says "App Planner 1 prepares the migration".
  - These predate this batch.
- **Recommendation:** fold the fix into the next canon revision. Describe App Planner 1 and App Builder 1 as historical roles, as OD-01 already does.

**E5 — ADR 0003 names consequences for later phases — *no action; noted***

ADR 0003 states that P06.3's notification content "comes only from Glow's server path, never from Stream's push". That follows from Nathan's principle and from the I1 configuration, where push is off. It binds P06.3's design. That is appropriate for an ADR, and P06.3's brief should cite it.

**Checked with no finding:**

- The owner-direction register: 15 rows, append-only rules, quotes marked as exact or "Recorded". It matches the directions I know of from DM-01 and DM-02's reading.
- The slimmed handoff: 4.3 KB, routing only, with a waiting checkpoint that has a fallback time.
- The `docs/README.md` homes table.
- The Claude handoff, frozen with a pointer.
- The moved start prompts, with links fixed. The next-manager reading list is shorter and still covers `AGENTS.md`'s required reading, as AM2-09 requires.
- The brief's I2a, I2b, economics and restore changes, which match DM-02 B2.
- The mistakes-log rules, AM3-04's checklist note and AM3-05, which is accurate to the history I observed in DM-01.

## 4. Verdicts

| # | Item | Verdict | Conditions |
|---|---|---|---|
| 1 | Governing Markdown at `fa4dc5f` (`AGENTS.md`, PF01 1.9, PF00 1.8, the manager workflow, the charter, the CI policy) | **approved with conditions** | G1 and G2 before PR26 merges; G3 and G4 soon. The changes say what the dispositions say, and they are consistent with the governing set except for G1. No owner-level rule is added beyond OD-15's incorporation direction |
| 2 | The dispositions of DM-01 and DM-02 | **approved** | Faithful. P2 and P8 as changed are sound. The B4 refinement is accepted as a correction to my DM-02 and should go to Nathan with DM-02 question 3 (D1) |
| 3 | The revised I1 review prompt (revision 2) | **approved with conditions** | R1 (re-check the configuration after the runs; report differences, don't fix them) and R2 (the Stream system user after a manual cleanup) before Nathan runs it. R3 optional. Fill `<RECORDS_COMMIT>` with the commit holding the final text. Edits that only add R1 to R3's wording need no further read |
| 4 | ADR 0003, the register, the handoffs, `docs/README.md`, the start prompts, the brief, the mistakes log | **approved with conditions** | E1 before the I2b prompt; E2 soon; E3 and E4 when next touched |

## 5. New questions for Nathan

None. The B4 refinement sharpens DM-02 question 3; it is not a new question.

## 6. Documentation to update

- `AGENTS.md`, the charter, the CI policy and the workflow: G1 (cite OD-15, or mark pending) and G2 (the read is tied to a commit).
- `docs/continuity/dev-manager/README.md`: the commit each governing read covered (G2), and DM-03's dispositions.
- PF01 §7, the "Carve-outs" bullet: the interim sentence (G3). The next PF01 and PF00 revision also fixes the historical role names (E4).
- ADR 0003's status line and register row OD-14: split the conditional display rule from the principle (G4).
- `docs/ephemeral/2026-09-25-p06-1-i1-review-prompt.md`, section 4: R1, R2 and, optionally, R3.
- `docs/planning/p06-1-chat-provider-proof.md`, "Exclusions" (E1).
- `docs/operations/local-development.md`: the inventory link (E2).
- `docs/planning/start-prompts/dev-manager.md`: make it generic before its next use (E3).

## 7. Limits

- **Railway backups:** I did not check Railway's current backup documentation. Consulting Railway is outside my rules for this consultation, so D1 rests on the manager's statement.
- **Live behavior:** I did not run the harness or the review prompt. My judgement of its live safety comes from reading the code at `9ff600f`, not from observing a run.
- **What I did not read:** the archived handoff (`docs/continuity/history/m02-p06-1-handoff.md`) in full, or Notion.
- **Pending with Nathan:** I did not repeat or re-open the ten questions already with him.

Status: complete
