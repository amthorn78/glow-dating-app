# Nathan's answer to DM-52's Q1: the chart, staff review and approval

- **Given:** directly in Dev Manager 4's session (`session_01Q789u2u6fuC4fQPtHzP9gN`) on 10 November 2026, after the DM-52 report (`eefa349`).
- **Recorded by:** Dev Manager 4, verbatim, as the charter requires.
- **Boundaries kept:** as in DM-52. I wrote only this file and read only the repository at `73c109b`.

## His words

> "the human design chart is calculated immediately when someone signs up, there is no lag - there is no manual staff review either. Approval must be automated based on ID verification."

## What it answers

- **Q1 (a), the chart: answered.**
  - A resolved chart stays a completion requirement, as P04.2's reviewed rule has it, and it costs no wait.
  - **My reading:** "when someone signs up" means as soon as the member gives their birth details. The chart needs the birth date, time and place, and the birth step comes after the adult step (`/birth`).
  - **What follows:** if the engine cannot resolve a chart (it is down, or the birth data is ambiguous or unsupported), the profile waits until it can. That is the reviewed rule. Q4 asks him about an unknown birth time.
- **Q1 (b), staff review: answered.** No staff review stands between a complete profile and `visible`. P04.2's "Profile review" requirement is dropped, by his decision.
- **New: approval is automated, on ID verification.**
  - Identity verification becomes a completion requirement, decided by an automated check with no staff step.
  - It is not the contract's `verify_identity`. In `OnboardingEligibility.requirements` that value means email verification: the mobile store adds it while the account is `unverified`.
- **A correction to DM-52.** In section 8, I wrote that inventing an engine identifier, even in a test, would cross the brief's D8. That was too strict for test setup. A row that a test seeds in the disposable database, marked `fixture:` and written by no app code, is test data, not an identifier the app invents. PF01 §7 allows synthetic labels in test contexts when they are marked as fixtures. Now that the chart is a requirement, completion's success path needs such a row (B16).

## What changes in DM-52

| DM-52 item | Now |
|---|---|
| Q1 | Answered |
| B8c | Withdrawn; B15 takes its place |
| B9d | Withdrawn; B19 takes its place |
| B12a | Withdrawn; B20 takes its place |
| K5 | Withdrawn; K6 takes its place |
| New | B16 (the chart in tests), B17 (D18, identity verification behind a seam), B18 (the owner's completion read), B21 (acceptance), B22 (the review's focus), K7 (P07) |
| Everything else | Unchanged |

**Still true:**
- No further read is needed before Stage A's prompt if every condition is applied as written.
- A script applied every condition in order to a copy of revision 1: all of DM-52's except the three withdrawn, then B15 to B22. Each passage it replaces occurs exactly once.
- B22's passage is one that B13 adds, so B22 applies after B13.

## The conditions

**B15** (replaces B8c): in D9, replace:

> ```
>     The sensitive fields are not required.
> ```

with:

> ```
>     The sensitive fields are not required. **Two more requirements, from Nathan's answer of 10 November 2026** ("the human design chart is calculated immediately when someone signs up, there is no lag - there is no manual staff review either. Approval must be automated based on ID verification"):
>     - a current birth input with its chart resolved (P04.2's reviewed rule). The chart is calculated as soon as the birth input is given; if the engine cannot resolve it (it is down, or the birth data is ambiguous or unsupported), the profile waits until it can. SV2 has no HDE, so in the sealed runtime nothing resolves (D8);
>     - identity verification passed, decided by an automated check with no staff step (D18).
>
>     No staff review stands between a complete profile and `visible`: P04.2's "Profile review" requirement is dropped by his answer.
> ```

**B16:** in D8, replace:

> ```
> No HDE call, and no engine identifier is invented (the protected boundary; A01).
> ```

with:

> ```
> No HDE call, and no engine identifier is invented (the protected boundary; A01). **The chart in completion's tests:** no SV2 code writes a resolved mapping. To prove completion's success path, a test may seed a resolved `EngineIdentity` in its own setup, through the ORM in the disposable database, with `engine_reference`, `engine_version`, `contract_version` and `adapter_version` each beginning `fixture:`, so it can never pass for an engine result. A new birth input revision returns the mapping to `pending` in the same transaction (F03: "changed input invalidates old mapping"), and a visible profile then follows D9's rule for a removed requirement.
> ```

**B17:** before "Owned paths", add D18. Replace:

> ```
> ## Owned paths (the sessions)
> ```

with:

> ```
> - **D18 — Identity verification, behind a seam** (Nathan, 10 November 2026: "Approval must be automated based on ID verification").
>   - **One account-private record:** the identity verification state, `unverified` until a check passes and then `verified`, with the method, the provider's opaque reference and the time. It is written only through a port, after the account row lock (DM-13 4.1), with the eligibility bump. It is not the contract's `verify_identity`, which means email verification.
>   - **SV2 builds the seam and no provider:** its fixture adapter never writes `verified` in the runtime, and a test may seed `verified` in its own setup, as D8's mapping is seeded. Completion requires `verified` (D9).
>   - **The rest comes with Nathan's decision, after the matrix's recheck:** what the check is, its provider, the data it collects (a selfie matched to an ID is face geometry, UST-51), its cost (an M07 line he approves first, OD-50), its consent and retention, what a member can do when it fails, and whether a verified birth date replaces the self-entered one as the adult check (D7; OD-55's D3).
>
> ## Owned paths (the sessions)
> ```

**B18:** in D11, replace:

> ```
>   - the current catalog: the lists, which may be narrowed, and the defaults, read-only for the member;
> ```

with:

> ```
>   - the current catalog: the lists, which may be narrowed, and the defaults, read-only for the member;
>   - the owner's completion read: the missing requirements, from a closed list of its own (consent, the adult check, the profile's fields, the area, a photo, the chart, identity verification), for the owner only, since P04.2's rule keeps missing requirements visible to the owner. Identity verification gets its own value, not `verify_identity`, which `OnboardingEligibility` uses for email verification;
> ```

**B19** (replaces B9d): in D10's moderator decisions, replace:

> ```
> are domain operations that take a staff subject and a reason and write `StaffAudit`; P07 exposes them.
> ```

with:

> ```
> are domain operations that take their decider and a reason and write `StaffAudit`. The decider is an automated check's result, recorded as a `system:` subject as D2's seed is, or a staff subject where a staff step remains (Nathan, 10 November 2026: "there is no manual staff review"; whether that covers photos is put to him). P07 exposes the staff ones. An owner's removal and a moderation restriction keep separate revocation records, so a later approval clears only the restriction and never undoes an owner's removal (`private-media-fixtures.md`, "F05 and revocation").
> ```

**B20** (replaces B12a): in "Owned paths", replace:

> ```
> - `services/api/glow_domain/`: new modules for the profile fields, the settings' schemas and fixed limits, and the media port only.
> ```

with:

> ```
> - `services/api/glow_domain/`: new modules for the profile fields, the settings' schemas and fixed limits, the media port and the identity verification port (D18); and in `identity.py`, the age section only, for D7's date and transition.
> - `services/api/glow_identity/age.py`: D7's transition only; `record` is unchanged.
> ```

**B21:** in check 9, replace:

> ```
>    - resume rechecks completion;
> ```

with:

> ```
>    - resume rechecks completion;
>    - completion is refused without a resolved chart and without identity verification, and passes with both seeded in setup; no SV2 code writes either;
>    - the owner's completion read lists exactly what is missing;
> ```

**B22** (after B13): in the review's focus as B13 leaves it, replace:

> ```
>   - the stored idempotency digests (D17);
> ```

with:

> ```
>   - the stored idempotency digests (D17);
>   - the chart and identity verification requirements: no runtime path writes a resolved mapping or `verified`, and a test's seeded rows cannot reach the runtime;
> ```

## Carried items

**K6** (replaces K5), to the P11 plan:

> - **From SV2's brief (DM-52) and Nathan's answer of 10 November 2026:** completion requires a resolved chart, which P11B's HDE adapter writes as soon as the birth input is given ("the human design chart is calculated immediately when someone signs up, there is no lag"). It also requires identity verification, automated, with no staff step; its provider is wired only after his decision on it and its M07 line (OD-50). The server's `SECRET_KEY` also keys the stored idempotency digests (D17), so rotating it makes a replayed command conflict instead of returning its first result; P11 plans the rotation with the records' expiry.

**K7,** to "Carried to P07":

> - **From Nathan's answer of 10 November 2026** (recorded at DM-52): "there is no manual staff review either. Approval must be automated based on ID verification." P07's console has no profile-approval queue. P07 plans what a member can do when the automated check fails: a retry, and an appeal its one operator answers (OD-23). If he answers that photos are approved automatically too, P07 also plans photo moderation without a staff queue, with staff acting on reports.

## Three questions for Nathan

None of them stops Stage A. Each has a default, and Stage A can be built on it.

- **Q2, photos.** Does "no manual staff review" include photos: each photo approved automatically before it shows, with staff acting only on reports?
  - My reading, and the default: yes.
  - It changes Stage B only (D10, B19).
- **Q3, what ID verification is.** Is it a government photo ID, checked by a verification company with a selfie matched to it, for every member before their profile shows?
  - My reading, and the default: yes.
  - If yes, the manager prepares the full decision after the matrix's recheck: which company, the cost, the consent, what is kept and for how long, what happens when a check fails, and whether the ID's birth date replaces the typed one. Section 10's triggers apply: an age-assurance method chosen, and a detection or moderation vendor proposed.
  - The matrix has one biometric row, Illinois' (UST-51): notice, a public retention policy and a written release before collecting face geometry. Other states' biometric laws are not in it yet.
  - Nothing is bought before he approves its cost line (OD-50).
- **Q4, an unknown birth time.** Can his engine calculate a chart when a member does not know their birth time? If not, is that member:
  - (a) not shown until a chart can be calculated; or
  - (b) shown without compatibility?

  The default is (a), the reviewed rule.

## What the manager does

- Records his words as a new register row. It adds to OD-55's D3 and to OD-60, and supersedes neither.
- Applies DM-52's conditions as this file leaves them: B1 to B22, less B8c, B9d and B12a; R1; and K1 to K4, K6 and K7.
- Carries Q2 to Q4 to Nathan, unless he answers them here.
- Routes the age part of identity verification to G-01's Work Register row, which holds "any method stronger than a self-entered birth date".

Status: complete
