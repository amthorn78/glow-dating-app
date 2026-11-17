# A05-V: research for the decision on the identity verification company and the photo check's service

**Research, not legal advice.** This record, like [the matrix](../../planning/store-legal-safety-requirements.md) it updates, says what official pages, legal texts and services' own public pages said when they were read on **17 November 2026**. It was prepared by a research session, not by a lawyer. It decides no applicability to Glow, says nothing about whether Glow is or would be compliant, and makes no recommendation: the manager writes the decision message, and the Dev Manager reads it before Nathan (OD-32; DM-37 1.1).

- **What:** the three outcomes of [A05-V's brief](../../planning/a05-v-verification-services.md) (revision 2): the recheck of the 60 matrix rows the brief lists, with the three searches it names (its PP5 text); a comparison of identity verification companies, automated photo check services and hash matching for child sexual abuse material, from their own public pages; and a facts table for DM-52 section 16's six items.
- **Who and when:** the A05-V research session, started by Nathan from the prompt at `3fce46b` (revision 1) on the manager branch, on 17 November 2026, from about 14:15 UTC. It used three research subagents (state law; identity verification companies; photo checks and hash matching), each under the same source rules and fetch method; this session checked and merged what they returned (section 11). No account, form, sign-up, trial, demo or quote request, message, provider API call or application command was made.
- **Start gate:** HEAD `3fce46b0e1e6f4023322bfcc888cd7f7c40cf303`; PR49 (`cf0ac60`) present; no non-Markdown difference from `origin/main`; the matrix unchanged on the manager branch since the prompt's commit (its head was `a6b7d48`, whose two later commits touch only manager-practice files); the brief's "Sessions" said "None yet." Environment: none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `STREAM_*` name set (names only checked).

## 1. Method

As the [SV3 recheck](2026-11-11-sv3-matrix-recheck.md) and the [OD-60 recheck](2026-11-10-od-60-matrix-recheck.md) did it:

- **Fetching.** `curl` (with a browser-style User-Agent) fetched each source into its own new directory in the session's scratchpad, outside the repository. A page that needs JavaScript was rendered with the pre-installed Chromium (Playwright) and its rendered HTML saved the same way; the sources tables mark these "(rendered)". Each fetched file was hashed with SHA-256; no fetched file is committed.
- **Reading.** A Python script run with `-I`, kept outside the fetch directories, stripped the HTML tags and flattened white space; `pdftotext` read the PDFs (`-layout`, and `-raw` for one two-column PDF, USF-02's).
- **Quotation checks.** A second script searched for each quotation, split at its ellipses, as one continuous string in the stripped text, and reported **exact**, or **normalised** where it matched only after normalising white space before punctuation, curly quotation marks, a ligature or a PDF line number. Each normalised match was then read in place.
- **California's bulk data** (`pubinfo_2025.zip`, 1,292,263,530 bytes, `Last-Modified: Mon, 16 Nov 2026 05:26:36 GMT`, ETag `"4d06606a-6605e05841b00"`) is too large to download, as SV3's recheck found. The server accepts byte ranges, so the zip's central directory, the law section table and only the members needed were read by HTTP range requests (a small part of the file: each of five runs re-read the 20 MB central directory); each extracted member is hashed below. This is how P09.3a's session read it (its record, section 3, "Method").
- **One certificate chain completed.** `www.ilga.gov` serves its certificate without the Sectigo intermediate, so `curl` refused it. The intermediate named in the certificate's own Authority Information Access field (`http://crt.sectigo.com/SectigoPublicServerAuthenticationCAOVR40.crt`) was fetched and the chain verified against the trusted bundle (`openssl verify`: `OK`) before BIPA was fetched with it. Verification was never turned off.
- **Searches.** The WebSearch tool found URLs only; a secondary page led to a primary one. A fact resting on a secondary source is marked **UNCONFIRMED**.

## 2. The rows taken, and why

The brief's table (DM-83 section 3 says why each row is taken):

| Group | Rows | Why |
|---|---|---|
| Biometric and identity data | UST-51; UST-42, UST-44 (CCPA); UST-45, UST-46 (Texas TDPSA); UST-47 (Virginia VCDPA); UST-48 (Colorado CPA); USF-13 (FTC Act section 5 and the FTC's guidance); USF-21, USF-22 (PADFA; the Justice Department's bulk sensitive data rule) | A selfie matched to an ID photo is face geometry; most state privacy laws treat biometric data as sensitive data; vendor agreements may meet the bulk data rule |
| Age | AP-14 to AP-17, AP-19, AP-31; GP-15, GP-16; UST-32 to UST-41; USF-11 | Whether a birth date read from a government ID changes what these rows ask, or meets an "age determination" they name; item 5 changes what the age state is built from; UST-41's duties start on knowledge that a user is a minor; AP-31 bars reuse without further consent |
| Store privacy rows a vendor touches | AP-22, AP-23, AP-27, AP-29, AP-30; GP-24 to GP-27, GP-29, GP-30, GP-32 | Declaring the data types, including third-party code and partners, and a service provider's part; retention text; consent; sending data to a third party |
| The photo check and G-02 | AP-21; GP-18 to GP-23; USF-01 to USF-07; UST-49 | Whether a photo check service may, must or may not run hash matching for child sexual abuse material, and what follows a match |
| Deletion of the vendor's copy | AP-33, GP-33, UST-43 | Item 3, and K4 of DM-52 |
| The dating-service safety policy | UST-20 | Colorado's posted policy says whether and when Glow verifies identity or age, and how suspension and appeal work: items 4 and 5 |

## 3. The sources (the recheck)

Every source below was fetched on 17 November 2026 between 14:18 and 14:35 UTC (each row's own time is in its fetch metadata, not committed). "Final URL" is where redirects ended. The page date is as the page shows it; "none found" means no date was found on the page.

| Fetch name | URL fetched | Final URL | HTTP, bytes | SHA-256 | Page date |
|---|---|---|---|---|---|
| `al-hb161` | `https://alison.legislature.state.al.us/files/pdf/SearchableInstruments/2026RS/HB161-enr.pdf` | the same | 200, 107,175 | `b4672a280178426355dec957e03343e286109540641303d661e2d34b6aa00d33` | enrolled text (passed 10 Feb 2026) |
| `al-hb161-status` (rendered) | `https://beta.alaleg.gov/legislation/HB161-2026RS` | the same | 200, 243,375 | `53a0a5ae2cea271bfd63fcdb03264e48c81bea6ef2ec41b11c55cfc0aa09d895` | "Last Action 2/17/2026" |
| `alreporter-hb161` | `https://www.alreporter.com/2026/02/19/gov-ivey-signs-app-store-accountability-act-into-law/` | `https://www.alreporter.com/2026/02/19/gov-ivey-signs-app-store-accountability-act-into-law` | 200, 639,599 | `979c98d3a11c5441f9cd1b7214fe8a295f29c0e8cdfce3b4527a08820191d988` | 19 Feb 2026 (URL) |
| `android-age-signals` | `https://developer.android.com/google/play/age-signals/overview` | `https://developer.android.com/google/play/age-signals/overview?auto_signin=false` | 200, 274,975 | `102dc2f9fcaf603bbe6dda75c4c29d42ca3f27154821516f4d0b621fc7d79ffe` | "Last updated 2026-07-20 UTC" |
| `apple-acct-deletion` | `https://developer.apple.com/help/app-review/guideline-reference/5-1-1-account-deletion` | the same | 200, 134,696 | `acebb536d55477d97d9e11e6d3a0a373b416bd452c26d5d8b4e6c56b899a74c4` | none found |
| `apple-age-assurance` | `https://developer.apple.com/support/age-assurance` | the same | 200, 121,964 | `674093936bacd4a489ff8b0612cd7b7683d03c98ae8d43b75e4a14cb8341d30d` | none found |
| `apple-arg` | `https://developer.apple.com/app-store/review/guidelines/` | the same | 200, 240,876 | `04d314bff0e31796247af6886247844a64c7c39ec1d1201cff89830349b0c230` | "Last Updated: October 16, 2026" |
| `apple-asc-manage-privacy` | `https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/` | the same | 200, 375,490 | `b57f8486c23b823f5c7ab0d9c9e2d38fe89641b0b46407402105abad949a3edb` | none found |
| `apple-dar-docs` | `https://developer.apple.com/tutorials/data/documentation/declaredagerange.json` | the same | 200, 9,672 | `4e4f4ce9e531c0914620157dadf40eff8bcc2cd530fb7ae812880207c240e2a8` | none found |
| `apple-dar-requesting` | `https://developer.apple.com/tutorials/data/documentation/declaredagerange/requesting-people-share-their-age-range-with-your-app.json` | the same | 200, 60,289 | `ff77411ed9028b6ac0312123b7b00d13f896c3bcb41441644c089fdcd116d718` | none found |
| `apple-dpla` | `https://developer.apple.com/support/terms/apple-developer-program-license-agreement/` | the same | 200, 849,495 | `85a739726b41ae6338798c7011af2161575b2c290b9111ff9a7f02ed79a6d811` | version stamp "LYL262 October 29, 2026" |
| `apple-news-8jzbigf4` | `https://developer.apple.com/news/?id=8jzbigf4` | the same | 200, 108,446 | `5af0169febd78bff2c8c2bb324ddbd7787830ecbc90f63c7b035a16670943b6b` | December 23, 2025 |
| `apple-news-ey6d8onl` | `https://developer.apple.com/news/?id=ey6d8onl` | the same | 200, 111,966 | `d80975b99899c39b47ef7c1bf2bd934956bc929c7499886d6b41e0ec0f25a596` | November 13, 2025 |
| `apple-news-f5zj08ey` | `https://developer.apple.com/news/?id=f5zj08ey` | the same | 200, 109,459 | `d537e0efbfc109591e3cbe3c6a66a4c9257cd384b4fe783c8a90ad1627064e69` | February 24, 2026 |
| `apple-news-list` | `https://developer.apple.com/news/` | the same | 200, 533,575 | `07ac546f2324bb9ec1b9d93cbde9e1510b928412f853b242f867e8954c9d8b54` | none found |
| `apple-news-sg176nne` | `https://developer.apple.com/news/?id=sg176nne` | the same | 200, 112,313 | `95c0b5e3735d30833a64553c36bedf9b5df3625a0fe48084c8b2819d64639802` | June 3, 2026 |
| `apple-news-vvzx6cul` | `https://developer.apple.com/news/?id=vvzx6cul` | the same | 200, 118,901 | `975f6edb5fc167ba2c9d96f89c9eaca2006a6893da7a77c3d036dd60e00f6397` | October 16, 2026 |
| `apple-privacy-details` | `https://developer.apple.com/app-store/app-privacy-details/` | the same | 200, 134,919 | `bb5cea6177f57d93bed618086068b118fbac135b9cc4193e82cd3bcad7007c99` | none found |
| `ca-ag-sb976` | `https://www.oag.ca.gov/sb976` | the same | 200, 48,588 | `f7cb3628268274cc62f661906a12d56f5f330b74f4c02b999d76e0318351901d` | "Notice Register Publication Date: May 15, 2026" |
| `ca5-25-51073` | `https://www.ca5.uscourts.gov/opinions/pub/25/25-51073-CV0.pdf` | the same | 200, 182,077 | `2f3c8d870e22515ca4e9c9aec20bf0fb5b01ef15235989eb3a67205e08b65e10` | order of 4 Jun 2026 |
| `ccpa-regs` | `https://cppa.ca.gov/regulations/pdf/ccpa_statute_eff_20260101.pdf` | the same | 200, 615,548 | `8d57eba97a7fe13346b7827d0131e1ab84dc110c6ff20daa6fa6ec4a4329d0fe` | "Effective 1/1/2026" |
| `ccpa-statute` | `https://cppa.ca.gov/regulations/pdf/ccpa_statute.pdf` | the same | 200, 772,399 | `0beb83ccf73d82ede066f7e4154952435484410f748da09ac4329ed9afe6a43f` | "effective 01/01/2025" |
| `co-4ccr904-5` | `https://coag.gov/app/uploads/2026/02/2026.2.4-Online-Dating-Safety-Rules-FINAL-DRAFT.pdf` | the same | 200, 120,287 | `2b7721bb5a545514d963cf7b6517aa1c9fa3a83852c15726168d4c8f58ddc100` | rules adopted 4 Feb 2026 (AG page) |
| `co-ag-dating` | `https://coag.gov/dating-safety/` | the same | 200, 62,770 | `f979cddd089ea481501ada46a82a967a72a96bfdeedb5ba0b558b3c0a992cac7` | none found |
| `co-crs2024-t6` | `https://content.leg.colorado.gov/sites/default/files/images/olls/crs2024-title-06.pdf` | the same | 200, 2,108,494 | `560ff6d64b5afdf2a3bc5ac917a392269d16270a029b252ff8f7957deb38b423` | "Colorado Revised Statutes 2024" (uncertified printout) |
| `co-sb24-011` | `https://content.leg.colorado.gov/sites/default/files/documents/2024A/bills/sl/2024a_sl_402.pdf` | the same | 200, 95,071 | `7bb8d21f748c3fc885c806ec4c714f109f7edd5c387f510badc2d735b3352ba8` | session law (2024) |
| `cybertip-api-doc` | `https://report.cybertip.org/ispws/documentation/index.html` | the same | 200, 169,982 | `e880713985e67ce2d684b5f6b6e06302db1cf198aee92440a8a317fa8bf37d9b` | "Last updated 2026-10-07" |
| `dutah-order` | `https://www.govinfo.gov/content/pkg/USCOURTS-utd-2_23-cv-00911/pdf/USCOURTS-utd-2_23-cv-00911-1.pdf` | the same | 200, 506,640 | `faa10f2d050841f0c2a3b074dc00d65a9416cf41d8e74cada7212d9914cd90bb` | order (2024) |
| `ecfr-16-312` | `https://www.ecfr.gov/api/versioner/v1/full/2026-10-29/title-16.xml?part=312` | the same | 200, 49,603 | `5a29d13e4512092a2d064a62a581031dc75aa99998540e6c2ef24f0dbfc66df9` | eCFR point-in-time 2026-10-29 |
| `ecfr-28-202` | `https://www.ecfr.gov/api/versioner/v1/full/2026-10-29/title-28.xml?part=202` | the same | 200, 473,095 | `76cac3b71b315fb64e6ec549a6d9d76228bd23e975a8600ff1f7284cca1b653c` | eCFR point-in-time 2026-10-29 |
| `fr-90-16918` | `https://www.govinfo.gov/content/pkg/FR-2025-04-22/html/2025-05904.htm` | the same | 200, 598,701 | `c165022b82aa0e86f931f4561e8b3f74f793878eceaada1d683a9136511e0b34` | 22 Apr 2025 |
| `ftc-coppa-faq` | `https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions` | the same | 404, 1,301 | `6cb6ddd1f7eefd58b6094bfb287c9fafa16b34eb1dfbf27416431220d9e45e5e` | none found |
| `ftc-mobile-app` | `https://www.ftc.gov/business-guidance/resources/marketing-your-mobile-app-get-it-right-start` | the same | 404, 1,301 | `6cb6ddd1f7eefd58b6094bfb287c9fafa16b34eb1dfbf27416431220d9e45e5e` | none found |
| `ftc-root` | `https://www.ftc.gov/` | the same | 404, 1,301 | `6cb6ddd1f7eefd58b6094bfb287c9fafa16b34eb1dfbf27416431220d9e45e5e` | — |
| `gp-10144311` | `https://support.google.com/googleplay/android-developer/answer/10144311?hl=en` | the same | 200, 1,681,319 | `b5f469ee05d3aac52e0f4c7e21a83bd350ebf03c9470ae981ce9935ad6ed8cb4` | none found |
| `gp-10787469` | `https://support.google.com/googleplay/android-developer/answer/10787469?hl=en` | the same | 200, 1,730,157 | `3cecd799961764699622fe78b592ca6abbdd66b2dd1f550ca946f3cfaf277268` | none found |
| `gp-11150561` | `https://support.google.com/googleplay/android-developer/answer/11150561?hl=en` | the same | 200, 1,635,330 | `3d816b774b5e87f39c2fa421fabde741eb6f8940061c2ddd77d31c4470316ee1` | none found |
| `gp-13327111` | `https://support.google.com/googleplay/android-developer/answer/13327111?hl=en` | the same | 200, 1,661,061 | `5d769e783a1133c2dc8cfaad06224426637c58af00a9e3315eecb1e8a6c968de` | none found |
| `gp-14747720` | `https://support.google.com/googleplay/android-developer/answer/14747720?hl=en` | the same | 200, 1,652,564 | `2023fe342d1aca086542361e077be2af717ef45768b90ca084b431fdbed415a0` | none found |
| `gp-16558241` | `https://support.google.com/googleplay/android-developer/answer/16558241?hl=en` | the same | 200, 1,712,671 | `82072f1d7da95767f73ec0762dbdea55ac3b5aa3418f57f973ab1de2367925df` | "Effective January 27, 2027" |
| `gp-16569691` | `https://support.google.com/googleplay/android-developer/answer/16569691?hl=en` | the same | 200, 1,653,692 | `dbcb1ff1adabd5c61617390d6e3b782bff5352cb2c8540ff94553dbe2c37ce79` | none found |
| `gp-18265346` | `https://support.google.com/googleplay/android-developer/answer/18265346?hl=en` | the same | 200, 1,942,720 | `6c9b53197688df84156a1f06f0b6c40c4b371ef9f46230c3375d3274744d8c97` | "Effective July 12, 2023" |
| `gp-9859455` | `https://support.google.com/googleplay/android-developer/answer/9859455?hl=en` | the same | 200, 1,654,290 | `ec49f64d02817f966c4c1e35b65dd9bf73df3904c6a7471f4558fc209f29e8b7` | none found |
| `gp-9878809` | `https://support.google.com/googleplay/android-developer/answer/9878809?hl=en` | the same | 200, 1,635,117 | `ec3c2d2758b0d806cee444d4b66a2564f2cbcd6f710cfddffe0ed5ddfd064e84` | none found |
| `gp-dda` | `https://play.google/developer-distribution-agreement.html` | the same | 200, 52,915 | `8feae3149985efda8c4777dc6d64a63e7fcdca60ca90de65e31f03316b833faf` | "Effective as of September 15, 2025" |
| `il-bipa` | `https://www.ilga.gov/Legislation/ILCS/Articles?ActID=3004&ChapterID=57` | the same | 200, 87,164 | `68284b94dc42a45b54e8a994293a69d2b9300eab237ba499489f103dc91f93f4` | latest source P.A. 103-769 (2024) |
| `kelleydrye-ab1043` | `https://www.kelleydrye.com/viewpoints/blogs/ad-law-access/faq-digital-age-assurance-act-california-youth-safety-on-the-internet` | the same | 200, 152,883 | `f2843da357690dfb16ea8e2e49d6a7cdeb353b136c1e65da7b665c4f4398b5cc` | October 2025 (secondary) |
| `la-act185` | `https://www.legis.la.gov/Legis/ViewDocument.aspx?d=1475238` | the same | 200, 82,361 | `b4331c6182baff86794c1d641125c88465c48515765d10340fd8f391f17ddb67` | Act 185 (2026) |
| `la-hb977-status` | `https://legis.la.gov/legis/BillInfo.aspx?s=26RS&b=HB977&sbi=y` | the same | 200, 76,770 | `3422360417e70784cda601191e850c6ea2b0445ec65b5a1ba38d14a0473ccd5a` | signed 05/15 (2026) |
| `ncmec-data` | `https://www.missingkids.org/gethelpnow/cybertipline/cybertiplinedata` | the same | 200, 725,469 | `7c1e1294ac58f80d3bcf2588311f282b6596134c5dcb2db7bd110c8561723970` | none found |
| `ncmec-report-act` | `https://cf.missingkids.org/content/dam/missingkids/pdfs/NCMEC-REPORT-Act-Guidelines.pdf` | the same | 200, 2,610,786 | `336dca9f5a893ee884fac1e4beed335ad8662eb5aac4c57d13b215d2922b3e1e` | "Copyright © 2024" |
| `ny-ag-safe` | `https://ag.ny.gov/press-release/2026/attorney-general-james-and-governor-hochul-release-final-safe-kids-act-rules` | the same | 200, 60,731 | `fba7f754b25f5dbbcbbb5362e71858ca6727a923b26a8fa674875d1a0ffe3e61` | July 28, 2026 |
| `plaw-118-59` | `https://www.govinfo.gov/content/pkg/PLAW-118publ59/html/PLAW-118publ59.htm` | the same | 200, 11,963 | `a130e131284f55b635a165e217fcfa2d21ed4a5da0fb356c4c5382b13bd36180` | 7 May 2024 |
| `scotus-070626` | `https://www.supremecourt.gov/orders/courtorders/070626zr1_dc8f.pdf` | the same | 200, 29,502 | `964c507f4092487b40812fe84d9f63da375b373aa8e933626b01f9c395a4f44c` | "MONDAY, JULY 6, 2026" |
| `tx-bc-541` | `https://tcss.legis.texas.gov/resources/BC/htm/BC.541.htm` | the same | 200, 80,485 | `1f56ef0a23bae698ba6234921a4dded70a2444059214093791dcc8d7797591be` | none found |
| `tx-sb2420` | `https://capitol.texas.gov/tlodocs/89R/billtext/html/SB02420F.htm` | the same | 200, 102,413 | `95db4ee9d15537a44fbe3ed5257726dafe71b051fc432655802befc5cbea0f5c` | enrolled text |
| `usc-15-45` | `https://www.govinfo.gov/link/uscode/15/45?link-type=html&year=2024` | `https://www.govinfo.gov/content/pkg/USCODE-2024-title15/html/USCODE-2024-title15-chap2-subchapI-sec45.htm` | 200, 47,198 | `28de76e074dde70c74930d24738fda83a837c04bba6304c148051d1600679546` | 2024 edition |
| `usc-15-6502` | `https://www.govinfo.gov/link/uscode/15/6502?link-type=html&year=2024` | `https://www.govinfo.gov/content/pkg/USCODE-2024-title15/html/USCODE-2024-title15-chap91-sec6502.htm` | 200, 9,965 | `019202fb7d756918bced071c46b75c082d88c37a365f9fd0d8e3ccfa1f483980` | 2024 edition |
| `usc-15-9901` | `https://www.govinfo.gov/link/uscode/15/9901?link-type=html&year=2024` | `https://www.govinfo.gov/content/pkg/USCODE-2024-title15/html/USCODE-2024-title15-chap123-sec9901.htm` | 200, 32,740 | `c91d6478418ff2243e94afc3ab65c6b67e4b58cfca0d911841b6e47080a1bc24` | 2024 edition |
| `usc-18-2258A` | `https://www.govinfo.gov/content/pkg/USCODE-2024-title18/html/USCODE-2024-title18-partI-chap110-sec2258A.htm` | the same | 200, 33,987 | `65fc4ae66a912cfe87ff2fee671433dd77db12ac8397c4ea9c59f06fb222708c` | 2024 edition |
| `usc-18-2258B` | `https://www.govinfo.gov/content/pkg/USCODE-2024-title18/html/USCODE-2024-title18-partI-chap110-sec2258B.htm` | the same | 200, 12,777 | `786f42cfb743ff9f78d7995f48212089e15968ca5122c695de3de48674251579` | 2024 edition |
| `usc-18-2258C` | `https://www.govinfo.gov/content/pkg/USCODE-2024-title18/html/USCODE-2024-title18-partI-chap110-sec2258C.htm` | the same | 200, 8,797 | `d47aebf94c0db894659deb478c11b6fe0a6951fde25dd5efd2699541faef88f0` | 2024 edition |
| `usc-18-2258E` | `https://www.govinfo.gov/content/pkg/USCODE-2024-title18/html/USCODE-2024-title18-partI-chap110-sec2258E.htm` | the same | 200, 4,066 | `89c2d5f420abdfe08d45ab659ae44def18b3e7fdb7ddbc97d868f4a0d18c7a18` | 2024 edition |
| `ut-13-71` | `https://le.utah.gov/xcode/Title13/Chapter71/C13-71_2024100120240501.pdf` | the same | 200, 16,118 | `9d5f78fe2cb517a304066a4442f6f3975e1c4a6a154b414e167f48f751119c81` | "Effective 10/1/2024" |
| `ut-13-71-index` | `https://le.utah.gov/xcode/Title13/Chapter71/13-71.html` | the same | 200, 26,614 | `0b3684ffff7c067598c3da9a97a900cf9c90d46f981937ce7b1e4ef1bd5f0c96` | — |
| `ut-13-76` | `https://le.utah.gov/xcode/Title13/Chapter76/C13-76_2025050720250507.pdf` | the same | 200, 16,514 | `342243680f903b6aa5751cae2cc35c9bc8a710ec3dd672be77ecbfed232ccc85` | "Effective 5/7/2025" |
| `ut-13-76-index` | `https://le.utah.gov/xcode/Title13/Chapter76/13-76.html` | the same | 200, 26,614 | `1d06056e8a4868fc2b2df4ad84bbec85db3edb57c44f214d69c423762bc0564d` | — |
| `va-59.1-575` | `https://law.lis.virginia.gov/vacode/title59.1/chapter53/section59.1-575/` | the same | 200, 38,952 | `362471406ae02b2e5f533428990441b13949158d31d247f4b8dd95f1f386f5cc` | none found |
| `va-59.1-578` | `https://law.lis.virginia.gov/vacode/title59.1/chapter53/section59.1-578/` | the same | 200, 35,732 | `60e472b9413d5cc8a3147627884cc26f1784d11b9e7e725d386c0aa48e713f4a` | none found |

**California's bulk data, read by byte range.** `https://downloads.leginfo.legislature.ca.gov/pubinfo_2025.zip`: `200`, 1,292,263,530 bytes, `Last-Modified: Mon, 16 Nov 2026 05:26:36 GMT`, ETag `"4d06606a-6605e05841b00"`, 205,287 members. The members read, each hashed after extraction:

| Member | Bytes | SHA-256 |
|---|---|---|
| `LAW_SECTION_TBL.dat` | 43,309,305 | `a8f35d3749b06195ebbc94252b4101f37c48256491fe051ab12cab6ddec5334c` |
| `LAW_SECTION_TBL_24675.lob` | 4,988 | `0ff9f248d184bb9b7b98de994e990d5e584ac4e5fa6179222854c42ae4bec49e` |
| `LAW_SECTION_TBL_24999.lob` | 2,842 | `11940ed3e8e111c31736a25e97b72b16a524bd471feaec1483272034c67d1d49` |
| `LAW_SECTION_TBL_25000.lob` | 3,293 | `d5702d3d36c03e29beeafd085d43d8e1d2261651ee791a27e3f517b3e811ca2b` |
| `LAW_SECTION_TBL_33594.lob` | 933 | `fa0258257fac23850a33703bda2ded134bed3acd1e88d96cff20362e5a8fa599` |
| `LAW_SECTION_TBL_33389.lob` | 1,000 | `1e644eb4e20953f21091e40be7707d922118ee58e7319a210b2785007c51b654` |
| `LAW_SECTION_TBL_25001.lob` | 2,606 | `996a2888a62bd1f90caf4af65f57194c348c0c6fa4b1aeb5ee073a313b57415e` |
| `LAW_SECTION_TBL_25002.lob` | 149 | `4ddc4fc44a05a479d5705845677e15cb89d39dad21128d65f5eec359b16c9555` |
| `LAW_SECTION_TBL_86392.lob` | 1,259 | `6d5f92fc9f4d1fcf8a3b4fcda46e02633a54a816ac5b7a83ded0cd639cceba70` |
| `LAW_SECTION_TBL_86485.lob` | 1,112 | `0aeaf3062638bbd00084aaa74d72bfb7935bb7bd967b46343c225ec2ed7b03cb` |
| `LAW_SECTION_TBL_44569.lob` | 3,250 | `c5a9cfa5a93c3387a0807f4dd2b78cf17cf0e40d0bf6153a8f305f02bb42a7ee` |
| `LAW_SECTION_TBL_25818.lob` | 2,392 | `ae7e34f96a204b31cd1ae24b77aa27f918d396fb736dabcb2e4cf9ba684177e3` |
| `LAW_SECTION_TBL_25819.lob` | 5,463 | `ce061b262f6c1df7fbbbfab8c2c9690b6918d5cfc2b3e5198b1b0e91e36d7013` |
| `LAW_SECTION_TBL_25820.lob` | 3,895 | `af7e0dec80993979b0177f7cc51b60ea3e4cca7cfc9f224db50ba82a159b86e3` |
| `LAW_SECTION_TBL_25821.lob` | 196 | `f637b1b6f20ff4c485c1fafda0923d78fd9ae2ab4e89c0e071477410b5ab6967` |
| `LAW_SECTION_TBL_25822.lob` | 343 | `b8f6b9a51a48c1d28781e8e5f6aea7b4b589aba770a0d6da10c770a2710475e5` |
| `LAW_SECTION_TBL_44568.lob` | 156 | `8ab75116878f71b87b1d55f2cca041331ef6598adef087687f6ad507205e6abd` |
| `BILL_VERSION_TBL.dat` | 4,512,719 | `2c4eebab90988ec5c569f3db33ab0ade9f6683458fc986e87676a46839482044` |
| `BILL_TBL.dat` | 954,316 | `57283fd9935200e27255e4938338815409a6e3b16fde218d46ae5e8bce79cbcd` |
| `BILL_VERSION_TBL_18610.lob` | 23,397 | `473514267202c76d483868a42c31a8bf8721b2bcab76510439176314989ce403` |
| `BILL_VERSION_TBL_19051.lob` | 28,393 | `4f5ba2af452e4f845d498376a5af20f19219c0edea18bf8413428e9787ba11e6` |

The section numbers map to members through `LAW_SECTION_TBL.dat`: §1798.105 `24675`; §1798.500 to §1798.505 `24999`, `25000`, `33594`, `33389`, `25001`, `25002`; Health and Safety Code §27001 `86392`; §28000 to §28002 `44568`, `86485`, `44569`; Civil Code §3273.65 to §3273.69 `25818` to `25822`. The member numbers differ from those P09.3a's record cites, because the file is regenerated; the sections are the same. AB 1856 (chaptered, Stats. 2026, ch. 184) is `BILL_VERSION_TBL_18610`, and SB 923 (chaptered, Stats. 2026, ch. 482) is `BILL_VERSION_TBL_19051`.

## 4. The quotation checks, row by row

One line per row. "Exact" means the row's quotation (split at its ellipses) was found as one continuous string in the stripped text; "normalised" says what was normalised, and the passage was then read in place.

| Row | Source read (fetch name) | SHA-256 | Result |
|---|---|---|---|
| UST-51 | `il-bipa` | `68284b94dc42a45b54e8a994293a69d2b9300eab237ba499489f103dc91f93f4` | Confirmed: all four fragments exact. Status corrected for OD-61 (below); precision added |
| UST-42 | `ccpa-statute` | `0beb83ccf73d82ede066f7e4154952435484410f748da09ac4329ed9afe6a43f` | Confirmed: both fragments exact (the agency's posted copy). Precision added |
| UST-44 | `ccpa-regs` | `8d57eba97a7fe13346b7827d0131e1ab84dc110c6ff20daa6fa6ec4a4329d0fe` | Confirmed: both fragments exact |
| UST-45 | `tx-bc-541` | `1f56ef0a23bae698ba6234921a4dded70a2444059214093791dcc8d7797591be` | Confirmed after normalising one space the tag stripping added ("541.002 (a)(3)"), as at OD-60's recheck; read in place. Precision added |
| UST-46 | `tx-bc-541` | `1f56ef0a23bae698ba6234921a4dded70a2444059214093791dcc8d7797591be` | Confirmed: exact |
| UST-47 | `va-59.1-578`<br>`va-59.1-575` | `60e472b9413d5cc8a3147627884cc26f1784d11b9e7e725d386c0aa48e713f4a`<br>`362471406ae02b2e5f533428990441b13949158d31d247f4b8dd95f1f386f5cc` | Confirmed: exact in §59.1-578; the definitions read in §59.1-575. Precision added |
| UST-48 | `co-crs2024-t6` | `560ff6d64b5afdf2a3bc5ac917a392269d16270a029b252ff8f7957deb38b423` | Confirmed: exact (the same file as on 10 and 11 November). Precision added |
| USF-13 | `usc-15-45`<br>`ftc-mobile-app` | `28de76e074dde70c74930d24738fda83a837c04bba6304c148051d1600679546`<br>`6cb6ddd1f7eefd58b6094bfb287c9fafa16b34eb1dfbf27416431220d9e45e5e` | Statute confirmed: exact. Guidance not re-read: `404`, 1,301 bytes (the same refusal as on 10 November; the FTC home page answers the same) |
| USF-21 | `usc-15-9901` | `c91d6478418ff2243e94afc3ab65c6b67e4b58cfca0d911841b6e47080a1bc24` | Confirmed: exact |
| USF-22 | `ecfr-28-202` | `76cac3b71b315fb64e6ec549a6d9d76228bd23e975a8600ff1f7284cca1b653c` | Confirmed: both fragments exact. Precision added (biometric identifiers, 1,000-person threshold) |
| AP-14 | `apple-age-assurance` | `674093936bacd4a489ff8b0612cd7b7683d03c98ae8d43b75e4a14cb8341d30d` | Confirmed: both quotations exact. Precision added (iOS 26.5's `confirmed` value) |
| AP-15 | `apple-news-sg176nne`<br>`apple-news-8jzbigf4` | `95c0b5e3735d30833a64553c36bedf9b5df3625a0fe48084c8b2819d64639802`<br>`5af0169febd78bff2c8c2bb324ddbd7787830ecbc90f63c7b035a16670943b6b` | Confirmed: both quotations exact; the pause notice of 23 December 2025 read |
| AP-16 | `apple-news-f5zj08ey`<br>`apple-dar-requesting` | `d537e0efbfc109591e3cbe3c6a66a4c9257cd384b4fe783c8a90ad1627064e69`<br>`ff77411ed9028b6ac0312123b7b00d13f896c3bcb41441644c089fdcd116d718` | Confirmed: exact; the significant-update text read in both |
| AP-17 | `apple-dpla` | `85a739726b41ae6338798c7011af2161575b2c290b9111ff9a7f02ed79a6d811` | Confirmed: exact |
| AP-19 | `kelleydrye-ab1043`<br>`apple-news-list` | `f2843da357690dfb16ea8e2e49d6a7cdeb353b136c1e65da7b665c4f4398b5cc`<br>`07ac546f2324bb9ec1b9d93cbde9e1510b928412f853b242f867e8954c9d8b54` | No quotation in the row (secondary only). The secondary page still says the Act "takes effect on January 1, 2027" (exact). Still UNCONFIRMED: Apple's Q&A and news list name no California guidance |
| AP-31 | `apple-arg` | `04d314bff0e31796247af6886247844a64c7c39ec1d1201cff89830349b0c230` | Confirmed: exact ("Last Updated: October 16, 2026") |
| GP-15 | `gp-18265346`<br>`gp-16569691` | `6c9b53197688df84156a1f06f0b6c40c4b371ef9f46230c3375d3274744d8c97`<br>`dbcb1ff1adabd5c61617390d6e3b782bff5352cb2c8540ff94553dbe2c37ce79` | Confirmed: exact; "Google Play doesn’t mandate the use of these features" exact in answer 16569691 |
| GP-16 | `gp-16569691`<br>`android-age-signals` | `dbcb1ff1adabd5c61617390d6e3b782bff5352cb2c8540ff94553dbe2c37ce79`<br>`102dc2f9fcaf603bbe6dda75c4c29d42ca3f27154821516f4d0b621fc7d79ffe` | **Not found:** both quotations are absent from answer 16569691 today. Replacement quotations exact in the Age Signals overview and answer 16569691. Requirement unchanged; quotations and lead sentence corrected |
| UST-32 | `tx-sb2420`<br>`ca5-25-51073`<br>`scotus-070626` | `95db4ee9d15537a44fbe3ed5257726dafe71b051fc432655802befc5cbea0f5c`<br>`2f3c8d870e22515ca4e9c9aec20bf0fb5b01ef15235989eb3a67205e08b65e10`<br>`964c507f4092487b40812fe84d9f63da375b373aa8e933626b01f9c395a4f44c` | Confirmed: three fragments exact; the stay order and the order denying vacatur exact. A merits decision: none found (web search only) |
| UST-33 | `ut-13-76`<br>`ut-13-76-index` | `342243680f903b6aa5751cae2cc35c9bc8a710ec3dd672be77ecbfed232ccc85`<br>`1d06056e8a4868fc2b2df4ad84bbec85db3edb57c44f214d69c423762bc0564d` | Confirmed: exact; the chapter index lists only this version |
| UST-34 | `la-act185`<br>`la-hb977-status` | `b4331c6182baff86794c1d641125c88465c48515765d10340fd8f391f17ddb67`<br>`3422360417e70784cda601191e850c6ea2b0445ec65b5a1ba38d14a0473ccd5a` | Confirmed: exact; status "Signed by the Governor - Act 185" exact |
| UST-35 | `bulk: BILL_VERSION_TBL_18610.lob`<br>`bulk: LAW_SECTION_TBL_25000.lob` | `473514267202c76d483868a42c31a8bf8721b2bcab76510439176314989ce403`<br>`d5702d3d36c03e29beeafd085d43d8e1d2261651ee791a27e3f517b3e811ca2b` | Confirmed: exact in AB 1856's chaptered text; the code table still has AB 1043's "when the application is downloaded and launched" (exact), as the manager's note says |
| UST-36 | `al-hb161`<br>`al-hb161-status` | `b4672a280178426355dec957e03343e286109540641303d661e2d34b6aa00d33`<br>`53a0a5ae2cea271bfd63fcdb03264e48c81bea6ef2ec41b11c55cfc0aa09d895` | Enactment now confirmed: "Act No. 2026-59 Effective Date Certain Friday, January 1, 2027" exact on the Legislature's page. The duty matched after removing the PDF's line number "186", read in place. UNCONFIRMED removed |
| UST-37 | `bulk: LAW_SECTION_TBL_86392.lob`<br>`ca-ag-sb976` | `6d5f92fc9f4d1fcf8a3b4fcda46e02633a54a816ac5b7a83ded0cd639cceba70`<br>`f7cb3628268274cc62f661906a12d56f5f330b74f4c02b999d76e0318351901d` | Confirmed: the statute's quotation exact (bulk data, by byte range); the AG page still reviewing comments (exact) |
| UST-38 | `ny-ag-safe` | `fba7f754b25f5dbbcbbb5362e71858ca6727a923b26a8fa674875d1a0ffe3e61` | Confirmed: exact; the rule text itself again not read |
| UST-39 | `bulk: LAW_SECTION_TBL_44569.lob` | `c5a9cfa5a93c3387a0807f4dd2b78cf17cf0e40d0bf6153a8f305f02bb42a7ee` | Confirmed: both fragments exact (bulk data, by byte range) |
| UST-40 | `ut-13-71`<br>`ut-13-71-index`<br>`dutah-order` | `9d5f78fe2cb517a304066a4442f6f3975e1c4a6a154b414e167f48f751119c81`<br>`0b3684ffff7c067598c3da9a97a900cf9c90d46f981937ce7b1e4ef1bd5f0c96`<br>`faa10f2d050841f0c2a3b074dc00d65a9416cf41d8e74cada7212d9914cd90bb` | Confirmed: exact; the chapter index lists only this version; the order grants the preliminary injunction. The appeal's outcome: none found (web search only); still UNCONFIRMED |
| UST-41 | `co-crs2024-t6` | `560ff6d64b5afdf2a3bc5ac917a392269d16270a029b252ff8f7957deb38b423` | Confirmed: exact |
| USF-11 | `usc-15-6502`<br>`ecfr-16-312`<br>`fr-90-16918`<br>`ftc-coppa-faq` | `019202fb7d756918bced071c46b75c082d88c37a365f9fd0d8e3ccfa1f483980`<br>`5a29d13e4512092a2d064a62a581031dc75aa99998540e6c2ef24f0dbfc66df9`<br>`c165022b82aa0e86f931f4561e8b3f74f793878eceaada1d683a9136511e0b34`<br>`6cb6ddd1f7eefd58b6094bfb287c9fafa16b34eb1dfbf27416431220d9e45e5e` | Confirmed: the statute exact; the Rule's actual-knowledge text exact (the eCFR answered `200` today); the compliance date exact. FAQ not re-read (`404`) |
| AP-22 | `apple-privacy-details`<br>`apple-asc-manage-privacy` | `bb5cea6177f57d93bed618086068b118fbac135b9cc4193e82cd3bcad7007c99`<br>`b57f8486c23b823f5c7ab0d9c9e2d38fe89641b0b46407402105abad949a3edb` | Confirmed: exact; "those of third-party partners whose code you integrate into your app" exact |
| AP-23 | `apple-privacy-details` | `bb5cea6177f57d93bed618086068b118fbac135b9cc4193e82cd3bcad7007c99` | Confirmed: exact. Precision added ("biometric data") |
| AP-27 | `apple-arg` | `04d314bff0e31796247af6886247844a64c7c39ec1d1201cff89830349b0c230` | Confirmed: exact |
| AP-29 | `apple-arg` | `04d314bff0e31796247af6886247844a64c7c39ec1d1201cff89830349b0c230` | Confirmed: exact |
| AP-30 | `apple-arg`<br>`apple-news-ey6d8onl` | `04d314bff0e31796247af6886247844a64c7c39ec1d1201cff89830349b0c230`<br>`d80975b99899c39b47ef7c1bf2bd934956bc929c7499886d6b41e0ec0f25a596` | Confirmed: exact in both |
| GP-24 | `gp-10787469` | `3cecd799961764699622fe78b592ca6abbdd66b2dd1f550ca946f3cfaf277268` | Confirmed: exact |
| GP-25 | `gp-10787469` | `3cecd799961764699622fe78b592ca6abbdd66b2dd1f550ca946f3cfaf277268` | Confirmed: exact |
| GP-26 | `gp-10787469` | `3cecd799961764699622fe78b592ca6abbdd66b2dd1f550ca946f3cfaf277268` | Confirmed: exact |
| GP-27 | `gp-10144311` | `b5f469ee05d3aac52e0f4c7e21a83bd350ebf03c9470ae981ce9935ad6ed8cb4` | Confirmed: exact |
| GP-29 | `gp-10144311` | `b5f469ee05d3aac52e0f4c7e21a83bd350ebf03c9470ae981ce9935ad6ed8cb4` | Confirmed: both fragments exact |
| GP-30 | `gp-10144311` | `b5f469ee05d3aac52e0f4c7e21a83bd350ebf03c9470ae981ce9935ad6ed8cb4` | Confirmed: exact |
| GP-32 | `gp-dda` | `8feae3149985efda8c4777dc6d64a63e7fcdca60ca90de65e31f03316b833faf` | Confirmed: exact ("Effective as of September 15, 2025") |
| AP-21 | `apple-arg`<br>`apple-news-vvzx6cul`<br>`apple-dpla` | `04d314bff0e31796247af6886247844a64c7c39ec1d1201cff89830349b0c230`<br>`975f6edb5fc167ba2c9d96f89c9eaca2006a6893da7a77c3d036dd60e00f6397`<br>`85a739726b41ae6338798c7011af2161575b2c290b9111ff9a7f02ed79a6d811` | Confirmed: exact; the news item and DPLA §3.2 clause exact |
| GP-18 | `gp-14747720` | `2023fe342d1aca086542361e077be2af717ef45768b90ca084b431fdbed415a0` | Confirmed: both quotations exact |
| GP-19 | `gp-14747720`<br>`gp-9878809` | `2023fe342d1aca086542361e077be2af717ef45768b90ca084b431fdbed415a0`<br>`ec3c2d2758b0d806cee444d4b66a2564f2cbcd6f710cfddffe0ed5ddfd064e84` | Confirmed: exact in answer 14747720, the row's second source; answer 9878809 states the duty in other words (exact) |
| GP-20 | `gp-9878809` | `ec3c2d2758b0d806cee444d4b66a2564f2cbcd6f710cfddffe0ed5ddfd064e84` | Confirmed: exact |
| GP-21 | `gp-9878809` | `ec3c2d2758b0d806cee444d4b66a2564f2cbcd6f710cfddffe0ed5ddfd064e84` | Confirmed: exact |
| GP-22 | `gp-14747720` | `2023fe342d1aca086542361e077be2af717ef45768b90ca084b431fdbed415a0` | Confirmed: exact |
| GP-23 | `gp-9878809` | `ec3c2d2758b0d806cee444d4b66a2564f2cbcd6f710cfddffe0ed5ddfd064e84` | Confirmed: both quotations exact |
| USF-01 | `usc-18-2258A`<br>`usc-18-2258E` | `65fc4ae66a912cfe87ff2fee671433dd77db12ac8397c4ea9c59f06fb222708c`<br>`89c2d5f420abdfe08d45ab659ae44def18b3e7fdb7ddbc97d868f4a0d18c7a18` | Confirmed: exact; the fines and the definition of "provider" read |
| USF-02 | `usc-18-2258A`<br>`ncmec-report-act` | `65fc4ae66a912cfe87ff2fee671433dd77db12ac8397c4ea9c59f06fb222708c`<br>`336dca9f5a893ee884fac1e4beed335ad8662eb5aac4c57d13b215d2922b3e1e` | Confirmed: the statute exact; NCMEC's sentence exact in a raw-order extraction (`pdftotext -raw`) of the two-column PDF, not in the layout extraction |
| USF-03 | `usc-18-2258A`<br>`cybertip-api-doc` | `65fc4ae66a912cfe87ff2fee671433dd77db12ac8397c4ea9c59f06fb222708c`<br>`e880713985e67ce2d684b5f6b6e06302db1cf198aee92440a8a317fa8bf37d9b` | Confirmed: exact; the API's cardinality table read |
| USF-04 | `usc-18-2258A`<br>`plaw-118-59` | `65fc4ae66a912cfe87ff2fee671433dd77db12ac8397c4ea9c59f06fb222708c`<br>`a130e131284f55b635a165e217fcfa2d21ed4a5da0fb356c4c5382b13bd36180` | Confirmed: exact; the Cybersecurity Framework clause exact |
| USF-05 | `usc-18-2258B` | `786f42cfb743ff9f78d7995f48212089e15968ca5122c695de3de48674251579` | Confirmed: exact |
| USF-06 | `usc-18-2258A` | `65fc4ae66a912cfe87ff2fee671433dd77db12ac8397c4ea9c59f06fb222708c` | Confirmed: both fragments exact |
| USF-07 | `usc-18-2258A`<br>`usc-18-2258C`<br>`ncmec-data` | `65fc4ae66a912cfe87ff2fee671433dd77db12ac8397c4ea9c59f06fb222708c`<br>`d47aebf94c0db894659deb478c11b6fe0a6951fde25dd5efd2699541faef88f0`<br>`7c1e1294ac58f80d3bcf2588311f282b6596134c5dcb2db7bd110c8561723970` | Confirmed: both fragments exact; §2258C's use limit read |
| UST-49 | `bulk: LAW_SECTION_TBL_25819.lob` | `ce061b262f6c1df7fbbbfab8c2c9690b6918d5cfc2b3e5198b1b0e91e36d7013` | Confirmed: exact (bulk data, by byte range); the 36-hour, 7-day and final-determination clauses read |
| AP-33 | `apple-acct-deletion` | `acebb536d55477d97d9e11e6d3a0a373b416bd452c26d5d8b4e6c56b899a74c4` | Confirmed: exact |
| GP-33 | `gp-10144311`<br>`gp-13327111` | `b5f469ee05d3aac52e0f4c7e21a83bd350ebf03c9470ae981ce9935ad6ed8cb4`<br>`5d769e783a1133c2dc8cfaad06224426637c58af00a9e3315eecb1e8a6c968de` | Confirmed: exact in answer 10144311; answer 13327111's "request the service provider to do the same" exact |
| UST-43 | `bulk: LAW_SECTION_TBL_24675.lob`<br>`ccpa-statute`<br>`bulk: BILL_VERSION_TBL_19051.lob` | `0ff9f248d184bb9b7b98de994e990d5e584ac4e5fa6179222854c42ae4bec49e`<br>`0beb83ccf73d82ede066f7e4154952435484410f748da09ac4329ed9afe6a43f`<br>`4f5ba2af452e4f845d498376a5af20f19219c0edea18bf8413428e9787ba11e6` | Confirmed: exact in the code table and the agency's copy. Precision added (SB 923's amendment) |
| UST-20 | `co-sb24-011`<br>`co-4ccr904-5`<br>`co-ag-dating` | `7bb8d21f748c3fc885c806ec4c714f109f7edd5c387f510badc2d735b3352ba8`<br>`2b7721bb5a545514d963cf7b6517aa1c9fa3a83852c15726168d4c8f58ddc100`<br>`f979cddd089ea481501ada46a82a967a72a96bfdeedb5ba0b558b3c0a992cac7` | Confirmed after normalising a space before the full stop in the session law PDF; read in place. The rules' item 6 matched after normalising the "ﬁ" ligature. Precision added |


## 5. What changed in the matrix

### 5.1 Requirements or status corrected (old and new text)

**GP-16: the source's wording changed; the requirement stands.** Answer 16569691 no longer names SB 2420 or says it is in effect, and its sentence on responsibility now reads "whether and how". Google's Age Signals overview still says signals flow for Texas under SB 2420.
- Old (Requirement cell): *Texas SB 2420 is in effect on Play; developers must work out their own obligations. "Texas’ App Store Accountability Act, Texas SB 2420, is now in effect after a federal appeals court stayed the preliminary injunction issued in December 2025." "It is your responsibility to determine how these laws apply to your app…" Age signals flow for eligible Texas accounts created after 28 May 2026*
- New: *Google Play returns age signals for Texas accounts under SB 2420; developers must work out their own obligations. "The API has started returning age signals for eligible users in Texas who created their accounts after May 28, 2026 as part of our compliance efforts for Texas SB2420." (Age Signals overview) "It is your responsibility to determine whether and how these laws apply to your app, and whether and how to use these features to meet your obligations." (answer 16569691)*, with a bracketed note that it was corrected at this recheck.
- Google's page still says *"Google Play doesn’t mandate the use of these features."* (exact), so section 9's sentence on GP-15 and GP-16 still holds.

**UST-36: enactment confirmed; the UNCONFIRMED mark is removed.** The Legislature's bill page gives *"Last Action 2/17/2026 - House Enacted - 2026-59"* and *"Act No. 2026-59 Effective Date Certain Friday, January 1, 2027"* (both exact).
- Old (Requirement cell): *Alabama HB 161: from 1 January 2027, developers verify age category through the store. **UNCONFIRMED (enactment):** the enrolled text was read; the governor's signature rests on a secondary source*
- New: *Alabama HB 161 (Act 2026-59): from 1 January 2027, developers verify age category through the store. "Verify through the app store's data sharing methods: (i) the age category of users located in this state"*, with the correction noted.
- Old (Binds): *Alabama, if enacted*. New: *Alabama, from 1 January 2027* (marked).
- Source cell: the Legislature's bill page added.
- A secondary tracker found by web search reports a CCIA suit against the Act on 28 October 2026. **UNCONFIRMED**; not checked in a court record.

**UST-51: the requirement is unchanged; its status changed with OD-61.** The row's condition, "if Glow ever scans face geometry", was stated as "none planned". OD-61 (10 November 2026) plans identity verification that matches a selfie to the ID photo.
- Binds. Old: *Only if Glow ever scans face geometry (none planned)*. New: *Only if Glow scans face geometry. OD-61 (10 November 2026) plans identity verification that matches a selfie to the ID photo, through a verification company …; whether Glow, the company or both collect or possess the data under §15 is a reading for counsel.*
- Asks. Old: *Nothing today*. New: the §15 duties, stated as what it would ask if it applies.
- Owner. Old: *—*. New: *P08 (consent wording), after OD-61's decision message* (a routing suggestion; see section 10).
- State. Old: *Not applicable*. New: *Not applicable at `f40f1d7` (nothing scans a face); OD-61 plans the face match, and the consent waits on its decision message.*

**Section 10, dated events.** Old: *Alabama HB 161 (enactment unconfirmed)*. New: *Alabama HB 161 (Act 2026-59) [corrected at the A05-V recheck: this said "enactment unconfirmed"; the Legislature's bill page confirms it]*. No other sentence of sections 9 or 10 states a row whose requirement or status changed (section 10 below lists sentences that new rows make incomplete, outside this session's owned scope).

### 5.2 Precisions added (no requirement changed)

Each is marked "[precision added at the A05-V recheck: …]" in its row.

| Row | Precision | Source (fetch name) |
|---|---|---|
| AP-14 | As of iOS 26.5, a range *"confirmed using a credit card or government ID"* returns a single `confirmed` value, no longer naming the method; apps are asked to handle it and rebuild against the iOS 26.5 SDK | `apple-age-assurance` |
| AP-23 | Sensitive Info also lists *"genetic information, or biometric data"* | `apple-privacy-details` |
| UST-20 | The rules' annual report asks for *"Information on enforcement of the Online Dating Service Member identity verification and age verification policies during the reporting period"*, including the numbers removed or not allowed on the service as a result of each | `co-4ccr904-5` (matched after normalising the "ﬁ" ligature) |
| UST-35 | AB 1856: a developer with *"internal clear and convincing information that a user’s age is different than the age indicated by a signal"* uses that information as the primary indicator, with actual knowledge | bulk `BILL_VERSION_TBL_18610.lob` |
| UST-42 | Sensitive personal information also includes the processing of biometric information to identify a consumer, and driver's license and state ID numbers | `ccpa-statute` |
| UST-43 | SB 923 (Stats. 2026, ch. 482) amends §1798.105(a) to *"collected from or about the consumer"* and adds the online method; the code table is unchanged | bulk `BILL_VERSION_TBL_19051.lob`, `LAW_SECTION_TBL_24675.lob` |
| UST-45, UST-46 | Sensitive data includes biometric data processed to identify an individual, and biometric data *"does not include a physical or digital photograph or data generated from a physical or digital photograph"* | `tx-bc-541` |
| UST-47 | The same in Virginia (§59.1-575), whose biometric data excludes photographs and *"data generated therefrom"* | `va-59.1-575` |
| UST-48 | Colorado's sensitive data includes biometric data that may be processed to identify an individual (§6-1-1303); the biometric provision that applies at any size is the new UST-55 | `co-crs2024-t6` |
| UST-51 | The written release's definition (*"informed written consent, electronic signature"*, P.A. 103-769), the retention limit (purpose met, or *"within 3 years of the individual's last interaction"*) and one violation per person and method (§20(b)) | `il-bipa` |
| USF-22 | Biometric identifiers include *"facial images"* enrolled in a biometric system and their templates (§202.204); the bulk threshold is more than 1,000 U.S. persons in 12 months (§202.205); the countries of concern are listed in §202.601 | `ecfr-28-202` |

### 5.3 Rows added

AP-67, AP-68 and AP-69 (section 6.3) and UST-52 to UST-59 (section 6.1), each marked "Added at the A05-V recheck", each naming its primary text, and each added to section 7's T5 (or T7) cell and to G-10's Rows in section 8 (AP-68 to T7 only: it binds only if facial sign-in is proposed). Every quotation in them was searched in its source (section 11): all exact.

## 6. The searches

The three searches of the brief's PP5 text. A law or rule already in a row was rechecked there, not added again.

### 6.1 US state laws on biometric identifiers or biometric data, other than BIPA

Run by the state-law subagent (section 11), each candidate read in its primary text and re-checked here. Sources: the "State law search" sources table (appendix C).

**Found and added:**

| New row | Law, primary text read | Fetch name(s) | What makes it a biometric provision that may bind at Glow's size | Rows compared (same state) |
|---|---|---|---|---|
| UST-52 | Texas, Capture or Use of Biometric Identifier, Bus. & Com. Code §503.001 (as amended by HB 149, eff. 1 Jan 2026), `tcss.legis.texas.gov` | `law-tx-503b` | Names *"record of hand or face geometry"*; no size threshold or photograph exclusion; notice and consent before capture; destruction within a year after the purpose expires; (e)(3) exempts AI used against fraud | UST-01, UST-02 (ch. 106), UST-45, UST-46 (ch. 541): none duplicated |
| UST-53 | Washington, Biometric Identifiers, RCW ch. 19.375 (2017) | `law-wa-19375` | Notice, consent or opt-out before enrolment for a commercial purpose; excludes photographs and *"data generated therefrom"*; no threshold | No Washington row |
| UST-54 | Washington, My Health My Data Act, RCW ch. 19.373 (2023); RCW 19.86.090 | `law-wa-19373`, `law-wa-19.86.090` | Consumer health data includes *"(ix) Biometric data;"*; small businesses covered since 30 June 2024; consent before collection | No Washington row |
| UST-55 | Colorado, C.R.S. §§6-1-1303, 6-1-1304(1)(a)(II), 6-1-1314 (HB 24-1130, from 1 July 2025), Colorado Revised Statutes 2026 linked from the Office of Legislative Legal Services | `law-co-crs2026-t6`, `law-co-crs2026-dl` (also `law-co-crs2024-t6`, which agrees) | Applies to a controller of *"any amount of biometric identifiers or biometric data"*, below the general thresholds; *"A facial map, facial geometry, or facial template"*; consent; public retention policy | UST-48 (general thresholds) and UST-41 (minors); UST-18 to UST-20 are dating safety: none duplicated |
| UST-56 | Nevada, NRS 603A.400 to 603A.550 (SB 370, 2023) | `law-nv-603a` | No threshold in the text read; biometric data counts only when *"related to"* listed health information | No Nevada row |
| UST-57 | Connecticut Data Privacy Act as amended by Public Act 25-113 §6 (CGS §42-516, from 1 July 2026) and Public Act 26-64 (CGS §42-515, from 1 October 2026) | `law-ct-pa25-113-b`, `law-ct-pa26-64-b` | From 1 July 2026 applies to anyone who controlled or processed consumers' sensitive data, with no number; sensitive data includes *"genetic or biometric data or information derived therefrom"* and government ID numbers | UST-09 to UST-11 (dating): none duplicated |
| UST-58 | Nebraska Data Privacy Act, Neb. Rev. Stat. §87-1118 with §§87-1102, 87-1103 (LB1074, operative 1 Jan 2025) | `law-ne-87-1118`, `law-ne-87-1102`, `law-ne-87-1103`, `law-ne-lb1074-slip` | A small business may not sell sensitive data (biometric data for identification) without prior consent | No Nebraska row; mirrors Texas's UST-45 |
| UST-59 | Minnesota Consumer Data Privacy Act, Minn. Stat. §325M.17 (Laws 2024 ch. 121, eff. 31 July 2025) | `law-mn-325m-full`, `law-mn-2024c121` | The same small-business sale rule | No Minnesota row |

**Read and not added:**
- **Connecticut, CGS §42-526** (consumer health data, no threshold; `law-ct-743jj-b`): its consumer health data definition does not list biometric data, so it is not a biometric provision. Biometric data appears under "sensitive data" instead (UST-57).
- **Facts for existing rows, not new rows:** Texas's sensitive and biometric definitions (UST-45, UST-46; precision added); Virginia (UST-47) and California (UST-42 to UST-44): no biometric rule below their thresholds was found in the sections read.
- **Threshold-bound privacy laws (read, not added):** Vermont Act 145 of 2026 (applies at 35,000 consumers or the sensitive data of 3,000, from 1 January 2028; `law-vt-act145`); Alabama HB 351 (2026; more than 25,000 consumers; from 1 May 2027; `law-al-hb351-enr`); Louisiana SB 386, enrolled as Act 502 (2026; $25 million revenue, 75,000 consumers or 50% of revenue from sales; from 1 January 2027; signature not shown on the enrolled text; `law-la-sb386-1480202`); Oklahoma SB 546 (2026; 100,000 consumers or 25,000 with 50% of revenue from sales; from 1 January 2027; `law-ok-sb546-enr`). Vermont's 3,000-consumer sensitive-data threshold is low; it is noted for the manager.
- **Category only:** state data-breach notification statutes that count biometric data as personal information (examples read: Washington RCW 19.255.005, `law-wa-19255`; Colorado §6-1-716, in `law-co-crs2026-t6`, where biometric data means data used to authenticate an account login). Not surveyed state by state.

**Searched, found nothing:** other standalone state biometric statutes beyond Illinois, Texas and Washington. The queries (in the subagent's notes) returned law-firm trackers and blogs only, none reporting another enacted standalone statute; this negative result rests on secondary sources.

### 6.2 State laws on identity verification by online dating services

**No enacted state law was found** that requires or regulates identity or age verification by online dating services, or requires a disclosure about it, beyond the rows already held.
- **Already in rows, rechecked for amendments:** Colorado §6-1-731.5 (UST-20; item (c) unchanged in the 2026 code: *"(c) A description of whether and when the online dating service verifies a member's identity or that the member is at least eighteen years of age."*), Texas ch. 106 (UST-01, UST-02), Illinois 815 ILCS 518 (UST-05, UST-06; latest source P.A. 102-220), Utah ch. 13-67 (UST-12 to UST-14), Vermont §2482b (UST-15, UST-16), Arizona §44-7157 (UST-17), New York GBL §394-c (UST-07, UST-08, UST-25; L.2025 ch. 13 read on nyassembly.gov, no verification duty), New Jersey (UST-03, UST-04).
- **Bills, not law:** New York A.3323 (would add GBL §394-cccc requiring a New York member's *"identity verification"*, a selfie matched to a government ID; in committee since 7 January 2026; `law-ny-a3323-asm`); New York A.8713-B (passed both houses on 2 June 2026, not shown delivered or signed; it would require a social referral service's personal material, including photographs, to be returned or destroyed within 30 days, with an exception for a fraud or content ban; `law-ny-a8713-asm`); New Jersey S1040 (criminal record screening on request; `law-nj-s1040`); California SB 1390 (background checks; status from a secondary tracker only, **UNCONFIRMED**) and SB 957 (from a search summary only, not fetched).
- **Sources tried:** the queries listed in the subagent's notes; the legislatures' own sites for each state above; `leginfo.legislature.ca.gov` and `nysenate.gov` refused (section 9).

### 6.3 Apple's and Google's own rules on face or biometric data

This session searched the fetched store pages for "biometric", "facial", "face data", "Face ID", "face geometry", "TrueDepth", "faceprint" and "face recogn".

**Apple: found, three rows added.**
- **AP-67**, DPLA §3.3.3(K) "Face Data" (`apple-dpla`): Face Data is defined to include *"data from an uploaded photo"* and data *"provided by a user in or through an Application (e.g., uploads for a facial analysis service)"*; an app that accesses it must *"inform users of Your intended uses and disclosures of Face Data by Your Application and to obtain clear and conspicuous consent from such users before any collection or use of Face Data"*; *"You may not use Face Data for authentication, advertising, or marketing purposes"*; transfer off the device only with consent and for a specific function; service providers held to the consent.
- **AP-68**, ARG 2.5.13 (`apple-arg`): facial recognition for account authentication uses LocalAuthentication where possible, with another method under 13.
- **AP-69**, ARG 5.1.2(vi) (`apple-arg`): data from facial mapping tools, the Camera APIs or the Photo APIs may not be used for marketing, advertising or use-based data mining, including by third parties.
- **AP-23** already covers the privacy label's Sensitive Info, which lists *"biometric data"*: a precision, not a new row.
- Compared with every AP row: none names face or biometric data (DM-83's finding); AP-23, AP-29 to AP-31 are the nearest and are not duplicated.
- **Found incidentally, not face or biometric rules, not added:** DPLA §3.3.3(M), *"Your Application may use the ID Verifier APIs solely for the purpose of enabling the verification of the end users’ age or ID through Your Application."*; and §3.3.3(N), *"You may not transmit off the user’s device any information about whether an image or video has been identified by the Sensitive Content Analysis Framework as containing nudity or sexually explicit material, or graphic violence or gore."* Both bear on the decision (an Apple route to read an ID; an on-device nudity check whose result may not reach the server) and are left to the manager (section 10).

**Google Play: searched, nothing found.** No "biometric", "facial", "face" or "selfie" rule in the Developer Program Policy print view (answer 18265346), User Data (10144311), Data safety (10787469), Permissions (16558241) or the Developer Distribution Agreement; a web search found no other Play page. The general rules on third-party code, prominent disclosure and consent (GP-24, GP-29, GP-30) already apply to an SDK that collects such data.

## 7. The comparison of services

All facts are from each service's own pages read on 17 November 2026. The full fields, with a quotation and its check for each, are in appendices A and B; every page is in the sources tables (appendix C). "Not published" means not found on the pages read. No ranking or recommendation.

### 7.1 How the candidates were chosen

- **The pools.** This session gave each subagent a pool of widely marketed services to consider (named from general knowledge, not from a source, and not an endorsement); each subagent then chose from its pool by a stated rule applied to the services' own pages.
- **Identity verification:** from a pool of 11 (Persona, Veriff, Onfido (Entrust), Jumio, Stripe Identity, Incode, Sumsub, Socure, AU10TIX, Yoti, Footprint): every one whose own pricing page publishes a self-serve price for document-plus-selfie verification (Stripe Identity, Veriff, Sumsub), then the first unpriced one, in that order, whose privacy notice and developer documentation could be read. Persona and Onfido refused automated reads (403), so Jumio was taken. Incode, Yoti and Footprint returned 404 for pricing; Socure and AU10TIX were not assessed once four were chosen.
- **Photo check:** from a pool of six (Amazon Rekognition, Google Cloud Vision SafeSearch, Azure AI Content Safety, Hive, Sightengine, Clarifai), every one whose own pages show an image API with sexual and violence classes, a public price and data-handling terms. Five qualified; Clarifai's pages could not be reached (connection reset, 502).
- **Hash matching:** each programme in the pool (PhotoDNA, Google's Child Safety Toolkit, Thorn's Safer, Cloudflare's tool, NCMEC's hash sharing, the Tech Coalition's Lantern), plus those the subagent found: the Internet Watch Foundation, Project Arachnid Shield, Take It Down and (separately, not CSAM) StopNCII.

### 7.2 Identity verification companies

Stripe Identity is Stripe's verification product, which its use-cases page describes as usable *"as a stand-alone service"* (`idv-stripe-usecases-md`); it is separate from payments, so in-app billing through the stores does not bear on it.

| Field | Stripe Identity | Veriff | Sumsub | Jumio |
|---|---|---|---|---|
| Price | $1.50 per verification; first 50 free; minimum and contract not published (`idv-stripe-pricing`, `idv-stripe-identity`) | $0.80, $1.39 or $1.89 per verification, with $49, $99 or $209 monthly minimums; 15-day trial; custom above 5,000 a month (`idv-veriff-pricing`) | $1.35 ($149 monthly minimum) or $1.85 ($299); 14-day trial with 50 checks (`idv-sumsub-pricing`) | No public price (pricing page 404) |
| Eligibility for a dating app | Stripe lists *"Online dating and matchmaking services"* under Restricted Businesses (*"require additional due diligence"*), and lists use *"in furtherance of, any Prohibited or Restricted Business"* as unsupported for Identity, five restricted categories (not dating) being allowed *"without pre-approval"* in the US or UK (`svc-stripe-restricted`, `idv-stripe-usecases-md`) | Not published (no dating restriction on the pages read) | Not published | Not published |
| What it keeps, default | Biometrics up to one year; other identity data typically 7 years; redaction API (`idv-stripe-manage-r`, `idv-stripe-sessions-md`) | Session data 3 or 6 months by plan, 2 years for $0.30 more; Illinois biometrics destroyed within 3 years; *"Veriff may retain the Personal Data for its own purposes irrespective of the retention schedule"* (`idv-veriff-pricing`, `idv-veriff-privacy`) | Set by the client, no longer than the contract; Illinois at most 3 years; pseudonymised data kept for model calibration (`idv-sumsub-privsvc`) | Biometrics destroyed within 3 years as controller; as processor, as the customer instructs; deletion APIs (`idv-jumio-osnotice`, `idv-jumio-delcred`) |
| Own use | Cross-checks new selfies against past submissions (end-user opt-out by email); training only with a separate consent; reusable identity via Link (`idv-stripe-faq-r`) | Machine-learning training in its DPA, except Illinois and Texas residents' biometrics; cross-session links on Plus and Premium (`idv-veriff-dpa2303`, `idv-veriff-privacy`) | Training with client permission, which the self-serve terms grant; cross-customer comparison; Sumsub ID as controller (`idv-sumsub-privsvc`, `idv-sumsub-terms`, `idv-sumsub-dpa`) | Improvement including machine learning; a perpetual licence to user information including biometric information; reuse of a verified ID (`idv-jumio-osnotice`, `idv-jumio-tc73`, `idv-jumio-selfiedone`) |
| Where; sub-processors | United States; list published (`idv-stripe-manage-r`, `idv-stripe-svcprov`) | Stored in Ireland, processed from the EEA, UK, US and India; list published (`idv-veriff-tp-faq`, `idv-veriff-tp-subproc`) | EU (Germany default); US region on request; list published (`idv-sumsub-privsvc`, `idv-sumsub-ldp`, `idv-sumsub-subproc`) | May be processed in the US; regional endpoints; list on request only (`idv-jumio-osnotice`, `idv-jumio-auth`) |
| BIPA and consent | Stripe's flow asks two consents; customer may not change the consent language; consent record kept; a non-biometric alternative where law requires; no Illinois notice found (`idv-stripe-faq-r`, `idv-stripe-idterms`) | Its flow: continuing is consent; Illinois and Texas notice; no sale or profit from biometrics; "written release" not used (`idv-veriff-privacy`) | SDK consent screen by default, with a US version; its notice requires *"written informed consent"*; API integrations collect consent themselves (`idv-sumsub-consent`, `idv-sumsub-privsvc`, `idv-sumsub-privdisc`) | Consent built into its UI; through the API the customer presents it, and implicit consent is accepted; no Illinois section (`idv-jumio-consent`, `idv-jumio-tc73`) |
| Failed check | `requires_input` retry; customer can override; some manual reviewers; end-user appeal not published | Up to 9 resubmissions, not charged; specialists on Plus and Premium; the user may request human intervention | `RETRY` or `FINAL`; a human when the system cannot decide; client manual-review step; appeal through the client | Retry guidance; staff review and end-user appeal not published |
| Birth date; liveness | `dob` returned; presentation-attack and manipulation checks ("liveness" not named) | `dateOfBirth`; passive liveness | `dob`; active liveness (blink, smile, move) | `dateOfBirth`; Liveness PASSED/WARNING/REJECTED |
| Integration | `@stripe/stripe-identity-react-native` (Expo not mentioned); iOS, Android, web, no-code, API | `@veriff/react-native-sdk`, with an Expo plugin and EAS Build; hosted page; API | `@sumsub/react-native-mobilesdk-module` (Expo not mentioned); WebSDK, links, API | React Native plugin from GitHub (Expo not mentioned); iOS, Android, Web Client, API |
| DPA; role | Published (28 Sep 2026); processor, and controller for fraud and (with consent) improvement | Published (ver-DPA-2303; current version not established); customer is controller | Published (EU/UK PDF, 28.08.2026; Annex 3 in the terms); processor and independent controller | Not published; controller by default |
| CSAM detection | Not published (none of the four) | Not published | Not published | Not published |

### 7.3 Automated photo check services

| Field | Amazon Rekognition | Google Vision SafeSearch | Azure AI Content Safety | Hive (now Deploy) | Sightengine |
|---|---|---|---|---|---|
| Price | $0.0010 per image for the first million a month (US East), lower tiers above; 1,000 a month free for 12 months | $1.50 per 1,000 (1,001 to 5 million a month); first 1,000 free | $0.75 per 1,000 images; 5,000 a month free (region not shown) | $3.00 per 1,000 at 100 a day (testing); its docs say Visual Moderation needs an annual contract | Free 2,000 operations a month; $29 a month for 10,000 |
| Keeps images | May store; period not published; deletion through Support | Online requests not persisted; asynchronous for a few hours | Not stored (except blocklists) | 14 days by default; adjustable on request | Deleted after processing by default |
| Own use | Yes by default, to improve AWS AI; opt-out by an AWS Organizations policy | No training use stated | No training use stated | Yes by default, including manual review by Hive Workers, unless agreed otherwise in writing | Only images sent through its Feedback API |
| Where; sub-processors | Chosen region; list published | SafeSearch location not published; list published | Chosen region; Microsoft's list PDF dated Feb 2025 | US-operated, may process elsewhere; list not published | EU, Canada, US by default; list published |
| BIPA | Biometric notice and consent terms name BIPA | Not published | DPA biometric clause; BIPA not named | Not published | Not published |
| Disputed result | Amazon A2I human review | Not published | The customer's own | Moderation dashboard review and appeals | Workflow to the customer's own moderators |
| DPA | Published; processor | Cloud DPA; processor | Microsoft DPA; processor | Not published | Published; processor |
| CSAM | *"this API does not detect whether an image includes illegal content (such as child sexual abuse material)"* | Not in Vision (Google's separate toolkit) | *"You can't use Azure AI Content Safety to detect illegal child exploitation images."* | Hash matching and a classifier with Thorn, Enterprise customers only; reports use the customer's NCMEC credentials | Not published |

### 7.4 Hash matching for child sexual abuse material

- **Which compared services offer it:** of the photo checks, only Hive (with Thorn, Enterprise only). None of the four identity verification companies publishes any.
- **Programmes, with their eligibility as published** (appendix B, part B):

| Programme | Eligibility as published | Cost as published | What the provider agrees to |
|---|---|---|---|
| Microsoft PhotoDNA Cloud Service | *"Must be a qualified organization subject to approval by third-party vetting service."*; for trusted online services hosting user content; case by case | *"free for qualified customers"*; terms (May 2018) cap free transactions | Use solely to prevent CSAM's spread; internal use; aggregate match reports to NCMEC; images only |
| Google Child Safety Toolkit | Qualifying partners; *"Applications are subject to approval."*; Content Safety API is a classifier; CSAI Match is for video | Free | Partners make their own review decisions; detailed terms not published |
| Thorn's Safer | A commercial product; Thorn *"will engage in dialogue with any company"*; companies report to NCMEC themselves | Not on safer.io; its AWS Marketplace listing (seller Thorn) starts at $45,384 for 12 months | Contract terms; suspension for misuse |
| Cloudflare CSAM Scanning Tool | Content served through Cloudflare's cache; an email address | Free | Use solely against CSAM; Cloudflare may block matches and reports with its own CyberTipline credentials |
| NCMEC hash sharing | Voluntary; credentials *"must be requested from and supplied by NCMEC"*; criteria not published | Not published | Not published |
| Tech Coalition Lantern | Vetting; signal sharing that includes CSAM hashes; membership terms separate | Membership from US$10,000 a year | Secure handling, investigations, legal compliance |
| Internet Watch Foundation hash list | Members trading over 12 months with more than 2 full-time employees | £5,000+ to £100,000+ a year | Not published on the pages read |
| Project Arachnid Shield | For electronic service providers; account request | *"There is no cost to using this tool"* | Not published |

Take It Down (NCMEC's list of images that people under 18 submit of themselves) and StopNCII (adults' intimate images, not CSAM) are recorded in appendix B. 18 U.S.C. 2258C limits a provider's use of elements NCMEC gives it (USF-07).

## 8. The facts table for DM-52 section 16's six items

Facts and their sources only; no recommendation. Rows are the matrix's; pages are fetch names (appendix C).

| Item | What the rows say | What the services' pages say |
|---|---|---|
| **1. The cost of each** | No row prices a service; M07 costs them (OD-50). USF-22: a vendor agreement with a company in a country of concern restricts biometric identifiers above 1,000 U.S. persons | Identity verification: Stripe $1.50 (first 50 free); Veriff $0.80 to $1.89 with $49 to $209 monthly minimums; Sumsub $1.35 or $1.85 with $149 or $299 minimums; Jumio no public price (7.2). Photo check: Rekognition $0.0010 an image; Google $1.50 per 1,000; Azure $0.75 per 1,000; Hive $3.00 per 1,000 for testing, annual contract stated; Sightengine from $29 a month (7.3). Hash matching: PhotoDNA, Google's toolkit, Cloudflare and Arachnid Shield free on their terms; Safer from $45,384 a year on AWS Marketplace; IWF from £5,000; NCMEC's cost not published (7.4). Stripe lists dating as a restricted business (`svc-stripe-restricted`) |
| **2. The consent, with BIPA's written release** | UST-51: written notice of purpose and term and a written release (*"informed written consent, electronic signature"*) before collecting face geometry, and a public retention policy; UST-52 (Texas): notice and consent before capture; UST-55 (Colorado, any amount, from 1 July 2025): consent and a public policy; UST-57 (Connecticut, from 1 July 2026): consent for sensitive data, which includes biometric data and ID numbers; UST-54 (Washington), UST-56 (Nevada) where they apply; UST-53's conditions; AP-67: *"clear and conspicuous consent"* before Face Data is collected, and no use *"for authentication"* (a reading for counsel); AP-69; AP-29, AP-30 (explicit permission before sharing with a third party); GP-29, GP-30; UST-42, UST-45, UST-47, UST-48 (biometric data is sensitive data); USF-13 (the FTC's guidance, unread) | Stripe's own flow asks two consents and fixes the wording; Veriff's flow treats continuing as consent, with an Illinois and Texas notice; Sumsub's SDK shows a consent screen with a US version and its notice requires *"written informed consent"*; Jumio's UI has consent built in, and through the API the customer presents it, implicit consent accepted. None uses the words "written release" on the pages read (7.2) |
| **3. What each keeps, and for how long** | UST-51: destroy when the purpose is met or within 3 years of the last interaction; UST-52: within a year after the purpose expires; UST-55: purpose met, 24 months after the last interaction, or 45 days after found unnecessary; UST-53: no longer than reasonably necessary; AP-33, GP-33 (ask service providers to delete; tell users what is kept), UST-43; AP-27, GP-27 (the privacy policy states retention); AP-22, GP-24, GP-26 (declare what partners and service providers collect); GP-32 | Stripe: biometrics up to a year, other data typically 7 years, own fraud and Link uses; Veriff: 3 or 6 months by plan, Illinois biometrics within 3 years, may keep for its own purposes; Sumsub: client-set within the contract, Illinois within 3 years, training permitted by its self-serve terms; Jumio: biometrics within 3 years as controller, a perpetual licence in its terms (7.2). Photo checks: Rekognition may store and uses inputs to improve unless opted out; Google and Azure state no storage or training; Hive 14 days and own use unless agreed otherwise; Sightengine deletes after processing (7.3) |
| **4. What a member can do when a check fails** | UST-20: Colorado's posted policy describes whether and when Glow verifies identity or age, and suspension and appeal, and its annual report counts people removed or refused after identity or age verification; K3 of DM-52 plans a retry and an appeal its one operator answers. No other row read sets a failure path | Stripe: retry (`requires_input`), customer override, some manual review, user told to contact the business; its terms ask a non-biometric alternative where law requires; Veriff: up to 9 free resubmissions, specialists on higher plans, the user may request human intervention; Sumsub: `RETRY` or `FINAL`, a human when the system cannot decide, appeal through the client; Jumio: retry guidance only (7.2). Photo checks: Rekognition's A2I, Hive's appeals, Sightengine's workflow; Google and Azure leave it to the customer (7.3) |
| **5. Whether the ID's birth date replaces the typed one** | OD-64 (13 November 2026) already records Nathan's answer: the birth date is *locked to the ID's once the member is identity-verified*, so at verification the ID's date replaces the typed one. Rows that bear on it: AP-31 (no repurposing without further consent); UST-35 (California, 1 January 2027: the store signal is the primary indicator, but internal clear and convincing information of a different age becomes the primary indicator, with actual knowledge; precision added); AP-14 (Apple's `confirmed` value); UST-32 to UST-34, UST-36 (store age data); UST-37, UST-39 ("reasonably determined"), UST-38; UST-41 and USF-11 (knowledge that a user is a minor); UST-20 (the policy says whether and when Glow verifies age) | All four return the birth date: Stripe `dob` (restricted key), Veriff `dateOfBirth`, Sumsub `dob`, Jumio `dateOfBirth` (7.2) |
| **6. Whether one service also runs G-02's detection step** | USF-07: no federal duty to scan; NCMEC-provided elements are use-limited (§2258C); USF-01, USF-05, USF-06 (reporting, staff access, disclosure); GP-20, GP-21 (Google mandates no detection method; a reporting process); AP-21; UST-49; GP-18 to GP-23 | No identity verification company publishes detection. Among photo checks, only Hive offers CSAM hash matching and a classifier (with Thorn, Enterprise only); Rekognition and Azure say they do not detect it; Google's is a separate toolkit; Sightengine publishes none. Programmes: 7.4 |

## 9. Unread sources

| Source | URL | Why | Effect |
|---|---|---|---|
| FTC, "Marketing Your Mobile App" | `https://www.ftc.gov/business-guidance/resources/marketing-your-mobile-app-get-it-right-start` | `404`, the same 1,301-byte page ftc.gov gave for every URL, its home page included (`ftc-root`) | USF-13's guidance stays UNCONFIRMED |
| FTC, COPPA FAQ | `https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions` | As above | USF-11's FAQ citation not re-read |
| Texas SB 2420's merits appeal; Utah's appeal (UST-40) | court dockets (PACER) | not accessible; web search found no decision | Both stay as the rows say |
| New York SAFE for Kids rule text (UST-38) | — | not read, as before | As before |
| California legislature site | `https://leginfo.legislature.ca.gov/faces/billHistoryClient.xhtml?bill_id=202520260SB1390` (and the status page; Civ. Code §1694.3) | `403`, Cloudflare challenge (state-law subagent) | SB 1390's status UNCONFIRMED; UST-21 not in this recheck |
| New York Senate site | `https://www.nysenate.gov/legislation/bills/2025/A3323`; GBL §394-c current text | `403`, Cloudflare challenge | Bills read on nyassembly.gov; §394-c's current text not read |
| Colorado Revised Statutes 2025 | `https://content.leg.colorado.gov/sites/default/files/images/olls/crs2025-title-06.pdf` | `404` | The 2026 printout was read |
| Texas statutes site | `https://statutes.capitol.texas.gov/Docs/BC/htm/BC.503.htm` | JavaScript shell only | Read at `tcss.legis.texas.gov` |
| Persona | `https://withpersona.com/pricing`, `https://withpersona.com/legal/privacy-policy` | `403`; Cloudflare challenge when rendered | Not compared |
| Onfido (Entrust) | `https://onfido.com/pricing/` (to entrust.com), the facial-scan policy, the product privacy notice PDF, the Onfido-specific terms | `403` | Not compared |
| Veriff | help-centre sub-processor article; DPA insight article (login); DPA version index | no article text; login page; no version list | The trust-centre list used; DPA version not established |
| Jumio trust centre | `https://trust.jumio.com/` | `403` | Sub-processor list "on request" only |
| Clarifai | `https://www.clarifai.com/pricing`, `https://docs.clarifai.com/` | connection reset; `502` | Not compared |
| Safer | `https://safer.io/pricing/`, `https://safer.io/faq/` | `404` | Price from the AWS Marketplace listing |
| YouTube CSAI Match | `https://youtube.com/csai-match/` | redirected to a general page | CSAI Match's terms not read |
| NCMEC hash-sharing root | `https://hashsharing.ncmec.org/` | empty body | The `/npo` page read |

Pages that were redirects or JavaScript shells but whose content was read another way are listed in appendices A and B.

## 10. Deviations, limits and open questions

**Deviations from the prompt's method:**
- **Subagents.** Three research subagents did the state-law search and the two comparisons (the prompt allows it). They used this session's fetch, strip and search tools in the same scratchpad. Section 11 says how their work was checked.
- **Page dates of service pages** were found by an automatic search for "Last updated", "Last modified", "Effective" and similar, shown as "none found" where it found none; the recheck sources' dates were read by hand.
- **One Word file** (Microsoft's DPA) was read by extracting its `word/document.xml`, since the strip script reads HTML and PDF only.
- **Two certificate chains were completed** from the issuer named in the server's own certificate: `www.ilga.gov` (Sectigo, by this session) and `www.cga.ct.gov` (GoDaddy, by the state-law subagent, which took the leaf from the public crt.sh log to read its AIA URL). Verification was never turned off.
- **A stray file.** At 14:27 UTC the state-law subagent's `curl` call to crt.sh ran after a failed `cd` and wrote `crtsh.json` (public certificate-log data) into the repository root. It was deleted at once; this session confirmed `git status` clean before committing.

**Limits:**
- Research, not legal advice; no applicability finding and no compliance statement (DM-37 1.1).
- Comprehensive state privacy laws whose biometric provisions bind only at volume thresholds were not added as rows (as P09.3a did not add them); four read are listed in 6.1; the rest were not surveyed. Breach-notification statutes are recorded as a category. City and county laws were not searched (the search is of state law).
- The negative result for further standalone biometric statutes rests on secondary trackers.
- Owners given to new rows (P08, P10, SV1) and UST-51's new owner follow the carried-items file's routes (K3, K4, K6 of DM-52) but are routing suggestions for the manager.
- Service facts are what the public pages said today; signed contracts, enterprise terms and DPAs can differ, and none was requested. "Not published" means not found on the pages read.

**Outside this session's owned scope, now stale (for the manager):**
- Section 1's Summary counts (320 rows; Apple 66; US states 51; 85 no owner; 81 not applicable now) and the Contents ranges ("AP-01 to AP-66", "UST-01 to UST-51") do not count AP-67 to AP-69 and UST-52 to UST-59, or UST-51's change.
- Section 8, G-01's Timing cell still says "California and Alabama (unconfirmed)" (UST-36 is now confirmed). UST-51 is not in G-10's Rows (only new rows may be added there).
- Section 9, Launch geography: "The comprehensive privacy laws read bind at thresholds Glow does not meet, except Texas's no-sale rule for small businesses (UST-45) and Colorado's minors duties (UST-41)" does not mention UST-55 (Colorado's biometric provision at any size), UST-57 (Connecticut from 1 July 2026), UST-58, UST-59 or UST-52 to UST-54, UST-56; and its list of app-store acts (UST-32 to UST-35) omits Alabama (UST-36). These sentences state rows whose requirement or status did not change, so they were left as they are.
- Section 10's "Texas SB 2420's merits appeal is pending": no decision was found (web search only); left as it is.

**Two questions only counsel can answer** (whether to take advice is Nathan's decision, DM-31):
- **Apple's word "authentication" (AP-67).** DPLA §3.3.3(K) says *"You may not use Face Data for authentication, advertising, or marketing purposes"* and does not define "authentication". Face Data includes a selfie. If the word means proving who someone is, a selfie matched to an ID could fall within it; if it means signing in, it would not. The text does not settle which.
- **Who "collects" the face data (UST-51, UST-52, UST-55).** BIPA, Texas §503.001 and Colorado §6-1-1314 put their notice, written-release and retention duties on whoever collects, captures or possesses the face data. When a verification company's SDK takes the selfie inside Glow's app and the company computes the face template, the texts do not say whether that is Glow, the company or both. The answer decides who must show the notice and obtain the release; the companies differ (Stripe, Veriff and Sumsub show their own consent screens; through Jumio's API the customer presents it).

**A fact for the decision message, not a question:**
- **Stripe Identity is Stripe's identity verification product,** usable *"as a stand-alone service"* and priced per verification; it is not payment processing, and how Glow bills (through the stores, AP-39 to AP-45 and GP-38 to GP-45, if a paid launch is chosen, A06) does not change it. Stripe's public pages list dating as a restricted business, and Identity's unsupported uses include restricted businesses other than five named categories, so its pages do not show whether Stripe would accept Glow for Identity. Only Stripe can say, and no one asked it.

**Not covered by this research, for the manager:**
- **Apple's ID Verifier APIs** (DPLA §3.3.3(M)): an Apple API for verifying a user's age or ID. Not compared; being Apple's, it would not serve Android members on its own.
- **Apple's Sensitive Content Analysis Framework** (DPLA §3.3.3(N)): its result may not leave the device, so it cannot supply the server-side photo approval OD-61 sets.
- **New York A.8713-B** (passed both houses on 2 June 2026, not shown signed): if signed, a social referral service would return or destroy a member's personal material, including photographs, within 30 days of the contract ending. It belongs to UST-25 (paying members), which was not in this recheck.
- **Item 5** is already answered by OD-64; the decision message may cite it with AP-31 and UST-35's new precision.
- **The federal Romance Scam Prevention Act** is reported by secondary sources as Public Law 119-129; USF-18 holds it and was not in this recheck.

## 11. How this session checked the subagents' work

- **Scope and conduct.** Each subagent had the same source rules and the same tools, wrote only in the scratchpad, and made no account, form, request or message. Apart from the stray file above, nothing was written outside the scratchpad.
- **Quotations re-run.** This session re-ran every recorded quotation against the saved stripped text with its own search script: 118 of 118 for the state-law search, 164 of 164 for identity verification and 234 of 234 for the photo checks and hash matching, all exact.
- **New rows read in place.** Each of UST-52 to UST-59 was read in its primary text by this session (Texas §503.001 in full; Colorado §6-1-1304(1)(a)(II) and its 2026 source on the legislature's download page; Connecticut PA 25-113 §6; Washington's definition; Nevada's definition; Nebraska §87-1103 and §87-1118; Minnesota §325M.17). Every quotation in the eleven new rows was searched in its source: all exact (one UST-57 quotation was re-taken from PA 26-64's current wording, *"unless such data are generated to identify a specific individual"*, after the pre-2025 code's "is" was found).
- **One fact added.** The identity verification write-up left Stripe's unsupported use cases unexamined; this session read them and Stripe's restricted-business list (`svc-stripe-restricted`) and added the eligibility row in 7.2.
- **Counts:** 364 fetches in all: 69 for the recheck and the store search (section 3), 55 for the state-law searches, 111 for identity verification (one of them, Stripe's restricted-business list, by this session) and 129 for photo checks and hash matching (appendix C), besides the California bulk members (section 3).

**Research, not legal advice.**

## Appendix A. Identity verification companies: every field, with its page and quotation

Written by the identity verification subagent and checked by this session (section 11). Every page was read on 17 November 2026. A fetch name maps to its URL, final URL, HTTP code, bytes, SHA-256 and page date in appendix C; each quotation's check result follows it.

### How the candidates were chosen

**Universe.** The universe was the 11 companies named in the brief: Persona, Veriff, Onfido (Entrust), Jumio, Stripe Identity, Incode, Sumsub, Socure, AU10TIX, Yoti and Footprint. No others were added.

**Rule 1: published self-serve price.** The subagent fetched each candidate's `/pricing` URL today. It included every candidate whose own pricing page, as read today, publishes a self-serve per-verification price for document-plus-selfie verification. Three qualified:

| Service | Self-serve price page (fetch name) | Evidence of US government ID coverage |
|---|---|---|
| Stripe Identity | `idv-stripe-pricing` | The document-check country list includes the United States. Quote: "United Kingdom United States" (`idv-stripe-checks`, EXACT). |
| Veriff | `idv-veriff-pricing` | The docs index lists US checks. Quote: "Streamline US identity verification with SSN and driver's license checks." (`idv-veriff-llms`, EXACT). |
| Sumsub | `idv-sumsub-pricing` | The notice covers US identifiers. Quote: "Social Security number, driver's license number" (`idv-sumsub-privsvc`, EXACT). The consent screen also has a US variant (field 5). |

**Rule 2: one candidate without a public price.** As a contrast, it added the first candidate in the brief's list order, not already chosen, whose own privacy notice and developer documentation could be read today. It stopped at four services.

- **Persona: not taken (unreadable).** withpersona.com returned HTTP 403 by curl for `/pricing` (`idv-persona-pricing`) and `/legal/privacy-policy` (`idv-persona-privacy`). A headless render of `/pricing` returned only a Cloudflare challenge page: "Performing security verification" (`idv-persona-pricing-r`, EXACT). Persona's docs site was readable (`idv-persona-docs`), but its pricing, privacy and legal pages were not.
- **Onfido (Entrust): not taken (unreadable).** onfido.com/pricing redirects to entrust.com/pricing, which returned HTTP 403 (`idv-onfido-pricing`). The Entrust facial-scan policy returned 403 by curl and by render: "Your request was blocked due to our security policies." (`idv-ent-facial-r`, EXACT). The product privacy notice PDF and the Onfido-specific terms also returned 403. Two Onfido pages were readable, its US consent documentation (`idv-ent-docconsent`) and a consent page (`idv-ent-consent`), but its own retention, privacy and contract terms were not. They were not used.
- **Jumio: taken.** Its privacy notice, terms and developer documentation were readable. Its pricing URL returned 404 (field 1).

**Not taken, and why.**

| Candidate | Reason |
|---|---|
| Incode, Yoti | Only their `/pricing` URLs were checked. Both returned HTTP 404 (`idv-incode-pricing`, `idv-yoti-pricing`). The four-service cap was reached under Rule 2 before their turn. |
| Socure, AU10TIX | Not assessed. The cap was reached first. |
| Footprint | `/pricing` returned 404 (`idv-fp-pricing`). Its homepage today describes "The agentic platform that learns your compliance program and runs it end-to-end." (`idv-fp-home`, EXACT). It did not check further for a document-plus-selfie product. |

Being left out says nothing about a company's quality.

---

### 1. Stripe Identity

All pages were read on 2026-11-17.

#### Field 1. Published price; minimums and contract terms

- **Price.** $1.50 per document-plus-selfie verification. The first 50 verifications are free. ID-number lookup costs $0.50.
  - `idv-stripe-pricing` (https://stripe.com/pricing): "$1.50 per verification Charged when a user completes verification." (EXACT)
  - `idv-stripe-identity` (https://stripe.com/identity): "Your first 50 verifications are free." (EXACT)
  - `idv-stripe-pricing`: "$0.50 per lookup" (EXACT)
- **Monthly minimum or annual contract.** Not published on these pages.

#### Field 2. What it keeps, for how long, and customer controls

- **Default retention.** Biometric identifiers are removed within one year. Images, extracted data (name, date of birth, ID number) and results are typically kept for 7 years in the customer's Dashboard.
  - `idv-stripe-manage-r` (https://support.stripe.com/questions/managing-your-id-verification-information): "The biometric identifiers created to conduct the verification will be fully removed from our systems within one year." (EXACT)
  - `idv-stripe-manage-r`: "We will typically store the rest of your submitted identity information for 7 years." (EXACT)
  - `idv-stripe-legal-r` (https://support.stripe.com/questions/legal-considerations-for-handling-id-verification-data-for-your-business): "retaining data in your Stripe Dashboard for 7 years and providing you with the ability to delete it sooner" (EXACT)
- **Customer control.** A redaction endpoint, also available in the Dashboard. Stripe states two different timescales on two different pages.
  - `idv-stripe-sessions-md` (https://docs.stripe.com/identity/verification-sessions.md): "You can redact a session to make sure Stripe deletes personal information." (EXACT)
  - `idv-stripe-sessions-md`: "Redaction can take up to 7 days." (EXACT)
  - `idv-stripe-legal-r`: "The process may take up to 4 days." (EXACT)
- **Copies Stripe keeps as processor.** Stripe keeps copies on the business's behalf until the business deletes them.
  - `idv-stripe-manage-r`: "Stripe will retain copies of your submitted identity data" (EXACT)

#### Field 3. Use for Stripe's own purposes, and opt-outs

- **Cross-customer fraud use.** Stripe keeps biometrics for one year to find fraud "over time and across photo IDs", and cross-checks new selfies against past submissions. The end user can opt out by emailing privacy@stripe.com.
  - `idv-stripe-faq-r` (https://support.stripe.com/questions/stripe-identity-faq): "Stripe retains biometrics for one year to identify fraud over time and across photo IDs, but you can opt-out at any time by contacting privacy@stripe.com" (EXACT)
  - `idv-stripe-faq-r`: "With this retained data, we also cross check new selfies against past submissions." (EXACT)
- **Model training.** This needs a separate end-user consent, which the user can decline.
  - `idv-stripe-faq-r`: "If you give us permission, we will occasionally generate additional biometric identifiers for training purposes—which will be deleted within one year." (EXACT)
  - `idv-stripe-faq-r`: "you can click to decline consent and we will only use your biometric information for the initial verification." (EXACT)
- **Controller of non-biometric data.**
  - `idv-stripe-manage-r`: "Stripe is also a data controller of non-biometric data like images of your ID documents, extracted data, web metadata" (EXACT)
- **Reusable identity.** End users can save identity data to Stripe's Link account.
  - `idv-stripe-faq-r`: "If you save your identity information to your Link account, Stripe will retain that information for longer." (EXACT)
- **Duplicate check within the customer's own verifications.**
  - `idv-stripe-review-md` (https://docs.stripe.com/identity/review-tools.md): "Stripe reviews your completed verifications for duplicate identities using biometric data" (EXACT)
- **Customer-side opt-out of Stripe's own use.** Not published.

#### Field 4. Processing and storage location; sub-processor list

- **Location.** United States, wherever the user or business is based.
  - `idv-stripe-manage-r`: "We are also processing and storing your verification data in the United States, no matter where you are based" (EXACT)
- **Sub-processor list.** https://stripe.com/legal/service-providers (`idv-stripe-svcprov`). It has a Stripe Identity subsection listing Trulioo, London Stock Exchange Group, Data Zoo, Shufti Pro, LexisNexis Risk Solutions, Ekata and Lob.
  - `idv-stripe-svcprov`: "Stripe Identity Trulioo Information Services, Inc. End Customer data Identity verification for End Customers of Business Users Canada" (EXACT)
  - `idv-stripe-svcprov`: "Last updated: September 27, 2026" (EXACT)

#### Field 5. Illinois BIPA and biometric laws

- **Who obtains consent.** Stripe's own flow asks for consent. There are two separate consents: one for verification and one for training.
  - `idv-stripe-faq-r`: "There are two different sets of permissions that we will ask of you for Stripe Identity." (EXACT)
  - `idv-stripe-identity`: "Users explicitly give consent before sharing data" (EXACT)
- **The customer may not change the consent wording.**
  - `idv-stripe-idterms` (https://stripe.com/legal/identity, which redirects to /legal/ssa-service-terms): "the manner or language used to obtain consent from Submitted Individuals" (EXACT). This is from the list of restricted uses. The section is headed "Stripe Identity Last modified: September 28, 2026" (EXACT).
- **Consent record.** Stripe stores a record of consent.
  - `idv-stripe-legal-r`: "as well as a record of the consent (where applicable)" (EXACT)
- **Non-biometric alternative.** The customer must offer one where law requires.
  - `idv-stripe-idterms`: "If Law requires, User must provide each individual with an alternative method of verification that does not involve processing any biometric information." (EXACT)
- **Public biometric retention schedule.** Published.
  - `idv-stripe-manage-r`: "Biometrics Verification, fraud and security purposes Up to one year" (EXACT)
- **Illinois-specific notice or the term "written release".** Not published. The word "Illinois" does not appear in any Stripe page read.

#### Field 6. Manual review, retry and appeal path

- **Retry.** A failed check sets `requires_input`, and the same session can be retried.
  - `idv-stripe-sessions-md`: "If any of the checks fail, the VerificationSession will have a `requires_input` status." (EXACT)
- **Customer-side review.** Dashboard review tools let the customer override a status or blocklist a document or selfie.
  - `idv-stripe-review-md`: "Manually override the verification status to match your decision on whether or not the customer is verified." (EXACT)
- **Vendor-side human review.**
  - `idv-stripe-checks` (https://docs.stripe.com/identity/verification-checks): "Stripe uses a combination of AI models, automated heuristic analysis, and manual reviewers to verify the authenticity of many document types." (EXACT)
  - `idv-stripe-manage-r`, on third-party review: "This will only happen in situations where our automated verification technology cannot make a decision with confidence." (EXACT)
- **End-user appeal path.** Not published. The FAQ tells users to contact the business for an alternative.

#### Field 7. Birth date and liveness result

- **Birth date.** Returned as `verified_outputs.dob`, and needs a restricted key.
  - `idv-stripe-results-md` (https://docs.stripe.com/identity/access-verification-results.md): "Here’s an example of accessing the extracted date of birth, ID number, and document number" (EXACT)
- **Liveness.** The docs do not use the word "liveness". They describe presentation-attack and manipulation checks, and the selfie result carries error codes.
  - `idv-stripe-selfie-md` (https://docs.stripe.com/identity/verification-checks.md?type=selfie): "`selfie_manipulated` | The captured face image was manipulated." (EXACT)
  - `idv-stripe-checks`: "To prevent presentation attacks, such as fraudsters using pictures of stolen documents or someone else’s face" (EXACT)
- **Passive or active liveness.** Not published.

#### Field 8. Integration

- **React Native SDK.** `@stripe/stripe-identity-react-native`. Expo is not mentioned on the React Native page.
  - `idv-stripe-rn-new-md`: "yarn add @stripe/stripe-identity-react-native" (EXACT)
- **Other integration paths.** Native iOS and Android SDKs, web modal or redirect, no-code Dashboard and verification flows, and an API.
  - `idv-stripe-rn-md`: "- React Native: - [New integration]" (EXACT)
  - `idv-stripe-rn-md`: "- No code: - [Dashboard]" (EXACT)

#### Field 9. DPA and role

- **DPA.** Published at https://stripe.com/legal/dpa (`idv-stripe-dpa`): "Last updated: September 28, 2026" (EXACT).
- **Role.** Stripe acts as processor when verifying on the business's behalf, and as controller for fraud, security and, with consent, improvement. The Identity Terms require the customer's privacy policy to say both parties are independent controllers.
  - `idv-stripe-manage-r`: "Stripe is a data processor when we use data captured to verify your identity on behalf of the business that requested our services." (EXACT)
  - `idv-stripe-idterms`: "state that User and Stripe are each independent controllers of Personal Data" (EXACT)

#### Field 10. CSAM detection or hash matching

- Nothing published. None of the Stripe pages read mention child sexual abuse material, CSAM, NCMEC, PhotoDNA or hash matching.

---

### 2. Veriff

All pages were read on 2026-11-17.

#### Field 1. Published price; minimums and contract terms

- **Self-serve plans.** All three are charged per verification, with a minimum monthly commitment.
  - Essential, `idv-veriff-pricing` (https://www.veriff.com/pricing): "$0.80 per verification $49 minimum monthly commitment" (EXACT)
  - `idv-veriff-pricing`: Plus: "$1.39 per verification $99 minimum monthly commitment" (EXACT)
  - `idv-veriff-pricing`: Premium: "$1.89 per verification $209 minimum monthly commitment" (EXACT)
- **Free trial.** 15 days, up to 50 sessions.
  - `idv-veriff-pricing`: "15-day free Trial Period (up to 50 Sessions)." (EXACT)
- **Billing.** A monthly subscription fee, paid at the start of each period. Retries are not charged.
  - `idv-veriff-pricing`: "Customers pay a monthly Subscription Fee, based on their plan, at the beginning of each period." (EXACT)
  - `idv-veriff-pricing`: "You only pay for IDV decisions, not retries." (EXACT)
- **Enterprise tier.** Custom pricing.
  - `idv-veriff-pricing`: "Best for businesses with more than 5,000 verifications/month. Custom pricing" (EXACT)
- **Annual contract.** Not published for self-serve.

#### Field 2. What it keeps, for how long, and customer controls

- **Session data available to the customer.** 3 months on Essential, 6 months on Plus and Premium. Extended retention of 2 years costs an extra $0.30 per verification. The FaceBlock list is kept for 3 years.
  - `idv-veriff-pricing`: "Read the data retention FAQ → 3 months 6 months 6 months" (EXACT)
  - `idv-veriff-pricing`: "Extended data retention 2 years +$0.30" (EXACT)
  - `idv-veriff-pricing`: "FaceBlock (3 years in FaceBlock list)" (EXACT)
- **Veriff's own retention.**
  - `idv-veriff-pricing`: "To the extent not prohibited by law, Veriff may retain the Personal Data for its own purposes irrespective of the retention schedule implemented for the Service provision." (EXACT)
- **Illinois biometric destruction.**
  - `idv-veriff-privacy` (https://www.veriff.com/privacy-notice): "we will permanently destroy their biometric identifiers and biometric information when the initial purpose for collecting or obtaining such identifiers or information has been satisfied or within 3 years of the individual’s last interaction with Veriff, whichever occurs first." (EXACT)
- **Deletion API.** In the self-serve table, session deletion via API is Premium only.
  - `idv-veriff-pricing`: "Session deletion via API Remove outdated or unnecessary verification sessions via API to meet compliance or privacy requirements. – Not included – Not included" (EXACT)
- **Deletion API conditions.** The endpoint is off by default, rate-limited, and deletes within 12 hours.
  - `idv-veriff-delete` (https://devdocs.veriff.com/apidocs/v1sessionsid-3.md): "The endpoint is not available by default" (EXACT)
  - `idv-veriff-delete`: "10 sessions per 24 hours and 5 sessions per 1 hour" (EXACT)
  - `idv-veriff-delete`: "Data will be deleted within 12 hours" (EXACT)
- **Enterprise retention setting.**
  - `idv-veriff-pricing`: "Set how long Veriff stores session data and keeps it accessible to you before deletion, per jurisdiction." (EXACT)

#### Field 3. Use for Veriff's own purposes, and opt-outs

- **Model training.** The DPA's Permitted Business Purposes include training.
  - `idv-veriff-dpa2303` (https://www.veriff.com/data-processing-addendum/ver-DPA-2303): "developing, testing, improving and altering the functionality of the Service, including for machine learning, data annotation, testing and training" (EXACT)
- **Illinois and Texas carve-out.** Their biometric data is excluded from service development.
  - `idv-veriff-privacy`: "Veriff may use your information, except for the biometric identifiers and other information of Illinois and Texas residents, for Service development" (EXACT)
- **Conditional on the customer contract.**
  - `idv-veriff-privacy`: "Such processing is only done for internal use to improve and develop our Services and done only based on the contractual mandate received from our Customers under the precondition that a valid legal basis has been obtained." (EXACT)
- **Cross-session fraud links.** CrossLinks is on the Plus and Premium plans.
  - `idv-veriff-pricing`: "Cross-checks data points such as document, device, and network to indicate potential links between different sessions." (EXACT)
  - `idv-veriff-privacy`: "Veriff may compare if session media matches each other and if technical data indicates associations with previously occurred suspicious sessions." (EXACT)
- **Reusable identity.** Not published.
- **Customer opt-out from service-development use.** Not published as a setting.

#### Field 4. Processing and storage location; sub-processor list

- **Location.** Primary storage is in Ireland. Processing takes place from the EEA, the UK, the US and India.
  - `idv-veriff-tp-faq` (https://trust.veriff.com/faq): "For the provision of the Service, Veriff’s primary data storage location is in Ireland." (EXACT)
  - `idv-veriff-tp-faq`: "The personal data is being processed from the EEA, the UK, the US and India." (EXACT)
- **US data-residency option.** Not published.
- **Sub-processor list.** https://trust.veriff.com/subprocessors (`idv-veriff-tp-subproc`), 16 entries, including an India-based review provider.
  - `idv-veriff-tp-subproc`: "Amazon Web Services EMEA SARL • Storage, computing and media processing EEA" (EXACT)
  - `idv-veriff-tp-subproc`: "EXLService (Ireland) Limited Default sub-processor." (EXACT)
- **Help-centre version of the list.** The list linked from the privacy notice, https://help.veriff.com/en/articles/6896122-sub-processors-used-by-veriff, was **unread** (see Unread pages).

#### Field 5. Illinois BIPA and biometric laws

- **State notice.** Published.
  - `idv-veriff-privacy`: "Notice to Individuals Who are Residents of the State of Illinois and the State of Texas" (EXACT)
- **Who obtains consent.** Veriff's own flow shows icons before verification, and clicking continue is consent.
  - `idv-veriff-privacy`: "By clicking the relevant icons presented prior to the verification or authentication process, and choosing to continue, you acknowledge and agree that you have read the relevant disclosures, and that you voluntarily consent to Veriff’s collection, storage, retention, use, and disclosure of your data, including biometric data." (EXACT)
- **No profit from biometrics.**
  - `idv-veriff-privacy`: "Veriff does not sell, lease, trade or otherwise profit from the biometric data." (EXACT)
- **Public retention and destruction policy.** Published: the 3-year Illinois schedule under field 2.
- **The term "written release".** Not used.

#### Field 6. Manual review, retry and appeal path

- **Retry.** Up to 9 resubmissions are allowed, and retries are not charged (field 1).
  - `idv-veriff-decisions` (https://devdocs.veriff.com/docs/verification-session-decisions.md): "One end-user can resubmit their data up to 9 times." (EXACT)
- **Vendor-side human review.** On the Plus and Premium plans only.
  - `idv-veriff-pricing`: "All include automated verification, while Plus and Premium plans add review by trained verification specialists when automation can't decide." (EXACT)
- **Customer-side view.** The Customer Portal shows decisions.
  - `idv-veriff-decisions`: "**Manually**: the **Verifications page in the** Veriff Customer Portal" (EXACT)
- **End-user path.** The user may request human intervention or object.
  - `idv-veriff-privacy`: "at any time, you will have the right to request human intervention or object to the decision made on grounds relating to your particular situation." (EXACT)

#### Field 7. Birth date and liveness result

- **Birth date.** Returned in the decision webhook.
  - `idv-veriff-decwh` (https://devdocs.veriff.com/docs/decision-webhook.md): "\"dateOfBirth\": \"1967-03-30\"" (EXACT)
- **Liveness.** All self-serve plans include liveness, and passive liveness is named on the same page.
  - `idv-veriff-pricing`: "Key data fields extracted from ID. iBeta conformant liveness detection." (EXACT)
  - `idv-veriff-pricing`: "Verify the identity of an individual using document authenticity checks, data extraction, face matching, and passive liveness detection." (EXACT)

#### Field 8. Integration

- **React Native SDK.** `@veriff/react-native-sdk`, with explicit Expo support.
  - `idv-veriff-rn` (https://devdocs.veriff.com/docs/react-native-sdk-guide.md): "npm install @veriff/react-native-sdk --save" (EXACT)
  - `idv-veriff-rn`: "If using Expo: add the plugin to `app.json` and use EAS Build" (EXACT)
- **Hosted page and web flow.**
  - `idv-veriff-pricing`: "Hosted verification page For fast no-code implementation." (EXACT)
  - `idv-veriff-llms` (https://devdocs.veriff.com/llms.txt): "[Redirection Guide](https://devdocs.veriff.com/docs/redirection-guide-1.md): Redirect users to Veriff web flow with session management." (EXACT)
- **Also listed in the same docs index.** Native iOS and Android SDKs, Flutter, WebViews and an API.

#### Field 9. DPA and role

- **DPA.** A versioned DPA is published at https://www.veriff.com/data-processing-addendum/ver-DPA-2303 (`idv-veriff-dpa2303`). The index page https://www.veriff.com/data-processing-addendum (`idv-veriff-dpa-idx`) returned no list of versions in its static text, so it is **not established** that version 2303 is the current one.
- **Role.** The customer is the controller or business. Veriff processes on the customer's behalf and also for its Permitted Business Purposes (field 3). Section 10 carries the US service-provider restrictions.
  - `idv-veriff-dpa2303`: "The Customer shall be the controller or business of the Personal Data" (EXACT)
  - `idv-veriff-dpa2303`: "without Customer’s instruction, Veriff is prohibited from: (a) Selling or Sharing the Personal Data" (EXACT)
- **Privacy notice date.** "Last update: April 16, 2026" (`idv-veriff-privacy`, EXACT).

#### Field 10. CSAM detection or hash matching

- Nothing published on the Veriff pages read.

---

### 3. Sumsub

All pages were read on 2026-11-17.

#### Field 1. Published price; minimums and contract terms

- **Basic plan.**
  - `idv-sumsub-pricing` (https://sumsub.com/pricing/): "$1.35 per verification" (EXACT) and "$149 min. monthly commitment" (EXACT)
- **Compliance plan.** Adds AML and proof-of-address checks.
  - `idv-sumsub-pricing`: "$1.85 per verification" (EXACT) and "$299 min. monthly commitment" (EXACT)
- **Free trial.**
  - `idv-sumsub-pricing`: "Yes, we offer a 14-day free trial with 50 free checks available." (EXACT)
- **Charging.** Only successful verifications are charged.
  - `idv-sumsub-pricing`: "No, you will be charged for successful verifications only." (EXACT)
- **Enterprise tier.** Custom ("Let’s talk!").
- **Annual contract.** Not published.

#### Field 2. What it keeps, for how long, and customer controls

- **Who sets retention.** The client sets it, capped at the length of the contract. Illinois data is kept at most 3 years.
  - `idv-sumsub-privsvc` (https://sumsub.com/privacy-notice-service/, "Last updated: 19 March 2026", EXACT): "Our Clients define how long Personal data should be stored and when to delete it." (EXACT)
  - `idv-sumsub-privsvc`: "but no longer than for the period of contractual relationship with the Client" (EXACT)
  - `idv-sumsub-privsvc`: "For the residents of Illinois, the maximum retention period of Personal data, including biometric data, will be three (3) years from the date of data provision to the Sumsub system." (EXACT)
- **Data kept for development.**
  - `idv-sumsub-privsvc`: "we will keep Personal data in a pseudonymised format for the period required to calibrate and select the perfect algorithm and model" (EXACT)
- **Custom retention.** Can be bought under the Master Agreement.
  - `idv-sumsub-dpa`: "(e.g. a custom data retention period)" (EXACT)
- **On termination.** 30 days to retrieve the data, then deletion.
  - `idv-sumsub-terms` (https://sumsub.com/terms-and-conditions/): "within 30 days following the termination date" (EXACT)
- **Per-applicant deletion API or retention setting in the docs.** Not published. The docs index `idv-sumsub-llms` lists reset and deactivate endpoints for applicants, but no delete endpoint.

#### Field 3. Use for Sumsub's own purposes, and opt-outs

- **Model training.** Allowed with the client's permission.
  - `idv-sumsub-privsvc`: "This may include using Personal Data to train, test, evaluate and improve our technologies, algorithms and systems" (EXACT)
- **Self-serve terms grant that permission.**
  - `idv-sumsub-terms`: "The Customer grants the Service Provider permission to use personal data transferred to the Service Provider under these Terms and Conditions for: (i) developing and testing the Services" (EXACT)
- **Cross-customer fraud comparison.** As an independent controller.
  - `idv-sumsub-dpa`: "including, where permitted by law, comparing personal data, derived signals and event data across sessions, customers, services, datasets and third-party sources" (EXACT)
- **Face search.** Within the same client's users.
  - `idv-sumsub-privsvc`: "we compare the User's facial image to those of other Users previously verified on behalf of that particular Client" (EXACT)
- **Reusable identity (Sumsub ID).** Sumsub acts as controller.
  - `idv-sumsub-privsvc`: "The processing of Personal data for the purpose of Sumsub ID, including the creation of a dedicated storage space (“ Data Pool Key ”) for an Applicant is carried out by Sumsub as a data controller." (EXACT)
- **End-user right to object** to service-development use.
  - `idv-sumsub-privsvc`: "You have the right to object to the processing of your Personal" (EXACT)
- **Customer opt-out under the self-serve terms.** Not published.

#### Field 4. Processing and storage location; sub-processor list

- **Default location.** EU servers, with Germany as the default hosting region.
  - `idv-sumsub-privsvc`: "Sumsub confirms that all Personal data is stored on Sumsub’s servers located in the EU" (EXACT)
  - `idv-sumsub-subproc`: "Germany – by default, other countries and regions – by request and if available." (EXACT)
- **US data residency.** Available on request through Local Data Processing.
  - `idv-sumsub-ldp` (https://docs.sumsub.com/docs/local-data-processing.md): "For the v2 processing level, we currently support the following regions: * USA * UAE * Singapore" (EXACT)
  - `idv-sumsub-ldp`: "Local Data Processing is enabled on request." (EXACT)
- **Sub-processor list.** https://docs.sumsub.com/docs/third-party-processors-and-affiliates (`idv-sumsub-subproc`).
  - `idv-sumsub-subproc`: "THIRD-PARTY PROCESSORS AND AFFILIATES November 2, 2026" (EXACT)

#### Field 5. Illinois BIPA and biometric laws

- **Special biometric notice.** Covers Illinois, Washington and Texas, and requires written informed consent.
  - `idv-sumsub-privsvc`: "biometric data shall only be collected and further processed by Sumsub after obtaining a written informed consent of the respective Data Subject" (EXACT)
- **Client responsibility.**
  - `idv-sumsub-privsvc`: "Clients are independently responsible for complying with the privacy regulations, including BIPA" (EXACT)
- **Consent screen.** Shown by default in the SDK, with a separate US version.
  - `idv-sumsub-consent` (https://docs.sumsub.com/docs/consent-screen.md): "By default, the consent screen is shown at the beginning of verification" (EXACT)
  - `idv-sumsub-consent`: "the US consent for USA residents, or the global consent for everyone else" (EXACT)
  - `idv-sumsub-privdisc` (https://docs.sumsub.com/docs/applicant-privacy-disclosures-and-consent-requirements.md): "For SDK integrations, Sumsub handles the collection of Consents automatically." (EXACT)
  - `idv-sumsub-privdisc`: "I additionally consent to the processing of my biometric information and biometric identifiers as described in the Sumsub Biometrics Processing Consent" (EXACT)
- **API-only integrations.** The client must collect consent (field 8).
- **Public retention and destruction policy.** Published: the sumsub.com footer link "Data Disposal And Destruction" points to the service privacy notice (`/privacy-notice-service/`). That notice's retention section holds the Illinois 3-year rule (field 2) and a "Disposal and Destruction Policy".

#### Field 6. Manual review, retry and appeal path

- **Retry.** A `RETRY` rejection lets the applicant resubmit. A `FINAL` rejection does not.
  - `idv-sumsub-results` (https://docs.sumsub.com/docs/receive-and-interpret-results-via-api.md): "`RETRY` — applicants are allowed to resubmit their documents" (EXACT)
  - `idv-sumsub-results`: "`FINAL` — indicates a final rejection" (EXACT)
- **Vendor-side human review.**
  - `idv-sumsub-privsvc`: "A human will be involved if the system cannot reach a verdict on its own or recheck the system verdict." (EXACT)
- **Customer-side manual review step.**
  - `idv-sumsub-manualrev` (https://docs.sumsub.com/docs/delegate-rejected-applicants-for-manual-review.md): "Identify the type of terminal step—select **Manual review**." (EXACT)
- **End-user appeal.** Through the client.
  - `idv-sumsub-privsvc`: "Any User can appeal automated decisions by reviewing the methods provided on a Client's side." (EXACT)

#### Field 7. Birth date and liveness result

- **Birth date.**
  - `idv-sumsub-getapp` (https://docs.sumsub.com/reference/get-applicant-data.md): "\"dob\": \"1989-07-16\"" (EXACT)
- **Liveness.** The user is prompted to blink, smile or move the device, which is active. The analysis maps the face in 3D.
  - `idv-sumsub-privsvc`: "As a rule, Users are prompted to blink, smile, or move their device while passing Liveness." (EXACT)
  - `idv-sumsub-liveness` (https://docs.sumsub.com/docs/liveness.md): "Our neural network maps a face in 3D and analyzes it in real time." (EXACT)

#### Field 8. Integration

- **React Native module.** `@sumsub/react-native-mobilesdk-module`. Expo is not mentioned on the module page.
  - `idv-sumsub-rn` (https://docs.sumsub.com/docs/react-native-module.md): "yarn add @sumsub/react-native-mobilesdk-module" (EXACT)
- **Other paths.** WebSDK, MobileSDK, verification links and an API.
  - `idv-sumsub-liveness`: "Configure the [WebSDK](https://docs.sumsub.com/sumsub/docs/web-sdk) and [MobileSDK](https://docs.sumsub.com/sumsub/docs/mobile-sdk) integration." (EXACT)
  - `idv-sumsub-llms`: "[Verification links](https://docs.sumsub.com/docs/verification-links.md): Explore ways to create and share verification links with applicants without complex integration." (EXACT)
  - `idv-sumsub-privdisc`: "For API integrations, clients are responsible for collecting Consents" (EXACT)

#### Field 9. DPA and role

- **DPA.** Published as a PDF at https://sumsub.com/files/data_processing_agreement.pdf (`idv-sumsub-dpa`). It is titled for EU/UK parties and stamped 28.08.2026. A separate US-party DPA is not published on the pages read.
  - `idv-sumsub-dpa`: "DATA PROCESSING AGREEMENT – EU/UK PARTIES" (EXACT)
  - `idv-sumsub-dpa`: "Confidential, 28.08.2026" (EXACT)
- **DPA inside the self-serve terms.** The Terms and Conditions also include a DPA as Annex 3.
  - `idv-sumsub-terms`: "DPA means the Data Processing Agreement as contained in Annex 3 to these Terms and Conditions." (EXACT)
- **Role.** Processor, and also an independent controller for named purposes.
  - `idv-sumsub-dpa`: "Sumsub processes Personal Data provided to it by the Customer or an Applicant in relation to the Customer’s use of the Services as a Processor." (EXACT)
  - `idv-sumsub-dpa`: "as an independent Controller for the following purposes" (EXACT)

#### Field 10. CSAM detection or hash matching

- Nothing published on the Sumsub pages read.

---

### 4. Jumio

All pages were read on 2026-11-17.

#### Field 1. Published price; minimums and contract terms

- **Price.** No public price. https://www.jumio.com/pricing/ (`idv-jumio-pricing`) returned HTTP 404: "Page not found - Jumio" (EXACT).
- **Minimums.** Not published.
- **Contract.** The Jumio Service Terms and Conditions v7.3 (v07012025) are published as a PDF (`idv-jumio-tc73`).

#### Field 2. What it keeps, for how long, and customer controls

- **Biometrics, as controller.** Destroyed within three years. As processor, kept per the customer's instructions.
  - `idv-jumio-osnotice` (https://www.jumio.com/privacy-center/privacy-notices/online-services-notice/, "Last Updated: October 29, 2026", EXACT): "Jumio will permanently destroy such biometric data derived from images and recordings in its possession within three years, except where a shorter period is required by law after you first provided those images or videos." (EXACT)
  - `idv-jumio-osnotice`: "Where Jumio is a processor (or service provider), we retain personal information only as instructed by the Customer." (EXACT)
- **Other retention periods.** Available only on request.
  - `idv-jumio-osnotice`: "they are accessible upon request via the contact details provided in Section 16" (EXACT)
- **Customer controls.** Delete-credential APIs and the Portal, a biometrics-only delete, and a tenant retention period set through Jumio Support.
  - `idv-jumio-delcred` (https://documentation.jumio.ai/docs/developer-resources/API/CreateUpdateAccounts/deleting-credentials): "You can delete the credentials associated with an account , or a specific transaction . The transaction metadata and decision will not be deleted." (EXACT)
  - `idv-jumio-delcred`: "Jumio supports deleting only biometric credentials within transactions, without affecting other data." (EXACT)
  - `idv-jumio-delcred`: "You can also contact Jumio Support to set a retention period for all transactions for your tenant for automatic deletion of all credentials." (EXACT)

#### Field 3. Use for Jumio's own purposes, and opt-outs

- **Improvement and machine learning.**
  - `idv-jumio-osnotice`: "To perform analytics and research concerning the Services and to improve the Services or develop new services, including through the use of machine learning" (EXACT)
- **Licence in the terms.** A perpetual licence to user information, including biometric information.
  - `idv-jumio-tc73` (https://www.jumio.com/app/uploads/2025/07/jumio-terms-and-conditions-v7.3.v07012025.pdf): "worldwide, perpetual, irrevocable, royalty-free license (with the right to sublicense) to use, reproduce, modify, create derivative works from, distribute, transmit, and display the User Information (including any rights specifically pertaining to biometric information)" (EXACT)
- **Comparison against other end users.**
  - `idv-jumio-osnotice`: "Comparing and analyzing newly-collected personal information relating to you or another End User against previously-collected personal information relating to you or another End User to detect fraudulent activities" (EXACT)
- **Reusable identity (selfie.DONE).** The search is limited to the tenant's accepted-ID configuration. Whether a reused ID can come from another customer is **not stated** on the page read.
  - `idv-jumio-selfiedone` (https://documentation.jumio.ai/docs/quickStart/selfieDone): "Instead of scanning an ID every time, Jumio can reuse a previously verified ID when no risk is detected." (EXACT)
  - `idv-jumio-selfiedone`: "Jumio always limits the search to the “Accepted IDs” configuration of the tenant account where the transaction is processed." (EXACT)
- **End-user withdrawal of consent.** Possible, but Jumio may keep data.
  - `idv-jumio-osnotice`: "Jumio may retain your personal information independent of your consent as permitted by applicable law" (EXACT)
- **Customer opt-out.** Not published.

#### Field 4. Processing and storage location; sub-processor list

- **Location.** Data may be transferred to and processed in the US.
  - `idv-jumio-osnotice`: "Your personal information may be transferred to and processed in the United States for the purposes described in Section 6 ." (EXACT)
- **Regional API endpoints.** US, EU and SG.
  - `idv-jumio-auth` (https://documentation.jumio.ai/docs/developer-resources/API/authorization): "US https://auth.amer-1.jumio.ai/oauth2/token EU https://auth.emea-1.jumio.ai/oauth2/token SG https://auth.apac-1.jumio.ai/oauth2/token" (EXACT)
- **Statement of data-residency guarantees.** Not published.
- **Sub-processor list.** No public list was read. It is offered on request.
  - `idv-jumio-osnotice`: "a list of the third parties with whom we may share your personal information can be made available upon request" (EXACT)
- **Trust centre.** https://trust.jumio.com/ was **unread** (HTTP 403, CloudFront).

#### Field 5. Illinois BIPA and biometric laws

- **Consent built into the UI.** The Web Client and default SDK screens include consent.
  - `idv-jumio-consent` (https://documentation.jumio.ai/docs/developer-resources/API/end-user-consent): "If your integration implements the customer journey using the Web Client or the default SDK UIs, user consent management is built into the UI." (EXACT)
- **US biometric data through the API.** Consent language is needed even when Jumio is processor, and implicit consent is accepted.
  - `idv-jumio-consent`: "When biometric data is collected through the API channel from an end user located in the United States, consent language must be presented to the end user, even when Jumio acts as the data processor." (EXACT)
  - `idv-jumio-consent`: "Explicit consent, such as requiring the end user to select a checkbox, is not mandatory. Implicit consent is also accepted." (EXACT)
- **Customer obligation under the terms.** Where Jumio's UI is not used, the customer obtains consent on Jumio's behalf.
  - `idv-jumio-tc73`: "then Customer shall present such notice and obtain consent on behalf of Jumio" (EXACT)
- **Public retention and destruction policy.** Published: the 3-year rule under field 2.
- **Illinois-specific section or the term "written release".** Not published. "Illinois", "BIPA" and "written release" do not appear in the online services notice.

#### Field 6. Manual review, retry and appeal path

- **Retry guidance.**
  - `idv-jumio-bizlogic` (https://documentation.jumio.ai/docs/developer-resources/businessLogicGuide): "Common next steps are to prompt to retry, perhaps on a different channel." (EXACT)
  - `idv-jumio-bizlogic`: "Liveness REJECTED Typically maps to fraud/bad actor." (EXACT)
- **Customer-side portal.** The Jumio Portal Explorer for viewing transactions is listed in the docs index (`idv-jumio-llms`).
- **Manual review by Jumio staff.** Not published on the pages read.
- **End-user appeal of a verification decision.** Not published. The notice offers an appeal only for denied privacy-rights requests.

#### Field 7. Birth date and liveness result

- **Birth date.**
  - `idv-jumio-extract` (https://documentation.jumio.ai/docs/references/capabilities/extraction): "dateOfBirth string($date) The ID holder's date of birth." (EXACT)
- **Liveness result.** A Liveness capability returns PASSED, WARNING or REJECTED.
  - `idv-jumio-liveness` (https://documentation.jumio.ai/docs/references/capabilities/liveness): "The Liveness capability provides automated checks that ensure the end user is physically present during the verification and is not attempting a spoofing attack." (EXACT)
- **Premium liveness.** Uses "active illumination".
  - `idv-jumio-livprod` (https://www.jumio.com/products/liveness-detection/): "Jumio’s premium liveness solution uses active illumination, a patented Jumio technique" (EXACT)
- **Passive or active for standard liveness.** Not published.

#### Field 8. Integration

- **React Native plugin.** Installed from GitHub rather than a named npm registry package. Expo is not mentioned.
  - `idv-jumio-rn` (https://documentation.jumio.ai/docs/developer-resources/SDKs/crossplatform/mobile-react-master/README_React): "npm install --save https://github.com/Jumio/mobile-react.git#v4.13.0" (EXACT)
- **Native SDKs.**
  - `idv-jumio-sdks` (https://documentation.jumio.ai/docs/developer-resources/SDKs/Overview_of_SDKs): "Jumio provides dedicated Mobile SDKs for iOS and Android" (EXACT)
- **Hosted Web Client.**
  - `idv-jumio-llms` (https://documentation.jumio.ai/llms.txt): "Jumio provides a turnkey web client that you can provide to your end users to guide them through the customer journey." (EXACT)
- **Also documented.** Web SDK and REST API.

#### Field 9. DPA and role

- **DPA.** None was published on the pages read. The terms index lists no DPA, and terms v7.3 ends earlier DPAs.
  - `idv-jumio-tc73`: "any data processing agreements or addenda entered into between the Parties shall no longer be effective with respect to data processed by Jumio after the Effective Date of this Agreement." (EXACT)
- **Role.** Controller by default, and processor for certain customers.
  - `idv-jumio-consent`: "By default, Jumio acts as the data controller for end-user credentials. In certain cases, Jumio may act as the data processor." (EXACT)
  - `idv-jumio-osnotice`: "For certain Customers (including some in the EEA/UK), Jumio serves as a “processor” (or “service provider”)." (EXACT)

#### Field 10. CSAM detection or hash matching

- No detection or hash matching is published. The only related text is a general content rule in the terms, which is not CSAM detection.
  - `idv-jumio-tc73`: "Customer and its Users shall not use the Service to transmit inappropriate content." (EXACT)

---

### Cross-service summary (short cells; details and quotes above)

| Field | Stripe Identity | Veriff | Sumsub | Jumio |
|---|---|---|---|---|
| 1. Price | $1.50 per verification; first 50 free. Minimum and contract: not published. | Self-serve $0.80, $1.39 or $1.89; monthly minimums $49, $99 or $209; 15-day trial (50 sessions); custom above 5,000 a month. | $1.35 (minimum $149 a month) or $1.85 (minimum $299 a month); 14-day trial with 50 checks. | No public price (404). |
| 2. Retention default | Biometrics up to 1 year; other data 7 years. | Session data 3 or 6 months by plan (2 years extra); Illinois biometrics 3 years or less; may keep data for own purposes. | Set by client, capped at contract length; Illinois at most 3 years. | Biometrics within 3 years (controller); per customer (processor). |
| 2. Customer delete or retention control | Redact API or Dashboard (up to 7 days per docs; 4 days per support page). | Delete API on Premium, off by default, 10 a day; enterprise retention setting. | Custom retention by contract; delete API not published. | Delete-credential APIs and Portal; biometrics-only delete; tenant retention via Support. |
| 3. Own use | Cross-customer selfie fraud checks (user opt-out); training only with separate consent; Link reuse. | ML training under DPA (excludes Illinois and Texas biometrics); CrossLinks. | Training with client permission (granted in self-serve terms); cross-customer fraud comparison; Sumsub ID reuse. | ML improvement; perpetual licence including biometrics; selfie.DONE reuse. |
| 4. Location | US. | Stored in Ireland; processed EEA, UK, US, India; US residency not published. | EU (Germany default); US region on request. | US; regional endpoints US, EU, SG. |
| 4. Sub-processor list | stripe.com/legal/service-providers | trust.veriff.com/subprocessors | docs.sumsub.com/docs/third-party-processors-and-affiliates | Not public (on request). |
| 5. Consent and BIPA | Stripe's flow, two consents; Illinois notice not published. | Veriff's flow (clicking icons); Illinois and Texas notice. | SDK consent screen with US version; notice requires "written informed consent". | Built into Web Client and SDK; API needs customer consent, implicit accepted; no Illinois section. |
| 6. Review and retry | `requires_input` retry; Dashboard override; some manual reviewers. | 9 resubmissions; specialists on Plus and Premium; user may request human review. | RETRY or FINAL; Sumsub human when system cannot decide; client manual-review step. | Retry guidance; Jumio staff review not published. |
| 7. Birth date / liveness | `dob` yes; "liveness" not named; manipulation and presentation-attack checks. | `dateOfBirth` yes; passive liveness. | `dob` yes; active prompts (blink, smile, move). | `dateOfBirth` yes; Standard or Premium (active illumination). |
| 8. RN or Expo package | `@stripe/stripe-identity-react-native`; Expo not mentioned. | `@veriff/react-native-sdk`; Expo plugin with EAS Build. | `@sumsub/react-native-mobilesdk-module`; Expo not mentioned. | GitHub `Jumio/mobile-react`; Expo not mentioned. |
| 8. Other paths | iOS, Android, web modal or redirect, no-code, API. | iOS, Android, Flutter, hosted page, API. | WebSDK, MobileSDK, links, API. | iOS, Android, Web SDK, Web Client, API. |
| 9. DPA / role | Yes (2026-09-28); processor and controller. | Yes (ver-DPA-2303; current version not established); customer controller, Veriff also for own purposes. | Yes (EU/UK PDF, 28.08.2026; Annex 3 in terms); processor and independent controller. | Not published; controller by default. |
| 10. CSAM / hash matching | Not published. | Not published. | Not published. | Not published. |

## Appendix B. Photo check services and hash matching: every field, with its page and quotation

Written by the photo check subagent and checked by this session (section 11). Every page was read on 17 November 2026. A fetch name maps to its URL, final URL, HTTP code, bytes, SHA-256 and page date in appendix C; each quotation's check result follows it.

### How the candidates were chosen

Stated method (applied the same way to every candidate): a service qualifies for Part A if its own pages, read today, show all three of:
1. an image-moderation API with classes for nudity or sexual content **and** for violence;
2. a published price for that image API (a public price list, not only "contact sales");
3. published data-handling terms (a data-use/privacy FAQ, DPA or service terms covering submitted content).

Candidates considered: the six named in the brief (Amazon Rekognition, Google Cloud Vision SafeSearch, Azure AI Content Safety, Hive, Sightengine, Clarifai). No others were added.

| Candidate | Sexual + violence classes | Public image price | Data-handling terms | Result |
|---|---|---|---|---|
| Amazon Rekognition (DetectModerationLabels) | yes (A1-c2, A1-c3) | yes | yes (FAQ, Service Terms, DPA) | chosen |
| Google Cloud Vision SafeSearch | yes: adult, racy, violence (A2-c1) | yes | yes (Data Usage FAQ, Cloud DPA) | chosen |
| Azure AI Content Safety (Analyze image) | yes: sexual, violence, hate, self-harm (A3-c1) | yes (rendered page) | yes (data-privacy page, Microsoft DPA) | chosen |
| Hive Visual Moderation (now under the **Deploy** brand: thehive.ai/pricing redirects to deploy.com/pricing) | yes (A4-c1, A4-c2) | yes, $3.00 / 1,000 requests with a 100 requests/day limit; higher limits are "Contact Sales", and the docs say Visual Moderation requires an annual contract | yes (terms of use, FAQ retention answer) | chosen, with the contract caveat recorded |
| Sightengine | yes (A5-c1, A5-c2) | yes | yes (FAQ, terms, DPA, sub-processor list) | chosen |
| Clarifai | could not be checked | could not be checked | could not be checked | **not chosen: its pages could not be read today** (curl connection reset; Chromium HTTP 502; docs host 502). This is not a judgement on the service. |

Quote IDs in this table refer to the quotations in the Part A sections below.

### Part A — automated photo check services

#### A1. Amazon Rekognition — content moderation (DetectModerationLabels)

Classes: three-level taxonomy, for example Explicit > Explicit Sexual Activity; Violence > Graphic Violence > Weapon Violence; Visually Disturbing > Death and Emaciation.
- Taxonomy and classes.
  - `mod-aws-rek-modapi`: "Amazon Rekognition uses a three-level hierarchical taxonomy to label categories of inappropriate, unwanted, or offensive content." (EXACT)
  - `mod-aws-rek-modapi`: "Explicit Sexual Activity" (EXACT)
  - `mod-aws-rek-modapi`: "Graphic Violence Weapon Violence" (EXACT)
  - `mod-aws-rek-modapi`: "Visually Disturbing Death and Emaciation" (EXACT)
- AWS names dating sites as a use case.
  - `mod-aws-rek-faqs`: "This API can be used in moderation workflows for applications such as social and dating sites" (EXACT)

**1. Published price**

- Per image, tiered by monthly volume. DetectModerationLabels is a Group 2 API.
  - `mod-aws-rek-pricing`: "Group 2: DetectFaces, DetectModerationLabels, DetectLabels, DetectText, RecognizeCelebrities, DetectProtectiveEquipment APIs" (EXACT)
  - `mod-aws-rek-pricing`: "Usage is billed based on a tiered pricing model tied to volume of images processed per month." (EXACT)
  - `mod-aws-rek-pricing`: "Group API* First 1 million images Next 4 million images Next 30 million images Over 35 million images" (EXACT)
- Group 2 prices for US East (N. Virginia) from AWS's public pricing data file, which the pricing page loads (the HTML table itself is filled by JavaScript): $0.0010 per image for the first 1 million images a month, $0.0008 for the next 4 million, $0.0006 for the next 30 million, $0.00025 over 35 million. The region key "US East (N. Virginia)" was read by parsing the JSON; the file's manifest is dated 2026-09-11.
  - `mod-aws-rek-pricejson`: ""rateCode":"22JVRTPVPTB5SRD7.JRTCKXETXF.SB2VSFF4TP","price":"0.0010000000"" (EXACT)
  - `mod-aws-rek-pricejson`: ""rateCode":"22JVRTPVPTB5SRD7.JRTCKXETXF.H3BBRCJ78Y","price":"0.0008000000"" (EXACT)
  - `mod-aws-rek-pricejson`: ""rateCode":"22JVRTPVPTB5SRD7.JRTCKXETXF.8GSZJDB5W5","price":"0.0006000000"" (EXACT)
  - `mod-aws-rek-pricejson`: ""rateCode":"22JVRTPVPTB5SRD7.JRTCKXETXF.SHZJ45KC4M","price":"0.0002500000"" (EXACT)
- Free tier: 1,000 images a month in Group 2 for 12 months from account creation; new customers from 15 July 2025 receive up to $200 in Free Tier credits.
  - `mod-aws-rek-pricing`: "During the free tier period you can analyze 1,000 images per month for free each, in Group 1 and Group 2 APIs." (EXACT)
  - `mod-aws-rek-pricing`: "The free tier period lasts 12 months from the date of account creation." (EXACT)
  - `mod-aws-rek-pricing`: "Starting July 15, 2025, new AWS customers will receive up to $200 in AWS Free Tier credits" (EXACT)
- Minimum spend or contract term: not published on the pricing page read (pay per image).
  - Pages checked (read 2026-11-17): `mod-aws-rek-pricing`

**2. What it keeps, and for how long**

- Inputs may be stored; the Rekognition FAQ says they may be stored and used to provide the service and, unless the customer opts out, to improve Amazon technologies. A retention period for images or results is **not published**.
  - `mod-aws-rek-faqs`: "Amazon Rekognition may store and use image and video inputs processed by the service solely to provide and maintain the service and, unless you opt out as provided below, to improve and develop the quality of Amazon Rekognition and other Amazon machine-learning/artificial-intelligence technologies." (EXACT)
- Deletion: by request to AWS Support; opting out deletes stored copies kept for service improvement, but not content used to provide the service.
  - `mod-aws-rek-faqs`: "You can request deletion of image and video inputs associated with your account by contacting AWS Support ." (EXACT)
  - `mod-aws-ai-optout`: "When you opt out of content use by an AWS AI service, that service deletes all of the associated historical content that was shared with AWS before you set the option." (EXACT)
  - `mod-aws-ai-optout`: "any content that is used to provide the service to you is not deleted" (EXACT)

**3. Own use of images/results (training, improvement) and opt-out**

- Yes, by default: Service Terms 50.3 let AWS use and store "AI Content" processed by Rekognition to develop and improve the service; content that is not personal data may be used for other AWS/affiliate ML technologies.
  - `mod-aws-service-terms`: "(a) we may use and store AI Content that is processed by each of the foregoing AI Services to develop and improve the applicable AI Service and its underlying technologies" (EXACT)
- Opt-out: an AWS Organizations AI services opt-out policy. Without it, content may be stored in another AWS Region for this purpose.
  - `mod-aws-service-terms`: "You may instruct AWS not to use and store AI Content processed by an AI Service to develop and improve that Service or technologies of AWS or its affiliates by configuring an AI services opt-out policy using AWS Organizations." (EXACT)
  - `mod-aws-ai-optout`: "For this purpose, we might store such content in an AWS Region outside of the AWS Region where you are using the service." (EXACT)
- The customer is responsible for privacy notices and consents to its end users for AI Content.
  - `mod-aws-service-terms`: "You are responsible for providing legally adequate privacy notices to End Users of your products or services that use any AI Service" (EXACT)

**4. Where it processes data; sub-processor list**

- Customer chooses the AWS Region endpoint; the endpoints page lists US and other regions (e.g. us-east-1, us-east-2, us-west-1, us-west-2).
  - `mod-aws-rek-endpoints`: "US East (Ohio) us-east-2 rekognition.us-east-2.amazonaws.com" (EXACT)
- Sub-processor list published: https://aws.amazon.com/compliance/sub-processors/ . Rekognition is listed among services whose "AWS development entities" provide service improvement (processing location shown as USA, from reading the stripped table) unless the customer opts out.
  - `mod-aws-subprocessors`: "AWS will update this page at least 30 days before engaging a new sub-processor" (EXACT)
  - `mod-aws-subprocessors`: "Unless customer opts out of AWS using Customer Data for service improvement, where permitted in accordance with the AWS Service Terms, the AWS entities listed below provide service improvement for the applicable AWS services." (EXACT)

**5. Illinois BIPA / biometric data**

- Published. The Biometric Notice and Consent Terms govern use of Amazon Rekognition and name Illinois BIPA; notices and consents must be given on behalf of the customer and AWS. The FAQ gives sample notice-and-consent language. Service Terms 50.9.2 make AWS the customer's processor for face vectors when Rekognition's face APIs are used. Whether DetectModerationLabels itself computes face data is not stated on the pages read.
  - `mod-aws-biometric-terms`: "These terms and conditions govern your access to and use of Amazon Rekognition, Amazon Chime SDK speaker search, Amazon Connect Voice ID, and Amazon One Enterprise Services." (EXACT)
  - `mod-aws-biometric-terms`: "including without limitation requirements under the Illinois Biometric Information Privacy Act (“BIPA”)" (EXACT)
  - `mod-aws-biometric-terms`: "Any notices you provide, and any consents you obtain, must be provided and obtained on behalf of you and on behalf of AWS (identified as your service provider)." (EXACT)
  - `mod-aws-rek-faqs`: "If you provide notice and obtain consent, you should do so on behalf of any relevant service providers, including AWS (identified as your service provider)." (EXACT)
  - `mod-aws-service-terms`: "if you use Amazon Rekognition’s face APIs to analyze, detect, or process faces in images or videos, then you instruct AWS, as your processor, to: (1) generate face vectors and extract other facial attributes on your behalf" (EXACT)

**6. Manual review path / disputed results**

- Amazon Augmented AI (A2I), integrated with DetectModerationLabels: reviewers can be the customer's own workforce, Amazon Mechanical Turk or vetted vendors (A2I is a separately priced AWS service; its price was not read). The customer's own path for disputes is otherwise not described.
  - `mod-aws-a2i-rek`: "Amazon A2I provides a human review workflow for image moderation." (EXACT)
  - `mod-aws-a2i-rek`: "With Amazon A2I, you can use a pool of reviewers within your own organization or Amazon Mechanical Turk." (EXACT)
  - `mod-aws-rek-moderation`: "typically 1-5% of the total volume, already flagged by machine learning" (EXACT)

**7. Birth date, liveness, age estimation**

- Not applicable: moderation returns labels and confidence scores, not a birth date or liveness result. Separate features are published: DetectFaces returns an estimated AgeRange, and Rekognition Face Liveness has its own pricing.
  - `mod-aws-rek-agerange`: "Amazon Rekognition estimates an age range for faces detected in the input image." (EXACT)
  - `mod-aws-rek-pricing`: "Amazon Rekognition Face Liveness pricing" (EXACT)

**8. Integration**

- REST/SDK API; image sent as base64 bytes or as an S3 object reference; JPEG or PNG. Server SDKs listed include JavaScript v3, Python (Boto3), Java, Go, .NET, PHP, Ruby, Kotlin, C++.
  - `mod-aws-rek-dml-api`: "You pass the input image either as base64-encoded image bytes or as a reference to an image in an Amazon S3 bucket." (EXACT)
  - `mod-aws-rek-dml-api`: "The image must be either a PNG or JPEG formatted file." (EXACT)
  - `mod-aws-rek-dml-api`: "AWS SDK for JavaScript V3 AWS SDK for Kotlin AWS SDK for PHP V3 AWS SDK for Python (Boto3)" (EXACT)
- React Native client: AWS Amplify's React Native docs show `Predictions.identify` with type 'UNSAFE' (requires IAM roles set up through Amplify). Expo is not mentioned on that page.
  - `mod-amplify-rn-label`: "Detect unsafe content in an image" (EXACT)
  - `mod-amplify-rn-label`: "type : 'UNSAFE'" (EXACT)
  - `mod-amplify-rn-label`: "set up the IAM roles with the right policy actions" (EXACT)

**9. DPA and role**

- DPA published (https://d1.awsstatic.com/legal/aws-dpa/aws-dpa.pdf) and incorporated by the Service Terms; AWS acts as processor. AWS CCPA Terms (https://d1.awsstatic.com/legal/aws-ccpa/aws-ccpa-terms.pdf) apply when CCPA applies; they restrict AWS's use and prohibit selling or sharing, but do not use the words "service provider" in the text read.
  - `mod-aws-dpa-pdf`: "In this context, AWS will act as processor to Customer, who can act either as controller or processor of Customer Data." (EXACT)
  - `mod-aws-service-terms`: "These Service Terms incorporate the AWS Data Processing Addendum (“DPA”), when you use AWS Services to process Customer Data" (EXACT)
  - `mod-aws-ccpa-terms`: "not retain, use, or disclose Personal Information for any purpose, including any commercial purpose, except as permitted in the Agreement or under CCPA" (EXACT)
  - `mod-aws-ccpa-terms`: "not sell or share Personal Information" (EXACT)

**10. CSAM detection or hash matching offered by the service**

- No. The FAQ says the moderation API does not detect illegal content such as CSAM, and CSAM is not accepted through the feedback process. No AWS CSAM hash-matching service was found on the pages read (Safer by Thorn is sold on AWS Marketplace; see Part B).
  - `mod-aws-rek-faqs`: "this API does not detect whether an image includes illegal content (such as child sexual abuse material) or unnatural adult content" (EXACT)
  - `mod-aws-rek-faqs`: "Please note that illegal content (such as child sexual abuse material) will not be accepted through this process." (EXACT)

#### A2. Google Cloud Vision API — SafeSearch detection

- Classes: likelihoods for adult, spoof, medical, violence and racy.
  - `mod-gcv-safesearch`: "This feature uses five categories ( adult , spoof , medical , violence , and racy ) and returns the likelihood that each is present in a given image." (EXACT)

**1. Published price**

- Per 1,000 units, where each feature applied to an image is one unit: SafeSearch first 1,000 units a month free, $1.50 per 1,000 from 1,001 to 5,000,000, $0.60 per 1,000 above 5,000,000 (list column; two further columns are Gemini Enterprise Flexible Savings Plan discounts, which may require opting in).
  - `mod-gcv-pricing`: "Safe Search (explicit content) Detection 0 count to 1,000 count $0.00 (Free) 1,000 count to 5,000,000 count $1.50 5,000,000 count and above $0.60" (EXACT)
  - `mod-gcv-pricing`: "The table below shows the price for each feature per 1000 units." (EXACT)
  - `mod-gcv-pricing`: "Pricing is tiered - the first 1000 units used each month are free" (EXACT)
  - `mod-gcv-pricing`: "Each feature applied to an image is a billable unit ." (EXACT)
  - `mod-gcv-pricing`: "You may need to opt-in to be eligible for consumption model discounts." (EXACT)
- Minimums or contract terms: not published on the pricing page read.
  - Pages checked (read 2026-11-17): `mod-gcv-pricing`

**2. What it keeps, and for how long**

- Online requests: image processed in memory, not persisted to disk. Asynchronous batch: stored briefly, typically deleted after processing with a failsafe TTL of a few hours. Request metadata is logged temporarily. Retention of results: not published beyond this.
  - `mod-gcv-datausage`: "For online (immediate response) operations ( BatchAnnotateImages and BatchAnnotateFiles ), the image data is processed in memory and not persisted to disk." (EXACT)
  - `mod-gcv-datausage`: "The stored image is typically deleted right after the processing is done, with a failsafe Time to live (TTL) of a few hours." (EXACT)
  - `mod-gcv-datausage`: "Google also temporarily logs some metadata about your Vision API requests (such as the time the request was received and the size of the request) to improve our service and combat abuse." (EXACT)

**3. Own use of images/results (training, improvement) and opt-out**

- Google says it does not use the content to train or improve Cloud Vision and uses content only to provide the service; an opt-out is therefore not described.
  - `mod-gcv-datausage`: "Google does not use the content you send to train and improve our Cloud Vision features such as its machine perception model." (EXACT)
  - `mod-gcv-datausage`: "Google does not use any of your content (such as images and labels) for any purpose except to provide you with the Vision API service." (EXACT)

**4. Where it processes data; sub-processor list**

- Regional (EU/US) endpoints are documented on the OCR page, which says multi-regional support currently applies only to the OCR feature. A processing location for SafeSearch requests on the default global endpoint: **not published** on the pages read.
  - `mod-gcv-ocr`: "This functionality currently only applies to the OCR feature (types TEXT_DETECTION or DOCUMENT_TEXT_DETECTION )." (EXACT)
  - `mod-gcv-ocr`: "The Vision API supports a global API endpoint ( vision.googleapis.com ) and also two region-based endpoints" (EXACT)
- Sub-processor list published: https://cloud.google.com/terms/subprocessors (Google Cloud Platform-wide).
  - `mod-gcp-subprocessors`: "Google and its affiliates engage the third-party entities in the table below to perform limited activities in connection with the Google Cloud Platform Services." (EXACT)

**5. Illinois BIPA / biometric data**

- Nothing on BIPA or "biometric" was found in the Cloud service-specific terms or the Cloud DPA (0 matches). The face-detection page says Vision does not support facial recognition or individual identification. SafeSearch itself is not described as processing faces.
  - `mod-gcv-faces`: "The Cloud Vision API doesn't support facial recognition or individual identification." (EXACT)
  - Pages checked (read 2026-11-17): `mod-gcp-service-terms`; `mod-gcp-dpa`

**6. Manual review path / disputed results**

- Not published: no human-review service or dispute path for SafeSearch was found on the pages read; the customer would need its own path.
  - Pages checked (read 2026-11-17): `mod-gcv-safesearch`; `mod-gcv-datausage`

**7. Birth date, liveness, age estimation**

- Not applicable to SafeSearch. No age-estimation output was found on the face-detection page (0 matches for age).
  - Pages checked (read 2026-11-17): `mod-gcv-faces`

**8. Integration**

- REST: base64 image content in the request body, or a Cloud Storage URI or public web URL (Google advises not depending on externally hosted images in production). Server client libraries: C++, C#, Go, Java, Node.js, PHP, Python, Ruby. React Native/Expo client SDK: not published on the pages read.
  - `mod-gcv-safesearch`: "For REST requests, send the contents of the image file as a base64 encoded string in the body of your request." (EXACT)
  - `mod-gcv-safesearch`: "To send a remote file request, specify the file's Web URL or Cloud Storage URI in the request body." (EXACT)
  - `mod-gcv-safesearch`: "don't depend on externally-hosted images for production applications" (EXACT)
  - `mod-gcv-libraries`: "Client libraries Overview C++ Reference C# Reference Go Reference Java Reference Node.js Reference PHP Reference Python Reference Ruby Reference" (EXACT)

**9. DPA and role**

- Vision API is covered by the Cloud Data Processing Addendum (https://cloud.google.com/terms/data-processing-addendum): Google is a processor; under applicable privacy law "processor" includes "service provider".
  - `mod-gcv-datausage`: "Vision API complies with the Cloud Data Processing Addendum ." (EXACT)
  - `mod-gcp-dpa`: "Google is a processor and Customer is a controller or processor, as applicable, of Customer Personal Data." (EXACT)
  - `mod-gcp-dpa`: "The terms “data subject”, “controller” and “processor” include “consumer”, “business”, and “service provider”, respectively, as required by Applicable Privacy Law." (EXACT)

**10. CSAM detection or hash matching offered by the service**

- Not on the Vision pages read. Google offers CSAM tools separately through its Child Safety Toolkit (Content Safety API and CSAI Match; see Part B).
  - Pages checked (read 2026-11-17): `mod-gcv-safesearch`; `mod-goog-toolkit`

#### A3. Microsoft Azure AI Content Safety — Analyze image

- Classes: sexual, violence, hate and self-harm, each with severity; the image model returns severities 0, 2, 4 and 6.
  - `mod-azcs-overview`: "Analyze image API Scans images for sexual content, violence, hate, and self harm with multi-severity levels." (EXACT)
  - `mod-azcs-harm`: "The classifier only returns severities 0, 2, 4, and 6." (EXACT)

**1. Published price**

- Standard tier $0.75 per 1,000 images; Free tier 5,000 images a month, and usage stops at the free limit. These values appeared only on the Chromium-rendered page (the curl copy shows "$-"); the region the displayed price applies to is not shown (the region selector had no default value). Prices are labelled estimates. A disconnected-container commitment tier is listed at $103,883 a year for up to 180M images.
  - `mod-azcs-pricing-r`: "Image Multimodal $0.75 per 1,000 images" (EXACT)
  - `mod-azcs-pricing-r`: "Image Multimodal 5,000 images per month" (EXACT)
  - `mod-azcs-pricing-r`: "Usage is stopped if the transaction limit is reached on the Free tier." (EXACT)
  - `mod-azcs-pricing-r`: "500,000 Analyze Image S1 $0.75 /1,000 * 500,000 = $375" (EXACT)
  - `mod-azcs-pricing-r`: "Prices are estimates only and are not intended as actual price quotes." (EXACT)
  - `mod-azcs-pricing-r`: "Image $103,883 180M images 15M images" (EXACT)

**2. What it keeps, and for how long**

- No input images are stored during detection (except customer blocklists); inputs are not stored or made available for human review by Microsoft employees. Retention of results: not published beyond this.
  - `mod-azcs-privacy`: "No input texts or images are stored in the model during detection (except for customer-supplied blocklists, as discussed below), and user inputs are not used to train, retrain, or improve the Azure AI Content Safety models." (EXACT)
  - `mod-azcs-privacy`: "User input data sent to Azure AI Content Safety is not stored or made available for human review by Microsoft employees." (EXACT)

**3. Own use of images/results (training, improvement) and opt-out**

- Microsoft says it does not use customer data to train, retrain or improve the Content Safety models; no opt-out is needed or described.
  - `mod-azcs-privacy`: "We do not use customer data to train, retrain or improve the models in Azure AI Content Safety." (EXACT)

**4. Where it processes data; sub-processor list**

- Data stays in the region chosen for the resource, though the region page says some features require global or data-zone routing. The region table marks "Content harms image" as available in US regions centralus, eastus, eastus2, northcentralus, southcentralus, westus, westus2 and westus3 (reading of the stripped table).
  - `mod-azcs-privacy`: "All customer data sent to Azure AI Content Safety remains within Azure AI Content Safety and in the region you chose and will not be transmitted to other regions." (EXACT)
  - `mod-azcs-regions`: "When you use Azure AI Content Safety directly, create the resource in the region where you want data processed." (EXACT)
  - `mod-azcs-regions`: "Some features require global or data zone routing." (EXACT)
  - `mod-azcs-regions`: "Content harms image - - ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅" (EXACT)
- Sub-processors: the Microsoft DPA says information is on a Microsoft website without giving the URL in the text. A Microsoft Online Services Subprocessors PDF was read from Microsoft's Service Trust API host (URL found by web search); it is dated 28 February 2025, and whether it is the current issue could not be confirmed.
  - `mod-ms-dpa-docx`: "Microsoft makes available information about Subprocessors on a Microsoft website." (EXACT)
  - `mod-ms-subproc-pdf`: "Microsoft Online Services Subprocessors DATE OF ISSUE: February 28, 2025" (EXACT)

**5. Illinois BIPA / biometric data**

- Content Safety pages do not describe face processing. The Microsoft Products and Services DPA has a Biometric Data clause putting notice, consent and deletion on the customer; BIPA is not named in the text read.
  - `mod-ms-dpa-docx`: "If Customer uses Products and Services to process Biometric Data, Customer is responsible for: (i) providing notice to data subjects" (EXACT)

**6. Manual review path / disputed results**

- No Microsoft human-review service was found. The transparency note recommends human judgement over full automation; Content Safety Studio offers a monitoring "moderation workflow". The dispute path is the customer's own.
  - `mod-azcs-transparency`: "We recommend using Azure AI Content Safety to support people making accurate and efficient judgments, rather than fully automating a process." (EXACT)
  - `mod-azcs-overview`: "Studio also lets you set up a moderation workflow , where you can continuously monitor and improve content moderation performance." (EXACT)

**7. Birth date, liveness, age estimation**

- Not applicable; no age-estimation or liveness feature was found on the Content Safety pages read.
  - Pages checked (read 2026-11-17): `mod-azcs-overview`

**8. Integration**

- REST; image as base64 `content` or an Azure `blobUrl`; 4 MB maximum. Server SDKs in the quickstart: Python (azure-ai-contentsafety), JavaScript/TypeScript (@azure-rest/ai-content-safety), .NET (Azure.AI.ContentSafety), Java. React Native/Expo client SDK: not published.
  - `mod-azcs-qs-image`: "Populate the "image" field in the body with either a "content" field or a "blobUrl" field." (EXACT)
  - `mod-azcs-regions`: "Analyze image API : Maximum image file size: 4 MB" (EXACT)
  - `mod-azcs-qs-image`: "python -m pip install azure-ai-contentsafety" (EXACT)
  - `mod-azcs-qs-image`: "npm install @azure-rest/ai-content-safety" (EXACT)
  - `mod-azcs-qs-image`: "search for Azure.AI.ContentSafety" (EXACT)

**9. DPA and role**

- Microsoft Products and Services DPA (November 2026 English edition, .docx) published at https://www.microsoft.com/licensing/docs/view/Microsoft-Products-and-Services-Data-Protection-Addendum-DPA . Microsoft is processor; a CCPA section limits retention, use and disclosure.
  - `mod-ms-dpa-docx`: "Customer and Microsoft agree that Customer is the controller of Personal Data and Microsoft is the processor of such data" (EXACT)
  - `mod-ms-dpa-docx`: "Microsoft will process Customer Data, Professional Services Data, and Personal Data on behalf of Customer and, not retain, use, or disclose that data for any purpose other than for the purposes set out in the DPA Terms and as permitted under the CCPA" (EXACT)

**10. CSAM detection or hash matching offered by the service**

- No. The overview says Content Safety cannot be used to detect illegal child exploitation images. Microsoft offers PhotoDNA separately (Part B).
  - `mod-azcs-overview`: "You can't use Azure AI Content Safety to detect illegal child exploitation images." (EXACT)

#### A4. Hive Visual Moderation (Hive is now presented under the Deploy brand)

thehive.ai/pricing returned the page at https://deploy.com/pricing (final URL in the Sources table); thehive.ai/terms is a JavaScript redirect to deploy.com, so the Deploy terms of use and privacy policy were read. Developer docs remain at docs.thehive.ai.
- Classes include sexual content and violent imagery heads (e.g. blood/gore).
  - `mod-hive-docs-vcm`: "Broadly, visual moderation classes can be separated into five main categories: sexual content, violent imagery, drugs, hate imagery, and image attributes." (EXACT)
  - `mod-hive-docs-vcm`: "very_bloody - gore, visible bleeding, self-cutting" (EXACT)

**1. Published price**

- Visual Moderation: $3.00 per 1,000 requests with a 100 requests/day limit; higher limits "Contact Sales". The docs describe that tier as for developer testing only and say Visual Moderation requires an annual contract, pointing smaller customers to the self-serve VLM (DeployVLM, priced per token). V2 is reserved for Enterprise projects (higher throughput, custom support or invoiced billing). Fees are non-cancelable and non-refundable under the terms.
  - `mod-hive-pricing`: "Visual Moderation Limit: 100 requests/day $3.00 / 1000 Requests Visual Moderation (higher limits) Contact Sales" (EXACT)
  - `mod-hive-docs-vcm`: "For developer testing ONLY : 100 requests/day limit." (EXACT)
  - `mod-hive-docs-vcm`: "Note: Visual Moderation requires an annual contract. Smaller customers should use our self-serve VLM ." (EXACT)
  - `mod-hive-pricing`: "DeployVLM $0.50 / 1M Input Tokens $2.50 / 1M Output Tokens" (EXACT)
  - `mod-hive-faq`: "*V2* is reserved for Enterprise projects that need higher throughput, custom support, or invoiced billing." (EXACT)
  - `mod-deploy-termsofuse`: "payment obligations are non-cancelable and fees paid are non-refundable" (EXACT)

**2. What it keeps, and for how long**

- FAQ: customer data is kept for 14 days by default; the retention period can be raised or lowered on request, including no retention. Configurable retention is also stated on the Enterprise Commitments page.
  - `mod-hive-faq`: "Our default policy is to retain customer data for 14 days. We can increase or decrease our retention time upon request according to your needs (including not retaining your data at all)." (EXACT)
  - `mod-deploy-entcommit`: "Configurable data retention — Set custom rules for how your data is retained or removed." (EXACT)

**3. Own use of images/results (training, improvement) and opt-out**

- Yes, by default. The terms grant Deploy a right to use Customer-Provided Content to provide, develop and improve its services, subject to limits agreed in writing. AI Services subject content to **manual review by Hive Workers** unless both parties agree in writing that it will not be done. Demo Content carries a perpetual licence including development and improvement. The terms also require Deploy's prior written consent before personal data is submitted. A self-serve opt-out is not published; the route is written agreement.
  - `mod-deploy-termsofuse`: "you hereby grant Deploy a non-exclusive, worldwide, royalty-free right to access, process, store, transmit and otherwise use Customer-Provided Content solely (a) for purposes of providing, developing and improving Deploy Services, their underlying technologies and the output Deploy delivers to Customer" (EXACT)
  - `mod-deploy-termsofuse`: "Subject to any limitations agreed upon in writing between you and Deploy" (EXACT)
  - `mod-deploy-termsofuse`: "using AI Services will subject Customer-Provided Content to manual review by Hive Workers (as defined in the Labeling Service Addendum ) to, among other things, confirm machine learning model predictions, unless the parties expressly agree in writing that such manual review will not be performed." (EXACT)
  - `mod-deploy-termsofuse`: "Customer shall submit Personal Data to Deploy solely with Deploy’s prior express written consent" (EXACT)
  - `mod-deploy-termsofuse`: "otherwise use and exploit your Demo Content and the output generated therefrom" (EXACT)
  - `mod-deploy-termsofuse`: "(including to develop and improve Deploy Services)" (EXACT)

**4. Where it processes data; sub-processor list**

- The privacy policy says the services are operated from the United States and information may be processed and stored in the US or other countries. Hive Workers are described as globally distributed and may act as sub-processors. A sub-processor list: **not published** on the pages read.
  - `mod-hive-privacy`: "The Services are operated from the United States. Information may be processed and stored in the United States or other countries." (EXACT)
  - `mod-deploy-termsofuse`: "such persons may serve as sub-processors of Customer data in accordance with Customer instructions" (EXACT)
  - `mod-deploy-termsofuse`: "Hive Workers are independent globally distributed workers performing such services worldwide" (EXACT)

**5. Illinois BIPA / biometric data**

- Not published: no mention of BIPA or "biometric" on the privacy policy or terms of use (0 matches). The terms mention components that predict whether the same subject appears across images.
  - `mod-deploy-termsofuse`: "Certain components of the AI Service use machine learning to detect similarities between different images and generate predictions of the likelihood the same subject appears across images." (EXACT)
  - Pages checked (read 2026-11-17): `mod-hive-privacy`; `mod-deploy-termsofuse`

**6. Manual review path / disputed results**

- Hive Moderation Dashboard provides human-review rules, review feeds and an appeals process; false positives can be reported through the API.
  - `mod-hive-humanreview`: "In this part, we'll configure our human review rules and walk through the manual review workflow." (EXACT)
  - `mod-hive-appeals`: "Moderation Dashboard supports the entire appeal process for both users and moderators." (EXACT)
  - `mod-hive-faq`: "You can send us feedback directly through the API." (EXACT)

**7. Birth date, liveness, age estimation**

- Not applicable to Visual Moderation. A separate Demographic Attributes model predicts gender, age group and "liveness" from faces; age regression is in beta (priced "Contact Sales").
  - `mod-hive-demographic`: "Face detections are passed through an additional classification step to predict attributes like gender, age, or "liveness"." (EXACT)
  - `mod-hive-demographic`: "This class returns a number representing the predicted exact age of the subject." (EXACT)

**8. Integration**

- REST (sync and async task endpoints); image by URL or uploaded file. A server SDK or a React Native/Expo client SDK: not published on the pages read.
  - `mod-hive-docs-vcm`: "# Submit a task with an image URL (sync)" (EXACT)
  - `mod-hive-docs-vcm`: "# Submit a task with a local file (sync)" (EXACT)

**9. DPA and role**

- DPA: **not published** on the pages read (no DPA link in deploy.com footer pages; 0 matches for DPA/data processing in the terms and privacy policy).
  - Pages checked (read 2026-11-17): `mod-deploy-termsofuse`; `mod-hive-privacy`; `mod-deploy-entcommit`

**10. CSAM detection or hash matching offered by the service**

- Yes: a Combined CSAM Detection API with Thorn (hash matching for known CSAM plus a classifier for novel CSAM), Enterprise customers only, priced "Contact Sales". The classifier deletes original media after creating embeddings. NCMEC reporting from the Dashboard requires the customer's own NCMEC credentials.
  - `mod-hive-csam-combined`: "This model is available to Enterprise customers only." (EXACT)
  - `mod-hive-csam-combined`: "Hive's Combined CSAM Detection API runs two CSAM (Child Sexual Abuse Material) detection models, created in partnership with Thorn" (EXACT)
  - `mod-hive-pricing`: "CSAM Detection Combat child exploitation content with Thorn's specialized CSAM detection model. CSAM Detection Contact Sales" (EXACT)
  - `mod-hive-csam-combined`: "After we create the embeddings, we permanently delete all of the original media." (EXACT)
  - `mod-hive-ncmec`: "In order to submit reports on your behalf, your NCMEC credentials are required." (EXACT)
  - `mod-deploy-entcommit`: "For special safety workflows, hash conversions may be securely shared with vetted third parties." (EXACT)

#### A5. Sightengine — Image Moderation

- Classes include nudity/sexual levels and violence.
  - `mod-se-docs-nudity21`: "Sexual activity : Actual or simulated sexual activity with exposed nudity" (EXACT)
  - `mod-se-docs-violence`: "The Violence model returns an overall probability in violence.prob ." (EXACT)

**1. Published price**

- Plans: Free 2,000 operations a month (max 500/day, no time limit); Starter $29/month for 10,000 operations plus $0.002 per extra operation; Pro $99/month for 40,000 plus $0.002; Enterprise custom. Nudity detection on one image is one operation. Monthly plans run in 30-day periods.
  - `mod-se-pricing`: "2,000 operations / month (max 500/day)" (EXACT)
  - `mod-se-pricing`: "Can I stay on the Free plan forever? Yes, you can. There is no time limit." (EXACT)
  - `mod-se-pricing`: "$29 /mo 10,000 operations / month + $0.002 per additional op" (EXACT)
  - `mod-se-pricing`: "$99 /mo 40,000 operations / month + $0.002 per additional op" (EXACT)
  - `mod-se-pricing`: "As an example, running Nudity Detection on an image counts as 1 operation." (EXACT)
  - `mod-se-pricing`: "Downgrades and terminations become effective at the end of your current subscription period (30-day period for monthly plans)." (EXACT)

**2. What it keeps, and for how long**

- Images are deleted after processing by default, unless a storing feature is used (e.g. human review in a hybrid workflow, the Feedback API, near-duplicate lists). DPA: deletion instructions completed within a maximum of 90 days.
  - `mod-se-faq-retention`: "By default, images, videos and audios are deleted after processing ." (EXACT)
  - `mod-se-faq-retention`: "you send it for human review (hybrid moderation workflow)" (EXACT)
  - `mod-se-dpa`: "Sightengine will comply with this instruction as soon as reasonably practicable within a maximum of 90 days" (EXACT)

**3. Own use of images/results (training, improvement) and opt-out**

- The terms describe training use only for media the customer voluntarily submits through the Feedback API ("Training Data"); the DPA lets Sightengine keep Feedback Data in perpetuity. Use of ordinary moderation requests for training: not stated on the pages read. Opt-out: by not using the Feedback API (as published).
  - `mod-se-terms`: "if Subscriber voluntarily submits raw media (including but not limited to images, videos, text, or audio) with or without associated labels through Sightengine's Feedback API or similar reporting mechanisms" (EXACT)
  - `mod-se-terms`: "Subscriber grants Sightengine a non-exclusive license to use, reproduce, and process such Training Data specifically to train, test, develop, and improve Sightengine's machine learning models and Services." (EXACT)
  - `mod-se-dpa`: "Feedback Data submitted voluntarily by the Subscriber may be retained in perpetuity." (EXACT)

**4. Where it processes data; sub-processor list**

- By default processing may happen in the EU (France, Ireland, Germany, Finland), Canada or the US; region choice is for Enterprise plans. Sub-processor list published (https://sightengine.com/policies/subprocessors).
  - `mod-se-faq-location`: "The processing may currently happen in any of the following regions: EU (France, Ireland, Germany, Finland) Canada US" (EXACT)
  - `mod-se-faq-location`: "If you need to control exactly where your data is analyzed, you can sign up to one of our Enterprise plans ." (EXACT)
  - `mod-se-pricing`: "Regional Endpoints Process media only in the region of your choice" (EXACT)
  - `mod-se-subprocessors`: "Amazon Web Services, Inc. Cloud Service Provider United States Google LLC Cloud Service Provider United States OVH SAS Server Provider France Hetzner Online GmbH Server Provider Germany OVH US LLC Server Provider United States Scaleway SAS Server Provider France" (EXACT)

**5. Illinois BIPA / biometric data**

- BIPA: not published. The DPA says customers may choose to include special-category data such as biometric data.
  - `mod-se-dpa`: "may include, for example, (i) biometric data" (EXACT)
  - Pages checked (read 2026-11-17): `mod-se-privacy`; `mod-se-terms`

**6. Manual review path / disputed results**

- Hybrid Moderation workflows send items to the customer's own human moderation platform based on review thresholds.
  - `mod-se-faq-hybrid`: "some decisions could be reviewed / confirmed through your human moderation platform" (EXACT)

**7. Birth date, liveness, age estimation**

- Not applicable to moderation. Separate models: Face Age (age group and probability of under 18) and Liveness Detection; Age Estimation and Liveness are listed under the Pro plan.
  - `mod-se-docs-minor`: "The Face Age model estimates the age group of people appearing in photographs, based on face analysis." (EXACT)
  - `mod-se-docs-minor`: "This represents the probability that a detected face belongs to a person who is a minor (under 18 years of age)." (EXACT)
  - `mod-se-pricing`: "Liveness Detection Recapture Detection Age Estimation" (EXACT)

**8. Integration**

- REST; direct upload or public image URL. Docs show curl, Python, PHP and Node.js examples; an SDK package name was not found on the pages read. The plan table's Upload API row (signed upload links for direct uploads from apps or clients) reads "— — Custom" with one cell empty in the text, so which plans include it is unclear. React Native/Expo SDK: not published.
  - `mod-se-faq-send`: "When using the Image Moderation API, you can either directly upload the image or submit the image URL." (EXACT)
  - `mod-se-docs-getstarted`: "Moderate by submitting an Image URL curl python php nodejs" (EXACT)
  - `mod-se-pricing`: "Signed upload links for very large videos and direct uploads from your apps or clients" (EXACT)

**9. DPA and role**

- DPA published (https://sightengine.com/policies/dpa); where EU data-protection law applies, the customer is controller and Sightengine processor. A CCPA or "service provider" clause: not found in the DPA (0 matches).
  - `mod-se-dpa`: "Subscriber is the controller and Sightengine and the Sightengine Group are the processor of the Subscriber Personal Data" (EXACT)
  - `mod-se-dpa`: "if the EU Data Protection Laws apply to the processing of Subscriber Personal Data" (EXACT)

**10. CSAM detection or hash matching offered by the service**

- No CSAM detection or hash matching is published. The terms prohibit use involving child sexual exploitation; a minor-detection model exists (it is not a CSAM tool).
  - `mod-se-terms`: "shall not use Sightengine services in any way that involves child sexual exploitation or abuse" (EXACT)
  - Pages checked (read 2026-11-17): `mod-se-docs-models`

#### Part A cross-service table

| Field | Amazon Rekognition | Google Vision SafeSearch | Azure AI Content Safety | Hive (Deploy) | Sightengine |
|---|---|---|---|---|---|
| 1. Price (image) | $0.0010/image first 1M/mo (US East), tiers down to $0.00025; free 1,000/mo for 12 months | $1.50 per 1,000 (1,001–5M/mo), $0.60 above; first 1,000/mo free | $0.75 per 1,000 images; free 5,000/mo (region of price not shown) | $3.00 per 1,000 at 100/day (testing); annual contract stated for Visual Moderation | Free 2,000 ops/mo; $29/mo for 10k; $99/mo for 40k; $0.002 extra op |
| 2. Keeps images | May store; period not published; deletion via Support | Online: not persisted; async: TTL of a few hours | Not stored (except blocklists) | 14 days by default; adjustable on request | Deleted after processing by default |
| 3. Own use / opt-out | Yes by default; AWS Organizations opt-out | No training use stated | No training use stated | Yes by default (incl. Hive Worker manual review) unless agreed otherwise in writing | Only Feedback API submissions |
| 4. Regions / sub-processors | Customer-chosen AWS Region; list published | SafeSearch location not published (EU/US endpoints documented for OCR only); list published | Customer-chosen region (some features global); MS list PDF dated Feb 2025 | US-operated, may process elsewhere; list not published | EU/Canada/US by default; region choice Enterprise; list published |
| 5. BIPA / biometric | Biometric Notice and Consent Terms name BIPA | Not published; no facial recognition | DPA biometric clause; BIPA not named | Not published | Not published (DPA mentions biometric data generally) |
| 6. Human review | Amazon A2I | Not published | Not offered (customer's own) | Moderation Dashboard review + appeals | Hybrid workflow to customer's own moderators |
| 7. Age / liveness | Not applicable; AgeRange and Face Liveness exist separately | Not applicable; none found | Not applicable; none found | Not applicable; Demographic model (age, liveness beta) | Not applicable; Face Age/minor and Liveness models |
| 8. Integration | REST/SDKs; bytes or S3; Amplify React Native `UNSAFE` | REST/libraries; bytes, GCS or web URL | REST/SDKs; base64 or blob URL | REST; URL or file upload | REST; upload or URL |
| 9. DPA / role | DPA; processor; CCPA Terms | Cloud DPA; processor (= service provider) | MS DPA; processor; CCPA section | Not published | DPA; processor (EU law) |
| 10. CSAM | No (FAQ) | Not in Vision; Google toolkit separately | No (overview); PhotoDNA separately | Yes, with Thorn, Enterprise only | Not published |

### Part B — hash matching for child sexual abuse material

Note from the brief, not analysed here: 18 U.S.C. 2258C limits use of NCMEC-provided hash values to stopping child sexual exploitation. Below, each programme's own page is recorded as published.

#### (a) CSAM hash matching or classifiers offered by the Part A services

| Service | CSAM hash matching | CSAM classifier | Terms as published | Source quote IDs |
|---|---|---|---|---|
| Amazon Rekognition | No | No ("does not detect" CSAM) | — | A1-10a, A1-10b |
| Google Cloud Vision | Not in Vision | Not in Vision | Google's separate Child Safety Toolkit (Part B b2) | B2-a |
| Azure AI Content Safety | No | No ("can't use" for child exploitation images) | Microsoft's separate PhotoDNA Cloud Service (Part B b1) | A3-10a |
| Hive (Deploy) | Yes (with Thorn) | Yes (with Thorn) | Enterprise customers only; "Contact Sales"; customer's own NCMEC credentials for reporting | A4-10a to A4-10f |
| Sightengine | Not published | Not published | Terms prohibit CSE use | A5-10a |

Identity-verification companies were not checked (optional in the brief).

#### (b) Programmes that give hash matching to services hosting user photos

##### b1. Microsoft PhotoDNA Cloud Service

- Who may apply: qualified organisations, approved by a third-party vetting service; intended for trusted online service providers and businesses hosting user-generated content; an online application is approved case by case.
  - `mod-pdna-home`: "PhotoDNA Cloud Service is free for qualified customers." (EXACT)
  - `mod-pdna-cloud`: "Must be a qualified organization subject to approval by third-party vetting service." (EXACT)
  - `mod-pdna-faq`: "Intended users are trusted online service providers and businesses hosting user-generated content." (EXACT)
  - `mod-pdna-faq`: "Service applicants will submit an online form and subscriptions are approved on a case-by-case basis." (EXACT)
  - `mod-pdna-faq`: "This evaluation process is performed by a third party and involves careful consideration of organization-specific attributes and other relevant qualifications." (EXACT)
- Eligibility in the terms: access at Microsoft's sole discretion under its eligibility criteria and vetting.
  - `mod-pdna-terms`: "Access to the PhotoDNA Cloud Service is subject to Microsoft’s sole discretion based on our eligibility criteria and vetting process." (EXACT)
- Cost: free for qualified customers; the terms (last updated May 2018) say free with limited transactions per month, or charged as Content Moderator transactions for high volume. No support or SLA.
  - `mod-pdna-terms`: "The PhotoDNA Cloud Service is provided free of charge (with limited transactions per month) or charged as Content Moderator transactions (if used with Content Moderator as required for high volume usage)." (EXACT)
  - `mod-pdna-terms`: "Last updated: May 2018" (EXACT)
  - `mod-pdna-terms`: "The PhotoDNA Cloud Service is not covered by customer support and does not have an SLA." (EXACT)
- NCMEC: the pages read do **not** state NCMEC registration as an application requirement. Microsoft recommends its API for NCMEC reports, or customers may report directly; customers authorise Microsoft to send NCMEC aggregate match reports identifying them.
  - `mod-pdna-faq`: "The PhotoDNA Cloud Service provides an API which we recommend all customers use to submit reports to the National Center for Missing and Exploited Children (NCMEC)." (EXACT)
  - `mod-pdna-faq`: "Alternatively, customers may choose to report directly to NCMEC." (EXACT)
  - `mod-pdna-terms`: "You hereby authorize Microsoft to provide aggregate reports to NCMEC that summarize the number of images you uploaded on the PhotoDNA Cloud Service that match the signatures of known child pornography images." (EXACT)
- What the provider agrees to: use solely to prevent the spread of CSAM and support investigations; Microsoft may monitor and audit use; internal use only. Images only (no video). Images are converted to hashes and not retained.
  - `mod-pdna-terms`: "You may use the PhotoDNA Cloud Service solely for the Purpose, and you must not use it for any other purposes." (EXACT)
  - `mod-pdna-terms`: "You will use the PhotoDNA Cloud Service solely for your internal use." (EXACT)
  - `mod-pdna-faq`: "The PhotoDNA Cloud Service cloud is limited to images at this time" (EXACT)
  - `mod-pdna-cloud`: "Your images are instantly converted to secure hashes and are never retained by Microsoft." (EXACT)

##### b2. Google Child Safety Toolkit (Content Safety API and CSAI Match)

- Free of charge to qualifying partners; industry and civil-society third parties protecting their platforms can sign up; applications are subject to approval. Entry is an interest form (not submitted).
  - `mod-goog-toolkit`: "the Content Safety API and CSAI Match , that we offer to qualifying partners free of charge" (EXACT)
  - `mod-goog-toolkit`: "Industry and civil society third parties seeking to protect their platform against abuse can sign up to access the Content Safety API. Applications are subject to approval." (EXACT)
  - `mod-goog-toolkit`: "Share a few details about your organization to register your interest" (EXACT)
- Content Safety API is a classifier that prioritises images/videos for review (not hash matching); partners must make their own review decisions. It accepts raw bytes or embeddings.
  - `mod-goog-toolkit`: "Partners must conduct their own review in order to determine whether they should take action on the content." (EXACT)
  - `mod-goog-toolkit`: "We have options to support both raw content bytes and embeddings derived from media files." (EXACT)
- CSAI Match is hash (fingerprint) matching for **video**; available to partners in industry and NGOs.
  - `mod-goog-toolkit`: "YouTube makes CSAI Match available to partners in industry and NGOs." (EXACT)
  - `mod-goog-toolkit`: "CSAI Match is designed for video" (EXACT)
- Detailed application criteria, NCMEC requirements and use terms: not published on the page read. The linked CSAI Match page (youtube.com/csai-match/) redirected to the How YouTube Works homepage and could not be read.
  - Pages checked (read 2026-11-17): `mod-goog-toolkit`; `mod-yt-csai`

##### b3. Thorn — Safer (Safer Match hash matching, Safer Predict classifiers)

- Eligibility: a commercial product; Thorn will engage with any company interested; companies must report to their national clearinghouse (NCMEC in the US) and Thorn does not report for them; access may be suspended for misuse; scholarships/discounts via referral partners case by case.
  - `mod-safer-criteria`: "Safer is a commercial product and service, built by Thorn" (EXACT)
  - `mod-safer-criteria`: "We will engage in dialogue with any company that comes to us interested in using Safer to better protect their platform." (EXACT)
  - `mod-safer-criteria`: "Companies must adhere to their national reporting mandates and report to the appropriate clearinghouse for CSAM." (EXACT)
  - `mod-safer-criteria`: "Thorn provides post-detection tools to report to NCMEC but does not report on a company’s behalf." (EXACT)
  - `mod-safer-criteria`: "Thorn may suspend or terminate access to Safer if it is not used in accordance with the parties’ contractual terms." (EXACT)
  - `mod-safer-criteria`: "we work with referral partners to help provide scholarship and discounting programs to make Safer accessible to as many platforms as possible" (EXACT)
- Price on safer.io: **not published** (safer.io/pricing/ and safer.io/faq/ returned 404); agreements follow Thorn's pricing schedule. API option stated.
  - `mod-safer-criteria`: "Commercial agreements for Safer are unaffiliated with fundraising efforts and must adhere to the pricing schedule and terms set by Thorn." (EXACT)
  - `mod-safer-solutions`: "Use fewer engineering resources to get started with CSAM detection via API." (EXACT)
  - Pages checked (read 2026-11-17): `mod-safer-pricing`; `mod-safer-faq`
- Published price elsewhere: Thorn's "Safer Enterprise" listing on AWS Marketplace (linked from the safer.io footer as "Safer for AWS"; seller shown as Thorn) lists 12-month contracts, the smallest shown being 1M queries/month for $45,384.00. Read by Chromium; the load hit the 90-second network-idle timeout but the page content was captured.
  - `mod-safer-awsmp-r`: "Sold by: Thorn" (EXACT)
  - `mod-safer-awsmp-r`: "1M Queries Contract price includes 1M Queries/month $45,384.00" (EXACT)

##### b4. Cloudflare CSAM Scanning Tool

- Requirement: content must be served through Cloudflare's cache for the customer's website (so the customer must use Cloudflare for that content); enabling requires an email address. NCMEC credentials are **not** listed as a requirement in the docs read; Cloudflare files NCMEC reports using its own CyberTipline credentials.
  - `mod-cf-csam-docs`: "By enabling this tool, Cloudflare will compare content served for your website through the Cloudflare cache to known lists of CSAM." (EXACT)
  - `mod-cf-csam-docs`: "You must provide an email address, which will be used to notify you in the event Cloudflare detects a positive match." (EXACT)
  - `mod-cf-sst-app`: "You understand and agree that Cloudflare will use its NCMEC CyberTipline credentials to submit these reports on a third-party basis." (EXACT)
- Cost: free, for all customers regardless of plan (blog, December 2019; terms say free of charge).
  - `mod-cf-sst-app`: "The CSAM Scanning Tool is provided free of charge." (EXACT)
  - `mod-cf-csam-blog`: "CSAM Scanning will be available via the Cloudflare dashboard at no cost for all customers regardless of their plan level." (EXACT)
- What the customer agrees to: use solely to prevent the spread of CSAM; Cloudflare may block matched images; internal use only.
  - `mod-cf-csam-docs`: "You agree to use this tool solely for the purposes of preventing the spread of CSAM." (EXACT)
  - `mod-cf-sst-app`: "You hereby authorize Cloudflare to block images that the CSAM Scanning Tool matches to signatures of known CSAM images." (EXACT)
  - `mod-cf-sst-app`: "You will use the CSAM Scanning Tool solely for your internal use." (EXACT)

##### b5. NCMEC hash sharing for electronic service providers

- Voluntary: companies can elect to use NCMEC's hash list; as of 31 December 2025, 78 ESPs received more than 12.1 million hashes.
  - `mod-ncmec-ctldata`: "On a voluntary basis, companies can elect to use NCMEC's hash list to detect CSAM on their systems so that abusive content can be reported and removed." (EXACT)
  - `mod-ncmec-ctldata`: "As of December 31, 2025, NCMEC shared more than 12.1 million hashes with 78 ESPs who have voluntarily chosen to access this hash-sharing initiative." (EXACT)
- Access: through the Hash Sharing API ("Industry CSAM" environment at report.cybertip.org); credentials must be requested from and supplied by NCMEC; read-only or read/write access is granted per environment.
  - `mod-ncmec-hs-npo`: "Authentication is required and a username and password must be requested from and supplied by NCMEC." (EXACT)
  - `mod-ncmec-hs-npo`: "Industry CSAM https://report.cybertip.org/hashsharing" (EXACT)
  - `mod-ncmec-hs-npo`: "Members are also granted either read-only or read/write access separately within each environment." (EXACT)
- CyberTipline registration: NCMEC's ESP registration form says NCMEC uses the information to decide whether a company qualifies (form not submitted). Whether CyberTipline registration is a precondition for hash-list access, the eligibility criteria and any cost: **not published** on the pages read.
  - `mod-ncmec-esp-reg-r`: "The CyberTipline will use this information to determine if you qualify for registration." (EXACT)
- UNCONFIRMED (third-party/archived, from web search only): a 2017 archived NCMEC page described registration by emailing an ESP team and eligibility for US-based companies providing an electronic communication or remote computing service to the public. Not read today from NCMEC's live site.

##### b6. Tech Coalition — Lantern (and Tech Coalition membership)

- Lantern is a cross-platform signal-sharing programme; content signals include hashes of known CSAM. Open to qualifying tech companies and financial institutions; participants must pass vetting and show they can manage signals securely and meet legal obligations. Entry by interest form (not submitted). Hosted on Meta's ThreatExchange. No automated enforcement.
  - `mod-tc-lantern`: "Hashes of known CSAM that can be used to detect and prevent redistribution" (EXACT)
  - `mod-tc-lantern`: "Lantern is open to qualifying tech companies and financial institutions that demonstrate a firm commitment to combating OCSEA and meet the program’s requirements." (EXACT)
  - `mod-tc-lantern`: "Participating companies must complete a vetting process and demonstrate their ability to securely manage signals, conduct appropriate investigations, and comply with applicable legal obligations." (EXACT)
  - `mod-tc-lantern`: "Please fill out our interest form with your information." (EXACT)
  - `mod-tc-lantern`: "Lantern is hosted on the ThreatExchange platform, a secure information-sharing platform developed by Meta." (EXACT)
  - `mod-tc-lantern`: "Lantern does not facilitate automated enforcement actions." (EXACT)
- Whether Lantern requires Tech Coalition membership, and any Lantern fee: **not published** on the Lantern page read.
  - Pages checked (read 2026-11-17): `mod-tc-lantern`
- Membership (separate): annual membership starts at US$10,000; members must be technology companies with a product that could be affected by child sexual exploitation and must prohibit CSEA material in public policies (nine criteria in total). Member services include facilitating PhotoDNA licensing.
  - `mod-tc-membership`: "Annual membership starts at US$10,000." (EXACT)
  - `mod-tc-criteria`: "Members must be technology related companies and have at least one product or service that could reasonably be affected by child sexual exploitation." (EXACT)
  - `mod-tc-criteria`: "Members must prohibit child sexual exploitation and abuse material in their terms of service, community guidelines, or other publicly available policies or statements." (EXACT)
  - `mod-tc-services`: "Facilitating interoperability (e.g., Video Hash Project) and licensing (e.g., PhotoDNA)" (EXACT)

##### b7. Other: Internet Watch Foundation (IWF) Image Hash List

- Available to licensed IWF members; hashes in PhotoDNA, MD5, SHA-1 and SHA-256. Membership open worldwide; fees £5,000+ to £100,000+ a year by sector and size.
  - `mod-iwf-hashlist`: "Licenced Members can download the list in two ways." (EXACT)
  - `mod-iwf-hashlist`: "This covers the following hash types: Microsoft’s PhotoDNA, MD5, SHA-1 and SHA-256." (EXACT)
  - `mod-iwf-howtojoin`: "IWF membership is open to companies and organisations all over the world." (EXACT)
  - `mod-iwf-fees`: "All fees are calculated on your industry sector and company size ranging between £5,000+ and £100,000+ GBP per year." (EXACT)
- Minimum threshold to apply: legally registered and trading for more than 12 months; publicly listed on the country registration database; more than 2 full-time unrelated employees; appropriate data security.
  - `mod-iwf-howtojoin`: "be legally registered organisations trading for more than 12 months" (EXACT)
  - `mod-iwf-howtojoin`: "have more than 2 full-time unrelated employees" (EXACT)

##### b8. Other: Canadian Centre for Child Protection — Shield by Project Arachnid

- For ESPs, to detect known CSAM and harmful-abusive images of children; no cost; access by account request (form not submitted). Eligibility criteria or use terms for Shield: not published on the pages read (the site terms of use are general website terms dated 2018).
  - `mod-c3p-arachnid`: "Shield by Project Arachnid has been developed for use by ESPs to assist with the proactive detection of known CSAM and harmful-abusive images of children." (EXACT)
  - `mod-c3p-arachnid`: "There is no cost to using this tool" (EXACT)
  - `mod-c3p-shield-docs-r`: "The Arachnid Shield API is a free HTTP API" (EXACT)
  - `mod-c3p-shield-register`: "Request an account Please provide the following information." (EXACT)
  - Pages checked (read 2026-11-17): `mod-c3p-terms`

##### b9. Related: NCMEC Take It Down (self-submitted images of people under 18)

- Hashes of nude, partially nude or sexually explicit images of people under 18, submitted by the people pictured, are shared with participating platforms that agree to scan public or unencrypted services. How a platform joins, its terms and any cost: not published on the pages read.
  - `mod-tid-home`: "nude, partially nude, or sexually explicit images or videos of people under the age of 18" (EXACT)
  - `mod-tid-home`: "The hash is added to a secure list maintained by NCMEC that is shared only with participating online platforms who have agreed to use this list to scan their public or unencrypted sites and apps for the hashes of your explicit content." (EXACT)
  - `mod-tid-participants`: "These are the companies who have agreed to use the Take It Down hash list to scan for images and videos on their public or unencrypted platforms." (EXACT)

##### b10. Separate, not CSAM: StopNCII.org (non-consensual intimate images of adults)

- Hashes (PDQ/PhotoDNA for photos, MD5 for video) created by adults who were 18 or older when the image was taken are shared with participating companies; platforms can register as "Approved Participants" or "Programme Partners". Eligibility terms for platforms and any cost: not published on the pages read.
  - `mod-stopncii-industry`: "Companies who will receive cases and hashes from StopNCII.org:" (EXACT)
  - `mod-stopncii-join`: "Approved Participants Register to integrate StopNCII.org into your platform – combat NCII without becoming a partner." (EXACT)
  - `mod-stopncii-faq`: "Algorithms we use are PDQ/PhotoDNA for photos and MD5 for videos." (EXACT)
  - `mod-stopncii-home`: "18 or older at the time the image was taken?" (EXACT)

## Appendix C. Sources tables for the searches and the comparison

All fetched on 17 November 2026. The page date is as the page shows it, found by an automatic search ("none found" where it found none). Rows with an error code are pages tried and not read (section 9).

### C.1 The state-law searches (6.1, 6.2)

| Fetch name | URL fetched | Final URL | HTTP, bytes | SHA-256 | Page date |
|---|---|---|---|---|---|
| `law-al-hb351-enr` | `https://alison.legislature.state.al.us/files/pdf/SearchableInstruments/2026RS/HB351-enr.pdf` | the same | 200, 155,350 | `2ec42f5ac3f6757d5c57879cdb8d73fba6fc6e3c8c6a07f037f4825f17c4e42b` | none found |
| `law-az-44-7157` | `https://www.azleg.gov/ars/44/07157.htm` | the same | 200, 2,468 | `906b4dd3e54ccc887bc1faa3c41d5c3444fb58179e71d6595869405432f5dad0` | none found |
| `law-ca-ccpa-statute` | `https://cppa.ca.gov/regulations/pdf/ccpa_statute.pdf` | the same | 200, 772,399 | `0beb83ccf73d82ede066f7e4154952435484410f748da09ac4329ed9afe6a43f` | none found |
| `law-ca-sb1390-calm` | `https://calmatters.digitaldemocracy.org/bills/ca_202520260sb1390` | the same | 200, 243,576 | `96899a262b9a892d83d69fa677d3c506438a474dcfdf57d52d80bd672cdfa94c` | none found |
| `law-ca-sb1390-hist` | `https://leginfo.legislature.ca.gov/faces/billHistoryClient.xhtml?bill_id=202520260SB1390` | the same | 403, 5,857 | `1135003cbb386aefa98e735b8d0edfec1258cf69666399b19c411769538f43cd` | none found |
| `law-ca-sb1390-hist-r` (rendered) | `https://leginfo.legislature.ca.gov/faces/billHistoryClient.xhtml?bill_id=202520260SB1390` | the same | 0, 45,128 | `c075d7601ffde1feb46b53867f160f64b41fe24392a8fdc86462216b7e4dc81d` | none found |
| `law-ca-sb1390-status` | `https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202520260SB1390` | the same | 403, 5,854 | `eacf50896baf405be37005d69e5785b79ff87a03ad5ade0e458302aaffe5abc4` | — |
| `law-co-crs-page` | `https://content.leg.colorado.gov/agencies/office-legislative-legal-services/colorado-revised-statutes` | the same | 200, 58,346 | `3262debd111d6f27d47945989646326c62cf4f86e472e2ab4769db19a5ea6374` | — |
| `law-co-crs2024-t6` | `https://content.leg.colorado.gov/sites/default/files/images/olls/crs2024-title-06.pdf` | the same | 200, 2,108,494 | `560ff6d64b5afdf2a3bc5ac917a392269d16270a029b252ff8f7957deb38b423` | "Effective January 1, 2028" |
| `law-co-crs2025-dl` | `https://content.leg.colorado.gov/index.php/agencies/office-legislative-legal-services/2025-crs-titles-download` | `https://content.leg.colorado.gov:443/agencies/office-legislative-legal-services/2025-crs-titles-download` | 404, 41,819 | `ee76fb12597ab38161329403029a7d58df8af7db24a13390a706e50cf9315453` | — |
| `law-co-crs2025-t6` | `https://content.leg.colorado.gov/sites/default/files/images/olls/crs2025-title-06.pdf` | the same | 404, 39,413 | `ca975d75fe3239f46c0d9413436f17dda583bf2d907f423d8af7c8666a4a14d0` | — |
| `law-co-crs2026-dl` | `https://content.leg.colorado.gov/agencies/office-legislative-legal-services/2026-crs-titles-download` | the same | 200, 56,894 | `49235b657663b8ee46c4e930cf8c1ac1b0715388c3be7198039c80e83c9050c8` | none found |
| `law-co-crs2026-t6` | `https://olls.info/crs/crs2026-title-06.pdf` | the same | 200, 2,238,793 | `6dc53360d27d583c760c30346c56c27aaae22570ad56dab33bdf9864b03c40b9` | "Effective January 1, 2028" |
| `law-ct-743jj` | `https://www.cga.ct.gov/current/pub/chap_743jj.htm` | the same | 000, 0 | `none` | — |
| `law-ct-743jj-b` | `https://www.cga.ct.gov/current/pub/chap_743jj.htm` | the same | 200, 121,179 | `ff6266b5a7ba0087ec489b463e1cff1cca3dd7be874a488aec01585d5396e633` | none found |
| `law-ct-743jj-r` (rendered) | `https://www.cga.ct.gov/current/pub/chap_743jj.htm` | the same | 502, 174 | `9d25629d26cd3d047df9b9d431d9764e2b718796255de95d9452e37c8fa05742` | — |
| `law-ct-pa25-113` | `https://www.cga.ct.gov/2025/ACT/PA/PDF/2025PA-00113-R00SB-01295-PA.PDF` | the same | 000, 0 | `none` | — |
| `law-ct-pa25-113-b` | `https://www.cga.ct.gov/2025/ACT/PA/PDF/2025PA-00113-R00SB-01295-PA.PDF` | the same | 200, 419,672 | `bd8bf2c8453c5cd1b74cb5c1e14fcd1851ecd71a9defcdd771b87dfe091a474a` | "Effective July 1, 2025" |
| `law-ct-pa26-64` | `https://www.cga.ct.gov/2026/ACT/PA/PDF/2026PA-00064-R00SB-00004-PA.PDF` | the same | 000, 0 | `none` | — |
| `law-ct-pa26-64-b` | `https://www.cga.ct.gov/2026/ACT/PA/PDF/2026PA-00064-R00SB-00004-PA.PDF` | the same | 200, 270,091 | `dadca977dba5e7b6c29ef47d258a97c05ade1af6567d41b3656773eb5be6edc6` | "Effective October 1, 2026" |
| `law-il-815-518` | `https://www.ilga.gov/Legislation/ILCS/Articles?ActID=2391&ChapterID=67` | the same | 200, 69,211 | `3c1127bf2802c148a5f0c19522a1d20dad77b11f7673d5dbc3e41b72170af05f` | none found |
| `law-il-815-518b` | `https://ilga.gov/Legislation/ILCS/Articles?ActID=3427&ChapterID=67` | the same | 200, 83,226 | `ad3d5d2d3b229a3411571046af0904dccd9fa2659738cb905423e370078dc9c7` | none found |
| `law-la-sb386-1480202` | `https://www.legis.la.gov/legis/ViewDocument.aspx?d=1480202` | the same | 200, 161,075 | `c0d18d805dace759a5f4b953c99d40269597af35432550c140ee05ad44660b90` | none found |
| `law-mn-2024c121` | `https://www.revisor.mn.gov/laws/2024/0/121/` | the same | 200, 981,435 | `d094816c76d322b4957f09e732497eb3533bfcf35b66b75d8523b4a6b353da06` | none found |
| `law-mn-325m` | `https://www.revisor.mn.gov/statutes/cite/325M` | the same | 200, 65,838 | `3a7c2a2f5167b8223abda5f7670a68b8c32b2a9041e714ef82d9d3521e4b85b9` | none found |
| `law-mn-325m-full` | `https://www.revisor.mn.gov/statutes/cite/325M/full` | the same | 200, 198,167 | `d97066c5c00a815178e1752a8fddaa64bf65c8a2f3182049987903d807609015` | "Effective July 1, 2026" |
| `law-ne-87-1101` | `https://nebraskalegislature.gov/laws/statutes.php?statute=87-1101` | the same | 200, 21,738 | `c2aab814a332ce6eefc199badbc279cce31e946a76b802a5ca66a041eb5882d6` | none found |
| `law-ne-87-1102` | `https://nebraskalegislature.gov/laws/statutes.php?statute=87-1102` | the same | 200, 35,840 | `ba82d640be788fec30522f759b6a2f11f1fdca3febe2aeaf972be5fd5ed3a7f5` | none found |
| `law-ne-87-1103` | `https://nebraskalegislature.gov/laws/statutes.php?statute=87-1103` | the same | 200, 23,546 | `5ba41275f51c08f5609296ca9ec0944bc6fcadc92f766aeadec5e59019506b8c` | none found |
| `law-ne-87-1118` | `https://nebraskalegislature.gov/laws/statutes.php?statute=87-1118` | the same | 200, 21,978 | `57d337aced92ec05b61d91a4aae37f96fcf012861b3b09719c35ea10685382cf` | none found |
| `law-ne-87-1124` | `https://nebraskalegislature.gov/laws/statutes.php?statute=87-1124` | the same | 200, 22,706 | `0d6cdbdad0b8c4932bb4599345eb4fd6981206f9fcb943d07c9f337981b7b7f8` | none found |
| `law-ne-87-1130` | `https://nebraskalegislature.gov/laws/statutes.php?statute=87-1130` | the same | 200, 21,770 | `ea5d3c9281ac21e07b898632e7350cf76784585794dd42ea496ee41fd3c62330` | none found |
| `law-ne-lb1074-slip` | `https://nebraskalegislature.gov/FloorDocs/108/PDF/Slip/LB1074.pdf` | the same | 200, 346,178 | `d9c7b8489ea6503086712617e374bbf94888e95fe42e3f68ac36f9a140a23eb6` | "Effective July 1, 2014" |
| `law-nj-s1040` | `https://pub.njleg.gov/Bills/2026/S1500/1040_I1.HTM` | the same | 200, 14,643 | `5b3904a979ecf4c566eaec6b16dc1968ec9b109e19ce034f529da2909fbb1a53` | none found |
| `law-nv-603a` | `https://www.leg.state.nv.us/NRS/NRS-603A.html` | the same | 200, 130,020 | `b158c2235ea98fa63af2f92924a9298e68de0fc70dbfcdbe45430d4d75b48b06` | "Rev. 4/15/2026" |
| `law-ny-a3323` | `https://www.nysenate.gov/legislation/bills/2025/A3323` | the same | 403, 5,736 | `fa504ea41715e0ac347288d152037c1f55b924291798a08ddac1fcef6eabddcb` | none found |
| `law-ny-a3323-asm` | `https://nyassembly.gov/leg/?default_fld=&leg_video=&bn=A03323&term=2025&Summary=Y&Actions=Y&Text=Y` | the same | 200, 20,859 | `61f31a12bee9678c75ede90ab8a6ed4e51774c3e4ef4ec7bb9a3a1b881707dbf` | none found |
| `law-ny-a3323-r` (rendered) | `https://www.nysenate.gov/legislation/bills/2025/A3323` | the same | 0, 44,976 | `96307b6b420e6b33f3338bfd8f573d148aa9789fe08a4282fa3db2792b3e6255` | none found |
| `law-ny-a428-asm` | `https://nyassembly.gov/leg/?default_fld=&leg_video=&bn=A00428&term=2025&Summary=Y&Actions=Y&Text=Y` | the same | 200, 37,211 | `13d0cba424fd16f983fda0ccf65cc020c07bb6fd279eb93fc44d1fc9bb539672` | none found |
| `law-ny-a8713-asm` | `https://nyassembly.gov/leg/?default_fld=&leg_video=&bn=A08713&term=2025&Summary=Y&Actions=Y&Text=Y` | the same | 200, 22,235 | `b914594dd74d3184c27019ac6686e00a87d85e7a7fe971c0f6c39eb29ae7e92d` | none found |
| `law-ok-sb546-enr` | `http://webserver1.lsb.state.ok.us/cf_pdf/2025-26%20ENR/SB/SB546%20ENR.PDF` | the same | 200, 148,815 | `5bd0846753bb87ffbca103b59c9b4cd7edc7c7051740ab884387c7f009fc8646` | none found |
| `law-tx-106` | `https://tcss.legis.texas.gov/resources/BC/htm/BC.106.htm` | the same | 200, 14,517 | `f90430c16e154a06bc774a1992a368e1514f06b852bead4e0a9a18bc5b040f1b` | none found |
| `law-tx-503` | `https://statutes.capitol.texas.gov/Docs/BC/htm/BC.503.htm` | the same | 200, 250,874 | `dbfba8a96dc3cd584157ca66aaafdf67e0ed15dd5a0c8a58f3d4bd0f109fc646` | none found |
| `law-tx-503b` | `https://tcss.legis.texas.gov/resources/BC/htm/BC.503.htm` | the same | 200, 8,847 | `8b539dd29940ee9f53068717e4da88573070be4121f438a20e64cca70df81d3c` | none found |
| `law-tx-541` | `https://tcss.legis.texas.gov/resources/BC/htm/BC.541.htm` | the same | 200, 80,485 | `1f56ef0a23bae698ba6234921a4dded70a2444059214093791dcc8d7797591be` | none found |
| `law-ut-13-67` | `https://le.utah.gov/xcode/Title13/Chapter67/13-67.html` | the same | 200, 26,614 | `0acad4d6c878c96e7825c2d1ab41f506ad4227ae4784c918012234979cff5af3` | none found |
| `law-ut-13-67-r` (rendered) | `https://le.utah.gov/xcode/Title13/Chapter67/13-67.html` | the same | 200, 29,997 | `aed6b71fa9486dbd6c4b3b6f7af60063be9fc833e8f488bd6f75647684bb0f09` | none found |
| `law-va-59.1-575` | `https://law.lis.virginia.gov/vacode/title59.1/chapter53/section59.1-575/` | the same | 200, 41,030 | `2e0aa8fa38d69d8f7bb05ca26d93ef786a39e9860f041f3e0b99e7eb0ffeea6b` | none found |
| `law-va-59.1-576` | `https://law.lis.virginia.gov/vacode/title59.1/chapter53/section59.1-576/` | the same | 200, 33,953 | `66355f6af30047239cfdc9ddcdf83b938af862290cf6ebc95bc20d0e1ed2d027` | none found |
| `law-vt-2482b` | `https://legislature.vermont.gov/statutes/section/09/063/02482b` | the same | 200, 62,230 | `f4afa08db8a6e9c1250facc9249e6d34594c74a81d57bf1976d7a15c18504ddb` | none found |
| `law-vt-act145` | `https://legislature.vermont.gov/Documents/2026/Docs/ACTS/ACT145/ACT145%20As%20Enacted.pdf` | the same | 200, 250,042 | `06e6c157cf970984bc4c00ebe440f9817961aa060ef0d3907017f7504558624f` | none found |
| `law-wa-19.86.090` | `https://app.leg.wa.gov/RCW/default.aspx?cite=19.86.090` | the same | 200, 113,435 | `6a79082a697eb0967d937a8a37a7197fa5dce33afab03edbb6ddcd255e818a4a` | none found |
| `law-wa-19255` | `https://app.leg.wa.gov/RCW/default.aspx?cite=19.255.005` | the same | 200, 111,348 | `839dc7b5fdd372e52aa7e893612fa8608f5b4fbeca46a918237cff89446e583d` | none found |
| `law-wa-19373` | `https://app.leg.wa.gov/RCW/default.aspx?cite=19.373&full=true` | the same | 200, 168,144 | `5f2cb52d3babdf2ac7b92cec1314f3157507e8b5eef7d9c12961a1daec3fc95a` | none found |
| `law-wa-19375` | `https://app.leg.wa.gov/RCW/default.aspx?cite=19.375&full=true` | the same | 200, 122,870 | `3e3536dc18cbb5eba41f423bf2463b9d75e3512e98ccf786e080c4e2c630c813` | none found |

### C.2 Identity verification companies (with Stripe's restricted-business list)

| Fetch name | URL fetched | Final URL | HTTP, bytes | SHA-256 | Page date |
|---|---|---|---|---|---|
| `idv-didit-pricing` | `https://didit.me/pricing` | `https://didit.me/pricing/` | 200, 1,685,470 | `b51182543231baf78645bfd8f3b069b7cf3f18db76feeb2af2ba276107ccd0c2` | none found |
| `idv-ent-consent` | `https://assets.onfido.com/consent/user_consent.html` | the same | 200, 4,716 | `61b3fb8e72e39def4c9f51d7229a03956137c06573e4d3f8db72bb79e28b511a` | none found |
| `idv-ent-docconsent` | `https://documentation.identity.entrust.com/guide/onfido-privacy-notices-and-consent/` | the same | 200, 94,444 | `940b5a858721f7b8b66f19234aa53314caee13caa367e64cf354c4c56a871084` | none found |
| `idv-ent-facial` | `https://www.entrust.com/legal-compliance/data-privacy/facial-scan-policy-and-release` | the same | 403, 21,738 | `ba0b17311bb2c02cd77867c2110075e703d7e3b7e8408eec8ff3cc15a0b4bf61` | none found |
| `idv-ent-facial-r` (rendered) | `https://www.entrust.com/legal-compliance/data-privacy/facial-scan-policy-and-release` | the same | 403, 22,488 | `6e018de8eb2ccfb90229a75b00b43732902206c7dcb3fbbe1757b5ada6cb8652` | none found |
| `idv-ent-ppn` | `https://www.entrust.com/sites/default/files/documentation/licensingandagreements/product-privacy-notice-onfido-identity-services.pdf` | the same | 403, 20,624 | `e5ae61f4c72d03fb5ddb0e54b82b7198f9bd7806ce74c1f7b1d8e7fed79827cd` | none found |
| `idv-ent-specific` | `https://www.entrust.com/legal-compliance/terms-conditions/idv/onfido-specific-terms` | the same | 403, 21,738 | `541142d6f5e428950c230f8602921546ebace28344fbe5c04b96dfa51803de88` | none found |
| `idv-fp-docs` | `https://docs.onefootprint.com/` | `https://docs.onefootprint.com/articles/getting-started/introduction` | 200, 141,241 | `c9f423632368a3bb7856aa9822d6bc86afc511e3a888160b59c9a18e9c81a631` | none found |
| `idv-fp-home` | `https://www.onefootprint.com/` | `https://onefootprint.com/` | 200, 338,587 | `37ea4e6c4c0c09ebc751143d28ad2a0e785e765885e791b3a7f938c51be6d9c5` | none found |
| `idv-fp-pricing` | `https://www.onefootprint.com/pricing` | `https://onefootprint.com/pricing` | 404, 181,129 | `a4fb4275ff4f02e25cc002067699846c01208d4d1956956255fc1351fc80793d` | none found |
| `idv-incode-pricing` | `https://incode.com/pricing/` | `https://www.incode.com/pricing/` | 404, 131,525 | `43b3c6d3a2c77b973e4cdabb4b4a6fb6043e2b42de9777afa310672ef47969e5` | none found |
| `idv-jumio-auth` | `https://documentation.jumio.ai/docs/developer-resources/API/authorization` | the same | 200, 63,381 | `54306abac15ee1c947f592445bf47972cf39caacc02453633dbf4489845ea9f4` | none found |
| `idv-jumio-bizlogic` | `https://documentation.jumio.ai/docs/developer-resources/businessLogicGuide` | the same | 200, 33,428 | `da939b57b4a805dc0f9c54626fea43f8493c9ac4043d58b1888bee5cc00711b3` | none found |
| `idv-jumio-consent` | `https://documentation.jumio.ai/docs/developer-resources/API/end-user-consent` | the same | 200, 54,048 | `8896371b7cc75cd60f8367e169ba19f22fc81c1c4a78f43cb7627ad1154fa7a9` | none found |
| `idv-jumio-delcred` | `https://documentation.jumio.ai/docs/developer-resources/API/CreateUpdateAccounts/deleting-credentials` | the same | 200, 32,018 | `f3cb99aa8aca276e6b6dedae96a2a953667432d7ab009254ced650e8db136010` | none found |
| `idv-jumio-docs` | `https://docs.jumio.com/` | `https://documentation.jumio.ai/` | 200, 46,999 | `04276a177718516c2dfaa0429230a4f7fe57a9d22c9d445e3d43a2289a6f5eba` | none found |
| `idv-jumio-extract` | `https://documentation.jumio.ai/docs/references/capabilities/extraction` | the same | 200, 43,044 | `2d1d0263e667f8cdc2c3d2bb3524a51eddc1a6663bdab6c7051bae795560b8fa` | none found |
| `idv-jumio-idv` | `https://www.jumio.com/products/id-verification/` | the same | 200, 165,297 | `a1e778cde570379875b15e938ac8b1b06ffd2f45e546186e3c28d3fb7581fb16` | none found |
| `idv-jumio-legal` | `https://www.jumio.com/legal-information/` | `https://www.jumio.com/privacy-center/privacy-notices/` | 200, 85,222 | `eb083c8475774d058407eacbff4998686fc9a263fa39433a3470429ecbf0255f` | none found |
| `idv-jumio-liveness` | `https://documentation.jumio.ai/docs/references/capabilities/liveness` | the same | 200, 42,286 | `ad95619931652b9b3035da943cd47ae10536867c9ef787b929a2f629d94fa1d3` | none found |
| `idv-jumio-livprod` | `https://www.jumio.com/products/liveness-detection/` | the same | 200, 141,817 | `fb04165cfebbda5a6f9518b4f226629bb1db2f955ed260234eea6c83021b573e` | none found |
| `idv-jumio-llms` | `https://documentation.jumio.ai/llms.txt` | the same | 200, 37,591 | `9210f8a8509088ef94b0a6ee5bedd2fd5d8f06c54b8ed617b404b807bd3e7fc3` | none found |
| `idv-jumio-osnotice` | `https://www.jumio.com/privacy-center/privacy-notices/online-services-notice/` | the same | 200, 105,276 | `745faa734235921630df20cd9c5b15b74b09bef751085df2c78e5c1b783123bc` | "Last Updated: October 29, 2026" |
| `idv-jumio-pricing` | `https://www.jumio.com/pricing/` | the same | 404, 116,170 | `6c1477fabf1653ae5cc35578af58a969a8ea089dc3b7dc78ca2faeee2d341029` | none found |
| `idv-jumio-privctr` | `https://www.jumio.com/privacy-center/` | the same | 200, 86,929 | `a89558d10689b75e1f170417e5e4100b17282b5a4a01a68cb438a64155b54201` | none found |
| `idv-jumio-rn` | `https://documentation.jumio.ai/docs/developer-resources/SDKs/crossplatform/mobile-react-master/README_React` | the same | 200, 86,968 | `c15e42c8451dfddea39b69a75a714944e57ff84fc3513604cf6e53162d3c6c4b` | none found |
| `idv-jumio-sdks` | `https://documentation.jumio.ai/docs/developer-resources/SDKs/Overview_of_SDKs` | the same | 200, 25,740 | `79d63945d279ae9096033fa8f1a94584e44c0a172b6cab74a7ef08f10eb777c8` | none found |
| `idv-jumio-selfiedone` | `https://documentation.jumio.ai/docs/quickStart/selfieDone` | the same | 200, 50,157 | `c037ca5ecc6044b3ae5f0f9f3c1304ee34a76a2f9ada2a73d3a889cdcde5b059` | none found |
| `idv-jumio-sitemap` | `https://documentation.jumio.ai/sitemap.xml` | the same | 200, 33,035 | `78568c6932c06ec56fd4d08fc4c60fb12a262342eef187241bae1be01d38416c` | none found |
| `idv-jumio-tc73` | `https://www.jumio.com/app/uploads/2025/07/jumio-terms-and-conditions-v7.3.v07012025.pdf` | the same | 200, 231,498 | `51f6f7c797978d96ffcf6d460d2a06eab98d4569e95482f007667dd832729135` | none found |
| `idv-jumio-tcidx` | `https://www.jumio.com/legal-information/terms-and-conditions/` | `https://www.jumio.com/terms-and-conditions/` | 200, 107,987 | `d53fdba2db08f28e0a6f9c0bbd012196efcfd3e41d7e65facad39d48ed495ed3` | none found |
| `idv-jumio-trust` (rendered) | `https://trust.jumio.com/` | the same | 403, 923 | `fd789e3413d591594fd6417b83db61d656d06a508a27948298502793fbdbaeaa` | none found |
| `idv-onfido-pricing` | `https://onfido.com/pricing/` | `https://www.entrust.com/pricing/` | 403, 21,738 | `ab69f96eb193e45daa5616f290e83230f1329a9c18091ad68a6648dcd70acb99` | none found |
| `idv-persona-docs` | `https://docs.withpersona.com/` | `https://docs.withpersona.com/getting-started` | 200, 194,909 | `7a7159d7d88617ee7e3c61626cbee782c201734ce0e140edc6ab245ac31455b4` | none found |
| `idv-persona-pricing` | `https://withpersona.com/pricing` | the same | 403, 5,608 | `862d0b8f8e0591a30020ef350a436ea87a3ea9892f280181368f8e39a21b275c` | none found |
| `idv-persona-pricing-r` (rendered) | `https://withpersona.com/pricing` | the same | 0, 44,798 | `cee0ec531cd4951ac3fff7c1ba011ce2ca04662fb28a5f6b84f7490bc467f53e` | none found |
| `idv-persona-privacy` | `https://withpersona.com/legal/privacy-policy` | the same | 403, 5,668 | `d865a5ef3b2c3e450cdcba813b6a7b253f9fd946cf318791581251f03b82b355` | none found |
| `idv-stripe-checks` | `https://docs.stripe.com/identity/verification-checks` | the same | 200, 463,186 | `976ce3608d81052482e494f84c1cae61e46c57aadfb781e57bca9b763d45ec88` | none found |
| `idv-stripe-checks-md` | `https://docs.stripe.com/identity/verification-checks.md` | the same | 200, 753 | `9e3d3c5a72f68ced06e43c97d87cb72003f25650968a37ac6a71c27e692d6eca` | none found |
| `idv-stripe-docs` | `https://docs.stripe.com/identity` | the same | 200, 285,971 | `ae05602d9a46635860516eae6dde2f87c1e72196b671741f1207a6399b749287` | none found |
| `idv-stripe-dpa` | `https://stripe.com/legal/dpa` | the same | 200, 194,389 | `046c3ec5f41e684659efde3bb03c55d7dba3c4df2926f25a46f9e36aa9498944` | "Last updated: September 28, 2026" |
| `idv-stripe-explain-md` | `https://docs.stripe.com/identity/explaining-identity.md` | the same | 200, 9,818 | `5cd17b9ff60cb42f1e48f9411d972a337d3e814d58ce0b482c1b3c47863bf19d` | none found |
| `idv-stripe-faq` | `https://support.stripe.com/questions/stripe-identity-faq` | the same | 200, 27,054 | `8d56fdec50e423fb1a54135579c698057752348f00a90c447ddb13bd97625438` | none found |
| `idv-stripe-faq-r` (rendered) | `https://support.stripe.com/questions/stripe-identity-faq` | the same | 0, 78,025 | `0b006d4867d3b4f5f760f765315fbb5f8e0000597ed82732fcae977b594d86ce` | none found |
| `idv-stripe-identity` | `https://stripe.com/identity` | the same | 200, 666,436 | `a8e0b5d94f931a749d56b618c00f69c11626579303af5f4e6a073cb41d9b63b5` | none found |
| `idv-stripe-idterms` | `https://stripe.com/legal/identity` | `https://stripe.com/legal/ssa-service-terms` | 200, 961,194 | `8684e428ccd1761eac6ff141443c0e2c4c51f45406fbfa7ab13598ffd4049b44` | "Last modified: September 28, 2026" |
| `idv-stripe-legal` | `https://support.stripe.com/questions/legal-considerations-for-handling-id-verification-data-for-your-business` | the same | 200, 23,573 | `63f60bb282c9a4affaba0e0fd8acee93bce41fc986fe8e29d03ff095fecc2581` | none found |
| `idv-stripe-legal-r` (rendered) | `https://support.stripe.com/questions/legal-considerations-for-handling-id-verification-data-for-your-business` | the same | 200, 71,911 | `377393b245cf4062329f54f97ab63b61fc48a70b8217615c00c802393bd304e1` | none found |
| `idv-stripe-manage` | `https://support.stripe.com/questions/managing-your-id-verification-information` | the same | 200, 31,333 | `a16005053b99a3e81c9af21a1abbe88225faee0d0996ce361f0e966e72322ecf` | none found |
| `idv-stripe-manage-r` (rendered) | `https://support.stripe.com/questions/managing-your-id-verification-information` | the same | 0, 80,681 | `2415f054f3963dd69573bc877b9bbcca167d388a2b962a709d98a31be48ffbb2` | none found |
| `idv-stripe-outcomes-md` | `https://docs.stripe.com/identity/handle-verification-outcomes.md` | the same | 200, 15,123 | `f4cd95a83ca4b403075207bee7fb312890f7d7e6f3900074fdfde36a747f12d7` | none found |
| `idv-stripe-pricing` | `https://stripe.com/pricing` | the same | 200, 984,514 | `4d20f936744270996ad59f4e19b448ee117388862f11d6522f083c437e5b9424` | none found |
| `idv-stripe-privacy` | `https://stripe.com/privacy` | the same | 200, 280,879 | `8b39bc8b29f127275c27dab71571b9b0e83e20ce54c7eed33afdc330dc5adf97` | "Last updated: April 28, 2026" |
| `idv-stripe-privcons` | `https://support.stripe.com/questions/privacy-considerations-for-handling-id-verification-data-as-a-business` | `https://support.stripe.com/questions/legal-considerations-for-handling-id-verification-data-for-your-business` | 200, 23,573 | `73714da5323d5b98eab802abb48288a73acaf70d701d64021c93bef551f8d3fd` | none found |
| `idv-stripe-redact` | `https://docs.stripe.com/api/identity/verification_sessions/redact` | the same | 200, 1,050,093 | `9de8a802d110e5eb42abb044b06a8bef123f7af17bc118e4fe40718f2fb8a709` | none found |
| `idv-stripe-results` | `https://docs.stripe.com/identity/access-verification-results` | the same | 200, 535,202 | `af77e3f874163ecd1e6f687691549ebea37f99be02eae6d0a11cb54f4f4c6980` | none found |
| `idv-stripe-results-md` | `https://docs.stripe.com/identity/access-verification-results.md` | the same | 200, 14,937 | `a249254eb27239e742a2c29c64ed149c7ed0a42034aaf0e0d0890c18ca56a0f8` | none found |
| `idv-stripe-review-md` | `https://docs.stripe.com/identity/review-tools.md` | the same | 200, 8,314 | `326a221f18e8d8ece1e776bc66e7040ebda94b7710678b1096c021c8ad466092` | none found |
| `idv-stripe-rn` | `https://docs.stripe.com/identity/verify-identity-documents?platform=react-native` | the same | 200, 1,071,805 | `a699dd658cdc7a6584ed9f11757f194d59a4aecbcc453487254056e15ca96873` | none found |
| `idv-stripe-rn-md` | `https://docs.stripe.com/identity/verify-identity-documents.md?platform=react-native` | the same | 200, 1,454 | `c7ca9ce7f7b4a98d6ccc761102894e19fd9998c518c85be89b30474fdb465992` | none found |
| `idv-stripe-rn-new-md` | `https://docs.stripe.com/identity/verify-identity-documents.md?platform=react-native&type=new-integration` | the same | 200, 13,445 | `5fcf9db426a2d9cbdea6046a85179ea9d58be1ec487cad9fbb3d7678d3de553c` | none found |
| `idv-stripe-selfie-md` | `https://docs.stripe.com/identity/verification-checks.md?type=selfie` | the same | 200, 9,905 | `ff857cc3daec023d4f5be2204fc670e9ea1ff5cf7108b8027813311d6ac10a89` | none found |
| `idv-stripe-sessions` | `https://docs.stripe.com/identity/how-sessions-work` | `https://docs.stripe.com/identity/verification-sessions` | 200, 548,657 | `d6f14e1f3a1eed89b33551d4129a48dc976742daa4a23dd1b34fc61da79e2906` | none found |
| `idv-stripe-sessions-md` | `https://docs.stripe.com/identity/verification-sessions.md` | the same | 200, 14,109 | `dcbc7218053b05aa55606f02b47512d5f7566c39077bfb6d914d228e7adc8ebb` | none found |
| `idv-stripe-svcprov` | `https://stripe.com/legal/service-providers` | the same | 200, 204,858 | `e77ab54dbcb9802d15911d54417545d84305c1eeff11d8b3d5ca5aacf298b21c` | "Last updated: September 27, 2026" |
| `idv-stripe-usecases-md` | `https://docs.stripe.com/identity/use-cases.md` | the same | 200, 3,898 | `94b4f7acbfccf31e1fd3199ceda5c22815d15e1d890363b8c0ba16acd212b3b0` | none found |
| `idv-sumsub-consent` | `https://docs.sumsub.com/docs/consent-screen.md` | the same | 200, 9,508 | `a243d80f213b5e528f8925758a66cc6a4ef771886f1094f7abb77527a6087740` | none found |
| `idv-sumsub-dpa` | `https://sumsub.com/files/data_processing_agreement.pdf` | the same | 200, 412,126 | `ad7086344ec1d830dcb2257c6889bea23f5fabb50245e5260264f35fd8859410` | none found |
| `idv-sumsub-fraudnet` | `https://docs.sumsub.com/docs/fraud-networks-detection.md` | the same | 200, 20,272 | `08e9cf90f23bab57becbe59a5528a7c8997fd351e492c30e4823076d66d6c93e` | none found |
| `idv-sumsub-getapp` | `https://docs.sumsub.com/reference/get-applicant-data.md` | the same | 200, 181,843 | `be01b4432fcde98282715f2fa5424d6266aaf841af7774bfb2e0edc33c2c3389` | none found |
| `idv-sumsub-ldp` | `https://docs.sumsub.com/docs/local-data-processing.md` | the same | 200, 5,978 | `14456930dbb6b6fd511b99ac4c1f9c2450d0d2da08b44fe203fd0f7938a4970c` | none found |
| `idv-sumsub-liveness` | `https://docs.sumsub.com/docs/liveness.md` | the same | 200, 4,367 | `10a6f76b56cc9fc37db5e35569fd5abd801b9bce5c1895d755921ddd2eccd804` | none found |
| `idv-sumsub-llms` | `https://docs.sumsub.com/llms.txt` | the same | 200, 85,587 | `65c58f49d84077c974388aea1cbeccb83832bd2efa6de5c50bde77663cc6bfb2` | none found |
| `idv-sumsub-manualrev` | `https://docs.sumsub.com/docs/delegate-rejected-applicants-for-manual-review.md` | the same | 200, 4,027 | `400d85f86b233e85cae6530e0c20a68186dcdd91a6514a259affbb574e78dcc4` | none found |
| `idv-sumsub-pricing` | `https://sumsub.com/pricing/` | the same | 200, 247,199 | `be8c7505656695db477e3d34337e3b601fb9a72331c92f0c37e979c5ecf57adc` | none found |
| `idv-sumsub-privacy` | `https://sumsub.com/privacy-notice/` | the same | 200, 154,137 | `60a9895bbed50b15f57d31286816f4a05734256a867265b7e318e6ff160a1bdb` | none found |
| `idv-sumsub-privdisc` | `https://docs.sumsub.com/docs/applicant-privacy-disclosures-and-consent-requirements.md` | the same | 200, 6,323 | `aaf44b63d7140b5ad5635a44951e7e1b55a42d12bb3e7e96c49c874d2c5c8340` | none found |
| `idv-sumsub-privsvc` | `https://sumsub.com/privacy-notice-service/` | the same | 200, 258,655 | `fee3a5437def4069b230d4fe3c63fc6c517ffafdb69e638d65db59eb9253ea24` | none found |
| `idv-sumsub-results` | `https://docs.sumsub.com/docs/receive-and-interpret-results-via-api.md` | the same | 200, 4,034 | `d895a37d30c5a1dba8f41bba8b1f8c3e3909bbacb347233b3ef53ebeb8be8e27` | none found |
| `idv-sumsub-rn` | `https://docs.sumsub.com/docs/react-native-module.md` | the same | 200, 20,145 | `b5a29b1bc23ae3a3e7de552b29e3551edf9a92e3e7c64d041c741a8e75f56334` | none found |
| `idv-sumsub-subproc` | `https://docs.sumsub.com/docs/third-party-processors-and-affiliates` | the same | 200, 1,517,112 | `096c86a8ebfcb233e1659f343740f985b1a3c94c065cb0f33d17094b0c5e24a8` | none found |
| `idv-sumsub-terms` | `https://sumsub.com/terms-and-conditions/` | the same | 200, 329,947 | `c4ab9d1924657ea0880e1cfc7eaaac82a8dbb43dad6429540413aafb2a64771c` | none found |
| `idv-sumsub-trust` | `https://sumsub.com/sumsub-trust-center/` | the same | 200, 162,622 | `562c879116a349941b48ccb58cbc9e3d1653e819e0320d43c9cf787cd1f0b531` | none found |
| `idv-veriff-bioliv` | `https://devdocs.veriff.com/docs/biometric-liveness.md` | the same | 200, 18,632 | `57d711cc0fd18841fe381a4adba3c91f380006951719770e7d8dbba3d78bbc36` | none found |
| `idv-veriff-biover` | `https://www.veriff.com/product/biometric-verification` | the same | 200, 128,477 | `50420f6cf5492cbe5e1d0f505a7598a28d8c944fdc460e09573fb7ad8692f58f` | none found |
| `idv-veriff-decisions` | `https://devdocs.veriff.com/docs/verification-session-decisions.md` | the same | 200, 4,587 | `65baac599d9ff5959fa3b0e9191e57944d29f9b73694055bd56cb585f9334732` | none found |
| `idv-veriff-decwh` | `https://devdocs.veriff.com/docs/decision-webhook.md` | the same | 200, 93,135 | `a590b8d8c5ed3911d0a1769be846faf0c3ee19e4b3146114ece14c3948864cca` | none found |
| `idv-veriff-delete` | `https://devdocs.veriff.com/apidocs/v1sessionsid-3.md` | the same | 200, 10,297 | `3be355f3f25bc6bc67aac48c9e4ee631bbc7a2597653053f0dbde075d745ed63` | none found |
| `idv-veriff-devprivacy` | `https://devdocs.veriff.com/docs/privacy-notice-and-data-collection-purposes.md` | the same | 200, 2,873 | `8809a51f8c188b81a8091cb51f0f67381934227aaa911a0239a7170e8d792d21` | none found |
| `idv-veriff-docfields` | `https://devdocs.veriff.com/docs/document-data-fields-1.md` | the same | 200, 1,439 | `55a38db045d530782a9cfe166d30043255e6247725757a62123a3cd8f102111b` | none found |
| `idv-veriff-dpa-idx` | `https://www.veriff.com/data-processing-addendum` | the same | 200, 89,031 | `ad456ea3fd2f6184edfe76031d6e6941979547cc67d7694bbee7c275b8bd78bb` | none found |
| `idv-veriff-dpa2303` | `https://www.veriff.com/data-processing-addendum/ver-DPA-2303` | the same | 200, 132,365 | `dd11350ca77ae09fc775990ce7782341abb801bf577aaeb7e9d4923061888ac5` | none found |
| `idv-veriff-dpainsight` | `https://help.veriff.com/en/articles/13106404-insight-into-the-data-processing-addendum-how-will-veriff-use-the-data` | `https://help.veriff.com/VeriffLogin?startURL=%2Fen%2Farticles%2F13106404-insight-into-the-data-processing-addendum-how-will-veriff-use-the-data` | 200, 15,354 | `38f79511fecedded1059de970f0edd9fa9a810c139fd08b8e14c55b7ec5c314b` | none found |
| `idv-veriff-fullauto` | `https://devdocs.veriff.com/docs/full-auto-webhook.md` | the same | 200, 10,293 | `adf00d69e9c2635f60abc8739f8ee3ac4df04062445ebb42bcf94ac7923f2813` | none found |
| `idv-veriff-gran` | `https://devdocs.veriff.com/docs/granular-reason-codes.md` | the same | 200, 13,387 | `cbf2276444c71211ce1792915f62de6ae7fa40f7a560f776754f114135441de8` | none found |
| `idv-veriff-llms` | `https://devdocs.veriff.com/llms.txt` | the same | 200, 26,234 | `85b6adfc27538816c3b0c4544a873a589b70f7c7c5ac22b2ad88c2384e1df8b1` | none found |
| `idv-veriff-pricing` | `https://www.veriff.com/pricing` | the same | 200, 487,036 | `d9aeef6a7c3a215edb3f4dbabea7e0e89a70c67d01a2673af106a5c14e639f26` | none found |
| `idv-veriff-privacy` | `https://www.veriff.com/privacy-notice` | the same | 200, 198,131 | `5ad372dcd196374e179a510420c2b9ca33da9442634aba5f1cbbfbaf5ac27028` | none found |
| `idv-veriff-rn` | `https://devdocs.veriff.com/docs/react-native-sdk-guide.md` | the same | 200, 13,174 | `f17290d4c5451e6fc36029f8cd64e7c8028808b3e8a60882cf1d2130d4d9d1df` | none found |
| `idv-veriff-sdkintro` | `https://devdocs.veriff.com/docs/quick-guide-of-idv-using-the-sdks-1.md` | the same | 200, 4,291 | `fab3b4d233cbbaeee8c07eed6eebcc1839fc753b48c0fe89249b8cc92a0f6b2e` | none found |
| `idv-veriff-seccomp` | `https://www.veriff.com/security-and-compliance` | the same | 200, 103,215 | `f480eb5fd6d99c7a9512f95de6c9e327333c032161f77edb587243ad4ce75caf` | none found |
| `idv-veriff-subproc` | `https://help.veriff.com/en/articles/6896122-sub-processors-used-by-veriff` | `https://help.veriff.com/s/article/Sub-processors-used-by-Veriff` | 200, 581,190 | `cee4ba74c302850ed9e236c1a2f308baa37a8794e9a6be064f37186d0b0c3959` | none found |
| `idv-veriff-subproc-r` (rendered) | `https://help.veriff.com/s/article/Sub-processors-used-by-Veriff` | the same | 200, 244,760 | `6d7f933ccc782cb4c4e94e4a26f18392e0604104b7265bd85d180120617aaa14` | none found |
| `idv-veriff-subproc-r2` (rendered) | `https://help.veriff.com/en/articles/6896122-sub-processors-used-by-veriff` | `https://help.veriff.com/s/article/Sub-processors-used-by-Veriff` | 200, 244,760 | `6d7f933ccc782cb4c4e94e4a26f18392e0604104b7265bd85d180120617aaa14` | none found |
| `idv-veriff-tos-idx` | `https://www.veriff.com/terms-of-service` | the same | 200, 89,105 | `3859c05cd5c089d77089a62ded8b0048431ed2b1e255165955eb2c847529bc2c` | none found |
| `idv-veriff-tp-faq` (rendered) | `https://trust.veriff.com/faq` | the same | 200, 48,126 | `51890e7d9f73c08cd5e888bb009a550dce5182b8417c6dee6b7290961b4146b1` | none found |
| `idv-veriff-tp-subproc` (rendered) | `https://trust.veriff.com/subprocessors` | the same | 200, 63,912 | `2be7ee6e7d0d56de826bce90d9fab0fea643783ff1c255086e699f637aeabec1` | none found |
| `idv-veriff-trust` | `https://www.veriff.com/trust-center` | the same | 200, 109,315 | `ea2eed7c6d4b7c671458296c4f47c28ad7fc2d4391f36e31b36c2f83ef3a9f14` | none found |
| `idv-veriff-trustportal` (rendered) | `https://trust.veriff.com/` | the same | 200, 119,894 | `7023a3e937e7f5c16e759364dffb2f45a331d711bbfc76d34358e154e025a69c` | none found |
| `idv-yoti-pricing` | `https://www.yoti.com/business/pricing/` | the same | 404, 65,890 | `e0718d93d44787955830a2b7929e8571c3e51fb41ac51266d7d8b71fb62c339c` | none found |
| `svc-stripe-restricted` | `https://stripe.com/restricted-businesses` | `https://stripe.com/legal/restricted-businesses` | 200, 219,127 | `e051923bb5bcac74c89b824c0559254c4c2a9fd04ac6b54268a35babb9d6b664` | "Last updated: 2026-09-22" |

### C.3 Photo checks and hash matching

| Fetch name | URL fetched | Final URL | HTTP, bytes | SHA-256 | Page date |
|---|---|---|---|---|---|
| `mod-amplify-rn-label` | `https://docs.amplify.aws/react-native/build-a-backend/add-aws-services/predictions/label-image/` | the same | 200, 293,912 | `e2ce69ed34aed186baf95270ef09c16598f436e7406e1e5186d605ae15fae6ac` | none found |
| `mod-aws-a2i-rek` | `https://docs.aws.amazon.com/rekognition/latest/dg/a2i-rekognition.html` | the same | 200, 25,588 | `69ca8fa29bab58363b730fb57e133a6d76b3135e8c0448fa4c1ebdbc21b5a0c8` | none found |
| `mod-aws-ai-optout` | `https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_ai-opt-out.html` | the same | 200, 15,893 | `d4b66ed7f470b753c356076e053d46a08aaf4787641e8fd37a54e66f735c8c6e` | none found |
| `mod-aws-biometric-terms` | `https://aws.amazon.com/legal/biometric-notice-and-consent-terms/` | the same | 200, 298,101 | `aaf2dd0fddcb6e2d94c6333f2d4dc29dd170e32d39924469bb0358e6e33aa097` | "Last Updated: November 14, 2024" |
| `mod-aws-ccpa-terms` | `https://d1.awsstatic.com/legal/aws-ccpa/aws-ccpa-terms.pdf` | the same | 200, 77,472 | `96dc7d67697120a1759cc8bdcccbdcbd27bcdddd1bbd466617012ff31fe8b172` | none found |
| `mod-aws-dataprivacy-faq` | `https://aws.amazon.com/compliance/data-privacy-faq/` | the same | 200, 388,933 | `1638a6980b946ad1abac79a3be1207260223ff28a374167eb64ad2241e3ceb63` | none found |
| `mod-aws-dpa-pdf` | `https://d1.awsstatic.com/legal/aws-dpa/aws-dpa.pdf` | the same | 200, 212,839 | `15f95fd3f83f4880e538ec08867b58f4648bf48fb7a0f8af7d0f79c94f456c19` | none found |
| `mod-aws-rek-agerange` | `https://docs.aws.amazon.com/rekognition/latest/APIReference/API_AgeRange.html` | the same | 200, 13,578 | `aaab7684c4bdd136cfe0aa7212e827406f5f4ea8b25e2c768573d7cc26cfb5bb` | none found |
| `mod-aws-rek-dml-api` | `https://docs.aws.amazon.com/rekognition/latest/APIReference/API_DetectModerationLabels.html` | the same | 200, 33,128 | `f7133474d301bca41e20c855fd827186a80b971a8e8abab9fe6fd7e86a89e4cc` | none found |
| `mod-aws-rek-endpoints` | `https://docs.aws.amazon.com/general/latest/gr/rekognition.html` | the same | 200, 67,269 | `c85d4bbe8ebe21072b7c6daf4fe6b3d07fbc8481d4490ddcd3c16f10b69408b7` | none found |
| `mod-aws-rek-faqs` | `https://aws.amazon.com/rekognition/faqs/` | the same | 200, 647,645 | `bc98b9d54c143857e0f621ccd6e01a8c0dc61e3731403155092fbc3931da57d0` | none found |
| `mod-aws-rek-modapi` | `https://docs.aws.amazon.com/rekognition/latest/dg/moderation-api.html` | the same | 200, 35,949 | `b10b882f66fb367b9b0d6bbda6169802ba679189407e79442d892c5b1eebc4b2` | none found |
| `mod-aws-rek-moderation` | `https://docs.aws.amazon.com/rekognition/latest/dg/moderation.html` | the same | 200, 13,780 | `06a3c5b95db97c8f242f6bdfdb9fbd70b96159fb03792658115affba53a1933a` | none found |
| `mod-aws-rek-pricejson` | `https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/rekognition/USD/current/rekognition.json` | the same | 200, 244,247 | `bcc2e019bc28545c8ef1265dd433403c8d61a290c7728dc3da87162d5ba3b7ff` | none found |
| `mod-aws-rek-pricing` | `https://aws.amazon.com/rekognition/pricing/` | the same | 200, 401,104 | `149884a5dc987662d636c94ffe5a0c3d34c7353abe00023f1074e08ec28baef5` | none found |
| `mod-aws-rek-pricing-r` (rendered) | `https://aws.amazon.com/rekognition/pricing/` | the same | 200, 489,008 | `c7c7cd6cd7ec20d957dc9de79ca82c1622294eb0958130a1bc506fae05aca873` | none found |
| `mod-aws-service-terms` | `https://aws.amazon.com/service-terms/` | the same | 200, 1,041,795 | `07e11b5a96b3b645eddc5dc933857c2cd92ae44b244ad196c4519f805bfbe8b3` | none found |
| `mod-aws-subprocessors` | `https://aws.amazon.com/compliance/sub-processors/` | the same | 200, 378,338 | `c56fe5d4be56ac22ee847c388f4a7f313042a969fd83592fea5415d1d80c69ab` | "Last Updated: October 30, 2026" |
| `mod-azcs-harm` | `https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/harm-categories` | the same | 200, 118,033 | `76128cd5f75397849dbc00c2809139309ca1c237b3747819fd95bddef477e23a` | none found |
| `mod-azcs-overview` | `https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview` | the same | 200, 67,976 | `38da639616fb7545cd9bd1b183488b1e32d061d044c9abbdb61047e4e325afab` | none found |
| `mod-azcs-pricing` | `https://azure.microsoft.com/en-us/pricing/details/cognitive-services/content-safety/` | `https://azure.microsoft.com/en-us/pricing/details/content-safety/` | 200, 196,716 | `8006ef4cca70b3c43582fe3b3139c8ccfedcec2f1ae3c4f5d6c165578fc9dff7` | none found |
| `mod-azcs-pricing-r` (rendered) | `https://azure.microsoft.com/en-us/pricing/details/content-safety/` | the same | 200, 477,000 | `8b5af8e671706236180aacee93a73507008afe76fda9ff2ba4999440c05ed0cd` | none found |
| `mod-azcs-privacy` | `https://learn.microsoft.com/en-us/legal/cognitive-services/content-safety/data-privacy` | `https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/content-safety/data-privacy` | 200, 51,264 | `6e1716f70158918517b71fd33dee0f76d97a5f0b389c678b2c24de3a56c232c6` | none found |
| `mod-azcs-qs-image` | `https://learn.microsoft.com/en-us/azure/ai-services/content-safety/quickstart-image` | the same | 200, 104,216 | `fa7682b35aaff0dfe5dd5c02489f2fd5ea146d29e85e3962cfe2c9423951ea73` | none found |
| `mod-azcs-regions` | `https://learn.microsoft.com/en-us/azure/ai-services/content-safety/region-availability` | the same | 200, 80,998 | `4ec34505970c1a82d085433187a862152c62f4ce60f1a1c0bfb36959a838e45f` | none found |
| `mod-azcs-transparency` | `https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/content-safety/transparency-note` | the same | 200, 73,162 | `7bd3d42db5678c9c06cff23917d8e88c33165f7bbc83cc60766d4082811c6469` | none found |
| `mod-c3p-arachnid` | `https://projectarachnid.ca/en/` | `https://projectarachnid.com/en/` | 200, 139,211 | `ba23538cae81632e736ee1cc2fe86cb463929d1b0964dfe548f523432a2cc78d` | none found |
| `mod-c3p-shield-docs` | `https://shield.projectarachnid.com/docs/` | the same | 200, 734 | `bb9928afd0ea8c12e124c42fef58fb080f36770389684badb2a4dcf548624eeb` | none found |
| `mod-c3p-shield-docs-r` (rendered) | `https://shield.projectarachnid.com/docs/` | the same | 200, 23,891 | `18e004edbbaa9092092dba0bc4b68e9555975f55767fb890d41aae18752c690d` | none found |
| `mod-c3p-shield-register` | `https://projectarachnid.com/en/api/accounts/register/` | `https://projectarachnid.com/en/api/accounts/register/account/` | 200, 15,825 | `5fbf1229861d12fa5f69ac1c4870ab98fd4fb18a0742c2cbfe0a4a974d6da664` | none found |
| `mod-c3p-terms` | `https://projectarachnid.com/en/terms-of-use/` | the same | 200, 32,972 | `a37642e7e1e3ba6d3dbe1083ad1ccad96c96355506b19190f26c4b5d82bc8e27` | none found |
| `mod-cf-csam-blog` | `https://blog.cloudflare.com/the-csam-scanning-tool/` | the same | 200, 311,191 | `3568bd36a951ae7fcd112ec4da132b94c9fb4d42517b13d9c38b0861ea4d8601` | none found |
| `mod-cf-csam-docs` | `https://developers.cloudflare.com/cache/reference/csam-scanning/` | the same | 200, 117,220 | `44c11d048a0d5a9ebe7ccdaee066d3bdf4fa5d8eb3f7710217bd9c7148882671` | none found |
| `mod-cf-sst-app` | `https://www.cloudflare.com/service-specific-terms-application-services/` | the same | 200, 425,557 | `3124b67e788660b857c8c67635e3b7bcdfb8855ede545a5baf5cbb8838a99248` | "Last updated: September 28, 2026" |
| `mod-clar-docs-mod` | `https://docs.clarifai.com/` | the same | 000, 0 | `none` | — |
| `mod-clar-pricing` | `https://www.clarifai.com/pricing` | the same | 000, 0 | `none` | — |
| `mod-clar-pricing-r` (rendered) | `https://www.clarifai.com/pricing` | the same | 502, 174 | `9d25629d26cd3d047df9b9d431d9764e2b718796255de95d9452e37c8fa05742` | — |
| `mod-clar-pricing2` | `https://www.clarifai.com/pricing` | the same | 000, 0 | `none` | — |
| `mod-deploy-entcommit` | `https://deploy.com/enterprise-commitments` | the same | 200, 84,320 | `9b554c8f71b3b94b15d1157fc7b4fc65ad756a19051f70f00f3f46bc08958ab8` | none found |
| `mod-deploy-home` | `https://deploy.com/` | the same | 200, 393,215 | `ecc0d667cc7656e64b9f220200d62d970bc1ee65369e96a81180e295c8f0c5b0` | none found |
| `mod-deploy-terms` | `https://deploy.com/terms` | the same | 200, 7,892 | `dc824d78afb58dc896f667ce2226ac9f3744f8db887ec537e66469a15d5c1f5a` | none found |
| `mod-deploy-termsofuse` | `https://deploy.com/terms-of-use` | the same | 200, 173,181 | `277e93217fec3c94319b1b635db529427b51af92275b2585d757ff22b54d1f3a` | none found |
| `mod-gcp-dpa` | `https://cloud.google.com/terms/data-processing-addendum` | the same | 200, 913,744 | `c8d6224056cda73a51df4eb510728d97d02ed7a7347d77cd923607e0edd1f1eb` | "Last modified October 30, 2026" |
| `mod-gcp-service-terms` | `https://cloud.google.com/terms/service-terms` | the same | 200, 1,071,004 | `dfe9485481db0bd7ce963cec7d1b35c5790873ac88e6c3dfcf5ef6156666fca3` | "Last modified November 11, 2026" |
| `mod-gcp-subprocessors` | `https://cloud.google.com/terms/subprocessors` | the same | 200, 1,971,263 | `bd66c20ae512bd0ab836ef60ab8659f7fd951a81225b979b3a6dd951cee11c46` | "Last modified November 16, 2026" |
| `mod-gcv-datausage` | `https://cloud.google.com/vision/docs/data-usage` | `https://docs.cloud.google.com/vision/docs/data-usage` | 200, 125,254 | `bf4a9d060c3269aa1b05c6f7754ed37664c04664520ec5d9f62592f5c142f87d` | "Last updated 2026-11-10" |
| `mod-gcv-faces` | `https://cloud.google.com/vision/docs/detecting-faces` | `https://docs.cloud.google.com/vision/docs/detecting-faces` | 200, 362,695 | `28ea878c362f9b71be6568feadf3a1a45ceef3f25b1802d659576d7ee3b6311c` | "Last updated 2026-11-10" |
| `mod-gcv-libraries` | `https://cloud.google.com/vision/docs/libraries` | `https://docs.cloud.google.com/vision/docs/libraries` | 200, 288,888 | `ce7806951f26e60534125e6d4d84dcd5a23f52da3e8c3230e860194c1da265e1` | "Last updated 2026-11-10" |
| `mod-gcv-ocr` | `https://docs.cloud.google.com/vision/docs/ocr` | the same | 200, 352,441 | `2904527a5d47c34830f8d2759b5651be6df7b8e8bbe510c50a539318440f744e` | "Last updated 2026-11-10" |
| `mod-gcv-pricing` | `https://cloud.google.com/vision/pricing` | the same | 200, 1,597,571 | `fffce5861f7cb822f2f7fe7f0ea40496a42234aec5f61214faccf68e7a2184f4` | none found |
| `mod-gcv-safesearch` | `https://cloud.google.com/vision/docs/detecting-safe-search` | `https://docs.cloud.google.com/vision/docs/detecting-safe-search` | 200, 305,079 | `fef4105b83bbea5c0f0f1bbafcf5b3cf1025b72fc942eefb4042e22bf30e1452` | "Last updated 2026-11-10" |
| `mod-gcv-setendpoint` | `https://docs.cloud.google.com/vision/docs/samples/vision-set-endpoint` | the same | 200, 158,860 | `bb5ba8edd7493ab5a18d93a7f78ac40b30e2fb53b76713acb039a3d366684f9f` | none found |
| `mod-goog-toolkit` | `https://protectingchildren.google/tools-for-partners/` | the same | 200, 205,860 | `163e8569ea5e7f9c98fc673d804a2b922e8b99768d427870d789ef09b822c453` | none found |
| `mod-hive-appeals` | `https://docs.thehive.ai/docs/handle-appeals.md` | the same | 200, 8,909 | `84220e48b50f4928895f1e781543afa166a4a3a62d3afb1cbaeae9626b9204c6` | none found |
| `mod-hive-csam-classifier` | `https://docs.thehive.ai/docs/csam-detection-api.md` | the same | 200, 2,297 | `ab22aaec59f26dde2f3e01d53457d4126a4f90925470b8305ddee745db8095e4` | none found |
| `mod-hive-csam-combined` | `https://docs.thehive.ai/docs/csam-detection-combined-api.md` | the same | 200, 3,688 | `8956868cd7c589376cc83a5be15b275f34bd3556f4978300270a514f5829f8f9` | none found |
| `mod-hive-csam-hash` | `https://docs.thehive.ai/docs/image-and-video-csam-matching.md` | the same | 200, 2,838 | `70c810871a2ef93f05c008bcda222ebba05ca51878abf90e8a1ba7cb8d1d2ff6` | none found |
| `mod-hive-demographic` | `https://docs.thehive.ai/docs/demographic-attributes.md` | the same | 200, 4,358 | `469998fe2ea8df3acd6b16d5bf3a9ae00c935cfb47600cebb7a888c1eaf6dd94` | none found |
| `mod-hive-docs-vcm` | `https://docs.thehive.ai/docs/visual-content-moderation` | the same | 200, 265,394 | `5848354f70a54ec86defbdeba5c638763fa89eecfdd64a7ff28200984d21b5bd` | none found |
| `mod-hive-faq` | `https://docs.thehive.ai/docs/frequently-asked-questions-faq.md` | the same | 200, 13,493 | `c64a6a172e45db5c8bb25ee695684059fd90576b23b7ed31808767d6c14c8141` | none found |
| `mod-hive-getting-started` | `https://docs.thehive.ai/docs/getting-started.md` | the same | 200, 11,681 | `ddce24ee888afed28f0f8337d4540199e9191ebc28c555fdd78d06b3b625501d` | none found |
| `mod-hive-humanreview` | `https://docs.thehive.ai/docs/moderation-dashboard-quickstart-part-2-human-review.md` | the same | 200, 9,819 | `1e286c18b9c4d46e54a80ab99ff147790cf1cc3954d87ec2739353f87237349c` | none found |
| `mod-hive-llmstxt` | `https://docs.thehive.ai/llms.txt` | the same | 200, 16,598 | `7532df79970ed5bba1a19485d6122aa69b5269d1a1cf7532985df8c293bcea1b` | none found |
| `mod-hive-ncmec` | `https://docs.thehive.ai/docs/report-to-ncmec.md` | the same | 200, 15,000 | `3773304000a637965f3d8803796611585cb8ad0d6c3ca132dcc80c532b5e82eb` | none found |
| `mod-hive-pricing` | `https://thehive.ai/pricing` | `https://deploy.com/pricing` | 200, 209,109 | `e67c3128374c37c1a69c7705587fbe90c83ea4a9b8513e74ed6e9916aec5cb65` | none found |
| `mod-hive-privacy` | `https://thehive.ai/privacy` | `https://deploy.com/privacy` | 200, 161,207 | `83a35d026c79def7eae5873c57bae8ea562ea9fffff8c18990f8a7d7475cb7c7` | none found |
| `mod-hive-terms` | `https://thehive.ai/terms` | the same | 200, 1,096 | `e390b3c513593a45dfdf5bd9937973921783d8408088141e2caab0c70fae8db8` | none found |
| `mod-hivemod-home` | `https://hivemoderation.com` | `https://hivemoderation.com/` | 200, 519,849 | `7adb25df5142c672f21bd1c0fae932c36594f463419fbdb703209e88180f8ecf` | none found |
| `mod-iwf-fees` | `https://iwf.org.uk/membership/fees/` | `https://www.iwf.org.uk/membership/fees/` | 200, 189,649 | `4f62df68769fe2131cb3ed2b42bd437ace5a466dd95f87699c8a79d1ebf24494` | none found |
| `mod-iwf-hashlist` | `https://www.iwf.org.uk/our-technology/our-services/image-hash-list/` | the same | 200, 196,713 | `aee3f714b6b2a5c20db471d1398f8aad3ffcafe60044226210f0f09f47f11db5` | none found |
| `mod-iwf-howtojoin` | `https://iwf.org.uk/membership/how-to-join/` | `https://www.iwf.org.uk/membership/how-to-join/` | 200, 249,108 | `0212dffe9e95ea51743aeec3e33e5173c40c40a8ac1cff3518578d671f19ff07` | none found |
| `mod-ms-dpa` | `https://www.microsoft.com/licensing/docs/view/Microsoft-Products-and-Services-Data-Protection-Addendum-DPA` | the same | 200, 1,043,734 | `a74de214a0a2ebe2d45ce4a75b023b351a3f4e1e2888d92bc11d583706005583` | none found |
| `mod-ms-dpa-docx` | `https://www.microsoft.com/licensing/docs/documents/download/MicrosoftProductandServicesDPA(WW)(English)(November_2026)(CR).docx` | the same | 200, 6,592,518 | `f324f04afcb9763324411da705e6df6d79b704c74dab04f0a6e62bc2404425aa` | none found |
| `mod-ms-subproc-pdf` | `https://api.servicetrust.microsoft.com/api/v2/downloadDocuments/f2cc90fe-471f-4f07-a9ae-af71ebce8486/7b1d8c02-6105-4be4-9995-ff01f87443bc` | the same | 200, 239,807 | `6342b4033805f49c01ada876098f1f77d2ff2c8e6e54ad9442e66d4593c5faff` | none found |
| `mod-ncmec-csam` | `https://www.missingkids.org/theissues/csam` | the same | 200, 67,792 | `943fee5d920afbe704a36de462944a1217c2bc529f4b9ac316380b525770c2b0` | none found |
| `mod-ncmec-ctldata` | `https://www.missingkids.org/gethelpnow/cybertipline/cybertiplinedata` | the same | 200, 725,469 | `7c1e1294ac58f80d3bcf2588311f282b6596134c5dcb2db7bd110c8561723970` | none found |
| `mod-ncmec-cybertipline` | `https://www.missingkids.org/gethelpnow/cybertipline` | the same | 200, 70,201 | `c023fe8fec3ee9bdf8ed058d29573481e8591c53e63b2a54d969f56782e39a25` | none found |
| `mod-ncmec-esp-reg` | `https://esp.ncmec.org/registration` | the same | 200, 886 | `e7534bb30c29586c61a7556a1e8b30c765473bb79cb822c5fd2c2ccbb7307861` | none found |
| `mod-ncmec-esp-reg-r` (rendered) | `https://esp.ncmec.org/registration` | the same | 200, 19,083 | `5e872f2f75b76e98c83b479fb5b1a858d81874a3cf5c2450272bea1148a2701a` | none found |
| `mod-ncmec-hs-npo` | `https://hashsharing.ncmec.org/npo` | `https://hashsharing.ncmec.org/npo/v2/documentation/` | 200, 181,920 | `9ad4a4a73814e07147a198d4e40fea01b563a39e1afeff0454c775295e4a4712` | "Last updated 2026-11-02" |
| `mod-ncmec-hs-root` | `https://hashsharing.ncmec.org/` | the same | 200, 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | none found |
| `mod-ncmec-ourdata` | `https://www.missingkids.org/ourwork/ncmecdata` | the same | 200, 74,242 | `05754ec7fb3e18e741421392c8b04153be984818906bcfe28f93470feb442d68` | none found |
| `mod-pdna-cloud` | `https://www.microsoft.com/en-us/photodna/cloudservice` | the same | 200, 154,881 | `5f6c905b71edcfadf3120920858b3320bfaaa05d20a3e5d6bb639bb1e4e25887` | none found |
| `mod-pdna-faq` | `https://www.microsoft.com/en-us/photodna/faq` | the same | 200, 131,338 | `c9da30a42ef2162abfc7c38f1b1129d289babd0f1b0733ae5c27ba61bcf67538` | none found |
| `mod-pdna-home` | `https://www.microsoft.com/en-us/photodna` | the same | 200, 134,466 | `057ae35592a86a7c6ba6b4102e73a87405eeea60cbcb41d0750815735219e7c5` | none found |
| `mod-pdna-terms` | `https://www.microsoft.com/en-us/PhotoDNA/TermsofUse` | the same | 200, 104,750 | `9b647708a92c57932684aa4e3fb00bc6ac520143cdc5ea06e57186b2ee06907f` | none found |
| `mod-safer-awsmp-r` (rendered) | `https://aws.amazon.com/marketplace/pp/prodview-unzbqt3w6pqbg` | the same | 0, 4,670,006 | `9835ee9d38711d602623daeb3a49d8ec45f4bb83491ea669b81adb57326123dd` | none found |
| `mod-safer-criteria` | `https://safer.io/safer-partnership-criteria/` | the same | 200, 23,198 | `ef6bd98b4de808d8581d91e81ad46f8bd1f812550840b6d98027e2c4d85f3d01` | none found |
| `mod-safer-faq` | `https://safer.io/faq/` | the same | 404, 14,430 | `9c994a74057bac4133fdef9573ffa080fab9c2047015db7fca4243bf2886366c` | none found |
| `mod-safer-home` | `https://safer.io/` | the same | 200, 36,161 | `c47163c80e3ed4c8f21061e5132a30617decf3e29c3d75c0b61950d27778c011` | none found |
| `mod-safer-pricing` | `https://safer.io/pricing/` | the same | 404, 14,430 | `9c994a74057bac4133fdef9573ffa080fab9c2047015db7fca4243bf2886366c` | none found |
| `mod-safer-solutions` | `https://safer.io/solutions/` | the same | 200, 64,392 | `7aa139ec246ab93e903e2ff1218a358cd81b0b61ed03e29a7821d51d5db94d00` | none found |
| `mod-se-aup` | `https://sightengine.com/policies/acceptable-use` | the same | 200, 48,399 | `c168f6495599e98d6218c9678abc27fc8b6de35fcd775f94a7c6bd6386b51712` | none found |
| `mod-se-docs-faceanalysis` | `https://sightengine.com/docs/face-analysis` | the same | 200, 158,373 | `b936fa7932b7fcc463391fb695bb8ceb5bec7379fd6b5c963a9909b56bb3c345` | none found |
| `mod-se-docs-getstarted` | `https://sightengine.com/docs/getstarted` | the same | 200, 74,271 | `c8e0857dd42745c35c95bdc19d9d2630d24db53c3e6a8f276411521bc869478e` | none found |
| `mod-se-docs-gore` | `https://sightengine.com/docs/gore-disgusting-horrific-content-detection` | the same | 200, 131,717 | `e02891325eede48169f86cafe402e212ac966cc80b394a5f0dcb2acd091f5c0f` | none found |
| `mod-se-docs-index` | `https://sightengine.com/docs/` | the same | 200, 96,202 | `caf8a606066694db3dc8296661783adea4b568e50cdd11f3f3c5a5e334af3968` | none found |
| `mod-se-docs-minor` | `https://sightengine.com/docs/face-age-minor-detection` | the same | 200, 125,073 | `d30a92a2b717df0a5dad1281d6d5da266310124f12185486c1abdca03873042c` | none found |
| `mod-se-docs-models` | `https://sightengine.com/docs/models` | the same | 200, 110,035 | `84903fef16d67add700471318e8214cc633a414a96533db865bbf54b268a7cf5` | none found |
| `mod-se-docs-nudity` | `https://sightengine.com/docs/nudity-detection` | the same | 404, 38,564 | `89f0fa4da07eab17503177b83c51b981e5d05ed1b1193a032f4d0b0b6a98e968` | none found |
| `mod-se-docs-nudity21` | `https://sightengine.com/docs/advanced-nudity-detection-model-2.1` | the same | 200, 145,099 | `bda9c35abeb2d85bbd0da59ad07dc0a85c064845460b601fb73241c93b5a0b80` | none found |
| `mod-se-docs-violence` | `https://sightengine.com/docs/violence-detection-model` | the same | 200, 124,453 | `ce7a664077b67fa9c3cd9a5c1d56a4c83eba907c6226cabf64e13ce2d81af3a0` | none found |
| `mod-se-docs-workflows` | `https://sightengine.com/docs/image-moderation-workflows` | the same | 200, 103,081 | `0302ceb63c18e9c8310f11e9b41dee208f08c1f5569189195c9f06dbb7f06785` | none found |
| `mod-se-dpa` | `https://sightengine.com/policies/dpa` | the same | 200, 101,734 | `3f8b1832862c4cbb50b1637a4a25b4b053a3686a0bbafe5f27458abe56303508` | none found |
| `mod-se-faq` | `https://sightengine.com/faq/` | the same | 200, 92,634 | `93701d338456ec21c28732307747bb0f4033aba826882cbe526d741f6d34ee38` | none found |
| `mod-se-faq-feedback` | `https://sightengine.com/faq/report-images-feedback` | the same | 200, 92,351 | `042b8650268a871bf240f3d6a40e7851de640662ec58e4570eab9b6b2ab36c68` | none found |
| `mod-se-faq-gdpr` | `https://sightengine.com/faq/gdpr-content-moderation` | the same | 200, 85,900 | `5e13892c13bf20ae3ca38af31212246d921f580f90ec3cb998dbe57299719c3a` | none found |
| `mod-se-faq-hybrid` | `https://sightengine.com/faq/automated-vs-hybrid-moderation` | the same | 200, 86,353 | `51626768195726eca293016845071a1a8cf43a062ae785b65427d3d0067136a1` | none found |
| `mod-se-faq-location` | `https://sightengine.com/faq/data-processing-location` | the same | 200, 86,331 | `0ef6c11f6feef5be37b14ba23eb533615b34ab3657f8aabeda1772916f902815` | none found |
| `mod-se-faq-retention` | `https://sightengine.com/faq/data-retention-after-processing` | the same | 200, 86,192 | `f371550fad7effa4bc7646b03d62a47e60e74e1810568b796d19180f66564cb0` | none found |
| `mod-se-faq-send` | `https://sightengine.com/faq/ways-to-send-image-to-api` | the same | 200, 85,991 | `081b628221873fabf9fcad054a34a43e2dd148678ee01030ea549b2b1abc5cd8` | none found |
| `mod-se-pricing` | `https://sightengine.com/pricing` | the same | 200, 86,931 | `84b8294dedf79800624443ccffa16bec529386e674bc416c1eb5f84c993d4ac1` | none found |
| `mod-se-privacy` | `https://sightengine.com/policies/privacy` | the same | 200, 55,774 | `a75ee2508edb334fac0b0f25e77c3c7f1678b7aa06eb3fe084160a312f5ac276` | none found |
| `mod-se-profile` | `https://sightengine.com/profile-image-moderation` | the same | 200, 57,337 | `dcf04df9da9abcccdf8b6f4224edb92a3eddbfc3b15eb7059ee8decb532a214c` | none found |
| `mod-se-security` | `https://sightengine.com/security` | the same | 200, 45,942 | `a1710316c7e6614ef67bc095030c923131a077cd1ead1e386d79fd44ffb5b142` | none found |
| `mod-se-subprocessors` | `https://sightengine.com/policies/subprocessors` | the same | 200, 46,723 | `c672a7d48169a62ef9fae70ea2aee7b5dac8fd1657c602edfe4e80859c55a825` | none found |
| `mod-se-terms` | `https://sightengine.com/policies/terms` | the same | 200, 92,474 | `408b96f7827c82928119169c27b86862afa1acf895102a89d66807256ab4449f` | none found |
| `mod-stopncii-faq` | `https://stopncii.org/faq/` | the same | 200, 36,830 | `14ffcf2bf132de12821987f4076504d027098e72c034befa7c327c6c2ceaf697` | none found |
| `mod-stopncii-home` | `https://stopncii.org/` | the same | 200, 42,203 | `8f041b2fbc3480f2f40716aacf473ee4d3a63627cee51fe0eb24edf4146efb7b` | none found |
| `mod-stopncii-industry` | `https://stopncii.org/partners/industry-partners/` | the same | 200, 37,074 | `dcfba84605c8f416a25246010bbc8b21f7b22194f65e7bc36e2ce28cd2dd9a28` | none found |
| `mod-stopncii-join` | `https://stopncii.org/partners/join/` | the same | 200, 10,798 | `dbb45ed0be8c4d2f62adb10c06b93f32e984505780e1d69e606617335147a59d` | none found |
| `mod-tc-criteria` | `https://technologycoalition.org/membership/criteria/` | the same | 200, 113,573 | `a05c51781945f4aac155ac842a24b7dca165e85c174868508920a0f9db882a49` | none found |
| `mod-tc-lantern` | `https://www.technologycoalition.org/lantern` | `https://technologycoalition.org/programs/lantern/` | 200, 139,128 | `5cc8dab7f64ea76005a76b6a4cbef8e8072fcbe09e536f64dcdd67895c9b8218` | none found |
| `mod-tc-membership` | `https://www.technologycoalition.org/membership` | `https://technologycoalition.org/membership/` | 200, 124,868 | `52c81566608f10416de799819a750feb4a8092d3b31dc1d9b6ca9e0c27587a85` | none found |
| `mod-tc-services` | `https://technologycoalition.org/membership/services/` | the same | 200, 118,634 | `2cf33bc40c1e593af9e7933dd4b28f269c25e11b1981f86a5a0de31eda02e07c` | none found |
| `mod-tid-faq` | `https://takeitdown.ncmec.org/faq/` | the same | 200, 117,498 | `e4e3ec1d7f6dda26ff3a7510a87c5f464f2040c624c07940fb1139096cc47c9b` | none found |
| `mod-tid-home` | `https://takeitdown.ncmec.org/` | the same | 200, 97,309 | `e2055334a9021e69fbe8f3f12146b59a4cee7e8b1bb982bcc9c29f14ec746ff9` | none found |
| `mod-tid-participants` | `https://takeitdown.ncmec.org/participants/` | the same | 200, 79,554 | `e7aaa91716ed4e3bedd7993a7132ec0da71109c0c638add078cc592349415e6c` | none found |
| `mod-yt-csai` | `https://youtube.com/csai-match/` | `https://www.youtube.com/howyoutubeworks/` | 200, 159,761 | `04d252fb60a0280f3622394b4000914db82e6ce442e017ca367125a2322ba504` | none found |

## 12. Manager verification (App Manager 12, 17 November 2026, 15:44 UTC)

Against the brief's review plan (revision 2; PP9), on the session's head `0859532` (from `3fce46b`), merged into the manager branch at `e038596`.

- **Scope.** The branch changes the two owned paths only. In the matrix, outside the table rows, it changes the header's Rechecks entry, section 7's T5 and T7 cells (new rows added), G-10's Rows (new rows added) and one dated event of section 10 (Alabama, marked as corrected): all within the owned parts.
- **IDs, by script** (the prompt's check, run here): 320 rows before, 331 after; none missing; none reordered; 11 added (AP-67 to AP-69, UST-52 to UST-59). Every one of the brief's 60 rows carries `rechecked 2026-11-17 (A05-V)`, and no row outside the 60 changed.
- **Fresh fetches**, each into its own scratchpad directory, stripped by a script run with `-I` and searched as one continuous string, after 15:34 UTC (the clock read after the first batch: 15:40 UTC):
  - **the changed requirements:** GP-16, answer 16569691 (both quotations exact) and the Age Signals overview (exact); UST-36, the enrolled HB 161 (same SHA-256 as the session's, `b4672a28…`; the duty matched after removing the PDF's line number "186", as the record says);
  - **unchanged rows sampled:** AP-14, Apple's age-assurance page (exact); UST-51, BIPA (same SHA-256 as the session's, `68284b94…`; three quotations exact; fetched with the Sectigo intermediate from the certificate's AIA URL, verified with `openssl verify`, verification left on); USF-07, 18 U.S.C. 2258A (same SHA-256, exact);
  - **the new rows:** AP-67, the DPLA (two quotations exact); AP-68 and AP-69, the App Review Guidelines (exact); UST-52, Texas §503.001 (same SHA-256, exact); UST-53, RCW 19.375 (two exact); UST-54, RCW 19.373 (exact); UST-55, Colorado's 2026 title 6 (same SHA-256, two exact); UST-56, NRS 603A (same SHA-256, two exact); UST-58, Neb. Rev. Stat. §§87-1118 and 87-1102 (exact); UST-59, Minn. Stat. ch. 325M (same SHA-256, two exact).
  - **Not re-fetched: UST-57** (Connecticut PA 25-113). `www.cga.ct.gov` serves an incomplete chain; the session completed it from the certificate log. GoDaddy's G2 intermediate did not complete it here, crt.sh did not answer, and verification was not turned off. UST-57 is checked against the session's record only.
- **The corrected sentence** of section 10 (Alabama HB 161) agrees with UST-36's row.
- **Since the session's research,** Nathan has changed OD-61 (OD-68, 17 November 2026): for the MVP, no selfie is matched to an ID, ID validation is set aside and kept possible later, a credit card check stands at signup during a free trial of a paid plan, and the automated photo check is dropped behind a toggle. This record stays the dated research for ID validation later and for the photo check's toggle. Three of its statements now depend on OD-68's design, which goes to the Dev Manager first (DM-84): UST-51's State cell ("OD-61 plans the face match"), the identity verification half of the facts table (section 8), and the comparison's use for the MVP (section 7.2).
- **Left for the manager** (the session's section 10, outside its scope): section 1's counts and Contents ranges, G-01's Timing cell, and section 9's sentences on the privacy laws' thresholds and the app-store acts. They go into DM-84 as records corrections.

## 13. PR50's merge receipt (App Manager 12, 17 November 2026, 18:09 UTC)

- **PR50 merged** into `main` at `0a0c4fd619260211ecb54a4ba6a472750f516695` at 18:08 UTC (a merge commit, with the final head `b42ff94` given as the expected head). It carried this record with its verification, OD-68, DM-83's and DM-84's texts and PF02's revision 1.2. `main`'s parents are `cf0ac60` and `b42ff94`, and its tree is `b42ff94`'s.
- **Its pre-merge checklist:** the PR run [44143969115](https://github.com/amthorn78/glow-dating-app/actions/runs/44143969115) on `b42ff94` (ordinary documentation, the application jobs skipped by design); Codex's pass on `b42ff94` with no findings; Dev Manager 5's read, DM-84 (`01603c1`, a read of `21c8fcf`), approving PF02's revision 1.2 as written.
- **`main`'s push run** [44144569576](https://github.com/amthorn78/glow-dating-app/actions/runs/44144569576): Change scope and the Foundation gate `success`, the six application jobs skipped, the gate printing `Ordinary documentation: application jobs intentionally skipped`.
- **The cleanup** [44144569557](https://github.com/amthorn78/glow-dating-app/actions/runs/44144569557) (event `push`, delete mode; no open pull request): `claude/vigilant-ramanujan-jbxqro` (`0859532`) deleted, "merged into main"; `main`, the manager branch and `claude/dev-manager` kept by the keep-list.
- **The remote at 18:09 UTC** (`git ls-remote`): three branches, `main` at `0a0c4fd`, the manager branch at `b42ff94` and `claude/dev-manager` at `01603c1`. The manager branch was then fast-forwarded to `0a0c4fd` (DM-57).
- **Pruned with this receipt:** the DM-84 consultation, its deletion condition met; its link in the review log pinned at `0a0c4fd`.
- **After the merge:** AM12-15 folded into PF02-R54 as PF02's revision 1.3, for the Dev Manager's next read.

## 14. PR51's merge receipt (App Manager 12, 17 November 2026, 19:14 UTC)

- **PR51 merged** into `main` at `a316a3aace9c7a0a6a2e7b0d9e80c1ac7312888c` at 19:12 UTC (a merge commit, with the final head `495d55b` given as the expected head). It carried section 13's receipt, OD-69, DM-85's texts, PF01's revision 1.18 (in the Dev Manager's words), PF02's revision 1.3, and A05-V2's brief (revision 2) and research prompt (at `b9534a9`). `main`'s parents are `0a0c4fd` and `495d55b`, and its tree is `495d55b`'s.
- **Its pre-merge checklist:** the PR run [44155556453](https://github.com/amthorn78/glow-dating-app/actions/runs/44155556453) on `495d55b` (ordinary documentation, the application jobs skipped by design); Codex's pass on `495d55b` with no findings; Dev Manager 5's read, DM-85 (`05c469d`, a read of `8d272a4`).
- **`main`'s push run** [44156121822](https://github.com/amthorn78/glow-dating-app/actions/runs/44156121822): Change scope and the Foundation gate `success`, the six application jobs skipped, the gate printing `Ordinary documentation: application jobs intentionally skipped`.
- **The cleanup** [44156120517](https://github.com/amthorn78/glow-dating-app/actions/runs/44156120517) (event `push`, delete mode): nothing deleted; `main`, the manager branch and `claude/dev-manager` kept by the keep-list.
- **The remote at 19:13 UTC** (`git ls-remote`): three branches, `main` at `a316a3a`, the manager branch at `495d55b` and `claude/dev-manager` at `05c469d`. The manager branch was then fast-forwarded to `a316a3a` (DM-57).
- **Pruned with this receipt:** the DM-85 consultation, its deletion condition met; its link in the review log pinned at `a316a3a`.

