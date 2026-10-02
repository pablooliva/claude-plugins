---
name: worktree-merge
description: "INVOKE THIS SKILL when work done in a git worktree should go back into the main line — e.g. 'merge this worktree back', 'merge this into main', 'land this branch', 'I'm done in this worktree', 'wrap up this worktree', 'hand this back to main'. Works on any linked worktree and is adapted to BB IDE, where each thread runs in a BB-managed worktree on a `bb/…` branch. Resolves the target branch (BB's recorded default branch, else the remote's default) and confirms it, requires the work to be committed, brings the branch up to date with the target INSIDE the worktree (so conflicts are resolved there, never in the main checkout), verifies, then fast-forwards the target branch — or opens a pull request instead when asked. In a repo with an `SDD/` folder it also detects ADR and feature numbers that this branch and the target both claimed, and renumbers this branch's side once the user has approved the old → new mapping. Before the worktree goes away it surfaces git-ignored files that exist only there (hand-made `.env*` and the like), without ever writing a script-rewritten env back into the main checkout. Cleanup depends on who owns the worktree: a BB-managed worktree is left for BB to remove when its thread is archived; any other worktree is removed and its branch deleted, with confirmation before each step. Never force-deletes unmerged work, never cleans up after a failed merge, never pushes unasked."
---

# Worktree Merge

Lands the work done in a linked git worktree on the main line, then deals with what is left behind. It runs **from inside the worktree** (the normal case in BB IDE: the thread that did the work finishes it) or from the main checkout with a branch named.

One rule shapes the whole flow: **the target branch only ever fast-forwards.** Any divergence is settled on the work branch, inside the worktree, where the session has the context to resolve conflicts and re-run checks. The main checkout — which may hold someone's uncommitted work — is never left mid-merge.

## Expert Vocabulary

Linked worktree vs. main worktree (`--git-dir` ≠ `--git-common-dir`). Target branch. Merge base. Ahead/behind. Fast-forward-only integration. Rebase vs. merge-in for syncing. Published branch (exists on a remote). Checked-out-elsewhere branch (`git worktree list --porcelain`). Ref-only fast-forward (`git fetch . <src>:<dst>`). Dirty tree guard. Git-ignored files invisible to `git status`. Provisioned copy (`.worktreeinclude`) and rewrite marker line. Reconciliation direction (worktree → main is the dangerous one). BB-managed environment, thread archive, retirement grace, teardown hook. `git branch -d` (safe) vs. `-D` (force). Confirmation gate. SDD number collision (same `NNNN` or `[###]`, different slug — no git conflict). Branch-added vs. branch-modified file.

## Anti-Pattern Watchlist

1. **Merging in the main checkout.** Running a real merge (one that can conflict) where the target branch is checked out. Detection: `git merge` without `--ff-only` outside the worktree. Resolution: sync on the work branch first (Step 3); the target only fast-forwards (Step 5).
2. **Guessing the target branch.** Detection: target taken from whatever is checked out somewhere, never shown to the user. Resolution: resolve it (Step 1) and state it before integrating; ask when sources disagree.
3. **Handing off uncommitted work.** Detection: `git status --porcelain` non-empty in the worktree. Resolution: stop; offer to commit. Only committed work lands.
4. **Rewriting published history.** Rebasing a branch that exists on a remote, then force-pushing. Detection: `git for-each-ref "refs/remotes/*/<branch>"` prints a ref. Resolution: merge the target in instead, or ask.
5. **Pressing on after a failed sync or check.** Detection: rebase/merge stopped on conflicts that could not be resolved with confidence, or the project's checks fail afterwards. Resolution: abort (`git rebase --abort` / `git merge --abort`) or stop, report, and leave everything intact. No integration, no cleanup.
6. **Removing a BB-managed worktree by hand.** `git worktree remove` on a worktree BB owns skips BB's teardown hook, leaves BB's environment record pointing at a missing directory, and usually deletes the running session's own working directory. Detection: about to remove a worktree whose `bb environment show` reports `managed: true`. Resolution: leave it; BB removes it after the thread is archived (Step 7).
7. **Force-deleting a branch.** Detection: reaching for `git branch -D` after `-d` refused. Resolution: the refusal means the commits are not in the target — stop and say so.
8. **Skipping the confirmation gate.** Detection: a worktree removal, branch deletion, or push issued without an explicit yes. Resolution: ask before each.
9. **Losing git-ignored files.** A hand-made `.env.test` never appears in `git status`, and dies with the worktree. Detection: cleanup reached without the Step 6 scan. Resolution: scan first.
10. **Writing a worktree's env back over main's.** A provisioned env file was copied from the main checkout and then rewritten by the repo's setup script so every path points inside the worktree; it differs from main's by design. Copying it back points the main checkout at a directory that is about to be deleted. Detection: file contains the marker line, or is in the main checkout's provisioning list (Step 6). Resolution: never a writeback candidate (Step 6).
11. **Unquoted paths.** Checkout paths contain spaces. Resolution: quote every path.
12. **Landing duplicate SDD numbers.** Two ADRs numbered `0011`, or two features numbered `045`, merge cleanly and leave every later `ADR-0011` reference ambiguous. Detection: repo has `SDD/` and Step 3b was not run. Resolution: run the detection on every run; it is cheap and silent when clean.
13. **Renumbering the wrong side, or by blanket search-and-replace.** Renaming the target's artifact, or replacing `SPEC-045` everywhere, rewrites references that belong to the feature that landed first. Detection: a rename of a file the branch did not add, or an edit to a line the branch did not add. Resolution: only branch-added files are renamed; in branch-modified files only branch-added lines change; nothing changes before the user approves the mapping.

## When to Activate

- The user is done with work in a worktree and wants it on the main line: "merge this back", "land this", "wrap up this worktree", "merge into main/master".
- From the main checkout: "merge `<branch>` and clean up its worktree".

## When NOT to Activate

- **Not a linked worktree and no worktree named.** A plain branch merge needs no skill.
- **Work still in progress.** Nothing to land yet.
- **Creating a worktree.** BB IDE does that when a thread starts.
- **Preparing a repo for worktrees** (`.worktreeinclude`, `.bb-env-setup.sh`). That is `bb-worktree-init`.
- **Not a git repo.** Stop and say so.

## Behavioral Instructions

### Step 0: Locate everything

```bash
git rev-parse --show-toplevel                        # this checkout
git rev-parse --git-dir --git-common-dir             # differ ⇒ this is a linked worktree
git worktree list --porcelain                        # first entry = main checkout; each entry lists its branch
git rev-parse --abbrev-ref HEAD
```

Record: **WT** (the worktree holding the work), **BRANCH** (its branch), **MAIN** (the main checkout path). If running from the main checkout, the user names the branch and WT is the `git worktree list` entry that has it checked out; run the Step 2–4 git commands as `git -C "<WT>" …`.

Is WT BB-managed? Only when `$BB_ENVIRONMENT_ID` is set and its record matches:

```bash
bb environment show "$BB_ENVIRONMENT_ID" --json      # managed: true, path == WT ⇒ BB-managed; note defaultBranch
```

`bb guide environments` is the authority on BB's behavior if anything below looks out of date.

### Step 1: Resolve the target branch

In order: a branch the user named → BB's `defaultBranch` → `git symbolic-ref --short refs/remotes/origin/HEAD` (strip `origin/`) → whichever of `main` / `master` exists. The target is the **local** branch. State it ("landing `<BRANCH>` on `main`"); ask if the sources disagree or none resolves.

Then `git fetch` and report where the local target stands against its upstream. If it is behind, ask whether to fast-forward it first — do not decide silently. Note where the target is checked out (TARGET_WT, from `git worktree list --porcelain`), if anywhere.

### Step 2: Require committed work

```bash
git status --porcelain
git log --oneline "<target>..<BRANCH>"
git diff --stat "<target>...<BRANCH>"
```

Dirty tree ⇒ stop and offer to commit. No commits ahead of the target ⇒ nothing to land; say so and skip to Step 6.

### Step 3: Bring the branch up to date (inside WT)

Skip if the branch is not behind the target (`git rev-list --count "<BRANCH>..<target>"` is 0). Otherwise:

- **Branch not published** (`git for-each-ref "refs/remotes/*/<BRANCH>"` prints nothing): `git rebase "<target>"`.
- **Branch published**, or the repo's instructions ask for merge commits: `git merge "<target>"`.

Resolve conflicts here, with the context of the work just done. If a conflict cannot be resolved with confidence, abort the operation, report the conflicting files, and stop.

### Step 3b: SDD number collisions (only when the repo has `SDD/`)

Skip unless `SDD/` exists at the repo root. SDD artifacts are numbered by listing what the checkout already has, and a worktree cannot see numbers taken by work that had not landed when it was created. Two threads can therefore claim the same ADR number or feature number, and the duplicates merge with **no git conflict** because the filenames differ. Now that the branch contains the target (Step 3), both sides are in the tree and the collision is visible. Always run the detection:

```bash
# ADR numbers carried by more than one file
git ls-files 'SDD/adr/[0-9][0-9][0-9][0-9]-*.md' | sed -E 's#^SDD/adr/([0-9]{4})-.*#\1#' | sort | uniq -d
# feature numbers ([###]) carried by more than one feature name
git ls-files 'SDD/requirements/SPEC-*.md' 'SDD/research/RESEARCH-*.md' \
  | sed -E 's#.*/(SPEC|RESEARCH)-([0-9]+)-(.*)\.md$#\2 \3#' | sort -u | awk '{print $1}' | uniq -d
# what this branch added — the only files that may be renumbered
git diff --name-only --diff-filter=A "<target>" HEAD -- SDD/
```

No output from the first two ⇒ say "SDD numbers: no collisions" and move on.

For each duplicated number, the side to renumber is **this branch's** — the target's number has already landed and may be referenced elsewhere. If neither colliding file was added by this branch, the duplicate predates this work: report it and leave it alone.

New number = the highest in use across the whole tree, plus one (four digits for ADRs; the width the repo already uses for features), assigned in ascending order when several collide. Then show the plan and **wait for a yes** before changing anything:

- the **old → new mapping** (`ADR-0011 → ADR-0013`, `SPEC-045 → SPEC-047`);
- the **renames**: every branch-added file carrying the old number — for an ADR, `SDD/adr/NNNN-slug.md`; for a feature, each `SDD/**` artifact with that `[###]` and this feature's name (`CLARIFICATION-`, `RESEARCH-`, `SPEC-`, `DECOMPOSITION-`, `IMPLEMENTATION-PLAN-`, `REVIEW-`, `SLICE-`), plus the branch-added `IMPLEMENTATION-SUMMARY-[###]-*`;
- the **reference edits**: hits for the old identifiers (`ADR-0011`, `0011-slug`, `SPEC-045`, `RESEARCH-045`, …) from `git grep -n` over the files this branch added or modified (`git diff --name-only "<target>" HEAD`), code and docs included.

On confirmation: `git mv` each rename; in files the branch **added**, replace throughout; in files the branch only **modified** (`SDD/adr/README.md`, `SDD/orchestration/progress.md`, the glossary, source comments), change only lines this branch added (`git diff -U0 "<target>" HEAD -- <file>`) — the same identifier on any other line belongs to the feature that landed first. Re-run the detection (it must print nothing), then commit the renumbering on the branch as its own commit so Step 4 verifies it.

If the user declines, stop and say the duplicates are still there; land them only on an explicit instruction to do so.

### Step 4: Verify

If the branch moved in Step 3 or Step 3b, or checks have not been run on the final commits, run the project's test/build command and report the result. A failure stops the run. Do not invent a result for checks that were not run.

### Step 5: Integrate

Default — fast-forward the local target:

```bash
git -C "<TARGET_WT>" merge --ff-only "<BRANCH>"      # target checked out somewhere (usually MAIN)
git fetch . "<BRANCH>:<target>"                      # target checked out nowhere: moves the ref, fast-forward only
```

Uncommitted changes in TARGET_WT are carried along untouched; if they overlap the incoming files git refuses — report that and stop, do not stash or discard them. A refusal for any other reason means Step 3 was skipped or the target moved; go back to Step 3.

If the repo's instructions require a merge commit, use `git -C "<TARGET_WT>" merge --no-ff "<BRANCH>"` — safe at this point because the branch already contains the target.

**Pull-request route** — when the user asks for a PR, or the target cannot be pushed to directly: confirm, then `git push -u origin "<BRANCH>"` and `gh pr create --base "<target>"`. The local target is not touched; the work has landed only once the PR merges (`gh pr merge`, or `bb environment pull-request merge "$BB_ENVIRONMENT_ID" --method <merge|squash|rebase>`). Until then, treat Step 7's cleanup as premature.

After a local fast-forward, report whether the target is now ahead of its upstream and **offer** to push. Never push unasked.

### Step 6: Scan for files that would die with the worktree

Git-ignored files are invisible to `git status` and are not on the branch. List them, ignoring dependency and build directories:

```bash
git -C "<WT>" status --porcelain --ignored           # "!!" entries
git -C "<MAIN>" ls-files -o -i --exclude-from=.worktreeinclude 2>/dev/null   # what provisioning copies from MAIN
```

Classify each ignored **file** in WT:

- **Provisioned** — its path is in MAIN's provisioning list above (so it was copied from MAIN when the worktree was created), or it contains the line `# --- rewritten by .env-setup.sh for this worktree ---`. Worktree-local by design. Never offer to copy it back. If the user asks what they added by hand, list keys present here and absent from main's copy as a read-only report (names only, never values).
- **Identical** to the same path in MAIN — nothing to do.
- **Hand-made** — absent from MAIN, or different and not provisioned. Show the names (a diff only for non-secret files) and let the user choose per file: **apply to main** (first `cp "<MAIN>/<f>" "<MAIN>/<f>.bak"` — an untracked file has no other undo), **preserve aside** (`cp "<WT>/<f>" "<MAIN>/<f>.from-worktree"`), or **discard**.

Nothing found ⇒ say "nothing to preserve" and move on. Run this even when Step 7 leaves the worktree in place: BB removes it later, with no further prompt.

### Step 7: Clean up

Only after the work has landed (Step 5 fast-forward done, or PR merged).

**BB-managed worktree.** Do not remove it and do not delete its branch (a checked-out branch cannot be deleted). Tell the user: archiving the thread is what retires it — once the last thread in the environment is archived BB waits five minutes, runs `.bb-env-teardown.sh` if the repo has one, stops every process running inside the worktree, and removes it. **BB keeps the branch.** So offer, with confirmation, to sweep branches left by earlier threads:

```bash
git worktree prune
git branch --merged "<target>" --format='%(refname:short)'    # candidates; drop <target> and any branch listed in `git worktree list --porcelain`
git branch -d "<name>"                                        # one per confirmed branch; never -D
```

This thread's own branch becomes sweepable the next time, after BB has removed its worktree.

**Any other linked worktree.** Ask before each step; run from MAIN, since removing WT from a session inside it deletes that session's working directory (if running inside WT, say so and offer to leave the two commands for the user):

```bash
git -C "<MAIN>" worktree remove "<WT>"     # refuses if WT has modified/untracked files — inspect them; --force only after the user has seen the list
git -C "<MAIN>" branch -d "<BRANCH>"       # worktree first: a checked-out branch cannot be deleted
```

If the repo has a `.bb-env-teardown.sh` and the worktree was provisioned with its setup script, mention that nothing has run the teardown.

### Step 8: Report

What landed and where the target now points, check results, what was preserved or discarded, what was cleaned up, and what remains for the user (archive the thread, push, merge the PR).

## Output Format

```
Landed ✓
  bb/fix-login-redirect-thr_ab12 → main   (rebased onto main, fast-forward to a1b2c3d, 2 commits)
  SDD:       ADR-0011 → ADR-0013 (collided with main); 1 file renamed, 4 references updated
  Checks:    npm test — 42 passed
  Ignored:   .env provisioned (not copied back); .env.test preserved as .env.test.from-worktree
  Worktree:  BB-managed — archive this thread and BB removes it after 5 minutes
  Branches:  deleted 3 merged bb/* branches from earlier threads
  Remaining: main is 2 ahead of origin/main — not pushed
```

When the run stops early, lead with the reason and state that nothing was integrated or removed.

## Examples

### GOOD — BB thread, target moved while the work was in progress

BRANCH is 1 ahead and 1 behind `main`, never pushed. Rebase onto `main` inside the worktree, re-run the checks, `git -C "<MAIN>" merge --ff-only "<BRANCH>"`, scan ignored files, then tell the user to archive the thread and offer the merged-branch sweep. The main checkout never saw a conflict.

### GOOD — conflict that cannot be resolved with confidence

The rebase stops on a file both sides rewrote and the right result is unclear. `git rebase --abort`, report the file and the two competing changes, stop. The target is untouched and the worktree is exactly as it was.

### BAD — tidying up a BB worktree

After the fast-forward, running `git worktree remove --force` on the BB-managed worktree and `git branch -D` on its branch. The session's own directory vanishes, BB's teardown hook never runs, and BB still lists the environment. **Right:** leave both; archiving the thread retires the worktree, and the branch is swept later with `-d`.

### BAD — copying the worktree's `.env` back

`.env` in the worktree differs from main's, so it is offered as "changes to apply". It differs because the setup script rewrote its paths to point inside the worktree. **Right:** it was copied from main per `.worktreeinclude` (or carries the marker line), so it is reported as provisioned and never written back.

### GOOD — two threads both wrote ADR 0011

After the rebase the tree holds `SDD/adr/0011-use-postgres.md` (already on `main`) and `SDD/adr/0011-queue-retries.md` (added here). Show `ADR-0011 → ADR-0012`, the one rename, and the four lines that mention it — the ADR itself, this branch's row in `SDD/adr/README.md`, the spec's `cross_cutting_decisions`, and one code comment. On yes: `git mv`, edit those lines, re-run the detection, commit, then verify and land. `main`'s ADR and every reference to it are untouched.

## Questions This Skill Answers

- "Merge this worktree back into main."
- "I'm done here — land this and clean up."
- "Merge `<branch>` and remove its worktree."
- "Open a PR for this worktree's work."
- "What happens to this worktree once it's merged?"

## Scope Boundary

This skill lands a linked worktree's committed work on a target branch — by fast-forwarding the local branch after syncing inside the worktree, or by pull request — detects SDD number collisions and renumbers this branch's side on confirmation, surfaces git-ignored files that would be lost, and cleans up according to ownership: BB-managed worktrees are left to BB's thread-archive teardown, others are removed with their branch on confirmation. It does not create worktrees (BB IDE does), does not author provisioning files (`bb-worktree-init`), does not run teardown hooks, does not push, delete, or renumber without an explicit yes, never renumbers an artifact that has already landed, and never writes a provisioned env file back into the main checkout.
