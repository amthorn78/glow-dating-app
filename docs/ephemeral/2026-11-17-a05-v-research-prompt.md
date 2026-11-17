# A05-V prompt — research for the decision on the identity verification company and the photo check's service

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 17 November 2026.**
- **Durable brief:** [A05-V](../planning/a05-v-verification-services.md), revision 2 (with DM-83's PP1 to PP9).
- **Where the result goes:** the matrix, `docs/planning/store-legal-safety-requirements.md`, and the session's record, `docs/testing/evidence/<date>-a05-v-verification-services.md`, on the session's own branch. The manager adds its verification to the record and the outcome to the brief's "Sessions", then writes the decision message.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 3.04 (confidence 0.54); rung probabilities low 0.00, medium 0.02, high 0.28, extra high 0.38, max 0.27, ultracode 0.05. Model probabilities Fable 5.1 0.03, Opus 5.5 0.89, Sonnet 5.5 0.06, Haiku 5.5 0.02 (confidence 0.85). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.008, Fable 5.1 at extra high 0.011, Fable 5.1 at max 0.008, Fable 5.1 at ultracode 0.002, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.018, Opus 5.5 at high 0.249, Opus 5.5 at extra high 0.338, Opus 5.5 at max 0.240, Opus 5.5 at ultracode 0.045, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.017, Sonnet 5.5 at extra high 0.023, Sonnet 5.5 at max 0.016, Sonnet 5.5 at ultracode 0.003, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.006, Haiku 5.5 at extra high 0.008, Haiku 5.5 at max 0.005, Haiku 5.5 at ultracode 0.001. Flags: boundary between high and extra high. Sent 2026-11-17T11:16:58Z. Nathan picks the cell.
- **The Dev Manager's read:** the brief was read in DM-83. The prompt needs none before it runs: it authorizes no credential use and no live provider action, and changes nothing but Markdown. The decision message built from its record goes to the Dev Manager before Nathan (OD-32).
- **Environment** (OD-36, OD-40): `Glow App - No Stream`, which reaches public policy and legal sites through its proxy. No Stream variable is needed. If core sources stay unreadable there, the manager can give that part to Nathan's CLI agent (OD-43).
- **It runs alone** (OD-29). Its change is Markdown only, so no code review follows; the manager verifies it.
- **Deletion condition:** prune after the session's branch is integrated and the brief's "Sessions" holds the outcome.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **A05-V research session** for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What A05-V is.** Glow is a dating app for adults, built with Expo (iOS and Android) and Django, that matches people using Human Design, an astrology-like system, with photo profiles and in-app chat. It is at fixture scope: nothing is launched and no real user exists. The launch is the US, all states (OD-55). Nathan has decided (OD-61) that a member's profile shows only after **identity verification**, a government photo ID checked by a verification company with a live selfie matched to it, decided automatically, and that each photo is approved by an **automated photo check**. He has not yet chosen the company or the service. Before the manager puts that choice to him, the requirements matrix's rows it touches must be rechecked against their sources, and candidate services compared from their own public pages. Your job is that research, as the brief sets it. **You make no recommendation:** the manager writes the decision message.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs. Subagents that each recheck one group of rows, or research one kind of service, suit this work; you check and merge what they return.
- **Your boundary is scope:**
  - write only the two outputs: `docs/planning/store-legal-safety-requirements.md` (only the parts the brief's "Owned paths" names) and `docs/testing/evidence/<today's date>-a05-v-verification-services.md`;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **Sources:** every row rests on a primary source you read today: the legal text, the regulator's own guidance, or the store's own policy page. Every service fact rests on the service's own public page, read today. A secondary source only leads you to a primary one; a fact that rests on one is marked **UNCONFIRMED**. Quote briefly, a sentence or a clause.
- **Never fill a requirement or a service fact from memory or training data.** These laws, policies and prices change often. A page you cannot read is listed as unread, with its URL. Some sites refuse automated fetches; try the legal text's own publisher (for example the state legislature's site, `ecfr.gov`, `uscode.house.gov`, `govinfo.gov`) before you call a source unreadable. A source too large to fetch is recorded as not re-read, as SV3's recheck did for California's bulk data.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - create an account, sign up, start a trial, request a demo or a quote, submit any form, or send a message to anyone, a vendor included;
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
git merge-base --is-ancestor cf0ac604da77cff5917e20dd9d1389c5c7448b0c HEAD && echo "PR49 present"   # must print "PR49 present"
git diff --name-only origin/main HEAD | grep -v -E '\.md$'                                           # must print nothing
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- docs/planning/store-legal-safety-requirements.md   # must print nothing
git ls-tree -r --name-only origin/claude/magical-wozniak-yfmmx2 docs/testing/evidence/ | grep -c 'a05-v-verification-services'   # must print 0
git show origin/claude/magical-wozniak-yfmmx2:docs/planning/a05-v-verification-services.md | sed -n '/^## Sessions/,$p'   # must show "None yet."
```

If a check fails, stop and report. The prompt is stale if `<START_SHA>` is not on the live manager branch, if the matrix changed there after it, or if the brief's "Sessions" already records a session.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`;
- the brief, `docs/planning/a05-v-verification-services.md` (revision 2): its outcome, owned paths, exclusions, acceptance checks and report format bind you;
- OD-55, OD-60 and OD-61 in `docs/continuity/owner-directions.md`;
- DM-52 section 16 (`docs/continuity/dev-manager/reviews/2026-11-10-dm-52-sv2-brief.md`) and DM-83 section 3 (`docs/continuity/dev-manager/reviews/2026-11-17-dm-83-a05-v-brief-and-pf02-1-1.md`), which say why each row is taken;
- the matrix's header, sections 1, 7, 8, 9 and 10, and each of the 60 rows the brief's table lists;
- the three earlier recheck records, for their method and form: `docs/testing/evidence/2026-11-08-p06-3-matrix-recheck.md`, `2026-11-10-od-60-matrix-recheck.md` and `2026-11-11-sv3-matrix-recheck.md`.

## 3. What to do

Do the brief's three outcomes, in its words. In short:

1. **The recheck of the 60 rows.** Re-read each row's source today. Find the row's quotation in the text you read, as one continuous string; say so where it matched only after normalising white space or punctuation, and read it in place. Update the row's Source cell in the matrix's existing form: `read 2026-11-01, rechecked <today> (A05-V)` (keep any earlier recheck note). If a requirement has changed, correct the row in place and say so in the record; delete nothing and keep every ID. Then add the header's **Rechecks** entry for this recheck, and correct any sentence of sections 9 and 10 that states a row whose requirement or status changed, marked as corrected at this recheck.
2. **The three searches** (the brief's PP5 text): US state laws on biometric identifiers or biometric data other than BIPA, including a biometric provision inside a wider law and any biometric provision of a privacy law already in the matrix that applies below its general thresholds; state laws on identity verification by dating services; and Apple's and Google's own rules on face or biometric data. A law or rule already in a row is rechecked there, not added again (Colorado's dating safety law is UST-20). Each new row takes the next free ID in its section, is marked as added at this recheck, and is added to the Rows columns of sections 7 and 8 where it belongs. Each search that finds nothing is recorded with the sources tried.
3. **The comparison of services:** at least three identity verification companies (a US government photo ID with a live selfie matched to it, decided automatically), at least three automated photo check services, and the hash-matching options for child sexual abuse material (which of those services offer it, and the programmes that give it to services like Glow, with their published eligibility terms). Say how you chose the candidates. For each, every field the brief's outcome 2 lists, including whether the service uses the images, data or templates for its own purposes. A fact not published is written as not published.
4. **The facts table** for DM-52 section 16's six items: cost; consent, with BIPA's written release; what each service keeps and for how long; what a member can do when a check fails; whether the ID's birth date replaces the typed one; whether one service also runs G-02's detection step. Each cell cites the rows and pages that bear on it. No recommendation.

**Method** (as the earlier rechecks did it):
- Fetch each source into its own new directory in your scratchpad, never inside the repository. Read it with a Python script run with `-I`, kept outside that directory, that strips tags and flattens white space; read PDFs with `pdftotext`.
- Search for each quotation as one continuous string in the stripped text.
- Hash each fetched file with SHA-256 and record it; commit no fetched file.

**The record** (`docs/testing/evidence/<today's date>-a05-v-verification-services.md`) holds: what, who and when; the method; the rows taken and why (the brief's table); the sources table (URL fetched, final URL, HTTP status and bytes, SHA-256, page date); the quotation checks, row by row; each changed requirement, with old and new text; the searches and what each found, with the rows each new row was compared with; the comparison; the facts table; the unread sources; deviations and limits; and the note "Research, not legal advice", as the matrix's opening note says.

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
- A script lists each of the brief's 60 rows whose Source cell lacks `rechecked <today> (A05-V)`; the list must be empty, or each row on it must be named in the record as not re-read, with the reason.
- The record's quotation table has one line per row, with its source's SHA-256 and the result.
- Each new row names its primary text, and the record lists the rows of the same state or store it was compared with.
- Each service fact names its page and the date read.

## 5. Push

Commit only the two owned paths, with a message that names A05-V. Push your session branch with `git push -u origin <branch>`. Push nothing else.

## 6. Report

Report, in this order:
- your branch, the start SHA and your head SHA, and the changed paths;
- the rows rechecked, with each changed requirement named; the rows not re-read, with the reason;
- the rows added, with their primary texts; the searches that found nothing;
- the services compared, by kind;
- every check in section 4, with its exact output;
- the sources unread, with their URLs;
- deviations, limits and open questions.
