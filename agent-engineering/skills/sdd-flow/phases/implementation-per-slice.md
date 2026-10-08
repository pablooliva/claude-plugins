# Phase: Implementation — per-slice mode

Reached at Step 4 when the spec's `delivery_mode:` is `per-slice`. The whole-feature 4a–4j steps DO NOT run; the orchestrator iterates `SLICE-XXX` entries from the spec's `## Delivery Slices` section, executing the per-slice cycle for each in order, then runs the end-of-feature cycle once after the last slice lands.

Per-slice subagents carry the Safety-Net Rule + a fresh counter file (`Reads: 0/20` for the implement step and the blind site count, `Reads: 0/15` otherwise) + a compact body path (`site-count-compact.md` for the blind site count, `implementation-compact.md` for every other step). Body paths are `SKILL_ROOT/bodies/<file>.md`, resolved absolute. **STANDARD** = `SKILL_ROOT/references/enforcement-sites.md` (resolved absolute) is passed to the implement, site-count, review, fix, and retro spawns — it defines control, enforcement site, the per-site mutation standard, the three dispositions, and the inventory shape.

**Tracing inputs** are the ones `phases/implementation-whole-feature.md` defines at its top — the gate line `tracing: on|off` and, with the gate on, **TRACING**, **OBS_RECORD**, **TRACE_TREE_SCRIPT**, **LENS**, and **TRACE_TREE** — with one difference: for a slice, **TRACE_TREE** = `SDD/reviews/TRACE-TREE-SLICE-XXX-[feature-name]-[YYYYMMDD].md`. They go to the implement (4a), review (4b), and fix (4c) spawns of every slice, to the end-of-feature fix (4e), and to the shared end-of-feature steps as that file says — the 4e.5 verification and its fix, and the completion spawn (4f: the gate line, OBS_RECORD, and the final tree only) — never to the blind site count, the retrospective, or the 4a.0 scaffold spawn. The fix rule defined there is embedded verbatim in every fix prompt when the gate is on. Tracing adds no slice state, marker, or stop: the table below is unchanged by it.

---

## Who owns what on the slice path

Every slice state change, stop, and commit has one owner, named here. A slice body does what its row says and nothing else; what a row gives to the orchestrator, the orchestrator does at the step named — no body does it, and no body describes it as something the orchestrator "may" do.

| What | Owner | Step |
|---|---|---|
| Slice row `Not Started` → `In Progress`; `## Slice SLICE-XXX - In Progress` (with `Base commit:`); `## Slice SLICE-XXX - Implemented` | `bodies/slice-start.md` | 4a |
| `## Site Count SLICE-XXX iter <N> - Complete` | `bodies/site-count.md` | 4a.5 |
| `## Site Diff SLICE-XXX iter <N> - …` | orchestrator | 4a.5 |
| `## Review SLICE-XXX iter <N> - …` | `bodies/slice-review.md` | 4b |
| `## Fix SLICE-XXX iter <k> - Complete` | the fix subagent | 4c |
| The fix-loop stop: `## Awaiting Slice Resolution` | orchestrator | 4c |
| The stopped slice's open findings into the ledger; `## Slice SLICE-XXX - Halt Note Recorded` | `bodies/slice-retro.md`, `MODE: halt-note` | 4c, on halt |
| Slice row → `Acceptance Check Passing`; `## Slice SLICE-XXX - Retrospective Complete` | `bodies/slice-retro.md` | 4c.5 |
| `## Slice SLICE-XXX - Retro Matched (…)`; the re-planning stop: `## Awaiting Re-planning Decision` | orchestrator | 4c.5 |
| Slice row → `Complete`; the slice's commit; `## Slice SLICE-XXX - Committed` | orchestrator | 4c.6 |
| The slice-boundary pause (no halt block — it needs no answer) | orchestrator | after 4c.6 |
| After a re-plan: `## Re-plan Preparation - Started`; archiving the old slice table; moving the replaced plan's slice files to `superseded/<stamp>/`; stamping its slice IDs in the ledger's `Sources:` fields; `## Slices Superseded` | orchestrator | 4a.0 |
| Finishing a retrospective that was cut short — its ledger, table, and progress writes, from the retrospective already on disk | `bodies/slice-retro.md`, `--reconcile-ledger` with `FINISH: SLICE-XXX` | 4c.5, on resume |

How a resumed session reads these markers: `phases/protocols.md` → Phase Detection Priority, per-slice cycle sub-steps.

The end-of-feature steps (4d–4j) are shared with whole-feature mode, and their markers and stops — `## Final Recount - …`, `## Awaiting Site-Count Resolution`, `## Awaiting Commit Approval`, `## Implementation - Committed`, `## Feature - Done` — are owned as `phases/implementation-whole-feature.md` states: all by the orchestrator.

---

## Slice-boundary checkpoint axis (REQ-024)

A **separate axis** from the supervised/autonomous (phase-boundary) axis. Default `on` in per-slice mode in BOTH modes — without this default, opting into per-slice would degrade into "more internal gates with no human review," defeating the reason to opt in. Suppressed via `--skip-slice-checkpoints`.

| Phase-boundary | Slice-boundary | Behavior |
|---|---|---|
| supervised | on | Pauses at the design gate + each completed slice + impl-end |
| supervised | off | Pauses at the design gate + impl-end; slices run continuously inside |
| **autonomous** | **on** (default) | Pauses at the design gate; then planning autonomous; pause between each fully-completed slice; end-of-feature autonomous through commit |
| autonomous | off (via `--skip-slice-checkpoints`) | Pauses at the design gate; autonomous from there to the finish |

The design gate (Step 2.5) stops in every row, and so does the Step 3g deviation check when the spec departs from the approved brief — neither is a slice-boundary or mode setting.

---

## Per-slice 4a.0 — Scaffold the implementation tracker (once per feature)

Before the first slice, if `progress.md` has no `## Feature - Implementing` line for this feature, append one with its `Base commit:` line, exactly as whole-feature 4a does (`phases/implementation-whole-feature.md` → 4a). It records the commit before SLICE-001; the end-of-feature recount (4e.5) takes its `BASE` from it. A re-plan does not rewrite it.

**After a re-plan, clear the replaced plan away first** — before the table check below. It applies when the latest `## Awaiting Design Approval` block says `Re-plan: yes` and no `## Slices Superseded` line follows the latest `## Planning - Accepted`. The orchestrator, in this order:

1. Appends `## Re-plan Preparation - Started` to `progress.md` — one line naming a **new** folder `SDD/implementation/slices/superseded/[YYYY-MM-DD_HH-MM-SS]/`. If such a line already follows the latest `## Planning - Accepted` (an earlier attempt was cut short), write no new one and reuse its folder: steps 2–4 each skip what is already done.
2. In the IMPLEMENTATION-PLAN, renames the live `## Slice Progress` header to `## Archived Slice Progress (pre-replan)`. The table stays verbatim, as audit trail. (No live header: already done — skip. The fresh table is scaffolded only after step 5, so a live table found here is always the replaced plan's.)
3. Moves the replaced plan's per-slice files into that folder (`git mv`, so history follows): every `RETROSPECTIVE-SLICE-*`, `REVIEW-SLICE-*`, `SITE-COUNT-SLICE-*`, `SITE-DIFF-SLICE-*`, and `TRACE-TREE-SLICE-*` file of this feature still in its original place. They are kept, never deleted, and a folder per re-plan means a second re-plan — whose files carry the same names — never collides with the first. The new plan reuses the old slice IDs, and the retrospective body refuses to write a retrospective for a slice that already has one; the reviews and diffs a new slice's retrospective and the brief-check line pick up by ID must be the new plan's only. The site inventory and the per-slice commits stay where they are.
4. In the rolling ledger, marks the replaced plan's slice IDs: inside every `Sources:` field, appends `@<the folder's stamp>` to each **bare** slice ID (`SLICE-001` → `SLICE-001@2026-10-03_14-30-45`); an ID that already carries a stamp is left alone. Nothing else in the ledger changes. A stamped ID names a slice of the replaced plan, so the new plan's `SLICE-001` is never mistaken for one the ledger already covers (`bodies/slice-retro.md` → `Sources:` convention).
5. Appends `## Slices Superseded` to `progress.md` — one line: the folder, and how many files it holds.

Then check whether `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md` already exists with a `## Slice Progress` table (it will, when resuming). If absent, spawn ONE **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/implementation.md` — its `per-slice` branch is **scaffold-only**: create the tracker with the `## Slice Progress` table populated from the spec's `## Delivery Slices` (all rows `Not Started`), then return without implementing anything.
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `progress.md`.
- **Output:** the IMPLEMENTATION-PLAN tracker at the path above (always named in the prompt — the body returns a failure without it); append `progress.md`.
- **After a re-plan** the live table is always absent at this point: give the scaffold a post-replan note in the prompt, and it writes a FRESH `## Slice Progress` table from the revised spec.

Without this scaffold, `bodies/slice-start.md` halts per FAIL-007 (missing `## Slice Progress` table).

---

## Per-slice cycle (runs once per `SLICE-XXX`, in order)

### Per-slice 4a — Implement slice
Spawn ONE **`agent-engineering:sdd-workhorse`** subagent (strict — no bundling):
- **Body:** `bodies/slice-start.md` (for `SLICE-XXX`).
- **Which slice:** always name it in the prompt — never leave the body to pick. It is the first row after the last committed slice, in table order, that is not `Complete`; on the first cycle after a re-plan with `--from-slice`, the slice that flag named. Pass `--resume SLICE-XXX` when that slice's row is already `In Progress` (a 4a that was interrupted): the body re-attaches and carries on from the working tree, without resetting the row or the base commit. There is no way to re-start a `Complete` slice — the body refuses; work on a finished slice goes into a later slice or a re-plan.
- **Inputs:** the active spec, the rolling ledger `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md`, the IMPLEMENTATION-PLAN path, **STANDARD**, and — if it exists — **CONVENTIONS** (`SDD/implementation/sites/SITE-CONVENTIONS-[feature-name].md`, standard §4.2). **The prompt receives ONLY the ledger** (per OQ-6 — individual retrospectives are out of the prompt path).
- **Outputs:** slice code + tests; the living site inventory `SDD/implementation/sites/SITES-IMPL-[feature-name].md` (rows for every site of every control the slice touches, each with a disposition and per-site mutation evidence); a `## Slice SLICE-XXX - Implemented` entry in `progress.md`.
- **Tracing:** the **tracing inputs** (top of this file). With `tracing: on` the body's Step 11.5 applies: the implementer follows the tracing standard for what the slice adds and checks the slice's `Traced nodes:` against the trace run.
- **Task:** Implement the slice end-to-end and record its enforcement sites (body Steps 10–12). Bounded return: "Slice X delivered. Acceptance check `<test name>` passes."

### Per-slice 4a.5 — Blind site count + diff (iteration N)

Runs after 4a (as `iter0`) and again after every 4c fix iteration k (as `iter<k>`). **It exists because an implementer's site list shares the implementer's blind spots** — every under-count in the motivating project was found by someone reading the code fresh, never by the implementer checking its own list.

**Spawn** ONE fresh **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/site-count.md`. **Compact body:** `bodies/site-count-compact.md`. **Counter:** `SDD/orchestration/counters/4a5-SLICE-XXX-iter<N>-[timestamp].md` with `Reads: 0/20`. Embed the Safety-Net Rule verbatim.
- **Inputs — the allowlist, and nothing else:** the SPEC path, `SDD/UBIQUITOUS_LANGUAGE.md` (if present), **STANDARD**, `SCOPE = SLICE-XXX`, `ITER = N`, the slice's `Modules touched`, `BASE` = the `Base commit:` recorded in the slice's latest `## Slice SLICE-XXX - In Progress` entry (HEAD when the slice started — never re-derive it from HEAD, which may already include the slice after a resume) (the slice's work is uncommitted until 4c.6, so the counter diffs the working tree against `BASE` and lists untracked files — never `BASE..HEAD`), the **CONVENTIONS** path if that file exists (filing rules only — it is count-free by the standard §4.2; never paste its content or anything else from a review into the prompt), and — only on a recount whose previous review recorded one — the `ALSO INVENTORY` SPEC IDs (IDs only).
- **Output:** `SDD/reviews/SITE-COUNT-SLICE-XXX-[feature-name]-iter<N>-[YYYY-MM-DD].md`; appends `## Site Count SLICE-XXX iter <N> - Complete`.
- **Blindness is enforced by this prompt.** NEVER put in it: the implementer's inventory path or contents, the IMPLEMENTATION-PLAN, `progress.md` excerpts, the implementer's bounded return, earlier `SITE-COUNT-*`/`SITE-DIFF-*`/review paths, or any count. A fresh spawn per iteration — never a continuation of an earlier count. Using `sdd-workhorse` is still independent: the counter shares the implementer's model but not its context or its claims, which is the independence that caught every historical miss (the per-slice reviewers who found them were also `sdd-workhorse`).
- If the counter appends `## Site Count SLICE-XXX iter <N> - BREACHED` (or the output's first line says `BLINDNESS BREACHED`), discard that output and re-spawn a fresh counter for the same iteration (counts toward Error Handling's two-failure limit).

**Diff (orchestrator, mechanical):**

```bash
python3 "$SKILL_ROOT/scripts/site-diff.py" \
  SDD/implementation/sites/SITES-IMPL-[feature-name].md \
  SDD/reviews/SITE-COUNT-SLICE-XXX-[feature-name]-iter<N>-[YYYY-MM-DD].md \
  SDD/reviews/SITE-DIFF-SLICE-XXX-[feature-name]-iter<N>-[YYYY-MM-DD].md \
  --scope SLICE-XXX --base <BASE>
```

`<BASE>` is the same slice base commit the counter received (`none` if the repo had no commits). With it, the script classifies disagreements on code the slice did not change as **carried** — LOW, in their own section, owed to the FEATURE recount (standard §6). The script compares which `Control + File + Symbol` keys each side lists, not how many rows a key has: a key both sides list with different row counts is LOW in its own `## Row Counts Differ` section and never makes the result `MISMATCH`. Always pass it at `SLICE-XXX` scope; without it every disagreement is compared as owned.

Exit 0 = `MATCH`, 1 = `MISMATCH`, 2 = input error (missing/malformed inventory — treat as a failed implement or count step and re-spawn it; a git error on `--base` — re-check the recorded base commit). The script's first stdout line is the `Result:` line. Append to `progress.md`, copying the result verbatim (it may carry a LOW suffix — carried lines, row-count lines, or both):

```markdown
## Site Diff SLICE-XXX iter <N> - <MATCH | MISMATCH (h HIGH, m MEDIUM)>[ LOW suffix]

- **Diff:** SDD/reviews/SITE-DIFF-SLICE-XXX-[feature-name]-iter<N>-[YYYY-MM-DD].md
```

The orchestrator does not interpret the diff further: every outcome goes to 4b, which turns it into findings. A mismatch is a finding inside the existing review/fix loop — never a separate loop.

### Per-slice 4b — Per-slice code review
Spawn an **`agent-engineering:sdd-workhorse`** subagent with `bodies/slice-review.md` for `SLICE-XXX`. **Mandatory per slice** — not deferred to end-of-feature. Writes `SDD/reviews/REVIEW-SLICE-*`. Pass the active spec and the IMPLEMENTATION-PLAN path — the body takes both from its prompt and returns a failure without them. Pass **BRIEF** (`SDD/requirements/DESIGN-[###]-[feature-name].md`, with its approved revision and tier) for the review's `## Design Brief Check`, and **TIERS** when the spec carries `tier:` (the body's *Respect the Tier* rule). Pass `SCOPE = SLICE-XXX` and `ITER = N` — the iteration of the count and diff being reviewed (0 after 4a, k after fix round k); the review writes its resume marker from them and must not infer either. Pass `BASE` — the same slice base commit 4a.5 uses; the slice is uncommitted during review, so the reviewer diffs the working tree against it. Pass **STANDARD**, the site inventory, **CONVENTIONS** (the path even if the file does not yet exist — the review may create it), and the latest iteration's `SITE-COUNT` and `SITE-DIFF` paths — the body's Step 5.6 carries every diff finding into the review, resolves `EXTRA` and `CROSS-FILED` keys by re-running their mutations, checks every row-count key where the blind count has more rows, re-runs a mutation sample, and verifies dispositions (ii)/(iii) are argued. When the spec's `agent_security:` gate is `true` or `auto`/absent **and CATALOG exists**, pass the resolved **CATALOG** path, the resolved gate value (`agent_security: true` or `agent_security: auto`), and the panel review `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md` so the body's Agentic-Surface Lens can run over the slice's file set and check it against the panel's `AI Agent Security Findings` and `Abuse cases to cover`. A missing catalog closed the gate for the whole run at Step 0: pass neither, and the body records that the lens was skipped.

**Tracing (4b).** Pass the **tracing inputs**. With `tracing: on` the body's Step 5.8 runs the application's trace run once the slice's tests pass, writes TRACE_TREE, and compares it with the marked nodes on this slice's `Traced nodes:` line and those of the slices before it — never a later slice's. Its findings are ordinary findings of the slice review, counted in the review marker like any other. With `tracing: off` the body records that the lens was skipped.

### Per-slice 4c — Address per-slice findings
If the review found anything — HIGH, MEDIUM, or LOW — spawn an **`agent-engineering:sdd-workhorse`** fix subagent; it resolves all of it (Key Principle 2). The slice goes on to 4c.5 only when its latest review reports no finding. The orchestrator tells from the review marker, without opening the review: the three counts follow either verdict, and "no finding" means all three are zero. (A marker with no LOW count was written before 3.5.1, when LOW was not reported: for the slice in progress, open that review document and count its LOW findings before treating it as finding-free.) Standard fix-and-re-review with the **per-slice iteration cap (REQ-012):** max 3 iterations with progress-stall check — mirrors Step 3c's panel cap, with one refinement: the stall check counts **needs-code-or-test** HIGH only. Each review marker reports how many of its HIGH are **row-only** (a missed site the reviewer proved already caught by a test — see `bodies/slice-review.md` Step 5.6); needs-code-or-test HIGH = h − r. Progress = needs-code-or-test HIGH strictly decreased, OR — when it was zero in the previous iteration — MEDIUM strictly decreased. Row-only HIGH never trip the stall on their own (a recount that finds more already-tested sites is not a regression), but they still reject the slice until closed, and the 3-iteration cap still applies. **LOW never counts toward the stall check:** when needs-code-or-test HIGH and MEDIUM were both zero in the previous iteration there is nothing to stall on, and only the cap applies. A slice whose review found only LOW therefore takes one round (fix → blind recount → diff → re-review) — the accepted cost of resolving every finding. The cap counts the `## Fix SLICE-XXX iter <k>` lines after the slice's latest `In Progress` entry — and, once the slice has an `## Awaiting Slice Resolution` block after that entry, only those after the latest such block. Lines above the `In Progress` entry belong to an earlier run of that ID (a replaced plan's slice) and never count.

**One iteration k = fix → 4a.5 recount (`iter<k>`) → diff → 4b re-review.** The fix subagent appends `## Fix SLICE-XXX iter <k> - Complete` to `progress.md` when done; each review appends `## Review SLICE-XXX iter <N> - APPROVED | REJECTED (h HIGH [r row-only], m MEDIUM, l LOW)` (`N` is the `ITER` passed in its prompt — 4b; a marker without the bracket means r = 0, which is how every pre-2.7.0 marker reads; the LOW count is always written, zero included, and a marker without one is a pre-3.5.1 marker — see above). These, with the `Site Count` / `Site Diff` lines, are the phase-detection markers for a resumed run. The fix subagent receives **STANDARD**, **CONVENTIONS** (if it exists), the review, and the inventory; for every site-count finding it adds the missing site(s) to `SITES-IMPL-[feature-name].md` with a disposition, a fresh per-site mutation, and `Slice` = this SLICE-XXX; deletes rows for sites its fix removed; fixes or implements any `GAP`, and never deletes a (ii)/(iii) site as dead code. It never adds, splits, or merges rows only to make the two sides' row counts agree — a row-count difference is not a finding (standard §6). The recount is a fresh blind spawn (its prompt carries no earlier count, diff, or review) — fixes add sites, so a stale count would miss them. Site-count findings are ordinary review findings, so the progress-stall check counts them with everything else (row-only HIGH excepted, as above); the cap is unchanged. Carried LOW lines and row-count LOW lines in the diff are not review findings and never enter the loop or the stall check; only a site the reviewer's row-count check found unproven does, as an ordinary needs-code-or-test HIGH.

**On halt (cap exhausted or progress stall)** the flow stops, in every mode and whatever the slice-checkpoint setting — building later slices on unresolved findings compounds them. The slice does NOT proceed to 4c.5 or 4c.6, and no later slice starts. The orchestrator:

1. Spawns an **`agent-engineering:sdd-workhorse`** subagent with `bodies/slice-retro.md` and the line `MODE: halt-note`, passing `SLICE-XXX`, the active spec, the IMPLEMENTATION-PLAN path, the latest review, and the ledger path. It appends the unresolved findings to `LEARNINGS-FEATURE-[feature-name].md` under *Open recommendations awaiting user decision* and a short `## Slice SLICE-XXX - Halt Note Recorded` entry to `progress.md`, and writes nothing else — no retrospective, no table change. The orchestrator does not write the ledger itself.
2. Appends this halt block to `progress.md`, shows it, and stops:

```markdown
## Awaiting Slice Resolution

SLICE-XXX did not pass its review after <k> fix round(s) (<cap reached | no progress>). Unresolved: <h> HIGH, <m> MEDIUM, <l> LOW.
Latest review: <REVIEW-SLICE path>   Latest diff: <SITE-DIFF path>
Resolve the findings (or amend the SPEC), then run `/sdd-flow continue` — the flow re-counts and re-reviews the slice from a fresh iteration.
```

**On `/sdd-flow continue`** (`phases/protocols.md`): a fresh blind recount (4a.5) at the next unused iteration — one past the slice's highest `## Site Diff SLICE-XXX iter <k>` line — then the diff and a 4b review at that iteration, with a fresh 3-round cap and a stall check that starts over from that review. Never resume from the halted iteration's review: the code or the spec has changed since. This mirrors the final recount's `## Awaiting Site-Count Resolution`.

**Tracing (4c).** The fix subagent is passed the **tracing inputs** — TRACE_TREE being the file written by the review it answers, or none when that review wrote none (a trace run that failed or could not be rendered) — and, with the gate on, the fix rule, the active spec (it holds the planned call graph the finding is about), and the IMPLEMENTATION-PLAN path (the fix rule lets it record a deviation there). Nothing else about the loop changes: the 4b re-review that closes each round runs the lens again, so a tracing finding is re-checked after every fix, under this same cap, this same stall check, and this same stop.

### Per-slice 4c.5 — Slice retrospective (REQ-013)
Spawn an **`agent-engineering:sdd-workhorse`** subagent with `bodies/slice-retro.md` for `SLICE-XXX`, passing the active spec, the IMPLEMENTATION-PLAN path, **STANDARD**, and every `SITE-DIFF-SLICE-XXX-*` path for this slice. It records count mismatches in the retro's `## Site Count Reconciliation` section and the ledger's `Enforcement-site count mismatches` section, and updates the IMPLEMENTATION-PLAN's `## Control Site Status` rows. It writes `RETROSPECTIVE-SLICE-XXX-[feature-name]-YYYY-MM-DD.md` (audit trail; never modified after writing) and updates the rolling ledger in place.

**Two-stage matcher contract (resolves M-2; REQ-013 + REQ-014).** TWO surfaces — the retro-body header (in the retrospective ARTIFACT) and the halt block (in `progress.md`) — DIFFERENT strings, DIFFERENT times, DIFFERENT actors:
- **Retro-body header** (written by `bodies/slice-retro.md` into the retrospective artifact): BOTH `## Recommended SPEC Amendments` and `## Recommended Re-planning` are REQUIRED sections. When there is nothing to recommend, the section's body is the exact single line `None.` (case-insensitive, trailing period optional). A section whose body is `None.` carries NO recommendation; an absent section is a **malformed retro** (see the malformed-retro rule in Stage 1), not a "no" answer.
- **Progress.md halt block** (written by **THE ORCHESTRATOR**, never by the retro body): `## Awaiting Re-planning Decision` — written ONLY when the orchestrator's matcher finds a **non-`None.`** `## Recommended Re-planning` section in the just-written retro AND elects to halt.

**Stage 1 — Retro-stage match (right after the retro subagent returns, IN this cycle):** the orchestrator reads the just-written retrospective ARTIFACT (path from the subagent's return) and matches the EXACT retro-body header strings against the **artifact**.

**The artifact is the only evidence.** NEVER key Stage 1 off the retro subagent's bounded return, its summary, or any claim it makes about which sections it emitted — subagent self-reports about their own output have been observed to be wrong in both directions. The return supplies the retrospective PATH; the file supplies the answer.

**The match is conjunctive: header present AND body is not a no-op.** A section whose first non-empty body line is `None.` (case-insensitive, trailing period optional) is a declared "nothing to recommend" and MUST NOT be treated as a recommendation. Reference matcher:

```bash
# first non-empty line of the named section's body, or empty if the section is absent
section_body() {
  awk -v h="$2" '$0==h{f=1;next} f&&/^## /{exit} f&&NF{print;exit}' "$1"
}
BODY=$(section_body "$RETRO" '## Recommended Re-planning')
[ -z "$BODY" ] && echo "MALFORMED: section absent or empty"        # neither yes nor no
printf '%s\n' "$BODY" | grep -qiv '^none\.\?$' && echo "RE-PLANNING RECOMMENDED"  # halt
```

Apply the same conjunction to `## Recommended SPEC Amendments`. A missing or empty section on either header is a **malformed retro** — surface it at the slice-boundary pause and do NOT infer "no recommendation" from the absence.

**The matcher fails safe toward halting.** A body line that merely BEGINS with `None.` and continues into prose (`None. SLICE-002's ordering remains valid...`) does not match the no-op string and WILL halt. That is deliberate: the alternative — accepting a `None.` prefix — would silently swallow a genuine recommendation phrased as `None of the remaining slices survive...`. A missed halt is the more expensive failure. If a retro halts on this shape, the recommendation is a contract violation in the retro body, and `/sdd-flow continue --override-replan` is the correct operator resolution.

**Record the result, whatever it is.** As soon as the matcher has run, the orchestrator appends one line to `progress.md`: `## Slice SLICE-XXX - Retro Matched (<none | amendments | re-planning | malformed>)` — comma-separated when more than one applies. When the result includes `re-planning`, the halt block below is written in the same append, directly under it. Without this line nothing on disk says whether the matcher ran: a session that ended right after the retrospective would resume at the commit and skip a halt that is meant to fire in every mode. A resumed session that finds `Retrospective Complete` with no later `Retro Matched` for the slice runs the matcher from the retrospective file before anything else.

Header-match outcomes:
- `^## Recommended SPEC Amendments$` with a non-`None.` body → routine amendment recommendation; surface it in the slice-boundary pause as a per-recommendation summary (one or two lines per affected `SLICE-XXX`/`MODULE-XXX`/`REQ-XXX` — what should change, why), with the retrospective path for the user to read full wording. No halt block written.
- `^## Recommended Re-planning$` **whose first non-empty body line is not `None.`** → elevated severity. Per **REQ-014**, this HALTS the flow even under `--skip-slice-checkpoints`. The header alone does NOT halt — the body contract above permits `None.` as the declared no-re-plan shape, so halting on bare presence is a false positive. On match, the **orchestrator** writes this halt block to `SDD/orchestration/progress.md`:

```markdown
## Awaiting Re-planning Decision

SLICE-XXX retrospective recommends re-planning. SLICE-XXX is reviewed and not yet committed. Resume options:
- `/sdd-flow continue --replan` — commit SLICE-XXX as it stands, revise the design brief (Step 2.5; the design gate stops for your approval), then re-run Step 3 (planning) with the rolling ledger and triggering retro in scope; resumes implementation from SLICE-001 of the new plan.
- `/sdd-flow continue --replan --from-slice SLICE-XXX` — same, but resume from a user-specified slice (must match `^SLICE-\d{3}[a-z]?$` AND reference an existing SLICE-XXX in the new spec's `## Delivery Slices` per REQ-025).
- `/sdd-flow continue --override-replan` — commit SLICE-XXX and continue with the current plan — including any edit you have made to the spec by hand — despite the recommendation. Documented but discouraged.

This halt fires even under `--skip-slice-checkpoints` (mirrors the Step 3c panel-review halt).

Triggering retrospective: <retro-path>
```

The pause message uses the re-planning-specific shape:
> **Re-planning recommended.** The slice retrospective has determined the original plan is no longer fit. The flow is halted to await your direction.
> Resume options:
>   1. `/sdd-flow continue --replan` — commit this slice as it stands, revise the design brief for your approval, then re-run Step 3 with the ledger + triggering retro; produces a revised SPEC; resumes implementation from `SLICE-001` of the new plan.
>   2. `/sdd-flow continue --replan --from-slice SLICE-XXX` — the same, resuming from the slice of the new plan you name.
>   3. `/sdd-flow continue --override-replan` — explicit override; commit this slice and continue on the current plan, including any edit you have made to the spec by hand.
> A plain `/sdd-flow continue` is refused while this is pending.
> See `<retro-path>` for the full rationale.

The message lists exactly the options the resume rule accepts (`phases/protocols.md`) — no others.

**What either flag does first.** The halt leaves the triggering slice reviewed, retrospected, and uncommitted. Both flags begin by recording the answer — `## Halt Resolved - Awaiting Re-planning Decision`, with the flags on one line — and then running **4c.6 for the triggering slice**: under `--override-replan` as an ordinary slice commit, after which the next slice starts (no slice-boundary pause — the flag was the user's direction); under `--replan` with a commit message that says the slice preceded a re-plan, after which Step 2.5 re-runs. No slice ever starts on top of another slice's uncommitted work.

**In autonomous + --skip-slice-checkpoints mode this halt fires regardless** — compounding subagent runs on a known-broken plan is the higher-cost failure.

**Stage 2 — Resumption-stage match** (Phase Detection on `/sdd-flow continue` from a fresh session) reads `progress.md` for `## Awaiting Re-planning Decision` (the orchestrator-written block, NOT the retro-body header). See `phases/protocols.md` → Phase Detection Priority.

### Per-slice 4c.6 — Per-slice commit
Reached only when the slice has a `Retro Matched` line and no halt is pending. The **orchestrator**, in this order:

1. **Sets the slice's row to `Complete`** in the IMPLEMENTATION-PLAN's `## Slice Progress` table — its last edit before the commit, so the commit carries it. No body sets `Complete`, and the next slice's start refuses while another row is `In Progress` or `Acceptance Check Passing`.
2. **Runs the atomic per-slice commit** (commit conventions in `commands/commit.md`) covering: slice code + tests + site inventory + the IMPLEMENTATION-PLAN + every `SITE-COUNT-SLICE-XXX-*` / `SITE-DIFF-SLICE-XXX-*` + the slice's `TRACE-TREE-SLICE-XXX-*` (when the tracing gate is on) + per-slice review doc + fix-findings notes + retrospective + ledger update — and, for the first slice after a re-plan, the 4a.0 archive and moves. Message references `SLICE-XXX` and `SPEC-XXX`; **no co-author attribution**.
3. **Appends `## Slice SLICE-XXX - Committed`** to `progress.md` — one line, the commit's SHA. It is the marker that the slice is finished. A resumed session that finds `Retro Matched` with no `Committed` line re-enters here; both steps are safe to repeat (the row is already `Complete`; with nothing left to commit, no commit is made and the line reads `already committed`).

If `progress.md` exceeds ~500 lines, rotate it now (`phases/protocols.md` → Progress Rotation).

### PAUSE (slice-boundary)
Fires when slice-boundary checkpoints are `on`. The pause message includes: slice X completed + brief summary of what landed; acceptance-check status; the brief-check line (below); what the matcher recorded (SPEC amendments, or a malformed retrospective); the next slice in queue. It writes no halt block — it needs no answer: a plain `/sdd-flow continue` starts the next slice, found from the `Committed` line.

**Brief-check line.** Read the `## Design Brief Check` section of the slice's review document — the file, not the review subagent's return — and quote it as one line: `Brief check: delivers [outline entry]. Outside the approved footprint: [none | N file(s) — list]`. It tells the user whether the slice stayed inside what they approved at the design gate. It is information only: it never blocks a slice and never enters the fix loop. Resume via `/sdd-flow continue` (advances to next slice). A re-planning match never reaches this pause unanswered — it halts at 4c.5, before the commit.

When checkpoints are `off` (`--skip-slice-checkpoints`), this pause is skipped. The re-planning halt (4c.5) and the fix-loop halt (4c) are not pauses and fire regardless.

---

## End-of-feature cycle (runs once after the last slice's 4c.6 lands — its `Committed` line is written and no later row is `Not Started`)

7. **End-of-feature 4d — Critical review across the assembled feature.** Spawn an `agent-engineering:sdd-critical-reviewer` subagent with `bodies/critical-review.md` (Implementation Phase section); reviews the whole assembled feature, not individual slices. Pass **TIERS** when the spec carries `tier:`.
8. **End-of-feature 4e — Address critical review findings.** Standard `agent-engineering:sdd-workhorse` fix subagent. It is passed the **tracing inputs** (no TRACE_TREE — the critical review ran no lens) and, with the gate on, the fix rule.
   - **End-of-feature 4e.5 — Final blind recount (always runs).** Feature-wide (`SCOPE = FEATURE`) blind count + diff + site-verification loop. *(Shared step — see `implementation-whole-feature.md` §4e.5.)* Catches sites that span slices (a later slice's path needing an earlier slice's control) and sites changed by 4e. 4f does not start until it resolves. With `tracing: on` its verification always runs and also runs the Tracing Lens at `SCOPE = FEATURE`, writing `TRACE-TREE-FEATURE-[feature-name]-iter<k>-*`: the one comparison of the whole planned call graph with a single run, made after the last fix.
9. **End-of-feature 4f — Implementation completion subagent.** `bodies/implementation-complete.md` — finalize plan, write IMPLEMENTATION-SUMMARY, capture glossary deltas. *(Shared step — see `implementation-whole-feature.md` §4f.)*
10. **End-of-feature 4h — Supervised checkpoint.** Fires only in supervised phase-boundary mode. *(Shared — §4h, including its halt block, `## Awaiting Commit Approval`.)* Its brief-check line, and 4j's, is the per-slice form: collect each slice review's `## Design Brief Check` (`grep -A3 '^## Design Brief Check' SDD/reviews/REVIEW-SLICE-*-[feature-name]-*.md`) and report how many slices stayed inside the approved footprint, listing the exceptions.
11. **End-of-feature 4i — End-of-feature commit.** For a tiered spec, first run the in-review task mirror *(shared — §4i; it runs in both modes, right after 4f and before any 4h pause)*. Covers: critical review doc, fix-findings code from 4e, the 4e.5 `SITE-COUNT-FEATURE-*` / `SITE-DIFF-FEATURE-*` / `REVIEW-SITES-FEATURE-*` / `TRACE-TREE-FEATURE-*` files and inventory updates, completion artifacts from 4f. Per-slice code is already committed in each 4c.6. Then append `## Implementation - Committed` *(shared — §4i)*.
12. **End-of-feature 4j — Announcement.** *(Shared — §4j.)* Surface any ADRs. Append `## Feature - Done`. Then perform the **feature-completion rotation** per §4j (`phases/protocols.md` → Progress Rotation).

---

## EDGE-006 — plain `continue` while a re-planning recommendation is pending

If `/sdd-flow continue` is invoked **without a flag** while an `## Awaiting Re-planning Decision` block is the pending halt in `progress.md` (the latest block — no `## Halt Resolved - ` line follows it), the orchestrator emits an informative refusal naming the three options (`--replan`, `--replan --from-slice SLICE-XXX`, `--override-replan`) and exits. **No work is performed.** (Full resumption routing is in `phases/protocols.md`.)
