# M06 exact-head review prompt — the Expo SDK 58 upgrade

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 1 November 2026.**
- **Durable brief:** [M06](../planning/m06-dependency-remediation.md), revision 2, "Stage two" (DM-35's conditions 3.1 to 3.11 and its new-package review; OD-54).
- **What it reviews:** stage two's code head `524d42f`, in [PR38](https://github.com/amthorn78/glow-dating-app/pull/38). It is the only security reading of this change before the merge (3.11; Codex's security reviews are no longer available, OD-41).
- **Where the result goes:** the review's report, relayed by Nathan. The manager records it in the stage-two record, "Exact-head review of stage two", and runs fix or carry by step 6's rule.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 3.25 (confidence 0.81); rung probabilities low 0.00, medium 0.00, high 0.02, extra high 0.72, max 0.26, ultracode 0.00. Model probabilities Fable 5.1 0.44, Opus 5.5 0.56, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.41). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.009, Fable 5.1 at extra high 0.317, Fable 5.1 at max 0.114, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.011, Opus 5.5 at extra high 0.403, Opus 5.5 at max 0.146, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: model near tie between Opus 5.5 and Fable 5.1. Sent 2026-11-01T13:43:56Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. It authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of the code head and of the commit that holds this prompt (step 6).
- **Deletion condition:** prune after M06's PR merges and its receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head code and security review of M06's stage two**, the Expo SDK 58 upgrade, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage one** assessed the npm advisories (`docs/testing/evidence/2026-10-26-m06-dependency-assessment.md`, with its "Manager verification" of 1 November).
- **The Dev Manager chose path (B):** SDK 58 now, before E11, with conditions 3.1 to 3.11 and a new-package review (DM-35; the brief's "Stage two").
- **Nathan accepted** `zod`, `glob` and `minimatch`, all in tooling, until their parents' ranges move (OD-54).
- **Stage two** (branch `claude/magical-lovelace-s0akbt`, code head `524d42f`, records `5103063`; record `docs/testing/evidence/2026-11-01-m06-sdk-58-upgrade.md`):
  - `apps/mobile` to Expo SDK 58.0.22, with every range exact;
  - in-range fixes, and one lock entry each in `packages/contracts` and `proofs/stream-chat`;
  - both inventories regenerated;
  - an 11-line type-only fix;
  - six rendered-test changes.
- **Its run of record,** push run 41310128518 on `524d42f`: all eight jobs passed, the gate printed `Application checks passed`, and the rendered suite passed 97 of 97. The manager verified it ("Manager verification of stage two") and fast-forwarded the manager branch.

**The code head under review is `524d42f`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `524d42f` (the start gate checks this).

**Your scope:**
- `git diff 836f3e91ff35371b53a252503b93aabe7b92e43e 524d42f0a628c0e35d9e4f95de9a474a360493e5`:
  - `apps/mobile/package.json`, `package-lock.json` and `dependency-inventory.json`;
  - `packages/contracts/package-lock.json` and `dependency-inventory.json`;
  - `proofs/stream-chat/package-lock.json`;
  - the type-only fix in `src/chat/screen.tsx`, `src/components/ui.tsx` and `src/interactions/controls.tsx`;
  - the rendered-test changes in `rendered/onboarding.spec.ts`, `rendered/profile-preferences.spec.ts` and `rendered/state-corrections.spec.ts`.
- **The stage-two record,** with its "Manager verification", against the code and the runs.
- **The runs:** run 41310128518, and the PR run on PR38's final head (event `pull_request`) once it has finished.
- **Out of scope:** code this stage does not change. A finding there is reported as pre-existing, not as a defect of this stage.

**The security focus** (DM-35 3.11 and section 8):
1. **The lock's sources and integrity:**
   - every `resolved` URL is `https://registry.npmjs.org/`, and every entry has a `sha512` `integrity`;
   - for each new package, the lock's `integrity` matches the registry's `dist.integrity` (`npm view <name>@<version> dist.integrity`);
   - no git, tarball or file source.
2. **Install scripts and `bin`s:**
   - no new `install`, `preinstall` or `postinstall` script (the lock's `hasInstallScript`; only `fsevents` before);
   - every new `bin` listed (`2g`, `expo-modules`, and the nested `metro` and `metro-symbolicate`), and whether anything in CI or the npm scripts runs it.
3. **The new packages** (23 new names): `2g`, `noxcturnal` and its 8 platform binaries, `expo-modules-macros` and its binaries, and the rest.
   - Each one's publisher, its repository, and which Expo or React Native package requires it.
   - **`noxcturnal`** (one maintainer, `philpl`; repository `github.com/expo/noxcturnal`; no provenance; required by `@expo/metro-config` 58): do these facts hold at the head? Is anything else true of it that DM-35 section 8 says must go to the Dev Manager?
4. **The type-only fix (3.4):** every changed source line is a type annotation or an import, and the runtime JavaScript is unchanged. One way to show it: compare the stripped output of the three files before and after, for example with `tsc` emit, or Babel or Metro's transform of the file alone, in a scratch copy.
5. **The rendered-test changes (3.6):** no test is weakened.
   - **Changes 1 to 5:** each only adds a wait for the destination screen after a navigating click. Does each wait for the right screen, and could it pass while the step it guards is wrong?
   - **Change 6,** `onboarding.spec.ts` after the failed `wrong_context` reset: it expected recovery and now expects account entry, then opens recovery and asserts no reset is offered.
     - Does it still prove that the reset screen is unreachable?
     - Under Router 58, does every guard in `src/app/_layout.tsx` (with `canAccessRoute` in `src/onboarding/routes.ts`) allow exactly what it allowed on SDK 57, for every state the suite reaches?
     - Is the new landing screen acceptable for a member, or does it need a fix in `_layout.tsx` or `routes.ts`? Weigh the record's reason against `redirectTo`. A fix that changes what a guard allows is outside this stage (3.7).
6. **The bundles:** the head's `export:development` bundles hold no module of `glob`, `minimatch`, `zod`, `node-forge`, `shell-quote` or `fast-uri`, and `query-string` and `decode-uri-component` are gone.
7. **The advisories at the head:** `npm audit --package-lock-only` in all three npm packages. The list must be OD-54's or smaller, with nothing new, more severe or in the bundle.

**What comes after this review: the correction classes.** Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a test pass where it should fail, or weaken what a test proves (3.6);
- let a guard allow what it did not allow on SDK 57;
- change runtime code beyond types (3.4);
- leave a lock entry from a source other than the registry, without an integrity hash or with a hash that does not match the registry, or with a new install script;
- leave an advisory outside OD-54's list, or one that reaches the bundle;
- make a record claim more than the code, the lock, the tests or the runs show;
- leave a condition of DM-35 (3.1 to 3.11, section 8) unmet at this head.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 8. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - allowed: the npm registry (installs with scripts off, `npm view`, `npm audit`) and `docs.expo.dev`;
  - `npm audit signatures` also fetches Sigstore's public TUF metadata from `tuf-repo-cdn.sigstore.dev`. You may run it once, and you must say so if you do;
  - nothing else.
- **Rendered tests:** CI's run is the evidence. You may run the suite locally against the container's preinstalled Chromium, with a scratch config outside the checkout. Such a run is informational only. Never run `playwright install`.
- **Never:**
  - dump the environment, or print a credential, token or password;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/` that sends a request;
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
git merge-base --all origin/main HEAD                 # expected: one line, 1ce2fcbe1c1b81db5c4f0a8a9e513c806bb4d932
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 524d42f0a628c0e35d9e4f95de9a474a360493e5 HEAD -- .github scripts services apps packages proofs && echo "the code head under review"
git diff --quiet 524d42f0a628c0e35d9e4f95de9a474a360493e5 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs && echo "no code on the live branch after 524d42f"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-m06-sdk-58-upgrade.md | grep -c -E '^#+ Exact-head review of stage two'   # must print 0
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, if a non-Markdown path changed there after `524d42f`, or if this review is already recorded.

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
- the brief's "Stage two";
- DM-35, `docs/continuity/dev-manager/reviews/2026-11-01-dm-35-m06-recommendation.md`;
- OD-54 in `docs/continuity/owner-directions.md`;
- the stage-two record, whole;
- `src/app/_layout.tsx` and `src/onboarding/routes.ts`, whole;
- the three changed spec files, whole.

**The runs,** with your GitHub tools:
- run 41310128518: every job's conclusion, the gate's line, the Mobile job's rendered result and duration;
- the PR run on PR38's final head, if it has finished.

Say what you read.

## 3. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's and the classification's results;
- the environment check;
- a verdict, **approve** or **changes required**, with the findings that require changes;
- every finding, numbered, with:
  - its severity (blocking, should fix, nit);
  - its file and line;
  - what is wrong, and why it matters;
  - a suggested fix;
  - whether it falls in a correction class;
- for each of the seven focus areas, what you checked and what you found;
- your answer on change 6: is the guard proof kept, are the guards' allowances unchanged, and is the landing screen acceptable;
- the commands, scratch runs and network use, with their exact results;
- limits of the review, and open questions.
