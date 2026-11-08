# DM-41 — P06.2-F: correction C4's failed run, under OD-21 and OD-58 (with the addendum on the `504`)

- **From:** Dev Manager 4, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4"), branch `claude/dev-manager`, environment `Glow App - No Stream`.
- **To:** App Manager 10 (OD-58), through Nathan (OD-25).
- **Read at:** the manager branch `claude/magical-wozniak-yfmmx2` at `106f849e659880bd16c6a501327e2fccb9ada713` (DM-41 revision 2) and at `10cb35f4f0003026d5131cd1d823285ec9f06f11` (the addendum). Between them only Markdown changed: the addendum, the handoff, the review log's DM-41 row and one record bullet. **This read covers both commits.** C4's code head `691dfbad0ab38d60ba2eb0d9715512c85b5aaccf` and `main` at `bac3c19` were read for the code.
- **Written:** 8 November 2026, about 10:55 UTC. The relayed texts match the two files in `docs/ephemeral/`, with their commits filled in.
- **Environment check (names only):** none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_APP_ID`, `STREAM_API_KEY` or `STREAM_API_SECRET` is present.

## 1. What I read and ran

- **The inputs DM-41 names**, at `106f849`:
  - the record's "Correction C4: the stop, and the manager's verification";
  - the M06 record's "The test changes", with its section 9 diagnosis (Router 58's two mechanism changes);
  - `apps/mobile/rendered/profile-preferences.spec.ts` (lines 1 to 60 and 300 to 360);
  - the workflow's OD-21 bullet and its "Actions re-runs" line, with `git diff 0a63219 106f849 -- docs/planning/manager-workflow.md`;
  - OD-58 and OD-59 in the register;
  - AM9-10 and AM9-11 in the mistakes log;
  - DM-40's sections 4.2 and 5;
  - Dev Manager 3's handover.
- **Governing diff since my start note's read (`0a63219`):**
  - the workflow's "Actions re-runs" line;
  - the next-manager start prompt (owner line; "Reporting to Nathan");
  - the register: OD-58, OD-59 and the header's list.
  - Nothing under `docs/pf-canon/`, and no `AGENTS.md` or `CLAUDE.md` at any level.
  - No non-Markdown file changed from `0a63219` to `10cb35f`: `9e0334a`, `27b90b0`, `106f849` and `10cb35f` carry C3's code byte for byte.
- **Also read:**
  - the charter's "When the primary manager consults";
  - the CI policy, whole;
  - workflow steps 5 to 7;
  - the handoff at `10cb35f`;
  - `apps/mobile/AGENTS.md`'s rendered-test bullet;
  - `apps/mobile/README.md` (web is "an internal development test surface");
  - the P11 plan's N01 row;
  - P06.2-F's diff from `main` to `691dfba` under `apps/mobile` (26 files), including `_layout.tsx`, `release-guard.ts`, `onboarding/shell.tsx` and the two rendered specs it touches;
  - the logout handlers (`store.logout(); router.replace('/')`), `index.tsx`, `routes.ts` and `+not-found.tsx`;
  - every `page.goBack()` in `apps/mobile/rendered/` (13 calls in 7 spec files).
- **CI, read-only through the GitHub tools:**
  - C4's push run 42464917902: every job's steps, and the Mobile job's log tail;
  - PR runs 42468434772 (steps), 42467985101 (cancelled) and 42460584909 (success);
  - PR run 42469365545 on `106f849`: its two failed jobs' logs and the gate's results.
- **Probes,** in scratch copies outside the checkout (`git archive`; `npm ci --ignore-scripts`; a clean process environment). The rendered probes ran against this container's Chromium 1243 headless shell. Playwright 1.62.1 pins 1234 (151.0.7922.34), so they are **informational only** (`apps/mobile/AGENTS.md`). No `playwright install` was run, and nothing was committed but this file.

| ID | What | Result |
|---|---|---|
| P1 | `npm run check` at `691dfba`; `node --test src/chat/display-rule.test.ts` | Typecheck and lint clean; 650 of 650; display-rule 21 of 21 |
| P2 | The repository's spec, `--grep "logout and account switching" --repeat-each 3`, at `691dfba` | 1 failed, 2 passed. Same line (`:342`) and same `Visible screen identities after failure: []` as CI |
| P3 | A probe spec with the test's steps to `:340`; back at 0 ms after the second `logout`; a page snapshot on failure | 5 of 12 failed. In each failure the page was the tab's initial `about:blank` (path `blank`, history length 4), still blank 20 s later; nothing private in any input |
| P4 | P3 with in-page hooks on `pushState`, `replaceState`, `go`, `back` and `popstate` | 8 of 8 passed (the hooks shift timing). Two orders seen: (i) the test's back lands first on `/profile`, then the app's `replaceState('/')` and redirect to `/account`; (ii) the app's `replaceState('/')` and **`history.go(-2)`** land first, so back reaches `about:blank` and the test's guard (`:341`) reloads `/profile-edit`, which shows account entry |
| P5 | P3 with a navigation-only trace | 6 of 16 failed. Each failure: `goBack()` **resolved at `/`**, the app's `replaceState`, 12 to 27 ms after it was sent; the guard read that URL and did nothing; `about:blank` followed 10 to 24 ms later |
| P6 | P3 with `await expect(active(page, 'screen-account')).toBeVisible()` between the `logout` click and `goBack()` | 12 of 12 passed. Each ended at `/account` with history length 2, which is the guard's fresh-load path (P4's order (ii)): back left the app |
| P7 | P3 with a pause of 50, 100 or 250 ms in place of the wait | 12 of 12 passed at each pause, all by P6's path |
| P8 | P3 on `main` (`bac3c19`, without P06.2-F's code), back at 0 ms | 4 of 12 failed, with P3's signature |

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 The rendered failure | **(a) approved with conditions 1.1 to 1.8**, with one change: the repair pass runs in `Glow App - No Stream`, not a CLI environment. No Dev Manager read before its prompt runs. (b) and (c) declined |
| 2 The `504` (on the addendum's fact) | **(b) approved with conditions 2.1 to 2.6:** a bounded retry of the toolchain install, in the same repair pass. (a) declined on the recurrence; (c) declined |
| 3 Verifying C4's code | **(a) approved with conditions 3.1 to 3.3;** (b) declined |
| 4 C4's record section | **(b) approved with conditions 4.1 to 4.3;** (a) declined |
| 5 The review | **Approved with conditions 5.1 to 5.3** |
| 6 The "Actions re-runs" line and the start prompt | **Approved with conditions 6.1 to 6.4.** The line applies OD-58 faithfully. Three texts route more widely than it does, and two other governing texts conflict with it |
| 7 AM9-10's prevention | **Approved with conditions 7.1 and 7.2** |
| 8 Notion | Matches in what I read, except **two mismatches** (section 10) |
| — DM-40 4.2 (the deferred condition) | **Confirmed for the code** (section 9); its record part stays open until 4.1 lands |

## 3. Item 1 — the rendered failure

### 3.1 What the evidence shows

- **The mechanism** (P2 to P7, informational):
  - Logout calls `store.logout(); router.replace('/')`.
  - After the click's task, Router applies the app's own history clean-up: `replaceState('/')`, then `history.go(-2)`, which drops the protected entries, then the redirect to `/account`.
  - The test sends `page.goBack()` at once (`:340`). When the back lands between the `replaceState` and the `go(-2)`, Playwright's `goBack()` resolves on the `replaceState`, a same-document navigation. So the guard at `:341` checks `page.url()` too early.
  - The two traversals then carry the tab past the app's entries to its initial `about:blank`.
- **What the "empty screen" is:** the browser's blank page, outside the app, not an app route showing nothing. The app loads normally afterwards (P3's fresh load).
- **The window:** under 50 ms after the click resolves, in my sample (P7).
- **This refines the manager's reading.** The root is the one M06 found: navigation lands after the click's task. The hazard is different. M06's was a lookup that resolved the outgoing screen's copy of a shared control. Here a browser back races the app's protected-history removal. M06's scan looked for the first form only, so it could not find this one.
- **Not P06.2-F's code:**
  - `main` fails the same way (P8).
  - P06.2-F's `_layout.tsx` edit is De Morgan-equivalent: `!(isDevelopment && mode === 'fixture')` for `!__DEV__ || mode !== 'fixture'`.
  - Its `onboarding/shell.tsx` edit changes only `FixtureOutcomeControl`'s text, not the logout button.
- **Members:**
  - Web is not a member surface ("Consumer web delivery is outside scope", `apps/mobile/README.md`). On web the same race only leaves the site, as a quick double back does.
  - The native analogue (Android hardware back, or an iOS back gesture, during the clean-up) is beyond what the web harness can show. It is carried (1.7).
- **The suite's own pattern:** each other sequence that signs out and then goes back waits for account entry first:
  - `onboarding.spec.ts`'s `backAfterLogout` (`:24-31`);
  - `discovery.spec.ts:215-221` (logout);
  - `state-corrections.spec.ts:208-213` (session expiry).

  Of the 13 `page.goBack()` calls at `691dfba`, `profile-preferences.spec.ts:340` is the one that follows a navigating click with no wait. The two others that follow a click directly, `:139` and `:191`, follow development controls that call `profiles.developmentChange` and navigate nowhere (`development.tsx:26`). That is my reading; 1.5 has the session confirm it.

### 3.2 Why (a), and why the cloud

- **(a), not (b):** OD-21 puts a failure that "prevents this work from being verified" in the current item, whatever its cause. A separate item would wait behind P06.2-F (OD-29) while P06.2-F waited on it. **(c) declined**, as the manager says.
- **The cloud, not a CLI environment:**
  - The failure reproduces in a cloud container with its own Chromium (P2, P3, P5, P8). So the pinned browser adds nothing the diagnosis needs, and CI's run stays the pinned-browser run of record either way (`apps/mobile/AGENTS.md`).
  - The CLI route would install operating-system packages with root on Nathan's machine (DM-40 section 7). It would push, and act on GitHub, with his personal credential. It would run on an open network, and need him to set the environment (OD-43).
  - For item 2's workflow change it adds one more risk: if his local token lacks the `workflow` scope, the push fails, and only a GitHub action of his could fix that (OD-58).
  - A cloud session's integration has pushed workflow changes before: M04's implementation, in `Glow App - No Stream`, changed both workflow files.

### 3.3 Conditions

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
- **1.8 The prompt:**
  - No Dev Manager read before it runs: in the cloud it authorizes no credential use and no live provider action.
  - It states 1.1 to 1.7, 2.1 to 2.6, 3.1 to 3.3 and 4.1 to 4.3 as written, and my next consultation confirms that it did.
  - A prompt that names a CLI environment, or departs from a condition, comes to me first.

## 4. Item 2 — the `504`, on the addendum's fact

- **The fact holds.** In PR run 42469365545 (on `106f849`):
  - Stream proof checks failed at `actions/setup-python`: `Version 3.12.14 was not found in the local cache`, then three `504` responses (09:58:09, 09:58:32, 09:59:01 UTC);
  - the gate's results read API checks, Mobile checks, API mobile smoke, API artifact checks and Database proof checks as `success`, and Stream proof checks as `failure`.

  So the `504` failed one job in two of the last three completed runs of PR40's code (C3's or C4's).
- **The exposure:**
  - The runner image does not hold Python 3.12.14, so each code run downloads it four times (API checks, API mobile smoke, Stream proof checks, Database proof checks). `actions/setup-node` installs Node 24.19.0 in three jobs.
  - Each time, other jobs of the same run downloaded the same file. The failure looks sporadic per request, so a delayed second attempt would likely succeed. That is a likelihood, not shown.
- **(a) declined.** A recorded explanation fits a diagnosed one-off. A recurring failure that turns the gate red on code that is otherwise green prevents verification, and OD-58 removed the manual re-run, which used to absorb such failures.
- **(b), in the same repair pass.**
  - It is OD-21's first branch, the same branch the manager uses for item 1, whose cause is also outside P06.2-F (P8).
  - The repair pass's own push run then exercises the retry.
- **(c) declined.**
  - A separate item would need its own green run, exposed to the same download.
  - It would run while P06.2-F waits, against one item at a time (OD-29).
  - Once merged, it would protect PR40's PR runs, but not the push runs of PR40's branches.
- **The manager's concern** that a workflow change widens the review is met by 5.1 and 5.2.

### Conditions

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

## 5. Item 3 — verifying C4's code without a re-run

**(a) approved.** (b) is declined: it integrates a head before its own run passes, which departs from step 5's verify-then-integrate. Its PR run would also meet the same two failures.

- **3.1 The branch:**
  - The repair pass fast-forwards from `691dfba`, so its code head holds C4's code.
  - Its branch is one the push filter names (`claude/**` or `ccr-**`).
  - Its first push to a new branch runs full checks (the CI policy: "New-branch zero-base pushes conservatively run full checks").
- **3.2 The run of record:**
  - It pushes its code commits first, and nothing else until that run completes (AM8-20).
  - The gate prints `Application checks passed`.
  - The record reads every job, the rendered count, and whether a toolchain retry fired.
- **3.3 If the run is not green,** the session stops and reports. The manager brings it to me with options that need no action from Nathan (OD-58).

## 6. Item 4 — C4's record section

**(b) approved.** (a) is declined for three reasons:
- The manager's section does not carry C4's Outcome 5: the line that supersedes C3's items, nits 6 and 7 (C2's forms by class and ID, `R3` and `R6`, the 49th form placed), and DM-40 1.3's forms for (c)'s inputs.
- DM-40 4.2 also requires that "the record says the same", and the carried-items file points to "Correction C4" for the forms by class and ID.
- The manager cannot write these itself. The workflow's role table: it "performs a commissioned work item" only if Nathan directs it.

- **4.1 What the repair pass appends.** After the manager's section, it adds "Correction C4" in the brief's Outcome 5 form, written from `691dfba` and the manager's verification:
  - the words as the comment carries them, naming the one narrowing ("Another expression") and the punctuation change;
  - the new test name;
  - the supersession line;
  - nits 6 and 7;
  - DM-40 1.3's forms.
- **4.2 Provenance:** the section says that the repair pass wrote it, not C4's session, whose draft was not recovered. It names what it cannot supply (C4's own start gate, environment check and command results) and points to the manager's verification for what was verified.
- **4.3 The repair pass's own section** follows: the diagnosis, the fix, the measurement, the scan, item 2's change and the run of record.

## 7. Item 5 — the review

**Agreed: one review**, with these conditions.

- **5.1 Form and timing:**
  - It reviews the repair pass's code head, after Codex has completed on that head and on the commit that holds its prompt (step 6).
  - It is on S2's terms (each path the pass touches read whole at the head, with the security focus) if the pass's non-test lines (the workflow's) are 60 or fewer. Otherwise it is a full exact-head review.
- **5.2 Its focus:**
  1. C4's items under DM-40 3.1 to 3.4, unchanged;
  2. the diagnosis: the trace supports the mechanism;
  3. the spec: one wait added, nothing removed, loosened or moved, and the comment true;
  4. the workflow: 2.1 to 2.3, the same pins, and the gate unchanged;
  5. the record sections: true to the code, the runs and this report.
- **5.3 A runtime change** found by the diagnosis stops the pass, comes to me first, and gets its own full review. A form inside DM-40's narrowed words still comes to me before any further correction (DM-40 3.4).

## 8. Items 6 and 7 — OD-58's texts, and AM9-10's prevention

- **6.1 The rule and its quote.**
  - The line applies OD-58's rule as Nathan gave it, and the quote is exact.
  - "A GitHub operation" reads his "github actions" as any operation on GitHub. That is a reading, and the safe one: it limits what the manager asks, never what Nathan may do himself.
  - OD-58's State cell should say it is a reading, as OD-10 does for OD-34.
  - It is not put to Nathan: nothing breaks under it.
- **6.2 The scope.** The workflow line routes a failure that "seems to call for a re-run". Four texts say "a CI failure", which would also send ordinary test failures to me. Step 6's fix-or-carry rule decides those, and the charter excludes them. Align each to the workflow's words:
  - the start prompt: "Take a CI failure that seems to call for a re-run to the Dev Manager first, with options that need no action from him.";
  - OD-58's State cell and AM9-10's prevention: "A CI failure that seems to call for a re-run, or any question about how to verify a head, goes to the Dev Manager first (OD-32), with options that need no action from Nathan.";
  - the handoff: "A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him."
- **6.3 The charter's "Not for"** lists "CI reruns", which now contradicts the workflow line. Replace it with:

  > **Not for:** routine verification, routine records, small documentation fixes, exact-head code review, or a review finding's fix-or-carry that the workflow's rule decides (step 6), unless its fix meets one of that rule's limits. **A CI failure that seems to call for a re-run does come to it first** (OD-58; the manager workflow, "Actions re-runs"), with options that need no action from Nathan.
- **6.4 Step 7's branch-cleanup sentence** still says that when a cleanup run fails "the names to delete go to Nathan". That is a written procedure that puts a GitHub operation on him. Replace "Until M04's merge receipt records the cleanup's first run, and whenever a cleanup run fails, the manager lists the branches by hand; a session cannot delete a branch, so the names to delete go to Nathan, and the manager records the result once he has." with:

  > Whenever a cleanup run fails, the manager lists the branches by hand and records them in the merge receipt; the next cleanup run deletes the fully merged ones. A session cannot delete a branch, and the manager never asks Nathan to (OD-58).

  Its first clause is history: M04's receipt recorded the first run.
- **Applied as written,** 6.2 to 6.4 need no further read before PR40 merges (the charter, "A read covers one commit"). My next consultation confirms them. Otherwise the start prompt's bullet matches the workflow line.
- **7.1 AM9-10's prevention** takes 6.2's wording. With that, the never-ask rule, routing to me, and reporting a conflicting procedure cover what went wrong.
- **7.2 The missed sweep.** App Manager 9's OD-58 batch missed the two texts in 6.3 and 6.4 in its supersession sweep (step 5). App Manager 10 records that in the mistakes log as App Manager 9's (OD-11), and AM9-10's correction lists 6.3 and 6.4.

## 9. DM-40 section 4.2, confirmed for the code

C4's comment at `691dfba` against section 4.2, by script (each quotation and entry searched for in the comment, whitespace normalized) and by reading:

- **Exact:**
  - the source check's sentence;
  - "written with `=`";
  - the `Reflect` and `Object` item;
  - F0's family, with its sentence's start kept;
  - the four known-passing entries.
- **With differences:**
  - the callback item reads "Another expression" for "Any other expression". That is narrower: it drops a coverage word that DM-38 4.2 bars, which the predecessor's text should not have used;
  - the destructuring exception ends in ";" for ".", to continue its sentence.
- **The test name** is as DM-40 section 6 gives it.
- **A nit, not wrong:** the `Reflect` item now cites C2-3c and C2-3d twice, because the prompt kept the old bracket.
- **Still open:** the record's part ("the record says the same") stays open until 4.1's section lands. My next consultation confirms it.

## 10. Notion (read-only, about 10:45 UTC, against `10cb35f`)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control | The status heading and lead | **Match:** App Manager 10, matched at `10cb35f`, with the addendum |
| Implementation Control | The "Manager", "Dev Manager" and mistakes-log bullets; "Standing directions" | **Match:** App Manager 10 (OD-58); Dev Manager 4 (OD-59); AM9-01 to AM9-11 at `106f849`; OD-01 to OD-59 |
| Implementation Control | The "Branches" bullet | **Mismatch:** it is still the 3 November listing, says the manager branch is "`0a63219` at this sync", has `claude/dev-manager` at `497ba97`, and omits `claude/upbeat-mccarthy-499h9k` (C4, `691dfba`). The handoff lists the branches at 09:34 UTC, with C4's branch and `claude/dev-manager` at `a2b985b`. AM9-07's prevention covers it: a readback includes each section that names a commit |
| Register copy | Stamp; OD-58 and OD-59; row order | **Match:** stamped `9e0334a`, and the register is unchanged from `9e0334a` to `10cb35f`. OD-58's and OD-59's rows are identical after normalizing markup. 59 rows, in the repository's order. Other cells were not compared word for word |
| Dev Manager — reviews and approvals | The Dev Manager 4 row; the DM-41 row | The session row matches the review log (both say "Starting"; my start note is at `58bacb8`, to be recorded when my branch is integrated). **Mismatch:** its DM-41 row lacks the addendum, which the review log's DM-41 row carries at `10cb35f` |
| Work Register `P06.2-F` | State, next action, plan link | **Match** at `10cb35f`: DM-41 revision 2 and the addendum, App Manager 10, 2 of 31. The plan link is pinned to `106f849`, and the brief is unchanged since |

## 11. Where each item goes

| Item | Home |
|---|---|
| 1.1 to 1.6; 2.1 to 2.3, 2.5, 2.6; 3.1 to 3.3; 4.1 to 4.3 | The P06.2-F brief's next revision (a repair-pass section) and its prompt (1.8); the record's two sections |
| 1.7 | The P11 plan's N01 row |
| 2.4 | The CI policy's new paragraph (governing; confirmed at my next consultation) |
| 5.1 to 5.3 | The repair pass's review prompt |
| 6.1, 6.2 | OD-58's State cell, the start prompt's bullet, AM9-10's prevention and the handoff |
| 6.3, 6.4 | The charter's "Not for"; step 7 (governing; confirmed at my next consultation) |
| 7.2 | The mistakes log (App Manager 9's sweep miss) |
| Section 9 | "Deferred conditions": DM-40 4.2's record part stays open |
| Section 10 | Implementation Control's Branches bullet; the Dev Manager page's DM-41 row |
| Deferred, new | My next consultation confirms 1.8's prompt, 2.4's paragraph, 6.2 to 6.4 and DM-40 4.2's record part |

Status: complete
