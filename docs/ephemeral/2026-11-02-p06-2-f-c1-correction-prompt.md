# P06.2-F correction C1 prompt — the render-rule check, the copy test's word list and the record

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 2 November 2026.**
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 1, its section "Correction C1". The findings are in the record, [`docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`](../testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md), "Exact-head review of P06.2-F".
- **Where the result goes:** the session's change to `apps/mobile/src/chat/display-rule.test.ts` and its record's corrections and new "Correction C1" section, on its own branch; the run of record, the Foundation push run on its code commit. The manager verifies it and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.61 (confidence 0.74); rung probabilities low 0.00, medium 0.39, high 0.61, extra high 0.00, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.91, Sonnet 5.5 0.09, Haiku 5.5 0.00 (confidence 0.88). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.355, Opus 5.5 at high 0.555, Opus 5.5 at extra high 0.000, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.035, Sonnet 5.5 at high 0.055, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-02T02:44:00Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. C1 changes one test within the design the brief accepted, and no runtime code, guard, contract, dependency or interface; step 6's rule decides its disposition (the brief, "Correction C1"). This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's review of its head follows, then a delta re-review.
- **Deletion condition:** prune after P06.2-F's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C1 of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.** P06.2-F's implementation (code head `3db50d8`) closed seven fixture-only items in `apps/mobile`, each with a test and the reversal that fails it. Its exact-head review asked for changes in one test and the record; the runtime code is correct and needs no change.
- **Finding 1 (should fix, in a correction class).** Item 2's render-rule check in `src/chat/display-rule.test.ts` (`renderedPaths` and `renderRuleViolations`, about lines 133 to 160 at `3db50d8`) reads only the paths reached through six variable names: `message`, `conversation`, `list`, `state`, `match` and `row`. Two probes passed `tsc` and the test while rendering a provider-shaped field:
  - **PA:** in `screen.tsx`, `MessageRow`'s binding renamed (`{ message: item, name, rowRef }`, with `item.` for `message.` in its body), rendering `{'name' in item ? String(item.name) : null}`;
  - **PB:** a helper component whose loosely typed prop `{ name?: string; text: string | null }` renders `entry.name`, used as `<Eyebrow entry={message} />`; it passes ESLint too.

  The record's "Source-reading tests" limit says only "a determined edit" evades the check; a plain rename does.
- **Finding 2 (nit, taken here because it is the same file).** The copy test's word list (`display-rule.test.ts:18`) has no plurals and lacks `cloudflare` and `allauth`, which item 3's list in `src/components/provider-wording.test.ts` has.
- **Findings 5, 6, 8 and 10 (nits in the record):**
  - **5:** item 5's "unless the member started a new one while it was pending" is wrong, since the composer cannot be edited while a send is pending (`screen.tsx`, `editable={!pending}`). The case arises through Retry: a draft typed after a retryable failure, then a final refusal on the retry;
  - **6:** the run of record's Mobile time is 5 min 58 s (22:54:52 to 23:00:50 UTC), not 5 min 56 s;
  - **8:** the checker is tested against nine planted forms, not seven;
  - **10:** "Expo still inlines the mode there" is imprecise. A development bundle reads the mode through Expo's env module (`_expoVirtualEnv.env.EXPO_PUBLIC_GLOW_MODE`), the same rewrite the two unchanged reads get (`onboarding/context.tsx`, `discovery/context.ts`).

**What you do** is the brief's "Correction C1", Outcome 1 to 3. Follow it.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 8. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only `apps/mobile/src/chat/display-rule.test.ts` and the record `docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`. In the record, change only the session's own sections, and add "Correction C1" before "Manager verification". Never edit "Manager verification" or "Exact-head review of P06.2-F";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete or force-push a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - closing finding 1 seems to need a change to `screen.tsx`, `rows.ts` or any path outside the two above;
  - it seems to need a dependency or a lock change (the brief's D3; `typescript` is already a devDependency and may be imported by the test);
  - a stronger check fails on today's `screen.tsx` or `rows.ts` in a way you cannot allow by a named exception in the test.
- **Network:** none beyond the npm registry for `npm ci --ignore-scripts`.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas`, `eas-cli` or `migrate`;
  - run package install scripts: always `npm ci --ignore-scripts`;
  - weaken or delete a test or a planted form to make the suite pass.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH in every process. Record `node --version` and `npm --version`.
5. **A clean process environment** for every npm and Expo command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. The proxy and CA variables pass by reference, never printed (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 3db50d876e2c9423d25ee197735855a77228f93c HEAD -- .github scripts services apps packages proofs && echo "the code head under correction"
git diff --quiet 3db50d876e2c9423d25ee197735855a77228f93c origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs && echo "no code on the live branch after 3db50d8"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^#+ Correction C1'   # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, if a non-Markdown path changed there after `3db50d8`, or if the record already holds "Correction C1".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `apps/mobile/CLAUDE.md`;
- the brief, whole, and its "Correction C1" above all;
- the record, whole, with "Exact-head review of P06.2-F";
- ADR 0003 (`docs/adr/0003-chat-display-rule.md`);
- `src/chat/display-rule.test.ts`, `src/chat/screen.tsx`, `src/chat/rows.ts` and `src/components/provider-wording.test.ts`, whole.

## 3. What to do

1. **Finding 1.** Make the render-rule test fail on PA, PB and PC (the brief's Outcome 1), each added to the test's planted list beside the nine there today. The nine must still fail, and today's `screen.tsx` and `rows.ts` must still pass. You choose the mechanism: a read of provider-shaped property names through any binding with named exceptions, plus a refusal of the `in` operator on a string literal; or a type-aware check built on the installed TypeScript compiler. Keep the test's existing checks unless the new one covers them and you say so.
2. **Each planted form is a reversal.** Run each one also as an edit to `screen.tsx` in a scratch copy of `apps/mobile` outside the checkout: the test must fail with the edit in place and pass once it is undone. Record each edit and its failing output. Then try at least two forms of your own that the check should catch, and name every form you know still evades it.
3. **Finding 2.** Widen the copy test's word list as the brief's Outcome 2 says. Its reversal: `READ_COPY.unavailable` changed to "Our providers cannot show this conversation." fails the test, then is restored.
4. **The local checks,** in `apps/mobile`: `npm ci --ignore-scripts`, then `npm run check` (typecheck, lint, every unit test). Record the test count; it must be at least 649.
5. **Push the code commit first,** with `git push -u origin <branch>`, and read its Foundation push run with your GitHub tools: every job's conclusion, the gate's line (`Application checks passed`), the rendered suite's count in the Mobile job, and the Mobile job's duration against its 25 minutes. **Push nothing else until that run has completed** (AM8-20): a newer push cancels the run in progress. If the gate's line is not `Application checks passed`, stop and report.
6. **Then the record** (the brief's Outcome 3): correct item 2's row and the "Source-reading tests" limit, and findings 5, 6, 8 and 10. Mark each correction "[Corrected in C1: …]", giving the old wording. Add "Correction C1": the start gate's results, the environment check (names only), the toolchain versions, the change, each reversal with its failing output, every command with its result line, the run of record (ID, each job, the gate's line, the rendered count, Mobile's duration), and what you could not run. Commit and push it.

Commit each logical step with a clear message ending in the session's attribution lines. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only the two paths.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and your records head;
- the start gate's and the environment check's results;
- the mechanism you chose, and why; each planted form and reversal with its result; the forms you know still evade the check;
- finding 2's change and its reversal;
- `npm run check`'s result and test count, and the run of record: its ID, every job, the gate's line, the rendered count and the Mobile job's duration;
- the record's corrections, by finding;
- anything that met the stop rule, and what you could not run.
