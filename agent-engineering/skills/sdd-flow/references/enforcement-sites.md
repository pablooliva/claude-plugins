# Enforcement Sites — Definitions, Mutation Standard, Inventory Shape

Canonical reference for sdd-flow's enforcement-site standard. Read by the implementer (`bodies/slice-start.md`, `bodies/implementation.md`), the blind counter (`bodies/site-count.md`), the reviewers (`bodies/slice-review.md`, `bodies/code-review.md`), the retro (`bodies/slice-retro.md`), and completion (`bodies/implementation-complete.md`). Every one of them receives this file's resolved absolute path in its spawn prompt. When a rule here and a body disagree, this file wins.

**Why this exists.** A control whose tests cannot fail is not a control. The site list used to be the implementer's alone, and an implementer's list comes from memory of what it just built — it shares the implementer's blind spots. In the project that motivated this standard, implementers under-counted on every control over four slices, and twice a control was recorded closed while still broken; every miss was found by someone reading the code fresh. So the standard has two halves: a per-site mutation proof, and a site count produced **independently** of the implementer.

---

## 1. Definitions

**Control.** Any rule the SPEC says must hold on **every path** through some part of the system. Includes: guards, refusals, write controls (what may be written, where, when), output contracts (what goes to stdout/stderr, exit codes, response shapes), invariants, and security controls. **Not limited to `SEC-xxx` IDs** — a non-security output contract ("stdout line 1 is always `exit_reason: <value>`") is a control, and historically the worst under-counts were in exactly that kind. A requirement that describes a single happy-path behaviour ("export writes a CSV") is not a control; a requirement that constrains all paths ("no path writes outside the export dir") is.

A control is keyed by the **SPEC ID that states the rule** (`REQ-018`, `SEC-003`, `D-10`, `EDGE-004`, …). A rule with no SPEC ID is keyed `UNID-<slug>`, where `<slug>` is the kebab-cased text of the nearest SPEC heading above the rule, then `-` and the rule's 1-based position among un-ID'd rules under that heading (e.g. `UNID-output-format-2`). It is itself a LOW finding (the retro recommends a SPEC amendment giving it an ID). Two sides can still slug the same rule differently; the reviewer may pair a `MISSED` UNID with an `EXTRA` UNID naming the same rule and resolve both.

**Enforcement site.** One place in the code that makes a control true on one path. A control has one site per path it must hold on: "stdout line 1 is always `exit_reason: …`" has a site in each refusal branch, each prompt, each error handler, the Ctrl-C catch. Shared machinery (a helper every site calls) is **not** a site by itself — it is what sites call. The site is where the path commits to the rule.

**Gap.** A path on which the control must hold but where no site exists. A gap is a defect (the control is broken on that path), not a count entry.

## 2. The per-site mutation standard

Every control ships with a test that drives the **real entry point** with the adverse precondition **genuinely present** (not mocked away), plus a **per-site mutation check**:

1. Delete (or neutralise) exactly one enforcement site.
2. Run the tests. At least one test MUST fail.
3. Restore the site. Confirm `git diff -- <file>` shows no residue.

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
- **Symbol** — the **innermost named** function/method (`Class.method` for methods); `<module>` for top-level code. Lambdas and comprehensions take their enclosing named symbol. No line numbers — they drift.
- **Kind** — `site` or `gap`. Gaps are findings (HIGH) and are excluded from the count.
- **Path class** — the kind of path: `refusal`, `prompt`, `error-handler`, `interrupt`, `success`, `validation`, or a short project-specific label. Required for output/stream contracts; `—` allowed otherwise.
- **Disposition / Evidence** — implementer only: `(i)`, `(ii)`, `(iii)` with evidence per §3. The blind count writes `—` in both.
- **Slice** — `SLICE-XXX` that introduced or last changed the site (per-slice mode) — fix subagents set it to the slice being fixed; `—` in whole-feature mode.

**The implementer inventory is kept current, not append-only.** Whoever changes code (implementer or fixer) deletes the row of any site that no longer exists in the working tree, and records the removal in its progress entry's key-decision line. A stale row shows up as a phantom `EXTRA` in every later diff.

Cells must not contain a literal `|` (write `\|` if one is unavoidable). One row per site; two sites of the same control in the same symbol are two rows.

## 5. Artifacts

| Artifact | Path | Written by |
|---|---|---|
| Implementer inventory (living, one per feature) | `SDD/implementation/sites/SITES-IMPL-[feature-name].md` | implementer; fix subagents update it |
| Blind count (immutable) | `SDD/reviews/SITE-COUNT-<SCOPE>-[feature-name]-iter<N>-[YYYY-MM-DD].md` | blind counter (`bodies/site-count.md`) |
| Site diff (immutable) | `SDD/reviews/SITE-DIFF-<SCOPE>-[feature-name]-iter<N>-[YYYY-MM-DD].md` | orchestrator, via `scripts/site-diff.py` |

`<SCOPE>` is `SLICE-XXX` for a per-slice count or `FEATURE` for a whole-feature / final count. `iter<N>` is `iter0` for the first count of a scope and `iter<k>` for the recount after fix iteration k.

## 6. Diff outcomes and Complete

`scripts/site-diff.py` counts `Kind = site` rows per `Control + File + Symbol` on each side and reports, per control:

| Outcome | Meaning | Severity |
|---|---|---|
| `MATCH` | Every key's counts agree | — |
| `MISSED` | The blind count has more sites at some key than the implementer, or a control the implementer never listed | HIGH |
| `EXTRA` | The implementer lists more sites at some key than the blind count | MEDIUM — the reviewer re-runs each extra site's mutation in the same pass: a test fails → `CONFIRMED-EXTRA` (resolved); no test fails → HIGH |
| `UNCOUNTED` | A control in the implementer's inventory for this scope that the blind count did not inventory | control stays `Partial`; MEDIUM — the reviewer adjudicates it: **not a control / out of scope** → the fixer deletes its rows (resolved); **a real control** → its ID goes into the next recount's `ALSO INVENTORY` list (ID only, never sites or counts) |
| `MISSED+EXTRA` | Both of the above at different keys of one control (often the same site filed under different symbols) | the `MISSED` keys are HIGH and each `EXTRA` key is MEDIUM, handled as above |

Blind-count `gap` rows are reported separately as HIGH findings.

**A control is `Complete` only when** its latest site diff is `MATCH` (or its only differences are `CONFIRMED-EXTRA` recorded in the review), the blind count has no open gap for it, and the reviewer has accepted every (ii) argument and (iii) owner note. Otherwise it is `Partial`. **A control with no independent count is `Partial` — never `Complete`.** A (iii) site does not by itself block `Complete`; it is carried to the ledger's *Open recommendations awaiting user decision* with its owner.

Control status lives in the IMPLEMENTATION-PLAN's `## Control Site Status` table:

```markdown
## Control Site Status

| Control | Implementer sites | Independent sites | Latest diff | Status | Open (iii) owners |
|---|---|---|---|---|---|
| D-10 | 26 | 26 | SDD/reviews/SITE-DIFF-SLICE-003-…-iter2-….md | Complete | — |
```
