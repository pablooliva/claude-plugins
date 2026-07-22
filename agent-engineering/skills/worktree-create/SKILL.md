---
name: worktree-create
description: "INVOKE THIS SKILL when the user wants to start an isolated piece of work in a fresh git worktree — e.g. 'spin up a worktree', 'create a worktree for this', 'let me work on X in a separate worktree', 'give me an isolated branch/checkout to try Y', or runs a /worktree-create entry point. Asks for the task TYPE (feature/fix/refactor/spike/chore/docs/review) and a short description, then creates a git worktree at a SIBLING path `../<project>-WT/<you>/<type>-<desc>` on a new branch `<you>/<type>-<desc>`, symlinks the main repo's git-ignored `.env*` files (`.env`, `.env.prod`, `.env.test`, etc.) into the worktree so runtime config git never copies is available, and writes a `WORKTREE.md` breadcrumb recording the base branch, base commit, main-repo path, and linked env files. Pairs with the `worktree-handoff` skill, which merges the work back and cleans the worktree up. Does NOT nest the worktree inside the repo; does NOT commit or push."
---

# Worktree Create

Spins up an **isolated git worktree** so a discrete task can be done on its own branch, in its own directory, in its own Claude Code session — without disturbing the main working tree. The worktree lives *beside* the repo (never nested inside it), and carries a `WORKTREE.md` breadcrumb so the companion `worktree-handoff` skill can later merge the work back and delete the worktree with no guesswork.

Because a worktree checks out from a **commit**, git-ignored files never travel into it — a fresh worktree has no `.env` or other secret/config files, since git doesn't track them. This skill closes that gap: it **symlinks the main repo's git-ignored `.env*` files** (`.env`, `.env.prod`, `.env.test`, `.env.local`, …) into the new worktree, so the isolated checkout can run against the same config without hand-copying secrets.

This skill is the **spin-up half** of a two-skill lifecycle:

1. **`worktree-create`** (this skill) — start the isolated worktree.
2. **`worktree-handoff`** — generate a handoff from inside the worktree, then merge + clean up from the main repo.

## Expert Vocabulary

Git worktree. Linked worktree vs. main worktree. Sibling placement (out-of-tree). Detached vs. branch-backed worktree. Branch namespace (`user/task` slash form). Task type taxonomy (feature/fix/refactor/spike/chore/docs/review). Slugification. Base branch / base commit. Breadcrumb metadata (`WORKTREE.md`). Path collision. Branch collision. Isolation of working state. Quoting paths with spaces. Git-ignored files (never checked out into a worktree). `.env` family / dotenv files. `git check-ignore` (consults `.gitignore`). Symbolic link (absolute-target). Shared vs. isolated config. Secret leakage.

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

Record the linked filenames for the breadcrumb (Step 7) and the final report (Step 8).

### Step 7: Write the breadcrumb

Write `WORKTREE.md` at the worktree path root (see **Output Format**), recording: task type, description, branch, base branch, base commit SHA, main-repo absolute path, the env files symlinked in (Step 6), and creation context. This is what `worktree-handoff` reads to merge back. (It lives only in the worktree and disappears when the worktree is removed — do not commit it unless the user wants to; if the repo would otherwise track it, mention it so they can `.gitignore` or commit as they prefer.)

### Step 8: Report and point to the next step

Tell the user:

- The worktree path and the branch name.
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

Next:
  cd "/Volumes/.../claude-plugins-WT/pablo-oliva/fix-login-redirect"
  # start a new Claude Code session there and do the work
  # when done, run the worktree-handoff skill from inside it
```

(Omit the `Env links:` line, or show `Env links: none found`, when the main repo has no git-ignored env files.)

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
- **Created:** from `worktree-create`

<!-- Read by the worktree-handoff skill to merge this branch back and remove the worktree. -->
<!-- Env links are symlinks into the main repo — removing the worktree removes the links, not the originals. -->
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
7. Write `WORKTREE.md` (including the linked env files).
8. Report path + branch + env links + "start a new session there; run worktree-handoff when done."

### GOOD — env files linked in

**User:** "Make a worktree for the payments spike — I'll need the API keys from `.env`."

The main repo root has git-ignored `.env` and `.env.test` (both matched by `git check-ignore`) and a tracked `.env.example`. After `git worktree add`, symlink `.env` and `.env.test` into the worktree (absolute targets) and **skip `.env.example`** — it's tracked, so it's already in the checkout and linking would clobber it (Anti-Pattern 8). Report: "Env links: `.env`, `.env.test` (symlinked — shared with main, not copies)."

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

This skill **creates** a single sibling worktree, symlinks the main repo's git-ignored `.env*` files into it, and writes its breadcrumb — and nothing more. It does not commit, push, run the task, or merge anything. It links only git-ignored env files (tracked ones are already in the checkout) and never overwrites an existing file at the worktree path. Merging the work back and removing the worktree — which drops the symlinks but leaves the original env files untouched — is the job of the paired **`worktree-handoff`** skill. It operates only within one git repository (shared `.git`); it does not clone or fork.
