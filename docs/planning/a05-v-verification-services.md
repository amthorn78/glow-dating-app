# A05-V — Research for the decision on the identity verification company and the photo check's service

- **Work ID:** A05-V, under A05 (launch market and operating policy decisions). Source: Nathan's answers of 10 November 2026 (OD-61) and DM-52 section 16, "The next decision for Nathan".
- **Owner:** a research session started by Nathan. **Manager:** App Manager 12.
- **Starting commit:** the commit of the manager branch `claude/magical-wozniak-yfmmx2` named in the prompt.
- **Revision 2, 17 November 2026,** with DM-83's PP1 to PP9 (Dev Manager 5, `3c0a5fe`, a read of `8995d37`), applied as given. Revision 1 went to the Dev Manager in DM-83. Status: approved; the prompt follows PR49's merge.

## Why

OD-61 is in force: a member's profile shows only after **identity verification** (a government photo ID, checked by a verification company with a selfie matched to it, decided automatically), and each photo is approved by an **automated photo check**; staff act only on reports, and may approve a member without verification while a console setting allows it. DM-52 section 16 leaves two choices open, the verification company and the photo check's service, for a decision message to Nathan in OD-32's form **after the matrix's recheck of the rows they touch**. That message covers six items:

1. the cost of each;
2. the consent, including the written release Illinois's BIPA asks for (UST-51);
3. what each service keeps, and for how long;
4. what a member can do when a check fails;
5. whether the ID's birth date replaces the typed one (OD-55's D3);
6. whether one service also runs G-02's detection step (child sexual abuse material).

The launch is the US, all states (OD-55). Nothing in SV2 waits on this decision (DM-52). P07 (the failure path and staff approval), P08 (consent wording, deletion of the vendor's copy), P10 (the onboarding step), P11 (wiring the services) and M07 (their cost lines, OD-50) take its answers (the carried-items file, K3 to K7 of DM-52).

The manager rechecked the matrix itself before (P06.3: three rows; OD-60; SV3: eight rows). This recheck touches 60 rows and adds a comparison of services from their public pages, so it is given to a research session, with the manager verifying.

## Outcome

**1. The matrix recheck** (DM-37 5.1; the matrix's section 10, whose triggers include choosing an age-assurance method and proposing a detection or moderation vendor). Each row's source is re-read today, its date updated, its quotation found in the text read, and its ID kept. A row whose requirement has changed is corrected in place and marked as rechecked; nothing is deleted.

| Group | Rows | Why |
|---|---|---|
| Biometric and identity data | UST-51; UST-42, UST-44 (CCPA); UST-45, UST-46 (Texas TDPSA); UST-47 (Virginia VCDPA); UST-48 (Colorado CPA); USF-13 (FTC Act section 5 and the FTC's guidance); USF-21, USF-22 (PADFA; the Justice Department's bulk sensitive data rule) | A selfie matched to an ID photo is face geometry; most state privacy laws treat biometric data as sensitive data; vendor agreements may meet the bulk data rule |
| Age | AP-14 to AP-17, AP-19, AP-31; GP-15, GP-16; UST-32 to UST-41; USF-11 | Whether a birth date read from a government ID changes what these rows ask, or meets an "age determination" they name. Item 5 changes what the age state is built from, so this recheck also takes the store-signal rows that SV3's recheck left out (AP-15 to AP-17, AP-19, GP-15, UST-33 to UST-36) and the rest of section 10's age-assurance list (UST-40). UST-41's duties start when Glow knows (or wilfully disregards) that a user is a minor, which an ID check can show. AP-31 bars reusing data collected for one purpose without further consent, which bears on using the ID's birth date as the member's birth data |
| Store privacy rows a vendor touches | AP-22, AP-23, AP-27, AP-29, AP-30; GP-24 to GP-27, GP-29, GP-30, GP-32 | Declaring the data types, including what third-party code or partners collect through the app (AP-22, GP-24) and how a service provider's part is declared (GP-26); the privacy policy's retention text; consent; and sending data to a third party |
| The photo check and G-02 | AP-21; GP-18 to GP-23; USF-01 to USF-07; UST-49 | Whether a photo check service may, must or may not run hash matching for child sexual abuse material, and what follows a match |
| Deletion of the vendor's copy | AP-33, GP-33, UST-43 | Item 3, and K4 of DM-52 (the vendor's copy is deleted on the schedule Nathan sets and on account deletion): Google asks the app to ask its service providers to delete (GP-33); Apple's deletion removes the account's associated data, and users are told what is kept (AP-33); UST-43 is the CCPA's right to delete, which binds only a CCPA business |
| The dating-service safety policy | UST-20 | Colorado's posted safety policy says whether and when Glow screens members, verifies identity or verifies that members are at least 18, and how suspension and appeal work: items 4 and 5. The row records no small-service exemption |

The session also searches primary sources for **US state laws on biometric identifiers or biometric data other than BIPA**, including a biometric provision inside a wider law (a consumer health data law, for example) and any biometric provision of a privacy law already in the matrix that applies below that law's general thresholds; for **state laws on identity verification by dating services**; and for **Apple's and Google's own rules on face or biometric data**, which no AP or GP row names. A law or rule already in a row is rechecked in that row, not added again (Colorado's dating safety law, for example, is UST-20). Each one found in a primary text becomes a new row with the next free ID in its section (the matrix's section 1: IDs are added, never reused), marked as added at this recheck; each search that finds none is recorded as searched, with the sources tried.

**2. A comparison of candidate services**, each fact from the service's own public pages read today, with the URL and date:
- **identity verification companies** that check a US government photo ID and match a live selfie to it with an automated decision: at least three;
- **automated photo check services** for profile photos (sexual content, violence and similar classes): at least three;
- **hash matching for child sexual abuse material**: which of the services above offer it, and the programmes that give hash matching to services like Glow, with their eligibility terms as published.

For each service: its published price (or "no public price"), minimums and contract terms as published; what it keeps (images, extracted data, face templates) and for how long, by default and as configurable, and whether it uses them for its own purposes, such as training its models; where it processes data, and its published sub-processor list; what it publishes on BIPA (consent capture, a written release, a retention policy); its manual review or retry path for a failed check; whether it returns the ID's birth date and a liveness result; how it is integrated (a native SDK for React Native or Expo, a hosted web flow, or an API); and whether a data processing agreement is published. A fact not published is written as not published, never inferred.

**3. A facts table for the six items above,** each citing the rows and the services' pages that bear on it. **No recommendation:** the manager writes the decision message and its recommendation, and the Dev Manager reads it before Nathan receives it (OD-32).

## Owned paths (the session)

- `docs/planning/store-legal-safety-requirements.md`: the rechecked rows, their dates, any new rows, the Rows column of section 8's gaps and section 7's coverage where a new row is added, the header's **Rechecks** entry for this recheck, and each sentence of sections 9 and 10 that states a rechecked row whose requirement or status changed, corrected and marked as corrected at this recheck.
- `docs/testing/evidence/<the session's date>-a05-v-verification-services.md`: the session's record (method, sources with their hashes, the quotation checks, the comparison, the facts table, deviations and limits).

## Manager-owned

This brief; the prompt; the carried-items file; the handoff; the owner-direction register; the review log; the decision message.

## Exclusions

All code, configuration, workflows and other Markdown. No account, sign-up, trial, form, sales contact or message to any vendor. No call to Stream, a database, HDE or Railway. No statement that Glow is, or would be, compliant: the matrix is a dated record of research, not legal advice or an applicability finding (DM-37 1.1).

## Dependencies and inputs

Public web pages only. The session reads OD-55, OD-60 and OD-61 in the owner-direction register, DM-52 section 16 (`docs/continuity/dev-manager/reviews/2026-11-10-dm-52-sv2-brief.md`), the matrix's sections 1, 8, 9 and 10, and the earlier recheck records (`docs/testing/evidence/2026-11-08-p06-3-matrix-recheck.md`, `2026-11-10-od-60-matrix-recheck.md`, `2026-11-11-sv3-matrix-recheck.md`) for their method.

## Acceptance checks

- `git diff --name-only <START_SHA> HEAD` prints only the two owned paths.
- Every row ID present at `<START_SHA>` is present at the head, in the same order: a script prints the IDs missing and the IDs reordered, and both lists are empty.
- Every rechecked row names today's date as its date read.
- Each rechecked row's quotation is found as one continuous string in the stripped text of the source read today; the record's table lists each row, its source's SHA-256 and the result. A quotation found only after normalising white space or punctuation says so.
- Each service fact in the comparison names its page and the date read.
- Each new row names its primary text, and the record lists the rows of the same state or store it was compared with, so that no law or rule already in a row is added again.

## Classification expectation

`ordinary-docs-only`: both owned paths are Markdown, outside any `.claude/` directory. No application checks and no code or security review apply.

## Evidence home

The session's record; the manager's verification is added to it as a section.

## Report format

Branch, start and head SHAs, changed paths, the rows rechecked (with any changed requirement named), the rows added, the sources unread with their URLs, the services compared, every acceptance check with its exact result, deviations and open questions.

## Review plan

The change is Markdown only, so no code review applies. The manager verifies: the ID script and a sample of the quotation checks re-run from fresh fetches, every changed requirement read against its source, every new row read against its primary text, and each corrected sentence of sections 9 and 10 read against its row. The decision message built from the record goes to the Dev Manager before Nathan.

## Sessions

- **The research session** (`claude/vigilant-ramanujan-jbxqro`, head `0859532`, from `3fce46b`; 17 November 2026): the 60 rows rechecked (GP-16's wording and UST-36's enactment corrected; UST-51's status changed with OD-61), 11 rows added (AP-67 to AP-69, UST-52 to UST-59), four identity verification companies, photo check services and hash-matching options compared, and the facts table; [its record](../testing/evidence/2026-11-17-a05-v-verification-services.md). Verified by the manager (the record, section 12) and merged into the manager branch at `e038596`.
- **After it,** Nathan changed OD-61 (OD-68): no selfie matched to an ID for the MVP, a card check at signup during a free trial of a paid plan, and the photo check dropped behind a toggle. The decision message this brief prepared is not sent (DM-84 item 5): two questions go to Nathan first (a paid plan at launch, A06; what the card check is for), and a follow-up research item, A05-V2, is scoped by his answers. This brief's record stands as the research for ID validation later, the photo check's toggle and G-02's detection choice.
