# P06.2-F review prompt — correction C6, on S2's terms (DM-42 5.1 to 5.3)

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 8 November 2026.**
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 6, "Correction C6" (its "Review" line). The terms are [DM-42](../continuity/dev-manager/reviews/2026-11-08-dm-42-p06-2-f-c5-review-findings.md) 5.1 to 5.3, held to DM-39 1.2 for the text that changes. C6 changes comment lines only, so this is one delta review on M05 S2's terms (manager workflow, step 6).
- **Where the result goes:** the report Nathan relays. The manager records it in the P06.2-F record, "Delta review of correction C6", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.81 (confidence 0.73); rung probabilities low 0.00, medium 0.30, high 0.59, extra high 0.11, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.297, Opus 5.5 at high 0.584, Opus 5.5 at extra high 0.109, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.003, Sonnet 5.5 at high 0.006, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-08T16:06:48Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR40's head, which holds this prompt and C6's code (manager workflow, step 6).
- **Deletion condition:** prune after PR40 merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta review of correction C6 of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The render-rule test** (`apps/mobile/src/chat/display-rule.test.ts`) checks from source that `src/chat/screen.tsx` and `src/chat/rows.ts` render only contract fields (ADR 0003). Its comment states, under DM-39, what the check refuses as a positive list, and what it is known to pass. The check's code has not changed since C2; DM-39 1.1 froze its design.
- **The review of C4 and repair pass C5** (code head `7f1df96`) found two forms inside C4's narrowed inline-callback words that pass the render test: a function expression with a declared `this` parameter (finding 1) and a parameter after a rest parameter of the contextual signature (finding 2). It also found a false word-check sentence in C5's record section (finding 3) and a `VirtualizedList` reason narrower than the comment says (finding 4).
- **DM-42** approved option (a): words that state the inline rule's pairing as the code does it, the two forms and a third (F3) named as known passing classes, finding 3's correction line and finding 4's sentence, in its own words. It declined changing the check, and carried the fix to option (c), view models built by explicit field copy.
- **Correction C6** (branch `claude/charming-albattani-o8i1cb`, code head `6913cc06822b6f26c185ea525ce3b3f28a3a5eca`, records `e0910c7`): DM-42 1.1, 1.2 and 3.1 word for word in the comment, with no narrowing, and the record's "Correction C6". Its run of record, push run 42494621474 on `6913cc0`: all eight jobs passed, `Application checks passed`, 650 of 650 unit tests, rendered 97 passed; no retry fired. Its own probes add T1 (a declared `this` against a signature whose only parameter is a rest parameter: passes, as the words predict) and U1 (a union contextual type: refused).
- **The manager verified it** (the record, "Manager verification of correction C6": the words by script, the comment-free parse trees, F1 to F5, F7, F8 and T1 re-run, the run's jobs and logs) and merged it at `80383d8`. Before C6, the manager added DM-42 4.1's line to the CI policy's "Toolchain installs are retried once" paragraph.

**The code head under review is `6913cc0`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `6913cc0` (the start gate checks this). Line numbers below are at `6913cc0`; DM-42 cites the same code at `7f1df96`, 13 lines earlier (its `:476-486` is `:489-499` here, and its `:375-387` is `:388-400`).

**Your scope (each path read whole as it stands at the head, not the diff alone):**
- `apps/mobile/src/chat/display-rule.test.ts`: C6's comment changes, read against the code they describe. Guide: `git diff 7f1df9615b10e844dc252b9111b3c4c5b67b0b37 6913cc06822b6f26c185ea525ce3b3f28a3a5eca`.
- The P06.2-F record (`docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`): "Correction C6" and "Manager verification of correction C6", checked against the code, the run and DM-42.
- The CI policy's (`docs/operations/ci-and-branch-policy.md`) "Toolchain installs are retried once" paragraph: DM-42 4.1's line only, against the workflow's retry steps (`.github/workflows/foundation.yml`, read as context).
- **The runs:** run 42494621474, and the PR run on PR40's head (event `pull_request`) once it has finished.
- **Read as context, not under review:** `src/chat/screen.tsx`, `src/chat/rows.ts`, and the rest of the test file's code.

**DM-42's terms for this review, as written (section 5):**

> **Agreed:** a delta review on S2's terms of the next correction's code head, after Codex has completed on that head and on the commit that holds its prompt (step 6), held to DM-39 1.2 for the text that changes.
>
> - **5.1 What it checks:**
>   - the callback sentence against the inline rule (`:476-486`), place by place;
>   - that F1, F2 and F3 pass as written;
>   - that at least F4, F5, F7 and F8 are refused, as the words say;
>   - finding 4's line, against V1 to V3 or its own forms;
>   - finding 3's correction line;
>   - that the parse trees without comments are identical to `7f1df96`'s, so only comments changed;
>   - the CI line, if it has been applied.
> - **5.2 What it does not do:** it does not re-probe unchanged items. Any other passing form is a records line, carried to (c)'s inputs, not a finding (DM-40 3.3).
> - **5.3 What still comes to me first:** a form that fits inside the new callback sentence and evades it, before any further correction (DM-40 3.4).

**The focus (the security focus is the display rule: that no provider-shaped field reaches member-visible output while the comment says the check refuses it):**
1. **The callback sentence against `:489-499`, place by place.** Read each clause of the new sentence against the code: "that has a contextual type" (`getContextualType`); "each call signature of that type (of each member, for a union)" (`nonNull(expected).flatMap(part => part.getCallSignatures())`); "at each parameter that has a type annotation" (`!parameter.type`); "the parameter in the same place" and "Places are counted as written" (`node.parameters[index]` against `signature.parameters[index]`); a declared `this` (in the function's list, not the signature's); a rest parameter of the signature (one entry in its list); "a parameter with no parameter in its place is not compared" (`!given`); "What it returns is checked as a widening (above)". A clause that says more or less than the code does is a finding. A form that fits inside the sentence and evades it is a finding, and goes to the Dev Manager first (5.3).
2. **The forms.** With `type Loose = { name?: string; text: string | null }` and each form a real edit to `MessageRow` in `screen.tsx` in a scratch copy: F1, F2 and F3 pass as written; at least F4, F5, F7 and F8 are refused, with the reasons DM-42's table gives (its section 1, which states each form). You may add forms of your own at the sentence's stated places; one that passes as the words predict is a records line (5.2).
3. **Finding 4's line** (`:253-255`) against DM-42's V1 to V3, or forms of your own: a widening to `unknown` at the `data` prop, and to `any` where `getItem` returns Glow's data, and nothing the sentence leaves out.
4. **Finding 3's correction line** in "Correction C6": true at `7f1df96` (`:185`, `:105`, `:721`, `:511`).
5. **Only comments changed:** show it your own way (for example, comment-free parse trees or printed sources against `7f1df96`'s), and that the two new known-passing entries add no word that claims coverage of code paths (DM-38 4.2: no "follows", "any", "every", "all" or "wherever" about what the check covers).
6. **The CI line:** DM-42 4.1's words, as written, in the retry paragraph, and true of the workflow's retry steps and the gate.
7. **The record sections:** true to the code, the run and DM-42, claiming no more than they show, including the session's counts, its T1 and U1, and its limits.

**What comes after this review: the correction classes.** Report every finding with its severity. A further correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a form evade a refusal the comment lists, or the new callback sentence (DM-39 1.2; DM-42 5.3 routes it to the Dev Manager first);
- weaken what any test proves, or make one pass vacuously;
- change any non-comment line, add a dependency, change a lock, or change runtime code;
- make the comment, the CI policy's line or a record claim more than the code, the tests or the runs show.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

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
5. **A clean process environment** for every repository command: `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`npm ci` also needs the proxy and certificate variable names passed through by reference; never print them).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 6913cc06822b6f26c185ea525ce3b3f28a3a5eca HEAD -- . ':(exclude)*.md' && echo "the code head under review"
git diff --quiet 6913cc06822b6f26c185ea525ce3b3f28a3a5eca origin/claude/magical-wozniak-yfmmx2 -- . ':(exclude)*.md' && echo "no code on the live branch after 6913cc0"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^#+ Delta review of correction C6'   # must print 0
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

**Then read, completely, at `HEAD`:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`; the CI policy; the brief's "Correction C6"; DM-42's report, whole; the record's "Review of C4 and repair pass C5", "Correction C6" and "Manager verification of correction C6"; the test file, whole.

## 3. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), the head reviewed, the start gate's and the classification's results, and the environment check;
- a verdict: **approve**, or **changes required**;
- each finding with its severity, its evidence (the form or command and its result), and whether it falls in a correction class;
- focus items 1 to 7, each with what you checked and found;
- the runs you read, with IDs and results;
- what you could not check, and why.
