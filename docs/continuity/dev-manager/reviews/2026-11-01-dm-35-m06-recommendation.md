# DM-35 — M06's recommendation: SDK 57 now or SDK 58 now

- **Consultation:** DM-35, revision 1, from App Manager 8, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 3, `session_01KVuPEpFRh9B22beZKTKb27`, branch `claude/dev-manager`.
- **Date:** 1 November 2026.
- **Commit read:** `0139b1072fd8c68b4e3b2d4aed9ee175c5672012`, the head of `claude/magical-wozniak-yfmmx2`. **This read covers `0139b10`** (DM-03 G2). `main` is `35a5827` (PR37).
- **Environment (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set, and no `STREAM_*` name is present.
- **What I did not do:** I called no provider, database, HDE, Railway or the TypeSafe API, ran no repository code and installed nothing. My own checks were read-only npm registry queries in a scratch copy of the three manifests and locks: `npm audit --package-lock-only` and `npm view`, in a clean environment, with scripts off.

## 1. What I read and checked

- **The M06 material:**
  - the M06 record, whole, with "Manager verification";
  - the M06 brief, revision 1;
  - my DM-31, section 6;
  - OD-49's order.
- **The audits, today, on the locks at `0139b10`.** My audit on 1 November matches the manager's re-audit exactly:
  - `apps/mobile`: 33 vulnerable packages (1 critical, 7 high, 23 moderate, 2 low), from 25 advisories, among them:
    - `decode-uri-component`: GHSA-qr28-fpjm-wq7f (high, a denial-of-service class like its moderate);
    - `node-forge`: 12 advisories (6 high, 3 moderate, 3 low);
    - `glob` and `minimatch`: moderate; `deepmerge`: low;
  - `packages/contracts`: 1 moderate;
  - `proofs/stream-chat`: 1 high.
- **The registry:**
  - `node-forge` 1.4.2 is published;
  - `decode-uri-component` 0.5.1 is `"type": "module"`, while `query-string` 7.1.3 needs `^0.2.2`, and `expo-router` 57.0.29 still needs `query-string` `^7.1.3`;
  - `@expo/cli` 58 declares `zod` `^3.25.76`, `glob` `^13.0.0` and `node-forge` `^1.4.0`;
  - `expo`'s `latest` is 58.0.22, and `sdk-57` is 57.0.31;
  - the publisher facts of the new SDK 58 packages are in section 8.
- **Notion, read-only:**
  - *Implementation Control*'s status and procedure summary;
  - the Work Register rows M06, P06.2-F and P06.3.

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 The record and its verification | **Approved, with one records fix (1.1).** The record met Outcome 1 to 4 as of its run. The verification is right, and I reproduced it. It is enough to decide on, so no re-run of the assessment is needed |
| 2 The path | **(B): SDK 58 now, as M06's second stage, before E11. Approved with conditions 3.1 to 3.11.** (C) is declined on today's facts |
| 3 Stage two's scope | **Approved with conditions 3.1 to 3.11** (section 5) |
| 4 The SDK 58 item under (C) | **Moot under (B).** Under (C), it would be Nathan's to approve |
| 5 The advisories left | **To Nathan before stage two runs,** on the expected list, in OD-32's form. The final head confirms the list, and anything new goes back to him before the merge |
| 6 New packages | **A recorded review before the exact-head review** (section 8). `noxcturnal` is acceptable on today's facts. Any change in those facts comes to me first |
| Notion | **One wording mismatch** (section 9) |

## 3. Item 1 — the record and its verification

- **Outcome 1 to 4 were met as of the run:**
  - the counts, one line per npm package;
  - one row per GHSA, with its path, runtime or tooling by D5's bundle evidence, reach, and fix path;
  - both trials, each with the advisories left, the lock change, the install scripts, the checks, what broke and the fix's size;
  - three paths, with the costs and the advisories each leaves.
- **The verification is right,** and section 1 reproduces it.
  - **One precision:** `@expo/cli` 57.0.32 declares `node-forge` `^1.3.3`, not `^1.4.0`, which is 58's range. 1.4.2 satisfies both.
- **The verification is enough to decide on.** Stage two's own record gives the counts at its head, so it becomes the current figure.
- **1.1 (the manager's):** put a dated note at the top of the record's Summary: "Partly superseded on 1 November: see 'Manager verification' and DM-35". The Summary still says `node-forge` has no fix, counts 10 advisories and recommends (C). A reader of the Summary alone would be misled.

## 4. Item 2 — the path: (B)

**Why (B):**
1. **The facts moved against (C).** On SDK 57, the one package in the app's bundle now carries a high with no clean fix, and SDK 58 removes it. (C) would leave six advisories against (B)'s three. Two of the extra three are `decode-uri-component`'s high and moderate, the only advisories in the bundle; the third is `deepmerge`'s low, in tooling.
2. **(B) pays the upgrade's risk before E11 instead of after it.** That risk is Router 58's protected routes against the 14 guards, and either path pays it before P06.3. E11 tests the release guard in `_layout.tsx`, the file whose 14 guards Router 58 changes. It also changes the chat code (the window-replacement follow-up), where SDK 58 retypes the refs in `src/chat/screen.tsx`. Under (B), E11 is written once, on the final base.
3. **One full-scope dependency cycle, not two.** Each cycle needs a run of record with the rendered suite, an exact-head review and Codex.
4. **It is the path Nathan accepted.** DM-31 item 4 said "If it says upgrade, the upgrade comes before E11", and OD-49 adopted that order. Nothing new enters it.
5. **The record itself calls (B) "viable on this evidence".**

**What (C) would buy, and how (B) still covers it:** (C) makes a smaller first change, and E11 would not wait on a Router surprise. Condition 3.7's stop rule covers both: trial (a)'s SDK 57 path stays the fallback.

**No build item waits under (B):** P09.3a, research only, sits between M06 and E11 in the order anyway.

## 5. Item 3 — stage two's conditions (under (B))

| # | Condition |
|---|---|
| 3.1 | **The version:** the current SDK 58 release at the session's start, recorded with its tag (`latest` was 58.0.22 on 1 November). Pinned exactly (`save-exact`), through the wrapper with scripts off (`apps/mobile/AGENTS.md`), with the `expo-router` uninstall and reinstall the trial needed |
| 3.2 | **Every advisory left is tried in range,** as trial (a) did: `shell-quote`, `fast-uri`, `node-forge` 1.4.2, and `glob`, `minimatch` and `deepmerge` where a parent's range allows. Each that cannot move is named with the range that holds it. For example: `glob` is held at `^13.0.0` by `@expo/cli` 58 and fixed only from 14.0.2; `zod` is held at `^3.25.76` and fixed only from 4.6.6 |
| 3.3 | `fast-uri` 3.1.9 in `packages/contracts` and `follow-redirects` 1.16.2 in the proof's lock, one lock entry each. `dependency-inventory.json` changes to match |
| 3.4 | **The source fix stays type-only:** the exact-head review checks that every changed source line is a type annotation or an import |
| 3.5 | **The counts at the exact head** (DM-02 B9): one row per advisory left, with D5's evidence from that head's `export:development` bundles. The list is the one Nathan accepted (item 5), or smaller |
| 3.6 | **The rendered suite on the exact head,** in the run of record, with the Mobile job's duration against its 25-minute timeout (finding 11). **No test is weakened to pass.** Where Router 58 changes a mechanism a test asserts, for example "removed from the tree" against "renders a redirect", the test still asserts the same outcome for the member: the protected screen stays unreachable. Each such change is listed with its reason, for the exact-head review |
| 3.7 | **A stop rule.** The session stops and reports in either case below. The manager brings the design to me, since it changes a component's interface (the fix-or-carry rule's limits). The fallback is (A), trial (a)'s SDK 57 path, with Nathan asked to accept `decode-uri-component` until SDK 58 lands. The two cases: <br>- the rendered suite needs a fix that changes what any guard allows; <br>- the fix needs more than `_layout.tsx` and `src/onboarding/routes.ts` |
| 3.8 | **The Router 58 items the record names, each checked and recorded:** <br>- the 14 `Stack.Protected` guards; <br>- the module-level `router` before the first render, `_layout.tsx:32` above all; <br>- `useRootNavigationState()`'s `key`; <br>- on web, `SafeAreaView` and async routes, against the 320px layout cases |
| 3.9 | **The new-package review** (section 8), in the record before the exact-head review |
| 3.10 | **The limits named:** <br>- no native build, so React Native 0.88, Hermes, gesture-handler 3, Reanimated 4.7, worklets 0.13 and the new native binaries are untested natively, carried to the first native build; <br>- Expo's release notes, if they are still outside the session's network; <br>- `expo-doctor`, not run unless it is pinned |
| 3.11 | **Full scope:** <br>- the run of record and Codex; <br>- an exact-head code and security review, whose security focus covers the lock's sources and integrity hashes, install scripts and `bin`s, the new packages and 3.4. <br>A brief revision that applies 3.1 to 3.11 and section 8 as written needs no further read (the charter's exception). Anything beyond them comes back to me |

**If (C) is chosen against this read:** 3.1 to 3.3, 3.5 and 3.6 still apply. The six advisories go to Nathan before the stage, the bundled `decode-uri-component` high accepted only until SDK 58. The later SDK 58 item needs his approval (item 4).

## 6. Item 4 — the SDK 58 item under (C)

- **Under (B):** nothing enters the order. The upgrade is M06's own second stage, so the manager records it and names it to Nathan before it starts (OD-49).
- **Under (C): Nathan's to approve.** It moves an upgrade the order he accepted placed before E11 to after it, and it adds an item between E11 and P06.3's UI. OD-49 has the manager name each item, not reorder them.

## 7. Item 5 — the advisories left

- **Which:** every advisory left at stage two's head. The manager's lock-only run expects three under (B), all tooling and none in the bundle; stage two confirms them at its head:
  - `zod` GHSA-mrhx-c7xc-m3w5, high;
  - `glob` GHSA-3g3m-2fjr-6pw4, moderate;
  - `minimatch` GHSA-g3hv-75wg-m249, moderate.
- **The form** (OD-32): one message, with one row for each advisory giving:
  - what it is;
  - where it runs: the Expo CLI or ESLint, not the app;
  - whether it is reached, from the record's reach reading, re-checked at the head;
  - why no fix applies: the parent's declared range;
  - the options: accept it until a named event, or force an `overrides` that breaks the parent's range;
  - the recommendation: accept until the parent's range moves, re-checked at every dependency change (DM-02 B9) and before P09's release preparation.
- **When:** before stage two runs, on the expected list, so that the merge does not wait on a reply.
  - At the final head, the manager confirms that the list is the same or smaller.
  - Any new advisory, any higher severity, or anything that reaches the bundle goes back to Nathan before the merge.
- **Not needed:** an acceptance of today's state on `main`. Stage two is its fix.

## 8. Item 6 — new packages

**The review, in the stage-two record before the exact-head review,** for every package new to the lock:
- **Its source:** every `resolved` URL is `registry.npmjs.org`, and every entry has an `integrity` hash. No git or tarball URLs.
- **Its scripts and `bin`s:** none run, since installs use `--ignore-scripts`. Any `install`, `preinstall` or `postinstall` script is named, and every `bin` is listed (`2g` has one).
- **Its native binaries:** which platform packages arrive, and which one CI and a session would execute.
- **Its publisher:** the npm maintainers and the repository URL; the provenance, from `npm audit signatures` in the scratch install, which checks registry signatures and provenance attestations; and which package requires it.

**What the registry shows on 1 November** (metadata only; the session re-reads it at its head):
- **`noxcturnal` 0.1.11, with its 8 `@noxcturnal/*` platform binaries:**
  - **The facts:**
    - one npm maintainer, `philpl`, and repository `github.com/expo/noxcturnal`;
    - first published on 3 August 2026, and **no provenance attestation**;
    - required by `@expo/metro-config` 58 (`^0.1.11`);
    - no install script.
  - **Where it runs:** it is a native transform that runs at bundle time, in CI and in sessions.
- **`2g` 1.0.1:** the same single maintainer, repository `github.com/kitten/2g`, a `bin`, and SLSA provenance.
- **`expo-modules-macros` 0.30.0:** 13 maintainers, Expo's accounts and `philpl` among them, and SLSA provenance.

**My view: acceptable on those facts.** The residual risk is one account, no provenance, and a native binary run at build time. Stage two records it as a limit. What makes it acceptable:
- Expo's own package requires it, and its repository is in Expo's organization;
- its one maintainer also maintains Expo's packages;
- the lock pins its integrity hash, and it runs no install script;
- the Foundation jobs that run it hold no secret and only a read-only token;
- sessions build only in a clean environment.

**When it comes to me before the exact-head review:** if any of these facts differs at the head:
- another maintainer or publisher;
- a new install script;
- a source other than the registry, or a missing integrity hash;
- a native package that no Expo package requires.

It is a technical judgment (the charter), so it goes to Nathan only if I decline it.

## 9. Notion

- **DM-34's N1 to N3 are applied:** the summary's S2 qualifiers, the HDE-shared environment rule, and the status lead. The summary's stamp is `1ce2fcb`.
- **One wording mismatch:** *Implementation Control*'s status and the M06 row read "SDK 57 would leave 6 advisories and SDK 58 3, all tooling".
  - Only SDK 58's three are all tooling.
  - SDK 57's six include the bundled `decode-uri-component` high and moderate (the record's verification).

## 10. What goes to Nathan, and where each item goes

- **To Nathan before stage two:** item 5's list for risk acceptance, in OD-32's form. The manager also names stage two to him as the next item, under OD-49.
- **If the manager prefers (C):** that is a disagreement with this read, and Nathan decides it (the charter). Item 4 makes it his anyway.
- **The M06 brief, revision 2:** stage two under (B), with 3.1 to 3.11 and section 8.
- **The M06 record:** 1.1's note.
- **Notion:** section 9's wording.

Status: complete
