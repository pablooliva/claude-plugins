# Initialize Planning/Specification Phase

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow’s flat-orchestration contract forbids it; all work happens inline in your own context.

SPECIFICATION PHASE INITIALIZATION

Starting planning phase based on completed research.

## Initial Context Load

1. **Read Progress File:**
   - Load `SDD/orchestration/progress.md` to understand research completion status
   - Identify the research document referenced
   - Note any important context from the research phase

2. **Read Ubiquitous Language Glossary:**
   - If `SDD/UBIQUITOUS_LANGUAGE.md` exists, load it. This is the project-wide glossary of domain terms — use these names exactly when writing the spec, in preference to any synonyms or near-synonyms. Aligning vocabulary with the glossary is non-negotiable; if the spec needs a term not in the glossary, propose it as an addition (captured during the planning-complete phase's glossary-delta step).
   - If the glossary does not exist, proceed without it.

3. **Update Progress for Planning Phase:**
   - Add a new planning section to `SDD/orchestration/progress.md`
   - IMPORTANT: Preserve all research phase information - do NOT delete or reset it
   - Add reference to the SPEC document being created
   - Document the transition from research to planning phase

## Specification Setup

1. Create `SDD/requirements/SPEC-[###]-[feature-name].md` document where:
   - `[###]` matches the research document number (e.g., if using RESEARCH-042, create SPEC-042)
   - `[feature-name]` is a kebab-case description matching the research document (e.g., "user-authentication", "csv-export")
   - Full example: `SPEC-042-user-authentication.md`

## Prerequisite Verification

Before creating specification:

1. **Locate Research Document:**
   - Find the corresponding `SDD/research/RESEARCH-[###]-[feature-name].md` file
   - If multiple research documents exist, append an `## Awaiting Research Document Selection` block to `SDD/orchestration/progress.md` (following the `## Awaiting Clarification` shape) naming the candidate files, then return immediately.
   - Verify the research document is complete (has all sections filled)

2. **Confirm Research Completeness:**
   - System Data Flow: Documented with specific file:line references
   - Stakeholder Mental Models: All perspectives captured
   - Production Edge Cases: Historical issues analyzed
   - Files That Matter: Core logic and tests identified
   - Security Considerations: Auth/privacy/validation documented
   - Testing Strategy: Test scenarios outlined
   - Documentation Needs: Section identifying future docs requirements is complete

3. **Validate Research Quality:**
   - If any research sections are missing or incomplete, note this in the progress file
   - Check if the research-complete step was run (look for completion marker in progress.md)
   - If research is not complete, append an `## Awaiting Research Completion` block to `SDD/orchestration/progress.md` naming the missing or incomplete sections, then return immediately.

## Specification Document Structure

Create the specification using this enhanced template:

```markdown
---
review_panel: [security, performance, data-modeling, api-contract, module-depth]
eval_required: false
cross_cutting_decisions: []
delivery_mode: per-slice
agent_security: auto
---

# SPEC-[###]-[feature-name]

## Executive Summary

- **Based on Research:** RESEARCH-[###]-[feature-name].md
- **Creation Date:** [YYYY-MM-DD]
- **Author:** Claude (with [user's name if known])
- **Status:** Draft/In Review/Approved

## Research Foundation

### Production Issues Addressed
- Issue #[XXX]: [Brief description from research]
- Issue #[YYY]: [Brief description from research]

### Stakeholder Validation
- Product Team: [Key requirements from research]
- Engineering Team: [Technical constraints from research]
- Support Team: [Common pain points from research]

### System Integration Points
- [List key integration points identified in research with file:line references]

## Intent

### Problem Statement
[Clear statement of the problem being solved, based on research findings]

### Solution Approach
[High-level approach to solving the problem]

### Expected Outcomes
[What will be different after implementation]

## Success Criteria

### Functional Requirements
- REQ-001: [Specific, testable requirement]
- REQ-002: [Another specific requirement]
- REQ-003: [Whenever a requirement targets or constrains a quantity, state the number and its unit. "Improves relevance", "shifts appropriately", "significantly reduces" are not requirements — they are placeholders for a number nobody wrote down.]

### Non-Functional Requirements
- PERF-001: [Performance requirement with specific metrics]
- SEC-001: [Security requirement from research — if it caps, bounds, or budgets a quantity, state the bound and its unit]
- UX-001: [User experience requirement]

### Quantitative Ledger

> Every number this spec asserts, in one table — the goals it must hit and the bounds it must respect, side by side. Downstream reviewers do arithmetic against this table; they do not go hunting for numbers scattered across the document.
>
> If the spec asserts no quantities at all, replace the table with the single line `No quantitative goals or constraints.` and move on. Do not fabricate numbers to fill it.

| ID | Kind | Quantity (with unit) | Value or bound | Bears on |
|---|---|---|---|---|
| [REQ-XXX] | goal | [what is being moved or reached, with unit] | [target value, threshold to cross, or required delta] | [IDs of constraints that limit this] |
| [SEC-XXX / PERF-XXX] | constraint | [the same or an overlapping quantity, with unit] | [cap, bound, budget, or ceiling] | [IDs of goals this limits] |

> **Kind** is `goal` (a value to reach, a threshold to cross, a delta to produce) or `constraint` (a cap, bound, limit, budget, rate/size/latency ceiling). **Bears on** is the cross-reference that makes the arithmetic checkable: for each goal, list every constraint acting on the same quantity or on the mechanism that moves it; leave `—` only when genuinely none does.

## Edge Cases (Research-Backed)

### Known Production Scenarios
- EDGE-001: **[Scenario name]**
  - Research reference: [Section from RESEARCH-XXX]
  - Current behavior: [What happens now]
  - Desired behavior: [What should happen]
  - Test approach: [How to verify]

- EDGE-002: **[Another scenario]**
  - Research reference: [Section from RESEARCH-XXX]
  - Current behavior: [What happens now]
  - Desired behavior: [What should happen]
  - Test approach: [How to verify]

## Failure Scenarios

### Graceful Degradation
- FAIL-001: **[Failure type]**
  - Trigger condition: [What causes this failure]
  - Expected behavior: [How system should handle it]
  - User communication: [Error messages/feedback]
  - Recovery approach: [How to recover]

- FAIL-002: **[Another failure type]**
  - Trigger condition: [What causes this failure]
  - Expected behavior: [How system should handle it]
  - User communication: [Error messages/feedback]
  - Recovery approach: [How to recover]

## Implementation Constraints

### Context Requirements
- **Context discipline:** implementation subagents operate under the sdd-flow Safety-Net Reads budget (no percentage self-checks)
- **Essential files for implementation:**
  - [file path]:lines [why needed]
  - [file path]:lines [why needed]
- **Files requiring multi-pass inline analysis:**
  - [file path] - [why it may need multiple passes or careful inline review]

### Technical Constraints
- [Constraints from research - framework limitations, API restrictions, etc.]
- [Performance requirements from stakeholders]
- [Security requirements from research]

## Modules

For each module created or significantly changed by this feature, articulate the public interface and the complexity it hides. Prefer **deep modules** (Ousterhout): a small interface that hides substantial functionality. Reject shallow modules — wide interfaces over thin internals — as a default position; if a module must be shallow, justify it explicitly.

Each module also carries a **Risk** tier consumed by code review to scale review depth proportionally.

### MODULE-001: [name]
- **Public Interface:** [exported functions, types, endpoints, or commands. Keep small. List signatures, not implementation hints.]
- **Hides:** [the substantive complexity protected behind the interface — algorithms, state machines, external integrations, error recovery, caching, etc. If this section is short, the module is shallow; restructure or justify.]
- **Risk:** [low | medium | high]
  - **low** — boundary-only consequences; failure is recoverable and contained. Reviewer attention focuses on interface contract and tests at the boundary.
  - **medium** — default. Standard review depth.
  - **high** — failure has outsized consequences (financial, security, data integrity, irreversible side effects, regulatory exposure). Reviewer attention extends to internals.
- **Spec refs:** [REQ-XXX, EDGE-XXX, FAIL-XXX implemented by this module]
- **Justification (if shallow):** [Only required if the interface surface is comparable to or larger than what is hidden. Explain why depth was sacrificed — e.g., framework requires this shape, integration adapter with no logic to add, etc.]

### MODULE-002: [name]
[Same structure.]

[Add as many modules as the feature touches. If the feature does not introduce or significantly change any module — e.g., a config-only change — write a single line stating that and skip module entries.]

## Delivery Slices

> **Required only when `delivery_mode: per-slice`.** Omit this section entirely when `delivery_mode: whole-feature` (the default).
>
> A slice is a **concentrated function with a thread line through every relevant layer** this feature touches. It is testable in a focused way; exercising it surfaces the interaction and behavior of every layer it crosses.
>
> Slices are **not restricted to user-facing behavior**. A slice could be an internal pipeline trigger, a webhook handler, a batch job's primary path, or a user-facing form submission. The defining property is the **vertical thread**, not the audience.
>
> SLICE-001 must be the thinnest possible end-to-end happy path — its only job is to prove the thread exists. Subsequent slices add capability and harden edges.

### SLICE-001: [name]
- **Concentrated function:** [one-line description of the vertical thread this slice delivers]
- **REQs satisfied:** [REQ-XXX references — full or partial. A slice may partially satisfy a REQ; later slices fill it in. Mark partial coverage explicitly, e.g., "REQ-003 (partial: happy path only)".]
- **Modules touched:** [MODULE-XXX entries this slice cuts through. Use the `Spec refs:` field on each module as the raw material for this list.]
- **Acceptance check:** [a single, focused test that proves the slice works end-to-end. Ideally an automated test name; manual verification step otherwise.]
- **Sequence rationale:** [why this slice is at this position. SLICE-001 = thinnest end-to-end happy path; subsequent slices add depth, edge cases, and additional concentrated functions.]

### SLICE-002: [name]
[Same structure.]

[Add as many slices as the feature decomposes into, ordered by delivery sequence.]

## Validation Strategy

### Automated Testing
- Unit Tests:
  - [ ] [Specific test scenario from research]
  - [ ] [Another test scenario]
- Integration Tests:
  - [ ] [Integration point test]
  - [ ] [Another integration test]
- Edge Case Tests:
  - [ ] Test for EDGE-001
  - [ ] Test for EDGE-002

### Manual Verification
- [ ] [User flow to verify]
- [ ] [Admin functionality to check]
- [ ] [Error handling to validate]

### Performance Validation
- [ ] [Metric to measure with target value]
- [ ] [Another metric with benchmark]

### Stakeholder Sign-off
- [ ] Product Team review
- [ ] Engineering Team review
- [ ] Security Team review (if applicable)
- [ ] Legal/Compliance review (if applicable)

## Dependencies and Risks

### External Dependencies
- [API/Service dependencies from research]
- [Third-party library dependencies]

### Identified Risks
- RISK-001: [Risk description and mitigation plan]
- RISK-002: [Another risk and mitigation]

## Implementation Notes

### Suggested Approach
[High-level implementation strategy based on research]

### Areas Requiring Careful Inline Analysis
[Specific areas that need thorough inline analysis during implementation — complex integrations, security-sensitive paths, performance-critical logic]

### Critical Implementation Considerations
[Important technical details from research that must be considered]
```

## Specification Frontmatter Fields

The spec template includes five YAML frontmatter fields consumed by sdd-flow and related phases. Populate them thoughtfully based on the research foundation:

- **`review_panel:`** — List of specialist reviewers to convene during spec-review-panel. Default includes `module-depth` (Ousterhout deep-module check on the `## Modules` section) and covers API/data-backed features. Adjust based on feature characteristics:
  - Add `accessibility` for UI features with user-facing interaction.
  - Add `privacy` for features handling PII, consent, or regulated data.
  - Add `cost` for data-intensive or high-traffic features.
  - Add `reliability` for distributed systems, async processing, or retry-heavy flows.
  - Add `agent-security` for agentic features — see `agent_security:` below, which normally appends this value for you.
  - Remove specialists that clearly don't apply (e.g., `api-contract` for pure internal tooling). Removing `module-depth` is rare — almost every spec creates or changes modules.

- **`eval_required:`** — Boolean. Set to `true` if this feature produces LLM output, probabilistic behavior, classification/extraction/summarization, or any quality dimension that unit tests can't verify. When `true`, regression-eval-capture will scaffold a LangSmith eval dataset at implementation completion. Set to `false` for deterministic features (CRUD, UI, data transforms).

- **`cross_cutting_decisions:`** — List of topic labels (snake_case) for any architectural decisions made during this feature that bind future work across the system. Examples: `orchestration_engine`, `vector_store`, `auth_provider`, `primary_datastore`, `logging_format`. Leave empty `[]` if this feature makes no cross-cutting decisions. During planning-complete, the cross-cutting-adr step will extract details for each label from the research/spec and write ADR files under `SDD/adr/`.

- **`agent_security:`** — `auto` (default), `true`, or `false`. Gates the OWASP AI-agent security controls at three points in the flow: the `agent-security` panel value at Step 3c, the agentic-surface lens in the Step 4b code review, and abuse-case seeding at Step 4g eval capture. The control catalog is `skills/ai-agent-security-review/references/owasp-ai-agent-controls.md`.

  **Agentic-surface detection (resolving `auto`).** Set `agent_security: true` and append `agent-security` to `review_panel:` when the research or the spec you are writing describes any of:
  - a call to an LLM / foundation model (direct API, SDK, or framework);
  - a tool or function definition exposed to a model, or an MCP server or client;
  - agent memory, conversation persistence, or a retrieval (RAG) store that feeds a model's context;
  - message passing between two or more agents, or a model-driven subagent spawn;
  - a model output that drives an action on an external system (shell, HTTP write, payment, deploy, file mutation, message send).

  When none applies, leave `auto` (or set `false` explicitly if the feature merely mentions agents without building one). Set `true` by hand to force the review on regardless of detection; set `false` to suppress it — the user's declaration wins over detection in both directions. `auto` is not a silent skip: it is re-evaluated by the orchestrator at Step 3c, and the specialist runs its own scope gate and short-circuits cheaply when the surface is absent.

  This field is about **agentic** risk — prompt injection, tool over-scoping, memory poisoning, excessive autonomy, Denial of Wallet. Classical appsec stays with the `security` panel value; do not drop `security` because you added `agent-security`.

- **`delivery_mode:`** — `whole-feature` (default) or `per-slice`. Controls whether the spec must include a `## Delivery Slices` section and whether downstream phases route through per-slice behavior.

  **Authoring default (new specs):** Set `delivery_mode: per-slice` unless the feature yields fewer than 2 genuine vertical slices — in which case set `delivery_mode: whole-feature` and record a one-line justification inline in the spec (e.g., as a comment in the `## Delivery Slices` section placeholder, or at the top of `## Implementation Notes`). The template above starts from `per-slice` to reflect this recommendation.

  The parse-side default (field absent → `whole-feature`) is unchanged for backward compatibility with specs written before this guidance.

  `whole-feature` preserves the existing flow exactly; the `## Delivery Slices` section is omitted entirely. `per-slice` opts into vertical-slicing decomposition — a concentrated function threaded end-to-end through every relevant layer per slice; in that mode this body must populate `## Delivery Slices`. If the field is absent from a spec written before this change, treat it as `whole-feature`.

  - **Value validation (binding for every consumer of this field):** the canonical enum is exactly `{whole-feature, per-slice}` (lowercase, hyphenated). Absent → silent default to `whole-feature` (no log line; this is the documented default behavior). Any other value (typos like `per_slice`, `PerSlice`, `vertical-thread`, `whole_feature`, etc.) is invalid: fail fast with a clear error naming (a) the SPEC file path, (b) the offending value verbatim, and (c) the canonical enum. Never silently fall through to the default branch. When this body runs in autonomous mode, surface the failure by emitting an `## Awaiting Slicing Decision` block to `SDD/orchestration/progress.md` (mirrors `## Awaiting Clarification` shape) so the orchestrator halts; in supervised mode, surface inline. The same rule applies wherever `delivery_mode:` is read by downstream phases — the implementation phase, the slice handling, sdd-flow Step 4, the slice-integrity reviewers, and the practicality gate below — each consumer either fails fast with the same error shape or delegates to a single shared validation step.

These fields have sensible defaults; populate them intentionally rather than leaving as boilerplate.

## Planning Process

1. **Load Research Foundation:**
   - Read the complete RESEARCH-XXX document
   - Extract all findings, edge cases, and stakeholder inputs
   - Note specific file:line references for implementation

2. **Transform Research into Requirements:**
   - Convert research findings into specific, testable requirements
   - Ensure every edge case from research has a corresponding specification
   - Map stakeholder needs to success criteria

3. **Define Clear Validation:**
   - Create specific test scenarios for each requirement
   - Include performance benchmarks where applicable
   - Define acceptance criteria for stakeholder sign-off

4. **Plan for Implementation:**
   - Identify which files need to be loaded during implementation
   - Note areas that will require multi-pass inline analysis during the implementation phase
   - Ensure context requirements stay under 40%

5. **Articulate Modules — Prefer Deep Over Shallow:**
   - For every module the feature creates or significantly changes, fill in a `MODULE-XXX` entry under the `## Modules` section.
   - **Deep module** (preferred): small public interface, substantial hidden complexity. Hidden complexity is what callers don't have to know — algorithms, state, retries, caching, integration glue, error recovery.
   - **Shallow module** (avoid by default): public interface comparable to or larger than what it hides. Examples: pass-through wrapper, getter/setter façade with no logic, public method per private field, module that exists only to call one external service with no added behavior.
   - If a module must be shallow, fill the `Justification (if shallow)` field. Unjustified shallow modules will be flagged by the `module-depth` specialist in spec-review-panel and should be merged, deepened, or removed.
   - Assign each module a **Risk** tier (low/medium/high) — this drives review depth in code review. High-risk = irreversible, financial, security-critical, regulatory. Low-risk = contained, recoverable, boundary-only.
   - Map every REQ-XXX/EDGE-XXX/FAIL-XXX to at least one module via the `Spec refs:` field — every requirement must have a home.

6. **Define Delivery Slices (per-slice mode only):**
   - Applies only when `delivery_mode: per-slice` is set in the spec frontmatter. In `whole-feature` mode (the default), omit the `## Delivery Slices` section entirely and skip this step.
   - Decompose the feature into ordered `SLICE-XXX` entries, each describing a concentrated function threaded end-to-end through every relevant layer. Use each MODULE-XXX entry's `Spec refs:` as raw material — REQs that span multiple modules are candidate slices.
   - **SLICE-001 must be the thinnest possible end-to-end happy path.** Its only job is to prove the thread exists; resist the urge to put depth or edge cases here.
   - Subsequent slices add capability or harden edges, building on prior slices. Capture the reason for each slice's position in `Sequence rationale`.
   - A slice is a vertical thread, not a horizontal layer. Slices that touch only one module when the feature spans multiple are likely horizontal layers in disguise — either widen the thread or justify the single-module slice explicitly in the rationale.
   - REQs may be split across slices; mark partial coverage explicitly (e.g., `REQ-003 (partial: happy path only)`) so later slices can complete them.
   - Every REQ-XXX / EDGE-XXX / FAIL-XXX should be reachable through some slice in the sequence by the time the last slice lands.

7. **Validate `delivery_mode:` value (spec ingestion gate):**
   - Read the `delivery_mode:` field from the spec frontmatter being created (or, when this body runs against an existing spec, the field already on disk).
   - Apply the value-validation rule from the frontmatter prose above: exact match against `{whole-feature, per-slice}`; absent → silent default `whole-feature`; any other value → fail fast.
   - On invalid value, emit the error: `Invalid delivery_mode value '<value>' in <spec-path>. Allowed values: whole-feature, per-slice. Edit the spec frontmatter and re-invoke the planning body.` In autonomous mode, append an `## Awaiting Slicing Decision` block to `SDD/orchestration/progress.md` mirroring the `## Awaiting Clarification` shape so the orchestrator halts; in supervised mode, surface inline and stop processing.
   - Do NOT silently fall through to the `whole-feature` branch when the value is malformed — that masks user typos and produces silent misbehavior downstream.

8. **Practicality Check (per-slice mode only — the practicality gate):**
   - Applies only when `delivery_mode: per-slice` is set. Skip otherwise.
   - After Step 6 has populated `## Delivery Slices`, evaluate whether the slicing produced is meaningful. Run these four boolean heuristics against the spec's `## Modules` section and the candidate slice set:
     1. **Single-MODULE touch-set.** Only one `MODULE-XXX` entry exists for the feature, OR every candidate slice's `Modules touched` field lists the same single module.
     2. **No thinner happy path.** The only honest decomposition producible is "build all of it, then test it" — i.e., SLICE-001 cannot be made thinner than the whole feature without losing end-to-end reachability.
     3. **Universal-slice REQ touch.** Every `REQ-XXX` in the spec is touched by every plausible slice — i.e., the slices are not actually decomposable, they all carry the same REQ load. **Disable this heuristic when the spec has exactly one REQ (resolves L-1):** with a single-REQ spec, every slice trivially touches that REQ, and heuristic 3 would fire spuriously regardless of whether slicing is meaningful. The single-REQ case is already covered by heuristic 4 (single concentrated function) and, if applicable, heuristic 1 (single-MODULE touch-set). Skip heuristic 3 for single-REQ specs to avoid the vacuous-trigger.
     4. **Single concentrated function.** The feature, examined honestly, has exactly one concentrated function and no candidate slice expresses a different concentrated function.
   - **Qualitative-judgment escape:** if all four boolean heuristics return false but qualitative judgment is that slicing is impractical anyway, that escape may fire — but the `<reason>` text MUST begin with the literal prefix `Qualitative judgment: ` so the audit trail can distinguish boolean firings from free-form ones.
   - **When the gate fires (any heuristic returns true OR the qualitative escape applies):**
     - Replace the populated `## Delivery Slices` section with the single line: `Slicing not applicable: <reason citing the firing heuristic or "Qualitative judgment: <specific concern>">`.
     - Append an `## Awaiting Slicing Decision` block to `SDD/orchestration/progress.md` mirroring the `## Awaiting Clarification` shape exactly. The block names the spec, the firing heuristic (or qualitative judgment text), and the options.
     - **Supervised mode** — surface inline:
       > Per-slice was requested for this feature, but meaningful vertical slices were not found. Either (a) fall back to `whole-feature` for this feature only [recommended], or (b) push back — point at a slice boundary that was missed and retry.
     - **Autonomous mode** — halt and return a bounded completion message (≤200 words) describing the two options: (a) fall back to `whole-feature` for this feature only, or (b) provide a hint about a slice boundary to retry slicing. Include the SPEC file path and `SDD/orchestration/progress.md` as artifact paths. This mirrors the autonomous halt pattern, with different option labels.
   - When none of the heuristics fire and qualitative judgment is that slicing is meaningful, proceed with the populated `## Delivery Slices` section — no halt, no annotation.

9. **Run the Feasibility Arithmetic Self-Check:**
   - Applies only when the `### Quantitative Ledger` table has at least one row of kind `goal`. If the ledger says `No quantitative goals or constraints.`, skip this step — do not manufacture a check.
   - For each `goal` row, take every constraint named in its `Bears on` column and do the arithmetic: does the headroom the constraint permits cover the movement the goal requires? Convert to a common unit first; a unit mismatch is itself a finding.
   - If any goal needs more headroom than its constraints permit, the spec is internally contradictory — effective and compliant are mutually exclusive. Do NOT write the spec around it. Resolve it now: relax the constraint, lower the goal, or specify a different mechanism, and record which you chose in `## Implementation Notes`.
   - If a goal's `Bears on` column is empty because no constraint was written down, re-read the Non-Functional Requirements before accepting that — an unstated cap that shows up later as an eval criterion is the same failure, discovered more expensively.

## Deliverable Expectations

A complete specification must have:

- ✓ All template sections filled with specific, actionable content
- ✓ Every research finding reflected in requirements or edge cases
- ✓ Clear, measurable success criteria
- ✓ Specific test scenarios for validation
- ✓ Implementation guidance with context management plan
- ✓ Risk assessment and mitigation strategies

## Quality Checklist

Before considering the specification complete:

- [ ] All research findings are incorporated
- [ ] Requirements are specific and testable
- [ ] Edge cases have clear expected behaviors
- [ ] Failure scenarios include recovery approaches
- [ ] Context requirements are documented
- [ ] Validation strategy covers all requirements
- [ ] Implementation notes provide clear guidance
- [ ] Best practices have been researched inline as needed
- [ ] Architectural decisions are documented with rationale
- [ ] Every module has a `MODULE-XXX` entry with Interface, Hides, and Risk filled in
- [ ] No shallow modules without explicit justification
- [ ] Every REQ-XXX / EDGE-XXX / FAIL-XXX is mapped to at least one module
- [ ] If `delivery_mode: per-slice`, the `## Delivery Slices` section exists and is populated with at least one `SLICE-XXX` entry
- [ ] If `delivery_mode: per-slice`, every slice declares Concentrated function, REQs satisfied, Modules touched, Acceptance check, and Sequence rationale
- [ ] If `delivery_mode: per-slice`, SLICE-001 is the thinnest possible end-to-end happy path
- [ ] If `delivery_mode: per-slice`, slices are ordered by delivery sequence and each REQ-XXX / EDGE-XXX / FAIL-XXX is reachable through some slice by the last slice
- [ ] If `delivery_mode: whole-feature` (or absent), the `## Delivery Slices` section is omitted
- [ ] Every requirement that targets or constrains a quantity states the number and its unit — no qualitative stand-ins ("appropriately", "meaningfully", "significantly")
- [ ] `### Quantitative Ledger` is populated with every goal and constraint the spec asserts, or carries the single line `No quantitative goals or constraints.`
- [ ] Each `goal` row's `Bears on` column names the constraints acting on it, and the arithmetic clears — no goal requires more headroom than its constraints permit
- [ ] `agent_security:` is populated, and when the feature has an agentic surface the value is `true` and `review_panel:` includes `agent-security`

---

Begin specification creation now using the research foundation. Create the `SDD/requirements/SPEC-[###]-[feature-name].md` document and systematically transform research into executable specification.
