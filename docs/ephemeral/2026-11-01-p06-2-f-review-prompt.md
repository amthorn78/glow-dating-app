# P06.2-F exact-head review prompt — the mobile hardening

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 1 November 2026.**
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 1, "Review plan".
- **Where the result goes:** the report Nathan relays. The manager records it in the P06.2-F record, "Exact-head review of P06.2-F", with a disposition for each finding (fix before the merge, or carry), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.96 (confidence 0.97); rung probabilities low 0.00, medium 0.00, high 0.04, extra high 0.95, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.10, Opus 5.5 0.89, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.85). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.004, Fable 5.1 at extra high 0.095, Fable 5.1 at max 0.001, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.036, Opus 5.5 at extra high 0.845, Opus 5.5 at max 0.009, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.009, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-01T23:24:49Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR40's head and of this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after PR40 merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head code review of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The brief,** `docs/planning/p06-2-f-mobile-hardening.md`: seven fixture-only items from earlier reviews (M05's findings 17 to 20 and P-13; the P06.2 brief's carried follow-ups, DM-29 1.1 with DM-30 2.1 and 2.2; M06's exact-head review, findings 5 and 6, with DM-36 section 6), each with a test and the reversal that fails it. No guard's allowance and no dependency may change (D2, D3).
- **The implementation** (branch `claude/practical-wozniak-fg1e2i`, code head `3db50d8`, records `02f1972`; record `docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`): items 1 to 7 done; optional entries done or not, with reasons; some additions beyond the brief's lists (the record says which).
- **Its run of record,** push run 41359462167 on `3db50d8`: all eight jobs passed, the gate printed `Application checks passed`, and the rendered suite passed 97. An earlier run on the same commit was cancelled by the session's own records push (AM8-20).
- **The manager verified it** (the record, "Manager verification"): six reversals re-run in a scratch copy, each failing, and 649 of 649 unit tests.

**The code head under review is `3db50d8`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `3db50d8` (the start gate checks this).

**Your scope:**
- `git diff 67b02013a954c441f1d84d6a82da43a6afcf4009 3db50d876e2c9423d25ee197735855a77228f93c`: 25 paths under `apps/mobile`.
- **The P06.2-F record,** with its "Manager verification", against the code and the runs.
- **The runs:** run 41359462167, and the PR run on PR40's final head (event `pull_request`) once it has finished.
- **Out of scope:** code this item does not change. A finding there is reported as pre-existing, not as a defect of this item.

**The focus:**
1. **No guard allows anything new** (D2):
   - `src/config/release-guard.ts` and the layout's call: is `developmentPreviewAvailable(__DEV__, mode)` exactly the old `!__DEV__ || mode !== 'fixture'` negated, and does Expo still inline the mode where the layout passes it?
   - `app.config.ts`: a comment change only?
   - the route guards (`src/app/_layout.tsx`'s `Stack.Protected` guards, `src/onboarding/routes.ts`): unchanged in what they allow?
   - the closed-conversation row: can any path still open a `closed` conversation, by a link, the back stack or a stale selection?
2. **No test is weakened.** In every changed test file, no assertion is removed or loosened; each new test fails under the reversal the record names; and none could pass while the behavior it guards is wrong. Pay attention to source-reading tests (the screen's field reads, the provider-wording scan, the unimported-module test): could a plausible edit defeat them silently, or could they fail on harmless code?
3. **The behavior changes are the ones the brief asked for, and are correct:**
   - **the older-page state** after a newest-page reload (`src/chat/store.ts`): matches the P06.2 brief's carried entry and DM-29 1.1, including the ordering in the gap (DM-30 2.1) and the held-page case (DM-30 2.2);
   - **the draft restore** after a final send refusal: restored only when the refusal leaves access open and no new draft was started; never across a revocation, an account change or a conversation change; the retry and idempotency semantics unchanged;
   - **optional finding 9, not done:** is the session's reason right, that the line also sends a queued revalidation read for a hidden conversation?
4. **The removals:** `src/hooks/use-recommendations.ts` and `src/data/fixtures.ts` have no remaining importer, the root smoke script and `src/data/recommendations.ts` included.
5. **The display rule and the copy:** no provider name in member-visible copy (ADR 0003, decision 3); the copy test covers every copy table in `src/chat/copy.ts`.
6. **Item 7:** the two assertions pin the landing (account entry, the reset's error visible; the reset screen's count 0 without the visible filter), and no navigation changed.
7. **The README** says what the code does.
8. **The records:** every claim in the record and its "Manager verification" holds against the code and the runs.

**What comes after this review: the correction classes.** Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a test pass where it should fail, or weaken what a test proves;
- let a guard allow what it did not allow at `67b0201`;
- change runtime behavior beyond what the brief's items ask;
- add a dependency, or change a lock;
- put a provider's name, a credential or a provider-shaped field in member-visible output;
- make a record claim more than the code, the tests or the runs show;
- leave a condition the brief carries (DM-29 1.1, DM-30 2.1 and 2.2, DM-36 section 6) unmet at this head.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 8. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:** the npm registry only, for `npm ci --ignore-scripts` in a scratch copy.
- **Rendered tests:** CI's run is the evidence. You may run the suite locally against the container's preinstalled Chromium, with a scratch config outside the checkout. Such a run is informational only. Never run `playwright install`.
- **Never:**
  - dump the environment, or print a credential, token or password;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas` or `migrate`, or a package install script.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 05f4c3a0f78e72a5782fef62db4ef186a8558ac3
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 3db50d876e2c9423d25ee197735855a77228f93c HEAD -- .github scripts services apps packages proofs && echo "the code head under review"
git diff --quiet 3db50d876e2c9423d25ee197735855a77228f93c origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs && echo "no code on the live branch after 3db50d8"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^#+ Exact-head review of P06.2-F'   # must print 0
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, if a non-Markdown path changed there after `3db50d8`, or if this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`;
- the brief, and the P06.2 brief's "Carried to later changes" (`docs/planning/p06-2-chat-integration.md`);
- the P06.2-F record, whole;
- ADR 0003 (`docs/adr/0003-chat-display-rule.md`);
- every file in the diff, whole, with `src/chat/store.ts` and its tests above all.

**The runs,** with your GitHub tools:
- run 41359462167: every job's conclusion, the gate's line, the Mobile job's rendered result and duration;
- the PR run on PR40's final head, if it has finished.

## 3. What to do

1. Review the diff against the focus, item by item.
2. Re-run, in a scratch copy of `3db50d8`, `npm ci --ignore-scripts` and `npm run check` in `apps/mobile`, and any reversal you doubt.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 8), one or two lines each;
- what you ran, and what you could not run or read.
