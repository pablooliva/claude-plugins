# Phase: Planning — Step 2.5 (Design Gate) · Steps 3a–3g

Read when research's last step (2e) is done. Phase-execution and fix subagents carry the Safety-Net Rule + a fresh counter file (`Reads: 0/15`) + the `planning-compact.md` compact body path. Body paths are `SKILL_ROOT/bodies/<file>.md`, resolved absolute.

Three resolved paths recur below. **BRIEF** = `SDD/requirements/DESIGN-[###]-[feature-name].md`, the design brief. **TIERS** = the tier standard resolved at Step 0 (`SKILL.md` → SKILL_ROOT resolution). **TIER_PLAN** = `SDD/flow/TIERS-[feature-name].md`, the record of what each delivery tier contains — on a next-tier cycle it is the path recorded at Step 0, which carries the first tier's feature name (no `-t2` / `-t3` suffix).

Two more come from the Step 0 record. **TRACING** = the tracing standard. **The observability line** = `Observability record: present` or `Observability record: absent` — whether the application has the tracing foundation (`phases/setup.md` → Step 0). A Step 0 record with no such line (a flow started before tracing was part of the flow) is read as `absent`. From 3c on, the **tracing gate** is `on` or `off`, as the latest `## Gates - ` line says; a spawn after 3c in a cycle that has no such line (it was planned before tracing was part of the flow) is passed `tracing: off`.

---

## Step 2.5: Design Gate

Runs after 2e and before 3a. The brief is the human's review surface for planning; the spec is held to it.

### 2.5a. Design-Brief Subagent

Spawn an **`agent-engineering:sdd-workhorse`** subagent **with the per-spawn model override `opus`** (the workhorse's instructions and tools, Opus's judgment — `sdd-critical-reviewer` is also Opus but carries an adversarial reviewer's persona, which is wrong for an author):
- **Body:** `bodies/design-brief.md`
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/research/CLARIFICATION-[###]-[feature-name].md` (if present), `SDD/UBIQUITOUS_LANGUAGE.md` (if present), existing `SDD/adr/`, **TIERS**, **TIER_PLAN** (the path, whether or not the file exists yet), `TIER: N` if the user passed `--tier N` or this is a next-tier cycle, and on a next-tier cycle the previous tier's research document.
- **Outputs:** **BRIEF**, **TIER_PLAN** (none when the brief says tiers are not applicable), append `progress.md`.
- **Task:** Write the design brief. Carries the Safety-Net Rule, a fresh counter (`Reads: 0/15`), and `planning-compact.md` as the compact body.

### 2.5b. Gate

**Fires in BOTH supervised and autonomous modes, every time the brief is written or rewritten. No flag skips it.**

The orchestrator never edits the brief. Approval state is the latest `## Design Brief - ` line in `progress.md` — `Drafted` (written by the brief subagent: not yet decided) or `APPROVED` (written by the orchestrator, below).

Read the brief — the gate message is built from it, not from the subagent's return. Then append this block to `progress.md`, emit the message, and STOP:

```markdown
## Awaiting Design Approval

Brief: SDD/requirements/DESIGN-[###]-[feature-name].md (revision N)
Re-plan: <no | yes — triggering retrospective: <retro-path>; from-slice: <SLICE-XXX | none>>
```

> **Design brief ready. No detailed planning happens until you approve it.**
> [After a revision round, first: one line stating what changed.]
> [The brief's "In one paragraph", verbatim]
> **Tiers:** building **Tier [N]** — [one line]. Left for later: Tier 2 — [one line]; Tier 3 — [one line]. [Or: "Tiers: not applicable — [the brief's reason]".]
> **Decisions made:** [D1 title — chosen option] · [D2 …]
> **Questions for you:** [Q1 — options — recommended (a)] · [Q2 …] [Or: "None."]
> **Research review:** [one line: critical-review severity and whether findings were resolved] [· ADRs captured: [numbers] — only when an `## ADR Capture - Done` line that names any already follows the latest `## ADR Candidates` entry, as at a re-plan's gate. Otherwise omit this part.]
> **ADR candidates:** [title — chosen option] · [title — chosen option] — written as decision records when you approve; name any you want dropped. [Both modes. Only when the latest `## ADR Candidates` entry lists any and no `## ADR Capture - Done` line follows it. Otherwise omit this line.]
> Brief ([N] lines): `SDD/requirements/DESIGN-[###]-[feature-name].md`
> Research: `SDD/research/RESEARCH-[###]-[feature-name].md`
> Reply with your answers and any changes — including `tier 2` or `tier 3` to build more now. `approve` accepts the brief as written, and is available once every question above has an answer. `stop` halts here.

If the brief's first line under its title is `Too large for one brief — recommend decomposition`, show that line and the seams it names in place of the summary, and offer only a change request or `stop` — there is nothing to approve.

Act on the reply:

- **Answers or changes** (including a different tier) → 2.5c.
- **`approve`** → accepted only when the brief's `## Questions for you` is `None.`. Append `## Design Brief - APPROVED (revision N, tier T)` to `progress.md` — `T` is the brief's recommended tier (`1`, `2`, `3`), or `none` when the brief says tiers are not applicable — and proceed to 3a. If any question is still open, **refuse**: reply with the open questions, say that each needs an answer ("use your recommendation" counts as one, given per question), and stay at the gate. Nothing is rewritten and nothing is assumed.
- **`stop`** → leave `## Awaiting Design Approval` as the latest block and halt. `/sdd-flow continue` re-shows this gate.

**ADR candidates (both modes).** Research's ADR step (2b) proposes candidates and writes none; this gate is where the user accepts them. The `ADR candidates:` line is built from the latest `## ADR Candidates` entry in `progress.md`, minus any candidate already dropped.

- **A reply that drops a candidate** — at approval or in an earlier round — is recorded at once: append `## ADR Candidate Dropped - <title>` to `progress.md`, one line per candidate, so the choice survives a stop.
- **On `approve`**, after the `## Design Brief - APPROVED` line and before 3a: if the entry lists any candidate not dropped, spawn ONE **`agent-engineering:sdd-workhorse`** subagent with `bodies/adr-capture.md` in **AUTO mode**, passing the research document, the existing `SDD/adr/`, and the accepted candidate titles ("write exactly these"). Then append `## ADR Capture - Done (<ADR numbers | none>)` — `none` when every candidate was dropped or the entry said `none`. The records are committed at 3f.
- A re-plan's gate does not repeat this: a `## ADR Capture - Done` line already follows the candidates.
- *Runs started on 3.5.1 or earlier in autonomous mode:* 2b wrote the records itself and left no `## ADR Candidates` entry. With no entry there is nothing to list and nothing to write on approval — omit the `ADR candidates:` line and skip the capture.

**Mirror the tiers to BB tasks** on approval, when `T` is not `none` — before spawning 3a, so the task keys the script writes into the tier plan are part of the 3f commit:

```bash
python3 "$SKILL_ROOT/scripts/tier-mirror.py" sync <TIER_PLAN> --active <T> --brief SDD/requirements/DESIGN-[###]-[feature-name].md
```

Record and report the result as `SKILL.md` → Tier Task Mirror requires. It creates the tracker project (if the BB project has none), the feature's parent task, and one sub-task per tier; sets the approved tier — and any lower tier not yet shipped, which the same cycle builds — to in progress and the rest to backlog; and attaches the brief, and this thread when the flow runs inside a BB thread.

Pass the approved revision number and tier (`Design brief: revision N, approved, Tier T`) in the prompt of every later spawn that reads the brief.

### 2.5c. Revise

Spawn an **`agent-engineering:sdd-workhorse`** subagent, again with the model override `opus`:
- **Body:** `bodies/design-brief.md` — its **Revision runs** section.
- **Inputs:** the 2.5a inputs, the existing brief, and the user's reply **verbatim**.
- **Outputs:** updated brief and tier plan; updated RESEARCH document only if the reply showed it wrong on a point of fact; append `progress.md` (a new `## Design Brief - Drafted (revision N)` line).

Then return to 2.5b. The loop has no cap — every round is requested by the user.

### Re-plan

`/sdd-flow continue --replan` (after a re-planning halt — `phases/protocols.md`; the slice that triggered it is committed first) re-enters here before Step 3: run 2.5c with the rolling ledger and the triggering retrospective as extra inputs and, in place of a user reply, the line `RE-PLAN: revise the brief from the ledger and retrospective`. The gate then fires as above, in both modes, with `Re-plan: yes` in the halt block — it also records the `--from-slice` value, so the flag survives the stop. On `approve`, continue to 3a with the ledger and retrospective in the planning subagent's prompt; the re-plan's planning run ends, like any other, with `## Planning - Accepted` at 3g.

---

## 3a. Planning Subagent

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/planning.md`
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, **BRIEF** with its approved revision and tier, **TIERS** and **TIER_PLAN** (when the approved tier is not `none`), `SDD/orchestration/progress.md`, existing `SDD/adr/` (to reference accepted ADRs), `SDD/UBIQUITOUS_LANGUAGE.md` (if present), **the observability line** copied verbatim, **TRACING** when that line says `present`, and on a next-tier cycle the previous tier's research document.
- **Outputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, append `progress.md`.
- **Task:** Read the research and the approved design brief and create the full specification. The design brief is binding on Key decisions, Not doing, and answered questions; its delivery outline is the starting slice order. Record every departure in the spec's `## Deviations from Design Brief`; write `None.` when there are none. Specify the approved tier and nothing beyond it: set `tier:` in the frontmatter, and list what is left for later under `## Deferred to Later Tiers` (omit both when the approved tier is `none`). The spec MUST include the YAML frontmatter fields — `review_panel` (default includes `module-depth`), `cross_cutting_decisions`, `delivery_mode`, `agent_security` — populated thoughtfully. The body's **agentic-surface detection** applies: resolve `agent_security: auto` against the research and spec, and when the surface is present set the field and append `agent-security` to `review_panel`. The body's **per-slice authoring default** applies: set `delivery_mode: per-slice` unless the feature yields fewer than 2 genuine vertical slices, in which case `whole-feature` with a one-line justification in the spec. The spec MUST include the `## Modules` section with ≥1 `MODULE-XXX` entry (`Public Interface`, `Hides`, `Risk` low/medium/high, `Spec refs`) — prefer deep modules. Use canonical names from the glossary when present. The body's `delivery_mode` value-validation (enum fail-fast) and slice-practicality gate stay in force. The body's **tracing rule** applies: the spec carries `tracing:` (`auto` unless the task description in this prompt, the research, or the brief forces it), and — when the observability line says `present` and the field is not `false` — a `### Planned call graph` under `## Modules` with every entry point, LLM call, and external call marked, plus a `Traced nodes:` line per slice in per-slice mode; otherwise neither.

**If the practicality gate fired** — the subagent's return says so, and an `## Awaiting Slicing Decision` block is the latest in `progress.md` — do not go on: the spec asked for slices and no meaningful ones exist. Show the block's two options and stop, in both modes (in supervised mode the user may answer in the same session). The answer is handled by `phases/protocols.md` → `## Awaiting Slicing Decision`, and both answers come back here: falling back to whole-feature continues with the completion spawn below, and a retry re-runs the spawn above with `RETRY SLICING: <hint>`. Neither skips 3b–3g.

Then spawn a second **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/planning-complete.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, **BRIEF** with its approved revision and tier, **TIERS** (when the approved tier is not `none`), `SDD/UBIQUITOUS_LANGUAGE.md` (if present).
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

Panel composition comes from the spec's `review_panel:` frontmatter. If absent or empty, apply the **default panel**: `security`, `performance`, `data-modeling`, `api-contract`, `module-depth` — plus `slice-integrity` when the spec declares `delivery_mode: per-slice`, plus `agent-security` when the spec's `agent_security:` gate is open (see below). (Other available values: `reliability`, `accessibility`, `cost`, `privacy`.)

**`agent-security` gate.** Read the spec's `agent_security:` frontmatter — `auto` (default when absent), `true`, or `false`:
- `true` → include `agent-security` in the panel, and the specialist skips its own scope gate. It can only skip it if it is told: pass the line `agent_security: true` in its prompt.
- `false` → never include it; the user has declared the feature non-agentic.
- `auto` → include it when the spec describes an agentic surface (LLM/model call, tool or MCP definition, agent memory or retrieval store feeding model context, inter-agent messaging, or a model output driving an action on an external system). The planning body (3a) normally resolves `auto` and appends the value to `review_panel:` itself; when it did not, the orchestrator applies the same test. Pass `agent_security: auto` in the specialist's prompt. Including it under `auto` is cheap — the specialist short-circuits when its own scope gate is closed.
- **CATALOG missing** (recorded at Step 0 — `SKILL.md` → SKILL_ROOT resolution) → the gate is closed for the whole run, whatever the spec says, `true` included: drop `agent-security` from the panel and pass no catalog path to any spawn. The warning in `progress.md` already says so. The specialist cannot review without its catalog, and a spawn that fails on a missing file is worse than a review that is visibly absent.

The `agent_security:` value also gates Step 4b's agentic-surface code-review lens, so it must be resolved even when `review_panel:` was authored by hand.

**`tracing` gate — the binding decision.** Whether this feature's real call tree is checked against the planned one is decided here, once per planning run, before any panel spawn. It is decided when no `## Gates - ` line follows the latest `Planning Phase - COMPLETE` line in `progress.md` — so on the first entry to 3c after a spec is written or rewritten, and not again when the fix loop below re-runs the panel. Read the spec's `tracing:` frontmatter (absent means `auto`) and the observability line:

| `tracing:` | Observability line | Gate |
|---|---|---|
| `false` | — | `off` |
| `auto` | `absent` | `off` |
| `auto` | `present` | `on` |
| `true` | `present` | `on` |
| `true` | `absent` | none — halt (below) |
| any other value | — | none — halt (below) |

- **Record it.** Append `## Gates - tracing: on` or `## Gates - tracing: off` to `progress.md`. The latest such line is the gate for the rest of this cycle: every later spawn that needs it is passed exactly `tracing: on` or `tracing: off`, and no subagent reads the field to decide for itself. An edit to the field after this point — by a fix subagent or by hand — changes nothing until Step 3 runs again (a re-plan writes a new spec, a new `Planning Phase - COMPLETE`, and so a new line here).
- **No specialist is given the gate.** The panel does not review the planned call graph; the spec critical review (3d) does.
- **`true` with no foundation, or a value outside the three → halt, in both modes, and spawn nothing.** Append this block to `progress.md`, then tell the user which of the two it is:

  ```markdown
  ## Awaiting Tracing Decision

  SPEC: SDD/requirements/SPEC-[###]-[feature-name].md
  tracing: <the value, verbatim>   Observability record: <present|absent>
  Set `tracing:` in the spec to a value this cycle can honour, then run `/sdd-flow continue`.
  ```

  > **The spec asks for tracing, and this application has no tracing foundation.** `tracing: true` in `SDD/requirements/SPEC-[###]-[feature-name].md` needs `SDD/OBSERVABILITY.md`, which was absent when this cycle started. A cycle keeps the answer it started with, so tracing cannot be switched on in this one. Set `tracing:` to `auto` or `false` in the spec and run `/sdd-flow continue`; run `/observability-init` once this cycle is finished, and the next cycle is traced.

  > **Invalid `tracing` value '[value]' in `SDD/requirements/SPEC-[###]-[feature-name].md`.** Allowed values: `auto`, `true`, `false`. Edit the spec frontmatter and run `/sdd-flow continue`.

  No gate line is written. `/sdd-flow continue` — or the user's reply in the same session — comes back to this decision and reads the field again (`phases/protocols.md` → `## Awaiting Tracing Decision`). When it resolves, the `## Gates - ` line written then is what ends the halt.

### Stage 1 — specialists in parallel

Spawn **one subagent per `review_panel:` value, IN PARALLEL** (single message, multiple spawns). The panel is always Claude subagents — it is not on the second-model review route (`references/second-model-review.md` §1); the spec's second-model review is 3d. The agent type depends on the value:

- **Values with a shipped specialist agent** — `security`, `agent-security`, `performance`, `data-modeling`, `api-contract`, `module-depth`, `reliability`, `slice-integrity` → `agent-engineering:sdd-spec-<panel-value>-specialist`.
- **Every other allowed value** — today `accessibility`, `privacy`, `cost` → `agent-engineering:sdd-workhorse`, with the same body and the panel value in its prompt. No specialist agent ships for these; the body's Section 4.6 defines them. Never spawn an agent type that is not in the list above.
- A value that is in neither list is not a panel value: drop it and note that in `progress.md`.

Each spawn gets:
- **Body:** `bodies/panel-specialist.md` ("apply ONLY the Section your panel value names").
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, the panel value, and the resolved PANEL-FINDINGS output path. For the `agent-security` value, also pass the resolved **CATALOG** path (`SKILL.md` → SKILL_ROOT resolution) and the resolved gate value as the line `agent_security: true` or `agent_security: auto` (above). When the spec's frontmatter carries `tier:`, also pass **TIERS** — the body's *Respect the Tier* principle needs it.
- **Output:** `SDD/reviews/PANEL-FINDINGS-[panel-value]-[feature-name]-[YYYYMMDD].md`.
- Each specialist writes exactly one findings file and spawns nothing. (The `slice-integrity` specialist short-circuits unless `delivery_mode: per-slice`.)

### Stage 2 — synthesis

After all Stage 1 specialists return, spawn ONE **`agent-engineering:sdd-critical-reviewer`** subagent (Opus — the synthesis is the adversarial work):
- **Body:** `bodies/panel-synthesis.md`
- **Inputs:** the exact list of `SDD/reviews/PANEL-FINDINGS-*-[feature-name]-[YYYYMMDD].md` paths written in Stage 1, plus the spec path. (Its counter trigger may be raised to N+5 for an N-specialist panel.)
- **Output:** `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`.
- **Task:** Read each PANEL-FINDINGS file from disk, dedupe cross-specialist overlap, aggregate severity, and emit the verdict. It spawns nothing.

### Act on the verdict

- **`PROCEED`** (no HIGH; at most two MEDIUM, none of them cross-domain) → continue to 3d. Any MEDIUM and LOW findings it carries are resolved at 3e with the critical review's.
- **`STOP AND RECONSIDER`** (any HIGH) or **`REVISE BEFORE PROCEEDING`** (3+ MEDIUM or cross-domain MEDIUM) → enter the bounded **fix-and-re-review loop** below (both supervised and autonomous; the cap protects either).

### Fix-and-re-review loop (bounded — max 3 iterations)

Each iteration:

1. **Record iteration state** in `progress.md` under `## Panel Review Iterations`: iteration number, HIGH/MEDIUM/LOW counts, verdict, timestamp.
2. **Spawn a fix subagent** (`agent-engineering:sdd-workhorse`):
   - **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, **BRIEF** with its approved revision and tier, **TIERS** when the spec carries `tier:`, the tracing gate as the line `tracing: on` or `tracing: off`, and **TRACING** when it is `on`.
   - **Outputs:** updated spec (in place), "Findings Addressed" appended to the panel review.
   - **Task:** Resolve every HIGH and MEDIUM finding; each resolution cites the specific spec change made. Do NOT claim resolution without an actual edit. Embed the **Brief and tier rules for spec fixes** (below) verbatim, and with `tracing: on` the **Call-graph rule for spec fixes** beneath them.
3. **Re-run Step 3c** (both stages — fresh PANEL-FINDINGS + a fresh synthesis) over the updated spec, producing a new/overwritten `PANEL-SPEC-*`.
4. **Act on the new verdict, in this order:**
   - **The panel now returns `PROCEED`** → exit the loop and continue to 3d — at any iteration, the third included. A passing verdict is never a halt.
   - **Progress-stall check** (verdict still STOP/REVISE): if HIGH did not strictly decrease (when HIGH was non-zero), OR (in REVISE case) MEDIUM did not strictly decrease → **halt immediately**. The fix subagent is making no real progress; further iterations waste tokens or degrade review quality (placating edits).
   - **Still STOP/REVISE and iteration < 3** → next iteration.
   - **Still STOP/REVISE after iteration 3** → halt (cap exhausted).

### Brief and tier rules for spec fixes (embed verbatim in the 3c and 3e fix prompts)

> **Stay inside the approved brief.** If a resolution departs from the design brief's Key decisions, Not doing list, or answered questions, add an entry to the spec's `## Deviations from Design Brief` — do not leave that section saying `None.`. Never reopen a question the user has answered.
>
> **Deferral is a resolution only for absent scope.** When the spec carries `tier:` and a finding says something is *missing* — an unspecified edge case, variation, or hardening — you may resolve it by adding a row to `## Deferred to Later Tiers` (next free `DEFER-XXX`, `Came from` = `review`) instead of specifying it, provided the tier standard's cut tests place it in a later tier and its floor does not protect it. If this tier can reach the deferred case, add the `FAIL-XXX` entry for its loud failure in the same edit. A finding about behaviour this tier *does* specify is a defect: fix it — it can never be deferred. A finding that says a deferral is unsafe, or that a part is built ahead for a later tier, is resolved by specifying the item or removing the part.

### Call-graph rule for spec fixes (embed verbatim in the 3c and 3e fix prompts when the gate is `tracing: on`)

> **Keep the planned call graph true to the spec.** A fix that adds, removes, renames, or moves an entry point, a call to a model, a call to an external system, or a delivery slice updates `### Planned call graph` and the slices' `Traced nodes:` lines in the same edit: every such call is a marked node, every LLM node states its maximum, and in per-slice mode every marked node is in exactly one slice's line. Marks follow the tracing standard at the path in your prompt. Never change the spec's `tracing:` field.

### On halt (cap exhausted or progress stall)

- Leave all artifacts in place — do not delete the spec or any panel review document.
- Append a final `### Panel Review Halt` entry to `progress.md`: total iteration count, final HIGH/MEDIUM/LOW counts, halt reason (`cap-exhausted` | `progress-stall`), and a next-action hint.
- Do NOT proceed to 3d/3e/3f. The spec has not been accepted.
- Emit (identical in both modes):

> **Flow halted at panel review.** Spec did not pass specialist review after [N] iteration(s). Halt reason: [cap-exhausted | progress-stall].
> Final verdict: [STOP AND RECONSIDER | REVISE BEFORE PROCEEDING]
> Unresolved HIGH findings: [count]
> Unresolved MEDIUM findings: [count]
> Latest panel review: `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`
> Iteration history: `SDD/orchestration/progress.md` → "Panel Review Iterations"
> The fix subagent could not resolve findings autonomously. Address the remaining HIGH/MEDIUM issues manually in the spec (they likely require design judgment), then run `/sdd-flow continue` to resume.

---

## 3d. Spec Critical Review Subagent

Run this review by the cycle's **review route** (`references/second-model-review.md`). On the Claude route, spawn an **`agent-engineering:sdd-critical-reviewer`** subagent (Opus). Either route is given:
- **Body:** `bodies/critical-review.md` — apply its **Planning Phase** section.
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`, **BRIEF** with its approved revision and tier, **TIERS** when the spec carries `tier:`, the tracing gate as the line `tracing: on` or `tracing: off`, and **TRACING** when it is `on`.
- **Outputs:** `SDD/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md`.
- **Task:** Adversarial review of the spec — the Design Brief Fidelity block (is the spec what the user approved?), ambiguities, untestable criteria, dropped research findings, contradictions, the feasibility-arithmetic gate over the spec's `### Quantitative Ledger` (do the spec's own numeric constraints permit its own numeric goals?), and the body's **Planned Call Graph** block (with `tracing: on`: is every entry point, LLM call, and external call the spec describes a marked node, and assigned to a slice? with `tracing: off`: is the spec free of one?). Complementary to the panel: critical-review is generalist/adversarial; the panel was domain-specialist.

---

## 3e. Address Spec Review Findings (panel + critical, combined)

Spawn an **`agent-engineering:sdd-workhorse`** fix subagent:
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`, `SDD/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, **BRIEF** with its approved revision and tier, **TIERS** when the spec carries `tier:`, the tracing gate as the line `tracing: on` or `tracing: off`, and **TRACING** when it is `on`.
- **Outputs:** updated SPEC, append `progress.md`.
- **Task:** Resolve ALL findings from BOTH reviews — clarify ambiguous requirements, make criteria testable, add missing edge cases or record them as deferred, resolve contradictions, address panel anti-patterns, incorporate dropped research findings. Append "Findings Addressed" sections to both review documents. Embed the **Brief and tier rules for spec fixes** (3c) verbatim, and with `tracing: on` the **Call-graph rule for spec fixes** (3c).

---

## 3f. Commit Planning Artifacts

The **orchestrator** runs the commit per `commands/commit.md` — no co-author attribution. Include the design brief, the tier plan, and every ADR change made since the research commit — the records written on approval at the design gate (2.5b) and those written in 3b, with the `SDD/adr/README.md` index and any superseded record edited along the way.

If `progress.md` exceeds ~500 lines, rotate it now (`phases/protocols.md` → Progress Rotation).

---

## 3g. Deviation Check and Transition

The spec was rewritten up to three times after the brief was approved (3a, the 3c loop, 3e). Before any code is written, check whether it is still what the user agreed to.

Read the spec's `## Deviations from Design Brief` with the same body contract the re-planning matcher uses (`phases/implementation-per-slice.md` → 4c.5): take the first non-empty line of the section's body.

- **`None.`** (case-insensitive, trailing period optional) → no pause; route to Step 4 below.
- **The section is absent or empty** → the spec is malformed: re-spawn the 3a completion subagent to add it (Error Handling's two-failure limit applies). Never read an absent section as "no deviations".
- **Anything else** → in **both supervised and autonomous modes**, append `## Awaiting Deviation Approval` (with the spec path) to `progress.md` and pause. The halt block is required: `Planning Phase - COMPLETE` was recorded in 3a, so without it `/sdd-flow continue` would route straight to Step 4.

  > **The spec departs from the brief you approved in [N] way(s):**
  > [each deviation: what the brief said → what the spec says — why]
  > Reply **y** to accept and start implementation, or **n** to halt and edit the spec.

  - **y** → append `## Design Deviations - ACCEPTED` to `progress.md` and route to Step 4.
  - **n** → halt with the block pending. `/sdd-flow continue` re-reads the section (the user may have edited the spec) and re-runs this check.

A spec written before the design gate shipped has no brief: if no `## Design Brief - ` line exists in `progress.md`, skip this check.

**Route to Step 4.** First append `## Planning - Accepted` to `progress.md` — one line, the spec path. It is the phase-detection marker that planning's reviews and this check are done: `Planning Phase - COMPLETE` alone does not say so, because the completion subagent writes it back in 3a. Then read the spec's `delivery_mode:`: `whole-feature` → `phases/implementation-whole-feature.md`; `per-slice` → `phases/implementation-per-slice.md`. There is no other planning checkpoint — the design gate covered the decision. The next stops are the slice-boundary pauses (per-slice mode) and the supervised checkpoint before the final implementation commit.
