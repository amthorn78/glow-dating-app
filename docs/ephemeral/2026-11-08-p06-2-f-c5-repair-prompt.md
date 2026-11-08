# P06.2-F repair pass C5 prompt — the rendered race, the toolchain retry, C4's code and record (DM-41)

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 8 November 2026.**
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 5, its section "Repair pass C5". The design is [DM-41](../continuity/dev-manager/reviews/2026-11-08-dm-41-p06-2-f-c4-run-failure.md), sections 3 to 6.
- **Where the result goes:** the session's code commits (one wait in `apps/mobile/rendered/profile-preferences.spec.ts`; the toolchain retry in `.github/workflows/foundation.yml`) and the record's two new sections, "Correction C4 (written by repair pass C5)" and "Repair pass C5", on its own branch; the run of record, the Foundation push run on its code head. The manager verifies it and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.80 (confidence 0.86); rung probabilities low 0.00, medium 0.20, high 0.79, extra high 0.01, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.03, Opus 5.5 0.88, Sonnet 5.5 0.09, Haiku 5.5 0.00 (confidence 0.84). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.006, Fable 5.1 at high 0.024, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.176, Opus 5.5 at high 0.695, Opus 5.5 at extra high 0.009, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.018, Sonnet 5.5 at high 0.071, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-08T10:50:46Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (DM-41 1.8): in the cloud it authorizes no credential use and no live provider action. Its next consultation confirms that this prompt states DM-41's conditions as written.
- **Environment** (OD-36): `Glow App - No Stream`, not a CLI environment (DM-41 1.1). No Stream variable is needed.
- **It runs alone** (OD-29). Codex's review of its code head follows, then one review on DM-41 5.1 to 5.3.
- **Deletion condition:** prune after P06.2-F's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **repair pass C5 of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Correction C4** (branch `claude/upbeat-mccarthy-499h9k`, code head `691dfbad0ab38d60ba2eb0d9715512c85b5aaccf`) narrowed the render-rule comment in `apps/mobile/src/chat/display-rule.test.ts` to DM-40 section 4.2's words and renamed the first render test. The manager verified that, outside comments, only that test name changed. Its session did not push its record section and has been archived.
- **C4's push run, 42464917902, failed in two jobs C4 does not touch:**
  - Database proof checks: `actions/setup-python` got three `504` responses while downloading Python 3.12.14, before any job step. It recurred in Stream proof checks on PR run 42469365545.
  - Mobile checks: `rendered/profile-preferences.spec.ts:321` failed at `:342`. 2 of 31 rendered runs since M06's fix have failed this test, on C3's code too.
- **The Dev Manager's DM-41** (read it whole) traced the rendered failure, with informational probes against the container's Chromium. The test's `page.goBack()` at `:340`, sent straight after the second `logout` click, races the app's own post-logout history clean-up: `replaceState('/')`, then `history.go(-2)`. `goBack()` resolves on the `replaceState`, so the guard at `:341` reads `page.url()` too early, and the tab lands on its initial `about:blank`, outside the app. `main` fails the same way (its probe P8, 4 of 12). It approved one repair pass, you, under OD-21: fix the race in the spec, retry the toolchain install once, verify C4's code with your own run, and finish C4's record, which the manager cannot write itself.

**What you do: DM-41's conditions, as written.** In them, "me" and "my" mean the Dev Manager, and "the session" means you. 1.7 is already applied: the P11 plan's N01 row carries it. 2.4's CI policy paragraph is the manager's to add when your change is integrated; you do not edit the CI policy.

**Item 1, the rendered failure (DM-41 section 3.3):**

- **1.1 Environment:** `Glow App - No Stream`.
  - The diagnosis may run the rendered configuration against the container's Chromium, from an uncommitted configuration outside the checkout, as informational. Never `playwright install`.
  - If the session cannot reproduce the failure there, it stops and reports. A CLI-environment prompt then comes to me before it runs.
- **1.2 The diagnosis,** in the session's own repeats, with the browser named:
  - the failure count at the test's own sequence;
  - for at least one failing repeat, the order of history operations: the app's `replaceState` and `go(-2)`, the test's back, the URL `goBack()` resolved at, and the page at `about:blank`.

  It may cite this report's P8 for `main` rather than repeat it.
- **1.3 The fix,** in `apps/mobile/rendered/profile-preferences.spec.ts` only:
  - add `await expect(active(page, 'screen-account')).toBeVisible();` after the second `logout` click and before `page.goBack()`, as the suite's other sign-out-then-back sequences do;
  - remove, loosen or move no assertion;
  - make its comment state the mechanism 1.2 shows (Router's post-logout history clean-up runs after the click's task, and a back sent before it lands can leave the app), not M06's shared-control reason.
- **1.4 The measurement:**
  - the fixed sequence passes at least 30 repeats with no failure, beside the unfixed count in the same environment;
  - the record says where back lands with the fix. In P6 it always left the app, so the test's last two assertions then run after a fresh load, as in its siblings, and its in-app retained-state checks are the ones at `:331-332` and `:336-338`.

  The session may add an assertion that back leaves the app, if its repeats show it always does. That adds a check; it loosens none.
- **1.5 The scan:** the record names each `page.goBack()` in `apps/mobile/rendered/` (13 at `691dfba`) with what precedes it. A call is changed only if it follows, with no wait, a click whose handler calls `router` or flips a `Stack.Protected` guard.
- **1.6 The stop rule:** stop and report, changing nothing, if any of these holds:
  - the blank page appears with the wait in place;
  - the page left is an app route showing no screen, not the tab's initial `about:blank`;
  - the fix needs a change outside the spec, apart from item 2's workflow change and the record.

  A runtime change comes to me first, with its own full review.
- **1.7 Carried, a native check:** the P11 plan's N01 row gains: "After logout, an immediate back (Android hardware back, iOS back gesture) lands on account entry, never on a private screen or an empty one (DM-41)."

**Item 2, the `504` (DM-41 section 4):**

- **2.1 What is retried, and nothing else:**
  - only the toolchain install: `actions/setup-python` at its existing pin, for 3.12.14, in the jobs that use it;
  - optionally `actions/setup-node` at its existing pin, the same way;
  - no checkout, dependency install, check, test or proof step is retried or made `continue-on-error`;
  - the gate's logic is unchanged.
- **2.2 Bounded and visible:**
  - one retry, after a fixed pause the session states;
  - the first attempt's failure and the retry show in the job log;
  - a failure of the retry fails the job.
- **2.3 Nothing new:**
  - no third-party action, no new pin, and no cache of the interpreter (the install keeps its present source);
  - permissions, triggers, concurrency, timeouts and the six job names unchanged.
- **2.4 The CI policy's workflow rules:**
  - the manager classifies with the pre-change policy (full scope);
  - it reads the whole workflow diff and the run of record's actual job steps.
  - The CI policy gains this paragraph after "The push filter" (the parenthesis is dropped if the pass does not wrap `setup-node`; that edit is within this text):

    > **Toolchain installs are retried once** (DM-41 item 2). Each job retries its `actions/setup-python` step (and its `actions/setup-node` step) once, after a fixed pause, if the first attempt fails, with the same pinned action and version. On 8 November 2026 the download of Python 3.12.14, which the runner image does not hold, failed with `504` responses in two runs (42464917902 and 42469365545), before any job step, and no one re-runs failed jobs (OD-58). No checkout, dependency install, check, test or proof step is retried, and the gate is unchanged. A failure after the retry fails the job; the manager takes it to the Dev Manager, with options that need no action from Nathan (the manager workflow, "Actions re-runs").

    Applied as written, it needs no further read; my next consultation confirms it.
- **2.5 Honest limits:**
  - unless a download fails during it, the run of record does not exercise the retry path; the record says so;
  - the review reads the YAML against GitHub's documented semantics of `continue-on-error` and `steps.<id>.outcome`;
  - no deliberately failing run is pushed to test it.
- **2.6 If the retry fails too,** the item comes back to me. No re-run is asked of anyone.

**Item 3, verifying C4's code (DM-41 section 5):**

- **3.1 The branch:**
  - The repair pass fast-forwards from `691dfba`, so its code head holds C4's code.
  - Its branch is one the push filter names (`claude/**` or `ccr-**`).
  - Its first push to a new branch runs full checks (the CI policy: "New-branch zero-base pushes conservatively run full checks").
- **3.2 The run of record:**
  - It pushes its code commits first, and nothing else until that run completes (AM8-20).
  - The gate prints `Application checks passed`.
  - The record reads every job, the rendered count, and whether a toolchain retry fired.
- **3.3 If the run is not green,** the session stops and reports. The manager brings it to me with options that need no action from Nathan (OD-58).

**Item 4, C4's record (DM-41 section 6):**

- **4.1 What the repair pass appends.** After the manager's section, it adds "Correction C4" in the brief's Outcome 5 form, written from `691dfba` and the manager's verification:
  - the words as the comment carries them, naming the one narrowing ("Another expression") and the punctuation change;
  - the new test name;
  - the supersession line;
  - nits 6 and 7;
  - DM-40 1.3's forms.
- **4.2 Provenance:** the section says that the repair pass wrote it, not C4's session, whose draft was not recovered. It names what it cannot supply (C4's own start gate, environment check and command results) and points to the manager's verification for what was verified.
- **4.3 The repair pass's own section** follows: the diagnosis, the fix, the measurement, the scan, item 2's change and the run of record.

**What the review will read** (DM-41 5.2, for your information): C4's items under DM-40 3.1 to 3.4, unchanged; your diagnosis against the mechanism; the spec, with one wait added and nothing removed, loosened or moved, and its comment true; the workflow against 2.1 to 2.3, the same pins and the gate unchanged; and your record sections, true to the code, the runs and DM-41. A runtime change found by your diagnosis stops the pass (5.3).

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - **in `apps/mobile/rendered/profile-preferences.spec.ts`,** only 1.3's wait and its comment, and 1.4's optional assertion; no other spec changes unless 1.5's rule requires it, and then report it;
  - **in `.github/workflows/foundation.yml`,** only the toolchain steps, under 2.1 to 2.3;
  - **in the record** (`docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`), append "## Correction C4 (written by repair pass C5)" and then "## Repair pass C5" at the file's end, after the manager's section "Correction C4: the stop, and the manager's verification", and change nothing else in it;
  - nothing else: no dependency, lock file, application source, governing Markdown or other workflow;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete or force-push a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **Rendered runs here are informational** (1.1; `apps/mobile/AGENTS.md`). Run the rendered configuration against the container's preinstalled Chromium (for example with `executablePath: '/opt/pw-browsers/chromium'` in an uncommitted configuration outside the checkout), and name the browser in the record. CI's run is the pinned-browser run of record.
- **Network:** the npm registry for `npm ci --ignore-scripts`, and GitHub through your tools to read your run. Nothing else.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas`, `eas-cli` or `migrate`;
  - run package install scripts: always `npm ci --ignore-scripts`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`. Put it first on PATH yourself. Record their versions.
5. **A clean process environment** for every npm and Playwright command: `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

Your branch starts at C4's code head and takes the manager's records from this prompt's commit, so its code is C4's and its record has the manager's sections (3.1).

```bash
git fetch origin claude/magical-wozniak-yfmmx2 claude/upbeat-mccarthy-499h9k main
git switch -C <your session branch> 691dfbad0ab38d60ba2eb0d9715512c85b5aaccf
git merge --no-edit <START_SHA>                      # must not conflict
git merge-base --is-ancestor 691dfbad0ab38d60ba2eb0d9715512c85b5aaccf HEAD && echo "C4's code head is in the branch"
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 691dfbad0ab38d60ba2eb0d9715512c85b5aaccf HEAD -- . ':(exclude)*.md' && echo "the code is C4's"
git diff --quiet <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- . ':(exclude)*.md' && echo "no code on the live branch after this prompt"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^## (Correction C4 \(written by repair pass C5\)|Repair pass C5)$'   # must print 0
```

If a check fails, stop and report. **Your branch name must match the push filter, `claude/**` or `ccr-**` (3.1).** If it does not, stop before pushing and report.

**Then read, completely:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`; the CI policy (`docs/operations/ci-and-branch-policy.md`); the brief's "Correction C4" and "Repair pass C5"; the record's "Correction C4: the stop, and the manager's verification", and the M06 record's "The test changes" (`docs/testing/evidence/2026-11-01-m06-sdk-58-upgrade.md`); DM-40's report, sections 4 to 6 (`docs/continuity/dev-manager/reviews/2026-11-08-dm-40-p06-2-f-c3-review-and-od-57.md`); DM-41's report, whole; C4's prompt (`docs/ephemeral/2026-11-08-p06-2-f-c4-correction-prompt.md`), for Outcome 5's lines; `apps/mobile/rendered/profile-preferences.spec.ts`, whole; `.github/workflows/foundation.yml`, whole.

## 3. What to do, in order

1. **The diagnosis** (1.2): reproduce at the test's own sequence in this container, with the count and the browser named; capture one failing repeat's order of history operations. If it does not reproduce, stop and report (1.1).
2. **The fix** (1.3) and **the measurement** (1.4): 30 or more repeats of the fixed sequence with no failure, beside the unfixed count, and where back lands. If 1.6 holds, stop and report.
3. **The scan** (1.5): every `page.goBack()` in `apps/mobile/rendered/`, with what precedes it.
4. **The retry** (2.1 to 2.3): in the workflow; state the pause, show how the first failure and the retry appear in the log, and that a failed retry fails the job. Count the workflow's changed non-test lines and record the number (DM-41 5.1 uses it).
5. **The local checks,** in `apps/mobile`: `npm ci --ignore-scripts`, then `npm run check` (at least 650 unit tests); `node --test src/chat/display-rule.test.ts` 21 of 21.
6. **Push your code commits first** (3.2), then read the Foundation push run on your code head with your GitHub tools: every job's conclusion and steps, the gate's line, the `@glow/mobile` unit count, the rendered count, and whether any toolchain retry fired. **Push nothing else until that run has completed** (AM8-20). If the gate does not print `Application checks passed`, stop and report (3.3); if a retry also failed, say so (2.6).
7. **Then the record** (4.1 to 4.3): "Correction C4 (written by repair pass C5)", in Outcome 5's form with 4.2's provenance, then "Repair pass C5", with the start gate, the environment check (names only), every command with its result line, the run of record, 2.5's limits and what you could not run. Commit and push it.

Confirm that `git status` is clean and that `git diff --name-only 691dfbad0ab38d60ba2eb0d9715512c85b5aaccf HEAD -- . ':(exclude)*.md'` lists only the spec and the workflow.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, code head and records head;
- the start gate's and the environment check's results;
- the diagnosis: the counts, the browser, the order of operations, and whether 1.6 held;
- the fix and the measurement, and where back lands;
- the scan's table, and any call changed;
- the retry: the steps wrapped, the pause, and the workflow's changed non-test line count;
- the local checks' results;
- the run of record (ID, every job, the gate's line, the unit and rendered counts, whether a retry fired);
- anything that met a stop rule, and what you could not run.
