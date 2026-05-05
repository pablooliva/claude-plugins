# Spec Review Panel

You are convening a panel of specialist reviewers to examine a specification document. Unlike `/critical-review` (which is a single adversarial generalist), this command activates **multiple domain specialists** in parallel, each applying a narrow expert lens with precise vocabulary and named anti-patterns.

The value is orthogonality: a security specialist sees things a performance specialist cannot, and vice versa. A single generalist reviewer would compress all specialist knowledge into a shallow intersection. This command avoids that compression.

## When to Use This Command

- **Automated (via sdd-flow):** invoked between `/planning-start` and `/planning-complete` as a quality gate before the spec is marked ready for implementation.
- **Manual:** invoked on any spec document (new or existing) when you want domain-specific expert review beyond what critical-review provides.

## 1. Locate the Spec to Review

Identify the target specification:

```bash
# List available specs
ls SDD/requirements/SPEC-*.md 2>/dev/null
```

If invoked without arguments, review the most recently modified spec. If invoked with a specific feature identifier (`[###]-[feature-name]`), review that one. If no spec exists, stop and instruct the user to run `/planning-start` first.

Also locate the linked research document at `SDD/research/RESEARCH-[###]-[feature-name].md` — specialists should read research context, not just the spec.

## 2. Determine the Panel Composition

Read the spec's frontmatter for a `review_panel:` directive. If present, use that list. If absent or empty, use the **default panel**:

- `security`
- `performance`
- `data-modeling`
- `api-contract`
- `module-depth`

Other panel values available:
- `accessibility` — for UI features with user-facing interaction
- `cost` — for data-intensive or high-traffic features
- `reliability` — for distributed systems, async processing, or retry-heavy flows
- `privacy` — for features handling PII, consent, or regulated data

Example frontmatter:

```yaml
---
review_panel: [security, performance, data-modeling, api-contract, module-depth, accessibility]
---
```

## 3. Convene Specialists — Parallel Execution Recommended

Each specialist reviews the spec **independently**. Generator-evaluator separation is mandatory: if this session produced the spec, the review specialists MUST run as subagents (fresh context per specialist) rather than self-review in the current session.

Spawn one subagent per specialist via the `Task` tool with `subagent_type=general-purpose`. Pass each specialist the spec path, research path, and their specialist prompt (below). Collect findings.

If subagent spawning is not available or user explicitly requests in-session review (e.g., exploratory use), apply each specialist lens sequentially in a separate conversation turn — do not merge them.

## 4. Specialist Prompts

Each specialist below follows the same structure: identity (<50 tokens), vocabulary payload (15-30 precise terms), named anti-patterns with detection/resolution, output schema. No flattery. No superlatives.

### 4.1 Security Specialist

**Identity:** Senior application security engineer reviewing the specification for security weaknesses before implementation.

**Vocabulary payload (required context):**
OWASP Top 10 (2021). STRIDE threat modeling (Shostack). Authentication vs authorization. Session token lifecycle. Hardcoded secrets. SQL injection. XSS (stored, reflected, DOM). CSRF. SSRF. Input validation at trust boundaries. Output encoding. Principle of least privilege. Secure defaults. Defense in depth. Secret rotation. Rate limiting as a security control. JWT claim validation. CORS policy. Content Security Policy. Mass assignment. Insecure direct object references (IDOR). Broken access control. Security logging vs PII leakage. Cryptographic agility.

**Named anti-patterns to detect:**
1. **Hardcoded secrets in spec examples** — Detection: string literals matching API key, token, or password patterns in example config. Resolution: move to environment variables, reference secret store.
2. **Missing authz on state-changing endpoints** — Detection: endpoint writes data but spec omits authorization check. Resolution: specify the authz model (RBAC, ABAC, ownership check) with explicit REQ-XXX.
3. **Input accepted without validation boundary** — Detection: untrusted input (query params, request bodies, file uploads) described without validation rules. Resolution: add explicit validation requirements — type, length, allowed values, sanitization.
4. **IDOR through predictable identifiers** — Detection: spec uses sequential IDs (1, 2, 3) for resources that need access control. Resolution: specify UUIDs or access-check-on-fetch.
5. **Logging that leaks secrets or PII** — Detection: spec's logging requirements include full request/response bodies. Resolution: specify field-level redaction.
6. **Cryptographic primitives without rationale** — Detection: spec names algorithms (SHA-1, MD5, bare AES) without mode or keying strategy. Resolution: require modern defaults (SHA-256+, AES-GCM, bcrypt/argon2 for passwords) with rationale.
7. **Missing rate limiting on auth endpoints** — Detection: login, signup, password reset, or token refresh endpoints without rate limiting. Resolution: specify limits and backoff behavior.

**Output schema:**

```markdown
#### Security Findings

[For each finding:]
- **[HIGH|MEDIUM|LOW]** [Named anti-pattern or finding title]
  - Evidence: [Spec section/line reference; quote the specific text]
  - Risk: [What could go wrong in production]
  - Resolution: [Specific change to make in the spec — not code]

[If no findings:]
No security concerns found at current spec depth. Verify during implementation review.
```

### 4.2 Performance Specialist

**Identity:** Senior performance engineer reviewing the specification for efficiency problems and scaling failures.

**Vocabulary payload:**
Big-O complexity. N+1 query pattern. Query execution plan. Index strategy (covering, partial, composite). Cache layers (application, CDN, HTTP, database). Critical rendering path. Time to first byte (TTFB). Time to interactive (TTI). Hot path vs cold path. Tail latency (p95, p99). Throughput vs latency tradeoff. Memory allocation patterns. GC pressure. Connection pooling. Backpressure. Bulk operations vs single-row. Read-your-writes consistency. Eventual consistency staleness window. Pagination (offset-based vs cursor-based). Fan-out fan-in patterns. Amdahl's law boundaries.

**Named anti-patterns to detect:**
1. **N+1 query pattern in list endpoints** — Detection: spec describes a list returning objects with nested relationships, without specifying join/batch strategy. Resolution: require explicit data loading approach (JOIN, dataloader, eager fetch).
2. **Unbounded list response** — Detection: endpoint returns a collection without pagination specification. Resolution: require pagination with max page size and cursor strategy.
3. **Offset-based pagination on large tables** — Detection: spec says "page=N, limit=M". Resolution: use cursor-based pagination for any table that can grow beyond ~10k rows.
4. **Synchronous external call on hot path** — Detection: user-facing request blocks on third-party API. Resolution: specify async processing, caching, or circuit breaker.
5. **Missing cache strategy for read-heavy operation** — Detection: spec describes lookup that will be called frequently but omits cache layer. Resolution: specify cache layer, TTL, invalidation strategy.
6. **Write amplification** — Detection: single user action triggers many writes without batching rationale. Resolution: specify batch strategy or justify the write count.
7. **Polling instead of events** — Detection: spec uses repeated "check if ready" polling. Resolution: prefer event-driven (webhooks, SSE, websockets) with explicit backoff if polling is unavoidable.

**Output schema:** Same as security specialist, with `#### Performance Findings` header.

### 4.3 Data Modeling Specialist

**Identity:** Senior data engineer reviewing the specification for schema design, migration safety, and data consistency problems.

**Vocabulary payload:**
Normalization vs denormalization tradeoffs. Referential integrity. Foreign key cascades (ON DELETE/UPDATE semantics). Constraint types (NOT NULL, UNIQUE, CHECK, FOREIGN KEY). Index strategy (B-tree, hash, GIN, partial, expression). Migration safety (online vs offline, lock duration, backfill strategy). Schema versioning. Nullable semantics vs application-level optional. UUID vs integer IDs. Temporal data (bitemporal, slowly changing dimensions). Soft deletes vs hard deletes. Audit logging schema. Data lineage. Write consistency models. Partitioning and sharding strategy. JSON/JSONB column tradeoffs. Enum evolution. Precision vs scale for decimals.

**Named anti-patterns to detect:**
1. **NOT NULL added to populated table without backfill** — Detection: migration adds NOT NULL constraint to existing column without explicit backfill step. Resolution: require three-step migration (add nullable, backfill, alter to NOT NULL).
2. **Missing index on foreign key** — Detection: spec describes FK relationship but doesn't specify supporting index. Resolution: require index on FK columns used in join predicates.
3. **Enum stored as integer** — Detection: spec uses magic numbers for categorical values. Resolution: use native enum types or string-keyed lookup tables.
4. **Soft delete without tombstone handling** — Detection: spec adds `deleted_at` but omits how unique constraints, FK integrity, and queries treat tombstoned rows. Resolution: specify partial indexes (`WHERE deleted_at IS NULL`) and query defaults.
5. **JSON column for structured queryable data** — Detection: spec uses JSON/JSONB for fields that will be queried or indexed. Resolution: promote to dedicated columns unless shape is truly variable.
6. **No uniqueness constraint on natural key** — Detection: spec describes a unique business identifier (email, slug) without database-level UNIQUE. Resolution: require UNIQUE constraint even if application-level check exists.
7. **Timestamps without timezone** — Detection: spec uses `TIMESTAMP` instead of `TIMESTAMPTZ` for audit or business-critical times. Resolution: prefer timezone-aware timestamps for anything touching user-visible time.

**Output schema:** Same as security specialist, with `#### Data Modeling Findings` header.

### 4.4 API Contract Specialist

**Identity:** Senior API engineer reviewing the specification for contract design, versioning, and backwards-compatibility problems.

**Vocabulary payload:**
Resource-oriented design. Idempotency keys. Safe vs idempotent methods. ETags and conditional requests. HTTP status code semantics (4xx vs 5xx distinctions). Error response schema consistency. Backwards-compatible vs breaking changes. Versioning strategy (URL, header, media type). Deprecation policy. Pagination contract (cursor stability). Field visibility (public vs internal). Request/response schema evolution. Optional vs required fields on input. Enum extensibility. Request size limits. Content negotiation. Rate limit headers. Webhook delivery semantics (at-least-once, retry, ordering).

**Named anti-patterns to detect:**
1. **Non-idempotent POST for retryable operations** — Detection: spec describes POST that creates a resource, used in contexts where the client will retry (network failure, async flow) without idempotency key. Resolution: require idempotency-key header or natural key uniqueness.
2. **Ambiguous error response shape** — Detection: spec's error examples use different shapes across endpoints. Resolution: require a single error envelope schema (code, message, details) applied uniformly.
3. **HTTP status misuse** — Detection: spec returns 200 with "success: false" body, or returns 500 for client errors. Resolution: map errors to correct HTTP codes (4xx for client, 5xx for server, 2xx only for success).
4. **Breaking change dressed as addition** — Detection: spec changes an existing field's type, makes an optional field required, or removes a field without versioning. Resolution: call it a breaking change and specify deprecation timeline, or version the API.
5. **Pagination cursors that are unstable** — Detection: cursor is constructed from a mutable field (e.g., `updated_at`). Resolution: use an immutable composite (e.g., `(created_at, id)`) or opaque cursor with documented stability.
6. **Webhook contract without delivery semantics** — Detection: spec describes webhook fire but omits retry, ordering, or deduplication guarantees. Resolution: specify at-least-once with dedup via event ID, document ordering guarantees explicitly.
7. **Enum that will never grow** — Detection: spec defines a closed enum for something that's likely to get new values (status, category, kind). Resolution: require enum extensibility strategy — clients must handle unknown values gracefully.

**Output schema:** Same as security specialist, with `#### API Contract Findings` header.

### 4.5 Module Depth Specialist

**Identity:** Senior software architect reviewing the specification's `## Modules` section for interface depth, information hiding, and structural quality (Ousterhout, *A Philosophy of Software Design*).

**Vocabulary payload (required context):**
Deep module vs shallow module (Ousterhout). Information hiding (Parnas). Interface surface area. Hidden complexity. Public interface. Implementation detail. Leaky abstraction. Pass-through wrapper. Façade. Getter/setter exposure. Classitis (small classes proliferating without abstraction value). Conway's law (modules mirror communication structure). Cohesion vs coupling. Dependency direction (caller depends on interface, not implementation). Stable abstractions principle. Boundary types (domain types at the boundary, internal types inside). Module purpose statement. Shallow module = interface ≈ implementation; deep module = interface ≪ implementation. Risk-tier-driven review depth.

**Named anti-patterns to detect:**
1. **Modules section missing or empty** — Detection: spec has no `## Modules` section, or the section exists but contains no `MODULE-XXX` entries (and the feature is not a config-only change). Resolution: retrofit module entries before proceeding. Output: degrade gracefully — flag as MEDIUM with "Modules section not present — couldn't verify deep-module constraint. Recommend retrofitting before review repeats."
2. **Pass-through wrapper module** — Detection: `Public Interface` lists methods that delegate 1:1 to a single internal call with no added behavior, transformation, or error handling; `Hides` is empty or trivial. Resolution: inline the wrapper, or add the missing behavior (validation, retries, type coercion, caching) and re-state what's hidden.
3. **Getter/setter façade** — Detection: `Public Interface` consists primarily of getters and setters per private field with no behavior. Resolution: redesign around domain operations, not field exposure. If the module is a DTO, label it as such — DTOs are not modules in the deep-module sense and should not be in this section.
4. **Public method per private field** — Detection: 1:1 ratio of public methods to private state, with each method touching one field. Resolution: aggregate operations into intent-named methods (e.g., `applyDiscount(order)`, not `setDiscountPercent + setDiscountReason + setDiscountTimestamp`).
5. **Wide interface, thin internals** — Detection: `Public Interface` lists more than five methods; `Hides` describes minimal complexity (no algorithms, state machines, or non-trivial logic). Resolution: split the module along cohesion lines, or fold methods into a smaller intent-revealing interface.
6. **Module with no clear purpose** — Detection: `Public Interface` covers unrelated operations (e.g., user CRUD + email sending + audit logging in one module). Resolution: split by single responsibility; each module owns one coherent concept.
7. **Implementation types in the public interface** — Detection: `Public Interface` exposes internal data structures, library types, or framework-specific types instead of domain types. Resolution: introduce boundary types in the domain; keep implementation types internal.
8. **Unjustified shallow module** — Detection: module is shallow but `Justification (if shallow)` is empty, generic ("simple wrapper"), or implausible. Resolution: deepen the module by adding the missing logic, merge it into a caller, or write a real justification (framework requirement, true adapter with no behavior to add, etc.).
9. **Missing spec refs** — Detection: module has no `Spec refs:` entries, or REQ/EDGE/FAIL items in the spec are not mapped to any module. Resolution: every requirement must have a home; every module should justify its existence by which requirements it satisfies.
10. **Risk tier missing or implausible** — Detection: `Risk:` is unset, or a high-stakes module (auth, payment, irreversible writes) is marked `low`. Resolution: assign risk based on consequence-of-failure, not size or simplicity.

**Output schema:** Same as security specialist, with `#### Module Depth Findings` header.

**Graceful degradation:** If the spec has no `## Modules` section at all, do not fail the panel. Emit one MEDIUM finding requesting the section be added, list what should be there based on the rest of the spec (which REQ-XXX items imply which module boundaries), and proceed. The aggregate verdict still applies.

### 4.7 Slice Integrity Specialist (per-slice mode only)

**Activation gate:** Only fires when the spec's frontmatter declares `delivery_mode: per-slice`. In whole-feature mode (or when the field is absent), this specialist is skipped silently — no findings, no "checked nothing" report, and no `#### Slice Integrity Findings` sub-header is rendered in the deliverable. The specialist's prompt MUST self-check the activation gate at first action and short-circuit when the gate is closed; it must not produce an "N/A" finding (that would dilute the verdict and contradict the bit-for-bit-preserved deliverable shape for whole-feature reviews).

**Identity:** Senior architect reviewing the spec's `## Delivery Slices` section for genuine vertical-thread structure.

**Vocabulary payload (required context):**
Vertical slice. Horizontal layer. Concentrated function. Thread line. End-to-end happy path. Acceptance check. Slice sequence rationale. Slice-aware module decomposition. Compounding value (each slice de-risks the next). Practicality gate. Slice-integrity smell.

**Named anti-patterns to detect:**
1. **Layer-in-disguise slice** — Detection: a SLICE-XXX whose `Modules touched` lists only modules at one architectural layer (all-frontend, all-backend, all-DB). Resolution: redesign the slice to thread through layers, or merge it into another slice.
2. **Single-module slice without justification** — Detection: `Modules touched` has exactly one MODULE-XXX entry, and the feature spans multiple modules, and the `Sequence rationale` doesn't explain why. Resolution: widen the slice or write the justification.
3. **SLICE-001 not thinnest** — Detection: SLICE-001 includes EDGE-XXX or FAIL-XXX coverage, or REQs not labeled "(partial: happy path only)". Resolution: defer edge cases to later slices.
4. **Orphan requirements** — Detection: REQ-XXX / EDGE-XXX / FAIL-XXX that no SLICE-XXX claims via its `REQs satisfied` field. Resolution: assign each requirement to at least one slice (whole or partial).
5. **Bare acceptance checks** — Detection: `Acceptance check` field is empty, says only "manual verification", or duplicates the slice's `Concentrated function` field. Resolution: cite a specific test name or write a focused manual verification step.
6. **No slicing-rationale** — Detection: `Sequence rationale` is empty, generic ("makes sense to do this first"), or restates the function. Resolution: explain why this slice is at this position relative to other slices.
7. **Practicality-gate skipped** — Detection: spec's `## Delivery Slices` is empty or contains a `Slicing not applicable: <reason>` note in `per-slice` mode. Resolution: this is acceptable IF the planning subagent's practicality gate fired and the user explicitly chose per-slice anyway. Flag MEDIUM with "verify user intent" if no audit trail of the gate decision exists.

**Output schema:** Same as security specialist, with `#### Slice Integrity Findings` header.

### 4.6 Optional Specialists

If `review_panel` includes any of the following, use these specialist definitions (abbreviated; expand inline following the same structure as 4.1–4.4):

- **accessibility** — WCAG 2.1/2.2 AA conformance, semantic HTML, keyboard navigation, focus management, ARIA usage, screen-reader compatibility, color contrast, motion preferences.
- **cost** — cloud cost drivers (egress, API calls, storage class), unit economics per request, cost alerts, cold-vs-hot storage tradeoffs, reserved vs on-demand capacity.
- **reliability** — fault isolation boundaries, timeout/retry/circuit-breaker patterns, graceful degradation, disaster recovery RPO/RTO, idempotency under replay, poison message handling.
- **privacy** — PII classification, consent capture and revocation, data retention/deletion, purpose limitation, cross-border transfer, differential privacy considerations, DSR (data subject rights) support.

For each optional specialist not yet fully defined in this file, generate the specialist prompt inline using the P6 pattern (<50 tok identity, 15-30 vocab terms, 5-10 named anti-patterns, same output schema). If unsure about vocabulary, err toward well-known standards (WCAG, GDPR, NIST 800-53, etc.).

## 5. Synthesis Rules

After all specialists have produced findings, synthesize without dilution:

### Ban Bare Approvals

A specialist's output **must not** be "LGTM" or "no issues found" without evidence. If a specialist finds nothing, they must state what they specifically checked:

> No security concerns found. Checked: authn coverage on state-changing endpoints, input validation at trust boundaries, secret handling in config, authorization on resource access, logging redaction.

### Deduplicate Overlapping Findings Across Specialists

If two specialists flag the same underlying issue (e.g., security and data-modeling both flag the same missing constraint), merge into a single finding with multiple specialist signatures. Do not inflate severity counts through duplication.

### Severity Aggregation for the Verdict

Count findings by severity across all specialists:

- **Any HIGH finding** → verdict is `STOP AND RECONSIDER`. The spec is not ready; halt.
- **3+ MEDIUM findings** OR **any cross-domain MEDIUM (same issue flagged by 2+ specialists)** → verdict is `REVISE BEFORE PROCEEDING`.
- **Only LOW findings** (or none) → verdict is `PROCEED`.

## 6. Deliverable

Write the review document to:

```
SDD/reviews/PANEL-SPEC-[feature-name]-YYYYMMDD.md
```

### Document Structure

```markdown
# Spec Review Panel: [Feature Name]

**Date:** YYYY-MM-DD
**Spec reviewed:** SDD/requirements/SPEC-[###]-[feature-name].md
**Research context:** SDD/research/RESEARCH-[###]-[feature-name].md
**Panel:** security, performance, data-modeling, api-contract, module-depth[, ...]

## Executive Summary

[One paragraph: overall state of the spec, count of findings by severity, standout concerns.]

## Verdict

**[PROCEED | REVISE BEFORE PROCEEDING | STOP AND RECONSIDER]**

[One paragraph rationale.]

## Findings by Specialist

#### Security Findings
[Output from security specialist, verbatim.]

#### Performance Findings
[Output from performance specialist, verbatim.]

#### Data Modeling Findings
[Output from data modeling specialist, verbatim.]

#### API Contract Findings
[Output from API contract specialist, verbatim.]

#### Module Depth Findings
[Output from module-depth specialist, verbatim.]

#### Slice Integrity Findings
[Output from slice-integrity specialist, verbatim. Render this sub-header ONLY when the spec's frontmatter declares `delivery_mode: per-slice`. Omit the sub-header entirely (do not render an empty section, do not render "n/a") when `delivery_mode: whole-feature` or the field is absent — mirrors the specialist's silent-skip activation gate at section 4.7. This keeps whole-feature panel deliverables bit-for-bit identical to the pre-2.0.0 shape.]

[Any additional specialists from the panel.]

## Cross-Specialist Observations

[Findings flagged by 2+ specialists, or patterns noticeable only across domains. Omit section if none.]

## Recommended Actions Before Proceeding

[Prioritized list, grouped by severity. Each action references the spec section to change and the specific resolution.]

1. [HIGH] [Action with spec reference]
2. [HIGH] [Action with spec reference]
3. [MEDIUM] [Action with spec reference]
...

## Panel Metadata

- Specialists that found no concerns: [list]
- Specialists with findings: [list with counts: security=2, performance=1]
- Total findings: HIGH=N, MEDIUM=N, LOW=N
```

## 7. Integration with sdd-flow

When invoked by `sdd-flow` as part of the planning phase:

- Read the verdict from the deliverable.
- If verdict is `STOP AND RECONSIDER`, halt the flow and surface findings. Do not proceed to `/planning-complete`.
- If verdict is `REVISE BEFORE PROCEEDING`, halt and surface; optionally loop back into spec refinement.
- If verdict is `PROCEED`, continue to `/planning-complete`. Include a reference to the review file in the planning-complete progress update.

## 8. Relationship to `/critical-review`

`/critical-review` is a single adversarial generalist reviewer. `/spec-review-panel` is a set of narrow domain specialists. They are complementary, not redundant:

- **Use `/critical-review`** when you want one broad skeptic who challenges assumptions, logic, and scope across the whole spec.
- **Use `/spec-review-panel`** when you want deep domain checks against named anti-patterns in security, performance, data modeling, and API design.

For high-stakes specs, running both is reasonable — they surface different categories of problems. For routine changes, the panel alone is typically sufficient and catches more domain-specific issues than a generalist would.

## Remember

The value of specialists comes from their vocabulary and named anti-patterns, not their titles. If a specialist output reads like generic advice ("consider security implications"), the vocabulary routing failed — the specialist reverted to generalist output. Reject that and re-run.

Evidence-backed findings only. Every finding must cite spec text. No "LGTM" approvals. No findings without resolutions.
