# Reasoning-strength matrix and the TypeSafe request v5

**Status:** in force from 27 September 2026 for every prompt given after it (OD-33). This file is the home of the matrix, of the v5 request and of its pre-registered rule; the Notion page *TypeSafe effort scorer — Glow app usage log* carries a matching copy and the uses table. Where the two differ, this file wins (OD-27).

**Why it exists.** Nathan, 27 September 2026: *"I am feeling less trust about the scoring. There is a huge gap between fable extra high and opus extra high. I want you to make sure all strength levels are researched and included in this matrix for both models. They are Low, Medium, High, Extra, Max, and Ultracode for both models. It's important that your semantic query contains enough information for actual informed decisions. Revise and then re-score the last task."* The earlier requests, v4 (a level) and m1 (a model), sent TypeSafe one paragraph about the work and criteria of one line each; neither said what a level costs or does on either model, and v4's second question was written for another project.

**How it was researched.** App Manager 4 ran a research workflow at Nathan's opt-in (the word "ultracode" in his message): five agents each researched one topic (the levels on Fable 5.1, the levels on Opus 5.5, ultracode, the cross-model comparison, this project's scoring history) from Anthropic's public documentation and the local Claude API skill, returning only sourced claims; five skeptics re-opened every cited source and corrected or refuted claims; three agents then drafted request designs from the verified claims and three hostile reviewers attacked each. The manager chose and edited the final request. Every sentence in the matrix and the request below traces to a source in the list at the end. Sixteen agents, 2.1 million tokens, 42 minutes.

## 1. The six settings

Anthropic's models expose **five effort levels**, `low`, `medium`, `high`, `xhigh` (called "extra high" in this project) and `max`, through `output_config.effort`. Effort is "a behavioral signal, not a strict token budget": it scales how readily and how long the model thinks, how many tool calls it makes and how much it explains and verifies, on all output tokens [S1]. Both models support all five; Fable 5.1 defaults to `high`, Opus 5.5 to `medium`; setting the default explicitly is the same as omitting it [S1, S4].

**Ultracode is not a sixth effort level.** In Claude Code it is a harness setting: the session runs at `xhigh` per request ("it sends xhigh to the model") and, for every substantive task, plans and runs a dynamic workflow, a script that orchestrates dozens to hundreds of agents in the background and returns only the result, with the large-run warning and the 20-concurrent-subagent limit switched off [S6, S7, S8]. It is unavailable when workflows are off, the model lacks `xhigh` or an effort cap below `xhigh` applies; then the session runs at the highest allowed level with ultracode off [S6]. The word `ultracode` typed in a prompt runs that one task as a workflow without changing the session's level [S7]. `ultrathink` is a different keyword and orchestrates nothing [S6]. Without ultracode a session can already spawn up to 20 concurrent subagents and can run a workflow when asked [S7, S8]. So the matrix has six columns per model, and the sixth is "extra high plus many-agent workflows".

**The level scale is calibrated per model** [S6, S9]. No source maps Fable 5.1's levels to Opus 5.5's level for level; the only cross-model guidance is to start with Opus 5.5 for most workloads and to use Fable 5.1 "for demanding reasoning and long-horizon agentic work, or when your evals on Claude Opus 5.5 at higher effort still fall short" [S4]. The manager's earlier statement that "a lower level on Fable often matches a higher one on Opus" is a judgement, not a measurement; the vendor's statements compare each model with its own predecessor only [S3, S5].

**Cost.** Fable 5.1 lists at $10 input and $50 output per million tokens, Opus 5.5 at $4 and $20, so 2.5 times per token; cache reads are $0.25 against $0.20 per million, nearly equal, so on long agentic sessions that re-read a cached prefix the gap is below 2.5 times [S2, S4]. Cost is judged per completed task, not per token: a higher sticker price is cheaper when the job finishes in fewer turns, and per-token lists do not predict the ranking [S10]. No measured cost-per-task comparison of Fable 5.1 against Opus 5.5 exists; the one previous-generation figure is that Opus 5 matched Fable 5 on a saturated coding subset at about 60 percent of its cost, and both successors are documented as cheaper per task than their predecessors [S3, S5, S10]. Fable 5.1's comparative latency is rated slower, Opus 5.5's moderate; single Fable requests on hard tasks can run 15 minutes at higher effort [S3, S4].

**Refusal classifiers.** Both models run cybersecurity, biology and reasoning-extraction classifiers; both permit finding vulnerabilities in source code; neither performs high-risk dual-use security work; either can decline benign security-adjacent work by mistake, and Claude Code falls back to an Opus model when that happens [S3, S5, S6]. Nothing in the sources says one refuses security reviews more than the other.

## 2. The matrix

Each cell: the work it fits; then its cost and behaviour. "Measured" figures are Anthropic's runs on the previous generation (Fable 5, Opus 5) and are labelled so; none was measured on these two models. "In this project" figures are from the uses table (section 3).

| Level | Opus 5.5 ($4 / $20) | Fable 5.1 ($10 / $50) |
|---|---|---|
| **Low** | Short, scoped, latency-sensitive steps that are not intelligence-sensitive: a subagent's mechanical step, a named command, recording given answers. On several coding evaluations Opus 5.5 at low came close to Opus 5 at high at much lower cost [S5]. The cheapest cell; fewest and tersest tool calls; the model may skip thinking. Measured on Opus 5, long-horizon coding lost about 8 points at low for a quarter of the cost [S10]. Never run in this project. | The same class of step inside a Fable session. At low Fable 5.1 "is often competitive with Opus and Sonnet on cost per task while performing better", measured against earlier models, not Opus 5.5 [S3]. It calls search and retrieval tools less at low and answers from memory more, so not for look-up-heavy steps [S3]. Never below $10 / $50 per token. Never run in this project. |
| **Medium** | Opus 5.5's default and Anthropic's starting point for most workloads: well-specified agentic coding, code review and knowledge work with a written task list (named fixes each with a test, a bounded review against named findings, document updates). At medium it "matches or exceeds" Opus 5 at high on coding and knowledge-work evaluations, in fewer steps and tokens [S5]. Moderate token savings; measured on Opus 5, medium gave up about 2 points of long-horizon coding for half the cost [S10]. Never run in this project. | Routine work kept on Fable where switching model would lose the session's reasoning state (Opus 5.5 reads no Fable thinking blocks) [S3]. At medium, results "roughly match Claude Fable 5 at lower cost" [S3]. Moderate savings against high, still 2.5 times Opus per token. Never run in this project. |
| **High** | Real judgement with moderate stakes, one step above the default: reviewing a bounded diff for defects, diagnosing a failing check, a correction pass where a miss would be costly. "Spends as many tokens as the task needs" [S1]; Opus 5.5 thinks more per turn than Opus 5 at the same level [S5]. In this project: three runs at high (the flake-fix review, C2, C3), all adequate. | Fable 5.1's default and recommended start: "complex reasoning, difficult coding problems, agentic tasks"; step up only for the most capability-sensitive work [S1, S3]. Buys "excellent verification behavior"; on routine work it "can gather context and deliberate beyond what the task needs" [S3]. Single requests can run many minutes; set a large `max_tokens`. Long deliverables are best written at high, because at xhigh and max they may be drafted twice [S3]. Anthropic estimates 25 to 45 percent lower cost than Fable 5 at default effort, from cheaper cache reads [S11]. Never run in this project. |
| **Extra high** | "Extended capability for long-horizon work": long-running agentic and coding tasks over 30 minutes with token budgets in the millions [S1]; Anthropic reserves it for a measured gain over high [S5]. Turns run longer than on Opus 5 at the same level; `max_tokens` of 64K to 128K [S5]. If Opus at this level still falls short, Fable is the next step [S4]. In this project: the most-used cell, 11 runs before OD-30 (Opus levels), all adequate. | "The most capability-sensitive agentic and coding work" [S1]: a new system's first live runs, establishing the soundness of a large new system, work where Opus 5.5 at higher effort has fallen short [S4]. Fable 5.1's gains over Fable 5 are widest at the higher levels [S3]. Turns of many minutes, `max_tokens` 128K, long deliverables roughly double their output tokens [S3, S10]. In this project: the I2a review and I2b ran here, both adequate. |
| **Max** | "Absolute maximum capability with no constraints on token spending" [S1], for when correctness matters more than cost [S12]. Uncapped; the most thinking per turn; on earlier models and in Claude Code's own table, max "may show diminishing returns and is prone to overthinking" [S5, S6]. In this project: I2a ran here (the new harness's first live runs) and was adequate where m1 read Fable. | The deepest reasoning of the most capable model in one session: root cause of a systemic failure after earlier fixes failed, an audit for any bypass of a new guard. The most expensive single-session cell; the same diminishing-returns and double-drafting caveats [S3, S6]. Never run in this project (the log's three max runs were Opus levels). |
| **Ultracode** (extra high plus many-agent workflows) | Work in dozens to hundreds of independent units whose per-agent steps are well specified: a codebase-wide sweep for one class of defect, a migration across hundreds of files, research cross-checked by independent agents, a plan drafted from several angles and adversarially reviewed [S7]. Each substantive task becomes one or more workflows; every agent bills its own requests; "meaningfully more tokens" than one session, no large-run warning, no subagent cap [S7, S8]. The lower per-agent price is what keeps a large run affordable. Never run in this project. | The same shapes of work where every agent must be the most capable, or where the result must be built from independent agents adversarially checking one another for a decision that cannot be revisited. The most expensive cell of all: dozens to hundreds of agents at 2.5 times the price; Anthropic advises a smaller model on stages that do not need the strongest one [S7]. Not for a bounded change or review that one reader can hold, since a session already has 20 concurrent subagents [S8]. Never run in this project. |

## 3. What this project's history can and cannot show

The uses table holds 20 rows (24 to 27 September 2026). Levels run: extra high 11, max 3, high 3, three not yet run. Low and medium were never run and never read by v4 (P(low) 0.00 in every row; P(medium) at most 0.07). Manager and TypeSafe disagreed on the level six times; in every case the higher level was run, and "better call" went by convention to whoever named the level run, never by running the other level. All 17 judged outcomes are "adequate"; "too low" and "too high" have never been recorded, and two sessions that missed things a later pass caught were kept "adequate" because an independent review exists to catch them. So the history cannot rank levels, cannot show that a lower level would have failed or that a higher one was wasted, and holds no session cost or duration figures. Ultracode has never been run here: v4's flag fired six times and was not followed. The Dev Manager's DM-01 finding stands: the scorer gates nothing and has not yet earned its cost. The matrix above therefore rests on Anthropic's published guidance, not on this project's outcomes; the outcomes of the next sessions, recorded against the cell run, are what will test it.

## 4. The request v5

One request replaces v4 and m1 for every prompt given after 27 September 2026. It sends the same one or two sentences describing the session's work (never code, diffs, prompt bodies, records or credentials) and asks three questions: a five-rung `effort` score whose rungs carry the vendor's level definitions and measured anchors; an `orchestration` choice that carries ultracode as what it is, a harness setting; and a `model` choice whose options and trade-off carry price, positioning, latency, predecessor comparisons and classifier facts. Product names do not appear; the options are `most_capable_model` and `strong_lower_cost_model`, as in m1. `POST https://api.typesafe.ai/v1/systemone`, `Content-Type: application/json`, `jev-1.13.0` pinned, no Authorization header (the `Glow app` environment attaches the credential). About 3,100 input tokens per request against 800 to 1,000 for v4 or m1.

**Action-text template** (from the next prompt on; the re-score below used the existing text so that its readings compare with v4's and m1's): one or two sentences that state the object and its size in round independent units (files, endpoints, sources, phases), whether a task list already exists, whether the cause is known, whether a live run of new code occurs, whether a later independent review follows, and whether the work decomposes into many independent units that must be examined or cross-checked separately.

**Pre-registered rule** (saved before any v5 run):

- **Level.** S is the effort Score on 0 to 4; L is the nearest rung, exact halves going up: 0 low, 1 medium, 2 high, 3 extra high, 4 max. The same rule as v4, so the level axis stays comparable.
- **Ultracode.** U is true if and only if P(`many_agent_workflow`) is 0.5 or more. When U is true the cell's level column reads "ultracode", which in Claude Code means extra high per request with workflow orchestration on; L is recorded beside it, never combined with max or a lower level. v4's flag rule is retired. If Nathan's harness cannot run ultracode for the chosen model, a U-true reading is recorded as "ultracode read, unavailable" and the cell used is (M, extra high); that is not a re-reading.
- **Model.** M is Fable 5.1 if P(`most_capable_model`) is 0.5 or more, else Opus 5.5, as m1.
- **Cell.** (M, ultracode) if U, else (M, L). No adjustment of L for M, because no verified level-for-level mapping exists.
- **Recorded, never used to gate:** the three confidences, the five rung probabilities, whether the effort mass is bimodal (two non-adjacent rungs each 0.30 or more), the runner-up rung, P(`many_agent_workflow`) and P(`most_capable_model`) as numbers.
- **Governance.** The manager writes its own model, level and ultracode call in the prompt header before sending the request; the reading is written beside it; Nathan picks; no conditional commitment is made on any reading (DM-01 P8); the readings live only in the prompt header and the uses table. Outcomes are judged on the existing scale (adequate, too low, too high), and the row records the model and level run, whether ultracode was used, whether the session used subagents, and the better call, with "not tested" written whenever the other party's call was not run.
- **Versioning.** Rows are tagged `v5` and are not pooled with the 20 v4 rows. The pre-registered ten-session comparison restarts with the first v5 row. Changing the request creates v5.1, and so on.

**Calibration gate, pre-registered before the run.** Cases: the ten P06.1 action texts recorded in the uses table, unchanged (I1, the I1 review, the flake-fix review, C1, its review, C2, its review, C3, its review, I2a). The eleventh text m1 used, the flake diagnosis, was not recorded in its row or anywhere in the repository, so it is not available; the gate uses ten. Labels, fixed before the run: **level** is the manager's call already recorded in each row (I1 extra high; I1 review max; flake-fix review high; C1 extra high; C1 review extra high; C2 high; C2 review extra high; C3 high; C3 review extra high; I2a max); **model** is m1's labels (Fable 5.1 for I1, the I1 review and I2a; Opus 5.5 for the other seven); **orchestration** is `one_session` for all ten (none was run with ultracode). Pass: level within one rung of the label on at least 8 of 10; `one_session` on at least 9 of 10; model matching the label on at least 8 of 10. If the gate fails, one fitted revision, v5.1, is allowed and the same gate applied once; a second failure keeps v4 and m1 in use and is reported. Limit, as for m1: the labels are the manager's own, so the gate shows whether v5 says what the manager meant, not whether the calls are right.

**Results** are recorded in section 5 after the run, with the time the run started.

**The request** (`ACTION` is replaced by the session's description):

```json
{
 "model": "jev-1.13.0",
 "state": {
  "action": "ACTION"
 },
 "questions": {
  "effort": {
   "type": "score",
   "instructions": {
    "question": "How much reasoning depth does the AI coding session described in `action` need? The five settings below are ordered from cheapest to most expensive. Judge the judgement the work requires, not how much text it produces or how many files it touches. Weigh two risks: that a weaker setting misses something that matters, and that a stronger setting spends time and tokens deliberating or gathering context without finding more.",
    "tradeoff": "Each step up spends more tokens and takes longer. The setting is a behavioural signal, not a token budget: lower settings make fewer, terser tool calls, act without preamble and may skip thinking on simpler problems; higher settings make more tool calls, explain the plan first, verify more and summarise more. The two models default to different settings (one to the second, one to the third) and the scale is calibrated per model, so a level name is not the same amount of thinking on both. Measured on the previous generation of these models: on research and knowledge work the lowest setting lost 1 to 3 points for a third to a half off cost per task, the second matched the default at 70 to 85 percent of its cost, and the default bought nothing measurable over the second; on long-horizon coding the second lost about 2 points for half the cost and the lowest about 8 points for a quarter; on work at the reasoning ceiling each step up bought about 2.4 rubric points. Lower settings also finish sooner (4.5 against 7.9 minutes per problem in one research run)."
   },
   "criteria": [
    "low: the most efficient setting, with significant token savings and some capability reduction; for short, scoped, latency-sensitive steps that are not intelligence-sensitive, such as a subagent's mechanical step, running a named command, recording given answers or relaying a message. The model may skip thinking entirely, and on one of the two models it calls search or retrieval less and answers from memory more, so a miss is likely wherever the work must look things up or verify.",
    "medium: a balanced setting with moderate token savings, for agentic work that needs a balance of speed, cost and performance, and often a favourable balance; the default on one of the two models. Fits routine judgement inside a clear procedure: filling a template, a small bounded edit, summarising results, a fix whose file and defect are already named. On research-type work the next setting up measured no gain over it; on long-horizon coding this setting gave up about 2 points.",
    "high: spends as many tokens as the task needs for excellent results; the default on the other model and its vendor's starting point for complex reasoning, difficult coding and agentic tasks. Fits real judgement with moderate stakes: reviewing a diff for defects, diagnosing a failing check, drafting a plan section. It buys strong verification behaviour; on routine work it can gather context and deliberate beyond what the task needs.",
    "extra high: extended capability for long-horizon work, meaning long-running agentic and coding tasks over 30 minutes with token budgets in the millions; reserved for the most capability-sensitive work where a quality gain over high is expected or measured. At this setting and above, single requests on hard tasks can run many minutes, and a long deliverable may be drafted in thinking and then written again. Fits complex judgement where a miss is costly: designing a multi-part change, reconciling conflicting rules, a first execution of a plan against a live system, verifying a large new piece of work whose soundness is not yet established.",
    "max: absolute maximum capability with no constraint on token spending, for the deepest possible reasoning, where correctness matters more than cost. It can show diminishing returns and is prone to overthinking, and one of the two models tends to think more per turn than its predecessor did, most of all at the top two settings. Fits open-ended, high-stakes analysis with no clear procedure: root-cause analysis of a systemic failure after earlier fixes failed, redesigning a process, searching for any way to bypass a new guard."
   ]
  },
  "orchestration": {
   "type": "choice",
   "instructions": {
    "question": "Should the session described in `action` run as one conversation, or with the harness setting that plans a many-agent workflow for every substantive task?",
    "tradeoff": "The workflow setting is a harness setting, not a model setting: every request runs at extra high (not max) and the session writes and runs a script that orchestrates many agents, dozens to hundreds per run, with the concurrent-subagent limit lifted and the large-run warning off; the script holds the loop and the intermediate results, and only the final answer returns to the conversation. Each request then uses meaningfully more tokens and takes longer than the same work at high, and one request can become several workflows in a row. Without it, one conversation can already spawn up to 20 concurrent subagents for reads, research or a second-opinion pass, and every result lands in its own context."
   },
   "criteria": {
    "one_session": {
     "what": "Work that one conversation can hold and coordinate: a bounded change, diff or review that a single reader can hold, a diagnosis following one thread of evidence, a plan, a first live run, a correction pass; including work that delegates reads, research or a second opinion to a few subagents.",
     "not_for": "Work whose units number in the dozens or hundreds and must each be examined, transformed or cross-checked independently, or whose trustworthiness depends on several independent agents checking one another.",
     "examples": [
      "Review one pull request for defects, with a subagent re-reading the riskiest module",
      "Fix the five findings a review named",
      "Run a new integration against a sandbox for the first time and record what happened"
     ]
    },
    "many_agent_workflow": {
     "what": "Work that needs more agents than one conversation can coordinate, or whose result must be built from independent agents cross-checking or adversarially reviewing one another: a codebase-wide sweep of every module for one class of defect, a migration across hundreds of files, research cross-checked across many sources, a plan drafted from several independent angles before committing to one.",
     "not_for": "One bounded change, diff or review that a single reader can hold, or a task with a written list, however many lines it spans.",
     "examples": [
      "Audit every API endpoint in the service for missing authorisation checks",
      "Migrate 400 call sites to a new client and verify each",
      "Draft a redesign from three independent angles and weigh them"
     ]
    }
   }
  },
  "model": {
   "type": "choice",
   "instructions": {
    "question": "Which model should run the AI coding session described in `action`, at whatever setting it needs?",
    "tradeoff": "Both are frontier agentic coding models with the same five settings, and the workflow setting is available on both; the setting scale is calibrated per model, so a level name is not the same amount of thinking on both. The most capable model lists at $10 per million input tokens and $50 per million output tokens; the strong lower-cost model at $4 and $20, so 2.5 times the price per token, with cached input reads nearly equal ($0.25 against $0.20). The most capable model's comparative latency is slower against moderate, and its single requests on hard tasks can run many minutes. Cost is judged per completed task, not per token: a higher sticker price is cheaper when it finishes in fewer turns, and per-token lists do not predict the ranking. Evidence: the most capable model at its lowest setting is often competitive on cost per task with earlier lower-tier models while scoring higher (not yet measured against this lower-cost model); in the previous generation, on a coding subset where both largely saturated, the lower-cost model matched the most capable one (91.7 against 91.3 percent) at about 60 percent of its cost. The vendor's guidance is to start with the lower-cost model for most workloads and to use the most capable one for demanding reasoning and long-horizon agentic work, or when the lower-cost model at a higher setting still falls short. The lower-cost model defaults to medium, where it matches or exceeds its predecessor at high; on several coding evaluations its low comes close at much lower cost; it generates output more than 30 percent faster than its predecessor, and early testers report stronger code review with fewer false alarms. The most capable model's gains over its predecessor are widest at higher settings and in agentic coding over hours-long sessions, research, and long-context retrieval. Both run similar safety classifiers; both permit finding vulnerabilities in source code."
   },
   "criteria": {
    "most_capable_model": {
     "what": "Work where even a strong model often falls short and a miss is costly or would pass unnoticed: demanding reasoning; long autonomous work with several dependent phases; open-ended diagnosis where the cause is not yet known; designing and building a new system with many interacting parts; establishing the soundness of a large new system for the first time; a first run of new code against a live external service; or work on which the lower-cost model at a higher setting has already fallen short.",
     "not_for": "Work whose task list is already written and on which both models largely succeed: applying named fixes, reviewing a correction against the findings it claims to fix, checking results against a list, recording decisions or updating documents, even when the code is large or security-sensitive; there the 2.5 times price buys little.",
     "examples": [
      "Find why a background job intermittently loses data after two earlier fixes failed",
      "Build a new payment integration and run it against the provider's sandbox for the first time",
      "Audit a large new login service for any way to bypass its checks"
     ]
    },
    "strong_lower_cost_model": {
     "what": "Well-specified agentic coding, code review and knowledge work that a strong model completes reliably, including long-running coding sessions on a known task list: applying named fixes each with a test, reviewing a bounded change against the findings it claims to fix, checking results against a list, recording decisions, writing or updating documents. The vendor's starting point for most workloads.",
     "not_for": "Open-ended diagnosis or design, establishing the soundness of a large new system for the first time, long work with several dependent phases that includes a first live run of new code, or work on which this model at a higher setting has already fallen short.",
     "examples": [
      "Fix five review findings that each name a file and a defect, adding a test for each",
      "Review a correction pass against the findings it says it fixed",
      "Update the project's handoff notes after a verified release"
     ]
    }
   }
  }
 }
}
```

## 5. Runs

### Calibration run, 27 September 2026

Pre-registration was pushed at `b755b07` (09:35:23 UTC); the run started at 09:35:45 UTC and ended at 09:35:48 UTC. Every request returned HTTP 200 from `jev-1.13.0` in 0.23 to 0.63 s, with 2,728 to 2,866 input tokens and 90 output tokens. **The gate passed on all three axes: level within one rung 10 of 10; `one_session` 10 of 10; model 10 of 10.** So v5 is in use unchanged.

| Text | Label (level, model) | Effort score, rung (probabilities) | P(many-agent) | P(most capable) (confidence) | v5 cell |
|---|---|---|---|---|---|
| P06.1-I1 implementation session | extra high, Fable 5.1 | 2.97, extra high (high 0.03, extra high 0.97; confidence 0.97) | 0.36 | 0.98 (0.97) | Fable 5.1, extra high |
| P06.1-I1 exact-head code and security review | max, Fable 5.1 | 3.15, extra high (extra high 0.85, max 0.15; confidence 0.87) | 0.23 | 0.98 (0.97) | Fable 5.1, extra high |
| P06.1 flake fix exact-head review | high, Opus 5.5 | 1.94, high (medium 0.07, high 0.91, extra high 0.02; confidence 0.92) | 0.00 | 0.01 (0.98) | Opus 5.5, high |
| P06.1-C1 offline correction pass on the I1 harness | extra high, Opus 5.5 | 1.88, high (medium 0.24, high 0.64, extra high 0.12; confidence 0.70) | 0.00 | 0.00 (0.99) | Opus 5.5, high |
| P06.1-C1 exact-head review | extra high, Opus 5.5 | 2.47, high (high 0.53, extra high 0.47; confidence 0.60) | 0.02 | 0.01 (0.98) | Opus 5.5, high |
| P06.1-C2 second offline correction pass on the harness | high, Opus 5.5 | 1.97, high (medium 0.15, high 0.73, extra high 0.12; confidence 0.77) | 0.00 | 0.01 (0.97) | Opus 5.5, high |
| P06.1-C2 exact-head review | extra high, Opus 5.5 | 2.78, extra high (high 0.28, extra high 0.65, max 0.07; confidence 0.70) | 0.01 | 0.04 (0.91) | Opus 5.5, extra high |
| P06.1-C3 third offline correction pass on the harness | high, Opus 5.5 | 2.03, high (medium 0.13, high 0.70, extra high 0.17; confidence 0.75) | 0.00 | 0.02 (0.96) | Opus 5.5, high |
| P06.1-C3 exact-head review | extra high, Opus 5.5 | 2.73, extra high (high 0.30, extra high 0.66, max 0.04; confidence 0.71) | 0.01 | 0.01 (0.97) | Opus 5.5, extra high |
| P06.1-I2a revocation and safety, live | max, Fable 5.1 | 2.99, extra high (high 0.01, extra high 0.98, max 0.01; confidence 0.97) | 0.08 | 0.94 (0.88) | Fable 5.1, extra high |

What the run shows. The level rung agreed exactly with the manager's recorded call in 7 of 10 and sat one rung below it in 3 (the I1 review and I2a, called max, read extra high; the C1 pass and the C1 review, called extra high, read high at 0.64 and at 0.53 against 0.47). The four correction passes and the fix review read high or the boundary of medium and high, never extra high. The many-agent option never rose above 0.36 (the I1 implementation, a first live build; confidence 0.28), so the sixth column did not fire on any bounded session, as intended. The model readings sit near 0 or 1 in 9 of 10 (I2a 0.94). As with m1, the labels are the manager's own, so this shows that v5 says what the manager meant, not that the calls were right. Compared with v4 on the same texts, v5 reads the same rung in 8 of 10 and one rung lower in 2 (the C2 review and the C3 review are unchanged at extra high; the C1 review moved from high 2.54 to high 2.47; no text moved up).

### Re-score of the I2b review prompt, 27 September 2026

The action text is the one v4 and m1 read at 07:58 UTC, unchanged, so the readings compare. Sent 09:35:48 UTC; HTTP 200 in 0.29 s; 2,866 input and 90 output tokens.

- **Manager's call, recorded at 07:58 UTC before any reading:** Fable 5.1, extra high, no ultracode.
- **v5 reading: Opus 5.5, extra high, no ultracode.** Effort score 2.73: extra high 0.72, high 0.27, max 0.01, confidence 0.76; not bimodal; runner-up high. Many-agent workflow 0.03 (one session 0.97, confidence 0.93). Most capable model 0.18 (confidence 0.65).
- **Against the earlier readings:** v4 read extra high (2.77) and raised its ultracode flag from the foreign shape question (P(single session) 0.12); v5 reads extra high (2.73) and no ultracode (0.03). m1 read Opus 5.5 at 0.71; v5 reads Opus 5.5 at 0.82 with its price, positioning and code-review facts in front of it. The informed request agrees with the manager on the level and on no ultracode, and disagrees on the model more firmly than m1 did.
- **Disposition:** both calls go to Nathan with the prompt, as OD-10 and OD-30 require; the manager's call stands as recorded and is not changed after the reading. The row in the uses table records both.

## Sources

Public pages were fetched on 27 September 2026 by the research workflow and re-read by its skeptics; the local skill files are the Claude API skill bundled with Claude Code (`claude-api`, `shared/` folder), outside this repository.

- [S1] Effort levels, "How effort works", "Effort with tool use", per-model recommendations and best practices: https://platform.claude.com/docs/en/build-with-claude/effort
- [S2] Fable 5.1 model page (pricing, default effort): https://platform.claude.com/docs/en/models/fable-5-1/overview ; Opus 5.5 model page: https://platform.claude.com/docs/en/models/opus-5-5/overview
- [S3] Prompting Claude Fable 5.1 (effort sweep, cost per task at low, search triggering at low, double drafting at xhigh and max, classifiers): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1 ; and the skill's `model-migration.md`, sections "Migrating to Claude Fable 5.1" and "... from Claude Fable 5" (15-minute requests, "gather context and deliberate beyond what the task needs", "gap is widest at higher effort levels", thinking blocks not read by Opus 5.5)
- [S4] Models overview (compare table: pricing, cache-read fractions, default effort, comparative latency; "start with Claude Opus 5.5 for most workloads"): https://platform.claude.com/docs/en/about-claude/models/overview
- [S5] Prompting Claude Opus 5.5 ("Calibrate effort": medium matches or exceeds Opus 5 at high, low comes close, more thinking per turn, reserve xhigh and max for measured gains; safeguards): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5 ; what's new: https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5 ; and the skill's `model-migration.md`, "Migrating to Claude Opus 5.5"
- [S6] Claude Code model configuration (effort table, ultracode definition and availability, max caveats, "calibrated per model", ultrathink, automatic model fallback): https://code.claude.com/docs/en/model-config
- [S7] Claude Code dynamic workflows (what a workflow is, the ultracode keyword and setting, cost profile, size guideline, limits): https://code.claude.com/docs/en/workflows
- [S8] Claude Code subagents (20 concurrent subagents per session; ultracode sessions exempt; effort inheritance): https://code.claude.com/docs/en/sub-agents ; costs: https://code.claude.com/docs/en/costs
- [S9] Claude Code settings reference (`ultracode` key, precedence, keyword trigger setting): https://code.claude.com/docs/en/settings-reference
- [S10] The skill's `cost-optimization.md` (cost per completed task; measured effort curves on Fable 5 and Opus 5; `max_tokens` guidance)
- [S11] Anthropic's announcement of Fable 5.1 and Mythos 5.1 (25 to 45 percent lower cost than Fable 5; low or medium similar to or better than Fable 5; cyber safeguards): https://www.anthropic.com/claude-fable-and-mythos-5-1
- [S12] The skill's `agent-design.md` ("Use max when correctness matters more than cost")
