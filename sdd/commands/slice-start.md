# Start a Vertical Slice

You are initiating implementation work on a single vertical slice (`SLICE-XXX`) within a feature whose SPEC declares `delivery_mode: per-slice`. This command is one of four cross-cutting slice primitives: `/slice-start`, `/slice-review`, `/slice-retro`, `/slice-commit`. Each is inert outside per-slice mode.

## Active-Slice Resolution Convention (shared across all four `/slice-*` commands)

The four slice commands resolve the active slice via the SAME priority chain — but the *expected status* differs by command intent (per SPEC MODULE-002 active-slice fallback asymmetry):

1. **Explicit `[SLICE-ID]` argument** — if provided, use it. Validate against `^SLICE-\d{3}$` BEFORE interpolating into any path (per REQ-024 path-traversal prevention; see "Slice-ID Validation" below).
2. **IMPLEMENTATION-PLAN's `## Slice Progress` row matching the command's expected status:**
   - `/slice-start` → first row at `Not Started` (you can't start what's already running).
   - `/slice-review` / `/slice-retro` / `/slice-commit` → row at `In Progress` or `Acceptance Check Passing` (you can't review/retro/commit something not yet implemented).
3. **Error** — never silently pick. If priority 2 yields multiple candidates, prompt the user (supervised mode) or halt with an `## Awaiting Slicing Decision`-shaped block (autonomous mode).

## Inert-Mode Gate

This command requires `delivery_mode: per-slice`. **Slice commands are inert in whole-feature mode** (per REQ-007 + EDGE-002). The first action of every `/slice-*` command is to read `delivery_mode:` from the active SPEC's frontmatter and short-circuit when not `per-slice`.

### Step 1: Locate the active SPEC

```bash
ls SDD/requirements/SPEC-*.md
```

- Zero matches → fail with: `No SPEC found in SDD/requirements/. Run /planning-start to create one before invoking /slice-start.`
- One match → use it.
- Multiple matches → ask the user to pick one (supervised mode) or halt with an `## Awaiting Slicing Decision`-shaped block to `SDD/orchestration/progress.md` (autonomous mode).

### Step 2: Read `delivery_mode:` from the SPEC frontmatter

The canonical enum is exactly `{whole-feature, per-slice}` (lowercase, hyphenated). Branch:

- **`per-slice`** → continue with this command's normal behavior (Step 3 onward).
- **`whole-feature` OR field absent** (default per OQ-3 — stay silent on absence) → emit the REQ-007 verbatim inert message and exit cleanly with NO partial state writes:

  ```
  This command requires `delivery_mode: per-slice` in the spec frontmatter. Current spec uses `delivery_mode: <value>`. Run `/implementation-start` instead, or set `delivery_mode: per-slice` in your spec and re-run `/planning-start`.
  ```

  Where `<value>` is either the actual offending value or the literal string `whole-feature (default; field absent)` when the field is missing.

  **Typo-detection hint (resolves L-7):** when emitting the "field absent → default `whole-feature`" branch, ALSO grep the spec frontmatter for any line matching `mode:` (case-insensitive). If a near-miss field is found (e.g., `delvery_mode:`, `Delivery_mode:`, `delivery-mode:`), append a one-line hint to the inert message: `Hint: detected nearby field '<offending-line>' — possible typo of 'delivery_mode:'?`. The hint is informational; the inert message itself is unchanged. Users who genuinely intended `whole-feature` are unaffected.

- **Any other value** (typos like `per_slice`, `PerSlice`, `vertical-thread`, `whole_feature`, `delivry_mode` field-name typos, etc.) → fail per REQ-001 validation: `Invalid delivery_mode value '<value>' in <spec-path>. Allowed values: whole-feature, per-slice. Edit the spec frontmatter and re-run /planning-start (or /implementation-start in whole-feature mode).` Do NOT silently fall through to the default branch.

## Slice-ID Validation (REQ-024 / SEC-003) — canonical regex shared across slice commands

> **Canonical regex (single source of truth — resolves L-4):** the slice-ID validation regex `^SLICE-\d{3}$` is duplicated verbatim in `slice-start.md`, `slice-review.md`, `slice-retro.md`, and `slice-commit.md`. **`slice-start.md` is the canonical home** for this regex; the other three commands SHOULD cross-reference this section rather than re-deriving the pattern. Future changes (e.g., allowing 4-digit slice IDs `SLICE-####`) MUST be coordinated across all four files in a single commit; a drift between the four would produce inconsistent regex enforcement at command boundaries.

Slice-ID arguments MUST be validated against the regex `^SLICE-\d{3}$` BEFORE being interpolated into any read or write path. This prevents directory-traversal attacks (a malicious arg like `../../etc/passwd` would otherwise bypass the path templates).

On regex mismatch, refuse with the REQ-007 message-discipline shape: name the offending value, name the canonical pattern, name the resolution. Example:

```
Invalid SLICE-ID argument '<arg>'. SLICE-ID must match the pattern SLICE-### (three digits). Example: /slice-start SLICE-002.
```

## `## Slice Progress` Table — Binding Schema (REQ-022)

The IMPLEMENTATION-PLAN's `## Slice Progress` table is the source of truth for slice state during implementation. Its schema is BINDING:

- **Columns:** `SLICE-ID | Name | Status | Acceptance check | Test result | Notes`.
- **Status enum (4 states, forward-only — no backwards transitions):** `Not Started`, `In Progress`, `Acceptance Check Passing`, `Complete`.
- **Column-write authority:**
  - `/implementation-start` scaffolds the table (one row per `SLICE-XXX` from the SPEC's `## Delivery Slices` section).
  - `/slice-start` flips `Status` from `Not Started` → `In Progress` for the active slice.
  - `/slice-retro` updates `Status`, `Test result`, and `Notes` only — NEVER `SLICE-ID`, `Name`, or `Acceptance check` (those are SPEC-derived and immutable from this side).
  - `/slice-commit` flips `Status` to `Complete` (terminal state).
- **FIRST-WRITE-WINS rule:** at most ONE slice may be at `Status: In Progress` at any time. Enforced by the EDGE-012 conflict check below.
- **SLICE-XXX uniqueness invariant:** SLICE-XXX values within a single IMPLEMENTATION-PLAN's `## Slice Progress` table MUST be unique; duplicate detection is the human reviewer's responsibility (tooling does not enforce).

## Step 3: Locate the IMPLEMENTATION-PLAN and verify the `## Slice Progress` table

```bash
ls SDD/implementation/IMPLEMENTATION-PLAN-*.md
```

Read the matching IMPLEMENTATION-PLAN. Verify it contains a `## Slice Progress` section. If MISSING, halt per FAIL-007 with:

```
No '## Slice Progress' table found in <IMPLEMENTATION-PLAN-XXX-...md>. Either run /implementation-start to scaffold the table, or restore the table from a previous git commit. /slice-start cannot proceed without the table.
```

No partial state writes; no fall-through to "first Not Started row" search on missing data.

## Step 4: Resolve the active SLICE-XXX

Apply the **Active-Slice Resolution Convention** above. For `/slice-start`, the expected status is `Not Started`.

- **`[SLICE-ID]` provided:** use it (after regex validation). Verify the SLICE-XXX row exists in `## Slice Progress`; if missing, fail with: `SLICE-XXX not found in <IMPLEMENTATION-PLAN-XXX-...md>'s ## Slice Progress table. Available slice IDs: <list>. Either correct the argument or update the SPEC's ## Delivery Slices section and re-run /implementation-start.`
- **No argument, single `Not Started` row:** use it.
- **No argument, multiple `Not Started` rows (EDGE-010):** prompt the user listing all `Not Started` SLICE-IDs and Names. Do NOT silently pick the first. In autonomous mode, halt with an `## Awaiting Slicing Decision`-shaped block to `SDD/orchestration/progress.md` listing the candidates.
- **No argument, zero `Not Started` rows:** if all slices are `Complete`, fail with: `All slices in <IMPLEMENTATION-PLAN-XXX-...md> are already Complete. Nothing to start. To re-start a Complete slice, pass --force SLICE-XXX explicitly.` If any are `In Progress` / `Acceptance Check Passing`, fall through to the EDGE-012 conflict check.

## Step 5: EDGE-012 conflict — another slice is `In Progress` (or `Acceptance Check Passing`)

If ANY row in `## Slice Progress` is at `In Progress` OR `Acceptance Check Passing` and is NOT the row the user is trying to start, refuse with the friendly message naming the in-progress slice (per EDGE-012 spec text):

```
Cannot start <requested SLICE-XXX>: <other SLICE-XXX> is currently <state>. Resume the in-progress slice first (see /slice-review, /slice-retro, /slice-commit), or mark it abandoned by manually editing the Slice Progress row to a terminal state. Use /slice-start --resume <other SLICE-XXX> to re-attach to the in-progress slice if context was lost.
```

The command does NOT regress the in-progress slice's state, does NOT silently switch active slice, and does NOT overwrite either row's transition timestamp. The forward-only invariant in REQ-022 holds at the command boundary.

**`--resume SLICE-XXX` exception:** if the user explicitly passed `--resume SLICE-XXX` and that SLICE-XXX is the row currently at `In Progress`, skip the EDGE-012 refusal and proceed to Step 7 (re-attach without state regression). See "Flag Inventory" below.

## Step 6: EDGE-013 conflict — slice is already `Complete`

If the requested SLICE-XXX row is at `Status: Complete`, the default response is REFUSE. Re-starting a `Complete` slice would overwrite acceptance-check evidence on the row and create ambiguity in the ledger.

- **Without `--force`:**
  - **Supervised mode:** warn the user with: `SLICE-XXX is already Complete. Re-starting would overwrite Status/Test result/Notes columns (the RETROSPECTIVE-SLICE file and ledger entries are NOT deleted, but a re-start note will be appended to the ledger). Re-start anyway? [y/N]` — affirmative response is `--force`-equivalent.
  - **Autonomous mode:** there is no user to prompt; refuse with-halt — emit an `## Awaiting Re-start Decision` block to `SDD/orchestration/progress.md` per the REQ-011 halt-shape pattern (mirrors `## Awaiting Clarification` / `## Awaiting Slicing Decision`). The user resumes by re-invoking with `/slice-start SLICE-XXX --force` (or by manually editing the slice row to a non-`Complete` state, with the understanding that doing so leaves a `git log` paper trail). Interactive confirmation is supervised-mode-only; `--force` is the universal flag-equivalent.
- **With `--force` (or affirmative supervised confirmation):** proceed. Reset only `Status`/`Test result`/`Notes` columns to `In Progress` / `—` / `Re-started YYYY-MM-DD; previous retro at <path>`. Do NOT delete the pre-existing `RETROSPECTIVE-SLICE-XXX-...md` file. Do NOT erase ledger entries. Append a ledger note recording the re-start with timestamp under the `Open recommendations awaiting user decision` section.

## Step 7: Load the rolling ledger (audit-trail-only context propagation per OQ-6)

```bash
ls SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md
```

(Where `[feature-name]` is the kebab-case slug derived from the SPEC filename — e.g., `LEARNINGS-FEATURE-vertical-slicing-step-c.md`. Resolved per CLARIFICATION OQ-B.)

If present, read it into context. The ledger is the ONLY propagated context for slice work (per OQ-6 — strictly the ledger). Subagents that need an audit trail can read individual `RETROSPECTIVE-SLICE-XXX-...md` files from disk on demand, but the prompt path is the ledger only.

If the ledger does not yet exist (this is the first slice of the feature), continue without loading — `/slice-retro` will create it after this slice's retrospective.

## Step 8: Update the `## Slice Progress` table — flip Status to `In Progress`

Edit the IMPLEMENTATION-PLAN in place:

- Locate the row for the active SLICE-XXX.
- Change `Status` from `Not Started` (or `Complete` if `--force` was used) → `In Progress`.
- Leave `SLICE-ID`, `Name`, `Acceptance check` UNCHANGED (column-write authority — see schema above).
- Reset `Test result` to `—` and `Notes` to `Started YYYY-MM-DD` (or `Re-started YYYY-MM-DD; previous retro at <path>` under `--force`).

## Step 9: Update `progress.md`

Append an entry to `SDD/orchestration/progress.md` recording the slice start:

```markdown
## Slice <SLICE-XXX> - In Progress

- **Started:** YYYY-MM-DD HH:MM:SS
- **SPEC:** SPEC-XXX-<feature-name>
- **IMPLEMENTATION-PLAN:** SDD/implementation/IMPLEMENTATION-PLAN-XXX-<feature-name>-<date>.md
- **Ledger loaded:** Yes / No (first slice)
- **Flags:** <list of flags used, or "none">
- **Active-slice resolution:** <how the slice was resolved — explicit arg / single Not Started row / user prompt / --resume / --force>
```

## Step 10: Hand off to implementation

Output a friendly message to the user describing:

- The active SLICE-XXX, its Name, and its Acceptance check (verbatim from the row).
- The `Modules touched` field from the SPEC's `### SLICE-XXX:` block (read SPEC's `## Delivery Slices` section).
- The ledger summary (if loaded): one line per ledger section (`Interface contract clarifications`, `Integration patterns discovered`, `Performance / failure modes observed`, `Open recommendations awaiting user decision`) with entry counts.
- The next expected command: `/slice-review SLICE-XXX` (after implementation + tests are written).

The user (or a slice subagent in `/sdd-flow` per-slice mode) now implements the slice. Implementation work happens between `/slice-start` and `/slice-review` — there is no other slice command in this gap.

## Flag Inventory (REQ-025 — applies to `/slice-start`)

This command introduces TWO flags. The flag conventions are binding for downstream slice commands.

| Flag | Semantics | Default (without flag) | Supervised mode | Autonomous mode |
|------|-----------|------------------------|-----------------|-----------------|
| `--resume SLICE-XXX` | Re-attach to an `In Progress` slice if context was lost. Does NOT regress state, does NOT switch active slice. | EDGE-012 refusal fires when a slice is already `In Progress`. | User runs `/slice-start --resume SLICE-X` explicitly. | Orchestrator emits the flag in resume invocations after a context loss; same semantics. |
| `--force SLICE-XXX` | Destructive override for re-starting a `Complete` slice. Resets `Status`/`Test result`/`Notes` only; pre-existing `RETROSPECTIVE-SLICE` file and ledger entries are NOT deleted; a ledger note records the re-start with timestamp. | EDGE-013 refusal fires (default = REFUSE). | User passes `--force` OR confirms an interactive `y/N` prompt affirmatively (the prompt is `--force`-equivalent). | Absence of `--force` is refusal-with-halt: orchestrator emits an `## Awaiting Re-start Decision` block to `progress.md` per the REQ-011 halt-shape pattern. Interactive confirmation is supervised-mode-only. |

**Convention boundaries:**

- Every `--<flag>` is a literal CLI argument; absence is the default behavior; supervised-mode interactive prompts are flag-equivalent decisions; autonomous mode without the flag halts via the documented awaiting-decision-block pattern (REQ-011 halt shape).
- `--force` adopts the destructive-action override convention going forward (mirrors common Unix tooling: `git push --force`, `rm --force`). Future destructive overrides in the SDD plugin SHOULD use `--force` rather than ad-hoc names.
- The `/sdd-flow continue` flags `--replan`, `--from-slice SLICE-XXX`, and `--override-replan` are NOT slice-command flags — they belong to the orchestrator and are documented in `/slice-retro` (since retrospectives can recommend re-planning) and in the `sdd-flow` skill.

## Path Conventions (REQ-016)

This command emits paths under the SDD 2.0.0 layout for future runs:

- `SDD/requirements/SPEC-XXX-[feature-name].md`
- `SDD/implementation/IMPLEMENTATION-PLAN-XXX-[feature-name]-[date].md`
- `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` (kebab-case feature-name slug per CLARIFICATION OQ-B; uniform with REQ-003, REQ-005, REQ-016, MODULE-007, EDGE-007, FAIL-003)
- `SDD/orchestration/progress.md`

## Refusal-Message Discipline (REQ-007 / UX-001)

Every refusal path in this command follows the REQ-007 message-discipline standard:

1. Name the detected condition (e.g., "another slice is In Progress", "SLICE-XXX is already Complete", "no Slice Progress table").
2. Name the resolution path (`--resume`, `--force`, `/implementation-start`, manual edit).
3. Exit cleanly without partial state writes.

The friendly-message tone matches the existing SDD plugin convention (no cryptic stacktraces; no silent fallthroughs; no surprise behavior).
