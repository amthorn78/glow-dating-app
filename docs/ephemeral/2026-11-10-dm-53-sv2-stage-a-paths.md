# DM-53 consultation — SV2 Stage A's owned paths (the generated contract outputs and the flow registry), D8 against the models, and DM-52's conditions as applied

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 10 November 2026.**
- **Why:**
  - **The manager checked the brief against the code** while writing Stage A's prompt. D11's additive DTOs need two paths the brief does not own, and DM-52's report says one of them stays untouched. A departure from DM-52's words comes back first (DM-52, section 3), so the prompt is held.
  - **The review log's open row:** the next consultation confirms DM-52's conditions as applied.
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 10's disposition in the review log, "DM-53";
  - SV2's brief, revision 3;
  - Stage A's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** no SV2 prompt goes to Nathan; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-53's disposition and SV2's Stage A PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-53 — SV2 Stage A's owned paths (the generated contract outputs and the flow registry), D8 against the models, and DM-52's conditions as applied.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE or Railway;
- check environment variable names only.

**Where it stands.**
- **SV2's brief, revision 2** (`docs/planning/sv2-profiles-media.md`) applies DM-52 as written, with Nathan's answers as OD-61.
- **Writing Stage A's prompt, the manager read what D11's additions write.** Two paths the brief does not own are written by every DTO addition. Both were owned by the precedents DM-52 names ("as P04.3's `MediaCollection` and C1's responses were"). The manager's share is logged as AM10-12.
- **Stage A's prompt is held** until your answer. Nothing else waits on it.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The generated contract outputs** (D11; "Owned paths"; "Exclusions").
- **What the code does:**
  - `packages/contracts/scripts/generate.mjs` writes `apps/mobile/src/contracts/generated/` (`gapp-api-v1.ts`, `validators.js`, `validators.d.ts`) from every `$defs` entry of both schemas;
  - CI's Mobile checks job runs `npm run check` in `packages/contracts` (`.github/workflows/foundation.yml`, line 114). That runs `generate.mjs --check`, which regenerates the outputs in memory and fails on any byte difference ("Generated contract drift");
  - `packages/contracts/tests/corpus.test.mjs` imports those generated validators and `apps/mobile/src/contracts/production.ts`;
  - `packages/contracts/README.md`: "Committed artifacts live in `apps/mobile/src/contracts/generated/`. `--check` regenerates in memory and compares bytes; generated code is not hand edited."
- **So every new DTO changes those three files.** But the brief excludes `apps/**`, and D11 says "the mobile app's generated validators and fixtures are untouched until P10". Your report says the same (section 8: "The mobile app's validators and fixtures stay untouched until P10").
- **The precedent:** P06.2 C1's prompt owned "`apps/mobile/src/contracts/generated/**`, only as `npm run generate` writes it", with "The mobile app's checks must still pass with them".
- **Proposed words:**
  - **D11's lead sentence:** "New DTOs in the v1 production schema; every existing DTO is unchanged, so no mobile source, test or fixture changes until P10. The generated contract outputs in `apps/mobile/src/contracts/generated/` gain the new DTOs' types and validators. Only `npm run generate --prefix packages/contracts` writes them, never a hand edit, as for P04.3's and C1's DTOs. CI's Mobile checks job compares them byte for byte, and the shared corpus runs through them:"
  - **Owned paths, a new line:** "`apps/mobile/src/contracts/generated/**`, only as `npm run generate --prefix packages/contracts` writes it. If a mobile source, test or fixture would have to change for the Mobile checks job to pass, the session stops."
  - **Exclusions:** "`apps/**`, except the generated contract outputs (Owned paths)", in place of "`apps/**`".
- **Asked:** these words, or yours.

**2. The flow registry and the package's README** (D11; "Owned paths").
- **What the record shows:**
  - `packages/contracts/production/flows-v1.json` lists each flow's `request_contracts`, `response_contracts` and `projection_roles`. `test_schemas_and_flow_references` (`packages/contracts/tests/test_production_contract.py`) requires the keys of `projection_roles` to equal `response_contracts`;
  - P04.3 registered `MediaCollection` in F05, with role `owner`. C1 registered its DTOs in F11 (the README's "P06.2 C1 conversation reads", which is that change's section);
  - `production-contracts.md`'s flow index is "generated from the committed flow registry", and lists them;
  - **the registry's transitions:**
    - F02 has owner `accept` and `withdraw`, with no purpose;
    - F03 has no transition to `missing`;
    - F04 has `complete` (owner, policy `A05`) and an owner `edit` from `visible` to `incomplete`, but no system or staff demotion;
    - no flow holds an identity verification state.
- **The gap:** the brief owns `gapp-api-v1.schema.json`, `openapi.json`, the corpus and the contract tests, but not `flows-v1.json` or the README.
- **Proposed words, in Owned paths:**
  - "`packages/contracts/production/flows-v1.json`: D11's DTOs, each in its flow's `request_contracts`, `response_contracts` and `projection_roles` (`owner`), as F05's `MediaCollection` and F11's C1 DTOs are. Also the transitions SV2's writers make that the registry lacks, each as a new entry. No existing entry changes."
  - "`packages/contracts/README.md`: a section for SV2's additions, as P06.2 C1 has."
  - `production-contracts.md`, already owned, keeps its F02 to F06 index rows in step with the registry.
- **Which flow each joins, the manager's reading:**
  - **F02:**
    - the sensitive-fields consent's intent and read, with owner `accept` and `withdraw`;
    - the identity verification state. The system sets `verified`; staff approve and revoke without ID while D2's setting allows it, and a revoked approval returns the state to `unverified`;
  - **F03:** a new owner transition from the current revision's state to `missing` when the eligibility date changes (item 3);
  - **F04:**
    - the fields, the display choices, the age range, the area, the phone-location query and the catalog;
    - the owner's completion read;
    - the demotion from `visible` to `incomplete` for a removed requirement: role `system` for a failing adult rerun or a new birth input revision, role `staff` for a revoked staff approval, and role `owner` for a consent withdrawal or a cleared summary (the existing owner `edit` covers the summary).
- **Asked:**
  - these words, or yours;
  - is the mapping to flows and roles right?

**3. D8 and D7 against the models.** The brief does not name these three facts. The prompt will state the manager's reading unless you give other words.
- **The birth input's own state.** `BirthInput.state` (`missing`, `ambiguous`, `pending`, `resolved`, `unavailable`, `unsupported`) is the revision's resolution, returned as `OwnBirthInput.resolution`. It sits beside `EngineIdentity.state` (`pending`, `resolved`).
  - **Reading:**
    - SV2 keeps both pending;
    - "its chart resolved" (D9) means both are `resolved`, and a test's seed sets both, with D8's `fixture:` provenance on the mapping;
    - a new revision starts `pending`, and any mapping returns to `pending` and points at it.
- **The mapping row.** `EngineIdentity` is one row per account, with a `PROTECT` foreign key to its birth input, and its `adapter_version` is required even when pending.
  - **Reading:**
    - SV2 creates no `EngineIdentity` row: none exists until an engine adapter creates one, and `OwnBirthInput.mapping_version` is null;
    - a new revision returns an existing mapping (a seeded one, in SV2's tests) to `pending`, keeping its `adapter_version`;
    - so no SV2 code writes an adapter version.
- **"Stops being current"** (D7's choice, on DM-52's words: a new eligibility date while a current birth input holds another).
  - **P04's fixture** discards the birth input and clears the mapping (`apps/mobile/src/onboarding/store.ts`, lines 227 to 231: "The date changed. Re-enter private birth input; its previous mapping was cleared.").
  - **F03's `submit`** starts from `missing`.
  - **Reading:**
    - in the date change's transaction, the current revision's `state` becomes `missing`, and any mapping returns to `pending`;
    - the next `submit` writes a new revision;
    - completion reads `missing` as no birth input.
- **Asked:** are these readings right?

**4. DM-52's conditions as applied** (the review log's open row).
- **What to check, in revision 2 at this commit:**
  - B1 to B55;
  - R1, in OD-60;
  - R2, recorded as OD-61;
  - K1 to K7, in the carried-items file and the P11 plan;
  - the four choices revision 2 marks as the manager's: D6's writer, D7's one date, D9's removed requirements, and D18 in Stage A (D1).
- **Asked:** are they applied as written?

**What happens next:** App Manager 10 applies your words in revision 3 and gives Nathan Stage A's prompt, with its TypeSafe reading. No GitHub operation is asked of Nathan.
