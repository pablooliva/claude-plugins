# Retrospective for a Vertical Slice

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow’s flat-orchestration contract forbids it; all work happens inline in your own context.

You are running the per-slice retrospective for a single `SLICE-XXX` within a feature whose SPEC declares `delivery_mode: per-slice`. This body writes TWO artifacts in a strict order (per OQ-E conservative default — FIRST-WRITE-WINS): the immutable `RETROSPECTIVE-SLICE-XXX-...md` audit trail FIRST, then the rolling `LEARNINGS-FEATURE-[feature-name].md` ledger update SECOND.

## Active-Slice Resolution Convention (shared with slice-start, slice-review, slice-commit)

Per SPEC MODULE-002 active-slice fallback asymmetry:

1. **Explicit `[SLICE-ID]` argument** — if provided, use it. Validate against `^SLICE-\d{3}$` BEFORE interpolating into any path (REQ-024 / SEC-003 path-traversal prevention).
2. **IMPLEMENTATION-PLAN's `## Slice Progress` row** at `In Progress` or `Acceptance Check Passing` — the retrospective body retrospects implemented + reviewed code.
3. **Error** — never silently pick.

## Inert-Mode Gate

This body requires `delivery_mode: per-slice`. **Slice operations are inert in whole-feature mode** (per REQ-007 + EDGE-002).

### Step 1: Locate the active SPEC

```bash
ls SDD/requirements/SPEC-*.md
```

Single match → use it. Multiple → append `## Awaiting SPEC Selection` to `SDD/orchestration/progress.md` listing the found paths, then return. Zero → fail with: `No SPEC found in SDD/requirements/. A planning phase must be run to create one before invoking a slice retrospective.`

### Step 2: Read `delivery_mode:` from the SPEC frontmatter

The canonical enum is exactly `{whole-feature, per-slice}` (lowercase, hyphenated). Branch:

- **`per-slice`** → continue.
- **`whole-feature` OR field absent** → emit the REQ-007 verbatim inert message and exit cleanly with NO partial state writes:

  ```
  This retrospective body requires `delivery_mode: per-slice` in the spec frontmatter. Current spec uses `delivery_mode: <value>`. Run an implementation-start phase instead, or set `delivery_mode: per-slice` in your spec and re-run planning-start.
  ```

- **Any other value** → fail per REQ-001 validation: `Invalid delivery_mode value '<value>' in <spec-path>. Allowed values: whole-feature, per-slice. Edit the spec frontmatter and re-run planning-start.`

## Slice-ID Validation (REQ-024 / SEC-003)

Slice-ID arguments MUST be validated against the regex `^SLICE-\d{3}$` BEFORE being interpolated into any read or write path. On regex mismatch, refuse with the REQ-007 message-discipline shape: `Invalid SLICE-ID argument '<arg>'. SLICE-ID must match the pattern SLICE-### (three digits).`

> **Canonical regex source (resolves L-4):** the canonical home for this regex is the slice-start body's "Slice-ID Validation" section. Any future change (e.g., 4-digit slice IDs) MUST be coordinated across slice-start, slice-review, slice-retro, and slice-commit bodies in a single commit.

## Step 3: Resolve the active SLICE-XXX

Apply the **Active-Slice Resolution Convention** above. Expected statuses for a slice retrospective: `In Progress` or `Acceptance Check Passing`.

- **`[SLICE-ID]` provided:** verify the row exists; if at `Not Started`, fail with: `SLICE-XXX has not been started. Run slice-start SLICE-XXX first.` If at `Complete`, fall through to the EDGE-014 re-invocation refusal (Step 5 below).
- **No argument, single matching row:** use it.
- **No argument, multiple matching rows:** append `## Awaiting Slice Selection` to `SDD/orchestration/progress.md` listing the candidate rows, then return.
- **No argument, zero matching rows:** fail with: `No slice currently In Progress or Acceptance Check Passing in <IMPLEMENTATION-PLAN-XXX-...md>.`

## Step 4: Verify the per-slice review was run for this slice

The retrospective requires the per-slice review as input. Verify:

```bash
ls SDD/reviews/REVIEW-SLICE-<SLICE-XXX>-*.md
```

If absent, fail with: `No per-slice review found for SLICE-XXX (expected SDD/reviews/REVIEW-SLICE-<SLICE-XXX>-<feature-name>-<YYYY-MM-DD>.md). Run the slice-review body for SLICE-XXX before the slice retrospective.`

If present, read it into context. Note its findings (HIGH/MEDIUM/LOW counts and any unresolved items).

## Step 5: EDGE-014 — re-invocation refusal when retrospective already exists

Check for an existing retrospective at the canonical path:

```bash
ls SDD/implementation/slices/RETROSPECTIVE-SLICE-<SLICE-XXX>-*.md
```

If a retrospective for this slice already exists, refuse loudly per REQ-005's re-invocation policy:

```
Retrospective for SLICE-XXX already exists at <path>. Retrospectives are an audit trail and a second-write must be deliberate. Pass the `--reconcile-ledger` flag to refresh the ledger from the existing retro; otherwise the audit trail is final.
```

The user's documented escape hatches:
- **(a)** Pass `--reconcile-ledger SLICE-XXX` — refresh the ledger from the existing retro (per EDGE-007 / FAIL-003; see "Reconcile Mode" below).
- **(b)** Manually delete the existing retro before re-running (deliberate, leaves a paper trail in `git log`).

The default-write-second-retro path is REJECTED — the audit-trail invariant outweighs the convenience of dated re-writes.

If `--reconcile-ledger` IS passed, skip the retro write entirely and jump to "Reconcile Mode" (`--reconcile-ledger` algorithm) below.

## Step 6: Write the RETROSPECTIVE artifact FIRST (audit trail)

Write to:

```
SDD/implementation/slices/RETROSPECTIVE-SLICE-<SLICE-XXX>-<feature-name>-<YYYY-MM-DD>.md
```

Note the **hyphenated date format** `[YYYY-MM-DD]` (uniform across new artifact families). The retrospective is **immutable after writing** — never modified by this or any other body.

### Retrospective body structure (per OQ-4 hybrid — structured + free-form)

```markdown
# Retrospective: SLICE-<XXX> — [slice name]

**Slice:** SLICE-XXX
**Feature:** [feature-name]
**SPEC:** SDD/requirements/SPEC-XXX-[feature-name].md
**IMPLEMENTATION-PLAN:** SDD/implementation/IMPLEMENTATION-PLAN-XXX-[feature-name]-[date].md
**Per-slice review:** SDD/reviews/REVIEW-SLICE-XXX-[feature-name]-[YYYY-MM-DD].md
**Date:** YYYY-MM-DD

## What Was Learned

[Free-form prose narrative — insights from implementing this slice that don't fit a structured template. Surface integration patterns discovered, performance characteristics observed, failure modes encountered, interface contract clarifications, anything that informs future slices in this feature or future features. The narrative is the retro's primary deliverable for human readers.]

## Recommended SPEC Amendments

[Structured. Each entry follows this template. If no amendments are recommended, state "None." explicitly — do NOT omit the section.]

### Amendment 1: <short label>

- **Affects:** <SLICE-XXX | MODULE-XXX | REQ-XXX | EDGE-XXX | FAIL-XXX>
- **SPEC currently says:** <verbatim quote or paraphrase, with section/line reference>
- **Should change to:** <proposed wording>
- **Why:** <observation that grounds the change — what was learned that the SPEC didn't anticipate>

### Amendment 2: <short label>

(... same shape ...)

## Recommended Re-planning

[Structured, REQUIRED, ELEVATED severity. Each entry follows the same template as SPEC Amendments but signals a fundamental plan-level failure rather than a local clarification. If no re-planning is recommended, the section body MUST be the single line `None.` — do NOT omit the section. **One or more entries HALT the flow** even under `--skip-slice-checkpoints` per REQ-014; a `None.` body does not — see "Three-Tier Recommendation Surfacing" below.]

### Re-plan trigger 1: <short label>

- **Affects:** <plan-level scope — usually multiple SLICEs or a foundational MODULE-XXX>
- **Plan currently says:** <verbatim or paraphrase>
- **Should change to:** <proposed re-plan direction>
- **Why:** <observation grounding plan-level invalidation — typically: a foundational assumption broken, an interface contract that ripples through later slices, a discovered constraint that invalidates the slice ordering>

## Ledger Update Sections (structured)

[The retrospective records the ledger updates this retro will write into LEARNINGS-FEATURE-[feature-name].md. The ledger sections are:]

### Interface contract clarifications

- <entry>

### Integration patterns discovered

- <entry>

### Performance / failure modes observed

- <entry>

### Open recommendations awaiting user decision

- <entry>
```

### CRITICAL: Recommendation header strings (Chunk 4b matcher contract)

The retrospective MUST emit these EXACT header strings when learnings warrant SPEC amendments OR re-planning:

- `## Recommended SPEC Amendments`
- `## Recommended Re-planning`

These header strings are the **matcher contract** for the flow orchestrator's Step 4b/4c orchestration logic. Any deviation (e.g., `## Recommended Spec Amendments`, `## Spec Amendments`, `## Re-planning Recommended`) breaks the matcher and the orchestrator will fail to surface the recommendations correctly.

BOTH sections are **REQUIRED** in every retrospective, whether or not there is anything to recommend. When there is nothing to recommend, the section body is the exact single line:

```
None.
```

Accepted spellings for the no-op body: `None.` or `None`, any case. Nothing else — not "N/A", not "No amendments needed", not a sentence beginning with "None" followed by justification on the same line. The orchestrator's Stage-1 matcher tests this one string; free prose in the body reads as a live recommendation and will halt the flow. Put any rationale on a LATER line if you want it recorded.

Omitting either section is a **malformed retro** — the orchestrator cannot distinguish "no recommendation" from "the subagent forgot the section", so it treats absence as malformed rather than as a "no".

## Three-Tier Recommendation Surfacing (REQ-014 reference)

Retrospectives can raise recommendations at three escalating tiers (per REQ-014 three-tier model):

1. **Normal recommendation** — structured `## Recommended SPEC Amendments` entries (slice-bounded; user reviews at next slice-boundary pause OR at the consolidated announcement under `--skip-slice-checkpoints`; **no halt**).
2. **Iteration-cap-exhaustion** — per-slice review-fix-rerun loop fails to reduce HIGH findings across the cap (REQ-013); halts the slice's iteration loop, routes findings to ledger's `Open recommendations awaiting user decision` section; in `--skip-slice-checkpoints` mode halts the whole flow.
3. **Re-planning recommendation** — `## Recommended Re-planning` (this retro section) with a **non-`None.` body**; **halts the flow even under `--skip-slice-checkpoints`** (mirrors Step 3c panel-review halt). The section with a `None.` body is the required no-re-plan shape and does not halt.

Each tier has its own surfacing mechanism. Implementations SHOULD treat the three as distinct user-decision points; UI/CLI surfaces SHOULD label them by tier so users grasp the severity at a glance.

## Step 7: Update the rolling ledger (in-place; consolidate, refine, supersede — do not just append)

After the retrospective artifact is durable on disk, update:

```
SDD/implementation/slices/LEARNINGS-FEATURE-<feature-name>.md
```

(Where `[feature-name]` is the kebab-case slug derived from the SPEC filename per CLARIFICATION OQ-B — uniform across REQ-003, REQ-005, REQ-016, MODULE-007, EDGE-007, FAIL-003.)

If the ledger does not yet exist, scaffold it with this initial structure:

```markdown
# Rolling Ledger: <feature-name>

**Feature:** <feature-name>
**SPEC:** SDD/requirements/SPEC-XXX-<feature-name>.md
**Last updated:** YYYY-MM-DD by SLICE-XXX

> The rolling ledger consolidates learnings across all slices of this feature. It is the ONLY context propagated to subsequent slice subagents (per OQ-6 — strictly the ledger). Subagents that need an audit trail can read individual `RETROSPECTIVE-SLICE-XXX-...md` files from disk on demand. The ledger is updated in-place after each retrospective: consolidate, refine, supersede — do not just append.
>
> **`Sources:` field convention (REQ-025a; resolves M-4 reconcile-ledger orphan-vs-consolidated ambiguity):** every entry below MUST carry a `Sources:` field listing each contributing SLICE-XXX. Consolidated entries list every retro that contributed (e.g., `Sources: SLICE-001, SLICE-003`). User-authored manual entries (no retro source) carry NO `Sources:` field — that absence is the explicit signal `--reconcile-ledger` uses to flag them as orphans.

## Interface contract clarifications

(Per-slice entries; each entry carries a `Sources:` field listing every contributing SLICE-XXX.)

- <example entry text> (Sources: SLICE-001)

## Integration patterns discovered

- <example entry text> (Sources: SLICE-001, SLICE-002)

## Performance / failure modes observed

## Open recommendations awaiting user decision

(Iteration-cap exhaustions, deferred SPEC amendments, anything blocked.)
```

If the ledger exists, **consolidate** the new retrospective's ledger-update entries with the existing entries on the same topic — do NOT blind-append. The ledger's purpose is to consolidate and supersede; adding redundant or contradictory entries defeats that purpose. Sample consolidation rules:

- If a new entry says the SAME thing as an existing entry, do nothing (or merge citations: "originally captured in SLICE-001 retro; reaffirmed by SLICE-002").
- If a new entry REFINES an existing entry (more specific, narrower scope, additional caveat), update the existing entry in place and cite both retros.
- If a new entry SUPERSEDES an existing entry (contradicts it, but the new observation is more authoritative), replace the existing entry and add a note "superseded by SLICE-XXX retro; original observation preserved at retro path".
- If the new entry is genuinely novel, append it under the appropriate section.

### `Sources:` field convention (resolves M-4)

Every ledger entry — whether freshly appended or consolidated from multiple retros — MUST carry a `Sources:` field listing each contributing retro by SLICE-ID. This is the durable marker that `--reconcile-ledger` uses to determine "covered" without literal-text matching.

Entry shape:

```markdown
- **<entry text>**
  - Sources: SLICE-001, SLICE-003
```

Or inline:

```markdown
- <entry text> (Sources: SLICE-001, SLICE-003)
```

When Step 7 consolidation rewrites an existing entry to fold in a new retro's contribution, the `Sources:` list MUST be updated to include the new SLICE-XXX. When Step 7 supersedes an entry, the new entry's `Sources:` lists the retro that produced the supersession (and may optionally cite the prior retro in a "supersedes:" sub-line for audit trail).

User-edited entries that were authored manually (no retro source) carry no `Sources:` field — that is the explicit signal `--reconcile-ledger` uses to flag orphans (per Step 5 of the algorithm, see `--reconcile-ledger` Mode below).

## Step 8: Update the `## Slice Progress` table (per REQ-022 column-write authority)

This body updates `Status`, `Test result`, and `Notes` columns ONLY — never `SLICE-ID`, `Name`, or `Acceptance check`.

- **Status:** advance per the forward-only state machine. Typical transition: `In Progress` → `Acceptance Check Passing` (when the acceptance check has been run and passes; the row will go to `Complete` after the slice-commit body runs).
  - In sdd-flow per-slice mode, the orchestrator may set `Status: Complete` directly here if the retro+ledger writes are durable AND the commit will follow as part of the same orchestration step. This body documents both transitions; the orchestrator picks the appropriate one.
- **Test result:** free-form text — `passing`, `failing: <test name> + <reason>`, `n/a (manual)`, etc.
- **Notes:** brief pointer — `see retro at SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-<feature-name>-<YYYY-MM-DD>.md` or `see ledger §Open recommendations` for blocking issues.

State transitions are forward-only (no backwards transitions encoded in the column; "stuck" surfaces via the ledger's `Open recommendations` section, not the column). SLICE-ID, Name, and Acceptance check are SPEC-derived and immutable from this side.

## Step 9: Update `progress.md`

Append an entry to `SDD/orchestration/progress.md` recording the retrospective:

```markdown
## Slice <SLICE-XXX> - Retrospective Complete

- **Date:** YYYY-MM-DD
- **Retrospective:** SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-<feature-name>-<YYYY-MM-DD>.md
- **Ledger updated:** SDD/implementation/slices/LEARNINGS-FEATURE-<feature-name>.md
- **Recommendations raised:** <count of SPEC Amendments> SPEC amendment(s); <count of Re-planning entries> re-planning entr(y/ies)
- **Slice Progress Status advanced to:** <Acceptance Check Passing | Complete>
```

### Two-stage matcher contract — what this body does NOT write

This body writes only the `## Slice <SLICE-XXX> - Retrospective Complete` log entry above. It DOES NOT write a `## Awaiting Re-planning Decision` halt block to `progress.md` — that block is the **orchestrator's** responsibility (per `agent-engineering/skills/sdd-flow/SKILL.md` per-slice cycle Step 4c.5).

The contract is two-stage by design (resolves M-2):

1. **Retro stage (this body):** the retrospective ARTIFACT always contains the EXACT header `## Recommended Re-planning` (per Step 6 + the matcher-contract block above); its BODY carries the answer — entries when the slice's learnings warrant a re-plan, `None.` when they do not. The retro ARTIFACT (not this body's return summary) is the SOURCE OF TRUTH for the recommendation. This body does NOT itself touch any halt-shaped block in `progress.md`.
2. **Orchestrator stage (flow Step 4c.5):** after this body returns, the orchestrator reads the just-written retrospective and matches `^## Recommended Re-planning$` **AND** a first non-empty body line that is not `None.` (it never keys off this body's return summary). On match, the ORCHESTRATOR (not this body) writes the `## Awaiting Re-planning Decision` halt block to `progress.md` and halts the per-slice cycle. On a fresh-session resume, Phase Detection reads `progress.md` for `## Awaiting Re-planning Decision` (the progress-block name) and re-prompts the user.

This separates the two strings unambiguously:
- `## Recommended Re-planning` lives ONLY in the retrospective artifact (`SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-...md`).
- `## Awaiting Re-planning Decision` lives ONLY in `progress.md` and is written by the orchestrator (never by this body).

If this body is invoked outside the flow orchestrator and the retro contains `## Recommended Re-planning` entries, the user is responsible for either invoking the orchestrator's continue/resume step (which detects the recommendation via the matcher) or manually consulting the retro's recommendations. This body does not halt or write any halt-shaped block; it only records the retrospective and updates the ledger.

### Bounded return — what to report about the two recommendation sections

Your return MUST state the absolute path of the retrospective you wrote, and MUST quote the first non-empty body line of `## Recommended SPEC Amendments` and of `## Recommended Re-planning` **verbatim, re-read from the file you just wrote** — not from memory of what you intended to write.

Do NOT assert that you did or did not emit a section. Self-reports of that shape have been observed to contradict the artifact on disk. The orchestrator matches the file regardless; a return that contradicts it only creates a discrepancy the orchestrator must reconcile.

## `--reconcile-ledger` Mode (REQ-025a — full 8-step algorithm)

When `--reconcile-ledger` is passed, this body does NOT write a new retrospective. Instead, it rebuilds `LEARNINGS-FEATURE-[feature-name].md` from the on-disk retrospectives.

**Use cases (per EDGE-007 / FAIL-003):**

- A previous retro invocation wrote the retrospective but the ledger update failed (disk full, process killed mid-write). The ledger is out of sync with the retros on disk.
- The user manually edited the ledger and wants to re-derive it from the canonical retros.
- A retrospective was deleted and re-created (rare; intentional — the user's audit-trail decision).

### Algorithm

The classifier MUST use the durable `Sources:` field convention introduced in Step 7 above (resolves M-4) — NOT literal-text matching. The `Sources:` field on each ledger entry lists which retros contributed; the reconcile checks whether each retro is in some ledger entry's Sources list.

1. **Read all retros for the active feature:** `ls SDD/implementation/slices/RETROSPECTIVE-SLICE-*-<feature-name>-*.md`. Sort by SLICE-XXX number (lexicographic on the SLICE-ID is correct given the zero-padded `\d{3}` format).
2. **Read the current ledger:** `SDD/implementation/slices/LEARNINGS-FEATURE-<feature-name>.md`. If absent, treat as empty (the rebuild will scaffold it).
3. **For each retrospective (in order),** determine "covered" by reading every ledger entry's `Sources:` field. A retro is COVERED if its `SLICE-XXX` ID appears in at least one ledger entry's `Sources:` list. A retro is NOT covered if its SLICE-XXX is absent from every `Sources:` list — this means its learnings have not yet been incorporated. The classifier does NOT compare retro text to ledger text; consolidation under Step 7 may have rewritten the wording away from the retro's literal text, but the `Sources:` field is the authoritative marker.
4. **If a retro is NOT covered,** append its ledger-update entries to the appropriate ledger sections — consolidating with existing entries on the same topic, not blind-appending. Use the consolidation rules in Step 7 above. Each newly-appended or newly-consolidated entry MUST carry a `Sources:` field listing the retro's SLICE-XXX (plus any prior contributors if consolidating).
5. **Ledger entries with no `Sources:` field** are user-authored manual entries. They are PRESERVED — the ledger is not destroyed. Such entries are flagged in the rebuild output as `> orphan entry — no Sources field; review (was this intentionally hand-authored, or did Sources tracking drop?)` so the user can decide. Note: this is **distinct from "consolidated entry"** — consolidated entries carry one or more SLICE-XXX values in `Sources:` and are NOT flagged as orphans. The `Sources:` field convention IS the disambiguator.
6. **Mark the ledger header** with a `<!-- reconciled at YYYY-MM-DD -->` HTML comment timestamp (visible in source, invisible in rendered markdown).
7. **Detect conflicts** (e.g., contradictory learnings between two retros, or between retros and existing ledger entries) and surface them rather than auto-resolving. List conflicts in the reconcile output; the user resolves manually after the reconcile (with the rebuild as a starting point). Conflict detection is heuristic; if a true semantic conflict cannot be cleanly classified, surface as `> may be conflict OR refinement; review` rather than asserting binary classification.
8. **Proceed autonomously:** since this body runs as a subagent, write proceeds without diff-confirmation. The change is logged to `SDD/orchestration/progress.md` with the reconcile diff captured under a `## Reconcile Ledger Action` block. Include in the bounded return: a summary of what was added, what was preserved as orphan, and what conflicts were surfaced.

**Backward-compatibility note for ledgers predating the `Sources:` convention:** older ledgers may have entries lacking `Sources:` fields that ARE in fact retro-derived (just from before the convention was adopted). On the first reconcile run after upgrading, expect some false-orphans. The user can either (a) add `Sources:` fields manually based on inspection, or (b) accept the false-orphan flag and let the reconcile append fresh entries from the retros (which will carry `Sources:` fields going forward; duplicates can be cleaned up at the user's discretion).

### Scope

The reconcile uses the FULL retro corpus for the active feature, NOT just the named slice. The named SLICE-XXX argument scopes only the existence-check at REQ-005's re-invocation refusal (so users can target the reconcile to a specific slice's retro for diagnostic purposes); the rebuild uses every retro on disk.

**Audit-trail invariant:** retros remain authoritative; the ledger is derived. The reconcile algorithm respects this by treating retros as immutable inputs and the ledger as the rebuilt output.

## Flag Inventory (REQ-025)

This body recognizes ONE flag.

| Flag | Semantics | Default (without flag) | Supervised flow | Autonomous flow |
|------|-----------|------------------------|-----------------|-----------------|
| `--reconcile-ledger SLICE-XXX` | Re-reads every `RETROSPECTIVE-SLICE-XXX-...md` for the active feature; rebuilds `LEARNINGS-FEATURE-[feature-name].md` per the 8-step algorithm above. | Writes a new retro + updates ledger (or refuses per EDGE-014 if a retro already exists). | The orchestrator passes the flag only on an explicit user recovery directive; produce a diff between pre- and post-reconcile ledger and surface it via your bounded return so the user can confirm at the next checkpoint. | Same algorithm; the diff-confirm step degrades to "write without prompt" but the change is logged to `progress.md`. |

The `--reconcile-` prefix is the convention for "reconstruct derived state from authoritative sources" (the retros are authoritative; the ledger is derived). Future flags following the same pattern (`--reconcile-progress`, `--reconcile-counters`) inherit this convention.

## Boundary with orchestrator resume flags (REQ-025)

The flags `--replan`, `--from-slice SLICE-XXX`, and `--override-replan` are **NOT** slice-body flags — they belong to the orchestrator's continue/resume step. Documented here because retrospectives can recommend re-planning (the `## Recommended Re-planning` section), and the user's resume options after such a recommendation are these orchestrator flags.

| Flag | Step | Semantics | Default | Notes |
|------|------|-----------|---------|-------|
| `--replan` | orchestrator continue | Re-runs the planning phase with the ledger and triggering retro in scope; resumes implementation from SLICE-001. | Without `--replan`, the orchestrator's continue step proceeds along the existing flow. | Triggered by `## Recommended Re-planning` retro recommendations. |
| `--from-slice SLICE-XXX` | orchestrator continue (only meaningful with `--replan`) | Resume implementation from the named slice after the re-plan completes. | Without the flag, re-plan resumes from `SLICE-001`. | **Validation:** `--from-slice` value MUST match `^SLICE-\d{3}$` AND MUST reference an existing SLICE-XXX in the IMPLEMENTATION-PLAN's `## Slice Progress` table. Invalid value (regex mismatch or unknown slice) refuses with the REQ-007 message-discipline shape. |
| `--override-replan` | orchestrator continue | Continues with the current plan despite a `## Recommended Re-planning` recommendation. Documented but discouraged. | Without the flag, a non-`None.` `## Recommended Re-planning` halts the flow per REQ-014 (even under `--skip-slice-checkpoints`). | The orchestrator does NOT silently emit `--override-replan`; in autonomous mode the halt fires per REQ-014. |

**Combination semantics for the orchestrator's continue step:**

- `--replan` alone — re-runs the planning phase with retro context, resumes from SLICE-001.
- `--replan --from-slice SLICE-XXX` — re-runs planning, resumes from `SLICE-XXX` after re-plan.
- `--override-replan` alone — continues without re-plan.
- `--from-slice SLICE-XXX` without `--replan` — INVALID. Refuses with: `--from-slice requires --replan; running --replan --from-slice <id> is the documented combination.`
- `--replan --override-replan` — INVALID (mutually exclusive intents). Refuses with: `--replan and --override-replan are mutually exclusive; pick one.`

## Path Conventions (REQ-016)

This body emits paths under the SDD 2.0.0 layout:

- `SDD/requirements/SPEC-XXX-[feature-name].md`
- `SDD/implementation/IMPLEMENTATION-PLAN-XXX-[feature-name]-[date].md`
- `SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-[feature-name]-[YYYY-MM-DD].md`
- `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` (kebab-case feature-name slug per CLARIFICATION OQ-B)
- `SDD/reviews/REVIEW-SLICE-XXX-[feature-name]-[YYYY-MM-DD].md`
- `SDD/orchestration/progress.md`

## Refusal-Message Discipline (REQ-007 / UX-001)

Every refusal path follows the REQ-007 message-discipline standard: name the detected condition, name the resolution path, exit cleanly without partial state writes.

## Two-Write Ordering Invariant (per OQ-E + EDGE-007 / FAIL-003)

The ordering is **STRICT and BINDING**:

1. **First:** write the immutable `RETROSPECTIVE-SLICE-XXX-...md` audit-trail file.
2. **Then:** update the in-place `LEARNINGS-FEATURE-[feature-name].md` ledger.

This is FIRST-WRITE-WINS: if the second write fails (disk full, process killed, etc.), the next retro invocation (or explicit `--reconcile-ledger`) detects "ledger missing entries from existing retros" and reconciles. The retro file existing without the ledger update is a recoverable state; the inverse (ledger updated but retro missing) is NOT recoverable without re-running the entire retrospective. The ordering eliminates the unrecoverable inverse case.
