---
name: worktree-handoff
description: "INVOKE THIS SKILL to close the loop on an isolated git worktree created by `worktree-create`. It is CONTEXT-AWARE. (A) Run it from INSIDE the worktree — 'generate a handoff', 'I'm done in this worktree', 'hand this back to main', 'wrap up this worktree' — and it writes a `HANDOFF.md` and prints a ready-to-paste block summarizing what was done, the branch, and a merge+cleanup request. (B) Paste that block into your MAIN repo session and run it there — 'merge this worktree back', 'integrate the handoff', 'merge <branch> and clean up' — and it merges the branch into the target branch, verifies, and (with confirmation before each destructive step) removes the worktree and deletes the branch. Confirms before `git worktree remove` and `git branch -d`; never force-deletes unmerged work silently."
---

# Worktree Handoff

Closes the loop opened by **`worktree-create`**. The isolated work done in a sibling worktree has to get *back* into the main line — this skill handles both ends of that trip and figures out which end it's on:

- **Handoff mode** (running **inside the worktree**): summarize what was done and emit a paste-ready handoff (plus a durable `HANDOFF.md`).
- **Merge mode** (running **in the main repo**, handoff pasted in): merge the branch into the target, verify, and — with a confirmation gate before each destructive action — remove the worktree and delete the branch.

## Expert Vocabulary

Handoff artifact. Merge-back / integration. Context detection (linked worktree vs. main worktree). `git-dir` discriminator (`/worktrees/` substring). Base branch / merge-base. Fast-forward vs. merge commit. Diffstat / commit range (`base..HEAD`). Dirty tree guard. `git worktree remove`. `git branch -d` (safe) vs. `-D` (force). Prune. Confirmation gate. Non-destructive-on-conflict. Breadcrumb (`WORKTREE.md`).

## Anti-Pattern Watchlist

Check the plan against these before acting:

1. **Wrong-mode execution.** Trying to merge from inside the worktree, or trying to generate a handoff from the main repo. Detection: mode not derived from `git rev-parse --git-dir`. Resolution: always detect mode first (Step 0). `/worktrees/` in git-dir ⇒ Handoff mode; otherwise ⇒ Merge mode.
2. **Destructive-on-conflict.** Removing the worktree or deleting the branch after a merge that conflicted or failed. Detection: `git merge` exited non-zero or left conflict markers. Resolution: **stop** — report the conflict, leave the worktree and branch fully intact, let the user resolve. Cleanup only ever follows a *clean, completed* merge.
3. **Force-deleting unmerged branch work.** Using `git branch -D` to push past git's refusal that the branch isn't merged. Detection: reaching for `-D`. Resolution: use `-d`; if it refuses "not fully merged", the work is *not* in the target — stop, surface why, and ask. Never `-D` to bypass an unmerged branch silently.
4. **Blocked worktree removal (expected — handle, don't force blindly).** `git worktree remove` refuses because the worktree contains untracked/modified files. This is the NORMAL case: the worktree always carries the `WORKTREE.md` and `HANDOFF.md` breadcrumbs, which are untracked by design (committing them would merge junk into the target branch). Detection: `remove` fails "contains modified or untracked files". Resolution: inspect `git status --porcelain` in the worktree; if the ONLY entries are the known breadcrumbs (`WORKTREE.md`, `HANDOFF.md`), `git worktree remove --force` is correct and safe — the breadcrumbs are disposable. If ANY other modified/untracked file is present, that's real unexpected work: STOP and ask. Do NOT try to `rm` the breadcrumbs first — if they are tracked, deleting them on disk just creates a `modified` state that also blocks plain removal.
5. **Skipping the confirmation gate.** Removing the worktree / deleting the branch without asking. Detection: destructive command issued before an explicit user yes. Resolution: after showing the merge result, ask before *each* destructive step (worktree removal, branch deletion). Wait for confirmation.
6. **Handing off dirty/uncommitted work.** Generating a handoff while the worktree has uncommitted changes (beyond the breadcrumbs), so the summary references work that isn't on the branch. Detection: `git status --porcelain` non-empty in Handoff mode. Resolution: tell the user to commit (or stash) first; offer to commit. The handoff describes *committed* work.
7. **Losing the paste block.** Emitting only a file, or only screen text, when the user needs both. Detection: HANDOFF.md written but no paste block printed, or vice-versa. Resolution: in Handoff mode always do both — write `HANDOFF.md` **and** print the delimited paste block.
8. **Guessing the target branch.** Merging into whatever branch happens to be checked out in main rather than the recorded base. Detection: target branch not cross-checked against `WORKTREE.md` / the handoff. Resolution: default to the recorded base branch; if the currently checked-out branch differs, confirm which is the merge target before merging.
9. **Wrong cleanup order.** Running `git branch -d` before removing the worktree. Detection: branch deletion fails "used by worktree at …". Resolution: always `git worktree remove` FIRST (a branch checked out by a live worktree cannot be deleted), then `git branch -d`.
10. **Unquoted paths.** Worktree paths contain spaces on this machine. Detection: any unquoted path. Resolution: quote every path.

## When to Activate

**Handoff mode** — the user, working inside a worktree, signals they're done:

- "Generate a handoff", "wrap up this worktree", "I'm done here", "hand this back to main", "give me the merge-back summary".

**Merge mode** — the user, in the main repo, wants to integrate a worktree's work:

- "Merge this worktree back", "integrate the handoff", "merge `<branch>` and clean up the worktree", or they paste a handoff block produced by this skill.

## When NOT to Activate

- **No worktree involved.** A normal branch merge with no worktree to remove is just `git merge` — this skill's cleanup half doesn't apply.
- **Creating a worktree.** That's `worktree-create`.
- **Mid-work, nothing to hand off.** If the user is still working and hasn't committed, don't force a handoff — point them to commit first.
- **Not in a git repo.** Stop and say so.

## Behavioral Instructions

### Step 0: Detect the mode

```bash
git rev-parse --git-dir            # ".../.git/worktrees/<name>" ⇒ Handoff mode; ".../.git" (or ".git") ⇒ Merge mode
```

If the user pasted a handoff block, that's a strong signal for **Merge mode** regardless. If neither applies (not a repo), stop.

---

### Handoff mode (running inside the worktree)

**H1 — Gather state.**

```bash
git rev-parse --abbrev-ref HEAD          # branch
git status --porcelain                   # must be clean (Anti-Pattern 5)
```

Read `WORKTREE.md` at the worktree root for base branch, base commit, and main-repo path. If it's missing, derive: base via `git merge-base HEAD <base-branch>`, main repo via `git worktree list` (the entry whose git-dir is the common `.git`).

```bash
git log --oneline "<base>..HEAD"         # commits made in the worktree
git diff --stat "<base>..HEAD"           # files changed
```

**H2 — Guard dirty state.** If `git status --porcelain` is non-empty, stop and tell the user to commit or stash first (offer to commit). Do not describe uncommitted work as done.

**H3 — Summarize.** From the commit messages and diffstat, write a concise, factual "What was done" summary (2–6 bullets) plus any test/verify status the session established. Don't invent results.

**H4 — Write `HANDOFF.md`** at the worktree root (see **Output Format**).

**H5 — Print the paste block.** Print the same content between clear delimiters, with an explicit instruction: *paste this into your MAIN repo Claude Code session.* The block must include the branch, worktree path, main-repo path, base branch, commit list, summary, and an explicit **merge + cleanup request** so the main session knows to invoke Merge mode.

---

### Merge mode (running in the main repo, handoff in hand)

**M1 — Parse the handoff.** Extract: branch, worktree path, base/target branch. If the user pasted the block, read it from there; if they only named a branch, look it up via `git worktree list`. If anything's ambiguous, ask.

**M2 — Preconditions.**

```bash
git rev-parse --git-dir                  # confirm main worktree (not "/worktrees/")
git status --porcelain                   # target working tree should be clean; warn if not
```

Determine the **target branch** = recorded base branch (Anti-Pattern 7). If the currently checked-out branch differs, confirm which is the target. Check out the target if needed.

**M3 — Merge.**

```bash
git merge "<branch>"                      # into the checked-out target
```

Show the result (fast-forward, merge commit, or conflict). **If it conflicts or fails: STOP.** Report the conflicting files, leave the worktree and branch untouched, and let the user resolve. Do not proceed to cleanup.

**M4 — Verify (if applicable).** If the project has a quick test/build/verify step and the user wants it, run it and report. A failure here is a reason to pause before cleanup, not to auto-cleanup.

**M5 — Confirmation gate (destructive).** Only after a clean, completed merge. Show what will be removed and ask:

> Merge is clean. Remove the worktree at `<path>` and delete branch `<branch>`?

Wait for an explicit yes. If the user only wants the merge, stop here.

**M6 — Clean up (on confirmation).** Order matters: remove the worktree **before** deleting the branch (a branch checked out by a live worktree can't be deleted).

First, classify the worktree's leftover files — the worktree will always carry the untracked breadcrumbs, so a plain `remove` *will* refuse; that's expected, not an error:

```bash
git -C "<worktree-path>" status --porcelain
```

- If the only entries are the known breadcrumbs (`WORKTREE.md`, `HANDOFF.md`), forcing is safe — they're disposable:

  ```bash
  git worktree remove --force "<worktree-path>"   # safe: verified only-breadcrumbs leftovers
  ```

- If **any other** modified/untracked file appears, that's unexpected work — **stop and ask**; do not force. (Never `rm` the breadcrumbs to coax a plain `remove` — if tracked, that leaves a `modified` state that also blocks it.)

Then delete the branch and tidy up:

```bash
git branch -d "<branch>"      # safe delete; refuses "not fully merged" → the work isn't in the target, stop & ask (never -D to bypass)
git worktree prune            # tidy administrative refs
```

Optionally remove the now-empty `<project>-WT/<you>/` parent dirs. `HANDOFF.md` and `WORKTREE.md` lived in the worktree and are gone with it.

**M7 — Report** the final state: what merged, the resulting HEAD, and what was cleaned up (or what remains and why).

## Output Format

### Handoff mode — `HANDOFF.md` and the printed paste block

```
────────── WORKTREE HANDOFF — paste into your MAIN repo session ──────────

Merge request: please merge this worktree's branch into the main line, then
remove the worktree and delete the branch (via the worktree-handoff skill).

  Branch:      pablo-oliva/fix-login-redirect
  Worktree:    /Volumes/.../claude-plugins-WT/pablo-oliva/fix-login-redirect
  Main repo:   /Volumes/.../claude-plugins
  Base branch: main   (base commit 695d075)

  Commits:
    a1b2c3d  fix: guard null redirect target
    d4e5f6a  test: cover empty redirect param

  What was done:
    - Fixed the login redirect crashing on a null `next` param.
    - Added a regression test for the empty-param case.
    - `npm test` passes locally (42/42).

  Files changed:
    src/auth/redirect.ts | 8 +++--
    test/auth/redirect.test.ts | 21 ++++++

──────────────────────────────────────────────────────────────────────────
(also saved to HANDOFF.md in this worktree)
```

### Merge mode — final report

```
Integrated ✓
  Merged pablo-oliva/fix-login-redirect → main (fast-forward to a1b2c3d)
  Removed worktree: ../claude-plugins-WT/pablo-oliva/fix-login-redirect
  Deleted branch:   pablo-oliva/fix-login-redirect
```

## Examples

### GOOD — handoff from inside the worktree

Clean tree, branch `pablo-oliva/fix-login-redirect`, two commits over `main`. Read `WORKTREE.md` for base + main-repo path, summarize the two commits, write `HANDOFF.md`, and print the delimited paste block telling the user to paste it into their main session.

### GOOD — merge that conflicts

In the main repo, paste block names branch `pablo-oliva/fix-login-redirect`. `git merge` reports a conflict in `src/auth/redirect.ts`. **Stop**: report the conflict, leave the worktree and branch intact, tell the user to resolve, and do **not** touch the worktree or branch.

### BAD — cleanup before confirmation

Merge succeeds, and the skill immediately runs `git worktree remove` + `git branch -d` without asking. Wrong — the user chose the confirm-before-destructive flow. **Right:** show the clean merge result, ask before removing the worktree and before deleting the branch, and wait for yes.

### BAD — force-deleting unmerged work

`git branch -d` refuses because the branch has commits not in the target. Wrong: escalating to `git branch -D`. **Right:** surface that the branch is unmerged, explain what would be lost, and ask — the refusal is a safety feature, not an obstacle.

## Questions This Skill Answers

- "Generate a handoff for this worktree."
- "I'm done in this worktree — wrap it up."
- "Merge this worktree back into main and clean it up."
- "Integrate the handoff I just pasted."
- "Merge `<branch>` and remove its worktree."

## Scope Boundary

This skill handles the **return trip** of a worktree created by `worktree-create`: it produces a handoff from inside the worktree and, in the main repo, merges the branch and (with confirmation) removes the worktree and deletes the branch. It never force-deletes unmerged work, never cleans up after a conflicted or failed merge, and never removes a worktree or branch without an explicit yes. Creating worktrees is out of scope — that's `worktree-create`.
