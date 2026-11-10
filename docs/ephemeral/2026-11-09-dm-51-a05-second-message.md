# DM-51 consultation — the second A05 message, before it goes to Nathan, and DM-50's conditions as applied

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 9 November 2026.**
- **Why:**
  - **The second A05 message** puts owner decisions to Nathan. The matrix says the manager writes the A05 questions to him "through the Dev Manager first" (section 9; OD-32, OD-50). DM-37 set the first message's terms; this message has new options and recommendations, and two of its items touch data ownership and a security boundary (the charter, "When the primary manager consults the Dev Manager").
  - **DM-50's open row** asks the next consultation to confirm its conditions as applied.
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 10's disposition in the review log, "DM-51";
  - the second A05 message, which goes to Nathan with your conditions applied;
  - the review log's Deferred row for DM-50.
- **Stream variables:** none are needed.
- **If no report arrives:** the message does not go to Nathan; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-51's disposition and Nathan's answer to the message is in the owner-direction register.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-51 — the second A05 message, before it goes to Nathan, and DM-50's conditions as applied.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE or Railway;
- check environment variable names only.

**Where it stands.**
- **SV1 is merged:** PR42 at `c864edd` on `main` (9 November 2026, 23:13 UTC). PR run 42717102638 on the final head `df8a04c` and `main`'s push run 42718647067 on `c864edd` each passed all eight jobs (identity 49 of 49), and Codex read `df8a04c` with no findings (the SV1 record, "The merge receipt").
- **Pruned at the merge:** SV1's eleven prompts and consultations, DM-45's to DM-50's among them, with their links pinned at `c864edd`.
- **Next in the order:** this message, then SV2's brief (DM-37 4.5).

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The second A05 message, revision 1** (`docs/ephemeral/2026-11-09-a05-second-decision-message.md`).

- **1.1 Its scope.** DM-37 4.5's three questions (P1, the preference taxonomy; R, resurfacing and rematch; H, the history policy) and DM-38 section 8's language line (L). The manager added **P2, age range and location**:
  - A05 owns both ("A05 owns … age ranges, distance": the discovery fixtures, "Later integration"; the reciprocal-eligibility fixtures), and no message or brief has scheduled them.
  - SV2's brief needs to know whether a profile stores a home area, and SV3's whether discovery filters by age or place.

  **Asked:** keep P2 in this message, or move it (to SV3's brief, or the third message)?
- **1.2 Its form** (OD-32, with DM-37 4.3's terms carried over): each item says what it is, what breaks without it, the options with what each gains, and the recommendation with its basis. Facts cite the matrix's rows (US only, OD-55). The message says that it is not legal advice, that it does not show compliance, and what the recommendations do not weigh. The legal-advice paragraph names two readings and takes no side.
- **1.3 The recommendations, where a challenge matters most:**
  - **P1: (a) woman, man or non-binary; (x) no separate orientation field; (m) the member chooses whether their gender shows.** It also recommends consent at the step where these are entered, no sale (UST-45), and both stores' declarations (AP-23, GP-25). The basis is minimization (the original research), and consent before any threshold applies.
  - **P2: age (a), a range applied both ways; location (a), a typed home area (a city or ZIP code) with a distance limit measured between area centres, and no distance shown.** The basis is the original research's location advice: no exact coordinates, and no exact distances, which repeated queries can narrow to a place.
  - **R: (a) for both, at launch.** The message claims that pass records are kept either way, so resurfacing can be added later as a policy change, while rematch added later changes the data model's one-pair rule (the interactions fixtures).
  - **H: (b) read-only for both members, with one neutral line for every cause** (a pause, a restriction, a suspension or a withdrawn consent). It also states that a deletion works as an unmatch does under OD-12, because AP-33 leaves no option of a readable copy. Points for your read:
    - (b) changes the recorded interim default (reads refuse whatever refuses a send; the P06.2 brief, D5; the P11 plan). SV4's brief would then give reads their own rule.
    - Under (b), the other member keeps reading a restricted or suspended member's past messages. The message leaves case-specific hiding to P07. Is that acceptable as the default on the security boundary?
    - P06.2's D6 deactivates the Stream user on suspension and deletion. Stage C's reads are server-side, by Glow's committed message IDs. Does (b) conflict with D6, or with the Standing guard (DM-30 1.1; the P11 plan)? The manager reads it as no: no message leaves a readable conversation under (b), and a deleted member's conversation leaves the view whole.

**Asked:** your verdict on the message. With your conditions applied as written, may it go to Nathan without another read?

**2. DM-50's conditions as applied** (the review log's open row, "The Dev Manager's next consultation"). They were applied at `df8a04c`, now on `main` through `c864edd`:
- **1.1:** C2.5's reading, in the SV1 record's N-1 row ("Delta review of correction C2");
- **2.1:** the P11 plan's failed-sign-in line replaced by your two lines, and its "No reauthentication" line deleted (`docs/testing/p11-deferred-acceptance.md`, "From SV1");
- **2.2:** three citations at revision 5 (the data model, the contract, the P11 plan);
- **2.3:** the CI policy's counts-only sentence (`docs/operations/ci-and-branch-policy.md`, Database proof checks).

1.2's carry is in the carried-items file, "Carried to SV2".

**Asked:** are they confirmed as applied?

**What happens next:** App Manager 10 applies your verdicts and gives Nathan the message. It records his answer as an owner direction, then writes SV2's brief. No GitHub operation is asked of Nathan.
