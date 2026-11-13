# Phase: Planning — Steps 3a–3g (Stop After the Spec)

Read when the design brief is approved (Step 2.5, `phases/design-gate.md`), with `phases/planning-inputs.md` (the counters and the paths BRIEF, TIERS, TIER_PLAN, TRACING, the observability line, EVALS).

---

## 3a. Planning Subagent

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/planning.md`
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, **BRIEF** with its approved revision and tier, **TIERS** and **TIER_PLAN** (when the approved tier is not `none`), `SDD/.records/progress.md`, existing `SDD/adr/` (to reference accepted ADRs), `SDD/UBIQUITOUS_LANGUAGE.md` (if present), **the observability line** copied verbatim, **TRACING** and **EVALS** when that line says `present`, **HARVEST** when there is one (derived as at 2.5a in `phases/design-gate.md`, again just before this spawn), and on a next-tier cycle the previous tier's research document.
- **Outputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, append `progress.md`.
- **Task:** Read the research and the approved design brief and create the full specification. The design brief is binding on Key decisions, Not doing, and answered questions; its delivery outline is the starting slice order. Record every departure in the spec's `## Deviations from Design Brief`; write `None.` when there are none. Specify the approved tier and nothing beyond it: set `tier:` in the frontmatter, and list what is left for later under `## Deferred to Later Tiers` (omit both when the approved tier is `none`). The spec MUST include the YAML frontmatter fields — `review_panel` (only the specialists whose area the change touches, at most three; `agent-security` and `slice-integrity` are added outside the three), `cross_cutting_decisions`, `delivery_mode`, `agent_security` — populated thoughtfully. The body's **agentic-surface detection** applies: resolve `agent_security: auto` against the research and spec, and when the surface is present set the field and append `agent-security` to `review_panel`. The body's **per-slice authoring default** applies: set `delivery_mode: per-slice` unless the feature yields fewer than 2 genuine vertical slices, in which case `whole-feature` with a one-line justification in the spec. The spec MUST include the `## Modules` section with ≥1 `MODULE-XXX` entry (`Public Interface`, `Hides`, `Risk` low/medium/high, `Spec refs`) — prefer deep modules. Use canonical names from the glossary when present. The body's `delivery_mode` value-validation (enum fail-fast) and slice-practicality gate stay in force. The body's **tracing rule** applies: the spec carries `tracing:` (`auto` unless the task description in this prompt, the research, or the brief forces it), and — when the observability line says `present` and the field is not `false` — a `### Planned call graph` under `## Modules` with every entry point, LLM call, and external call marked, plus a `Traced nodes:` line per slice in per-slice mode; otherwise neither. The body's **evals rule** applies: the spec carries `evals:` (`auto` unless the task description in this prompt, the research, or the brief forces it), and — when evals are on for this spec by the table under `evals:` in the body — an `### Evals` sub-section under `## Validation Strategy` with every case written out, a `Sign-off:` line under `### Manual Verification` for each requirement only a person can accept, and an `Evals:` line per slice in per-slice mode; otherwise none of the three.

**If the practicality gate fired** — the subagent's return says so — the spec now says `delivery_mode: whole-feature` with a `Slicing not applicable: <reason>` line. Do not stop: the stop after the spec (3g) shows the reason.

Then spawn a second **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/planning-complete.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, **BRIEF** with its approved revision and tier, **TIERS** (when the approved tier is not `none`), **EVALS** when the observability line says `present` (the body's Evals check), `SDD/UBIQUITOUS_LANGUAGE.md` (if present).
- **Outputs:** updated SPEC (if gaps found), updated `SDD/UBIQUITOUS_LANGUAGE.md` (incremental — only if the spec introduced new domain terms), append `progress.md`.
- **Task:** Validate completeness against the checklist (including the Modules-section verification and the design-brief and tier checks), ensure every research finding is incorporated or recorded as deferred, verify frontmatter fields are populated, and capture any glossary deltas the spec introduced (execute inline).

---

## 3b. ADR Capture from Spec Frontmatter

Read the spec's `cross_cutting_decisions:` frontmatter. If non-empty, for each topic label spawn an **`agent-engineering:sdd-workhorse`** subagent — **one at a time, each after the previous has returned**. Never in parallel: each takes the highest existing ADR number plus one and regenerates the index, so two at once collide on both.
- **Body:** `bodies/adr-capture.md` — **AUTO mode** (frontmatter-declared decisions are pre-approved; no user confirmation).
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, existing `SDD/adr/`.
- **Outputs:** new `SDD/adr/NNNN-slug.md`, updated `SDD/adr/README.md`, append `progress.md`.
- **Task:** Extract the decision, alternatives, rationale, and consequences for the topic from spec+research. If context is insufficient, emit a warning and skip the topic rather than fabricating rationale. Apply the scope test, then write the ADR.

If `cross_cutting_decisions:` is empty/absent, skip this step.

---

## 3c. Specialist Panel Review — two stages

Panel composition comes from the spec's `review_panel:` frontmatter: the specialists whose area the change touches, at most three (`bodies/planning.md` → `review_panel:`). If it is absent or empty, the panel is `module-depth` alone. To the chosen values add `slice-integrity` when the spec declares `delivery_mode: per-slice`, and `agent-security` when the spec's `agent_security:` gate is open (see below); neither counts toward the three. A `review_panel:` with more than three other values is not cut by the orchestrator: planning-complete (3a) checks the field, and the stop after the spec (3g) shows the panel that ran.

**`agent-security` gate.** Read the spec's `agent_security:` frontmatter — `auto` (default when absent), `true`, or `false`:
- `true` → include `agent-security` in the panel, and the specialist skips its own scope gate. It can only skip it if it is told: pass the line `agent_security: true` in its prompt.
- `false` → never include it; the user has declared the feature non-agentic.
- `auto` → include it when the spec describes an agentic surface (LLM/model call, tool or MCP definition, agent memory or retrieval store feeding model context, inter-agent messaging, or a model output driving an action on an external system). The planning body (3a) normally resolves `auto` and appends the value to `review_panel:` itself; when it did not, the orchestrator applies the same test. Pass `agent_security: auto` in the specialist's prompt. Including it under `auto` is cheap — the specialist short-circuits when its own scope gate is closed.

The `agent_security:` value also gates Step 4b's agentic-surface code-review lens, so it must be resolved even when `review_panel:` was authored by hand.

**The `tracing` and `evals` gates — the binding decision.** Two things are decided here, once per planning run, before any panel spawn: whether this feature's real call tree is checked against the planned one (`tracing`), and whether what the model really answers is checked against the spec's cases (`evals`). They are decided when no `## Gates - ` line follows the latest `Planning Phase - COMPLETE` line in `progress.md` — so on the first entry to 3c after a spec is written or rewritten, and not again when the fix loop below re-runs the panel. Read the spec's `tracing:` and `evals:` frontmatter (for each, absent means `auto`) and the observability line. The two gates are independent: neither needs the other to be on.

| `tracing:` | Observability line | Gate |
|---|---|---|
| `false` | — | `off` |
| `auto` | `absent` | `off` |
| `auto` | `present` | `on` |
| `true` | `present` | `on` |
| `true` | `absent` | none — halt (below) |
| any other value | — | none — halt (below) |

| `evals:` | Observability line | The spec has a model in it | Gate |
|---|---|---|---|
| `false` | — | — | `off` |
| `auto` | `absent` | — | `off` |
| `auto` | `present` | no | `off` |
| `auto` | `present` | yes | `on` |
| `true` | `present` | — | `on` |
| `true` | `absent` | — | none — halt (below) |
| any other value | — | — | none — halt (below) |

- **"The spec has a model in it"** is asked only for `evals: auto` with the record `present`. It is yes when the spec carries an `### Evals` sub-section — the planning subagent judged so — or when the spec describes an agentic surface by the test of the `agent-security` gate above. Apply that test to the spec's text whatever its `agent_security:` field says: the two gates share a test and nothing else.
- **Record it.** Append one line to `progress.md`: `## Gates - tracing: <on|off>, evals: <on|off>`. The latest such line holds both gates for the rest of this cycle: every later spawn that needs one is passed exactly `tracing: on` or `tracing: off`, and exactly `evals: on` or `evals: off`, and no subagent reads a field to decide for itself. An edit to either field after this point — by a fix subagent or by hand — changes nothing until Step 3 runs again (a re-plan writes a new spec, a new `Planning Phase - COMPLETE`, and so a new line here).
- **No specialist is given either gate.** The panel reviews neither the planned call graph nor the evals; the spec critical review (3d) does.
- **`true` with no foundation, or a value outside the three — in either field → halt and spawn nothing.** Append this block to `progress.md`, then tell the user what cannot be decided, with one of the messages below for each field named:

  ```markdown
  ## Awaiting Gate Decision

  SPEC: SDD/requirements/SPEC-[###]-[feature-name].md
  tracing: <the value, verbatim>   evals: <the value, verbatim>   Observability record: <present|absent>
  Cannot be decided: <tracing | evals | tracing, evals>
  Set each field named above to a value this cycle can honour, then run `/sdd-flow continue`.
  ```

  > **The spec asks for tracing, and this application has no tracing foundation.** `tracing: true` in `SDD/requirements/SPEC-[###]-[feature-name].md` needs `SDD/OBSERVABILITY.md`, which was absent when the design brief was approved. A cycle keeps the answer it had at approval, so tracing cannot be switched on in this one. Set `tracing:` to `auto` or `false` in the spec and run `/sdd-flow continue`; run `/observability-init` once this cycle is finished, and the next cycle is traced.

  > **Invalid `tracing` value '[value]' in `SDD/requirements/SPEC-[###]-[feature-name].md`.** Allowed values: `auto`, `true`, `false`. Edit the spec frontmatter and run `/sdd-flow continue`.

  > **The spec asks for evals, and this application has no tracing foundation.** `evals: true` in `SDD/requirements/SPEC-[###]-[feature-name].md` needs `SDD/OBSERVABILITY.md` — the eval run is set up from what that record says, and its command is written into it — which was absent when the design brief was approved. A cycle keeps the answer it had at approval, so evals cannot be switched on in this one. Set `evals:` to `auto` or `false` in the spec and run `/sdd-flow continue`; run `/observability-init` once this cycle is finished, and the next cycle can check what the model says.

  > **Invalid `evals` value '[value]' in `SDD/requirements/SPEC-[###]-[feature-name].md`.** Allowed values: `auto`, `true`, `false`. Edit the spec frontmatter and run `/sdd-flow continue`.

  No gate line is written — not for the field that could be decided either: the line is written whole or not at all. `/sdd-flow continue` — or the user's reply in the same session — comes back to this decision and reads both fields again (`phases/rare/resume.md` → `## Awaiting Gate Decision`). When both resolve, the `## Gates - ` line written then is what ends the halt.

### Stage 1 — specialists in parallel

Spawn **one subagent per `review_panel:` value, IN PARALLEL** (single message, multiple spawns). The panel is always Claude subagents — it is not on the second-model review route (`references/second-model-review.md` §1); the spec's second-model review is 3d. The agent type depends on the value:

- **Values with a shipped specialist agent** — `security`, `agent-security`, `performance`, `data-modeling`, `api-contract`, `module-depth`, `reliability`, `slice-integrity` → `agent-engineering:sdd-spec-<panel-value>-specialist`.
- **Every other allowed value** — today `accessibility`, `privacy`, `cost` → `agent-engineering:sdd-workhorse`, with the same body and the panel value in its prompt. No specialist agent ships for these; the body's Section 4.6 defines them. Never spawn an agent type that is not in the list above.
- A value that is in neither list is not a panel value: drop it and note that in `progress.md`.

Each spawn gets:
- **Body:** `bodies/panel-specialist.md` ("apply ONLY the Section your panel value names").
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, **BRIEF** with its approved revision and tier (the body's *Respect the Brief* principle: a finding that adds scope the brief did not ask for is an addition, not a defect), the panel value, and the resolved PANEL-FINDINGS output path. For the `agent-security` value, also pass the resolved **CATALOG** path (`SKILL.md` → SKILL_ROOT resolution) and the resolved gate value as the line `agent_security: true` or `agent_security: auto` (above). When the spec's frontmatter carries `tier:`, also pass **TIERS** — the body's *Respect the Tier* principle needs it.
- **Output:** `SDD/.records/reviews/PANEL-FINDINGS-[panel-value]-[feature-name]-[YYYYMMDD].md`.
- Each specialist writes exactly one findings file and spawns nothing. (The `slice-integrity` specialist short-circuits unless `delivery_mode: per-slice`.)

### Stage 2 — synthesis

After all Stage 1 specialists return, spawn ONE **`agent-engineering:sdd-critical-reviewer`** subagent (Opus — the synthesis is the adversarial work):
- **Body:** `bodies/panel-synthesis.md`
- **Inputs:** the exact list of `SDD/.records/reviews/PANEL-FINDINGS-*-[feature-name]-[YYYYMMDD].md` paths written in Stage 1, the spec path, **BRIEF** (to tell a finding from an addition), and **TIERS** when the spec carries `tier:` (the floor). (Its counter trigger may be raised to N+5 for an N-specialist panel.)
- **Output:** `SDD/.records/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`.
- **Task:** Read each PANEL-FINDINGS file from disk, dedupe cross-specialist overlap, aggregate severity, and emit the verdict. Collect every `ADDITION` into the review's `## Additions for the owner`, numbered `A1`, `A2`, …; additions carry no severity and never count toward the verdict. It spawns nothing.

### Act on the verdict

- **`PROCEED`** (no HIGH; at most two MEDIUM, none of them cross-domain) → continue to 3d. Any MEDIUM findings it carries are resolved at 3e with the critical review's; LOW findings are listed, not fixed.
- **`STOP AND RECONSIDER`** (any HIGH) or **`REVISE BEFORE PROCEEDING`** (3+ MEDIUM or cross-domain MEDIUM) → enter the bounded **fix-and-re-review loop** below.

### Fix-and-re-review loop (bounded — max 2 iterations)

Each iteration:

1. **Record iteration state** in `progress.md` under `## Panel Review Iterations`: iteration number, HIGH/MEDIUM/LOW counts, verdict, timestamp.
2. **Spawn a fix subagent** (`agent-engineering:sdd-workhorse`):
   - **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/.records/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, **BRIEF** with its approved revision and tier, **TIERS** when the spec carries `tier:`, the tracing gate as the line `tracing: on` or `tracing: off`, **TRACING** when it is `on`, the evals gate as the line `evals: on` or `evals: off`, and **EVALS** when it is `on`.
   - **Outputs:** updated spec (in place), "Findings Addressed" appended to the panel review.
   - **Task:** Resolve every HIGH and MEDIUM finding; each resolution cites the specific spec change made. Do NOT claim resolution without an actual edit. Embed the **Brief and tier rules for spec fixes** (below) verbatim, and beneath them the **Call-graph rule for spec fixes** with `tracing: on` and the **Evals rule for spec fixes** with `evals: on`.
3. **Re-run Step 3c** (both stages — fresh PANEL-FINDINGS + a fresh synthesis) over the updated spec, producing a new/overwritten `PANEL-SPEC-*`.
4. **Act on the new verdict, in this order:**
   - **The panel now returns `PROCEED`** → exit the loop and continue to 3d — at any iteration, the second included. A passing verdict is never a halt.
   - **Progress-stall check** (verdict still STOP/REVISE): if HIGH did not strictly decrease (when HIGH was non-zero), OR (in REVISE case) MEDIUM did not strictly decrease → **halt immediately**. The fix subagent is making no real progress; further iterations waste tokens or degrade review quality (placating edits).
   - **Still STOP/REVISE and iteration < 2** → next iteration.
   - **Still STOP/REVISE after iteration 2** → halt (cap exhausted).

### Brief and tier rules for spec fixes (embed verbatim in the 3c and 3e fix prompts)

> **Stay inside the approved brief.** If a resolution departs from the design brief's Key decisions, Not doing list, or answered questions, add an entry to the spec's `## Deviations from Design Brief` — do not leave that section saying `None.`. Never reopen a question the user has answered.
>
> **Additions are not yours to make.** The panel review's `## Additions for the owner` lists scope the brief did not ask for. Do not add any of it to the spec: the owner decides each at the stop after the spec. Resolve only findings.
>
> **Deferral is a resolution only for absent scope.** When the spec carries `tier:` and a finding says something is *missing* — an unspecified edge case, variation, or hardening — you may resolve it by adding a row to `## Deferred to Later Tiers` (next free `DEFER-XXX`, `Came from` = `review`) instead of specifying it, provided the tier standard's cut tests place it in a later tier and its floor does not protect it. If this tier can reach the deferred case, add the `FAIL-XXX` entry for its loud failure in the same edit. A finding about behaviour this tier *does* specify is a defect: fix it — it can never be deferred. A finding that says a deferral is unsafe, or that a part is built ahead for a later tier, is resolved by specifying the item or removing the part.

### Call-graph rule for spec fixes (embed verbatim in the 3c and 3e fix prompts when the gate is `tracing: on`)

> **Keep the planned call graph true to the spec.** A fix that adds, removes, renames, or moves an entry point, a call to a model, a call to an external system, or a delivery slice updates `### Planned call graph` and the slices' `Traced nodes:` lines in the same edit: every such call is a marked node, every LLM node states its maximum, and in per-slice mode every marked node is in exactly one slice's line. Marks follow the tracing standard at the path in your prompt. Never change the spec's `tracing:` field.

### Evals rule for spec fixes (embed verbatim in the 3c and 3e fix prompts when the gate is `evals: on`)

> **Keep the evals true to the spec.** A fix that adds, removes, renumbers, or changes a requirement about what a model says, or a delivery slice, updates `### Evals`, the `Sign-off:` lines under `### Manual Verification`, and the slices' `Evals:` lines in the same edit: every part of what such a requirement promises is checked by a hard eval, or by a judged eval of a sign-off requirement — one hard eval on one part does not cover the rest; every case is written out in full; and in per-slice mode every case is in exactly one slice's line. Kinds and cases follow the standard at the EVALS path in your prompt (§1, §2). Moving a behaviour between checked-by-rule and judged departs from what the design brief told the user about how quality is judged: record it under `## Deviations from Design Brief`. Never change the spec's `evals:` field.

### On halt (cap exhausted or progress stall)

- Leave all artifacts in place — do not delete the spec or any panel review document.
- Append a final `### Panel Review Halt` entry to `progress.md`: total iteration count, final HIGH/MEDIUM/LOW counts, halt reason (`cap-exhausted` | `progress-stall`), and a next-action hint.
- Do NOT proceed to 3d/3e/3f. The spec has not been accepted.
- Emit:

> **Flow halted at panel review.** Spec did not pass specialist review after [N] iteration(s). Halt reason: [cap-exhausted | progress-stall].
> Final verdict: [STOP AND RECONSIDER | REVISE BEFORE PROCEEDING]
> Unresolved HIGH findings: [count]
> Unresolved MEDIUM findings: [count]
> Latest panel review: `SDD/.records/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`
> Iteration history: `SDD/.records/progress.md` → "Panel Review Iterations"
> The fix subagent could not resolve findings autonomously. Address the remaining HIGH/MEDIUM issues manually in the spec (they likely require design judgment), then run `/sdd-flow continue` to resume.

---

## 3d. Spec Critical Review Subagent

Run this review by the cycle's **review route** (`references/second-model-review.md`). On the Claude route, spawn an **`agent-engineering:sdd-critical-reviewer`** subagent (Opus). Either route is given:
- **Body:** `bodies/critical-review.md` — apply its **Planning Phase** section.
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/.records/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`, **BRIEF** with its approved revision and tier, **TIERS** when the spec carries `tier:`, the tracing gate as the line `tracing: on` or `tracing: off`, **TRACING** when it is `on`, the evals gate as the line `evals: on` or `evals: off`, and **EVALS** when it is `on`.
- **Outputs:** `SDD/.records/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md`.
- **Task:** Adversarial review of the spec — the Design Brief Fidelity block (is the spec what the user approved?), ambiguities, untestable criteria, dropped research findings, contradictions, the feasibility-arithmetic gate over the spec's `### Quantitative Ledger` (do the spec's own numeric constraints permit its own numeric goals?), and the body's **Planned Call Graph** block (with `tracing: on`: is every entry point, LLM call, and external call the spec describes a marked node, and assigned to a slice? with `tracing: off`: is the spec free of one?), and the body's **Evals** block (with `evals: on`: does every requirement about what the model says have a hard eval, or a judged eval and a sign-off line, and can each case be applied as written? with `evals: off`: is the spec free of evals?). Complementary to the panel: critical-review is generalist/adversarial; the panel was domain-specialist.

---

## 3e. Address Spec Review Findings (panel + critical, combined)

Spawn an **`agent-engineering:sdd-workhorse`** fix subagent:
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/.records/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`, `SDD/.records/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, **BRIEF** with its approved revision and tier, **TIERS** when the spec carries `tier:`, the tracing gate as the line `tracing: on` or `tracing: off`, **TRACING** when it is `on`, the evals gate as the line `evals: on` or `evals: off`, and **EVALS** when it is `on`.
- **Outputs:** updated SPEC, append `progress.md`.
- **Task:** Resolve every HIGH and MEDIUM finding from BOTH reviews (a LOW finding is listed, not fixed) — clarify ambiguous requirements, make criteria testable, add missing edge cases or record them as deferred, resolve contradictions, address panel anti-patterns, incorporate dropped research findings. Append "Findings Addressed" sections to both review documents. Embed the **Brief and tier rules for spec fixes** (3c) verbatim, and beneath them the **Call-graph rule for spec fixes** (3c) with `tracing: on` and the **Evals rule for spec fixes** (3c) with `evals: on`.

---

## 3e.5. Check the Spec Fix

3e changed the spec after both reviews read it, and nothing has read those changes. Run one check by the cycle's **review route** (`references/second-model-review.md`; on the Claude route an **`agent-engineering:sdd-critical-reviewer`** subagent, Opus):
- **Body:** `bodies/critical-review.md` — its **Fix Check** section, with the line `FIX CHECK` in the prompt.
- **Inputs:** the same as 3d, plus `SDD/.records/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md` and the PANEL-SPEC, each with its `Findings Addressed`.
- **Outputs:** a `## Fix Check` section appended to the CRITICAL-SPEC document.
- **Then** the orchestrator appends `## Spec Fix Check - CONFIRMED` or `## Spec Fix Check - OPEN (<h> HIGH, <m> MEDIUM)` to `progress.md`, from the section's first line (on the second-model route only after the run's `## Review Route` line).
  - **`CONFIRMED`** → 3f.
  - **`OPEN`, first time** → one more 3e fix spawn, given the `## Fix Check` section as its findings, then this check once more.
  - **`OPEN` again** → halt as 3c does on halt: leave everything in place, append `### Spec Fix Check Halt` with the open counts to `progress.md`, do not commit, and tell the user that the spec fix left [h] HIGH / [m] MEDIUM open, with the CRITICAL-SPEC path, and that `/sdd-flow continue` re-runs this check over the spec as they left it.

A LOW finding of the check is recorded in the section and does not hold the spec.

---

## 3f. Commit Planning Artifacts

The **orchestrator** runs the commit per `commands/commit.md` — no co-author attribution. Include the design brief, the tier plan, and every ADR change made since the research commit — the records written on approval at the design gate (2.5b) and those written in 3b, with the `SDD/adr/README.md` index and any superseded record edited along the way.

If `progress.md` exceeds ~500 lines, rotate it now (`phases/rare/rotation.md`).

---

## 3g. Stop After the Spec

**Fires every time planning reaches this point, and on every return to it. No flag skips it.** The spec was rewritten up to four times after the brief was approved (3a, the 3c loop, 3e, and 3e.5's one further fix), and the panel may have proposed more. Before any code is written the owner sees what the spec has become, and is asked to cut it down.

Read, from the files (not from a subagent's return):

- the spec's `## Deviations from Design Brief`: the first non-empty line of its body (the first line after the heading that is not blank, an HTML comment, or a horizontal rule). `None.` (case-insensitive, trailing period optional) means none. **An absent or empty section** means the spec is malformed: re-spawn the 3a completion subagent to add it (Error Handling's two-failure limit applies) — never read it as "no deviations";
- the latest PANEL-SPEC's `## Additions for the owner` — every numbered addition not already marked `accepted` or `declined` in it;
- the spec's `review_panel:`, `delivery_mode:`, and its `Slicing not applicable:` line when there is one;
- the brief's `## Growth budget`, and the spec's line count (`wc -l`).

Append this block to `progress.md`, emit the message, and STOP:

```markdown
## Awaiting Spec Approval

Spec: SDD/requirements/SPEC-[###]-[feature-name].md   Brief: SDD/requirements/DESIGN-[###]-[feature-name].md
```

> **The spec is ready. Nothing is built until you approve it.**
> Spec: `SDD/requirements/SPEC-[###]-[feature-name].md` ([N] lines). Panel: [the panel that ran]. Delivery: [per-slice, [M] slices | in one piece — [the `Slicing not applicable:` reason]].
> Growth budget you approved: [the brief's three lines, on one line].
> **Departures from the brief:** [each: what the brief said → what the spec says — why] [or "none"].
> **Proposed by the panel, not in the spec:** [each open addition: `A[n]` — one line] [or "none"]. `accept A1, A3` adds them; the rest are dropped.
> **Cut it down:** `/simplicity-challenge SDD/requirements/SPEC-[###]-[feature-name].md --brief SDD/requirements/DESIGN-[###]-[feature-name].md` lists what the spec could drop or defer; a cut that touches a decision you made in the brief is marked "needs your call". Then reply `cut` with the cuts you want, by their rows or in your words. Optional; the flow does not run it for you.
> Reply `approve` to start building[, accepting the departures above], `cut …` and/or `accept …` to change the spec first, or `stop`.

**The `Cut it down` line is a reminder, not a step.** The orchestrator never invokes `simplicity-challenge` itself and records nothing about whether it was run. Its verdict reaches the flow only as the owner's reply.

Act on the reply:

- **`approve`** → when the spec lists departures, append `## Design Deviations - ACCEPTED` to `progress.md`; mark each open addition `declined` in the PANEL-SPEC's `## Additions for the owner` (the orchestrator edits only that marker); then route to Step 4 (below).
- **`cut …`, `accept …`, or both** → first append `## Spec Stop Request` to `progress.md`, with the reply verbatim beneath it, so the request survives a session that ends mid-fix. Then spawn an **`agent-engineering:sdd-workhorse`** fix subagent (Safety-Net Rule, a fresh counter, `planning-compact.md`):
  - **Inputs:** the spec, **BRIEF** with its approved revision and tier, the latest PANEL-SPEC, **TIERS** when the spec carries `tier:`, the tracing gate as the line `tracing: on` or `tracing: off`, **TRACING** when it is `on`, the evals gate as the line `evals: on` or `evals: off`, **EVALS** when it is `on`, and the owner's reply **verbatim**.
  - **Outputs:** updated spec; the accepted additions marked `accepted` in the PANEL-SPEC's `## Additions for the owner`; append `progress.md` (`## Spec Stop Fix - Done`).
  - **Task:** Make exactly what the reply asks and nothing else; a change the spec already shows (a run interrupted earlier made it) is left as it is. **A cut** of something the spec does is moved to `## Deferred to Later Tiers` (next free `DEFER-XXX`, `Came from` = `owner cut`) when the spec carries `tier:`, or removed; a cut of a part (a module, a layer, an option) is removed. A cut the tier standard's floor protects is not made: say so in the return. When the cut case stays reachable, add its `FAIL-XXX` loud failure in the same edit. **An accepted addition** is specified as the panel review describes it. Record each change that departs from the brief under `## Deviations from Design Brief`. Keep every ID stable that the cut does not remove. Embed the **Call-graph rule for spec fixes** (3c) with `tracing: on` and the **Evals rule for spec fixes** (3c) with `evals: on`.
  - **Then** the orchestrator commits the spec (per `commands/commit.md`, message naming the SPEC and "changes asked for at the stop after the spec") and **shows this stop again**, read afresh from the files. The changed spec is not reviewed again: what the owner asked for is the owner's decision.
- **`stop`** → leave `## Awaiting Spec Approval` as the latest block and halt. `/sdd-flow continue` shows this stop again; the owner may have edited the spec by hand.

**Route to Step 4.** First append `## Planning - Accepted` to `progress.md` — one line, the spec path. It is the phase-detection marker that planning's reviews and this stop are done: `Planning Phase - COMPLETE` alone does not say so, because the completion subagent writes it back in 3a. Then read the spec's `delivery_mode:`: `whole-feature` → `phases/implementation-whole-feature.md`; `per-slice` → `phases/implementation-per-slice.md`. There is no other planning checkpoint: the design gate approved the design, and this stop the spec. The next stops are the slice pauses (per-slice mode); the final commit stops only for a sign-off or a growth-budget overrun (`phases/end-of-feature.md` → 4h).
