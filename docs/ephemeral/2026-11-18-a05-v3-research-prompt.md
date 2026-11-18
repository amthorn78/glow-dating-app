# A05-V3 prompt — research for the decision on the founding-member offer

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 18 November 2026.**
- **Durable brief:** [A05-V3](../planning/a05-v3-founding-member-offer.md), revision 2 (with DM-88's UU1 to UU7).
- **Where the result goes:** the matrix, `docs/planning/store-legal-safety-requirements.md`, and the session's record, `docs/testing/evidence/<date>-a05-v3-founding-member-offer.md`, on the session's own branch. The manager adds its verification to the record and the outcome to the brief's "Sessions", then writes the offer's decision message.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.28 (confidence 0.49); rung probabilities low 0.01, medium 0.22, high 0.39, extra high 0.28, max 0.05, ultracode 0.05. Model probabilities Fable 5.1 0.02, Opus 5.5 0.79, Sonnet 5.5 0.16, Haiku 5.5 0.03 (confidence 0.72). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.004, Fable 5.1 at high 0.008, Fable 5.1 at extra high 0.006, Fable 5.1 at max 0.001, Fable 5.1 at ultracode 0.001, Opus 5.5 at low 0.008, Opus 5.5 at medium 0.174, Opus 5.5 at high 0.308, Opus 5.5 at extra high 0.221, Opus 5.5 at max 0.040, Opus 5.5 at ultracode 0.040, Sonnet 5.5 at low 0.002, Sonnet 5.5 at medium 0.035, Sonnet 5.5 at high 0.062, Sonnet 5.5 at extra high 0.045, Sonnet 5.5 at max 0.008, Sonnet 5.5 at ultracode 0.008, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.007, Haiku 5.5 at high 0.012, Haiku 5.5 at extra high 0.008, Haiku 5.5 at max 0.002, Haiku 5.5 at ultracode 0.002. Flags: boundary between extra high and high. Sent 2026-11-18T02:12:13Z. Nathan picks the cell.
- **The Dev Manager's read:** the brief was read in DM-88. The prompt needs none before it runs: it authorizes no credential use and no live provider action, and changes nothing but Markdown. The decision message built from its record goes to the Dev Manager before Nathan (OD-32).
- **Environment** (OD-36, OD-40): `Glow App - No Stream`, which reaches public policy, legal and Stripe pages through its proxy. No Stream variable is needed. If core sources stay unreadable there, the manager can give that part to Nathan's CLI agent (OD-43).
- **It runs alone** (OD-29). Its change is Markdown only, so no code review follows; the manager verifies it.
- **Deletion condition:** prune after the session's branch is integrated and the brief's "Sessions" holds the outcome.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **A05-V3 research session** for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What A05-V3 is.** Glow is a dating app for adults, built with Expo (iOS and Android) and Django, that matches people using Human Design, an astrology-like system, with photo profiles and in-app chat. It is at fixture scope: nothing is launched and no real user exists. The launch is the US, all states, for now (OD-55).

Nathan has set the MVP's terms (OD-69, OD-70):
- a paid plan and no free plan, with a two-week free trial at signup;
- the stores' own billing, plus a Stripe link in the iPhone app and on the web, not in the Android app;
- free accounts only as a staff grant.

He has added a **founding-member offer** after launch (OD-70): up to 1,000 members may buy a **lifetime subscription for $100, paid once** (the manager's reading of his "a one-time thing"), **ideally only through Stripe**.

What that offer needs from the dating-service contract laws, the consumer laws and the stores rests on no source read yet. Your job is that research, as the brief sets it. **You make no recommendation and no legal conclusion,** and you propose no plan, price or offer term: those are Nathan's, and the manager writes the decision message.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs. Subagents that each recheck one group of rows, or answer one of the four questions, suit this work; you check and merge what they return.
- **Your boundary is scope:**
  - write only the two outputs: `docs/planning/store-legal-safety-requirements.md` (only the parts the brief's "Owned paths" names) and `docs/testing/evidence/<today's date>-a05-v3-founding-member-offer.md`;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **Sources:** every row rests on a primary source you read today: the statute or regulation itself, the regulator's own guidance, or the store's own policy page. Every fact about a store or Stripe rests on its own public page, read today. A secondary source only leads you to a primary one; a fact that rests on one is marked **UNCONFIRMED**. Quote briefly, a sentence or a clause.
- **Where a text's application to a contract with no end date is unclear,** quote it as found and say so. Do not resolve it: that is a reading for counsel, not for this record.
- **Never fill a requirement or a fact from memory or training data.** These laws, policies and prices change often. A page you cannot read is listed as unread, with its URL. Some sites refuse automated fetches; try the legal text's own publisher (for example the state legislature's site, `govinfo.gov`, `uscode.house.gov`, `ecfr.gov`) before you call a source unreadable. A source too large to fetch is recorded as not re-read, as SV3's recheck did for California's bulk data.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - create an account, sign up, start a trial or a checkout, create or use a test-mode key, request a demo or a quote, submit any form, or send a message to anyone, Stripe, a store or a regulator included;
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
git merge-base --is-ancestor d57da657a3d3a8a0308e271c0b58d9416c0dc09a HEAD && echo "PR52 present"   # must print "PR52 present"
git diff --name-only origin/main HEAD | grep -v -E '\.md$'                                           # must print nothing
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- docs/planning/store-legal-safety-requirements.md   # must print nothing
git ls-tree -r --name-only origin/claude/magical-wozniak-yfmmx2 docs/testing/evidence/ | grep -c 'a05-v3-founding-member-offer'   # must print 0
git show origin/claude/magical-wozniak-yfmmx2:docs/planning/a05-v3-founding-member-offer.md | sed -n '/^## Sessions/,$p'   # must show "None yet."
```

If a check fails, stop and report. The prompt is stale if `<START_SHA>` is not on the live manager branch, if the matrix changed there after it, or if the brief's "Sessions" already records a session.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`;
- the brief, `docs/planning/a05-v3-founding-member-offer.md` (revision 2): its outcome, owned paths, exclusions, acceptance checks and report format bind you;
- OD-55, OD-69 and OD-70 in `docs/continuity/owner-directions.md`;
- DM-86 section 3 (`docs/continuity/dev-manager/reviews/2026-11-17-dm-86-card-check-decision-message-and-a05-v2.md`), DM-87 sections 3 and 5 (`docs/continuity/dev-manager/reviews/2026-11-17-dm-87-od-70-founding-member-offer-and-pf02-1-5.md`) and DM-88 sections 3 and 4 (`docs/continuity/dev-manager/reviews/2026-11-18-dm-88-a05-v3-brief-and-pf02-1-6.md`). They say why each row and question is taken. **DM-88 section 3 corrects DM-87 section 3:** UST-23's "Asks of Glow" cell does say "The clause; pro-rata refunds", a summary its quotation does not show;
- the matrix's header, sections 1, 7, 8, 9 and 10, and each of the 24 rows the brief's table lists;
- the A05-V2 record (`docs/testing/evidence/2026-11-17-a05-v2-card-check-and-paid-trial.md`): sections 1, 4, 7, 8, 10 and 14, for its method and its store and Stripe facts.

## 3. What to do

Do the brief's four outcomes, in its words. In short:

1. **The recheck of the 24 rows** (UST-08; UST-22 to UST-28; USF-13, USF-16, USF-17; UST-29 to UST-31, UST-60, UST-61; AP-39 to AP-42; GP-38, GP-39, GP-41, GP-42).
   - Re-read each row's source today. Find the row's quotation in the text you read, as one continuous string; say so where it matched only after normalising white space or punctuation, and read it in place.
   - Update the row's Source cell in the matrix's existing form, adding `rechecked <today> (A05-V3)` and keeping any earlier recheck note.
   - If a requirement has changed, correct the row in place and say so in the record; delete nothing and keep every ID. **UST-23's "Asks of Glow" cell is quoted from the statute or corrected** (UU3).
   - Then add the header's **Rechecks** entry for this recheck, and correct any sentence of sections 9 and 10 that states a row whose requirement or status changed, marked as corrected at this recheck.
   - Run the brief's two searches: state dating-service contract laws not in the matrix, and federal or state texts on "lifetime" memberships or contracts. A law found that no row holds becomes a new row with the next free ID in its section, marked as added at this recheck, and the record lists the rows it was compared with. A search that finds none is recorded as searched, with the sources tried.
2. **The four questions of fact** (the brief's outcome 2), each from the full statute or page, not only the quoted clause:
   - a term cap or a life measure;
   - refunds, read whole;
   - when a lifetime contract "ends";
   - the stores: Apple's 3.1.3(b) proviso on the US storefront and an in-app lifetime plan's type and commission; Google's rule on honouring a plan bought outside Play, and its fee on a one-time item through a link.
3. **Stripe's one-time payment** (the brief's outcome 3), including whether a payment can be limited to buyers in the US, and how (UU4).
4. **The facts table** for the brief's seven items, each cell citing the rows and pages that bear on it. No recommendation, no legal conclusion, and no plan, price or offer term proposed.

**Method** (as the earlier rechecks did it):
- Fetch each source into its own new directory in your scratchpad, never inside the repository. Read it with a Python script run with `-I`, kept outside that directory, that strips tags and flattens white space; read PDFs with `pdftotext`.
- Search for each quotation as one continuous string in the stripped text.
- Hash each fetched file with SHA-256 and record it; commit no fetched file.

**The record** (`docs/testing/evidence/<today's date>-a05-v3-founding-member-offer.md`) holds:
- what, who and when; the method; the rows taken and why (the brief's table);
- the sources table (URL fetched, final URL, HTTP status and bytes, SHA-256, page date);
- the quotation checks, row by row;
- each changed requirement, with old and new text; any new row, with the rows it was compared with;
- the four questions' and Stripe's findings, each fact with its page and date;
- the facts table; the unread sources; deviations and limits;
- the note "Research, not legal advice", as the matrix's opening note says.

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
- A script lists each of the brief's 24 rows whose Source cell lacks `rechecked <today> (A05-V3)`; the list must be empty, or each row on it must be named in the record as not re-read, with the reason.
- The record's quotation table has one line per row, with its source's SHA-256 and the result.
- Each new row names its primary text, and the record lists the rows of the same state or store it was compared with.
- Each fact for the four questions and for Stripe names its page and the date read.

## 5. Push

Commit only the two owned paths, with a message that names A05-V3. Push your session branch with `git push -u origin <branch>`. Push nothing else.

## 6. Report

Report, in this order:
- your branch, the start SHA and your head SHA, and the changed paths;
- the rows rechecked, with each changed requirement named (UST-23's cell included); the rows not re-read, with the reason;
- the rows added, with their primary texts; the searches that found none, with the sources tried;
- the four questions' and Stripe's findings, in short;
- every check in section 4, with its exact output;
- the sources unread, with their URLs;
- deviations, limits and open questions.
