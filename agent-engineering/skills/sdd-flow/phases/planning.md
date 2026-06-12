# Phase: Planning — Steps 3a–3g

Read at the Step 3 boundary. Phase-execution and fix subagents carry the Safety-Net Rule + a fresh counter file (`Reads: 0/15`) + the `planning-compact.md` compact body path. Body paths are `SKILL_ROOT/bodies/<file>.md`, resolved absolute.

---

## 3a. Planning Subagent

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/planning.md`
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/orchestration/progress.md`, existing `SDD/adr/` (to reference accepted ADRs), `SDD/UBIQUITOUS_LANGUAGE.md` (if present).
- **Outputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, append `progress.md`.
- **Task:** Read the research and create the full specification. The spec MUST include the YAML frontmatter fields — `review_panel` (default includes `module-depth`), `eval_required`, `cross_cutting_decisions`, `delivery_mode` — populated thoughtfully. The body's **per-slice authoring default** applies: set `delivery_mode: per-slice` unless the feature yields fewer than 2 genuine vertical slices, in which case `whole-feature` with a one-line justification in the spec. The spec MUST include the `## Modules` section with ≥1 `MODULE-XXX` entry (`Public Interface`, `Hides`, `Risk` low/medium/high, `Spec refs`) — prefer deep modules. Use canonical names from the glossary when present. The body's `delivery_mode` value-validation (enum fail-fast) and slice-practicality gate stay in force.

Then spawn a second **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/planning-complete.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/UBIQUITOUS_LANGUAGE.md` (if present).
- **Outputs:** updated SPEC (if gaps found), updated `SDD/UBIQUITOUS_LANGUAGE.md` (incremental — only if the spec introduced new domain terms), append `progress.md`.
- **Task:** Validate completeness against the checklist (including the Modules-section verification), ensure all research findings are incorporated, verify frontmatter fields are populated, and capture any glossary deltas the spec introduced (execute inline).

---

## 3b. ADR Capture from Spec Frontmatter

Read the spec's `cross_cutting_decisions:` frontmatter. If non-empty, for each topic label spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/adr-capture.md` — **AUTO mode** (frontmatter-declared decisions are pre-approved; no user confirmation).
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, existing `SDD/adr/`.
- **Outputs:** new `SDD/adr/NNNN-slug.md`, updated `SDD/adr/README.md`, append `progress.md`.
- **Task:** Extract the decision, alternatives, rationale, and consequences for the topic from spec+research. If context is insufficient, emit a warning and skip the topic rather than fabricating rationale. Apply the scope test, then write the ADR.

If `cross_cutting_decisions:` is empty/absent, skip this step.

---

## 3c. Specialist Panel Review — two stages

Panel composition comes from the spec's `review_panel:` frontmatter. If absent or empty, apply the **default panel**: `security`, `performance`, `data-modeling`, `api-contract`, `module-depth` — plus `slice-integrity` when the spec declares `delivery_mode: per-slice`. (Other available values: `reliability`, `accessibility`, `cost`, `privacy`.)

### Stage 1 — specialists in parallel

Spawn **one subagent per `review_panel:` value, IN PARALLEL** (single message, multiple spawns). Each uses its matching shipped agent type `agent-engineering:sdd-spec-<panel-value>-specialist`:
- **Body:** `bodies/panel-specialist.md` ("apply ONLY the Section your panel value names").
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, the panel value, and the resolved PANEL-FINDINGS output path.
- **Output:** `SDD/reviews/PANEL-FINDINGS-[panel-value]-[feature-name]-[YYYYMMDD].md`.
- Each specialist writes exactly one findings file and spawns nothing. (The `slice-integrity` specialist short-circuits unless `delivery_mode: per-slice`.)

### Stage 2 — synthesis

After all Stage 1 specialists return, spawn ONE **`agent-engineering:sdd-critical-reviewer`** subagent (Opus — the synthesis is the adversarial work):
- **Body:** `bodies/panel-synthesis.md`
- **Inputs:** the exact list of `SDD/reviews/PANEL-FINDINGS-*-[feature-name]-[YYYYMMDD].md` paths written in Stage 1, plus the spec path. (Its counter trigger may be raised to N+5 for an N-specialist panel.)
- **Output:** `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`.
- **Task:** Read each PANEL-FINDINGS file from disk, dedupe cross-specialist overlap, aggregate severity, and emit the verdict. It spawns nothing.

### Act on the verdict

- **`PROCEED`** → continue to 3d.
- **`STOP AND RECONSIDER`** (any HIGH) or **`REVISE BEFORE PROCEEDING`** (3+ MEDIUM or cross-domain MEDIUM) → enter the bounded **fix-and-re-review loop** below (both supervised and autonomous; the cap protects either).

### Fix-and-re-review loop (bounded — max 3 iterations)

Each iteration:

1. **Record iteration state** in `progress.md` under `## Panel Review Iterations`: iteration number, HIGH/MEDIUM/LOW counts, verdict, timestamp.
2. **Spawn a fix subagent** (`agent-engineering:sdd-workhorse`):
   - **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`.
   - **Outputs:** updated spec (in place), "Findings Addressed" appended to the panel review.
   - **Task:** Resolve every HIGH and MEDIUM finding; each resolution cites the specific spec change made. Do NOT claim resolution without an actual edit.
3. **Re-run Step 3c** (both stages — fresh PANEL-FINDINGS + a fresh synthesis) over the updated spec, producing a new/overwritten `PANEL-SPEC-*`.
4. **Compare finding counts to the previous iteration:**
   - **Progress-stall check:** if HIGH did not strictly decrease (when HIGH was non-zero), OR (in REVISE case) MEDIUM did not strictly decrease → **halt immediately**. The fix subagent is making no real progress; further iterations waste tokens or degrade review quality (placating edits).
   - **If the panel now returns `PROCEED`** → exit loop; continue to 3d.
   - **If still STOP/REVISE and iteration < 3** → next iteration.
5. **After iteration 3, regardless of verdict** → halt (cap exhausted).

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

Spawn an **`agent-engineering:sdd-critical-reviewer`** subagent (Opus):
- **Body:** `bodies/critical-review.md` — apply its **Planning Phase** section.
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`.
- **Outputs:** `SDD/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md`.
- **Task:** Adversarial review of the spec — ambiguities, untestable criteria, dropped research findings, contradictions. Complementary to the panel: critical-review is generalist/adversarial; the panel was domain-specialist.

---

## 3e. Address Spec Review Findings (panel + critical, combined)

Spawn an **`agent-engineering:sdd-workhorse`** fix subagent:
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`, `SDD/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`.
- **Outputs:** updated SPEC, append `progress.md`.
- **Task:** Resolve ALL findings from BOTH reviews — clarify ambiguous requirements, make criteria testable, add missing edge cases, resolve contradictions, address panel anti-patterns, incorporate dropped research findings. Append "Findings Addressed" sections to both review documents.

---

## 3f. Commit Planning Artifacts

The **orchestrator** runs the commit per `commands/commit.md` — no co-author attribution. Include any ADRs written in 3b.

If `progress.md` exceeds ~500 lines, rotate it now (`phases/protocols.md` → Progress Rotation).

---

## 3g. Transition

Proceed directly to **Step 4** (no checkpoint here — the research checkpoint covered the most critical decision point, and the second supervised checkpoint comes before the final implementation commit). Read the spec's `delivery_mode:` and route: `whole-feature` → `phases/implementation-whole-feature.md`; `per-slice` → `phases/implementation-per-slice.md`.
