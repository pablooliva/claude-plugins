---
adr: 0002
title: Restructure SDD artifact directory layout and rename PROMPT to IMPLEMENTATION-PLAN
status: Accepted
date: 2026-05-05
supersedes: null
superseded_by: null
tags: [cross-cutting, sdd-plugin, naming-convention, directory-layout]
---

# ADR 0002: Restructure SDD artifact directory layout and rename `PROMPT` to `IMPLEMENTATION-PLAN`

## Status

Accepted (2026-05-05)

## Context

The current `SDD/prompts/` directory has accumulated multiple unrelated artifact families: the per-feature implementation plan/tracking document (`PROMPT-XXX-...`), implementation summaries (`prompts/implementation-complete/`), context-management runtime state (`prompts/context-management/progress.md`, subagent-call logs, counters), and compaction snapshots (loose files at `prompts/context-management/`). Adding new per-slice artifacts (per-slice retrospectives, the rolling learnings ledger) on top of this directory would compound the overload and obscure what is a planning artifact, what is an orchestration artifact, and what is runtime context-management state.

Separately, the `PROMPT-XXX-feature.md` filename is historical. In the per-slice world it's more accurately an *implementation plan* — it lists slices, tracks their progress, and captures decisions. The "PROMPT" name described the *role of the document at the moment it was created* (it prompted the implementation work) rather than what the document is.

These two changes are technically independent but share the same migration cost: every plugin command and every `sdd-flow` skill reference must be updated, and every existing user's `SDD/` tree must be migrated. Coupling the rename and the restructure into a single major-version bump (and a single migration helper pass) avoids forcing users through two separate migrations.

This decision binds the path layout and naming convention every future SDD command and every future `sdd-flow` integration must respect. It is captured here so future contributors looking at `SDD/adr/` can find the rationale before proposing layout changes.

## Decision

**Restructure the SDD artifact directory layout** as follows. The change applies to **both** delivery modes — it is a one-time cleanup, not opt-in.

```
SDD/
├── UBIQUITOUS_LANGUAGE.md            # unchanged
├── adr/                              # unchanged
├── flow/                             # unchanged (DECOMPOSITION lives here)
├── research/                         # unchanged (RESEARCH, CLARIFICATION)
├── requirements/                     # unchanged (SPEC lives here)
├── reviews/                          # unchanged
├── implementation/                   # renamed from prompts/
│   ├── IMPLEMENTATION-PLAN-XXX-feature-YYYY-MM-DD.md
│   ├── slices/                                         # per-slice mode only
│   │   ├── RETROSPECTIVE-SLICE-XXX-feature-YYYY-MM-DD.md
│   │   └── LEARNINGS-FEATURE-XXX.md
│   ├── summaries/                                      # renamed from implementation-complete/
│   │   └── IMPLEMENTATION-SUMMARY-XXX-YYYY-MM-DD_HH-MM-SS.md
│   └── test-audits/                                    # relocated from prompts/test-audits/
└── orchestration/                    # split out from prompts/context-management/
    ├── progress.md
    ├── subagent-calls/
    ├── counters/
    └── compacted/                                      # renamed; was loose files at parent level
        ├── research-compacted-YYYY-MM-DD_HH-MM-SS.md
        ├── planning-compacted-YYYY-MM-DD_HH-MM-SS.md
        ├── implementation-compacted-YYYY-MM-DD_HH-MM-SS.md
        └── compact-YYYY-MM-DD_HH-MM-SS.md             # adhoc compactions
```

**Rename `PROMPT-XXX-feature-YYYY-MM-DD.md` to `IMPLEMENTATION-PLAN-XXX-feature-YYYY-MM-DD.md`** in the same major-version bump. The `[feature]` slug in slice and retrospective filenames standardizes on `[feature-name]` (the kebab-case slug), not the numeric `[###]`.

**Apply both changes via the same one-shot migration helper command** (`/sdd-migrate-layout`):

- Detects whether the old layout is present (`SDD/prompts/` exists with content) and whether the new layout is already in place.
- Performs the move set with `git mv` (preserves history).
- Refuses to run when `progress.md` shows an active phase (no in-flight relocation).
- Idempotent: re-running once migrated is a no-op.

**Coordinated version bumps:**

- `sdd/.claude-plugin/plugin.json` and the matching `.claude-plugin/marketplace.json` entry: `1.2.0` → `2.0.0`. The major bump signals the breaking change.
- `agent-engineering/.claude-plugin/plugin.json` and matching marketplace entry: `0.3.0` → `0.4.0`. Additive feature, but interacts with SDD 2.0.0.

## Alternatives Considered

### Restructure + rename, coupled, applied to both modes (chosen)

Coupling the rename and the restructure into a single migration pays the disruption tax once. Applying it to both delivery modes (rather than per-slice only) avoids the maintenance burden of two divergent layouts — one layout, both modes, same logic. The migration helper plus a major-version bump make the breakage explicit and recoverable.

### Per-slice-only restructure (whole-feature keeps current layout)

Rejected because maintaining two divergent layouts is exactly the maintenance burden the merged-codebase decision (ADR 0001) explicitly chose to avoid. Every command would have to know which layout applied based on `delivery_mode:`, and the cognitive overhead would compound with every future change to either layout.

### Restructure now, rename `PROMPT → IMPLEMENTATION-PLAN` later

Rejected because both changes touch the same set of plugin command files and both require coordinated user migration. Splitting them into two releases means users pay the migration cost twice, and the half-migrated state (new layout, old filename) carries its own confusion.

### Rename now, restructure later

Same as above, with the additional cost that the rename without the restructure leaves `SDD/prompts/` even more semantically misleading (`prompts/IMPLEMENTATION-PLAN-...` reads strangely).

### Add per-slice subdirectory under existing `prompts/` without restructuring

Rejected because the existing `prompts/` overload predates per-slice work. The cleanup benefits all users regardless of mode, and adding more artifact families to the already-overloaded `prompts/` would entrench the problem. The restructure is a one-time tax that pays back permanently.

### Rename to something other than `IMPLEMENTATION-PLAN`

Considered alternatives included `IMPL-PLAN`, `PLAN`, `TRACKER`. `IMPLEMENTATION-PLAN` was chosen as the most self-documenting name — it states clearly what the artifact is (a plan for the implementation phase) without introducing abbreviations or overloading the more general word "plan" (which could be confused with planning-phase artifacts under `requirements/`).

## Consequences

### Positive

- **Each top-level directory has a single semantic purpose.** `implementation/` holds per-feature implementation artifacts (plan, slice retros, ledger, summary, test audits). `orchestration/` holds runtime state of the flow itself (progress, subagent-call logs, counters, compactions). `research/`, `requirements/`, `reviews/`, `adr/`, `flow/` retain their existing meanings.
- **`PROMPT → IMPLEMENTATION-PLAN` rename improves discoverability.** A new user looking for "the implementation plan for feature 003" finds it; "PROMPT-003" requires institutional memory.
- **Per-slice artifacts have a natural home under `implementation/slices/`** without polluting the top level or the orchestration tree.
- **One-time cost, one migration helper, one version bump.** Users pay the migration tax exactly once, with tooling to do the move correctly (preserving git history).
- **Future SDD artifacts have an obvious location decision rule:** "is this about *what gets built* (implementation) or *how the flow ran* (orchestration)?"

### Negative / Trade-offs accepted

- **One-time breaking change for all SDD users**, including whole-feature users who get no functional benefit from the per-slice work. Mitigated by the migration helper, the major-version bump signaling the break, and changelog documentation.
- **Every plugin command and the `sdd-flow` skill require coordinated path updates.** A partial restructure (some commands updated, some not) would leave the live system inconsistent and break Session Resumption. Mitigated by the implementation phase enumerating every reference up front (Branch 1 of the research) and verifying no orphan `prompts/` references remain.
- **The `SubagentStop` hook (`sdd/hooks/log_subagent_call.py`) hard-codes the legacy `LOG_SUBDIR` path** and must be updated in the same release. A version-skew between hook and skill would split logs across two paths.
- **In-flight runs at the moment of upgrade need careful handling.** The migration helper's "refuse during active phase" check is the safeguard; the `sdd-flow` Phase Detection logic must check the new path first and fall back to the legacy path so resumption works during the migration window.
- **Existing references in proposals, retros, README files, commit messages, and any external documentation that names `PROMPT-XXX` or `prompts/...` paths become stale.** They remain accurate as historical references but no longer match the current tree.

### Neutral observations

- **`SDD/adr/` is itself unchanged by this restructure** — ADRs already lived at the canonical location. This ADR's existence at `SDD/adr/0002-...` is unaffected.
- **The `[feature-name]` (kebab-case slug) standardization for slice and retrospective filenames** is captured here for consistency with existing conventions; future per-slice tooling should not invent a parallel `[###]`-based filename pattern.

## References

- `proposals/vertical-slicing-decomposition.md` — § "Directory Layout" and § "File rename: PROMPT → IMPLEMENTATION-PLAN"
- `SDD/research/RESEARCH-001-vertical-slicing-step-c.md` — Flow 2 (Directory restructure mapping table) and Branch 1 (full per-command reference enumeration)
- `SDD/research/CLARIFICATION-001-vertical-slicing-step-c.md` — locked decisions #6 (rename + restructure ship together) and #8 (restructure applies to both delivery modes)
- ADR 0001 — Distribution decision that motivates "one layout for both modes" rather than per-mode divergence
- `sdd/hooks/log_subagent_call.py` — `LOG_SUBDIR` constant requiring coordinated update
- `.claude-plugin/marketplace.json`, `sdd/.claude-plugin/plugin.json`, `agent-engineering/.claude-plugin/plugin.json` — version-bump touch points
