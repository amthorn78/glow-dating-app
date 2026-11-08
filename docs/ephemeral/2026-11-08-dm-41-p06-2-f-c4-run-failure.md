# DM-41 consultation — P06.2-F: correction C4's failed run, under OD-21 and OD-58

- **Owner:** App Manager 9, written at Nathan's direction (OD-58). Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4"), which Dev Manager 3 created at his direction (OD-59; its [handover](../continuity/dev-manager/reviews/2026-11-08-dev-manager-3-handover.md), `a2b985b`). **App Manager 10 receives the answer** (OD-58).
- **Revision 1, 8 November 2026.**
- **Why:**
  - **The failure:** correction C4's push run failed in two jobs that C4's change does not touch. Under OD-21 the failure belongs to the current item, and it has to be investigated, not settled by a re-run.
  - **The manager's error:** App Manager 9 asked Nathan to re-run the failed jobs. Nathan rejected that: *"asking me to do github actions is incorrect"* (OD-58). He directed this consultation, the error log (AM9-10) and a new manager to receive the answer.
  - **The question:** how the item proceeds is a process and CI decision for you first (OD-32).
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 10's disposition in the [review log](../continuity/dev-manager/README.md), "DM-41";
  - the P06.2-F record and brief;
  - the next prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** P06.2-F stays unmerged, and no prompt is written. App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-41's disposition and PR40's merge receipt is recorded.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-41 — P06.2-F: correction C4's failed run, under OD-21 and OD-58.** From App Manager 9, relayed by Nathan to Dev Manager 4, as your first consultation. **App Manager 10 receives your answer** (OD-58). This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. You may run the mobile unit tests in a clean process environment in a scratch copy outside the checkout.

**Where it stands.**
- **Correction C4** stopped under its stop rule. It ran from prompt revision 1 at `0a63219`, on branch `claude/upbeat-mccarthy-499h9k`, with code head `691dfba`.
  - **The code:** it carries DM-40 section 4.2's words, with one narrowing ("Another expression" for "Any other expression") and two punctuation changes, plus the new first render test's name.
  - **Verified:** the manager confirmed that only that one non-comment line changed. The parse trees without comments differ only in the test name.
  - **The record:** C4's own "Correction C4" section was drafted in the session's own files and not pushed. Nathan has since archived that session (by 09:07 UTC, by the session list), so the draft may not be recoverable. The manager's section, "Correction C4: the stop, and the manager's verification", holds the code head, the run, the failed jobs and the verification.
- **Its push run, 42464917902** (the record, "Correction C4: the stop, and the manager's verification"): five jobs passed. Two jobs failed, and so did the gate:
  - **Database proof checks:** `actions/setup-python` failed with three `504` responses from github.com while it downloaded Python 3.12.14. No job step ran.
  - **Mobile checks:** the unit tests passed (650 of 650), as did `check:expo` and `export:development`. The rendered suite gave `1 failed, 96 passed (5.2m)`, with no retries configured.
    - **The failing test:** `profile-preferences.spec.ts:321`. `screen-account` was not visible at `:342`, and no screen was visible at all.
    - **The sequence:** the test clicks `logout` at `:339`, then calls `page.goBack()` at once.
    - **The manager's unproven reading:** Router 58's deferred navigation, the hazard M06 fixed at this test's first `logout` (`:329`).
    - **Not P06.2-F's code:** P06.2-F does not touch this spec, logout or the onboarding routes.
    - **Unknown:** whether an empty screen after back-navigation can also reach a member.
- **What the manager did wrong** (AM9-10; OD-58):
  - it asked Nathan to re-run the failed jobs and posted that request on PR40, now marked withdrawn;
  - it followed the manager workflow's "Actions re-runs" line, which said to ask him. That line is now replaced (item 6).
- **Constraints:**
  - **OD-21:** a passing re-run alone resolves nothing. A failure that prevents this work from being verified is fixed as part of the current item.
  - **OD-58:** Nathan performs no GitHub operation.
  - **The manager's integration** cannot re-run jobs.
  - **No empty commits:** pushing one to trigger CI is not allowed.
  - **OD-57:** a CLI environment can install the pinned Chromium and run the rendered suite, when a prompt authorizes it.

**Read, at `<RECORDS_COMMIT>`:**
- the record's "Correction C4: the stop, and the manager's verification", and the M06 record's "The test changes" (`docs/testing/evidence/2026-11-01-m06-sdk-58-upgrade.md`);
- `apps/mobile/rendered/profile-preferences.spec.ts`, lines 321 to 345;
- the manager workflow's OD-21 bullet and its "Actions re-runs" line, with `git diff 0a63219 <RECORDS_COMMIT> -- docs/planning/manager-workflow.md`;
- OD-58's row in `docs/continuity/owner-directions.md`, and AM9-10 in the mistakes log;
- DM-40's report, section 5 (C4's review), and Dev Manager 3's handover (`a2b985b`).

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan.

1. **The rendered failure under OD-21.** The options:
   - **(a) A repair pass in P06.2-F (the manager's recommendation):**
     - **the session:** an implementation session in a CLI environment (OD-57), starting from C4's code head `691dfba`;
     - **its diagnosis:** it reproduces the failure with the pinned Chromium (for example `--repeat-each`), and says whether the empty screen is a test-ordering race or something a member could reach;
     - **its fix, if a race:** the test waits for `screen-account` after the second `logout`, before `page.goBack()`, in M06's pattern, with no assertion removed or loosened, and the same measurement shows the fix holds;
     - **its fix, if the app can show no screen:** it stops and reports, because that is a runtime change;
     - **why:** its push run, on a head that holds C4's code, is the run of record for both.
   - **(b) A separate focused repair item** (OD-21's "unrelated" branch), with P06.2-F's acceptance waiting on it.
   - **(c) A recorded explanation without a fix:** OD-21 does not allow it while the failure blocks this work's verification.

   Which, and on what conditions? If (a), does the prompt need your read before it runs? It authorizes a browser install, and `--with-deps` installs operating-system packages with root on Linux (DM-40 section 7's standing note).
2. **The `504`.** The manager proposes a recorded explanation, with no fix: GitHub's download endpoint failed before any job step, and no repository code was involved. Agreed, or does a repeat need a fix (for example, caching the interpreter)?
3. **Verifying C4's code without a re-run.** The options:
   - **(a)** the repair pass's push run, on a head that holds C4's code (with 1(a));
   - **(b)** the manager integrates C4 into the manager branch now, and the PR run on PR40's head, which compares from the merge base and runs every job, verifies its code. This integrates a head before its own run has passed.
   - **(c)** another option you name.

   Which?
4. **C4's record section.** C4's session is archived, and its own section was never pushed. The options:
   - **(a) the manager's section stands as C4's record** (the manager's proposal): it holds the code head, the run recorded as failed, the stop and the verification; the repair pass's own section cites the run that passes on C4's code;
   - **(b) the repair pass also appends a "Correction C4" section** in the implementer's form, from the pushed code and the run's logs;
   - **(c) another option you name.**

   Which?
5. **The review.** DM-40 3.1 to 3.4 bound C4's delta re-review to its changed items. The manager proposes one bounded review that also covers the repair pass:
   - the diagnosis is sound;
   - the wait loosens no assertion;
   - nothing outside the spec changes.

   A runtime change found by the diagnosis would need its own full review. Agreed?
6. **The workflow's "Actions re-runs" line, a governing text read before PR40 merges.** It now says the manager never asks Nathan to perform a GitHub operation, a re-run included (OD-58). When a failure seems to call for a re-run, the manager takes it to the Dev Manager first (OD-32), with options that need no action from Nathan. Does it apply OD-58 as Nathan gave it? Also: the next-manager start prompt's "Reporting to Nathan" adds the same rule; check it.
7. **AM9-10's prevention:**
   - never ask Nathan for a GitHub operation;
   - take CI failures to you with options that need no action from him;
   - report a written procedure that conflicts with this to you, not follow it.

   Is it enough?
8. **Notion:** check these against `<RECORDS_COMMIT>`:
   - Implementation Control's status section and its "Manager" bullet (App Manager 10);
   - the register copy's OD-58 row;
   - P06.2-F's Work Register row.

**The documents the decision touches:**
- the P06.2-F brief and record;
- the next prompt;
- the review log;
- the manager workflow's "Actions re-runs" line and the next-manager start prompt (governing, in PR40);
- Notion.

**What happens next:**
- App Manager 10 applies your verdicts. It writes the next prompt with its TypeSafe reading and gives it to Nathan.
- No GitHub operation is asked of Nathan.
