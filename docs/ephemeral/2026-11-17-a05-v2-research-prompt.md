# A05-V2 prompt — research for the decision on the card check and the paid plan's free trial

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 17 November 2026.**
- **Durable brief:** [A05-V2](../planning/a05-v2-card-check-and-paid-trial.md), revision 2 (with DM-85's RR12 to RR18).
- **Where the result goes:** the matrix, `docs/planning/store-legal-safety-requirements.md`, and the session's record, `docs/testing/evidence/<date>-a05-v2-card-check-and-paid-trial.md`, on the session's own branch. The manager adds its verification to the record and the outcome to the brief's "Sessions", then writes the decision message.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.20 (confidence 0.53); rung probabilities low 0.01, medium 0.22, high 0.45, extra high 0.23, max 0.04, ultracode 0.05. Model probabilities Fable 5.1 0.01, Opus 5.5 0.76, Sonnet 5.5 0.17, Haiku 5.5 0.06 (confidence 0.68). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.002, Fable 5.1 at high 0.005, Fable 5.1 at extra high 0.002, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.001, Opus 5.5 at low 0.008, Opus 5.5 at medium 0.167, Opus 5.5 at high 0.342, Opus 5.5 at extra high 0.175, Opus 5.5 at max 0.030, Opus 5.5 at ultracode 0.038, Sonnet 5.5 at low 0.002, Sonnet 5.5 at medium 0.037, Sonnet 5.5 at high 0.077, Sonnet 5.5 at extra high 0.039, Sonnet 5.5 at max 0.007, Sonnet 5.5 at ultracode 0.009, Haiku 5.5 at low 0.001, Haiku 5.5 at medium 0.013, Haiku 5.5 at high 0.027, Haiku 5.5 at extra high 0.014, Haiku 5.5 at max 0.002, Haiku 5.5 at ultracode 0.003. Sent 2026-11-17T19:07:18Z. Nathan picks the cell.
- **The Dev Manager's read:** the brief was read in DM-85. The prompt needs none before it runs: it authorizes no credential use and no live provider action, and changes nothing but Markdown. The decision message built from its record goes to the Dev Manager before Nathan (OD-32).
- **Environment** (OD-36, OD-40): `Glow App - No Stream`, which reaches public policy, legal and Stripe pages through its proxy. No Stream variable is needed. If core sources stay unreadable there, the manager can give that part to Nathan's CLI agent (OD-43).
- **It runs alone** (OD-29). Its change is Markdown only, so no code review follows; the manager verifies it.
- **Deletion condition:** prune after the session's branch is integrated and the brief's "Sessions" holds the outcome.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **A05-V2 research session** for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What A05-V2 is.** Glow is a dating app for adults, built with Expo (iOS and Android) and Django, that matches people using Human Design, an astrology-like system, with photo profiles and in-app chat. It is at fixture scope: nothing is launched and no real user exists. The launch is the US, all states (OD-55). Nathan has decided (OD-68, OD-69) that the MVP launches with **a paid plan and no free plan**; that **a free trial starts at signup**, when the member gives a card, and the plan is charged when the trial ends unless they cancel; that **free accounts exist only as a staff grant**; that the plan is sold through **the stores' own billing and by a link to a purchase outside it, through Stripe**; and that **the card check is for three purposes**: a payment method ready for when the trial ends, fake or duplicate accounts made harder, and showing that the member is an adult. How the card check works in each channel, what it can and cannot show for each purpose, and what it costs, rest on no source read yet. Your job is that research, as the brief sets it. **You make no recommendation,** and you propose no plan, price or trial length: those are Nathan's, and the manager writes the decision message.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs. Subagents that each recheck one group of rows, or answer one of the three questions, suit this work; you check and merge what they return.
- **Your boundary is scope:**
  - write only the two outputs: `docs/planning/store-legal-safety-requirements.md` (only the parts the brief's "Owned paths" names) and `docs/testing/evidence/<today's date>-a05-v2-card-check-and-paid-trial.md`;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **Sources:** every row rests on a primary source you read today: the legal text, the regulator's own guidance, or the store's own policy page. Every fact about a store or Stripe rests on its own public page, read today. A secondary source only leads you to a primary one; a fact that rests on one is marked **UNCONFIRMED**. Quote briefly, a sentence or a clause.
- **Never fill a requirement or a service fact from memory or training data.** These laws, policies and prices change often. A page you cannot read is listed as unread, with its URL. Some sites refuse automated fetches; try the legal text's own publisher (for example the state legislature's site, `ecfr.gov`, `uscode.house.gov`, `govinfo.gov`) before you call a source unreadable. A source too large to fetch is recorded as not re-read, as SV3's recheck did for California's bulk data.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - create an account, sign up, start a trial, create or use a test-mode key, request a demo or a quote, submit any form, or send a message to anyone, Stripe or a store included;
  - call Stream or any other provider's API, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas`, `eas-cli` or `migrate`, or any application command (you read the repository; you do not run it);
  - say that Glow is, or would be, compliant: the matrix is a dated record of research, not legal advice or an applicability finding (DM-37 1.1).

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **Other credential names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`, AWS names). Never read them.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor 0a0c4fd619260211ecb54a4ba6a472750f516695 HEAD && echo "PR50 present"   # must print "PR50 present"
git diff --name-only origin/main HEAD | grep -v -E '\.md$'                                           # must print nothing
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- docs/planning/store-legal-safety-requirements.md   # must print nothing
git ls-tree -r --name-only origin/claude/magical-wozniak-yfmmx2 docs/testing/evidence/ | grep -c 'a05-v2-card-check-and-paid-trial'   # must print 0
git show origin/claude/magical-wozniak-yfmmx2:docs/planning/a05-v2-card-check-and-paid-trial.md | sed -n '/^## Sessions/,$p'   # must show "None yet."
```

If a check fails, stop and report. The prompt is stale if `<START_SHA>` is not on the live manager branch, if the matrix changed there after it, or if the brief's "Sessions" already records a session.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`;
- the brief, `docs/planning/a05-v2-card-check-and-paid-trial.md` (revision 2): its outcome, owned paths, exclusions, acceptance checks and report format bind you;
- OD-55, OD-60, OD-61, OD-68 and OD-69 in `docs/continuity/owner-directions.md`;
- DM-84 sections 4 and 5 (`docs/continuity/dev-manager/reviews/2026-11-17-dm-84-od-68-card-check-toggle-and-pf02-1-2.md`) and DM-85 sections 4 and 7 (`docs/continuity/dev-manager/reviews/2026-11-17-dm-85-od-69-a05-v2-brief-pf01-and-pf02-1-3.md`), which say why each row and question is taken;
- PF01's §7 "Billing" paragraph and its A06 row (`docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md`);
- the matrix's header, sections 1, 7, 8, 9 and 10, and each of the 43 rows the brief's table lists;
- the A05-V record (`docs/testing/evidence/2026-11-17-a05-v-verification-services.md`): sections 1, 7.2, 10 and 11 and appendix C.2, for its method and its Stripe facts.

## 3. What to do

Do the brief's three outcomes, in its words. In short:

1. **The recheck of the 43 rows.** Re-read each row's source today. Find the row's quotation in the text you read, as one continuous string; say so where it matched only after normalising white space or punctuation, and read it in place. Update the row's Source cell in the matrix's existing form: `read 2026-11-01, rechecked <today> (A05-V2)` (keep any earlier recheck note). If a requirement has changed, correct the row in place and say so in the record; delete nothing and keep every ID. Then add the header's **Rechecks** entry for this recheck, and correct any sentence of sections 9 and 10 that states a row whose requirement or status changed, marked as corrected at this recheck. A rule found that no row holds becomes a new row with the next free ID in its section, marked as added at this recheck, and the record lists the rows it was compared with.
2. **The three questions of fact** (the brief's outcome 2): the stores' free trials, including the trial lengths each allows; the stores' rules beyond their billing on the US storefront; and Stripe's card check. For Stripe, the record says plainly whether Stripe's pages make a dating service **prohibited, accepted only after Stripe's review, or accepted**, and names no other processor.
3. **The facts table** for the brief's seven items, each cell citing the rows and pages that bear on it. No recommendation, and no plan, price or trial length proposed.

**Method** (as the earlier rechecks did it):
- Fetch each source into its own new directory in your scratchpad, never inside the repository. Read it with a Python script run with `-I`, kept outside that directory, that strips tags and flattens white space; read PDFs with `pdftotext`.
- Search for each quotation as one continuous string in the stripped text.
- Hash each fetched file with SHA-256 and record it; commit no fetched file.

**The record** (`docs/testing/evidence/<today's date>-a05-v2-card-check-and-paid-trial.md`) holds: what, who and when; the method; the rows taken and why (the brief's table); the sources table (URL fetched, final URL, HTTP status and bytes, SHA-256, page date); the quotation checks, row by row; each changed requirement, with old and new text; any new row, with the rows it was compared with; the three questions' findings, each fact with its page and date; the facts table; the unread sources; deviations and limits; and the note "Research, not legal advice", as the matrix's opening note says.

## 4. Checks (run each; report the exact output)

```bash
git diff --name-only <START_SHA> HEAD          # only the two owned paths
python3 -I - <<'EOF'
import re, subprocess
path = "docs/planning/store-legal-safety-requirements.md"
old = subprocess.run(["git", "show", "<START_SHA>:" + path], capture_output=True, text=True, check=True).stdout
new = open(path, encoding="utf-8").read()
pat = re.compile(r"^\| ((?:AP|GP|USF|UST|UK|EU)-\d+) \|", re.M)
a, b = pat.findall(old), pat.findall(new)
missing = [i for i in a if i not in b]
kept = [i for i in b if i in a]
print("missing:", missing)
print("reordered:", kept != a)
print("added:", [i for i in b if i not in a])
EOF
```

- `missing` must be `[]` and `reordered` must be `False`.
- A script lists each of the brief's 43 rows whose Source cell lacks `rechecked <today> (A05-V2)`; the list must be empty, or each row on it must be named in the record as not re-read, with the reason.
- The record's quotation table has one line per row, with its source's SHA-256 and the result.
- Each new row names its primary text, and the record lists the rows of the same state or store it was compared with.
- Each fact for the three questions names its page and the date read.

## 5. Push

Commit only the two owned paths, with a message that names A05-V2. Push your session branch with `git push -u origin <branch>`. Push nothing else.

## 6. Report

Report, in this order:
- your branch, the start SHA and your head SHA, and the changed paths;
- the rows rechecked, with each changed requirement named; the rows not re-read, with the reason;
- the rows added, with their primary texts;
- the three questions' findings, in short, with Stripe's place for a dating service stated plainly;
- every check in section 4, with its exact output;
- the sources unread, with their URLs;
- deviations, limits and open questions.
