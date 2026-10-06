# DM-14 — PR29's governing changes since DM-13, and Stage A's exact-head review dispositions

- **Consultation:** DM-14, revision 1, from App Manager 6, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, branch `claude/dev-manager` (at `80ce6c6` before this report).
- **Commit read:** `da9fac6a13a815eb08e3c3cd9e71b9e1e626e19b`, the head of `claude/magical-wozniak-yfmmx2` (PR29) when I fetched it. **This read covers `da9fac6`** (DM-03 G2).
- **Environment (names only):** `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are present, never read or used. No HDE name is present. I called no provider, database, HDE or Railway.

## 1. What I read

**At `da9fac6`:**

- the governing diff `a8db520..da9fac6`, which holds exactly the two changes named: step 3's OD-40 sentence and step 5's AM6-01 bullet;
- OD-40 in the register, and AM6-01 in the mistakes log, in full;
- the evidence record's "Exact-head review of Stage A", whole: findings F1 to F5, dispositions, the incident and the manager's verification;
- the brief's "Carried to Stage B and P11";
- the data model's token rules and its F1 gap paragraph, and the `session_epoch_bumped` row;
- `services/api/glow_domain/chat_tokens.py`'s `grant_chat_token`;
- `services/api/glow_chat/delivery.py` around line 240, where the cut-off is taken.

**Notion, read-only, 6 October:**

- *Implementation Control*: status and operating procedure;
- the Work Register's P06.2 row;
- the register copy;
- *Dev Manager — reviews and approvals*.

## 2. Summary verdict

| Item | Verdict |
|---|---|
| 1 Step 3's OD-40 sentence | **Approved;** one *consider* addition |
| 2 Step 5's AM6-01 sentence | **Approved with a condition:** words that keep the manager's verification of a finished run |
| 3 F1, the token cut-off | **Disposition approved. Mechanism for Stage B:** the grant under the account row lock, as recommended, **plus** the token's issue time read from the database clock under that lock, and the cut-off rounded up to the second. The lock alone leaves a clock-skew window |
| 4 F3, dead letters | **Approved with a condition:** Stage B names the path, and also makes a dead-lettered revocation visible on the binding; reconciliation stays with P11 |
| 5 F2, F4, F5 | **Approved** |
| 6 Nothing else before Stage A merges | **Confirmed,** with item 2's words applied first |
| 7 Notion | **Matches `da9fac6`** |

No item is Nathan's.

## 3. Findings

### Item 1 — Step 3's OD-40 sentence: approved

It records Nathan's words ("We are not restricted to cloud sessions") as the register states them. It keeps the two rules that matter: the prompt names the environment, and the credential and connection rules are unchanged.

*Consider,* because a session outside the cloud, such as one on Nathan's own machine, can carry credentials no cloud environment would, append to the sentence:

> "; the prompt's names-only environment check runs there too, and the session stops if an HDE, database or production credential name is present."

That restates rules already in `AGENTS.md` and `CLAUDE.md` where a reader of step 3 needs them. It adds no new rule.

### Item 2 — Step 5's AM6-01 sentence: approved with a condition

The rule is right: a session's open run of record is the session's to finish (AM6-01; Nathan's own words).

As written, though, "it never subscribes to, watches or chases that run itself" can be read as forbidding what step 5 still requires of the manager. Once a session reports its run of record, the manager verifies the report against that run's logs. The Stage A verification did exactly that, reading the database job's 1,302-line log. The sentence should separate waiting on an open run, which is the session's, from reading a finished one, which is the manager's verification.

**Words** (replace the bullet):

> - **A session's run of record is the session's** (AM6-01). While it is open, the manager does not subscribe to, watch or chase it: when a report leaves it open, the manager gives Nathan a relay message for that session. Once the session reports it finished, the manager reads its logs to verify the report, as this step requires.

These words go into governing text before PR29 merges. Applied as written, they need no further read (G2).

### Item 3 — F1, the token revocation's cut-off: disposition approved; the mechanism

Accepting F1 as a records finding now is right: no endpoint signs a token yet. The data model's gap paragraph and the P11 plan record it. The mechanism belongs to Stage B's prompt, which signs, and to P11's endpoint.

**The manager's mechanism, the grant under the account row lock, is right but not sufficient on its own.**

- **What it fixes.** A grant racing an epoch bump either waits for the bump's commit and then refuses at the new epoch, or runs before the bump.
- **The window that remains, in the second case.** The grant issues a legitimate old-epoch token, and the bump follows. The token's issue time (`iat`) comes from `now`, which the caller passes to `grant_chat_token` from the app server's clock. The revocation's cut-off is `event.available_at`, from the database's `clock_timestamp()`. If the app server's clock runs ahead of the database's, a grant made just before the bump carries an `iat` after the cut-off. Stream then leaves it valid for up to an hour.

  So the manager's reason for preferring the lock, that the alternative "depends on the app server's and the database's clocks agreeing", applies to the lock too, unless both times come from one clock.

**The mechanism Stage B's prompt should require:**

1. **The grant runs in one transaction** that takes the account row with `SELECT … FOR SHARE`, then the session row (`FOR SHARE`), in the canonical order the send uses. It runs every check of `grant_chat_token` on those locked rows. A bump in flight holds `FOR UPDATE`, so the grant waits for it and then refuses at the new epoch.
2. **The token's issue time comes from the database clock under those locks.** `clock_timestamp()` is read inside the grant's transaction and passed as `now`. The signer sets the JWT's `iat` from the grant's issue time, never from the SDK's own clock. Issue time and cut-off then come from one clock: a grant that ran before the bump has an issue time before the bump's cut-off, which is read after the bump took its lock, so the revocation covers it.
3. **The cut-off is rounded up to the next whole second when it is sent to Stream.** A JWT's `iat` is in whole seconds. Rounding up ensures a token issued earlier in the same second is revoked. A new-epoch token issued in that same second after the commit is revoked too, and the client simply fetches another.
4. **The cut-off itself stays as it is:** the bump's pre-commit time, read after the account lock. With points 1 to 3, the alternative of a cut-off at or after the commit gains nothing.
5. **Tests, offline and in Stage A's suite style:**
   - a grant forced to wait on a bump that holds the lock, which refuses afterwards;
   - a grant that commits just before a bump, whose `iat` is before the cut-off;
   - each run with the app clock deliberately skewed ahead, to show that the app clock plays no part.

This keeps the design's rule that every check runs on locked rows. It takes the app server's clock out of the safety argument entirely, which P11's multi-server deployment will need anyway.

### Item 4 — F3, dead letters: approved with a condition

P11 owning dead-letter reconciliation is right. Naming the path before the adapter runs live is not quite enough. Today a dead-lettered `contact_revoked`, `access_revoked` or `session_epoch_bumped` marks nothing, so the app's own records keep saying the binding is `active` when the provider may still let both members read. A record that is wrong, rather than merely incomplete, should not reach a live provider.

**Condition for Stage B's prompt:**

- A dead-lettered revocation marks its binding (or, for an epoch bump, its chat identity) as needing reconciliation. `ChatBinding.state` already has `failed`; if the session uses it, it records why.
- The conformance run shows that state after an injected terminal failure, and its cleanup still removes the run's channels and users.
- The prompt names P11's reconciliation path, as the disposition says.

This is a small change in Stage B's owned paths. It does not build reconciliation.

### Item 5 — F2, F4 and F5: approved

None of the three opens a gap today:

- F2: no writer changes a match's pair or a session's account;
- F4: a wrong deadlock mapping surfaces as `error`, which the suite fails;
- F5: no caller self-blocks, and the constraint holds.

Carrying all three to the next code change to `glow_chat/contact.py`, each with its test, is right. Stage B is likely to touch that file for item 3's grant, so the prompt should list them there.

### Item 6 — Nothing else before Stage A merges: confirmed

Stage A may merge with these dispositions once all of these hold:

- item 2's words are applied (governing text, no further read);
- Codex's review is complete and its findings are verified and dispositioned;
- a run passes on the final head, with its gate printing `Application checks passed`;
- the pre-merge checklist is filled in, and step 7's branch-state report is made at the merge.

This read covers `da9fac6`. Any other change to a governing file before the merge needs a read.

**The review session's incident.** It wrote briefly into its own working tree, restored it from `HEAD` and pushed nothing. The manager checked the remote. No further action is needed. The prompt template's rule that a review runs reversals in a scratch copy, never the checkout, deserves a line in the next review prompt.

### Item 7 — Notion: matches `da9fac6`

- ***Implementation Control*'s status** is matched to `da9fac6`. Its operating-procedure copy is stamped `ec87eac`, noting that the workflow last changed at `d360a36`. Both `d360a36` and `8bbad57` precede `ec87eac`, and no governing file changed between `ec87eac` and `da9fac6`, so the stamp is accurate. The copy carries the AM6-01 and OD-40 bullets.
- **The Work Register's P06.2 row** ("In progress") matches the brief and the evidence: Stage A at `e8eb5d3`, run of record 37383940454, the review's approval, F1 to F5 carried, and "Next: DM-14".
- **The register copy** is matched to `8bbad57`. The repository's register has not changed since, and OD-40 matches.
- ***Dev Manager — reviews and approvals*** has DM-13's disposition (option (a) for 7.2, `getstream` 6.1.0 at Stage B), the recreated branch in my session row, and DM-14 "Pending".

## 4. Verdicts

| Item | Verdict |
|---|---|
| 1 | Approved; *consider* the appended clause |
| 2 | Approved with a condition: item 2's words |
| 3 | Disposition approved; Stage B requires points 1 to 5 |
| 4 | Approved with a condition: mark a dead-lettered revocation |
| 5 | Approved |
| 6 | Confirmed, with item 2 applied |
| 7 | Notion matches `da9fac6` |

## 5. Questions for Nathan

None.

## 6. Documentation to update

- **Before Stage A merges:** the manager workflow's step 5 bullet (item 2), and step 3's clause if taken (item 1).
- **The brief's "Carried to Stage B and P11":** F1's mechanism (item 3, points 1 to 5), F3's marking (item 4), and F2, F4 and F5 with the grant's change.
- **The data model's F1 paragraph:** the mechanism chosen, once Stage B lands it.
- **The review log:** DM-14's disposition.

## 7. Limits

- **Stream's behavior, not checked live:** that Stream compares a token's `iat` with the per-user revocation time, at whole-second resolution, is taken from its documented behavior and the architecture document. Stage B's conformance run should show it.
- **Codex's review** had not run when I read. Item 6 is conditional on it.
- **No scoring** (OD-15).

## 8. Relay message for Nathan to paste into App Manager 6's session

> **From Dev Manager 2 to App Manager 6 (relayed by Nathan, 6 October 2026)**
>
> DM-14 is answered on `claude/dev-manager`, in the commit that adds `docs/continuity/dev-manager/reviews/2026-10-06-dm-14-p06-2-stage-a-governing-read.md`. My read covers `da9fac6`. No item is Nathan's.
>
> **1. Step 3's OD-40 sentence: approved.** Consider appending: "; the prompt's names-only environment check runs there too, and the session stops if an HDE, database or production credential name is present."
>
> **2. Step 5's AM6-01 sentence: approved with a condition.** As written it can be read to forbid verifying a finished run. Replace the bullet with:
>
> "- **A session's run of record is the session's** (AM6-01). While it is open, the manager does not subscribe to, watch or chase it: when a report leaves it open, the manager gives Nathan a relay message for that session. Once the session reports it finished, the manager reads its logs to verify the report, as this step requires."
>
> Applied as written, it needs no further read.
>
> **3. F1: disposition approved. Stage B's prompt requires:**
> 1. The grant in one transaction: account `FOR SHARE`, then session `FOR SHARE`, every check on those locked rows.
> 2. The token's issue time is `clock_timestamp()` read under those locks, passed as `now`; the signer sets `iat` from it, never from the SDK's clock.
> 3. The cut-off is rounded up to the next whole second when sent to Stream.
> 4. The cut-off stays the bump's pre-commit time.
> 5. Tests: a grant waiting on a bump refuses after it; a grant just before a bump has `iat` before the cut-off; both with the app clock skewed ahead.
>
> Why: the lock alone still leaves a window. A grant just before a bump, with the app server's clock ahead of the database's, gets an `iat` after the cut-off and survives the revocation.
>
> **4. F3: approved with a condition.** Before the adapter runs live, a dead-lettered revocation also marks its binding (or, for an epoch bump, its identity) as needing reconciliation, for example `failed` with the reason, shown in the conformance run. The prompt names P11's path. Reconciliation itself stays with P11.
>
> **5. F2, F4, F5: approved;** list them in Stage B's prompt, since the grant change touches `contact.py`.
>
> **6. Confirmed:** Stage A may merge once item 2's words are applied, Codex's findings are verified and dispositioned, the final head's run passes, and the checklist and branch-state report are done. Suggest a line in the next review prompt: reversals in a scratch copy, never the checkout.
>
> **7. Notion** matches `da9fac6`.

Status: complete
