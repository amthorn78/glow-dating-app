# P06.2-F review prompt — C4's narrowed words and repair pass C5, on S2's terms (DM-41 5.1 to 5.3)

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 8 November 2026.**
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 5, "Correction C4" (its "Review" line) and "Repair pass C5" (its "Review" line). The terms are [DM-41](../continuity/dev-manager/reviews/2026-11-08-dm-41-p06-2-f-c4-run-failure.md) 5.1 to 5.3 and [DM-40](../continuity/dev-manager/reviews/2026-11-08-dm-40-p06-2-f-c3-review-and-od-57.md) 3.1 to 3.4. C5 changes 48 non-test lines, so this is one review on M05 S2's terms (manager workflow, step 6): each path read whole at the head, with the security focus.
- **Where the result goes:** the report Nathan relays. The manager records it in the P06.2-F record, "Review of C4 and repair pass C5", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.07 (confidence 0.81); rung probabilities low 0.00, medium 0.11, high 0.71, extra high 0.18, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.110, Opus 5.5 at high 0.710, Opus 5.5 at extra high 0.180, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-08T13:02:01Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR40's head, which holds this prompt and C5's code (manager workflow, step 6).
- **Deletion condition:** prune after PR40 merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review of correction C4 and repair pass C5 of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The render-rule test** (`apps/mobile/src/chat/display-rule.test.ts`) checks from source that `src/chat/screen.tsx` and `src/chat/rows.ts` render only contract fields (ADR 0003). Its comment states, under DM-39, what the check refuses as a positive list, and what it is known to pass.
- **C3's delta re-review** found three forms that evade listed refusals and two false statements. **DM-40** kept the checks unchanged and narrowed the listed items to its section 4.2's syntax-exact words, with four new known passing classes.
- **Correction C4** (code head `691dfba`) put DM-40's words into the comment and renamed the first render test; outside comments only that test name changed (the manager's verification; DM-41 section 9). Its push run failed in two jobs it does not touch, and its session was archived before it recorded its work.
- **DM-41** traced the rendered failure (`profile-preferences.spec.ts:321`, about 1 run in 16) to the test's `page.goBack()` racing the app's own post-logout history clean-up, and the recurring `setup-python` `504` to GitHub's download endpoint. It approved **repair pass C5**: one wait in the spec, one bounded retry of the Python install, C4's code verified by C5's own run, and C4's record finished by C5.
- **Repair pass C5** (branch `claude/inspiring-ride-chqpjx`, code head `7f1df9615b10e844dc252b9111b3c4c5b67b0b37`, records `e4f9728`): the record's "Correction C4 (written by repair pass C5)" and "Repair pass C5". Its run of record, push run 42481684565 on `7f1df96`: all eight jobs passed, `Application checks passed`, 650 of 650 unit tests, rendered 97 passed; no retry fired.
- **The manager verified it** (the brief's "Sessions", C5's entry) and merged it. The CI policy gained DM-41 2.4's paragraph ("Toolchain installs are retried once"), governing Markdown for the Dev Manager, not under this review.

**The code head under review is `7f1df96`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `7f1df96` (the start gate checks this).

**Your scope (every path read whole as it stands at the head, not the diff alone):**
- `apps/mobile/src/chat/display-rule.test.ts` (C4's comment and test name). Guide: `git diff f87e8b19110544b1ceddfc1afd44a8492350fb81 691dfbad0ab38d60ba2eb0d9715512c85b5aaccf`.
- `apps/mobile/rendered/profile-preferences.spec.ts` (C5's wait and comment). Guide: `git diff 691dfbad0ab38d60ba2eb0d9715512c85b5aaccf 7f1df9615b10e844dc252b9111b3c4c5b67b0b37 -- apps/mobile/rendered`.
- `.github/workflows/foundation.yml` (C5's retry), whole. Guide: the same diff, `-- .github`.
- The P06.2-F record (`docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`): "Correction C4: the stop, and the manager's verification", "Correction C4 (written by repair pass C5)" and "Repair pass C5", checked against the code, the runs and DM-40 and DM-41.
- **The runs:** run 42481684565, and the PR run on PR40's head (event `pull_request`) once it has finished.
- **Read as context, not under review:** `src/chat/screen.tsx`, `src/chat/rows.ts`, the logout handlers and Expo Router's history adapter as the record cites them.

**The focus (DM-41 5.2; the security focus is the display rule, that no provider-shaped field reaches member-visible output, and the CI gate's integrity, that green still means every check passed):**
1. **C4's items under DM-40 3.1 to 3.4, unchanged.**
   - **3.1:** probe each narrowed item at its exact words, with forms just inside them: an arrow, a function expression, a reference and `{ key }`, each as a property of a literal that has a contextual type; `.map(view.line)`; an `=` destructuring assignment; a destructuring default whose pattern the initializer types. A form inside the words that evades is a finding.
   - **3.2:** each new known-passing class's example passes as written; the `VirtualizedList` reason is true; only comments changed apart from the test name's string (show it your own way, for example parse trees without comments).
   - **3.3:** do not re-probe the unchanged items; any other passing form is a records line.
   - **3.4:** a form inside the narrowed words is reported, and it goes to the Dev Manager before any further correction.
   - No words that claim coverage of code paths (DM-38 4.2): no "follows", "any", "every", "all" or "wherever" about what the check covers.
2. **The diagnosis:** the record's trace supports the mechanism it states (the app's `replaceState('/')`, `goBack()` resolving on it, `history.go(-2)`, the tab's initial `about:blank`). You may reproduce it informationally against the container's Chromium from an uncommitted configuration outside the checkout; never `playwright install`.
3. **The spec:** one wait added, nothing removed, loosened or moved, and its comment true. The scan (13 `page.goBack()` calls) is complete and its two "no wait" calls (`:139`, `:191`) are correctly left alone.
4. **The workflow, against DM-41 2.1 to 2.3:**
   - only `actions/setup-python` is retried, once, after a fixed pause, at the same pin and version, in the jobs that use it;
   - no checkout, dependency install, check, test or proof step is retried or made `continue-on-error`;
   - a failure of the retry fails the job, and the first failure is visible in the log;
   - permissions, triggers, concurrency, timeouts, the six job names and the gate's logic are unchanged; no new action or pin;
   - read the YAML against GitHub's documented semantics of `continue-on-error`, `steps.<id>.outcome` and `steps.<id>.conclusion`, including what the gate's job-level `needs` result sees when a first attempt fails and the retry passes (DM-41 2.5: no deliberately failing run is pushed).
5. **The record sections:** true to the code, the runs and DM-41, claiming no more than they show. That includes "Correction C4"'s provenance (DM-41 4.2), its words as `691dfba` carries them, nits 6 and 7 and DM-40 1.3's forms; and "Repair pass C5"'s counts, its browser, its limits and its `npm ci` deviation.

**What comes after this review: the correction classes.** Report every finding with its severity. A further correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a form evade a refusal the comment lists (DM-39 1.2; DM-40 3.4 routes it to the Dev Manager first);
- weaken what any test proves, or make one pass vacuously;
- let the Foundation gate pass when a check or test did not pass, or retry anything beyond the Python install;
- add a dependency, change a lock, or change runtime code;
- make the comment or a record claim more than the code, the tests or the runs show.

A runtime change found by the diagnosis stops the work and goes to the Dev Manager with its own full review (DM-41 5.3). Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout. Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:** the npm registry only, for `npm ci --ignore-scripts` in a scratch copy, and GitHub through your tools to read runs.
- **Never:**
  - dump the environment, or print a credential, token or password;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas` or `migrate`, or a package install script.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (C5 found `npm ci` also needs the proxy and certificate variable names passed through by reference; never print them).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 7f1df9615b10e844dc252b9111b3c4c5b67b0b37 HEAD -- . ':(exclude)*.md' && echo "the code head under review"
git diff --quiet 7f1df9615b10e844dc252b9111b3c4c5b67b0b37 origin/claude/magical-wozniak-yfmmx2 -- . ':(exclude)*.md' && echo "no code on the live branch after 7f1df96"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^#+ Review of C4 and repair pass C5'   # must print 0
```

If any check fails, stop and report: the prompt is stale.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`; the CI policy; the brief's "Correction C4" and "Repair pass C5"; DM-40's report, sections 3 to 6; DM-41's report, whole; the record sections named in the scope; the three files in scope, whole.

## 3. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), the head reviewed, the start gate's and the classification's results, and the environment check;
- a verdict: **approve**, or **changes required**;
- each finding with its severity, its evidence (the form or command and its result), and whether it falls in a correction class;
- focus items 1 to 5, each with what you checked and found;
- the runs you read, with IDs and results;
- what you could not check, and why.
