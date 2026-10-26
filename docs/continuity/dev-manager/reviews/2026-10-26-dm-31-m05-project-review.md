# DM-31 — the M05 whole-project review: its proposals, Nathan's decisions and the path

- **Consultation:** DM-31, revision 1, from App Manager 8, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 3, `session_01KVuPEpFRh9B22beZKTKb27`, branch `claude/dev-manager`.
- **Date:** 26 October 2026.
- **Commit read:** `bc6d08afa642bb884233da0cc255903962363cc6`, the head of `claude/magical-wozniak-yfmmx2` when I fetched it at 01:38 UTC. **This read covers `bc6d08a`** (DM-03 G2).
  - `main` is `5b9bcb1` (PR33). No code path differs from it (`git diff --quiet` over `apps`, `packages`, `services`, `proofs`, `.github` and `scripts`). Every path changed since is a regular Markdown file.
- **Environment (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set, and no `STREAM_*` name is present.
- **What I did not do:** no call to a provider, a database, HDE, Railway or the TypeSafe API. I ran no repository code.

## 1. What I read

- **The M05 record**, whole, with "Manager verification of M05"; **the M05 brief**.
- **`git diff f669f37 bc6d08a`:** the review's corrections (`300a24d`), the manager's records since, the refreshed State of the App and the handoff (4,396 bytes).
- **Every target of section 8, at `bc6d08a`:**
  - PF01 (its decisions D05 to D10, §6 to §8 and its revision history) and PF00's revision rules;
  - the manager workflow, the next-manager start procedure, the CI policy and the charter;
  - the register, `CLAUDE.md`, ADR 0004 and the HDE contract request;
  - the reasoning-strength matrix, `docs/README.md` and both component READMEs.
  - A script checked that every quoted "replace" text occurs exactly once in its target. All 28 do.
- **For particular claims:**
  - `configuration_profiles.py`'s `FORBIDDEN_CONNECTION_NAMES`;
  - `apps/mobile/package.json` (Expo SDK 57);
  - DM-01's question 3;
  - the P06.2 brief's "Carried to later changes" and the P11 plan's "Standing guard".
- **The governing diff** `git diff 5b9bcb1 bc6d08a` over every governing path the charter names, with the register and the start procedures.
- **Notion, read-only, about 01:40 UTC:**
  - *Implementation Control*'s status section;
  - the Work Register rows M03, M04, M05, P00.1, P00.2, D10, A01 and A07;
  - *Dev Manager — reviews and approvals*.

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 The proposed text | **Approved with conditions.** As written: P-8, P-9's database-proof bullet, P-16's line, P-18 and five of P-10's seven cells. With a stated change: P-4, P-5, P-7, P-10's OD-10 and OD-30 cells, P-11, P-12, P-14 and P-19 (3.2 to 3.6). With M04: P-7's push-run sentence, P-9's cancel bullet and its upload-artifact row (3.7). Fit to put to Nathan: P-1, P-2 and P-3, each with a change, and P-6 |
| 2 The process proposals | **K1, S1, S3, S4, S6, S7 and S8 approved, S1 with limits and S3 as a target.** These are the managers' to adopt on this approval, with Nathan told. **S2, S5 and D1 are Nathan's,** and I give him a view on each |
| 3 N1 to N6 | **Approved with conditions.** N1, N2, N4 and N5 are his and in OD-32's form, and I agree with each recommendation. N3 is scheduling, so it folds into N5's order. N6 carries only S2, S5 and D1. Three messages, decisions only |
| 4 The path | **Approved with conditions.** M04 next. M05's records merge as their own PR first. E8's assessment moves up to just after M04 |
| 5 The work items | **Approved with conditions.** E12 needs a home now. The standing guard needs pointers from P07 and P08. E15's API lists go with E7 |
| 6 OD-48's row | **Approved; it may merge.** It is the only governing change since `main` |
| 7 The Dev Manager's role | **Findings 31, 41 and 49 accepted, 42 in part. S1 accepted with limits; its estimate disputed** |
| 8 Notion | **No mismatch** |

- **What needs no further read:** every text applied as written here, including my changed wordings (the charter's exception).
- **What goes to Nathan, in item 3's order:**
  - **decisions:** N1, N2, N4 and N5, and S2, S5 and D1;
  - **information:** the process changes adopted on this approval, and the HDE request's six new questions.

## 3. Item 1 — the proposed text

**3.1 The PF01 changes land as a revision.** PF01's revision history requires each change to record "reason, affected tasks, source/contract impact and authority".

- P-4 and P-5 make PF01 1.13, with an entry naming M05 and DM-31. The P-1, P-2, P-3 and P-6 texts each go into a revision when Nathan decides.
- Unlike 1.11 and 1.12, the entry must say that **phase acceptance changes** (P-5: P06, P06.3 and P07).

**3.2 Each text:**

| Text | Verdict | Condition or reason |
|---|---|---|
| **P-1** (server slices; N1) | **Fit to put to Nathan, with one change** | **The slice IDs collide.** The same record uses S1 to S8 for the process proposals, and PF01 must stand alone. Give the slices IDs of their own (for example SV1 to SV4), and state each slice's scope in the text: identity; profiles and media; eligibility, discovery and interactions; chat's HTTP surface. The rest is sound. It keeps the runtime sealed until P11 and P06.DB's rules, and it is the explicit amendment §6 requires |
| **P-2** (the matrix; N3) | **Fit,** with one wording change | "for the launch countries (A05)" becomes "for the launch countries (A05), or the candidate list under comparison until Nathan chooses them". N4's recommendation is to compare first |
| **P-3** (the costed list; N2) | **Fit,** with one change | Move the dated clause ("which no record has updated since 25 September 2026") to the register or the handoff, where it can change. PF01 keeps "Nathan reports the Stream Maker application's status when it changes (OD-22)" |
| **P-4** (superseded statements) | **Approved, with one change** | D08's new cell says the permission is "applied to the sessions of the manual relay by D09". D09 does not say that. It reads "…; the controlling app-only permission, which governs the manual relay's sessions (`AGENTS.md`; OD-01; the named sessions are historical)". D05, D10, §7, P06's two lines and the `proofs/` row are approved as written |
| **P-5** (acceptance) | **Approved, with one change** | P06's completion gains "with the limits those records state", because P06.2's history read is unproven live (its closing record). P06.3's acceptance and P07's are approved. P07's brief shows that the disposable WordPress runs in CI at $0, or brings a fallback to me |
| **P-6** (A05; N4) | **Fit to put to Nathan** | It is wider than N4: all seven A05 questions go to him before P07's brief. The message says so |
| **P-7** (workflow) | **Approved with conditions 3.3 to 3.6** | The step-5 push-run sentence goes with M04 (3.7). The rest is below |
| **P-8** (start procedure) | **Approved as written** | It fixes finding 32, and AM8-01's thread check is right |
| **P-9** (CI policy) | **Part now, part with M04** | The database-proof bullet: approved as written now. The cancel-in-progress bullet and the upload-artifact row describe `always()` and the `v4.6.2` pin, which M04 changes. Writing them twice is waste, so they go into M04's change of the same text (3.7) |
| **P-10** (register State cells) | **Approved with two changes** | **OD-10:** "DM-01 question 3 is recorded as answered by OD-34" is an inference. Replace it with "OD-34 keeps the scorer, as the recommendation, and drops the outcome column the comparison needed, so DM-01 question 3 (keep or retire the scorer after the ten sessions) is read as answered, keep; this is a reading of OD-34, not Nathan's words". **OD-30:** "Superseded by OD-33 and OD-34" becomes "**Updated by OD-33, OD-34 and OD-42**". They extend it, as OD-34's own row says. OD-33, OD-38, OD-39, OD-44 and OD-31 are approved as written |
| **P-11** (matrix, map) | **Approved,** with one fix | Keep "(to 6 October 2026)" only if the uses table or the skill's history shows that date; otherwise drop it. The matrix's title ("…and the TypeSafe request v5") changes with it |
| **P-12** (ADR 0004) | **Approved as a marked correction** | ADR 0004 is accepted by Nathan (OD-18), so the change is shown as a correction, marked "[Corrected by M05, finding 22; DM-31]", not an unmarked replacement. The list it describes is accurate: three `DATABASE` names and five libpq `PG*` names. The hardening item edits the sentence again when it widens the list |
| **P-14** (HDE questions) | **Approved as written,** with a status note | The request's status line records the revision ("26 October 2026: C30 to C35 added, M05 finding 45"). Because the request is in Nathan's HDE process, he is told that it gained six questions (item 3) |
| **P-16's line** | **Approved as written** | — |
| **P-18** (`CLAUDE.md`) | **Approved as written** | It applies DM-09 2(b), and OD-36 says the same |
| **P-19** (charter) | **Approved with S1's limit** | Its last clause reads: "…or a review finding's fix-or-carry that the workflow's rule decides (step 6), unless its fix meets one of that rule's limits". See 3.4 |

**3.3 P-7, the Codex wait: approved, widened by one case.**

- **It restates** AM7-13, DM-28 2.4 and DM-30 4.2 correctly.
- **It also applies to a correction prompt for code under review,** as DM-28 3.1 did for C2-C4. A new finding then joins the pass instead of starting another.

**3.4 P-7, the fix-or-carry rule: approved, restated whole, with its limits.** As proposed, it drops DM-23's middle branch, so a nit would fall outside the rule and come to me. It reads:

- **(a)** A defect in a stage's own code is fixed before the merge if it misses an item of that stage's prompt or falls in a correction class its review prompt names.
- **(b)** A nit, one that misses no item and is in no class, is a recorded follow-up.
- **(c)** A defect that no offline test can show, because only P11's environment produces it, is carried to the P11 plan.
- **(a) wins over (c)** whenever a unit test can show the defect, as F1 and CX12 were shown.
- **The Dev Manager is still consulted when:**
  - the fix's design changes or departs from a condition I set (DM-25 2.1's terms);
  - the fix touches a security boundary (authorization, revocation, privacy or data ownership), a contract, a dependency or a component's interface;
  - the rule does not decide;
  - a charter trigger applies.
- **The mitigation the review names does not hold.** My pre-merge read covers governing text, not code decisions. The safeguard is the exact-head review, which reads the fix against the rule.

**3.5 P-7, the claims checklist: approved, with AM8-11 added.** Its last bullet adds: "and read back the whole status section, not only what changed". The step-7 PR-run bullet and the waiting-checkpoint sentence are approved as written.

**3.6 P-7, "Batching records": approved, with one addition.**

- **The gap:** a follow-up whose owning item has no brief yet still needs a home. That is finding 42's failure mode: DM-02 A4's items were lost exactly so.
- **The addition:** "…or, when the owning item has no brief yet, to a 'Carried to <item>' section of one file, `docs/planning/carried-to-later-items.md`. That item's Work Register row points to it, and its brief folds it in."

**3.7 What goes with M04.** M04 changes `always()` and the upload-artifact pin. So M04's own change of the CI policy and of workflow step 5 states, in their final form, P-7's push-run sentence, P-9's cancel bullet and its upload-artifact row. Its Dev Manager read covers them. Until then, the current text's rule is right ("count a push run only if its gate says `Application checks passed`"); only its explanation is wrong.

**P-13, P-15 to P-17 (the manager's).**

- **No challenge.** P-13 waits on E11 and E7, the next changes to those READMEs. P-15 to P-17 are applied.
- **DM-01 P3's two "later" items,** which P-17 puts to this read:
  - trimming *Implementation Control* is S5, Nathan's;
  - **the PR-to-work-item index is withdrawn.** The Work Register's evidence links and each merge receipt already map pull requests to items.

## 4. Item 2 — the process proposals

| # | Verdict | Whose call | Reason or condition |
|---|---|---|---|
| K1 | **Approved** | The managers' | The layered review finds real defects: 18 of 19 correction passes changed code |
| S1 | **Approved with the limits in 3.4** | The managers', on this approval (P-7, P-19). Nathan is told, since it narrows the oversight OD-15 set up | It applies OD-15's own test: consult where independent review "would materially reduce project risk". A rule-decided verdict adds little |
| S2 | **His.** My view: accept, on terms | Nathan (AI review follows root `AGENTS.md` by his direction, the CI policy) | **Terms:** the delta re-review reads every path the diff touches *as it stands at the head*, not the diff alone. F1 was such an interaction, outside C2-C2's delta. It keeps its security focus. The 60 lines are non-test lines. Codex still reads the final head |
| S3 | **Approved as a target, not a cap** | The managers' | About 150 lines per pass, more only with a stated reason. "What the review must know" is never cut |
| S4 | **Approved** | The managers' | DM-01 P3 already set the 5 KB limit. 3.6's addition applies |
| S5 | **His.** My view: accept | Nathan (OD-26) | The copy drifted (finding 30) and causes a class of mistakes. A summary with commit-stamped links still puts the guidance in Notion. The register copy stays |
| S6 | **Approved** | The managers' | Pin before pruning, OD-45's D8 message first (finding 44) |
| S7 | **Approved** | The managers' | As 3.5 |
| S8 | **Approved** | The managers' | — |
| D1 | **His.** My view: either works | Nathan (OD-34 asked for "plus my pick") | Recorded for 1 of 18 prompts, the column now records nothing. If he keeps it, the manager asks for the pick with each prompt and writes "not given", never "pending" |

## 5. Item 3 — Nathan's decisions N1 to N6

| # | Truly his? In OD-32's form? | My view for him |
|---|---|---|
| **N1** the server build | Yes (scope and the plan); yes | **Agree with (a).** It puts the largest remaining build where its defects surface early (R01). The cost: four more items before P10. Each slice is a full-scope item whose brief I read, because django-allauth headless is a significant new dependency and sign-in is a security boundary. With Codex's security reviews gone (OD-41), the identity slice's exact-head review carries a written threat model |
| **N2** the budget | Yes (spending); yes | **Agree with (a).** The costed list is research only: no account is created and nothing is spent until he approves its line. OD-12's $0 stands until then |
| **N3** the matrix's timing | **Not his alone.** Ordering a research item is the managers' scheduling, and PF01 already requires the matrix | **Fold it into N5's order.** If it stays separate, agree with (a) |
| **N4** countries, age assurance | Yes (product and legal scope); yes | **Agree with (b).** The matrix also says what it does not establish: it is research with dated sources, not legal advice. Whether to take legal advice is his |
| **N5** resuming | Yes (OD-05); yes | **Agree with (b).** A standing resume keeps OD-29 and each brief's read, he can withdraw it at any time, and the manager names each item before it starts |
| **N6** the process | Only S2, S5 and D1 are his | The rest are adopted on this approval and listed for him as information |

**The order: approved, with three messages, decisions only.**

1. **N5 and N1.** They gate the path; N5 carries the order, with the matrix (N3).
2. **N4 and N2.** This message also tells him that the HDE request gained C30 to C35 (P-14).
3. **N6: S2, S5 and D1,** with DM-29 2.3's optional standing direction on `@codex review`, still open.

M04 waits on none of them, so its brief can start once this report's dispositions are recorded.

## 6. Item 4 — the path

**Approved, with three changes:**

- **M04 next,** with findings 10, 11 and 14 (12 and 13 optional). If 12 is taken, M04 is also a classification-policy change. The manager then classifies with the pre-change policy and reads the whole workflow diff (`AGENTS.md`). Its brief comes to me: a workflow with `contents: write` that deletes branches.
- **M05's records, with the texts applied, merge first as their own docs-only PR.** P-7's Codex rule is then on `main` before M04 runs, and M04's PR carries M04 alone.
- **E8's assessment moves up** to just after M04, or alongside the matrix.
  - **Why:** the app is on Expo SDK 57, and npm's fixes imply SDK 58. The assessment decides whether E11 and P06.3 are built on 57 or 58.
  - **It is research:** audit counts recorded (DM-02 B9) and the upgrade's cost. If it says upgrade, the upgrade comes before E11.
- **Then** the matrix (P09.3a), E11, P06.3, and the server slices if N1 is (a), as proposed.
  - **The matrix's prompt** names an environment that can read public web sources (OD-40, OD-43). `Glow App - No Stream`'s network policy may not.
  - **E7 with E15's API and proof refusal lists** goes before the chat slice: both are `services/api` hygiene. E7's open question, whether an epoch bump still revokes provider tokens, comes to me, as a security-boundary question.

## 7. Item 5 — the work items and their homes

**The proposed rows are approved:** E2 (P09.3a), E7, E8, E11, and the second-block-writer proof case (finding 25). The changes:

- **E12 needs a home now,** not "when P07's brief is written". Until then it would sit where DM-02 A4's items were lost (finding 42). It goes in the carried-items file (3.6), and P07's row points to it.
- **The standing guard (DM-30) is accepted in the P11 plan,** where M05 moved it. That departs from DM-30 1.3 ("the guard itself stays out of the P11 plan"), and the departure is acceptable because the entry is permanent and its wording names any phase. Two changes keep 1.3's intent:
  - P07's and P08's carried lists point to it (moderation and deletion are the other likely triggers);
  - the P11 plan's history-policy item, which still says "the guard in the recorded follow-ups", says "the Standing guard below".
- **E15:** the API and proof refusal lists go with E7, not into M04's workflow change. The classifier's submodule flag stays with M04.
- **E6 (CSAM detection and the reporting duty)** is inside E2's scope as a requirement, not an option.
- **E3** follows N2. **Finding 44's pruning** is a manager batch after this read, with OD-45's D8 link pinned first.

Nothing else is missing that completion needs, beyond the security note on the identity slice (item 3, N1).

## 8. Item 6 — OD-48's row

- **The governing diff from `main` is the register alone,** with OD-48's row. No `AGENTS.md`, `CLAUDE.md`, canon, workflow, charter, CI policy, start procedure, `.github` or script changed.
- **The row is accurate:**
  - its quote is exact, "I will branches" included;
  - it marks the manager's reading of those words as a reading;
  - its State matches the M05 brief.
- **It may merge.** The texts approved in item 1 come back before their PR merges only where they do not apply the text approved here.

## 9. Item 7 — the review's view of the Dev Manager's role

**Accepted:**

- **Finding 31.** I wrote DM-28 2.4 and DM-30 4.2 and 4.3 as one item's conditions and never asked for them to be standing rules. P-7 now does that.
- **Finding 41.** In DM-27 to DM-29 I saw the repeated claim slips (AM8-03, AM8-04, AM8-06, AM8-08) without invoking DM-01 P8, which requires a checklist. P-7's checklist answers it.
- **Finding 49, as it bears on me.** My reports are long: DM-28 ran to 289 lines, DM-30 to 191. From now on a report gives the verdicts, the conditions and their reasons, and does not restate what it read.

**Accepted in part:**

- **Finding 42.** Most items are the manager's to apply. The Dev Manager's share is tracking. The charter has "the next consultation or the close-out read" confirm deferred dispositions, but nothing lists them. So DM-09 2(b)'s "at the next change to each file" passed unnoticed at PF01 1.12 and at `CLAUDE.md`'s later changes.
- **My remedy:** the manager keeps a "Deferred conditions" table in the review log (each condition, the event that triggers it, and its state), and each of my governing reads checks it.

**S1: accepted with 3.4's limits. Its estimate I dispute.**

- **The estimate:** "about 5 of Stage C2's 8 consultations would not have been needed". Under the rule with those limits, about 2 would have gone: DM-29, and DM-30's nit half.
- **Why the rest would remain:**
  - **DM-23** created the rule itself, and it reversed the manager's first disposition, which had carried CX8 to P11.
  - **DM-24 and DM-28** touched the revocation path.
  - **DM-25 and DM-27** changed the cursor rule a Dev Manager had set (DM-23 2.3, then DM-25 3.1).
  - **DM-26** answered a departure from a Dev Manager condition (DM-24 1.4).
- **Why the consultations' weight was not their fix-or-carry verdict.** Every verdict matched the manager's recommendation. Their weight was the fix's conditions, which corrected defects in the proposals: d.2's impossible tests (DM-27), and e.1's dropped refusal and its conflict with e.2 (DM-28).
- **The record cuts both ways.** A Dev Manager condition was itself wrong once: DM-24 1.4's impossible pairings, which cost DM-26.
- **The size of a fix** (14 to 63 lines) does not measure its weight. CX9 was a revoked member's history coming back.

**P-19:** accepted with 3.2's wording.

## 10. Item 8 — Notion

**No mismatch:**

- ***Implementation Control*'s status section:** last matched to `bc6d08a`. Its standing bullets agree with the repository:
  - App Manager 8 and Dev Manager 3;
  - `main` at `5b9bcb1`;
  - four branches;
  - AM8-01 to AM8-12;
  - M05 first, then M04.
- **The Work Register rows:**
  - P00.1 and P00.2 link `authority-transfer.md`;
  - A01 and A07 name `c775f39`, and A01 notes C30 to C35 for DM-31;
  - D10 names Dev Manager 3 and PF01 1.12;
  - M03 explains its records;
  - M04's Next Action names push and dispatch, never a pull-request event;
  - M05 is in progress.
- ***Dev Manager — reviews and approvals*:**
  - its lead names App Manager 8;
  - DM-30 is "every item accepted as written" at the merge `ec6e4f6`;
  - DM-31 is "Pending".
- **The procedure copy's stamp** (`51844a5`) waits on S5, as the dispositions say.

## 11. Where each condition goes

- **PF01, revision 1.13:** P-4 and P-5 with 3.1 and 3.2's changes. P-1, P-2, P-3 and P-6 follow Nathan's decisions, each in a revision.
- **The manager workflow:** P-7 with 3.3 to 3.6, apart from the step-5 sentence (3.7).
- **The charter:** P-19 with 3.2.
- **The start procedure:** P-8 and P-16's line.
- **The CI policy:** P-9's database-proof bullet now; the rest with M04 (3.7).
- **The register:** P-10 with 3.2's two changes.
- **The other texts:**
  - the matrix and the map: P-11;
  - ADR 0004: P-12, marked;
  - the HDE request: P-14, with its status note;
  - `CLAUDE.md`: P-18.
- **`docs/planning/carried-to-later-items.md`:** E12, created now (3.6, item 5).
- **The P11 plan:** the history item's pointer to the guard. **P07's and P08's carried lists:** a pointer to the guard.
- **The review log:**
  - "Deferred conditions" (item 7);
  - DM-01 P3's index, withdrawn;
  - DM-31's row and its disposition;
  - item 7's answer beside the review's findings.
- **The messages to Nathan:** item 3's order.
- **The Work Register:** the proposed rows, and E8 moved up the path.

Status: complete
