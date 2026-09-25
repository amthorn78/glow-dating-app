# P06.1 flake diagnosis prompt — the intermittent rendered-test failure

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Direction** (Nathan, 25 September 2026; OD-21): *"CI needs to give us a dependable result. Investigate the failure now. If it is caused by this work or prevents this work from being verified, fix it as part of the current item. If it is unrelated, create a focused repair item and treat reliable CI as a prerequisite for accepting the affected work. A passing rerun alone does not resolve an intermittent failure."*
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Sessions" (the rendered-test flake diagnosis) and "Owned paths".
- **Where the result goes:**
  - the session writes `docs/testing/evidence/2026-09-25-p06-1-rendered-flake-diagnosis.md`;
  - the manager adds its verification there;
  - the manager records the outcome and its route in the brief's "Sessions": a fix inside P06.1, or a focused repair item.
- **Reasoning level.** Neither reading gates anything, and Nathan picks.
  - Manager: max.
  - TypeSafe v4: max (score 3.81, P(max) 0.89), with no ultracode flag (P(single session) 0.88).
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **It runs beside the I1 review.** The two sessions share no files, and this one makes no provider call.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this prompt.

---

You are the **diagnosis session for an intermittent failure in the Glow dating app's rendered test suite**, in private repository `amthorn78/glow-dating-app`. This work is part of P06.1, the current work item.

Nathan's direction, 25 September 2026: *"CI needs to give us a dependable result. Investigate the failure now. If it is caused by this work or prevents this work from being verified, fix it as part of the current item. If it is unrelated, create a focused repair item and treat reliable CI as a prerequisite for accepting the affected work. A passing rerun alone does not resolve an intermittent failure."*

- Nathan started you manually and will relay your report to the manager (App Manager 3). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - diagnose first;
  - fix only under section 5's conditions;
  - write only your owned paths (section 6);
  - push only your own session branch. On GitHub do nothing else: no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment;
  - connect to a database, HDE, Railway, Stream or any other provider;
  - run `playwright install`, `eas` or `migrate`.

  The rendered suite runs against local fixtures only.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. The `STREAM_*` variables may be present or absent. This session never uses them.
3. Record `command -v node npm npx python3.12` and their versions. Expected: v24.19.0, 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`.
4. Run app commands in a clean process environment, as "Claude Code cloud sessions" in `docs/operations/local-development.md` describes.
5. **The browser.** Use the Chromium preinstalled under `/opt/pw-browsers`; never download one.
   - If the pinned Playwright cannot find its own browser revision, use an uncommitted scratch configuration in the ignored `apps/mobile/.work/`.
   - That configuration extends `playwright.config.ts` with `launchOptions.executablePath` set to the preinstalled Chromium.
   - The M02 evidence record's "Rendered suite (informational only)" paragraph describes one such run: 83 passed in 4.7 minutes.

## 2. Start gate

```bash
git fetch origin claude/stoic-carson-66gdig
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
```

If any check fails, stop and report. Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`, and `apps/mobile/AGENTS.md`;
- the P06.1 brief's "Sessions" and "Owned paths";
- `docs/operations/local-development.md`;
- `apps/mobile/playwright.config.ts`, and the rendered specs `apps/mobile/rendered/state-corrections.spec.ts` and `apps/mobile/rendered/onboarding.spec.ts`, including their shared helpers;
- the screens, stores and form components that those two cases drive, from the eligibility screen through the birth screen to the remaining-steps screen;
- the earlier diagnosis and fix, listed in section 3;
- the Foundation workflow's Mobile job in `.github/workflows/foundation.yml`, to know what CI runs and what it keeps.

## 3. What is known

One kind of failure has occurred three times: **a form submit that does not advance to the next screen.** Each time, the parallel run on the same code passed.

| # | Run and job | Case | Symptom |
|---|---|---|---|
| 1 | PR run [35991614536](https://github.com/amthorn78/glow-dating-app/actions/runs/35991614536), attempt 1, Mobile job 107606799357 (24 September, PR14) | `rendered/state-corrections.spec.ts:45` ("eligibility correction replaces an obsolete unsaved birth draft") | Stayed on eligibility, with an alert showing. The alert's text and input state were not captured |
| 2 | PR run [36020836838](https://github.com/amthorn78/glow-dating-app/actions/runs/36020836838), Mobile job 107706842358 (24 September, M02, head `022929d`) | The same case | After `adult-date` was filled with `1992-07-16` and `eligibility-submit` was clicked, `screen-birth` was not visible within 10 s (line 57). Logged diagnostics: the visible screen was `screen-eligibility`; birth controls `submitCount: 0`, no date or place fields; `visibleAlertPresent: true`. The alert text is not in the log |
| 3 | Push run [36025919795](https://github.com/amthorn78/glow-dating-app/actions/runs/36025919795) (24 September, M02, head `9280bdc`) | `rendered/onboarding.spec.ts:103` ("private birth journey validates input, preserves uncertainty and stops before profile discovery") | After `birth-submit`, `screen-remaining` did not appear within 10 s (line 113) |

- **The records:** the M02 evidence record (`docs/testing/evidence/2026-09-24-m02-claude-setup.md`, around "Failure preserved" and "PR18 CI before integration") and `docs/continuity/history/AB1-R012.md` (the PR14 candidate paragraph).
- **An earlier, related fix.** P05.1's post-merge correction found that React Native Web's `ScrollView` dismissed the keyboard on scroll events, which blurred the active birth field. The shared page now uses `keyboardDismissMode="none"` on web. See `docs/testing/p05-1-checkpoint.md`, "Post-merge web birth-field focus correction".
- **Earlier diagnostics** are on the unmerged branch `app-builder-1/p05-1-birth-diagnostics`: commits `f0680fa` ("diagnose inherited birth journey event delivery") and `6ad567c` ("reproduce focus loss through the actual web scroll handler"). Read them; don't merge them.
- **What CI keeps:**
  - `playwright.config.ts` sets `retries: 0`, `workers: 1`, `trace: 'off'`, `screenshot: 'off'` and a 10 s expect timeout;
  - the workflow uploads only two layout screenshots, so a failure leaves no trace, no `error-context.md` and no alert text.
- Neither earlier investigation found a cause. None of the three commits changed mobile code.

These are leads, not conclusions. Establish the cause from evidence.

## 4. The diagnosis

1. **Reproduce.**
   - Run the two cases repeatedly, for example with `--repeat-each`, and record the counts.
   - If they don't fail, raise the pressure until they do or you have a clear negative result. Useful ways:
     - CPU throttling through the Chrome DevTools Protocol;
     - a loaded machine;
     - slowed network or bundle serving;
     - timing changes in the test's own steps, used only as probes and never as the fix.
   - In your scratch configuration, turn on traces and screenshots on failure, and capture the alert's text and the form's state at the moment of failure.
2. **Explain.** Identify the mechanism: which state or event is lost, reset or reordered, in which component, and why only sometimes. Show it with evidence: a reproducible trigger, logs or traces, and code references with `file:line`.
3. **Classify the cause:**
   - **(a)** a defect in the app's code that the test exposes;
   - **(b)** a defect in the test, such as acting before the screen is ready or a selector that can match a leaving screen;
   - **(c)** an environment or tooling effect that the app and test cannot control;
   - **(d)** not found, with what you ruled out and why.
4. **The route,** from Nathan's direction. The Mobile job runs on every full-scope run of PR26, so a red occurrence stops P06.1 being verified. A proven cause in (a) or (b) is therefore fixed inside P06.1, under section 5. For (c) or (d), make no fix. Propose the next step, for example a focused repair item or better failure capture in CI.

## 5. Fix, only under all of these conditions

- The cause is proven, not supposed.
- The fix is confined to the files under `apps/mobile/src/` and `apps/mobile/rendered/` that the cause requires.
- **No masking.** No assertion is weakened, no timeout is raised, no retry is added and no test is skipped.
- **No other file.** You don't change `playwright.config.ts`, the workflow, dependencies or any other file. Propose such changes in your report instead.
- **Proof that it works:**
  - under the same trigger that reproduced the failure, the failure occurs before the fix and does not occur after it;
  - repeated runs of both cases pass, at least 20 each, with the counts reported;
  - one full rendered suite passes;
  - `npm run check` passes in `apps/mobile`.
- A regression test that exercises the mechanism, where one is practical.

If any condition cannot be met, don't fix. Report the proposal instead.

## 6. Owned paths and records

- **Always:** `docs/testing/evidence/2026-09-25-p06-1-rendered-flake-diagnosis.md` (new). It records:
  - the start SHA and environment;
  - every command, with its counts and results;
  - the reproduction method and rate;
  - the mechanism with its evidence;
  - the classification and route;
  - the fix and its proof, if any;
  - what you ruled out;
  - limits.
- **Only with a fix under section 5:** the files under `apps/mobile/src/` and `apps/mobile/rendered/` that it requires.
- **Scratch work** stays in ignored paths such as `apps/mobile/.work/`. Commit none of it.
- Commit on your own session branch and push it. Retry up to four times with backoff on a network error.

## 7. Report

Your final message is the report Nathan relays:

- the branch, start SHA, head SHA and changed paths;
- the environment check;
- **the cause:** its classification (a)–(d) and the mechanism, with evidence and `file:line`;
- **the reproduction:** method, rate before any fix, and the trigger;
- **the fix:** what changed and why it is not masking, with the before-and-after proof and the repeat counts. If there is no fix, say why, and give your proposal;
- **the route:** a fix inside P06.1, or a focused repair item, with the reason;
- every check you ran, with its exact result;
- proposals outside your owned paths, such as capturing failures in CI;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. A passing rerun is not a resolution.
