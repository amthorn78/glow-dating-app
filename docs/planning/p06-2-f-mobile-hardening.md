# P06.2-F — Mobile hardening and P06.2's carried follow-ups

- **Work ID:** P06.2-F (P06; M05's E11, with findings 17 to 20).
- **Status:** correction C1 is done and verified (code head `0881db5`, integrated at `8b0b72a`); **its delta re-review is next** ("Sessions" below). Brief revision 1. **Prompts:** the implementation, [`docs/ephemeral/2026-11-01-p06-2-f-implementation-prompt.md`](../ephemeral/2026-11-01-p06-2-f-implementation-prompt.md), correction C1, [`docs/ephemeral/2026-11-02-p06-2-f-c1-correction-prompt.md`](../ephemeral/2026-11-02-p06-2-f-c1-correction-prompt.md), and C1's delta re-review, [`docs/ephemeral/2026-11-02-p06-2-f-c1-delta-review-prompt.md`](../ephemeral/2026-11-02-p06-2-f-c1-delta-review-prompt.md), each revision 1, for `Glow App - No Stream`.
- **Owner:** Nathan Amthor, by the order he resumed on 26 October (OD-49): P06.2-F after P09.3a, before P06.3's UI. **Manager:** App Manager 8; App Manager 9 from 2 November (OD-56). **Session:** one implementation session, started by Nathan.
- **Revision 1, 1 November 2026.**
- **Starting point:** `main` at `bac3c19` (PR39), with the manager branch's Markdown records after it. The prompt names the exact commit. The app is on Expo SDK 58.0.22 (M06).
- **Evidence home:** `docs/testing/evidence/<date>-p06-2-f-mobile-hardening.md`, written by the session.

## Why

- **M05's E11** gathered the mobile follow-ups into one item at the next change to `apps/mobile`, before P06.3's UI: findings 17 to 20, the P06.2 brief's carried follow-ups, and M05's P-13 README lines.
- **M06's exact-head review** carried two more (the carried-items file, "Carried to P06.2-F"): the failed-reset landing and two assertions that pin it. DM-36 section 6 asks this brief to state the landing it chooses.
- **P09.3a's matrix routes no row here** (DM-37 3.1). The work is fixture-only.

## Outcome

The item is done when each of these holds, **each with a test and the reversal that fails it**, recorded in the evidence record. Line numbers are as the sources give them; the session re-locates each at the starting commit.

1. **The release guards are tested** (M05 finding 17):
   - **the layout's development check:** removing `!__DEV__` from `src/app/_layout.tsx` (line 58) fails a test. Nothing imports the layout today, so the session may move the predicate into a module the test imports; the layout's behavior stays the same;
   - **the app config's environment allow-list:** `GLOW_APP_ENV` set to `staging`, `preview` or unset is refused by `app.config.ts`, so turning the allow-list into a deny-list of `production` fails a test (`scripts/build-guard.test.mjs` probes only `production` today);
   - **the public-name allow-list:** an unreviewed name that shares a reviewed prefix, for example `EXPO_PUBLIC_GLOW_STREAM_TOKEN`, is refused, so a prefix rule in place of the exact allow-list fails a test;
   - **the comment** at `app.config.ts:7` names SDK 57. The session checks that SDK 58 still injects `EXPO_PUBLIC_PROJECT_ROOT` for the rendered harness, and corrects the comment. The guard's behavior does not change.
2. **The display rule's client-side gaps are closed** (M05 finding 18):
   - **`no-console`** in `eslint.config.mjs` (an ESLint core rule; no dependency change), so a `console.info` of message text in `src/chat/store.ts` fails lint;
   - **the render rule** does not rest on the client validator alone: a provider-shaped field, such as a `name` on a message, rendered by `src/chat/screen.tsx`, fails a test;
   - **the copy test covers every copy table** in `src/chat/copy.ts`, not only `invalid_response`, so a provider's name in any entry fails it (`display-rule.test.ts:39` today);
   - **the list clear on an account change** (`store.ts:189`) has a test that fails when the clear is removed.
3. **No provider wording outside chat** (M05 finding 19; ADR 0003, decision 3): the member-visible strings at `src/interactions/screen.tsx:76`, `src/app/media.tsx:91` and `:100`, and `src/app/verify.tsx:12` say what the preview does without naming a provider. A test over these screens' copy fails if a provider term returns.
4. **Dead code, a closed conversation and the README** (M05 finding 20; P-13; DM-23 3.1; DM-26 item 2):
   - `src/hooks/use-recommendations.ts`, with no importer since P05.2, is removed;
   - a `ConversationSummary` whose `state` is `'closed'` does not render as an openable row; a test fails if it does;
   - `apps/mobile/README.md`: P-13's text at `:18` and `:440`, the development-origin sentence at `:24`, and the last sentence, which names only "Stage C2" and "Stage C2-C1" as record sections.
5. **The C2 review's findings** (the P06.2 brief, "Carried to later changes"):
   - **finding 4:** a final send refusal restores the draft;
   - **finding 5:** the restricted-match tests assert `match-conversation` absent;
   - **finding 1, optional:** a bare `WebSocket` or `EventSource` identifier check in `no-provider.test.ts`.
6. **The window-replacement follow-up** (DM-29 1.1 with DM-30 2.1 and 2.2): exactly as the P06.2 brief's "Carried to later changes" lists it, each test with its named reversal; that list is the specification. The optional entries there stay optional.
7. **The failed-reset landing** (M06's exact-head review, findings 5 and 6; DM-36 section 6). **The landing this brief chooses: account entry, with the reset's generic error,** the landing SDK 58 gives today.
   - **Why:** it needs no new navigation, so nothing can race the reset's own `router.replace('/account')`; no guard changes; and recovery stays one step away from account entry.
   - **Pinned by finding 5's two assertions** in `rendered/onboarding.spec.ts`: the failure's alert is visible on account entry, and `page.getByTestId('screen-reset-password')` has a count of 0 without the visible filter.

## Design

- **D1 — Fixture-only.** No live provider, no network client, no new screen. The release block and every runtime guard stay as they are.
- **D2 — No guard's allowance changes.** Every guard allows exactly what it allows at the starting commit. A test may need a guard's predicate moved into an importable module; its behavior must not change. A change that would alter what a guard allows stops the session, and goes to the Dev Manager before the exact-head review (the carried-items file, "Carried to P06.2-F").
- **D3 — No dependency change.** `no-console` is an ESLint core rule. If any item seems to need a package, the session stops and reports; `apps/mobile/AGENTS.md`, "Dependency changes", then applies, step 5 (`noxcturnal`) included.
- **D4 — Every test comes with its reversal.** The record names, for each, the edit that makes it fail and the failing output, in the style of the P06.2 records.
- **D5 — Checks:** from `apps/mobile`, `npm run check`, `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`, in a clean process environment. The rendered suite needs the Chromium revision only CI has (`playwright install` is forbidden), so the run of record is CI's.
- **D6 — Not in scope:** the standing guard for an older page answered `stale_version` (DM-30 1.1 and 1.2; the P11 plan, "Standing guard"), which waits for a phase that lets a readable conversation lose accepted messages; the read phase's N2 and N3 notes and the fixture adapter's `already` (the P06.2 brief's later bullets), which are not mobile.

## Owned paths (the session)

- `apps/mobile/src/**`, `apps/mobile/rendered/**`, `apps/mobile/scripts/build-guard.test.mjs`, `apps/mobile/eslint.config.mjs`, `apps/mobile/README.md`;
- `apps/mobile/app.config.ts`, for item 1's comment only;
- **new:** `docs/testing/evidence/<date>-p06-2-f-mobile-hardening.md`.

## Manager-owned

- This brief and its "Sessions"; the prompt; the Work Register's P06.2-F row; Notion; the handoff; the PR.

## Exclusions

- No change to `package.json`, `package-lock.json`, `.npmrc` or `dependency-inventory.json`; to `apps/mobile/AGENTS.md` or any governing Markdown; or under `services/`, `packages/`, `proofs/`, `scripts/` (the repository's) or `.github/`.
- No `eas`, `playwright install` or `migrate`. No provider call, and no connection to a database, HDE or Railway.

## Acceptance checks

- Items 1 to 7 hold, each with its test and its reversal recorded (item 5's finding 1 and item 6's optional entries only if done).
- The three local checks pass, and the run of record passes all eight jobs, with `Application checks passed` and the rendered suite, the Mobile job within its timeout.
- `git diff --name-only <start> <head>` lists only owned paths.
- The trusted classifier reads the change as full scope.

## Review plan

- **Full scope:** the code change runs normal CI and gets exact-head review evidence (`AGENTS.md`).
- **The manager verifies the report** against the pushed branch: the diff within the owned paths, each reversal re-run where cheap, the run of record's logs.
- **Then** the PR, Codex's review of its head, and an exact-head code review of the code head, whose prompt waits for Codex on the code head and on the commit that holds the prompt (manager workflow, step 6).
- **Dev Manager:** this brief makes no architectural or procedural choice. It applies the conditions it carries as written (DM-29 1.1, DM-30 2.1 and 2.2, DM-36 section 6), and the landing is DM-36's case (b) flow choice, stated here, so the charter asks no read of it. A change to what a guard allows goes to the Dev Manager before the exact-head review (D2).

## Correction C1 (the exact-head review's finding 1, with finding 2 and the record's corrections)

- **Why:** the exact-head review of `3db50d8` found that item 2's render-rule check reads only the paths reached through six variable names (`message`, `conversation`, `list`, `state`, `match` and `row`). A provider-shaped field rendered through a renamed binding, or through a loosely typed helper prop, passes it, and the record's limit claimed more than that. Both fall in the review's correction classes, so step 6's rule (a) fixes them before the merge (the record, "Exact-head review of P06.2-F", finding 1).
- **Outcome:**
  1. **The render-rule test** in `src/chat/display-rule.test.ts` fails when `src/chat/screen.tsx` or `src/chat/rows.ts` renders a provider-shaped field through any binding. At least these planted forms fail it, each added to the test's planted list beside the nine there today, which still fail:
     - **PA:** `MessageRow`'s binding renamed (`{ message: item, name, rowRef }`, with `item.` for `message.` in its body), rendering `{'name' in item ? String(item.name) : null}`;
     - **PB:** a helper component whose loosely typed prop (`{ name?: string; text: string | null }`) renders `entry.name`, used as `<Eyebrow entry={message} />`;
     - **PC:** a destructured read of a provider-shaped field from a message under any name, for example `const { name: label } = item`.

     Today's `screen.tsx` and `rows.ts` still pass it: no harmless code fails. The mechanism is the session's choice. It may read provider-shaped property names through any binding, with named exceptions such as `row.name`, and refuse the `in` operator on a string literal; or it may be a type-aware check built on the TypeScript compiler the app already declares (`typescript`, a devDependency). No dependency or lock changes (D3).
  2. **The copy test's word list** (`display-rule.test.ts:18`) covers item 3's terms as well as its own, with plurals (`providers?`, `stream`, `getstream`, `cloudflare`, `allauth`, `channels?`, `members?`, `custom`, `ai`), so `READ_COPY.unavailable` changed to "Our providers cannot show this conversation." fails it (finding 2).
  3. **The record,** in the session's sections: item 2's row and the "Source-reading tests" limit say exactly what the check now covers and which forms still evade it, and findings 5, 6, 8 and 10 are corrected (items 1 and 5, the run of record's Mobile time, the planted-form count), each marked as corrected in C1. A new section, "Correction C1", holds the changes, each reversal with its failing output, and the run of record.
- **Owned paths:** `apps/mobile/src/chat/display-rule.test.ts`, and the record's session sections with its new "Correction C1" section. No runtime file and no other test.
- **The stop rule:** if closing finding 1 seems to need a change to `screen.tsx`, `rows.ts` or any other path, or a dependency, the session stops and reports.
- **Review:** a delta re-review, since C1 changes no non-test line (step 6). It reads every path C1 touches as it stands at C1's head, after Codex's review of that head and of the delta prompt's commit.
- **Dev Manager:** no read. C1 changes one test within the design this brief accepted (a check from source, since the screens cannot load in Node), and no runtime code, guard, contract, dependency or interface; step 6's rule decides the disposition.

## Sessions

- **The implementation** (1 November 2026; prompt revision 1 at `67b0201`; branch `claude/practical-wozniak-fg1e2i`, code head `3db50d8`, records `02f1972`; Nathan's pick: not recorded): items 1 to 7, each with a test and its reversal; nothing met the stop rule. Optional entries done: item 5's finding 1, and item 6's finding 5; item 6's finding 9 not done, with its reason. Beyond the brief's list: `src/data/fixtures.ts` removed with the dead hook, a test against unimported modules, and more provider wording on the same screens. Run of record: push run 41359462167 on `3db50d8`, all eight jobs passed, rendered 97 passed, Mobile 5 min 58 s of 25. The first run was cancelled by the session's own records push (AM8-20); Nathan approved the re-push. The manager verified it (the record, "Manager verification": six reversals re-run, each failing) and fast-forwarded the manager branch. Next: the PR, Codex, and the exact-head code review.
- **PR40** (1 November 2026): P06.2-F's full-scope PR from the manager branch. **The exact-head review prompt, revision 1** ([prompt](../ephemeral/2026-11-01-p06-2-f-review-prompt.md)), of code head `3db50d8`, for `Glow App - No Stream`; TypeSafe v8.2: Opus 5.5 at extra high. Codex found nothing on `b924afa`; it did not start on `a007328`, so at Nathan's direction the manager posted `@codex review` once, and that review completed with no finding. Given to Nathan on 2 November.
- **The exact-head review** (2 November 2026; prompt revision 1 at `a007328`; Nathan's pick: not recorded): **changes required,** in one test and the records; the runtime code is correct, no guard allows anything new and no test is weakened. Ten findings: finding 1 (should fix, in two correction classes) to C1 with finding 2 and the record's corrections; finding 3 to the P06.2 brief's "Carried to later changes"; finding 4 to the P11 plan; finding 7 and the manager's half of finding 10 corrected in the record (AM8-21); finding 9 a recorded limit (the record, "Exact-head review of P06.2-F"). Next: correction C1.
- **Correction C1** ([prompt](../ephemeral/2026-11-02-p06-2-f-c1-correction-prompt.md), revision 1): the section above, for `Glow App - No Stream`; TypeSafe v8.2: Opus 5.5 at high. Codex's review of `cdc7c48`, the commit that holds it, raised one finding (P2, `display-rule.test.ts:133`): the review's finding 1, with the same aliased-binding probe, so it joins C1 as planted form PA. The manager replied on its thread, which stays open until C1's head is on PR40. PR run 41379670526 on `cdc7c48` passed. Given to Nathan on 2 November (start commit `cdc7c48`). **Done** (2 November; branch `claude/trusting-cori-gxlila`, code head `0881db5`, records `0e98f25`; Nathan's pick: not recorded): the source check kept, with an `in` check on a string literal added, and a type check on the installed TypeScript compiler that finds Glow's data by type through any binding; 22 planted forms, each failing for a named reason; the copy test's word list widened; the record's findings 5, 6, 8 and 10 corrected. Known evasions: a module outside `screen.tsx` and `rows.ts`, and a template literal's coercion (the record, "Correction C1"). Nothing met the stop rule. Run of record: push run 41383619096 on `0881db5`, all eight jobs passed, 650 unit tests, rendered 97 passed, Mobile 7 min 27 s of 25. App Manager 9 verified it (the record, "Manager verification of correction C1": PA, PB, PC and finding 2's reversal re-run, each failing; the named evasion confirmed) and merged it into the manager branch at `8b0b72a`.
- **C1's delta re-review** ([prompt](../ephemeral/2026-11-02-p06-2-f-c1-delta-review-prompt.md), revision 1): of code head `0881db5`, on M05 S2's terms, for `Glow App - No Stream`; TypeSafe v8.2: Opus 5.5 at high. Its prompt waits for the PR run and Codex on PR40's head, which holds it. Next: the review, then the merge and its receipt.
