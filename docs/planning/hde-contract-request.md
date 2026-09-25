# HDE contract request: what the app needs from HDE's supported contract

- **Status:** written on 25 September 2026 by App Manager 3, for Nathan to take into HDE's own process (OD-23). No delivery date is set yet.
- **Who holds each role.** Nathan is the Product Owner, the HDE owner and the app's integration owner (OD-23): *"there is only one human involved in any of this, me"*.
  - He takes this request into HDE's own process, outside this repository and outside the app sessions' authority, and sets the delivery date there.
  - HDE's own sessions and canon produce the contract.
- **What this document is not.**
  - It is not an HDE contract, specification or endpoint list. It lists the questions the app needs answered. HDE decides the answers and governs the contract's text (PF00: HDE behavior and contracts are *"referenced, never rewritten by app documentation"*).
  - Nothing was read from HDE's systems to write it. Its facts come from PF01 §5's earlier source snapshot and from the app's own documents.
- **What waits on it:**
  - A01 and A07 (PF01 §10);
  - P11B's live HDE checks (PV01 and PV02 in the [P11 deferred acceptance cases](../testing/p11-deferred-acceptance.md));
  - P11C's HDE connection.

  Nothing before P11 waits on it. The app builds against fixtures until then.
- **Sources:**
  - PF01 §5 "Before live integration", A01, A07 and R02;
  - the [provisional HDE seam](../architecture/provisional-hde-seam.md) and its "Adapter activation record still required";
  - the A01 and A07 rows in [provider conformance](../architecture/provider-conformance.md#dependencies-and-real-proofs-still-required);
  - the Dev Manager's [A7 consequences](../continuity/dev-manager/reviews/2026-09-25-owner-answers-to-dm-01-dm-02.md) and [addendum](../continuity/dev-manager/reviews/2026-09-25-owner-answers-addendum.md).

## 1. What the app knows today

- **The earlier snapshot** (PF01 §5):
  - The HDE HTTP adapter and CLI/API reference described `POST /api/reader?v=1`, with `a_id` and `b_id` UUID inputs and a closed, numeric-free public Reader response.
  - Eligible public results include a harmony band.
  - The development sampler is not a production recommendation API.
  - This was a snapshot of an unfinished system, not a commitment to a final contract.
- **The app's rules,** which the contract has to fit (PF01 §5 and D08). The app never:
  - reads undocumented HDE tables;
  - scrapes CLI diagnostics;
  - opens development routes;
  - reimplements compatibility math;
  - adds numeric scores to the public Reader v1 shape.

  If only bands are available, ranking works at band granularity with documented app-owned secondary criteria. A richer interface needs an authorized engine contract, made in HDE's own system.
- **The app's side is ready for an adapter.**
  - Four app-owned ports, with fixtures and conformance tests: `BirthInput` / `ChartResolver`, `CompatibilityProvider`, `CompatibilityProjection` and `EngineLifecycle` ([provisional HDE seam](../architecture/provisional-hde-seam.md)).
  - One app-owned adapter will implement the supported contract. The ports adapt to HDE; HDE does not reproduce them.

## 2. The questions

HDE's contract answers each question below. **"Not supported" is a complete answer:** the app designs around it and infers nothing from silence. The IDs let the receipt (section 6) map each answer to HDE's text.

### 2.1 Identity, release and environments

| ID | Question |
|---|---|
| C01 | What is the contract's name and version, and how do versions change? Which changes are compatible, and what notice comes before a breaking one? |
| C02 | Which HDE release or commit does the contract describe? |
| C03 | Where is it served? The app needs a test environment for P11B and the production environment for P11C. If no test environment exists, what narrowly authorized read or test-data protocol applies before any live call (PF01 P11B)? |
| C04 | How does a response identify the engine and contract versions that produced it? |

### 2.2 Access

| ID | Question |
|---|---|
| C05 | How does the app authenticate? Give the mechanism only. Credentials are delivered outside documents and source control. |
| C06 | Which operations and data may the app use? Which reads, which writes (for example, creating a chart), and which are forbidden? |
| C07 | How do the app's services reach HDE? They are in the same Railway project (ADR 0002), but that confers no API permission, and the app changes nothing in HDE's networking. |
| C08 | Who issues, rotates and revokes the app's credential, and how is a compromised credential revoked? |

### 2.3 Birth input and chart identity (`BirthInput` / `ChartResolver`)

| ID | Question |
|---|---|
| C09 | Which input fields are accepted: civil date, local time and place? What is the authority for place and time zone? |
| C10 | How are an uncertain or missing birth time and an ambiguous place handled? The app preserves what the user entered, never guesses a time and never converts local time to UTC without a verified place and time zone. |
| C11 | What chart identifier does HDE return? The app stores it as an opaque reference, never as its own account ID. |
| C12 | Are chart creation and update idempotent, and how? When a user corrects their birth input, is it a new chart or an update, and which identity survives? |
| C13 | Can a chart be pending, and what signals completion? |

### 2.4 Compatibility output (`CompatibilityProvider` / `CompatibilityProjection`)

| ID | Question |
|---|---|
| C14 | Which operations are supported: a single pair, a batch or a candidate set? What is the largest batch? |
| C15 | Which output fields and granularity are supported? What band values exist, and what do they mean? Is any finer ordering authorized (A07)? |
| C16 | Is the output for (A, B) the same as for (B, A)? The app keeps direction until symmetry is guaranteed. |
| C17 | Which fields and wording may users see, and which must stay internal? |
| C18 | What does HDE mean by "eligible"? The app runs its own eligibility first and rechecks it; a compatibility result never creates a match or permits chat. |

### 2.5 Reliability and throughput

| ID | Question |
|---|---|
| C19 | What rate limits and quotas apply, and what throughput can the app plan on (A07)? |
| C20 | What timeouts and latency should the app expect? |
| C21 | What errors can occur? Which are retryable, and what retry policy does HDE expect: backoff and a maximum number of attempts? |
| C22 | Which operations are idempotent, and by what key? |
| C23 | How is a partial batch result reported? |
| C24 | Is there a status or health signal the app can check? One person operates both systems (OD-23), so automated signals matter. |

### 2.6 Data rights: caching, retention and deletion (`EngineLifecycle`)

| ID | Question |
|---|---|
| C25 | What may the app store from HDE's output, for how long, and what invalidates it? The app's cache keys include input, engine and contract versions. |
| C26 | Which data does HDE own, and which does the app own? What does HDE keep about the app's users? |
| C27 | When a user deletes their account, what may the app ask HDE to do? Which operation does it call, and what evidence shows completion? The app never assumes a deletion right. |
| C28 | How is a chart that HDE also uses elsewhere handled on deletion (a shared chart)? It must not be destroyed through assumed ownership (PV02). |
| C29 | How does HDE protect birth details, and does it log them? Users' birth details are private in the app. |

## 3. What the app commits to

HDE can rely on these, whatever the answers:

- It uses only the supported contract: no tables, diagnostics or development routes (PF01 §5).
- It changes nothing in HDE: no source, canon, database objects, roles, services, secrets, DNS or networking. The boundary is protected by effect (D08).
- It keeps its data in its own logical database, with no grant on HDE's database (ADR 0004).
- It stays within the agreed rate limits and retries only as the contract allows.
- It shows users only the fields the contract allows, with no numeric scores. Fixture labels never reach users as real Human Design results.
- It keeps credentials out of source, documents, logs and Notion.
- It records the contract version and HDE release with every stored result (PF01 §5).

## 4. How the contract is delivered (OD-23)

1. **Nathan** takes this request into HDE's own process and sets the delivery date there. Until then, A01 and A07 stay blocked with "date not yet set".
2. **HDE's own sessions and canon** produce the versioned contract. HDE governs its text.
3. **Nathan receives it** as the app's integration owner, and also as the Product Owner.
4. **The app records a receipt** in repository Markdown (section 6). If a verbatim copy is wanted, it goes under `docs/planning/sources/`, marked non-governing.
5. **Adapter work and the P11B live checks start only after the receipt,** and only within the access it names.

## 5. When the app treats the contract as delivered

- Every question in section 2 has an answer, or an explicit "not supported".
- The contract version and the HDE release or commit are named.
- A test environment, or an authorized test-data protocol, exists for P11B.
- The access is described by name only, and Nathan confirms the credential exists. It is delivered outside the repository.
- Any conflict with PF01 §5's rules is resolved before adapter work starts. One example would be numeric scores in a user-facing response.

## 6. The receipt

When the contract arrives, the app creates `docs/architecture/hde-contract-receipt.md`, holding:

- the contract version, and the HDE release or commit;
- the environments;
- the authorized access, by name only, with no secret values;
- the delivery date, and the delivery itself: from Nathan, as HDE owner, to Nathan, as integration owner and Product Owner;
- each answer from section 2, cited by its place in HDE's text, not rewritten;
- the adapter mapping against the four ports, and any gaps.

This file then records the delivery in its status line and links the receipt.

## 7. Status

| Item | State |
|---|---|
| This request | Written on 25 September 2026. Waiting for Nathan to take it into HDE's process |
| Delivery date | Not yet set. Nathan sets it in HDE's process |
| A01 and A07 | Blocked: date not yet set |
| P11B live HDE checks (PV01, PV02) | Gated on the receipt |
