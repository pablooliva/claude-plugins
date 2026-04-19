---
name: correction-codifier
description: "INVOKE THIS SKILL when the user corrects Claude's behavior during a session (e.g., 'no, don't do X', 'stop using Y', 'use Z instead', 'actually, that's wrong because...'), or when the user explicitly asks to codify, save, or remember a rule/convention. Proposes a durable `Always|Never [action] BECAUSE [reason]` rule and, on confirmation, appends it to the current project's CLAUDE.md so the correction compounds across future sessions. Operationalizes the Institutional Memory Principle — turns one-time corrections into permanent steering instead of letting knowledge evaporate at session end."
---

# Correction Codifier

Captures behavioral corrections into the project's `CLAUDE.md` as `Always|Never [action] BECAUSE [reason]` rules so one-time corrections become permanent institutional memory.

## Expert Vocabulary

Institutional memory. Always/Never directive. BECAUSE clause. Living principle vs. dead rule. Rule codification. Steering mechanism. Output distribution. Convention drift. Rule contradiction. CLAUDE.md project config. Corrective feedback loop. Anti-pattern capture.

## Anti-Pattern Watchlist

Before writing any rule, check against these patterns:

1. **Bare directive.** Rule lacks a BECAUSE clause. Detection: no rationale after the action. Resolution: ask the user *why*. If the user can't articulate it, the rule probably isn't durable enough to codify — suggest not adding.
2. **Contradictory rule.** New rule opposes or partially negates an existing rule in CLAUDE.md. Detection: scan the `Always/Never` section for the same subject (e.g., both addressing `.then()` vs `async/await`). Resolution: update the existing rule rather than appending a new one. Never create a chronological log of shifting opinions.
3. **Over-codification.** Capturing preference-level nitpicks as rules (e.g., "use single quotes"). Detection: the correction is already enforced by a linter or formatter in the repo. Resolution: decline to codify — say "your linter already enforces this, no rule needed."
4. **False-positive correction.** Treating clarification as correction. Detection: user said "no, I meant X" (clarifying what they asked for) rather than "no, don't do X" (correcting what you did). Resolution: do not activate; clarifications shape the current task, not durable rules.
5. **Scope creep to user-level.** Writing to `~/.claude/CLAUDE.md` instead of project-level. Detection: attempting any path outside the current project's root. Resolution: this skill ONLY writes to the current project's CLAUDE.md. User-level rules are out of scope.
6. **Feature-scoped rule.** The "rule" is really about how one feature should behave, not a cross-project convention. Detection: the rule references specific feature names, files, or temporary state. Resolution: decline — that belongs in the feature's SDD spec, not CLAUDE.md.

## When to Activate

Activate when the conversation contains any of these signals:

- **Correction verbs toward Claude:** "no, don't...", "stop doing...", "you shouldn't...", "that's wrong, use...", "actually, don't use X, use Y because...".
- **Explicit codification requests:** "codify that", "save this as a rule", "remember this", "add this to the project conventions", "make this a rule".
- **Convention declarations:** "in this project we always...", "we never...", "our convention is..." (especially when directed at correcting a just-produced output).

## When NOT to Activate

Explicitly skip these cases:

- **Pure clarification.** "No, I meant the other file." "Sorry, I was unclear." The user is correcting their own earlier message, not Claude's behavior.
- **Transient preferences.** "For this task, do it this way" — task-scoped, not durable.
- **Inside SDD planning discussions.** If the conversation is inside an `sdd-flow` planning phase and the "correction" is really about what the spec should say, that belongs in the spec, not CLAUDE.md.
- **Linter-enforced rules.** The repo already runs ESLint/Prettier/Ruff/gofmt etc. that enforces the style. Don't duplicate tool enforcement in prose.
- **Project doesn't have or want a CLAUDE.md.** If there's no CLAUDE.md and the user declines to create one, stop.

## Behavioral Instructions

Execute these steps in order. Do not skip steps.

### Step 1: Confirm the correction is real

Before anything else, check that what just happened is a correction of Claude's behavior (not clarification, not preference, not an in-task adjustment). If in doubt, ask: *"Is this something you'd like me to remember as a rule for this project going forward?"* — if user says no, stop.

### Step 2: Extract the three components

Every rule needs:

- **Action** — what to always or never do (the behavioral rule itself).
- **Modality** — `Always` or `Never`.
- **Reason** — the BECAUSE clause; *why* this rule exists.

If the user provided all three, proceed. If the reason is missing, ask for it: *"What's the reason behind this — so the rule generalizes to related decisions?"*

### Step 3: Check for contradictions and duplicates

Read the current project's `CLAUDE.md`. Locate the `## Always/Never` section (or equivalent). Scan for:

- **Exact duplicate** — same rule already present. If found, stop and tell the user.
- **Contradiction** — existing rule takes the opposite stance on the same subject. If found, surface the conflict and ask whether to *update* the existing rule (preferred) or document the change in reasoning.
- **Near-duplicate** — existing rule covers the same topic with different phrasing. Offer to merge.

### Step 4: Draft the rule

Format, strictly:

```
Always|Never [action], BECAUSE [reason].
```

Examples of correct form:

- `Always use T[] for array types, BECAUSE our ESLint config enforces the 'array' style and Array<T> triggers CI failures.`
- `Never import from @internal/legacy-auth, BECAUSE it was deprecated in v3.2 — use @internal/auth instead.`
- `Always run the test suite before committing, BECAUSE our pre-commit hook is advisory only and CI failures block deploys.`

### Step 5: Confirm with the user

Show the proposed rule and the target file path. Ask explicitly:

> Proposed rule:
> `Always|Never [action], BECAUSE [reason].`
>
> Append to `<project-root>/CLAUDE.md` under the `## Always/Never` section?

Do not write without explicit confirmation. The user may edit the phrasing before approving.

### Step 6: Append to CLAUDE.md

On confirmation:

1. Locate the project root (the nearest ancestor directory containing `CLAUDE.md`, `.git/`, or a recognizable project marker).
2. If `CLAUDE.md` exists:
   - If a `## Always/Never` section exists, append the rule as a new bullet at the end of that section.
   - If no `## Always/Never` section exists, create one (typically near the top, after introductory sections) and add the rule.
3. If `CLAUDE.md` does not exist, ask whether to create one. If yes, create a minimal file with the `## Always/Never` section and the new rule. If no, stop.

### Step 7: Close the loop

Confirm to the user what was written and where. Do not add further commentary.

## Output Format

Proposed rule shown as a code block:

```
Always|Never [action], BECAUSE [reason].
```

On confirmation, the rule appears as a bullet under `## Always/Never` in CLAUDE.md:

```markdown
## Always/Never

- Always use `T[]` for array types, BECAUSE our ESLint config enforces the 'array' style and `Array<T>` triggers CI failures.
- Never import from `@internal/legacy-auth`, BECAUSE it was deprecated in v3.2 — use `@internal/auth` instead.
```

## Examples

### BAD example — bare directive

**User:** "Actually, use async/await here."
**Skill draft (BAD):** `Never use .then() chains.`

Problems: no BECAUSE clause, too narrow (doesn't generalize to `.catch()`, `.finally()`), and the correction might have been task-scoped (just this file) rather than a project convention.

**Correct response:** Ask the user *why* before proposing a rule. If the reason is "our codebase convention is async-first and mixed styles make PRs harder to review," draft:

```
Always use async/await over .then() chains, BECAUSE our codebase convention is async-first and mixed styles make PRs harder to review.
```

### GOOD example — full rule with rationale

**User:** "Stop using `index` as a React list key — our perf reviews flagged re-render bugs from non-stable keys."
**Skill draft:**

```
Never use `index` as a React list key, BECAUSE our performance reviews flagged re-render bugs from non-stable keys — use stable IDs from the data instead.
```

Confirm with user, then append to `## Always/Never` in CLAUDE.md.

### BAD example — false positive

**User:** "No wait, I meant the other auth service, not that one."

This is clarification about which service was meant, not a correction of Claude's behavior. **Do not activate.** Continue the current task with the corrected target.

### BAD example — over-codification

**User:** "Use single quotes, not double quotes."

If the project has Prettier or ESLint configured with a quotes rule, decline: *"Your formatter already enforces single quotes — no CLAUDE.md rule needed; the linter will catch this automatically."*

## Questions This Skill Answers

- "Can you codify that?"
- "Add this to the project conventions."
- "Save this as a rule."
- "Remember that for next time."
- "Make this a convention."
- "Write that down so you don't forget."
- "Put this in CLAUDE.md."
- "How do I make Claude remember this correction?"
- "In this project we always/never do X — save that."

## Scope Boundary

This skill writes to **project-level** `CLAUDE.md` only. User-level config (`~/.claude/CLAUDE.md`) is out of scope by design — personal preferences that span projects are a different concern. If a user asks for a user-level rule, decline and explain the scope.

This skill does not prune or update existing rules wholesale — that's a separate maintenance concern. It appends new rules and flags direct contradictions with existing ones, but quarterly review/pruning of CLAUDE.md is explicitly out of scope.
