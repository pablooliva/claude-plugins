# SDD Ubiquitous Language

Canonical project-wide vocabulary for the SDD plugin and the `sdd-flow` skill. Terms here are case-sensitive; downstream subagents and command authors MUST use the canonical name to keep specs, plans, retrospectives, and ledgers internally consistent.

**Source of authority:** Each entry cites a `proposal §<section>` (from `proposals/vertical-slicing-decomposition.md`) or `research §<heading>` (from `SDD/research/RESEARCH-001-vertical-slicing-step-c.md`). When the proposal and the research differ in nuance, the proposal wins for design intent and the research wins for `file:line` mechanics.

**Scope rule (when to add a term here):** an entry belongs in this glossary only if it is (a) introduced or refined by an SDD feature, (b) appears repeatedly across multiple commands or skills, AND (c) has plausible synonyms that would fragment the design concept. Per-feature jargon stays in the feature's spec.

---

## Delivery model

### `delivery_mode`
Spec frontmatter field that gates per-slice behavior. Values: `whole-feature` (default; existing horizontal flow) or `per-slice` (opt-in vertical-slice flow). Authored at the spec frontmatter level; read by `/planning-start`, `/implementation-start`, `/critical-review`, `/spec-review-panel`, the `/slice-*` commands, and the `sdd-flow` skill at the planning → implementation boundary.
- Synonyms to avoid: "delivery style", "delivery type", "slicing mode", "implementation mode", "decomposition mode".
- Source: proposal §Distribution Strategy; research §Flow 1.

### whole-feature mode
The default delivery mode. Implementation proceeds as one tracked pass over the flat REQ list; existing horizontal chunking applies. Behavior is preserved bit-for-bit modulo the directory restructure and `PROMPT → IMPLEMENTATION-PLAN` rename.
- Synonyms to avoid: "monolithic mode", "horizontal mode", "default mode" (use the canonical name even when default).
- Source: proposal §Distribution Strategy.

### per-slice mode
The opt-in delivery mode. Implementation proceeds one vertical slice at a time, end-to-end through every module the slice touches, with mandatory per-slice code review, retrospective, and per-slice commit. Activates the practicality gate, slice-integrity review checks, slice-boundary checkpoint axis, and the `/slice-*` command surface.
- Synonyms to avoid: "vertical mode", "slicing mode", "sliced mode".
- Source: proposal §Distribution Strategy.

### vertical thread / vertical slice
A concentrated function with a thread line through every relevant layer of the application. The defining property is the vertical traversal (e.g., UI → API → DB; or scheduler → worker → external API → state store), not user-facing audience. A slice that touches only one module when the feature spans multiple is a slice-integrity smell.
- Canonical short form: **slice**. Use **vertical slice** when contrasting with horizontal layering.
- Synonyms to avoid: "feature slice", "story slice", "thread", "increment".
- Source: proposal §What "slice" means here.

### horizontal layer
The pre-existing pattern (REQs implemented layer-by-layer or module-by-module without end-to-end completion) that vertical slicing replaces in per-slice mode. Used in slice-integrity findings to name the anti-pattern (a "layer-in-disguise slice").
- Synonyms to avoid: "stripe", "row", "tier-pass".
- Source: proposal §Problem.

### concentrated function
The single user-meaningful or system-meaningful capability that defines one slice. Cited in the `Concentrated function` field of each `SLICE-XXX` entry. A slice's concentrated function is what the slice's acceptance check exercises end-to-end.
- Synonyms to avoid: "core function", "primary capability", "slice goal".
- Source: proposal §1.

---

## Slice mechanics

### slice cycle
The sequence Implement → Per-slice code review → Address findings → Slice retrospective → Per-slice commit → (optional) slice-boundary pause. Runs once per `SLICE-XXX` entry in per-slice mode. Distinct from the **end-of-feature cycle**, which runs once after the last slice lands and covers critical review + completion + eval scaffolding + end-of-feature commit.
- Synonyms to avoid: "slice loop", "slice iteration", "slice round".
- Source: proposal §6 "Per-slice cycle".

### end-of-feature cycle
The sequence Critical review → Address findings → Completion subagent → Eval scaffolding (conditional) → Supervised end-of-implementation checkpoint → End-of-feature commit → Announcement. Runs once after all slices land. In per-slice mode, the end-of-feature commit covers ONLY whole-feature artifacts (per-slice code is already committed in each slice cycle's commit step).
- Synonyms to avoid: "feature wrap-up", "final cycle", "closeout cycle".
- Source: proposal §6 "End-of-feature cycle".

### acceptance check
The single, focused, automated-or-manual test that proves a slice works end-to-end. Each `SLICE-XXX` entry cites one. The slice does not advance to per-slice code review until its acceptance check passes.
- Synonyms to avoid: "slice test", "slice gate", "acceptance criterion" (singular plural confusion — use **acceptance check**).
- Source: proposal §1.

### sequence rationale
The `Sequence rationale` field of a `SLICE-XXX` entry explaining why this slice comes at this position. SLICE-001's rationale should justify "thinnest possible end-to-end happy path"; later slices add depth and edges.
- Synonyms to avoid: "ordering rationale", "slice ordering".
- Source: proposal §1.

### thinnest possible end-to-end happy path
The design constraint on SLICE-001. Its job is to prove the vertical thread exists, not to cover edges or fail modes. Edge / fail-mode coverage defers to later slices.
- Synonyms to avoid: "MVP slice", "smallest slice".
- Source: proposal §1.

---

## Per-slice artifacts

### IMPLEMENTATION-PLAN
The per-feature implementation plan/tracking document. Renamed from `PROMPT` as part of the SDD 2.0.0 directory restructure. Filename pattern: `IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`. Lives at `SDD/implementation/`. Holds the `## Slice Progress` table in per-slice mode.
- Synonyms to avoid: "PROMPT" (deprecated; only acceptable in changelog/migration prose), "tracker doc", "plan doc", "implementation tracker" (use the canonical name).
- Source: proposal §Directory Layout "File rename"; research §Branch 1.

### `## Slice Progress`
The table inside an `IMPLEMENTATION-PLAN` (per-slice mode only) that tracks each slice's status. **Binding column schema:** `SLICE-ID | Name | Status | Acceptance check | Test result | Notes`. **Binding 4-state enum** for the `Status` column: `Not Started`, `In Progress`, `Acceptance Check Passing`, `Complete`. State transitions are forward-only (no backwards transitions encoded in the column; "stuck" surfaces via the ledger's `Open recommendations` section). The active slice is the next entry with status `Not Started` (or `In Progress`, if resuming mid-slice). Column-write authority: `/implementation-start` scaffolds the table; `/slice-retro` updates only `Status`, `Test result`, and `Notes` (never `SLICE-ID`, `Name`, or `Acceptance check` — those are SPEC-derived).
- Synonyms to avoid: "slice tracker", "slice status", "slice table".
- Source: proposal §2; research §Branch 3 / §"## Slice Progress table schema"; SPEC-001 REQ-022 / EDGE-011.

### IMPLEMENTATION-SUMMARY
The whole-feature completion artifact. Filename unchanged across the 2.0.0 restructure (relocation only). Filename pattern: `IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md`. Lives at `SDD/implementation/summaries/` (relocated from `SDD/prompts/implementation-complete/`).
- Synonyms to avoid: "completion doc", "summary doc".
- Source: research §Q-A resolution.

### slice retrospective (`RETROSPECTIVE-SLICE-XXX-...`)
The per-slice audit-trail artifact written by `/slice-retro` (or by Step 4c.5 of the orchestrator). Filename: `RETROSPECTIVE-SLICE-XXX-[feature-name]-[YYYY-MM-DD].md`. Lives at `SDD/implementation/slices/`. Audit trail; never modified after writing. The `XXX` is the slice number, not the feature number; `[feature-name]` is the kebab-case slug.
- Synonyms to avoid: "slice retro file", "slice postmortem".
- Source: proposal §6 "Slice retrospective"; research §Q-B resolution.

### learnings ledger (`LEARNINGS-FEATURE-XXX.md`)
The single rolling ledger file per feature. One per feature; lifetime equals the duration of the implementation phase. Updated **in place** by every retro (consolidate, refine, supersede — do NOT just append). Subsequent slice subagents receive ONLY the ledger in their prompts (per-slice mode propagation channel). Lives at `SDD/implementation/slices/LEARNINGS-FEATURE-[###].md`. The `XXX` here is the FEATURE number (not the slice number).
- Canonical short form: **the ledger**.
- Synonyms to avoid: "learnings doc", "rolling notes", "slice memory", "feature notes".
- Source: proposal §6 "Rolling learnings ledger".

### Recommended SPEC Amendments
A structured section inside a slice retrospective. Each entry cites which `SLICE-XXX` / `MODULE-XXX` / `REQ-XXX` / `EDGE-XXX` / `FAIL-XXX` is affected, what the SPEC currently says, what should change with proposed wording, and why grounded in observation. Surfaced in the slice-boundary pause as a per-recommendation summary; full proposed wording stays in the retrospective artifact.
- Synonyms to avoid: "spec changes", "amendment list", "proposed edits".
- Source: proposal §6 "Slice retrospective" / "Spec-amendment recommendation".

### Recommended Re-planning
An elevated-severity structured section inside a slice retrospective. Reserved for genuine plan-level failures (original module decomposition is wrong, or an assumption underlying multiple upcoming slices is falsified). Halts the flow even under `--skip-slice-checkpoints` (mirrors the panel-review halt at Step 3c).
- Synonyms to avoid: "re-plan", "plan reset", "plan invalidation".
- Source: proposal §6 "Re-planning recommendation".

### Open recommendations awaiting user decision
A structured section inside `LEARNINGS-FEATURE-XXX.md`. Accumulates spec-amendment and re-planning recommendations the user has not yet acted on. Especially relevant under `--skip-slice-checkpoints`, where there is no per-slice pause for the user to triage at; surfaced as a single consolidated block in the Step 4j announcement.
- Synonyms to avoid: "pending recommendations", "user decisions queue".
- Source: proposal §6 "Rolling learnings ledger".

### slice review (`REVIEW-SLICE-XXX-...`)
The per-slice code review output of `/slice-review`. Filename: `REVIEW-SLICE-XXX-[feature-name]-[YYYYMMDD].md`. Lives at `SDD/reviews/` (parent unchanged from existing `REVIEW-XXX-...md`; only the filename pattern is SLICE-aware to reflect scope). `/slice-review` is a thin wrapper over `/code-review` scoped to the slice's file set.
- Synonyms to avoid: "slice code review", "scoped review".
- Source: research §Branch 3 / Q-Open5 conservative default.

---

## Workflow gates

### practicality gate
The Step 6 gate inside `/planning-start` that fires only when `delivery_mode: per-slice`. The planning subagent assesses whether the feature decomposes meaningfully into slices. If it doesn't, the subagent must (a) document `Slicing not applicable: <reason>` in `## Delivery Slices` and (b) surface to the user via an `## Awaiting Slicing Decision` block in `progress.md` (autonomous halt analogous to Step 1.5's clarification gate). User options: fall back to `whole-feature` or retry slice extraction with a hint.
- Synonyms to avoid: "sliceability check", "slicing gate", "slice viability check".
- Source: proposal §5; research §Flow 1.

### slice-integrity check
The review check that fires only when `delivery_mode: per-slice` and verifies slices are genuine vertical threads (not horizontal layers in disguise). Inserted in both `/critical-review` (Planning Phase Critical Review section) and `/spec-review-panel` (new specialist 4.7). Detects layer-in-disguise slices, single-module slices without justification, non-thin SLICE-001, orphan REQs, bare acceptance checks, missing sequence rationale, and skipped practicality gate.
- Synonyms to avoid: "slice review" (collides with `/slice-review` artifact), "slice quality check", "slice audit".
- Source: proposal §4; research §Branch 5.

### slice-boundary checkpoint
A pause point in the per-slice cycle, after a slice's full Implement → Review → Fix → Retrospective → Commit cycle has completed. Independent of the existing **phase-boundary checkpoint** (research-end / impl-end). Default in per-slice mode: `on` (in both supervised and autonomous). Suppressed by `--skip-slice-checkpoints`.
- Synonyms to avoid: "slice pause", "inter-slice checkpoint", "between-slices gate".
- Source: proposal §6 "Checkpoint cadence in per-slice mode".

### phase-boundary checkpoint
The existing pause axis for `supervised` vs `autonomous` modes — pauses at research-end (Step 2f) and implementation-end (Step 4h). Orthogonal to **slice-boundary checkpoint** (the two axes form a 2x2 cross-product matrix in per-slice mode).
- Synonyms to avoid: "phase pause", "supervised checkpoint" (the term covers both supervised and autonomous shapes).
- Source: proposal §6 "Checkpoint cadence".

### per-slice review iteration cap
The bound on the 4b → 4c → re-run-4b loop. Max 3 iterations with a progress-stall check (HIGH must strictly decrease; or MEDIUM when HIGH is zero). Mirrors Step 3c's panel-review cap. On halt, findings route to the ledger's `Open recommendations` section; in `--skip-slice-checkpoints` mode the entire flow halts.
- Synonyms to avoid: "review loop cap", "review iteration limit".
- Source: proposal §6 "Per-slice review iteration cap".

### `## Awaiting Slicing Decision`
The `progress.md` block emitted when the practicality gate halts the flow (autonomous mode). Mirrors `## Awaiting Clarification` in shape. Resumed via `/sdd-flow continue --fall-back-to-whole-feature` or `/sdd-flow continue --retry-slicing "<hint>"`.
- Synonyms to avoid: "awaiting slice", "awaiting practicality decision".
- Source: research §Open Question 1 conservative default; proposal §5.

---

## Filenames & paths

### `SDD/implementation/`
Top-level directory introduced by SDD 2.0.0. Holds artifacts about *what gets built* — `IMPLEMENTATION-PLAN`, `summaries/IMPLEMENTATION-SUMMARY-...`, `slices/RETROSPECTIVE-SLICE-...`, `slices/LEARNINGS-FEATURE-...`, and (relocated) `test-audits/`. Replaces the relocated portion of the legacy `SDD/prompts/`.
- Synonyms to avoid: "build artifacts dir", "impl dir".
- Source: proposal §Directory Layout.

### `SDD/orchestration/`
Top-level directory introduced by SDD 2.0.0. Holds runtime state of the flow itself — `progress.md`, `subagent-calls/`, `counters/`, and `compacted/`. Replaces `SDD/prompts/context-management/` plus the loose compaction files at the parent level.
- Synonyms to avoid: "flow state dir", "context-management dir" (deprecated).
- Source: proposal §Directory Layout.

### `SDD/implementation/slices/`
The per-feature subdirectory holding per-slice retrospectives and the rolling learnings ledger. Per-slice mode only.
- Synonyms to avoid: "slice artifacts dir".
- Source: proposal §Directory Layout.

### `SDD/orchestration/compacted/`
The subdirectory holding compaction snapshots: `{research,planning,implementation}-compacted-*.md` and adhoc `compact-*.md`. Replaces the loose-files-at-parent layout in `SDD/prompts/context-management/`.
- Synonyms to avoid: "compaction dir", "snapshots dir".
- Source: proposal §Directory Layout.

---

## Frontmatter fields

### `delivery_mode:` (frontmatter)
See **Delivery model → `delivery_mode`**. The frontmatter syntax is the entry point; the runtime semantics live there.

### `review_panel:` (frontmatter)
Existing field that toggles `/spec-review-panel`. Unchanged by this feature except that the new specialist 4.7 (Slice Integrity) gates on `delivery_mode`, not on `review_panel`. If `review_panel: true` AND `delivery_mode: per-slice`, the slice-integrity specialist fires; if either is missing, it does not.
- Source: research §Branch 5.

### `eval_required:` (frontmatter)
Existing field that gates Step 4g eval scaffolding. Unchanged by this feature.
- Source: research §Flow 1 (mention).

### `cross_cutting_decisions:` (frontmatter)
Existing field that gates ADR capture in research/planning. Unchanged by this feature.

---

## Modes & flags

### `--skip-slice-checkpoints`
Argument to `/sdd-flow` (per-slice mode only). Mirrors the existing `--skip-clarify` precedent: suppresses the per-slice pause between slice cycles; accumulates `Open recommendations` in the ledger; consolidated surface in the 4j announcement. In autonomous mode + `--skip-slice-checkpoints`, a `## Recommended Re-planning` retrospective still halts the flow.
- Synonyms to avoid: "no-slice-pause", "skip-slice-pause".
- Source: proposal §6 "Checkpoint cadence" / "Per-slice review iteration cap".

### `--replan`
Argument to `/sdd-flow continue` (per-slice mode only). Triggered after a slice retrospective emitted `## Recommended Re-planning`. Re-runs Step 3 with the ledger and triggering retrospective in scope; produces a revised SPEC; resumes implementation from `SLICE-001` (default) or from `--from-slice SLICE-XXX`.
- Synonyms to avoid: "re-plan", "redo-planning".
- Source: proposal §6 "Re-planning recommendation"; research §Q-D resolution.

### `--from-slice SLICE-XXX`
Optional argument to `/sdd-flow continue --replan`. Resumes implementation from a user-specified slice rather than `SLICE-001`. The orchestrator never auto-determines validity of completed slices; the user vouches.
- Source: research §Q-D resolution.

### `--override-replan`
Argument to `/sdd-flow continue` (per-slice mode only). Explicit override that continues with the current plan despite a `## Recommended Re-planning` recommendation. Documented but discouraged.
- Source: proposal §6 "Re-planning recommendation".

### `--fall-back-to-whole-feature`
Argument to `/sdd-flow continue`. Used to resume from the practicality gate's `## Awaiting Slicing Decision` block by accepting that the feature ships in `whole-feature` mode for this run only. Does NOT modify the spec frontmatter (the user does that explicitly if they want the change to persist beyond this run).
- Synonyms to avoid: "fallback-mode", "force-whole-feature".
- Source: research §Open Question 1 conservative default.

### `--retry-slicing "<hint>"`
Argument to `/sdd-flow continue`. Used to resume from the practicality gate by asking the planning subagent to retry slice extraction with the user's hint about a slice boundary the subagent missed.
- Synonyms to avoid: "retry-slice", "redo-slicing".
- Source: research §Open Question 1 conservative default.

---

## Glossary discipline

- **Add a term** when this feature or a future feature introduces project-wide vocabulary that satisfies all three scope-rule conditions above. Per-feature jargon belongs in the feature's spec.
- **Refine a term** in place when a later feature changes its meaning. Update the source citation. Do NOT delete superseded terms silently — strike through with `~~old definition~~` and add the new one with a note.
- **Retire a term** by moving it to a `## Retired terms` section at the bottom (added when first needed) with a one-line note on what replaced it.
- **Cross-cutting decisions** (technology choices, conventions binding multiple features) belong in `SDD/adr/`, not here. The glossary names things; ADRs decide things.
