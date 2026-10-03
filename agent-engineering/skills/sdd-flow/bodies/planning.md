# Initialize Planning/Specification Phase

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow’s flat-orchestration contract forbids it; all work happens inline in your own context.

SPECIFICATION PHASE INITIALIZATION

Starting planning phase based on completed research.

## Initial Context Load

1. **Read Progress File:**
   - Load `SDD/orchestration/progress.md` to understand research completion status
   - The research document is the path in your prompt — do not take it from this file, which may also reference earlier features' research
   - Note any important context from the research phase

2. **Read Ubiquitous Language Glossary:**
   - If `SDD/UBIQUITOUS_LANGUAGE.md` exists, load it. This is the project-wide glossary of domain terms — use these names exactly when writing the spec, in preference to any synonyms or near-synonyms. Aligning vocabulary with the glossary is non-negotiable; if the spec needs a term not in the glossary, propose it as an addition (captured during the planning-complete phase's glossary-delta step).
   - If the glossary does not exist, proceed without it.

3. **Read the Design Brief:**
   - Read the design brief at the path in your prompt (`SDD/requirements/DESIGN-[###]-[feature-name].md`). Your prompt states its approved revision and tier. The user read and approved this document; the spec you write is held to it.
   - If your prompt names no brief (a flow that began before the design gate existed), proceed without one and write the single line `None.` under `## Deviations from Design Brief`.

4. **Read the Tier Standard and Tier Plan (tiered features only):**
   - When your prompt gives an approved tier of `1`, `2`, or `3`, read **TIERS** (the tier standard — tiers, the floor, the cut tests) and **TIER_PLAN** (what this feature's tiers contain, with its Deferred table) at the paths in your prompt.
   - When the approved tier is `none`, the feature is untiered: skip this, omit `tier:` from the frontmatter, and omit `## Deferred to Later Tiers`.

5. **Update Progress for Planning Phase:**
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

1. **Use the Research Document Named in Your Prompt:**
   - The research document is the `SDD/research/RESEARCH-[###]-[feature-name].md` path in your prompt. Do not list `SDD/research/` to find or choose one — other research documents there belong to earlier features and tiers.
   - If the path is missing from your prompt, or the file is missing or unreadable, return a failure to the orchestrator naming it; write no stop note.
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
   - If research is not complete, return a failure to the orchestrator naming the missing or incomplete sections. Write no spec and no stop note.

## Specification Document Structure

Create the specification using this enhanced template:

```markdown
---
review_panel: [security, performance, data-modeling, api-contract, module-depth]
cross_cutting_decisions: []
delivery_mode: per-slice
agent_security: auto
tier: 1
---

# SPEC-[###]-[feature-name]

## Executive Summary

- **Based on Research:** RESEARCH-[###]-[feature-name].md
- **Based on Design:** DESIGN-[###]-[feature-name].md (revision N, Tier T)
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

## Deviations from Design Brief

[`None.` — or one entry per departure:]

- **[decision | scope | footprint | slice-outline]:** the brief said [X]; this spec says [Y]. **Why:** [research finding, arithmetic, or review finding that required it].

## Deferred to Later Tiers

> **Tiered specs only** (`tier:` present). Omit this section entirely when the spec has no `tier:`.
>
> What this tier deliberately leaves out. Reviewers treat every row as left out on purpose. Deferred items carry **no** `REQ-` / `EDGE-` / `FAIL-` ID — they are not requirements of this tier — so every "each REQ / each EDGE" rule in the flow covers this tier's items and nothing else. Write `None.` when nothing is deferred (always the case for `tier: 3`).

| ID | Item | To tier | Why it was safe to leave out | If reached now | Cost to add later | Came from |
|---|---|---|---|---|---|---|
| DEFER-001 | [behaviour left out — never a module or interface] | 2 | [reason, naming the cut test] | [FAIL-XXX — the loud failure this tier implements — or "not reachable"] | cheap / moderate / expensive | [proposal / review / implementation] |

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

For each module created or significantly changed by this feature, articulate the public interface and the complexity it hides. Prefer **deep modules**: a lot of behaviour behind an interface that is small for callers to learn. Depth is **leverage** — behaviour a caller gets per fact of interface it must know — not a ratio of interface size to implementation size. Reject shallow modules — ones a caller must learn nearly as much to use as to do the work itself — as a default position; if a module must be shallow, justify it explicitly.

Each module also carries a **Risk** tier consumed by code review to scale review depth proportionally.

### MODULE-001: [name]
- **Public Interface:** [everything a caller must know to use the module correctly: exported functions, types, endpoints, or commands (signatures, not implementation hints), plus any invariants the caller must uphold, required call order, error modes it must handle, configuration it must supply, and performance bounds it must respect. Keep it small to learn.]
- **Hides:** [the behaviour callers are spared — algorithms, state machines, external integrations, error recovery, caching, etc. Apply the deletion test: if deleting this module would leave callers making the same call one level down, with nothing more to own, the module is shallow; restructure or justify.]
- **Risk:** [low | medium | high]
  - **low** — boundary-only consequences; failure is recoverable and contained. Reviewer attention focuses on interface contract and tests at the boundary.
  - **medium** — default. Standard review depth.
  - **high** — failure has outsized consequences (financial, security, data integrity, irreversible side effects, regulatory exposure). Reviewer attention extends to internals.
- **Spec refs:** [REQ-XXX, EDGE-XXX, FAIL-XXX implemented by this module]
- **Justification (if shallow):** [Only required if a caller must learn about as much to use the module as to do the work itself. Explain why depth was sacrificed — e.g., framework requires this shape, integration adapter with no logic to add, etc. A later tier's needs are never a justification.]

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
>
> Slice IDs are `SLICE-` plus three digits. When a re-plan splits an existing slice, its parts may keep the number and take one lowercase letter (`SLICE-005a`, `SLICE-005b`) instead of renumbering the slices after it. No other suffix is valid (`^SLICE-\d{3}[a-z]?$`).

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

The spec template includes these YAML frontmatter fields, consumed by sdd-flow and related phases. Populate them thoughtfully based on the research foundation:

- **`review_panel:`** — List of specialist reviewers to convene during spec-review-panel. Default includes `module-depth` (deep-module check on the `## Modules` section, depth measured as leverage) and covers API/data-backed features. Adjust based on feature characteristics:
  - Add `accessibility` for UI features with user-facing interaction.
  - Add `privacy` for features handling PII, consent, or regulated data.
  - Add `cost` for data-intensive or high-traffic features.
  - Add `reliability` for distributed systems, async processing, or retry-heavy flows.
  - Add `agent-security` for agentic features — see `agent_security:` below, which normally appends this value for you.
  - Remove specialists that clearly don't apply (e.g., `api-contract` for pure internal tooling). Removing `module-depth` is rare — almost every spec creates or changes modules.


- **`cross_cutting_decisions:`** — List of topic labels (snake_case) for any architectural decisions made during this feature that bind future work across the system. Examples: `orchestration_engine`, `vector_store`, `auth_provider`, `primary_datastore`, `logging_format`. Leave empty `[]` if this feature makes no cross-cutting decisions. During planning-complete, the cross-cutting-adr step will extract details for each label from the research/spec and write ADR files under `SDD/adr/`.

- **`agent_security:`** — `auto` (default), `true`, or `false`. Gates the OWASP AI-agent security controls at two points in the flow: the `agent-security` panel value at Step 3c and the agentic-surface lens in the Step 4b code review. The control catalog is `skills/ai-agent-security-review/references/owasp-ai-agent-controls.md`.

  **Agentic-surface detection (resolving `auto`).** Set `agent_security: true` and append `agent-security` to `review_panel:` when the research or the spec you are writing describes any of:
  - a call to an LLM / foundation model (direct API, SDK, or framework);
  - a tool or function definition exposed to a model, or an MCP server or client;
  - agent memory, conversation persistence, or a retrieval (RAG) store that feeds a model's context;
  - message passing between two or more agents, or a model-driven subagent spawn;
  - a model output that drives an action on an external system (shell, HTTP write, payment, deploy, file mutation, message send).

  When none applies, leave `auto` (or set `false` explicitly if the feature merely mentions agents without building one). Set `true` by hand to force the review on regardless of detection; set `false` to suppress it — the user's declaration wins over detection in both directions. `auto` is not a silent skip: it is re-evaluated by the orchestrator at Step 3c, and the specialist runs its own scope gate and short-circuits cheaply when the surface is absent.

  This field is about **agentic** risk — prompt injection, tool over-scoping, memory poisoning, excessive autonomy, Denial of Wallet. Classical appsec stays with the `security` panel value; do not drop `security` because you added `agent-security`.

- **`tier:`** — `1`, `2`, or `3`: the delivery tier this spec covers, copied from the approved tier in your prompt. A tier says how much of the feature to build; slices say in what order to build it. Omit the field when the approved tier is `none` (the brief said tiers are not applicable). **Absent means untiered:** every rule applies as it did before tiers existed, so specs written before this field behave unchanged. A `tier:` value is never a reason to lower rigour — the same panel, reviews, tests, and site counts apply to whatever the tier builds.

- **`delivery_mode:`** — `whole-feature` (default) or `per-slice`. Controls whether the spec must include a `## Delivery Slices` section and whether downstream phases route through per-slice behavior.

  **Authoring default (new specs):** Set `delivery_mode: per-slice` unless the feature yields fewer than 2 genuine vertical slices — in which case set `delivery_mode: whole-feature` and record a one-line justification inline in the spec (e.g., as a comment in the `## Delivery Slices` section placeholder, or at the top of `## Implementation Notes`). The template above starts from `per-slice` to reflect this recommendation.

  The parse-side default (field absent → `whole-feature`) is unchanged for backward compatibility with specs written before this guidance.

  `whole-feature` preserves the existing flow exactly; the `## Delivery Slices` section is omitted entirely. `per-slice` opts into vertical-slicing decomposition — a concentrated function threaded end-to-end through every relevant layer per slice; in that mode this body must populate `## Delivery Slices`. If the field is absent from a spec written before this change, treat it as `whole-feature`.

  - **Value validation (binding for every consumer of this field):** the canonical enum is exactly `{whole-feature, per-slice}` (lowercase, hyphenated). Absent → silent default to `whole-feature` (no log line; this is the documented default behavior). Any other value (typos like `per_slice`, `PerSlice`, `vertical-thread`, `whole_feature`, etc.) is invalid: fail fast with a clear error naming (a) the SPEC file path, (b) the offending value verbatim, and (c) the canonical enum. Never silently fall through to the default branch. This body surfaces the failure by returning it to the orchestrator, in both modes, and writes no stop note — `## Awaiting Slicing Decision` belongs to the practicality gate alone. The same rule applies wherever `delivery_mode:` is read by downstream phases — the implementation phase, the slice handling, sdd-flow Step 4, the slice-integrity reviewers, and the practicality gate below — each consumer either fails fast with the same error shape or delegates to a single shared validation step.

These fields have sensible defaults; populate them intentionally rather than leaving as boilerplate.

## Planning Process

1. **Load Research Foundation:**
   - Read the complete RESEARCH-XXX document. On a next-tier cycle it is a delta: where it says a section is unchanged from the previous tier's research, read that section in the previous document (path in your prompt)
   - Extract all findings, edge cases, and stakeholder inputs
   - Note specific file:line references for implementation

2. **Conform to the Brief:**
   - Its Key decisions, Not doing list, and answered questions are binding; its delivery outline is your starting slice order (you may refine it — you run the slice-practicality gate, which the brief did not).
   - Where research or the feasibility arithmetic forces a departure, make it and record it under `## Deviations from Design Brief`. Never depart silently, and never reopen a question the user has answered.
   - A module or file area the brief's "What changes where" table does not cover is a `footprint` deviation — record it.

3. **Scope to the Tier (tiered specs only):**
   - Specify the approved tier and nothing beyond it. Start `## Deferred to Later Tiers` from the tier plan's Deferred rows, keeping their `DEFER-XXX` IDs; a deferral you add takes the next free ID with `Came from` = `proposal`. Apply the cut tests in TIERS to anything the research suggests that the brief did not place.
   - **The floor is never deferred** (TIERS → The floor). Whatever it protects is specified in this tier, whichever tier is being built.
   - **A deferred case this tier can reach becomes a real requirement of this tier: its loud failure.** Give it a `FAIL-XXX` entry ("input of kind X is rejected with message Y"), name that ID in the row's `If reached now` column, and implement and test it like any other. In per-slice mode these entries stay out of SLICE-001 (which must be the bare happy path) and are delivered by a later slice of this tier — all of them by its last slice.
   - **Build nothing ahead** (TIERS → Tenet 2). No module, interface member, parameter, option, or dependency may exist because a later tier is expected to need it. Apply the later-tier test to every `MODULE-XXX` entry: with the later tiers deleted from the plan, would this part still be here? If not, remove it. Take the simplest structure this tier's behaviour needs, even when a later tier will have to reshape it.
   - Only behaviour is deferred. Never write a module, interface, or other structure into the Deferred table.

4. **Transform Research into Requirements:**
   - Convert research findings into specific, testable requirements
   - Ensure every edge case from research has a corresponding specification, or — in a tiered spec — a row under `## Deferred to Later Tiers`
   - Map stakeholder needs to success criteria

5. **Define Clear Validation:**
   - Create specific test scenarios for each requirement
   - Include performance benchmarks where applicable
   - Define acceptance criteria for stakeholder sign-off

6. **Plan for Implementation:**
   - Identify which files need to be loaded during implementation
   - Note areas that will require multi-pass inline analysis during the implementation phase
   - Ensure context requirements stay under 40%

7. **Articulate Modules — Prefer Deep Over Shallow:**
   - For every module the feature creates or significantly changes, fill in a `MODULE-XXX` entry under the `## Modules` section.
   - **Interface** means everything a caller must know to use the module correctly — signatures, and also invariants, required call order, error modes, configuration, and performance bounds. Write all of it into `Public Interface`; an obligation left unstated is still part of the interface.
   - **Deep module** (preferred): high leverage — a lot of behaviour per fact of interface a caller must learn. What is hidden is what callers don't have to know — algorithms, state, retries, caching, integration glue, error recovery. Judge by what callers must learn, not by method count or by how long the `Hides` list is.
   - **Shallow module** (avoid by default): a caller must learn about as much to use it as to do the work itself. Apply the **deletion test** — if deleting the module would leave callers making the same call one level down, it is a pass-through. Examples: pass-through wrapper, getter/setter façade with no logic, public method per private field, module that exists only to call one external service with no added behavior.
   - **Seams need two adapters.** Do not introduce a port, plugin point, or injected dependency unless at least two things will sit behind it (typically production + a test stand-in); with one, it is only indirection.
   - If a module must be shallow, fill the `Justification (if shallow)` field. Unjustified shallow modules will be flagged by the `module-depth` specialist in spec-review-panel and should be merged, deepened, or removed.
   - Assign each module a **Risk** tier (low/medium/high) — this drives review depth in code review. High-risk = irreversible, financial, security-critical, regulatory. Low-risk = contained, recoverable, boundary-only.
   - Map every REQ-XXX/EDGE-XXX/FAIL-XXX to at least one module via the `Spec refs:` field — every requirement must have a home.

8. **Define Delivery Slices (per-slice mode only):**
   - Applies only when `delivery_mode: per-slice` is set in the spec frontmatter. In `whole-feature` mode (the default), omit the `## Delivery Slices` section entirely and skip this step.
   - Decompose the feature into ordered `SLICE-XXX` entries, each describing a concentrated function threaded end-to-end through every relevant layer. Use each MODULE-XXX entry's `Spec refs:` as raw material — REQs that span multiple modules are candidate slices.
   - **SLICE-001 must be the thinnest possible end-to-end happy path.** Its only job is to prove the thread exists; resist the urge to put depth or edge cases here.
   - Subsequent slices add capability or harden edges, building on prior slices. Capture the reason for each slice's position in `Sequence rationale`.
   - A slice is a vertical thread, not a horizontal layer. Slices that touch only one module when the feature spans multiple are likely horizontal layers in disguise — either widen the thread or justify the single-module slice explicitly in the rationale.
   - REQs may be split across slices; mark partial coverage explicitly (e.g., `REQ-003 (partial: happy path only)`) so later slices can complete them.
   - Every REQ-XXX / EDGE-XXX / FAIL-XXX should be reachable through some slice in the sequence by the time the last slice lands.

9. **Validate `delivery_mode:` value (spec ingestion gate):**
   - Read the `delivery_mode:` field from the spec frontmatter being created (or, when this body runs against an existing spec, the field already on disk).
   - Apply the value-validation rule from the frontmatter prose above: exact match against `{whole-feature, per-slice}`; absent → silent default `whole-feature`; any other value → fail fast.
   - On invalid value, emit the error: `Invalid delivery_mode value '<value>' in <spec-path>. Allowed values: whole-feature, per-slice. Edit the spec frontmatter and re-invoke the planning body.` Stop processing and return that error to the orchestrator as a failure, in both modes. Write no stop note — `## Awaiting Slicing Decision` is the practicality gate's block (step 10) and its resume options do not apply to a malformed value.
   - Do NOT silently fall through to the `whole-feature` branch when the value is malformed — that masks user typos and produces silent misbehavior downstream.

10. **Practicality Check (per-slice mode only — the practicality gate):**
   - Applies only when `delivery_mode: per-slice` is set. Skip otherwise.
   - After Step 8 has populated `## Delivery Slices`, evaluate whether the slicing produced is meaningful. Run these four boolean heuristics against the spec's `## Modules` section and the candidate slice set:
     1. **Single-MODULE touch-set.** Only one `MODULE-XXX` entry exists for the feature, OR every candidate slice's `Modules touched` field lists the same single module.
     2. **No thinner happy path.** The only honest decomposition producible is "build all of it, then test it" — i.e., SLICE-001 cannot be made thinner than the whole feature without losing end-to-end reachability.
     3. **Universal-slice REQ touch.** Every `REQ-XXX` in the spec is touched by every plausible slice — i.e., the slices are not actually decomposable, they all carry the same REQ load. **Disable this heuristic when the spec has exactly one REQ (resolves L-1):** with a single-REQ spec, every slice trivially touches that REQ, and heuristic 3 would fire spuriously regardless of whether slicing is meaningful. The single-REQ case is already covered by heuristic 4 (single concentrated function) and, if applicable, heuristic 1 (single-MODULE touch-set). Skip heuristic 3 for single-REQ specs to avoid the vacuous-trigger.
     4. **Single concentrated function.** The feature, examined honestly, has exactly one concentrated function and no candidate slice expresses a different concentrated function.
   - **Qualitative-judgment escape:** if all four boolean heuristics return false but qualitative judgment is that slicing is impractical anyway, that escape may fire — but the `<reason>` text MUST begin with the literal prefix `Qualitative judgment: ` so the audit trail can distinguish boolean firings from free-form ones.
   - **When the gate fires (any heuristic returns true OR the qualitative escape applies):**
     - Replace the populated `## Delivery Slices` section with the single line: `Slicing not applicable: <reason citing the firing heuristic or "Qualitative judgment: <specific concern>">`.
     - Append an `## Awaiting Slicing Decision` block to `SDD/orchestration/progress.md` mirroring the `## Awaiting Clarification` shape exactly. The block names the spec, the firing heuristic (or qualitative judgment text), and the two options: (a) fall back to `whole-feature` for this feature only — `/sdd-flow continue --fall-back-to-whole-feature` [recommended]; (b) point at a slice boundary that was missed and retry — `/sdd-flow continue --retry-slicing "<hint>"`. This header is this gate's alone; nothing else writes it.
     - **In both modes, return** a bounded message (≤200 words) saying the gate fired, with the SPEC path and `SDD/orchestration/progress.md` as artifact paths. You cannot ask the user anything; the orchestrator shows the options (supervised) or stops (autonomous), and either answer brings the flow back into planning — the spec is checked and reviewed before any code is written.
   - **Retry run.** When your prompt carries the line `RETRY SLICING: <hint>`, the spec already exists and the gate fired on it once: redo step 8 using the hint as the slice boundary to start from, then steps 9–10. Change nothing else in the spec. If the gate fires again, write a new block as above.
   - When none of the heuristics fire and qualitative judgment is that slicing is meaningful, proceed with the populated `## Delivery Slices` section — no halt, no annotation.

11. **Run the Feasibility Arithmetic Self-Check:**
   - Applies only when the `### Quantitative Ledger` table has at least one row of kind `goal`. If the ledger says `No quantitative goals or constraints.`, skip this step — do not manufacture a check.
   - For each `goal` row, take every constraint named in its `Bears on` column and do the arithmetic: does the headroom the constraint permits cover the movement the goal requires? Convert to a common unit first; a unit mismatch is itself a finding.
   - If any goal needs more headroom than its constraints permit, the spec is internally contradictory — effective and compliant are mutually exclusive. Do NOT write the spec around it. Resolve it now: relax the constraint, lower the goal, or specify a different mechanism, and record which you chose in `## Implementation Notes`.
   - If a goal's `Bears on` column is empty because no constraint was written down, re-read the Non-Functional Requirements before accepting that — an unstated cap that shows up later as an eval criterion is the same failure, discovered more expensively.

## Deliverable Expectations

A complete specification must have:

- ✓ All template sections filled with specific, actionable content
- ✓ Every research finding reflected in requirements or edge cases — or, in a tiered spec, recorded under `## Deferred to Later Tiers`
- ✓ Clear, measurable success criteria
- ✓ Specific test scenarios for validation
- ✓ Implementation guidance with context management plan
- ✓ Risk assessment and mitigation strategies

## Quality Checklist

Before considering the specification complete:

- [ ] All research findings are incorporated, or recorded under `## Deferred to Later Tiers` (tiered specs)
- [ ] `## Deviations from Design Brief` is present, and is `None.` only if the spec matches every binding part of the brief
- [ ] Tiered spec: `tier:` matches the approved tier; every Deferred row is behaviour, not structure; every deferred case this tier can reach has a `FAIL-XXX` named in its row; nothing the floor protects is deferred; no module or interface member exists only for a later tier
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
