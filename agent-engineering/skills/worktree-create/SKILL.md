---
name: worktree-create
description: "INVOKE THIS SKILL when the user wants to start an isolated piece of work in a fresh git worktree — e.g. 'spin up a worktree', 'create a worktree for this', 'let me work on X in a separate worktree', 'give me an isolated branch/checkout to try Y', or runs a /worktree-create entry point. Asks for the task TYPE (feature/fix/refactor/spike/chore/docs/review) and a short description, then creates a git worktree at a SIBLING path `../<project>-WT/<you>/<type>-<desc>` on a new branch `<you>/<type>-<desc>`, COPIES the untracked runtime config git never checks out (the files listed in the repo's `.worktreeinclude`) and runs its `.env-setup.sh`/`.bb-env-setup.sh` to rewrite those copies for this worktree (the BB IDE contract), reserves collision-free SDD artifact numbers (next free ADR `NNNN` and SPEC/RESEARCH `NNN`) by scanning every live worktree, every branch's history, and sibling worktrees' own reservations, and writes a `WORKTREE.md` breadcrumb recording the base, main-repo path, what was copied, the env-setup result, and reserved numbers. BOTH `.worktreeinclude` AND an env-setup script are HARD REQUIREMENTS, checked before anything is created: if either is missing the skill STOPS with an error, having created no worktree and no branch. There is no symlink fallback. Pairs with the `worktree-handoff` skill, which merges the work back and cleans the worktree up. Does NOT nest the worktree inside the repo; does NOT commit or push."
---

# Worktree Create

Spins up an **isolated git worktree** so a discrete task can be done on its own branch, in its own directory, in its own Claude Code session — without disturbing the main working tree. The worktree lives *beside* the repo (never nested inside it), and carries a `WORKTREE.md` breadcrumb so the companion `worktree-handoff` skill can later merge the work back and delete the worktree with no guesswork.

Because a worktree checks out from a **commit**, git-ignored files never travel into it — a fresh worktree has no `.env` or other secret/config files, since git doesn't track them. This skill closes that gap using the [BB IDE worktree contract](https://github.com/get-bb/bb/blob/main/docs/worktrees.md), which has two halves and requires **both**:

1. **`.worktreeinclude`** — a gitignore-syntax file at the repo root listing the *untracked* files to **copy** into every new worktree.
2. **`.env-setup.sh`** (or `.bb-env-setup.sh`) — a per-repo provisioning script, run from the worktree root *after* the copies land, which rewrites those copies (absolute paths, ports, output dirs) to worktree-local values and verifies it did.

**Both are hard prerequisites.** A repo missing *either* one is not set up for this skill, and the skill **stops with an error** rather than improvising — checked in Step 1b, *before* any worktree or branch exists, so a failed check leaves nothing behind to clean up. There is **no symlink fallback**: a symlinked `.env` cannot be rewritten per-worktree, and a copy that is never rewritten still points at the main repo's production sinks. Half a provisioning contract is worse than none, because the result *looks* isolated and isn't.

The payoff is that the worktree ends up with its **own independent** config, deliberately diverged from main — which is why `worktree-handoff` must never write it back.

A worktree checking out from a commit creates a second, subtler gap: **sequentially numbered artifacts**. Two worktrees branched off the same commit see the same `SDD/adr/` and `SDD/requirements/`, so both independently compute the same "next" number and both create an ADR `0008` or a `SPEC-042`. Because the filenames differ (`0008-use-postgres.md` vs. `0008-adopt-grpc.md`), git merges both **without a conflict** and the duplicate is discovered long after the fact. This skill closes that gap too: it **reserves the next free numbers up front** and records them in the breadcrumb, so each worktree starts from a number no sibling can claim.

This skill is the **spin-up half** of a two-skill lifecycle:

1. **`worktree-create`** (this skill) — start the isolated worktree.
2. **`worktree-handoff`** — generate a handoff from inside the worktree, then merge + clean up from the main repo.

## Expert Vocabulary

Git worktree. Linked worktree vs. main worktree. Sibling placement (out-of-tree). Detached vs. branch-backed worktree. Branch namespace (`user/task` slash form). Task type taxonomy (feature/fix/refactor/spike/chore/docs/review). Slugification. Base branch / base commit. Breadcrumb metadata (`WORKTREE.md`). Path collision. Branch collision. Isolation of working state. Quoting paths with spaces. Git-ignored files (never checked out into a worktree). `.env` family / dotenv files. Symbolic link (why it is *rejected* here, not used). Shared vs. isolated config. Secret leakage. BB IDE worktree contract. Hard prerequisite / precondition gate. Fail-before-mutate (check before `git worktree add`). `.worktreeinclude` (gitignore-syntax include list of *untracked* files to copy). Negation pattern (`!`). `git ls-files -o -i --exclude-from` (untracked-and-matching). Tracked-takes-precedence. Copy-not-symlink provisioning. Per-repo env-setup script (`.env-setup.sh`, `.bb-env-setup.sh`). Provisioning run contract (cwd = worktree root, `env bash`, stdin closed, streamed output, 15-minute timeout, non-zero exit fails provisioning). Path rewrite / worktree-local absolute path. Un-rewritten env copy (unsandboxed). Abort semantics (remove worktree + branch on failed provision). Sequential artifact numbering (ADR `NNNN`, SPEC/RESEARCH `NNN`). Number-space collision. Silent (conflict-free) merge of duplicate numbers. Reservation / high-water mark. `git worktree list --porcelain`. `git log --all --diff-filter=A` (added-file history). Monotonic allocation.

## Anti-Pattern Watchlist

Before running `git worktree add`, check the plan against these:

1. **Nested worktree.** Placing the worktree *inside* the repo's own working tree (e.g. `<repo>/WT/...`). Detection: the computed worktree path has the repo toplevel as an ancestor. Resolution: never nest — git would treat it as untracked clutter and it can corrupt status/ignore logic. Always place under a **sibling** root `<parent-of-repo>/<project>-WT/`.
2. **Worktree-of-a-worktree.** Running this while already inside a linked worktree, so the new worktree bases off half-finished branch state. Detection: `git rev-parse --git-dir` contains `/worktrees/`. Resolution: warn the user they're already in a worktree, and confirm they want to branch from *here* rather than from the main repo before proceeding.
3. **Silent branch/path collision.** A branch or directory with the computed name already exists, and the command either fails cryptically or clobbers. Detection: `git rev-parse --verify <branch>` succeeds, or the target path already exists. Resolution: stop and surface the conflict; offer a suffixed name (`-2`) or reusing/removing the existing one — never overwrite silently.
4. **Copying dirty state by accident.** The user assumes uncommitted changes in the main tree travel into the worktree. Detection: main working tree is dirty at creation time. Resolution: clarify that a new worktree starts from the **base commit**, not from uncommitted edits — those stay in the main tree. Offer to base off a different branch/commit if that's not what they want.
5. **Unquoted paths.** The repo or parent path contains spaces (common on macOS), and an unquoted command splits the path. Detection: any path in a command not wrapped in quotes. Resolution: quote every path in every command.
6. **Missing breadcrumb.** Creating the worktree but not recording where it came from, so `worktree-handoff` later can't find the main repo or base. Detection: no `WORKTREE.md` written. Resolution: always write the breadcrumb as the last creation step.
7. **Committing or pushing on the user's behalf.** Detection: any `git commit`/`git push` in this skill. Resolution: this skill only *creates* the worktree — the user does the work. Do not commit or push.
8. **Provisioning a *tracked* file.** Copying a file git already tracks (e.g. a committed `.env.example`) over the worktree's real checked-out copy. Detection: the selection mechanism can return tracked paths at all. Resolution: this is enforced **structurally** — `git ls-files -o` lists *untracked* files only, so a tracked file can never be selected. Do not bolt a `git check-ignore` filter on top of it; a duplicate check just implies the mechanism is untrusted.
9. **Clobbering an existing worktree file.** A file with the same name already exists at the worktree path (a tracked template, or a leftover from a rerun). Detection: `[ -e "<dest>" ]` before copying. Resolution: skip and report it; never overwrite. A rerun of this skill is thus idempotent — existing files are left alone.
10. **Assuming a copied env file is safe to use as-is.** `.worktreeinclude` copies the main repo's `.env` verbatim, so before the setup script runs it still holds main's values — including any **absolute** paths pointing at production sinks (output directories, vaults, deploy hooks). A worktree with an un-rewritten copy looks isolated and is not. Detection: the setup script exited non-zero (or was never there), yet a `.env` copy is present in the worktree. Resolution: the setup script must rewrite every path variable to a worktree-local absolute path and then *verify* it did — and the skill must treat a failed script as a failed provision (Step 7), and a missing script as a failed **precondition** (Step 1b). Never leave an un-rewritten copy sitting in a worktree that has been reported as created.
11. **Leaking secrets to the wrong place.** Copying env files into a worktree that is itself inside a synced/shared or world-readable location. Detection: worktree root under a cloud-synced or shared path. Resolution: the sibling-root placement (Anti-Pattern 1) keeps it beside the repo; note that a copy is a **second on-disk copy** of the secrets — strictly more exposure than the symlink this skill no longer does — and skip provisioning (which means not creating the worktree at all) if the user objects.
12. **Number reservation computed from the local checkout only.** Deriving the next ADR/SPEC number from `ls SDD/adr/` in one directory — exactly what the allocating skills do on their own, and exactly why sibling worktrees collide. Detection: the scan reads only the main repo (or only the new worktree). Resolution: the scan MUST union all four sources in Step 8 — every live worktree's files on disk (catches *uncommitted* in-flight artifacts), every branch's added-file history (catches unmerged or already-removed worktrees), and sibling `WORKTREE.md` reservations (catches worktrees created but not yet used). Dropping any one source reintroduces the collision.
13. **Reserving a number and then not telling anyone.** Writing the reservation into `WORKTREE.md` but leaving the worktree session to recompute a number locally anyway. Detection: the final report doesn't state the reserved numbers, or `WORKTREE.md` records them without the "do not recompute locally" instruction. Resolution: the reservation is only load-bearing if it is *honored* — state it in the report (Step 10) and phrase the breadcrumb as a directive so the session and the `cross-cutting-adr` skill both consume it.
14. **Treating the reservation as a hard quota.** Assuming the worktree may create exactly one ADR and one SPEC. Detection: the user asks "what if I need two ADRs?" and the answer is "you can't." Resolution: the reserved number is a **starting point**, not a cap — the worktree increments from there. The next `worktree-create` run finds those files on disk (source 1) and starts above them, so the scheme self-heals. Say "start here", never "you get one".
15. **Blocking on the reservation in a repo that doesn't use SDD.** Running the scan, finding nothing, and reporting an error or asking the user what number to use. Detection: the scan yields no numbered artifacts. Resolution: this is the normal case for most repos — skip the step silently, omit the line from the breadcrumb and report, and move on. Never create an `SDD/` directory here; this skill does not scaffold SDD.
16. **Symlinking `.env` instead of copying it.** A symlinked `.env` cannot be rewritten per-worktree — editing it would edit the main repo's real file, which for a path-rewriting setup script means corrupting production config for every checkout at once. A correct setup script detects this (`[ -L "$ENV_FILE" ]`) and refuses. Detection: any `ln -s` of an env file in this skill. Resolution: **always copy.** This skill has no symlink mode; earlier versions did, and reintroducing one silently reintroduces this hazard.
17. **Improvising past a missing prerequisite.** Reacting to an absent `.worktreeinclude` or absent env-setup script by symlinking, by copying `.env*` "just this once", by generating either file on the fly, or by creating the worktree anyway with a warning. Detection: any provisioning happening when Step 1b's precondition gate did not pass. Resolution: **stop and error out.** Name the missing file, say what it is for, and offer to help author it as a *separate, user-approved* action. A worktree is only safe when both halves of the contract are present; "created, but unprovisioned" is the failure state this skill exists to prevent.
18. **Creating the worktree before checking the preconditions.** Running `git worktree add` first and discovering the missing `.worktreeinclude` at Step 6, which leaves an orphan worktree directory and branch that now need cleaning up. Detection: the prerequisite check appears anywhere after Step 5. Resolution: the gate lives in **Step 1**, before any mutation. Fail before you mutate — then a rejected repo is byte-for-byte untouched.

## When to Activate

- The user asks to start work in an isolated worktree: "spin up a worktree", "create a worktree for the auth refactor", "give me a separate checkout to try this", "I want to work on X without touching main".
- The user runs a `/worktree-create` entry point (if wired up).
- The user describes wanting to parallelize or sandbox a task off the current branch and a worktree is the natural fit.

## When NOT to Activate

- **The user just wants a branch, not a separate directory.** A plain `git checkout -b` in place is simpler; don't impose a worktree.
- **They're inside a worktree and want to hand it back.** That's `worktree-handoff`, not this skill.
- **Not in a git repository.** If `git rev-parse --show-toplevel` fails, tell the user to `git init` or move into a repo first; do not proceed.
- **The user wants a full clone or a fork.** Worktrees share one `.git`; if they need an independent clone, this isn't it.
- **The repo lacks `.worktreeinclude` or an env-setup script.** The skill still *activates* — it has to, in order to run the check and produce the error — but it stops at Step 1 and creates nothing. Do not route around the gate by hand-copying config or making a plain branch under this skill's name.

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

### Step 1b: Precondition gate — `.worktreeinclude` and an env-setup script MUST exist

Both halves of the BB contract are **required**. Check them **here**, before `git worktree add` (Step 5), so a rejected repo is left byte-for-byte untouched with no orphan worktree or branch to clean up (Anti-Pattern 18):

```bash
# "<main>" is the main repo toplevel from Step 1.
[ -e "<main>/.worktreeinclude" ] && echo "OK: .worktreeinclude"     || echo "MISSING: .worktreeinclude"
if   [ -e "<main>/.env-setup.sh" ];    then echo "OK: .env-setup.sh"
elif [ -e "<main>/.bb-env-setup.sh" ]; then echo "OK: .bb-env-setup.sh"
else echo "MISSING: .env-setup.sh (or .bb-env-setup.sh)"; fi
```

Use `-e`, not `-f`: `.bb-env-setup.sh` is conventionally a **symlink** to `.env-setup.sh`, and `-f` follows symlinks so it accepts both a real file and a valid link — but a *broken* symlink fails both, which is the correct outcome. If a candidate exists but is not readable, treat it as missing and say why.

**If either is MISSING: STOP.** Create nothing — no worktree, no branch, no directories. Report the failure in the shape shown under **Output Format → Precondition failure**, naming each missing file and what it is for. Do not improvise a fallback (Anti-Pattern 17): no symlinking, no ad-hoc `cp` of `.env*`, no proceeding-with-a-warning.

You may **offer** to help author the missing file(s) — that is genuinely useful, since the pair is small and the reference shape is well known. But it is a **separate action the user must approve**, and this skill never writes them silently or as part of a create run. If the user accepts, author the files, then re-run this skill from Step 1.

Record which script was found (`.env-setup.sh` or `.bb-env-setup.sh`) — Step 7 runs that exact one.

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

### Step 6: Copy untracked files into the worktree (`.worktreeinclude`)

A worktree checks out from a commit, so **git-ignored files never come with it** — the fresh worktree has no `.env`. Fill that gap by copying what `.worktreeinclude` lists. Its existence was already confirmed in Step 1b, so there is no gate here and no alternative path: **copy, always.**

`.worktreeinclude` is a **gitignore-syntax** file listing *untracked* files to copy into each new worktree. Do **not** hand-parse gitignore syntax — `git ls-files` already implements it. Run this from the **main repo toplevel**:

```bash
# "<main>" is the main repo toplevel; "<worktree-path>" is the new worktree.
copied=0; skipped_link=0; skipped_exists=0; failed=0; copied_names=""
while IFS= read -r -d '' f; do
  src="<main>/$f"
  # BB rule: symlinks in the source checkout are skipped.
  [ -L "$src" ] && { skipped_link=$((skipped_link+1)); continue; }
  dest="<worktree-path>/$f"
  # Never clobber (Anti-Pattern 9).
  [ -e "$dest" ] && { skipped_exists=$((skipped_exists+1)); continue; }
  mkdir -p "$(dirname "$dest")"
  if cp -p "$src" "$dest"; then
    copied=$((copied+1)); copied_names="$copied_names $f"
  else
    failed=$((failed+1)); echo "copy FAILED: $f"
  fi
done < <(git -C "<main>" ls-files -z -o -i --exclude-from=.worktreeinclude)
echo "copied=$copied skipped_link=$skipped_link skipped_exists=$skipped_exists failed=$failed"
```

Three BB rules map onto three mechanisms — state this mapping rather than reimplementing any of them:

| BB rule | Mechanism |
|---|---|
| gitignore syntax incl. `!` negation | `--exclude-from=.worktreeinclude` |
| tracked files take precedence | `-o` (lists *untracked* files only) |
| symlinks in source are skipped | `[ -L "$src" ] && continue` |

Notes and clarifications:

- **Anti-Pattern 8 is satisfied structurally.** Because `-o` lists only *untracked* files, a tracked file can never be selected — so no separate `git check-ignore` filter is needed. Do not add one; a duplicate check just implies the mechanism is untrusted.
- **`--exclude-from` is resolved relative to the process's working directory,** which `git -C "<main>"` sets to the main repo toplevel — that's why the bare filename works. Keep the `-C`.
- **Copies, not links (Anti-Pattern 16).** The worktree gets independent files it can diverge; that divergence is the *point*, since Step 7's script rewrites them. Never `ln -s` an env file here.
- **Nested paths work.** `.worktreeinclude` may list directories (`scratchpad/`), which expand to individual files with relative paths — hence the `mkdir -p "$(dirname "$dest")"`.
- **A failed copy is reported but does not halt provisioning** (BB's rule). Count failures, report them at the end, keep going. This is deliberately *not* the same as a failed setup script (Step 7), which does halt.
- **Zero matches is not an error, but say so.** A `.worktreeinclude` that matches nothing (every listed path is tracked, absent, or negated) means the worktree gets no copied config. Report `copied=0` plainly rather than silently — Step 7's script still runs and will fail loudly if it needed a file that never arrived.
- **Idempotent.** A rerun skips anything already present.

Record `copied_names` for the breadcrumb (Step 9) and the final report (Step 10), plus the skip/fail counts if any are non-zero.

### Step 7: Run the repo's env-setup script (required — its absence stopped you at Step 1b)

Copies from Step 6 land **verbatim** — the worktree's `.env` still holds main's values, including absolute paths pointing at production sinks. The setup script is what makes the copy worktree-local. Run it **after** the copies and **before** the breadcrumb.

**Which script.** Step 1b already resolved this and recorded the answer. The precedence it applied, for reference:

1. `.env-setup.sh`
2. `.bb-env-setup.sh`

Run the **first** one found; **never run both** — in a repo following BB's convention, `.bb-env-setup.sh` is a symlink to `.env-setup.sh`, so running both would run the same script twice. Reaching this step with neither present is impossible by construction: the gate would have stopped the run before the worktree existed. If you somehow get here with no script, that is a **bug in the gate** — treat it as a failed provision (below), not as a step to skip.

**Invocation:**

```bash
# cwd = worktree root; run MAIN's copy of the script recorded in Step 1b; stdin closed; 15-minute cap.
( cd "<worktree-path>" && env bash "<main>/<script-from-step-1b>" < /dev/null )
```

Match the rest of BB's run contract: **cwd = worktree root**, launched with **`env bash`**, **stdin closed** (`< /dev/null`), stdout/stderr **streamed to the user**, and a **15-minute timeout** — a script still running at 15 minutes is a failed provision, not a slow one.

- **Why main's working copy rather than the worktree's.** A well-written setup script derives the worktree from `pwd` and the main checkout from `git rev-parse --path-format=absolute --git-common-dir`, so running main's file with the worktree as cwd behaves identically. Doing it this way also (a) works when the script isn't committed yet — which is exactly why the Step 1b gate checks the **main root** rather than the checkout — and (b) always runs the *current* version rather than whatever the base commit happened to carry. BB has no such option; it can only run what the commit materializes.
- **Enforcing the timeout.** macOS ships no `timeout(1)`, so don't assume it. Set the tool call's own timeout to 900000 ms (15 min); or, if GNU coreutils is present, wrap with `gtimeout 900` (`timeout 900` on Linux). Either way, a run cut short at 15 minutes is a **failure**, handled exactly like a non-zero exit below.

**Failure handling — non-zero exit, signal, or timeout.** This is not a warning-and-continue case. A failed script means the worktree holds a **copy** of `.env` still carrying the main repo's production absolute paths, un-rewritten — a worktree that *looks* like a sandbox and isn't (Anti-Pattern 10). Unlike Step 1b's gate, this failure happens *after* `git worktree add`, so there is now something to clean up. On failure:

1. **Report the failure and the script's output prominently** — do not bury it.
2. **Rename the copied env** so nothing picks it up accidentally:
   ```bash
   mv "<worktree-path>/.env" "<worktree-path>/.env.UNSAFE-NOT-REWRITTEN"
   ```
   (Do the same for any other copied env-family file the script was meant to rewrite.)
3. **Offer to remove the worktree and branch** — BB's abort semantics — and **default to recommending it**:
   ```bash
   git worktree remove --force "<worktree-path>" && git branch -D "<branch>"
   ```
   (`-D` is correct *only* here: the branch was created seconds ago and carries no commits, so there is no work to discard. It is never correct in `worktree-handoff`, where `-D` would bypass git's unmerged-branch refusal.)

**Never report success on a failed setup script.** If the user declines removal, the final report must state that provisioning failed and that the env file was quarantined.

**The rewrite marker.** A well-formed setup script appends a marker line to each file it rewrites:

```
# --- rewritten by .env-setup.sh for this worktree ---
```

This is `worktree-handoff`'s per-file anchor for "worktree-local by design — never reconcile back into main"; the breadcrumb's `**Env setup:**` line (Step 9) is its worktree-level anchor. If the repo's script doesn't emit the marker, the breadcrumb line still covers it — but mention the marker to the user, since it is the more robust of the two. This skill does **not** add the marker itself; it neither writes nor edits the setup script.

Record the script name and outcome for the breadcrumb (Step 9) and the final report (Step 10).

### Step 8: Reserve SDD artifact numbers (skip silently if the repo has none)

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

Record both reserved numbers for the breadcrumb (Step 9) and the final report (Step 10).

### Step 9: Write the breadcrumb

Write `WORKTREE.md` at the worktree path root (see **Output Format**), recording: task type, description, branch, base branch, base commit SHA, main-repo absolute path, the **`Files copied:`** list from Step 6, the **`Env setup:`** line from Step 7 (always present — a worktree only exists if a script ran), the reserved SDD numbers (Step 8, omit the line if none), and creation context. `worktree-handoff` keys on the `Env setup:` line to know this worktree's env is worktree-local by design, so it must always be written. This is what `worktree-handoff` reads to merge back — and what the *next* `worktree-create` run reads as scan source (3), so the reserved-numbers line must keep the literal marker text `SDD numbers reserved` for that grep to find it. (It lives only in the worktree and disappears when the worktree is removed — do not commit it unless the user wants to; if the repo would otherwise track it, mention it so they can `.gitignore` or commit as they prefer.)

### Step 10: Report and point to the next step

Tell the user:

- The worktree path and the branch name.
- What was provisioned: the copied files and the env-setup outcome.
- The reserved SDD numbers, if any — and that the session there should *use* them rather than recompute (Anti-Pattern 13). Omit entirely when Step 8 found nothing.
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
  Copied:    .env, scratchpad/  (per .worktreeinclude — independent copies, not symlinks)
  Env setup: .env-setup.sh ✓  (.env paths rewritten to worktree-local values)
  Reserved:  ADR-0011, SPEC-045  (start here — do not recompute locally; 2 sibling worktrees scanned)

Next:
  cd "/Volumes/.../claude-plugins-WT/pablo-oliva/fix-login-redirect"
  # start a new Claude Code session there and do the work
  # when done, run the worktree-handoff skill from inside it
```

Line rules:

- **`Copied:` and `Env setup:` are always present** on a successful run — a worktree cannot exist without both halves of the contract having run. Show non-zero skip/fail counts inline (e.g. `2 skipped (symlink), 1 FAILED`), and `Copied: none (.worktreeinclude matched no untracked files)` when the copy step matched nothing.
- Omit the `Reserved:` line entirely when Step 8 found no numbered SDD artifacts — the common case.

### Precondition failure (Step 1b) — nothing was created

```
Cannot create a worktree — this repo is missing the provisioning contract.

  Repo:    /Volumes/.../claude-plugins
  Missing: .worktreeinclude       (gitignore-syntax list of untracked files to COPY
                                   into each worktree — e.g. .env, scratchpad/)
  Present: .env-setup.sh          (rewrites those copies to worktree-local paths)

Nothing was created — no worktree, no branch, no directories.

Both files are required. `worktree-create` copies untracked config into the worktree
and then rewrites it for that worktree; without .worktreeinclude nothing is copied,
and without the setup script the copies still point at this repo's real paths.

I can draft the missing file(s) for you — say the word and I'll write them, then you
can re-run this. I won't create them as part of a worktree run.
```

Show `Missing:` for each absent file and `Present:` for the one that exists (omit `Present:` when both are missing). Never print a "created" report alongside this.

`WORKTREE.md` breadcrumb written into the worktree:

```markdown
# Worktree: fix-login-redirect

- **Task type:** fix
- **Description:** login redirect bug
- **Branch:** pablo-oliva/fix-login-redirect
- **Base branch:** main
- **Base commit:** 695d075
- **Main repo:** /Volumes/Crucial Data/Documents/Code & Dev/claude-plugins
- **Files copied:** `.env`, `scratchpad/` (copied per `.worktreeinclude` — independent copies, NOT symlinks)
- **Env setup:** `.env-setup.sh` ran OK — `.env` paths rewritten to worktree-local values
- **SDD numbers reserved:** ADR-0011, SPEC-045 — start here; do NOT recompute from the local `SDD/` directory
- **Created:** from `worktree-create`

<!-- Read by the worktree-handoff skill to merge this branch back and remove the worktree. -->
<!-- The "Files copied" / "Env setup" lines above are the .worktreeinclude provisioning contract, which
     this skill REQUIRES: the files are INDEPENDENT COPIES, and .env has been DELIBERATELY REWRITTEN
     with worktree-local absolute paths. It must NOT be reconciled back into the main repo — writing
     it into main would point production at directories that vanish with this worktree.
     worktree-handoff skips .env reconciliation whenever the "Env setup" line is present, so that line
     is always written. Use `none` where a list is empty (e.g. "Files copied: none"), never omit it.
     Nothing here is a symlink into the main repo; earlier versions of this skill symlinked env files
     and a worktree from that era will carry an "Env links:" line instead. -->
<!-- If the "Env setup" line reads FAILED, this worktree was never safely provisioned: the copied env
     was quarantined as `.env.UNSAFE-NOT-REWRITTEN` and the worktree should be removed, not used. -->
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
2. **1b:** `.worktreeinclude` present, `.env-setup.sh` present → gate passes; record `.env-setup.sh`.
3. Ask (if needed): type `fix`, description "login redirect".
4. Compute branch `pablo-oliva/fix-login-redirect`, path `../claude-plugins-WT/pablo-oliva/fix-login-redirect`.
5. No collision.
6. `git worktree add -b pablo-oliva/fix-login-redirect "<path>" main`.
7. Copy per `.worktreeinclude`: `git ls-files -o -i --exclude-from=.worktreeinclude`, skipping source symlinks and existing destinations. Say "copied `.env`, `.env.prod`".
8. Run `( cd "<path>" && env bash "<main>/.env-setup.sh" < /dev/null )`; exit 0 → the copies are now worktree-local.
9. Reserve SDD numbers: scan all live worktrees, all branch history, and sibling reservations; no numbered artifacts found, so skip the step and say nothing about it.
10. Write `WORKTREE.md` (including `Files copied:` and `Env setup:`).
11. Report path + branch + copied files + env-setup result + "start a new session there; run worktree-handoff when done."

### GOOD — the repo isn't set up: stop, create nothing

**User:** "Make a worktree for the payments spike — I'll need the API keys from `.env`."

Step 1b finds no `.worktreeinclude` (the setup script is there, but that's only half). **Right:** stop immediately, before `git worktree add`. Report which file is missing and what it does, state plainly that nothing was created, and offer to draft it as a separate step. **Wrong**, in every variant: symlinking `.env` "like the old version did"; `cp`-ing `.env` in by hand because the user said they need the API keys; writing a `.worktreeinclude` on the fly and continuing; or creating the worktree with a warning attached. The user asking for API keys is not authority to skip the sandbox that makes those keys safe to have there — and a half-provisioned worktree is precisely the failure this gate exists to prevent (Anti-Pattern 17).

### GOOD — copy, then rewrite

**User:** "Spin up a worktree for the ingest refactor."

The repo root has a `.worktreeinclude` containing `.env*`, `scratchpad/`, and `!.env.local`, plus a `.env-setup.sh` (with `.bb-env-setup.sh` symlinked to it). Step 1b passes and records `.env-setup.sh` — the first of the two, never both. `git ls-files -o -i --exclude-from=.worktreeinclude` yields `.env`, `.env.prod`, `scratchpad/notes.md` — **not** `.env.local` (negated), **not** the tracked `.env.example` (`-o` excludes it), and **not** the root symlink `.env.link` (skipped by the `[ -L ]` guard). Copy those three. Then Step 7 runs `( cd "<worktree>" && env bash "<main>/.env-setup.sh" < /dev/null )` — main's copy, so an uncommitted edit to the script still applies — which rewrites `OUTPUT_DIR` and friends in the worktree's `.env` to worktree-local absolute paths and verifies them. Exit 0 → report `Copied: .env, .env.prod, scratchpad/notes.md` and `Env setup: .env-setup.sh ✓`.

### GOOD — the setup script fails

Same repo, but `.env-setup.sh` exits 1 because a required tool is missing. **Right:** print the script's output prominently, rename the worktree's `.env` to `.env.UNSAFE-NOT-REWRITTEN` (it still holds main's production paths), report the provision as **failed**, and recommend removing the worktree and branch — `git worktree remove --force` then `git branch -D` on a branch that is seconds old and holds no commits. **Wrong:** printing "Worktree created ✓" with a warning underneath — the worktree looks sandboxed and is pointing at production sinks. Note the contrast with the Step 1b gate: there, nothing existed yet and there was nothing to undo; here the worktree is already on disk, which is exactly why the gate is placed as early as it is.

### BAD — symlinking an env file

Seeing `.env` in the main repo and reaching for `ln -s`. Wrong: the setup script's whole job is to rewrite `.env` per worktree, and rewriting a symlink edits **main's real file** — corrupting production config for every checkout at once. A correct script detects this with `[ -L "$ENV_FILE" ]` and refuses, so the best case is a failed provision and the worst case is silent corruption. **Right:** always copy (Anti-Pattern 16). This skill has no symlink mode at all.

### GOOD — numbers reserved around two sibling worktrees

**User:** "Spin up a worktree for the audit-logging feature."

The repo uses SDD. The Step 8 scan finds: `SDD/adr/0007-*` committed on `main`; an uncommitted `SDD/adr/0008-*` and `SPEC-042-*` sitting in a live worktree (`feature-a`) that hasn't committed yet; a `WORKTREE.md` in another live worktree (`feature-b`) reserving `ADR-0009, SPEC-043`; and `SDD/adr/0010-*` plus `SPEC-044-*` added on an unmerged branch whose worktree is already gone. High-water marks: ADR `0010`, SPEC `044`. Reserve **ADR-0011 / SPEC-045**, write them into `WORKTREE.md`, and report them. Note that three of those four numbers are invisible to a plain `ls SDD/adr/` in the main repo — which is precisely the collision this step prevents.

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

This skill **creates** a single sibling worktree, provisions its untracked runtime config, reserves collision-free SDD artifact numbers, and writes its breadcrumb — and nothing more. Provisioning has exactly **one** mode, and it is **conditional on the repo, not optional for the skill**: the main repo root must have both a `.worktreeinclude` and an `.env-setup.sh`/`.bb-env-setup.sh`, or the skill stops at Step 1b having created nothing. When they are present it **copies** the untracked files `.worktreeinclude` lists and runs the first script found (never both; a non-zero exit, signal, or 15-minute timeout is a **failed provision**, which quarantines the copied env and offers to remove the worktree). There is no symlink mode and no unprovisioned mode. It does not commit, push, run the task, or merge anything. It copies only untracked files (tracked ones are already in the checkout) and never overwrites an existing file at the worktree path. It does not author `.worktreeinclude` or an env-setup script as part of a create run — it may offer to write them as a separate, user-approved action, after which the user re-runs the skill. Number reservation is **advisory and creation-time only**: it records a starting number no sibling worktree can claim, but it does not lock anything, does not renumber existing artifacts, does not scaffold `SDD/` in repos that lack it, and does not write any SDD artifact itself — `cross-cutting-adr` and the SDD flow still author those, honoring the reserved number from `WORKTREE.md`. Merging the work back and removing the worktree — which discards worktree-local copies that must **never** be reconciled back into main — is the job of the paired **`worktree-handoff`** skill. It operates only within one git repository (shared `.git`); it does not clone or fork.
