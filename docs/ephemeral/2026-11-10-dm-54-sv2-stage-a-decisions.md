# DM-54 consultation — SV2 Stage A as built: the session's decisions, what moves a profile to visible, and a correction's scope

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 10 November 2026.**
- **Why:** Stage A's implementation session reported 13 decisions and deviations (the evidence record, "Decisions and deviations for the manager"). Design decisions that arise during verification go to the Dev Manager before they are treated as settled (the manager workflow, step 6). Two of them are launch values Nathan has not given (OD-32).
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 10's disposition in the review log, "DM-54";
  - the brief (revision 4) where a design changes;
  - Stage A's correction prompt, if one is needed;
  - the carried-items file.
- **Stream variables:** none are needed.
- **If no report arrives:** no Stage A prompt goes to Nathan; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-54's disposition and SV2's Stage A PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-54 — SV2 Stage A as built: the session's decisions, what moves a profile to visible, and a correction's scope.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE or Railway;
- check environment variable names only.

**Where it stands.**
- **Stage A is built.** The session branch `claude/sv2-stage-a-impl-0qqzvj` has code head `b97bc15` and records `f2635fa`. Its run of record, push run 42759801460 on `b97bc15`, passed every job, and the gate printed `Application checks passed`. The profile suite ran 44 of 44, with both scans clean.
- **The manager integrated it** at the merge `e0c0ffe`, and recorded its verification in the evidence record (`docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, "Manager verification"):
  - the scope;
  - the contract outputs, checked by regenerating them;
  - the area table's hash;
  - the API, mypy and proof re-runs;
  - four reversals re-run offline.
- **The CI policy's Database proof checks paragraph** now describes SV2's steps (`docs/operations/ci-and-branch-policy.md`). It is governing text, so you read it before Stage A merges. That read can be part of this one if you wish, or the pre-merge read.
- **Next after your answer:** a correction, if one is needed; then the PR's Codex review and the exact-head review with its threat model.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. Two launch values OD-60 does not give** (the session's items 1 and 2).
- **Orientation:**
  - **What OD-60 gives:** starting lists for gender, "looking for" and relationship status, but none for orientation ("optional to state and matched both ways").
  - **What the session seeded:** version 1 of orientation's list with no values. Until staff publish values, a member can only leave orientation "not stated", and the suite publishes its own test values.
- **Distance:**
  - **What OD-60 gives:** "console-set distance choices", with no values.
  - **What the session seeded:** one choice, `anywhere`. A radius needs a publication, within the 5,000-mile limit.
- **The manager's reading:**
  - Both seeds are safe. An empty orientation list collects no orientation, which fits OD-60's rule that "a setting that collects a new kind of data needs its permission wording and both stores' declarations before it can be switched on".
  - Both values are Nathan's. They can go to him in the third A05 message, beside the media limits and retention, with a recommendation in OD-32's form.
  - Nothing in SV2's code waits on them: each is one publication.
- **Asked:**
  - Are the seeds right?
  - Do the two values go in the third message, or to Nathan sooner?

**2. Two DTOs beyond D11's list** (item 3): `AdultCheckIntent` and `OwnAgeState`.
- D7's eligibility step takes a date before any birth input exists, and D11's list has no intent or read for it.
- Both are additive and registered in F02 with W5's `adult_check` entries.
- **Asked:** approve as additive?

**3. What moves a profile to `visible`** (item 4). This is the main design question.
- **As built:** completion runs only in the owner's profile edit, the display name and summary (`glow_profiles/operations.py`, the profile edit). This follows P04.2's table: "Remains incomplete unless all current requirements permit completion". No other writer attempts completion.
- **What follows:**
  - **A member edit that meets the last requirement completes nothing.** That covers setting a field, an area or the consent, passing the adult check, and submitting a birth input. The profile stays `incomplete` until the member edits their name or summary again.
  - **A requirement the system meets never completes a profile.** That covers the chart (resolved by P11's engine adapter), identity verification (by the verification company, through D18's port) and, in Stage B, a photo approved by the automated check. OD-61: "the human design chart is calculated immediately when someone signs up, there is no lag"; "Approval must be automated".
- **Options:**
  - **(a) Every writer of a completion requirement attempts completion** in its own transaction, after the account row lock, on rows read after it. That includes the owner's writers, the identity verification port's write, and, in Stage B, the photo approval.
    - A profile becomes `visible` as soon as its last requirement is met.
    - The registry needs F04 entries for the attempts no owner makes: `complete` from `incomplete` to `visible`, as `system`, and possibly as `provider` for the verification company's verdict.
  - **(b) An explicit owner action, "go visible",** which the client sends when the owner's completion read is empty. That needs a new intent, since `VisibilityIntent`'s closed `action` cannot gain a value. A requirement the system meets would still wait for the member to act.
  - **(c) Keep it as built:** the client re-sends the profile edit.
- **The manager recommends (a).** It is the only option under which OD-61's automatic chart and approval show a profile without the member acting again. Stage A's correction would add the attempt to Stage A's writers, and Stage B's brief would add it to the photo approval.
- **Asked:**
  - Which option?
  - If (a): the words for D9, and the registry entries.

**4. The idempotency records' lifetime** (item 5).
- **As built:** 24 hours, provisional. The contract leaves retention to A05, and the model requires a value.
- **The manager's reading:** acceptable as a provisional constant, carried to the third A05 message's retention question and to P11.
- **Asked:** approve?

**5. A new onboarding consent version and a visible member** (item 6).
- **As built:**
  - Completion requires the onboarding consent accepted at its current version.
  - Publishing a new version demotes no one by itself. A `visible` member's next profile edit finds consent missing and moves the profile to `incomplete` until they accept the new version.
  - Until that edit, the member stays `visible`. `glow_chat`'s send check reads the latest decision's state, not its version (`contact.py`, `_contact_state_checks`), so they can still send.
- **What applies:**
  - F02: "old consent version rejected".
  - OD-60's rule for H: a change that makes more readable reaches a member only after they accept updated consent wording.
- **The manager's reading:** acceptable for Stage A, since SV2 publishes no new version at runtime. What a new version does to visible members, and whether discovery (SV3) and messaging (SV4) read the version, is carried to SV3 and SV4.
- **Asked:**
  - Is that acceptable?
  - Or should Stage A's correction do more? For example, a publication of a new onboarding version could emit an event, or demote at once.

**6. A birth input whose date fails the adult check is saved** (item 7).
- **As built:** the birth input revision is saved. The rerun then sets the age state to `unknown`, clears its date, and demotes a `visible` profile. The session follows P04's `saveBirth` (`apps/mobile/src/onboarding/store.ts`), which saves the input and moves the eligibility date to the input's date.
- **D7's words:**
  - "A birth input saved with another date changes the age state's date in the same transaction."
  - "Every date change reruns the check. A failing rerun sets `unknown`, clears the date, and moves a `visible` profile to `incomplete`."
  - At the eligibility step: "A failing date is refused and not stored."
- **The concern:** this stores the private birth date, time and place of a member who has just declared they are under 18 (G-01).
- **Options:**
  - **(a) Keep it as built.**
  - **(b) Refuse the revision, and store nothing,** in the same transaction that still sets the age state to `unknown` and demotes. The refusal of the adult check then applies on both paths: "a failing date is refused and not stored".
  - **(c) Refuse the revision and change nothing,** leaving G-01 to decide what a suspected minor triggers.
- **The manager recommends (b).** The account stops being an adult's, as D7 intends, and no birth data of a self-declared minor is kept.
- **Asked:**
  - Which option?
  - If (b) or (c): the words for D7 and D8.

**7. CI does not type-check `glow_profiles`** (item 10).
- `services/api/pyproject.toml`'s `[tool.mypy] files` is `["glow_api", "glow_domain", "glow_chat", "glow_identity"]`, and the brief does not own the file.
- The session ran mypy on `glow_profiles` and the new tests by hand, and so did the manager: `no issues found in 24 source files`. CI checks none of it.
- **The manager recommends:** Stage A's correction owns that one line and adds `glow_profiles`. `glow_persistence` is also missing from it, a gap from before SV2; the manager suggests leaving it out of this item.
- **Asked:** approve, with the words for the owned path?

**8. Profile restriction has no registry entry** (item 13).
- SV2's staff operation `restrict_profile` calls `glow_chat`'s writer, which moves `visible` or `paused` to `restricted`. The registry has no entry for that move, before or after SV2.
- W5 says "each transition SV2's writers make that the registry lacks is a new entry".
- **The manager's reading:** under W5, Stage A's correction adds F04 entries, `restrict` from `visible` and from `paused` to `restricted` (`moderator`; `A05`), each with an allowed and a forbidden example.
- **Asked:** right, or carried to P07?

**9. A stale sentence** (item 8).
- `Profile.location_label` is gone (D5). `data-model.md`, "Identity, time and field semantics", still says "Empty profile bio/location labels mean incomplete or withheld text, not eligibility."
- That paragraph is outside the rows the brief lets the session rewrite.
- **Proposed words:** "An empty profile bio means incomplete or withheld text, not eligibility." Folded into Stage A's correction.
- **Asked:** approve?

**10. Settled by the manager, for your confirmation.**
- **Item 9:** the import line of `glow_domain/identity.py` gains `date`, which the age section needs.
- **Item 10 of the record:** an integral JSON number such as `1.0` is accepted as an integer, as the contract's own validators decide. The digest normalizes it.
- **Item 11:** the CI policy's paragraph is the manager's, and is updated in this batch.
- **Item 12:** D16 did not apply, so DM-50 1.2 stays carried.

**The correction, if items 3, 6, 7, 8 and 9 go as recommended:** Stage A's correction C1 carries them, with Codex's findings on the PR head if any arrive first. Its size decides whether a delta review or a full exact-head review follows (M05 S2). Either way, the exact-head review with its written threat model reads the corrected head.

**What happens next:** App Manager 10 applies your words in the brief's revision 4 and writes the correction's prompt, or the exact-head review prompt if no correction is needed. A design that needs another read comes back first. No GitHub operation is asked of Nathan.
