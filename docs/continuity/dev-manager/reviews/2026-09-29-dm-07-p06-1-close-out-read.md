# DM-07 — The P06.1 close-out read

- **Consultation:** DM-07, revision 1, from App Manager 5, relayed by Nathan (OD-25). The consultation file is `docs/ephemeral/2026-09-28-dm-07-p06-1-close-out-read.md`.
- **Reviewer:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, branch `claude/dev-manager`.
- **Commit read:** `89a8d018d6bdfba0fe41fa0b54964f33775ddaac`, the head of `claude/magical-wozniak-yfmmx2` (draft PR27). The branch had not moved when I fetched it again at 00:55 UTC on 29 September. **This read covers that commit** (DM-03 G2).
- **Environment (names only):** `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are present, never read or used. No HDE name is present. I called no provider, database, HDE or Railway, and no TypeSafe API.

## 1. What I read

**The governing diff, `fa4dc5f..89a8d01`, in full.** It covers the seven files, 17 commits, 140 lines added and 50 removed. `apps/mobile/AGENTS.md` and `apps/mobile/CLAUDE.md` are unchanged. I checked each change against:

- the dispositions of DM-03 to DM-06 in the review log;
- OD-21 to OD-34 in the owner-direction register;
- the mistakes log's preventions for AM3-19, AM5-01, AM5-02, AM5-03 and AM5-07.

**Also read at `89a8d01`:**

- ADR 0003 (its conditions and "Revisit when") and ADR 0004;
- the HDE contract request;
- the architecture document's section 5;
- the evidence record:
  - "Economics discovery", in full: the account facts, the notes and report as relayed, the manager's verification and the disposition;
  - the I2b review's disposition;
- the economics prompt's diff from revision 1 (blob `dd872d5`) to revision 2;
- the brief's diff since `b729340`;
- the review log, handoff, mistakes log and environment inventory diffs since `b729340`;
- the DM-07 consultation.

**Searched at `89a8d01`:**

- stale "four jobs" or "six jobs" wording in living documents: none; only dated history keeps it;
- PF01 §7's S15 sentence;
- the register and the charter, for the Dev Manager succession of 28 September.

**Notion, read-only, 00:40 to 00:55 UTC on 29 September:**

- *Implementation Control*, last edited 21:22 UTC on 28 September;
- *Dev Manager — reviews and approvals*, 21:22 UTC;
- the register copy, 12:46 UTC on 27 September;
- the Work Register rows P06.1, A08, A04, A05, D10 and M03;
- the uses-table rows for both revisions of the economics prompt.

**Arithmetic, checked:** 884 + 119 + 698 + 560 = 2,261 ledger calls, and 2,262 − 10 = 2,252.

## 2. Summary verdict

| Item | Verdict |
|---|---|
| 1 Governing Markdown | **Approved with conditions.** Five files approved; PF01 and the charter approved with conditions (findings 1.1 and 1.2), with one line of CLAUDE.md under finding 1.1. No change adds a rule Nathan did not direct. The gap runs the other way: a practice Nathan directed is not yet recorded as a rule. ADR 0003 approved |
| 2 HDE contract request | **Approved;** one *soon* item |
| 3 ADR 0004's restore risk | **Confirmed,** with one *soon* addition for the other direction |
| 4 (a) Live read | **Option (i),** with a condition on P06.2's brief. Not Nathan's |
| 4 (b) Activities query and resource roles | **Option (i).** Not Nathan's now; it becomes his before the production application is configured |
| 5 Economics disposition | **Approved,** with one wording nit on "within 7%" |
| 6 Close-out decisions | (a) agree; (b) agree, with a timing note; (c) agree, it is Nathan's |
| 7 Start prompt | Verbatim in the appendix |
| 8 Notion | Matches `89a8d01`, apart from two stale texts (finding 8) |

## 3. Findings

### Item 1 — The governing Markdown

| File | What changed, and what it applies | Verdict |
|---|---|---|
| `AGENTS.md` | Notion's role (OD-26, OD-27); the successor exception (OD-31); the read "at a named commit" (G2) | **Approved** |
| `CLAUDE.md` | The OD-31 successor path in the manager lines | **Approved,** with the one line in finding 1.1 |
| PF00 1.9 | Notion as a matching copy, with the repository winning (OD-26, OD-27); E4 | **Approved.** *Consider:* its sentence "Nathan reinitiates managers manually" could add "or directs a manager to create its successor (OD-31)", as `AGENTS.md` now does |
| PF01 1.10 | OD-16 to OD-19, OD-22, OD-23, OD-26 and OD-27 in §1, §4, §6, §7, D04 and §10 | **Approved with conditions:** finding 1.2 |
| Manager workflow | See the list below | **Approved** |
| Dev Manager charter | G1 (the read rests on OD-15); G2 (a read covers one commit); OD-25 (the relay); the continuity rule; OD-26 and OD-27 (Notion) | **Approved with conditions:** finding 1.1 |
| CI and branch policy | The fifth job and the job counts (DM-05 4 (c)); OD-24's controls and substitutes; OD-20 (no Stream secret in CI); OD-21; G2 in the pre-merge list | **Approved.** "Revisit at P09 at the latest" is already in the register's OD-24 row, so it is not new |

The manager workflow's changes each apply a recorded source:

- OD-32, OD-31 and the handover checklist;
- OD-29;
- OD-21;
- OD-25;
- OD-33 and OD-34 in step 3;
- AM3-19 in the prompt step;
- the supersession sweep (AM3-08, AM3-10);
- G2's item in the pre-merge checklist;
- AM5-01, full SHAs for the classifier;
- AM5-02 and AM5-03, the Notion status item;
- AM5-07, the link query, which reads every property.

**No change adds a rule Nathan did not direct.** The workflow's checklist items are the manager's own preventions, which OD-11 and OD-27 make its responsibility. Each one cites its mistake entry.

#### 1.1 The Dev Manager succession is practised but not recorded as a rule — *before PR27 merges*

The records give three statements:

- the charter's "Session lifecycle": "The primary manager creates the session with the remote-session tools… If it has ended, the primary manager starts a new one from the start prompt";
- `CLAUDE.md`: the Dev Manager is "created by the manager from the Dev Manager start prompt";
- the charter's boundary: the Dev Manager never commissions sessions.

On 28 September, Dev Manager 1 created Dev Manager 2 at Nathan's direction: *"Create a successor for this session with as much context as you can preserve. It will be Glow Dev Manager 2."* The review log's Sessions table calls this "the OD-31 pattern". The handoff, Implementation Control and D10 record the fact.

The register has no row for it, and OD-31's words are about App Manager 4. So the governing text PR27 would merge says the opposite of the practice it records. It also says nothing on what the successor inherits or on when the predecessor stops pushing.

**Condition.** Record it like OD-31:

1. **A register row,** OD-35, with Nathan's words above, verbatim, taken from Dev Manager 1's handover or the start prompt in the appendix. Its state: "In force. At Nathan's direction, the outgoing Dev Manager runs its handover and creates its successor with the remote-session tools. This is the only session a Dev Manager creates. The successor continues `claude/dev-manager` and the review log; the predecessor pushes nothing after its handover commit."
2. **The charter's "Session lifecycle":** one line citing OD-35. The boundary gets an exception naming OD-35.
3. **`CLAUDE.md`:** "created by the manager from the Dev Manager start prompt, or by its predecessor at Nathan's direction (OD-35)".
4. **Notion:** the register copy, and D10's *Next Action*.

A revision that applies these as written needs no further read (G2). If the manager words the rule differently, I read that commit.

#### 1.2 PF01 — one stale sentence, and one nit — *before PR27 merges* (the first); *consider* (the second)

- **§7, line 236:** "…the app never displays chat-provider user or member data ([ADR 0003]…; conditional on the exact-head review confirming S15…". S15 was confirmed on 25 September; OD-14's row and ADR 0003 say so, and the display rule stands. The supersession sweep should have caught this sentence. **Condition:** replace the parenthesis with "confirmed live by the I1 review on 25 September 2026", or remove the clause.
- **§4's Operations row:** "never reads app or HDE tables". OD-19's words are "access app or HDE tables directly", and §1 says "touches". *Consider:* "never reads or writes app or HDE tables", so the row does not read as allowing writes.

#### ADR 0003 — approved

The conditions' statuses match what the reviews confirmed, and condition (c) as corrected at `438d047` is accurate: the other roles' and settings' comparison exists in code and has not run live. The "Revisit when" additions each have a trigger a later session can check. Only Nathan adds an exception, which keeps OD-16.

### Item 2 — The HDE contract request: approved

- **D08:** consistent. The request sits wholly on the app's side:
  - HDE's own process produces the contract, and HDE governs its text;
  - the app records a receipt and acts only within the access the receipt names;
  - "not supported" is a complete answer;
  - the access is recorded by name only, with the credential delivered outside the repository.

  Nothing in it asks an app session to read, call or change HDE.
- **OD-23:** consistent. It covers:
  - the three roles, all Nathan's;
  - Nathan setting the date in HDE's own process;
  - the supported interface, release or environment, and the authorized access (sections 2, 5 and 6);
  - the versioned contract.
- **Complete enough** for Nathan to take into HDE's process.

**Soon (before the receipt is written):** OD-23 asks for *"the contract recorded in repository Markdown"*. Section 4 step 4 makes a verbatim copy optional ("If a verbatim copy is wanted"), and the receipt cites answers "by their place in HDE's text". An app session may not be able to open HDE's text at all, so a citation it cannot follow does not record the contract. Make the non-governing copy under `docs/planning/sources/` the default. If HDE's process forbids a copy, the receipt pins the exact HDE commit and path of each cited passage instead.

### Item 3 — ADR 0004's accepted restore risk: confirmed

The risk runs one way in the ADR: a platform restore of the shared service restores HDE and the app together, and an app-only incident must not use one without reviewing its effect on HDE. OD-18 accepts the shared service with a move-out path, and ADR 0004 keeps DB13's restore proof logical. The acceptance is within Nathan's direction, so it is not his to decide again (OD-32).

**Soon (before P11's runbooks; add to ADR 0004's consequences):** the other direction.

- **The risk:** a platform restore made for an HDE incident also rolls the app back, including its safety state (blocks, reports, moderation actions, deletions) and its chat entitlements, while Stream keeps its own state.
- **The consequence:** any restore of the shared service, whoever starts it, triggers the app's post-restore procedure before the app reopens. That procedure replays deletions and tombstones, reconciles safety state with Stream, and re-checks entitlements. HDE's own runbook, in HDE's process, should name that trigger.

This changes nothing now, and nothing for Nathan.

### Item 4 — The live read and the open Video and Feeds items

**(a) Option (i), no live read in P06.1.**

- No recorded verdict rests on the other roles or settings.
- Every lockdown body named only client roles.
- A read now would add a Stream session, a prompt and a read before merge, for evidence P06.2's first live use produces anyway.

**Condition** for the P06.2 brief: the harness's first live use in P06.2 runs `products.verify` (the full comparison C4 added) before any other live command. Its result closes ADR 0003 condition (c) and the architecture document's §5 caveat, or stops P06.2 if it differs. This is technical sequencing, not Nathan's to decide.

**(b) Option (i), leave both open and recorded.**

- The design constraint (the server creates no call, feed or activity for a user) closes both paths.
- The harness preflight refuses unowned calls, feeds and activities, so a breach of the constraint in a proof run is detected.
- Asking Stream (ii) is optional and harmless, but nothing waits on it. A live test (iii) proves nothing Glow relies on.

This is **not Nathan's now.** It becomes his before the production application is configured (P09 or P11): whether production relies on the design constraint alone, or also closes these paths in configuration. Configuration here means emptying `call_member` and the feed-creator grants, or disabling Video and Feeds if Stream allows it. The architecture document already names emptying `call_member` as his decision. The P06.2 brief should carry that question forward in OD-32's form.

### Item 5 — The economics disposition: approved

- **Revision 2 needed no read.** I compared it with revision 1: it applies DM-06 findings 1 to 3, 4 (a) and (b) and 5 (a) to (c) as written. The header's later "Result" and "Nathan's pick" lines change no rule.
- **5 (d): confirmed**, with a wording nit.
  - The ledgers total 2,261 calls.
  - If the Chat count includes I2b's Video and Feeds requests, the sessions' share of Stream's count is 2,252 and the ledgers are 9 higher. If it excludes them, Stream counted up to 162 more than the ledgers: 7.2% of the ledgers, or 6.7% of Stream's total.
  - "Within 7%" should read "within about 7%" or "at most 162 calls (about 7%)" in the brief, the evidence record and Notion. Either way the difference is immaterial: about 0.1% of the plan.
  - The stored-data comparison could not be made, because the dashboard shows "—". I2b's last `verify-clean` stands as the evidence.
- **5 (e): confirmed.**
  - The pages read show no attribution requirement (terms section 3, quoted), no excluded kind of app and no production-use restriction.
  - The disposition says what was not read: the data-processing addendum's PDF and the Trust Center.
  - Nothing goes to Nathan under 5 (e).
- **Section 6.2** (the customer's access and moderation duty): **not Nathan's now; P07 (A05)**, as recorded. Glow meets it with its own terms and moderation, which P07 plans anyway, and Nathan's one-operator constraint (OD-23) is already in A05. Before the P07 brief relies on it, the clause is read in Stream's exact words.
- **Section 12.5** (Stream may show the customer's name and logo): **not Nathan's now; at A04,** the billing and launch decision, where it goes to him in OD-32's form if it survives an exact reading.
  - It concerns Stream's marketing, not anything inside the app. Nathan's principle is about users seeing nothing outside Glow, and whether a provider's client list breaks it is his call.
  - Nothing is public yet, and a free development account is not a listed customer.
  - **Before A04,** the exact text of 12.5 is read, including whether it allows opting out by written notice. If it does, the A04 item gives Nathan that option. Until then it stays on A04's row, as Notion already has it.
- **PF01 left unchanged: agree.** My DM-06 documentation list made a PF01 change conditional on a finding that would change a rule, and none did. PF01 changes only when a rule does (DM-01 P3). The evidence record, the brief and Notion's A04 and A05 rows are the right homes for facts.
- **The quote deviation: enough to record the facts, not to decide on them.**
  - The report names every page, and each fact is marked account-specific or general policy.
  - The manager's rule stands: before a decision rests on Stream's exact words, that page is read again. This covers terms 4.5, 4.6, 6.2 and 12.5, the Fair Usage rates, the Maker criteria and the data-processing addendum.
  - I would add one point. For A05, the addendum's PDF and the Trust Center are unread, so the transfer mechanism and the hosting regions stay "unverified" until a later read. That read is under a Dev Manager-approved prompt if it acts in Nathan's signed-in browser; for public pages only, the manager can read them.
- **The two unfocused typing actions and the account menu:** accepted as disclosed. A future prompt's "type only once the search box has focus" is right.

### Item 6 — Nathan's close-out decisions

- **(a) The lockdown stays: agree.**
  - P06.2 builds on the locked configuration, and every run since I2b has verified it.
  - Restoring would reopen what the proof closed.
  - There is no products restore command, so a restore would itself need new code, a prompt and a read.

  This is Nathan's decision, as the brief says.
- **(b) The Stream secret: agree it is replaced; my view on timing differs slightly.**
  - OD-28 already directs the replacement at P06.1's close, so this is an action for Nathan, not a new decision.
  - It has no dependency on the merge: nothing needs the secret until P06.2's first live session, because item 4 (a) recommends no live read.
  - Replacing it as soon as Nathan can shortens the time three containers hold a live secret: App Manager 3's, Dev Manager 1's and mine.
  - The new value goes nowhere until the next session that calls Stream, and then only where 6 (c) settles.
  - Put (b) and (c) to him together.
- **(c) The environments: agree it is Nathan's to decide.**
  - My container shows the `Glow app` environment held all three variables at 16:16 UTC on 28 September, a day after I2b, the last session that called Stream. So either OD-28's "then deletes them" was not done after I2b, or Nathan's practice changed when he created `Glow App - No Stream` on 26 September. The records cannot tell which.
  - The two practices:
    - **one environment,** adding and removing the variables per session (OD-28);
    - **two environments:** the No Stream environment for managers, the Dev Manager and offline sessions, and `Glow app` holding the variables permanently, only for sessions that call Stream.
  - Either works if every prompt names the environment to start in.
  - **Recommendation:** two environments, because the add-and-remove step has already slipped once and a fixed split does not depend on Nathan remembering it.
  - Whichever he picks goes in a new register row that supersedes OD-28's mechanism (OD-28 itself stays for the variables' names and CI), with the environment inventory and the start prompts updated.
  - Future Dev Manager sessions should start in the environment without the variables.

### Item 7 — The start prompt

The text Dev Manager 1 sent as this session's first message is in the appendix, verbatim as it reached me. It is not in the repository. It contains Dev Manager 1's session ID with a typo, "345kmfmsSWv"; the correct ID is `session_01MrcrmqtuENZ345mKfmsSWv` (my start note).

For the rewrite of `docs/planning/start-prompts/dev-manager.md` (DM-03 E3), keep:

- the scope boundary list;
- the names-only environment line;
- the start gate with a "this commit or later" check;
- the reading order;
- the working method.

Parameterize:

- the session number;
- the predecessor and its handover path;
- the manager branch;
- the expected commit.

Add the environment to start in, which depends on 6 (c), and OD-35's succession line.

### 8. Notion — matches `89a8d01`, apart from two stale texts

The following match the repository at `89a8d01`:

- *Implementation Control:* the current status, the operating procedure (AM5-07's link query included) and the Dev Manager line;
- *Dev Manager — reviews and approvals:* the Sessions table with both Dev Managers, and DM-06's disposition, with DM-07 pending;
- the register copy: the repository register has not changed since `70a55c9`, the commit it was matched to;
- the rows P06.1, A08, A04 and A05, including the economics facts on A04 and A05;
- D10's two links, now on `claude/magical-wozniak-yfmmx2` and PR27;
- the uses-table rows: revision 2's reading matches the prompt header (score 1.33, the six rung probabilities and the model probabilities), with Nathan's pick "pending", and revision 1's is marked superseded.

The mismatches:

- **M03's *Next Action*** still says "The Dev Manager's ten questions are with Nathan." Nathan answered on 25 September, and questions 2 and 3 of DM-01 were not among his answers (DM-04 finding 12; the Dev Manager page says so). *Correct in the next records batch.*
- **D10's *Next Action*** says "the primary manager creates and consults the Dev Manager session", which is the same gap as finding 1.1. *Update with OD-35.*
- **For information, no action:** P06.1, A08, A04 and A05 take their *Plan Reference* from PF01 on `main`, which is still 1.8 until PR27 merges. After the merge those links are current.

## 4. Verdicts

| Item | Verdict |
|---|---|
| 1 `AGENTS.md` | Approved |
| 1 `CLAUDE.md` | Approved (one line under 1.1) |
| 1 PF00 1.9 | Approved |
| 1 PF01 1.10 | Approved with conditions (1.2, §7's sentence) |
| 1 Manager workflow | Approved |
| 1 Dev Manager charter | Approved with conditions (1.1) |
| 1 CI and branch policy | Approved |
| 1 ADR 0003 | Approved |
| 2 HDE contract request | Approved |
| 3 ADR 0004's restore risk | Confirmed |
| 4 (a) | Option (i), with the P06.2 condition |
| 4 (b) | Option (i) |
| 5 Economics disposition | Approved |
| 6 (a), (b), (c) | Agree; (b) timing as above; (c) recommend two environments |

**A revision that applies findings 1.1 and 1.2 as written needs no further read** (G2). Any other change to the seven files would need one.

## 5. Questions for Nathan

Only item 6, which the manager puts to him in one message (OD-32).

- **(a) Keep the lockdown.** It is his decision; the manager and I both recommend keeping it.
- **(b) Replace the development Stream secret.** OD-28 already directs this, so it is an action, not a decision; I recommend doing it as soon as he can.
- **(c) Which environment practice he intends.** I recommend two environments.

Items 4 (b), 6.2 and 12.5 come to him later, at the points named above, not now.

## 6. Documentation to update

- **Before PR27 merges:**
  - the register (OD-35), the charter, `CLAUDE.md` and PF01 §7 (findings 1.1 and 1.2);
  - "within about 7%" in the brief, the evidence record and Notion's P06.1 row;
  - Notion: the register copy, and the D10 and M03 texts.
- **After Nathan answers item 6:**
  - a register row for the environment practice;
  - the environment inventory, and its "Dedicated environment rule";
  - the brief's paragraph on the Stream secret.
- **Before the next Dev Manager session:** the start prompt's rewrite, from the appendix.
- **Soon:** HDE contract request section 4 step 4 (item 2); ADR 0004's consequences (item 3); the P06.2 brief's first live step and its production-configuration question (item 4).
- **The review log:** DM-07's disposition.

## 7. Limits

- **No call to Stream.** Every Stream fact here rests on the recorded reports. I read none of Stream's pages.
- **HDE:** not read, by design. Item 2 is judged against D08 and OD-23 only.
- **Not run:** the harness's offline checks. `proofs/stream-chat/` has not changed since the C5-reviewed head apart from the README line DM-06 noted, and no item here rests on its code.
- **Environments:** what I say of `Glow App - No Stream` rests on the environment inventory and the consultation. I did not list Nathan's environments.
- **The start prompt:** reproduced from this session's first message, which reached me as a notification. It is not a repository file, so no hash pins it.
- **No scoring** (OD-15).

## 8. Relay message for Nathan to paste into App Manager 5's session

> **From Dev Manager 2 to App Manager 5 (relayed by Nathan, 29 September 2026)**
>
> DM-07 is answered on `claude/dev-manager`, in the commit that adds `docs/continuity/dev-manager/reviews/2026-09-29-dm-07-p06-1-close-out-read.md`. My read covers `89a8d01`.
>
> **1. Governing Markdown: approved with conditions.** No change adds a rule Nathan did not direct. Five files are approved outright. Two conditions before PR27 merges; a revision that applies them as written needs no further read:
> - **1.1 Dev Manager succession.** The charter and `CLAUDE.md` still say only the primary manager creates the Dev Manager, but Dev Manager 1 created me at Nathan's direction. Add an OD-35 register row with his words (in my report's appendix), a line in the charter's "Session lifecycle" and an exception in its boundary, one clause in `CLAUDE.md`, and the Notion register copy and D10.
> - **1.2 PF01 §7 (line 236)** still calls the display rule "conditional on the exact-head review confirming S15"; S15 was confirmed on 25 September. Fix the clause. *Consider:* §4's WordPress row "never reads or writes".
>
> ADR 0003 is approved.
>
> **2. HDE contract request: approved.** Soon: make the non-governing verbatim copy the default; a pinned HDE commit and path if HDE's process forbids a copy (OD-23).
>
> **3. ADR 0004: confirmed.** Soon, before P11's runbooks: add the other direction. A restore made for HDE rolls the app back too, so any shared-service restore triggers the app's post-restore procedure before it reopens.
>
> **4. (a) Option (i),** with the condition that P06.2's first live step runs the full `products.verify`. **(b) Option (i).** Neither is Nathan's now. (b) becomes his before the production application is configured.
>
> **5. Economics: approved.** Change "within 7%" to "within about 7%": 162 is 7.2% of the ledgers. Section 6.2 goes to P07 and 12.5 to A04, each read in exact words first; neither is Nathan's now. PF01 stays unchanged: agree. The paraphrase is enough for the record, not for decisions. The addendum PDF and the Trust Center stay unverified for A05.
>
> **6.** (a) Agree: the lockdown stays. (b) Agree; OD-28 already directs it, and it need not wait for the merge. Replace the secret as soon as Nathan can, and put (b) with (c). (c) Agree it is Nathan's. I recommend two environments, because `Glow app` still held the variables a day after I2b. Record his answer in a new register row.
>
> **7.** The start prompt is verbatim in the report's appendix.
>
> **8. Notion** matches `89a8d01`, apart from M03's "ten questions are with Nathan" and D10's creation wording (1.1).
>
> Questions for Nathan: only item 6, in your one message.

## Appendix — the Dev Manager 2 start prompt, verbatim

This is the first message of this session, as Dev Manager 1 sent it on 28 September 2026. It reached me in a system-notification wrapper. The text is unchanged, including the typo in Dev Manager 1's session ID ("345kmfmsSWv"; correct: "345mKfmsSWv").

````text
You are **Glow Dev Manager 2**, the second Dev Manager session for the Glow dating app, private repository `amthorn78/glow-dating-app`. Nathan Amthor, the product owner, established the Dev Manager role on 25 September 2026 (owner direction OD-15, PF01 D10). Dev Manager 1 (`session_01MrcrmqtuENZ345kmfmsSWv`, branch `claude/dev-manager`) created this session on 28 September 2026 at Nathan's direction: *"Create a successor for this session with as much context as you can preserve. It will be Glow Dev Manager 2."* You continue its role, its branch and its review log.

**The role.** You are a second layer of oversight, not an implementer. You review, challenge and approve consequential architectural, implementation, workflow and process decisions; you read governing Markdown and every prompt that authorizes credential use or live provider actions before it takes effect; and you watch the documentation chain. Follow `docs/planning/dev-manager.md` (the charter) and the rules in `docs/continuity/owner-directions.md`.

**Your boundary is scope:**
- write only report files under `docs/continuity/dev-manager/reviews/`, each ending with the line `Status: complete`;
- push only the branch `claude/dev-manager`; commit nothing else;
- never implement, commission or run other sessions, open or merge PRs, or edit Notion (read it in every consultation and report mismatches; the repository wins, OD-27);
- never call Stream or any other provider, a database, HDE or Railway; never run `playwright install`, `eas` or `migrate`; do not call the TypeSafe API (the Dev Manager has no scoring, OD-15).

**Relay.** Nathan carries messages between you and the primary manager by hand (OD-25). Consultations arrive as pasted messages with an ID (DM-06 onward), an exact commit and what is asked. Every answer is a report file on `claude/dev-manager`, and your chat reply ends with a paste-ready relay message for Nathan naming the file and the branch commit. Verdicts: `approved`, `approved with conditions`, `changes requested` or `refer to Nathan`. Nathan may also answer you or give directions directly in this session: record his words verbatim in a report file and give him a relay message; never rely on chat alone.

**Environment (names only; never print values).** Run `for n in DATABASE_URL HD_API_KEY GEO_API_KEY STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done`. No HDE variable may be present; if one is, say so and run commands only in a clean process environment. If any `STREAM_*` name is present, record "present, never read or used" (the environment holds them only for sessions that call Stream, OD-28; a container keeps what it started with). Never dump the environment.

**Start gate:**
```bash
git fetch origin main claude/stoic-carson-66gdig claude/dev-manager
git switch claude/dev-manager 2>/dev/null || git switch -c claude/dev-manager origin/claude/dev-manager
git rev-parse HEAD      # must print 3ec0fac739d9f4dfee4213596a2099948bc7490a or a later commit of that branch
```

**Read, completely, in this order:**
1. `docs/continuity/dev-manager/reviews/2026-09-28-dev-manager-1-handover.md` — Dev Manager 1's handover: the binding rules beyond the charter, what it did, where P06.1 stands, its own corrections, and its working method for prompt reads and governing reads. Follow that method.
2. root `AGENTS.md` and `CLAUDE.md`; `docs/planning/dev-manager.md`; `docs/continuity/dev-manager/README.md` (the review log, with every disposition).
3. `docs/continuity/owner-directions.md` (OD-01 onward), `docs/continuity/current-handoff.md`, `docs/continuity/manager-mistakes.md`, `docs/planning/manager-workflow.md`, `docs/operations/ci-and-branch-policy.md`.
4. Dev Manager 1's reports in `docs/continuity/dev-manager/reviews/`: DM-01 to DM-05 and the owner-answer files.
5. `docs/pf-canon/GAPP-PF00-Canon-Index-and-Authority.md` and `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md`; `docs/planning/p06-1-chat-provider-proof.md`; the evidence record `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md` (skim the run tables; read every "Manager verification", "Exact-head review" and "Disposition"); `docs/architecture/chat-provider-permissions.md`; `docs/adr/0003-chat-display-rule.md` and `docs/adr/0004-app-database-placement.md`.

Read from the most current record: the manager branch (`claude/stoic-carson-66gdig` at `2a86c8e` when this prompt was written; App Manager 5 may have moved to a new branch and a replacement PR, so check open PRs and the handoff) is more current than `main`. Then read the Notion pages the handover names (Implementation Control, "Dev Manager — reviews and approvals", the owner-direction register copy, the Work Register rows for P06.1 and A08), read-only, using ToolSearch to load the Notion tools.

**Your first deliverable:** a start note, `docs/continuity/dev-manager/reviews/2026-09-28-dev-manager-2-start.md`, with: your session identity (`get_session` with no argument gives it) and the commit you started from; the environment check by name; what you read; the state of the manager branch, open PRs and the review log as you found them; any mismatch between the repository and Notion; anything in the handover you could not confirm; and a paste-ready relay message telling App Manager 5 your session ID, that DM-06 onward comes to you, and asking it to add you to the review log's Sessions table. End with `Status: complete`. Commit only that file with the message "Dev Manager 2: start note", push `claude/dev-manager` (retry up to four times with backoff on a network error), and give Nathan the commit hash and the relay message in chat.

Then wait. Answer each consultation as the handover's method describes: pin the commit or blob you read, verify the harness against its last reviewed head, run the offline checks in your scratchpad under `env -i`, read the code the prompt relies on and the SDK for the facts it asserts, read Notion, write the report in the fixed format, push, relay. Keep your independence: challenge the primary manager's framing when it is wrong, say when a question is Nathan's to decide, and put nothing to Nathan he has not been given the means to act on (OD-32).
````

Status: complete
