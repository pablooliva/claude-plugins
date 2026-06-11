# Commit Changes

You are tasked with creating git commits for the changes made during this session. This file is the single source of commit conventions for the sdd-flow orchestrator — it covers BOTH ordinary phase commits (research, planning, whole-feature implementation) and atomic **per-slice** commits.

## Process (ordinary phase commits)

1. **Think about what changed:**
   - Review the conversation history and understand what was accomplished
   - Run `git status` to see current changes
   - Run `git diff` to understand the modifications
   - Consider whether changes should be one commit or multiple logical commits

2. **Plan your commit(s):**
   - Identify which files belong together
   - Draft clear, descriptive commit messages
   - Use imperative mood in commit messages
   - Focus on why the changes were made, not just what

3. **Present your plan to the user:**
   - List the files you plan to add for each commit
   - Show the commit message(s) you'll use
   - Ask: "I plan to create [N] commit(s) with these changes. Shall I proceed?"
   - (In autonomous sdd-flow runs, the orchestrator proceeds without prompting.)

4. **Execute upon confirmation:**
   - Use `git add` with specific files (never use `-A` or `.`)
   - Create commits with your planned messages
   - Show the result with `git log --oneline -n [number]`

## Important — attribution

- **NEVER add co-author information or Claude attribution**
- Commits should be authored solely by the user
- Do not include any "Generated with Claude" messages
- Do not add "Co-Authored-By" lines
- Write commit messages as if the user wrote them

## Hooks and safety

- **MUST NOT use `--no-verify`** — pre-commit hooks run; if a hook fails, fix the underlying issue, re-stage, and create a NEW commit (do NOT amend, do NOT bypass).
- **Use a quoted heredoc** (`<<'EOF'`) to construct multi-line commit messages — this suppresses ALL shell expansion, treating the body as literal text and neutralizing shell-metacharacter / command-substitution hazards in any auto-derived summary.

## Remember

- You have the full context of what was done in this session
- Group related changes together; keep commits focused and atomic when possible
- The user trusts your judgment — they asked you to commit

---

## Per-slice atomic commits (`delivery_mode: per-slice`)

When the orchestrator runs the per-slice commit (per-slice cycle step 4c.6), the commit is **ATOMIC PER SLICE**: ONE commit covering everything the slice produced — slice code + tests + per-slice review doc + fix-findings notes + retrospective + ledger update. One slice = one commit, so the slice's contribution is traceable in `git log` and reversible with a single `git revert <SHA>`.

**Staging (looser default):** the per-slice commit does NOT enforce that the working tree contains only slice-scoped files (this is hostile to legitimate "I fixed an unrelated typo while here" workflows). The orchestrator stages the slice's files explicitly with `git add <specific paths>` (never `-A` or `.`); in supervised mode it may first show `git status` and confirm the staged set looks slice-scoped.

**Preconditions** (the orchestrator verifies before committing): the retrospective `SDD/implementation/slices/RETROSPECTIVE-SLICE-<SLICE-XXX>-<feature-name>-<YYYY-MM-DD>.md` exists, and the rolling ledger `SDD/implementation/slices/LEARNINGS-FEATURE-<feature-name>.md` exists (the first slice may legitimately be the one that creates the ledger — warn, don't hard-fail, if absent).

**Message form** (quoted heredoc; no co-author attribution):

```bash
git commit -m "$(cat <<'EOF'
slice: SLICE-XXX — <concentrated function summary in imperative mood, ≤60 chars after the prefix>

Slice scope: <one-line description of what this slice delivers>
SPEC: SDD/requirements/SPEC-XXX-<feature-name>.md
Acceptance check: <verbatim acceptance check, or "see Slice Progress row"> — PASSING
Retrospective: SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-<feature-name>-<YYYY-MM-DD>.md
Per-slice review: SDD/reviews/REVIEW-SLICE-XXX-<feature-name>-<YYYY-MM-DD>.md
Ledger: SDD/implementation/slices/LEARNINGS-FEATURE-<feature-name>.md

<body — 3-6 lines: implementation decisions, deviations from SPEC, retro highlights, key per-slice review findings. Plain prose, imperative mood.>
EOF
)"
```

**After the commit lands**, the orchestrator (or the slice subagent per its body) flips the IMPLEMENTATION-PLAN `## Slice Progress` row `Status` to `Complete` (terminal, forward-only), updates `Notes` to reference the commit SHA + retrospective path, and appends a `## Slice <SLICE-XXX> - Complete` entry to `SDD/orchestration/progress.md` recording the SHA, date, SPEC, plan, retrospective, and per-slice review paths.
