# Fill Recipes — what goes in each `@@PLACEHOLDER@@`

Snippets for rendering `templates/env-setup.sh.template` and `templates/env-teardown.sh.template`. Pick the ones the discovery step (SKILL.md Step 2) justified; delete the rest. A placeholder with nothing to put in it becomes a single comment saying so (e.g. `# (no runtime dirs needed)`), never an empty gap — the next reader should see the step was considered.

Rules for every snippet:

- **Bash 3.2 compatible** (macOS `/bin/bash`): no associative arrays, no `${var,,}`, no `mapfile`.
- **Quote every path.** Worktree roots can contain spaces.
- **`die` only for unusable or unsafe outcomes.** Missing optional tools `warn`. BB removes the worktree on any non-zero exit.
- **Use `$WT` and `$MAIN`**, never a hardcoded absolute path — the script runs in every worktree and on every machine.
- **No secrets in the script.** It is committed. Values come from the copied env files.

---

## `@@PROJECT@@`

Basename of the repo toplevel. Cosmetic — used in the header comment only.

## `@@OPT_IN_DOC@@`

Document any `<PROJECT>_WT_*` opt-in variables the script reads, or delete the placeholder line. Example:

```bash
#
# Opt-in via the environment:
#   MYAPP_WT_SKIP_DB=1    skip the database snapshot and migrations
```

## `@@RUNTIME_DIRS@@`

Git-ignored directories the app expects (logs, locks, uploads, output, a sandbox for anything that in main points at a real external location). Source them from `.gitignore` entries that are directories *and* are referenced by code or env values.

```bash
mkdir -p "$WT/logs" "$WT/tmp" "$WT/data/output" \
  || die "could not create runtime directories"
```

## `@@DEPS@@`

One block per detected ecosystem. Detect by lockfile, not by guess. Missing tool → `die` if nothing works without it, else `warn`.

**Python / uv** (`uv.lock`):
```bash
command -v uv >/dev/null 2>&1 || die "uv not found on PATH"
say "uv sync"
uv sync || die "uv sync failed — the worktree has no usable virtualenv"
```

**Python / Poetry** (`poetry.lock`):
```bash
command -v poetry >/dev/null 2>&1 || die "poetry not found on PATH"
POETRY_VIRTUALENVS_IN_PROJECT=true poetry install || die "poetry install failed"
```

**Python / pip** (`requirements.txt` only):
```bash
python3 -m venv "$WT/.venv" || die "could not create .venv"
"$WT/.venv/bin/pip" install -r "$WT/requirements.txt" || die "pip install failed"
```

**Node** — pick by lockfile. `NODE_ENV` is stripped by BB, so devDependencies install as normal.
```bash
# pnpm-lock.yaml
command -v pnpm >/dev/null 2>&1 || die "pnpm not found on PATH"
pnpm install --frozen-lockfile || die "pnpm install failed"
# package-lock.json
npm ci || die "npm ci failed"
# yarn.lock
yarn install --frozen-lockfile || die "yarn install failed"
# bun.lock / bun.lockb
bun install --frozen-lockfile || die "bun install failed"
```

**Rust** (`Cargo.lock`): usually nothing — `target/` builds on demand. Optionally `cargo fetch || warn "cargo fetch failed"`.

**Go** (`go.sum`): `go mod download || warn "go mod download failed"`.

**Ruby** (`Gemfile.lock`): `bundle install || die "bundle install failed"`.

**Nothing to install:** `# (no dependency install — <reason>)`.

## `@@DATA@@`

Local data the worktree needs that `.worktreeinclude` must NOT copy.

**SQLite, possibly in WAL mode** — `cp` can produce a torn copy; `VACUUM INTO` takes a consistent snapshot:
```bash
SRC_DB="$MAIN/data/app.db"
DST_DB="$WT/data/app.db"
if [ ! -f "$SRC_DB" ]; then
  warn "no database at $SRC_DB — starting from an empty one"
elif command -v sqlite3 >/dev/null 2>&1; then
  mkdir -p "$(dirname "$DST_DB")"; rm -f "$DST_DB"
  # SQL-quote the path: a ' in the worktree path would break the statement.
  sqlite3 "$SRC_DB" "VACUUM INTO '$(printf '%s' "$DST_DB" | sed "s/'/''/g")'" \
    || warn "database snapshot failed — the worktree starts with an empty DB"
else
  warn "sqlite3 not on PATH — cannot take a consistent snapshot; skipping"
fi
```

**Server database (Postgres/MySQL)** — a per-worktree database lives *outside* the worktree, so it also needs a teardown hook. Derive a stable name from the worktree path:
```bash
WT_ID="$(printf '%s' "$WT" | shasum | cut -c1-8)"
DB_NAME="myapp_wt_${WT_ID}"
createdb "$DB_NAME" 2>/dev/null || warn "createdb $DB_NAME failed (exists already?)"
```
Then rewrite `DATABASE_URL` to that name in `@@ENV_REWRITES@@` — and **do not** add it to `@@VERIFY_KEYS@@` (it is not a path); verify it with its own check instead:
```bash
  case "$(get_env "$f" DATABASE_URL)" in
    *"/$DB_NAME"*) ;;
    *) die "DATABASE_URL does not point at $DB_NAME — the rewrite did not take effect" ;;
  esac
```

**Large optional data** — gate behind an opt-in variable and document it in `@@OPT_IN_DOC@@`:
```bash
if [ "${MYAPP_WT_COPY_CACHE:-0}" = "1" ] && [ -d "$MAIN/data/cache" ]; then
  cp -a "$MAIN/data/cache/." "$WT/data/cache/" || warn "cache copy failed"
fi
```

**Nothing:** `# (no local data to snapshot)`.

## `@@ENV_REWRITES@@`

Inside `rewrite_env`, `$f` is the env file being rewritten. One `set_env` per key the user approved in Step 3. Every call ends `|| die` — a failed rewrite is unsafe.

```bash
  # Absolute, not relative: a relative path resolves against the process cwd,
  # so a command run from a subdirectory silently opens a different file.
  set_env "$f" APP_DB_PATH "$WT/data/app.db" || die "rewrite failed: APP_DB_PATH"
  set_env "$f" APP_LOG_DIR "$WT/logs"        || die "rewrite failed: APP_LOG_DIR"

  # SAFETY: main's value is <the real external location>. Writing there <consequence>.
  set_env "$f" APP_OUTPUT_DIR "$WT/data/output" || die "rewrite failed: APP_OUTPUT_DIR"

  # SAFETY: a hook in main runs <real deploy/publish>. Blank it in worktrees.
  set_env "$f" APP_POST_DEPLOY_HOOK "" || die "rewrite failed: APP_POST_DEPLOY_HOOK"

  # Deliberately NOT rewritten: APP_GLOBAL_LOCK — shared across checkouts on purpose.
```

Every `SAFETY:` comment names the concrete consequence the user confirmed in Step 3. Every key deliberately left alone that *looks* like it should be rewritten gets a `Deliberately NOT rewritten:` line with the reason.

**Ports** (two worktrees running dev servers at once). Derive a stable offset from the path; not a path, so check it separately rather than via `@@VERIFY_KEYS@@`:
```bash
  PORT_OFFSET=$(( $(printf '%s' "$WT" | cksum | cut -d' ' -f1) % 1000 + 1 ))
  set_env "$f" PORT "$(( 3000 + PORT_OFFSET ))" || die "rewrite failed: PORT"
```

**No keys to rewrite:** replace with `  # (no path-bearing keys in this file)` and set `@@VERIFY_KEYS@@` to nothing — `for k in ; do` is a valid empty loop.

## `@@VERIFY_KEYS@@`

Space-separated names of every key rewritten to a path under `$WT` (not blanked keys, not ports, not URLs). Example: `APP_DB_PATH APP_LOG_DIR APP_OUTPUT_DIR`.

## The env-file loop (no placeholder)

Step 5 rewrites every untracked match of `"$WT"/.env "$WT"/.env.*`, so every copied env file gets every override. Change the loop head only if `.worktreeinclude` copies env files under other names (e.g. add `"$WT"/config/local.env`) — keep the glob part outside the quotes so it expands. A file that needs *different* keys gets its own function and a `case "$(basename "$f")"` inside the loop.

## `@@REQUIRED_ENV_FILES@@`

Space-separated env files that must arrive whenever main has them — usually just `.env`. Leave empty only if the app genuinely runs without one.

**No env files at all:** delete the whole step-5 section down to the header comment, and replace it with `# (no env files — nothing to rewrite)`.

## `@@POST@@`

Steps that need deps *and* the rewritten env: migrations, codegen, a build the tests need. Usually non-fatal.

```bash
say "running migrations"
uv run myapp migrate || warn "migrations failed — run them by hand before using the database"
```

**Nothing:** `# (no post-install steps)`.

## `@@TEARDOWN@@` (teardown template only)

Undo exactly what setup created outside `$WT`, deriving names the same way:
```bash
WT_ID="$(printf '%s' "$WT" | shasum | cut -c1-8)"
dropdb --if-exists "myapp_wt_${WT_ID}" || warn "dropdb myapp_wt_${WT_ID} failed"
```
