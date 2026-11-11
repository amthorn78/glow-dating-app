# DM-57 consultation — SV2's brief, revision 6: Stage B, R2 for photos, and the pointer order

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 11 November 2026.**
- **Why:**
  - The brief's revision 6 changes D10's design on a security boundary (uploaded files), after Nathan's direction that photos use R2 object storage (OD-62).
  - It decides the settings' pointer order (D19), which DM-56 V5 left to Stage B's brief.
  - It lists Stage B's work, including changes to Stage A's code.

  Each goes to the Dev Manager before Stage B's prompt (the brief's review plan). This is also the next consultation, which confirms DM-56's V1 to V5 as applied.
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 10's disposition in the review log, "DM-57";
  - the brief's revision 7, where your words change it;
  - Stage B's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** no Stage B prompt goes to Nathan; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-57's disposition and SV2's Stage B PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-57 — SV2's brief, revision 6: Stage B, R2 for photos, and the pointer order.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **Stage A merged** with PR43 at `4dc2061` (10 November 2026). The merge receipt is in the evidence record (`docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, "The merge receipt for Stage A"). `main`'s push run 42925412949 passed every job, and no PR is open.
- **Nathan's direction** (OD-62, 11 November 2026, in App Manager 10's session): *"proceed with the brief. Note that we will use R2 object storage for photos"*. It is in the owner-direction register.
- **The brief's revision 6** (`docs/planning/sv2-profiles-media.md`) changes:
  - the status line and "Why";
  - D10: three new bullets and three changed;
  - D19, new;
  - three owned-path lines (`glow_profiles`, `glow_domain` and `flows-v1.json`);
  - the exclusions and the dependencies;
  - checks 10 and 13;
  - the review plan;
  - "Stage B (revision 6)", new;
  - the Sessions entry.

  `git diff 780fb20 <RECORDS_COMMIT> -- docs/planning/sv2-profiles-media.md` shows each. No governing Markdown changed.
- **Codex** reads no commit while no PR is open. This message's commit is ordinary documentation.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. D10 for R2 (OD-62).**
- **The reading.** The originals and the variants Glow delivers are objects in private Cloudflare R2 storage, not Cloudflare Images, and Glow's own processing makes each variant. PF01 §4 allows either ("Cloudflare Images/private R2 as appropriate"), so canon is unchanged.
- **What changes in the design:**
  - **Two ports with fixture adapters only:**
    - **storage:** the upload credential, the completion, writing a variant, deletion and the delivery reference;
    - **processing.**

    SV2 makes no R2 call, holds no credential and adds no SDK.
  - **Object keys** are random and opaque: no account, profile or asset ID, no filename and no member value, since keys show in the store's logs and in delivery addresses. No bucket has public access.
  - **The upload credential.** The domain does not rely on it being one-use. It adopts only the first completion that matches the grant's key and the policy's byte limit, and a later completion for that key changes nothing.
  - **The system review step** (quarantined → review_pending, `system`) is Glow's processing: decode within the policy's bounds, remove metadata, re-encode, and write the variant under a new key, on the adopted original only (its size and entity tag). This is where P04.3's fixture already simulates processing, so no lifecycle state or registry entry changes for it. P11 decides where the processor runs (a Glow worker, or a Cloudflare service reading from R2, whose cost goes to Nathan first).
  - **Removal** completes only on the storage adapter's acknowledgment that every object of the asset is deleted.
  - **Retention:** how long an original is kept after its variant is decided is a retention question for the third A05 message, with G-05's hold.
- **The P04.3 mapping's facts** that the design relies on (`docs/architecture/media-provider-mapping.md`, checked on 23 September 2026): R2's event notifications reach a consumer through Queues, and object-delete events omit size and entity tag. The brief states no other R2 mechanism as fact. Signed upload and delivery addresses, private access, event authentication and delivery properties are P11's to verify (PV04, DB08).
- **Asked:**
  - Is the reading right, or does the direction need Nathan's answer first, for example on whether a Cloudflare image service may process R2's objects?
  - Do the two ports and the processing step at `review` stand?
  - Does the matrix need a recheck for R2 as a processor before Stage B, or only before P11 activates it?

**2. D19, one pointer order in every transaction** (DM-56 V5, its recommended option).
- **The rule.** Every transaction takes all its settings pointers in its first `read_shared` call, in name order. A publication takes its own pointer, then any it reads, in name order. A later read of a held pointer waits for nothing.
- **The four changes in Stage A's code** are the transactions your DM-56 section 6 named: `set_field`, `set_area`, staff's approval without identity verification, and the owner's catalog read. Stage B's photo writers follow the rule.
- **The check.** `settings_store` records each transaction's held pointers. A lock that sorts before a held one, and is not itself held, raises an internal error that rolls the transaction back, never a member's refusal. Every profile-suite case runs under it, with an offline test, a static test that nothing outside `settings_store` locks a `PolicyRevision` row, and a reversal. Today the only lock sites are `settings_store.read_shared` (raw `FOR SHARE`) and `publish` (`select_for_update`); `glow_chat` locks no pointer.
- **Why.** With one order for every pointer lock, and publications taking no account row, no wait cycle forms whatever PostgreSQL's queueing does. V5's suite case is then not needed.
- **Options:**
  - **(a)** as written, the check raising in every environment (recommended);
  - **(b)** the same rule, with the check active only under the proof's and the tests' settings;
  - **(c)** keep the order and add V5's suite case.

  (b) avoids a programming error reaching a member as a server error; (a) also catches an order that only production's paths reach.
- **Asked:** a verdict, and whether the rule's statement covers every lock path you see.

**3. "Stage B (revision 6)":** Stage B's work, its stop rules and its review.
- **The work:** photos (D10); the photo requirement (D9) with its recompute and demotion; F05's `approve` and `reject` becoming `system` (OD-61), the only existing registry entries that change; D19; the carried items (C3's allowlist, N2 to N5's guards, DM-50 1.2 if `identity_support.py` changes); the proof's cases; the records.
- **The media policy** is a new setting, `media.policy`, seeded as version 1 with `development-media-1`'s values.
- **The stop rules:** a new dependency (an S3 or R2 client included), a provider call or credential, a change to `glow_chat`, `glow_identity` or `glow_api`, a mobile change, or a change to another existing registry entry.
- **The review:** a full exact-head review with a written threat model, which takes the media items, D19 and Stage B's changes to Stage A's code. Your pre-merge read covers the data model's and contract's rewritten texts, and the CI policy's paragraph if it changes.
- **Asked:** does the scope stand as one stage, with these stop rules and this review? Is anything missing that Stage B needs before its prompt?

**4. DM-56's V1 to V5 as applied** (the review log, "Deferred conditions").
- **Where they are:**
  - V1 and V2 in `docs/architecture/data-model.md`;
  - V3 in the brief's D7;
  - V4 in the evidence record's "Delta review of correction C3";
  - V5 in the carried-items file's Stage B entry.
- **The manager's check:** each was applied by script from your report's quoted blocks at `a644771`, each old passage was found once, and each new text is present once. They merged with PR43.
- **Asked:** confirm as applied.

**5. The manager branch after a merge.**
- **What happened:** after PR43 merged, the manager branch carried two receipt commits (`65a7221`, `c52b41f`) on top of PR43's merged head. The session's git rule says a merged PR's branch starts again from `main`.
  - App Manager 10 first rebased them onto `main`, but the force push that needs was refused by the session's safety check, and nothing was pushed.
  - It then merged `main` into the manager branch instead (`780fb20`), with no history rewritten. The next PR's merge base is `4dc2061`, and the content is unchanged.
- **Why it matters:** after PR42 the branch carried on from the merged head, and that is how AM10-13's start gate came to check a commit the branch did not hold.
- **Proposed words** for the manager workflow, step 7, after "Verify actual main and record an ordinary-documentation receipt in `docs/testing/evidence/`.":

  > ```
  > - **Bring `main` into the manager branch.** Once the merge is verified, and before any new commit, fast-forward the manager branch to `main` (`git merge --ff-only origin/main`). If commits already follow the merged head, merge `main` into the branch instead. No history is rewritten, and the next PR's merge base is `main`'s merge commit.
  > ```
- **Asked:** approve the words, change them, or keep the earlier practice.

**Notion:** please check that the Implementation Control page, SV2's Work Register row, the Dev Manager page and Notion's copy of the register (OD-62) match `<RECORDS_COMMIT>`. The repository wins (OD-27).
