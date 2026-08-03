---
name: worktree-create
description: "INVOKE THIS SKILL when the user wants to start an isolated piece of work in a fresh git worktree — e.g. 'spin up a worktree', 'create a worktree for this', 'let me work on X in a separate worktree', 'give me an isolated branch/checkout to try Y', or runs a /worktree-create entry point. Asks for the task TYPE (feature/fix/refactor/spike/chore/docs/review) and a short description, then creates a git worktree at a SIBLING path `../<project>-WT/<you>/<type>-<desc>` on a new branch `<you>/<type>-<desc>`, symlinks the main repo's git-ignored `.env*` files (`.env`, `.env.prod`, `.env.test`, etc.) into the worktree so runtime config git never copies is available, reserves collision-free SDD artifact numbers (next free ADR `NNNN` and SPEC/RESEARCH `NNN`) by scanning every live worktree, every branch's history, and sibling worktrees' own reservations, and writes a `WORKTREE.md` breadcrumb recording the base branch, base commit, main-repo path, linked env files, and reserved numbers. Pairs with the `worktree-handoff` skill, which merges the work back and cleans the worktree up. Does NOT nest the worktree inside the repo; does NOT commit or push."
---

# Worktree Create

Spins up an **isolated git worktree** so a discrete task can be done on its own branch, in its own directory, in its own Claude Code session — without disturbing the main working tree. The worktree lives *beside* the repo (never nested inside it), and carries a `WORKTREE.md` breadcrumb so the companion `worktree-handoff` skill can later merge the work back and delete the worktree with no guesswork.

Because a worktree checks out from a **commit**, git-ignored files never travel into it — a fresh worktree has no `.env` or other secret/config files, since git doesn't track them. This skill closes that gap: it **symlinks the main repo's git-ignored `.env*` files** (`.env`, `.env.prod`, `.env.test`, `.env.local`, …) into the new worktree, so the isolated checkout can run against the same config without hand-copying secrets.

A worktree checking out from a commit creates a second, subtler gap: **sequentially numbered artifacts**. Two worktrees branched off the same commit see the same `SDD/adr/` and `SDD/requirements/`, so both independently compute the same "next" number and both create an ADR `0008` or a `SPEC-042`. Because the filenames differ (`0008-use-postgres.md` vs. `0008-adopt-grpc.md`), git merges both **without a conflict** and the duplicate is discovered long after the fact. This skill closes that gap too: it **reserves the next free numbers up front** and records them in the breadcrumb, so each worktree starts from a number no sibling can claim.

This skill is the **spin-up half** of a two-skill lifecycle:

1. **`worktree-create`** (this skill) — start the isolated worktree.
2. **`worktree-handoff`** — generate a handoff from inside the worktree, then merge + clean up from the main repo.

## Expert Vocabulary

Git worktree. Linked worktree vs. main worktree. Sibling placement (out-of-tree). Detached vs. branch-backed worktree. Branch namespace (`user/task` slash form). Task type taxonomy (feature/fix/refactor/spike/chore/docs/review). Slugification. Base branch / base commit. Breadcrumb metadata (`WORKTREE.md`). Path collision. Branch collision. Isolation of working state. Quoting paths with spaces. Git-ignored files (never checked out into a worktree). `.env` family / dotenv files. `git check-ignore` (consults `.gitignore`). Symbolic link (absolute-target). Shared vs. isolated config. Secret leakage. Sequential artifact numbering (ADR `NNNN`, SPEC/RESEARCH `NNN`). Number-space collision. Silent (conflict-free) merge of duplicate numbers. Reservation / high-water mark. `git worktree list --porcelain`. `git log --all --diff-filter=A` (added-file history). Monotonic allocation.

## Anti-Pattern Watchlist

Before running `git worktree add`, check the plan against these:

1. **Nested worktree.** Placing the worktree *inside* the repo's own working tree (e.g. `<repo>/WT/...`). Detection: the computed worktree path has the repo toplevel as an ancestor. Resolution: never nest — git would treat it as untracked clutter and it can corrupt status/ignore logic. Always place under a **sibling** root `<parent-of-repo>/<project>-WT/`.
2. **Worktree-of-a-worktree.** Running this while already inside a linked worktree, so the new worktree bases off half-finished branch state. Detection: `git rev-parse --git-dir` contains `/worktrees/`. Resolution: warn the user they're already in a worktree, and confirm they want to branch from *here* rather than from the main repo before proceeding.
3. **Silent branch/path collision.** A branch or directory with the computed name already exists, and the command either fails cryptically or clobbers. Detection: `git rev-parse --verify <branch>` succeeds, or the target path already exists. Resolution: stop and surface the conflict; offer a suffixed name (`-2`) or reusing/removing the existing one — never overwrite silently.
4. **Copying dirty state by accident.** The user assumes uncommitted changes in the main tree travel into the worktree. Detection: main working tree is dirty at creation time. Resolution: clarify that a new worktree starts from the **base commit**, not from uncommitted edits — those stay in the main tree. Offer to base off a different branch/commit if that's not what they want.
5. **Unquoted paths.** The repo or parent path contains spaces (common on macOS), and an unquoted command splits the path. Detection: any path in a command not wrapped in quotes. Resolution: quote every path in every command.
6. **Missing breadcrumb.** Creating the worktree but not recording where it came from, so `worktree-handoff` later can't find the main repo or base. Detection: no `WORKTREE.md` written. Resolution: always write the breadcrumb as the last creation step.
7. **Committing or pushing on the user's behalf.** Detection: any `git commit`/`git push` in this skill. Resolution: this skill only *creates* the worktree — the user does the work. Do not commit or push.
8. **Symlinking a *tracked* env file.** Linking an env file that git already tracks (e.g. a committed `.env.example`). Detection: `git check-ignore -q "<file>"` returns non-zero (the file is NOT ignored). Resolution: only symlink git-ignored files — a tracked env file is already in the worktree's checkout, and linking over it would clobber the real checked-out copy. Filter every candidate through `git check-ignore`.
9. **Clobbering an existing worktree file with a symlink.** A file with the same name already exists at the worktree path (a tracked template, or a link from a rerun). Detection: `[ -e "<worktree>/<name>" ]` before linking. Resolution: skip and report it; never overwrite. A rerun of this skill is thus idempotent (existing links are left alone).
10. **Assuming a symlink gives the worktree its *own* env.** A symlink points at the *same* main-repo file — editing env in the worktree edits it everywhere, and vice versa. Detection: the user expects to diverge the worktree's config from main. Resolution: clarify that symlinks share one file; if they want an independent env, copy (`cp`) instead of linking. Default remains symlink (the user asked for it and it's usually the intent for secrets).
11. **Leaking secrets to the wrong place.** Symlinking env files into a worktree that is itself inside a synced/shared or world-readable location. Detection: worktree root under a cloud-synced or shared path. Resolution: the sibling-root placement (Anti-Pattern 1) keeps it beside the repo; note that the links expose the same secrets there, and skip linking if the user objects.
12. **Number reservation computed from the local checkout only.** Deriving the next ADR/SPEC number from `ls SDD/adr/` in one directory — exactly what the allocating skills do on their own, and exactly why sibling worktrees collide. Detection: the scan reads only the main repo (or only the new worktree). Resolution: the scan MUST union all four sources in Step 7 — every live worktree's files on disk (catches *uncommitted* in-flight artifacts), every branch's added-file history (catches unmerged or already-removed worktrees), and sibling `WORKTREE.md` reservations (catches worktrees created but not yet used). Dropping any one source reintroduces the collision.
13. **Reserving a number and then not telling anyone.** Writing the reservation into `WORKTREE.md` but leaving the worktree session to recompute a number locally anyway. Detection: the final report doesn't state the reserved numbers, or `WORKTREE.md` records them without the "do not recompute locally" instruction. Resolution: the reservation is only load-bearing if it is *honored* — state it in the report (Step 9) and phrase the breadcrumb as a directive so the session and the `cross-cutting-adr` skill both consume it.
14. **Treating the reservation as a hard quota.** Assuming the worktree may create exactly one ADR and one SPEC. Detection: the user asks "what if I need two ADRs?" and the answer is "you can't." Resolution: the reserved number is a **starting point**, not a cap — the worktree increments from there. The next `worktree-create` run finds those files on disk (source 1) and starts above them, so the scheme self-heals. Say "start here", never "you get one".
15. **Blocking on the reservation in a repo that doesn't use SDD.** Running the scan, finding nothing, and reporting an error or asking the user what number to use. Detection: the scan yields no numbered artifacts. Resolution: this is the normal case for most repos — skip the step silently, omit the line from the breadcrumb and report, and move on. Never create an `SDD/` directory here; this skill does not scaffold SDD.

## When to Activate

- The user asks to start work in an isolated worktree: "spin up a worktree", "create a worktree for the auth refactor", "give me a separate checkout to try this", "I want to work on X without touching main".
- The user runs a `/worktree-create` entry point (if wired up).
- The user describes wanting to parallelize or sandbox a task off the current branch and a worktree is the natural fit.

## When NOT to Activate

- **The user just wants a branch, not a separate directory.** A plain `git checkout -b` in place is simpler; don't impose a worktree.
- **They're inside a worktree and want to hand it back.** That's `worktree-handoff`, not this skill.
- **Not in a git repository.** If `git rev-parse --show-toplevel` fails, tell the user to `git init` or move into a repo first; do not proceed.
- **The user wants a full clone or a fork.** Worktrees share one `.git`; if they need an independent clone, this isn't it.

## Behavioral Instructions

Execute in order. Every command must quote paths (repo paths on this machine contain spaces).

### Step 1: Verify the context

Run:

```bash
git rev-parse --show-toplevel        # fails → not a repo; stop and tell the user
git rev-parse --git-dir              # contains "/worktrees/" → already in a linked worktree (Anti-Pattern 2)
git rev-parse --abbrev-ref HEAD      # current branch (the default base)
git status --porcelain               # note if dirty (for the Step 4 clarification)
```

If not in a repo, stop. If already inside a linked worktree, warn and confirm the base before continuing.

### Step 2: Ask for the task type and description

If the user hasn't already said, ask for **both**:

- **Task type** — one of: `feature`, `fix`, `refactor`, `spike` (experiment/throwaway), `chore`, `docs`, `review`. This becomes a reference to the kind of work, embedded in the branch and directory name.
- **Short description** — a few words naming the specific task (e.g. "login redirect bug").

Keep it to one question if you can (e.g. "What kind of task, and a short name for it?").

### Step 3: Compute the names

- **Project** = basename of the repo toplevel (e.g. `claude-plugins`).
- **You** = `git config user.name` slugified to lowercase kebab (spaces → `-`, drop non-`[a-z0-9-]`). Fallback to `$USER` if `user.name` is empty. (e.g. `Pablo Oliva` → `pablo-oliva`).
- **Task slug** = `<type>-<description-slug>` (e.g. `fix-login-redirect`).
- **Branch** = `<you>/<task-slug>` (e.g. `pablo-oliva/fix-login-redirect`). The slash namespaces the branch under you; git allows it.
- **Worktree root** = `<parent-of-toplevel>/<project>-WT` (a sibling of the repo).
- **Worktree path** = `<worktree-root>/<you>/<task-slug>`.
- **Base** = current branch's HEAD by default (Step 1). If the user wants to start from an up-to-date `main` or another ref, use that instead — confirm if the current branch isn't the default branch.

### Step 4: Check for collisions and clarify state

- If the branch already exists (`git rev-parse --verify --quiet "<branch>"`), or the worktree path already exists, **stop** and offer: a suffixed name (`<task-slug>-2`), or reusing the existing worktree, or removing it first. Never clobber.
- If the main tree was dirty (Step 1), note that the worktree starts from the **base commit**, so uncommitted edits stay in the main tree (Anti-Pattern 4). Offer a different base if that's not intended.

### Step 5: Create the worktree

```bash
mkdir -p "<worktree-root>/<you>"
git worktree add -b "<branch>" "<worktree-path>" "<base>"
```

(Omit the trailing `<base>` to use current HEAD.) Confirm the command succeeded via `git worktree list`.

### Step 6: Symlink git-ignored env files into the worktree

A worktree checks out from a commit, so **git-ignored files never come with it** — the fresh worktree has no `.env`. Link the main repo's git-ignored env files in so the isolated checkout can run against the same config.

**Discover** the candidates — every `.env`-family file at the main repo root that git actually ignores. Use `git check-ignore`, which consults `.gitignore` for real (robust; no glob-pattern parsing), and keep only ignored files (a *tracked* `.env.example` is already in the checkout — Anti-Pattern 8):

```bash
# Run against the MAIN repo toplevel ("<main>"); "<worktree-path>" is the new worktree.
find "<main>" -maxdepth 1 -type f \( -name '.env' -o -name '.env.*' \) | while IFS= read -r f; do
  git -C "<main>" check-ignore -q "$f" || continue   # skip tracked env files (Anti-Pattern 8)
  name="$(basename "$f")"
  dest="<worktree-path>/$name"
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    echo "skip (exists): $name"                        # never clobber (Anti-Pattern 9)
    continue
  fi
  ln -s "$f" "$dest"                                    # absolute target → resolves from anywhere
  echo "linked: $name"
done
```

Notes and clarifications:

- **Absolute target.** `find` yields an absolute `$f`, so the symlink resolves regardless of the worktree's location. Do not use a relative target.
- **This matches `.env`, `.env.prod`, `.env.test`, `.env.local`, `.env.production`, …** — any `.env.*` variant at the repo root, plus bare `.env`.
- **Shared, not isolated (Anti-Pattern 10).** A symlink shares the *one* main-repo file — edits in the worktree change it everywhere. That's the usual intent for secrets. If the user wants the worktree to have an independent env it can diverge, `cp` instead of `ln -s`.
- **Parent-directory env (the "directory that contains the main repo" case).** If the project keeps a shared env file one level *up* (in the parent of the repo) rather than at the repo root, and the repo root has none, offer to link that parent-level file too — same `check-ignore` + no-clobber rules. Do this only when it applies; the default source is the repo root.
- **If nothing is found,** say so briefly and move on — many repos have no `.env` (this one, `claude-plugins`, has none). Do not treat it as an error.
- **Idempotent.** Rerunning leaves existing links untouched.

Record the linked filenames for the breadcrumb (Step 8) and the final report (Step 9).

### Step 7: Reserve SDD artifact numbers (skip silently if the repo has none)

Sequentially numbered SDD artifacts collide across worktrees, because the skills that allocate them look only at their own working directory: `cross-cutting-adr` takes the highest `SDD/adr/NNNN-*` it can `ls` locally, and the SDD flow's `[###]` (shared by `CLARIFICATION` → `RESEARCH` → `SPEC` → `IMPLEMENTATION-PLAN`) is likewise "next sequential". Two worktrees off the same base therefore both pick the same number, and the duplicate merges **cleanly** — different filenames, no conflict. Reserve up front instead.

**Scan all four sources** and take the high-water mark. Run this against the main repo toplevel (`"<main>"`); every path is quoted because repo paths contain spaces:

```bash
names="$(
  {
    # (1) Files on disk in EVERY live worktree — catches in-flight, uncommitted artifacts.
    # (3) Sibling reservations — catches worktrees created but not yet used.
    git -C "<main>" worktree list --porcelain | sed -n 's/^worktree //p' | while IFS= read -r wt; do
      find "$wt/SDD" -type f -name '*.md' 2>/dev/null
      [ -f "$wt/WORKTREE.md" ] && grep -h 'SDD numbers reserved' "$wt/WORKTREE.md"
    done
    # (2) Every file ever ADDED under SDD/ on ANY branch — catches unmerged or removed worktrees.
    git -C "<main>" log --all --pretty=format: --name-only --diff-filter=A -- 'SDD/*'
  } | sort -u
)"

adr_max="$(printf '%s\n'  "$names" | grep -oE 'SDD/adr/[0-9]{4}|ADR-[0-9]{4}' | grep -oE '[0-9]{4}$' | sort -n | tail -1)"
spec_max="$(printf '%s\n' "$names" | grep -oE '[A-Z][A-Z-]*-[0-9]{3}'         | grep -oE '[0-9]{3}$' | sort -n | tail -1)"

printf 'ADR-%04d  SPEC-%03d\n' "$((10#${adr_max:-0} + 1))" "$((10#${spec_max:-0} + 1))"
```

Notes and clarifications:

- **The gate is "were any numbers found", not "does `SDD/` exist".** If both `adr_max` and `spec_max` come back empty, this repo keeps no numbered SDD artifacts — skip the step entirely, omit the line from the breadcrumb and the report, and do not create `SDD/` (Anti-Pattern 15). A directory named `SDD/` holding non-artifact files matches nothing, which is the correct outcome.
- **Why source (2) matters.** A worktree whose branch was never merged, or that was removed after committing, leaves no directory to scan — but its added files are still in `--all` history, so its numbers stay claimed.
- **Why source (3) matters.** Two worktrees created back-to-back have written no artifacts yet. Without reading each other's `WORKTREE.md`, both reserve the same number and Option A buys nothing. This is the source that makes reservation work.
- **The `[A-Z][A-Z-]*-[0-9]{3}` pattern** deliberately matches every SDD prefix generically — `SPEC-`, `RESEARCH-`, `CLARIFICATION-`, `DECOMPOSITION-`, `IMPLEMENTATION-PLAN-`, `IMPLEMENTATION-SUMMARY-`, `SLICE-`, `REVIEW-` — rather than enumerating them, so a new artifact type can't silently escape the sweep. Over-matching is safe: it only skips a number, and skipping is never a collision.
- **A start, not a quota (Anti-Pattern 14).** The worktree uses the reserved number and increments from it for further artifacts. The next `worktree-create` sees those files via source (1) and starts above them — the scheme self-heals without central bookkeeping.
- **Not a lock.** Nothing prevents someone editing files by hand. The reservation is a strong convention recorded in the breadcrumb, not enforcement.

Record both reserved numbers for the breadcrumb (Step 8) and the final report (Step 9).

### Step 8: Write the breadcrumb

Write `WORKTREE.md` at the worktree path root (see **Output Format**), recording: task type, description, branch, base branch, base commit SHA, main-repo absolute path, the env files symlinked in (Step 6), the reserved SDD numbers (Step 7, omit the line if none), and creation context. This is what `worktree-handoff` reads to merge back — and what the *next* `worktree-create` run reads as scan source (3), so the reserved-numbers line must keep the literal marker text `SDD numbers reserved` for that grep to find it. (It lives only in the worktree and disappears when the worktree is removed — do not commit it unless the user wants to; if the repo would otherwise track it, mention it so they can `.gitignore` or commit as they prefer.)

### Step 9: Report and point to the next step

Tell the user:

- The worktree path and the branch name.
- The reserved SDD numbers, if any — and that the session there should *use* them rather than recompute (Anti-Pattern 13). Omit entirely when Step 7 found nothing.
- How to enter it: `cd "<worktree-path>"` — and recommend starting a **fresh Claude Code session** there so the isolated work gets its own context.
- That when the work is done, they invoke **`worktree-handoff`** from *inside* the worktree to generate the merge-back handoff.

Do not commit, push, or start doing the task itself.

## Output Format

Final report to the user:

```
Worktree created ✓

  Branch:    pablo-oliva/fix-login-redirect
  Location:  ../claude-plugins-WT/pablo-oliva/fix-login-redirect
  Based on:  main @ 695d075
  Env links: .env, .env.prod, .env.test  (symlinked from the main repo; shared, not copies)
  Reserved:  ADR-0011, SPEC-045  (start here — do not recompute locally; 2 sibling worktrees scanned)

Next:
  cd "/Volumes/.../claude-plugins-WT/pablo-oliva/fix-login-redirect"
  # start a new Claude Code session there and do the work
  # when done, run the worktree-handoff skill from inside it
```

(Omit the `Env links:` line, or show `Env links: none found`, when the main repo has no git-ignored env files. Omit the `Reserved:` line entirely when Step 7 found no numbered SDD artifacts — the common case.)

`WORKTREE.md` breadcrumb written into the worktree:

```markdown
# Worktree: fix-login-redirect

- **Task type:** fix
- **Description:** login redirect bug
- **Branch:** pablo-oliva/fix-login-redirect
- **Base branch:** main
- **Base commit:** 695d075
- **Main repo:** /Volumes/Crucial Data/Documents/Code & Dev/claude-plugins
- **Env links:** `.env`, `.env.prod`, `.env.test` (symlinked from the main repo; `none` if there were none)
- **SDD numbers reserved:** ADR-0011, SPEC-045 — start here; do NOT recompute from the local `SDD/` directory
- **Created:** from `worktree-create`

<!-- Read by the worktree-handoff skill to merge this branch back and remove the worktree. -->
<!-- Env links are symlinks into the main repo — removing the worktree removes the links, not the originals. -->
<!-- The reserved numbers were computed across ALL live worktrees, all branch history, and sibling
     reservations, so no other worktree can claim them. Use ADR-0011 for the first ADR written here
     and increment locally for any further ones; same for SPEC-045 across the CLARIFICATION →
     RESEARCH → SPEC → IMPLEMENTATION-PLAN chain, which all share one [###].
     Keep the literal text "SDD numbers reserved" on that line — the next worktree-create run
     greps for it so it can start above this reservation. Omit the line if none were reserved. -->
```

## Examples

### GOOD — spin up a fix worktree

**User:** "Spin up a worktree so I can fix the login redirect without touching main."

1. Confirm in-repo, current branch `main` @ `695d075`.
2. Ask (if needed): type `fix`, description "login redirect".
3. Compute branch `pablo-oliva/fix-login-redirect`, path `../claude-plugins-WT/pablo-oliva/fix-login-redirect`.
4. No collision.
5. `git worktree add -b pablo-oliva/fix-login-redirect "<path>" main`.
6. Symlink git-ignored env files: `find` the repo root's `.env*`, keep the ones `git check-ignore` confirms are ignored, `ln -s` each into the worktree (skipping any that already exist). Say "linked `.env`, `.env.prod`" — or "no env files to link" if there are none.
7. Reserve SDD numbers: scan all live worktrees, all branch history, and sibling reservations; no numbered artifacts found, so skip the step and say nothing about it.
8. Write `WORKTREE.md` (including the linked env files).
9. Report path + branch + env links + "start a new session there; run worktree-handoff when done."

### GOOD — env files linked in

**User:** "Make a worktree for the payments spike — I'll need the API keys from `.env`."

The main repo root has git-ignored `.env` and `.env.test` (both matched by `git check-ignore`) and a tracked `.env.example`. After `git worktree add`, symlink `.env` and `.env.test` into the worktree (absolute targets) and **skip `.env.example`** — it's tracked, so it's already in the checkout and linking would clobber it (Anti-Pattern 8). Report: "Env links: `.env`, `.env.test` (symlinked — shared with main, not copies)."

### GOOD — numbers reserved around two sibling worktrees

**User:** "Spin up a worktree for the audit-logging feature."

The repo uses SDD. The Step 7 scan finds: `SDD/adr/0007-*` committed on `main`; an uncommitted `SDD/adr/0008-*` and `SPEC-042-*` sitting in a live worktree (`feature-a`) that hasn't committed yet; a `WORKTREE.md` in another live worktree (`feature-b`) reserving `ADR-0009, SPEC-043`; and `SDD/adr/0010-*` plus `SPEC-044-*` added on an unmerged branch whose worktree is already gone. High-water marks: ADR `0010`, SPEC `044`. Reserve **ADR-0011 / SPEC-045**, write them into `WORKTREE.md`, and report them. Note that three of those four numbers are invisible to a plain `ls SDD/adr/` in the main repo — which is precisely the collision this step prevents.

### BAD — reserving from the main repo alone

Running `ls SDD/adr/*.md | tail -1` in the main repo, seeing `0007`, and reserving `0008`. Wrong: `0008` is already in use in an uncommitted state inside a sibling worktree, so both will write an ADR `0008` and the two will merge with no conflict. **Right:** union all four sources (Anti-Pattern 12) before taking the high-water mark.

### BAD — nesting inside the repo

Computing the path as `<repo>/WT/pablo-oliva/fix-login-redirect`. Wrong: git would see `WT/` as untracked files inside the working tree. **Right:** place it at the sibling root `<parent>/<project>-WT/...`, outside the repo entirely.

### BAD — clobbering an existing branch

Branch `pablo-oliva/fix-login-redirect` already exists from a prior attempt. Wrong: forcing `git worktree add` and losing the old branch. **Right:** stop, surface the conflict, offer `fix-login-redirect-2` or reusing/removing the old worktree.

## Questions This Skill Answers

- "Spin up a worktree for this task."
- "Create an isolated worktree/branch so I don't touch main."
- "Give me a separate checkout to experiment in."
- "Start a worktree for the auth refactor."
- "I want to work on X in its own directory."

## Scope Boundary

This skill **creates** a single sibling worktree, symlinks the main repo's git-ignored `.env*` files into it, reserves collision-free SDD artifact numbers, and writes its breadcrumb — and nothing more. It does not commit, push, run the task, or merge anything. It links only git-ignored env files (tracked ones are already in the checkout) and never overwrites an existing file at the worktree path. Number reservation is **advisory and creation-time only**: it records a starting number no sibling worktree can claim, but it does not lock anything, does not renumber existing artifacts, does not scaffold `SDD/` in repos that lack it, and does not write any SDD artifact itself — `cross-cutting-adr` and the SDD flow still author those, honoring the reserved number from `WORKTREE.md`. Merging the work back and removing the worktree — which drops the symlinks but leaves the original env files untouched — is the job of the paired **`worktree-handoff`** skill. It operates only within one git repository (shared `.git`); it does not clone or fork.
