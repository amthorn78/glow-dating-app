# P06.2-F review prompt — correction C7, on DM-43 3.1 to 3.3

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 8 November 2026.**
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 7, "Correction C7" (its "Review" line). The terms are [DM-43](../continuity/dev-manager/reviews/2026-11-08-dm-43-p06-2-f-c6-review-finding.md) 3.1 to 3.3, on DM-42 5.1 to 5.3's terms, held to DM-39 1.2 for the changed text. C7 changes comment lines only, so this is one delta review on M05 S2's terms (manager workflow, step 6).
- **Where the result goes:** the report Nathan relays. The manager records it in the P06.2-F record, "Delta review of correction C7", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.87 (confidence 0.75); rung probabilities low 0.00, medium 0.25, high 0.62, extra high 0.13, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.247, Opus 5.5 at high 0.614, Opus 5.5 at extra high 0.129, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.003, Sonnet 5.5 at high 0.006, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-08T17:31:32Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR40's head, which holds this prompt and C7's code (manager workflow, step 6).
- **Deletion condition:** prune after PR40 merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta review of correction C7 of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The render-rule test** (`apps/mobile/src/chat/display-rule.test.ts`) checks from source that `src/chat/screen.tsx` and `src/chat/rows.ts` render only contract fields (ADR 0003). Its comment states, under DM-39, what the check refuses as a positive list, what it is known to pass and what harmless code it refuses. The check's code has not changed since C2; DM-39 1.1 froze its design.
- **Correction C6** (code head `6913cc0`) stated the inline rule's places in DM-42's words. **C6's delta review** found that at a rest parameter's place the rule compares the annotated parameter with the rest parameter's own type, the array, not its element (F-1), so an annotation that declares only names an array also has passes (R1), while a harmless annotation of the element type there is refused (H1). Codex found F-1 again.
- **DM-43** ruled F-1 a DM-42 5.3 form and approved option (a): words that name the compared type at each place, mapped clause by clause to the rule (its section 3.3), with an R1 entry in "What it is known to pass" and an H1 entry in "What harmless code it refuses". It declined changing the check and corrected the CI policy's `504` count (its 4.1).
- **Correction C7** (branch `claude/practical-cannon-1sag8n`, code head `d27324b831e29f482015d4b6d694bc14bf38bc27`, records `927ebbd`): DM-43 1.1 and 1.2 word for word in the comment, with no narrowing, and the record's "Correction C7". Its run of record, push run 42503721311 on `d27324b`: all eight jobs passed, `Application checks passed`, 650 of 650 unit tests, rendered 97 passed; no retry fired.
- **The manager verified it** (the record, "Manager verification of correction C7": the words by script, the comment-free parse trees, the run's jobs and logs) and merged it at `ed95d83`. Before C7, the manager applied DM-43 4.1's words to the CI policy's retry paragraph.

**The code head under review is `d27324b`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `d27324b` (the start gate checks this). Line numbers below are at `d27324b`. DM-43 cites the rule at `6913cc0`, 11 lines earlier: its `:489-496` is `:500-507` here. The changed comment is at `:166-174` (the sentence), `:249-253` (the R1 entry) and `:266-269` (the H1 entry).

**Your scope (each path read whole as it stands at the head, not the diff alone):**
- `apps/mobile/src/chat/display-rule.test.ts`: C7's comment changes, read against the code they describe. Guide: `git diff 6913cc06822b6f26c185ea525ce3b3f28a3a5eca d27324b831e29f482015d4b6d694bc14bf38bc27`.
- The P06.2-F record (`docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`): "Correction C7" and "Manager verification of correction C7", checked against the code, the run and DM-43.
- The CI policy's (`docs/operations/ci-and-branch-policy.md`) "Toolchain installs are retried once" paragraph: DM-43 4.1's words only.
- **The runs:** run 42503721311, and the PR run on PR40's head (event `pull_request`) once it has finished.
- **Read as context, not under review:** `src/chat/screen.tsx`, `src/chat/rows.ts`, and the rest of the test file's code.

**DM-43's terms for this review, as written (section 4):**

> - **3.1 The next review's terms:** a delta review on DM-42 5.1 to 5.3's terms, limited to the changed words and the new entries, after Codex has completed on its code head and on the commit that holds its prompt (step 6). It is held to DM-39 1.2 for the changed text.
> - **3.2 What it checks:**
>   - each clause of 1.1 against the rule's lines at the new head (section 3.3's table, by content, since line numbers move);
>   - that at least R1, R3, R4 and TU1 pass, and R2, R5, H1 and G1 are refused, for the reasons the words give;
>   - the two new entries as written: R1's passes, and H1's fails as stated;
>   - that only comments changed;
>   - 4.1's line, word for word.
> - **3.3 What it does not do:** it does not re-probe unchanged items. Other passing forms are records lines (DM-42 5.2). A form that fits inside the changed words and evades them comes to me first (DM-42 5.3).

DM-43 4.1's words, for item 3.2's last check: "failed with `504` responses in three runs (42464917902, 42469365545 and 42470101373)".

**The focus (the security focus is the display rule: that no provider-shaped field reaches member-visible output while the comment says the check refuses it):**
1. **Each clause of the new sentence against `:500-507`,** using DM-43 section 3.3's table by content: the inline arrow or function expression; its contextual type and each call signature (of each member, for a union); each annotated parameter, places counted as written, a declared `this` first in the function's list and none in the signature's, a rest parameter taking one place; no comparison for a parameter with no parameter in its place; the data's type as the type of the parameter in the same place (`checker.getTypeOfSymbol(given)`), the rest's own array type at a rest place; the comparison as a widening, with the annotation as the expected type (`carries(value) && !keeps(value, …)`). A clause that says more or less than the code does is a finding. A form that fits inside the changed words and evades them is a finding, and goes to the Dev Manager first (3.3).
2. **The forms.** As real edits to `MessageRow` in `screen.tsx` in a scratch copy, with `type Loose = { name?: string; text: string | null }` where a form uses it: at least R1, R3, R4 and TU1 pass, and R2, R5, H1 and G1 are refused, for the reasons the words give (DM-43's section 1 table states each form). You may add forms of your own at the changed words' places; one that passes as the words predict is a records line (3.3).
3. **The two new entries as written:** R1's example passes, and H1's example fails as `a widening callback parameter: first: ConversationMessage`; each sits where DM-43 1.2 places it.
4. **Only comments changed:** show it your own way (for example, comment-free parse trees or printed sources against `6913cc0`'s), and that the changed text adds no word that claims coverage of code paths (DM-38 4.2: no "follows", "any", "every", "all" or "wherever" about what the check covers).
5. **The CI policy's count:** DM-43 4.1's words, word for word, in the retry paragraph, and true of the three runs it names.
6. **The record sections:** true to the code, the run and DM-43, claiming no more than they show, including the session's counts, its line references and its limits.

**What comes after this review: the correction classes.** Report every finding with its severity. A further correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a form evade a refusal the comment lists, or the changed words (DM-39 1.2; DM-43 3.3 routes it to the Dev Manager first);
- weaken what any test proves, or make one pass vacuously;
- change any non-comment line, add a dependency, change a lock, or change runtime code;
- make the comment, the CI policy's words or a record claim more than the code, the tests or the runs show.

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
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`. Put it first on PATH yourself. Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`npm ci` also needs the proxy and certificate variable names passed through by reference; never print them).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet d27324b831e29f482015d4b6d694bc14bf38bc27 HEAD -- . ':(exclude)*.md' && echo "the code head under review"
git diff --quiet d27324b831e29f482015d4b6d694bc14bf38bc27 origin/claude/magical-wozniak-yfmmx2 -- . ':(exclude)*.md' && echo "no code on the live branch after d27324b"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^#+ Delta review of correction C7'   # must print 0
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

**Then read, completely, at `HEAD`:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`; the CI policy; the brief's "Correction C7"; DM-43's report, whole; the record's "Delta review of correction C6", "Correction C7" and "Manager verification of correction C7"; the test file, whole.

## 3. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), the head reviewed, the start gate's and the classification's results, and the environment check;
- a verdict: **approve**, or **changes required**;
- each finding with its severity, its evidence (the form or command and its result), and whether it falls in a correction class;
- focus items 1 to 6, each with what you checked and found;
- the runs you read, with IDs and results;
- what you could not check, and why.
