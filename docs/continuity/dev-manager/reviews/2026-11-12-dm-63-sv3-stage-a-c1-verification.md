# DM-63 — SV3 Stage A, correction C1: the rule case's wording, and three texts still stating the old lock mode

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `8828112be50dc17f75d8be502dfbe0252e06296c` of `claude/magical-wozniak-yfmmx2`, PR45's head. It holds the consultation (revision 2), the brief's revision 5, the evidence record's "Stage A, correction C1" and "Manager verification of C1", and the data model.
  - **The code:** C1's code head `b44e6f7`. No non-Markdown path differs between it and `8828112`.
  - All five remote heads were still there at 14:44 UTC (`git ls-remote`).
- **Written:** 12 November 2026, finished at 14:44 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only. The HDE names and the STREAM and `PG` names are absent; the three AWS names reported before are present. I read no value.
  - I called no provider, database, HDE, Railway, Cloudflare or TypeSafe service. I ran no application code and no test. I read the code, and checked texts with scripts kept outside the copy.
  - I wrote only this file. Notion was read, not edited.

## 1. What I read

- **The consultation,** revision 2, and the evidence record's "Stage A, correction C1" (the session's) and "Manager verification of C1" (yours), at `8828112`.
- **For item 1, the code:**
  - `glow_discovery/pages.py`: `create`, `continue_page`, `_with_photos`, and the module docstring's lock steps;
  - `glow_profiles/media.py`: `delivery_reference`;
  - `glow_profiles/tx.py`: `run`, `lock_account` and `read_account_shared`;
  - `glow_persistence/models.py`: `RecommendationBatch` and `RecommendationEntry`, for the foreign keys an entry's insert checks.
- **For item 2:**
  - the data model's `AccountAgeState` and `RecommendationBatch` rows, and every other `FOR UPDATE` in it, searched across line breaks;
  - `glow_chat/reads.py`'s module docstring, and the tests that load the module;
  - `glow_identity/revocation.py` and `glow_profiles/tx.py`, for the locks the docstrings describe;
  - SV1's brief line 88, SV2's lines 150 and 518, P06.DB's D5 (line 63), and the manager workflow's supersession sweep;
  - `glow_ordering_proof/cases.py`'s `_harness_holder`.
- **For item 3:** my DM-62 report's Y1 to Y6, against the brief, the P11 plan and the carried-items file. Also my DM-64 report's T8, against the brief.
- **DM-61 section 3.4 and K3, K4:** my own words for the rule.
- **Notion,** read-only (section 7).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. The rule case | **(a), approved with conditions (LM1 to LM3).** The rule is about the page's transaction, and C1 shows it. The words "completes without waiting" were mine (DM-61), and they were too broad. (b) is declined |
| 2. The three texts | **(a), approved with conditions (LM4 to LM6):** known items for the review, fixed in the correction after it. (b) is not chosen. **The done briefs:** three of the four lines are stale, and each gets a one-line supersession note (LM7), not needed for the merge. SV2's line 150 is accurate. **The harness writer:** nothing needed |
| 3. DM-62's Y1 to Y6 | **Confirmed as applied** at `8828112`, with DM-64's T8 (section 5) |
| 4. The sequence | **Agree,** with the brief's revision 6 before the review prompt (section 6) |
| 5. Notion | **Matches `8828112`.** One commit name to correct when DM-63's disposition is recorded, and the optional "Sessions" row (section 7) |

**How to apply:**
- **Where each condition goes:**
  - LM1 to LM4: the brief, as its revision 6, before the review prompt's revision 2;
  - LM5: the section for the correction after the review, when the manager writes it;
  - LM6: the review prompt's revision 2;
  - LM7: the three done briefs, with any records commit.
- **All are Markdown records, but LM5's third pair,** which is a docstring in `glow_chat/reads.py` that the correction session changes. All are in given words; line breaks may move. None is governing Markdown.
- **Verified by script:** each of the 10 old passages was found exactly once at `8828112`, and each pair applies to a copy. The docstring's new lines are at most 93 characters, within the API's 100.
- **No further read is needed** before the review prompt if they are applied as written. A departure comes back first. My next consultation confirms them.

## 3. Item 1 — The rule case

### 3.1 Confirmed

- **The page's transaction never waits on a candidate's writer:**
  - a page with no cursor locks only the viewer's account (`FOR NO KEY UPDATE`) and the selection's settings pointers (`FOR SHARE`); a page with a cursor takes the viewer's account and the same pointers `FOR SHARE` (`pages.py` steps 1 and 2; `continue_page`);
  - neither locks a candidate's account;
  - an entry's insert checks three foreign keys: its own batch, the candidate's account, and a snapshot that no page sets. The account check's `FOR KEY SHARE` does not conflict with a writer's `FOR NO KEY UPDATE`. No entry references a profile row, so SV2's profile lock (`FOR UPDATE`) is never checked.
- **The photo reads wait, as the session and you say:**
  - `_with_photos` runs after `run(body, probe)` has committed the page;
  - it calls `delivery_reference` once for each photo of each card;
  - each call is its own `run(body)`, which refuses inside a caller's transaction, and whose body takes the owner's account `FOR SHARE` (`read_account_shared`) and then reads the asset without a lock.
- **No cycle can form through a photo read:**
  - it holds nothing while it waits, since the page's transaction has ended;
  - once granted, it holds one account `FOR SHARE` and reads;
  - every writer takes that account first, so none holds something the read then needs.
- **The wait lasts as long as the writer's transaction:** `run` sets no lock timeout.
- **A photo read that fails gives that card no reference;** the page still answers.

### 3.2 The options

- **(a), approved.** The rule's purpose holds: no foreign-key check waits on a writer, and no cycle forms. C1's case shows it, and its reversal shows the page's transaction waiting at its entries' insert.
- **(b), declined.** The photo read's `FOR SHARE` is SV2's consistent view: it makes the read wait for a writer in flight, such as a removal request, and then read its result. Reading without it could hand out a photo's reference while its removal is being committed. That changes SV2's merged design, outside C1, for a wait that is bounded and safe.

### 3.3 My error

- **"A page … completes without waiting"** (DM-61 section 3.4, K3) named the whole page. I meant the page's transaction, the place where CX1's foreign-key wait was, and I did not account for the photo reads that follow it. The session was right to word its case against the brief and report it.
- **"One side `provider_unavailable`"** (K3, the reversals) is also inexact. In the block-first order, `glow_chat`'s `block` reports its own `deadlock` outcome, as the session found. LM1 corrects both.

### 3.4 The words

**LM1 (D14):** in the brief, D14, "Page creation under concurrency", replace:

> ```
> and a page whose candidate's writer holds that candidate's account lock completes without waiting. A scan of `services/api` and the reference design finds no explicit lock of an `AppAccount` row other than `FOR NO KEY UPDATE`. The reversals: with the account locks `FOR UPDATE` again, the first two cases deadlock (`40P01`, one side `provider_unavailable`) and the third waits; a planted `FOR UPDATE` lock fails the scan.
> ```

with:

> ```
> and while a candidate's writer holds that candidate's account lock, a viewer's page transaction commits its entries without waiting (DM-63). The page's photo reads, SV2's `delivery_reference` after that transaction, then wait for the writer, as every SV2 reader of an account does: each runs in its own transaction and holds only that account `FOR SHARE`, so it waits as long as the writer's transaction and no cycle forms through it. A scan of `services/api` and the reference design finds no explicit lock of an `AppAccount` row other than `FOR NO KEY UPDATE`. The reversals: with the account locks `FOR UPDATE` again, the first two cases deadlock (`40P01`; one side refused, as `provider_unavailable` from SV2's transaction or `deadlock` from `glow_chat`'s writer), and in the third the page's transaction waits at its entries' insert; a planted `FOR UPDATE` lock fails the scan.
> ```

**LM2 (check 5):** in the brief, acceptance check 5, replace:

> ```
> Since C1 (DM-61): page creation under concurrency (D14) succeeds;
> ```

with:

> ```
> Since C1 (DM-61): page creation under concurrency (D14) succeeds, and a page's transaction never waits on a candidate's writer, while its photo reads may wait for that writer's transaction (DM-63);
> ```

**LM3 (the review plan):** in the brief, "Review plan", the account locks' focus, replace:

> ```
> the page-creation concurrency cases and their reversals (D14);
> ```

with:

> ```
> the page-creation concurrency cases and their reversals (D14); a page's photo reads, which may wait for a candidate's writer, holding nothing another transaction waits for (DM-63);
> ```

## 4. Item 2 — Three texts still stating the old mode

### 4.1 Confirmed

- **The data model's two sentences:**
  - SV2's `transition` takes the account `FOR NO KEY UPDATE` (`glow_identity/age.py:87`), but the `AccountAgeState` row says `FOR UPDATE`;
  - a page locks the owner's account through `lock_account` (`FOR NO KEY UPDATE`), but the `RecommendationBatch` row says `FOR UPDATE`.
- **No other `FOR UPDATE` in the data model is stale:**
  - the settings pointer and the read cursor are not account rows;
  - "The transaction design" states P06.DB's `FOR UPDATE` and C1's change together;
  - the conversation reads' line was rewritten by C1.
- **`glow_chat/reads.py`'s module docstring** says a revocation in flight "holds those rows `FOR UPDATE`". The account rows among them are now `FOR NO KEY UPDATE`, and the match and session rows stay `FOR UPDATE`. The read's wait is unchanged, as you say.
- **No test pins the docstring:** `test_chat_reads_offline.py` and `test_chat_sealed_runtime.py` load and call the module. The AST comparison D10 requires is of `contact.py`, not `reads.py`.

### 4.2 The options

- **(a), approved.**
  - The review reads `b44e6f7`, whose run of record is green.
  - The three texts are records, not behaviour: they change no lock and no result, so nothing the review judges depends on them.
  - One correction then fixes them with the review's findings and DM-64's item (DM-64 T9), under one delta re-review.
  - The two data-model sentences are fixed before the merge, as the fix-or-carry rule requires.
- **(b), not chosen.** It buys a clean head for the review at the cost of one more session whenever the review finds anything, which is the likely case. It would also move DM-64's item before the review (DM-64 T9), where a full review would read it. But DM-64 T9 already gives the delta review the scans as a security boundary, so that gain is small.

### 4.3 The words

**LM4 (the owned paths):** in the brief, "Owned paths", after correction C1's bullet, replace:

> ```
> and the records that state the account lock's mode (the data model, the contract document's F07 server section and the P11 plan's revocation lock-wait line).
> ```

with:

> ```
> and the records that state the account lock's mode (the data model, the contract document's F07 server section and the P11 plan's revocation lock-wait line).
> - **The correction after the review only** (DM-63): in `services/api/glow_chat/reads.py`, the module docstring's sentence on what a revocation in flight holds, and nothing else in the file; and the data model's two sentences that still give the account lock as `FOR UPDATE` (the `AccountAgeState` and `RecommendationBatch` rows).
> ```

**LM5 (the three texts):** the correction after the review makes these three changes. Its section carries the item below.

In `docs/architecture/data-model.md`, the `AccountAgeState` row, replace:

> ```
> takes the account row `FOR UPDATE` before the age state's row
> ```

with:

> ```
> takes the account row `FOR NO KEY UPDATE` (DM-61) before the age state's row
> ```

In `docs/architecture/data-model.md`, the `RecommendationBatch` row, replace:

> ```
> after the owner's account row lock (`FOR UPDATE`)
> ```

with:

> ```
> after the owner's account row lock (`FOR NO KEY UPDATE`; DM-61)
> ```

In `services/api/glow_chat/reads.py`, the module docstring, replace:

> ```
>   ``FOR SHARE``: a read waits for a revocation in flight, which holds those rows ``FOR
>   UPDATE``, and then reads its result; a revocation waits for a read in flight; no reader
> ```

with:

> ```
>   ``FOR SHARE``: a read waits for a revocation in flight, which holds one of those rows under
>   its writer's lock (an account ``FOR NO KEY UPDATE``, any other row ``FOR UPDATE``; DM-61),
>   and then reads its result; a revocation waits for a read in flight; no reader
> ```

The item for the correction's section, numbered in its order:

> ```
> **The texts that still state the old account lock** (DM-63, LM5): the data model's `AccountAgeState` and `RecommendationBatch` rows, and `glow_chat/reads.py`'s module docstring, in DM-63 section 4.3's words. Nothing else in `reads.py` changes, and the API's checks pass with it.
> ```

**LM6 (the review prompt):** in the exact-head review prompt's revision 2, as its known items:

> ```
> **Known before this review** (DM-63, DM-64; not findings: the correction after this review fixes them):
> - the data model's `AccountAgeState` and `RecommendationBatch` rows, and `glow_chat/reads.py`'s module docstring, still give an account lock as `FOR UPDATE`;
> - the profile and discovery suites' value scans and database search can match what the run's own clock prints (DM-64).
>
> Report any other text that still gives an account lock as `FOR UPDATE`, searching across line breaks. By design (D14, as DM-63 words it), a page's photo reads may wait for a candidate's writer after the page's transaction; check that each holds nothing another transaction waits for.
> ```

### 4.4 The two other things seen

**The done briefs:**
- **They are dated records,** as you say. The manager workflow's supersession sweep keeps their history, "with a supersession note where they would otherwise mislead".
- **Three of the four lines would mislead,** because the code now states the new mode and cites these briefs:
  - SV1's line 88: `mark_verified`'s docstring cites "D6 (DM-45 6.1)";
  - SV2's line 518: `lock_account_any_state`'s docstring cites DM-58 item 9;
  - P06.DB's D5: the reference design's own lock changed in C1.
- **SV2's line 150 is accurate:** it gives the account lock without a mode, then "the profile `FOR UPDATE`", and the profile row is still locked `FOR UPDATE` (`operations.py:158`, `recompute.py:128`), as it should be.
- **One note each (LM7),** with any records commit; not needed for the merge.

**LM7 (the done briefs):** in `docs/planning/sv1-identity.md`, replace:

> ```
> the account row locked `FOR UPDATE` before anything else;
> ```

with:

> ```
> the account row locked `FOR UPDATE` before anything else (`FOR NO KEY UPDATE` since SV3 Stage A's correction C1; DM-61);
> ```

In `docs/planning/sv2-profiles-media.md`, replace:

> ```
> lock the owner's account row `FOR UPDATE` first, in any account state,
> ```

with:

> ```
> lock the owner's account row `FOR UPDATE` first (`FOR NO KEY UPDATE` since SV3 Stage A's correction C1; DM-61), in any account state,
> ```

In `docs/planning/p06-db-disposable-postgres-proof.md`, D5, replace:

> ```
> each with `SELECT ... FOR UPDATE`;
> ```

with:

> ```
> each with `SELECT ... FOR UPDATE` (the two accounts `FOR NO KEY UPDATE` since SV3 Stage A's correction C1; DM-61);
> ```

**The harness writer** (`_harness_holder`, `cases.py:1664`): nothing needed.
- Its docstring says it makes a change "which no app writer ever makes" (F2), so a stronger lock there is part of what it models.
- The app writer that arrives locks the same account `FOR NO KEY UPDATE`, which conflicts with `FOR UPDATE` as it would with `FOR NO KEY UPDATE`. So each case still sees the arriver wait and then read the changed key.
- The ordering suite passed with it in C1's run of record. It is outside the lock scan's roots, rightly: the scan judges the app and the reference design.

## 5. Item 3 — DM-62's Y1 to Y6 as applied

**Confirmed.** Each of Y1 to Y6's seven new passages stands exactly once at `8828112`, with no old passage left:
- the brief: Y1 (D3's ADULT), Y2 (check 3), Y3 (both passages of C1's section) and Y4 (the review plan);
- the P11 plan: Y5. The plan changed after `b67bae2` only in `cbeb050`, C1's records, and Y5 stands;
- the carried-items file: Y6, unchanged since `b67bae2`.

**DM-64's T8** stands in the owned paths as written (revision 5). DM-64 section 4.4's words are held for the correction, as DM-64 T9 says.

## 6. Item 4 — The sequence

**Agree,** with these additions:
1. **Before step 2:** the brief's revision 6, with LM1 to LM4, so that the review reads D14, check 5 and the review plan as they now stand. LM7 may go in the same commit.
2. **The review prompt's revision 2** carries LM6's words with K7's and Y4's focus. Waiting for Codex on PR45's head before giving it is your choice under OD-53, not a condition of mine.
3. **The review** reads `ad9ff08` and C1 together, at `b44e6f7`.
4. **The one correction after it** carries LM5's item, DM-64 section 4.4's words and the review's findings. Its delta re-review reads DM-64's item as a security boundary (DM-64 T9).
5. **The merge needs:**
   - a green run of record on the final head, with both items in it;
   - Codex on that head;
   - the delta re-review;
   - my pre-merge read, at a named commit: the CI policy's paragraph, and the data model's and contract's rewritten texts, as the brief's review plan says.

Until the correction, DM-64 T9's two failure signatures are recorded, not re-run.

## 7. Item 5 — Notion (read-only, at about 14:30 UTC; content as of 14:24 UTC, the register copy's as of 17:22 UTC on 11 November)

**How I read it:**
- I searched each page's full text for the items asked, and read Implementation Control's standing bullets whole.
- I did not read every line of its history.

**Implementation Control** says it is matched to `8828112`.
- **Its status** gives DM-64's answer in plain words, including the birth-time exposure, and DM-63 re-sent. It agrees with the record.
- **Its standing lines match:**
  - "Next items": the brief's revision 5, with DM-64's conditions;
  - "Branches": the five heads `git ls-remote` shows, listed at 14:22 UTC;
  - "Mistakes log": AM11-01 to AM11-12, as in the log;
  - "Standing directions": OD-01 to OD-63;
  - "Phase" and "Main": unchanged and right.

**SV3's Work Register row:** "In progress".
- Its Evidence link is pinned at `8828112`.
- Its next action names DM-64's answer, DM-63's revision 2 and the steps after, and matches the handoff.

**The Dev Manager page** matches the review log.
- **DM-64** is considered: merge `30790a9`, T8 applied as revision 5 at `8828112`.
- **DM-63** is pending.
- **One commit name:** both copies say revision 2 "was re-sent at `30790a9`'s batch". The revision is in `8828112`, the commit the message names; `30790a9` is the merge of DM-64's report. Name `8828112` when DM-63's disposition is recorded.
- **Still optional:** the two copies of Dev Manager 4's "Sessions" row still differ ("DM-45 to DM-57" in the repository, "DM-42 to DM-59" in Notion). DM-61 section 7 gives words that cannot go stale.

**The register copy** matches: neither it nor the repository's register has changed since `8130439`.

**The handoff** agrees: its title, the review log line (DM-63 open), the next step, and the branch list. It is 4,982 bytes.

## 8. Where each item goes

- **The brief, revision 6:** LM1 (D14), LM2 (check 5), LM3 (the review plan) and LM4 (the owned paths); a Sessions line for DM-63's answer.
- **The correction after the review:** its section carries LM5's item, with DM-64 section 4.4's words.
- **The review prompt's revision 2:** LM6's known items.
- **The done briefs:** LM7's three notes, with any records commit.
- **The evidence record:** the disposition of C1's first two deviations (the rule case's wording, now LM1 to LM3; `reads.py`'s docstring, now LM5).
- **The review log:**
  - DM-63's dispositions, naming `8828112` as the commit this read covered;
  - the deferred row for DM-62's Y1 to Y6 closes (section 5);
  - a new deferred row: LM1 to LM7, confirmed at my next consultation.
- **Notion:** the DM-63 row's commit, as in section 7; optionally, the "Sessions" row's wording.

Status: complete
