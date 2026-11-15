# SV3 Stage B exact-head review prompt — who may contact whom, with correction B-C1's own-versions read, D14's record of the row locks the suites send, and a written threat model

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 15 November 2026.** Drafted at PR47's first head and held for DM-74; it reviews Stage B and correction B-C1 together, at B-C1's code head `470d97a`.
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 16, "Review plan" (Stage B's items, for contact, with the own-versions read), "Stage B's review" and "Stage B, correction B-C1".
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Exact-head review of Stage B", with a disposition for each finding (fix before the merge, or carry), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 3.08 (confidence 0.83); rung probabilities low 0.00, medium 0.00, high 0.08, extra high 0.75, max 0.17, ultracode 0.00. Model probabilities Fable 5.1 0.19, Opus 5.5 0.81, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.75). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.015, Fable 5.1 at extra high 0.143, Fable 5.1 at max 0.032, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.065, Opus 5.5 at extra high 0.608, Opus 5.5 at max 0.138, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-15T15:29:11Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 5's pre-merge read follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR47's head, which is this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after SV3 Stage B's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head code and security review of SV3's Stage B**: who may contact whom, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head in full, with a written threat model. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **SV1 and SV2 merged** (PR42 to PR44): sign-in, the profile, its settings, consent, the adult check, the birth input, visibility and photos, all sealed until P11.
- **SV3's Stage A merged** (PR45, `8d83474`, with corrections C1 to C5): who may see whom. Pair eligibility, the two-way rule, age and distance, recommended then broader pages with batches and cursors, the page route, the discovery suite on a fourth disposable database, every explicit account lock `FOR NO KEY UPDATE` (DM-61), and a static scan of account locks whose rules are frozen (DM-68). **B0** (PR46, `947576d`) changed only the proof's tooling.
- **The brief,** `docs/planning/sv3-eligibility-discovery-interactions.md`, revision 16, applies the Dev Manager's conditions word for word, DM-60 to DM-74 (their reports are in `docs/continuity/dev-manager/reviews/`). It rests on Nathan's directions OD-12, OD-55, OD-60 (its R: resurfacing, undo and rematch) and OD-61.
- **Stage B decides who may contact whom.** It builds:
  - like and pass: idempotent directional actions, rechecked under both accounts' locks at commit (D9);
  - the mutual match: reciprocal likes make one match and one `match_activated` event through one new writer in `glow_chat`, `activate_reciprocal` (D10, option (a));
  - unmatch and block through `glow_chat`'s existing writers, unchanged (D11);
  - resurfacing and undo behind their settings, off at launch; rematch refused by a new fixed limit, `rematch_not_built` (D12);
  - D13's additions (undo's DTOs and F08's undo entries), migration `0011_interaction_undo`, and the action routes, each beside Stage A's code;
  - D14's Stage B cases (DB05, DB10) and a record, in each of the four suites, of every row lock it sends (acceptance check 15);
  - the section's items 1 to 6: the page probe's reach, D14's reach (`callproc` with it; DM-73), `VIEWER`'s unused column, B0's test hardening, the ordering harness's two account locks taken `FOR NO KEY UPDATE`, and six earlier tests rewritten as DM-73 named them.
- **Revision 1 of the implementation** stopped at its stop rule with the app code built (`29fad40`); DM-73 ruled on the stop. **Revision 2** was built by a new session on the same branch, `claude/brave-brown-o90q6i` (the merge `6544c2d`, code head `5d58993`, records `291edef`; the evidence record, "Stage B (interactions)").
- **Its run of record** is 43686623299 on `5d58993` (push): all eight jobs passed, the gate printed `Application checks passed`, the discovery suite passed 59 of 59 in 185 s, and each suite's D14 record printed `ROW LOCKS (D14): PASS`.
- **The manager verified it** ("Manager verification of Stage B") and integrated it by fast-forward. PR47 carries it; its push and pull-request runs on `622a4f4` passed all eight jobs.
- **Codex** reviewed `622a4f4` with one P2: no read gives a client the actor's directional version, which a like or pass on a resurfaced candidate, or after an undo, needs (the manager added a block after an unblock). **DM-74** ruled it fixed before this review, as **correction B-C1**: one owner-only read of the actor's own directional row and block, answering alike wherever the actor has no row, and the proof taking its versions as a client does. Codex's review of `6fa1b2c` (records only) raised nothing new.
- **B-C1** (branch `claude/sv3-stage-b-correction-tekmc2`, code head `470d97a`, records `53d3988`; the evidence record, "Stage B, correction B-C1"): `GET api/v1/interactions/<uuid:profile_id>` answering D13's new `OwnInteractionVersions`, seven discovery cases (66 in all), and a ledger over every interaction case. Its run of record is 43727020292 on `470d97a` (push): all eight jobs passed, the gate printed `Application checks passed`, discovery 66/66, each suite's D14 record `PASS`. **The manager verified it** ("Manager verification of B-C1") and integrated it by fast-forward.
- **Codex's review of this prompt's commit,** PR47's head, completes before Nathan gives you this prompt. Read its threads on PR47 with your GitHub tools, and judge any finding on this head as part of focus point 3.

**The code head under review is `470d97a`:** Stage B's `5d58993` with B-C1 on top. You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `470d97a` (the start gate checks this).

**Known before this review** (not findings; the manager records them):
- **DM-73 (6.2) asks this review** to confirm that no Stage B writer relies on `DirectionalInteraction.decided_at`'s default (the application's clock); each writer should set it from `clock(tx)`. Focus 4 below.
- **DM-74 (3.4), for the threat model, not a ruling:** Stage B's block answers 404 `target_not_found` for a profile ID that does not exist, before its locks (`interactions.py`); with a wrong `expected_version` it answers 409 for an existing profile and 404 for a missing one, changing nothing either way. Judge it against D8. B-C1's read must add no second such answer.
- **The proof README's SV3 paragraph** still cites the brief's revision 15 with DM-60's to DM-73's conditions while it describes B-C1 (revision 16, DM-74): a record nit the manager corrects.

**Your scope:**
- **The code:** `git diff 947576d98b7c3103455a670c20fdba2734ff5053 470d97acbf1faff6e81f1e8d8c9b9f27d0131765`, its 38 non-Markdown paths, read in full at `470d97a`; `git diff 5d58993389e1fafcbdece1338dbf9d83736132c6 470d97acbf1faff6e81f1e8d8c9b9f27d0131765` shows B-C1's 18:
  - `services/api/glow_discovery/` (8): new `interactions.py`, `interaction_views.py` and `interaction_urls.py` (with B-C1's `read_own_versions`, `OwnVersionsView` and its route); and Stage A's `contract.py` (with B-C1's `own_versions`), `eligibility.py` (the `resurfaced_before` parameter), `pages.py`, `policy.py` and `predicates.py`, as Stage B changes them;
  - `services/api/glow_chat/contact.py`: `activate_reciprocal` only (87 lines added, none removed);
  - `services/api/glow_domain/profile_settings.py`: `rematch_not_built`;
  - `services/api/glow_persistence/models.py` and migration `0011_interaction_undo`;
  - `services/api/tests/` (5, B-C1's `test_own_versions_offline.py` among them);
  - the contract (`gapp-api-v1.schema.json`, `openapi.json`, `flows-v1.json`, `corpus/shared-v1.json`, `tests/test_transition_contract.py`), with B-C1's `OwnInteractionVersions`, and the regenerated outputs in `apps/mobile/src/contracts/generated/` (3);
  - `proofs/postgres-ordering/` (13): `row_locks.py` and `interaction_cases.py`, new (with B-C1's client versions, its ledger and its seven `own_versions.*` cases); `discovery_cases.py`, `discovery_suite.py` and `discovery_urls.py`; the other three suites' runners (`__main__.py`, `identity_suite.py`, `profile_suite.py`), for D14's record; `cases.py`'s `_harness_holder` and `planted.py`'s `_suspend` (item 5); and the offline tests `test_discovery_offline.py`, `test_profile_offline.py` and `test_row_locks_offline.py`.
- **The records, as claims about the code:**
  - the evidence record's "Stage B (interactions)", "Manager verification of Stage B", "PR47 and Codex on its head", "Stage B, correction B-C1" and "Manager verification of B-C1";
  - the data model's interaction, block and match rows, and its unit-of-work and outbox rows Stage B adds;
  - the contract document's F08 to F10 and F13 index rows and their server mapping (with B-C1's read), and the contracts README's SV3 section;
  - `interactions-fixtures.md`'s server note;
  - the P11 plan's partial evidence for DB04, DB05 and DB10, and its SV3 entry;
  - the proof README: its SV3 paragraph, the write check's entry (with the `callproc` sentence the manager corrected under DM-73, EE9 and EE10), the probe's limit (item 1), and the new entry for the suites' record of the row locks they send (items 2 and 5);
  - the CI policy's new Stage B sentence (`docs/operations/ci-and-branch-policy.md`), against the workflow, which Stage B does not change.
- **The runs:** 43727020292 (B-C1's run of record, on `470d97a`); 43686623299 (Stage B's, on `5d58993`); PR47's runs on its head; and `main`'s push run 43673382167 on `947576d`, for item 5's comparison.
- **Out of scope:**
  - code Stage B does not change: `glow_identity`, `glow_profiles`, `glow_api`, everything in `glow_chat` but `activate_reciprocal`, and Stage A's code except what Stage B changes. A finding there is reported as pre-existing, not as a defect of this item;
  - B0's tooling and the lock scan's rules (frozen, DM-68);
  - the items the brief carries elsewhere: building rematch (SV4), reports and cases (P07.2). Report only where the code contradicts the carry.

**The threat model** (the brief's "Review plan"; DM-31 item 3: who may contact whom is a security, privacy and safety boundary). Write it in your report:
- **Assets:**
  - who has liked or passed whom, and above all that an unreciprocated like is never visible to its target;
  - who has matched with whom: one `Match` row per unordered pair, one `match_activated` event, one chat binding;
  - who has blocked whom, and that the blocked member never learns the direction;
  - contact itself: the send entitlement, revoked after an unmatch or a block, and never restored by an unblock;
  - the directional row's state and version, and its idempotency receipts (keys, keyed digests, replay before staleness);
  - a batch's freshness and consumption, which liked, passed, withdrawn and matched candidates leave or re-enter;
  - each setting's gate: resurfacing after `waiting_days`, undo of the most recent pass within `waiting_days`, and rematch's fixed limit;
  - the account rows' locks and their order: no deadlock, and no `FOR UPDATE` on the account table anywhere the suites send;
  - each member's eligibility (D3 to D5), rechecked for the pair under the locks at commit;
  - the actor's own versions, which B-C1's read returns to the actor alone, and what that read must not reveal: whether a profile exists, its state, and any row whose actor is the other member;
  - D14's record, the proof's secrets, and what CI prints and uploads.
- **Actors:**
  - an anonymous prober;
  - a holder of another member's stolen token (SV1's actor);
  - a member acting with forged, reused or changed idempotency keys, another member's batch, a stale or consumed batch, or a target outside the batch;
  - a member probing whether someone liked them, through any response, page, error, status code or ordering, B-C1's read included;
  - a member probing B-C1's read for whether a profile ID exists, or for its state;
  - a blocked member probing the block's direction;
  - two members liking each other at once, in either order;
  - a pair writer (`block`, `unblock`, `unmatch`), a pause, a consent withdrawal, a preference change or a settings publication racing a like (DB10);
  - an unmatched member trying to contact the other again by liking;
  - a console publication of `discovery.rematch` with `enabled` on, or of resurfacing or undo;
  - anyone who reads this public repository's CI logs and artifacts.
- **Entry points:**
  - the five action routes in `interaction_urls.py` under SV1's actor (the interaction, its undo, the unmatch, the match read and the block), and the page route as Stage B changes what it serves;
  - `activate_reciprocal`, called only from the like;
  - Stage A's selection and recheck, as Stage B changes them (the resurfacing cutoff, the withdrawn state in consumption);
  - migration 0011;
  - the settings publication's `rematch_not_built`;
  - the proof's `row_locks.py` and its wrapping of psycopg's cursor methods in the suites' processes;
  - B-C1's own-versions read, `GET api/v1/interactions/<uuid:profile_id>`.

For each threat, give the code that stops it and the test that proves it. It covers the brief's "Review plan" items for contact:
1. **idempotency** (D9): an identical repeat replayed before any staleness check and writing nothing; a changed payload with the same key a conflict; keys scoped by actor and operation; digests keyed;
2. **the recheck at commit** (D2, D9): D3 to D5 for the pair, blocks both ways, batch membership and freshness, all read under both accounts' locks, after they are held;
3. **the match's uniqueness and lock order** (D10): both accounts locked lower first through SV2's `lock_account`, `FOR NO KEY UPDATE`; one `Match` row and one event from reciprocal likes in either arrival order; the constraint behind it;
4. **`activate_reciprocal`** (the review plan's D10 bullet): every existing function and method in `glow_chat/contact.py` unchanged from `main`'s (compared by AST), `glow_chat`'s existing tests unchanged and passing, and no import of `glow_discovery`; refusing everything `activate_match` refuses and a missing `liked` row in either direction; writing the same rows and events; taking `activate_match`'s lock order and probe points; called only from the like, after its recheck;
5. **unmatch and block** (D11): through `glow_chat`'s writers; a send refused after each; block working after unmatch and while paused; unblock restoring no match and no send;
6. **D8's disclosure rules** in every response, page and error: no unreciprocated like, no block direction, no reason and no other member's private value;
7. **the settings** (D12): resurfacing only after `waiting_days`; undo only of the actor's most recent pass and only within `waiting_days`, the row kept and its version advanced; a withdrawn pass excluding nothing; `rematch_not_built` refusing a publication with `enabled` on and writing nothing; unmatch final, a like never making a second match or reactivating the first;
8. **Stage A's code as Stage B changes it:** the resurfacing cutoff reaching the selection and every recheck through D7's consumption; the selection and each recheck still one statement; the tie-break, the cursor's binding and the card unchanged in behaviour;
9. **ownership** (check 12): each route refusing an unauthenticated request, another member's match or batch, and a stale version;
10. **the seal** (D15): the served runtime imports none of Stage B's modules and selects no fixture provider;
11. **the log capture** (check 13): no private value of another member, birth date, coordinate, distance or "show me" set logged;
12. **the own-versions read** (B-C1; DM-74; FF1, FF3, FF6): owner-only; the actor's account held `FOR SHARE` first; the same 200 answer wherever the actor has no row, whether the profile exists or not and whatever its state, never a 404; the actor's own rows only, never the other member's; `no-store`; and no version recovered any other way in the proof (the ledger);
13. **D14's record** (DM-68, DM-70, DM-71, DM-73): its rule exact for what it reads; its reach (`stream`, `copy`, `callproc`, the driver's own connection), closed by recording, and its stated limits with their planted examples; never refusing or changing Django's own use of the driver's connection; the two harness locks; its reversal; and the proof's secret handling in what it prints.

**The focus:**
1. **The threat model above,** each threat with its stopping code and its test.
2. **The Dev Manager's conditions met in code:** DM-60's for Stage B (D9 to D12, the match's serialization), DM-68's D14 record, DM-70's BB3, DM-71's items and guard conditions, DM-72's item 4, DM-73's EE1 to EE8 (items 2, 5 and 6), and DM-74's FF1 to FF3 and FF6 (B-C1); and the brief's D9 to D15, D17 to D19 for Stage B's code. Name any condition the code does not meet.
3. **The session's deviations and readings** (the record's "Deviations, readings and what could not be run"), against the code, each accepted or a finding:
   - **D14's reach closed by recording, not by a guard.** The brief's item 2: "it closes the gap or states it in the README's 'Limits' with its planted example. A close may be a proof-only guard". Is recording a close? Is the README's word "exact" true for those forms? Can a statement reach the database through psycopg in the suites' processes without passing a wrapped method (a cursor class the wrapping misses, a method psycopg adds, a pipeline)?
   - the database's views and rules counted with its functions;
   - the two reversal findings fixed before the push (15b, the exact routes; 31, the unmatched match's exclusion);
   - DB10's settings publication answered `forbidden`, the viewer's own consent failing first;
   - `consent_not_current` reached through a withdrawn decision seeded as test data;
   - the earlier ordering test the first install broke, fixed in `row_locks.py`, not in the test;
   - the added DB04 case;
   - the contract's union additions (`AppIntent`, `AppResponse`) and F08's request and response lists;
   - the AST comparison run against pinned digests in CI: can it pass while an existing function in `contact.py` changes?
   - D14's counts of connections and threads, of distinct identities;
   - **B-C1's** (the record's "Stage B, correction B-C1"): the unmatch's version taken from the existing match read, where FF3 names "a command's own answer or the read"; the ledger's count at the end of Stage B's case lines; the contract document's F08 and F13 index rows left as they were;
   - **any finding of Codex's** on this prompt's commit (above).
4. **`decided_at`** (DM-73 6.2): no Stage B writer relies on the field's default; each sets it from `clock(tx)`.
5. **No test is weakened or vacuous:**
   - each reversal the record names fails its case;
   - no case could pass while the behaviour it guards is wrong. Above all: the hidden unreciprocated like, the recheck under locks, the match's uniqueness in both orders, DB10's six changes, `activate_reciprocal`'s refusals, the settings' gates, ownership, the log capture, and B-C1's alike answers, its owner-only cases and its ledger;
   - the six rewritten earlier tests keep what they protected (the whole route set and no other, every parameter name and still no key or pad, the migration leaf pinned as `0010` was);
   - the sealed-runtime test is not defeated by a plausible edit.
6. **The contract:**
   - no existing DTO's own properties or enums change;
   - the registry changes only by F08's lists gaining undo's two DTOs and its three new transitions (`undo` from `passed` under `A05`, `like` and `pass` from `withdrawn`), each with an allowed and a forbidden example, and by F08's and F13's response lists gaining B-C1's `OwnInteractionVersions` with its owner projection, no transition changing;
   - the generated outputs match the schemas when regenerated.
7. **The migration:** 0011's `withdrawn` state, `decided_at` with its default, and the receipt code's constraint. Is it safe for P11's empty target, and what would a populated target need?
8. **The workflow and dependencies:** no workflow, lock or requirement file changes. Read the Database proof checks job's steps and logs in run 43686623299: the new cases and D14's record run in the existing steps, as the CI policy's new sentence describes.
9. **The records:** every claim in the texts listed in the scope holds against the code and the runs.

**Re-run, at least,** in a scratch copy of `470d97a`:
- **The API's checks:** `manage.py check`, `manage.py test tests`, `ruff`, `ruff format --check`, the configured `mypy` and `glow_persistence.static_check`. The contract tests. The proof's offline tests, `ruff` and `mypy`, and the lock scan.
- **The contract outputs:** `npm run check` in `packages/contracts`, after `npm ci --ignore-scripts` there and in `apps/mobile`, since the corpus test loads the mobile app's generated validators.
- **Four offline reversals, at least:**
  - the runtime's URL configuration importing `glow_discovery.interaction_urls`, against the sealed-runtime tests;
  - `rematch_not_built` dropped from `_discovery_refusals`, against the API's tests;
  - D14's rule passing `FOR UPDATE` on the account table, against `test_row_locks_offline`;
  - B-C1's read reading the other member's directional row as well as the actor's, against `test_own_versions_offline`;
  - one line of an existing function in `contact.py` changed, against the AST comparison (both its forms);
  - one of your own choosing, against a claim you doubt.
- **The discovery suite, informational:** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows. It is informational, and you name it so. If you can run it, add database reversals you doubt, such as:
  - the like's recheck read before the locks are held;
  - `activate_reciprocal` accepting a missing `liked` row;
  - the two accounts locked in arrival order, not lower first;
  - undo deleting and recreating the directional row;
  - a withdrawn pass still excluding the candidate;
  - an unreciprocated like changing anything the target can see;
  - B-C1's read answering differently for a missing, paused or blocking profile.

**What comes after this review: the correction classes.** Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a member learn of an unreciprocated like, a block's direction, a reason, or another member's private value;
- let a like, pass or undo be applied for a member a predicate in either direction excludes, outside the actor's current batch, on a stale or consumed batch, or without the recheck under both locks;
- let reciprocal likes make no match, or more than one match, event or binding, in either order, or let a route create a match;
- let contact survive an unmatch or a block, an unblock restore it, or an unmatched pair match again;
- let resurfacing, undo or rematch work while off or outside their rules, or a publication of `discovery.rematch` with `enabled` on be accepted;
- let an idempotent repeat write twice, or a changed payload with the same key be accepted;
- let two writers deadlock, take an account lock out of order, or take `FOR UPDATE` on the account table;
- change an existing writer in `glow_chat`, or let `glow_chat` import `glow_discovery`;
- let B-C1's read reveal whether a profile exists, its state, or any row whose actor is the other member, or answer anyone but the actor;
- let the served runtime import Stage B's code, select a fixture provider, or add a package;
- let a test pass where it should fail, or fail where the code is right;
- leave a Dev Manager condition unmet;
- make a record claim more than the code, the tests or the runs show, above all a record that claims the scan, the write check or D14's record refuses or sees more than it does (class 5, as DD1 words it).

Everything else goes into the records. For each finding, say whether it falls in one of these classes. The known items above are not findings.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI and the npm registry, for hash-locked installs in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, through your tools, to read runs.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.
- **Never:**
  - dump the environment, or print a credential, password, token, session key or key;
  - read, print or use the value of any `AWS_*` variable (section 1);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE` (DM-57 and DM-58). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values. If any other `AWS_*` name is present, stop and report.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 947576d98b7c3103455a670c20fdba2734ff5053
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 470d97acbf1faff6e81f1e8d8c9b9f27d0131765 HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet 470d97acbf1faff6e81f1e8d8c9b9f27d0131765 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after 470d97a"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Exact-head review of Stage B'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `470d97a`;
- this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree, from the repository's root:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`; `packages/contracts/README.md`;
- the brief, revision 16, and the Dev Manager's DM-60 (its sections on D9 to D12 and the match's serialization), DM-68, DM-70, DM-71, DM-72, DM-73 and DM-74 reports;
- OD-12, OD-55, OD-60 and OD-61 in the owner-direction register;
- the evidence record's sections from "Stage B, B0" to the end;
- F08 to F10 and F13 in `packages/contracts/production/flows-v1.json`, and `InteractionIntent`, `InteractionOutcome`, `InteractionCommandResult`, `CommandReceipt`, `MatchProjection`, `UnmatchIntent`, `BlockIntent`, `BlockOutcome`, undo's four new DTOs and B-C1's `OwnInteractionVersions` in `gapp-api-v1.schema.json`;
- the contract document's "Pagination, idempotency and stale state", "Policy boundaries and deliberately unavailable operations", "P05.3 internal interaction result and identity bridge" and "Compound actions and model projections";
- P05's notes and code: `docs/architecture/interactions-fixtures.md` and `reciprocal-eligibility-fixtures.md`; `services/api/glow_domain/interactions.py`, `eligibility.py` and `trusted_eligibility.py`;
- the code Stage B builds beside (read only): `glow_chat/contact.py` whole (`_run`, `_lock`, `_contact_state_checks`, `activate_match`, `block`, `unblock`, `unmatch`); `glow_profiles/tx.py` (`lock_account`), `settings_store.py` (`read_shared`, D19) and `idempotency.py`; `glow_identity/authentication.py`;
- every file in the code diff, whole: `interactions.py` (with `read_own_versions`), `interaction_views.py`, `contract.py`, `predicates.py`, `eligibility.py` and `pages.py` above all, with `activate_reciprocal`, the models, the migration, `interaction_cases.py`, `discovery_cases.py`, `row_locks.py` and the runners.

**The runs,** with your GitHub tools: 43727020292 and 43686623299, every job's conclusion, the gate's line, the Database job's steps and its lines for each suite (D14's included); PR47's runs and Codex's threads on its head; and `main`'s 43673382167, for item 5.

## 3. What to do

1. Write the threat model, then review the code against the focus, item by item.
2. In a scratch copy of `470d97a`:
   - re-run the checks and the offline reversals above, and any you doubt;
   - run the discovery suite locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the threat model;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 9), one or two lines each;
- the reversals you re-ran, with their results, the local database ones named informational;
- what you ran, and what you could not run or read.
