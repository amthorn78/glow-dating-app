# P09.3a prompt — the store, legal and safety requirements matrix

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 1 November 2026.**
- **Durable brief:** [P09.3a — The store, legal and safety requirements matrix](../planning/p09-3a-requirements-matrix.md), revision 1.
- **Where the result goes:** the matrix, `docs/planning/store-legal-safety-requirements.md`, and the session's record, `docs/testing/evidence/<date>-p09-3a-requirements-matrix.md`, on the session's own branch. The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at max.** Effort score 3.74 (confidence 0.62); rung probabilities low 0.00, medium 0.00, high 0.07, extra high 0.26, max 0.50, ultracode 0.17. Model probabilities Fable 5.1 0.10, Opus 5.5 0.68, Sonnet 5.5 0.19, Haiku 5.5 0.03 (confidence 0.57). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.007, Fable 5.1 at extra high 0.026, Fable 5.1 at max 0.050, Fable 5.1 at ultracode 0.017, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.048, Opus 5.5 at extra high 0.177, Opus 5.5 at max 0.340, Opus 5.5 at ultracode 0.116, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.013, Sonnet 5.5 at extra high 0.049, Sonnet 5.5 at max 0.095, Sonnet 5.5 at ultracode 0.032, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.002, Haiku 5.5 at extra high 0.008, Haiku 5.5 at max 0.015, Haiku 5.5 at ultracode 0.005. Sent 2026-11-01T18:16:43Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The session authorizes no credential use and no live provider action, and changes nothing but Markdown. The A05 questions it informs go to the Dev Manager before Nathan.
- **Environment** (OD-36, OD-40): `Glow App - No Stream`, which reaches the official policy sites through its proxy (the brief, D3). No Stream variable is needed. If core sources stay unreadable there, the manager can give that part to Nathan's CLI agent (OD-43).
- **It runs alone** (OD-29). Its change is Markdown only, so no code review follows; the manager verifies it.
- **Deletion condition:** prune after the matrix is integrated and the brief's "Sessions" holds the outcome.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **P09.3a research session** for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What P09.3a is.** Glow is a dating app for adults, built with Expo (iOS and Android) and Django, that matches people using Human Design, an astrology-like system, with photo profiles and in-app chat. It is at fixture scope: nothing is launched and no real user exists. Before the next feature phases are designed, Nathan needs a dated matrix of what the App Store, Google Play and the law of the candidate countries, **the US, the UK and the EU**, require of an app like this. Your job is research: build that matrix from official sources, map each requirement to the phase that will deliver it and to what the repository already does, and list the gaps. **It is research, not legal advice, and it says so.** The brief, `docs/planning/p09-3a-requirements-matrix.md`, is the specification: its "Outcome" and D1 to D6; follow them.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 8. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs. Subagents that research one store or one jurisdiction each, in parallel, suit this work; you check and merge their rows.
- **Your boundary is scope:**
  - write only the two outputs: `docs/planning/store-legal-safety-requirements.md` and `docs/testing/evidence/<today's date>-p09-3a-requirements-matrix.md`;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **Sources** (D2): every requirement rests on a primary source you read today: the store's own policy pages or the legal text and the regulator's own guidance. A secondary source only leads you to a primary one; a row that rests on one is flagged as unconfirmed. Quote briefly, a sentence or a clause.
- **Network** (D3): read public web pages with your web tools. A page you cannot read is listed as unread, with its URL. **Never fill a requirement from memory or training data:** store policies and these laws change often, and a remembered rule may be stale. Some regulators' sites refuse automated fetches; try the legal text's own publisher (for example `legislation.gov.uk`, EUR-Lex, `uscode.house.gov`, `ecfr.gov`) before you call a source unreadable.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - create an account, sign up, log in, buy, or submit a form on any site, or send a message to anyone;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas`, `eas-cli` or `migrate`, or any application command (D5: you read the repository; you do not run it).

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`; the environment inventory). Never read them.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor 6eaee357b4ba24d19dd8464b140f32266619e4d4 HEAD && echo "PR38 present"   # M06's final head; main's merge fcd6ebc has the same tree. Must print "PR38 present"
git diff --name-only fcd6ebc0be2c33d570dd25c5e4a2f31a862258dd HEAD | grep -v -E '\.md$'                  # against main: must print nothing
test ! -e docs/planning/store-legal-safety-requirements.md && echo "no matrix yet"   # must print "no matrix yet"
```

If a check fails, stop and report. The prompt is stale if `<START_SHA>` is not on the live manager branch, or if the brief's "Sessions" already records a session.

**Then read, completely:** root `AGENTS.md` and `CLAUDE.md`; the brief, `docs/planning/p09-3a-requirements-matrix.md`; PF01's §7 "Mobile/store readiness" and "Billing" paragraphs, its A04 and A05 rows and R05 (`docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md`); OD-23, OD-49 and OD-50 in `docs/continuity/owner-directions.md`; M05's E2, E6, N3 and N4 in `docs/testing/evidence/2026-10-25-m05-project-review.md`; the carried-items file's "Carried to P09.3a" (`docs/planning/carried-to-later-items.md`); `docs/architecture/privacy-and-safety-rules.md`. For the current-state column (D5), read what each row needs: the architecture documents, the briefs in `docs/planning/`, the P11 plan, and the code they cite.

## 3. What to do

1. **List the requirements** (Outcome 2 and 3), store by store and jurisdiction by jurisdiction, covering every topic in Outcome 3. For each candidate jurisdiction, find which of its laws bind a dating app with photo uploads, messaging and possibly paid subscriptions, and on what conditions, such as a size threshold or a user count. Child safety is a requirement in every jurisdiction: CSAM detection, the reporting duty and the authority it goes to, and the stores' child-safety standards for dating and social apps.
2. **Fill each row:** the requirement, its source (section, URL, date read), whom it binds and when, what it asks of Glow, the owning phase or "no owner", and the current state at fixture scope with the file you read it in.
3. **The gaps** (Outcome 4): every row with no owner, or whose owner's plan does not cover it, each with the smallest change that would give it one.
4. **What the A05 questions turn on** (Outcome 5): for each open A05 question, what the requirements imply in each candidate jurisdiction. Give facts and sources only; do not recommend.
5. **Maintenance** (Outcome 6): when to recheck, and the rows most likely to change.

## 4. The outputs

- **The matrix,** `docs/planning/store-legal-safety-requirements.md`:
  - the header (Outcome 1): research, not legal advice; what it does not establish; the research date and `<START_SHA>`;
  - the requirement tables, the gaps, the A05 section and the maintenance section.
- **The record,** `docs/testing/evidence/<today's date>-p09-3a-requirements-matrix.md`:
  - the start gate's results and the environment check (names only);
  - the method: how you searched, and how subagents' rows were checked if you used them;
  - every source read, with its date, and every source not read, with the reason;
  - the limits: what the matrix does not establish, and any row flagged as unconfirmed.

Commit both with a clear message ending in the session's attribution lines, and push your branch. Confirm `git status` is clean and that `git diff --name-only <START_SHA> HEAD` prints only the two outputs.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision you received (revision 1, from `<START_SHA>`), your branch and head commit;
- the start gate's and the environment check's results;
- the number of requirement rows, by store and jurisdiction;
- the child-safety rows in full;
- the gaps, each with its proposed owner;
- the A05 section's summary;
- the sources you could not read, the rows flagged as unconfirmed, and the matrix's limits.
