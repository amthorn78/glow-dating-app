# SV3: recheck of the matrix rows that eligibility and discovery take

- **What:** the recheck that DM-37 5.1 asks of every brief that takes a matrix row ("Every brief that takes a row rechecks it on the day the brief is written"), for [SV3's brief](../../planning/sv3-eligibility-discovery-interactions.md), revision 1. It follows section 10 of [the matrix](../../planning/store-legal-safety-requirements.md): each row's source is re-read, the row's date is updated, the IDs stay as they are, and the reading is recorded here.
- **Who and when:** App Manager 11, on 11 November 2026, from 18:04 UTC (the fetches) to 18:07 UTC (the quotation checks). This is a records reading of public pages, not an implementation or review session.
- **Method,** as the [OD-60 recheck](2026-11-10-od-60-matrix-recheck.md) did it:
  - `curl` fetched each source into its own directory in the manager's scratchpad. A Python script run with `-I`, kept outside that directory, stripped the HTML tags and flattened white space. `pdftotext` read the PDFs.
  - A second script searched for each row's quotation as one continuous string in the stripped text. GP-16's first quotation matched only after a space that the tag stripping had added ("SB 2420 ,"), and was then read in place.
  - The fetched files were hashed and not committed.
- **Research, not legal advice** (the matrix's opening note applies).

## The rows SV3 takes

SV3 builds eligibility and discovery, so it takes the rows on which the decision to show a person to a member rests. That means the age state it reads (G-01; DM-37 2.2) and the rows that bind a feed or a recommendation to an age determination. The launch is the US only (OD-55), so the UK and EU rows of G-01 (UK-12 to UK-14, EU-24, EU-25 and EU-62) are not taken.

| Group | Rows | Why SV3 takes them |
|---|---|---|
| The age state's basis | AP-14, GP-16, UST-32 | The store age-signal duties. SV3 reads the age state these rows will add states to (P09.2), so its adult predicate must take further states without a redesign |
| A feed gated on age | UST-37, UST-38, UST-39 | Recommendations and broader discovery may count as an "addictive feed" or an "algorithmic feed", which these laws gate on an age determination |
| Known minors | USF-11, UST-41 | Actual knowledge that a member is a minor: no profiling, and COPPA's duties below 13 |

These rows are not taken: AP-15 to AP-17, AP-19, GP-15 and UST-33 to UST-36. They concern the handling of the store signals, which belongs to G-01's own item and P09.2, and none of them changes what SV3 reads.

## The sources

| Source | URL fetched | Final URL | HTTP, bytes | SHA-256 of the fetched file | Page date |
|---|---|---|---|---|---|
| Apple, age assurance Q&A | `https://developer.apple.com/support/age-assurance` | the same | 200, 121,964 | `9ffeab520892efac2046ea6e984b7e4b9511e65c00e305121e8e09eea847f55f` | none given |
| Google Play, US state app store bills (answer 16569691) | `https://support.google.com/googleplay/android-developer/answer/16569691?hl=en` | the same | 200, 1,671,107 | `98d1f79ad46d49fa5efe72ced964cd9ae26710c488b16a6ccb7c9375e673960f` | none given |
| Texas SB 2420, enrolled | `https://capitol.texas.gov/tlodocs/89R/billtext/html/SB02420F.htm` | the same | 200, 102,413 | `95db4ee9d15537a44fbe3ed5257726dafe71b051fc432655802befc5cbea0f5c` | the enrolled text |
| Fifth Circuit order, 25-51073 | `https://www.ca5.uscourts.gov/opinions/pub/25/25-51073-CV0.pdf` | the same | 200, 182,077 | `2f3c8d870e22515ca4e9c9aec20bf0fb5b01ef15235989eb3a67205e08b65e10` | the order |
| Supreme Court order list, 6 July 2026 | `https://www.supremecourt.gov/orders/courtorders/070626zr1_dc8f.pdf` | the same | 200, 29,502 | `964c507f4092487b40812fe84d9f63da375b373aa8e933626b01f9c395a4f44c` | "MONDAY, JULY 6, 2026" |
| California AG, SB 976 page | `https://www.oag.ca.gov/sb976` | the same | 200, 48,588 | `ccec77bd25df78834f479a7f1214e8b2a78836a9e1d967d4a677b7325a0e590e` | "Notice Register Publication Date: May 15, 2026" |
| New York AG, final SAFE for Kids rules | `https://ag.ny.gov/press-release/2026/attorney-general-james-and-governor-hochul-release-final-safe-kids-act-rules` | the same | 200, 60,731 | `f8bb5c2d5b62fa3979eab741db062a07cfcc25fa7c9a57b7ba0b750f892ede8b` | July 28, 2026 |
| 15 U.S.C. 6502 | `https://www.govinfo.gov/link/uscode/15/6502?link-type=html&year=2024` | `https://www.govinfo.gov/content/pkg/USCODE-2024-title15/html/USCODE-2024-title15-chap91-sec6502.htm` | 200, 9,965 | `019202fb7d756918bced071c46b75c082d88c37a365f9fd0d8e3ccfa1f483980` | the 2024 edition |
| Colorado Revised Statutes 2024, title 6 | `https://content.leg.colorado.gov/sites/default/files/images/olls/crs2024-title-06.pdf` | the same | 200, 2,108,494 | `560ff6d64b5afdf2a3bc5ac917a392269d16270a029b252ff8f7957deb38b423` (the same file as on 10 November) | "Colorado Revised Statutes 2024" |

**What could not be read:**

- **California's bulk data** (`downloads.leginfo.legislature.ca.gov/pubinfo_2025.zip`): the server answered `200` with a `content-length` of 1,292,248,187 bytes. That is too large to fetch within a session's disk allowance, so it was not downloaded. UST-37's and UST-39's statutory quotations were therefore not re-read. UST-37's state was re-read from the Attorney General's page. UST-39 was not rechecked; its date stays 1 November 2026. Both can be re-read from the bulk data in Nathan's CLI agent (OD-43) before P09.2's brief or the G-01 item's brief, whichever comes first.
- **The eCFR's Part 312** (`ecfr.gov/api/versioner/v1/full/2026-10-29/title-16.xml?part=312`) answered `406` twice, with and without an `Accept: application/xml` header. USF-11's statutory quotation was read; its rule citation was not re-read.

## The readings

**AP-14: confirmed.** *"Yes. In regions where legally required, you need to check the age of the people using your app with the Declared Age Range API."* *"Yes, developers are responsible for their own age restrictions."*

**GP-16: confirmed.** *"Texas' App Store Accountability Act, Texas SB 2420, is now in effect after a federal appeals court stayed the preliminary injunction issued in December 2025."* *"It is your responsibility to determine how these laws apply to your app"*.

**UST-32: confirmed.**
- The enrolled text holds *"shall create and implement a system to use information received under Section 121.024 to verify"*.
- The Fifth Circuit's order grants the stay pending appeal: *"We grant the opposed motion because Texas has met its burden under Nken v. Holder."*
- The Supreme Court's order list of 6 July 2026, in 25A1390, *Computer & Communications Indus. Assn. v. Paxton*: *"The application to vacate stay presented to Justice Alito and by him referred to the Court is denied."*
- Whether the merits appeal has been decided since was not checked.

**UST-37: state confirmed; statute not re-read.**
- The Attorney General's page still describes the age-assurance regulations as proposed: *"The Act requires the Attorney General to adopt regulations regarding age assurance and parental consent methods in furtherance of the Act's purpose by January 1, 2027."*
- It also says *"Status of the Proposal: The Department is reviewing public comments received during the 45-day public comment period. The proposed regulations must also be reviewed by the Office of Administrative Law (OAL)."*
- The row's quotation from Health & Safety Code §27001 was not found on this page; it comes from the bulk data, which was not fetched (above).

**UST-38: confirmed.** *"social media companies must determine that the user is an adult before allowing them to access algorithmic feeds and/or nighttime notifications."* The same page adds: *"Companies may confirm a user's age using any existing method, as long as the methods are shown to meet accuracy benchmarks and protect users' data."* The rule text itself was again not read.

**UST-39: not rechecked** (above).

**USF-11: statute confirmed.** 15 U.S.C. 6502 holds *"any operator that has actual knowledge that it is collecting personal information from a child"*. The rule citation was not re-read (above).

**UST-41: confirmed** (the same file as the OD-60 recheck read on 10 November). *"A controller that offers any online service, product, or feature to a consumer whom the controller actually knows or willfully disregards is a minor shall use reasonable care"*.

## What changes in the matrix

- No requirement changed.
- Rows AP-14, GP-16, UST-32, UST-38, USF-11 and UST-41 get "rechecked 2026-11-11 (SV3)" in their source column. UST-37 gets "state rechecked 2026-11-11 (SV3); statute not re-read".
- The matrix's header line "Rechecks" names this record.
- UST-39 and USF-11's rule citation stay as they were.

## What SV3's brief takes from it

- **The adult predicate takes a set of accepted age states** (D3 of the brief). Today the set holds only `self_declared_adult`. P09.2 adds the store-signal states (AP-14, GP-16, UST-32), and a later item may require a stronger one, without a redesign.
- **Whether Glow's recommendations or broader discovery are an "addictive feed" (UST-37) or an "algorithmic feed" (UST-38) is a reading for counsel.** Whether to take that advice is Nathan's decision (DM-31). The earliest dates are 1 January 2027 (California) and 25 January 2027 (New York), and launch is not before P12. SV3 builds nothing for these laws beyond the age-state gate. The question is carried to the G-01 item, and to P09.2's release-gate list (PF01 §7, 1.17).
- **A member whose age state is not an accepted adult state** is neither shown to anyone nor given a page, and no recommendation is computed for them (UST-41's no-profiling duty on actual knowledge; USF-11).
