---
name: worktree-handoff
description: "INVOKE THIS SKILL to close the loop on an isolated git worktree created by `worktree-create`. It is CONTEXT-AWARE. (A) Run it from INSIDE the worktree — 'generate a handoff', 'I'm done in this worktree', 'hand this back to main', 'wrap up this worktree' — and it writes a `HANDOFF.md` and prints a ready-to-paste block summarizing what was done, the branch, and a merge+cleanup request. (B) Paste that block into your MAIN repo session and run it there — 'merge this worktree back', 'integrate the handoff', 'merge <branch> and clean up' — and it merges the branch into the target branch, verifies, settles the worktree's `.env*` files before removal — every worktree `worktree-create` makes is SCRIPT-PROVISIONED (copied per `.worktreeinclude`, rewritten by `.env-setup.sh`), and a script-provisioned env is NEVER reconciled back into main, since its paths point inside the worktree being deleted; only a file the user hand-copied in, or a legacy symlink from an older worktree, is handled differently — and (with confirmation before each destructive step) removes the worktree and deletes the branch. Confirms before `git worktree remove` and `git branch -d`; never force-deletes unmerged work or a diverged copied env silently."
---

# Worktree Handoff

Closes the loop opened by **`worktree-create`**. The isolated work done in a sibling worktree has to get *back* into the main line — this skill handles both ends of that trip and figures out which end it's on:

- **Handoff mode** (running **inside the worktree**): summarize what was done and emit a paste-ready handoff (plus a durable `HANDOFF.md`).
- **Merge mode** (running **in the main repo**, handoff pasted in): merge the branch into the target, verify, and — with a confirmation gate before each destructive action — remove the worktree and delete the branch.

## Expert Vocabulary

Handoff artifact. Merge-back / integration. Context detection (linked worktree vs. main worktree). `git-dir` discriminator (`/worktrees/` substring). Base branch / merge-base. Fast-forward vs. merge commit. Diffstat / commit range (`base..HEAD`). Dirty tree guard. `git worktree remove`. `git branch -d` (safe) vs. `-D` (force). Prune. Confirmation gate. Non-destructive-on-conflict. Breadcrumb (`WORKTREE.md`). Symlinked vs. copied env file. Env divergence / reconciliation. Reconciliation **direction** (worktree → main is the dangerous one). Script-provisioned worktree (`.worktreeinclude` copy + `.env-setup.sh` rewrite). Rewrite marker line. Worktree-local absolute path. Deliberate divergence (not a diff to review). Read-only surfacing vs. writeback. Git-ignored files invisible to `git status`. Untracked-file safety (no git history to recover from).

## Anti-Pattern Watchlist

Check the plan against these before acting:

1. **Wrong-mode execution.** Trying to merge from inside the worktree, or trying to generate a handoff from the main repo. Detection: mode not derived from `git rev-parse --git-dir`. Resolution: always detect mode first (Step 0). `/worktrees/` in git-dir ⇒ Handoff mode; otherwise ⇒ Merge mode.
2. **Destructive-on-conflict.** Removing the worktree or deleting the branch after a merge that conflicted or failed. Detection: `git merge` exited non-zero or left conflict markers. Resolution: **stop** — report the conflict, leave the worktree and branch fully intact, let the user resolve. Cleanup only ever follows a *clean, completed* merge.
3. **Force-deleting unmerged branch work.** Using `git branch -D` to push past git's refusal that the branch isn't merged. Detection: reaching for `-D`. Resolution: use `-d`; if it refuses "not fully merged", the work is *not* in the target — stop, surface why, and ask. Never `-D` to bypass an unmerged branch silently.
4. **Blocked worktree removal (expected — handle, don't force blindly).** `git worktree remove` refuses because the worktree contains untracked/modified files. This is the NORMAL case: the worktree always carries the `WORKTREE.md` and `HANDOFF.md` breadcrumbs, which are untracked by design (committing them would merge junk into the target branch). Detection: `remove` fails "contains modified or untracked files". Resolution: inspect `git status --porcelain` in the worktree; if the ONLY entries are the known breadcrumbs (`WORKTREE.md`, `HANDOFF.md`), `git worktree remove --force` is correct and safe — the breadcrumbs are disposable. If ANY other modified/untracked file is present, that's real unexpected work: STOP and ask. Do NOT try to `rm` the breadcrumbs first — if they are tracked, deleting them on disk just creates a `modified` state that also blocks plain removal. **Caveat (see Anti-Patterns 11 and 13):** `git status` will NOT list git-ignored env files (`.env*`), so a copied env in the worktree is invisible here and `--force` would delete it unremarked — settle the env files (Merge mode M5.5) BEFORE removal. Note that for a *script-provisioned* worktree, deleting its env with the worktree is the **correct** outcome, not a loss.
5. **Skipping the confirmation gate.** Removing the worktree / deleting the branch without asking. Detection: destructive command issued before an explicit user yes. Resolution: after showing the merge result, ask before *each* destructive step (worktree removal, branch deletion). Wait for confirmation.
6. **Handing off dirty/uncommitted work.** Generating a handoff while the worktree has uncommitted changes (beyond the breadcrumbs), so the summary references work that isn't on the branch. Detection: `git status --porcelain` non-empty in Handoff mode. Resolution: tell the user to commit (or stash) first; offer to commit. The handoff describes *committed* work.
7. **Losing the paste block.** Emitting only a file, or only screen text, when the user needs both. Detection: HANDOFF.md written but no paste block printed, or vice-versa. Resolution: in Handoff mode always do both — write `HANDOFF.md` **and** print the delimited paste block.
8. **Guessing the target branch.** Merging into whatever branch happens to be checked out in main rather than the recorded base. Detection: target branch not cross-checked against `WORKTREE.md` / the handoff. Resolution: default to the recorded base branch; if the currently checked-out branch differs, confirm which is the merge target before merging.
9. **Wrong cleanup order.** Running `git branch -d` before removing the worktree. Detection: branch deletion fails "used by worktree at …". Resolution: always `git worktree remove` FIRST (a branch checked out by a live worktree cannot be deleted), then `git branch -d`.
10. **Unquoted paths.** Worktree paths contain spaces on this machine. Detection: any unquoted path. Resolution: quote every path.
11. **Silently deleting a divergent hand-copied env.** Beyond what `worktree-create` provisioned, the user may have added or copied an env file by hand during the work. It is git-ignored, so it never appears in `git status` — `git worktree remove --force` deletes it permanently with no warning and no git history to recover from. Detection: before removal, an explicit scan finds a **regular-file** (not symlink) `.env*` in the worktree that is **not** script-provisioned (Anti-Pattern 13) and whose contents differ from main's, or that doesn't exist in main. Resolution: run env reconciliation (M5.5) BEFORE removal — surface the diff and let the user apply-to-main / preserve-aside / discard. **Legacy symlinked env files need nothing** (they *are* main's file; edits already landed there) — skip them. Note this is now the *uncommon* case: `worktree-create` requires the `.worktreeinclude` contract, so the default state of every new worktree is script-provisioned and excluded by Anti-Pattern 13.
12. **Blindly copying an env back over main's.** "Reconcile" turning into `cp worktree/.env main/.env` without a diff or a backup. Detection: overwriting main's `.env*` unconditionally. Resolution: main's env is untracked — there is no `git checkout` to undo a bad overwrite. Show the diff, confirm per file, and back up main's current version (`.env.bak`) before applying. Never auto-apply; when unsure, preserve both and let the user merge by hand.
13. **Reconciling a script-provisioned env back into main.** The most damaging failure in this skill, and it has a *direction*. This is the **default state of every worktree** `worktree-create` produces, since that skill requires the `.worktreeinclude` contract: it **copied** `.env` and then ran `.env-setup.sh`/`.bb-env-setup.sh`, which **rewrote every path variable to a worktree-local absolute path**. That copy is therefore *always* diverged from main — divergence is the entire point, not a change to review. Writing it back would fill main's `.env` with paths under a worktree that is about to be deleted, pointing production at directories that will not exist. Detection — either anchor is sufficient: the worktree's env file contains the marker line `# --- rewritten by .env-setup.sh for this worktree ---`, or the worktree's `WORKTREE.md` carries an `**Env setup:**` line (its `**Files copied:**` line is a corroborating signal). Resolution: **exclude these files from reconciliation entirely** — not a diff to review, not a writeback candidate. Skip them and say so ("`.env` was worktree-local by design; not reconciled"). Genuine env *additions* the user made by hand may be surfaced as a **read-only report**, never as an automatic writeback. And if the breadcrumb says `Env setup: FAILED` (or a `.env.UNSAFE-NOT-REWRITTEN` file is present), that worktree was never safely provisioned — reconciling from it is doubly wrong; report it and let it die with the worktree.

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

**H4b — Classify the worktree's env files (heads-up for the main session).** Three cases, and only the third is ever reconciled:

1. **Script-provisioned — the normal case.** `worktree-create` requires the `.worktreeinclude` contract, so every worktree it makes has env files that were copied and then rewritten to worktree-local paths by `.env-setup.sh`/`.bb-env-setup.sh`. They are diverged **by design**. Never a reconciliation candidate (Anti-Pattern 13).
2. **Symlinked — legacy only.** Worktrees created before `worktree-create` dropped its symlink fallback may still carry links. A link *is* main's file; edits already landed there. Nothing to do.
3. **Hand-copied** — a regular, unmarked file the user added or copied in during the work. This one would be **lost when the worktree is removed**, and it's git-ignored so `git status` won't show it.

Detect case 1 first, from the breadcrumb, then per file from the marker line:

```bash
# "<main>" is the main-repo path from WORKTREE.md.
grep -q '^- \*\*Env setup:\*\*' WORKTREE.md 2>/dev/null && echo "SCRIPT-PROVISIONED worktree — env is worktree-local by design"

find . -maxdepth 1 \( -name '.env' -o -name '.env.*' \) | while IFS= read -r f; do
  [ -L "$f" ] && continue                             # case 2: legacy symlink → shared with main; nothing to reconcile
  grep -q '^# --- rewritten by \.env-setup\.sh for this worktree ---' "$f" 2>/dev/null && continue   # case 1
  name="$(basename "$f")"; main_f="<main>/$name"
  if [ ! -e "$main_f" ]; then echo "env NEW here (absent from main): $name"
  elif ! diff -q "$f" "$main_f" >/dev/null 2>&1; then echo "env DIVERGED from main: $name"
  fi
done
```

The breadcrumb check will fire for essentially every worktree — add an **Env: worktree-local (script-provisioned) — do NOT reconcile** line to `HANDOFF.md` and the paste block, so the main session doesn't rediscover the divergence and mistake it for lost work. If the per-file scan *also* reports something (case 3 — a file the user added by hand, on top of the provisioned ones), add an **⚠ Env to reconcile** line naming only those files, so the main session runs M5.5 before removing the worktree. If neither fires, say nothing.

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

**M5.5 — Settle the worktree's env files (BEFORE removal).** Removing the worktree deletes its working files — including any *copied* `.env*`, which is git-ignored and therefore invisible to `git status` (Anti-Patterns 4, 11). But "copied" is not the same as "reconcile me": `worktree-create` requires the `.worktreeinclude` contract, so **every** worktree env is a copy, and a script-rewritten one must be **excluded from reconciliation entirely** (Anti-Pattern 13). Expect the gate below to fire and the answer to be "nothing to reconcile" on a normal worktree — that is the designed outcome, not a scan that failed to find anything.

**Gate first — is this worktree script-provisioned?** Either anchor is sufficient:

```bash
# "<worktree-path>" comes from the handoff, "<main>" is this repo's toplevel.
grep -n '^- \*\*Env setup:\*\*' "<worktree-path>/WORKTREE.md" 2>/dev/null       # breadcrumb anchor
grep -rl '^# --- rewritten by \.env-setup\.sh for this worktree ---' \
     "<worktree-path>"/.env "<worktree-path>"/.env.* 2>/dev/null                # per-file marker anchor
```

If either fires, **skip `.env` reconciliation for the matching files** and report exactly that:

> `.env` was worktree-local by design (rewritten by `.env-setup.sh`); not reconciled.

Do not show its diff as a decision, do not offer apply-to-main, and do not treat the divergence as lost work. If the user asks what changed, you may **surface hand-made additions read-only** — keys present in the worktree's file but absent from main's, e.g. `grep -vf <(cut -d= -f1 "<main>/.env") ...` presented as a report — and tell them to add anything they want by hand in main. Never turn that into a writeback. If the breadcrumb reads `Env setup: FAILED`, or a `.env.UNSAFE-NOT-REWRITTEN` file is present, say so plainly: that worktree was never safely provisioned, nothing from it goes back to main, and removal is the right outcome.

**Then scan whatever the gate did not exclude.** Run this in every case, not only when the gate misses — a script-provisioned worktree can still contain an env file the user added by hand during the work, and that one *is* a reconciliation candidate. The scan skips **legacy symlinks** (they already point at main's file) and **script-marked files** (worktree-local by design), leaving exactly the hand-made remainder:

```bash
find "<worktree-path>" -maxdepth 1 \( -name '.env' -o -name '.env.*' \) | while IFS= read -r f; do
  [ -L "$f" ] && continue                              # legacy symlink → shared with main; nothing to copy back
  grep -q '^# --- rewritten by \.env-setup\.sh for this worktree ---' "$f" 2>/dev/null && \
    { echo "worktree-local (script-rewritten), NOT reconciled: $(basename "$f")"; continue; }
  name="$(basename "$f")"; main_f="<main>/$name"
  if [ ! -e "$main_f" ]; then echo "NEW: $name"        # exists here, not in main → offer to copy in
  elif ! diff -q "$f" "$main_f" >/dev/null 2>&1; then echo "DIVERGED: $name"   # differs → show diff, offer to apply
  else echo "identical: $name"; fi                     # same → nothing to do
done
```

For each **NEW** or **DIVERGED** file, show the diff (`diff "<main>/<name>" "<worktree-path>/<name>"`) and let the user choose — never auto-apply, never blind-overwrite (Anti-Pattern 12):

- **Apply to main** — back up main's current file first (`cp "<main>/<name>" "<main>/<name>.bak"`), then copy the worktree's version over it. (main's env is untracked; the `.bak` is the only undo.)
- **Preserve aside** — copy the worktree's version into main under a side name (`cp "<worktree-path>/<name>" "<main>/<name>.from-worktree"`) so nothing is lost and the user merges by hand later.
- **Discard** — proceed to removal; the worktree's copy dies with it. Confirm explicitly, since it's unrecoverable.

If everything is script-provisioned, a legacy symlink, or identical — the expected result for a normal worktree — say "env: nothing to reconcile" and move on. Only after this is settled proceed to M6.

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

  Env: worktree-local (script-provisioned by .env-setup.sh) — do NOT reconcile .env
    back into main; its paths point inside this worktree. (Present whenever
    WORKTREE.md carries an "Env setup:" line, i.e. on every normal worktree.)

  ⚠ Env to reconcile: .env.test  (added here BY HAND, on top of the provisioned files,
    and absent/diverged from main — reconcile before removing the worktree, or it is
    lost. Omit this line unless the M5.5 scan turns up such a file.)

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
  Env:              .env was worktree-local by design (script-provisioned); not reconciled
  Removed worktree: ../claude-plugins-WT/pablo-oliva/fix-login-redirect
  Deleted branch:   pablo-oliva/fix-login-redirect
```

The `Env:` line above is the normal one — state the skip explicitly rather than omitting it, so the user can see the decision was made deliberately. When a hand-added file *was* reconciled, say what happened to it too:

```
  Env:              .env worktree-local (not reconciled); .env.test applied to main (backup at .env.test.bak)
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

### GOOD — a hand-added env file alongside the provisioned ones

Merge is clean. The worktree **is** script-provisioned, so `.env` is excluded outright. But the M5.5 scan also turns up `.env.test` — a regular file with no rewrite marker, absent from main, which the user created by hand during the work to hold a test key. It is not part of the provisioning contract, nothing rewrote it, and removal would delete it with no git history to recover from. **Right:** report `.env` as not-reconciled-by-design, then show `.env.test` separately and offer to apply it to main (backing up first), preserve it as `.env.test.from-worktree`, or discard — and only proceed to removal once the user picks. **Wrong:** either extreme — running `git worktree remove --force` straight away and losing it, or sweeping it into the same "worktree-local, skip it" bucket as `.env` because the worktree is script-provisioned. The gate excludes *marked* files, not every file.

### GOOD — script-provisioned worktree: skip reconciliation entirely

Merge is clean. `WORKTREE.md` carries `- **Env setup:** .env-setup.sh ran OK — .env paths rewritten to worktree-local values`, and the worktree's `.env` contains `# --- rewritten by .env-setup.sh for this worktree ---`. The file differs from main's in every path variable. **Right:** do not diff it as a decision and do not offer apply-to-main — report "`.env` was worktree-local by design (script-provisioned); not reconciled" and go straight to the removal gate. If the user asks what they changed by hand, list keys present here and absent in main as a **read-only** report. **Wrong:** treating "regular file + diverged from main" as the trigger it used to be and offering to apply it — that would write `/…/claude-plugins-WT/pablo-oliva/feature-x/out` into main's `.env` as the production output directory, and the very next step deletes that directory.

## Questions This Skill Answers

- "Generate a handoff for this worktree."
- "I'm done in this worktree — wrap it up."
- "Merge this worktree back into main and clean it up."
- "Integrate the handoff I just pasted."
- "Merge `<branch>` and remove its worktree."

## Scope Boundary

This skill handles the **return trip** of a worktree created by `worktree-create`: it produces a handoff from inside the worktree and, in the main repo, merges the branch and (with confirmation) removes the worktree and deletes the branch. Before removal it settles the worktree's env files under a three-way classification: **script-provisioned** files (copied per `.worktreeinclude` and rewritten by `.env-setup.sh`/`.bb-env-setup.sh`) are excluded from reconciliation entirely — this is the normal case for every worktree `worktree-create` produces, since that skill requires the contract, and writing such a file back would point main at directories the removal is about to delete; **symlinked** files need nothing, as their edits already reached main, and appear only in worktrees predating the contract requirement; only a **hand-added** file that diverged is offered for reconciliation, where it shows the diff and lets the user apply-to-main, preserve-aside, or discard. It never overwrites main's env or deletes a diverged copy without an explicit choice, and never writes a worktree's env back into main automatically under any classification. It never force-deletes unmerged work, never cleans up after a conflicted or failed merge, and never removes a worktree or branch without an explicit yes. Creating worktrees is out of scope — that's `worktree-create`.
