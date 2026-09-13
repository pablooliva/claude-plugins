---
name: bb-worktree-init
description: "INVOKE THIS SKILL when the user wants to make a new or existing repository ready for isolated worktrees — e.g. 'set this project up for BB worktrees', 'add a .worktreeinclude', 'write an env setup script', 'make worktrees work in this repo', 'bootstrap worktree provisioning', or when `worktree-create` stopped because the repo lacks `.worktreeinclude` or `.env-setup.sh`. Inspects the repo (untracked config, env keys that hold paths or point at real external sinks, dependency lockfiles, local databases, git-ignored runtime dirs), proposes a provisioning plan for the user to approve, then renders its bundled templates into `.worktreeinclude`, `.env-setup.sh`, a `.bb-env-setup.sh` symlink, and — only when setup creates resources outside the worktree — `.bb-env-teardown.sh`. Validates the result (syntax check, dry-run of what would be copied, optional throwaway-worktree trial). Also audits and upgrades these files in a repo that already has them. Never prints env values, never commits, never creates a worktree for real work."
---

# BB Worktree Init

Authors the **BB IDE worktree provisioning contract** for a repository, so both BB IDE and the `worktree-create` skill can create worktrees that are usable and safe.

A worktree checks out from a commit, so it has none of the repo's git-ignored files — no `.env`, no dependencies, no local database. The contract fixes that with files committed at the repo root:

1. **`.worktreeinclude`** — gitignore-syntax list of *untracked* files to **copy** into each new worktree.
2. **`.env-setup.sh`** — the canonical script, run from the new worktree's root *after* the copies land. Installs dependencies, snapshots data, and **rewrites the copied env files** so every path points inside the worktree. `worktree-create` runs this name.
3. **`.bb-env-setup.sh` → `.env-setup.sh`** (required symlink) — **the only name BB IDE runs.** BB never looks for `.env-setup.sh`. And when `.bb-env-setup.sh` is absent BB does not fail: it copies `.worktreeinclude` files, skips setup silently, and opens a worktree whose `.env` still points at main. One script, two names, so the two callers can't drift apart.
4. **`.bb-env-teardown.sh`** (optional) — run by BB before it deletes a worktree, for resources setup created *outside* the worktree.

Copying without rewriting is the hazard this skill exists to prevent: a copied `.env` still holds main's absolute paths, so a worktree that looks sandboxed writes into the main checkout's database, output directory, or a live publish target.

Lifecycle position:

1. **`bb-worktree-init`** (this skill) — one-time, per repo: author the contract.
2. **`worktree-create`** — per task: create a worktree using the contract.
3. **`worktree-handoff`** — per task: merge back and clean up.

Bundled files (read by path when needed):

- `templates/worktreeinclude.template`
- `templates/env-setup.sh.template`
- `templates/bb-env-setup.sh` — symlink to `env-setup.sh.template`, mirroring the layout the repo ends up with (Step 4 creates the repo's own symlink; don't copy this one)
- `templates/env-teardown.sh.template`
- `references/fill-recipes.md` — what goes in each `@@PLACEHOLDER@@`, per ecosystem

## BB Run Contract (the facts the templates encode)

- Both hooks and `.worktreeinclude` **must be committed** — BB reads them from inside the fresh worktree, which only has tracked files.
- BB copies `.worktreeinclude` matches **before** setup runs. Files only; symlinks in the source are skipped; nothing existing is replaced; unmatched patterns and unreadable files are reported, not fatal.
- Hooks run as `env bash <script>`, cwd = worktree root, stdin closed, **15-minute timeout**, with a sanitized environment: `NODE_ENV` and every `BB_*` variable removed, and **no source-checkout path provided** — the script finds main via `git rev-parse --git-common-dir`.
- Setup: non-zero exit, timeout, signal, or cancel **fails provisioning and BB deletes the worktree**. Teardown: failure is reported, worktree deleted anyway.
- Hooks run only for newly created BB-managed worktrees. `worktree-create` runs main's `.env-setup.sh` itself with the same contract; `worktree-handoff` does **not** run teardown.
- `worktree-handoff` skips reconciling any env file containing the exact line `# --- rewritten by .env-setup.sh for this worktree ---`. The template emits it; keep it verbatim.

Confirm against `bb guide environments` if the `bb` CLI is available — it is the authoritative source and may have changed since this skill was written.

## Anti-Pattern Watchlist

1. **Printing secrets.** Echoing `.env` contents into the conversation to classify keys. Detection: any `cat .env`, or a command whose output includes values. Resolution: extract key names and a value *shape* only (Step 2's classifier). Values never enter the transcript.
2. **Copying what should be rebuilt.** Listing `node_modules/`, `.venv/`, `target/`, or a database in `.worktreeinclude`. BB copies directories file by file (slow), venvs carry absolute shebangs pointing at main, and a copied live SQLite file can be torn. Resolution: install in `@@DEPS@@`, snapshot in `@@DATA@@`, and record the exclusion with its reason in the template's `EXCLUDED` section.
3. **Rewriting without verifying.** `set_env` without `|| die`, or a key rewritten but not listed in `@@VERIFY_KEYS@@`. A silent rewrite failure reports success while the worktree points at main's sinks. Resolution: every path key is in the verify loop; every non-path key (URL, port) has its own check.
4. **Guessing which sinks are dangerous.** Deciding alone that `OUTPUT_DIR` is harmless. Resolution: the classification is a plan the user approves (Step 3). You propose from evidence; they know which directory feeds production.
5. **Fatal optional steps.** `die` on a failed cache copy or migration. BB deletes the worktree on any non-zero exit. Resolution: `die` only when the worktree would be unusable (no deps) or unsafe (env not rewritten, symlinked env); everything else `warn`.
6. **Hardcoded paths.** An absolute main-checkout path baked into the script. It breaks on every other machine and in every BB data dir. Resolution: `$WT` and `$MAIN` only.
7. **Uncommitted hooks.** Writing the files and reporting done without saying they must be committed. BB silently skips a hook it can't find in the worktree. Resolution: the final report says so explicitly (the skill does not commit).
8. **Overwriting existing files.** Replacing a hand-tuned `.env-setup.sh` with a fresh render. Resolution: existing files switch the skill to audit mode (Step 1); changes are proposed as edits, applied only on approval.
9. **Teardown for nothing.** Writing `.bb-env-teardown.sh` when setup creates nothing outside the worktree. Resolution: only when `@@DATA@@` or `@@DEPS@@` creates an external resource (server DB, container, global cache entry).
10. **Trialing in a real worktree location.** Testing the script by creating a worktree alongside real ones and leaving it. Resolution: Step 6's trial uses a temp directory and removes the worktree and branch afterwards, on the user's approval.
11. **Missing or broken `.bb-env-setup.sh`.** Writing `.env-setup.sh` and stopping there, or leaving the symlink as a duplicate file, an absolute-target link, or a link to a renamed script. BB only runs `.bb-env-setup.sh`, and an absent one is **not** an error — the worktree opens with an un-rewritten `.env`, which is the unsafe outcome. A duplicate file drifts from `.env-setup.sh`, so BB and `worktree-create` provision differently. Resolution: always create it as a *relative* symlink (`ln -s .env-setup.sh .bb-env-setup.sh`), check it in Step 5, run the trial through it in Step 6, and include it in the commit hint.
12. **Leftover placeholders.** Shipping a script with `@@DEPS@@` still in it — a bash syntax trap at best, a silently skipped step at worst. Resolution: Step 5 greps for `@@` and fails validation if any remain.

## When to Activate

- The user asks to set up, bootstrap, or fix worktree provisioning for a repo — new or existing.
- `worktree-create` stopped at its precondition gate and the user accepted the offer to author the missing files.
- The user wants an existing `.worktreeinclude` / `.env-setup.sh` reviewed or brought up to the current contract.

## When NOT to Activate

- **The user wants a worktree now** and the repo is already provisioned — that is `worktree-create`.
- **Not a git repository** — tell the user; stop.
- **The user only wants BB agent-instruction files** (`AGENTS.md`, `.bb/skills/`) — see `bb guide agent-configuration`; not this skill.

## Behavioral Instructions

Execute in order. Quote every path — repo paths on this machine contain spaces.

### Step 1: Verify context and pick the mode

```bash
git rev-parse --show-toplevel                         # fails → not a repo; stop
git rev-parse --path-format=absolute --git-common-dir # parent ≠ toplevel → inside a linked worktree
for f in .worktreeinclude .env-setup.sh .bb-env-setup.sh .bb-env-teardown.sh; do
  if [ -L "$f" ]; then echo "$f -> $(readlink "$f")"; elif [ -e "$f" ]; then echo "$f (file)"; else echo "$f MISSING"; fi
done
git ls-files .worktreeinclude .env-setup.sh .bb-env-setup.sh .bb-env-teardown.sh   # which are committed
```

- **Inside a linked worktree:** warn — the files belong in the main checkout, and a worktree's copied `.env` has already been rewritten, so discovery would read the wrong values. Ask before continuing.
- **Mode = create** when none of the files exist.
- **Mode = audit** when any exists. Read them in full, then continue discovery; Step 3's plan becomes a list of proposed edits against the existing files (missing verify loop, missing marker line, `python3` dependency in a non-Python repo, hardcoded paths, symlinked-env guard absent, uncommitted files, `.bb-env-setup.sh` not a symlink to `.env-setup.sh`, and so on). Never overwrite (Anti-Pattern 8).
- **`.env-setup.sh` present but `.bb-env-setup.sh` missing** is the most common audit finding and the most urgent: BB is skipping setup today. Put the symlink first in the proposed edits, and warn that worktrees BB already created from this repo may hold un-rewritten `.env` copies.
- **Only `.bb-env-setup.sh` exists, as a real file** (BB's convention alone): propose renaming it to `.env-setup.sh` (`git mv` if tracked) and symlinking the old name back, so `worktree-create` and BB share one script.

### Step 2: Discover

Run these from the repo toplevel. None of them print env values.

**Untracked, ignored files and dirs** — the candidates for copying:
```bash
git ls-files -o -i --exclude-standard --directory | head -100
```

**Env-family files and their keys, classified by value shape only:**
```bash
for f in .env .env.*; do
  [ -f "$f" ] || continue
  git ls-files --error-unmatch "$f" >/dev/null 2>&1 && { echo "== $f (TRACKED — not copied)"; continue; }
  echo "== $f"
  awk -v home="$HOME" -v main="$(pwd)" '
    /^[ \t]*(#|$)/ { next }
    {
      s = $0; sub(/^[ \t]*(export[ \t]+)?/, "", s)
      eq = index(s, "="); if (!eq) next
      k = substr(s, 1, eq - 1); v = substr(s, eq + 1); gsub(/^["\047]|["\047]$/, "", v)
      if (v == "")                            t = "empty"
      else if (index(v, main) == 1)           t = "ABS PATH in main checkout"
      else if (index(v, home) == 1 || v ~ /^\//) t = "ABS PATH outside checkout"
      else if (v ~ /^~\//)                    t = "HOME-relative path"
      else if (v ~ /^\.{0,2}\/|^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.\/-]*$/) t = "relative path"
      else if (v ~ /^[a-z][a-z0-9+.-]*:\/\//) {
        t = "URL"; if (v ~ /localhost|127\.0\.0\.1|0\.0\.0\.0/) t = "URL (local)"
        if (v ~ /^(postgres|postgresql|mysql|mongodb|redis|sqlite)/) t = t " — DATABASE"
      }
      else if (v ~ /^[0-9]{2,5}$/ && k ~ /PORT/) t = "port"
      else if (k ~ /(KEY|TOKEN|SECRET|PASSWORD|PASS|CREDENTIAL)/) t = "secret (leave alone)"
      else                                    t = "other"
      printf "  %-40s %s\n", k, t
    }' "$f"
done
```

**Ecosystems** — lockfiles decide `@@DEPS@@`:
```bash
ls uv.lock poetry.lock requirements*.txt package-lock.json pnpm-lock.yaml yarn.lock bun.lock bun.lockb Cargo.lock go.sum Gemfile.lock 2>/dev/null
```

**Local databases and large data:**
```bash
git ls-files -o -i --exclude-standard | grep -E '\.(db|sqlite3?|duckdb)$' | head
git ls-files -z -o -i --exclude-standard --directory | while IFS= read -r -d '' d; do
  case "$d" in */) du -sh "$d" 2>/dev/null ;; esac
done | sort -h | tail -10
```

**Where env keys are consumed** — to learn what a key does and whether relative paths resolve against cwd:
```bash
git grep -n -E '<KEY1>|<KEY2>' -- ':!*.lock' | head -40
```
Run this for every key classified as a path, URL (local), port, or `other` with a name suggesting a sink (`*_DIR`, `*_PATH`, `*_HOOK`, `*_VAULT`, `*_OUTPUT*`, `*_BUCKET`, `*WEBHOOK*`). Also read the project's `CLAUDE.md`/`AGENTS.md`/README for test commands and "never touch X" warnings, and any `conftest.py`/test setup that guards against running against production.

### Step 3: Propose the plan and get approval

Present one plan. The user approves or corrects it before anything is written — this is where Anti-Pattern 4 is prevented.

- **Copy (`.worktreeinclude`)** — each pattern, one clause of why.
- **Not copied** — each large or rebuildable item and what replaces it (install, snapshot, opt-in).
- **Env rewrites** — per key: new value under `$WT`, and for anything that in main reaches outside the checkout, the concrete consequence of *not* rewriting it ("writes land in your real Obsidian vault"). Mark keys to **blank** (deploy/publish hooks) and keys **deliberately left alone** (secrets; shared global locks) with the reason.
- **Dependencies** — the install command per lockfile.
- **Data** — snapshot method, opt-in flags.
- **Post-install** — migrations, codegen.
- **Teardown** — needed or not, and why.
- **Open questions** — anything the evidence could not settle (a key whose consumer you couldn't find; a directory that may feed production). Ask them here, in the same message.

Use `AskUserQuestion` only for genuine forks (e.g. "copy the 400 MB model cache, make it opt-in, or skip it?"). Everything else goes in the plan for a single approval.

### Step 4: Render the files

Read the templates and `references/fill-recipes.md`, then write:

1. **`.worktreeinclude`** from `templates/worktreeinclude.template` — fill each `@@SECTION:*@@` block with the approved patterns and comments, then delete the `@@SECTION:*@@` marker lines.
2. **`.env-setup.sh`** from `templates/env-setup.sh.template` — replace every `@@PLACEHOLDER@@` using the recipes. Keep the template's comments; add a `SAFETY:` comment naming the consequence for every sink rewrite, as approved in Step 3.
3. **`.bb-env-setup.sh`** (required — Anti-Pattern 11) — the name BB IDE runs:
   ```bash
   ln -s .env-setup.sh .bb-env-setup.sh
   ```
   The target must be the **relative** name `.env-setup.sh`: git stores the link text as-is, so an absolute target breaks in every worktree and on every other machine. If a real file already sits there in audit mode, propose merging it into `.env-setup.sh` and replacing it with the symlink — don't do it unasked.
4. **`.bb-env-teardown.sh`** from `templates/env-teardown.sh.template` — only if Step 3 said so.
5. `chmod +x .env-setup.sh .bb-env-teardown.sh` (the latter if written).

In audit mode, apply only the approved edits to the existing files with targeted edits, preserving everything else.

If `.gitignore` would ignore any of the new files, say so (they must be committed) — do not edit `.gitignore` without asking.

### Step 5: Validate statically

```bash
bash -n .env-setup.sh && echo "syntax ok"
[ -e .bb-env-teardown.sh ] && bash -n .bb-env-teardown.sh && echo "teardown syntax ok"
grep -n '@@' .worktreeinclude .env-setup.sh .bb-env-teardown.sh 2>/dev/null && echo "LEFTOVER PLACEHOLDERS" || echo "no placeholders"
command -v shellcheck >/dev/null && shellcheck -S warning .env-setup.sh
[ -L .bb-env-setup.sh ] && [ "$(readlink .bb-env-setup.sh)" = ".env-setup.sh" ] && [ -f .bb-env-setup.sh ] \
  && echo "symlink ok" || echo "SYMLINK BROKEN: .bb-env-setup.sh must be a relative link to .env-setup.sh"
[ "$(git config --get core.symlinks)" = "false" ] && echo "WARN: core.symlinks=false — git will check the link out as a text file and BB's setup will fail"
grep -qF '# --- rewritten by .env-setup.sh for this worktree ---' .env-setup.sh && echo "marker ok"
# Guard test on a TRUNCATED copy (guard only), so a broken guard can't touch main's files:
g="$(mktemp)"; sed '/^# -* 2\. dirs/q' .env-setup.sh > "$g"
if grep -q '2\. dirs' "$g" && ! grep -q 'set_env\|rewrite_env' "$g"; then
  bash "$g"; echo "exit=$? (expected 1: refusing to run in the main checkout)"
else
  echo "guard-test truncation failed (no '# --- 2. dirs' header) — NOT run; test the guard by reading it"
fi; rm -f "$g"
```

Never run the full script in the main checkout to test the guard: if the guard is wrong, the script rewrites main's real `.env` and replaces main's data.

**Dry-run the copy list** — exactly what BB and `worktree-create` would copy:
```bash
git ls-files -o -i --exclude-from=.worktreeinclude
```
Show it (names only). Flag anything unexpected — a stray `.env.bak`, a large directory — and fix the patterns before moving on.

Any failure here: fix and re-run Step 5. Do not proceed with leftover placeholders or a syntax error.

### Step 6: Offer a live trial (user approval required)

Static checks can't prove the rewrite works against the real `.env`. Offer — don't run unasked, since `@@DEPS@@` may take minutes and `@@DATA@@` may copy data — a throwaway trial that mirrors the BB contract:

```bash
MAIN="$(git rev-parse --show-toplevel)"
TRIAL="$(mktemp -d)/provision-trial"
BR="provision-trial-$(date +%s)"
git worktree add -b "$BR" "$TRIAL" HEAD
# Copy step, as BB does it (files only, skip source symlinks, never replace):
git -C "$MAIN" ls-files -z -o -i --exclude-from=.worktreeinclude | while IFS= read -r -d '' f; do
  [ -L "$MAIN/$f" ] && continue; [ -e "$TRIAL/$f" ] && continue
  mkdir -p "$(dirname "$TRIAL/$f")" && cp -p "$MAIN/$f" "$TRIAL/$f"
done
# Run MAIN's script (the new one is not committed yet) through the symlink, as BB does:
( cd "$TRIAL" && env -u NODE_ENV bash "$MAIN/.bb-env-setup.sh" < /dev/null ); echo "exit=$?"
```

Set the tool timeout to 900000 ms (the 15-minute cap). Then check the rewritten keys **without printing other values**:
```bash
for k in <VERIFY_KEYS>; do grep -m1 -E "^(export )?$k=" "$TRIAL/.env" | sed "s|$TRIAL|<WT>|"; done
```
Every line must show `<WT>/…`. Then run teardown if one exists (`( cd "$TRIAL" && env bash "$MAIN/.bb-env-teardown.sh" < /dev/null )`), and clean up:
```bash
git worktree remove --force "$TRIAL" && git branch -D "$BR"
```
(`-D` is safe only because the trial branch was created seconds ago and holds no commits.)

A non-zero exit or an un-rewritten key is a failed trial: report the output, fix the script, re-run Steps 5–6.

### Step 7: Report

See **Output Format**. Do not commit — tell the user the files must be committed for BB to see them, and suggest a message.

## Output Format

```
Worktree provisioning ready (create mode)

  .worktreeinclude      copies: .env, .env.local, .claude/settings.local.json
                        not copied: node_modules/ (npm ci), data/app.db (VACUUM INTO snapshot)
  .env-setup.sh         deps: npm ci · data: SQLite snapshot · post: npm run migrate
                        rewrites .env: APP_DB_PATH, APP_LOG_DIR, APP_OUTPUT_DIR (verified)
                        blanks: APP_POST_DEPLOY_HOOK · leaves alone: API keys, APP_GLOBAL_LOCK
  .bb-env-setup.sh      → .env-setup.sh
  .bb-env-teardown.sh   not needed (setup creates nothing outside the worktree)

  Checks: syntax ✓  placeholders ✓  main-checkout guard ✓  copy dry-run ✓
  Trial:  worktree provisioned in 1m12s, all 3 keys point inside it ✓ (trial removed)

Not committed. BB only runs hooks that are committed:
  git add .worktreeinclude .env-setup.sh .bb-env-setup.sh
  git commit -m "chore: add worktree provisioning contract"
```

- After the user commits, `git ls-files -s .bb-env-setup.sh` should show mode `120000` (a symlink). Mode `100644` means it was committed as a plain file and BB will run the text `.env-setup.sh` as a command — say so if you see it.

- Show `Trial: skipped (not requested)` when Step 6 wasn't run — never omit the line, so an untested script is visible as untested.
- In audit mode, replace the file lines with the edits applied per file, and list proposed edits the user declined.

## Examples

### GOOD — new Node + SQLite project

`git ls-files -o -i` shows `.env`, `node_modules/`, `data/app.db`. The classifier marks `DB_PATH` as relative path, `EXPORT_DIR` as ABS PATH outside checkout, `STRIPE_KEY` as secret. `git grep EXPORT_DIR` shows it feeds a sync client that uploads to a shared drive. **Plan:** copy `.env`; exclude `node_modules/` (npm ci) and `data/app.db` (snapshot); rewrite `DB_PATH` to `$WT/data/app.db` (relative paths resolve against cwd) and `EXPORT_DIR` to `$WT/exports` with a `SAFETY:` comment naming the shared drive; leave `STRIPE_KEY`. The user approves; render; Step 5 passes; the trial shows both keys under `<WT>/`; report with the commit hint.

### GOOD — existing repo with an older script

`.env-setup.sh` exists and uses `sed -i` to rewrite paths, with no verify loop and no marker line; `.bb-env-setup.sh` is a separate copy rather than a symlink. **Audit mode:** propose (a) adding the marker, so `worktree-handoff` won't reconcile the copied `.env` back into main; (b) a verify loop over the rewritten keys; (c) replacing `sed -i` — BSD and GNU disagree on its syntax, so it breaks on one of the two machines; (d) replacing the duplicate with a symlink. Apply the approved ones as targeted edits.

### BAD — reading the env to classify it

Running `cat .env` "to see which values are paths". Wrong: the values — including live credentials — are now in the transcript. **Right:** the Step 2 classifier prints key names and value shapes only.

### BAD — copying the virtualenv

Adding `.venv/` to `.worktreeinclude` because "the install is slow". Wrong: BB copies it file by file, and its scripts' shebangs point at main's interpreter path, so the worktree runs main's packages. **Right:** `uv sync` in `@@DEPS@@`, and the reason written into the `EXCLUDED` section.

### BAD — `die` on a missing optional tool

`command -v sqlite3 || die` when the snapshot is a convenience. Wrong: BB deletes every new worktree on a machine without `sqlite3`. **Right:** `warn` and start with an empty database.

## Scope Boundary

This skill **authors and validates** a repo's worktree provisioning files: `.worktreeinclude`, `.env-setup.sh`, the `.bb-env-setup.sh` symlink, and, when justified, `.bb-env-teardown.sh`. It inspects the repo without printing env values, proposes a plan the user approves, renders its templates, and checks the result statically and — on approval — in a throwaway worktree it removes afterwards. It does not commit, does not edit `.gitignore` or any env file, does not create worktrees for real work (`worktree-create`), and does not merge or remove them (`worktree-handoff`). In a repo that already has the files it proposes edits rather than replacing them.
