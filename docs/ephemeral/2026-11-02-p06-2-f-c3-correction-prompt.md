# P06.2-F correction C3 prompt — what the render-rule check does, as a positive list (DM-39)

- **Owner:** App Manager 9. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 2 November 2026.**
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 3, its section "Correction C3". The design is [DM-39](../continuity/dev-manager/reviews/2026-11-02-dm-39-p06-2-f-render-rule-after-c2.md), sections 4 and 6.
- **Where the result goes:** the session's change to the comment in `apps/mobile/src/chat/display-rule.test.ts` and the record's new "Correction C3" section, on its own branch; the run of record, the Foundation push run on its code commit. The manager verifies it and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at medium.** Effort score 1.22 (confidence 0.78); rung probabilities low 0.06, medium 0.68, high 0.25, extra high 0.01, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.94, Sonnet 5.5 0.06, Haiku 5.5 0.00 (confidence 0.92). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.056, Opus 5.5 at medium 0.639, Opus 5.5 at high 0.235, Opus 5.5 at extra high 0.009, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.004, Sonnet 5.5 at medium 0.041, Sonnet 5.5 at high 0.015, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-02T23:41:52Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (DM-39 section 4.2). C3 changes a test comment and the record only. This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's review of its head follows, then a delta re-review.
- **Deletion condition:** prune after P06.2-F's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C3 of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The render-rule test** (`src/chat/display-rule.test.ts`) checks from source that `src/chat/screen.tsx` and `src/chat/rows.ts` render only contract fields, never a provider-shaped one (ADR 0003). Corrections C1 and C2 built its type check and its planted forms; C2's code head is `816cd60`.
- **C2's own probes** found 49 forms in nine classes (N1 to N9; the record, "Correction C2") that pass the check outside every limit the guarantee then named. N1's X2 is an ordinary refactor: an intermediate component with a narrower prop. Codex found N1 and N8 again.
- **The Dev Manager's DM-39** decided that the checks stay as they are, and the claim changes: the test comment and the record say what the check refuses, as a positive list, and name what it is known to pass. DM-38 section 4's wording, which C2 put in the comment, is withdrawn (DM-39 1.4). View models built by explicit field copy are the structural fix, carried to a later change, before P11 at the latest.

**What you do** is the brief's "Correction C3", Outcome 1 to 3. **The core paragraph,** word for word, which replaces DM-38 section 4's paragraph in the test comment and opens the record's new section:

> **What the check does (DM-39).** It refuses the forms listed below, and its planted forms are that list's specification: a form that evades a listed refusal is a defect, and any other form that passes is a limit, recorded when found. It treats a value as Glow's data while the value's type declares a field in a `GLOW_DATA` file, and it does not check the value once its type declares none, for example after a narrower type declared outside those files; a narrower type built from the contract's own, such as `Pick<>` or `Omit<>`, keeps it Glow's data. The forms it is known to pass are named below; probes found them, and more may exist. It refuses some harmless code, which fails closed. It is a test over two files' source, not a proof. The client validator is the first guard, and view models built by explicit field copy (DM-38 2.5) are the structural fix.

**Then the three lists,** on DM-39 section 4.2's terms:
- **What it refuses:** keep the comment's "What it refuses, in its own terms" list. Make each item name, by ID, the planted forms that pin it.
- **What it is known to pass:** finding 1's class (data held inside another value); N1 to N9, each with one example from the record's table, N1 naming X2 as an ordinary refactor; another module; a template literal's coercion. Say where these came from: C1's exact-head review, its delta re-review, and C2's 256 probe forms.
- **What harmless code it refuses,** each failing closed: F0's family; inferred predicates such as `.filter(text => text !== null)`; Node's `assert`; the source check's path list. Say that the next author changes the design (DM-38 2.5), not the check.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 9. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - **In the test file, change only its comment.** No refusal, exception, planted form or other line changes (DM-39 1.1);
  - **in the record,** add "Correction C3" after "Manager verification of correction C2", and change nothing else in it;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete or force-push a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **No words that claim coverage of code paths** (DM-38 4.2; DM-39 4.2): never write "follows", "any", "every", "all" or "wherever" about what the check covers, in the comment or the record. Name the forms and the limits.
- **The stop rule:** stop and report, with no further change, if the wording cannot be stated truly without changing a check, or if anything seems to need a change outside the comment and the new section, or a dependency.
- **Network:** none beyond the npm registry for `npm ci --ignore-scripts`.
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
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record their versions.
5. **A clean process environment** for every npm command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 816cd607019e69442f99007ef6324c9aa00dd83c HEAD -- .github scripts services apps packages proofs && echo "the code head under correction"
git diff --quiet 816cd607019e69442f99007ef6324c9aa00dd83c origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs && echo "no code on the live branch after 816cd60"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^#+ Correction C3'   # must print 0
```

If a check fails, stop and report.

**Then read, completely:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`; the brief's "Correction C2" and "Correction C3"; the record's "Correction C2" (its N1 to N9 table and false-positive list above all) and "Manager verification of correction C2"; DM-39's report, whole (`docs/continuity/dev-manager/reviews/2026-11-02-dm-39-p06-2-f-render-rule-after-c2.md`); `src/chat/display-rule.test.ts`, whole.

## 3. What to do

1. **The comment** (Outcome 1 and 2): the core paragraph word for word in place of DM-38 section 4's, then the three lists. Check the core paragraph against the brief's text with a script, and record the result.
2. **Prove nothing else changed:** `git diff 816cd607019e69442f99007ef6324c9aa00dd83c HEAD -- apps` shows comment lines only; record how you checked (for example, compiling both versions' test files with comments stripped and comparing).
3. **The local checks,** in `apps/mobile`: `npm ci --ignore-scripts`, then `npm run check`; the test count must be at least 650, and `node --test src/chat/display-rule.test.ts` 21 of 21.
4. **Push the code commit first** and read its Foundation push run with your GitHub tools: every job's conclusion, the gate's line (`Application checks passed`), the `@glow/mobile` unit count, the rendered count and the Mobile job's duration. **Push nothing else until that run has completed** (AM8-20). If the gate's line is not `Application checks passed`, stop and report.
5. **Then the record** (Outcome 3): "Correction C3" after "Manager verification of correction C2", with the core paragraph and the three lists, C2's 49 forms, the candidate's three rules with their measured results and DM-39 section 3's `Pick<>` result kept for option (c)'s brief (DM-39 1.3), a line saying it supersedes C1's and C2's guarantee wording without editing them, the start gate, the environment check (names only), every command with its result line, the run of record, and what you could not run. Commit and push it.

Confirm that `git status` is clean and that `git diff --name-only <START_SHA> HEAD` lists only the two paths.

## 4. Report

Your final message is the report Nathan relays: the prompt revision (revision 1, from `<START_SHA>`), your branch, code head and records head; the start gate's and the environment check's results; the comment's three lists in brief and the script's result for the core paragraph; how you showed that only the comment changed; `npm run check`'s result and count; the run of record (ID, every job, the gate's line, the unit and rendered counts, Mobile's duration); anything that met the stop rule, and what you could not run.
