---
name: todo-tidy
description: "INVOKE THIS SKILL when the user asks to tidy, organize, reformat, clean up, or restructure a running scratch/TODO file (e.g. 'tidy my scratch.md', 'organize my todos', 'reformat TODO.md', 'turn scratch.md into a proper TODO'), or to convert a `scratch.md` working list into a `TODO.md`. Finds `scratch.md` and/or `TODO.md` in the project, promotes `scratch.md` to `TODO.md` (folding both together when both exist), and reorganizes the contents hierarchically, visually, and structurally into a consistent checkbox-list format. It reformats only — it does NOT investigate, answer, resolve, or reprioritize the items, never drops content, and never edits `.gitignore` (it only checks and warns)."
---

# TODO Tidy

Promotes a free-form `scratch.md` working list into a well-structured `TODO.md`, and reorganizes an existing `TODO.md`, so an ever-growing pile of side-quests and follow-ups stays navigable. This skill is a **reformatter**, not a worker: it restructures what is written without acting on any item.

## What This Skill Does and Does Not Do

- **Does:** locate `scratch.md`/`TODO.md`, rename/merge to a single `TODO.md` (or create a fresh `TODO.md` when neither file exists), and reorganize the contents into a consistent, hierarchical, visually scannable checkbox list — preserving every item verbatim.
- **Does NOT:** investigate, research, answer, resolve, or start any listed task; invent priorities, statuses, due dates, or owners that aren't in the source; delete or silently drop any item; or edit `.gitignore` (the user owns that entry — this skill only checks it and warns).

## Expert Vocabulary

Working scratch list. Side-quest capture. Inbox / triage list. GitHub task-list checkbox (`- [ ]` / `- [x]`). Hierarchical outline. Section grouping by theme/area. Idempotent reformat. Content-preserving transform. File promotion (`scratch.md` → `TODO.md`). Merge-and-dedupe. `.gitignore` coverage check. Non-destructive rename. Faithful round-trip.

## Anti-Pattern Watchlist

Before writing the new `TODO.md`, check the output against these patterns:

1. **Task execution.** Treating a listed item as an instruction to perform (e.g. seeing "fix the flaky login test" and fixing it). Detection: any tool use beyond reading the todo files, `.gitignore`, and moving/writing the todo file itself. Resolution: stop — this skill only reformats text. Items stay as text.
2. **Content loss.** An item present in the source is missing from the output. Detection: the output has fewer distinct items than the input. Resolution: never drop an item; if a fragment is ambiguous or uncategorizable, keep it verbatim under an `## Inbox` (unsorted) section rather than discarding it.
3. **Fabricated metadata.** Inventing priorities ("P1"), statuses ("in progress"), owners, or dates the source never stated. Detection: metadata in the output that has no basis in the input. Resolution: only carry over signals that already exist in the text.
4. **Substantive rewording.** Rephrasing an item so its meaning could shift. Detection: the item's wording changed beyond trivial cleanup. Resolution: limit edits to trivial cleanup only — capitalization, trailing whitespace, checkbox normalization. Preserve the user's phrasing, and preserve verbatim all code refs (`path:line`), URLs, ticket/issue IDs, commands, and quoted text.
5. **`.gitignore` mutation.** Editing `.gitignore` to add `TODO.md`. Detection: any write to `.gitignore`. Resolution: never edit it — the user explicitly handles that. Only read it and warn if `TODO.md` isn't covered.
6. **Over-categorization.** Manufacturing many fine-grained section headings when the source gives no grouping cues. Detection: sections with one item each, invented category names. Resolution: infer groups only from cues already present (existing headings, `[area]` prefixes, obvious clusters). When there are no cues, keep a single flat list rather than imposing a taxonomy.
7. **Non-idempotent output.** Re-running the skill on an already-tidy `TODO.md` churns the structure. Detection: the second run produces materially different grouping/ordering from the first. Resolution: converge on a stable shape so repeated runs are near no-ops.

## When to Activate

Activate when the user does any of these:

- Runs the skill explicitly (e.g. via a `/todo-tidy` entry point, if one is wired up).
- Asks to tidy / organize / clean up / reformat / restructure their todo or scratch file: "tidy my scratch.md", "organize my todos", "reformat TODO.md", "make my scratch list readable".
- Asks to convert or promote a scratch list: "turn scratch.md into a TODO", "rename scratch.md to TODO.md and clean it up".

## When NOT to Activate

- **The user wants an item done, not the list reorganized.** "Do the first thing on my TODO" is task execution — out of scope.
- **A structured issue tracker is the real target.** If the user is talking about GitHub Issues, Jira, Linear, etc., this skill (which operates on a local markdown file) does not apply.
- **A different working file is meant.** If the user points at some other notes file (not `scratch.md`/`TODO.md`) and doesn't want it promoted to a `TODO.md`, this skill doesn't apply.

## Behavioral Instructions

Execute in order. The only files this skill may modify are the todo file itself (`scratch.md` → `TODO.md`). Never modify `.gitignore` or any source file.

### Step 1: Locate the files

Search the project root (and, if the user pointed at a subdirectory, that directory) for:

- `scratch.md` — the free-form working list.
- `TODO.md` — the structured target (uppercase `TODO`).

Match the filenames case-insensitively so a `Scratch.md` or `todo.md` is still found, but always write the target as uppercase **`TODO.md`**.

### Step 2: Determine the operation

Based on what exists:

| `scratch.md` | `TODO.md` | Operation |
|:---:|:---:|---|
| yes | no  | **Promote** — rename `scratch.md` to `TODO.md`, then reformat. |
| no  | yes | **Reformat in place** — reorganize the existing `TODO.md`. |
| yes | yes | **Merge** — fold `scratch.md`'s items into `TODO.md`, reformat the combined list, then remove `scratch.md`. Deduplicate only items that are clearly identical; when in doubt, keep both. |
| no  | no  | **Create** — no working list exists yet; create a fresh empty `TODO.md` skeleton (see **Output Format**) so future side-quests have a home. No confirmation needed. |

### Step 3: Check `.gitignore` (read-only)

Read `.gitignore` and determine whether the resulting `TODO.md` is matched by any pattern.

- If `scratch.md` was ignored but `TODO.md` is **not** covered, warn the user in the final summary: the todo file will now be visible to Git, and if they want it kept out of version control they should add `TODO.md` to `.gitignore` themselves.
- If `TODO.md` is already covered, note that briefly.
- **Never edit `.gitignore`.** The user handles that entry.

### Step 4: Reformat the contents

Reorganize the combined content into the target structure (see **Output Format**), applying every rule in the Anti-Pattern Watchlist. Reformatting is structural: group, nest, and normalize — never resolve, answer, or reprioritize.

### Step 5: Write and clean up

1. Write the reorganized content to `TODO.md`.
2. If the operation was **Promote** or **Merge**, remove the old `scratch.md` (a rename for Promote; a delete-after-merge for Merge). Use `git mv`/`git rm` only if the file is actually tracked; since `scratch.md` is typically gitignored, a plain filesystem move/remove is correct.
3. Do not leave both files behind — the end state is a single `TODO.md`.

### Step 6: Report

Give a short summary: which operation ran, how many items were carried over (and that none were dropped), the section headings produced, and the `.gitignore` warning if applicable. Do not comment on the substance of the tasks.

## Output Format

The reorganized `TODO.md` follows this shape:

```markdown
# TODO

<!-- Optional one-line intro, only if the source already had one. -->

## <Area / theme, only when the source gives grouping cues>

- [ ] Actionable item, phrasing preserved
  - [ ] Nested follow-up or sub-task
  - Note or context (non-actionable) kept as a plain bullet
- [ ] Item with a preserved reference — see `src/auth/session.ts:142`
- [ ] Item with a preserved link — https://example.com/issue/123

## Inbox

<!-- Items with no clear home go here verbatim, never dropped. -->

- [ ] Ambiguous fragment kept as-is

## Done

- [x] Completed item preserved from the source
```

Formatting rules:

- **H1 `# TODO`** at the top.
- **Actionable items** become GitHub task-list checkboxes: `- [ ]` for open, `- [x]` for done. Items already marked done or struck through map to `- [x]`.
- **Sub-tasks and follow-ups** nest as indented children under their parent.
- **Non-actionable context** (notes, links, references) stays as plain bullets so it isn't misread as a task.
- **Sections (`##`)** group items by area/theme *only when the source provides cues* (existing headings, `[tag]`/`area:` prefixes, obvious clusters). With no cues, use a single flat list.
- **`## Inbox`** holds anything uncategorizable — nothing is discarded.
- **`## Done`** (optional, at the bottom) collects completed items.
- Preserve verbatim: code refs (`path:line`), URLs, ticket/issue IDs, commands, and quoted text.

When the **Create** operation runs (neither file existed), write this minimal skeleton — a header and an empty `## Inbox` for the first captured item — and nothing more:

```markdown
# TODO

## Inbox

<!-- Capture side-quests and follow-ups here; run todo-tidy to reorganize. -->
```

## Examples

### GOOD — promote a messy scratch list

**`scratch.md` (input):**

```
- fix flaky login test - fails ~1/10 in CI
random: check if the retry config in src/http/client.ts:88 is even used
DONE: bumped node to 20
docs - the README install steps are out of date
also the README is missing the env var table
idea: maybe cache the token lookups?
```

**`TODO.md` (output):**

```markdown
# TODO

## Docs

- [ ] README install steps are out of date
- [ ] README is missing the env var table

## Code

- [ ] Fix flaky login test — fails ~1/10 in CI
- [ ] Check if the retry config in `src/http/client.ts:88` is even used
- [ ] Idea: maybe cache the token lookups?

## Done

- [x] Bumped node to 20
```

Every item is preserved, the two README lines cluster under a `Docs` heading (a cue that was already in the text), `DONE:` maps to the `Done` section, and the code reference is kept verbatim. Nothing was investigated or resolved.

### BAD — executing instead of reformatting

**`scratch.md`:** `- fix flaky login test`

**Wrong:** opening `login.test.ts` and attempting a fix.

**Right:** the line stays as `- [ ] Fix flaky login test` in `TODO.md`. This skill reorganizes the list; it does not work the list.

### BAD — mutating `.gitignore`

`scratch.md` is gitignored; after promotion `TODO.md` is not covered.

**Wrong:** adding `TODO.md` to `.gitignore`.

**Right:** leave `.gitignore` untouched and warn: *"Heads up — `scratch.md` was gitignored but `TODO.md` isn't matched by any `.gitignore` pattern, so it's now visible to Git. Add `TODO.md` to `.gitignore` yourself if you'd like to keep it out of version control."*

## Questions This Skill Answers

- "Tidy up my scratch.md."
- "Organize my todos."
- "Reformat TODO.md so it's readable."
- "Turn my scratch file into a proper TODO list."
- "Rename scratch.md to TODO.md and clean it up."
- "Group my todo items by area."

## Scope Boundary

This skill operates on a **single local markdown file** (`scratch.md` → `TODO.md`) at the project root (or a user-specified directory). It does not touch issue trackers, does not act on any listed task, and does not edit `.gitignore` or any source file. Its entire job is a faithful, content-preserving reorganization of the todo file's text.
