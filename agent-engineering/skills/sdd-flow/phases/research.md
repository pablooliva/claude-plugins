# Phase: Research — Steps 2a–2e

Read at the Step 2 boundary. All spawns follow the SKILL's spawn-prompt checklist; phase-execution and fix subagents carry the Safety-Net Rule + a fresh counter file (`Reads: 0/15`) + the `research-compact.md` compact body path. Body paths below are `SKILL_ROOT/bodies/<file>.md`, resolved absolute.

---

## 2a. Research Subagent

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/research.md` ("Read this file FIRST — it is your complete instruction set.")
- **Inputs:** task description, codebase access, `SDD/research/CLARIFICATION-[###]-[feature-name].md` (if present), `SDD/UBIQUITOUS_LANGUAGE.md` (if present — load before any research writing for vocabulary alignment).
- **Outputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, append `progress.md`.
- **Task:** Create the research document and perform the full systematic investigation. If a CLARIFICATION artifact exists, treat its branches and open questions as required research targets — every branch addressed; every open question resolved or explicitly deferred with rationale.
- **Next-tier cycle** (the flow was started with `--next-tier`; `phases/setup.md` Step 0): add to the inputs the previous tier's research document and **TIER_PLAN**, and state in the prompt `NEXT-TIER CYCLE: Tier N`. The body's next-tier branch makes this a delta investigation — the deferred items this tier takes up, the feedback, and what the shipped code changed — not a second full pass.

Then spawn a second **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/research-complete.md`
- **Inputs:** the RESEARCH document at its exact path, `SDD/UBIQUITOUS_LANGUAGE.md` (if present, for incremental update). On a next-tier cycle, also the previous tier's research document, **TIER_PLAN**, and the `NEXT-TIER CYCLE: Tier N` line, so the completeness check is scoped to the delta.
- **Outputs:** updated RESEARCH document (if gaps found), updated/created `SDD/UBIQUITOUS_LANGUAGE.md` (incremental — preserve stable terms, do not regenerate), append `progress.md`.
- **Task:** Validate completeness against the checklist, fill remaining gaps, and propose+apply incremental glossary updates for terms introduced or refined during research (execute the glossary brief inline).

---

## 2b. ADR Capture from Research

After research is complete, capture cross-cutting architectural decisions expressed as comparison-with-selection patterns.

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/adr-capture.md` — run in **PROPOSE mode** when supervised, **AUTO mode** when autonomous. State the mode in the prompt.
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, existing `SDD/adr/` (if present).
- **Outputs:** PROPOSE — one `## ADR Candidates` entry appended to `progress.md`, and nothing else. AUTO — zero or more `SDD/adr/NNNN-slug.md`, updated `SDD/adr/README.md`, append `progress.md`.
- **Task:** Scan research for cross-cutting decisions with explicit comparison+selection and apply the scope test to each. In PROPOSE mode the subagent writes no ADR and no stop note: it appends one `## ADR Candidates` entry (title and chosen option per candidate, or `none`) and returns. In AUTO mode it writes every ADR that passes the scope test.

**There is no confirmation stop here.** In supervised mode the candidates are shown at the design gate (`phases/planning.md` → 2.5b), where `approve` accepts them and a reply may drop any by title; the accepted ones are written right after approval, before 3a. In autonomous mode the ADRs are already written, and the gate shows which.

If no cross-cutting decisions are detected, AUTO mode writes nothing and PROPOSE mode appends the entry with `none` — either way, continue to 2c.

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

**Then append `## Research - Accepted` to `progress.md`** — one line, the research document's path. It is the phase-detection marker that research is done: review, fixes, and commit included. The orchestrator writes it, here and nowhere earlier; the note the completion subagent leaves in 2a ("Research phase complete…") is not a marker and nothing matches it.

If `progress.md` exceeds ~500 lines, rotate it now (`phases/protocols.md` → Progress Rotation) — a phase-boundary commit is a quiet point.

---

## After 2e

There is no pause here in either mode. The stop that follows research is the **design gate** — Step 2.5, in `phases/planning.md` — where the user sees what will be built, not only what was found. Proceed directly to Step 2.5 → read `phases/planning.md`.
