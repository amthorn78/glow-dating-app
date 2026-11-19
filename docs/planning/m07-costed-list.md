# M07 — The costed list of completion's accounts and services

- **Work ID:** M07 (cross-cutting; the owner's track, O1 in M09's order).
- **Status: done.** The record is integrated (merge `817ce5e`), with "Manager verification of M07". **Nathan approved no line** (OD-77, 19 November 2026): no cost now; the entity, and the accounts and domain that need it, deferred; Railway and WordPress hosting already available; Stream's Maker account assumed; the Actions line deferred while the repository is public.
- **Owner:** Nathan Amthor approves each line (OD-50). **Manager:** App Manager 12. **Research:** one session, started by Nathan.
- **Revision 1, 19 November 2026.**
- **Starting point:** the manager-branch commit the prompt names. `main` is at `6edae78`.
- **Prompt:** [`docs/ephemeral/2026-11-19-m07-costed-list-prompt.md`](https://github.com/amthorn78/glow-dating-app/blob/d3273f3eeb0ae947b33c479735fc2a3eb63e9f9f/docs/ephemeral/2026-11-19-m07-costed-list-prompt.md), revision 1, pruned after its record's integration (pinned at `d3273f3`) (TypeSafe v8.2: Opus 5.5 at medium).
- **Evidence home:** `docs/testing/evidence/<the session's date>-m07-costed-list.md`, written by the session on its own branch. The manager adds "Manager verification of M07".

## Why

- **PF01 A04 and OD-50.** Before P09 and P11B the manager keeps a costed list of each account and service completion needs, with its published price rechecked. Nathan approves each line when its phase needs it; no account is created and nothing is spent before he approves it. The $0 budget stands until then (OD-12).
- **M09 and OD-75 (D-02 (a)).** M07 runs next, before SV4. The legal entity, the store accounts and Stripe's review have lead times that other people set, and each waits on Nathan approving a line that M07 prices. The entity starts as soon as its line is priced and approved.
- **What is carried to it:** the "Carried to M07" section of [`carried-to-later-items.md`](carried-to-later-items.md), and M09's routes there ("Routed by M09": Stream's terms 12.5 and Trust Center, a mail provider, a monitoring tool, the public site's domain and host, the photo check and hash matching).

## Outcome

One research session writes a dated, costed list that Nathan can approve or decline line by line. For each line:

1. **What it is and why Glow needs it,** with the item that first needs it (PF01 1.19's order: M07, A01-R, SV4, SV5, SV2-L, AC1 to AC3, P07 to P12) and the owner direction behind it.
2. **The provider's published price,** read on a public page, with the page's URL, the date read and the plan or tier that fits Glow's launch: the US, both stores, one operator (OD-23), a paid plan with a free trial (OD-69, OD-70). Where no price is published, "no public price", with what would get one (a sales contact, a quote) and no contact made.
3. **Its shape:** one-time, monthly or yearly, usage-based (with the unit), or a share of revenue.
4. **Its lead time and prerequisites,** for example the D-U-N-S number before Apple's organization enrolment (AP-57, GP-57: up to 28 days).
5. **Who opens it** (Nathan or the entity) and what opening it starts: for an account, the requirements-matrix rows to recheck first, and any deadline that creating the account starts (for example GP-59, Google's trader declaration).
6. **Cheaper options beside it,** where they exist, with what each gives up.

**The lines,** from PF01 A04, the carried items and M09's O1 (none may be dropped; more may be added with a reason):

- **The US legal entity** (OD-55): formation, its registered agent, and any yearly state fee, for at least two common choices of state, with their trade-offs in one line each; and **its D-U-N-S number**.
- **Apple Developer Program** (organization) and **Google Play Console** (organization), with Google's developer verification and the account decisions of G-08 named for Nathan.
- **Expo's build service**, and signing.
- **Railway** app services (the API and the worker), and, as option (b) of M09's D-13, the app's own PostgreSQL in a US region beside OD-18's place on HDE's PostgreSQL service.
- **Stream's production chat plan.** The Maker application stays open (OD-76); price the plan as published, and the Maker terms, including its revenue limit. Read Stream's terms 12.5 (Stream may show its customer's name and logo) and say where the data-processing addendum and the Trust Center are (M09's H-03).
- **Cloudflare R2** for photos (OD-62), and any image processing service Glow would need beside its own processing.
- **The automated photo check and hash matching for known child sexual abuse material,** on at launch (OD-75, D-03 (a)); NCMEC's registration, and the named contacts G-02 lists.
- **Mail** (transactional email) and **push** (Expo's push service, APNs and FCM).
- **Stripe:** payments, Billing, Radar's tiers for free-trial abuse and the US-only card rule (OD-70, OD-71), and Stripe's review of a dating service; Stripe Tax as an option.
- **The stores' billing:** Apple's and Google's commission and their small-business rates, and RevenueCat's price beside the stores' own libraries (M09's D-11; the choice is not M07's).
- **A domain and WordPress hosting** for the public site and the staff console (P07.3; M09's D-16).
- **Monitoring:** error tracking, uptime and logs.
- **GitHub Actions minutes** once the repository is private (OD-51), priced from the measured use of the last full month, read through the GitHub tools, with the cheaper options beside it.
- **Legal advice:** on the founding-member offer's form before it is sold (OD-71), and, as Nathan's option, on the paid plan's terms, the renewal notices and the policies (M09's D-12). Published flat fees where they exist; otherwise "no public price".

**Not costed:** identity verification (OD-68 set it aside); a UK or EU representative and the ICO fee (no UK or EU launch, OD-55). A one-line note each is enough.

**Totals.** A summary table: one-time costs; the monthly cost at launch; and the monthly cost at **1,000** and at **10,000** active members, with each usage figure the totals rest on (photos per member, messages, emails, storage, builds, CI minutes) written down as an assumption. The two member counts are the manager's comparison points, not a forecast; Nathan can change them.

**The order of approvals.** The lines Nathan could approve now, in the order their lead times call for, starting with the entity and its D-U-N-S number, then the store accounts and Stripe, then the rest by the item that first needs each.

## Owned paths (the session's)

- **It writes,** on its own session branch, its evidence record only.
- **It never changes** any other file, anything in Notion, or anything on GitHub but its own branch's push.

## Manager-owned

This brief and the prompt; the carried-items file; the handoff, the register and the mistakes log; Notion; the verification.

## Exclusions

- **No account, no sign-up and no purchase.** It opens no account, starts no trial, fills in no form, contacts no sales team and gives no one Nathan's or Glow's details. Public pages only.
- **No credential.** None is read, printed or used; the environment is checked by names only, and the `AWS_*` names stay unread (OD-76).
- **No call to Glow's providers' APIs**, a database, HDE, Railway or Cloudflare; reading their public price pages and documentation is allowed.
- **No decision.** It prices; Nathan decides each line, and a provider choice goes to the Dev Manager first (the charter).
- **No legal advice.** It reports published prices and published terms, as the matrix did.

## Dependencies and inputs

PF01 1.19's A04 and order (pending DM-94; the list does not depend on it), OD-12, OD-23, OD-50, OD-51, OD-55, OD-62, OD-68 to OD-71, OD-75 and OD-76; the carried items; the requirements matrix (`store-legal-safety-requirements.md`) for each account's rows; the A05-V to A05-V3 records, which priced the photo check, Stripe and Radar on dated pages; M09's record, sections 4.3 and 5. An environment that reads public web pages (OD-40, OD-43): both app environments have open network access.

## Acceptance checks

- `git diff --name-only <prompt commit> <session head>` lists only the evidence record.
- The trusted classifier, taken from `main`, prints `"reason": "ordinary-docs-only"` for that comparison.
- Every line in "The lines" has a price with its URL and the date read, or "no public price" with what would get one.
- The totals add up from the lines, and each usage figure is marked as an assumption.

## Classification expectation

Ordinary documentation: one Markdown file, outside any `.claude/` directory. No application CI and no code review. The manager reads it whole when it integrates.

## Review plan

- **No Dev Manager read before it runs:** the prompt authorizes no credential use and no live provider action, and the item decides nothing.
- **After it reports:** the manager checks a sample of prices against their pages and the totals against the lines, integrates the record, and sends Nathan the list in OD-32's form, line by line, with the entity first. A line that implies a provider choice goes to the Dev Manager before it is settled.

## Sessions

- **Revision 1** (19 November 2026): the brief and the prompt, written while the Dev Manager reads DM-94, for `Glow App - No Stream`.
- **The prompt given** (19 November 2026): at Nathan's request (*"ok, give me the M07 handoff"*), before DM-94's answer, which it does not depend on; its start gate rechecked against the live branch first.
- **The research session** (19 November 2026; branch `claude/sharp-keller-j1uvsv`, head `02b7a1f`, Foundation run 44437200417): its record, `docs/testing/evidence/2026-11-19-m07-costed-list.md`; 13 of 15 sampled prices matched by an independent reader, none differing, and the two it could not read (Wyoming's fees) matched from the state's PDF.
- **Manager verification** (19 November 2026): the record's last section; the totals recomputed and three prices rechecked, all matching.
