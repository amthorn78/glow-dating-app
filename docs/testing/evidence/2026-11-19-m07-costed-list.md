# M07 — The costed list of completion's accounts and services: evidence record

- **Session:** the M07 research session, started by Nathan on 19 November 2026, on branch `claude/sharp-keller-j1uvsv`.
- **Prompt:** revision 1, from commit `f1653f194efd7e5ae0e145552cf42d111ee5cc12` of `claude/magical-wozniak-yfmmx2` (`docs/ephemeral/2026-11-19-m07-costed-list-prompt.md`). **Brief:** [`docs/planning/m07-costed-list.md`](../../planning/m07-costed-list.md), revision 1.
- **What this is:** published prices and published terms, read on public pages on 19 November 2026. It decides nothing, chooses no provider and is not legal or tax advice. Nathan approves or declines each line (OD-50); a line that implies choosing a provider goes to the Dev Manager first.

## Summary for Nathan

**What it costs to reach launch, on today's published prices.**

- **One-time: about $125.** That is a Wyoming LLC's $100 filing plus Google Play's $25 registration ($135 with Delaware's $110 filing instead). The EIN and the D-U-N-S number are free. Not included: legal advice, which no firm prices publicly, and your home state's fee if the company is formed elsewhere and must register there too.
- **Yearly: about $296** with a Wyoming LLC (Apple $99, Wyoming's $60 minimum yearly tax, a registered agent at $125 and the .com domain at $11.81). With Delaware's $400 yearly tax instead: about $636.
- **Monthly, the fixed services, with the yearly items spread over twelve months:**

| | At launch (up to about 100 members) | 1,000 active members | 10,000 active members |
|---|---|---|---|
| Fixed monthly cost | **about $479** | **about $501** | **about $647** |
| Of which Stream's chat plan | $399 | $399 | $406 |
| Plus GitHub Actions, if the repository goes private | $5.20–$8.40 | $5.20–$8.40 | $5.20–$8.40 |

- **On every sale, a share of the price, not in the table:** Apple or Google take 15% on a subscription (Google's 15% is now 10% plus a 5% billing fee). Stripe takes 2.9% + 30¢ a payment, plus 0.7% for Billing and a Radar fee of $0.05 to $0.09 for each screened payment. RevenueCat, if chosen, adds 1% above $2,500 a month.
- **Stream is most of the bill.** Its Start plan is $399 a month billed yearly ($499 monthly). If Stream approves the Maker application (pending since 25 September, left open by OD-76), chat is free up to 2,000 monthly active users with hard limits, while Glow has fewer than $10,000 a month in revenue, five or fewer team members and under $100,000 in funding. That would bring the launch figure to about $80 a month.
- **These figures rest on usage I assumed, not forecast** (section "Totals"): 4 photos a member, 2 photo checks and 5 emails a member a month, 100 messages sent a member a month, and the server sizes written there.

**The lines with the longest lead times**, all set by other people:

1. **The D-U-N-S number:** free. Up to 5 business days through Apple's page, then 2 more for Apple to receive it; Dun & Bradstreet says "within 30 business days" by its own route; Google says up to 28 days. It needs the entity first.
2. **Stripe's review of a dating service:** Stripe lists "online dating and matchmaking services" as a restricted business that needs its approval; no time is published.
3. **PhotoDNA (hash matching) and NCMEC's registration:** free, by application or by email to NCMEC; no time is published for either.
4. **Stream's Maker decision:** pending 55 days; no time is published.
5. **Apple's organization enrolment:** after the D-U-N-S number and a working website on the company's own domain; Apple publishes no review time.

**The first three approvals, in the order their lead times call for:**

1. **The legal entity:** the state (Wyoming: $100 to form, $60 a year; Delaware: $110 to form, $400 a year) and a registered agent ($25 to $125 a year). The EIN follows the same day, free.
2. **The D-U-N-S number** (free), requested through Apple's page as soon as the entity exists.
3. **The domain** ($11.81 a year at Porkbun's published price; others below) and a minimal public website, because Apple's organization enrolment requires "a website that is publicly available and functional" on the organization's domain.

Then Apple ($99 a year), Google Play ($25 once) and Stripe (no fee to open), each after its matrix rows are rechecked; then NCMEC and PhotoDNA, which cost nothing and have unknown waits; then the rest, in the order the build reaches them.

## 1. Identity, start gate and environment

**Environment check (names only; no value was read, printed or used).**

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | none present |
| `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` | none present |
| `AWS_*` names | `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE`, `AWS_SECRET_ACCESS_KEY` present (set by the cloud container, OD-76); never read |
| GitHub token names | `GH_TOKEN`, `GITHUB_TOKEN` present; never read |

**Start gate.**

| Command | Result |
|---|---|
| `git switch -C claude/sharp-keller-j1uvsv f1653f1…` then `git rev-parse HEAD` | `f1653f194efd7e5ae0e145552cf42d111ee5cc12` |
| `git merge-base --is-ancestor f1653f1… origin/claude/magical-wozniak-yfmmx2` | "this prompt's commit is on the live branch" |
| `git merge-base --is-ancestor 6edae780… HEAD` | "PR54's merge present" |
| `ls docs/testing/evidence \| grep -c 'm07-'` | `0` |

The live manager branch was one commit ahead, at `d435f96`. Its diff from `f1653f1` changes only the brief's status line and session note and the handoff's waiting table (the prompt given to Nathan before DM-94's answer). Nothing in it changes this work.

**Read in full before pricing:** `AGENTS.md`, `CLAUDE.md`, the brief, "Carried to M07" and "Routed by M09" in `carried-to-later-items.md`, PF01's A04 row and §8's "The owner's track", the owner directions OD-12, OD-18, OD-19, OD-22, OD-23, OD-45, OD-50, OD-51, OD-55, OD-60, OD-62, OD-68 to OD-71, OD-75 and OD-76, M09's sections 4.3 and 5, the matrix rows AP-21, AP-42, AP-56 to AP-58, AP-65, GP-14, GP-18, GP-22, GP-23, GP-39, GP-56 to GP-60, USF-01 to USF-07, UK-44 and gaps G-02, G-08 and G-09, and the prices in the A05-V, A05-V2, A05-V3 and P06.1 records.

## 2. How the prices were read

- **Public pages only,** read on 19 November 2026 with web-fetch tools by five research sub-agents of this session, each pricing a group of lines, and checked here. No account was opened, no trial started, no form filled in, no sales team or support contacted, and no one was given Nathan's or Glow's details. No provider's API, HDE, Railway, Cloudflare or a database was called.
- **Two independent rechecks** by fresh readers, given the page and the figure but no conclusion: (1) Google Play's service-fee table and GitHub's Actions allowance, both of which differed from earlier records; (2) a sample of 15 figures across the lines. Result: 13 matched, none differed. Wyoming's fee schedule is a PDF the reader could not extract; I extracted its text myself (`pdftotext`), and it reads "Articles of Organization*/Continuance/Domestication ....$100.00" and "Annual Report License tax is $60 or two-tenths of one mill on the dollar ($.0002) whichever is greater", "Schedule Effective July 1st, 2026".
- **Limits of the reading:**
  - The web-fetch tool returns page text through a summariser. Quotations are the words it returned as page text; where a reader found the tool's summary contradicting the verbatim text, the verbatim text is used.
  - Some pages draw prices with scripts. Where a reader took a figure from the page's own public script or data attribute rather than visible text, the line says so (Stripe Radar's Plus and Pro rates; Azure's image rate; Postmark's volume tiers).
  - Three readers also fetched public pages with plain `curl` to read exact strings. No page that needed a sign-in was read.
- **"Unchanged"** means the figure an earlier record gave is on today's page as stated.

## 3. The lines

Each line gives: (1) what it is and why, the item that first needs it (PF01 1.19's order) and the direction behind it; (2) the published price; (3) its shape; (4) lead time and prerequisites; (5) who opens it and what opening it starts; (6) cheaper options. "No public price" means the price needs a sign-in, a form, a quote or a sales call, none of which was done.

### Line 1 — The US legal entity (formation, registered agent, yearly state fee)

1. **What and why:** a US legal entity holds the store accounts and the service (OD-55; AP-57; G-08). It comes first on the owner's track (M09 O2) and unblocks Apple's and Google's organization accounts, Stripe, and the policies' named operator (P07.1). Direction: OD-55, OD-75 (D-02 (a)).
2. **Published prices** (read 19 November 2026):

| | Delaware LLC | Wyoming LLC |
|---|---|---|
| Formation (state) | "Formation – domestic $110.00" ([fee schedule, revised August 1, 2026](https://corpfiles.delaware.gov/Fee_Schedule/AugustFee2026.pdf), linked from [corp.delaware.gov/fee](https://corp.delaware.gov/fee/)); 24-hour expedite $50, same day $100 | "Articles of Organization*/Continuance/Domestication ....$100.00" ([fee schedule, effective July 1st, 2026](https://sos.wyo.gov/Business/Docs/BusinessFees.pdf)); expedite next day $700, same day $1,400 |
| Yearly state fee | "the $400 yearly tax on or before June 1st" ([LLC tax instructions](https://corp.delaware.gov/alt-entitytaxinstructions/)); late: "a penalty of $200.00 plus 1.5% interest per month" | "Annual Report License tax is $60 or two-tenths of one mill on the dollar ($.0002) whichever is greater", on Wyoming assets; due "on the first day of the anniversary month of formation" ([annual report](https://wyobiz.wyo.gov/Business/AnnualReport.aspx)) |
| Registered agent | Required: "Delaware law requires that every business entity have and maintain a Registered Agent in the State of Delaware" ([how to form](https://corp.delaware.gov/howtoform/)) | Required: "All businesses, domestic or foreign, are required to continuously maintain a registered agent" ([FAQ](https://sos.wyo.gov/FAQS.aspx?root=RAO)) |
| Foreign registration, if the company is formed elsewhere | $200 | $150 (Certificate of Authority) |
| Trade-off in one line | Higher yearly cost ($400); low formation fee | Lowest yearly cost ($60 minimum); lowest formation fee |

   - A corporation instead: Delaware "*$109.00" to incorporate, then a minimum tax of $175 and a $50 annual report by 1 March ([pay taxes](https://corp.delaware.gov/paytaxes/)); Wyoming $100, then the same $60 minimum.
   - **Registered agents** (yearly): Northwest Registered Agent "$125 Per Year" ([page](https://www.northwestregisteredagent.com/registered-agent)); Harbor Compliance "$99 first year for new customers. Renews at $159 annually" ([page](https://www.harborcompliance.com/registered-agent-service)); Wyoming Agents "$25 per year TOTAL", Wyoming only ([page](https://www.wyomingagents.com/)); Registered Agents Inc. shows "$200" with no period stated (unconfirmed).
   - **EIN:** free: "You never have to pay a fee for an EIN" ([IRS](https://www.irs.gov/businesses/small-businesses-self-employed/get-an-employer-identification-number)).
   - **FinCEN beneficial ownership:** "U.S. companies are exempt from BOI reporting requirements and therefore, are no longer required to file BOI reports" ([FinCEN](https://www.fincen.gov/boi)).
   - **A third pattern:** forming in the state where Nathan lives avoids a second state's fees and agent; a company formed in Delaware or Wyoming usually also registers in the home state, with that state's fee. The home state is not in the records, so it is not priced.
3. **Shape:** formation one-time; state fee yearly; registered agent yearly; EIN free.
4. **Lead time and prerequisites:** no processing time is published by either state for a standard filing (both sell paid expedites). The EIN needs the responsible party's SSN or ITIN and is issued "in minutes" online.
5. **Who opens it:** Nathan, as organizer. Forming it starts the yearly fee and report (Delaware by 1 June; Wyoming in the anniversary month) and the registered-agent duty. Matrix rows to recheck first: AP-57, AP-65 and GP-57 (the entity's legal name becomes the developer name and seller; Apple sets the developer name once), and G-08.
6. **Cheaper options:** Wyoming with Wyoming Agents ($100 + $25 a year + $60 a year) is the lowest published combination; it gives up nothing on these pages, but adds a foreign registration if Nathan lives and works elsewhere. Forming as an individual is not an option: OD-55 chose an entity, and Apple asks for a legal entity for apps that require sensitive information (AP-57).

### Line 2 — The D-U-N-S number

1. **What and why:** Apple and Google require a D-U-N-S number for an organization account (AP-57; GP-57). First needed by the store accounts (owner track O5, then P09.2). Direction: OD-55.
2. **Published price:** free. Dun & Bradstreet: "There is no charge to receive a D-U-N-S Number" ([D&B](https://www.dnb.com/en-us/smb/duns/get-a-duns.html)); expedited service "For a small fee" (**no public price**; D&B's checkout would show it). Apple: if the company is not listed, "you'll have the option to submit your information to Dun & Bradstreet for a free D‑U‑N‑S Number" ([Apple](https://developer.apple.com/support/D-U-N-S/)). Google: "Applying for a D-U-N-S number through Dun & Bradstreet is a completely free process" ([answer 13634885](https://support.google.com/googleplay/android-developer/answer/13634885)).
3. **Shape:** free (one-time).
4. **Lead time:** Apple: "please allow up to 5 business days to receive your number from D&B. Expediting your D‑U‑N‑S Number creation process will not shorten this waiting period", then "allow up to 2 business days for Apple to receive your information from D&B". D&B's own route: "In most cases, you'll receive your number within 30 business days"; expedited, about eight business days. Google's verification FAQ: "up to 28 days" ([FAQ](https://developer.android.com/developer-verification/guides/faq)). Prerequisite: the entity exists ("DBAs, fictitious businesses, trade names, and branches are not accepted").
5. **Who opens it:** Nathan, for the entity. It starts no deadline. Google requires the account details to be "consistent with the details stored on your Dun & Bradstreet profile" ([answer 10788890](https://support.google.com/googleplay/android-developer/answer/10788890)), so the entity's name and address must match.
6. **Cheaper options:** none; it is free. D&B's paid expedite does not shorten Apple's route.

### Line 3 — Apple Developer Program (organization)

1. **What and why:** publishing the iPhone app, TestFlight, StoreKit subscriptions and APNs. First needed by P08.3 (store test modes) and P09.2 (signed builds). Direction: OD-50, OD-55; PF01 A04.
2. **Published price:** "The Apple Developer Program is 99 USD per membership year" ([enrol](https://developer.apple.com/programs/enroll/)); "$99 annual membership" ([programs](https://developer.apple.com/programs/)). Fee waivers only for a "nonprofit organization, accredited educational institution, or government entity" ([fee waivers](https://developer.apple.com/help/account/membership/fee-waivers/)), so not Glow.
3. **Shape:** yearly.
4. **Lead time and prerequisites:** the organization "must be a legal entity so that it can enter into contracts with Apple"; "must have a D-U-N-S Number"; its website "must be publicly available and functional, and its domain name must be associated with your organization"; the enroller must have "the legal authority to bind your organization". Payment comes after Apple verifies the enrolment; Apple publishes no review time (only "If you haven't received a membership confirmation within 24 hours of your purchase, contact us").
5. **Who opens it:** the entity, enrolled by Nathan. **Recheck first:** AP-56 (the trader declaration, required "Even if you don't distribute apps in the EU"), AP-57, AP-58 (the support URL's contact details), AP-65 (the developer name is set once, at the first app record), AP-21, and G-08. Creating it starts the yearly renewal.
6. **Cheaper options:** an individual membership costs the same $99 and shows Nathan's legal name as the developer (AP-65); it gives up the entity OD-55 chose. No cheaper organization tier exists.

### Line 4 — Google Play Console (organization), Android developer verification, and G-08's decisions

1. **What and why:** publishing the Android app and Play Billing subscriptions. First needed by P08.3 and P09.2. Direction: OD-50, OD-55.
2. **Published price:** "There is a US$25 one-time registration fee" ([answer 6112435](https://support.google.com/googleplay/android-developer/answer/6112435)). Android developer verification: "For most Play developers, no new action is required for identity verification", new package names are registered automatically in Play Console, and no fee is stated for Play developers (the $25 the FAQ names is for the separate Android Developer Console used outside Play) ([developer verification](https://developer.android.com/developer-verification)).
3. **Shape:** one-time.
4. **Lead time and prerequisites:** "To create a developer account for an organization, you must provide a D-U-N-S number" (answer 13634885); contact email and phone (answer 10788890). Google's own verification time is not published.
5. **Who opens it:** the entity, through Nathan. **Opening it starts a deadline:** trader status must be declared "immediately upon account creation" for a new account (existing accounts by 1 February 2027), and from 1 March 2027 a trader's details are shown to users ([answer 17594752](https://support.google.com/googleplay/android-developer/answer/17594752); GP-59). **Recheck first:** GP-56 to GP-60, GP-14, GP-18 (the public child-safety standards page, linked in Play Console), GP-22 (the named child-safety contact), and G-08.
   - **G-08's account decisions, named for Nathan:** (a) personal or organization (OD-55 points to organization); (b) the trader declaration on creation (GP-59); (c) Android developer verification (GP-56; no action stated for Play developers today, global in 2027); (d) Google's closed test of 12 testers for 14 days, which the page states for personal accounts created after 13 November 2023 and does not state for organization accounts ([answer 14151465](https://support.google.com/googleplay/android-developer/answer/14151465)); (e) the ICO fee: not applicable while there is no UK launch (OD-55; UK-44).
6. **Cheaper options:** a personal account costs the same $25, shows the personal contact details, and brings the 12-tester, 14-day closed test (GP-58).

### Line 5 — Expo's build service, and signing

1. **What and why:** hosted iOS and Android builds and store submission; no cloud session can build natively (M09, item 15). First needed by P09.2 (and the release work Nathan authorizes, D-17). Direction: PF01 A04; `apps/mobile/AGENTS.md`.
2. **Published price** ([expo.dev/pricing](https://expo.dev/pricing)): "Free — $0/month" with "Up to 15 Android and 15 iOS builds", low priority; "Starter — $19/month plus additional usage cost" with $45 of build credit, high priority; "Production — $199/month plus additional usage cost" with $225 of credit; Enterprise custom. Per build: Android medium $1, large $2; iOS medium $2, large $4. EAS Update: Free 1,000 monthly active users; Starter 3,000, then $0.005 each. "Every plan includes Expo Build, Expo Submit, Expo Update", and credential management on all plans.
   - **Signing:** EAS-managed credentials are included on every plan ([docs](https://docs.expo.dev/app-signing/managed-credentials/)); Apple's signing certificates come with the Apple membership (Line 3; not separately priced on a page read); Play App Signing enrols new apps automatically ([answer 9842756](https://support.google.com/googleplay/android-developer/answer/9842756); no price stated).
3. **Shape:** monthly plan plus usage per build (and per update user).
4. **Lead time and prerequisites:** none published; iOS credentials need the Apple membership. Whether the Free plan's build allowance renews monthly is not stated on the page.
5. **Who opens it:** Nathan (or the entity) creates the Expo account and project; release work needs his authorization each time (D-17). No matrix row is tied to the Expo account itself; P09.2's rows apply to the builds.
6. **Cheaper options:** the Free plan (low queue priority, at most one macOS build at a time); local builds on a Mac with Xcode and Android Studio (not priced; needs equipment no cloud session has); GitHub's macOS runners at $0.062 a minute ([runner pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing)), which give up managed signing and need their own pipeline.

### Line 6 — Railway app services (the API and the worker), and option (b) of D-13: the app's own PostgreSQL in a US region

1. **What and why:** the hosted API and worker (SV5's composed server, P11B staging, P11C production). D-13 (b) is the alternative to OD-18's placement on HDE's PostgreSQL service, which a record of 23 September puts in a European region. First needed by P11B (item 19). Direction: OD-18, OD-50, PF01's autonomy table.
2. **Published price** ([plans](https://docs.railway.com/reference/pricing/plans), confirmed by the second reader): "Hobby | $5 / month" ("includes $5 of resource usage per month"); "Pro | $20 / month" per workspace, with $20 of usage, "Seats are unlimited and included" ([pricing](https://railway.com/pricing)); Enterprise custom (**no public price**). Usage: "CPU | $20 / vCPU / month"; "RAM | $10 / GB / month"; "Network Egress | $0.05 / GB"; "Volume Storage | $0.15 / GB / month". US regions: "US East Metal" (Virginia) and "US West Metal" (California) ([regions](https://docs.railway.com/reference/deployment-regions)).
   - **PostgreSQL on Railway** is a template service ("This deploys a single node that Railway maintains"), billed at the same usage rates ([guide](https://docs.railway.com/guides/postgresql)); it can be converted to a high-availability cluster (extra nodes, price not stated). Backups are "incremental and Copy-on-Write, we only charge for the data exclusive to them", at volume rates; daily backups are kept 6 days, weekly 27, monthly 89 ([backups](https://docs.railway.com/reference/backups)).
   - **Estimate at launch sizes (assumed, not measured):** API 0.5 vCPU and 1 GB ($20.00), worker 0.25 vCPU and 0.5 GB ($10.00), 10 GB egress ($0.50): **$30.50 a month**, on Hobby or Pro alike, since the plan's fee is credited against usage. **With option (b):** PostgreSQL at 0.25 vCPU and 0.5 GB with a 5 GB volume adds $10.75: **$41.25** (about $42 with backups). A 5 GB volume is Hobby's per-service limit; growth needs Pro, which costs the same at this usage.
3. **Shape:** monthly plan credited against usage (per vCPU-month, GB-month, GB of egress).
4. **Lead time:** none (self-serve).
5. **Who opens it:** Nathan; each Railway app service is created only after he approves this line (PF01's autonomy table). Under OD-18 the database is a separate logical database on HDE's PostgreSQL service; its cost and capacity are A02's check, not priced here.
6. **Cheaper options** (managed PostgreSQL, US): Neon Launch "$0.106/CU-hour", "$0.35/GB-month", no minimum; free 100 CU-hours and 1 GB a project ([Neon](https://neon.com/pricing)). Supabase Pro "from $25/month", with daily backups kept 7 days; its free tier is "paused after 1 week of inactivity" with no backups ([Supabase](https://supabase.com/pricing)). Render: paid from $6 a month, storage $0.30/GB-month, per Render's own article; its pricing table did not render ([article](https://render.com/articles/managed-postgresql-pricing-2026)). Each adds a second vendor beside Railway. Railway's own Free plan ($1 of usage a month, 0.5 GB per service) cannot run the API.

### Line 7 — Stream's production chat plan, the Maker terms, terms 12.5, the DPA and the Trust Center

1. **What and why:** chat behind Glow's server (OD-45). First needed by P11B (item 19; C-18; D-10). Direction: OD-22, OD-45, OD-50, OD-76.
2. **Published price** ([chat pricing](https://getstream.io/chat/pricing/)):
   - **Build:** free, "1,000 MAU 100 Concurrent Connections", overage "Limits Apply".
   - **Start:** "$399.00 USD /mo Billed annually, or $499.00 monthly 10,000 MAU 500 Concurrent Connections", with "Advanced Moderation & Filters … Data Export"; overage "$0.09 per user" and "$0.99 per concurrent". Other limits in the table (the summariser's reading, not verbatim): 5M stored messages, then $5.00 per 1M; 2M API calls a month, then $7.00 per 1M; 500 GB bandwidth. **Unchanged** since P06.1's 28 September reading ($399 billed yearly) and the 23 September research ($499 monthly, 10,000 MAU and 500 connections).
   - **Elevate:** $599 billed annually or $675 monthly. **Enterprise:** "Contact Sales" (**no public price**).
   - Retention: "Messages are securely stored for as long as your plan is active."
   - **The Maker terms** ([Maker account](https://getstream.io/maker-account/)): "If your company has five or less team members, less than $10k in monthly revenue and has taken less than $100k in funding, Stream is free/gratis/complimentary"; "The Maker Account for Chat offers a modified Chat Start Plan with all the same capabilities, but with a limit of 2,000 monthly active users and 100 concurrent connections"; "Hard limits - no surprise bills". The revenue limit is **unchanged** ("under $10k monthly revenue"). The pricing page words the team limit as "less than 5 team members", which differs from the Maker page's "five or less".
   - **Terms 12.5** ([terms](https://getstream.io/legal/), "Last update: October 2024"): "12.5. Publicity. Stream shall have the right to use Customer's name and logo on client lists published on Stream's website and in marketing materials. Stream may also announce the relationship hereunder in a press release."
   - **The data-processing addendum:** [getstream.io/legal/dpa](https://getstream.io/legal/dpa/), "Effective Date: November 3, 2026" (newer than the earlier research), current PDF linked there. It goes to P08.1's processor list (H-03). **The Trust Center:** [trust.getstream.io](https://trust.getstream.io/) (its content loads by script and was not read; nothing gated was requested); security page [getstream.io/security](https://getstream.io/security/).
3. **Shape:** monthly, or yearly commitment billed monthly; usage overage per MAU and per connection.
4. **Lead time:** the Maker account is an application ("Sign in to your Stream dashboard to submit your application"); no review time is published; Nathan's has been pending since 25 September (OD-22). No other lead time.
5. **Who opens it:** Nathan holds the Stream organization; the production plan is bought there. Before approving, the terms Nathan's decision rests on are 12.5 (publicity; ADR 0003's display rule, OD-16) and the moderation duty in section 6.2 (P07, A05), each in Stream's words. No matrix row is tied to it.
6. **Cheaper options:** Maker, if approved: free to 2,000 MAU with hard limits, and lost when revenue reaches $10,000 a month (the founding-member offer alone could cross it, D-10). Build: free to 1,000 MAU, without advanced moderation, data export or a paid overage path. Building Glow's own chat was set aside by OD-45.

### Line 8 — Cloudflare R2 for photos, and an image processing service beside Glow's own

1. **What and why:** private storage for photo originals and Glow's own variants (OD-62). First needed by AC2 for a real upload (item 6) and the photo processor with the R2 adapter (P11; C-06, C-11). Direction: OD-62.
2. **Published price** ([R2 pricing](https://developers.cloudflare.com/r2/pricing/), confirmed by the second reader): "Storage | $0.015 / GB-month"; "Class A Operations | $4.50 / million requests"; "Class B Operations | $0.36 / million requests"; "Egress (data transfer to Internet) | Free"; free each month: "10 GB-month", 1 million Class A and 10 million Class B. Infrequent Access: $0.01/GB-month, $0.01/GB retrieval, 30-day minimum. A `us` jurisdiction keeps objects in the US ([data location](https://developers.cloudflare.com/r2/reference/data-location/)).
   - **An image processing service:** Cloudflare Images: 5,000 unique transformations a month free, then "$0.50 / 1,000 unique transformations"; stored "$5 / 100,000 images"; delivered "$1 / 100,000 images" ([Images pricing](https://developers.cloudflare.com/images/pricing/)). It would add on-the-fly resizing and format conversion; Glow already makes its own variants (OD-62), so it duplicates that step. How private, signed delivery works with transformations was not read. **Not in the totals.**
3. **Shape:** usage (per GB-month and per million operations).
4. **Lead time and prerequisites:** "You need a Cloudflare account with an R2 subscription", added through a checkout ([get started](https://developers.cloudflare.com/r2/get-started/)); no Workers plan needed. Whether the checkout asks for a payment method is visible only after sign-in.
5. **Who opens it:** Nathan (the entity's Cloudflare account). No matrix row is tied to it; the photo rows bind to the processing (P07, P08).
6. **Cheaper options:** Railway's buckets at "$0.015 per GB-month", operations and bucket egress free, but no backups, versioning or lifecycle rules, public networking only ([buckets](https://docs.railway.com/guides/storage-buckets)); Backblaze B2 "$6.95 / TB / mo", first 10 GB free, egress free up to 3× storage ([B2](https://www.backblaze.com/cloud-storage/pricing)). Each departs from OD-62's R2.

### Line 9 — The automated photo check and hash matching for known CSAM; NCMEC's registration and G-02's named contacts

1. **What and why:** OD-75 (D-03 (a)) turns the photo check on at launch, with hash matching for known child sexual abuse material; the detection tool is chosen with D-08 at P07.1 (item 8). G-02 lists the registrations and named contacts. First needed by P07.1, then PV04 in P11. Direction: OD-68, OD-75; G-02.
2. **Published prices** (each rechecked against A05-V's 17 November reading):

| Service | Today's price | Against A05-V |
|---|---|---|
| Azure AI Content Safety, image | $0.75 per 1,000 images; free 5,000 a month, usage stops at the limit ([page](https://azure.microsoft.com/en-us/pricing/details/content-safety/); the amount is in the page's data attribute, us-east 0.75, and its worked example "500,000 … = $375") | unchanged |
| Google Cloud Vision SafeSearch | "0 count to 1,000 count $0.00 (Free)", "1,000 count to 5,000,000 count $1.50", per 1,000 ([page](https://cloud.google.com/vision/pricing)) | unchanged |
| AWS Rekognition moderation | $0.0010 an image for the first million (Group 2, from the page's worked example; the US East table loads by script); 1,000 free a month for 12 months ([page](https://aws.amazon.com/rekognition/pricing/)). **An AWS service: OD-76 says no AWS usage is planned.** | unchanged as far as the static text shows |
| Hive (now "Deploy") Visual Moderation | "$3.00 / 1000 Requests", "Limit: 100 requests/day"; higher limits "Contact Sales" ([page](https://deploy.com/pricing)) | price unchanged; the annual-contract wording is no longer on the pricing page |
| Sightengine | Free 2,000 operations a month; Starter "$29/mo" for 10,000; Pro "$99/mo" for 40,000; "$0.002 per additional op" ([page](https://sightengine.com/pricing)) | unchanged |
| Microsoft PhotoDNA (hash matching) | "PhotoDNA Cloud Service is free for qualified customers", by application ([page](https://www.microsoft.com/en-us/photodna)) | unchanged |
| Thorn Safer | No public price on safer.io; AWS Marketplace, 12 months: Safer Enterprise from $45,384.00 (1M queries a month) ([listing](https://aws.amazon.com/marketplace/pp/prodview-unzbqt3w6pqbg)); **Safer Match** from $30,720.00 ([listing](https://aws.amazon.com/marketplace/pp/prodview-dfwekn4bx4ake)) | Enterprise unchanged; Safer Match newly listed |
| Hive's CSAM Detection (Thorn's model) | "Contact Sales": **no public price** | new |
| Cloudflare CSAM Scanning Tool | No price or plan stated; it compares "content served for your website through the Cloudflare cache" and emails a notice daily; "You are responsible for understanding and complying with any legal obligations you have" ([page](https://developers.cloudflare.com/cache/reference/csam-scanning/)). It does not check a private photo before it is shown | — |
| Tech Coalition (Lantern) | "Membership starts at US$10,000 per year" ([page](https://technologycoalition.org/membership/apply/)) | unchanged |

   - **NCMEC's registration:** no fee is published; NCMEC says more than 2,000 providers are registered ([data page](https://www.missingkids.org/gethelpnow/cybertipline/cybertiplinedata)) and recommends contacting its ESP team to register (USF-02; not contacted). **G-02's named contacts:** NCMEC's point of contact (USF-02) and Google's child-safety contact (GP-22); the NCA's administrator and emergency contact only if Glow has UK links (none under OD-55). Nathan holds every role (OD-23). These cost nothing on the pages read.
3. **Shape:** the check is usage-based (per 1,000 images) or a monthly plan; PhotoDNA free; Safer a yearly contract; NCMEC free.
4. **Lead time:** PhotoDNA's vetting and NCMEC's registration publish no time; both should start early. The cloud checks are self-serve.
5. **Who opens it:** the entity, through Nathan; the tool is chosen at P07.1 with the Dev Manager (D-08). **Recheck first:** G-02 and its rows AP-21, GP-18 to GP-23, USF-01 to USF-07 (UK-15 to UK-20 only if Glow gains UK links).
6. **Cheaper options:** Azure or Google within their free tiers costs nothing at launch volumes; hash matching through PhotoDNA costs nothing if Microsoft qualifies Glow, while Safer costs about $30,700 a year or more. Sightengine's free plan caps at 500 a day. **The totals use Azure's price for the check and PhotoDNA at $0;** if PhotoDNA is refused, hash matching adds about $2,560 a month (Safer Match's yearly price spread over twelve months). This implies a provider choice, which goes to the Dev Manager.

### Line 10 — Mail (transactional email)

1. **What and why:** sign-up and reset codes, the trial-ending notice, receipts. First needed by SV5 (the mail adapter can be added once its account exists), then C-12 at P11B. Direction: OD-50; H-13.
2. **Published prices:**

| Provider | Free | Entry paid | About 20,000 a month | About 100,000 a month |
|---|---|---|---|---|
| Resend ([page](https://resend.com/pricing)) | "3,000 emails / mo 100 emails a day" | Pro "$20 / mo 50,000 emails / mo Extra emails: $0.90 / 1,000"; monthly only | $20 | Scale "$90 / mo 100,000", or Pro with overage $65 (my arithmetic) |
| Postmark ([page](https://postmarkapp.com/pricing)) | 100 a month (testing) | Basic "$15.00 /mo" for 10,000, "Extra emails @ $ 1.80 / 1,000" | $33 (Basic), $29.50 (Pro) | $125.50 (Pro; my arithmetic) |
| SendGrid ([page](https://www.twilio.com/en-us/products/email-api/pricing)) | 100 a day for 60 days only | Essentials 50k "$19.95/mo" | $19.95 | Essentials 100k "$34.95/mo" |
| Mailgun ([page](https://www.mailgun.com/pricing/)) | 100 a day | Basic "$15/mo" for 10,000, "from $1.80 / 1,000" | $33 | Scale "$90/mo" |
| Brevo ([page](https://www.brevo.com/pricing/)) | 300 a day | Starter "$9 per month", from 5,000 | not readable (script) | not readable |
| Amazon SES ([page](https://aws.amazon.com/ses/pricing/)) | — | Essentials $0.16 per 1,000 | about $3.20 | about $16 |

   - SES is an AWS service; OD-76 says no AWS usage is planned. It is listed only as a price.
3. **Shape:** monthly plan with included volume, plus overage per 1,000 emails.
4. **Lead time:** self-serve; sending from Glow's domain needs the domain (Line 14) and its DNS records.
5. **Who opens it:** the entity, through Nathan. No matrix row is tied to the account.
6. **Cheaper options:** Resend's free plan (3,000 a month, 100 a day) fits the launch; Brevo's free plan (300 a day). **The totals use Resend:** $0 at launch, $20 at 1,000 and at 10,000 members (5,000 and 50,000 emails assumed). This implies a provider choice, which goes to the Dev Manager.

### Line 11 — Push (Expo's push service, APNs and FCM)

1. **What and why:** message and match notifications. Server side in SV4 Stage B (item 2); real push in P09.2. Direction: OD-50; PF01 A04.
2. **Published price:** Expo: "There is no cost associated with sending notifications through Expo push notification service", with "a limit of 600 notifications per second per project" ([FAQ](https://docs.expo.dev/push-notifications/faq/)). FCM: "No-cost" ([Firebase pricing](https://firebase.google.com/pricing)). APNs: part of the Apple membership (Line 3); no Apple page read today prices it separately.
3. **Shape:** free.
4. **Lead time:** needs the Apple membership (APNs key) and a Firebase project for FCM.
5. **Who opens it:** the entity, through Nathan, with the store accounts. No separate matrix row.
6. **Cheaper options:** none needed.

### Line 12 — Stripe: payments, Billing, Radar, its review of a dating service; Stripe Tax as an option

1. **What and why:** the Stripe link in the iPhone app and the web checkout (OD-69, OD-70), the card check at signup, Radar for free-trial abuse and the US-only card rule (OD-70, OD-71). First needed by P08.3 (item 13). Direction: OD-69 to OD-71.
2. **Published prices** (rechecked against A05-V2 and A05-V3):
   - Payments: "2.9% + 30¢ per successful transaction for domestic cards", "+ 0.5%" manually entered, "+ 1.5%" international, "+ 1%" currency conversion; disputes "$15.00" each, and $15.00 "for each dispute you respond to manually" ([pricing](https://stripe.com/pricing)). **Unchanged.**
   - Billing: "0.7%" of Billing volume, pay as you go ([Billing pricing](https://stripe.com/billing/pricing)). **Unchanged.** (Contracts from $620 a month exist for high volume.)
   - Radar ([Radar pricing](https://stripe.com/radar/pricing)): Lite "included at no additional charge for businesses on standard payments pricing"; pay as you go: Standard $0.05, Plus $0.07, Pro $0.09 per screened transaction plus $0.005 per abuse event. **Unchanged.** Standard's $0.05 is visible on stripe.com/pricing; Plus and Pro were read from the page's public script behind its "Show pricing" control. **New:** monthly plans "Starting at $10 per month" (Standard), $14 (Plus), $20 (Pro). Custom rules, allowlists and blocklists are not in Standard, so **the US-only card rule needs Plus or Pro.** **A change is announced:** "Starting January 22, 2027, new Radar pricing will go into effect", with "four tiers—Lite, Standard, Plus, and Pro"; after a trial, accounts "automatically continue on Radar Standard and be charged" ([support](https://support.stripe.com/questions/updates-to-radar-pricing-(january-2027))). Recheck the tier before approving.
   - **Stripe Tax** (option): Tax Basic "0.5%" per transaction where registered, through Billing or Checkout, or $0.50 per API transaction; Tax Complete from $90 a month on a one-year contract ([Tax pricing](https://stripe.com/tax/pricing)).
   - **The review:** "Online dating and matchmaking services" are listed under Restricted Businesses: "Businesses in these categories require additional due diligence by Stripe in order to confirm our ability to support them"; "Stripe might not be able to grant approval for your business to use our products. If we do provide approval, note that the approval is specific to each service offer, and it may be modified or revoked by Stripe at any time" ([restricted businesses](https://stripe.com/legal/restricted-businesses)).
3. **Shape:** a share of each payment (percentage plus a fixed fee), Billing as a percentage, Radar per screened transaction or monthly, Tax per transaction or monthly; no monthly fee for payments.
4. **Lead time:** Stripe's review of a dating business publishes no time. Prerequisites: the entity, its EIN and bank account, and a description of the business model.
5. **Who opens it:** the entity, through Nathan (owner track O6). **Recheck first:** A05-V2's rows, with AP-42 and GP-39 (the link to purchase outside the stores), and the state renewal rows A05-V2 read.
6. **Cheaper options:** Radar Lite only (free), which gives up custom rules and so the US-only card rule (OD-71); Radar pay as you go instead of a monthly plan at low volume. Stripe Tax is optional; without it, tax is worked out another way.

### Line 13 — The stores' billing: commissions, small-business rates, and RevenueCat beside the stores' own libraries

1. **What and why:** the paid plan sold through each store (OD-69). First needed by P08.3 (item 13). The library choice is D-11, a design choice for the Dev Manager; it reaches Nathan as this cost line.
2. **Published prices:**
   - **Apple:** the App Store Small Business Program: "reduced commission rate of 15% on paid apps and Apple In-App Purchases" for developers with "no more than 1 million USD in total proceeds" ([program](https://developer.apple.com/app-store/small-business-program/)). Standard auto-renewable subscriptions: "After a subscriber accumulates one year of paid service, your net revenue increases to 85%", and "Free trials and renewal extensions are excluded from days of paid service" ([subscriptions](https://developer.apple.com/app-store/subscriptions/)). Purchases through the Stripe link on the US storefront: no commission is stated on the pages read (as A05-V2 and A05-V3 found).
   - **Google** ([answer 112622](https://support.google.com/googleplay/android-developer/answer/112622), confirmed by the second reader): from "June 30, 2026 for the EEA, UK, and US", auto-renewing subscriptions "10% + 5% billing fee"; other transactions on the first $1M "20% + 5% billing fee" (new installs) and "25% + 5% billing fee * OR; 20% for external web links" (existing installs). **This changes the records' "15% for subscriptions":** the total on a subscription is still 15%, now split as 10% plus a 5% billing fee; one-time purchases through Play billing cost 25% or more. No US rate above $1M is shown. Linking out on Android is not in OD-70's design (C3 (a)).
   - **RevenueCat:** "Once you reach $2.5K MTR, you'll be charged 1%"; "No charges apply on months when you don't hit the $2.5K threshold"; MTR is revenue tracked "before the platform cut" ([pricing](https://www.revenuecat.com/pricing/)). Its page names receipt validation across StoreKit, Google Play and web, one subscription status, dashboards and paywalls.
   - **The stores' own libraries** (StoreKit 2 and the Play Billing Library) carry no fee on the pages read; Glow's server then verifies purchases itself.
3. **Shape:** a share of revenue.
4. **Lead time:** the Small Business Program needs the Paid Apps agreement accepted in App Store Connect; proceeds are adjusted "fifteen (15) days after the end of the fiscal calendar month in which your enrollment is approved".
5. **Who opens it:** the entity, inside the store accounts. **Recheck first:** AP-39 to AP-43, GP-39 to GP-43 (A05-V2's set).
6. **Cheaper options:** the stores' own libraries with server verification cost nothing per sale but need that server work and its upkeep. Enrolling in Apple's Small Business Program halves Apple's first-year subscription commission.

### Line 14 — A domain, and WordPress hosting for the public site and the staff console

1. **What and why:** the public site, the policy and support URLs the stores require (AP-58), the staff console (OD-19, OD-60), and email from Glow's domain. The domain is also needed earlier: Apple's organization enrolment requires a working website on the organization's domain (Line 3). First needed by P07.3 (item 10; D-16) for hosting, and by Apple's enrolment for the domain. Direction: OD-19, OD-60; D-16.
2. **Published prices:**
   - **Domain (.com):** Porkbun ".com $11.81 $11.81 $11.81" (registration, renewal, transfer), "include ICANN and any other fees" ([Porkbun](https://porkbun.com/products/domains)). Namecheap, from 1 November 2026: registration "$15.98/year", renewal "$19.98/year" ([notice](https://www.namecheap.com/support/knowledgebase/article.aspx/10840/2201/com-price-change-november-1-2026/)). Cloudflare Registrar "does not mark up domain prices at all" ([registrar](https://www.cloudflare.com/products/registrar/)); its .com figure is not on a public page (**no public price** without signing in).
   - **WordPress hosting** (entry tier that allows custom plugins): WordPress.com Business "US$25" a month billed yearly, "US$40" monthly, with plugin upload, SSL, real-time backups and a staging site ([pricing](https://wordpress.com/pricing/); the yearly pairing is read from the page layout). WP Engine Essential $28 a month billed yearly ($336), $35 monthly ([plans](https://wpengine.com/plans/)). Kinsta Single 35k $35 monthly, $315 a year ([pricing](https://kinsta.com/pricing/)). SiteGround StartUp $1.99 a month for the first year, "Renews at $17.99 /mo.", without staging ([page](https://www.siteground.com/wordpress-hosting.htm)). Cloudways DigitalOcean Micro "$14" a month, a server Glow manages ([pricing](https://www.cloudways.com/en/pricing.php)).
3. **Shape:** domain yearly; hosting monthly or yearly.
4. **Lead time:** none published.
5. **Who opens it:** the entity, through Nathan. **Recheck first:** AP-58 and GP-18 (the support and child-safety pages the site will carry). Registration starts a yearly renewal.
6. **Cheaper options:** Cloudflare at cost (likely below Porkbun, not readable); SiteGround's first year ($1.99) or Cloudways ($14), which give up staging or managed WordPress; a WordPress container on Railway (not priced), which gives up managed backups and security. **The totals use Porkbun and WordPress.com Business, billed yearly.**

### Line 15 — Monitoring: error tracking, uptime and logs

1. **What and why:** error and crash reports from the API and the app, uptime alerts and logs for one operator. First needed by P09.3 (item 16). Direction: OD-50; H-13.
2. **Published prices:**
   - **Sentry** ([pricing](https://sentry.io/pricing/)): Developer "Free $0 Limited to one user", 5,000 errors, 30-day lookback; Team $29 a month monthly or $26 a month billed yearly ($312), unlimited users, 50,000 errors. Supports React Native with Expo ([docs](https://docs.sentry.io/platforms/react-native/manual-setup/expo/)) and Django ([docs](https://docs.sentry.io/platforms/python/integrations/django/)).
   - **UptimeRobot** ([pricing](https://uptimerobot.com/pricing/)): "Free $ 0 /month Good for personal and commercial projects", 50 monitors at 5-minute intervals; Solo from $144 a year; Team $39 monthly or $396 a year.
   - **Better Stack** ([pricing](https://betterstack.com/pricing)): free 10 monitors, 100,000 exceptions a month, logs kept 3 days; paid bundles from about $25 a month (which figure is monthly and which yearly is read from the page's order, unconfirmed).
   - **Railway's own logs** ([logs](https://docs.railway.com/observability/logs)): kept 7 days on Hobby and 30 days on Pro, no extra charge.
3. **Shape:** monthly or yearly plans; free tiers.
4. **Lead time:** none.
5. **Who opens it:** Nathan. No matrix row is tied to it; P09.3 owns the runbooks.
6. **Cheaper options:** Sentry Developer, UptimeRobot Free and Railway's logs together cost nothing, at the price of one user, 5,000 errors a month and 5-minute checks. **The totals use these at launch and at 1,000 members, and Sentry Team (yearly) at 10,000.**

### Line 16 — GitHub Actions minutes once the repository is private

1. **What and why:** CI for every push and pull request. While the repository is public, standard runners are free; Nathan intends to make it private again (OD-51), and then GitHub Free's allowance applies. First needed when he makes it private. Direction: OD-51; "Carried to M07".
2. **Published price** ([Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions); [runner pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing); [pricing](https://github.com/pricing); confirmed by the second reader):
   - GitHub Free: "$12 USD" of included compute a month; "The included compute usage is expressed as a monetary amount, not a fixed number of minutes"; the pricing page says "2,000 CI/CD minutes/month", the same at "Linux 2-core (x64) | actions_linux | $0.006" a minute. **Changed in form, not in amount,** from the 26 October reading (2,000 minutes, then $0.006 a minute).
   - "If your account does not have a valid payment method on file, usage is blocked once you consume the included compute usage." **Unchanged.**
   - "GitHub rounds the minutes and partial minutes each job uses up to the nearest whole minute." Neither page says whether queued time or skipped jobs are billed.
   - Storage: 500 MB of artifacts (shared with Packages), then $0.25 a GB-month; cache 10 GB a repository, then $0.07.
   - GitHub Team: "$4USD per user / month", "$18 USD" of compute ("3,000 CI/CD minutes/month").
   - Public repositories: "The use of standard GitHub-hosted runners is free: In public repositories".
   - **Measured use, October 2026** (the last full month), read through the GitHub tools (`list_workflow_runs`, `list_workflow_jobs`; no re-run or change). GitHub reports 0 billable milliseconds for a public repository, so the minutes are rebuilt from job times by GitHub's rounding rule: each job that ran, rounded up to a whole minute.
     - **332 runs** in October (created 4 to 26 October; none on 1 to 3 or 27 to 31 October, nor on 7 to 21): 330 Foundation and 2 Branch cleanup. No run had a second attempt (earlier attempts of a re-run are not listed, so re-runs would be missed). Every job ran on `ubuntu-24.04`.
     - **175 documentation-only Foundation runs** (60 s or less): 9 sampled, each 2 billable minutes (the change-scope and gate jobs; the other six skipped): **350 minutes.**
     - **152 full-scope Foundation runs** (over 150 s, 8 jobs each): 28 sampled job by job. By period: 4 to 5 October, all 8 runs counted, 115 minutes; 5 to 24 October, 75 runs at a sampled mean of 18.6 (10 samples); 24 to 26 October, 69 runs at 19.1 (10 samples). **About 2,830 minutes** (2,830 to 3,000 by the other method, billable minutes per minute of run time). One cancelled run whose three jobs never reached a runner was counted at its 11 ran minutes, not the 45 its queue time would give; another cancelled run had no jobs and counted 0.
     - **3 runs of 61 to 150 s** (not sampled; 6 to 24 minutes by the two methods) and **2 Branch cleanup runs** (1 minute each).
     - **Total: about 3,200 to 3,400 billable minutes,** against 2,000 included. The month's runs fell on eight days; a month with more active days would use more.
3. **Shape:** monthly allowance, then usage per minute; Team per user per month.
4. **Lead time:** none. **Prerequisite:** a payment method on file, or CI stops once the allowance is spent.
5. **Who opens it:** Nathan, on his GitHub account (the repository owner pays). Making the repository private is his decision (OD-51); nothing else starts.
6. **Price, and the cheaper options beside it,** at October's use:
   - **Keep the repository public:** $0 (today; the code and records stay readable by anyone).
   - **Private, GitHub Free with a payment method:** (3,200 to 3,400 − 2,000) × $0.006 = **$7.20 to $8.40 a month**.
   - **Private, GitHub Team (one user):** $4 + (3,200 to 3,400 − 3,000) × $0.006 = **$5.20 to $6.40 a month**, with more included storage.
   - **Private, GitHub Free with no payment method:** $0, and CI is blocked for the rest of each month after about 2,000 minutes, roughly two-thirds of October's use.
   - **Fewer minutes:** the documentation-only runs used about 350 minutes; running the classification and gate in one job, or not running Foundation for documentation-only pushes, would save up to half of that. Cancelled and superseded full runs still billed. This is a workflow change, which needs full review (`AGENTS.md`).

### Line 17 — Legal advice

1. **What and why:** on the founding-member offer's form before it is sold (OD-71; five state laws bar a contract "measured by the life of the buyer", A05-V3), and, as Nathan's option, on the paid plan's terms, the renewal notices and the policies (D-12). First needed before the offer is built (after launch, D-09); optionally before P08.3 ships. Direction: OD-71; D-12.
2. **Published prices:** **no public price** for a law firm's review of the offer or of the terms; a firm's quote or engagement would give one. Published fixed prices from online legal services:
   - LegalZoom Business Attorney Plan: "$39.09 /mo billed annually at $469", or $259 every six months; "Unlimited 30-minute attorney consults on new legal matters" and "Attorney review for contracts and key documents (10 pages included)", longer documents $69 (11 to 15 pages) or $149 (16 to 25) ([LegalZoom](https://www.legalzoom.com/attorneys/)).
   - Rocket Lawyer: memberships "$149/year or $34.99/month" and up; a 30-minute legal advice session $149, 60 minutes $249 ([Rocket Lawyer](https://www.rocketlawyer.com/pricing)).
   - UpCounsel: no flat fee; sample hourly ranges "Commercial Contracts $240 - $600/hr" ([UpCounsel](https://www.upcounsel.com/pricing)).
3. **Shape:** a quote (firm); yearly or per-session (plans); hourly (marketplaces).
4. **Lead time:** none published.
5. **Who opens it:** Nathan, for the entity. Nothing starts.
6. **Cheaper options:** policy generators, which are not legal advice: Termly from $10 a month billed yearly ([Termly](https://termly.io/pricing/)); iubenda Advanced, with a terms generator, $24.99 a month billed yearly ([iubenda](https://www.iubenda.com/en/pricing)). They give up a lawyer's judgement on the offer's form, the renewal notices and the state laws. **Not in the totals.**

### Not costed

- **Identity verification:** OD-68 set it aside for the MVP (kept possible later); A05-V priced it if it returns.
- **A UK or EU representative, and the ICO fee:** no UK or EU launch (OD-55; G-09, UK-44).

## 4. Totals

**Every usage figure below is an assumption, chosen to make the arithmetic visible; none is a forecast.** The member counts are the manager's comparison points. "Members" means active members in the month. The totals take the lowest published tier that fits on each line, which is not a choice of provider; the lines name the alternatives.

| Assumption | At launch | 1,000 members | 10,000 members |
|---|---|---|---|
| Photos stored a member | 4 (the four-photo limit), each about 3 MB original plus 0.5 MB of variants | same | same |
| Photo storage | under 10 GB | 14 GB | 140 GB |
| Photo uploads (and checks) a member a month | 2 | 2 (2,000) | 2 (20,000) |
| R2 writes (an original and three variants an upload) | in free tier | 8,000 | 80,000 (free tier) |
| R2 reads (signed photo views) a member a month | in free tier | 3,000 (3M, free tier) | 3,000 (30M; 20M above the free 10M) |
| Emails a member a month | 5 | 5,000 | 50,000 |
| Messages sent a member a month; Stream API calls a message | 100; 3 | 300,000 calls | 3M calls (1M above Start's 2M) |
| Stream monthly active users | up to 100 | 1,000 | 10,000 (Start's limit) |
| Railway API / worker | 0.5 vCPU, 1 GB / 0.25 vCPU, 0.5 GB | same | 2 vCPU, 4 GB / 0.5 vCPU, 1 GB |
| Railway egress | 10 GB | 50 GB | 500 GB |
| Builds a month | 8 (4 each platform) | 8 | 8 |
| Errors a month | under 5,000 | under 5,000 | over 5,000 |
| CI minutes a month | October's, about 3,200 to 3,400 | same | same |

**One-time.**

| Line | Amount |
|---|---|
| Entity formation (Wyoming LLC; Delaware $110) | $100 |
| EIN, D-U-N-S number | $0 |
| Google Play registration | $25 |
| **Total one-time** | **$125** (Delaware: $135) |

Not included: legal advice (no public price), a home-state foreign registration (state unknown), any state filing expedite.

**Yearly.**

| Line | Amount |
|---|---|
| Apple Developer Program | $99.00 |
| Wyoming yearly license tax (Delaware $400) | $60.00 |
| Registered agent (Northwest; Wyoming Agents $25) | $125.00 |
| .com domain (Porkbun) | $11.81 |
| **Total yearly** | **$295.81** (Delaware: $635.81) — **$24.65 a month** (Delaware: $52.98) |

**Monthly, fixed and usage-based services (US dollars).**

| Line | Launch | 1,000 | 10,000 | Arithmetic |
|---|---|---|---|---|
| Railway: API, worker, egress | 30.50 | 32.50 | 125.00 | launch 20 + 10 + 0.50; 1,000: 20 + 10 + 50 × 0.05; 10,000: (2 × 20 + 4 × 10) + (0.5 × 20 + 1 × 10) + 500 × 0.05 |
| Stream, Start billed yearly | 399.00 | 399.00 | 406.00 | 399 + 1M extra API calls × $7 at 10,000 |
| Cloudflare R2 | 0.00 | 0.06 | 9.15 | 1,000: (14 − 10) × 0.015; 10,000: (140 − 10) × 0.015 + (30 − 10) × 0.36 |
| Photo check (Azure) | 0.00 | 0.00 | 11.25 | (20,000 − 5,000 free) × 0.75 / 1,000 |
| Hash matching (PhotoDNA, if qualified) | 0.00 | 0.00 | 0.00 | free; Safer Match instead adds 2,560.00 |
| Mail (Resend) | 0.00 | 20.00 | 20.00 | Free to 3,000; Pro $20 to 50,000 |
| Push (Expo, APNs, FCM) | 0.00 | 0.00 | 0.00 | free |
| Monitoring | 0.00 | 0.00 | 26.00 | free tiers; Sentry Team billed yearly at 10,000 |
| Expo builds (Free plan) | 0.00 | 0.00 | 0.00 | 8 builds within 15 + 15 |
| WordPress.com Business, billed yearly | 25.00 | 25.00 | 25.00 | |
| Yearly items, spread monthly (Wyoming) | 24.65 | 24.65 | 24.65 | 295.81 / 12 |
| **Total, without GitHub Actions** | **479.15** | **501.21** | **647.05** | |
| GitHub Actions, if private | 0 to 8.40 | 0 to 8.40 | 0 to 8.40 | $0 while public; (3,400 − 2,000) × 0.006 = 8.40 at most on Free with a payment method; Team $5.20–$6.40 |

- **With the Maker plan** (if approved, while eligible): subtract $399 at launch and at 1,000 members (Maker covers 2,000 MAU): **$80.15** and **$102.21**. At 10,000 members Maker does not fit.
- **With Delaware** instead of Wyoming: add $28.33 a month.
- **With the app's own PostgreSQL on Railway** (D-13 (b)) instead of OD-18's placement: add about $11 at launch, $21.50 at 1,000 members (0.5 vCPU, 1 GB, 10 GB volume) and $47.50 at 10,000 (1 vCPU, 2 GB, 50 GB), plus backups at $0.15 a GB of exclusive data. OD-18's own cost on HDE's service is not priced here (A02).
- **With Stream's stored messages above 5M** (about five months at 10,000 members and 100 messages a member a month): add $5 for each further million.

**Shares of each sale (not in the totals; the plan's price is undecided, D-04).**

| Channel | On each payment |
|---|---|
| Apple in-app subscription | 15% (Small Business Program), or 30% in a subscriber's first paid year and 15% after |
| Google Play subscription | 10% + 5% billing fee |
| Stripe (web, iPhone link) | 2.9% + 30¢; + 0.7% Billing on subscriptions; + Radar Plus $0.07 or Pro $0.09 a screened payment (or a monthly Radar plan from $14 or $20); disputes $15 each; Stripe Tax, if chosen, 0.5% |
| RevenueCat, if chosen | 1% of tracked revenue in a month once it reaches $2,500 |

**Check:** each total is the sum of its column, recomputed in a script from the figures above: launch 30.50 + 399.00 + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 25.00 + 24.65 = 479.15; 1,000: 32.50 + 399.00 + 0.06 + 20.00 + 25.00 + 24.65 = 501.21; 10,000: 125.00 + 406.00 + 9.15 + 11.25 + 20.00 + 26.00 + 25.00 + 24.65 = 647.05.

## 5. The order of approvals

Lines Nathan could approve now, ordered by lead time, then by the item that first needs each (PF01 1.19's order).

| # | Approval | Cost | Why now | Waits on |
|---|---|---|---|---|
| 1 | **The legal entity:** state, registered agent; then the EIN (free) | $100–$110 once; $60–$400 a year; agent $25–$125 a year | Everything below waits on it (OD-75, D-02 (a)) | Nathan's choice of state |
| 2 | **The D-U-N-S number** (through Apple's page) | free | Up to 7 business days by Apple's route; up to 30 by D&B's; Google up to 28 days | 1 |
| 3 | **The domain**, and a minimal public website on it | $11.81 a year; site from $25 a month (or a cheaper host until P07.3) | Apple's organization enrolment needs a working website on the organization's domain | 1 |
| 4 | **Apple Developer Program** | $99 a year | No review time published; needed by P08.3 and P09.2 | 2, 3; recheck AP-56, AP-57, AP-58, AP-65, AP-21, G-08 |
| 5 | **Google Play Console** | $25 once | Trader declaration due on creation; needed by P08.3 and P09.2 | 2; recheck GP-56 to GP-60, GP-14, GP-18, GP-22, G-08 |
| 6 | **Stripe** (account and review) | no fee to open; shares of sales | Review of a dating service, no time published; needed by P08.3 | 1 (EIN, bank account); recheck A05-V2's rows, AP-42, GP-39; Radar's change on 22 January 2027 |
| 7 | **NCMEC registration and PhotoDNA application** | free | No time published; bind from the first user; needed by P07.1 | 1; recheck G-02's rows |
| 8 | **Mail** | $0 at launch | SV5 can add the adapter once it exists; C-12 at P11B | 3 (domain) |
| 9 | **Cloudflare R2** and the photo check | $0 at launch | AC2's real upload; P11's processor | 1 |
| 10 | **Expo** (Free plan) | $0 | P09.2 | 4 |
| 11 | **WordPress hosting** | $25 a month (yearly) | P07.3 | 3 |
| 12 | **Monitoring** (free tiers) | $0 | P09.3 | — |
| 13 | **Railway app services** (and D-13's option) | about $30.50 a month | P11B | Dev Manager on D-13 |
| 14 | **Stream's production plan** | $399 a month billed yearly, or Maker | P11B (D-10) | the Maker decision |
| 15 | **GitHub Actions** | Line 16 | when Nathan makes the repository private (OD-51) | — |
| 16 | **Legal advice** | no public price | before the offer is sold (OD-71); optionally before P08.3 (D-12) | 1 |

Lines 8 to 14 imply provider choices (mail, photo check, hash matching, monitoring, hosting, database), which go to the Dev Manager before they are settled.

## 6. What I could not price, and why

| Item | Why | What would get it |
|---|---|---|
| A law firm's review of the founding-member offer and of the terms | No firm publishes one | A firm's quote |
| D&B's expedited D-U-N-S | "For a small fee", not stated | D&B's checkout |
| Railway Enterprise; Stream Enterprise; Expo Enterprise; RevenueCat Enterprise; Hive's higher tiers and CSAM detection; Thorn Safer direct; Sightengine Enterprise | "Contact Sales" or "negotiated" | A sales contact |
| Cloudflare Registrar's .com price | Not on a public page | The Cloudflare dashboard |
| PhotoDNA's vetting criteria and time | Behind the application | The application |
| NCMEC registration fee | No current page states one (none is expected) | NCMEC's ESP team |
| Stripe's review time; Apple's and Google's organization review times; Stream's Maker decision time | Not published | — |
| Your home state's formation and foreign-registration fees | The state is not in the records | Its secretary of state's fee schedule |
| Google's US rate above $1M of earnings | Not shown in the US table | — |
| Apple's commission, if any, on purchases through the US link | Not stated on the pages read | Apple's licence agreement and StoreKit External Purchase documents |
| Brevo above 5,000 emails | Drawn by script | — |
| The cost of OD-18's database on HDE's service | Not a public price; A02's capacity check | A02 |

Also unconfirmed and marked in the lines: Registered Agents Inc.'s billing period; whether Expo's free build allowance renews monthly; Better Stack's and UptimeRobot's monthly-versus-yearly figures, read from page order; the Rekognition US East figure (AWS, not planned).

## 7. Checks

| Check | Result |
|---|---|
| `git diff --name-only f1653f194efd7e5ae0e145552cf42d111ee5cc12 HEAD` | `docs/testing/evidence/2026-11-19-m07-costed-list.md` only |
| The trusted classifier, `scripts/change_scope.py` taken from `origin/main` (`6edae78`) into the scratchpad, run with `python3 -I … --base f1653f1… --head <record commit> --merge-base` | `{"full": false, "reason": "ordinary-docs-only", "paths": ["docs/testing/evidence/2026-11-19-m07-costed-list.md"]}` (run on the record's commit and again after this table was added) |
| The totals recomputed in a script from the lines | launch 479.15, 1,000 members 501.21, 10,000 members 647.05; with Maker 80.15 and 102.21; one-time 125 (Delaware 135); yearly 295.81 (Delaware 635.81); Delaware's monthly difference (400 − 60) / 12 = 28.33 |
| The October Actions count, merged from the three segments' run lists, de-duplicated by run ID | 332 October runs; buckets and samples as in Line 16 |
| Independent rechecks of the prices | 15 sampled: 13 matched, 0 differed, Wyoming's PDF extracted by me and matched; Google's fee table and GitHub's allowance rechecked separately and confirmed |

## 8. Boundary

Only this record was written, on `claude/sharp-keller-j1uvsv`. On GitHub, only reads through the GitHub tools (workflow and run listings and job lists); no pull request, comment, review, re-run, dispatch or setting. Nothing in Notion. No account opened, no trial, form or contact; no credential, `AWS_*` value or token read; no provider API, HDE, Railway or Cloudflare call; no database; no `playwright install`, `eas`, native build or `migrate`. No legal or tax advice: published prices and terms only.
