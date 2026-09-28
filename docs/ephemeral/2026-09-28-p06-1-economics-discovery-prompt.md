# P06.1 economics discovery prompt (Claude in Chrome)

- **Owner:** App Manager 5. Nathan runs it in Claude in Chrome, in his own browser signed in to the Stream dashboard, and relays its report.
- **Revision 1, 28 September 2026.**
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md): "Stream dashboard baseline (25 September 2026, 02:04 UTC)", outcome 5 in "Brief — P06.1", and "Economics" in "Sessions". The scope is the Dev Manager's DM-02 B2: the plan limits, overage behaviour with no payment method on file, any attribution requirement (DM-02 B1), the data-processing agreement and region (US East against the launch geography, A05), and Maker eligibility, plus the Maker application's status (OD-22).
- **Where the result goes:** the manager checks the report against the pages it names where it can, and records it in the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md) under a new heading, "Economics discovery", and in the brief's "Sessions". The facts feed P06.1's close-out and the A04 and A05 records.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Opus 5.5, medium.** Effort score 0.99 (confidence 0.70); rung probabilities low 0.23, medium 0.61, high 0.13, extra high 0.02, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.02, Opus 5.5 0.98 (confidence 0.97). Sent 2026-09-28T14:21:41Z. Nathan picks the cell.
- **A Dev Manager read comes first:** the prompt authorizes a session that acts in Nathan's signed-in Stream dashboard, a live provider account, so the Dev Manager reads it before Nathan runs it (DM-01 P1; [charter](../planning/dev-manager.md)). The consultation is [DM-06](2026-09-28-dm-06-economics-discovery-prompt-read.md).
- **Stream variables** (OD-28): none are needed, and Nathan adds none. The session uses no API key or secret; it reads the dashboard and Stream's public pages in Nathan's browser.
- **It runs alone** (OD-29, the linear process). P06.1's close-out follows it.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

---

You're helping Nathan record the cost, limits and terms of Stream (getstream.io), the chat provider his Glow dating app is testing. This prompt is revision 1, written by App Manager 5 on 28 September 2026. Nathan is signed in to the Stream dashboard in this browser; start at dashboard.getstream.io. Part A is his account's dashboard; part B is Stream's public website. **This is a read-only lookup.**

**Rules**

- Only look. Don't change any setting, and don't create, edit or delete anything: apps, users, channels, channel types, roles, permissions, products, webhooks, API keys, team members, billing details or alerts.
- Don't open an Edit dialog, a settings form or a create form, even to read it. If a fact is visible only inside one, record it as "not shown".
- Don't click anything that upgrades or downgrades a plan, starts a trial, opens a checkout, adds a payment method, applies to or withdraws from a program (including Maker), signs or accepts terms or an agreement, books a call, or contacts sales or support. If a page pushes you toward one of those, stop and tell Nathan.
- Never reveal, copy, type or record the API secret. If you see a secret unmasked, don't record it, and tell Nathan it was visible.
- Don't record email addresses, people's names, card or bank details, or any user's or message's content. For a payment method, record only whether one is on file: yes or no.
- If you need to sign in, pass a security check or choose between accounts, stop and ask Nathan.
- For every fact, record where you saw it: the dashboard page, or the public page's URL. Quote the exact words for anything about charges, overage, limits, attribution, eligibility or data processing. Don't infer: if a page doesn't say, record "not shown".

**A. In the dashboard** (organization "Glow Connection System"; application 1729640, "Glow Connection System Chat Engine")

1. **Plan.** The current plan's name for Chat, and for Video and Feeds if the dashboard shows them separately. Whether it is a trial. The current billing period, and the amount billed or due for it so far.
2. **Limits.** Every limit the plan shows, as shown. On 25 September the dashboard showed: 1,000 active users; 100 concurrent connections; 2,000,000 API calls a month; 200,000 QueryChannels calls a month; 500,000 stored channels; 5,000,000 stored messages; 5,500,000 total records; 500 GB of outbound traffic a month. Say whether each is the same now, and record any limit shown for Video or Feeds.
3. **Usage.** This billing period's usage for every resource the dashboard shows, for Chat, Video and Feeds, with any warning shown. Say whether any usage is near or past a limit.
4. **Past a limit.** What the dashboard says happens when a limit is passed (a hard stop, automatic overage charges, or a prompt to upgrade), in its own words. Whether a payment method is on file: yes or no. Whether any spending cap or usage alert is shown, and its setting as displayed, without opening it.
5. **Maker.** The Maker Account application's status as the dashboard shows it (submitted, pending, approved, declined, or not shown), with any date. Don't click anything in it.
6. **Region.** The application's region, and anything the dashboard says about other regions or about changing an application's region.
7. **Attribution and agreements.** Any notice in the dashboard about required branding or attribution (for example "Powered by Stream"), and any data-processing agreement, security or compliance documents the dashboard offers: their names and where they are. Don't sign, accept or download anything that needs acceptance.

**B. On Stream's public website** (getstream.io; no sign-in needed)

8. **Chat pricing.** Every Chat plan listed, with its monthly price, what it includes (active users, concurrent connections and any other allowance), and how overage is billed, in the page's words. Note any "last updated" date.
9. **Video and Feeds pricing.** Whether Video and Feeds are priced separately from Chat, what any free allowance includes, and how usage past it is billed.
10. **No payment method.** What Stream's pricing, fair-usage or terms pages say happens when an account on the free plan passes a limit with no payment method on file.
11. **Maker Account program.** Its eligibility (for example company size, revenue, funding or team size), what it includes, how long it lasts, what happens when it ends or when an account stops qualifying, and any attribution or publicity it requires.
12. **Attribution.** Whether any plan, the Maker program or the terms require a visible attribution to Stream in an app (for example a "Built with Stream" badge), quoted with its source. If none is found, say where you looked.
13. **Data processing and region.** Where Stream's data-processing agreement is, and whether it is self-serve or needs a request; the data-hosting regions Stream offers for Chat; whether an application's region can be changed after it is created; and where Stream lists its subprocessors.
14. **Terms.** The URL and "last updated" date of Stream's terms of service and of any acceptable-use policy. Quote any clause that names dating apps, adult content or a content-moderation duty. Don't summarize other clauses.

**Report back in this format**

- The prompt revision you received (revision 1).
- Checked at: date and time (UTC).
- One line per item, numbered as above: *value (page or URL) — confirmed, not shown, or unclear*, with quotes where the rules ask for them.
- Changes since 25 September: any plan or limit that differs from item 2's figures. On 25 September the usage was 10 API calls, and everything else zero.
- Risks noticed: for example usage near a limit, automatic billing, an attribution requirement, or a payment method on file.
- Actions taken: "navigation and reading only", or exactly what else happened.
