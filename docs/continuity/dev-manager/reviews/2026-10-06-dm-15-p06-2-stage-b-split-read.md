# DM-15 — Stage B's split and B1's design points (P06.2 brief revision 3)

- **Consultation:** DM-15, revision 1, from App Manager 6, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, branch `claude/dev-manager`.
- **Commit read:** `d12cc0dd3cbd3db6a47d011f107458b400345680`, the head of `claude/magical-wozniak-yfmmx2` when I fetched it (no PR yet). The code is read at `main`, `02072f4dcb0c20dd45dee9bc02e75323d0a2aec7`. **This read covers `d12cc0d`** (DM-03 G2).
- **Environment (names only):** `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are present, never read or used. No HDE name is present. I called no provider, database, HDE or Railway, and ran no code.

## 1. What I read

**At `d12cc0d`:**

- the brief's diff since `335ce7d` (`git diff 335ce7d d12cc0d -- docs/planning/p06-2-chat-integration.md`), whole: the Status line, D1's Stage B, the environment line, the owned paths, acceptance check 5, the review plan, "Carried to Stage B and P11" and "B1's design points";
- the brief's D7 and its checks;
- the evidence record's "Codex's review of PR29", with "Codex's second code review, of `9f6f6ab`" (CX4 to CX6), and "Stage A's merge receipt";
- the DM-15 consultation file, the review log's DM-14 and DM-15 rows, and the handoff's lines on Stage B;
- the migration plan's "Committed schema order".

**At `02072f4`:**

- `services/api/glow_chat/delivery.py`, whole: the plans, the lease, the order and dead-lettering;
- `services/api/glow_chat/contact.py`: the module docstring, `_run`, `_lock`, `_event` and `activate_match` (lines 1 to 245), and the outline of `_revoke_account` and the profile and consent writers;
- `glow_chat/events.py`;
- `glow_domain/chat_provider.py`, `chat_provider_fixtures.py` (the port's operations, lines 120 to 212) and `chat_tokens.py`;
- `glow_persistence/models.py`: `Record`, `OutboxEvent`, `ChatBinding`, `ChatIdentity` and `ChatReadCursor`;
- migration `0003`'s header and operations;
- `tests/test_model_definitions.py`'s test of `0003` (lines 155 to 192).

**Notion, read-only, about 02:05 UTC on 6 October:**

- *Implementation Control*;
- the Work Register's P06.2 row;
- *Dev Manager — reviews and approvals*.

## 2. Summary verdict

| Item | Verdict |
|---|---|
| 1 The split | **Approved with conditions.** B1 needs no read of its own if its prompt meets 1.1 to 1.3. B2's prompt comes to me |
| 2 B1's owned paths | **Approved with conditions:** the dependency files named as unchanged; the migration plan added; `proofs/stream-chat/**` offline only |
| 3 Point a, provisioning before the channel | **Approved with conditions.** Today the order falls to a random ID inside one transaction (3.1). Four further conditions, 3.2 to 3.5 |
| 4 Point b, the reconciliation mark; amend `0003` | **Approved with conditions.** B1 may amend `0003`, under conditions 4.1 to 4.5 |
| 5 Points c and d, the grant and the cut-off | **Confirmed**, with two precisions: the grant refuses an unprovisioned identity (5.1); for B2, `iat` is the issue time truncated to the second (5.2) |
| 6 Points e and f, activation's checks and the suite | **Approved with conditions** 6.1 to 6.3 |
| 7 Notion | **Matches `d12cc0d`.** Two stale sentences, one in Notion and one in the repository |

The conditions are words for brief revision 3 and B1's prompt. Applied as written, they need no further read (G2). No item is Nathan's.

## 3. Findings

### Item 1 — The split: approved with conditions

**The split is right.** All eight carried items (F1 to F5, CX4 to CX6) are changes to the domain, the persistence adapter, the delivery logic, the fixture and the suite. Each can be built and proven offline against the fixture provider and a disposable database. Two things follow:

- B2's live session then has one job: an adapter on a port that is already settled, plus its conformance run. Its review sees only that.
- B1's offline review sees the concurrency and schema changes without live noise.

That is the reason D1 gave against one session, applied one level down. Each part merges before the next, which matches OD-08 and OD-29.

**B1 needs no prompt read of its own.** The charter requires a read before effect for prompts that authorize credential use or live provider actions. B1 authorizes neither. Its design choices are settled in this read, and its PR's governing changes come to me before it merges, as the review plan says. B2's prompt comes to me (credential, live actions, `getstream`).

**Conditions.** B1's prompt goes to Nathan without a further read only if:

- **1.1** it states design points a to f with this report's conditions as written;
- **1.2** it authorizes no credential, no network call to any provider and no new dependency. It starts in `Glow App - No Stream`. At start the session checks that no `STREAM_*` name is present, and if one is, it stops and reports to Nathan;
- **1.3** a departure from any of these, found while the prompt is written, comes back to me before the prompt goes to Nathan, as DM-11's did.

### Item 2 — B1's owned paths: approved with conditions

The list covers the work. Three precisions:

- **2.1** "Adding no dependency" is checkable: `services/api/requirements*.in`, `requirements*.lock`, `pyproject.toml`'s dependencies and `dependency-inventory.json` are unchanged. No `getstream` import and no Stream adapter module appear in B1. Those are B2's.
- **2.2** Add `docs/operations/migration-plan.md`. Its "Committed schema order" lists `0001` and `0002` only; `0003` is not there at `d12cc0d`. B1 adds `0003`'s row (and `0004`'s, if one is added) and the amendment rule of item 4.
- **2.3** `proofs/stream-chat/**`: the C5 nits 2 and 3 and the header-name allowlist, with their offline tests only. No harness command runs live in B1. The harness's guard, budget and cleanup are otherwise unchanged. B2's prompt read covers the harness as B1 leaves it.

### Item 3 — Point a, provisioning before the channel: approved with conditions

**The rule is right.** One idempotent provisioning call per new identity, delivered before the channel that names it, with the ID committed first, is what Stream needs. It also makes the fixture honest.

**The current order cannot carry it as it is.** The order is `(available_at, created_at, id)` (`delivery.py:263`). Every event that one writer writes takes the same `available_at`: the `clock_timestamp()` read once after its locks (`contact.py:204`, `:236`). `created_at` is `auto_now_add`, the app's clock at each save, which can repeat or step back. `id` is a random UUID. So within activation's transaction, the provisioning events and the channel event can tie on the first two keys and fall to the random ID. That is the outcome point a forbids.

The conditions:

- **3.1 A deterministic order key.** Events of one transaction are delivered in the order that transaction wrote them, with neither the app's clock nor a random value deciding. The recommended mechanism is a database-assigned, monotonically increasing column on `OutboxEvent` (an identity column), used in place of `created_at, id` after `available_at`. Its schema follows item 4. Another mechanism is acceptable if the session shows it is equally deterministic and records why. A test writes the channel event and the provisioning events in one transaction and shows the order over repeated runs. It does not rest on clock values.
- **3.2 Provisioned only on receipt; no waiting on what lies behind.**
  - The identity gains a state that means "not yet provisioned". It becomes provisioned only on the provider's receipt.
  - When the channel event reaches the head and either member is not provisioned, it does not retry or wait. Its provisioning, ordered ahead of it, has already been settled. The channel event dead-letters with `member_unavailable`, and its binding takes item 4's mark.
- **3.3 Lost provisioning response (the CX6 analogue for users).** A provisioning event dead-lettered after a call whose response may have been lost marks the identity with item 4's mark. A later `access_revoked` or `session_epoch_bumped` for that identity still makes its call. A user the provider does not have counts as deactivated, or as revoked.
- **3.4 The port and the fixture.**
  - `OPERATIONS` gains the provisioning operation with `user_id` only, and `events.DELIVERED` gains its event.
  - The fixture's `create_channel` refuses an unknown member, as the brief says.
  - Provisioning a user the fixture already holds returns `already=True`.
- **3.5 One identity, one provisioning.** An identity that already exists from an earlier match gets no second provisioning event. Its earlier event precedes the new channel by `available_at`, since both writers lock that account. A test covers a second match for an already-provisioned account.

### Item 4 — Point b, the mark, and amending `0003`: approved with conditions

**The mark is right:** a state or field meaning "needs reconciliation", with the Glow code that caused it, on the binding and on the identity. It must be a code from `ERROR_CODES` or a named Glow reason, never provider text.

**Amending `0003` is allowed.** The reasons:

- `0003` has been applied only to the CI job's disposable databases, which are created and destroyed each run;
- P11 applies migrations, and no persistent database exists before it (D7; the migration plan);
- so no database has to reconcile its migration ledger with a changed `0003`;
- one reviewed migration for P06.2's schema is easier for P11 to review than a `0004` that exists only because review found the gap after Stage A merged.

A `0004` is also acceptable. Either way, the conditions are:

- **4.1 Never through `0001` or `0002`.** The mark on `ChatBinding`, and any order column on `OutboxEvent` (3.1), change models that `0001` and `0002` created. Those changes are new operations (`AddField` or `AlterField`) in `0003` or `0004`. The two files stay byte-identical; their hash test stays as it is.
- **4.2 Generated, not hand-written.** The amended `0003` (or the new `0004`) comes from the pinned autodetector and is reviewed as source. It has no `RunSQL` or `RunPython`, as the migration plan requires of `0001` and `0002`.
- **4.3 The test names the change.** `test_migration_0003_is_additive_and_0001_0002_are_unchanged` today asserts exactly two `CreateModel` operations. It is updated to assert the exact operation list, so that a later edit cannot pass unnoticed. `makemigrations --check --dry-run` passes, and the proof's run applies the result from zero.
- **4.4 The rule is recorded.** The migration plan says: an unapplied migration may be amended until it is first applied to a database that is not disposable; from P11's first such application it is frozen, and changes go into a new migration. The B1 report states that `0003` has been applied only to disposable databases, and says how this was established (the repository's records; no persistent database exists before P11).
- **4.5 Where the mark acts.** A message is never delivered into a marked binding. A revocation of a marked or `failed` binding still makes its removal (CX6), and a channel the provider does not have counts as removed. The fixture today raises `channel_unavailable` for that case (`chat_provider_fixtures.py`, `remove_members`). The delivery maps it to "removed" for that plan only and records the binding `revoked`, keeping the mark's reason.

### Item 5 — Points c and d: confirmed, with two precisions

**DM-14 item 3's points fall in the right places:**

| Point | Part |
|---|---|
| 1. Grant's transaction, account then session `FOR SHARE` | B1, persistence adapter |
| 2. Issue time from `clock_timestamp()` under the locks | B1 (the read); B2 (the signer uses it) |
| 3. Cut-off up to the next whole second | B1, delivery; B2's conformance shows Stream's comparison |
| 4. Cut-off stays the bump's pre-commit time | B1, unchanged: `event.available_at` |
| 5. Tests with the app clock skewed | B1 (the grant and the bump); B2 (the live comparison) |

`grant_chat_token` stays pure. The adapter passes it the locked rows and the database time. Rounding in delivery, with the stored value exact, means the fixture and Stream see the same value, and Glow's record keeps the true time.

Two precisions:

- **5.1** "Identity active" in the grant means provisioned (3.2) and not deactivated. A grant for an identity not yet provisioned is refused with `no_chat_identity`, so that no token is signed for a user the provider does not have.
- **5.2 For B2's prompt.** The signer sets `iat` to the issue time **truncated** to the whole second, never rounded to the nearest second or up. Rounding to the nearest second would let a token issued at 10.6 s carry `iat` 11 and survive a cut-off at 10.8 s, which is sent as 11. "The next whole second" in point 3 means strictly greater: a cut-off of exactly 10.000000 s is sent as 11. A B1 test covers a cut-off with zero microseconds. B2's prompt states the truncation, and its conformance run shows it.

### Item 6 — Points e and f: approved with conditions

**Point e is right.** Activation reads profile and consent state under both account locks, as the send does. The pause, restriction and consent writers take the account lock first (D5), so the same protocol makes these checks race-free. Reciprocal likes and two-person eligibility stay with P11's F09 activation, as the brief records.

- **6.1 The races.**
  - Forced cases both ways: a pause commits first, so activation refuses; activation commits first, so the pause follows, and the send refuses afterwards. The same both ways for a consent withdrawal.
  - Restriction shares the pause's writer (`_set_profile`) at `02072f4`. The pause case covers it only if the session shows that the code path is shared. Otherwise restriction gets its own case.
  - Each forced wait is observed, as for the send.
- **6.2 The oracle.** A new rule says that no activation commits after a committed pause, restriction or withdrawal of either member that it would have read. The rule has a planted control that fails in the same run. The same applies to any other new rule (for example, provisioning before the channel, if the session states it as an oracle rule rather than an offline test).
- **6.3 Unchanged, and shown.** `reference.py` is byte-identical to `02072f4`, and its 56 cases and ten controls are unchanged. The B1 report shows the hash or an empty diff. `activate_match`'s docstring says it is the proof's and the conformance run's way to make a match, not F09's activation.

**Point f is right as written**, with 6.2's controls. The delivery cases (B1, offline or in the database job) cover:

- provisioning before the channel;
- a lost provisioning response (3.3);
- a lost creation response followed by a revocation (CX6, 4.5);
- each dead-lettered revocation marking its row (F3).

### Item 7 — Notion: matches `d12cc0d`

- ***Implementation Control*** is matched to `d12cc0d`: brief revision 3 (proposed), the B1 and B2 split, design points a to f, the DM-15 consultation and main's push run 37401265870.
- **The Work Register's P06.2 row** is "In progress". Its text matches through "Next: DM-15 … then B1's prompt. The Dev Manager reads B2's prompt before Nathan runs it."
- ***Dev Manager — reviews and approvals*** matches the review log:
  - DM-14's disposition is "Considered by App Manager 6 at `9f6f6ab`", every item accepted;
  - DM-15's row is pending;
  - my session row runs through DM-14 (`e85bad6`, integrated at `52a642d`).

**Two stale sentences, to update when revision 3 is accepted:**

- **Implementation Control** still says "the Dev Manager reads Stage B's and Stage C's prompts". Under revision 3, that is B2's and Stage C's.
- **In the repository,** the evidence record's "Stage A's merge receipt", "Next", still describes one live Stage B whose prompt I read. It predates revision 3. A pointer to revision 3 fixes it.

The consultation file in the repository still holds `<RECORDS_COMMIT>`. The message Nathan carried names `d12cc0d`, which is what the file's instruction requires, so this is not a mismatch.

## 4. Verdicts

| Item | Verdict |
|---|---|
| 1 | Approved with conditions 1.1 to 1.3; B1's prompt needs no read of its own; B2's comes to me |
| 2 | Approved with conditions 2.1 to 2.3 |
| 3 | Approved with conditions 3.1 to 3.5 |
| 4 | Approved with conditions 4.1 to 4.5; amending `0003` allowed |
| 5 | Confirmed, with 5.1 (B1) and 5.2 (B2's prompt) |
| 6 | Approved with conditions 6.1 to 6.3 |
| 7 | Notion matches `d12cc0d`; two stale sentences |

## 5. Questions for Nathan

None. Amending `0003` touches no persistent database, so it is not a risk acceptance for him.

## 6. Documentation to update

- **Brief revision 3:** conditions 1.1 to 6.3 in D1, the owned paths and "B1's design points"; 5.2 in "Carried to Stage B and P11", item 1, for B2.
- **The migration plan:** in B1, under 2.2 and 4.4.
- **The evidence record:** the receipt's "Next", pointing to revision 3.
- **Notion:** *Implementation Control*'s "Stage B's and Stage C's prompts".
- **The review log:** DM-15's disposition.

## 7. Limits

- **Code:** I read the code at `02072f4` and ran nothing. The claims about tied order keys come from the code: one `clock_timestamp()` per writer, `auto_now_add`, and a UUID primary key. They do not come from a run.
- **Stream's `iat` comparison** at whole seconds is DM-14's premise. B2's conformance run shows it.
- **Notion:** the three pages in section 1 only.
- **No scoring** (OD-15).

## 8. Relay message for Nathan to paste into App Manager 6's session

> **From Dev Manager 2 to App Manager 6 (relayed by Nathan, 6 October 2026)**
>
> DM-15 is answered on `claude/dev-manager`, in the commit that adds `docs/continuity/dev-manager/reviews/2026-10-06-dm-15-p06-2-stage-b-split-read.md`. My read covers `d12cc0d`, with the code at `02072f4`. No item is Nathan's. Applied as written in revision 3 and B1's prompt, the conditions need no further read.
>
> 1. **The split: approved with conditions.** B1's prompt needs no read of its own if it states points a to f with my conditions, authorizes no credential, provider call or dependency, starts in `Glow App - No Stream` and stops if any `STREAM_*` name is present. Any departure comes back to me. B2's prompt comes to me.
> 2. **Owned paths: approved with conditions.** The dependency files are named as unchanged, with no `getstream` and no adapter in B1. Add `docs/operations/migration-plan.md`, which lacks `0003`. `proofs/stream-chat/**` is offline only.
> 3. **Point a: approved with conditions.** Today the order `(available_at, created_at, id)` ties within activation's transaction and falls to a random UUID. Require a deterministic key; I recommend a database-assigned identity column after `available_at`. Also:
>    - provisioned only on receipt;
>    - a channel event whose member is not provisioned dead-letters, never waits;
>    - a lost provisioning response marks the identity, and later deactivation or revocation still calls (a user the provider lacks counts as done);
>    - `user_id` only, idempotent;
>    - no second provisioning for an existing identity.
> 4. **Point b: amending `0003` allowed**, with conditions:
>    - the binding's and outbox's changes are new operations, never edits to `0001` or `0002`;
>    - generated by the pinned autodetector, with no `RunSQL` or `RunPython`;
>    - the `0003` test asserts the exact operation list;
>    - the migration plan records the rule "amendable until first applied to a non-disposable database";
>    - the mark carries a Glow code;
>    - a channel the provider lacks counts as removed for a marked binding's revocation.
> 5. **Points c and d: confirmed.** The placement is right: the lock and the database time in B1, rounding in delivery, the signer in B2. Two precisions:
>    - the grant refuses an unprovisioned identity;
>    - for B2's prompt, `iat` is the issue time truncated to the second (rounding to nearest is unsafe), and "next whole second" is strict, with a B1 test at zero microseconds.
> 6. **Points e and f: approved with conditions.**
>    - Forced races both ways for pause and withdrawal; restriction too, unless it shares the pause's path.
>    - A new oracle rule with a planted control.
>    - `reference.py` shown byte-identical.
>    - `activate_match`'s docstring says it is not F09's.
>    - Delivery cases for provisioning order, lost responses, CX6 and F3's marks.
> 7. **Notion matches `d12cc0d`.** Two stale sentences:
>    - *Implementation Control*'s "the Dev Manager reads Stage B's and Stage C's prompts" (now B2's);
>    - the evidence record's merge-receipt "Next".

Status: complete
