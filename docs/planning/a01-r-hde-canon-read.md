# A01-R — HDE's canon read against the contract request

- **Work ID:** A01-R (cross-cutting; research; M09's O3; PF01 1.19, §8 "The owner's track" and §10, A01).
- **Status:** brief and prompt written; the prompt is with Nathan.
- **Owner:** Nathan Amthor, as HDE's owner and the app's integration owner (OD-23). **Manager:** App Manager 12. **Research:** one session, started by Nathan.
- **Revision 1, 19 November 2026.**
- **Starting point:** `main` at `d3273f3` (PR55), with the manager branch's records after it; the prompt names the exact commit.
- **Prompt:** [`docs/ephemeral/2026-11-19-a01-r-hde-canon-read-prompt.md`](../ephemeral/2026-11-19-a01-r-hde-canon-read-prompt.md), revision 1 (TypeSafe v8.2: Opus 5.5 at high).
- **Evidence home:** `docs/testing/evidence/<the session's date>-a01-r-hde-canon-read.md`, written by the session on its own branch. The manager adds "Manager verification of A01-R".

## Why

- **Nathan, 19 November 2026 (OD-78):** *"I mean actual working app components, database, server, code, HDE complete and integrated."* The MVP prototype needs HDE integrated, and HDE is the one part the app cannot build (D08).
- **OD-75 (D-01 (a)):** A01-R runs first; Nathan then sets HDE's date in HDE's own process from its gap list.
- **M09's finding** (its record, section 4.5): HDE's canon specifies the pair read and HDE's repository largely builds it, but it is not proven live, and the way a new member's chart gets into HDE is not built. No real profile can become visible without it (C-03).
- **The contract request** (`docs/planning/hde-contract-request.md`) asks 35 questions (C01 to C35). It was written on 25 September from an earlier snapshot, before HDE's canon was attached (OD-74) and before OD-61 (a birth time is required; the chart is calculated at sign-up).

## Outcome

One research session reads HDE's canon in `amthorn78/glow-docs` (`docs/hde/pfcanon/`, read-only) and writes one record:

1. **Each question, C01 to C35,** answered from the canon: the document, its section and its version, at the glow-docs commit read, quoted where the words matter. Each answer is marked:
   - **specified** (the canon states it as a contract or design);
   - **built** (the canon's build notes, state-of-the-repository or audit records say it exists in HDE's code);
   - **proven live** (a record shows it working against HDE's real database over HTTP);
   - **not in the canon**.
2. **Conflicts:** every place the canon and the app's plan disagree (PF01 §5 and D08, the contract request, A01, A07, OD-61, the provisional HDE seam), each with both texts quoted.
3. **What HDE must still build for the app,** in two lists:
   - **for the MVP prototype** (OD-78): the least that lets the app's own adapter create a new member's chart from their birth details (with a required birth time, OD-61) and read the pair result, against a deployed HDE the app's server can reach, with an authentication mechanism and a test environment;
   - **before launch:** the rest of C01 to C35 (deletion, export, consent withdrawal, data rights, rate limits, change notices).

   Each gap names where it would sit in HDE's own process (the epic, phase or change-record form PF06, PF16 and PF20 use), as a proposal for Nathan to take there. The session writes nothing in glow-docs.
4. **The app's side:** for each of the four app-owned ports (`BirthInput` / `ChartResolver`, `CompatibilityProvider`, `CompatibilityProjection`, `EngineLifecycle`; `docs/architecture/provisional-hde-seam.md`), how HDE's specified shape maps to it, and what the app's adapter would need that the canon does not give.
5. **A draft receipt** in the form of the contract request's section 6, marked draft and not a delivered contract.
6. **A one-page summary for Nathan:** what HDE already has, what it must build for the prototype, the order in which to build it, and what he must decide in HDE's process.

## Owned paths (the session's)

- **It writes,** on its own session branch, its evidence record only.
- **It never changes** any other file, anything in `amthorn78/glow-docs`, anything in Notion, or anything on GitHub but its own branch's push.

## Manager-owned

This brief and the prompt; the contract request; the handoff, the register and the mistakes log; Notion; the verification.

## Exclusions

- **No call to HDE** or to any HDE service, database, route or CLI, and no change to HDE (D08). Reading HDE's canon authorizes neither (OD-74).
- **No credential** read, printed or used; the environment is checked by names only, and the `AWS_*` names stay unread (OD-76).
- **No call** to any provider, Railway, Cloudflare or a database.
- **No write** to glow-docs, and its prompt libraries and skills are not this application's workflow (OD-74; `AGENTS.md`).
- **No decision:** HDE decides its contract (PF00); Nathan sets its date in HDE's process.

## Dependencies and inputs

`amthorn78/glow-docs`, attached to the session (OD-74), read at the commit the session records; the contract request; PF01 §5, D08, §10's A01 and A07; the provisional HDE seam and provider conformance; OD-23, OD-60, OD-61, OD-74, OD-75, OD-77 and OD-78; M09's record, section 4.5.

## Acceptance checks

- `git diff --name-only <prompt commit> <session head>` lists only the evidence record.
- The trusted classifier, taken from `main`, prints `"reason": "ordinary-docs-only"` for that comparison.
- Every question C01 to C35 has a row with its marking and its citation (document, section, version, glow-docs commit), or "not in the canon".
- Each gap in the prototype list names the question it answers.

## Classification expectation

Ordinary documentation: one Markdown file, outside any `.claude/` directory. No application CI and no code review. The manager reads it whole when it integrates.

## Review plan

- **No Dev Manager read before it runs:** the prompt authorizes no credential use and no live action, and the item decides nothing.
- **After it reports:** the manager checks a sample of citations against glow-docs, integrates the record, and gives Nathan the prototype list in OD-32's form for HDE's process. PF01 1.20, the plan revised around the prototype (OD-78), uses the list and goes to the Dev Manager.

## Sessions

- **Revision 1** (19 November 2026): the brief and the prompt, for `Glow App - No Stream`.
