# DM-53 — SV2 Stage A's owned paths (the generated contract outputs and the flow registry), D8 against the models, and DM-52's conditions as applied

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 10, relayed by Nathan (OD-25).
- **Read at:** `c2ee87aa54947f13cef5e3b5e0ed32479aecaa25` of `claude/magical-wozniak-yfmmx2`, with `main` at `c864edd`. Both were still there at 02:23 UTC (`git ls-remote`).
- **Written:** 10 November 2026, finished at 02:35 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only; none of the six names is present.
  - I called no provider, database, HDE, Railway or TypeSafe service, downloaded nothing, and wrote only this file.
  - Notion was read, not edited.

## 1. What I read

- **The consultation, and the brief, revision 2,** whole, at `c2ee87a`.
- **Item 1:**
  - `packages/contracts/scripts/generate.mjs` and `package.json`;
  - the Foundation workflow's Mobile checks job;
  - `tests/corpus.test.mjs`;
  - `apps/mobile/src/contracts/production.ts`, and every mobile use of `parseAppIntent` and `parseAppResponse`;
  - `apps/mobile/package.json`'s scripts and `apps/mobile/AGENTS.md`;
  - C1's prompt from history (`d1f7ea1`, "Owned paths").
- **Item 2:**
  - `production/flows-v1.json` (every flow's transitions, roles and policies);
  - `transition_contract.py`, the oracle;
  - `tests/test_production_contract.py` and `tests/test_transition_contract.py`;
  - the package's README;
  - `production-contracts.md`'s flow index and its list of trusted test prerequisites.
- **Item 3:**
  - `BirthInput` and `EngineIdentity` in the models;
  - `BirthInput` and `OwnBirthInput` in the schema;
  - F03's transitions;
  - P04's `store.ts` (`setAdultDate`).
- **Item 4:**
  - DM-52's conditions, checked by script against revision 2;
  - the register (OD-60, OD-61), the carried-items file and the P11 plan;
  - a sweep of the living documents for the texts DM-52 replaced.
- **Notion,** read-only (section 7).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. The generated contract outputs | **Approved with conditions.** The manager's words are right, and the precedent holds: C1 owned the outputs "only as `npm run generate` writes it". W1 adds which files change and how a review checks them. W2 and W3 take the manager's owned-path and exclusion words. W4 adds `apps/mobile`'s own check to the acceptance checks |
| 2. The flow registry and the README | **Approved with conditions.** The words are right. The mapping needs four corrections: the registry has no `staff` role, and the oracle would always refuse one; the sensitive consent needs events of its own; the age state's transitions are missing; and every demotion that follows another write is one `system` entry. W5 gives the entries, and W6 extends `production-contracts.md`'s owned scope to the rows the manager keeps in step |
| 3. D8 and D7 against the models | **The three readings are right.** W8 to W10 put them in D8 and check 8, so that the brief, not only the prompt, carries them |
| 4. DM-52's conditions as applied | **Confirmed as applied.** 53 of B1 to B55 are word for word. B20 and B28 are word for word plus the marked choices their words left to the brief. R1, OD-61 (R2) and K1 to K7 are in place. **The four choices are approved:** D6's writer, D7's one date, D9's removed requirements, and D18 in Stage A. One more miss of mine: the migrations line (W7). DM-52's open row can close |
| Notion | **Matches** `c2ee87a`, with two nits (section 7) |

**How to apply:**
- W1 to W10 are in given words; line breaks may move. A script applied all ten in order to a copy of revision 2, and each passage was found exactly once.
- **No further read is needed before Stage A's prompt** if they are applied as written; a departure from the words comes back first. My next consultation confirms them as applied (step 6).

**My share.** DM-52's section 11 said: "The mobile app's validators and fixtures stay untouched until P10." That is wrong for the generated validators, which every new DTO rewrites. I also left D11's matching sentence standing.
- **What stays untouched** is the mobile app's source, tests and fixtures.
- **Prevention:** when a condition says a path stays untouched, I check what the build writes there, not only what code imports from it.

## 3. Item 1 — The generated contract outputs

- **What the code does** (confirmed):
  - `generate.mjs` reads both schemas and writes four files to `apps/mobile/src/contracts/generated/`: `gapp-dev-v1.ts`, `gapp-api-v1.ts`, `validators.js` and `validators.d.ts`. A production-only change rewrites three of them; `gapp-dev-v1.ts` stays byte-identical, since the development schema does not change.
  - `npm run check` in `packages/contracts` runs `generate.mjs --check`, which fails with "Generated contract drift" on any byte difference, and then the node tests. The Mobile checks job runs it after `npm ci --ignore-scripts` in `packages/contracts`.
- **Nothing in the mobile app's source has to change.**
  - `production.ts` uses only `validateAppIntent`, `validateAppResponse` and `validateError`, with the types `AppIntent`, `AppResponse` and `Error`.
  - The mobile code narrows by comparing `operation` or `kind` with `===`, and has no exhaustive `never` check that new union members would break.
  - So the manager's stop rule fits: if a mobile source, test or fixture would have to change, the session stops.
- **C1's precedent** (`d1f7ea1`) owned "`packages/contracts/**`, except its dependency files", and "`apps/mobile/src/contracts/generated/**`, only as `npm run generate` writes it". C1 also owned "the mobile app's existing tests or code only where `channel_ref`'s removal requires it". SV2 removes nothing, so the stricter stop rule is right.
- **Two additions:**
  - **How a review checks the outputs.** Ajv numbers its compiled schemas in order, so new DTOs can renumber much of `validators.js`. A review checks the outputs by regenerating them, which is what CI does, not by reading the diff (W1).
  - **The mobile app's own check.** The acceptance checks run `packages/contracts`' tests, but not `npm run check` in `apps/mobile` (`tsc --noEmit`, ESLint and the node tests), which compile and import the regenerated files. CI runs it, and so should the session (W4).

**W1:** in D11, replace:

> ```
> New DTOs in the v1 production schema; every existing DTO is unchanged, so the mobile app's generated validators and fixtures are untouched until P10:
> ```

with:

> ```
> New DTOs in the v1 production schema; every existing DTO is unchanged, so no mobile source, test or fixture changes until P10. The generated contract outputs in `apps/mobile/src/contracts/generated/` gain the new DTOs' types and validators: `gapp-api-v1.ts`, `validators.js` and `validators.d.ts` change, and `gapp-dev-v1.ts` does not. Only `npm run generate --prefix packages/contracts` writes them, never a hand edit, as for P04.3's and C1's DTOs. Ajv numbers its compiled schemas in order, so new DTOs can renumber much of `validators.js`; a review checks the outputs by regenerating them, not by reading their diff. CI's Mobile checks job compares them byte for byte, and the shared corpus runs through them:
> ```

**W2:** in "Owned paths", replace:

> ```
> - `packages/contracts/production/gapp-api-v1.schema.json`, `openapi.json` (DTOs only, no paths), `corpus/shared-v1.json` and the contract tests: D11's additions only.
> ```

with:

> ```
> - `packages/contracts/production/gapp-api-v1.schema.json`, `openapi.json` (DTOs only, no paths), `corpus/shared-v1.json` and the contract tests: D11's additions only.
> - `packages/contracts/production/flows-v1.json`: D11's DTOs, each in its flow's `request_contracts`, `response_contracts` and `projection_roles` (`owner`), as F05's `MediaCollection` and F11's C1 DTOs are. Also the transitions SV2's writers make that the registry lacks, each as a new entry (D11's list). No existing entry changes.
> - `packages/contracts/README.md`: a section for SV2's additions, as P06.2 C1 has.
> - `apps/mobile/src/contracts/generated/**`, only as `npm run generate --prefix packages/contracts` writes it. If a mobile source, test or fixture would have to change for the Mobile checks job to pass, the session stops.
> ```

**W3:** in "Exclusions", replace:

> ```
> - `apps/**`, `wordpress/**`,
> ```

with:

> ```
> - `apps/**`, except the generated contract outputs (Owned paths), `wordpress/**`,
> ```

**W4:** in "Acceptance checks", replace:

> ```
> **In `packages/contracts`:** its tests, with the corpus run through Python and the generated validators.
> ```

with:

> ```
> **In `packages/contracts`:** its tests, with the corpus run through Python and the generated validators, and `npm run check`, which regenerates the outputs in memory and compares them. **In `apps/mobile`:** `npm run check` (its typecheck, lint and tests) passes with the regenerated outputs and no other change; CI's Mobile checks job runs its export and rendered checks.
> ```

## 4. Item 2 — The flow registry and the README

- **The gap is real.**
  - P04.3 registered `MediaCollection` in F05, and C1 registered its DTOs in F11, with a README section.
  - The brief owns neither `flows-v1.json` nor the README.
  - `test_schemas_and_flow_references` checks that each flow's `projection_roles` keys equal its `response_contracts`, and that the flows are exactly F01 to F20. So new DTOs go into existing flows, as the manager reads.
- **The flow index is kept by hand.** `production-contracts.md` says it "is generated from the committed flow registry", but no script or test produces or checks it. Keeping its F02 to F06 rows in step is a manual step, and the brief owns that section only for "F02 to F06's server mapping" (W6).
- **Four corrections to the mapping:**
  1. **There is no `staff` role.** The registry's roles are `owner`, `system`, `provider`, `moderator`, `support`, `participant`, `auth`, `public` and `presentation`. The oracle's `authorized` returns `False` for any other role, so a `staff` entry would always be refused. Staff act as `moderator`, which needs `moderator:case` scope: F01's `suspend`, F05's `approve` and `restrict_media`, and the tests' `STAFF` context (`Context("staff", "moderator", …)`). Staff approval and its revocation are `moderator`, with `A05` as other staff actions have.
  2. **The sensitive consent needs events of its own.** Reusing F02's `accept` and `withdraw` would make an optional consent start as `required`, and leave the registry unable to tell the two consents apart. With `accept_sensitive` and `withdraw_sensitive` from a `not_given` start, no rule repeats another (the oracle matches on event, from and to).
  3. **The age state's transitions are missing.** D7 adds a writer that moves `unknown` to `self_declared_adult` and back. Under the manager's own words ("the transitions SV2's writers make that the registry lacks"), it belongs in F02, whose acceptance already says "underage … cannot use discovery".
  4. **Every demotion that follows another write is one `system` entry.**
     - That is how F04's `deletion_requested` follows F18's request.
     - The cause keeps its own entry, with its own actor's role, in its own flow: the owner's withdrawal in F02, staff's revocation in F02, the owner's correction in F03.
     - The manager's split by actor would give staff and the owner a direct "demote" transition in F04 that neither has as an action.
     - The owner's own edit that clears the summary keeps the existing owner `edit` from `visible` to `incomplete`.
- **Two smaller points:**
  - **Names.** F01 already uses the event `verified` and the state `unverified` for email verification. D18's events need names that cannot be read as F01's; its state names can stay, because the oracle keys states by flow.
  - **Who reports a verification.** The verification company's verdict arrives through the port, as F05's `uploaded` and `purged` do, so its role is `provider`, and B30's authentication rule applies. `system` is for Glow's own rules.
- **Stage B, not Stage A:** OD-61 makes F05's `approve` and `reject` the automated check's (`system`). The `moderator` entries then go, and `test_f05_quarantine_cannot_be_published_by_uploader` changes with them. Those are changes to existing entries, which Stage B's prompt must own; `restrict_media` stays `moderator`.
- **A new prerequisite name.** Gating staff approval on D2's setting gives the oracle a new trusted test prerequisite, `staff_approval`. It joins `production-contracts.md`'s list, beside `consent_current` and the others.
- **The README section** is approved as worded.

**W5:** at the end of D11, replace:

> ```
> (`production-contracts.md` says so for these DTOs).
> ```

with:

> ```
> (`production-contracts.md` says so for these DTOs).
>
>   **The flow registry** (`flows-v1.json`; DM-53). Each new DTO joins its flow's `request_contracts`, `response_contracts` and `projection_roles` (`owner`), and each transition SV2's writers make that the registry lacks is a new entry. Every entry uses a role the oracle authorizes (`transition_contract.py`, `authorized`): staff act as `moderator`, as F01's `suspend` and F05's `restrict_media` do. No existing entry changes, and each new entry has an allowed and a forbidden example in `tests/test_transition_contract.py`. The entries:
>   - **F02:**
>     - the sensitive-fields consent's intent and read, with events of its own, so that no rule repeats the onboarding consent's and an optional consent never starts as `required`: `accept_sensitive` from `not_given` and from `withdrawn` to `accepted` (`owner`; `consent_current`), and `withdraw_sensitive` from `accepted` to `withdrawn` (`owner`);
>     - the age state (D7): `adult_check` from `unknown` to `self_declared_adult`, and from `self_declared_adult` to itself for a passing correction (`owner`; `A05`), and `adult_check_failed` from `self_declared_adult` to `unknown` (`owner`);
>     - identity verification (D18), with events no one can read as F01's email verification: `id_check_passed` from `unverified` or `staff_approved` to `verified` (`provider`, since the company's verdict arrives through the port, as F05's provider events do), `approve_without_id` from `unverified` to `staff_approved` (`moderator`; `A05`, `staff_approval`), and `revoke_approval` from `staff_approved` to `unverified` (`moderator`; `A05`).
>   - **F03:** `date_changed` from `pending`, `ambiguous`, `resolved`, `unavailable` and `unsupported` to `missing` (`owner`; D7's choice), one entry each.
>   - **F04:**
>     - the fields with the display choices, the age range, the area, the phone-location query and its response, the catalog, and the owner's completion read;
>     - `requirement_removed` from `visible` to `incomplete` (`system`). It is the demotion that follows another write, as `deletion_requested` follows F18's request: a consent withdrawal, a failing adult rerun, a new birth input revision, a revoked staff approval, and, in Stage B, the removal or restriction of the last approved photo. The cause keeps its own entry, with its actor's role, in its own flow. The owner's own edit that clears the summary keeps the existing owner `edit` from `visible` to `incomplete`.
>   - **F05 is Stage B's:** `approve` and `reject` from `review_pending` become the automated check's (`system`; OD-61), so the `moderator` entries go and `test_f05_quarantine_cannot_be_published_by_uploader` changes with them. These are changes to existing entries, which Stage B's prompt owns; `restrict_media` stays `moderator`.
>   - **`staff_approval`,** D2's setting being on, is a new trusted test prerequisite, added to `production-contracts.md`'s list.
> ```

**W6:** in "Owned paths", replace:

> ```
> `docs/architecture/production-contracts.md` (F02 to F06's server mapping)
> ```

with:

> ```
> `docs/architecture/production-contracts.md` (F02 to F06's index rows, kept in step with the registry by hand, and their server mapping; the oracle's list of trusted test prerequisites)
> ```

## 5. Item 3 — D8 and D7 against the models

**The three readings are right**, checked against the models, the schema and the registry:

- **The two states:**
  - `BirthInput.state` holds the revision's resolution, which is what `OwnBirthInput.resolution` returns. `EngineIdentity.state` holds the mapping's.
  - "Its chart resolved" needs both to be `resolved`. One condition must be added: **the mapping must point at the current revision.** One mapping row per account means a stale mapping could still read `resolved`.
- **The mapping row:**
  - `EngineIdentity` is one-to-one with the account, has a `PROTECT` foreign key to its birth input, and requires `adapter_version`.
  - Its check constraint ties `resolved` to non-null `engine_reference`, `engine_version` and `contract_version`, and `pending` to null ones.
  - So SV2 creating no row is right, and `OwnBirthInput.mapping_version` stays null. Returning a seeded mapping to `pending` clears those three and keeps `adapter_version`. No SV2 code writes an adapter version.
- **"Stops being current" as `missing`:**
  - P04's `setAdultDate` discards a birth input with another date ("The date changed. Re-enter private birth input; its previous mapping was cleared.").
  - The registry gives `missing` exactly one way out, the owner's `submit`, which writes a new revision. So no engine path can resolve a revision whose date no longer stands.
  - **One thing to say:** the owner's read of that revision returns it as it is, with `resolution: missing`. Its stale facts are the owner's own, and the client asks for re-entry.
  - W5's F03 entries record the move.
- **These belong in the brief,** where the design lives, not only in the prompt (W8).
- **D8's "`EngineIdentity` stays `pending`" is imprecise** once no row is created (W9), and check 8 has the same sentence (W10).

**W7:** in "Owned paths" (my miss in DM-52: D18 added a record, but the migrations line still names only D2 to D10), replace:

> ```
> (the settings, the field values, the area table and its data, consent's new purpose, the media grant): only what D2 to D10 need.
> ```

with:

> ```
> (the settings, the field values, the area table and its data, consent's new purpose, the age state's date, the identity verification record, the media grant): only what D2 to D10 and D18 need.
> ```

**W8:** in D8, replace:

> ```
> A new birth input revision returns the mapping to `pending` in the same transaction (F03: "changed input invalidates old mapping"), and a visible profile then follows D9's rule for a removed requirement.
> ```

with:

> ```
> A new birth input revision returns the mapping to `pending` in the same transaction (F03: "changed input invalidates old mapping"), and a visible profile then follows D9's rule for a removed requirement.
>   - **The two resolution states (DM-53):**
>     - `BirthInput.state` is the revision's resolution, returned as `OwnBirthInput.resolution`; `EngineIdentity.state` is the mapping's. A new revision starts `pending`.
>     - SV2 creates no `EngineIdentity` row, so `mapping_version` stays null, and no SV2 code writes a resolved state or an adapter version. A new revision returns an existing mapping (in SV2, only a test's seed) to `pending`, clears its engine reference and versions, keeps its `adapter_version`, and points it at the new revision.
>     - "Its chart resolved" (D9) means both states are `resolved` and the mapping points at the current revision. A test's seed sets both, with the `fixture:` values above on the mapping.
>     - A new eligibility date (D7) sets the current revision's state to `missing` and returns any mapping to `pending`. The owner's read then returns that revision with `resolution: missing`, completion reads it as no birth input, and only the owner's next `submit` moves it on, by writing a new revision.
> ```

**W9:** in D8, replace:

> ```
>   - `EngineIdentity` stays `pending`, and no transition
> ```

with:

> ```
>   - SV2 creates no `EngineIdentity` row and resolves none, and no transition
> ```

**W10:** in check 8, replace:

> ```
> `EngineIdentity` stays `pending` unless a test seeds it (D8), and a new revision returns it to `pending`.
> ```

with:

> ```
> SV2 creates no `EngineIdentity`, a new revision returns a test's seeded one to `pending`, and a new eligibility date sets the current revision to `missing` (D8).
> ```

## 6. Item 4 — DM-52's conditions as applied

- **B1 to B55,** checked by script against revision 2, ignoring line breaks:
  - **53 are word for word,** and none of their replaced texts remains.
  - **B20 (D7) and B28 (D9)** are word for word, plus a sentence marked "**Which (the manager, on DM-52's words)**". That is where my words said "the brief says which".
- **R1** is in OD-60, word for word.
- **R2 is OD-61.** It has:
  - Nathan's three quotes, each with its question;
  - the six rules in force;
  - my three defaults, marked as mine;
  - "adds to OD-55's D3 and to OD-60, and supersedes neither";
  - what waits on the decision message.
- **K1 to K7** are in place, word for word: K5 in the P11 plan, and K6 in a new "Carried to P10" section.
- **The four choices are approved:**
  - **D6's writer:** recorded as "Decided (DM-52): SV2's own writer, as recommended". That is accurate, since DM-52's section 8.1 approved it. One nit: the status line says all three choices are "each marked as the manager's". D6's is marked as DM-52's, so revision 3's status line can say two (D7, D9).
  - **D7's one date:** the second option, P04's discard. It is item 3's third reading, and the safer of the two: no birth input with a date that no longer stands can be resolved.
  - **D9's removed requirements:**
    - A removal that a member or staff is entitled to make demotes and is never refused: a consent withdrawal, a cleared summary, the last photo's removal or restriction, a new birth input revision, a failing rerun, and a revoked approval. A member must always be able to withdraw consent and remove photos, and staff must always be able to restrict.
    - An edit that would empty a required value is refused, since each is replaced, never cleared.
    - Both are right.
  - **D18 in Stage A:** right, since Stage A's completion requires identity verification or a staff approval, and D2's setting gates the approval.
- **The supersession sweep** found no living document still holding a text DM-52 replaced. Two hits are expected:
  - D11's lead sentence, which W1 replaces;
  - F03's acceptance, "Unknown time remains unknown", in the registry, its index row and the brief's quote of it. It stays true, since nothing guesses a time, and B21 has the server mapping say that a time is required.
- **DM-52's open row can close,** with W7 added.

## 7. Notion (read-only, at about 02:30 UTC; both pages as of 02:21 UTC)

What I read: the parts named here, not the whole of either large page.

- **Implementation Control:**
  - **The status** says the page was last matched at `c2ee87a`, with DM-53 to the Dev Manager and AM10-12.
  - **Main** is `c864edd`, with no PR open.
  - **The Branches bullet** lists `main` (`c864edd`), the manager branch ("`c2ee87a` at this sync") and `claude/dev-manager` (`093204a`), matching my `git ls-remote` at 02:23 UTC.
- **The Dev Manager page:**
  - DM-52's row: answered at `093204a`, a read of `73c109b`.
  - DM-53's row: "Awaited".
  - **A nit:** the page's table has six columns and no "Requested by". DM-53's row carries the repository's "App Manager 10" cell, so its question sits under "Report" and "Awaited" under "Verdict". The other rows are aligned.
- **The Work Register:**
  - **SV2:** In progress, with Stage A's prompt held for DM-53.
  - **SV3:** now records OD-60 and DM-52's carry, so DM-52's nit is fixed.
  - **A05, a nit:** its Next Action predates OD-61. The third message's "who moderates and how fast" is now partly answered: there is no staff review before a profile or a photo shows, and staff act only on reports.
- The repository wins (OD-27).

## 8. Where each item goes

| Item | Goes to |
|---|---|
| W1 to W10 | SV2's brief, revision 3, before Stage A's prompt |
| Stage A's prompt | Owns W2's paths and runs W4's checks, starting with `npm ci --ignore-scripts` in `packages/contracts` and in `apps/mobile`, as CI does |
| F05's `approve` and `reject` (W5) | Stage B's prompt, which owns those changes to existing entries |
| The status line's count of the manager's choices | Revision 3's status line |
| The two Notion nits | The manager's next Notion batch |
| DM-52's open row | Closes, with W7 |
| Confirming W1 to W10 as applied | My next consultation |

Status: complete
