# P09.3a — The requirements matrix: session record

- **Work item:** P09.3a, the store, legal and safety requirements matrix ([brief](../../planning/p09-3a-requirements-matrix.md), revision 1).
- **Prompt:** revision 1, from commit `f40f1d7c2c224d450132855bf3930009554fe142` of the manager branch `claude/magical-wozniak-yfmmx2` ([prompt](../../ephemeral/2026-11-01-p09-3a-matrix-prompt.md)).
- **Session:** the P09.3a research session, started by Nathan in `Glow App - No Stream`. **Branch:** `claude/stoic-pasteur-r24pz8`, started at `f40f1d7`.
- **Date:** 1 November 2026. **Output:** [the matrix](../../planning/store-legal-safety-requirements.md), 320 requirement rows.
- **Research, not legal advice.** The limits are in section 6.

## 1. Environment check (names only)

Run before any other command. No value was read or printed.

| Check | Command (as the prompt gives it) | Result |
|---|---|---|
| HDE-shared names | `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done` | Printed nothing: none of the three is set |
| Stream names | `compgen -e \| grep -E '^STREAM_'` | Printed nothing (grep exit 1): no `STREAM_*` name is set, as `Glow App - No Stream` requires |
| GitHub token names | `compgen -e \| grep -E '^(GITHUB_TOKEN\|GH_TOKEN)$'` | `GH_TOKEN` and `GITHUB_TOKEN` are present, as the environment inventory expects. Their values were never read |

## 2. Start gate

| Step | Result |
|---|---|
| `git fetch origin claude/magical-wozniak-yfmmx2 main` | Fetched; the local `origin/main` moved `35a5827..fcd6ebc` |
| Prompt commit on the live manager branch | `origin/claude/magical-wozniak-yfmmx2` was at `f40f1d7c2c224d450132855bf3930009554fe142` itself: the prompt is current |
| `git switch -C claude/stoic-pasteur-r24pz8 f40f1d7…` | Branch reset to the prompt's commit |
| `git rev-parse HEAD` | `f40f1d7c2c224d450132855bf3930009554fe142` |
| `git merge-base --is-ancestor 6eaee357… HEAD` | `PR38 present` |
| `git diff --name-only fcd6ebc… HEAD \| grep -v -E '\.md$'` | Printed nothing: against `main`, the start holds only Markdown changes |
| `test ! -e docs/planning/store-legal-safety-requirements.md` | `no matrix yet` |
| The brief's "Sessions" | "None yet": the prompt is not stale |
| Open pull requests (GitHub, read only) | None |

**Read before the work**, completely: root `AGENTS.md` and `CLAUDE.md`; the brief; PF01 §7 (all of it, including "Billing" and "Mobile/store readiness"), §8 (phases P04 to P12, for the owner column), A04, A05 and R05; the owner-direction register (OD-23, OD-49 and OD-50 and the rest); M05's findings 2 and 6, E2, E6, N3, N4 and §7; the carried-items file (all of it, including "Carried to P09.3a"); `docs/architecture/privacy-and-safety-rules.md`; and `docs/README.md`, PF00 and the current handoff, as `AGENTS.md` asks.

The session pushed its branch once at the prompt's commit, before any output existed, when the stop hook asked for it (the branch then held only the manager branch's three commits, already on `origin`).

## 3. Method

### 3.1 Research

Six research subagents ran in parallel, one per source family, as the prompt suggests: Apple, Google Play, US federal law, US state law, the UK and the EU. Each received the same brief from this session:

- **Glow's facts** (section 1 of the matrix), with the instruction that the owner's country of establishment is not recorded, so a row gives its condition for each case.
- **The topics** T1 to T11 (the matrix, section 1) and, per family, the specific instruments and questions to cover.
- **Hard rules:** primary sources only (the stores' own pages; the legal text; the regulators' own guidance); a secondary source only to find a primary one, with any row resting on one marked UNCONFIRMED; **never fill a requirement, date, threshold or quote from memory or training data**; a page that cannot be read is listed as unread with its URL and reason; quotes verbatim and short, each marked `curl-text` (exact text from the raw HTML, XML or PDF) or `webfetch` (the WebFetch summariser, which can paraphrase); no write to the repository; scratch files only in the session's scratchpad, with each download in its own directory and Python run as `python3 -I`; never inspect environment variables or credentials, create an account, sign in, buy, submit a form, send a message, call a provider or connect to any service.
- **The network routes this session had tested** at the start (section 3.2).
- **An output format:** rows (ID, topic, requirement, trigger quote and method, source with URL and read date, binds, asks of Glow, status), applicability notes, sources read, sources not read, and facts bearing on the A05 questions.

Each family's researcher machine-checked its quotes against its downloaded text and reported the result: Apple about 340 checks, Google Play more than 200, the EU about 340, each with no miss; the US and UK families quoted from extracted text throughout and listed their few `webfetch` quotes.

**Methods beyond a plain fetch** (all read-only, with TLS verification kept on):

- **developer.android.com** redirected anonymous `curl` requests into a sign-in check loop; the Google researcher used a per-download anonymous cookie jar. No account or credential was used.
- **California:** `leginfo.legislature.ca.gov` refused every request (HTTP 403), so the codes and chaptered bills were read from the Legislature's own bulk data, `https://downloads.leginfo.legislature.ca.gov/pubinfo_2025.zip` (dated 26 October 2026), pulling only the needed members by HTTP byte range.
- **Connecticut and Illinois:** their servers omit the intermediate certificate, so the state researcher fetched each public intermediate from its CA's published address, checked it against the trusted root bundle, and passed it to `curl --cacert`. Verification stayed on.
- **US Code currency:** `uscode.house.gov` section pages returned 404 to every URL form, so the federal researcher read the US Code 2024 edition at govinfo.gov and checked later amendments against the Office of the Law Revision Counsel's classification tables (Pub. L. 119-1 to 119-136, current to 22 October 2026).
- **EU currency:** the EU researcher queried the Publications Office's SPARQL index for acts amending each instrument, consolidated versions, and 2025–2026 acts and proposals.

### 3.2 Routes tested at the start

| Host | Result on 1 November 2026 |
|---|---|
| developer.apple.com | Readable (curl and WebFetch); documentation pages through their DocC JSON data files |
| support.google.com (Play Console Help) | Readable (curl and WebFetch) |
| developer.android.com | Sign-in redirect loop for plain curl; readable with an anonymous cookie jar |
| legislation.gov.uk | Readable, including exact `data.xml` |
| govinfo.gov | Readable (US Code 2024 edition, public laws, Federal Register, court opinions) |
| www.ecfr.gov | HTML redirects to a bot challenge; the API is readable with `curl --compressed` |
| ftc.gov | WebFetch only; curl gets 404 |
| missingkids.org | Readable |
| publications.europa.eu | Readable (the Official Journal texts that EUR-Lex shows) |
| digital-strategy.ec.europa.eu | WebFetch readable |
| eur-lex.europa.eu | Empty HTTP 202 (bot challenge) to curl and WebFetch |
| ofcom.org.uk, ico.org.uk | HTTP 403 to curl and WebFetch |
| leginfo.legislature.ca.gov | HTTP 403 to curl and WebFetch |
| congress.gov | HTTP 403 |
| uscode.house.gov | HTTP 404 to every section URL form |

### 3.3 How the rows were checked and merged

- **Independent re-reads.** This session re-read, by its own fetches, the key clause of all 31 rows tagged child safety (T4), of 56 of the 85 no-owner rows, and of at least one row in every family (section 7). Every clause re-read matched its row. The 29 no-owner rows not re-read here rest on their researcher's verbatim extraction [counts corrected by the manager: UK-14 was re-read in `1eefca1`, section 7]: AP-19 (secondary only); GP-15, GP-56, GP-57; UST-05, UST-06, UST-07, UST-09, UST-10, UST-11, UST-13, UST-18, UST-19, UST-21, UST-35 to UST-39; UK-35, UK-37, UK-39, UK-40; EU-03, EU-25, EU-40, EU-52, EU-63, EU-64. The brief's review plan has the manager re-read every no-owner row.
- **Owner and current state.** This session filled the owner and current-state columns itself, from the repository at `f40f1d7` (D5): PF01 §§1, 4, 6–8, 10–11; the owner-direction register; the P06.2 brief; the P11 plan (`docs/testing/p11-deferred-acceptance.md`); M05's §7.1 (for P07.1 to P09.3); `docs/architecture/` (onboarding, profiles and preferences, private media, media provider mapping, interactions, production contracts, data model, privacy and safety rules); ADR 0003; `apps/mobile/app.config.ts`, `apps/mobile/AGENTS.md` and `apps/mobile/package.json`; `apps/mobile/src/app/`, `src/interactions/` and `src/chat/` (for which block, unmatch and report controls exist); `services/api/glow_persistence/models.py` (location and place fields). No application command was run. A fixture behaviour is never counted as an obligation met.
- **Conflicts resolved from primary text:**
  - **UK s.66's commencement:** the XML annotations show s.66(1)–(2) in force on 7 April 2026 by S.I. 2026/262; an earlier commencement, S.I. 2025/371, was revoked by S.I. 2025/1062.
  - **Texas SB 2420:** the store pages say it is in force; the court orders were read directly (the Fifth Circuit's stay of 4 June 2026; the Supreme Court's refusal to vacate it on 6 July 2026).
  - **Utah and Louisiana:** Apple's news of 24 February 2026 gives 6 May 2026 and 1 July 2026 for Apple sharing age categories; the state laws read set developer duties from 6 May 2027 (Utah, as amended in 2026) and 1 July 2027 (Louisiana's Act 185, which keeps the 2025 Act 481 from taking effect). Both are kept, with sources, and flagged in maintenance.
  - **The EU's interim derogation:** secondary sources disagreed on whether the 2026 act extended Regulation 2021/1232 or replaced it; the Official Journal text of Regulation (EU) 2026/1881 (recital 12) says 2021/1232 "has expired" and the new act applies until 3 April 2028.
- **Normalisation:** the researchers' IDs are kept; quotations are trimmed to the clause that shows the trigger; a row resting on a secondary source, or the part of a row that does, says UNCONFIRMED; no row rests on memory.

## 4. Sources read (all on 1 November 2026)

Each matrix row cites the exact URL it rests on. This list groups every source read, by family. "(WF)" marks a page read only through WebFetch.

### Apple (developer.apple.com)

- App Review Guidelines, "Last Updated: October 16, 2026": `/app-store/review/guidelines/`.
- Apple Developer Program License Agreement (web copy; Schedule 1 updated 29 October 2026; Schedules 2 and 3, 13 October 2026; Exhibits, 27 August 2026): `/support/terms/apple-developer-program-license-agreement/`.
- Developer News: the RSS feed `/news/rss/news.rss` (147 items, 4 November 2024 to 29 October 2026), the news index `/news/`, `/news/upcoming-requirements/`, and the items `?id=` 92th7e5i, vvzx6cul (16 Oct 2026), a233fmpw, 0d2gpmml (8 Jun 2026), d75yllv4 (6 Feb 2026), ey6d8onl (13 Nov 2025), 9txfddzf (1 May 2025), r9dcmrvs, 76371du6, btkirlj8 (8 Oct 2025), 2ezb6jhj (4 Nov 2025), 8jzbigf4 (23 Dec 2025), sg176nne (3 Jun 2026), f5zj08ey (24 Feb 2026), ks775ehf (24 Jul 2025), tlur8uvi (9 Jul 2026), k1mtkt1k (9 Sep 2026), einwn76m, 6agg0lja, idsft9ai (16 Sep 2026), j9zukcr6, gmws0jgp (18 Aug 2026), av1nevon.
- App Review Help: 5.1.1(v) account deletion (the former `/support/offering-account-deletion-in-your-app/` redirects there), 5.1.1(ii) purpose strings, "Provide information for a complete review", app removals, report an app, App Store improvements.
- App Store Connect Help: age ratings values and definitions; set an app age rating; DSA trader requirements; manage app privacy; app privacy reference; app information; platform version information; Digital Goods and Services questionnaire; custom licence agreement; auto-renewable subscription information; availability; export compliance; set your developer name; submit an app.
- App Store and Support pages: app privacy details; user privacy and data use; auto-renewable subscriptions; categories; the age assurance Q&A (`/support/age-assurance`); kids; third-party SDK requirements; distributing dating apps in the Netherlands; the policy paper "Helping Protect Kids Online" (February 2025, background).
- Documentation (DocC JSON): Declared Age Range and its pages; privacy manifest files and required-reason APIs; the Info.plist keys for camera, photo library, location and tracking; requesting access to protected resources; asking permission to use notifications; PhotoKit's privacy page; StoreKit External Purchase; TN3194; Human Interface Guidelines, managing accounts.
- Secondary leads only: Kelley Drye on California AB 1043; 9to5Mac on iOS 26.4 in the UK.

### Google Play (support.google.com/googleplay/android-developer, play.google, developer.android.com)

- Developer Policy Center index and the Developer Program Policy print view ("effective October 29, 2026, unless otherwise stated", answer 18265346); the policy announcement of 29 October 2026 (18100766); Policy Deadlines (table 12921780); announcements of 30 October 2025, 19 November 2025 and 9 December 2025 (16550159, 16706838, 16671517); the Policy Archive index (13386702).
- Child safety: Child Safety Standards (14747720); Child Endangerment (9878809); Google's page on reporting child sexual abuse imagery (support.google.com/websearch/answer/148666).
- Content and audience: Inappropriate Content (9878810); User Generated Content (9876937) and its moderation article (12923286); Age-Restricted Content and Functionality (16302250); incidental dating features (16838200); target audience and content settings (9867159); US state app-store bills (16569691); Families (9893335); Content Ratings (9898843) and content-rating requirements (9859655).
- Play Age Signals (developer.android.com/google/play/age-signals/): overview, use, request, responses, significant changes, release notes.
- Privacy and deletion: User Data (10144311); Data safety (10787469); prominent disclosure (11150561); account deletion (13327111).
- Review and accounts: sign-in details (15748846); prepare your app for review (9859455); Play Console requirements (10788890); target API level (11926878); trader status declaration (17594752); developer verification (support.google.com/android-developer-console/answer/16561738; developer.android.com/developer-verification and its guides; developer.android.com/distribute/play-policies); app testing for new personal accounts (14151465); account types (13634885); identity verification (10841920); Japan developer verification (support.google.com/paymentscenter/answer/17595997).
- Permissions: Permissions and APIs that access sensitive information (16558241); minimum-scope alternatives (16935362); preview of the permissions policy (16909972); location button (17033915); background location (9799150); Android pages on notification permission, runtime permissions and the photo picker.
- Payments: Payments (9858738) and its FAQ (10281818); program topic indexes (16470499, 16471708); US alternative billing (16497028); US external content links (16470497); billing choice program (17161464); Japan external payments (16787536); Subscriptions (9900533) and its preview (18204939).
- Other policies: Spam (9899034); Functionality (9898783); Deceptive Behavior (17006354); Device and Network Abuse (16559646); categories (9859673); country requirements (6223646); EEA general conditions (14659200); financial features declaration (13849271); health apps declaration (14738291); advertising ID (6048248); technical quality requirements (17492799); 16 KB page sizes and Restore Credentials (developer.android.com).
- The Developer Distribution Agreement (play.google/developer-distribution-agreement.html, effective 15 September 2025).

### US federal

- US Code 2024 edition at govinfo.gov: 18 U.S.C. 2258A to 2258E, 2252A, 2256, 2510, 2702, 2703, 2711; 15 U.S.C. 45, 6501–6506, 6851, 8401–8405, 9901; 47 U.S.C. 230; 8 U.S.C. 1375a; 34 U.S.C. 20916–20917.
- Public laws at govinfo.gov: Pub. L. 118-59 (REPORT Act), 119-12 (TAKE IT DOWN Act), 119-60 §8202(i), 119-129 (Romance Scam Prevention Act); the metadata of every law 119-1 to 119-136; bill-status files for H.R. 2481, S. 841, S. 1748, S. 836, S. 1586, H.R. 3149, S. 737, H.R. 1623, S. 1829, H.R. 7757, H.R. 8413 and (118th) H.R. 8818.
- OLRC classification tables (uscode.house.gov/classification/tables.html and the 119th Congress tables).
- eCFR API (as of 29 October 2026): 16 CFR parts 312, 425, 318 and 14, sections 310.2 and 1.98, the parts structure and version histories; 28 CFR part 202.
- Federal Register at govinfo: 2025-05904 (COPPA dates), 2026-02866 (Negative Option Rule restored), 2026-04952 (advance notice), 2021-24094 (negative-option policy statement); Federal Register API searches for FTC documents.
- Court: Custom Communications v. FTC (8th Cir., 8 July 2025), ecf.ca8.uscourts.gov.
- NCMEC: the CyberTipline page and data page; the 2025 CyberTipline report; the REPORT Act guidelines PDF; report.cybertip.org and its FAQs; the CyberTipline API documentation.
- FTC (WF): the COPPA FAQ; the COPPA age-verification policy statement (PDF; its text extracted exactly with `pdftotext`) and its press release; "Complying With the Take It Down Act"; the 19 May 2026 blog post; the privacy and security pages; "Marketing Your Mobile App"; the X-Mode press release (context only).

### US states

- Texas (tcss.legis.texas.gov; capitol.texas.gov): Bus. & Com. Code chapters 106, 541 and 509; SB 2420 enrolled.
- Courts: CCIA v. Paxton (W.D. Tex.) preliminary injunction and stay denial (govinfo); the Fifth Circuit's stay order of 4 June 2026 (ca5.uscourts.gov); the Supreme Court's order of 6 July 2026, the docket and filings in 25A1390 (supremecourt.gov); NetChoice v. Reyes preliminary injunction (D. Utah, govinfo).
- New Jersey: P.L.2007, c.272 (pub.njleg.gov); the Attorney General's Bumble release of 21 February 2024 (njoag.gov).
- Illinois (ilga.gov): 815 ILCS 518, 815 ILCS 615, 740 ILCS 14, P.A. 97-1056.
- New York: GBL §394-cc and §1500 (nysenate.gov, WF); A428 (2025) and A1057 (2023) texts and actions (nyassembly.gov); S1759B (legislation.nysenate.gov); the Department of State alert of 11 February 2025 (WF); the Attorney General's SAFE for Kids release of 28 July 2026.
- Connecticut (cga.ct.gov): chapter 420l, its 2026 supplement, P.A. 22-82.
- Utah (le.utah.gov): chapters 13-67, 13-76 and 13-71.
- Vermont (legislature.vermont.gov): 9 V.S.A. §§2482a–2482d.
- Arizona (azleg.gov): A.R.S. 44-7151 to 44-7157; Laws 2021 ch.110.
- Colorado: C.R.S. title 6 (2024 printout, content.leg.colorado.gov); SB 24-011 session law; the Attorney General's dating-safety page and rules 4 CCR 904-5 (coag.gov).
- California: the Legislature's bulk data (members named in the rows; bill and history tables); the CPPA's threshold adjustment, rulemaking page and regulations effective 1 January 2026 (cppa.ca.gov); the Attorney General's SB 976 page (oag.ca.gov).
- Louisiana (legis.la.gov): Act 185 (HB 977, 2026), HB 570 (2025) enrolled and digest, HB 977 status.
- Alabama: HB 161 enrolled (alison.legislature.state.al.us); the Alabama Reporter (secondary, for enactment).
- Virginia (law.lis.virginia.gov): §§59.1-575 to -580, 59.1-577.1, 59.1-207.46.
- Florida: Fla. Stat. §501.1736 (leg.state.fl.us).

### UK

- legislation.gov.uk (`data.xml`): Online Safety Act 2023 ss.3–13, 20, 20A, 21–23, 35–37, 41, 43, 46, 49–51, 54, 55, 59, 61, 62, 64, 66–72, 77, 83–86, 94, 95, 121, 192, 204, 214A, 226, 227, 230–232, 236, 240, Schedules 1, 3, 4, 6, 7 and 11, its contents, the whole Act and its changes feed; S.I. 2023/1420, 2026/262, 2026/268, 2025/226, 2025/747, 2025/1032, 2025/1204, 2025/1352 (and the titles of revoked 2025/368 and 2025/1066); the Crime and Policing Act 2026 ss.77, 85, 100, 101, 103, 104, 106, 107 and Schedule 14, with commencement S.I. 2026/689, 939, 960, 1090, 1111 and S.I. 2026/1107; Sexual Offences Act 2003 ss.66A, 66B, 66E, 66F; UK GDPR Arts 3, 5–9, 8ZA, 12, 12A, 13–15, 17, 20, 21, 22A–22C, 25, 27, 28, 30, 32–35, 37, 44A, 46, 77 and Annex 1; DPA 2018 ss.9, 10, 123, 127, 137, 164A, 164B, 165 and Schedule 1; Data (Use and Access) Act 2025 commencement S.I. 2026/82 and 2026/1015; PECR reg 6 and Schedule A1; S.I. 2018/480; DMCC Act 2024 ss.225, 226, 253–256, 258, 260, 264, 275, 339 with S.I. 2025/272, 2026/284, 2026/1040; the Consumer Contracts Regulations 2013 regs 29, 30, 36, 37.
- gov.uk: the Online Safety Act explainer; the illegal content codes' explanatory memorandum and the code as laid (PDF); the June 2026 draft amendments and memoranda; Amendments No. 2 (18 June 2026); the Protection of Children Code as laid and its memorandum; the Online Fraud Charter 2023; the CMA's online dating guidance.
- National Crime Agency: the CSEA industry reporting portal page; "The Online Safety Act and the Role of the NCA" (v1.0, 7 April 2026); the registration guide (v1.0, 7 April 2026).

### EU

- EU Publications Office (`http://publications.europa.eu/resource/celex/…`): the DSA (32022R2065); the GDPR consolidated 04.05.2016 (02016R0679-20160504) and original (32016R0679); the ePrivacy Directive consolidated 19.12.2009 (02002L0058-20091219); Regulation (EU) 2026/1881, 2021/1232 and 2024/1307; the Commission's Art 28 guidelines C/2025/5519 (52025XC05519); Recommendation (EU) 2026/1035 (32026H1035); the Data Privacy Framework decision 2023/1795, the T-553/23 judgment notice, the C-703/25 P appeal notice and COM(2024) 451; the SCC decision 2021/914; the Consumer Rights Directive consolidated 27.09.2026 (02011L0083-20260927) and Directive 2023/2673; the Digital Content Directive 2019/770; the European Accessibility Act 2019/882; Recommendation 2003/361/EC; the EECC 2018/1972; Directive 2011/93/EU (consolidated and original); Directive 2024/1385; the AI Act consolidated 27.07.2026, the original, and Regulation 2026/1744; NIS2 2022/2555; the Geo-blocking Regulation 2018/302; the e-Commerce Directive 2000/31/EC; CJEU judgments C-184/20, C-252/21 and joined C-188/24 and C-190/24; the EU KIDS Act proposal COM(2026) 681.
- The Parliament's Legislative Observatory, 2022/0155(COD).
- EDPB: Guidelines 3/2018 (v2.1), 9/2022 (v2.0), 2/2023 (v2.0), 05/2021 (v2.0); Statement 1/2025 on age assurance.
- Commission pages (WF): EU age verification (updated 22 September 2026) and its FAQ (18 May 2026); the DSA questions and answers (19 December 2025); EU-US data transfers.
- The Publications Office SPARQL endpoint (amendment and title queries).

### This session's own reads

developer.apple.com (the guidelines, the news index, the age assurance Q&A, the trader-status help, the developer-name help, the deletion help); support.google.com (the child-safety, child-endangerment, age-restricted, trader, testing, deletion, user-generated-content, technical-quality and US-state pages); govinfo.gov (18 U.S.C. 2258A and 2258B, 2703, 47 U.S.C. 230, Pub. L. 119-12 and 119-129); missingkids.org (the CyberTipline page and the REPORT Act guidelines); the eCFR API (16 CFR 312); legislation.gov.uk (OSA ss.9, 10, 23, 35–37, 66, 69, 230, Schedules 4 and 7, S.I. 2026/268 and 2026/1107; UK GDPR Art 27; S.I. 2018/480 regs 1–3; DPA 2018 s.137); gov.uk (the illegal content codes as laid); tcss.legis.texas.gov (chapter 106); pub.njleg.gov (P.L.2007, c.272); le.utah.gov (chapters 13-67 and 13-76); legislature.vermont.gov (§2482b); azleg.gov (§44-7157); legis.la.gov (Act 185); ca5.uscourts.gov and supremecourt.gov (the SB 2420 orders); content.leg.colorado.gov (SB 24-011); the California bulk data (AB 1394's sections, by byte range); the EU Publications Office (the DSA, the GDPR, Regulation 2026/1881, the Art 28 guidelines, Directive 2023/2673, the ePrivacy Directive, Directives 2011/93/EU and 2024/1385, Recommendation 2026/1035); the Legislative Observatory; the FTC's age-verification statement (through WebFetch's saved PDF, text extracted with `pdftotext`); and, as leads only, two web searches (on Regulation 2021/1232's extension and on Apple's Texas guidance).

## 5. Sources not read

| Source | Reason |
|---|---|
| ofcom.org.uk: every page, including the illegal-harms statement, the codes PDFs (including the consolidated code of 9 September 2026), the Risk Assessment Guidance and Risk Profiles, the children's access assessment guidance, the highly effective age assurance guidance, the illegal content judgements guidance, the record-keeping guidance, the Regulations Checker, the s.54 guidance, fees statements and any exemptions | HTTP 403 (Cloudflare challenge) to curl and WebFetch. The codes were read from the copies laid before Parliament (gov.uk); any later amendment is unread |
| ico.org.uk: every page, including the data protection fee page, the Age Appropriate Design Code PDF, the "likely to be accessed" guidance, the DPIA list, and representative and DPO guidance | HTTP 403 to curl and WebFetch |
| questions-statements.parliament.uk (HLWS72, 1 June 2026) | HTTP 403 |
| www-bau.drcf.org.uk copy of an Ofcom PDF | Not used: provenance could not be verified |
| eur-lex.europa.eu | Empty HTTP 202 (bot challenge); the same texts were read from the EU Publications Office |
| consilium.europa.eu: press releases of 23 July 2026 and 26 November 2025, and the CSA timeline | HTTP 403. A search snippet attributing a Council mandate on the CSA Regulation to 26 November 2025 is UNCONFIRMED and not relied on |
| curia.europa.eu (C-703/25 case list) | A JavaScript application; no text extractable |
| uscode.house.gov section pages and download page | HTTP 404 for every URL form; govinfo and the OLRC tables were used |
| congress.gov (H.R. 2481, the TAKE IT DOWN Act's page) | HTTP 403; govinfo bill-status files were used |
| www.ecfr.gov HTML | Redirects to a bot challenge; the eCFR API was used |
| ftc.gov by curl (all pages) | HTTP 404 to curl; read by WebFetch instead |
| An FTC 2022 sensitive-data blog post (and an alternative address) | HTTP 404 |
| media.ca8.uscourts.gov copy of the 8th Circuit opinion | TLS name mismatch, not bypassed; the ecf host's copy was read |
| An archived 2017 NCMEC page (webarchive.library.unt.edu) | TLS verification failure, not bypassed |
| esp.ncmec.org/registration (NCMEC's provider portal) | JavaScript only; only its title was readable. Never submitted |
| leginfo.legislature.ca.gov (all pages) | HTTP 403; the Legislature's official bulk data was used |
| nysenate.gov law pages and dos.ny.gov by curl | HTTP 403 to curl; read by WebFetch (wording may be paraphrased) |
| The New York SAFE for Kids rule text | Not read; the Attorney General's release was |
| The current New Jersey code (N.J.S.A. 56:8-168 et seq.) and the Division's internet-dating regulations | Not read; the 2007 chapter law and the 2024 release were |
| Colorado's 2025 and 2026 code updates (a 2025 title 6 PDF returned 404) | The 2024 printout and the Attorney General's page were used |
| Connecticut's 2026 session acts | Not checked |
| Alabama's bill status and act number (the ALISON site is JavaScript only) | Enactment rests on a secondary source (UNCONFIRMED) |
| The Fifth Circuit's merits decision on SB 2420; the Tenth Circuit's decision in NetChoice v. Reyes; NetChoice v. Bonta (SB 976) | Not found or not checked |
| A September 2026 New Jersey settlement with Match Group; Louisiana Act 456's reported injunction | Secondary reports only; not relied on |
| Michigan and Florida dating-disclosure laws | No enacted statute found (bill analyses and old bills only) |
| Other states' social-media age-verification laws (Georgia, Tennessee, Mississippi, Arkansas, Ohio, Nebraska); other states' automatic-renewal laws; the Washington My Health My Data Act; state age-appropriate design codes; other states' platform CSAM or intimate-image laws | Not researched (outside the scope set for the session) |
| Play Console pages behind sign-in (the IARC questionnaire, App content forms, the Age signals page, Restrict Minor Access, the child-safety and precise-location declarations) | Signing in is prohibited for this session |
| Google's Policy Archive PDFs; the user-facing "Age range sharing" page; the Age Signals test and error pages; EEA external offers and alternative billing pages (downloaded, not reviewed) | Not needed for any row, or not read |
| Apple's wider EU terms (communication of offers in the EU; the DMA page; the 18 August 2026 changes page) | Outside the brief's scope for Apple's EU payment terms |
| Apple's Sensitive Content Analysis documentation, HIG Privacy, the minimum EULA terms; Apple Developer Forums threads; news items for Australia, Korea, Vietnam, Brazil and medical devices | Not needed, or user posts rather than Apple policy |
| Apple guidance on California AB 1043 or UK age assurance | None exists on developer.apple.com (searched) |
| EU texts not read: the DMA's definitions, Rome I, the Unfair Commercial Practices and Unfair Terms Directives, the AVMSD, Regulation (EU) 2025/2518, the consolidated EECC of 18.10.2024, the DSA transparency-report implementing act, the 2026/1881 report-form implementing act, EDPB Guidelines 8/2022 and WP243, and the pending proposals other than the EU KIDS Act (titles only) | Not needed for any row, or not reached |

## 6. Limits, and the rows flagged UNCONFIRMED

**What the matrix does not establish** (also its header): it is research with dated sources, not legal advice; it states each source's conditions but does not decide whether Glow meets them; it does not survey every law of the 79 legal systems involved; it does not establish store approval; it sets no cost and designs no feature. Whether to take legal advice is Nathan's.

**Rows, or parts of rows, marked UNCONFIRMED:**

- **AP-19:** California AB 1043's date from a secondary source (Apple has published no guidance); the statute itself is UST-35.
- **AP-20:** Apple's UK account-level 18+ confirmation (press reports only).
- **UST-36:** Alabama HB 161's enactment (enrolled text read; signature from a secondary source).
- **GP-11:** the original compliance date of Google's age-restricted policy (the announcement says only "at least 30 days").
- **GP-16:** Utah, Louisiana and California are not named on Google's page read today (secondary sources only).
- **GP-23:** the original child-safety declaration deadline (a search summary only; the page read has no timeline).
- **UK-05:** whether s.51's "first code" rule delays the 48-hour intimate-image duty.
- **UK-11, UK-20:** that Ofcom's codes are unchanged since they were issued (later amendments on ofcom.org.uk unread).
- **UK-14:** the month the Protection of Children Code came into force (a June 2026 memorandum gives two months).
- **UK-35:** the Age Appropriate Design Code's content and the ICO's test (unread).
- **UK-40:** the DPO threshold ("large scale" undefined in the text; ICO guidance unread).
- **UK-44:** whether a controller not established in the UK must pay the fee.
- **UK-46:** whether Glow or the store is the "trader" for in-app purchases (also EU-55).
- **UST-40:** the Tenth Circuit's outcome on Utah's enjoined act.
- **USF-02:** that `esp.ncmec.org/registration` is the registration route (the statute and NCMEC's guidance were read).
- **EU-28, EU-49:** the Council's and the Court of Justice's own pages were unreadable; the status rests on the Legislative Observatory and the Official Journal.

**Quotes read only through WebFetch** (wording may be paraphrased): the FTC pages (USF-08's guidance, USF-11's FAQ, USF-13's guidance), UST-07 (New York GBL §394-cc), UST-38's definition (GBL §1500), the New York Department of State's date in UST-08, and the Commission's age-verification and DSA pages.

**Method limits:**

- Text extraction from HTML can add spaces at link boundaries; quotes were normalised for those spaces only.
- Consolidated texts carry their own currency dates (legislation.gov.uk: revised to 30 September 2026 for most UK texts; the US Code 2024 edition with tables to 22 October 2026; EU consolidations as dated in section 4); a change after those dates may be missing.
- Where an application to Glow is an inference from the stated facts (the DSA classification, C-184/20's "indirectly", California's "social media platform", the NI-ICS question), the row says so.
- The current-state column reads records and code only (D5); no application command, native build or provider call was run.

## 7. Verification by this session

Each check below fetched the source afresh, extracted its text, and searched for the row's quoted clause. Every one matched.

| Rows | Source re-read | Clause checked |
|---|---|---|
| AP-01, AP-05, AP-36, AP-57 | App Review Guidelines (curl) | 4.3(b) "dating … fortune telling"; 1.2's four safeguards; 4.8 and its own-sign-in exception; 5.1.1(ix) legal entity; "Last Updated: October 16, 2026" |
| AP-21 | App Review Guidelines §5 introduction | "…appropriate authorities will be notified and the apps will be removed…" |
| AP-14 | Age assurance Q&A | "In regions where legally required…"; "developers are responsible for their own age restrictions" |
| AP-15, AP-16, AP-62 | Developer News index | the Texas update of 3 June 2026; the 24 February 2026 Utah and Louisiana item; guideline revisions of 16 October, 8 June and 6 February 2026 |
| AP-32, AP-33 | Account deletion help | "Offer to delete the entire account record, along with associated personal data." |
| AP-56, AP-65 | ASC Help: DSA trader; developer name | "Even if you don’t distribute apps in the EU…"; "You must assess whether you're a trader…"; "You can set your developer name only when adding an app…" |
| GP-18 to GP-22 | Child Safety Standards help page (curl) | scope "Social and Dating categories"; the five requirements; actual-knowledge removal; the named point of contact |
| GP-21, GP-23 | Child Endangerment policy | "…report confirmed CSAM to the National Center for Missing and Exploited Children or your relevant regional authority"; "social and dating apps must follow the Child Safety Standards policy" |
| GP-05, GP-06 | User Generated Content policy | the full moderation list, including 1:1 blocking |
| GP-11 | Age-Restricted Content and Functionality | "required to use the Play Console functionality and tools to block minors"; "core functionality is to facilitate matchmaking or dating" |
| GP-33, GP-34 | Account deletion requirements | in-app request and web link; retention for legitimate reasons |
| GP-36, GP-16, GP-58, GP-59 | Technical quality; US state bills; testing; trader status | zero-tap restoration; SB 2420 "now in effect"; 12 testers for 14 days; "completed by February 1, 2027" |
| USF-01 to USF-04, USF-06, USF-07 | 18 U.S.C. 2258A (govinfo 2024 edition) | (a)(1)(A) actual knowledge; (a)(1)(B)(i) contact details; (b) "sole discretion"; (e) fines; (f) no duty to monitor; (g)(4); (h) one-year preservation; Pub. L. 118-59 included |
| USF-02 | NCMEC REPORT Act guidelines (PDF) | "contact ESPteam@ncmec.org to learn more about registering" |
| USF-05 | 18 U.S.C. 2258B | "minimize the number of employees…" |
| USF-08 to USF-10 | Pub. L. 119-12 | the covered-platform definition and exclusions; the one-year deadline; the 48-hour removal; the notice; FTC enforcement |
| USF-12, USF-15 | 47 U.S.C. 230; 18 U.S.C. 2703 | the parental-control notice; preservation on request |
| USF-18, USF-19 | Pub. L. 119-129 | the fraud-ban duty; 24 hours; effective one year after enactment; approved 20 October 2026 |
| USF-11 | eCFR API, 16 CFR 312 | the part as of 29 October 2026 |
| UST-01, UST-02 | Tex. Bus. & Com. Code ch.106 | §106.006 notice; §106.004 disclosure |
| UST-03, UST-04 | New Jersey P.L.2007, c.272 | the safety notification; the two-form disclosure |
| UST-12, UST-14 | Utah Code ch.13-67 (PDF) | the pre-communication disclosure; the fraud-ban notice |
| UST-15 | 9 V.S.A. §2482b | the fraud-ban disclosure |
| UST-17 | A.R.S. §44-7157 | the fraud-ban notice |
| UST-33 | Utah Code ch.13-76 (PDF) | "Beginning May 6, 2027, a developer shall" |
| UST-34 | Louisiana Act 185 (PDF) | "Act No. 481 of the 2025 Regular Session shall not become effective"; effective 1 July 2027 |
| UST-20 | Colorado SB 24-011 | the one-year clock |
| UST-32 | Fifth Circuit order; Supreme Court order | "…preliminary injunctions pending appeal is GRANTED" (filed 4 June 2026); "The application to vacate stay … is denied" (6 July 2026) |
| UST-49 | California bulk data, `LAW_SECTION_TBL_25872`–`25874` (by byte range) | the reporting mechanism; 36 hours; seven days; 30 days |
| UK-03, UK-10 | OSA ss.9, 23 | the risk-assessment and record duties |
| UK-05 | OSA s.10 | "…no later than 48 hours, after the provider receives the report"; inserted 29 June 2026 |
| UK-12, UK-13 | OSA ss.35, 36, 230 | s.35(2); s.36 in force 10 January 2024; s.230(4) self-declaration |
| UK-14 | OSA s.7 | s.7(4): services likely to be accessed by children must comply with ss.11 and 12 |
| UK-15 | OSA s.66 | s.66(1)–(2); in force 7 April 2026 by S.I. 2026/262 |
| UK-16 to UK-18 | S.I. 2026/268 | registration before the first report; priority 1 "immediately"; five-year reference retention |
| UK-19, UK-21 | OSA s.69; Schedule 7 | false information; para 28A |
| UK-20, UK-11 | Ofcom code as laid (gov.uk); Schedule 4 | the 700,000-user threshold; the accountable individual; no recommendation to analyse private content |
| UK-23 | S.I. 2026/1107 | the trusted-flagger designation |
| UK-27, UK-44 | UK GDPR Art 27; S.I. 2018/480 regs 1–3; DPA 2018 s.137 | the representative; the £52, £78 and £3,763 tiers; the controller definition |
| EU-02, EU-08, EU-11, EU-13, EU-18, EU-19, EU-29 | DSA (Publications Office) | Art 3(i), (k), recital 14; Art 15(2); Art 18; Art 19; Art 24; Art 8 |
| EU-04 to EU-06, EU-09, EU-10 | DSA Arts 11–13, 16, 17 | the opening duty of each |
| EU-24 | Commission guidelines C/2025/5519 | Art 28 does not apply to micro or small platforms; self-declaration not appropriate |
| EU-26, EU-27 | Regulation (EU) 2026/1881 | Arts 1, 3 and 11; recitals 11–12 (2021/1232 expired) |
| EU-28 | Legislative Observatory | "Awaiting Parliament's position in 1st reading" |
| EU-30, EU-31, EU-32 | ePrivacy Directive; Directive 2011/93/EU; Directive 2024/1385 | Art 5(1); Art 25; Art 23(2) |
| EU-34, EU-36, EU-43, EU-46, EU-47 | GDPR | Arts 27, 9(1), 30(5), 35(3)(b), 37(1)(c) |
| EU-58 | Directive (EU) 2023/2673 | "They shall apply those measures from 19 June 2026" |
| Section 9 (A05) | Recommendation (EU) 2026/1035; the FTC age-verification statement | "…by 31 December 2026, an EU age verification solution"; "will not bring an enforcement action under the COPPA Rule…"; "does not create any substantive rights or entitlements" |

## 8. Outputs and checks

- **Written:** `docs/planning/store-legal-safety-requirements.md` (the matrix) and this record. Nothing else in the repository was written; downloads, extracts and scripts stayed in the session's scratchpad.
- **Structure check** (a script over the matrix): 320 requirement rows, every row with eight non-empty cells, every source cell with a URL and "read 2026-11-01", no duplicate IDs, every contents link resolving to a heading.
- **Classification:** the change is two Markdown files outside any `.claude/` directory. This session did not run the classifier (D5: no repository command); the brief's acceptance check has the manager run the trusted classifier.
- **Not done, by rule:** no pull request, comment, review, re-run, workflow dispatch or setting on GitHub; nothing in Notion; no account, form, purchase, message, provider call or database connection.

## Manager verification (1 November 2026, App Manager 8)

- **The branch:** `claude/stoic-pasteur-r24pz8`, head `1eefca1`, two commits on `f40f1d7` (`86688d1`, `1eefca1`), integrated into the manager branch by fast-forward.
  - Its two paths are new regular Markdown files (mode `100644`), the brief's two outputs, and nothing else.
  - The trusted policy from `main` classified `f40f1d7..1eefca1` as `ordinary-docs-only`, and `git diff --check` printed nothing.
- **The matrix's structure,** parsed by the manager: 320 rows, each with eight cells and a unique ID; every source cell names a URL and a read date; 85 rows with no owner and 31 tagged T4, by family as the summary says.
- **The live re-read** (the brief's review plan). The sample was every T4 row, every no-owner row and one owned row per family: 108 rows and 115 source URLs. The manager fetched each row's cited sources from `Glow App - No Stream` and checked each quoted fragment (25 or more letters and digits, case and punctuation ignored) against the source's text.
  - **Confirmed, 104 of 108:** 97 by that check; UST-08 once the bill's line numbers were removed; UST-07 by WebFetch (the New York Senate's site refuses `curl`, as the session found); UST-21, UST-37, UST-39 and UST-49 from the Legislature's bulk data, read by byte range (members `LAW_SECTION_TBL_24819`, `85913`, `85309` with `45355`, and `25872` to `25876`); UST-35 from AB 1856's chaptered text (below).
  - **Every T4 row is confirmed (31 of 31), and 81 of the 85 no-owner rows.** The other four: AP-19, UST-36 and UK-35 carry no quote and are already marked UNCONFIRMED; GP-56 is corrected below.
  - **Connecticut and Illinois** serve incomplete certificate chains. The manager added their issuers' intermediates (GoDaddy's G2, from `certificates.godaddy.com`; Sectigo's OV R40, from `crt.sh`) to the proxy's CA bundle and fetched with verification on.
- **Corrections, marked in the files:**
  - **GP-56:** its quote was not Google's wording. The developer verification guides page says *"…we will expand these protections globally for all apps on certified Android devices in 2027."* The row's substance (global in 2027) stands.
  - **UST-35:** the quoted words are AB 1856's amendment (chaptered 10 September 2026, Stats. 2026, ch. 184). The bulk data's code table still shows AB 1043's "when the application is downloaded and launched". A precision was added to the source cell; the requirement stands.
  - **This record, section 3.3:** UK-14 was re-read in `1eefca1`, so the counts read 56 and 29, and UK-14 left the list of rows not re-read.
- **The current-state column,** checked against the cited files at `f40f1d7`: AP-21 (M05 E6), GP-18 (PF01 §7: "Draft real public community/child-safety/support policies"), GP-19 (contract F14: "After-unmatch reporting allowed"), GP-20 (PF01's P07 operations: "moderation, child-safety and support responsibilities"), USF-03 (`SafetyReport` and `ModerationCase` in the data model), USF-04 (F18; no legal or preservation hold anywhere in `docs/`) and USF-05 (the moderation projection in the privacy rules). Each says what the row says.
- **Not re-checked by the manager:** the 212 rows outside the sample; the routes the session tested; the A05 section beyond its row references; whether each row's reading of its source, or its applicability condition, is right. The check confirms that each quote is in the cited source, not the legal reading.
- **The session's early push** of its branch at `f40f1d7`, before any output, changed nothing.
- **Next:** the gaps' routing and the A05 questions go to the Dev Manager (DM-37), then the A05 questions to Nathan in OD-32's form before P07's brief.

## The records' merge receipt (1 November 2026, App Manager 8)

- **PR39 merged** at 21:02 UTC as the merge commit `bac3c1983134f4e977f867ac30b3086b5318216f`, with parents `fcd6ebc` (`main`) and `05f4c3a` (the manager branch), by the expected-head guard. `main`'s tree equals `05f4c3a`'s. It carried the matrix, this record, DM-37's routing, PF01 1.17 and M06's receipt.
- **Its checks:** the trusted policy read `ordinary-docs-only`; PR run 41349650700 passed change scope and the gate, with the application jobs skipped; Codex's review of `05f4c3a` completed with no finding.
- **The cleanup run** 41349863365 passed and deleted `claude/stoic-pasteur-r24pz8`, this session's branch. `git ls-remote` after it: `main` at `bac3c19`, the manager branch at `05f4c3a`, `claude/dev-manager` at `0db8c42`, and nothing else.
- **Left open:** Nathan's answer to the first A05 message.
