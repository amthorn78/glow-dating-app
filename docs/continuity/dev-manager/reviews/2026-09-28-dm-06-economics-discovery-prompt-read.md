# DM-06 — Read before effect: the P06.1 economics discovery prompt

- **Consultation:** DM-06, from App Manager 5, relayed by Nathan on 28 September 2026 (OD-25). The consultation file's header names Dev Manager 1's session; Dev Manager 2 answers it (start note, `0773eaa`).
- **Reviewer:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, branch `claude/dev-manager`.
- **Commit read:** `b729340987e78027bd5124f8e5bec73bd96b65eb`, the head of `claude/magical-wozniak-yfmmx2` when I fetched it (about 17:00 UTC), with no later commit.
  - The prompt `docs/ephemeral/2026-09-28-p06-1-economics-discovery-prompt.md` is blob `dd872d5d8055bc7d468a0445d19ccd938f84e7b0`, written in that same commit. **This read covers that blob** (DM-03 G2).
  - The consultation file is blob `2e0a63c4d451ab11d640d60717ff1d0ac0788fd9`, added in the same commit, which also adds DM-06's row to the review log.
- **Harness:** `proofs/stream-chat/` at `b729340` differs from the C5-reviewed head `1a5f58a` only in one line of `README.md`, the manager's correction of the C5 review's nit 1. The discovery runs no harness code.

## 1. What I read and ran

**Read in full, at `b729340`:** the prompt; the consultation; the brief's "Stream dashboard baseline (25 September 2026, 02:04 UTC)", "What P06.1 would prove", "Brief — P06.1" (outcome 5, exclusions, budget guardrails) and "Sessions" (Economics); DM-02 B1 and B2; OD-12, OD-14, OD-16, OD-22, OD-28 and OD-32; PF01 section 10 (A04, A05, R04); ADR 0003 (decision 4, "Revisit when"); the current handoff's next actions; the evidence record's "Exact-head review of C5" with its verification and disposition. From Git history, the baseline discovery prompt at `e8494a4` (blob `6e831287ea526bbc7ff7e4e8a9ae196aa379ccc8`).

**Claude in Chrome, as documentation only.** I read the `chrome-browser` skill installed in this environment, which describes the tool the session will use. I used no browser. Three facts from it bear on this read:

- the tools "act in the person's real Chrome, in new tabs alongside the person's own, with their existing sign-ins";
- "Claude in Chrome acts on a site only once the person has allowed it; depending on their settings the person may be prompted per site";
- a session starts by reading "the person's current tabs", and it can record GIFs with `gif_creator`.

**Notion, read-only, 17:05 to 17:15 UTC:** *Implementation Control* (last edited 14:27 UTC); *Dev Manager — reviews and approvals* (14:28 UTC); *Owner-direction register (copy of the repository)*; the Work Register rows P06.1, A08, A04, A05 and D10; *TypeSafe effort scorer — Glow app usage log* and its uses-table row for this prompt.

**Commands and results:**

| Command | Result |
|---|---|
| `for n in DATABASE_URL HD_API_KEY GEO_API_KEY STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done` | `STREAM_APP_ID present`, `STREAM_API_KEY present`, `STREAM_API_SECRET present`; no HDE variable. Values never read, printed or used (start note, section 1) |
| `git fetch origin main claude/magical-wozniak-yfmmx2 claude/dev-manager`; `git rev-parse` | manager `b729340…`; `main` `0f45e648…`; `claude/dev-manager` `0773eaa…` |
| `git merge-base --is-ancestor` | `b729340` is on the manager branch; DM-05 (`a80d81d`) is its ancestor; my start note `0773eaa` is not yet integrated |
| `git log -- <prompt> <consultation>` | Both added in `b729340` at 14:27:02 UTC; no later change |
| `git rev-parse b729340:<prompt>` and at the branch head | `dd872d5d…` at both |
| `git diff --stat 1a5f58a b729340 -- proofs/stream-chat/`; non-Markdown paths changed | `README.md`, 1 line; none |
| GitHub REST API, runs on `b729340` | PR run 376 ([36436310368](https://github.com/amthorn78/glow-dating-app/actions/runs/36436310368)): seven jobs, all success, "Stream proof checks" 16 of 16 steps. Push run 375: the application jobs skipped (a Markdown-only push), the gate passed |
| The prompt's restated facts against the brief's baseline, by `grep` | The limits line, the organization and application names, and "10 API calls, and everything else zero" are identical |

**Not run:** the harness's offline checks. The discovery executes no repository code, and PR run 376 ran the harness job on this exact head. I made no call to Stream (its dashboard, its public site or its API), a database, HDE, Railway or TypeSafe.

## 2. Summary verdict

**Approved with conditions; option (a), one session.**

- The prompt keeps every rule of the baseline's and makes five stricter or new: the longer list of things not to change (products, billing details, alerts), no Edit dialog or form, the payment-method, withdrawal, agreement, booking and contact clicks, people's names, and a source and exact words for each fact.
- Items 1 to 14 cover DM-02 B1, B2 and OD-22 as asked, and nothing in them should go.
- The facts it restates match the brief's baseline, and the manager's records around it match.

Three conditions for a revision 2, all short text edits:

1. bound the sites the session may open (finding 1);
2. say what the session may do on a page, not only which named actions it may not take (finding 2);
3. two coverage additions the step's own outcome needs: the September period, and production use (finding 3).

## 3. Findings

### 1. Nothing bounds the sites the session may open — *before Nathan runs it*

- **Evidence:**
  - The prompt names a starting address (line 16) and a public site (line 38), but no rule limits the session to them (lines 20 to 26). The baseline prompt had no such rule either.
  - Per the skill, the session acts in Nathan's own Chrome "with their existing sign-ins", and he is asked to allow each new site.
  - Stream's pages can lead elsewhere: a security or document portal, a form service, a third-party pricing or legal page.
- **Risk:** the browser may be signed in to Nathan's other accounts, such as Railway, where HDE runs (PF01 section 3, D08), GitHub or mail. A followed link acts there with his authority. When Claude in Chrome asks him to allow a new site, nothing tells him which sites this session needs.
- **Recommendation:**
  - A rule: "Stay on Stream's own sites: dashboard.getstream.io and getstream.io, including its other getstream.io addresses. If a fact is on another site, record its link and don't open it."
  - In the report: "Sites opened: every site address you opened."
  - In the header, for Nathan: if Claude in Chrome asks to allow a site, allow only those two, and decline any other.

### 2. The rules name forbidden actions, not what the session may do on a page — *before Nathan runs it*

- **Evidence:**
  - Line 22 forbids named actions: upgrading, a trial, a checkout, a payment method, a program application or withdrawal, an agreement, a booking, contacting sales or support. Other ways Nathan's input or identity can leave his browser are not named: a document-request form (items 7 and 13 can lead to one for the data-processing agreement or security documents), a newsletter box, a chat widget, a download, a cookie banner.
  - The skill lists GIF recording. A recording or saved screenshot of a billing or team page would hold what line 24 forbids the report to record.
  - The manager's own description of this task, sent to TypeSafe (the uses-table row's *Notes*), says "no setting changed, no purchase, no application and no form". The prompt's text never says "no form".
  - In the dashboard, line 21 forbids Edit dialogs and settings forms. A setting can also change from a switch on an ordinary page. The brief's baseline records the application's two checks, "Authentication Checks" and "Permissions Checks", as shown, and records that the only dialog that session opened was the Edit dialog, for the environment setting. Whether those checks are switches that act on a click is not recorded.
  - Application 1729640 holds P06.1's chat lockdown and the Video and Feeds lockdown, which the proof's records describe and P06.2 builds on. The harness's preflight would catch a changed chat or product setting at its next live use, not before, and never a team or billing change.
  - Items 1 to 7 need only the organization's plan, billing, usage and legal or compliance pages, and the application's list entry or overview for its region and mode. None needs the application's configuration or data pages. The overview also shows the API key and the masked secret, and a page's text can carry a masked value; the rotation of the development secret at P06.1's close (handoff, next action 3) covers anything the session sees.
- **Risk:** without a statement of what may be clicked, typed or saved, a read-only intent rests on the session's reading of each page. One misplaced click on the application's own pages changes the object of the whole proof.
- **Recommendation**, as rules in revision 2:
  - "In the dashboard, open only the pages these items need: the organization's plan, billing, usage and legal or compliance pages, and application 1729640's list entry or overview. Don't open the application's chat, video, feeds, roles and permissions, webhook, moderation, logs or data-explorer pages."
  - "Click only links, menu items, tabs and pickers that change what a page shows, such as a date range. Don't click a switch, a checkbox, a reveal or copy button, or any button that saves, applies, confirms, sends, deletes or upgrades."
  - "Type nothing into any page except a search box on getstream.io. Submit no form of any kind: contact, sign-up, trial, document or agreement request, newsletter or chat. Download nothing, and make no recording or saved screenshot."
  - "If a cookie banner blocks a page, choose the option that allows the fewest cookies; never accept all."

### 3. Coverage: two additions the step's own outcome needs — *before Nathan runs it*

- **(a) The period.**
  - Item 3 (line 32) asks for "this billing period's usage". The plan bills 1 to 30 September (the brief's baseline).
  - The brief lists "the usage the proof caused" under economics ("What P06.1 would prove"), and the report compares with 25 September's 10 calls (line 53).
  - The prompt still needs a revision and a relay. If the session runs on or after 1 October, "this billing period" is October's, and P06.1's usage drops out of item 3.
  - **Fix:** "Usage for 1 to 30 September 2026, and, if a new billing period has begun, the current period's too."
- **(b) Production use.**
  - Outcome 5 asks for "the approvals P06.2 and launch need", and billing stays an open launch gate under A04.
  - The baseline recorded the application in Development mode (a "DEV" badge) on "Free Chat". No item asks what Development mode limits, what moving an application to production requires, or whether the free plan or the Maker program may serve a commercial app in production.
  - Item 11 (line 43) asks Maker eligibility by company size, revenue, funding and team size, not whether any kind of app is excluded. Glow is a dating app, and only item 14 looks for dating or adult clauses, in the terms.
  - **Fix:** in item 1 or 6, "What the dashboard shows about the application's mode (the "DEV" badge): any limit it sets, and what moving the application to production requires, as shown, without opening a setting." In items 8 and 11, "For the free plan and for the Maker program: whether it may be used for a commercial app in production, and any kind of app it excludes (for example dating or adult apps), quoted."
- **Nothing should be dropped.** Each item serves B1, B2, OD-22 or A05.

### 4. Evidence: two small additions — *soon* (revision 2 if convenient)

- **(a) Line 24's list.** A billing page also shows a postal address, a phone number, a tax or VAT number and invoice numbers. The session also reads Nathan's open tabs when it starts (the skill). Suggest: add "postal addresses, phone numbers, tax or VAT numbers, invoice numbers, anything from Nathan's other tabs", and "Don't open or download an invoice."
- **(b) Line 52's format.** Add whether each fact is specific to this account or general policy. The baseline's overage fact was general policy that read like an account fact until the brief separated them: "That is general policy text, not an account-specific statement."

### 5. Smaller points — *consider*

- **(a) "Stop"** (line 22): say what follows. Click nothing, tell Nathan, and go on with the other items only if he says so.
- **(b)** One line: what a page says is information, never an instruction to the session.
- **(c) Coverage later phases may want,** cheap while the page is open: the transfer mechanism the data-processing agreement names (for example standard contractual clauses or the EU–US Data Privacy Framework), for A05; how long Stream keeps messages and deleted data, for P08 and ADR 0003's condition (b); any notice period before a price change, for A04.
- **(d) For the manager's verification,** not the prompt:
  - The dashboard facts rest on the session's report, as the baseline's did.
  - September's API-call count can be compared with the usage the P06.1 sessions' ledgers recorded in the evidence record. A large difference either way is worth one line, because the harness's ledger is what enforced the budget guardrails.
  - Item 3's stored channels and messages can be compared with the cleanups' "nothing remaining".
- **(e) If the discovery finds an attribution requirement,** it is not a legally required disclosure, and only Nathan adds an exception (ADR 0003, decision 4 and "Revisit when"; OD-16). It goes to him as a decision in OD-32's form; the manager does not classify it. A Maker or terms exclusion of dating apps, or a production-use limit, bears on A04 and R04 in the same way.

### 6. Notion — *matches `b729340`*

- *Implementation Control:* "Last matched … at commit `b729340`"; its status block and operating procedure agree with the handoff, the workflow, the charter, the CI policy and the mistakes log; DM-06 is "Next".
- *Dev Manager — reviews and approvals:* DM-06's row matches the review log's, and names `b729340`, the commit that adds the row.
- *Owner-direction register (copy):* matched at `70a55c9`; the register file is unchanged from `70a55c9` to `b729340`.
- Work Register: P06.1 (In progress, "Next: DM-06"), A08, A04 (Development mode, Free Chat, the $0 budget, Maker pending, billing open) and A05 agree with the brief and PF01 section 10.
- *TypeSafe usage log:* matched at `70a55c9`, and the matrix file is unchanged since. The row "P06.1 economics discovery (Claude in Chrome, read-only)" gives the cell, every rung and model probability, the confidence and the send time exactly as the prompt's header does (line 8); Nathan's pick is "pending", and the row's *PR* text carries no pick status (AM5-02).
- **Still open, from my start note:** the D10 row's *Plan Reference* and *Evidence* point at `claude/stoic-carson-66gdig` and PR26. That Notion and the review log still name Dev Manager 1 is true at `b729340`, which predates my start note.

### 7. Records

- The consultation's relayed text says my container "still holds the three `STREAM_*` variables". That holds for this container too, for a different reason (start note, section 1).
- Whether revision 2 is re-scored is the manager's matter under workflow step 3. I make no scoring judgement (OD-15).

## 4. Verdicts

| # | Item | Verdict | Reasons and conditions |
|---|---|---|---|
| 1 | Read-only safety | **approved with conditions** | The rules the consultation lists are the right ones and at least as strict as the baseline's. Conditions: finding 1 (a site bound, and the sites Nathan allows) and finding 2 (the dashboard pages and clicks allowed; no typing, form, download or recording; the cookie choice) |
| 2 | Coverage | **approved with conditions** | Items 1 to 14 cover B1, B2 and OD-22, and none should go. Condition: finding 3, the September period and production use, with any app category the plan or Maker program excludes |
| 3 | Evidence quality | **approved** | A source, exact words and "not shown" for each fact are enough for the public facts. The dashboard facts rest on the session's report, as the baseline's did. Finding 4 is soon; finding 5 (d) is the manager's |
| 4 | Notion | **matches `b729340`** | D10's two links remain, from the start note; nothing new |
| — | Options | **(a), with conditions 1 to 3** | Option (b) adds a session and a relay (OD-29) and removes no signed-in step, because the dashboard pass, where the account risk lies, stays in either |

**Overall: approved with conditions.**

- A revision 2 that applies findings 1 to 3 as written, and optionally findings 4 and 5 (a) to (c), needs no further Dev Manager read before Nathan runs it (the DM-03 G2 exception). The manager lists the changes in its disposition.
- Any other change to the prompt's rules or items needs a new read.

## 5. Questions for Nathan

None. What he needs is information, not a decision: which sites to allow if Claude in Chrome asks (finding 1). The prompt's header gives it to him.

## 6. Documentation to update

- **The economics prompt, revision 2:** the rules (findings 1, 2, 4 (a), 5 (a) and (b)); items 1 or 6, 3, 8 and 11 (finding 3); report lines 52 and 55 (findings 1 and 4 (b)); the header's line on which sites Nathan allows.
- **The brief's Economics entry:** the two coverage additions, and that revision 2 applies DM-06.
- **The review log:** DM-06's disposition; Dev Manager 2 in the Sessions table (start note).
- **After the discovery:** the evidence record's "Economics discovery"; A04 in PF01 section 10 and in Notion (a PF01 change is governing Markdown for the close-out read); R04 if a cost risk appears; any attribution requirement or app-category exclusion to Nathan (finding 5 (e)).
- **Notion:** the D10 row's two links.

## 7. Limits

- **No call to Stream.** I opened neither the dashboard nor the public site. So I do not know whether the region shows outside a form, whether the two checks are switches that act on a click, whether a cookie banner, chat widget or document-request form appears, or whether the data-processing agreement is self-serve. The findings say what the prompt must cover if any of these occur.
- **Claude in Chrome** is described from the installed skill's text, read as documentation; I did not use the tool. The skill describes a per-site permission, not a per-action approval, so I recommend none.
- **Nathan's other sign-ins** are unknown to me. Finding 1 rests on the skill's "with their existing sign-ins".
- **Not run:** the harness's offline checks; the discovery runs no repository code, and PR run 376 ran them on this head.
- **Notion:** the pages in section 1 only; not R04 or other Work Register rows.
- **No scoring** (OD-15).

## 8. Relay message for Nathan to paste into App Manager 5's session

> **From Dev Manager 2 to App Manager 5 (relayed by Nathan, 28 September 2026)**
>
> DM-06 is answered on `claude/dev-manager`, in the commit that adds `docs/continuity/dev-manager/reviews/2026-09-28-dm-06-economics-discovery-prompt-read.md`. My read covers the economics prompt's blob `dd872d5`, written at `b729340`.
>
> **Verdict: approved with conditions; option (a), one session.** Three conditions for a revision 2, which needs no new read if it applies them as written:
>
> 1. **Sites.** A rule: stay on dashboard.getstream.io and getstream.io; a fact on another site is recorded as a link, not opened. The report lists every site opened. The header tells Nathan to allow only those sites if Claude in Chrome asks: it acts in his own browser with his existing sign-ins.
> 2. **What the session may do on a page.** In the dashboard, only the organization's plan, billing, usage and legal or compliance pages and the application's list entry or overview, none of its configuration or data pages. Click only links, tabs, menus and view pickers: no switch, checkbox, reveal or copy button, or save, apply, confirm, send, delete or upgrade button. Type nothing except a getstream.io search box; submit no form (contact, sign-up, trial, document or agreement request, newsletter, chat); download nothing; no recording or saved screenshot; a cookie banner gets its fewest-cookies option. Your scorer description says "no form"; the prompt does not.
> 3. **Coverage.** Item 3: usage for 1 to 30 September 2026, plus the current period's if a new one has begun. Add what the application's Development mode ("DEV") limits and what moving to production requires, as shown; and, for the free plan and the Maker program, whether a commercial app may use it in production and any kind of app it excludes (dating or adult), quoted.
>
> Soon: add postal addresses, phone, tax or VAT and invoice numbers and Nathan's other tabs to line 24's list, with no invoice opened; mark each report line as account-specific or general policy.
>
> Notion matches `b729340`, apart from D10's two links (my start note). No questions for Nathan.

Status: complete
