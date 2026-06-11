# Phase: Research — Steps 2a–2f

Read at the Step 2 boundary. All spawns follow the SKILL's spawn-prompt checklist; phase-execution and fix subagents carry the Safety-Net Rule + a fresh counter file (`Reads: 0/15`) + the `research-compact.md` compact body path. Body paths below are `SKILL_ROOT/bodies/<file>.md`, resolved absolute.

---

## 2a. Research Subagent

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/research.md` ("Read this file FIRST — it is your complete instruction set.")
- **Inputs:** task description, codebase access, `SDD/research/CLARIFICATION-[###]-[feature-name].md` (if present), `SDD/UBIQUITOUS_LANGUAGE.md` (if present — load before any research writing for vocabulary alignment).
- **Outputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, append `progress.md`.
- **Task:** Create the research document and perform the full systematic investigation. If a CLARIFICATION artifact exists, treat its branches and open questions as required research targets — every branch addressed; every open question resolved or explicitly deferred with rationale.

Then spawn a second **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/research-complete.md`
- **Inputs:** the RESEARCH document at its exact path, `SDD/UBIQUITOUS_LANGUAGE.md` (if present, for incremental update).
- **Outputs:** updated RESEARCH document (if gaps found), updated/created `SDD/UBIQUITOUS_LANGUAGE.md` (incremental — preserve stable terms, do not regenerate), append `progress.md`.
- **Task:** Validate completeness against the checklist, fill remaining gaps, and propose+apply incremental glossary updates for terms introduced or refined during research (execute the glossary brief inline).

---

## 2b. ADR Capture from Research

After research is complete, capture cross-cutting architectural decisions expressed as comparison-with-selection patterns.

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/adr-capture.md` — run in **CONFIRM mode** when supervised (ambient detection), **AUTO mode** when autonomous.
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, existing `SDD/adr/` (if present).
- **Outputs:** zero or more `SDD/adr/NNNN-slug.md`, updated `SDD/adr/README.md`, append `progress.md`.
- **Task:** Scan research for cross-cutting decisions with explicit comparison+selection. For each match, apply the scope test and render an ADR. In CONFIRM mode the subagent appends an `## Awaiting ADR Confirmation` block to `progress.md` and returns without writing (the orchestrator surfaces it to the user); in AUTO mode it writes every ADR that passes the scope test.

If no cross-cutting decisions are detected this is a no-op — skip to 2c without writing anything.

---

## 2c. Research Critical Review Subagent

Spawn an **`agent-engineering:sdd-critical-reviewer`** subagent (Opus by frontmatter):
- **Body:** `bodies/critical-review.md` — apply its **Research Phase** section.
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/research/CLARIFICATION-[###]-[feature-name].md` (if present, for the Design Concept Fidelity check), `SDD/UBIQUITOUS_LANGUAGE.md` (if present, for vocabulary-alignment).
- **Outputs:** `SDD/reviews/CRITICAL-RESEARCH-[feature-name]-[YYYYMMDD].md`.
- **Task:** Adversarial review of the research document. Apply the Design Concept Fidelity block first — verify every CLARIFICATION branch is addressed and every open question resolved or explicitly deferred. If no CLARIFICATION exists (gate skipped), record the gate-skip note in the executive summary.

---

## 2d. Address Research Review Findings

Spawn an **`agent-engineering:sdd-workhorse`** subagent (fix subagent — no body file; brief inline):
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md` AND `SDD/reviews/CRITICAL-RESEARCH-[feature-name]-[YYYYMMDD].md`.
- **Outputs:** updated RESEARCH document, append `progress.md`.
- **Task:** Resolve ALL findings — HIGH, MEDIUM, and LOW. Fill gaps, strengthen weak evidence, add missing perspectives, address questionable assumptions; no finding left unresolved. After fixing, append a "Findings Addressed" section to the review document noting how each was resolved.

---

## 2e. Commit Research Artifacts

The **orchestrator** runs the commit directly (not a subagent), per `commands/commit.md` conventions — **no co-author attribution**. Include any ADRs written in 2b.

---

## 2f. Supervised Checkpoint (supervised mode only)

In **supervised mode**, pause:

> **Research phase complete.** Here's what was found:
> [Brief summary of key findings and critical-review results]
> Research document: `SDD/research/RESEARCH-[###]-[feature-name].md`
> Critical review: `SDD/reviews/CRITICAL-RESEARCH-[feature-name]-[YYYYMMDD].md`
> ADRs captured: [list of ADR numbers, or "none"]
> **Proceed to planning?** (y/n)

Wait for confirmation before Step 3. In **autonomous mode**, proceed directly to Step 3 → read `phases/planning.md`.
