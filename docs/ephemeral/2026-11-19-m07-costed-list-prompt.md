# M07 prompt — the costed list of completion's accounts and services

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 19 November 2026.**
- **Durable brief:** [M07 — The costed list](../planning/m07-costed-list.md), revision 1 (OD-50; OD-75, D-02).
- **Where the result goes:** the session's record, `docs/testing/evidence/<the session's date>-m07-costed-list.md`, on its own branch; the manager verifies it, adds "Manager verification of M07", and sends Nathan the list line by line.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at medium.** Effort score 1.37 (confidence 0.69); rung probabilities low 0.05, medium 0.60, high 0.30, extra high 0.04, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.65, Sonnet 5.5 0.21, Haiku 5.5 0.14 (confidence 0.53). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.033, Opus 5.5 at medium 0.390, Opus 5.5 at high 0.195, Opus 5.5 at extra high 0.026, Opus 5.5 at max 0.007, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.011, Sonnet 5.5 at medium 0.126, Sonnet 5.5 at high 0.063, Sonnet 5.5 at extra high 0.008, Sonnet 5.5 at max 0.002, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.007, Haiku 5.5 at medium 0.084, Haiku 5.5 at high 0.042, Haiku 5.5 at extra high 0.006, Haiku 5.5 at max 0.001, Haiku 5.5 at ultracode 0.000. Sent 2026-11-19T00:57:16Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (the brief's "Review plan"). The prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`, which has open network access for public pages. If a page is refused there, Nathan's CLI agent in an open environment may take the lookup (OD-40, OD-43). No Stream variable is needed.
- **`amthorn78/glow-docs`** is attached, read-only (OD-74). This task does not need it.
- **Deletion condition:** prune after M07's record is integrated and the brief's "Sessions" holds the outcome.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **costed-list research session (M07)** of the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**Why you exist.** Glow's budget is $0 until Nathan approves a line of a costed list (OD-12, OD-50). No account exists with any store or provider except Stream's free development application. The legal entity, the store accounts and Stripe's review each take weeks that other people set, and each waits on Nathan approving a line you price. He chose to run this first (OD-75). Your list is what he approves from, line by line.

**What the app is, in brief.** A native dating app for the US (Expo; iOS and Android), with a Django API, text chat through Stream behind Glow's own server (OD-45), photos in private Cloudflare R2 storage (OD-62), a paid plan with a two-week free trial and a Stripe link in the iPhone app and on the web (OD-69, OD-70), a WordPress public site and staff console (OD-19, OD-60), and one operator (OD-23). It launches in the US only, in English, through both stores, held by a US legal entity (OD-55).

## What to deliver

Read the brief, `docs/planning/m07-costed-list.md`, completely: its "Outcome" names every line you must cover and what each line must state. In short, for each line:

1. what it is, why Glow needs it, the item that first needs it, and the owner direction behind it;
2. the published price, from a public page: its URL, the date you read it, and the plan or tier that fits Glow's launch; or "no public price", with what would get one, and no contact made;
3. its shape: one-time, monthly or yearly, usage-based (with the unit), or a share of revenue;
4. its lead time and prerequisites;
5. who opens it, and what opening it starts: for an account, the rows of the requirements matrix (`docs/planning/store-legal-safety-requirements.md`) to recheck first, and any deadline that creating it starts;
6. cheaper options beside it, with what each gives up.

Then:
- **the totals:** one-time costs; the monthly cost at launch; the monthly cost at 1,000 and at 10,000 active members. Write down every usage figure they rest on (photos per member, messages, emails, storage, builds, CI minutes) and mark each as an assumption, not a forecast;
- **the order of approvals:** the lines Nathan could approve now, in the order their lead times call for, starting with the entity and its D-U-N-S number.

**Where earlier research priced a line,** reuse it only after rechecking the page today, and say whether the price changed: A05-V priced the photo check and hash-matching tools, A05-V2 and A05-V3 priced Stripe and Radar (`docs/testing/evidence/`, their records). The P06.1 records priced Stream's plans on 28 September.

**GitHub Actions minutes:** read the last full month's runs through your GitHub tools and count the billable minutes the repository would have used if private; price them against GitHub Free's allowance (the carried-items file, "Carried to M07").

Lead the record with a one-page summary for Nathan in plain words: the total to launch, the monthly cost at each level, the lines with the longest lead times, and the first three approvals.

## How you work

- Nathan started you and will relay your report. You research; you decide nothing. A line that implies choosing a provider says so, and the choice goes to the Dev Manager later.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs. Subagents that each price a group of lines are a good fit; you own and check what they report against the page.
- **Your boundary is scope:**
  - **write only your record,** `docs/testing/evidence/<your session's date>-m07-costed-list.md`, on your own session branch, and push only that branch with `git push -u origin <branch>`;
  - on GitHub, read only, through your GitHub tools: no pull request, comment, review, re-run, workflow dispatch or setting. Use `gh` for nothing but a search;
  - nothing written to Notion.
- **Web:** public pages only, read with your web tools. Quote the price as the page states it, with its currency and billing period; when a page needs a login, a form or a sales call to show a price, record "no public price".
- **Never:**
  - open an account, start a trial, sign up, fill in a form, contact a sales team or support, or give anyone Nathan's or Glow's details;
  - dump the environment, or read, print, log or commit any credential, password, token or key;
  - read, print or use the value of any `AWS_*` variable (OD-76);
  - call the API of any provider Glow uses or plans to use, HDE, Railway or Cloudflare, or connect to any database;
  - run `playwright install`, `eas`, a native build or `migrate`;
  - give legal or tax advice: report published prices and terms, as the matrix did.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`); the cloud container sets them (OD-76). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git merge-base --is-ancestor 6edae780a0fbf1e5d2659c3eb8c9c48eeeea1a70 HEAD && echo "PR54's merge present"
ls docs/testing/evidence | grep -c 'm07-'             # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, or an M07 record already exists.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`;
- the brief, `docs/planning/m07-costed-list.md`;
- the "Carried to M07" section and the "Routed by M09" section of `docs/planning/carried-to-later-items.md`;
- PF01's A04 row and section 8's "The owner's track" (`docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md`);
- the owner directions the brief names, in `docs/continuity/owner-directions.md`;
- M09's record, sections 4.3 and 5 (`docs/testing/evidence/2026-11-18-m09-project-status-review.md`);
- the requirements matrix's account rows (AP-57, GP-57, GP-59, G-02, G-08 and those they point to);
- the A05-V, A05-V2 and A05-V3 records, for the prices they read.

## 3. The record and the report

Your record, `docs/testing/evidence/<your session's date>-m07-costed-list.md`:
- the one-page summary for Nathan, first;
- the prompt revision (revision 1, from `<PROMPT_SHA>`), the start gate's and the environment check's results;
- one section per line, in the brief's order, with the six points;
- the totals table, with its assumptions;
- the order of approvals;
- what you could not price, and why.

Then check:
- `git diff --name-only <PROMPT_SHA> HEAD` lists only your record;
- the totals add up from the lines.

Your final message, which Nathan relays: your branch and head, the record's path, the one-page summary, and the lines with "no public price".
