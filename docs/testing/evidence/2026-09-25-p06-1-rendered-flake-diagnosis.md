# P06.1 rendered-test flake diagnosis — 25 September 2026

Evidence record for the rendered-test flake diagnosis in the [P06.1 brief](../../planning/p06-1-chat-provider-proof.md) ("Sessions", OD-21). This file records observations only. It is not an instruction source.

## Result

- **Cause, class (a): a defect in the app's code that the tests expose.** On web, the app moves keyboard focus one animation frame *after* a screen or error message appears: `ScreenTitle` focuses the screen heading and `Feedback` focuses the error alert, both through `focusText`. If a field on that screen has been focused inside that short gap, the deferred focus takes focus away from it. The text entry that follows is then lost: Chrome applies it to the field's old selection, so a field whose text was selected is **emptied**. The emptied date fails validation, and the submit stays on the same screen with an alert.
- **Reproduction.**
  - No natural failure occurred locally in 322 started runs of the two cases, with and without load.
  - A scratch trigger holds only the app's own deferred-focus frame callbacks until a text field gains focus. With the heading's focus held, the unsaved case failed at line 57, CI #1/#2's line, in 10 of 10 runs (runs 06, 07, 10 and 11-title). Holding only the alert's focus made the birth journey fail at line 113, CI #3's line, in 3 of 3 runs.
  - The app's focus timing was measured and shows how narrow the natural race is.
- **Fix, inside P06.1.** `focusText` does not take focus from a shown text field that already has focus. There is also a rendered regression test for the mechanism.
- **Proof.**
  - Under the same triggers, 22 runs failed before the fix; the 3 others passed as expected. After the fix, 82 of 82 passed.
  - After the fix, both cases passed 30 times each without the trigger.
  - The full rendered suite passed 84 of 84, and `npm run check` passed.
  - The regression test failed 10 of 10 before the fix and passed 40 of 40 after it.
- **Browser caveat.** All browser results here come from the container's preinstalled Chromium, not the pinned revision, so they are informational. Hosted CI remains the rendered acceptance.

## Session and environment

- **Branch:** `claude/trusting-mayer-bw6p40`.
- **Start gate:** `git fetch origin claude/stoic-carson-66gdig`, then `git merge --ff-only 8d202fd02b0064ce4ca281f978b31ce4d07c99d9`. `git rev-parse HEAD` printed `8d202fd02b0064ce4ca281f978b31ce4d07c99d9`.
- **Host:** Claude Code cloud container, x86_64, 4 CPUs, 15 GiB memory.

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | None present |
| `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` | Present. Names only; values not read or used |
| `command -v node npm npx python3.12` | `/root/.local/bin/{node,npm,npx,python3.12}` (`$HOME` is `/root`) |
| Versions | `node` v24.19.0, `npm` 11.9.0, `npx` 11.9.0, `python3.12` Python 3.12.14 |
| Install | `npm ci --ignore-scripts` in `apps/mobile`, passing only `HOME`, `PATH`, `LANG`, `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` into an `env -i` process: exit 0 |
| Browser | Preinstalled `/opt/pw-browsers/chromium_headless_shell-1194` (Chromium 141.0.7390.37). One timing sample also used the full `/opt/pw-browsers/chromium-1194`. Playwright 1.62.1 pins revision 1234 (Chrome for Testing 151.0.7922.34), which CI installs. `playwright install` was not run |

Every app and test command ran as `env -i HOME="$HOME" PATH="$PATH" LANG=C.UTF-8 …` from `apps/mobile`. There was no database, HDE, Railway, Stream or other provider connection, and no `eas` or `migrate`. On GitHub, the session only read one job log (below).

## Scratch tooling

All of it lived in the ignored `apps/mobile/.work/`, and none of it is committed.

- **`pw.scratch.config.ts`** extends `playwright.config.ts`. It adds `launchOptions.executablePath` for the preinstalled headless shell, `trace: 'retain-on-failure'` and `screenshot: 'only-on-failure'`, and writes its output to `.work/`. It runs the committed specs unchanged.
- **Instrumented copies** of `state-corrections.spec.ts` and `onboarding.spec.ts` are byte-identical to the committed specs apart from a two-line hook, checked with `diff`. The hook's line offset is +2, so line 57 appears as 59 and line 113 as 115. The hook does four things:
  - installs a page recorder of focus, `beforeinput`, `input`, click, visible-screen and alert events, with timestamps and the caller of every `HTMLElement.focus()`;
  - on failure, writes the alert text, every input's value and the event log;
  - optionally applies CDP CPU throttling;
  - optionally installs the trigger below.
- **Trigger.** The page script below defers only the frame callbacks whose source calls `focusText`. They run as soon as a text field gains focus. It changes neither app code, test steps nor state.

  ```js
  const nativeRaf = requestAnimationFrame.bind(window), nativeCancel = cancelAnimationFrame.bind(window);
  const held = new Map(); let seq = 1e9;
  window.requestAnimationFrame = cb => String(cb).includes('focusText') ? (held.set(++seq, cb), seq) : nativeRaf(cb);
  window.cancelAnimationFrame = id => held.has(id) ? held.delete(id) : nativeCancel(id);
  document.addEventListener('focusin', e => {
    if (!(e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) || !held.size) return;
    const ids = [...held.keys()];
    queueMicrotask(() => ids.forEach(id => { const cb = held.get(id); held.delete(id); cb?.(performance.now()); }));
  }, true);
  ```

  - **Timing:** `microtask` mode releases right after the focusing script, which is deterministic. `task` mode releases in the next task, which is probabilistic.
  - **Which callbacks:** `HOLD_ONLY=title` holds callbacks scheduled through Expo Router's `useFocusEffect` (`ScreenTitle`). `HOLD_ONLY=alert` holds the rest (`Feedback`). Scheduling stacks confirmed the split.
- **Split-fill probe:** performs Playwright's two fill phases by hand with a two-frame gap between them.
- **Load:** a wrapper runs the whole command under `taskset -c 0,1`, with three shell busy loops pinned to the same two CPUs.
- **Second port:** a copy of the configuration on port 8082 let runs 06 and 07 use CPUs 2–3 while run 05 used CPUs 0–1.

## Runs

"Cases" means `rendered/state-corrections.spec.ts:45`, which covers both the accepted and the unsaved variants, and `rendered/onboarding.spec.ts:103`, the private birth journey. Runs 01–13 and 19 use the start SHA's app code. Runs 14–18 and 20–22 include the fix.

| Run | What | Result |
|---|---|---|
| 01 | Cases, committed specs, `--repeat-each=30`, no pressure | **90 passed** (5.9 min) |
| 02 | Instrumented cases, CDP CPU throttling ×4, `--repeat-each=10` | Stopped after 10 of 30 started (≈1 min per test); 0 failures |
| 03 | Split-fill probe at four fill points | 4 passed. The deferred focus had already run before the probe's first phase |
| 04 | Timelines of the unsaved case and the birth journey | 2 passed; timing below |
| 05 | Instrumented cases pinned to 2 CPUs with 3 CPU hogs, `--repeat-each=20` | **60 passed** (5.7 min) |
| 06 | Trigger (`task` mode), cases once, port 8082 on CPUs 2–3 (overlapping run 05) | 2 failed, 1 passed. Unsaved stopped on eligibility with "Enter a real civil date that is not in the future."; accepted stopped on birth with "Check the civil birth date…"; the birth journey passed |
| 07 | Trigger (`task`), unsaved case once, full timeline (CPUs 2–3, overlapping run 05) | 1 failed; timeline below |
| 08 | Committed cases, `--workers=4 --fully-parallel --repeat-each=100` | Stopped after 130 of 300 started (≈7 per minute); 0 failures |
| 09 | Timing sample, `--repeat-each=5`, headless shell and full Chromium | 15 passed on each browser |
| 10 | **Before fix**, trigger (`microtask`, all), unsaved + birth journey, `--repeat-each=5` | **10 failed**: unsaved 5 of 5 at line 57, on eligibility with the date alert; birth journey 5 of 5 at line 120 |
| 11 | **Before fix**, trigger (`microtask`), `HOLD_ONLY=alert` and `=title`, `--repeat-each=3` | alert: birth journey **3 failed at line 113**, unsaved 3 passed. title: **6 failed**, unsaved at line 57 and birth journey at line 120 |
| 12 | **Before fix**, new regression test, `--repeat-each=10` | **10 failed**: `adult-date` not focused ("Received: inactive") at line 201 |
| 13 | **Before fix**, scratch copy of the regression test's alert half only, `--repeat-each=5` | **5 failed**: `birth-date` not focused |
| 14 | After fix, regression test, `--repeat-each=20` | **20 passed** |
| 15 | After fix, alert half only, `--repeat-each=5` | **5 passed** |
| 16 | After fix, same trigger as run 10 | **10 passed** |
| 17 | After fix, same triggers as run 11 | alert **6 passed**; title **6 passed** |
| 18 | After fix, cases with committed specs, no trigger, `--repeat-each=30` | **90 passed** (5.8 min): 30 unsaved, 30 accepted, 30 birth journey |
| 19 | **Before fix** (start SHA `ui.tsx` restored for this run only), trigger (`microtask`), accepted case, `--repeat-each=3` | **3 failed**: on birth with "Check the civil birth date…", then test timeout |
| 20 | After fix, trigger (`microtask`, all), all three cases, `--repeat-each=20` | **60 passed** (3.9 min) |
| 21 | After fix, **full rendered suite** | **84 passed** (4.2 min): 83 existing cases and the new test |
| 22 | After fix, regression test on 2 CPUs with 3 hogs, `--repeat-each=20` | **20 passed** |

Other checks, with the fix:

| Command | Result |
|---|---|
| `npm run check` | Exit 0: `tsc --noEmit` clean, `eslint .` clean, **516/516** unit tests passed |
| `EXPO_OFFLINE=1 npm run check:expo` | Exit 0, "Dependencies are up to date" (offline validation) |
| `EXPO_OFFLINE=1 npm run export:development` | Exit 0: iOS (1,321 modules) and Android (1,467 modules) development bundles exported |
| `git diff --check` | Clean |

**Before and after under the same triggers:**

- Before the fix, 22 runs failed: run 10 (10), run 11-title (6), run 11-alert's birth journey (3) and run 19 (3). Run 11-alert's 3 unsaved runs passed, because that case shows no alert before line 57.
- After the fix, 82 of 82 passed: run 16 (10), run 17 (12) and run 20 (60). Runs 16 and 17 repeat the commands of runs 10 and 11 exactly.

## Mechanism

### The code at the start SHA

- `apps/mobile/src/components/ui.tsx:21-31`: on web, `focusText` sets `tabIndex = -1` on the node and calls `node.focus()` (line 28).
  - `ScreenTitle` calls it from `requestAnimationFrame` inside `useFocusEffect` (line 36).
  - `Feedback` calls it from `requestAnimationFrame` whenever `error` changes (lines 46–48).
  - `src/interactions/controls.tsx:16` uses the same pattern.
  - `focusText` is the only app code that moves focus.
- `apps/mobile/src/onboarding/shell.tsx:13-14`: every onboarding screen renders both `ScreenTitle` and `Feedback`.
- Expo Router queues `router.push` and `router.replace` (`node_modules/expo-router/build/global-state/router.js:68-69`, `80-81` and `165`) and dispatches them from an effect (`imperative-api.js:11-12`). The new screen therefore commits after the click has returned; in the timelines, 20–75 ms later. The heading's frame callback runs after that commit.

### Why a fill can be hit

Playwright 1.62.1's `fill` (in `node_modules/playwright-core/lib/coreBundle.js`, `_fill`) has two phases:

1. One page evaluate checks that the field is visible, enabled and editable, then runs `input.select(); input.focus();`.
2. A separate CDP `Input.insertText` inserts the text.

Before the evaluate, Playwright waits for the element by retrying from its server at 0, 20, 50, 100, 100 and 500 ms (`retryWithProgressAndBackoff`). The field is ready by Playwright's documented checks, and nothing tells it that the app's focus handling is still pending. If the app's deferred `focusText` runs between phase 1 and phase 2, focus leaves the field just before the text arrives.

### What the browser then does

This is from run 07's timeline, in milliseconds since page start. The values are the specs' own fictional literals.

```text
3059.0 focusin      adult-date                          (Playwright phase 1: select + focus)
3059.6 focus()      heading of screen-eligibility       by focusText  (app, deferred frame)
3059.8 focusin      heading of screen-eligibility
3060.4 beforeinput  target=heading  insertText data="1992-07-16"        (Playwright phase 2)
3061.5 input        target=adult-date insertText data="" value=""       active=heading
3108.0 focusin      eligibility-submit
3132.6 alert        "Enter a real civil date that is not in the future."  (screen-eligibility)
```

Chrome sent `beforeinput` to the newly focused heading, then applied the edit to the field that still held the selection.

- **A field whose value was selected received an empty insertion, so it was emptied.** This happened to `birth-date` (2885–2887 ms) and `adult-date` (3059–3062 ms) in run 07, and to `birth-date` and `birth-time` in run 10.
- **An empty field with a collapsed selection received the text.** This happened to `adult-date` at 2621–2630 ms.

With the date emptied, the eligibility submit ran `store.setAdultDate('')` (`src/app/eligibility.tsx:39`). That reached `fail('Enter a real civil date that is not in the future.')` (`src/onboarding/store.ts:223`), so the screen stayed on eligibility with a visible alert. On the birth screen, the emptied date reached `fail('Check the civil birth date, …')` (`store.ts:255`).

### Why only sometimes

Run 09 measured timings with the unmodified app. The **gap** below is the time between the app's deferred focus and Playwright's first focus of a field.

| Browser | Screen or alert commit → app's deferred focus | Commit → Playwright's focus of the field | Gap |
|---|---|---|---|
| Headless shell 1194, 42 transitions | median 1.8 ms, p90 2.3, **max 27.3** | median 23.0 ms, min 12.7 | min **3.2 ms**, p10 15.1 |
| Full Chromium 1194, 45 transitions | median 1.8 ms, p90 18.9, **max 36.8** | median 28.2 ms, min 19.9 | min **3.7 ms**, p10 16.1 |

Run 04 had one transition with a 27.6 ms deferred focus and a **2.8 ms** gap.

The app normally wins by 15–25 ms, but its focus is occasionally delayed by tens of milliseconds. Its lead then shrinks to a few milliseconds. A slightly slower frame, a busier hosted runner or a different Chrome build puts the deferred focus between Playwright's two phases.

### The CI failures, matched

| CI failure | Symptom | Reproduced by |
|---|---|---|
| #1 PR run 35991614536 attempt 1; #2 PR run 36020836838 (job 107706842358) | `state-corrections.spec.ts:57`: stayed on `screen-eligibility` with a visible alert, no birth controls | `HOLD_ONLY=title`: 3 of 3 at line 57, and 5 of 5 in run 10. The captured alert is "Enter a real civil date that is not in the future.", with the eligibility date field empty (Playwright's `error-context.md`, run 06) |
| #3 push run 36025919795 | `onboarding.spec.ts:113`: `screen-remaining` did not appear after `birth-submit` | `HOLD_ONLY=alert`: 3 of 3 at line 113. The alert that followed the future-date check took focus from the date re-entry |

The job log of #2, read through the GitHub integration, shows `screen-eligibility`, `submitCount: 0`, no birth fields and `visibleAlertPresent: true`. The case took 11.3 s, which is 1.3 s of steps and then the 10 s wait.

With a current account and accepted consent, the date check is the only error that step can raise (`eligibility.tsx:37-44`; `store.ts:220-251`). The consent is already accepted and the checkbox is not touched. So the CI alert was that message. **This is an inference; CI never captured the text.**

The earlier failures match the same signature: an empty date field, a filled place and a visible validation alert after both inputs were filled (P04.3), and an empty date field with a visible validation alert (the P05.1 baseline). Those ran on older code, which was not re-run here.

## Classification and route

**Class (a).** The app moves focus asynchronously, after the screen is visible and editable, without checking whether focus has moved in the meantime.

- **Not (b).** The test acts on a field that meets Playwright's actionability checks. The app gives no other readiness signal, and a person, autofill or an input tool can focus a field just as early.
- **Not a test-side fix.** Making the test wait for the heading's focus would couple it to the defect and leave the behavior unfixed.
- **The browser's part.** Chrome's handling of the interrupted insertion decides only whether the entry is dropped or erased.
- **Native is not affected.** `focusText` uses `AccessibilityInfo.sendAccessibilityEvent` there.

**Route: fix inside P06.1.**

- The Mobile job runs on every full-scope run of PR26, so an occurrence stops P06.1 being verified.
- The cause is proven in app code, and the fix stays inside `apps/mobile/src/` and `apps/mobile/rendered/`.
- The change is full scope.

## Fix

**`apps/mobile/src/components/ui.tsx`:** `focusText` now returns without moving focus when `document.activeElement` is a shown text field. The new `enteringText` helper (lines 21–28, guard at line 38) defines that as:

- an `<input>` whose type is not a button, checkbox, radio, file, range, colour, image, reset, submit or hidden type; or a `<textarea>`; or `contenteditable`; and
- one that currently has layout boxes (`getClientRects().length > 0`), so fields on hidden, retained screens do not count.

Everything else is unchanged:

- the deferred focus still moves to the heading after navigation, and to the alert after a button submit;
- a field on a screen that became hidden has no layout boxes, so focus still moves;
- the native branch is untouched.

**`apps/mobile/rendered/onboarding.spec.ts:181`:** new test, "deferred screen and alert focus leaves a field someone already entered".

1. A `MutationObserver` focuses and selects a field in the same task that shows it, before the next animation frame. This is the order the CI failures needed, made deterministic.
2. After two frames, the test asserts that the field still has focus and that inserted text lands.
3. It covers both sources, mirroring failures #1/#2 and #3:
   - the heading after `birth-back` shows the eligibility screen;
   - the alert after a future birth date is rejected.
4. Both journeys must then advance.

**Not masking:**

- no assertion was weakened, no timeout raised, no retry added and no test skipped;
- `playwright.config.ts`, the workflow and dependencies are unchanged;
- the 83 existing cases are unchanged.

**Behavior change (web only):** if a shown text field has focus when a deferred screen or error focus runs, focus stays in the field. The error is still in the `role="alert"` element inside the polite live region. No existing rendered focus assertion changed: runs 18 and 21 cover the alert-focus checks in `onboarding.spec.ts:47` and `profile-preferences.spec.ts:72`, and the heading checks.

## Ruled out

- **A stale `Pressable` press handler.** React Native Web updates the press configuration in a passive effect. React 19.2 flushes the passive effects of sync-lane commits at the end of the commit (`react-dom-client.development.js`, `pendingEffectsLanes & 3`). Timelines show the submitted values reaching the store. The empty date arrives in a real `input` event.
- **The eligibility owner guard dropping edits** (`eligibility.tsx:29`). The field itself was emptied by the browser, and the store received that empty value.
- **The P05.1 scroll-dismiss path.** `keyboardDismissMode` is `none` on web at the start SHA, and no scroll events come before the focus loss.
- **Misdirected clicks and hidden retained screens.** Timelines show every click and focus on the visible intended control.
- **Load alone as a local reproducer.** 0 failures in the no-trigger runs:

  | Runs | Condition |
  |---|---|
  | 01 | 90 unloaded |
  | 05 | 60 on 2 CPUs with 3 hogs |
  | 08 | 130 started, 4 parallel workers |
  | 02 | 10 started, ×4 CPU throttling |
  | 09 | 30 timing samples |
  | 04 | 2 timeline samples |

  That is 322 started runs in all.

  The gap measurements explain this. The natural window is usually 1–3 ms.

## Proposals outside this session's paths

- **Keep failure evidence in CI.** Capture a trace and a screenshot on failure, either in `playwright.config.ts` or as workflow flags. The Mobile job would then upload `apps/mobile/.work/rendered-results/**` only on failure, with short retention. Traces hold the fixtures' fictional values, while the specs' own diagnostics avoid logging values by design. That trade-off is the manager's decision.
- **Rendered case count.** Records that track the count (83) need 84 after this change.
- **Old diagnostics branch.** `app-builder-1/p05-1-birth-diagnostics` was already recording whether the heading had focus. It can be retired once this change merges.

## Limits

- **Informational browser results.** Every browser result here is from the preinstalled Chromium 1194, not the pinned 1234. Hosted CI remains the rendered acceptance.
- **Reproduction relied on the trigger.** No natural failure occurred locally, and the natural CI rate is not measured. The trigger changes only when the app's own deferred-focus callbacks run; the proof of the fix uses that same trigger.
- **Historical CI failures are attributed by matching, not by capture.** The match covers the screen, the alert, the failing line and the empty-field signature, plus elimination of the alternatives. No CI trace or alert text exists for them. P04.3's and P05.1's failures ran on older code and were not re-run.
- **Browser detail.** The erase-versus-drop detail was observed on Chromium 141; Chrome 151 may differ. The entry is lost either way.
- **Regression test sensitivity.** It failed 10 of 10 before the fix. Under extreme load, the heading's deferred focus could run after the test's two-frame wait, so the test could miss a regression. After the fix it cannot fail through this mechanism, and it passed 20 of 20 under load.
- **Native not tested.** No native or device check was performed; native focus code is unchanged.
- **Documentation count.** The rendered suite is now 84 cases. Documents that quote 83 are outside this session's owned paths.

## Manager verification (App Manager 3, 25 September 2026)

Checked against the pushed branch, not the report alone.

- **Branch and scope.** `claude/trusting-mayer-bw6p40` at `a7ab30bbc17d9ce8fef6f41715ac2f0f2bbaa83f` builds on the start SHA `8d202fd`. It holds two commits, `3fe8742` (fix and test) and `a7ab30b` (this record), and changes exactly the three owned paths. `git diff --check` from the start SHA is clean.
- **Classification.** The trusted `main` policy classifies `8d202fd..a7ab30b` as full scope (`behavior-or-empty`), as expected for a code change.
- **Code read.** The guard is `enteringText` and its one-line check in `focusText` (`apps/mobile/src/components/ui.tsx`). The regression test is at `apps/mobile/rendered/onboarding.spec.ts:181`. Every `file:line` cited for the start SHA was checked there: `ui.tsx:21-31`, `36` and `46-48`; `onboarding/shell.tsx:13-14`; `onboarding/store.ts:223` ("Enter a real civil date that is not in the future.") and `255` ("Check the civil birth date…").
- **Re-run.** In a separate worktree at `a7ab30b`, `npm ci --ignore-scripts` and then `npm run check` in `apps/mobile`, both in an `env -i` process: exit 0, 516 of 516 unit tests passed. The manager did not re-run the browser suites; hosted CI is the rendered acceptance.
- **Integration.** Merged into the manager branch with a merge commit, `8b8b1bdfe5c403686efb44070807dd003a466964`, pushed alone so that hosted CI tests exactly this code.
- **Hosted CI on `8b8b1bd`:** push run [36169923119](https://github.com/amthorn78/glow-dating-app/actions/runs/36169923119) and PR run [36169930205](https://github.com/amthorn78/glow-dating-app/actions/runs/36169930205) passed all six jobs, and the push run's gate says `Application checks passed`. On the pinned Chromium, the rendered suite passed **84 of 84** in 3.9 minutes, the new regression test included. A passing run alone does not show that the intermittent failure is gone (OD-21); acceptance rests on the proven cause, the before-and-after proof and the fix's review.
- **Proposals:**
  - **Failure capture in CI:** recorded as a follow-up in the current handoff, for Nathan to schedule after P06.1. It changes the workflow and the Playwright configuration, so it needs its own full-scope change and review.
  - **Case count:** no living document states the current rendered case count. The records that say 83 are dated and keep their history.
  - **Old diagnostics branch:** `app-builder-1/p05-1-birth-diagnostics` is retired after PR26 merges.
- **Acceptance.** The fix is new code in PR26. OD-21's acceptance needs its own exact-head review of code head `8b8b1bd`, queued after the I1 review (OD-29). Points for that review:
  - with focus kept in a field, the heading is not focused; the alert text stays in the `role="alert"` live region;
  - `enteringText` trusts layout boxes to tell a hidden retained screen from a shown one;
  - the regression test's sensitivity limit under heavy load, noted above.
