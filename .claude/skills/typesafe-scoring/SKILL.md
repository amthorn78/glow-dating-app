---
name: typesafe-scoring
description: Score a Glow app session prompt with TypeSafe (systemone, jev-1.13.0) using the project's request v6 and its pre-registered rule, and record the reading. Use this every time a manager writes or revises a prompt for Nathan (implementation, review, correction, diagnosis, manager start), every time a prompt is re-scored, and whenever anyone asks for "the TypeSafe reading", "the scorer", "which model and level", "the strength ladder", "rung probabilities" or the uses table. The reading, not the manager's judgement, is what Nathan sees. Never hand-write a request or a reading; run the script.
---

# TypeSafe scoring (request v6)

The reading is Nathan's decision aid (OD-10, OD-30, OD-33, OD-34). He has said he does not want the manager's own judgement of model strength; he wants the TypeSafe reading, with every probability, and his own pick recorded beside it. This skill exists so that the reading is produced the same way every time: same request body, same rule, same fields.

## What the reading is

One request, `request-v6.json` in this folder, sent to `POST https://api.typesafe.ai/v1/systemone` with the session's description as `state.action`. Two questions:

- `effort`: a six-rung score, 0 to 5, over **low, medium, high, extra high, max, ultracode**. Ultracode is the top rung of Nathan's strength ladder; in Claude Code it is the many-agent workflow setting, which runs every request at extra high and orchestrates a dynamic workflow of agents. The rung texts carry third-party benchmark figures (Artificial Analysis v4.3.2, ARC Prize, Vals AI, CodeRabbit, Dealwatch) and are worded by the cost of a miss and how much later work rests on the result, not by whether a procedure exists, so that max and ultracode are reachable for first reviews of new systems and first live runs and stay out of reach for listed correction passes. The evidence and its sources are in `docs/planning/reasoning-level-matrix.md`.
- `model`: a choice between `most_capable_model` (Fable 5.1) and `strong_lower_cost_model` (Opus 5.5), with third-party price, index, speed and head-to-head facts in the text. Product names never appear in the request.

**Pre-registered rule** (applied by the script, never by hand): rung = the rung nearest the score, exact halves up (0.5 medium, 1.5 high, 2.5 extra high, 3.5 max, 4.5 ultracode); model = Fable 5.1 if P(most_capable_model) is 0.5 or more, else Opus 5.5; cell = (model, rung). Flags are recorded, never used: "boundary" when the score is within 0.10 of a cut or the top two rungs are within 0.20 of each other; "model near tie" when P(most capable) is between 0.40 and 0.60. Run-to-run noise on identical text is about 0.05, so a boundary flag means the reading can flip.

## How to score a prompt

1. Write the action text: one or two sentences describing the session's work. Never code, diffs, prompt bodies, records or credentials. State the facts the rungs read: what the object is and whether it is new or already reviewed once; its size in round units (files, lines, endpoints, phases); whether a task list exists; whether a live run of new code against a provider occurs; whether a later independent review or gate follows; whether the work decomposes into many independent units that must each be checked. Readings move with these facts (removing the size and novelty words from a first-review text drops it from max to extra high), so leave none of them out and add none that are not true.
2. Run the script from the repository root, with the action text in a file so that quoting cannot corrupt it:

   ```bash
   python3 .claude/skills/typesafe-scoring/scripts/score.py --label "<step name>" --action-file action.txt --markdown
   ```

   The credential is attached by the `Glow app` environment; the script sends no Authorization header and reads no environment values. A non-200 answer is retried once, then reported as "not read", never filled in by hand.
3. Copy the printed header line into the prompt's header under **Model and reasoning setting**. It carries the cell, the score, the confidence, every rung probability, both model probabilities and the flags. Do not add the manager's own call to the message Nathan reads; if the manager records a call for later comparison, it goes into the uses table only (the *Manager level* and *Manager model* columns), written before the script is run.
4. Add or update the prompt's row in the Notion uses table (*TypeSafe effort scorer — Glow app uses*, data source `collection://e1d83c6d-23b7-447f-8bc6-dcbb4829f24e`) with the printed field values: *Version* v6, *TypeSafe level*, *TypeSafe model*, *Rung probabilities*, *Model probabilities*, *TypeSafe detail*, *Input tokens*, *Output tokens*; plus *Step*, *Date*, *Kind*, *Session*, *PR* and *PR metrics* as before, and the action text in *Notes* prefixed "Action sent (v6):". Read the row back.
5. When Nathan picks, record his pick in *Nathan's pick (level)* and *Nathan's pick (model)*. There is no outcome column (OD-34): the table records readings and picks, not the manager's verdict on them.

## Re-scoring several texts

`--batch cases.json` takes a list of `{"label": ..., "action": ...}` and `--out results.json` saves the raw results; use it for calibration runs and for re-reading earlier prompts after a request change. A changed request is a new version: copy the body to `request-v7.json`, update `REQUEST_PATH` in the script, pre-register the rule and the acceptance test in `docs/planning/reasoning-level-matrix.md`, push, and only then run. Acceptance does not use the manager's labels: it checks that archetype texts (a whole-codebase pre-launch audit; a first live run against real money; a first review of a large new system; a documented one-file fix; recording given answers) read the rung they plainly warrant, and that recorded correction passes stay at high or extra high.

## What not to do

- Do not paraphrase a reading, round differently, or omit a probability. The header line is the record.
- Do not re-word the action text after seeing a reading to move it. One text, one reading; a genuinely revised prompt gets a new reading, recorded as such.
- Do not turn a reading into a commitment ("ultracode if flagged"). Nathan picks (DM-01 P8).
- Do not edit `request-v6.json` in place. Versions are immutable once run.
