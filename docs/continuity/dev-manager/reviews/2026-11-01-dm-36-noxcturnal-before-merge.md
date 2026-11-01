# DM-36 — `noxcturnal` at M06's head, before PR38 merges

- **Consultation:** DM-36, revision 1, from App Manager 8, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 3, `session_01KVuPEpFRh9B22beZKTKb27`, branch `claude/dev-manager`.
- **Date:** 1 November 2026.
- **Commit read:** `20667bddea78b9bc3f4629dacc5d6f20a0a16001`, the head of `claude/magical-wozniak-yfmmx2`. **This read covers `20667bd`** (DM-03 G2). PR38's code head is `524d42f`, and `main` is `35a5827`.
- **Environment (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set, and no `STREAM_*` name is present.
- **What I did not do:** I called no provider, database, HDE, Railway or the TypeSafe API, and ran no repository code. I read no repository outside this one.
- **What I did:**
  - downloaded the published `@expo/cli` 58.1.18 and `@expo/metro-config` 58.0.20 tarballs into a scratch directory, without installing or running them, and read their code;
  - read registry metadata with `npm view`, in a clean environment;
  - read npm's trusted-publishing documentation (`docs.npmjs.com/trusted-publishers`, 1 November 2026).

## 1. What I read

- **The stage-two record** (`docs/testing/evidence/2026-11-01-m06-sdk-58-upgrade.md`):
  - the new-package review and its `noxcturnal` block;
  - the counts at the head;
  - "Limits";
  - "Manager verification of stage two";
  - "Exact-head review of stage two".
- **The rest:**
  - my DM-35, section 8;
  - the carried-items file's "Carried to P06.2-F", and the review log's "Deferred conditions";
  - PR38's governing paths against `main`: only the register, OD-54's row;
  - `app.config.ts` at `524d42f`;
  - Notion's Work Register rows M06 and P06.2-F.

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 `noxcturnal`'s acceptance | **It stands for the merge, on corrected reasons** (section 3). Two of DM-35 section 8's statements were wrong or unsupported, and I withdraw them |
| 2 A standing condition | **Yes. It lives in both places:** `apps/mobile/AGENTS.md`, in the exact text of section 4, and the Deferred conditions. Applied as written, the AGENTS line needs no further read and can ride in PR38 |
| 3 The records corrections | **Approved.** Findings 1, 3 and 4 say what the code and the registry show. One optional precision |
| 4 The carried landing | **Approved:** carrying findings 5 and 6 to E11 is right (section 6) |
| 5 The merge | **Approved with conditions 7.1 to 7.5** (section 7) |
| Notion | **One mismatch:** P06.2-F's row does not point to its new carried items |

## 3. Item 1 — `noxcturnal`'s acceptance

**Finding 1 holds; I verified it in the published code:**
- **The switch:** `@expo/cli` 58.1.18 sets `unstable_noxcturnalTransformWorker` from `exp.experiments?.noxcturnalTransformWorker`, with no default (`build/src/start/server/metro/instantiateMetro.js:268-269`).
- **The two call sites:** both in `@expo/metro-config` 58.0.20 check `isNoxcturnalTransformWorkerEnabled`, which tests `=== true` (`build/transform-worker/metro-transform-worker.js:623` for assets, `:668` for JavaScript).
- **The loader:** the only `require('noxcturnal')` is in `loadNoxcturnal()` (`noxcturnal/noxcturnal-transformer.js:232-239`). Its callers are three transform functions (`:763`, `:801`, `:862`):
  - two of them are called only from the two gated sites above;
  - the third, `transformNodeModuleWithNoxcturnalSync`, and its async wrapper have no caller in either package. In `@expo/cli`'s build, the only `noxcturnal` references are `instantiateMetro.js:268-269`.
- **The one unconditional use:** `require.resolve('noxcturnal/package.json')`, for the cache key (`:907`, through `getNoxcturnalCacheKeyFiles`). It resolves a path and loads no code.
- **The app:** `app.config.ts:37` sets only `typedRoutes`. Nothing in the app's own files names `noxcturnal` or the flag.
- **So at this head the addon is installed, never loaded, and runs no install script.**

**Finding 2 holds; I verified it in the registry:**
- `noxcturnal` 0.1.9, 0.1.10 and 0.1.11 were each published by `GitHub Actions <npm-oidc-no-reply@github.com>`, npm's trusted publishing, with no attestation.
- `2g` 1.0.1 and `expo-modules-macros` 0.27.1 were published the same way, and each carries SLSA provenance.
- npm's documentation says provenance is generated automatically under trusted publishing only "from a public repository" and for "a public package". It is "not supported for private repositories", and it can be switched off.

**My DM-35 section 8, corrected:**
- **Withdrawn:** "It is a native transform that runs at bundle time, in CI and in sessions."
  - I wrote that without tracing the gate. At this head it is wrong.
- **Withdrawn as a reason:** "its repository is in Expo's organization."
  - Without provenance, nothing links the published files to that repository.
  - By npm's documentation, the missing attestation means a private source repository or provenance switched off. Either way the source cannot be checked from outside.
- **Still true:**
  - Expo's own `@expo/metro-config` 58 requires it;
  - its one npm maintainer also maintains Expo's packages;
  - the lock pins its integrity hash;
  - it has no install script.
- **Added:** it is published through trusted publishing, from a GitHub Actions workflow, not with a personal token. That is weaker evidence than provenance, because it does not name the source.

**The acceptance stands for this merge,** because the binary does not run at this head. The residual risk moves to the moment something turns it on. The standing condition in section 4 controls that moment.

## 4. Item 2 — the standing condition

**Yes. It belongs in both places:**
- **`apps/mobile/AGENTS.md`,** where the session that would make such a change works;
- **the Deferred conditions,** where my reads track it.

**The text for `apps/mobile/AGENTS.md`:** a fifth step under "Dependency changes", word for word:

> 5. **`noxcturnal` stays unloaded** (DM-36). Expo SDK 58 installs `noxcturnal`, a native Metro transform whose published versions carry no provenance attestation, but the build does not load it: `@expo/cli` turns its worker on only when `app.config.ts` sets `experiments.noxcturnalTransformWorker`. A change that sets that flag, imports `noxcturnal`, or upgrades `expo`, `@expo/cli` or `@expo/metro-config` records whether `export:development` loads `noxcturnal`'s native addon, by a load trace like M06's exact-head review ran. If it does, the change goes to the Dev Manager before its exact-head review, and that review names it.

- **Why the upgrades are included:** a later `@expo/cli` could turn the worker on by default. Only a check at each upgrade would show that.
- **Its read:** applied word for word, it needs no further read (the charter's exception), and my next consultation confirms it. It should ride in PR38, the change that brings the package in (7.2).
- **The Deferred row:** "DM-36: `noxcturnal` stays unloaded; any change that would load its addon comes to the Dev Manager before its exact-head review | Any such change | Standing (`apps/mobile/AGENTS.md`, 'Dependency changes' 5), until the Dev Manager lifts it, for example when a loaded version carries provenance".

## 5. Item 3 — the records corrections

**Approved.** I checked each against the code or the registry:
- **Finding 1:** the record's table row and its limits now say the addon is installed and not executed, and they cite the gate and the lazy loader at the right lines (section 3).
  - **Optional precision:** "requires `noxcturnal` lazily on that path only" could add that the package is also resolved, not loaded, for the cache key.
- **Finding 3:**
  - `expo` 58.0.22 declares `expo-modules` (`bin/modules`), the same name as `expo-modules-cli` 0.4.0's `bin/expo-modules.js`;
  - `@expo/cli`'s `expo-internal` moved from `main.js` (57.0.26) to `bin/cli.js` (58.1.18).
  - I checked the declarations, not the link `npm ci` makes.
- **Finding 4:** `expo-modules-core` 58.0.29 pins `expo-modules-macros` 0.27.1 exactly, and the registry's `latest` is 0.31.0. 0.27.1 carries SLSA provenance, and its publisher is GitHub Actions. My DM-35 cited the `latest` of 1 November, not the locked version.

## 6. Item 4 — the carried landing

**Carrying is right, under the fix-or-carry rule's case (b): a nit.**
- **No guard changed.** The protected outcome is unchanged and asserted: the reset screen stays unreachable. The review found:
  - `_layout.tsx` and `routes.ts` unchanged;
  - every guard allowing what it allowed on SDK 57;
  - no redirect loop.
- **What did change:** a member-visible landing after a failed reset, account entry in place of recovery. That is a flow choice in a fixture-only preview. It misses no prompt item and is in no correction class.
- **Why E11 is the home:** E11 is the next change to these screens and tests. The carried item already names the decision, warns against `redirectTo`, and sends any change to a guard's allowance to me.
- **One condition for E11's brief:** it states the landing it chooses, with finding 5's two assertions pinning it.

## 7. Item 5 — the merge

PR38 may merge when all of these hold:

| # | Condition |
|---|---|
| 7.1 | The review log records DM-36's disposition |
| 7.2 | Section 4's step lands in `apps/mobile/AGENTS.md` as written, with its Deferred row |
| 7.3 | The PR run on the final head passes all eight jobs, with `Application checks passed` and the rendered suite (DM-30 4.3) |
| 7.4 | Codex's review of the final head completes (step 7) |
| 7.5 | The advisory list is re-audited at the final head, not carried over from 1 November, and is `glob` and `minimatch` or smaller. Anything new, worse or in the bundle goes back to Nathan before the merge (OD-54) |

- **PR38's governing paths:** only OD-54's row in the register, and with 7.2 the AGENTS line. OD-54 reads his "a" rightly: the three named advisories are accepted until their parents' ranges move, with DM-35 item 5's re-check.
- **The Deferred conditions, at the merge:**
  - **"DM-35 3.1 to 3.11 and section 8":** done, with section 3's corrections;
  - **"DM-35 item 5":** done with 7.5;
  - **"DM-36":** done.
  - **The new standing row** from section 4 stays open.

## 8. Notion

- **The M06 row matches the repository.**
- **One mismatch: P06.2-F's row does not point to its new carried items,** the failed-reset landing and finding 5's assertions. The workflow's "Batching records" has the item's row point to the carried-items file.

Status: complete
