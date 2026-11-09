# DM-49 — SV1's runs lost to GitHub's Actions incident, and whether C2's delta review goes now

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 10, relayed by Nathan (OD-25).
- **Read at:** `cae9cea8a6c15945e718f593857e4d5bfa8c515b` of `claude/magical-wozniak-yfmmx2`, with C2's code head `6da8061`. The manager branch was still at `cae9cea` at 19:18 UTC (`git ls-remote`).
- **Written:** 9 November 2026, finished at 19:21 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only; none of the six names is present.
  - I called no provider, database, HDE, Railway or TypeSafe service, ran no application test, and wrote only this file.
  - I read GitHub's runs, jobs and job logs, and PR42's reviews and comments, with GitHub's tools, read-only. I re-ran nothing.
  - I did not read GitHub's status page: this consultation names no page I may read, and nothing below rests on it.
  - Notion was read, not edited.

## 1. What I read

- **The consultation** at `cae9cea`, and the record's lines on the lost runs (at `38d48e2` and `cae9cea`).
- **C2's delta review prompt,** revision 1, whole. It is unchanged from `38d48e2` to `cae9cea`.
- **The manager workflow's rules:** OD-21's quotation, "No acceptance on a rerun alone", "Push runs as evidence" and "Actions re-runs".
- **The workflow at `cae9cea`:** each job's `needs` and `if`, and the gate.
- **Git:** every path that changed from `6da8061` to `cae9cea`, with its mode; the merge base with `main`; the start gate's checks.
- **GitHub's records:**
  - the job lists of runs 42669825647, 42671723917, 42673988451, 42673999110 and 42676003277;
  - the gate's log in 42669825647, 42673988451 and 42676003277;
  - in 42676003277, the classifier's log and the Database proof job's identity lines;
  - PR42's reviews, and Codex's summary comment.
- **Notion,** read-only (section 5).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. The lost runs | **(a) approved, with one update and words for the record (1.1).** The diagnosis holds on GitHub's own records. No step failed. The missing jobs differ from run to run. The gate's input gave the missing jobs a result, `abandoned`, that GitHub does not document and the workflow cannot set. The workflow file and the code are byte-identical across the runs that passed. **The update:** what (a) waits for has already happened. `cae9cea`'s own push started PR run 42676003277, and it passed all eight jobs, with `Application checks passed` and the identity suite 49 of 49. No re-run, no empty commit, no repair item, nothing for Nathan |
| 2. C2's delta review | **Yes: revision 1 may go to Nathan now, unchanged.** Its start gate holds at the live head. Codex has read `cae9cea`, which holds it, with no finding. The PR run on PR42's head is complete and green. (b) adds nothing, since its condition is already met |
| Notion | **Matches** `cae9cea`, apart from one place one commit behind (section 5). DM-48's Work Register nit is fixed |

**How to apply:** 1.1 changes text in given words; line breaks may move.

## 3. Item 1 — The lost runs

**What GitHub's records show** (read at about 19:12 to 19:17 UTC):

| Run | Head, event, times (UTC) | What GitHub recorded |
|---|---|---|
| 42669825647 | `6da8061`, push, C2's session branch, 17:58:49 to 18:07:05 | **All eight jobs `success`.** The gate's log reads `Application checks passed` (18:06:46). One oddity: the gate job is still listed `in_progress`, although its conclusion is `success` and every step had completed |
| 42671723917 | `080c9a9`, push, the same branch, 18:10:51 to 18:13:25 | **`failure`, with no job at all** |
| 42673988451 | `38d48e2`, push, the manager branch, 18:26:02 to 18:35:43 | **Five jobs listed.** API checks, API mobile smoke, API artifact checks and Database proof checks are `success`; the gate is `failure`. The gate's input gives the classifier, Mobile checks and Stream proof checks as `abandoned`, with no outputs, so the gate stopped at `Change classification failed` |
| 42673999110 | `38d48e2`, pull request, 18:26:07 to 18:29:37 | **Four jobs listed, all `success`:** API checks, API mobile smoke, Stream proof checks, API artifact checks. No classifier, Mobile checks, Database proof checks or gate. `failure` with no failed job |
| 42676003277 | `cae9cea`, pull request, 18:39:56 to 18:47:07 | **All eight jobs `success`.** The classifier, using `main`'s policy, says `"full": true` (`behavior-or-empty`). The gate's log reads `Application checks passed`. The identity suite reads `cases: 49/49 passed`, its scan clean, `IDENTITY VERDICT: PASS`; `ratelimit.password_change` passed (the sixth request, at 120 to 121 seconds, refused with 429) |

**Why the cause is GitHub's, not this work:**
- **The workflow file did not change.** From `6da8061` to `cae9cea` only regular Markdown files changed, with no mode change and no `.claude/` path. The same workflow file ran all eight jobs at 17:58 and again at 18:39, so no error in it explains the run with no job.
- **No step failed** in any of the three runs, and the missing jobs differ from run to run.
- **`abandoned` comes from GitHub, not from the workflow.** GitHub sets the result of a needed job; its documented values are `success`, `failure`, `cancelled` and `skipped`. The jobs given as `abandoned` are exactly the ones missing from the job list.
- **GitHub's records were unreliable from about 18:06:** the run of record's gate job is still listed `in_progress` after it finished.
- **The gate did its job.** It failed closed when the classifier's result was not `success`. Nothing in it needs to change.

**One reading to avoid** (the consultation does not make it):
- The application jobs that ran in 42673988451 do not show that the classifier ran.
- By design they also run when the classifier does not succeed: each job's condition is `needs.scope.result != 'success' || needs.scope.outputs.full != 'false'` (`foundation.yml:53`, and the same in each application job).
- So the record should not say that the classifier ran.

**The status page:** its times are the manager's reading at 18:37 UTC, not mine. Run 42671723917 began at 18:10:51, before the incident's posted start at 18:12:37. Since GitHub's own records were already inconsistent at 18:06, that fits a problem that began before GitHub posted it.

**What (a) means now:**
- **The record** states the three lost runs with this explanation (1.1), and names PR run 42676003277 as the complete PR run on `cae9cea`.
- **The CI evidence for the code** is C2's run of record, 42669825647, and now PR run 42676003277 on the PR head too.
- **Nothing is re-run, no empty commit is pushed, and nothing is asked of Nathan.**
- **No repair item.** OD-21 asks for a focused repair item when a failure is unrelated to the work, but nothing in the repository failed. OD-21's prerequisite, reliable CI before acceptance, is step 7's rule: a complete PR run on the final head.
- **The merge** needs a PR run on the final head with all eight jobs passed and `Application checks passed` (step 7), whatever GitHub's status page says.
- **If a later run loses jobs,** it is recorded in the same way, and the next real records push gives the next PR run.

**1.1 — The record's words.** Replace "The three lost runs go to the Dev Manager as DM-49 (OD-58; OD-21), and C2's delta review prompt waits for its answer. Nothing is re-run." with:

> **The explanation, reviewed** (DM-49; OD-21): GitHub lost these jobs; nothing in the repository failed. No step failed in any of the three runs, and the jobs missing differ from run to run. The gate's input gave the missing jobs as `abandoned`, a result GitHub does not document and the workflow cannot set, and the gate failed closed, as designed. The application jobs that ran do not show that the classifier ran: they also run when it does not succeed. The workflow file and every other non-Markdown path are byte-identical from `6da8061` to `cae9cea`. With them, push run 42669825647 on `6da8061` and PR run 42676003277 on `cae9cea` each ran all eight jobs, with `Application checks passed` and the identity suite 49 of 49. GitHub's records were unreliable from about 18:06 UTC: the run of record's gate job is still listed `in_progress`, though its step succeeded and its log reads `Application checks passed`. Nothing was re-run, no empty commit was pushed, and no repair item is needed: the merge rests on a complete PR run on the final head (step 7).

## 4. Item 2 — C2's delta review prompt

**Revision 1 may go to Nathan now, unchanged.**

- **Its start gate holds at the live head, `cae9cea`:**
  - `main` is still `da92f1f`, and the single merge base is `8d2de72`, for both `38d48e2` and `cae9cea`;
  - `38d48e2` is on the live branch;
  - the non-Markdown paths at `38d48e2` and at `cae9cea` are identical to `6da8061`'s;
  - the record holds no heading that starts "Delta review of correction C2" (the count is 0);
  - the classification is full (PR run 42676003277's classifier, against `main`).
- **Codex has read a commit that holds the prompt.** Its summary comment on PR42 shows a completed code review of `cae9cea`, with no findings (18:42 UTC). The comment shows only the latest review, so I could not see the read of `38d48e2` itself. `cae9cea` holds the same prompt and the same code.
- **Its runs:**
  - "The PR run on PR42's head, once it has finished" is today PR run 42676003277, complete and green.
  - DM-49's disposition push will start another run, and the prompt's "once it has finished" already covers waiting for it.
- **The lost runs make nothing in revision 1 false.**
  - Its focus 8 already covers run 42671723917.
  - The reviewer reads the record at `38d48e2`, where the two later runs are not yet recorded. If the reviewer notices them on GitHub, the live record explains them, and they fall in no correction class.
- **(b) adds nothing:** its condition, a PR run on a new head with all eight jobs passed, is met by 42676003277.
- **Two things would make the prompt stale and need a revision** (notes, not conditions):
  - a heading in the record that starts "Delta review of correction C2" before the review reports, since the start gate counts it;
  - `main` moving before the review starts, since the start gate checks the merge base.

**The note on empty commits:** agreed. The rule is the manager workflow's ("Actions re-runs": "Pushing an empty commit to trigger CI is not allowed"), not the workflow file's.

## 5. Notion (read-only, at about 19:15 UTC; the pages as of 18:40 UTC)

What I read: the parts named here, not the whole of either large page.

- **Implementation Control:**
  - **The status** says the page was last matched at `cae9cea`, with its message. That matches.
  - **The Branches bullet** lists six branches, from an 18:25 UTC listing. Every hash matches my `git ls-remote` at 19:18 UTC:
    - `main` (`da92f1f`);
    - `claude/dev-manager` (`c6bce37`);
    - `claude/hopeful-cerf-kc91xx` (`157c1f6`);
    - `claude/stoic-franklin-ief71e` (`96dc3e2`);
    - `claude/trusting-goldberg-e4ogat` (`080c9a9`);
    - the manager branch, except as below.
  - **One stale value, a nit:** the bullet gives the manager branch as "`38d48e2` at this sync", while the status names `cae9cea`. This is the same one-commit lag as DM-48's nit.
- **The Dev Manager page:** both rows match the review log:
  - DM-48's row: the report pinned at `2f577f8`, answered at `c6bce37`, merged at `5a576dd`, every condition accepted;
  - DM-49's row: the consultation at `cae9cea`, "Awaited".
- **The Work Register:** SV1 is In progress, and its Next Action describes DM-49 as the consultation does. Its Evidence link is now pinned at `cae9cea`, so DM-48's nit is fixed.
- The repository wins (OD-27).

## 6. Where each item goes

| Item | Goes to |
|---|---|
| 1.1 | The SV1 record, in the lines on the lost runs, which also name PR run 42676003277 |
| Item 2 | C2's delta review prompt, revision 1, given to Nathan unchanged |
| The merge | Before it: a complete PR run on the final head (step 7), and DM-45 14.1's pre-merge read |

Status: complete
