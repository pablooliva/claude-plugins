# Migrate the SDD Artifact Layout to 2.0.0 Conventions

You are running a one-shot migration helper that relocates legacy SDD artifacts from the pre-2.0.0 layout (`SDD/prompts/...`) to the 2.0.0 layout (`SDD/implementation/...` + `SDD/orchestration/...`) and renames `PROMPT-XXX` trackers to `IMPLEMENTATION-PLAN-XXX`. Per ADR 0002, the relocation and the rename ship together in one major-version bump.

This command is **mode-agnostic** — it runs identically whether the active SPEC declares `delivery_mode: whole-feature` or `delivery_mode: per-slice` (or has no SPEC at all). The migration operates only on `SDD/` at the repo root; it does NOT touch user CLAUDE.md, AGENTS.md, plugin source code, or any path outside `SDD/`.

**Safety posture (binding):**

- **Dry-run is the default.** Without `--apply`, the command enumerates every move it WOULD perform and exits without changing the tree.
- **Refusals are fail-closed.** If the helper cannot prove it is safe to migrate (active flow detected, `progress.md` unparseable, both layouts populated, working tree dirty, non-bash shell, plugin version too old), it refuses and exits cleanly without partial state writes per REQ-007 / UX-001 message-discipline standard.
- **Every move is a `git mv`.** History is preserved per file. Plain `mv` is never used (would lose blame). `--no-verify` and force flags are NEVER passed to git per SEC-001 — pre-commit hooks run; if a hook fails, fix the underlying issue and re-run.

## Flag Inventory (binding)

| Flag | Semantics | Default | Notes |
|------|-----------|---------|-------|
| `--apply` | Actually perform the migration. Without this flag, the command is dry-run only. | Off | Dry-run is the default safety stance. |
| `--allow-dirty` | Skip the clean-working-tree precondition. User accepts that `git reset --hard HEAD` rollback will discard their other in-flight edits. | Off | Destructive-adjacent; do not use without understanding. |
| `--force-no-active` | Override BOTH the active-flow refusal (SEC-002) AND the parse-failure refusal (EDGE-015 / FAIL-008). Used for genuinely orphaned `progress.md` (e.g., last flow concluded long ago and the file was left behind). | Off | Destructive override; use only after manually inspecting `progress.md`. |
| `--resume-partial` | Acknowledge a partial-migration tree (BOTH `SDD/prompts/` AND `SDD/orchestration/` populated) and proceed with the remaining moves. Default refusal halts on partial state per REQ-008. | Off | Use only after manually reconciling what's at each path. |

The orchestrator-level flags (`--replan`, `--from-slice`, `--override-replan`) belong to `/sdd-flow continue`, not to this command.

## Step 0: Bash availability check (FAIL-005)

The migration script uses bash 3.0+ syntax (parameter expansion `${f//OLD/NEW}`, `for f in glob; do … done` loops with `[ -e "$f" ] || continue` guards). On Windows, Claude Code may invoke commands via PowerShell or cmd.exe by default; those interpreters do not support these constructs and would produce partial moves on failure.

**First action of the command, before any other check:**

```bash
command -v bash >/dev/null 2>&1 || { echo "ERROR: /sdd-migrate-layout requires bash. On Windows, run from Git Bash."; exit 1; }
```

If bash is not available, refuse cleanly with the diagnostic message above and exit. No moves attempted; no rollback needed because no state was changed.

## Step 1: Plugin-version precondition

The migration helper belongs to the SDD 2.0.0 release. If the installed SDD plugin is older, the source-code path emissions in the rest of the plugin will still target the legacy layout, and migrating now would produce a tree the plugin cannot read. Verify:

```bash
grep '"version"' "$(find . -path '*/sdd/.claude-plugin/plugin.json' -maxdepth 5 2>/dev/null | head -1)" 2>/dev/null
```

If the version is below 2.0.0 (or the file cannot be located), refuse with:

```
Refusing migration: /sdd-migrate-layout requires the SDD plugin at version 2.0.0 or later.
The migration ships in the 2.0.0 release; older versions of the plugin write artifacts at the legacy paths and migrating now would orphan them.
Update via: /plugin install https://github.com/poliva83/claude-plugins sdd
Then re-run /sdd-migrate-layout.
```

## Step 2: Detect tree state (4-state machine, surfaced explicitly to users)

Per SPEC REQ-008 (panel data-modeling LOW): the migration helper has FOUR states. Each must be classified before any move is performed. Read these signals:

```bash
# Signal A: legacy layout present?
test -d SDD/prompts/context-management || \
test -d SDD/prompts/implementation-complete || \
ls SDD/prompts/PROMPT-*.md >/dev/null 2>&1
# (any one of the above true → legacy is present)

# Signal B: new layout present and populated?
test -d SDD/orchestration && \
{ test -f SDD/orchestration/progress.md || \
  ls SDD/orchestration/subagent-calls/* >/dev/null 2>&1 || \
  ls SDD/implementation/IMPLEMENTATION-PLAN-*.md >/dev/null 2>&1; }
```

Branch on the four resulting states:

| State | Signal A (legacy) | Signal B (new) | Action |
|-------|-------------------|----------------|--------|
| **1. Nothing to migrate** | False | False | Print `Nothing to migrate. Tree has no SDD artifacts at either layout.` and exit 0 (idempotent-clean). |
| **2. Already migrated** | False | True | Print `No migration needed; layout is already at 2.0.0 conventions.` and exit 0 (EDGE-001 idempotence). |
| **3. Ready to migrate** | True | False | Continue to Step 3 (active-flow refusal check). |
| **4. Partial migration** | True | True | Refuse unless `--resume-partial` was passed. See partial-migration handling below. |

**State 4 (partial migration) refusal message (per REQ-008 + REQ-007 discipline):**

```
Both old and new layouts contain content; previous migration may have crashed.
Inspect manually; resolve by hand before re-running.
  Legacy artifacts at: <list files under SDD/prompts/>
  New-layout artifacts at: <list files under SDD/implementation/ and SDD/orchestration/>
If you have manually reconciled the trees and want to proceed with remaining legacy moves, re-run with --resume-partial.
```

Then exit 1. The `--resume-partial` mode skips this refusal but still runs Steps 3–7 normally (any move whose source no longer exists is a no-op; idempotence is preserved by the `[ -e "$f" ] || continue` guards in the move set).

## Step 3: Active-flow refusal (SEC-002, FAIL-002, EDGE-015, FAIL-008) — fail-closed

This is the load-bearing safety check. A migration during an active flow would relocate live `progress.md` mid-write and silently corrupt orchestration state. Detection logic:

### Step 3a: locate progress.md

The legacy path is `SDD/prompts/context-management/progress.md`. (After migration, progress.md moves to `SDD/orchestration/progress.md`, but Step 2 already routed Already-Migrated trees to exit; at this step we are in State 3, so the legacy path is the one to read.)

```bash
PROGRESS_PATH="SDD/prompts/context-management/progress.md"
test -f "$PROGRESS_PATH" || { echo "No progress.md found at legacy path; assuming no active flow. Continuing."; ACTIVE=no; }
```

If the file does not exist AND legacy artifacts ARE present (Step 2's Signal A was true), this is a degenerate case: a legacy tree without `progress.md`. Per SEC-002, the fail-closed rule applies when `progress.md` is absent AND other SDD content exists. Refuse with:

```
Could not determine flow status; refusing migration. Inspect progress.md manually before re-running.
Reason: legacy artifacts present but progress.md is missing — cannot prove no flow is active.
If progress.md is genuinely orphaned (no flow ever ran or it concluded long ago), re-run with --force-no-active.
```

If the file does not exist AND no legacy artifacts exist (impossible in State 3 per Step 2's classification, but defense-in-depth): treat as Step 2 State 1.

### Step 3b: parse the latest `## Phase: <name> - <status>` block

When `progress.md` IS present at the legacy path, parse it for the most recent phase status block. Look for:

- The latest `## Phase: <name> - <status>` heading (e.g., `## Phase: Research - In Progress`, `## Phase: Planning - COMPLETE`, `## Phase: Implementation - In Progress`).
- OR any of these alternative active-state headings: `## Awaiting Clarification`, `## Awaiting Slicing Decision`, `## Recommended Re-planning`, `## PARTIAL: needs continuation`.
- The terminal-success marker is `## Phase: Implementation - COMPLETE` (or, in older trees, `## Implementation Phase - COMPLETE`).

```bash
# Parse the latest top-level "## " heading whose text begins with "Phase:" or one of the alternative-active markers.
# (Use awk/grep to extract; do not eval the file contents.)
LATEST_BLOCK=$(grep -E '^## (Phase:|Awaiting |Recommended Re-planning|PARTIAL:)' "$PROGRESS_PATH" | tail -1)
```

### Step 3c: classify the parse result and refuse if active

Three classification outcomes:

**(i) Parse succeeds, status = `COMPLETE`:** safe to migrate. Continue to Step 4.

**(ii) Parse succeeds, status != `COMPLETE` (active phase detected):** refuse with REQ-007 message-discipline shape. The diagnostic names the detected condition and the resolution path:

```
Refusing migration: an SDD flow appears to be active.
Detected: <verbatim text of the latest block — e.g., "## Phase: Implementation - In Progress" or "## Awaiting Slicing Decision">
Path: SDD/prompts/context-management/progress.md
Resolve the in-flight flow first (run /sdd-flow continue to completion, or /implementation-complete if implementation is done), then re-run /sdd-migrate-layout.
```

Exit 1. No moves attempted.

**(iii) Parse FAILS** (file unreadable, malformed, schema unexpected, or no `## Phase:` / `## Awaiting ` / `## Recommended Re-planning` / `## PARTIAL:` heading found at all): per SEC-002 / EDGE-015 / FAIL-008 fail-closed posture, refuse:

```
Refusing migration: progress.md exists but cannot be parsed.
Path: SDD/prompts/context-management/progress.md
Reason: <parser error or "no recognizable phase-status heading found">
Failing closed to avoid data-loss-by-misclassification. The cost of a false-refusal is one inspect-and-rerun; the cost of a false-proceed is silent data-loss. Either:
  1. Repair progress.md manually and re-run, OR
  2. If progress.md is genuinely orphaned (last flow concluded long ago), back it up with `cp progress.md progress.md.orphan` and re-run with --force-no-active to override this refusal.
```

Exit 1. No moves attempted.

**`--force-no-active` semantics:** when this flag is passed, Steps 3a–3c are SKIPPED entirely. The orchestrator (or user) has affirmed that no flow is active. This flag overrides BOTH the active-status refusal (case ii) AND the parse-failure refusal (case iii). It does not override Step 4 (clean-working-tree) or Step 5 (move set integrity); those are independent gates.

## Step 4: Working-tree cleanliness precondition

The migration produces a sequence of `git mv` operations. If any individual move fails partway (disk full, permission denied, antivirus interference), recovery via `git reset --hard HEAD` is the simplest rollback path — but this is only safe if the working tree was clean before the migration started (otherwise the user's other in-flight edits get destroyed).

```bash
git status --porcelain
```

If the output is non-empty (uncommitted changes present), refuse:

```
Refusing migration: working tree has uncommitted changes.
Commit or stash uncommitted changes before migrating to ensure rollback is possible.
  git stash push -u -m "pre-sdd-migrate-layout"
  /sdd-migrate-layout --apply
  git stash pop
If you understand that rollback will require manual `git mv` reverse-operations and want to proceed with a dirty tree, re-run with --allow-dirty.
```

Exit 1. No moves attempted.

`--allow-dirty` skips this gate but does NOT skip Step 3 (active-flow refusal); the gates compose.

## Step 5: Plan and dry-run the move set (default behavior — no `--apply`)

When `--apply` is NOT passed (dry-run mode, the default), enumerate every move that WOULD be executed and print them. Do NOT actually execute. The user inspects the plan, then re-runs with `--apply` to commit to it.

The move set, exactly per ADR 0002 + research Branch 4:

```bash
# Setup (idempotent — mkdir -p is no-op when target exists)
mkdir -p SDD/implementation/summaries
mkdir -p SDD/implementation/slices
mkdir -p SDD/orchestration/subagent-calls
mkdir -p SDD/orchestration/counters
mkdir -p SDD/orchestration/compacted

# 1. Implementation tracker (relocate AND rename PROMPT- → IMPLEMENTATION-PLAN-)
for f in SDD/prompts/PROMPT-*.md; do
  [ -e "$f" ] || continue
  newname="${f//PROMPT-/IMPLEMENTATION-PLAN-}"
  newpath="SDD/implementation/$(basename "$newname")"
  git mv "$f" "$newpath"
done

# 2. Implementation summaries (relocation only — filename unchanged)
if [ -d "SDD/prompts/implementation-complete" ]; then
  for f in SDD/prompts/implementation-complete/*.md; do
    [ -e "$f" ] || continue
    git mv "$f" "SDD/implementation/summaries/$(basename "$f")"
  done
  rmdir SDD/prompts/implementation-complete 2>/dev/null
fi

# 3. Test audits (if present)
if [ -d "SDD/prompts/test-audits" ]; then
  mkdir -p SDD/implementation/test-audits
  for f in SDD/prompts/test-audits/*.md; do
    [ -e "$f" ] || continue
    git mv "$f" "SDD/implementation/test-audits/$(basename "$f")"
  done
  rmdir SDD/prompts/test-audits 2>/dev/null
fi

# 4. Orchestration state — progress.md
if [ -f "SDD/prompts/context-management/progress.md" ]; then
  git mv SDD/prompts/context-management/progress.md SDD/orchestration/progress.md
fi

# 5. Subagent-calls
if [ -d "SDD/prompts/context-management/subagent-calls" ]; then
  for f in SDD/prompts/context-management/subagent-calls/*; do
    [ -e "$f" ] || continue
    git mv "$f" "SDD/orchestration/subagent-calls/$(basename "$f")"
  done
  rmdir SDD/prompts/context-management/subagent-calls 2>/dev/null
fi

# 6. Counters
if [ -d "SDD/prompts/context-management/counters" ]; then
  for f in SDD/prompts/context-management/counters/*; do
    [ -e "$f" ] || continue
    git mv "$f" "SDD/orchestration/counters/$(basename "$f")"
  done
  rmdir SDD/prompts/context-management/counters 2>/dev/null
fi

# 7. Compaction files (research-, planning-, implementation-, adhoc-)
for f in SDD/prompts/context-management/research-compacted-*.md \
         SDD/prompts/context-management/planning-compacted-*.md \
         SDD/prompts/context-management/implementation-compacted-*.md \
         SDD/prompts/context-management/compact-*.md; do
  [ -e "$f" ] || continue
  git mv "$f" "SDD/orchestration/compacted/$(basename "$f")"
done

# 8. Cleanup empty parents
rmdir SDD/prompts/context-management 2>/dev/null
rmdir SDD/prompts 2>/dev/null
```

**Cross-platform shell note:** every construct above is bash 3.0+ compatible. The `${f//OLD/NEW}` parameter-expansion is bash-specific (not POSIX `sh`), which is why Step 0's bash detection is the load-bearing portability gate. macOS / Linux / Git Bash for Windows all satisfy this. The `for f in glob; do ... [ -e "$f" ] || continue ... done` idiom handles the no-match case cleanly (the unmatched glob expands to itself; the `-e` test then fails and `continue` skips it).

**Hardcoded-path safety (SEC-001 / SEC-003):** every source and destination path in the move set is a HARDCODED string literal in the command body. The command does NOT accept a path argument, does NOT interpolate environment variables into source/destination paths, and does NOT eval any file contents. There is no opportunity for path traversal or arbitrary command execution.

### Dry-run output format

```
Dry-run: would execute the following migration plan.
(Re-run with --apply to actually perform the moves.)

Setup:
  mkdir -p SDD/implementation/summaries
  mkdir -p SDD/implementation/slices
  mkdir -p SDD/orchestration/subagent-calls
  mkdir -p SDD/orchestration/counters
  mkdir -p SDD/orchestration/compacted

Moves (N total):
  git mv SDD/prompts/PROMPT-001-foo.md SDD/implementation/IMPLEMENTATION-PLAN-001-foo.md
  git mv SDD/prompts/PROMPT-002-bar.md SDD/implementation/IMPLEMENTATION-PLAN-002-bar.md
  git mv SDD/prompts/implementation-complete/SUMMARY-001-foo.md SDD/implementation/summaries/SUMMARY-001-foo.md
  git mv SDD/prompts/context-management/progress.md SDD/orchestration/progress.md
  git mv SDD/prompts/context-management/subagent-calls/<N items> SDD/orchestration/subagent-calls/
  git mv SDD/prompts/context-management/counters/<M items> SDD/orchestration/counters/
  git mv SDD/prompts/context-management/research-compacted-001-foo-2026-01-01.md SDD/orchestration/compacted/...
  ...

Cleanup:
  rmdir SDD/prompts/context-management
  rmdir SDD/prompts/implementation-complete
  rmdir SDD/prompts

To execute this plan, re-run: /sdd-migrate-layout --apply
```

If the dry-run shows zero moves (all files match a no-op), report `Nothing to migrate at the legacy paths. Tree may already be partially migrated; check Step 2 classification.`

## Step 6: Apply the move set (only when `--apply` is passed)

When the user re-runs with `--apply`, execute the move set sequentially. Capture each `git mv`'s exit code; on first non-zero exit, halt and route to Step 7 (rollback / partial-migration recovery).

```bash
set -e  # halt on first failure
# (run the move set as enumerated in Step 5, but actually execute, not echo)
```

After all moves succeed:

```bash
git status --short
git diff --stat --cached
```

Print a summary:

```
Migration complete.
  Files moved: <N>
  Directories removed: <M>
  Tree now matches SDD 2.0.0 layout (SDD/implementation/, SDD/orchestration/).

Next steps:
  1. Inspect:    git diff --stat --cached
  2. Verify:     git status
  3. Commit:     git commit -m "chore(sdd): migrate to 2.0.0 layout"
                 (uses the project's standard commit policy — no --no-verify, no co-author lines)

Hook reminder: ensure your installed SDD plugin is at version 2.0.0 or later. Older versions of sdd/hooks/log_subagent_call.py write to the legacy path (SDD/prompts/context-management/subagent-calls/), which would silently re-create the legacy directory and produce a split-tree. The 2.0.0 hook writes to SDD/orchestration/subagent-calls/.
```

Then run Step 8 (CLAUDE.md staleness scan) and Step 9 (post-migration verification).

## Step 7: Partial-migration recovery (FAIL-001) — invoked when `git mv` fails mid-run

Per FAIL-001: a `git mv` failure mid-migration (disk full, permission denied, antivirus interference, etc.) leaves the tree partially migrated. Recovery:

```
ERROR: git mv failed during migration.
  Failed move: <command and stderr>
  Successful moves before failure: <list>
  Pending moves not attempted: <list>

The tree is now partially migrated. To recover:

Option A (simplest — discard the migration entirely):
  git reset --hard HEAD
  (Safe ONLY because pre-flight verified the working tree was clean. If you ran with --allow-dirty, this will also discard your other uncommitted edits.)

Option B (preserve progress; manually undo the successful moves):
  <enumerated list of inverse `git mv` operations, one per successful move; each is the source/destination swap of the corresponding move from Step 5>

Option C (preserve progress; commit what succeeded and address the failure):
  Investigate why <failed move> errored (disk space? permissions? antivirus?), fix, then re-run /sdd-migrate-layout --apply --resume-partial.

After recovery, re-run /sdd-migrate-layout to verify a clean state.
```

Exit 1.

The recovery recipe is computed dynamically: every move attempted before the failure is added to the "successful moves" list, and its inverse is computed as `git mv <destination> <source>`. The user pastes Option B verbatim into a shell to manually undo. (Option A is recommended as the default — it is idempotent and the cleanest recovery; Option B exists for users who reject the destructive `git reset`.)

## Step 8: CLAUDE.md staleness scan (EDGE-004)

Per EDGE-004 + spec REQ-019 reminder: the migration helper does NOT auto-edit user-authored CLAUDE.md or AGENTS.md. The user owns those files. But the helper SHOULD warn if those files contain stale legacy-path references that will not work post-migration:

```bash
# Scan for legacy-path references in user-authored agent docs.
for pattern in 'SDD/prompts/context-management' 'SDD/prompts/implementation-complete' 'SDD/prompts/PROMPT-' 'PROMPT-XXX' 'PROMPT-[0-9]'; do
  grep -rn -l "$pattern" --include='CLAUDE.md' --include='AGENTS.md' --include='CLAUDE.local.md' . 2>/dev/null
done | sort -u
```

If any hits are found, print:

```
Warning: detected legacy SDD path references in CLAUDE.md / AGENTS.md files.
These references will not work after migration:
  <file>:<line>: <quoted line>
  ...

Update them manually to match the new layout:
  SDD/prompts/context-management/  →  SDD/orchestration/
  SDD/prompts/implementation-complete/  →  SDD/implementation/summaries/
  SDD/prompts/PROMPT-XXX  →  SDD/implementation/IMPLEMENTATION-PLAN-XXX
  PROMPT-XXX (numbering convention)  →  IMPLEMENTATION-PLAN-XXX

This warning is informational; the migration completed successfully. The /sdd-migrate-layout helper does NOT auto-edit user-authored documentation per project policy.
```

If no hits, print `No legacy-path references detected in CLAUDE.md / AGENTS.md files.` and continue.

## Step 9: Post-migration verification (EDGE-001 idempotence loop-closure)

After `--apply` succeeds, re-run the Step 2 detection to confirm the tree is now in State 2 (already migrated):

```bash
# Re-detect:
test -d SDD/prompts/context-management && echo "ANOMALY: legacy directory still present"
test -d SDD/orchestration && test -f SDD/orchestration/progress.md && echo "OK: orchestration state at new path"
ls SDD/implementation/IMPLEMENTATION-PLAN-*.md 2>/dev/null && echo "OK: implementation trackers at new path"
```

If anomalies are detected (e.g., `SDD/prompts/context-management` still exists despite no errors during the move set), print a warning instructing the user to inspect manually. The verification is informational — by this point all moves have committed and rolling back the verification step itself is meaningless.

## Step 10: Refusal-message discipline summary (REQ-007 / UX-001)

Every refusal path in this command follows the REQ-007 message-discipline standard:

1. **Name the detected condition** ("active flow", "parse failure", "partial migration", "dirty working tree", "non-bash shell", "plugin too old").
2. **Name the resolution path** (concrete next command or manual step).
3. **Exit cleanly without partial state writes.**

Refusal-message inventory (each appears in the corresponding step):

| Step | Trigger | Message snippet |
|------|---------|-----------------|
| 0 | non-bash shell | `On Windows, run from Git Bash` |
| 1 | plugin < 2.0.0 | `requires the SDD plugin at version 2.0.0 or later` |
| 2 (state 4) | partial migration | `Both old and new layouts contain content; previous migration may have crashed.` |
| 3a | progress.md absent + legacy artifacts present | `Could not determine flow status; refusing migration.` |
| 3c (ii) | active phase | `Refusing migration: an SDD flow appears to be active.` |
| 3c (iii) | parse failure (fail-closed) | `Refusing migration: progress.md exists but cannot be parsed.` ... `Failing closed to avoid data-loss-by-misclassification` |
| 4 | dirty working tree | `Refusing migration: working tree has uncommitted changes.` |
| 7 | mid-migration failure | `ERROR: git mv failed during migration.` (with rollback recipe) |

## Path Conventions (REQ-016)

This command is the ONLY file in the SDD plugin that legitimately references both legacy paths (as migration sources) and new paths (as migration destinations). The closing-oracle grep `grep -rn 'prompts/\|PROMPT-' sdd/commands/` will match this file's body, which is expected and excluded from the path-cleanup invariant for other commands.

Source paths (legacy, pre-2.0.0):
- `SDD/prompts/context-management/progress.md`
- `SDD/prompts/context-management/subagent-calls/`
- `SDD/prompts/context-management/counters/`
- `SDD/prompts/context-management/{research,planning,implementation}-compacted-*.md`
- `SDD/prompts/context-management/compact-*.md`
- `SDD/prompts/implementation-complete/*.md`
- `SDD/prompts/test-audits/*.md` (if present)
- `SDD/prompts/PROMPT-*.md`

Destination paths (2.0.0):
- `SDD/orchestration/progress.md`
- `SDD/orchestration/subagent-calls/`
- `SDD/orchestration/counters/`
- `SDD/orchestration/compacted/`
- `SDD/implementation/summaries/`
- `SDD/implementation/test-audits/` (if present)
- `SDD/implementation/IMPLEMENTATION-PLAN-*.md` (renamed from PROMPT-*.md)
- `SDD/implementation/slices/` (created empty for per-slice mode artifacts)

## Atomicity Note

`/sdd-migrate-layout` does NOT itself produce a git commit. It stages renames via `git mv`. The user is responsible for the commit, per the post-migration "Next steps" output. Rationale: keeping migration and commit separate lets the user inspect `git diff --stat --cached` before committing, and if anything looks wrong, the user can `git reset HEAD` to unstage without having to interact with commit history.

When the user does commit, project policy applies (per `/commit` and CLAUDE.md): no `--no-verify`; no co-author / "Generated with Claude" lines. Suggested message: `chore(sdd): migrate to 2.0.0 layout`.
