# The first A05 decision message — establishment, launch countries and language, age assurance

- **Owner:** App Manager 8. Sent to Nathan in the manager session on 1 November 2026, as written below.
- **Revision 1, 1 November 2026.**
- **Why:** OD-50 sends the open A05 questions to Nathan in OD-32's form; DM-37 4.1 to 4.5 set this message's scope and terms, and its next consultation reads the message as sent. The matrix is [`docs/planning/store-legal-safety-requirements.md`](../planning/store-legal-safety-requirements.md); row IDs below are its rows.
- **Where the answer goes:** the owner-direction register (a new OD row), the carried-items file's SV1 and P07 sections, and G-01's Work Register row.
- **Deletion condition:** prune after Nathan's answer is in the register and the Dev Manager's next consultation has read this message.

---

**Three decisions for launch, before the identity slice (SV1).** Nothing breaks today: Glow has no users and the release block stands. SV1's brief needs D3, and the safety and privacy briefs (P07, P08) and the costed list (M07) need D1 and D2.

| # | Question | What it changes | Recommendation |
|---|---|---|---|
| D1 | Where is the business established, and are the store accounts yours or a company's? | Whether Glow needs UK or EU representatives; how much it reports to the UK's NCA; Apple's and Google's account rules | Tell me where it is established; hold the accounts in a legal entity |
| D2 | Which launch countries, and which language? | Which of the matrix's 320 rows bind, and who you must name and register | **The US first, all states, in English** |
| D3 | How is age checked? | SV1's age state; whether a UK launch brings children's duties | **A self-entered birth date plus the stores' age signals, behind a seam that can take a stronger check later** |

**What this message is and is not.** The facts are the matrix's, read from primary sources on 1 November 2026. It is not legal advice, it does not show that Glow is or would be compliant, and no cost is priced yet: the costed list (M07) prices each line before you approve it. The recommendations weigh only the duties a single operator (you, OD-23) must carry. They do not weigh your audience, where your users are, or your business reasons, and those can outweigh them.

## D1 — Where the business is established, and who holds the accounts

- **What it is:** the country (and, for the US, the state) where the business is or will be established, and whether the developer accounts and the service are in your own name or a legal entity's.
- **What breaks without it:**
  - a provider not established in the UK needs a UK representative (UK-27); one not established in the EU needs a DSA legal representative, who can be held liable (EU-06), and a GDPR representative (EU-34);
  - a "UK provider" (habitually resident in the UK, or a UK-formed entity) reports all detected child sexual abuse content to the NCA; others report only UK-linked content (UK-15);
  - Apple says apps that require sensitive user information should be submitted by a legal entity (AP-57; whether Glow "requires" it is a reading);
  - a personal Google account must run a closed test with 12 testers for 14 days before production (GP-58), and a personal trader's phone and address are shown to users (GP-59).
- **Options:**
  - **(a) Your own name:** no formation step; the 12-tester test; your personal contact details published as a trader; Apple's legal-entity line unmet.
  - **(b) A legal entity:** a formation step and its cost (not priced; M07 can add the line); a D-U-N-S number for Apple's organization enrolment; the entity's details published instead of yours; no 12-tester test.
- **Recommendation: (b), before any store account is created** (no account is opened before you approve its line, OD-50), because it meets Apple's line and avoids publishing your personal address. **And tell me the country of establishment**, which I need as a fact.

## D2 — Launch countries and language

- **What it is:** the first launch countries, chosen from your candidate list (OD-50), and the app's language.
- **What breaks without it:** P07's and P08's briefs cannot be scoped (each country brings its own assessments, notices and contacts), and M07 cannot price representatives or registrations.
- **The options** (rows that bind, people and registrations, representatives, the clocks one operator must meet; cost: not priced yet for any):

| Option | Rows that bind | Named people and registrations | Representatives | Clocks |
|---|---|---|---|---|
| **(a) The US, all states as one set** (store availability is set per country, AP-64; state duties attach per member) | Federal: NCMEC reporting (USF-01 to USF-07), intimate-image removal (USF-08 to USF-10), COPPA on actual knowledge (USF-11), a sign-up notice (USF-12), fraud-ban notices from 20 October 2027 (USF-18, USF-19). States: dating-safety notices, background-check disclosures and fraud-ban notices in ten states, Colorado's safety policy with its Attorney General filing and annual report, Connecticut's safety centre (UST-01 to UST-21); store age-signal laws, Texas now and California, Utah and Louisiana in 2027 (UST-32 to UST-35) | An NCMEC point of contact, registration recommended (USF-02); Colorado's filing (UST-20) | None found | Intimate images: 48 hours (USF-10); fraud-ban notices: 24 hours (USF-19; state laws now); CyberTipline: "as soon as reasonably possible" (USF-01) |
| **(b) The UK** | The Online Safety Act: an illegal-content risk assessment and a children's access assessment within three months (UK-03, UK-12), code measures with a named accountable individual (UK-11), intimate-image takedown (UK-05), reporting to the NCA (UK-15 to UK-19), trusted-flagger reports from 12 November 2026 (UK-23); UK GDPR, with explicit consent for orientation (UK-26, UK-29); the ICO fee (UK-44). With a self-entered birth date, the children's duties also follow (UK-12 to UK-14, UK-35): see D3 | The accountable individual (UK-11); the NCA's organisation administrator and emergency contact, registered before the first report (UK-16) | A UK representative unless UK-established (UK-27) | Intimate images: 48 hours (UK-05); NCA priority 1: "immediately", NCA requests: 7 days (UK-17); assessments: three months (UK-03, UK-12) |
| **(c) The EU, one or more Member States** | The DSA's Articles 11 to 14 and 16 to 18 (contact points, terms, notice and action open to anyone, statements of reasons, threats to life) (EU-04, EU-05, EU-07, EU-09 to EU-11); the GDPR, with explicit consent for orientation inferred from preferences (EU-33, EU-36), breach notice to every authority where users live (EU-45); whether the chat is an electronic communications service (G-12). Each Member State's own law is not in the matrix. As a micro-enterprise, Glow is outside DSA Articles 15 and 20 to 28 (EU-13) | DSA contact points for authorities and users (EU-04, EU-05) | A DSA legal representative and a GDPR representative unless EU-established (EU-06, EU-34) | Breach: 72 hours (EU-45); notices: "timely" (EU-09); threats to life: "promptly" (EU-11); removal orders from 14 June 2027 (EU-32) |
| **(d) A combination** | The union of the rows above | All of the above | As above | All of the above |

- **In every option:** Google's Child Safety Standards for dating apps, with a published standards page and a named child-safety contact (GP-18 to GP-23); Restrict Minor Access on Play (GP-11); Apple's and Google's trader declarations (AP-56, GP-59). NCMEC reporting (USF-01) states no territorial limit, so it may bind whatever you choose.
- **Language:** English only for the first launch, or English plus others. Availability in an EU national store, its language or currency counts towards "offering services" in the EU (EU-01).
- **Recommendation: (a), the US first, all states, in English.** On the matrix's facts it is the smallest set one operator can meet: the US rows are mostly notices and disclosures whose text the statutes give, one filing, and two clocks (48 and 24 hours); no representative is needed, and the state privacy laws' assessments and consent duties start only at their size thresholds (UST-44, UST-46 to UST-48). The UK adds two written assessments within three months, an "immediately" reporting clock and, with today's age check, the children's duties. The EU adds two representatives (unless EU-established), GDPR explicit consent and a DPIA, and national laws the matrix did not research. If D1 says the business is established in the UK or an EU country, I would revisit this, since the representatives fall away there.

## D3 — How age is checked

- **What it is:** the method that keeps under-18s out. Today a member enters a birth date (`onboarding-fixtures.md`, F02).
- **What breaks without it:** nothing until SV1's brief. If there is no answer by then, SV1 keeps a recorded age state with the method left open, and chooses none (DM-37 3.2).
- **How it links to D2:**
  - **UK:** a self-entered date "is not to be regarded as age verification or age estimation" (UK-13), so it cannot support a conclusion that children cannot use the service (UK-12). A UK launch on it brings the children's risk assessment and safety duties (UK-14) and, if likely accessed by children, the Age Appropriate Design Code (UK-35).
  - **US:** no federal age-verification duty for dating apps was found (USF-11). The state store laws use the stores' age data (UST-32 to UST-35; Apple's Declared Age Range, AP-14 to AP-16). California's SB 976 asks for a "reasonably determined" age only if the feed counts as addictive (UST-37), and New York's SAFE Act similarly (UST-38).
  - **EU:** the Commission's age-assurance guidelines apply only once Glow is no longer micro or small (EU-24); any method needs a DPIA (EU-25), and AI facial age estimation is biometric categorisation (EU-62).
- **Options:**
  - **(a) A self-entered birth date plus the stores' age signals** where the law requires them, and Google's Restrict Minor Access everywhere (GP-11, GP-12). Cost: native work in P09.2, no vendor. For the UK, it brings the children's duties.
  - **(b) Verified or estimated age for every member** (a third-party service). Cost: a vendor (not priced; an M07 line), a DPIA, friction at sign-up. It supports the UK conclusion that children cannot access the service.
  - **(c) (a) everywhere, and (b) for UK members only**, if the UK is a launch country.
- **Recommendation: (a), with SV1 holding the age state behind a seam** so that (b) or (c) can be added without rework. If you choose the UK in D2, then (c).

## Whether to take legal advice

That is your decision (DM-31), and this message takes no side. The decisions above touch readings the sources leave to interpretation:
- how the DSA classifies Glow's features (EU-02);
- whether orientation revealed indirectly, by gender and "who I want to see", is special-category data (EU-36, C-184/20);
- whether Glow is a California "social media platform" (UST-49, UST-50);
- whether the chat is an electronic communications service under EU law (G-12);
- whether Glow's recommendations count as an "addictive feed" (UST-37 to UST-39);
- three rows marked UNCONFIRMED in part: UK-05 (whether the UK's 48-hour duty is delayed), UST-36 (Alabama's enactment) and GP-11 (Google's original compliance date).

**The rest of A05 comes later,** in two messages: before SV2's brief, the preference taxonomy, resurfacing and rematch, and the history policy; before P07's brief, retention and moderation operators.

**DECISION NEEDED:** your answer to D1 (the country of establishment, and (a) or (b)), D2 ((a) to (d), and the language) and D3 ((a) to (c)). A reply like "D1: <country>, b; D2: a, English; D3: a" is enough.

---

## Follow-up (1 November 2026)

**Nathan's answer:** "1) I will establish a legal entity in the US. Does this mean we can't publish in the EU or UK? 2) Same questions 3) This will depend on where I can launch"

**The manager's reply, as sent:**

No. A US company can publish in the UK and the EU; it carries more duties there, not a bar. Nothing in the matrix stops a US entity from launching in either.

| | What a US entity adds |
|---|---|
| **UK** | A UK representative for UK GDPR (UK-27). Its exemption covers only occasional processing without large-scale special-category data, and Glow's preference fields reveal orientation (UK-29), so expect to need one. The Online Safety Act still applies to a provider outside the UK with UK links (UK-02). As a non-UK provider, Glow reports to the NCA only UK-linked content (UK-15). Whether a controller outside the UK pays the ICO fee is unconfirmed (UK-44) |
| **EU** | A DSA legal representative, in a Member State where Glow offers services, notified to its regulator, named publicly and liable for Glow's DSA duties (EU-06). A GDPR representative, on the same exemption test (EU-34). A breach is notified to every EU authority where affected users live (EU-45). Each Member State's own law is not in the matrix |

Representative services are not priced yet; M07 would price them before you approve any line.

- **D1** is answered: a US legal entity, option (b).
- **D2's options are unchanged, and my recommendation stands, with D1 making it stronger: (a), the US first, all states, in English.** As a US entity, the US option needs no representative; the UK and the EU each add one or two, plus their own assessments and notices. A UK or EU launch can follow later: the matrix's rows stay ready for it.
- **D3 follows from D2,** as you say: the US alone, or the EU alone while Glow is micro, takes (a), a self-entered birth date plus the stores' age signals behind SV1's seam; any option with the UK takes (c), verified or estimated age for UK members.

**DECISION NEEDED:** D2 only. A reply like "D2: a, English" is enough; D3 then follows as above, and I record D1 to D3 as one owner direction.

(Nathan's next message interrupted the reply above during its last sentence.)

**Nathan:** "I will not be able to establish legal resident status in the UK or EU right away. I need to work within that limitation"

**The manager's reply, as sent:**

That limitation fits the recommendation, and it does not close the UK or the EU later.

- **Neither needs you to be resident.** The UK and EU representatives are a person or firm already established there that the US company appoints in writing (UK-27, EU-06, EU-34), usually a paid service (not priced yet; M07). So a later UK or EU launch stays open without residency.
- **What it settles:** Glow is a US company with no UK or EU establishment. A launch there would need those representatives, and Glow would report to the NCA only UK-linked content (UK-15).
- **So D2 stays (a), the US first, all states, in English,** and D3 is then (a): a self-entered birth date plus the stores' age signals, behind SV1's seam.

**DECISION NEEDED:** shall I record D2 as (a), the US first, all states, in English? A "yes" records D1 to D3 as one owner direction; otherwise name the option.

**Nathan:** "tell me what I need for EU access at least"

**The manager's reply, as sent:**

**For an EU launch, a US company with no EU presence needs two appointed representatives, about a dozen documents and processes, and one legal reading on the chat.** While Glow stays a micro-enterprise, most of the heavier EU platform rules do not apply. From the matrix (EU rows); not legal advice, and it does not show compliance.

| Area | What you need | Rows |
|---|---|---|
| **People you appoint** | A Digital Services Act legal representative in an EU country where Glow is offered: a written mandate, notified to that country's regulator, named publicly, and liable for Glow's DSA duties. A GDPR representative in a country where your users are, named in the privacy notice | EU-06, EU-34 |
| **Published contacts** | One electronic contact point for EU authorities, with its languages; one for users that reaches a person | EU-04, EU-05 |
| **In the stores** | The trader declarations, in both stores | AP-56, GP-59 |
| **Documents** | Terms and community rules that describe moderation and any automated tools; a privacy notice; records of processing; a DPIA (a data protection impact assessment) before processing starts, since orientation data, matching and age checks are high-risk; contracts with every processor (chat, storage, hosting, email); a transfer basis for each US vendor (the EU-US Data Privacy Framework, or standard contractual clauses) | EU-07, EU-38, EU-43, EU-46, EU-42, EU-48 |
| **Safety processes** | A report form open to anyone, members or not, with an acknowledgment and a reasoned decision; a statement of reasons for every removal, hidden profile or suspension; acting on authority orders; telling the police promptly about threats to life or safety | EU-09, EU-10, EU-03, EU-11 |
| **Privacy features** | Explicit, withdrawable consent for the fields that reveal orientation (gender plus "who I want to see"); a lawful basis for each purpose; access, export, correction and deletion within one month; consent before non-essential SDKs or device access; private-by-default settings | EU-36, EU-35, EU-37, EU-39, EU-53, EU-50, EU-41 |
| **Incidents** | A breach runbook: 72 hours, to every EU regulator where affected users live | EU-45 |
| **Numbers** | The ability to give EU monthly users on request; evidence that Glow is a micro-enterprise | EU-18, EU-13 |
| **Access** | No blocking or different terms between EU countries | EU-65 |

- **One open reading:** whether Glow's chat counts as an electronic communications service under EU law. If it does, confidentiality, security-incident and notice rules for messaging also apply (EU-30, EU-52, EU-63, EU-64; gap G-12). No source settles it, so it is a question for a lawyer, if you take advice.
- **Not needed while Glow is a micro-enterprise:** transparency reports, an internal complaints system, trusted flaggers, the minors' rules and their age-verification guidelines, recommender transparency, and the DSA's dark-pattern rule (EU-08, EU-14 to EU-24); the Accessibility Act (EU-60). Consumer-law duties apply only with paid features (EU-54 to EU-59).
- **Not in the matrix:** each EU country's own laws.
- **Cost:** the two representatives and the DPIA work are not priced yet (M07).
- **Where the work sits:** the safety processes in P07, the privacy work and representatives in P08, already routed (gaps G-09, G-11, G-15).

**D2, with this:** (a) the US only first, the EU later; or (d) the US and the EU together. **I recommend (a), with the EU as the second launch** once P07 and P08 have built the items above and M07 has priced the representatives. The EU items are mostly documents and processes Glow needs anyway, and they become a launch decision you can take later, under PF01's new release gate. D3 is (a) either way: while Glow is micro, the EU's age-verification guidelines do not apply, though any age check needs a DPIA (EU-24, EU-25).

**DECISION NEEDED:** D2, (a) or (d). A reply of "a" or "d" is enough, and I record D1 to D3 as one owner direction.

**Nathan:** "so I need two people"

**The manager's reply, as sent:**

**Two appointments, not two hires.** Each is a person or firm already established in the EU that Glow's US company appoints in writing, usually a paid representative service (EU-06, EU-34):

- **the DSA legal representative,** in an EU country where Glow is offered, named publicly and liable for Glow's DSA duties;
- **the GDPR representative,** in an EU country where your users are, named in the privacy notice.

Whether one firm may hold both roles is not in the matrix. M07 checks it when it prices them, since a single provider would be one contract. Everything else on the list is yours to run: you can be both published contact points (EU-04, EU-05), as you hold every other role (OD-23).

**DECISION NEEDED:** D2, "a" (the US first, the EU later) or "d" (the US and the EU together).

**Nathan:** "so I cannot take on both roles myself?"

**The manager's reply, as sent:**

**No, not while you are outside the EU.** Both laws place the representative in the EU:

- **GDPR:** *"the controller or the processor shall designate in writing a representative in the Union"* (EU-34);
- **DSA:** a provider with no EU establishment designates *"a legal or natural person to act as their legal representative"* in an EU country where it offers its services (EU-06).

So someone established in the EU has to hold both roles. It can be an individual rather than a firm: the DSA says "legal or natural person". But the DSA representative can be held liable for Glow's DSA duties (EU-06), so whoever takes it on carries that risk. A later UK launch works the same way: *"a representative in the United Kingdom"* (UK-27).

**DECISION NEEDED:** D2, "a" (the US first, the EU later) or "d" (the US and the EU together).

**Nathan:** "ok, then we are stuck with the US for now, then"

**Recorded** as OD-55: D1 (b), a US legal entity; D2 (a), the US, all states, in English, for now; D3 (a), by his rule that it follows the geography.
