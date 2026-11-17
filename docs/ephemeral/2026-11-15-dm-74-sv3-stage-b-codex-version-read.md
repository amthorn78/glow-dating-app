# DM-74 consultation — SV3 Stage B: Codex's finding on PR47 (no read gives a client the directional version), before the exact-head review

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 11 receives the answer.
- **Revision 1, 15 November 2026.**
- **Why:** Codex's code review of PR47's head `622a4f4` raised one P2 finding, which the manager confirmed in the code. Its fix, if there is one, is a design change (a read the brief's D13 does not provide), and it would change the code the exact-head review reads. In Stage A, Codex's design-changing findings went to the Dev Manager before the review (DM-61, DM-62), and the review then read the corrected code once. The review prompt is drafted and held until this answer.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-74"; the brief's revision 16 if you give words; then either a correction prompt or the exact-head review prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** the review stays held; App Manager 11 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-74's disposition and Stage B's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-74 — SV3 Stage B: Codex's finding on PR47 (no read gives a client the directional version), before the exact-head review.** From App Manager 11, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **Stage B is built, verified and integrated** (code head `5d58993`; the evidence record, "Stage B (interactions)" and "Manager verification of Stage B"). Its run of record, 43686623299, passed all eight jobs: discovery 59/59 in 185 s, and each suite's D14 record `PASS`, every account-table writer lock `FOR NO KEY UPDATE`, none refused. Item 5's lines match `main`'s run 43673382167 but for process IDs. Nothing met the stop rule.
- **PR47** is open from the manager branch at `622a4f4` (code identical to `5d58993`). Its push run 43718074254 and pull-request run [43718124052](https://github.com/amthorn78/glow-dating-app/actions/runs/43718124052) on `622a4f4` each passed all eight jobs; the pull-request run's gate printed `Application checks passed`, with ordering 56/56, 115/115 and 62/62, identity 49/49, profile 69/69 and discovery 59/59 (its phase 181 s), each suite's D14 record `PASS`.
- **The CI policy's Database proof checks paragraph** gains Stage B's sentence (governing; you read it at the pre-merge read, not now).

**Codex's finding** (P2, `services/api/glow_discovery/interactions.py` lines 307 to 308, [thread](https://github.com/amthorn78/glow-dating-app/pull/47#discussion_r4578551630)), in its words: *"When resurfacing is enabled and a member returns on another device or after losing local state, a previously passed candidate appears in a fresh page, but acting on that candidate requires the existing directional row's version rather than zero. `contract.card()` exposes no interaction version, and a repository-wide search found no interaction-read route that lets the actor recover it; the stale response supplies no replacement version either. Consequently, the client cannot recover from this rejection without guessing versions. The discovery proof masks this gap because `interaction_cases._version()` reads the ORM directly when constructing requests. Expose the actor-owned directional version through a projection or read endpoint while retaining this concurrency check."*

**The manager's check** (at `5d58993`):
- **Confirmed.**
  - The like and pass compare `CommandMeta.expected_version` with the actor's row: `0` if there is none, else its version (line 307). This follows the contract's rule: zero requires absence, and a positive value requires the current revision. That rule is in `production-contracts.md` ("`CommandMeta.expected_version` addresses the directional interaction …") and P05's `interactions-fixtures.md` ("Version, digest and replay boundary").
  - `contract.card()` returns the profile ID, the profile and the details, and no version.
  - The only read route Stage B serves is `GET api/v1/matches/<uuid:match_id>`; the other four are commands.
  - Every stale cause answers one 409 `stale_version` body with no version (D8).
  - The proof's `interaction_cases._version()` reads the row through the ORM.
- **Where a client has the version:** the actor's own pass, like or undo answers `InteractionOutcome` or the undo outcome, each with the row's version. So a client that keeps its own state can act; one that has lost it, or a second device, cannot.
- **When it can happen:** only once resurfacing is on (D12; off at launch), for a passed candidate who resurfaces, and after an undo (the row is `withdrawn`, version above zero). No route publishes a setting before P07's console.
- **The same pattern, not raised by Codex:** block and unblock compare `expected_version` with the actor's directional block, `0` if there is none (line 518). After an unblock, the row is `removed` with a version, and no read returns it. So a second device cannot block that member again without the version. Unmatch is not affected: the match read returns `MatchProjection` with its version.
- **What constrains a fix:**
  - D13: additions only, each as a new DTO or registry entry, with no existing DTO changing. `CandidateCard` is Stage A's, merged in PR45.
  - D8: no reason, count or other member's value. A read keyed on a profile ID must not tell an existing profile from a missing one, or an eligible one from an excluded one.
  - The version check itself stays (Codex: "while retaining this concurrency check").
- **The brief's part:** the brief's D13 (the manager's, approved in DM-60) adds no read of the actor's own directional row or block. The design omitted it, and Codex found it.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. Codex's finding** (recommended, (a)):
- **(a) Fixed in Stage B before the exact-head review,** as correction **B-C1**, with the read you word. Two shapes, for your choice:
  - **(a1)** a new owner-only read: the actor's own directional state and version, and their own block's state and version, for a target profile ID. It answers alike, with no row (version `0`), for a profile with none, a profile that does not exist, and one the actor cannot see. It is a new route and a new DTO in F08 and F13's registry entries, with its projection to the owner only.
  - **(a2)** a new card DTO, beside `CandidateCard`, that also carries the viewer's own directional version for that candidate. It covers resurfacing and undo only; the block's version would need its own field or read.

  The review then reads `5d58993` with B-C1 together, as Stage A's review read C1.
- **(b) Carried,** with a stated limit in the contract document and the proof README: no read gives a client its directional or block version, and a client recovers only from its own command's answer. The fix is carried to the item before resurfacing can be switched on (P07's console), and the block case to P10's client wiring. The proof's `_version()` is named as reading the ORM.
- **(c) Declined** as designed: a client keeps its own command answers. This would need a sentence in the contract document saying so.
- **Asked:** which; under (a), the shape and your words for the brief's revision 16 (D13, the owned paths, a section "Stage B, correction B-C1" with its stop rule); under (b), the words for the limit and the carry.

**2. The F2 named cases' wording** (a record):
- EE1 and EE6 say "on both subjects" for `f2_session_account_changed_under_wait` and `f2_match_pair_changed_under_wait`. These cases are P06.2 B1's, which run on the adapter subject only (`cases.all_cases`). My DM-73 consultation called them "the adapter subject's named cases". Stage B compared them where they run, and the control on both subjects.
- **Asked:** the words to narrow EE1 and EE6 in the brief's revision 16, or whether the record's note is enough.

**3. The sequence** (recommended):
- **Under (a):** your answer; the brief's revision 16; correction B-C1's prompt with its TypeSafe reading; B-C1; the manager's verification; PR47's run and Codex on its head; the exact-head review of `5d58993` with B-C1; your pre-merge read; the merge.
- **Under (b) or (c):** your answer; the records; the exact-head review prompt (drafted, with Codex's finding and your disposition as known items); your pre-merge read; the merge.
- **Asked:** agree.

**4. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**
