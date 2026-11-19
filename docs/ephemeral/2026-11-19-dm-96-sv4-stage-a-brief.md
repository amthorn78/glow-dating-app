# DM-96 consultation — SV4's brief, revision 1: Stage A (chat's routes)

- **Owner:** App Manager 12. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 12 receives the answer.
- **Revision 1, 19 November 2026.**
- **Why:** D-07's first read of a code item, before any prompt. SV4 is the first item of PF01 1.20's stage 1. Its brief decides three security-boundary rules (who may read a conversation, what a member learns of a block, the token surface) and answers the epoch-bump question open since DM-31 item 4.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 12's disposition in the review log, "DM-96"; the brief's revision 2, if you give words.
- **Stream variables:** none are needed.
- **If no report arrives:** no SV4 prompt is written; App Manager 12 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-96's disposition and the pull request carrying it has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-96 — SV4's brief, revision 1: Stage A (chat's routes).** From App Manager 12, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **PR56 merged** at `c2cffbe`: PF01 1.20 with your AE1 to AE5, OD-77 to OD-81, DM-95's disposition. Your DM-95 conditions are applied (the review log, "DM-95").
- **This is D-07's first read** of SV4, the first item of stage 1. The brief is `docs/planning/sv4-chat-notifications.md`, revision 1. It designs Stage A (M09's item 1); Stage B (notifications) comes in a later revision.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The staging (D1, D2).** Recommended: three sessions, each reviewed and merged on its own:
- **A0**, the CI tooling, no app code: the database job split into one job per suite (M09's C-17), DM-59 item 7's Chromium retry, and the pin test's two fixes;
- **A1**, the rules, no new route: D3 to D7 on the existing suites;
- **A2**, the routes and a fifth suite (D8 to D10).
The alternative is A1 and A2 as one session. **Asked:** agree, and is D2's job split (one job per suite, each with its own PostgreSQL and every check it ran before) the right shape, against a matrix?

**2. C-01, a block retires the pair's old likes (D3).** Recommended: the sample rules' rule (a like made before a block between the pair never counts toward a match), by a nullable `retired_at` on `DirectionalInteraction` (migration `0013`) that `glow_chat`'s `block` sets on both directions' `liked` rows, which `activate_reciprocal` requires null, and which no read of the actor's own row returns. Alternatives: a time comparison (unsound: `Block.updated_at` is the server's clock, `decided_at` the database's), or any block ever refusing a match. **Asked:**
- the rule and the mechanism;
- whether the write in `block` may touch what the ordering suite compares between the reference design and the adapter (the brief stops if it does);
- my reading that this restores a reviewed rule dropped by omission, so Nathan need not decide it.

**3. C-02, a block's direction (D4; your DM-75 requirement).** Recommended: (i) a member is never served `restricted`, which `_match_projection` maps to `unmatched` at the stored version; (ii) `glow_chat`'s `unmatch` answers `no_change` for a `restricted` match, as for an `unmatched` one, writing nothing. So the version a member sees stops at the first end of contact, whoever ended it. F10's transition from `restricted` changes accordingly. Alternatives: a block stores `unmatched` (changes P06.DB's reference design and six ordering cases), or the projection alone (the blocker's later unmatch would still move the version). **Asked:**
- does it meet your requirement on every surface D4 lists;
- my reading that it changes neither D8's rule nor what either member can do, so it need not go to Nathan.

**4. C-08, the reads under OD-60 H (D5).** **Asked:** the read rule, and my mapping of the five keys:
- `own_pause` and `other_pause` as the reader's or the other member's profile `paused`;
- `restriction` as either profile `restricted` or `removed`;
- `suspension` as the other account `suspended`;
- `withdrawn_consent` as either member's latest onboarding decision not `accepted`;
- SV2's `incomplete` (DM-52) read as a pause of that member, not a sixth key;
- read-only lets the read cursor move; the send stays refused;
- every hidden cause refuses with one code.

**5. The send's expected version (D6; the P11 plan's C2-X2).** Recommended: `MatchProjection.version`, with a test that it equals `contact_version` for every writer of either, and the contract's sentence that a match's version changes only when contact ends. That also closes the P11 plan's retry case. The alternative is a `contact_version` field on `ConversationSummary`. **Asked:** agree?

**6. P06.2-T and the epoch-bump question (D7; DM-31 item 4).**
- **Recommended: remove** the grant (port and adapter), the grant rule, `token_claims`, `sign_chat_token` and its `import jwt`, keeping `pyjwt` (SV1 needs it) and `_lock_shared` (the reads use it). The Stream proof's token rows become history; A1 stops if its offline tests or `run_plan.py` need the signer. The alternative is to seal.
- **The epoch question. Recommended:** keep the provider revocation on each bump unchanged in Stage A, as defence in depth: today every bump is a suspension or deletion, which also deactivates the user. Revisit at integration. The alternative is to retire it.
- With it: the refusal lists in both places, the API README's lines, the pin test's gap.
**Asked:** remove or seal, and keep or retire the revocation?

**7. Chat's routes and the contract (D8, D9).** Recommended:
- five sealed routes on SV3's patterns, served `non_atomic_requests` and tested with `TransactionTestCase` (the P11 plan's R4);
- the text reader from a factory only the proof's settings name;
- the list's candidates bounded before locking (the P11 plan's finding 4);
- no `ChannelIntent` route;
- `ConversationSummary.state` gains `read_only`, keeping its count and marker;
- a new `MatchList` of at most 200 `MatchProjection`s, since `ConversationSummary` carries no other profile.
**Asked:** agree, or give the words?

**8. M02's hardening (H-01; D7).** Recommended: the pin test's N2 in A0; the Setup script's items (N1, N4, N6, the Codex P2) closed as declined, since each needs a manual paste into both environments and none is a security defect. **Asked:** agree?

**9. The carried entries (D12).** Recommended:
- Stage B takes F12, the sweep, the ledger and G-04's records;
- rematch moves to a later item, unbuilt until Nathan wants it (M09's P-07);
- G-05 goes to P08.1 and G-12 to an EU launch;
- DM-54's consent version follows P08;
- the P11 plan's live rows and mobile items stay with integration.
**Asked:** anything misplaced, or anything Stage A should take?

**10. The review plan.** Recommended:
- for A1 and A2: an exact-head code and security review with a threat model, then Codex, then your pre-merge read;
- for A0: a bounded review of the workflow diff, with your read of the CI policy's change before it merges.
**Asked:** agree?

**11. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**
