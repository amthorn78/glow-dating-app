# P06.1 flake fix review prompt — exact-head review of the focus fix

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Revision 1, 26 September 2026.**
- **Direction** (Nathan, 25 September 2026; OD-21): *"CI needs to give us a dependable result. … A passing rerun alone does not resolve an intermittent failure."* The fix is new code in PR26, so its acceptance needs this review.
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Sessions" (the flake diagnosis and the review of the flake fix).
  - Evidence: [flake evidence record](../testing/evidence/2026-09-25-p06-1-rendered-flake-diagnosis.md), with the manager's verification and its review points.
- **Where the result goes:** the manager records the verified review in the flake evidence record, under a new heading "Exact-head review of the fix". The outcome goes into the brief's "Sessions".
- **Reasoning level.** Neither reading gates anything, and Nathan picks.
  - Manager: high.
  - TypeSafe v4: high (score 2.04, P(high) 0.96), with no ultracode flag (P(single session) 0.95).
  - **Used: high.** Nathan started this session on 26 September. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **Result:** approve. The manager verified the report and recorded it on 26 September, in the flake evidence record under "Exact-head review of the fix".
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **No Stream variables** (OD-28): this session never calls Stream.
- **It runs alone** (OD-29, the linear process).
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for the P06.1 rendered-test flake fix** of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

An intermittent failure in the rendered test suite stopped form submits advancing. A diagnosis session found the cause in the app's own code:

- On web, `focusText` moved focus to the screen heading or the error alert one frame after they appeared.
- When a test had just focused a field, the text entered next was erased, so the submit stayed on the same screen with an alert.
- The fix leaves focus in a shown text field that already has it, and adds a regression test.

The manager integrated the fix into PR26's branch with a merge commit.

- **You review one exact head:** `8b8b1bdfe5c403686efb44070807dd003a466964`, that merge commit.
  - Its first parent, `8051c04`, is the manager branch before the merge. Its second parent, `a7ab30b`, is the diagnosis branch's head.
  - The merge added three files' changes: `apps/mobile/src/components/ui.tsx`, `apps/mobile/rendered/onboarding.spec.ts` and the flake evidence record.
- **Your scope is the fix:** those two code files and the evidence record's claims about them.
  - The rest of PR26's code is P06.1-I1's harness under `proofs/stream-chat/`, already reviewed at `9ff600f`; it is not yours.
  - Later commits are Markdown-only manager records, which you read at `<RECORDS_COMMIT>`.
- Nathan started you manually and will relay your report to the manager (App Manager 3). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review capability.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - Keep scratch work outside the repository, or in its ignored paths (`node_modules/`, `apps/mobile/.work/`).
- **Never:**
  - dump the environment;
  - connect to a database, HDE, Railway, Stream or any other provider;
  - run `playwright install`, `eas` or `migrate`.

  The rendered suite runs against local fixtures only.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` should be absent (OD-28): `for n in STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, report its name first in your report, never read or use its value, and continue.
3. Record `command -v node npm npx python3.12` and their versions. Expected: v24.19.0, 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`.
4. Run app commands in a clean process environment, as "Claude Code cloud sessions" in `docs/operations/local-development.md` describes. The diagnosis ran every app and test command as `env -i HOME="$HOME" PATH="$PATH" LANG=C.UTF-8 …` from `apps/mobile`. For `npm ci`, pass the proxy and CA variables through by reference, never printed.
5. **The browser.** Use the Chromium preinstalled under `/opt/pw-browsers`; never download one.
   - If the pinned Playwright cannot find its own browser revision, use an uncommitted scratch configuration in the ignored `apps/mobile/.work/`.
   - That configuration extends `playwright.config.ts` with `launchOptions.executablePath` set to the preinstalled Chromium. The evidence record's "Scratch tooling" describes the one the diagnosis used.
   - The diagnosis used the preinstalled headless shell, Chromium 141. CI installs the revision Playwright pins, Chrome for Testing 151. Say which you used.

## 2. Start gate

```bash
git fetch origin claude/stoic-carson-66gdig main
git switch --detach 8b8b1bdfe5c403686efb44070807dd003a466964
git rev-parse HEAD                      # must print 8b8b1bdfe5c403686efb44070807dd003a466964
git merge-base --all origin/main HEAD   # expected: one line, 0f45e648099b415217938c25d7369164c0101def
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git diff --stat HEAD^1 HEAD             # expected: the three files above, 308 insertions, no deletions
```

If any check fails, stop and report.

Classify three times, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree, and every run uses the same policy file:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base 9ff600fea99cd17e6410b773a618281cc1a79b6b --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only 9ff600fea99cd17e6410b773a618281cc1a79b6b "$head" | grep -v '\.md$'
```

- **The first run** is the head against `main`. Expected: `"full": true`.
- **The second run** is everything after I1's reviewed code head. Expected: `"full": true`. The last command must print exactly the two code files, `apps/mobile/rendered/onboarding.spec.ts` and `apps/mobile/src/components/ui.tsx`. Anything else is non-Markdown code this review would not cover: stop and report it.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`. Anything else means a non-Markdown change landed after the head: stop and report it.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`, and `apps/mobile/AGENTS.md`;
- the diagnosis prompt, `docs/ephemeral/2026-09-25-p06-1-flake-diagnosis-prompt.md`: what the session was asked to do, and its conditions for a fix (its section 5);
- `docs/operations/local-development.md`;
- the whole of `git diff HEAD^1 HEAD`;
- `apps/mobile/src/components/ui.tsx`, whole, and every caller of `focusText`, `ScreenTitle` and `Feedback`;
- how the app shows and hides screens on web: its Expo Router layouts and navigators, and `apps/mobile/src/onboarding/shell.tsx`;
- `apps/mobile/playwright.config.ts` and `apps/mobile/rendered/onboarding.spec.ts`, whole, with its shared helpers;
- `docs/architecture/onboarding-fixtures.md`, the paragraph on the shared `Page` primitive, `ScreenTitle` and `Feedback` (around line 59).

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the flake evidence record, `docs/testing/evidence/2026-09-25-p06-1-rendered-flake-diagnosis.md`, including its last section, "Manager verification";
- the P06.1 brief's "Sessions", `docs/planning/p06-1-chat-provider-proof.md`.

## 3. What to review

1. **Is the fix correct?**
   - Does the guard stop exactly the race the evidence describes, on both paths: the heading (`ScreenTitle`, through `useFocusEffect`) and the error alert (`Feedback`)?
   - `enteringText` decides what a "shown text field" is. Check its input types, `textarea` and `contentEditable`, and the elements it leaves out, such as `select`.
   - It trusts layout boxes (`getClientRects()`) to tell a hidden retained screen from a shown one. Find how this app hides a screen it keeps mounted on web. If a hidden screen can keep layout boxes (through visibility, opacity, a transform or off-screen placement), a field on it would still count as shown. The heading would then never take focus on the new screen.
   - Native behavior must be unchanged.
2. **Accessibility.** The fix changes where focus goes.
   - **A new screen,** when a field already has focus: the heading is not focused. How does a screen-reader user learn that the screen changed? Can a person, not only a test, reach that state?
   - **A validation error:** before the fix, focus moved to the error; now it stays in the field when the person submitted from it, for example with Enter. Is the error still announced, through the alert's role and the live region? What does React Native Web render for `accessibilityRole="alert"` and `accessibilityLiveRegion="polite"`?
   - Check the result against the onboarding-fixtures note, which says that `ScreenTitle` requests focus on route focus and that `Feedback` requests error focus. Report any difference between that note and the behavior as a documentation finding.
3. **Does the regression test prove what it claims?** It is `rendered/onboarding.spec.ts:181`, "deferred screen and alert focus leaves a field someone already entered".
   - It focuses and selects a field when the screen or alert appears, waits two frames, then checks that the field keeps focus and that entered text lands, on both paths.
   - Would it fail without the fix? Confirm it yourself: restore the guard-free `focusText` from the diagnosis's start SHA, `8d202fd02b0064ce4ca281f978b31ce4d07c99d9`, in a scratch copy outside your checkout, such as a temporary `git worktree` at the head, and run the test there. Never commit it, and remove it afterwards. The evidence reports 10 of 10 failures.
   - The evidence names a limit: under extreme load, the heading's deferred focus could run after the test's two-frame wait, so the test could miss a regression. Is that limit acceptable, or is there a sound way to remove it without a timeout or a retry?
   - The diagnosis's conditions still apply: no weakened assertion, no raised timeout, no added retry and no skipped test anywhere in the diff.
4. **Evidence.** Do the evidence record's mechanism, runs and "before and after" claims match the code? Report claims the code or results do not support. This is a full-scope review: never skip a finding because its file ends in `.md`.
5. **Scope of the change.** Only the two code files and the evidence record changed. There is no change to `playwright.config.ts`, the workflow, dependencies, locks or any other file.

**Out of scope:**

- I1's harness under `proofs/stream-chat/`, which has its own review, and the findings from that review;
- failure capture in CI, a recorded follow-up;
- anything in HDE.

## 4. Checks to run

Report the exact commands and results, with counts.

1. `git diff --check HEAD^1 HEAD`.
2. The three classifications above.
3. `npm ci --ignore-scripts` in `apps/mobile`, in a clean process.
4. `npm run check` in `apps/mobile`. The diagnosis reported 516 of 516 unit tests.
5. **The rendered suite on the head, on the preinstalled Chromium:**
   - the full suite once (the diagnosis ran 84 cases);
   - the regression test (`rendered/onboarding.spec.ts:181`) and the two cases that failed before, `rendered/state-corrections.spec.ts:45` and `rendered/onboarding.spec.ts:103`, with `--repeat-each=20`.
6. **The regression test without the fix,** in the scratch copy from section 3, item 3.
7. Anything else you judge necessary, such as the diagnosis's deterministic trigger (its "Scratch tooling") against the head.

The manager reads hosted CI on the reviewed head, so you need not wait for it.

## 5. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`);
- the head you reviewed (`git rev-parse HEAD`) and the three classification outputs;
- **verdict:** "approve" (the fix is sound, and OD-21's acceptance can rest on it) or "changes required";
- **the three review points** from the manager's verification, each answered:
  - with focus kept in a field, is the heading left unfocused, and does the alert text stay in its `role="alert"` live region?
  - is trusting layout boxes to tell a hidden retained screen from a shown one sound in this app?
  - is the regression test's limit under heavy load acceptable?
- **findings,** most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario and a suggested fix;
- the areas you reviewed with no findings;
- every check you ran, with its exact result;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. Change nothing in the repository, on GitHub or in Notion.
