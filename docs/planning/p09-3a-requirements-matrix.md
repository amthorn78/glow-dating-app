# P09.3a — The store, legal and safety requirements matrix

- **Work ID:** P09.3a (P09; M05's E2, with E6 inside it; PF01 §7, "Mobile/store readiness"; R05).
- **Status:** the matrix is written, verified and routed (DM-37); the first A05 message is with Nathan. Brief revision 1. **Prompt:** [`docs/ephemeral/2026-11-01-p09-3a-matrix-prompt.md`](../ephemeral/2026-11-01-p09-3a-matrix-prompt.md), revision 1, for `Glow App - No Stream`.
- **Owner:** Nathan Amthor, by the order he resumed on 26 October (OD-49): P09.3a after M06, before P06.2-F. N3 was folded into that order (DM-31). **Manager:** App Manager 8. **Session:** one research session, started by Nathan.
- **Revision 1, 1 November 2026.**
- **Starting point:** `main` at `fcd6ebc` (PR38's merge), with the manager branch's Markdown records after it. The prompt names the exact commit.
- **Outputs:**
  - the matrix, `docs/planning/store-legal-safety-requirements.md`, kept current after this item (PF01 §7: "prepare and then maintain");
  - the session's record, `docs/testing/evidence/<date>-p09-3a-requirements-matrix.md`: method, sources read and unread, limits.

## Why

- **PF01 §7** asks for a dated requirements matrix for Apple and Google before P06.3's and P07's briefs, "for the launch countries (A05), or the candidate list under comparison until Nathan chooses them". **R05** names the store, safety and operations gap as a project risk.
- **M05's E2 and N3:** without the matrix, P06.3, P07 and P08 may miss store-mandated features (child-safety standards, in-app and web deletion, report and block, age rating) and need rework or meet rejection.
- **M05's E6:** a photo-UGC dating app has child-safety detection and reporting duties, and no item or provider choice holds them yet.
- **Nathan's decisions:**
  - the candidate countries are **the US, the UK and the EU** (OD-50, N4 (b)). He names the launch countries from the matrix before P07's brief;
  - before P07's brief, the open A05 questions go to him in OD-32's form (OD-50).

## Outcome

The matrix is done when it holds all of these:

1. **A header that says what it is not.** It is research with dated sources, not legal advice, and it says so (DM-31, on N4). It states what it does not establish, and that whether to take legal advice is Nathan's.
2. **One row per requirement,** for each source that imposes one. The sources are the two stores (Apple's App Store and Google Play) and the three candidate jurisdictions (the US, federal and the states that bear on a dating app; the UK; the EU and its regulations). Each row gives:
   - **the requirement,** in a sentence, with the source's own words for its trigger where that decides whether it applies;
   - **the source:** an official page or the legal text, its section, its URL and the date read;
   - **whom it binds:** which store or jurisdiction, and the condition that makes it apply to Glow (for example, photo uploads, messaging, paid subscriptions, a size threshold);
   - **what it asks of Glow,** concretely: a feature, a disclosure, a process, a report or a named contact;
   - **the owning phase:** the PF01 phase or Work Register item that would deliver it (P06.3, P07, P08, P09, P11 or P12), or "no owner";
   - **the current state at fixture scope,** from the repository's records and code at the starting commit: met, partly met, planned (with the item), or not planned. A fixture behavior is never counted as the production obligation met.
3. **PF01 §7's topics, each covered:**
   - distinctive dating-product value, including how the stores treat dating and astrology-like products;
   - user-generated content: moderation, reporting, blocking and a published contact;
   - adults-only eligibility: the age rating, and the age assurance each jurisdiction requires;
   - **child-safety duties, as a requirement, not an option** (M05 E6; DM-31 item 5): CSAM detection, the reporting duty to the authority each jurisdiction names, and the stores' child-safety standards for dating and social apps;
   - privacy disclosures: Apple's privacy labels and privacy manifests, Google Play's Data safety form, and the data-protection law's duties for the data Glow holds (birth data, photos, sexual orientation and preferences, approximate location, messages);
   - account deletion: in the app and on the web, and what it must remove;
   - sign-in: the stores' rules when a third-party or social login is offered;
   - subscriptions and in-app purchases, for a paid launch (PF01's billing is conditional);
   - permissions and their purpose strings;
   - review access: demo accounts and reviewer instructions.
   It adds a requirement outside these topics only when a source makes it binding on a dating app in a candidate jurisdiction, for example a dating-safety law or a takedown duty for intimate images.
4. **The gaps:** each requirement with no owning phase, or whose owner's plan does not cover it, in one list. Each gap carries the smallest change that would give it an owner (a Work Register row, a PF01 line or a brief's scope), for the manager to route.
5. **What the A05 questions turn on:** for each open A05 question (launch geography, age assurance, the preference taxonomy, resurfacing and rematch, the history policy, retention, moderation operators), what the requirements imply in each candidate jurisdiction. Facts and their sources only, not a recommendation. The manager writes the questions to Nathan.
6. **Its maintenance:** when it is rechecked (before P06.3's and P07's briefs, and before any release artifact, PF01 §7), and which rows are most likely to change.

## Design

- **D1 — Research only.** The session changes no code, configuration, dependency or governing file. Its repository writes are the two outputs above, so the change is ordinary documentation: no application CI and no code review (`AGENTS.md`). The manager verifies it against its sources.
- **D2 — Primary sources for every requirement.**
  - **Stores:** Apple's App Review Guidelines, App Store Connect Help and Apple Developer documentation; Google Play's Developer Policy Center and Play Console Help.
  - **Law and regulators:** the legal text (for example `uscode.house.gov`, `ecfr.gov`, state legislatures, `legislation.gov.uk`, EUR-Lex) and the regulators' own guidance (for example the FTC, NCMEC, Ofcom, the ICO, the National Crime Agency, the European Commission, the EDPB).
  - **Secondary sources** (law-firm notes, news, trade press) only to find a primary source. A row that rests on one says so and is flagged as unconfirmed.
  - **Quotes** are short, a sentence or a clause, enough to show the trigger.
- **D3 — Network and tools.** The session reads public web pages with its web tools (search and fetch). The manager's check from `Glow App - No Stream` on 1 November reached Apple's guidelines, Google Play's help and EUR-Lex through the proxy, while Ofcom's and the FTC's sites answered plain `curl` with bot challenges. A page the session cannot read is listed as unread with its URL, never filled from memory or training data. If a core source of a topic stays unreadable, the session says so, and the manager can give that part to Nathan's CLI agent in an open environment (OD-40, OD-43).
- **D4 — Dated.** Each row carries the date its source was read. The matrix's header carries the date of the research and the starting commit.
- **D5 — The app's current state, from the repository.** The session reads the repository's records and code at the starting commit, for example `docs/architecture/privacy-and-safety-rules.md`, the briefs and PF01, and cites the file for each state. It runs no application command and no provider call.
- **D6 — What it does not decide:** the launch countries, the age-assurance method, whether to take legal advice (Nathan); costs (M07); any feature design (the owning phase's brief).
- **Considered and not chosen:**
  - **one matrix per jurisdiction:** the stores' rows apply in every jurisdiction, and one table shows the overlaps;
  - **legal advice now:** that is Nathan's choice (DM-31, on N4). The matrix makes the choice concrete, and it can be taken later.

## Owned paths (the session)

- **New:** `docs/planning/store-legal-safety-requirements.md` and `docs/testing/evidence/<date>-p09-3a-requirements-matrix.md`.
- Nothing else.

## Manager-owned

- This brief and its "Sessions"; the prompt; the Work Register's P09.3a row; Notion; the handoff; routing the gaps and the A05 questions.

## Exclusions

- No change under `apps/`, `services/`, `packages/`, `proofs/`, `scripts/` or `.github/`, and no governing Markdown.
- No account creation, sign-up, purchase or form submission on any site. No message to a regulator, a store or anyone else.
- No provider call, and no connection to a database, HDE or Railway. No `eas`, `playwright install` or `migrate`.

## Acceptance checks

- The matrix holds each part of "Outcome" 1 to 6, and every row names its source, URL and read date.
- The record lists every source read and every source not read.
- The session branch changes only the two outputs (`git diff --name-only <start> <head>`).
- The trusted classifier reads the change as `ordinary-docs-only`.

## Review plan

- **No code review and no application CI:** the change is Markdown only (`AGENTS.md`).
- **The manager verifies the report** against the pushed branch:
  - it re-reads a sample of rows against their live sources: every child-safety row, every row whose owner is "no owner", and at least one row for each store and each jurisdiction;
  - it checks the current-state column against the cited files;
  - it checks that no row rests on memory or on an unread page.
- **Then** the gaps are routed (Work Register rows or a brief's scope). The A05 questions go to the Dev Manager first and then to Nathan, in OD-32's form, before P07's brief (OD-32, OD-50).
- **Dev Manager:** this brief makes no architectural or procedural choice, and it applies DM-31's conditions on the matrix as written (its environment, that it is not legal advice, CSAM in scope, the countries), so the charter asks no read of it. A gap that would change a phase's scope goes to the Dev Manager with the routing.

## Sessions

- **The research session** (1 November 2026; prompt revision 1 at `f40f1d7`; branch `claude/stoic-pasteur-r24pz8`, head `1eefca1`; Nathan's pick: not recorded): the matrix, `docs/planning/store-legal-safety-requirements.md`, with 320 rows (31 on child safety, 85 with no owner) and 16 gaps, and its record. Every part of "Outcome" is done. The manager verified it (the record, "Manager verification"): 104 of 108 sampled rows matched their live sources, including all 31 child-safety rows; three corrections are marked. Fast-forwarded into the manager branch. Next: DM-37, on the gaps' routing and the A05 questions.
- **DM-37** (1 November 2026; the Dev Manager's read of `3173bf3`): the matrix approved as a dated record, not an applicability finding; the routing approved with 2.1 to 2.6, now in the carried-items file; PF01 §7's release gate (2.7) applied in PF01 1.17; the order stands; the A05 questions in three messages (4.1 to 4.5), the first with Nathan; rechecks driven by events (5.1 to 5.4). Next: Nathan's answer to the first A05 message, and the records PR.
