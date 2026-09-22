# Blind Site Count Compaction

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow’s flat-orchestration contract forbids it; all work happens inline in your own context.

You are reading this because your Reads-counter safety-net tripped during a **blind site count** (`bodies/site-count.md`). The read allowlist in that body still binds you while compacting: do not open any file it forbids.

## 1. Write the compaction file

Write `SDD/orchestration/compacted/site-count-compacted-[YYYY-MM-DD_HH-MM-SS].md`:

```markdown
# Site Count Compaction — <SCOPE> iter <N> — [timestamp]

## Assignment
- **Scope:** <SCOPE>   **Iteration:** <N>   **Code range:** <range>
- **OUTPUT (not yet written):** <OUTPUT path>
- **SPEC / glossary / standard paths:** <paths>

## Controls in Scope
<ID — one-line rule — status: done | in progress | not started>

## Rows Found So Far
<The `## Site Inventory` rows you have already established, in the final table shape.>

## Current Focus
<The control, entry point, and path you were tracing when the trigger fired.>

## Remaining
<Controls and entry points not yet traced.>
```

Record only what you derived from the SPEC and production code. This file is the successor's sole carry-over, and it inherits your blindness: it must contain nothing from forbidden sources.

## 2. Append to `progress.md` (append only — do not read it)

```markdown
## PARTIAL: needs continuation

- **Step:** blind site count <SCOPE> iter <N>
- **Compaction:** SDD/orchestration/compacted/site-count-compacted-[timestamp].md
- **Left off at:** <control / entry point>
```

## 3. Return

≤100 words stating a Mid-Phase Handoff is required, with the compaction path.
