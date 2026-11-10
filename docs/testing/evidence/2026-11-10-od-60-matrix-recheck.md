# OD-60 — Recheck of the matrix rows the chosen taxonomy and the phone's location touch

- **What:** the recheck that [the matrix](../../planning/store-legal-safety-requirements.md), section 10, asks for "when Nathan … chooses … a preference taxonomy" and when "device location … is proposed". Nathan's answer to the second A05 message ([OD-60](../../continuity/owner-directions.md), 10 November 2026) does both: four two-way list fields (gender, orientation, looking for, relationship status), and location by a city or region the member chooses or the phone's approximate location. The carried-items file puts this recheck before SV2's brief ("Carried to SV2").
- **Who and when:** App Manager 10, on 10 November 2026, between 00:31 and 00:36 UTC. This is a records reading of public pages, not an implementation or review session.
- **Method:** the section 10 rule. Each row's source is re-read, the row's date is updated, the IDs stay as they are, and the reading is recorded here.
  - `curl` fetched each source into its own directory in the manager's scratchpad. A Python script run with `-I`, kept outside that directory, stripped the HTML tags; `pdftotext` read the PDFs.
  - A second script took each row's quotation, split it at its ellipses, and searched for each fragment as one continuous string in the stripped text. Two fragments matched only after a space the tag stripping had added (GP-50's "( ACCESS_FINE_LOCATION )", UST-45's "541.002 (a)(3)"), and were then read in place.
  - The fetched files were hashed and not committed.
- **Research, not legal advice** (the matrix's opening note applies).

## The rows

| Group | Rows |
|---|---|
| The taxonomy (sensitive data, declarations, consent) | AP-23, GP-25, GP-28, USF-13, UST-42, UST-44, UST-45, UST-46, UST-47, UST-48 |
| The phone's location | AP-23, AP-49, GP-25, GP-46, GP-49, GP-50, UST-41, UST-42 |

AP-50 (the app may not require location) was rechecked on 8 November 2026 (the [P06.3 recheck](2026-11-08-p06-3-matrix-recheck.md)) and is not repeated.

## The sources

| Source | URL fetched | Final URL | HTTP, bytes | SHA-256 of the fetched file | Page date |
|---|---|---|---|---|---|
| Apple, App privacy details | `https://developer.apple.com/app-store/app-privacy-details/` | the same | 200, 134,919 | `2532a2171760c88755f3aa185190bfdd068a251c14e9a0fd39c2798ac8ff497e` | none given |
| Apple App Review Guidelines | `https://developer.apple.com/app-store/review/guidelines/` | the same | 200, 240,818 | `2c34dba8608f6faec44f12d76b988003dbd184341b0d68c14f912f89b8577bb8` | "Last Updated: October 16, 2026", the revision P09.3a read |
| Apple, `NSLocationWhenInUseUsageDescription` (DocC JSON) | `https://developer.apple.com/tutorials/data/documentation/bundleresources/information-property-list/nslocationwheninuseusagedescription.json` | the same | 200, 17,942 | `3ed91a9b9232feb442cbcc967072e1a047c2e1b019922d579233e7d129e10e5c` | none given |
| Google Play, Data safety (answer 10787469) | `https://support.google.com/googleplay/android-developer/answer/10787469?hl=en` | the same | 200, 1,745,526 | `e3e63134b7012b6b2543e51cbe22e418b4437f42e1c0c31c3c6decea7fa764ec` | none given |
| Google Play, User Data (answer 10144311) | `https://support.google.com/googleplay/android-developer/answer/10144311?hl=en` | the same | 200, 1,696,690 | `f13d38f0c8f924185bb2c99555e8531ad12e310e58edad1e87c1fa867d9409b2` | none given |
| Google Play, Permissions (answer 16558241) | `https://support.google.com/googleplay/android-developer/answer/16558241?hl=en` | the same | 200, 1,728,037 | `fe474cf8d699d5922cdbc30804ea1c962dbcc3b07c6fc046a180076393d4036d` | none given |
| Google Play, foreground location (answer 17033915) | `https://support.google.com/googleplay/android-developer/answer/17033915?hl=en` | the same | 200, 1,669,305 | `6fc4584c96204a48f7484457e9ab1c2a9b3fde8048bfc8af7486fdd58c51d451` | none given |
| Google Play, policy update (answer 18100766) | `https://support.google.com/googleplay/android-developer/answer/18100766?hl=en` | the same | 200, 1,642,649 | `8f5cedec310e9f67e2137255563aa4502554b378fbad7440ab3fc93d42500c17` | none given |
| 15 U.S.C. 45 | `https://www.govinfo.gov/link/uscode/15/45?link-type=html&year=2024` | `https://www.govinfo.gov/content/pkg/USCODE-2024-title15/html/USCODE-2024-title15-chap2-subchapI-sec45.htm` | 200, 47,198 | `28de76e074dde70c74930d24738fda83a837c04bba6304c148051d1600679546` | the 2024 edition |
| FTC, "Marketing Your Mobile App" | `https://www.ftc.gov/business-guidance/resources/marketing-your-mobile-app-get-it-right-start` | the same | **404**, 1,301 | `6cb6ddd1f7eefd58b6094bfb287c9fafa16b34eb1dfbf27416431220d9e45e5e` | — |
| CCPA, the statute, as posted by the California Privacy Protection Agency | `https://cppa.ca.gov/regulations/pdf/ccpa_statute.pdf` | the same | 200, 772,399 | `0beb83ccf73d82ede066f7e4154952435484410f748da09ac4329ed9afe6a43f` | "effective 01/01/2025 – SB 1223, AB 1008, AB 1824 update; posted to cppa.ca.gov January 2025" |
| CCPA regulations (11 CCR), effective 1 January 2026 | `https://cppa.ca.gov/regulations/pdf/ccpa_statute_eff_20260101.pdf` | the same | 200, 615,548 | `8d57eba97a7fe13346b7827d0131e1ab84dc110c6ff20daa6fa6ec4a4329d0fe` | "Effective 1/1/2026" |
| Texas Business and Commerce Code, chapter 541 | `https://tcss.legis.texas.gov/resources/BC/htm/BC.541.htm` | the same | 200, 80,485 | `1f56ef0a23bae698ba6234921a4dded70a2444059214093791dcc8d7797591be` | none given |
| Virginia Code §59.1-578 | `https://law.lis.virginia.gov/vacode/title59.1/chapter53/section59.1-578/` | the same | 200, 35,767 | `35ae4387695a1d37a09491a3e492e200b1b084e30d14212bbf3ecca60102fd38` | none given |
| Virginia Code §59.1-575 (definitions) | `https://law.lis.virginia.gov/vacode/title59.1/chapter53/section59.1-575/` | the same | 200, 41,065 | `97d7d89552688aee6d0af30e9988d6ea4cd2d95b29a6275250c98be0b55a2663` | none given |
| Colorado Revised Statutes 2024, title 6 | `https://content.leg.colorado.gov/sites/default/files/images/olls/crs2024-title-06.pdf` | the same | 200, 2,108,494 | `560ff6d64b5afdf2a3bc5ac917a392269d16270a029b252ff8f7957deb38b423` | "Colorado Revised Statutes 2024", an uncertified printout |

**What could not be read:**
- **California's legislature site** refused this environment (`403` for `codes_displaySection.xhtml`, §1798.121 and §1798.140), as it refused P09.3a's session. UST-42 was read instead from the agency's posted copy of the statute, above.
- **The FTC site** refused this environment for every page tried:
  - the guide's page and two FTC-hosted PDF copies of it (`plain-language/pdf-0140_marketing-your-mobile-app.pdf` and `bulkorder.ftc.gov/…/829a_marketing_your_mobile_app.pdf`) each returned the same 1,301-byte "Page Not Found";
  - another FTC page (`/business-guidance/privacy-security`) returned `403`.

  A web search still lists the guide's page at its URL, so the 404 is read as a refusal of this client, not a removal.

## The readings

**AP-23: confirmed.**
- *"Such as racial or ethnic data, sexual orientation, pregnancy or childbirth information, disability, religious or philosophical beliefs, trade union membership, political opinion, genetic information, or biometric data"* (Sensitive Info).
- **The two location types:**
  - *"Precise Location: Information that describes the location of a user or device with the same or greater resolution as a latitude and longitude with three or more decimal places"*;
  - *"Coarse Location: Information that describes the location of a user or device with lower resolution than a latitude and longitude with three or more decimal places, such as Approximate Location Services"*.
- Apple's list names no gender, relationship-status or "looking for" type.

**AP-49: confirmed.**
- Section 5.1.5: *"Ensure that you notify and obtain consent before collecting, transmitting, or using location data. If your app uses Location Services, be sure to explain the purpose in your app"*.
- `NSLocationWhenInUseUsageDescription`: *"A message that tells people why the app is requesting access to their location information while the app is running in the foreground."* *"This key is required if your iOS app uses APIs that access the user's location information while the app is in use."*
- The manual fallback rests on 5.1.1(iv) ("Where possible, provide alternative solutions for users who don't grant consent"), confirmed on 8 November for AP-50.

**GP-25: confirmed.**
- The quotation: *"If you are purposefully collecting a data type during the collection of another data type, you should disclose both."*
- **The types OD-60's fields fall under:**
  - *"Sexual orientation: Information about a user's sexual orientation."*
  - *"Other info: Any other personal information such as date of birth, gender identity, veteran status, etc."*
  - *"Approximate location: User or device physical location to an area greater than or equal to 3 square kilometers, such as the city a user is in, or location provided by Android's ACCESS_COARSE_LOCATION permission."*
  - *"Precise location: User or device physical location within an area less than 3 square kilometers, such as location provided by Android's ACCESS_FINE_LOCATION permission."*

  So in Google's form, a city the member chooses is "Approximate location", as the phone's coarse location is.

**GP-28: confirmed.** *"Handle all personal and sensitive user data securely, including transmitting it using modern cryptography (for example, over HTTPS)."*

**GP-46: confirmed.** *"Request permissions and APIs that access sensitive information to access data in context (via incremental requests), so that users understand why your app is requesting the permission. Use the data only for purposes that the user has consented to."*

**GP-49: confirmed.**
- *"Apps should request the minimum scope necessary (for example, coarse instead of fine, and foreground instead of background) to provide the current feature or service requiring location"*.
- Answer 17033915 adds: *"Location permissions may not be requested for the sole purpose of advertising or analytics, and device location data may never be sold."*

**GP-50: confirmed.**
- *"All apps requesting precise location ( ACCESS_FINE_LOCATION ) must complete a declaration in the Play Console to demonstrate access needs and justify why the location button or coarse location is insufficient."*
- Answer 18100766: *"For apps targeting Android 17 (API 37+), this includes mandatory use of the Android location button for one-time or infrequent location requests."*
- The location button is the minimum scope for precise, one-time location. OD-60 asks for approximate location only, so neither the declaration nor the button applies to it.

**USF-13: confirmed in part.**
- The statute: *"unfair or deceptive acts or practices in or affecting commerce, are hereby declared unlawful"* (15 U.S.C. 45(a)(1)).
- **The guidance part is UNCONFIRMED at this recheck:** "FTC guidance asks for affirmative consent before collecting sensitive data" stands as P09.3a read it on 1 November. The FTC site could not be read from this environment (above).
- It is re-read from an open environment, as the matrix's section 10 asks for unreadable sources (OD-43).

**UST-41: confirmed.** *"A controller that offers any online service, product, or feature to a consumer whom the controller actually knows or willfully disregards is a minor shall use reasonable care to avoid any heightened risk of harm to minors"* (C.R.S. §6-1-1308.5). Glow is 18+; the row stays as it is.

**UST-42: confirmed, from the agency's posted copy of the statute.**
- §1798.121: *"A business that uses or discloses a consumer's sensitive personal information for purposes other than those specified in this subdivision shall provide notice to consumers, pursuant to subdivision (a) of Section 1798.135, that this information may be used, or disclosed to a service provider or contractor, for additional, specified purposes and that consumers have the right to limit the use or disclosure of their sensitive personal information."*
- **§1798.140, sensitive personal information:** *"(C) Personal information collected and analyzed concerning a consumer's sex life or sexual orientation."*
- **§1798.140, precise geolocation:** *"'Precise geolocation' means any data that is derived from a device and that is used or intended to be used to locate a consumer within a geographic area that is equal to or less than the area of a circle with a radius of 1,850 feet, except as prescribed by regulations."*

**UST-44: confirmed.** *"Business B provides a mobile dating application. Business B plans to disclose consumers' precise geolocation and the ethnicity and medical information the consumers provided in their dating profiles to Business B's analytics service provider. Business B must conduct a risk assessment because it plans to process sensitive personal information of consumers."*

**UST-45: confirmed.**
- §541.107(a): *"A person described by Section 541.002(a)(3) may not engage in the sale of personal data that is sensitive data without receiving prior consent from the consumer."*
- **§541.001, sensitive data:** *"personal data revealing racial or ethnic origin, religious beliefs, mental or physical health diagnosis, sexuality, or citizenship or immigration status; … (D) precise geolocation data"*.
- **Precise geolocation data:** *"information derived from technology, including global positioning system level latitude and longitude coordinates or other mechanisms, that directly identifies the specific location of an individual with precision and accuracy within a radius of 1,750 feet"*.

**UST-46: confirmed.** *"process the sensitive data of a consumer without obtaining the consumer's consent"* (§541.101(b)(4)).

**UST-47: confirmed.**
- §59.1-578: *"Not process sensitive data concerning a consumer without obtaining the consumer's consent"*.
- **§59.1-575, sensitive data:** *"Personal data revealing racial or ethnic origin, religious beliefs, mental or physical health diagnosis, sexual orientation, or citizenship or immigration status; … 4. Precise geolocation data."*
- **Precise geolocation data:** *"information derived from technology, including but not limited to global positioning system level latitude and longitude coordinates or other mechanisms, that directly identifies the specific location of a natural person with precision and accuracy within a radius of 1,750 feet"*.

**UST-48: confirmed.**
- *"A controller shall not process a consumer's sensitive data without first obtaining the consumer's consent"*.
- **§6-1-1303, sensitive data:** *"Personal data revealing racial or ethnic origin, religious beliefs, a mental or physical health condition or diagnosis, sex life or sexual orientation, or citizenship or citizenship status; (b) Genetic or biometric data that may be processed for the purpose of uniquely identifying an individual; (c) Personal data from a known child; or (d) Biological data."*
- **Precise geolocation:** in the 2024 printout, Colorado's list of sensitive data does not include precise geolocation; the statute defines it separately, within 1,750 feet, and uses it in the minors' duties (UST-41).

## What it shows for OD-60

Facts only; each reading is the Dev Manager's, at SV2's brief, and whether to take legal advice is Nathan's (DM-31).

- **Orientation:**
  - it is a named sensitive category in Apple's label (AP-23), Google's form (GP-25) and all four state laws: "sexual orientation" in California, Virginia and Colorado; "sexuality" in Texas;
  - OD-60's handling (consent at entry, never sold, declared in both stores) meets each consent and no-sale rule above as written.
- **Relationship status and "looking for":**
  - neither store names a type for them; Google's "Other info" ("Any other personal information") holds them, with gender identity;
  - California's and Colorado's lists name "sex life" (UST-42, UST-48). Whether either field concerns a member's "sex life" is a reading. That OD-60 handles relationship status like orientation is a choice that does not depend on the reading.
- **The location filter:**
  - in Google's form a chosen city is "Approximate location" ("such as the city a user is in"), declared like the phone's coarse location (GP-25);
  - in Apple's label, location coarser than three decimal places is "Coarse Location" (AP-23);
  - the three state laws define precise geolocation as data derived from a device or technology that locates a person within 1,850 feet (California) or 1,750 feet (Texas, Virginia). Whether a city or region the member chooses, or the phone's approximate location, falls inside those definitions is the reading the second A05 message named (UST-42);
  - Google's approximate location is an area of at least 3 square kilometres. Approximate location needs no Play Console declaration and no location button (GP-50), and on Apple it needs a when-in-use purpose string and consent first (AP-49).

## What changed in the matrix

- **The rows:**
  - each of the 15 rows adds "rechecked 2026-11-10 (OD-60)" after its read date;
  - UST-42's source adds the agency's posted copy;
  - USF-13's marks its guidance part UNCONFIRMED at this recheck;
  - GP-25's, AP-49's and GP-49's current-state cells now name OD-60.
  - No requirement, quotation, owner or ID changed.
- **The header's "Research date" bullet** names this recheck and its record.

## Limits

- **One reading of each source,** at the time above.
- **Only these rows were rechecked.** The others in section 9's "preference taxonomy" paragraph are UK and EU rows, which do not bind while the US is the only launch country (OD-55).
- **The stripping is a script, not a browser render.** Each quoted passage was found as one continuous string in the stripped text, except the two matched after a stripping space. The hashes identify the files fetched then, which were not kept; a hash does not re-identify a page that changes on every fetch (DM-44), but the quoted passages do.
- **The FTC guidance stays unread** until an open environment reads it.
