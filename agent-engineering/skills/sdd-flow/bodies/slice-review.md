# Review a Vertical Slice

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. You cannot spawn subagents and cannot invoke slash commands; all work happens inline in your own context.

You are conducting a per-slice code review for a single `SLICE-XXX` within a feature whose SPEC declares `delivery_mode: per-slice`.

## Active-Slice Resolution Convention (shared with slice-start, slice-retro, slice-commit)

Per SPEC MODULE-002 active-slice fallback asymmetry:

1. **Explicit `[SLICE-ID]` argument** — if provided, use it. Validate against `^SLICE-\d{3}$` BEFORE interpolating into any path (REQ-024 / SEC-003 path-traversal prevention).
2. **IMPLEMENTATION-PLAN's `## Slice Progress` row** at `In Progress` or `Acceptance Check Passing` — this review covers implemented code, so it expects a non-`Not Started`, non-`Complete` row.
3. **Error** — never silently pick. If priority 2 yields multiple candidates, append an `## Awaiting Slicing Decision` block to `SDD/orchestration/progress.md` and return.

## Inert-Mode Gate

This review requires `delivery_mode: per-slice`. **Slice commands are inert in whole-feature mode** (per REQ-007 + EDGE-002).

### Step 1: Locate the active SPEC

```bash
ls SDD/requirements/SPEC-*.md
```

Single match → use it. Multiple → append an `## Awaiting SPEC Selection` block to `SDD/orchestration/progress.md` and return. Zero → emit: `No SPEC found in SDD/requirements/. Complete the planning phase to create one before invoking slice review.`

### Step 2: Read `delivery_mode:` from the SPEC frontmatter

The canonical enum is exactly `{whole-feature, per-slice}` (lowercase, hyphenated). Branch:

- **`per-slice`** → continue with this review's normal behavior.
- **`whole-feature` OR field absent** → emit the REQ-007 verbatim inert message and exit cleanly with NO partial state writes:

  ```
  This review requires `delivery_mode: per-slice` in the spec frontmatter. Current spec uses `delivery_mode: <value>`. Use whole-feature implementation mode instead, or set `delivery_mode: per-slice` in your spec and re-run the planning phase.
  ```

- **Any other value** → fail per REQ-001 validation: `Invalid delivery_mode value '<value>' in <spec-path>. Allowed values: whole-feature, per-slice. Edit the spec frontmatter and re-run the planning phase.`

## Slice-ID Validation (REQ-024 / SEC-003)

Slice-ID arguments MUST be validated against the regex `^SLICE-\d{3}$` BEFORE being interpolated into any read or write path. On regex mismatch, refuse with the REQ-007 message-discipline shape: `Invalid SLICE-ID argument '<arg>'. SLICE-ID must match the pattern SLICE-### (three digits).`

## `## Slice Progress` Table — Binding Schema (REQ-022, reference)

- **Columns:** `SLICE-ID | Name | Status | Acceptance check | Test result | Notes`.
- **Status enum:** `Not Started`, `In Progress`, `Acceptance Check Passing`, `Complete`.
- This review does NOT modify the table directly; slice-retro updates `Status`/`Test result`/`Notes` after fix-and-rerun loops.

## Step 3: Resolve the active SLICE-XXX

Apply the **Active-Slice Resolution Convention** above. Expected statuses for this review: `In Progress` or `Acceptance Check Passing`.

- **`[SLICE-ID]` provided:** verify the row exists in `## Slice Progress` and is at `In Progress`/`Acceptance Check Passing`. If at `Not Started`, fail per EDGE-003: `No implementation found for SLICE-XXX. Run slice-start SLICE-XXX and implement the slice before review.`
- **No argument, single matching row:** use it.
- **No argument, multiple matching rows:** append an `## Awaiting Active Slice Selection` block to `SDD/orchestration/progress.md` and return.
- **No argument, zero matching rows:** fail with: `No slice currently In Progress or Acceptance Check Passing in <IMPLEMENTATION-PLAN-XXX-...md>. Run slice-start <SLICE-XXX> first.`

## Step 4: Compute the slice's file set (REQ-004)

The slice's reviewable file set is computed as the **intersection** of:

1. The SPEC's `## Delivery Slices` → `### SLICE-XXX:` → `Modules touched` field — for each MODULE-XXX listed there, expand to the file paths the SPEC's `## Modules` section attributes to that module.
2. The IMPLEMENTATION-PLAN's per-slice progress entries — the files actually modified for this slice (read git diff between the slice's start commit and HEAD; or read the IMPLEMENTATION-PLAN's per-slice changelog if maintained).

**Disagreement handling (per REQ-004):** if the two lists agree, use the intersection. If they disagree, **prefer the IMPLEMENTATION-PLAN list** (it reflects what was actually modified) and surface the divergence as a `MEDIUM` finding in the review output:

```markdown
**MEDIUM finding — Slice scope divergence**: SPEC's `Modules touched` for SLICE-XXX lists <X>; IMPLEMENTATION-PLAN's slice-progress entries list <Y>. Reviewing the IMPLEMENTATION-PLAN set; if the SPEC is correct, the IMPLEMENTATION-PLAN must be reconciled (likely a missing or extra file edit during the slice).
```

**Slice-scoped review caveat — shared/foundation files:** if the slice's file set includes a file that was also modified by an EARLIER slice (foundation file shared across slices), the review focuses on THIS slice's diff only — use `git diff <slice-start-commit>..HEAD -- <path>` to scope the diff. The earlier slice's review owns the earlier slice's diff; this slice owns its own.

## Step 5: Apply the code review process, scoped to the slice's files

Apply the following review process to the computed slice file set. The full review priority order applies:

1. **Specification Alignment (70%)** — verify the slice's REQ/EDGE/FAIL coverage from the SPEC. Restrict to REQ-XXX/EDGE-XXX/FAIL-XXX entries the slice's `Acceptance check` and `Modules touched` cite (a slice need not cover ALL of the feature's REQs — only its own).
2. **Context Engineering (20%)** — verify the slice's section in the IMPLEMENTATION-PLAN's `## Slice Progress` table reflects the work done; verify subagent calls (if any) are logged under `SDD/orchestration/subagent-calls/`; verify ledger consistency (no orphan references to slice work that the slice itself didn't capture).
3. **Test Specification Alignment (10%)** — verify tests exist and pass for the slice's contribution; verify test type coverage (unit / integration / E2E) is appropriate for the slice's surface.

**Apply Risk-Tiered Review Depth** per the slice's `Modules touched` field. For each MODULE-XXX in the slice's `Modules touched`, read the `Risk:` field from the SPEC's `## Modules` section and apply the matching depth:

- **`high` risk** — full internals review: examine every function, branch, and data mutation in the module's files; flag any missing error paths, unvalidated inputs, or state-consistency gaps.
- **`medium` risk** — default review: examine public interfaces, key internal logic paths, and error handling; spot-check internals where the acceptance criteria indicate risk.
- **`low` risk** — tested-boundary review: verify the public contract and acceptance-check tests; skip deep internals unless a surface signal (irreversible action, security-sensitive path, financial data) warrants escalation.

**Implausible-tier override:** if a module is marked `low` but you observe it touches state that is irreversible, security-sensitive, or financial, escalate to `medium` or `high` and note the override in the Module Review Log.

## Step 6: Write the per-slice review document

Write the review output to:

```
SDD/reviews/REVIEW-SLICE-<SLICE-XXX>-<feature-name>-<YYYY-MM-DD>.md
```

Note the **hyphenated date format** `[YYYY-MM-DD]` (uniform across the new artifact families introduced by this feature — RETROSPECTIVE-SLICE, REVIEW-SLICE; resolves panel deferred LOW-13). Pre-existing REVIEW artifacts authored before SDD 2.0.0 may continue to use `[YYYYMMDD]`; the carry-forward is internally consistent within the legacy family.

The review document follows the standard review template (`SDD/reviews/REVIEW-XXX-...md` shape) with these slice-specific additions:

```markdown
# Slice Review: SLICE-<XXX> — [slice name]

## Scope

**Slice:** SLICE-XXX
**Feature:** [feature-name]
**SPEC:** SDD/requirements/SPEC-XXX-[feature-name].md
**IMPLEMENTATION-PLAN:** SDD/implementation/IMPLEMENTATION-PLAN-XXX-[feature-name]-[date].md
**Slice file set (computed per REQ-004 intersection rule):**
- <file 1>
- <file 2>
- ...
**Source of file set:** <"intersection — agreement" / "IMPLEMENTATION-PLAN preferred — divergence">
**Slice diff range:** `<slice-start-commit>..HEAD`

## Slice-Specific Findings

[All standard review sections apply, scoped to the slice's REQ/EDGE/FAIL entries.]

## Module Review Log (Risk-Tiered Depth Applied)

| Module | Declared Risk | Depth Applied | Notes |
|--------|---------------|---------------|-------|
| MODULE-XXX | high \| medium \| low | full \| default \| boundary | [escalations, deviations, justifications] |

## Decision: [APPROVED / REJECTED]

[Standard review decision rationale.]
```

## Per-Slice Review Iteration Cap (REQ-013, reference — enforced elsewhere)

This review itself can be re-run any number of times. The **iteration cap of 3 with progress-stall check** (HIGH must strictly decrease across iterations; or MEDIUM when HIGH is zero) is enforced by the sdd-flow Step 4b/4c orchestration loop, NOT by this review. On halt, findings route to the rolling ledger's `Open recommendations awaiting user decision` section. In `--skip-slice-checkpoints` mode, the entire flow halts. See `agent-engineering/skills/sdd-flow/SKILL.md` Step 4b/4c for the loop logic.

## Flag Inventory (REQ-025 — applies to slice review)

This review introduces NO flags of its own (per SPEC MODULE-002 + REQ-025: `slice-review [SLICE-ID]` — no flags introduced by this feature). The slice-start and slice-retro flags do NOT apply here.

For reference, the slice-command flag inventory across all four slice commands (REQ-025):

| Flag | Command | Default | Notes |
|------|---------|---------|-------|
| `--resume SLICE-XXX` | `slice-start` | Off | Re-attach to In Progress slice. |
| `--force SLICE-XXX` | `slice-start` | Off | Destructive override for re-starting a Complete slice. |
| `--reconcile-ledger SLICE-XXX` | `slice-retro` | Off | Rebuild ledger from on-disk retros. |

The sdd-flow `--replan`, `--from-slice SLICE-XXX`, `--override-replan` are orchestrator-level flags, NOT slice-command flags.

## Path Conventions (REQ-016)

This review emits paths under the SDD 2.0.0 layout:

- `SDD/requirements/SPEC-XXX-[feature-name].md`
- `SDD/implementation/IMPLEMENTATION-PLAN-XXX-[feature-name]-[date].md`
- `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` (kebab-case feature-name slug per CLARIFICATION OQ-B)
- `SDD/reviews/REVIEW-SLICE-XXX-[feature-name]-[YYYY-MM-DD].md`
- `SDD/orchestration/subagent-calls/`

## Refusal-Message Discipline (REQ-007 / UX-001)

Every refusal path follows the REQ-007 message-discipline standard: name the detected condition, name the resolution path, exit cleanly without partial state writes.
