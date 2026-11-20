# DM-96 — SV4's brief, revision 1: Stage A (chat's routes)

- **Consultation:** DM-96, from App Manager 12, relayed by Nathan to Dev Manager 5 on 19 November 2026.
- **Read at:** `ccc05eca4592a36c9df59459ed4eb2c8f1e0a1a5` of `claude/magical-wozniak-yfmmx2`; `main` at `c2cffbe` (PR56).
- **Kind of read:** D-07's first read of SV4, a code item, before any prompt.
- **Answered by:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), on `claude/dev-manager`.

## 1. The answers

| Item | Verdict | In short |
|---|---|---|
| 1. The staging (D1, D2) | **Approved with conditions** (AG1) | Three sessions, each merged on its own. One job per suite, not a matrix. Each job keeps the cross-suite marker refusal, with a decoy database. |
| 2. C-01, old likes (D3) | **Approved with conditions** (AG2, AG3, AG18) | The rule is right. The mechanism misses SV3's like's own reciprocity check: as written, the other member's later like would be refused, and the refusal would reveal the old like. The write may go into `block`: it touches nothing the ordering suite judges. Nathan need not decide. |
| 3. C-02, a block's direction (D4) | **Changes requested, with the words** (AG4 to AG6, AG14, AG15, AG19) | (i) and (ii) meet DM-75's requirement on every surface D4 lists. But F10's change breaks the mobile fixture's cleanup of a restricted match, and Stage A changes no mobile file. Take revision 1's alternative (b): a block stores `unmatched`. Nathan need not decide. |
| 4. C-08, the reads (D5) | **Approved with conditions** (AG7 to AG9, AG13) | The rule and four of the five mappings are right. A `removed` profile is a deletion, so it is hidden, not a restriction. The read must apply `chat.history`'s consent version. |
| 5. The send's version (D6) | **Approved with conditions** (AG10) | Agreed. Two sentences made exact. |
| 6. P06.2-T and the epoch bump (D7) | **Approved with conditions** (AG11, AG17) | Remove. Keep the revocation; its premise holds. The list of tests that use the token code is incomplete; one class pins all of `contact.py`. |
| 7. Routes and contract (D8, D9) | **Approved with conditions** (AG13, AG17, AG20) | Agreed, plus: the send route answers one code for every cause; the generated files in the app are named as the exception; AC3 shows `read_only`. |
| 8. M02's hardening (H-01) | **Approved with conditions** (AG12) | N2 in A0; the rest declined. N6 needs no paste, so its reason is corrected. |
| 9. The carried entries (D12) | **Approved with conditions** (AG16, AG17) | Nothing is misplaced. Five new entries. |
| 10. The review plan | **Approved with conditions** (AG21) | A0 gets an exact-head review of the complete workflow diff, and Codex. |
| 11. Notion | Two mismatches, both on SV4's Work Register row (section 13) | |

The exact words are in section 14: AG1 to AG21. Applied as given, they need no further read. Under the charter, my next reads of SV4 are A0's CI policy change before A0 merges, and each stage's pre-merge read.

## 2. What I read and checked

- **The classification.** The trusted classifier is `main`'s `scripts/change_scope.py`, sha256 prefix `b564c62f4a076f51`. I ran it with `python3 -I --base c2cffbe --head ccc05ec --merge-base`; there is one merge base. Result: `ordinary-docs-only`, ten Markdown paths, the brief among them.
- **My earlier words.** DM-95's AE1 to AE9 are applied exactly at `c2cffbe` (by script). My note's AF1 to AF4 are applied, OD-81's row naming `6a3811b`.
- **The brief, whole:** each D-number against the code it cites, at `ccc05ec`, exported outside the repository. I read the code; I ran none of it.
- **Every citation checked:**
  - `contact.py`, `interactions.py`, `predicates.py`, `reads.py`, `profile_settings.py`;
  - the models and migrations (`0012` is the latest);
  - the ordering, discovery and read-phase cases;
  - the contract's schema and flow registry, the generator, the mobile fixture adapter and its tests;
  - the Foundation workflow, the CI policy, the P11 plan, the carried-items file;
  - SV2's brief, DM-51, DM-55 and M02's record.
- **Repository-wide searches:** for each name D7 removes; for every source pin of `contact.py`; for every reader of the flow registry; for `restricted` in the suites; and for every writer of a match's version and of the session epoch.
- **Remote branches** (`git ls-remote`): three, as the handoff lists: `main` `c2cffbe`, the manager branch `ccc05ec`, `claude/dev-manager` `6a3811b`.

## 3. Item 1 — the staging (D1, D2)

- **Three sessions: agreed.**
  - A1 and A2 cross different security boundaries: what a member learns of a block and who may read a conversation (A1), and the served surface (A2).
  - Separate diffs keep each exact-head review bounded.
  - A0 must come first, since A2 adds its suite's job "the same way".
- **One job per suite, rather than a matrix: agreed.**
  - Each job's steps stay explicit, and the gate names each job.
  - A matrix puts the per-suite steps behind conditions, and its single result hides which suite failed.
- **One check would be lost.** Today the database job holds four databases in one PostgreSQL. SV1's to SV3's suites each show that their database refuses the other suites' markers (`foundation.yml`, the steps at lines 541, 654 and 768). In a job with one database, there is no other marker to refuse. AG1 keeps the check: each job creates one more database, carrying another suite's marker, and shows its suite refuses it.
- **Cost:** none now, since the repository is public (OD-51). Once it goes private, each job's own setup adds to the minutes that M07's line 42 prices.

## 4. Item 2 — C-01, a block retires the pair's old likes (D3)

- **The rule: agreed.** It is the sample rules': a block marks both directions unmatchable (`glow_domain/interactions.py`, lines 694 to 698). In their test, the later like is committed and no match is made (`tests/test_interactions.py`, lines 480 to 487).
- **The gap in the mechanism.** SV3's like does not call `activate_reciprocal` blindly. It first checks for the target's `liked` row (`glow_discovery/interactions.py`, `interact`, lines 355 to 365). It then refuses the like with `state_conflict` whenever activation answers anything but `applied`. Here is the failure if only `activate_reciprocal` requires `retired_at` null:
  1. A likes B.
  2. Either member blocks the other, then unblocks.
  3. B's like then finds A's retired row and calls `activate_reciprocal`, which answers `not_reciprocal`.
  4. B's like is refused and rolled back, every time B tries.
  5. B learns that A had liked them before a block.

  The brief's own sentence "a like that replaces a pass writes it null" also needs a write in `interact`, but the owned paths allow only `_match_projection` there. AG2 puts the check in both places. AG18 widens the owned path.
- **The proof as written would pass for the wrong reason.** "No match" also holds when the like is refused. AG3 asks for the later like to be recorded and answered as any like is that finds no like in return. It also asks for the first like to read the same state and version, in its own-versions read, before and after the block. That second check is the privacy property; the brief states it (D3, "What the member sees") but tests nothing for it.
- **The write leaves the rest of the row alone** (AG2): not its state, version, `decided_at` or policy version. A version bump would show in the actor's own-versions read.
- **Whether the write in `block` touches what the ordering suite compares: it does not.**
  - The suite does not compare the two subjects with each other. It judges each against the same case expectations: rows, commit times and lock waits (`cases.py`, module docstring).
  - Its matches come from `activate_match`, which writes no directional row, so the update touches no row in those cases.
  - The reference design (`reference.py`) has no directional table.
  - The account lock scan checks explicit locks of account rows. A plain update adds none, and the block's lock order is unchanged.

  The reference design does change under item 3's resolution, but that is D4's change, not this write.
- **Whether Nathan decides it: agreed, he need not.** It is a reviewed sample rule the server dropped by omission. It keeps D8's rule and F13's projection. It takes no action away that the sample rules allow: there, as here, a retired like cannot be renewed.

## 5. Item 3 — C-02, a block's direction (D4)

- **Does (i) with (ii) meet DM-75's requirement on every surface D4 lists? Yes.** I checked each surface:
  - the send's and the reads' state check comes first (`contact.py`, lines 564 to 565; `reads.py`, lines 276 to 277);
  - discovery's consumption excludes a match row in any state (`predicates.py`, lines 179 to 187);
  - the own-versions read returns the actor's rows only;
  - a block by the blocked member answers as any first block does;
  - SV3's unmatch route compares the expected version with `match.version` and stores the same receipt either way.

  The only writers of a match's version and contact version are `block` and `unmatch` (`contact.py`, lines 693 to 694 and 779 to 780).
- **But it cannot be built inside Stage A.** D4 changes F10's row `unmatch` from `restricted` to `unmatched`.
  - The mobile fixture adapter reads that row while it runs. `transition('F10', 'unmatch', prior.state, 'unmatched')` (`apps/mobile/src/interactions/fixture-adapter.ts`, line 204) throws `conflict` when the rule is missing (lines 39 to 42).
  - The adapter's cleanup of a restricted match is built on that row: `cleanupMatches` and `unmatchIntent`, which the interactions screen and store use, and the cleanup cases in `fixture-adapter.test.ts` from line 414.
  - So A1's change to F10 would fail the mobile checks, and Stage A changes no mobile file.
  - Making the fixture follow is not a one-line change: its whole restricted-cleanup flow would stop working. That is AC3's work.
- **Resolution: alternative (b)** (AG4 to AG6). A block stores `unmatched`, with the same version advance and event as today.
  - The sameness then holds by construction: no projection maps a state, and no command treats `restricted` specially.
  - F10 only gains a row (the block's effect on an active match), so the fixture finds every rule it uses.
  - D6's invariant is untouched.
  - **The cost the brief named is real:**
    - P06.DB's reference design changes (`reference.py`, line 366);
    - six ordering cases and one SV3 case change their expectations (listed in AG14);
    - the match row no longer records the cause.
  - **That cost is acceptable.** The `Block` rows (never deleted, versioned) and the `block_changed` events keep the cause for staff and for the rematch rule.
- **Whether Nathan decides it: agreed, he need not, for either design.** Under (b), D8's rule holds, F13's projection holds, and neither member gains or loses an action. A block still ends contact, and an unblock still restores nothing.
- **What stays unchanged:** P05.3's Python fixture commands (`glow_domain.interactions`) still restrict on a block, and their tests still assert it (`tests/test_interactions.py`, lines 911 and 919). They read no flow registry, so they stay as they are (AG15).

## 6. Item 4 — C-08, the reads under OD-60 H (D5)

- **The read rule's structure: agreed.** That covers the session and account checks, the match and block checks, deletion as an unmatch, the settings pointer under SV2's D19 order, and one refusal for every hidden cause.
- **The mapping:**
  - `own_pause` and `other_pause`: agreed.
  - **`restriction`: `restricted` only** (AG7). F04 moves a profile to `removed` on one event only, `deletion_requested` (role `system`). A `removed` profile is a deletion. OD-60 H makes a deletion work as an unmatch, and AP-33 leaves the other member no readable copy (DM-51, M14). So it is hidden, never read-only. Today no server code writes `removed`, and the account checks come first. But the mapping must be right before a deletion flow writes it.
  - `suspension`: agreed. A suspended reader has no valid session: the only writer of the epoch is `_revoke_account` (`contact.py`, line 817).
  - `withdrawn_consent`: agreed.
  - **SV2's `incomplete` as a pause of that member: agreed, with truer words** (AG8). A profile can become `incomplete` through moderation or a new requirement, not only for "a reason of the member's own". What it shares with a pause is that its member can make it visible again, and that it is no safety restriction.
  - **Read-only lets the cursor move and the send stays refused: agreed.**
  - **Every hidden cause refuses with one code: agreed.** The send needs the same, and D8 does not say so (item 7).
- **A missing rule: the consent limit** (AG9).
  - `chat.history` carries `consent_policy_version` (launch: `consent.onboarding.v1`).
  - SV2's brief (line 77; DM-55) records OD-60 H's limit: "a change to H that makes more readable reaches a member only after they accept the consent wording that describes it".
  - SV2 enforces the publication side only: a more readable publication must name a new onboarding version. The read side is SV4's, and D5 is silent on it.
  - **AG9's interim rule:** while the setting names the launch version, each cause reads its value. Once it names any other, every cause reads `hidden`, which fails closed.
  - At launch every cause is already `read_only` under the launch version, so no read changes now. D10's cases (a cause set to `hidden`) keep the launch version, so they are unaffected.
  - The per-member rule (each member's accepted version against the setting's) goes to P08, with DM-54's consent version (AG17).

## 7. Item 5 — the send's expected version (D6)

- **Agreed.**
  - `MessageIntent.meta` is `CommandMeta` (`idempotency_key`, `expected_version`).
  - Both fields start at 1. They are advanced together, and only by `block` and `unmatch`.
  - Under item 3's resolution that stays so.
- **The retry case, made exact** (AG10). The send checks the state before the version, and the version before the deduplication. So a retry is never refused as stale. But a retry after contact has ended is refused as `match_not_active`, when no send is possible. "Cannot be refused as stale" is true; AG10 adds the rest, so that the P11 plan's entry closes on an exact sentence.

## 8. Item 6 — P06.2-T and the epoch bump (D7)

- **Remove, rather than seal: agreed.** `import jwt` appears only in `chat_provider_stream.py`, line 84, in the app's code. The `pyjwt` pin stays for SV1's dependency (H-02).
- **Keep the revocation on each bump: agreed.**
  - The premise is true: the only writer of `session_epoch` is `_revoke_account` (suspension and deletion), which also writes `access_revoked`.
  - A password change or reset signs out each session, with no bump (`glow_identity/revocation.py`, `sign_out_account`).
  - The revisit at integration needs a carried entry (AG17).
- **The list of the token code's users is incomplete** (AG11). A1's acceptance says no test changes beyond those D11 names, so each miss would stop the session:
  - **`test_chat_domain.py`:**
    - line 63 lists the port's method names, `grant_token` among them;
    - "lines 232 to 320" puts `TokenRuleTests` (to go) together with `RevocationCutoffTests` (lines 292 to 320), which must stay, since the revocation stays.
  - **`test_chat_adapter_offline.py`:** the grant is tested by `test_r2_the_grant_signals_before_commit_once` (from line 148) and `test_the_adapter_has_no_switch_and_the_grant_is_on_the_port` (from line 294), not just lines 192 and 304 to 305.
  - **`test_chat_provider_stream.py`:** the imports (lines 56, 57 and 59) and `SignerTests` (lines 1284 to 1348).
  - **`test_interactions_offline.py`:** `ReciprocalWriterTests` (from line 1343), with `MAIN_DEFINITION_DIGESTS` and `MAIN_MODULE_DIGEST` (lines 1200 to 1295).
    - It pins every function and method in `glow_chat/contact.py` as SV3 left it, by AST and by digest. The brief names only `grant_token`'s digest (line 1258).
    - D3, D4 and D7 each change `contact.py`, so all of that class's tests fail.
  - **The Stream proof:** its own `token_claims` fields (`proof_run.py`, `mechanisms.py`) describe the SDK's tokens. They are not the signer and stay.

  AG11 lists these and asks each prompt to repeat the search at its own commit.

## 9. Item 7 — chat's routes and the contract (D8, D9)

- **Agreed:**
  - the five sealed routes on SV3's patterns;
  - `non_atomic_requests` with `TransactionTestCase` (the P11 plan's R4: a Django test case's atomic block is refused);
  - the text reader from a factory only the proof's settings name, refusing to run without one;
  - the list bounded before it locks (the P11 plan's C1 finding 4);
  - no `ChannelIntent` route;
  - `read_only` added to `ConversationSummary.state`, rather than reusing `closed`;
  - `MatchList` of at most 200, since `ConversationSummary` carries no other profile.
- **The send route's refusals** (AG13). The contract's `Error` serves a code from a fixed list and no reason. So the risk is different causes mapped to different codes.
  - The send's internal reasons name the cause: `profile_unavailable` (either pause, `incomplete` or a restriction), `consent_not_current`, `account_not_active` (suspension, or deletion), `blocked` and `match_not_active`.
  - OD-60 H's one neutral line, D4's sameness and "a deletion works as an unmatch" all need those to reach the member as one code.
  - D5 says this for the reads; D8 does not say it for the send.
- **The generated files** (AG20). `npm run generate` writes the TypeScript types and validators into `apps/mobile/src/contracts/generated/`, so D9's additions change files under `apps/mobile/`. The exclusions forbid any change to the mobile app; AG20 names the generated files as the one exception.
- **The real client** (AG17). The fixture-era client shows any conversation whose state is not `open` as unavailable (`apps/mobile/src/chat/rows.ts`, line 13). Showing `read_only` as OD-60 H's one neutral line, with the history readable and no send, is AC3's work, so it goes in the carried entries.

## 10. Item 8 — M02's hardening (H-01)

- **N2 in A0: agreed.**
- **Declining the others: agreed.** None is a security defect (M02's record):
  - N1 is a signal race in `setsid`;
  - N4 is an optional completion stamp;
  - the Codex P2 is `ln -sfn` onto a directory.
  - Each changes `scripts/bootstrap-toolchain.sh` and needs a paste into both app environments.
- **N6's reason needs correcting** (AG12). It is not in the Setup script: it is the lint pattern `extend-exclude = ["*.md"]` in `services/api/pyproject.toml` and `proofs/postgres-ordering/pyproject.toml`, and needs no paste. It is declinable on M02's own reason: a Python file under a directory with that name is full scope anyway.

## 11. Item 9 — the carried entries (D12)

- **Placement: agreed.**
  - Stage B takes F12, the sweep, the ledger and G-04's records.
  - Rematch goes to the item that builds it.
  - G-05 goes to P08.1, G-12 to an EU launch, and DM-54's version to P08.
  - The P11 plan's live rows and the mobile items stay with integration.
- **Five additions** (AG16, AG17):
  - **Stage B:** a notification must never tell a block from an unmatch.
  - **P08:** the per-member consent limit for reads.
  - **Integration:** the revisit of the epoch revocation.
  - **AC3:** `read_only` on the real client.
  - **P07:** any staff path that makes a match `restricted` keeps D4's sameness.

## 12. Item 10 — the review plan

- **A1 and A2: agreed.** Each gets an exact-head code and security review with the threat model, then Codex, then my pre-merge read.
- **A0, condition AG21:** "a bounded review" becomes an exact-head review of the complete workflow diff. It checks that each job keeps every step and check it had, that the gate requires each job, and that no step prints a connection value. Codex follows, as the brief's own "Classification expectation" says for every stage. My read of the CI policy's change comes before A0 merges.
  - This also follows root `AGENTS.md` for workflow changes: the manager classifies with the pre-change policy and reads the jobs' actual steps and results.

## 13. Notion (read only, at `ccc05ec`)

- **Matching the repository:**
  - the Dev Manager page has DM-96's row, so AM12-35's check works;
  - the register copy has OD-81;
  - Implementation Control's branch list names three branches, with `main` at `c2cffbe` and the manager branch at `ccc05ec`, as section 2 lists them. The search showed no more of that sentence.
- **Two mismatches, both on SV4's Work Register row:**
  - **Next Action** begins "PF01 revision 1.19, in force since PR55 at d3273f3". PF01 1.20 has been in force since PR56 (`c2cffbe`).
  - **Owner Role** names "App Manager 8 (brief and prompt)". Revision 1 is App Manager 12's.

## 14. The words

Each old passage below occurs exactly once in `docs/planning/sv4-chat-notifications.md` at `ccc05ec`, applying the pairs in order (checked by script). Each new passage then occurs exactly once.

**AG1 — the brief, `docs/planning/sv4-chat-notifications.md`: D2, the cross-suite marker refusal kept in each job.**

> ```
> the secret check before any upload). The Foundation gate requires every suite's job.
> ```

> ```
> the secret check before any upload). Today SV1's to SV3's suites also show that their database refuses the other suites' markers, which only a shared PostgreSQL holds; each job keeps that check by creating, in its own PostgreSQL, one more database carrying another suite's marker and showing its suite refuses it. The Foundation gate requires every suite's job.
> ```

**AG2 — the brief, `docs/planning/sv4-chat-notifications.md`: D3, both reciprocity checks.**

> ```
>   - **The mechanism** (recommended): a nullable `retired_at` on `DirectionalInteraction`, one migration (`0013`). `glow_chat`'s `block` sets it, under its two account locks with the database's clock, on every `liked` row between the pair, in both directions, in the same transaction; `activate_reciprocal` requires it null on both rows. No read of the actor's own row returns it. A pass, or a like that replaces a pass, writes it null.
> ```

> ```
>   - **The mechanism** (recommended): a nullable `retired_at` on `DirectionalInteraction`, one migration (`0013`). `glow_chat`'s `block` sets it, under its two account locks with the database's clock, on every `liked` row between the pair, in both directions, in the same transaction, and changes nothing else of the row (not its state, version, `decided_at` or policy version). Both reciprocity checks require it null on both rows: `activate_reciprocal`'s, and SV3's like's own check before it calls `activate_reciprocal` (`glow_discovery/interactions.py`, `interact`, lines 355 to 365). That check finds any `liked` row of the target's today, and the like is refused `state_conflict` whenever activation does not apply; left as it is, the other member's later like would be refused, and the refusal would tell them that a like toward them was made before a block (DM-96). With both checks, the later like is recorded with no match, as is any like that finds no like in return. No read of the actor's own row returns `retired_at`. A pass, or a like that replaces a pass, writes it null.
> ```

**AG3 — the brief, `docs/planning/sv4-chat-notifications.md`: D3, the proof.**

> ```
>   - **The proof:** a database case that fails without the rule (a block and unblock, then a like from the other member, no match), with its reversal.
> ```

> ```
>   - **The proof:** two database cases that fail without the rule, each with its reversal: a like, then a block and unblock by either member (one case each), then a like from the other member, which is recorded and answered as a like that finds no like in return, with no match made. In each, the first like reads the same state and version in its actor's own-versions read before and after the block.
> ```

**AG4 — the brief, `docs/planning/sv4-chat-notifications.md`: D4, the recommended design.**

> ```
>   - **Recommended:**
>     - **(i) a member is never served `restricted`:** `_match_projection` maps a stored `restricted` to `unmatched`, for both participants, at the stored version;
>     - **(ii) unmatching a `restricted` match changes nothing:** `glow_chat`'s `unmatch` answers `no_change` (`already_unmatched`) for `restricted` as it does for `unmatched`, writing nothing and emitting no event. Contact already ended at the block, which bumped the contact version and emitted `contact_revoked`;
>     - so the version a member sees stops at the first end of contact, whoever ended it and however, and every later command of either member answers as it would after an unmatch. The stored `restricted` and the `Block` rows keep the cause for staff (P07) and for the rematch rule.
> ```

> ```
>   - **Recommended: a block ends an active match as an unmatch does** (revision 1's alternative (b); DM-96): `glow_chat`'s `block` stores `unmatched`, not `restricted`, with the same contact and version advance and the same `contact_revoked` event it writes today.
>     - So what a participant is served (the state, the version, and the answers to their own commands and reads) is the same after a block as after an unmatch, by construction. It stays the same after the blocker's later unblock, which changes no match, and after either member's later unmatch, which answers `no_change` (`already_unmatched`), as for any `unmatched` match.
>     - No projection maps a state, and no command treats one state specially. The version a member sees stops at the first end of contact, whoever ended it.
>     - The cause stays in the `Block` rows, which are never deleted, and in the `block_changed` events, for staff (P07) and for the rematch rule.
>     - The server then writes `restricted` for no command. The enum keeps it for the sample back-ends (P05.3's fixture commands and the mobile fixture adapter, which restrict a match when the pair loses eligibility) and for a later staff path, which keeps this sameness (D12).
> ```

**AG5 — the brief, `docs/planning/sv4-chat-notifications.md`: D4, the contract changes.**

> ```
>   - **The contract changes:** F10's transition `unmatch` from `restricted` to `unmatched` becomes `restricted` to `restricted`, with no change; `MatchProjection`'s description says a member is never served `restricted`; the enum keeps the value for staff projections.
> ```

> ```
>   - **The contract changes:** F10 gains the transition `block` from `active` to `unmatched`, the block's effect on an active match, with the role and flags of F10's `unmatch` rows (`participant`; no eligibility; no policy). No row is removed: the mobile fixture adapter looks up F10's rows while it runs (`apps/mobile/src/interactions/fixture-adapter.ts`, lines 39 to 42 and 204) and finds every rule it uses. `MatchProjection`'s description says that the server serves `restricted` to no member. `production-contracts.md`'s F10 and F13 paragraph and the data model's `Match` row say that a block ends an active match as an unmatch does, its cause kept in the `Block` rows.
> ```

**AG6 — the brief, `docs/planning/sv4-chat-notifications.md`: D4, revision 1's recommendation as the alternative.**

> ```
>     - **(b) a block stores `unmatched`:** the same projection with no mapping, but it changes the block's outcome in P06.DB's reference design and every ordering case that expects `restricted` at version 2 (`cases.py`, lines 360, 758, 847, 861, 878, 910), and loses the cause from the match row;
> ```

> ```
>     - **(a) serve `restricted` as `unmatched`, and make unmatching a `restricted` match change nothing** (revision 1's recommendation): it meets the requirement on every surface below and keeps the cause on the match row. But its F10 change (the transition `unmatch` from `restricted` to `unmatched` becoming `restricted` to `restricted`) removes a row the mobile fixture adapter looks up while it runs, and that adapter's cleanup of a restricted match (`fixture-adapter.ts`, line 204; `cleanupMatches` and `unmatchIntent`, which the interactions screen and store use; the cleanup cases in `fixture-adapter.test.ts` from line 414) would then fail. Stage A changes no mobile file (DM-96);
> ```

**AG7 — the brief, `docs/planning/sv4-chat-notifications.md`: D5, `restriction` and `removed`.**

> ```
>     - `restriction`: either member's profile is `restricted` or `removed`;
> ```

> ```
>     - `restriction`: either member's profile is `restricted`. A `removed` profile is hidden, never read-only: F04 moves a profile to `removed` only on `deletion_requested`, and a deletion works as an unmatch (OD-60, H; AP-33; DM-96);
> ```

**AG8 — the brief, `docs/planning/sv4-chat-notifications.md`: D5, why `incomplete` reads as a pause.**

> ```
> since both are a profile not shown for a reason of the member's own.
> ```

> ```
> since both are a profile that is not shown and that its member can make visible again; neither is a safety restriction.
> ```

**AG9 — the brief, `docs/planning/sv4-chat-notifications.md`: D5, the consent limit.**

> ```
>   - **Read-only means:** the history page and the list serve the conversation, the read cursor moves, and the send is refused as today (its checks do not change). One neutral state, the same for every cause, marks it (D9).
> ```

> ```
>   - **The consent limit** (SV2's D2; OD-60, H; DM-96): a change that makes a cause more readable reaches a member only after they accept the consent wording that describes it, and `chat.history` names that wording's onboarding version (`consent_policy_version`). Stage A reads it fail-closed: while the setting names the launch version (`consent.onboarding.v1`), each cause reads its value; once it names any other, every cause reads `hidden`. At launch every cause is already `read_only` under the launch version, so this changes no read now. The per-member rule (each member's accepted version against the one the setting names) goes to P08 with DM-54's consent version (D12).
>   - **Read-only means:** the history page and the list serve the conversation, the read cursor moves, and the send is refused as today (its checks do not change). One neutral state, the same for every cause, marks it (D9).
> ```

**AG10 — the brief, `docs/planning/sv4-chat-notifications.md`: D6, two sentences made exact.**

> ```
> with D4 (ii) that stays so. A test pins the equality for every writer of either field, and the contract says that a match's version changes only when contact ends. That also settles the P11 plan's retry case: while contact continues the version cannot rise, so a retry of a committed send cannot be refused as stale.
> ```

> ```
> with D4's design that stays so. A test pins the equality for every writer of either field, and the contract says that a match's version changes only when contact ends. That also settles the P11 plan's retry case: while contact continues the version cannot rise, so a retry of a committed send is never refused as stale; it can be refused only after contact has ended, as `match_not_active`, when no send is possible.
> ```

**AG11 — the brief, `docs/planning/sv4-chat-notifications.md`: D7, the token code's users.**

> ```
>   - **Who uses it now:** the offline tests (`test_chat_domain.py`, lines 232 to 320; `test_chat_adapter_offline.py`, lines 192 and 304 to 305; `test_interactions_offline.py`, line 1258; `test_chat_provider_stream.py`, lines 59 and 1362), the ordering suite (`cases.py`, line 1459; `delivery_phase.py`, line 593; `interface.py`, line 166; `adapter.py`, lines 181 to 182), and the Stream proof's live conformance (`proofs/stream-chat/glow_stream_proof/conformance.py`, lines 429 to 448).
> ```

> ```
>   - **Who uses it now** (read at `ccc05ec`; DM-96). Each stage's prompt repeats the search at its own commit, for every name D7 removes and for every source pin of a module the stage changes, and lists each hit by file and line:
>     - `test_chat_domain.py`: line 63 (the port's method names, `grant_token` among them) and `TokenRuleTests` (lines 228 to 290); `RevocationCutoffTests` (lines 292 to 320) stay, with the revocation;
>     - `test_chat_adapter_offline.py`: `test_r2_the_grant_signals_before_commit_once` (from line 148) and `test_the_adapter_has_no_switch_and_the_grant_is_on_the_port` (from line 294);
>     - `test_chat_provider_stream.py`: the imports (lines 56, 57 and 59), `SignerTests` (lines 1284 to 1348) and the seal test's import list (line 1362);
>     - `test_interactions_offline.py`: `ReciprocalWriterTests` (from line 1343) and its digests (`MAIN_DEFINITION_DIGESTS` and `MAIN_MODULE_DIGEST`, lines 1200 to 1295), which pin every definition in `glow_chat/contact.py` as SV3 left it, `grant_token`'s at line 1258. D3, D4 and D7 each change `contact.py`, so A1 rewrites the class against its own head and records the reason;
>     - the ordering suite (`cases.py`, line 1459; `delivery_phase.py`, line 593; `interface.py`, line 166; `adapter.py`, lines 181 to 182), and the Stream proof's live conformance (`proofs/stream-chat/glow_stream_proof/conformance.py`, lines 429 to 448). The Stream proof's own `token_claims` fields (`proof_run.py`, `mechanisms.py`) describe the SDK's tokens and are not the signer.
> ```

**AG12 — the brief, `docs/planning/sv4-chat-notifications.md`: D7, M02's N6.**

> ```
> The Setup script's items (N1, N4, N6 and the Codex P2 on link destinations) are closed as declined (recommended): each needs a script change and a manual paste into both app environments, the environments work as they are, and no finding is a security defect.
> ```

> ```
> The Setup script's items (N1, N4 and the Codex P2 on link destinations) and N6 are closed as declined (recommended). The first three need a change to `scripts/bootstrap-toolchain.sh` and a manual paste into both app environments, and the environments work as they are. N6 is the lint pattern `extend-exclude = ["*.md"]` in `services/api/pyproject.toml` and `proofs/postgres-ordering/pyproject.toml`; it needs no paste, and a Python file under a directory so named is full scope anyway (M02's record; DM-96). No finding is a security defect.
> ```

**AG13 — the brief, `docs/planning/sv4-chat-notifications.md`: D8, the send route's refusals.**

> ```
>   - `POST api/v1/chat/messages`: `MessageIntent`, answering `MessageSubmission`, through `glow_chat`'s `send` unchanged (D6's version).
> ```

> ```
>   - `POST api/v1/chat/messages`: `MessageIntent`, answering `MessageSubmission`, through `glow_chat`'s `send` unchanged (D6's version). Its refusals that come from either member's state or from the end of contact (`match_not_active`, `blocked`, `account_not_active`, `profile_unavailable`, `consent_not_current`) all answer one code, the same for each, so a member never learns which cause stopped a send (OD-60, H; D4; a deletion works as an unmatch; DM-96). D10 shows it for each cause.
> ```

**AG14 — the brief, `docs/planning/sv4-chat-notifications.md`: D11, D4's earlier tests.**

> ```
>   - **D4:** SV3's `block.works_after_unmatch_and_while_paused` (`interaction_cases.py`, lines 1046 to 1109), which asserts that both participants read the same `restricted` match; every case that unmatches a `restricted` match; the contract test of F10's transitions (`packages/contracts/tests/test_transition_contract.py`).
> ```

> ```
>   - **D4:** P06.DB's reference design's block (`reference.py`, line 366) and the six ordering cases that expect `restricted` at version 2 (`cases.py`, lines 360, 758, 847, 861, 878, 910), which then expect `unmatched`; SV3's `block.works_after_unmatch_and_while_paused` (`interaction_cases.py`, lines 1046 to 1109), whose expectations at lines 1082, 1089 and 1099 read `restricted`; and the contract test's frozen F10 table (`packages/contracts/tests/test_transition_contract.py`, lines 911 to 918), which gains the new row. That file's lines 699 to 707 read one sentence of `production-contracts.md` (the oracle's trusted test prerequisites), which A1 leaves as it is.
> ```

**AG15 — the brief, `docs/planning/sv4-chat-notifications.md`: D11, the mobile app and the sample back-ends.**

> ```
>   - **Mobile:** the fixture adapters restrict a match when the pair loses eligibility (`apps/mobile/src/interactions/fixture-adapter.ts`), so there `restricted` has more causes. Stage A does not change the app; AC2 and AC3 replace the fixtures.
> ```

> ```
>   - **Mobile:** the fixture adapters restrict a match when the pair loses eligibility (`apps/mobile/src/interactions/fixture-adapter.ts`), so there `restricted` has more causes, and that adapter looks up F10's rows while it runs; D4 removes none. Stage A changes no mobile file except those `npm run generate` writes (`apps/mobile/src/contracts/generated/`); AC2 and AC3 replace the fixtures. P05.3's fixture commands (`glow_domain.interactions`) still restrict a match on a block and read no flow registry, so they and their tests stay as they are.
> ```

**AG16 — the brief, `docs/planning/sv4-chat-notifications.md`: D12, Stage B keeps D4's sameness.**

> ```
> DM-44's optional revoke-on-all-off; G-04's records of who received a member's messages.
> ```

> ```
> DM-44's optional revoke-on-all-off; G-04's records of who received a member's messages; and D4's sameness for notifications: no notification tells a member a block from an unmatch (DM-96).
> ```

**AG17 — the brief, `docs/planning/sv4-chat-notifications.md`: D12, four entries elsewhere.**

> ```
>     - **DM-54's consent version in the send check:** follows P08's rule for a new version, as carried;
> ```

> ```
>     - **DM-54's consent version in the send check:** follows P08's rule for a new version, as carried, with D5's per-member consent limit for reads;
>     - **the epoch revocation's revisit** (D7; DM-96): integration (stage 2), when the live adapter is configured;
>     - **`read_only` on the real client** (D9; DM-96): AC3 shows a read-only conversation's history with OD-60 H's one neutral line, and no send;
>     - **a staff path that makes a match `restricted`** (D4; DM-96): P07 keeps D4's sameness, serving it to both members as `unmatched`;
> ```

**AG18 — the brief, `docs/planning/sv4-chat-notifications.md`: A1's owned paths, SV3's like.**

> ```
>   - `services/api/glow_discovery/interactions.py` (`_match_projection` only);
> ```

> ```
>   - `services/api/glow_discovery/interactions.py` (`interact`'s reciprocity check and its write of `retired_at`, only);
> ```

**AG19 — the brief, `docs/planning/sv4-chat-notifications.md`: A1's owned paths, the reference design.**

> ```
> (the cases D3 to D7 and D11 name; `environment.py`'s refusal list);
> ```

> ```
> (the cases D3 to D7 and D11 name; `reference.py`'s block (D4); `environment.py`'s refusal list);
> ```

**AG20 — the brief, `docs/planning/sv4-chat-notifications.md`: the exclusions, the generated files.**

> ```
> - **No change** to HDE's ports or adapters (OD-80), to the mobile app, or to `glow_api/` beyond D7's refusal list.
> ```

> ```
> - **No change** to HDE's ports or adapters (OD-80), to the mobile app except the files `npm run generate` writes in `apps/mobile/src/contracts/generated/`, or to `glow_api/` beyond D7's refusal list.
> ```

**AG21 — the brief, `docs/planning/sv4-chat-notifications.md`: the review plan, A0.**

> ```
> - **A0:** a bounded review of the workflow diff and the CI policy's change.
> ```

> ```
> - **A0:** an exact-head review of the complete workflow diff, the pin test and the CI policy's change (each job keeps every step and check it had, the gate requires each job, and no step prints a connection value); then Codex's review, as for every full-scope stage; then the Dev Manager's read of the CI policy's change before A0 merges (DM-96).
> ```

## 15. Checks

- **Environment, names only:** `DATABASE_URL`, `HD_API_KEY` and `GEO_API_KEY` are not set.
- **No calls** to Stream, a database, HDE, Railway, Cloudflare or TypeSafe. Notion and GitHub were read only. The code was read from an export, never run.
- **This file** is the only file committed, on `claude/dev-manager`.

Status: complete
