# Nathan's direction: operational guidance lives in Notion as well as the repository

- **Source:** Nathan Amthor, in the Dev Manager session on 25 September 2026.
- **Consultation ID:** none. This is owner input, with the Dev Manager's findings about it.
- **Basis:**
  - `claude/stoic-carson-66gdig` at `516bee2`, fetched after this direction;
  - Notion's *Glow Dating App — Implementation Control*, fetched at 09:42 UTC. I read its first 10,400 characters in full: the current-status block and the operating-procedure section. For the other roughly 92,600 characters, marked history, I read the section headings only.

## The direction, word for word

> "operational guidance should live in notion, not just in repo, do not ignore that resource, it is critical"

## What I read in Notion

- **Size.** Implementation Control is 103,059 characters. The first 7,662 are the current-status block, and 7,662–10,261 is "Operating procedure — manual relay". Everything after that is marked history: 36 sections running from M02 back to P03.
- **The current-status block is current** as of `516bee2`: DM-01 to DM-03 considered, revision 3 of the review prompt, AM3-01 to AM3-08.
- **Gaps between Notion and the repository and owner input:**
  - **(a) Owner answers missing.** The status block says the Dev Manager's "ten questions for Nathan are pending". Nathan answered all ten in this session. The answers are recorded on `claude/dev-manager` (`574ee0e`, `2beb86d`) but are not yet in Notion or on the manager branch.
  - **(b) Out-of-date procedure.** The operating-procedure section cites "PF00 1.4 and PF01 1.5" as its repository authority. The current revisions are PF00 1.8 and PF01 1.9. The section does not state any of the following:
    - the Dev Manager's relay;
    - the Dev Manager read of governing Markdown and of live-action prompts;
    - batching records;
    - the pre-merge checklist;
    - Nathan's relay direction ([relay direction](2026-09-25-relay-direction.md): reports in the repository, messages relayed by hand).
  - **(c) Standing directions not in Notion.** The owner-direction register exists only in the repository. The status block links to it, but the directions themselves are not in Notion.
- **A gap on my side.** DM-01 and DM-02 did not read Notion (their "Limits"). That understated Notion's role. From now on, every Dev Manager consultation reads the relevant Notion pages as well as the repository, and reports any mismatch.

## How this fits the current rules

- **The rule it changes.** PF01 D04 and D09, `AGENTS.md` and PF00 say that repository Markdown owns the operational documentation, and that Notion coordinates status and links (OD-05).
- **My reading of Nathan's direction:** the repository stays the versioned text that sessions read, and Notion carries the same operational guidance, kept in step with it. Notion is no longer only for status and links. This refines OD-05's "Notion coordinates" rather than reversing it.
- **What his direction does not settle** is which copy wins if the two disagree. That is his to decide (see the question below).
- **The operational guidance Notion should carry**, each linking back to its repository home and matching it:
  1. **The operating procedure:** the manual relay, one item at a time, the review paths, the Dev Manager's relay (reports in the repository, messages relayed by Nathan by hand), batching records and the pre-merge checklist.
  2. **Nathan's standing directions:** the owner-direction register, including the new rows from Nathan's answers.
  3. **The current routing:** already present, as the status block.
  4. **The Dev Manager's log and dispositions:** already present, as *Dev Manager — reviews and approvals*.
- **Keeping the two in step.** The workflow's close-out step and each records batch already include "sync Notion". Add an explicit check that Notion's operating procedure and register match the repository's current revisions, with a readback. A mismatch is a defect, to be fixed like any other.
- **Notion's size.** DM-01 P3 recommended trimming Implementation Control's history. That helps this direction, because the operational guidance should be the first thing on the page, not buried above 93,000 characters of history. Move the history to a linked sub-page rather than deleting it.

## What the Dev Manager does

- It reads Notion in every consultation from now on.
- It still does not edit Notion. Its charter forbids it, and the primary manager keeps Notion current. If Nathan wants the Dev Manager to write to Notion, that is a change to its charter and his to make.

## Documents and pages the primary manager should update

- **Notion, Implementation Control:**
  - add Nathan's answers to the ten questions (the status block);
  - rewrite the operating procedure to match `516bee2` and the relay direction;
  - add the owner-direction register, or a linked Notion copy of it;
  - move the history to a sub-page.
- **Notion, *Dev Manager — reviews and approvals*:** the answers and the two direction notes.
- **The owner-direction register:** a row for this direction.
- **The repository documents that state the Notion rule:**
  - PF01 D04 and D09, and §2's surface table;
  - PF00's authority map;
  - `AGENTS.md`'s first paragraph;
  - `docs/README.md`;
  - the manager workflow's Notion sync step, adding the match check above.

  Their wording depends on Nathan's answer below.
- **The Dev Manager charter and start prompt:** the Dev Manager reads Notion in every consultation.

## Question for Nathan

1. **When the repository and Notion disagree about operational guidance, which one is correct?**
   - (a) The repository is correct, and the Notion copy is fixed to match. That keeps one versioned source for sessions.
   - (b) Notion is correct, and the repository is fixed to match.

   I recommend (a). Sessions read the repository at an exact commit, and Git keeps its history. Either way, a mismatch gets fixed at once.

## Relay message for Nathan to paste into App Manager 3's session

> **From the Dev Manager to App Manager 3 (relayed by Nathan, 25 September 2026)**
>
> Four new files are on `claude/dev-manager` (head `e6af216` or later), after DM-03 (`23951c4`), which you have already integrated. Please integrate them with your next records batch and record their dispositions:
>
> 1. `docs/continuity/dev-manager/reviews/2026-09-25-owner-answers-to-dm-01-dm-02.md` (`574ee0e`): Nathan's word-for-word answers to all ten DM-01 and DM-02 questions, with what each changes. **They are answered; do not ask them again.** Notion still shows them as pending.
> 2. `docs/continuity/dev-manager/reviews/2026-09-25-owner-answers-addendum.md` (`2beb86d`):
>    - the Stream secret is yours to explore; bring Nathan a plain-language recommendation before I2a;
>    - Nathan holds every human role; write the HDE contract-requirements document for him.
> 3. `docs/continuity/dev-manager/reviews/2026-09-25-relay-direction.md` (`82e53f9`): reports stay in the repository, and Nathan relays messages by hand.
> 4. `docs/continuity/dev-manager/reviews/2026-09-25-notion-operational-guidance.md` (this commit): Nathan's direction that operational guidance lives in Notion as well as the repository.
>    - Implementation Control's operating procedure is out of date: it cites PF00 1.4 and PF01 1.5, and has no Dev Manager relay rules.
>    - The owner-direction register is not in Notion.
>    - Its status block still lists the ten questions as pending.
>
>    Update Notion to match, with readbacks. Nathan has been asked which copy is correct when the repository and Notion disagree.

Status: complete
