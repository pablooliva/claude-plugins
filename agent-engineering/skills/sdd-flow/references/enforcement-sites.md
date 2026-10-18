# Enforcement Sites — Definitions, Mutation Standard, Inventory Shape

Canonical reference for sdd-flow's enforcement-site standard. Read by the planner, which writes the control register (`bodies/planning.md`, checked by `bodies/planning-complete.md` and the spec critical review), the implementer (`bodies/slice-start.md`, `bodies/implementation.md`), the blind counter (`bodies/site-count.md`), the reviewers (`bodies/slice-review.md`, `bodies/code-review.md`), the retro (`bodies/slice-retro.md`), and completion (`bodies/implementation-complete.md`). Every one of them receives this file's resolved absolute path in its spawn prompt. When a rule here and a body disagree, this file wins.

**Why this exists.** A control whose tests cannot fail is not a control. The site list used to be the implementer's alone, and an implementer's list comes from memory of what it just built — it shares the implementer's blind spots. In the project that motivated this standard, implementers under-counted on every control over four slices, and twice a control was recorded closed while still broken; every miss was found by someone reading the code fresh. So the standard has two halves: a per-site mutation proof, and a site count produced **independently** of the implementer.

---

## 1. Definitions

**Control.** Any rule the SPEC says must hold on **every path** through some part of the system. Includes: guards, refusals, write controls (what may be written, where, when), output contracts (what goes to stdout/stderr, exit codes, response shapes), invariants, and security controls. **Not limited to `SEC-xxx` IDs** — a non-security output contract ("stdout line 1 is always `exit_reason: <value>`") is a control, and historically the worst under-counts were in exactly that kind. A requirement that describes a single happy-path behaviour ("export writes a CSV") is not a control; a requirement that constrains all paths ("no path writes outside the export dir") is.

**Not a control: the application's tracing rules.** In an application that has the tracing foundation, "every entry point has a span" and "no span records a header" hold on every path — and are still not controls here. A control is a rule **the SPEC** states; those are stated once for the whole application by the plugin's tracing standard (`skills/observability-init/references/tracing.md`), and most of them are made true by one setting in the application's tracing bootstrap module, so there is no per-path code to count or to break. No inventory row, per-site mutation, or blind count is owed for them, by the implementer or by the blind counter: the application's own entry-point test and the review's Tracing Lens check them. **A SPEC that needs one of them as a real control restates it with an ID** — a feature that handles credentials should carry "no path records the `Authorization` header on a span" as a `SEC-` requirement — and then this standard applies to that rule in full, in the application's own code (next paragraph).

**Not sites: the plugin's own files in the application.** Some files in an application are this plugin's, rendered from its templates and tested where the templates are made: the eval run, `evals/run.py`, which stays equal to its template apart from three placeholders (`references/evals.md` §3), and the files `/observability-init` rendered — the bootstrap module, the trace run, the trace lookup, and the entry-point test that `SDD/OBSERVABILITY.md` names. **No line of a plugin file is an enforcement site**, even where a control's path runs through it: no inventory row, no blind-count row, no mutation, and no test is owed for it, and a reviewer neither breaks it nor raises a finding about how it is tested. The control's sites are in the application's own code on that path — for an eval, `evals/task.py`, `evals/checks.py`, and the application itself. `scripts/site-diff.py` sets aside every row in `evals/run.py`, on both sides, and says how many; a row of an implementer's inventory in a plugin file is deleted by the next implementer or fixer, and is not a finding. Two things keep this honest. A plugin file changed beyond its placeholders is no longer the plugin's: for `evals/run.py` that is the Eval Check's HIGH finding (`references/evals.md` §7, finding 9), resolved by restoring the template, never by proving the change. And a placeholder an application filled with code of its own — the instrumentation and the header reader in the bootstrap module, the client the entry-point test builds — is the application's code, counted like any other.

A control is keyed by **its ID in the SPEC's control register** (§1.1) — one ID per rule, settled when the spec is written, so neither side picks among the several IDs a spec gives one behaviour. A rule with no SPEC ID is keyed `UNID-<slug>`, where `<slug>` is the kebab-cased text of the nearest SPEC heading above the rule, then `-` and the rule's 1-based position among un-ID'd rules under that heading (e.g. `UNID-output-format-2`). It is itself a LOW finding (the retro recommends a SPEC amendment giving it an ID). Two sides can still slug the same rule differently; the reviewer may pair a `MISSED` UNID with an `EXTRA` UNID naming the same rule and resolve both.

**Enforcement site.** One place in the code that makes a control true on one path. A control has one site per path it must hold on: "stdout line 1 is always `exit_reason: …`" has a site in each refusal branch, each prompt, each error handler, the Ctrl-C catch. Shared machinery (a helper every site calls) is **not** a site by itself — it is what sites call. The site is where the path commits to the rule.

**Gap.** A path on which the control must hold but where no site exists. A gap is a defect (the control is broken on that path), not a count entry.

### 1.1 The control register (which ID a site is keyed by)

A spec gives one behaviour several IDs: a `REQ`, and `EDGE`, `FAIL`, `SEC`, and `UX` entries that spell out one path of it. Left to choose, the implementer and every fresh blind counter file the same site under different ones, and the two lists differ on labels alone. So the choice is made once, in the SPEC, under the exact header `## Control Register`:

```markdown
## Control Register

| ID | Filed under | Reason |
|---|---|---|
| REQ-005 | REQ-005 | one question in flight; the page stays locked until it ends |
| EDGE-005 | REQ-005 | restates its in-flight path: a second submit while one is in flight |
| SEC-005 | SEC-005 | adds a rule of its own: no automatic retry |
```

- **An ID that states a rule of its own is a control**, filed under itself.
- **An ID that only restates one path of another control's rule** is filed under that control. Its sites carry that control's ID, and its text is read as **one more path that control must hold on** — a path to trace, never one to skip. An ID that restates a path *and* adds a clause of its own is a control: it is filed under itself.
- `Filed under` always names an ID that is filed under itself. There are no chains.
- **An ID in no row is not a control** (a single happy-path behaviour, a documentation requirement, a test requirement).

Both sides key by the register; neither picks. `scripts/site-diff.py` applies it as well: a row either side keys by an ID the register files under another control is compared under that control (§6), so a restating ID never makes a difference by itself.

**Why the blind counter may read it.** The register is part of the SPEC, written from the SPEC alone before any code exists, and checked by the planning-complete step and the spec critical review. It names no file, no symbol, and no count. That is what separates it from a filing convention (§4.2), which a reviewer writes after seeing both lists and which therefore may not say which controls to count. A later change to the register is a SPEC amendment like any other, made by whoever amends the SPEC and held to the same rule: it adds or re-files an ID, and names no file, symbol, or count.

**A rule the register leaves out.** The blind counter still reads the whole SPEC. A rule it judges must hold on every path, which the register does not list — or files under a control whose rule does not cover it — it counts under that rule's own ID and names in its count's `Outside the register:` line. The diff compares such a key like any other (§6): at a place the implementer lists it is `CROSS-FILED` and costs one mutation; at a place the implementer lists nowhere it is `MISSED`. It is not a finding by itself. The review lists it, and in per-slice mode the slice retrospective recommends the SPEC amendment that registers it. An **implementer** row keyed by an ID the register does not list is not that: the reviewer adjudicates it as an `UNCOUNTED` control (§6).

**A SPEC with no register** (one planned before 3.11.0). A control is keyed by the SPEC ID that states the rule (`REQ-018`, `SEC-003`, `D-10`, `EDGE-004`, …), as it was before, and a filing convention (§4.2) may settle which of several restating IDs a site is keyed to.

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
| (iii) | **Not proven, kept** — no test can currently fail for it, and it is kept deliberately | `owner: <name>; follow-up: <what would prove it>` — a reviewer that records a site no test proves (§6) writes `owner: review (<SCOPE> iter <N>)` |

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

- **Control** — the ID the register files the site under (§1.1) — in a SPEC with no register, the SPEC ID that states the rule — or `UNID-<slug>`, exactly as written in the SPEC.
- **File** — repo-relative path, no leading `./`.
- **Symbol** — the **innermost named** function/method (`Class.method` for methods); `<module>` for top-level code. Lambdas and comprehensions take their enclosing named symbol. No line numbers — they drift. Write File and Symbol plain: `<module>`, not `\<module\>`, and no wrapping backticks. (The diff normalises Markdown backslash-escapes and wrapping backticks in Control, File, and Symbol, so an escaped cell still keys correctly — but write it plain.)
- **Kind** — `site` or `gap`. Gaps are findings (HIGH) and are excluded from the count.
- **Path class** — the kind of path: `refusal`, `prompt`, `error-handler`, `interrupt`, `success`, `validation`, or a short project-specific label. Required for output/stream contracts; `—` allowed otherwise.
- **Disposition / Evidence** — the implementer's and the fixers': `(i)`, `(ii)`, `(iii)` with evidence per §3. Two exceptions, both a reviewer's: a row it adds after proving the site itself (§6, `CONFIRMED-MISSED`), whose Evidence ends `(reviewer, <SCOPE> iter <N>)`; and a site it found no test proves, of a control that is not a security control (§6), whose row it adds or changes to `(iii)` with Evidence `owner: review (<SCOPE> iter <N>); …`. The blind count writes `—` in both.
- **Slice** — `SLICE-XXX` that introduced or last changed the site (per-slice mode; three digits, optionally one lowercase letter, e.g. `SLICE-005a`) — fix subagents set it to the slice being fixed; `—` in whole-feature mode. The diff does **not** use this column to decide whether a site is carried from an earlier slice (see §6); it only decides which controls the implementer claims for the scope.

**The implementer inventory is kept current, not append-only.** A reviewer appends to it, and changes a row only to record that a site recorded `(i)` is not proven (§6); it deletes no row. Whoever changes code (implementer or fixer) deletes the row of any site that no longer exists in the working tree, and records the removal in its progress entry's key-decision line. A stale row shows up in every later diff — as a phantom `EXTRA` when it is the only row at its key.

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

`SDD/implementation/sites/SITE-CONVENTIONS-[feature-name].md` records how this feature's sites are **filed** — rulings a reviewer made so that the implementer and every later blind count file the same site at the same symbol. Both sides read it; it is the only file under `SDD/implementation/` the blind counter may read.

```markdown
# Site Filing Conventions — [feature-name]

| # | Convention | Added |
|---|---|---|
| 1 | A registry declaration read by a statement is data; file the site at the reading statement, not the declaration. | SLICE-003 iter 1 |
| 2 | A check written as a decorator is filed at the decorated function, not at the decorator's definition. | SLICE-003 iter 1 |
```

**What a convention settles.** Which **symbol** a site is keyed to. Which **control** is the register's (§1.1): a convention never adds a control, and never re-keys a site from one control to another — a register that files an ID wrongly is a SPEC amendment, not a convention. (Only in a SPEC with no register does a convention also settle the control, e.g. `EDGE-009 is enforced as part of REQ-005: key its sites REQ-005`.) A convention does not need to settle how many rows a statement or a compound condition is: the diff does not compare row counts (§6), so a ruling written only to make two row totals agree is not worth adding.

**Count-free by rule.** A convention states a filing or keying rule. It never contains: a number of sites, a site row, a file or symbol at which a particular site sits, a list of controls to count or to skip, or anything about scope. A convention that would only make sense to someone who had seen the inventory is a leak (MEDIUM in the reviewers' leak check) — rewrite it as a general rule or drop it. Rows are append-only; a reversed ruling is a new row that names the row it supersedes.

## 5. Artifacts

| Artifact | Path | Written by |
|---|---|---|
| Implementer inventory (living, one per feature) | `SDD/implementation/sites/SITES-IMPL-[feature-name].md` | implementer; fix subagents update it; reviewers append the row of a missed site they proved, and record a site no test proves (§6) |
| Blind count (immutable) | `SDD/reviews/SITE-COUNT-<SCOPE>-[feature-name]-iter<N>-[YYYY-MM-DD].md` | blind counter (`bodies/site-count.md`) |
| Site diff (immutable) | `SDD/reviews/SITE-DIFF-<SCOPE>-[feature-name]-iter<N>-[YYYY-MM-DD].md` | orchestrator, via `scripts/site-diff.py` |
| Filing conventions (living, append-only, one per feature) | `SDD/implementation/sites/SITE-CONVENTIONS-[feature-name].md` | reviewers (`bodies/slice-review.md`, `bodies/code-review.md`) |

`<SCOPE>` is `SLICE-XXX` for a per-slice count or `FEATURE` for a whole-feature / final count. `iter<N>` is `iter0` for the first count of a scope and `iter<k>` for the recount after fix iteration k.

## 6. Diff outcomes and Complete

`scripts/site-diff.py` groups `Kind = site` rows per `Control + File + Symbol` on each side and compares **which keys each side has — not how many rows a key has**. Two careful readers split a compound condition into different numbers of rows; that is a difference of filing, not a place either of them forgot.

**The register is applied first.** The orchestrator passes the SPEC (`--register`). A row either side keys by an ID the register files under another control is compared under that control, and the diff's header lists every row it moved. An ID the register does not list is compared as written. With no register in the SPEC, every control is compared as written.

**Places before labels.** A key only the blind count has is judged by its **place** — its File + Symbol — before its label. If the implementer lists that place under any control, the place was not forgotten: the two sides disagree only about which rule it serves, and what remains to settle is whether the specific site the blind row describes is proven. That is a mutation, not a filing question, so the key is `CROSS-FILED` (MEDIUM) — **also when the implementer lists that control nowhere**. Only a place the implementer lists under no control at all is `MISSED` (HIGH). The reviewer re-runs the mutation of every site a blind row names at either kind of key, so a second, forgotten check inside a listed function is still caught.

Per control the script reports:

**Carried sites (`--base` given).** The orchestrator passes a base commit: at `SLICE-XXX` scope the slice's base commit, or — on the recount after a fix round — the snapshot of the working tree it took before that fix (`scripts/site-diff.py --snapshot`; `phases/implementation-per-slice.md` → 4c); at `FEATURE` scope only such a snapshot, and never on the first round of the final check, which compares every key. A key whose code did not change since that base is *carried*: its file existed at `BASE`, still exists and is not git-ignored, and either differs in no line from `BASE`, or (Python) the named symbol's lines are untouched. The script decides this from git — the working tree as it is, untracked files included — identically for both sides, never from either side's labels. Anything it cannot place with certainty (a file new since `BASE` or git-ignored, a missing file, `<module>` in a changed file, a non-Python changed file, a symbol it cannot find) counts as changed, so uncertainty never hides a finding. A disagreement at a carried key — a key only one side has, or a different number of rows — is reported **LOW** in a separate `## Carried` section, never as `MISSED`/`CROSS-FILED`/`EXTRA`. At `SLICE-XXX` scope it is owed to the `FEATURE` recount (4e.5), whose first round always runs and compares every key. At `FEATURE` scope only a key where the implementer has the only rows, or more rows, is carried — the first round compared it already. A key where the blind count has more rows, or the only rows, is compared as owned (`MISSED`, `CROSS-FILED`, or a row-count key the reviewer checks): a fresh count may find a site no earlier round's count listed, and no later recount would. The reviewer of every later round checks the findings of the round before it one by one, so a finding a fix did not close stays open whatever the diff says. Carried keys with the same number of rows are ordinary matches.

| Outcome | Meaning | Severity |
|---|---|---|
| `MATCH` | Every key one side lists, the other lists too | — |
| `MISSED` | A key only the blind count has, at a File + Symbol the implementer lists under **no** control | HIGH — the reviewer re-runs the mutation of each site the blind count names there, in the same pass: a test fails → `CONFIRMED-MISSED` (resolved: the reviewer appends the row to the inventory, below); no test fails → *a site no test proves* (below) |
| `CROSS-FILED` | A key only the blind count has, at a File + Symbol the implementer lists under **any other control** — whether or not the implementer lists the blind key's control anywhere | MEDIUM — the reviewer re-runs the mutation of each site the blind count names there, in the same pass: a test fails → `CONFIRMED-CROSS-FILED` (resolved: the place is listed and proven, only the control label differs; no row is owed); no test fails → *a site no test proves* (below) — unless an argued row already covers that statement (below) |
| `EXTRA` | A key only the implementer has | MEDIUM — the reviewer re-runs each extra site's mutation in the same pass: a test fails → `CONFIRMED-EXTRA` (resolved); no test fails → *a site no test proves* (below) — unless the row is an argued (ii) or (iii) row (below) |
| `UNCOUNTED` | A control in the implementer's inventory for this scope that the blind count did not inventory | control stays `Partial`; MEDIUM — the reviewer adjudicates it: **not a control / out of scope** (with a register: an ID the register does not list is not a control) → the fixer deletes its rows, or re-keys them to the control the rule belongs to (resolved); **a real control** → its ID goes into the next recount's `ALSO INVENTORY` list (ID only, never sites or counts) |
| `MISSED+EXTRA`, `CROSS-FILED+EXTRA`, `MISSED+CROSS-FILED`, `MISSED+CROSS-FILED+EXTRA` | More than one of `MISSED`, `CROSS-FILED`, `EXTRA` at different keys of one control (often the same site filed under different symbols or controls) | each `MISSED` key is HIGH and each `CROSS-FILED` or `EXTRA` key is MEDIUM, handled as above |
| `CARRIED` | The only differences are at carried keys | LOW, listed under `## Carried`; not a finding. At `SLICE-XXX` scope the control stays `Partial` until the `FEATURE` recount; at `FEATURE` scope (a later round of the final check) it is judged as `MATCH` for `Complete`, below — the first round compared those keys in full |
| `OUT-OF-SCOPE-BY-DECLARED-SCOPE` | The blind count declared partial scope (§4.1) and the only differences are implementer rows outside it | carried rows: LOW, under `## Carried`. Rows in code this slice changed: MEDIUM — the count skipped code it was responsible for; the reviewer adjudicates as for `UNCOUNTED`. Control stays `Partial` |
| `GAP` | The only issue is a blind-count gap | HIGH (below) |

Blind-count `gap` rows are reported separately as HIGH findings, carried or not — a gap is broken code, not a filing disagreement. At `FEATURE` scope, each control in a `## Declared Scope` table is a MEDIUM `PARTIAL COUNT` finding and the comparison stays complete.

**A missed site a test already proves (`CONFIRMED-MISSED`).** When the reviewer deletes the site a blind row names at a `MISSED` key and a test fails, the site is real and proven; all that is owed is its inventory row. The reviewer appends that row itself, in the same pass: the blind row's Control, File, Symbol, Path class, and description, `Kind` = `site`, Disposition `(i)`, Evidence `mutation: <what was deleted> → failing test <test id> (reviewer, <SCOPE> iter <N>)`, and `Slice` = the slice under review at `SLICE-XXX` scope (at `FEATURE` scope: `—` in whole-feature mode, the slice that owns the code in per-slice mode). It is then resolved and is **not a finding** — no fix round, no recount, and no re-review is owed for it. This is safe because the reviewer changed no code: the blind count it reviewed still describes the code exactly. The reviewer adds a row only for a site it mutated itself in this pass — one a test failed for, or one recorded as *a site no test proves* (below); it never deletes a row, changes one only as that paragraph says, and never adds one on any other ground. One row per site, as everywhere (§4): a key with three blind rows that each fail a test gets three rows. If the inventory already holds a row **for that same site** — same key, same site, Evidence naming this scope and iteration, left by a review that was cut short and run again — it adds no second row for that site; other sites at the key still get theirs. *(Before 3.11.0 such a site was a HIGH tagged `[row-only]`, closed by a fix round, a recount, and a re-review.)*

**A green mutation at a site with an argued row.** A disposition-(ii) or (iii) row says in so many words that deleting its site alone fails no test (§3). So when the reviewer's mutation at an `EXTRA`, `CROSS-FILED`, or row-count key leaves every test green, **and an implementer row describes that same statement as (ii) or (iii) — under any control** — green is what the row claims, not a failed proof. It is resolved by the argument (`CONFIRMED-EXTRA` / `CONFIRMED-CROSS-FILED`, recorded as "by argument") once the reviewer has accepted that row's (ii) argument or (iii) owner note; a bare one is the usual MEDIUM. A green mutation is *a site no test proves* (below) only when no such row describes the statement, or when the row that does is recorded `(i)` — a site recorded as proven that is not. No further row is owed under the blind key's control: one argued row covers its statement under every label.

**A site no test proves.** The reviewer deleted a real site and every test stayed green, and no argued row covers that statement — at a `MISSED`, `CROSS-FILED`, `EXTRA`, or row-count key, or a recorded `(i)` in the reviewer's sample. The code holds the rule today; what is missing is the proof that it will tomorrow. What happens depends on the control:

- **A security control: HIGH `[needs-code-or-test]`**, fixed: a test that fails without the site, a change to the code, or an argued (ii)/(iii) row. A missing proof at a security site is the hole an attacker looks for. A control is a security control when its own ID, or any ID the register files under it, starts `SEC-` — so a restating `SEC-` entry filed under a `REQ-` makes that `REQ-` a security control; in a SPEC with no register, when its key starts `SEC-` or a filing convention files a `SEC-` ID under it. A rule the SPEC states as a security rule under another ID — an agent-security rule written as a `REQ`, say — is one too: the reviewer decides from the SPEC's text, and in doubt treats it as one.
- **Any other control: recorded, not fixed.** The reviewer writes it into the inventory, in the same pass. **When a row already describes the site** — the `EXTRA` row itself, the `(i)` row under another control at a `CROSS-FILED` key, a sampled `(i)` — the reviewer changes that row: Disposition `(iii)`, Evidence `owner: review (<SCOPE> iter <N>); follow-up: a test that fails when <what was deleted> is deleted`. **Only when no row describes it** does the reviewer add one: the blind row's Control, File, Symbol, Path class, and description; `Kind` `site`; Disposition and Evidence as above; `Slice` as for a `CONFIRMED-MISSED` row. That change is the one change to an existing row a reviewer ever makes. It is **not a finding**: not numbered, not counted in the marker, no fix round, no recount. The review lists it under `Recorded, not proven`; the implementation summary lists every such row for the user, and in per-slice mode the ledger carries it as it carries every (iii) site. It does not by itself keep the control from `Complete` (below). A later implementer or fixer who writes the test turns the row to `(i)`.

Why the line falls at security: in the cycles that led to this rule, most fix rounds went into writing tests for code that already held its rule, and each round re-ran the whole review. A gap is different, and stays HIGH for every control: a path with no site at all is broken code, not a missing proof.

**What is left to reject on.** With the register, places compared before labels, and the two rules above, a difference in how a site is filed is never a finding by itself. A review's site findings are these and no others: a gap; a site of a security control whose mutation leaves every test green and that no argued (ii)/(iii) row covers; a bare (ii) or (iii); an output contract's path class with no real-subprocess test; an uncounted control or a partial count; and a leak. A scope leaves its review loop when none of them is open.

**Row counts (`## Row Counts Differ`).** A key both sides list, with a different number of rows, is reported **LOW** in its own section with both counts (`ROWS-DIFFER`). It is **not a finding**: it does not make the result `MISMATCH`, does not change the control's outcome, does not block `Complete`, and never enters a review's findings, the fix loop, or the stall check. No inventory row is owed for it.

One check remains, because the diff no longer flags a second, forgotten site inside a function that already has one listed. At every such key where **the blind count has more rows**, the reviewer re-runs the mutation of each blind row there that no implementer row describes — every one, not a sample — and records the result per key in the review. A test fails → nothing is owed. No test fails → that site is *a site no test proves*, like any other (above) — unless an argued row already covers that statement (above). A key where the implementer has more rows needs nothing beyond the reviewer's ordinary mutation sample.

**The `Result:` line.** `MATCH` or `MISMATCH (h HIGH, m MEDIUM)`. A `MATCH` may carry a bracketed LOW note — `n LOW carried or out-of-scope, owed to the FEATURE recount`, `n LOW row counts differ` (with `, k with more blind rows` when the check above is owed at `k` keys), or both joined by `; `. A `MISMATCH` may carry `+ n LOW`, the total of both kinds.

**A control is `Complete` only when** the per-control outcome in its latest site diff is `MATCH` — or, at `FEATURE` scope, `CARRIED` — (or its only differences are `CONFIRMED-MISSED`, `CONFIRMED-EXTRA`, or `CONFIRMED-CROSS-FILED` recorded in the review, and sites the review recorded as not proven, above), every key of it where the blind count has more rows has its check recorded in a review of that diff with no site left open (a site recorded as not proven, above, is not open), the blind count has no open gap for it, and the reviewer has accepted every (ii) argument and (iii) owner note. Otherwise it is `Partial`. **A control with no independent count is `Partial` — never `Complete`.** A (iii) site does not by itself block `Complete`; it is carried to the ledger's *Open recommendations awaiting user decision* with its owner.

Control status lives in the IMPLEMENTATION-PLAN's `## Control Site Status` table:

```markdown
## Control Site Status

| Control | Implementer sites | Independent sites | Latest diff | Status | Open (iii) owners |
|---|---|---|---|---|---|
| D-10 | 26 | 26 | SDD/reviews/SITE-DIFF-SLICE-003-…-iter2-….md | Complete | — |
```

The two site columns are row totals copied from the diff. They are a record, not the test: a control can be `Complete` with different totals, and is not `Complete` merely because they are equal.

## 7. Depth by tier

The tier standard (`simplicity-challenge/references/tiers.md`, Tenet 1) sets, for a tiered SPEC, which controls are proven site by site and how many blind counts are made. This section says what that means for each step. When implementation begins, the orchestrator reads the SPEC's `tier:` and appends, directly under `## Feature - Implementing` and its `Base commit:` line:

```markdown
## Site Depth - sites: <all | security>, blind counts: <every scope | final check>
```

Tier 1 → `security`, `final check`; Tier 2 → `all`, `final check`; any later tier, or no `tier:` → `all`, `every scope`. A part of a tier takes its tier's row. A cycle whose record has no such line — one that began implementing before 3.14.0 — is `all`, `every scope`. Every implementer, fixer, counter, reviewer, retrospective, and completion spawn of Step 4 is passed the line `Site depth: all` or `Site depth: security`; the blind-count setting is the orchestrator's alone.

**`Site depth: security`.** The rules of this standard apply to the security controls only (§6, *A site no test proves*, says which controls those are). The implementer inventories their sites, with a mutation each; the counter counts only them; the reviewers verify only them; the `## Control Site Status` table has a row for each of them and no other. Every other control is held by a real test of the requirement that states it — which the Test Integrity Lens checks as it checks every test (`references/test-integrity.md`) — and has no inventory row, no blind count, no deletion proof, and no status row. An implementer row for one is set aside like a row in a plugin file (§1): the reviewer writes `not a site at this depth` beside it, it is not a finding, and the next implementer or fixer deletes it. A diff's `UNCOUNTED` for a control that is not a security control is resolved the same way, never a finding. A SPEC with no security control is counted at the final check all the same: the counter finds no control in scope, the diff says so, and the verification's site steps have nothing to check.

**`Blind counts: final check`.** No count is made after a slice, after a slice's fix round, or for the whole feature before its code review: 4a.5 is skipped. The final check (4e.5) counts and diffs as in every cycle. A slice review or the whole-feature code review then has no count and no diff, so its site verification runs only the steps that read the implementer's inventory — the mutation sample, the (ii)/(iii) arguments, the real-subprocess tests, and the leak check (steps 3–6) — while the steps that turn a diff into findings (1–2b) have nothing to carry. A slice's fix round has no recount: its iteration is snapshot → fix → snapshot → re-review. Until the final check every control is `Partial`, as a control with no independent count always is (§6).
