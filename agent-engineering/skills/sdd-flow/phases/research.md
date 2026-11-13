# Phase: Research — Steps 2a, 2b, 2e

Read at the Step 2 boundary. All spawns follow the SKILL's spawn-prompt checklist; phase-execution and fix subagents carry the Safety-Net Rule + a fresh counter file (`Reads: 0/15`) + the `research-compact.md` compact body path. Body paths below are `SKILL_ROOT/bodies/<file>.md`, resolved absolute. Research has no review step: the owner judges the design built on it at the design gate (2.5).

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

## 2b. ADR Candidates from Research

After research is complete, find the cross-cutting architectural decisions it expresses as comparison-with-selection patterns. Nothing is written here: the candidates go to the design gate.

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/adr-capture.md` — run in **PROPOSE mode**. State the mode in the prompt.
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, existing `SDD/adr/` (if present).
- **Outputs:** one `## ADR Candidates` entry appended to `progress.md`, and nothing else.
- **Task:** Scan research for cross-cutting decisions with explicit comparison+selection and apply the scope test to each. The subagent writes no ADR and no stop note: it appends one `## ADR Candidates` entry (title and chosen option per candidate, or `none`) and returns.

**There is no confirmation stop here, and no record is written here.** The candidates are shown at the design gate (`phases/planning.md` → 2.5b), which always stops: `approve` accepts them and a reply may drop any by title; the accepted ones are written right after approval, before 3a. A decision record is never written, or committed, before the design it belongs to is approved.

If no cross-cutting decisions are detected, the entry is appended with `none`. Continue to 2e.

---

## 2e. Commit Research Artifacts

The **orchestrator** runs the commit directly (not a subagent), per `commands/commit.md` conventions — **no co-author attribution**. No decision record exists yet — 2b only lists candidates; the accepted ones are committed at 3f.

**Then append `## Research - Accepted` to `progress.md`** — one line, the research document's path. It is the phase-detection marker that research is done, its commit included. The orchestrator writes it, here and nowhere earlier; the note the completion subagent leaves in 2a ("Research phase complete…") is not a marker and nothing matches it.

If `progress.md` exceeds ~500 lines, rotate it now (`phases/rare/rotation.md`) — a phase-boundary commit is a quiet point.

---

## After 2e

There is no pause here in either mode. The stop that follows research is the **design gate** — Step 2.5, in `phases/planning.md` — where the user sees what will be built, not only what was found. Proceed directly to Step 2.5 → read `phases/planning.md`.
