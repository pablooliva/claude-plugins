# Enforcement Sites — Definitions, Mutation Standard, Inventory Shape

Canonical reference for sdd-flow's enforcement-site standard. Read by the implementer (`bodies/slice-start.md`, `bodies/implementation.md`), the blind counter (`bodies/site-count.md`), the reviewers (`bodies/slice-review.md`, `bodies/code-review.md`), the retro (`bodies/slice-retro.md`), and completion (`bodies/implementation-complete.md`). Every one of them receives this file's resolved absolute path in its spawn prompt. When a rule here and a body disagree, this file wins.

**Why this exists.** A control whose tests cannot fail is not a control. The site list used to be the implementer's alone, and an implementer's list comes from memory of what it just built — it shares the implementer's blind spots. In the project that motivated this standard, implementers under-counted on every control over four slices, and twice a control was recorded closed while still broken; every miss was found by someone reading the code fresh. So the standard has two halves: a per-site mutation proof, and a site count produced **independently** of the implementer.

---

## 1. Definitions

**Control.** Any rule the SPEC says must hold on **every path** through some part of the system. Includes: guards, refusals, write controls (what may be written, where, when), output contracts (what goes to stdout/stderr, exit codes, response shapes), invariants, and security controls. **Not limited to `SEC-xxx` IDs** — a non-security output contract ("stdout line 1 is always `exit_reason: <value>`") is a control, and historically the worst under-counts were in exactly that kind. A requirement that describes a single happy-path behaviour ("export writes a CSV") is not a control; a requirement that constrains all paths ("no path writes outside the export dir") is.

**Not a control: the application's tracing rules.** In an application that has the tracing foundation, "every entry point has a span" and "no span records a header" hold on every path — and are still not controls here. A control is a rule **the SPEC** states; those are stated once for the whole application by the plugin's tracing standard (`skills/observability-init/references/tracing.md`), and most of them are made true by one setting in the application's tracing bootstrap module, so there is no per-path code to count or to break. No inventory row, per-site mutation, or blind count is owed for them, by the implementer or by the blind counter: the application's own entry-point test and the review's Tracing Lens check them. **A SPEC that needs one of them as a real control restates it with an ID** — a feature that handles credentials should carry "no path records the `Authorization` header on a span" as a `SEC-` requirement — and then this standard applies to that rule in full.

A control is keyed by the **SPEC ID that states the rule** (`REQ-018`, `SEC-003`, `D-10`, `EDGE-004`, …). A rule with no SPEC ID is keyed `UNID-<slug>`, where `<slug>` is the kebab-cased text of the nearest SPEC heading above the rule, then `-` and the rule's 1-based position among un-ID'd rules under that heading (e.g. `UNID-output-format-2`). It is itself a LOW finding (the retro recommends a SPEC amendment giving it an ID). Two sides can still slug the same rule differently; the reviewer may pair a `MISSED` UNID with an `EXTRA` UNID naming the same rule and resolve both.

**Enforcement site.** One place in the code that makes a control true on one path. A control has one site per path it must hold on: "stdout line 1 is always `exit_reason: …`" has a site in each refusal branch, each prompt, each error handler, the Ctrl-C catch. Shared machinery (a helper every site calls) is **not** a site by itself — it is what sites call. The site is where the path commits to the rule.

**Gap.** A path on which the control must hold but where no site exists. A gap is a defect (the control is broken on that path), not a count entry.

## 2. The per-site mutation standard

Every control ships with a test that drives the **real entry point** with the adverse precondition **genuinely present** (not mocked away), plus a **per-site mutation check**:

1. Delete (or neutralise) exactly one enforcement site.
2. Run the tests. At least one test MUST fail.
3. Restore the site. Confirm the file is exactly what it was before the deletion (keep a copy, or compare `git diff -- <file>` taken before and after — the work is uncommitted, so that diff is not empty to begin with).

N sites need N mutations. **Mutating shared machinery proves nothing about any single site** — a mutation of a helper every site calls shows the helper is tested, not that each call site is. Mutations are manual, per site, and recorded; no automated mutation-testing tool is used.

**Output / stream contracts** (anything that constrains what reaches stdout, stderr, or the exit code): each **path class** needs at least one test that runs the program as a **real subprocess** and asserts on the actual bytes. In-process runners (`click.testing.CliRunner`, `capsys`, captured `sys.stdout`) do not count toward this — they have been observed to hide real defects (e.g. `click.confirm(err=True)` still writing a space to stdout).

## 3. Site dispositions

Every site in the implementer's inventory carries exactly one disposition. The three exist so an honest negative is neither deleted later as dead code nor faked into a proof.

| # | Disposition | Required evidence |
|---|---|---|
| (i) | **Proven by its own mutation** | `mutation: <what was deleted> → failing test <test id>` |
| (ii) | **Not provable alone** — the site is real, but deleting it alone is unobservable (e.g. a later site on the same path also enforces the rule) | `argument at <file:line>` — a comment AT the site naming which other site/test covers this path and why deleting this one alone cannot be observed |
| (iii) | **Not proven, kept** — no test can currently fail for it, and it is kept deliberately | `owner: <name>; follow-up: <what would prove it>` |

A bare assertion ("not provable", "kept") without the evidence is a finding. A (ii) or (iii) site must never be removed as dead code without a SPEC-level decision.

**Site comments must not carry counts, indices, or a greppable site tag** (no `# site 3/17 for D-10`, no `# ENFORCEMENT-SITE`). The blind counter reads the code; a tag would hand it the implementer's list. Only (ii) arguments and (iii) owner notes are written at sites, and they describe the path, not the inventory.

## 4. Inventory shape (binding — both sides, machine-diffed)

Both the implementer's inventory and the blind count use this table under the exact header `## Site Inventory`:

```markdown
## Site Inventory

| Control | File | Symbol | Kind | Path class | Site description | Disposition | Evidence | Slice |
|---|---|---|---|---|---|---|---|---|
| D-10 | src/cli/main.py | run | site | refusal | refuses on missing config; writes exit_reason first | (i) | mutation: removed emit_exit_reason call → failing test tests/cli/test_exit.py::test_missing_config_line1 | SLICE-002 |
| D-10 | src/cli/main.py | run | gap | interrupt | Ctrl-C during prompt exits without exit_reason | — | — | SLICE-002 |
```

Column rules:

- **Control** — the SPEC ID (or `UNID-<slug>`), exactly as written in the SPEC.
- **File** — repo-relative path, no leading `./`.
- **Symbol** — the **innermost named** function/method (`Class.method` for methods); `<module>` for top-level code. Lambdas and comprehensions take their enclosing named symbol. No line numbers — they drift. Write File and Symbol plain: `<module>`, not `\<module\>`, and no wrapping backticks. (The diff normalises Markdown backslash-escapes and wrapping backticks in Control, File, and Symbol, so an escaped cell still keys correctly — but write it plain.)
- **Kind** — `site` or `gap`. Gaps are findings (HIGH) and are excluded from the count.
- **Path class** — the kind of path: `refusal`, `prompt`, `error-handler`, `interrupt`, `success`, `validation`, or a short project-specific label. Required for output/stream contracts; `—` allowed otherwise.
- **Disposition / Evidence** — implementer only: `(i)`, `(ii)`, `(iii)` with evidence per §3. The blind count writes `—` in both.
- **Slice** — `SLICE-XXX` that introduced or last changed the site (per-slice mode; three digits, optionally one lowercase letter, e.g. `SLICE-005a`) — fix subagents set it to the slice being fixed; `—` in whole-feature mode. The diff does **not** use this column to decide whether a site is carried from an earlier slice (see §6); it only decides which controls the implementer claims for the scope.

**The implementer inventory is kept current, not append-only.** Whoever changes code (implementer or fixer) deletes the row of any site that no longer exists in the working tree, and records the removal in its progress entry's key-decision line. A stale row shows up in every later diff — as a phantom `EXTRA` when it is the only row at its key.

Cells must not contain a literal `|` (write `\|` if one is unavoidable). One row per site: a row is a unit of evidence, with its own disposition and mutation. The diff compares which `Control + File + Symbol` keys each side lists, not how many rows a key has (§6), so the two sides do not have to split a compound condition into the same number of rows.

The table has exactly these nine columns. There is no owner/carried column: a note like "carried — owner SLICE-001a" in a description cell is harmless but ignored. Whether a site is carried is decided mechanically (§6).

### 4.1 Declared scope (blind count only, optional)

A blind count at `SLICE-XXX` scope that deliberately counted a control over only part of the code declares so in a table under the exact header `## Declared Scope`:

```markdown
## Declared Scope

| Control | File | Symbol |
|---|---|---|
| REQ-019 | src/search/group.py | _group_payload |
```

One row per place the control **was** counted; `*` in Symbol means the whole file. A control absent from this table was counted in full. Implementer rows for a declared control that fall outside it are set aside rather than reported `EXTRA` (§6). At `FEATURE` scope a declaration is itself a finding — a feature count must be complete.

### 4.2 Filing conventions (per feature, shared by both sides)

`SDD/implementation/sites/SITE-CONVENTIONS-[feature-name].md` records how this feature's sites are **keyed and filed** — rulings a reviewer made so that the implementer and every later blind count file the same site the same way. Both sides read it; it is the only file under `SDD/implementation/` the blind counter may read.

```markdown
# Site Filing Conventions — [feature-name]

| # | Convention | Added |
|---|---|---|
| 1 | A registry declaration read by a statement is data; file the site at the reading statement, not the declaration. | SLICE-003 iter 1 |
| 2 | EDGE-009 is enforced as part of REQ-005: key its sites `REQ-005`. | SLICE-003 iter 1 |
```

**What a convention settles.** Which **control** and which **symbol** a site is keyed to — the two things the diff compares. It does not need to settle how many rows a statement or a compound condition is: the diff does not compare row counts (§6), so a ruling written only to make two row totals agree is not worth adding.

**Count-free by rule.** A convention states a filing or keying rule. It never contains: a number of sites, a site row, a file or symbol at which a particular site sits, a list of controls to count or to skip, or anything about scope. A convention that would only make sense to someone who had seen the inventory is a leak (MEDIUM in the reviewers' leak check) — rewrite it as a general rule or drop it. Rows are append-only; a reversed ruling is a new row that names the row it supersedes.

## 5. Artifacts

| Artifact | Path | Written by |
|---|---|---|
| Implementer inventory (living, one per feature) | `SDD/implementation/sites/SITES-IMPL-[feature-name].md` | implementer; fix subagents update it |
| Blind count (immutable) | `SDD/reviews/SITE-COUNT-<SCOPE>-[feature-name]-iter<N>-[YYYY-MM-DD].md` | blind counter (`bodies/site-count.md`) |
| Site diff (immutable) | `SDD/reviews/SITE-DIFF-<SCOPE>-[feature-name]-iter<N>-[YYYY-MM-DD].md` | orchestrator, via `scripts/site-diff.py` |
| Filing conventions (living, append-only, one per feature) | `SDD/implementation/sites/SITE-CONVENTIONS-[feature-name].md` | reviewers (`bodies/slice-review.md`, `bodies/code-review.md`) |

`<SCOPE>` is `SLICE-XXX` for a per-slice count or `FEATURE` for a whole-feature / final count. `iter<N>` is `iter0` for the first count of a scope and `iter<k>` for the recount after fix iteration k.

## 6. Diff outcomes and Complete

`scripts/site-diff.py` groups `Kind = site` rows per `Control + File + Symbol` on each side and compares **which keys each side has — not how many rows a key has**. Two careful readers split a compound condition into different numbers of rows; that is a difference of filing, not a place either of them forgot. Per control the script reports:

**Carried sites (`SLICE-XXX` scope, `--base` given).** The orchestrator passes the slice's base commit. A key whose code the slice did not change is *carried*: its file existed at `BASE`, still exists, and either differs in no line from `BASE`, or (Python) the named symbol's lines are untouched. The script decides this from git, identically for both sides — never from either side's labels. Anything it cannot place with certainty (a file new since `BASE` — untracked, git-ignored, or renamed — or a missing file, `<module>` in a changed file, a non-Python changed file, a symbol it cannot find) counts as changed, so uncertainty never hides a finding. A disagreement at a carried key — a key only one side has, or a different number of rows — is reported **LOW** in a separate `## Carried` section, never as `MISSED`/`CROSS-FILED`/`EXTRA`, and is owed to the `FEATURE` recount (4e.5), which always runs and compares every key. Carried keys with the same number of rows are ordinary matches.

| Outcome | Meaning | Severity |
|---|---|---|
| `MATCH` | Every key one side lists, the other lists too | — |
| `MISSED` | A key only the blind count has, at a File + Symbol the implementer lists under no control — or a control the implementer never listed | HIGH |
| `CROSS-FILED` | A key only the blind count has, at a File + Symbol the implementer lists under **another control** | MEDIUM — the reviewer re-runs the mutation of each site the blind count names there, in the same pass: a test fails → `CONFIRMED-CROSS-FILED` (resolved: the place is listed and proven, only the control label differs — the reviewer records the keying in the filing conventions, §4.2); no test fails → HIGH, needing code or a test |
| `EXTRA` | A key only the implementer has | MEDIUM — the reviewer re-runs each extra site's mutation in the same pass: a test fails → `CONFIRMED-EXTRA` (resolved); no test fails → HIGH |
| `UNCOUNTED` | A control in the implementer's inventory for this scope that the blind count did not inventory | control stays `Partial`; MEDIUM — the reviewer adjudicates it: **not a control / out of scope** → the fixer deletes its rows (resolved); **a real control** → its ID goes into the next recount's `ALSO INVENTORY` list (ID only, never sites or counts) |
| `MISSED+EXTRA`, `CROSS-FILED+EXTRA`, `MISSED+CROSS-FILED`, `MISSED+CROSS-FILED+EXTRA` | More than one of `MISSED`, `CROSS-FILED`, `EXTRA` at different keys of one control (often the same site filed under different symbols or controls) | each `MISSED` key is HIGH and each `CROSS-FILED` or `EXTRA` key is MEDIUM, handled as above |
| `CARRIED` | The only differences are at carried keys | LOW, listed under `## Carried`; not a finding for this slice. The control stays `Partial` until the `FEATURE` recount |
| `OUT-OF-SCOPE-BY-DECLARED-SCOPE` | The blind count declared partial scope (§4.1) and the only differences are implementer rows outside it | carried rows: LOW, under `## Carried`. Rows in code this slice changed: MEDIUM — the count skipped code it was responsible for; the reviewer adjudicates as for `UNCOUNTED`. Control stays `Partial` |
| `GAP` | The only issue is a blind-count gap | HIGH (below) |

Blind-count `gap` rows are reported separately as HIGH findings, carried or not — a gap is broken code, not a filing disagreement. At `FEATURE` scope, each control in a `## Declared Scope` table is a MEDIUM `PARTIAL COUNT` finding and the comparison stays complete.

**Row counts (`## Row Counts Differ`).** A key both sides list, with a different number of rows, is reported **LOW** in its own section with both counts (`ROWS-DIFFER`). It is **not a finding**: it does not make the result `MISMATCH`, does not change the control's outcome, does not block `Complete`, and never enters a review's findings, the fix loop, or the stall check. No inventory row is owed for it.

One check remains, because the diff no longer flags a second, forgotten site inside a function that already has one listed. At every such key where **the blind count has more rows**, the reviewer re-runs the mutation of each blind row there that no implementer row describes — every one, not a sample — and records the result per key in the review. A test fails → nothing is owed. No test fails → that site is a HIGH `needs-code-or-test` finding, like any other site no test proves. A key where the implementer has more rows needs nothing beyond the reviewer's ordinary mutation sample.

**The `Result:` line.** `MATCH` or `MISMATCH (h HIGH, m MEDIUM)`. A `MATCH` may carry a bracketed LOW note — `n LOW carried or out-of-scope, owed to the FEATURE recount`, `n LOW row counts differ` (with `, k with more blind rows` when the check above is owed at `k` keys), or both joined by `; `. A `MISMATCH` may carry `+ n LOW`, the total of both kinds.

**A control is `Complete` only when** the per-control outcome in its latest site diff is `MATCH` (or its only differences are `CONFIRMED-EXTRA` or `CONFIRMED-CROSS-FILED` recorded in the review), every key of it where the blind count has more rows has its check recorded in a review of that diff with no site left unproven, the blind count has no open gap for it, and the reviewer has accepted every (ii) argument and (iii) owner note. Otherwise it is `Partial`. **A control with no independent count is `Partial` — never `Complete`.** A (iii) site does not by itself block `Complete`; it is carried to the ledger's *Open recommendations awaiting user decision* with its owner.

Control status lives in the IMPLEMENTATION-PLAN's `## Control Site Status` table:

```markdown
## Control Site Status

| Control | Implementer sites | Independent sites | Latest diff | Status | Open (iii) owners |
|---|---|---|---|---|---|
| D-10 | 26 | 26 | SDD/reviews/SITE-DIFF-SLICE-003-…-iter2-….md | Complete | — |
```

The two site columns are row totals copied from the diff. They are a record, not the test: a control can be `Complete` with different totals, and is not `Complete` merely because they are equal.
