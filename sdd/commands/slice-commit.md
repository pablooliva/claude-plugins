# Commit a Vertical Slice

You are creating an atomic per-slice git commit for a single `SLICE-XXX` within a feature whose SPEC declares `delivery_mode: per-slice`. This command produces ONE commit covering: slice code + tests + per-slice review doc + fix-findings notes + retrospective + ledger update. Per OQ-C conservative default — **looser staging:** trusts the user to manage staging; produces a structured commit message; does NOT enforce that the working tree contains only slice-scoped files.

## Active-Slice Resolution Convention (shared with `/slice-start`, `/slice-review`, `/slice-retro`)

Per SPEC MODULE-002 active-slice fallback asymmetry:

1. **Explicit `[SLICE-ID]` argument** — if provided, use it. Validate against `^SLICE-\d{3}$` BEFORE interpolating into any path (REQ-024 / SEC-003 path-traversal prevention).
2. **IMPLEMENTATION-PLAN's `## Slice Progress` row** at `In Progress` or `Acceptance Check Passing` — `/slice-commit` commits implemented + reviewed + retrospected code.
3. **Error** — never silently pick.

## Inert-Mode Gate

This command requires `delivery_mode: per-slice`. **Slice commands are inert in whole-feature mode** (per REQ-007 + EDGE-002).

### Step 1: Locate the active SPEC

```bash
ls SDD/requirements/SPEC-*.md
```

Single match → use it. Multiple → prompt the user (supervised) or halt (autonomous). Zero → `No SPEC found in SDD/requirements/. Run /planning-start to create one before invoking /slice-commit.`

### Step 2: Read `delivery_mode:` from the SPEC frontmatter

The canonical enum is exactly `{whole-feature, per-slice}` (lowercase, hyphenated). Branch:

- **`per-slice`** → continue.
- **`whole-feature` OR field absent** → emit the REQ-007 verbatim inert message and exit cleanly with NO partial state writes:

  ```
  This command requires `delivery_mode: per-slice` in the spec frontmatter. Current spec uses `delivery_mode: <value>`. Run `/implementation-start` instead, or set `delivery_mode: per-slice` in your spec and re-run `/planning-start`.
  ```

- **Any other value** → fail per REQ-001 validation: `Invalid delivery_mode value '<value>' in <spec-path>. Allowed values: whole-feature, per-slice. Edit the spec frontmatter and re-run /planning-start.`

## Slice-ID Validation (REQ-024 / SEC-003)

Slice-ID arguments MUST be validated against the regex `^SLICE-\d{3}$` BEFORE being interpolated into any read or write path. On regex mismatch, refuse with the REQ-007 message-discipline shape: `Invalid SLICE-ID argument '<arg>'. SLICE-ID must match the pattern SLICE-### (three digits).`

## Step 3: Resolve the active SLICE-XXX

Apply the **Active-Slice Resolution Convention** above. Expected statuses for `/slice-commit`: `In Progress` or `Acceptance Check Passing` (the slice has been implemented and retrospected; the commit is the delivery action).

- **`[SLICE-ID]` provided:** verify the row exists and is at `In Progress`/`Acceptance Check Passing`. If at `Not Started`, fail with: `SLICE-XXX has not been started. Run /slice-start SLICE-XXX first.` If at `Complete`, fail with: `SLICE-XXX is already Complete (committed). To re-commit a Complete slice, use /slice-start --force SLICE-XXX first to re-open it.`
- **No argument, single matching row:** use it.
- **No argument, multiple matching rows:** prompt the user (supervised) or halt (autonomous).
- **No argument, zero matching rows:** fail with: `No slice currently In Progress or Acceptance Check Passing in <IMPLEMENTATION-PLAN-XXX-...md>.`

## Step 4: Verify the retrospective has been written

`/slice-commit` requires `/slice-retro` to have run for this slice (the commit covers the retrospective + ledger update). Verify:

```bash
ls SDD/implementation/slices/RETROSPECTIVE-SLICE-<SLICE-XXX>-*.md
ls SDD/implementation/slices/LEARNINGS-FEATURE-*.md
```

If the retrospective is absent, fail with: `No retrospective found for SLICE-XXX (expected SDD/implementation/slices/RETROSPECTIVE-SLICE-<SLICE-XXX>-<feature-name>-<YYYY-MM-DD>.md). Run /slice-retro SLICE-XXX before /slice-commit.`

If the ledger is absent, surface a warning (not a hard fail — the first slice may legitimately be the one creating the ledger): `Warning: no LEARNINGS-FEATURE-<feature-name>.md ledger found. Expected /slice-retro to scaffold it. Verify the ledger was written before committing.`

## `## Slice Progress` Table — Binding Schema (REQ-022, reference)

- **Columns:** `SLICE-ID | Name | Status | Acceptance check | Test result | Notes`.
- **Status enum:** `Not Started`, `In Progress`, `Acceptance Check Passing`, `Complete`. Forward-only.
- `/slice-commit` flips `Status` to `Complete` (terminal state) after the commit lands.

## Step 5: Looser staging — show `git status` and ask user to confirm

Per OQ-C conservative default — `/slice-commit` does **NOT** enforce that the working tree contains only slice-scoped files. The user owns staging; the command owns message structure. Rationale (per Q-C): the stricter check is hostile to legitimate workflows like "I noticed an unrelated typo while implementing this slice and want to include the fix here."

Run:

```bash
git status
```

List the staged and unstaged files to the user. If nothing is staged yet, prompt the user to stage the slice's files (use `git add` with specific paths — never `-A` or `.`; per project convention from `/commit`).

In supervised mode, ask: `The staged files are: <list>. Confirm this looks slice-scoped for SLICE-XXX. [y/N]`. In autonomous mode, the orchestrator stages the slice's files explicitly (computed from the slice's file set per REQ-004's intersection rule); proceed without prompt.

## Step 6: Construct the commit message via heredoc (per L-2 fix; mirrors `/commit` precedent)

Per REQ-006 + SEC-001:

- **MUST use heredoc** to construct the commit message — no shell-string concatenation, no inline `git commit -m "$summary"` interpolation. This neutralizes shell-metacharacter / command-substitution hazards in the auto-derived summary text.
- **MUST NOT use `--no-verify`** — pre-commit hooks run; if a hook fails, fix the issue, re-stage, re-run `/slice-commit` (per CLAUDE.md project convention).
- **MUST NOT add co-author attribution or "Generated with Claude" lines** — per project convention from `/commit`. Commits are authored solely by the user.

Commit message form (per REQ-006 — first line follows the `slice: SLICE-XXX <Concentrated function summary>` shape):

```bash
git commit -m "$(cat <<'EOF'
slice: SLICE-XXX — <concentrated function summary in imperative mood, ≤60 chars after the SLICE-XXX prefix>

Slice scope: <one-line description of what this slice delivers>
SPEC: SDD/requirements/SPEC-XXX-<feature-name>.md
Acceptance check: <verbatim acceptance check from the row, or "see Slice Progress row"> — PASSING
Retrospective: SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-<feature-name>-<YYYY-MM-DD>.md
Per-slice review: SDD/reviews/REVIEW-SLICE-XXX-<feature-name>-<YYYY-MM-DD>.md
Ledger: SDD/implementation/slices/LEARNINGS-FEATURE-<feature-name>.md

<body — 3-6 lines summarizing implementation decisions, deviations from SPEC (if any), retro highlights, and the per-slice review's key findings if any. Plain prose; imperative mood.>
EOF
)"
```

**Why heredoc:** the body may contain backticks, dollar signs, parentheses, exclamation marks — anything that shell quoting interprets as syntax. Heredoc with quoted EOF (`<<'EOF'`, single-quoted) suppresses ALL shell expansion, treating the body as literal text. The `/commit` command uses the same pattern.

## Step 7: Run the commit

```bash
git commit -m "$(cat <<'EOF'
... (message from Step 6)
EOF
)"
```

If the commit fails due to a pre-commit hook failure: investigate and fix the underlying issue, re-stage the fixes, then create a NEW commit (do NOT amend, do NOT use `--no-verify`). This mirrors the project-wide `/commit` policy.

If the commit succeeds, capture the commit SHA from `git log -n 1 --format=%H` for the progress.md update.

## Step 8: Update the `## Slice Progress` table — flip Status to `Complete`

Edit the IMPLEMENTATION-PLAN in place:

- Locate the row for the active SLICE-XXX.
- Change `Status` from `In Progress` (or `Acceptance Check Passing`) → `Complete`. This is the terminal forward-only transition.
- Leave `SLICE-ID`, `Name`, `Acceptance check` UNCHANGED.
- Update `Notes` to reference the commit: `Committed YYYY-MM-DD at <commit-SHA-short>; retro at <retrospective-path>`.
- `Test result` should already reflect the test outcome from `/slice-retro`; do not overwrite unless the commit revealed a regression (rare; if so, abort the commit and re-run `/slice-review`).

## Step 9: Update `progress.md`

Append an entry to `SDD/orchestration/progress.md` recording the commit:

```markdown
## Slice <SLICE-XXX> - Complete

- **Date:** YYYY-MM-DD
- **Commit SHA:** <short SHA>
- **SPEC:** SDD/requirements/SPEC-XXX-<feature-name>.md
- **IMPLEMENTATION-PLAN:** SDD/implementation/IMPLEMENTATION-PLAN-XXX-<feature-name>-<date>.md
- **Retrospective:** SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-<feature-name>-<YYYY-MM-DD>.md
- **Per-slice review:** SDD/reviews/REVIEW-SLICE-XXX-<feature-name>-<YYYY-MM-DD>.md
- **Slice Progress Status:** Complete (terminal)
```

## Step 10: Hand off to the next slice (or end-of-feature)

Output a friendly message to the user describing:

- The commit SHA, date, and short message line.
- The next slice to start (read `## Slice Progress` for the next `Not Started` row, if any) — suggested next command: `/slice-start <next-SLICE-XXX>`.
- If no `Not Started` rows remain (all slices `Complete`), the slice cycle is done. The user (or `/sdd-flow`) proceeds to the end-of-feature steps: `/implementation-test`, `/code-review`, `/implementation-complete`, etc.

## Flag Inventory (REQ-025 — applies to `/slice-commit`)

`/slice-commit` introduces NO flags of its own (per SPEC MODULE-002 + REQ-025: `/slice-commit [SLICE-ID]` — no flags introduced by this feature). The user's standard `git` invocation options are not exposed at the slice-command layer.

For reference, the slice-command flag inventory across all four `/slice-*` commands (REQ-025):

| Flag | Command | Default | Notes |
|------|---------|---------|-------|
| `--resume SLICE-XXX` | `/slice-start` | Off | Re-attach to In Progress slice. |
| `--force SLICE-XXX` | `/slice-start` | Off | Destructive override for re-starting a Complete slice. |
| `--reconcile-ledger SLICE-XXX` | `/slice-retro` | Off | Rebuild ledger from on-disk retros. |

The `/sdd-flow continue` flags `--replan`, `--from-slice SLICE-XXX`, `--override-replan` are orchestrator-level flags, NOT slice-command flags.

## Path Conventions (REQ-016)

This command emits paths under the SDD 2.0.0 layout:

- `SDD/requirements/SPEC-XXX-[feature-name].md`
- `SDD/implementation/IMPLEMENTATION-PLAN-XXX-[feature-name]-[date].md`
- `SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-[feature-name]-[YYYY-MM-DD].md`
- `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` (kebab-case feature-name slug per CLARIFICATION OQ-B)
- `SDD/reviews/REVIEW-SLICE-XXX-[feature-name]-[YYYY-MM-DD].md`
- `SDD/orchestration/progress.md`

## Refusal-Message Discipline (REQ-007 / UX-001)

Every refusal path follows the REQ-007 message-discipline standard: name the detected condition, name the resolution path, exit cleanly without partial state writes.

## Atomicity Invariant

The commit produced by `/slice-commit` is **ATOMIC PER SLICE**. It includes everything the slice produced: code, tests, the per-slice review doc, any fix-findings notes, the retrospective artifact, and the ledger update. The slice is a discrete delivery unit; one slice = one commit. This makes the slice's contribution traceable in `git log` and reversible (a single `git revert <SHA>` rolls back the entire slice).
