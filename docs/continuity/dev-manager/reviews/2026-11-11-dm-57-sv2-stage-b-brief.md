# DM-57 — SV2's brief, revision 6: Stage B, R2 for photos, and the pointer order

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 10, relayed by Nathan (OD-25).
- **Read at:** `fea05085df1ffb47288c639514ddcce17ec37bfa` of `claude/magical-wozniak-yfmmx2`. Also read the code on `main` at `4dc2061` (PR43, Stage A). Both were still there at 00:51 UTC (`git ls-remote`).
- **Written:** 11 November 2026, finished at 00:51 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only. None of the HDE names is present, but three AWS names are (section 8). I read no value.
  - I called no provider, database, HDE, Railway, Cloudflare or TypeSafe service, ran no application code, and wrote only this file.
  - Notion was read, not edited.

## 1. What I read

- **The consultation** at `fea0508`.
- **The brief, revision 6,** in full at `fea0508`:
  - its own change, the diff from `780fb20`;
  - the change to it in the receipt commit `65a7221` (status lines and pinned links).
- **For item 1:**
  - OD-62's register row, and PF01 §4's media line ("Cloudflare Images/private R2 as appropriate");
  - the media provider mapping: its OD-62 note (lines 8 to 10) and its R2 events row (line 54);
  - `private-media-fixtures.md`;
  - the contract document's F05 row and its two paragraphs on `MediaUploadGrant` (lines 188 and 200);
  - the schema's `MediaUploadGrant` and `Error`;
  - F05's registry entries and their contract test.
- **The matrix:**
  - section 10 (its recheck triggers and dated events);
  - its processor, transfer, disclosure and photo rows;
  - DM-37's rules for every brief that takes a row (the carried-items file).
- **The code at `4dc2061`:**
  - `settings_store.py`, `recompute.py`, `tx.py`, and the error answer in `views.py`;
  - every row lock in `services/api` and the proof, by search;
  - the seed migration `0007` and the fields of `SettingVersion` and `StaffAudit`;
  - `profile_cases.py`'s `CASE_COUNT`.
- **For item 5:** the manager workflow's steps 5 and 7, and the CI policy's lines on force pushes.
- **For where the carries go:** the P11 plan (`docs/testing/p11-deferred-acceptance.md`) and the carried-items file.
- **For item 4:** my DM-56 report.
- **Notion,** read-only (section 9).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. D10 for R2 (OD-62) | **Approved with conditions.** The reading is right, and Nathan's answer is not needed before Stage B. The two ports and the processing step at `review` stand. U1 to U5 close two gaps: an upload that processing cannot make a variant of has no path, and could skip G-02's seam; and the byte limit and the credential's route to the client are unsettled. U6 and U7 carry the rest to P11 and P07. **No matrix recheck is needed before Stage B** |
| 2. D19, one pointer order | **Approved: (a), with one condition.** The rule's statement covers every lock path in the code. But it says more than its check enforces, and the check must record the publication's own lock. U8 gives the words |
| 3. "Stage B (revision 6)" | **Approved as one stage, with conditions.** The scope, stop rules and review stand. U9 lets the session change the F05 test that item 3 names, and U10 gives the media policy's seed reason. Three notes for the prompt (section 5) |
| 4. DM-56's V1 to V5 as applied | **Confirmed.** Each new text is present once on `main` (`4dc2061`) and at `fea0508`, with no old text left |
| 5. The manager branch after a merge | **Approved with a change (U11).** The rule is right. But placed after the receipt, which is itself a commit, its fast-forward never happens. U11 puts it before the receipt |
| Notion | **Matches** `fea0508`, apart from two older sentences on Implementation Control and one older row on the Dev Manager page, all optional (section 9) |

**How to apply:**
- **U1 to U5 and U8 to U10** change the brief (its revision 7). **U6** changes the P11 plan, **U7** the carried-items file, and **U11** the manager workflow, step 7.
- **All eleven are Markdown records.** None changes code, a test or the workflow file. All are in given words, and line breaks may move.
- **Verified by script:** each old passage was found exactly once at `fea0508`, and all eleven apply in order to copies.
- **No further read is needed before Stage B's prompt** if they are applied as written; a departure comes back first. My next consultation confirms them as applied (step 6).

## 3. Item 1 — D10 for R2 (OD-62)

**The reading is right, and it needs no answer from Nathan now.**
- **The canon is unchanged.** OD-62 says "we will use R2 object storage for photos", and PF01 §4 allows "Cloudflare Images/private R2 as appropriate". The reading takes private R2 for the originals and the variants alike.
- **The brief states only two R2 facts,** and both are the ones the mapping checked on 23 September (its line 54):
  - R2's events reach a consumer through Queues;
  - object-delete events omit size and entity tag.

  Everything else is P11's to verify (PV04, DB08), as the mapping's OD-62 note says.
- **Where processing runs is P11's choice, under OD-50.**
  - OD-62 neither picks nor rules out a Cloudflare service that reads R2's objects.
  - Either choice fits the processing port, and its cost goes to Nathan first when P11 makes it.
  - If Nathan meant "no Cloudflare Images in any form", that choice is where it would show, and it is his then. Nothing in Stage B depends on it.

**The two ports and the processing step at `review` stand.**
- **The step sits where P04.3's fixture already simulates processing** (`private-media-fixtures.md`: "Only system review moves quarantined → review_pending").
- **No state or entry is needed for it:** F05's `review` entry is `system` already.
- **The split holds whichever processor P11 picks:** storage keeps and deletes objects, and processing makes the variant.

But two gaps need words before the prompt.

**Gap 1: a photo processing cannot make a variant of.**
- **D10 says what processing does only when it succeeds.** F05 has no exit from `quarantined` except `review` and `remove`.
- **So nothing defines what happens** to an original that does not decode within the policy's bounds, or no longer matches its completion. As written, it would stay `quarantined` with no variant, or the session would invent an entry.
- **And the seam sees only the variant** ("before the detection seam and the automated check see it"). So a file made to fail processing would never reach G-02's seam.
- **U1 and U2 close the gap:**
  - every adopted upload passes the seam;
  - when there is no variant, the seam is given the original;
  - the asset is then rejected through F05's existing `reject` (`system`), so no state or entry is added, as the consultation intends;
  - an unavailable store is not a processing failure.
- **The seam keeps the variant as its normal input.** A detection service outside Glow then sees no original's metadata (location included) unless no variant exists. U7 carries that case to P07.1.
- **U5 adds the rule to the review's R2 item.**

**U1:** in the brief, D10, "The system review step is Glow's own processing", replace:

> ```
> It reads the adopted original, checked against the completion's size and entity tag, decodes it within the policy's bounds, removes its metadata, re-encodes it and writes the variant under a new key, before the detection seam and the automated check see it. The original is never delivered.
> ```

with:

> ```
> It reads the adopted original, checked against the completion's size and entity tag, decodes it within the policy's bounds, removes its metadata, re-encodes it and writes the variant under a new key. Every adopted upload then passes G-02's seam before the automated check sees it: the seam is given the variant, or the original when processing made none. If processing cannot make a variant (the original does not match the completion, or does not decode within the policy's bounds), no variant is written; the asset passes the seam with its original, moves to `review_pending`, and is rejected (F05 `reject`, `system`) with the reason that no variant was made, so a file made to fail processing cannot skip the seam. An unavailable store is not such a failure: the step changes nothing and can run again. The original is never delivered.
> ```

**U2:** in the brief, acceptance check 10, replace:

> ```
>     - processing reads only the adopted original (its size and entity tag), only its variant is ever referenced for delivery, and no object key holds an account, profile or asset ID, a filename or a member value;
> ```

with:

> ```
>     - processing reads only the adopted original (its size and entity tag), only its variant is ever referenced for delivery, and no object key holds an account, profile or asset ID, a filename or a member value;
>     - an upload with no variant (an original that does not match its completion, or does not decode within the policy's bounds) still passes the seam, with its original, and is rejected (`system`); an unavailable store changes nothing;
> ```

**Gap 2: the byte limit, and the credential's route to the client.**
- **"The policy's byte limit" leaves the version open.** The media policy is a setting, and it can be republished between a grant and its completion. The grant should record the version it was issued under, and the completion should be checked against that version's limit (U3, U4).
- **`MediaUploadGrant` cannot carry the credential:**
  - the schema closes it (`additionalProperties: false`);
  - `grant_ref` takes `PolicyVersion`'s pattern: a letter or digit, then only letters, digits and `._:-`, at most 100 characters. No URL fits it, since none can hold a `/`;
  - the contract document says the grant is "neither a provider endpoint nor proof of an uploaded asset" (line 188), and that it does not gain fields (line 200).

  A session told to "issue the upload credential" could not return it. U3 says what Stage B returns, and leaves the route to the client to P11 (U6).

**U3:** in the brief, D10, "The upload grant", replace:

> ```
> it adopts only the first completion that matches the grant's key and the policy's byte limit, and a later completion for that key changes nothing (check 10).
> ```

with:

> ```
> it adopts only the first completion that matches the grant's key and the byte limit of the policy version the grant records (the one it was issued under), and a later completion for that key changes nothing (check 10). The member's route returns `MediaUploadGrant` unchanged: its `grant_ref` is the grant's opaque reference, and its pattern cannot hold an address. In Stage B the store's credential goes to no member; how it reaches the client (a new DTO, additive under D11, or an upload through Glow's server) is P11's, once PV04 verifies its form.
> ```

**U4:** in the brief, acceptance check 10, replace:

> ```
> or exceeds the policy's bytes, changes nothing
> ```

with:

> ```
> or exceeds the byte limit of the policy version its grant records, changes nothing
> ```

**U5:** in the brief, "Review plan", the R2 item, replace:

> ```
> processing on the adopted object, and deletion acknowledged for every object;
> ```

with:

> ```
> processing on the adopted object, every adopted upload through the seam (one with no variant included), and deletion acknowledged for every object;
> ```

**The matrix: no recheck before Stage B.** It is needed only when P11 activates R2 and chooses the processor, and when P07.1 chooses G-02's detection service.
- **Stage B sends no byte anywhere.** It has fixture adapters only, with no R2 call, credential or SDK.
- **The matrix names no storage provider:** neither Cloudflare Images nor R2 appears in it.
- **A storage provider is not one of section 10's triggers.** "A detection or moderation vendor" is.
- **The rows R2 and a processor touch** are about processors, transfers and disclosure:
  - EU-38, EU-42 and EU-48 (EU-48 already names storage);
  - UK-36 and UK-41;
  - AP-22, AP-27 and AP-30.

  P11's brief takes them when it activates R2, and DM-37 5.1 has it recheck them on the day it is written. A Cloudflare service that processes photos is a processor too, so the same rows cover it. U6 records the credential's form there.
- **P07.1's choice of detection service is a section 10 trigger already.** U7 adds the private bucket's consequence for it.
- **One dated event falls while Stage B is likely to run:** UK-23 on 12 November (intimate image reports from a designated trusted flagger).
  - Its intake is gap G-03's, with no owner.
  - Stage B builds nothing for it.
  - Section 10 asks for that row's recheck on the day.

**U6:** in the P11 plan, after the entry from SV2 Stage A's exact-head review (finding 15), replace:

> ```
> P11's database integration decides whether one is added.
> ```

with:

> ```
> P11's database integration decides whether one is added.
> - **From SV2's brief, revision 6 (DM-57):** the upload credential's form (a time-limited signed upload address for the grant's key, D10) and how it reaches the client: a new DTO, additive (D11), or an upload through Glow's server. `MediaUploadGrant` gains no field (the contract document, "P04.3 media collection and binding clarification"). P11 decides once PV04 verifies the form. Where R2 supports it, the credential is signed so that an upload cannot replace an object already written; the domain still does not rely on that (D10).
> ```

**U7:** in the carried-items file, "Carried to P07", after the entry from the review after C2 (finding 6), replace:

> ```
> Nothing leaks, and a restricted profile is not shown. P07 decides what a restriction stops.
> ```

with:

> ```
> Nothing leaks, and a restricted profile is not shown. P07 decides what a restriction stops.
> - **From SV2's brief, revision 6 (DM-57), for G-02 (P07.1):** photos sit in a private R2 bucket, and nothing is served publicly (D10). G-02's seam is given each adopted upload's variant, or its original when processing made none (D10). P07.1's detection service must be one Glow hands those bytes to, or one that reads the private bucket: a scanner that sees only publicly served images would see none of them. An original keeps its metadata, so P07.1 also decides how one is sent outside Glow, under the matrix's third-party rows (AP-30, EU-42).
> ```

## 4. Item 2 — D19, one pointer order

**(a), approved.**

**Why (a) rather than (b):**
- **Production runs what the proof proves.** The suite imports `glow_profiles` unchanged. Under (b), production would run with the check switched off, a configuration no case covers.
- **(b) does not keep server errors from members.**
  - `tx.run` answers a deadlock that PostgreSQL breaks as `provider_unavailable` (503), and it answers the check's error the same way (the note below).
  - Under (a), an out-of-order path fails on its first call, in the suite or at its first use.
  - Under (b), it fails only when two transactions happen to meet, which is much harder to find.
- **The check is cheap:** one set lookup per pointer lock.

**Why not (c):** its claim rests on behaviour no documentation states. PostgreSQL granted a share lock without queueing behind a waiting update lock: the review saw it on 17.11, and no suite case tests it (DM-56 V4).

**Every lock path, at `4dc2061`:**
- **The only pointer locks** in `services/api` are in `settings_store`:
  - `read_shared` (raw `FOR SHARE`, line 69);
  - `publish` (`select_for_update`, line 118).
- **`read_unlocked`** (line 81) takes no lock.
- **No other code locks a pointer:** not `glow_chat` (its `_lock_shared` takes account, session and match rows), not `glow_identity`, not the proof.

So the statement covers every lock path, with two corrections:
- **It says more than its check.** "Takes all of them in its first `read_shared` call" rules out something harmless that the check allows: a transaction that takes `consent.onboarding` and later a `profile.*` pointer, in a second call, keeps name order and passes the check. Only the order matters for a wait cycle. So the rule should state the order, as the check does, and keep the single first call as the way SV2's transactions meet it.
- **The check must record the publication's own lock.** `publish` takes it with `select_for_update`, not through `read_shared`. Unless `settings_store` records it as held, the publication's later read is checked against nothing.

**U8:** in the brief, D19, replace:

> ```
>   - **The rule.** Every transaction that locks settings pointers takes all of them in its first `read_shared` call, in name order. A publication takes its own pointer `FOR UPDATE` and then any pointer it reads, which today sorts after it (`chat.history`, then `consent.onboarding`). A pointer read again later in the same transaction is already held, and waits for nothing.
> ```

with:

> ```
>   - **The rule.** Every transaction locks settings pointers in name order: it never locks a pointer whose name sorts before one it already holds, unless it already holds that pointer. SV2's member and staff transactions meet it by taking all their pointers in their first `read_shared` call; a pointer read again later in the same transaction, as the recompute rereads `consent.onboarding`, is already held and waits for nothing. A publication takes its own pointer `FOR UPDATE` and then any pointer it reads, which today sorts after it (`chat.history`, then `consent.onboarding`); `settings_store` records the publication's own pointer as held before that read.
> ```

**What a member gets from the check** (a note for the prompt; no brief change):
- **`tx.run` answers the check's error like any other exception** (lines 144 to 153). Anything other than a refusal or an integrity error comes back as `provider_unavailable`, marked retryable, with the exception's type as the internal reason.
- **That is acceptable for a sealed slice.** The contract has no internal-error code, and adding one would change an existing DTO (D11).
- **Stage B's offline test should show that result,** and that the check's error is not a `Refused`. Then the check can never turn into a member's refusal.

## 5. Item 3 — "Stage B (revision 6)"

**The scope stands as one stage.**
- **Its parts depend on each other.** The photo requirement needs the automated check's approval, and the registry change needs the writers.
- **D19's four changes are small,** and the review already takes every change Stage B makes to Stage A's code.

**The stop rules stand.** A decoder or image library is a new dependency, so the fixture adapter cannot grow a real decode path. That path is PV04's.

**The review stands,** with U5's addition.

**Missing before the prompt:**
- **The F05 test (U9).** The owned paths let the contract tests take "D11's additions only". But item 3 and D11 change an existing test: `test_f05_quarantine_cannot_be_published_by_uploader` (`packages/contracts/tests/test_transition_contract.py:137`, whose line 140 lets `STAFF` approve today). As written, the session would have to stop, or step outside its paths.
- **The media policy's seed reason (U10).**
  - D2 seeds each setting with the reason "OD-60", or, for D18's setting, the register row of 10 November.
  - Neither fits the media policy, whose version 1 holds `development-media-1`'s values.
  - U10 names its reason, and a new data migration, since `0007`'s seed "never changes after it is applied" (its docstring).

**U9:** in the brief, "Owned paths", replace:

> ```
> - `packages/contracts/production/gapp-api-v1.schema.json`, `openapi.json` (DTOs only, no paths), `corpus/shared-v1.json` and the contract tests: D11's additions only.
> ```

with:

> ```
> - `packages/contracts/production/gapp-api-v1.schema.json`, `openapi.json` (DTOs only, no paths), `corpus/shared-v1.json` and the contract tests: D11's additions only, and in Stage B the change D11 names to `test_f05_quarantine_cannot_be_published_by_uploader` (`packages/contracts/tests/test_transition_contract.py`).
> ```

**U10:** in the brief, D2, "The launch defaults", replace:

> ```
> or, for D18's setting, the register row that records Nathan's answers of 10 November 2026.
> ```

with:

> ```
> or, for D18's setting, the register row that records Nathan's answers of 10 November 2026. D10's media policy is seeded the same way in Stage B, by a new data migration, with the reason `development-media-1`, whose values it holds.
> ```

**Notes for Stage B's prompt** (no brief change):
- **The environment** (section 8).
- **The photo requirement reaches Stage A's cases.**
  - Once D9's requirement holds, every case that makes a profile `visible` needs an approved photo.
  - The pinned case count changes with Stage B's cases: `CASE_COUNT = 53` at `profile_cases.py:61`, held by `test_profile_offline.py:512`.
  - Both are in Stage B's paths. If the prompt says so, neither reads as a departure.
- **The check's error as a member sees it** (section 4).

## 6. Item 4 — DM-56's V1 to V5 as applied

**Confirmed.** I matched each V block of my DM-56 report against the four files, at `fea0508` and on `main` (`4dc2061`):
- `data-model.md` (V1, V2);
- the brief (V3);
- the evidence record (V4);
- the carried-items file (V5).

Each new text is present exactly once, and no old text is left. The deferred rows for V1 to V5 can close.

## 7. Item 5 — The manager branch after a merge

**The rule is right:**
- **It ends the practice behind AM10-13,** where the branch carried on from the merged head without `main`.
- **It keeps to the existing rules:**
  - the CI policy's procedural substitutes, "never force-pushing";
  - step 5's rule: "Integrate with `git merge --ff-only <head>`, or a merge commit if the manager branch moved".
- **Merging rather than rebasing also protects the records.** A rebase gives the receipt commits new IDs, and the records cite the old ones; Implementation Control cites `65a7221` and `c52b41f` today. The session's git rule (start again from `main`, rebasing later commits) would leave them orphaned. The project's rule should govern here, and U11 states it.

**But the placement defeats the fast-forward.**
- **The proposed words follow "record an ordinary-documentation receipt",** and that receipt is itself a new commit on the manager branch.
- **In that order a commit always follows the merged head.** So the branch is always merged and never fast-forwarded, as happened after PR43: `65a7221` and `c52b41f`, then `780fb20`.
- **The words would still work as written**, but their first branch would never be taken.
- **U11 splits the bullet,** so that the branch takes up `main` before the receipt, and names the fetch that the fast-forward needs.

**U11:** in the manager workflow, step 7, replace:

> ```
>    - Verify actual main and record an ordinary-documentation receipt in `docs/testing/evidence/`.
> ```

with:

> ```
>    - Verify actual main.
>    - **Bring `main` into the manager branch** (DM-57). Before any new commit on the manager branch, the receipt included, fast-forward it to `main` (`git fetch origin main`, then `git merge --ff-only origin/main`). If commits already follow the merged head, merge `main` into the branch instead. No history is rewritten, and the next PR's merge base is `main`'s merge commit.
>    - Record an ordinary-documentation receipt in `docs/testing/evidence/`.
> ```

## 8. The environment (names only)

- **Not present:** `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, and any `STREAM_*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name.
- **Present in this session's process environment:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`.
  - I read no value.
  - The environment's own settings list no variables, so these come from elsewhere in the container. I do not know where.
- **Why it matters for Stage B:**
  - an S3-compatible client reads the first two from the environment by default;
  - Stage B is the photo slice that P11 will put on R2.

  Stage B adds no client (its stop rule), so nothing reads them today.
- **For the prompt:**
  - the session checks these three names as it checks the HDE ones, by name only;
  - it reads no value;
  - it runs app and proof commands in a clean environment, as CLAUDE.md requires.

## 9. Notion (read-only, at about 00:28 UTC; content as of 00:14 UTC)

**How I read it:**
- I searched each page's full text for the items asked.
- I compared the register copy with the repository's register row by row, by script.
- I did not read every line of Implementation Control's history.

**Implementation Control** says it is matched to `fea0508`.
- **Its status says what the handoff says there:**
  - revision 6, OD-62 and D19;
  - `main` merged into the manager branch at `780fb20`;
  - DM-57 waiting.
- **Its state matches:** `main` at `4dc2061`, no PR open, and the three branches, with `claude/dev-manager` at `d342f05`.
- **Optional:** two older bullets in the same section contradict the repository.
  - "Next items (OD-49): now P06.2-F (PR40)". P06.2-F is done; the handoff lists it as done.
  - The Manager bullet's "PR40 is open from it". The next bullet says that no PR is open.

  Both were already on the page at my earlier reads in this session, DM-56's included, and I did not report them then. The repository wins (OD-27).

**SV2's Work Register row** matches.
- **State:** "In progress", with its evidence pinned at `fea0508`.
- **Its next action names:**
  - revision 6, OD-62 and D19;
  - Stage A's merge (PR43, `4dc2061`);
  - DM-57 at `fea0508`;
  - Stage B's carried items.
- **G-01's row** now names the two decisions carried to P07, so DM-56's optional nit was taken.

**The Dev Manager page** matches the review log at `fea0508`.
- **DM-56** is considered: merge `607ce47`; V1 to V5 applied at `a644771`; the nit taken.
- **DM-57** is pending.
- **Optional:** its Sessions row for Dev Manager 4 stops at DM-41. The repository's row (the Dev Manager README) runs to DM-44, and the consultation rows hold every answer.

**The register copy** matches.
- **Its rows:** 62, OD-01 to OD-62, as in the repository.
- **OD-62** matches word for word.
- **Across all 62 rows,** once formatting is set aside, the only differences are eight places in seven rows where Notion writes a file path as a name, for example "AGENTS file" for `AGENTS.md`. These are OD-04, OD-07, OD-26, OD-35, OD-47, OD-53 and OD-55.

## 10. Where each item goes

- **The brief, revision 7:**
  - U1 to U5 (D10, check 10, the review plan);
  - U8 (D19);
  - U9 (the owned paths);
  - U10 (D2).
- **The P11 plan:** U6.
- **The carried-items file:** U7, under "Carried to P07".
- **The manager workflow, step 7:** U11.
- **Stage B's prompt:**
  - the environment check (section 8);
  - the photo requirement in Stage A's cases and `CASE_COUNT`;
  - the check's error as a member sees it.
- **The review log:** DM-57's dispositions. The deferred rows for DM-56's V1 to V5 close (item 4).
- **Nathan:** the three AWS names (section 8), for his information. Nothing is asked of him.
- **Notion,** optional: the two Implementation Control sentences, and Dev Manager 4's Sessions row.

Status: complete
