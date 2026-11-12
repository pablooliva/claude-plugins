# Phase: Implementation — per-slice mode

Reached at Step 4 when the spec's `delivery_mode:` is `per-slice`. The whole-feature 4a–4j steps DO NOT run; the orchestrator iterates `SLICE-XXX` entries from the spec's `## Delivery Slices` section, executing the per-slice cycle for each in order, then runs the end-of-feature cycle once after the last slice lands.

Per-slice subagents carry the Safety-Net Rule + a fresh counter file (`Reads: 0/20` for the implement step, `Reads: 0/15` otherwise) + the `implementation-compact.md` compact body path. A review step run on the second model carries none of the three (`references/second-model-review.md` §3). Body paths are `SKILL_ROOT/bodies/<file>.md`, resolved absolute. **SECURITY** = `SKILL_ROOT/references/security-verification.md` (resolved absolute) is passed to the implement spawn (4a) and to the end-of-feature steps as `phases/implementation-whole-feature.md` says. **The LOW rule and the scope-of-the-fix rule** defined at the top of that file apply to every review and fix here.

**Test integrity inputs** are the ones `phases/implementation-whole-feature.md` defines at its top — **TEST_INTEGRITY**, passed in every cycle to the slice implementer (4a), the slice review (4b), every fix spawn (with `BASE`, the SPEC, the IMPLEMENTATION-PLAN path, and the fix rule that block gives, embedded verbatim), and the end-of-feature critical review (4d, with the feature's `BASE`). **FIT** is defined there too and passed in every cycle to the slice review (4b), every fix spawn, and the end-of-feature critical review (4d).

**Tracing inputs** are the ones `phases/implementation-whole-feature.md` defines at its top — the gate line `tracing: on|off` and, with the gate on, **TRACING**, **OBS_RECORD**, **TRACE_TREE_SCRIPT**, **LENS**, and **TRACE_TREE** — with one difference: for a slice, **TRACE_TREE** = `SDD/reviews/TRACE-TREE-SLICE-XXX-[feature-name]-[YYYYMMDD].md`. They go to the implement (4a), review (4b), and fix (4c) spawns of every slice, to the end-of-feature fix (4e), and to the shared end-of-feature steps as that file says — the 4e.5 final check and its fix, and the completion spawn (4f: the gate line, OBS_RECORD, and the final tree only) — never to the retrospective or the 4a.0 scaffold spawn. The fix rule defined there is embedded verbatim in every fix prompt when the gate is on. Tracing adds no slice state, marker, or stop: the table below is unchanged by it.

**Evals inputs** are likewise the ones `phases/implementation-whole-feature.md` defines at its top — the gate line `evals: on|off` and, with the gate on, **EVALS**, **EVAL_TEMPLATES**, **OBS_RECORD**, and, for a review and the fix that answers it, the eval run line and **EVAL_RESULTS** — with one difference: for a slice, **EVAL_RESULTS** = `SDD/reviews/EVAL-RESULTS-SLICE-XXX-[feature-name]-iter<N>-[YYYYMMDD].md`, one file per review iteration, with its `.json` beside it. They go to the implement (4a), review (4b), and fix (4c) spawns of every slice, to the end-of-feature fix (4e), and to the shared end-of-feature steps as that file says — the 4e.5 final check and its fix, and the completion spawn (4f: the gate line, EVALS, and the final eval run line and EVAL_RESULTS only) — never to the retrospective or the 4a.0 scaffold spawn. The evals fix rule defined there is embedded verbatim in every fix prompt when the gate is on. **The eval run of record** defined there is made by the orchestrator before every 4b review, and at `SCOPE = FEATURE` before every review of the end-of-feature final check (4e.5). Evals add one marker and one stop, both the orchestrator's, in the table below. At the end of the feature they add the sign-off stop at the commit checkpoint (4h), and only when the spec has a sign-off requirement.

---

## Who owns what on the slice path

Every slice state change, stop, and commit has one owner, named here. A slice body does what its row says and nothing else; what a row gives to the orchestrator, the orchestrator does at the step named — no body does it, and no body describes it as something the orchestrator "may" do.

| What | Owner | Step |
|---|---|---|
| Slice row `Not Started` → `In Progress`; `## Slice SLICE-XXX - In Progress` (with `Base commit:`); `## Slice SLICE-XXX - Implemented` | `bodies/slice-start.md` | 4a |
| Evals gate on: the eval run of record; `## Eval Run SLICE-XXX iter <N> - …`; the stop when the model cannot be reached: `## Awaiting Eval Run` | orchestrator | 4b, before the review |
| `## Review SLICE-XXX iter <N> - …` | `bodies/slice-review.md` | 4b |
| `## Snapshot SLICE-XXX iter <k> - …` (before and after each fix round) | orchestrator | 4c |
| `## Fix SLICE-XXX iter <k> - Complete` | the fix subagent | 4c |
| The fix-loop stop: `## Awaiting Slice Resolution` | orchestrator | 4c |
| The stopped slice's open findings into the ledger; `## Slice SLICE-XXX - Halt Note Recorded` | `bodies/slice-retro.md`, `MODE: halt-note` | 4c, on halt |
| Slice row → `Acceptance Check Passing`; `## Slice SLICE-XXX - Retrospective Complete` | `bodies/slice-retro.md` | 4c.5 |
| `## Slice SLICE-XXX - Retro Matched (…)` | orchestrator | 4c.5 |
| Slice row → `Complete`; the slice's commit; `## Slice SLICE-XXX - Committed` | orchestrator | 4c.6 |
| The slice pause (no halt block — it needs no answer) | orchestrator | after 4c.6 |
| A re-plan the user asks for at the pause: `## Re-plan Requested` | orchestrator | after 4c.6 |
| After a re-plan: `## Re-plan Preparation - Started`; archiving the old slice table; moving the replaced plan's slice files to `superseded/<stamp>/`; stamping its slice IDs in the ledger's `Sources:` fields; `## Slices Superseded` | orchestrator | 4a.0 |
| Finishing a retrospective that was cut short — its ledger, table, and progress writes, from the retrospective already on disk | `bodies/slice-retro.md`, `--reconcile-ledger` with `FINISH: SLICE-XXX` | 4c.5, on resume |

How a resumed session reads these markers: `phases/protocols.md` → Phase Detection Priority, per-slice cycle sub-steps.

The end-of-feature steps (4d–4j) are shared with whole-feature mode, and their markers and stops — `## Final Check - …`, `## Eval Run FEATURE iter <k> - …` and `## Awaiting Eval Run` (evals gate on), `## Awaiting Final Check Resolution`, `## Awaiting Commit Approval` and `## Sign-off - …` (evals gate on, with a sign-off requirement), `## Implementation - Committed`, `## Feature - Done` — are owned as `phases/implementation-whole-feature.md` states: all by the orchestrator.

---

## Per-slice 4a.0 — Scaffold the implementation tracker (once per feature)

Before the first slice, if `progress.md` has no `## Feature - Implementing` line for this feature, append one with its `Base commit:` line, exactly as whole-feature 4a does (`phases/implementation-whole-feature.md` → 4a). It records the commit before SLICE-001; the end-of-feature steps take their `BASE` from it. A re-plan does not rewrite it.

**After a re-plan, clear the replaced plan away first** — before the table check below. It applies when the latest `## Awaiting Design Approval` block says `Re-plan: yes` and no `## Slices Superseded` line follows the latest `## Planning - Accepted`. The orchestrator, in this order:

1. Appends `## Re-plan Preparation - Started` to `progress.md` — one line naming a **new** folder `SDD/implementation/slices/superseded/[YYYY-MM-DD_HH-MM-SS]/`. If such a line already follows the latest `## Planning - Accepted` (an earlier attempt was cut short), write no new one and reuse its folder: steps 2–4 each skip what is already done.
2. In the IMPLEMENTATION-PLAN, renames the live `## Slice Progress` header to `## Archived Slice Progress (pre-replan)`. The table stays verbatim, as audit trail. (No live header: already done — skip. The fresh table is scaffolded only after step 5, so a live table found here is always the replaced plan's.)
3. Moves the replaced plan's per-slice files into that folder (`git mv`, so history follows): every `RETROSPECTIVE-SLICE-*`, `REVIEW-SLICE-*`, `TRACE-TREE-SLICE-*`, and `EVAL-RESULTS-SLICE-*` file of this feature still in its original place. They are kept, never deleted, and a folder per re-plan means a second re-plan — whose files carry the same names — never collides with the first. The new plan reuses the old slice IDs, and the retrospective body refuses to write a retrospective for a slice that already has one; the reviews a new slice's retrospective and the brief-check line pick up by ID must be the new plan's only. The per-slice commits stay where they are.
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
Spawn ONE **`agent-engineering:sdd-workhorse`** subagent **with the per-spawn model override `opus`** (strict — no bundling):
- **Body:** `bodies/slice-start.md` (for `SLICE-XXX`).
- **Which slice:** always name it in the prompt — never leave the body to pick. It is the first row after the last committed slice, in table order, that is not `Complete`. Pass `--resume SLICE-XXX` when that slice's row is already `In Progress` (a 4a that was interrupted): the body re-attaches and carries on from the working tree, without resetting the row or the base commit. There is no way to re-start a `Complete` slice — the body refuses; work on a finished slice goes into a later slice or a re-plan.
- **Inputs:** the active spec, the rolling ledger `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md`, the IMPLEMENTATION-PLAN path, **SECURITY**, **TEST_INTEGRITY**, **BRIEF** (`SDD/requirements/DESIGN-[###]-[feature-name].md`, with its approved revision), and **FIT** — the body's Step 10 follows FIT §5. **The prompt receives ONLY the ledger** (per OQ-6 — individual retrospectives are out of the prompt path).
- **Outputs:** slice code + tests (each security rule the slice touches proven, body Step 11, under `## Security Proofs` in the IMPLEMENTATION-PLAN); a `## Slice SLICE-XXX - Implemented` entry in `progress.md`.
- **Tracing:** the **tracing inputs** (top of this file). With `tracing: on` the body's Step 11.5 applies: the implementer follows the tracing standard for what the slice adds and checks the slice's `Traced nodes:` against the trace run.
- **Evals:** the **evals inputs** (top of this file). With `evals: on` the body's Step 11.6 applies: the implementer builds the cases on the slice's `Evals:` line — rendering the eval run from EVAL_TEMPLATES when the application has none yet — and makes its own eval run.
- **Task:** Implement the slice end-to-end and prove the security rules it touches (body Steps 10–12). Bounded return: "Slice X delivered. Acceptance check `<test name>` passes."

### Per-slice 4b — Per-slice code review
By the cycle's **review route** (`references/second-model-review.md`) — on the Claude route, an **`agent-engineering:sdd-workhorse`** subagent — run `bodies/slice-review.md` for `SLICE-XXX`. **Mandatory per slice** — not deferred to end-of-feature. Pass the active spec and the IMPLEMENTATION-PLAN path — the body takes both from its prompt and returns a failure without them. Pass **BRIEF** (`SDD/requirements/DESIGN-[###]-[feature-name].md`, with its approved revision and tier) for the review's `## Design Brief Check`, **TIERS** when the spec carries `tier:` (the body's *Respect the Tier* rule), **TEST_INTEGRITY**, and **FIT**. Pass `SCOPE = SLICE-XXX` and `ITER = N` — 0 after 4a, k after fix round k; the review writes its resume marker from them and must not infer either. Pass `BASE` — the `Base commit:` in the slice's latest `## Slice SLICE-XXX - In Progress` entry (never a snapshot, on any iteration); the slice is uncommitted during review, so the reviewer diffs the working tree against it. On a re-review whose fix round has both snapshots (4c, *The snapshots*), also pass `SNAPSHOT` and `FIXED` — that round's *before fix* and *after fix* SHAs — and `PREVIOUS REVIEW`, the review document of iteration N − 1 that the fix answered: the body then checks that review's findings and what the fix changed, runs only the tests that change can affect, and runs the whole suite and the trace check only when it would pass the slice — the trace check also when the previous review had a Tracing Lens finding; the eval check reads the run of record in full (`bodies/slice-review.md` → Step 4.5). Pass none of the three on any other review. The review document is `SDD/reviews/REVIEW-SLICE-SLICE-XXX-[feature-name]-iter<N>-[YYYY-MM-DD].md` — one per iteration, so a re-review never overwrites the review before it. When the spec's `agent_security:` gate is `true` or `auto`/absent, pass the resolved **CATALOG** path, the resolved gate value (`agent_security: true` or `agent_security: auto`), and the panel review `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md` so the body's Agentic-Surface Lens can run over the slice's file set and check it against the panel's `AI Agent Security Findings` and `Abuse cases to cover`.

**Tracing (4b).** Pass the **tracing inputs**. With `tracing: on` the body's Step 5.8 runs the application's trace run once the slice's tests pass, writes TRACE_TREE, and compares it with the marked nodes on this slice's `Traced nodes:` line and those of the slices before it — never a later slice's. Its findings are ordinary findings of the slice review, counted in the review marker like any other. On a re-review with `SNAPSHOT` the lens is deferred while the review has findings, and runs when it would pass the slice or when the previous review had a Tracing Lens finding (`bodies/slice-review.md` → Step 4.5). With `tracing: off` the body records that the lens was skipped.

**Evals (4b).** Pass the **evals inputs**. With `evals: on`, before every 4b review — the first and each re-review — the orchestrator makes **the eval run of record** (`phases/implementation-whole-feature.md`, top) at `SCOPE = SLICE-XXX` and the review's `ITER`, appends its `## Eval Run SLICE-XXX iter <N> - …` line, and passes the review the eval run line and EVAL_RESULTS. The run puts every case built so far to the application, so an earlier slice's case that this slice broke fails here. The body's Step 5.9 reads the run and the eval files against the cases on this slice's `Evals:` line and those of the slices before it; its findings are ordinary findings of the slice review, counted in the review marker like any other. With `evals: off` no run is made and the body records that the check was skipped. A run that ends `UNAVAILABLE` twice stops the flow on `## Awaiting Eval Run` before the review starts — the slice's fix-round cap is not touched by it.

### Per-slice 4c — Address per-slice findings
If the review left a HIGH or MEDIUM finding open, spawn an **`agent-engineering:sdd-workhorse`** fix subagent; it fixes those, under the scope-of-the-fix rule, and leaves the LOW findings listed. The slice goes on to 4c.5 when its latest review has no HIGH and no MEDIUM. The orchestrator tells from the review marker, without opening the review: `## Review SLICE-XXX iter <N> - APPROVED | REJECTED (h HIGH, m MEDIUM, l LOW)`, written by the review with all three counts (`N` is the `ITER` passed in its prompt). Standard fix-and-re-review with the **per-slice iteration cap (REQ-012):** max 2 iterations with progress-stall check — mirrors Step 3c's panel cap, Progress = HIGH strictly decreased, OR — when it was zero in the previous iteration — MEDIUM strictly decreased. **A HIGH the whole-suite run raised is set aside by the stall check.** A re-review after a snapshotted fix round runs the whole suite only when it would otherwise pass the slice (`bodies/slice-review.md` → Step 4.5), so a failure there was hidden from the reviews before it and says nothing about whether the fix loop is progressing. The review then writes `## Whole Suite SLICE-XXX iter <N> - <w> HIGH raised` as the line directly before its marker; for the stall check that review's HIGH is h − w. Only a `Whole Suite` line directly above the review marker counts — one anywhere else was left by an attempt at the review that did not finish, and is ignored. Its findings are fixed like any other, and the cap is unchanged. The cap counts the `## Fix SLICE-XXX iter <k>` lines after the slice's latest `In Progress` entry — and, once the slice has an `## Awaiting Slice Resolution` block after that entry, only those after the latest such block. Lines above the `In Progress` entry belong to an earlier run of that ID (a replaced plan's slice) and never count.

**One iteration k = snapshot → fix → snapshot → 4b re-review.** The fix subagent receives the review, the active spec, the IMPLEMENTATION-PLAN path, `BASE`, **TEST_INTEGRITY**, **FIT**, and the fix rules, and appends `## Fix SLICE-XXX iter <k> - Complete` to `progress.md` when done. These lines, the snapshot lines, and the review markers are the phase-detection markers for a resumed run.

**The snapshots.** A re-review reads what the fix changed, not the whole slice again; the snapshots are how it knows what that is. The orchestrator takes each by running, from the repository root:

```bash
python3 "$SKILL_ROOT/scripts/snapshot.py"
```

The command prints the SHA of a commit holding the working tree as it is — untracked files included, git-ignored ones left out — that no ref points to; it changes neither the index, HEAD, a branch, nor the stash, and the fix sees nothing of it. Two per iteration k:

1. **Before fix** — immediately before the fix spawn: append `## Snapshot SLICE-XXX iter <k> - before fix <sha>`.
2. **After fix** — immediately before the re-review of iteration k is spawned (after — evals on — the eval run of record): append `## Snapshot SLICE-XXX iter <k> - after fix <sha>`. Taken this late, it holds exactly the code the reviewer reads, whatever ran after the fix.

The *before fix* snapshot is taken once. When its line is already there after the slice's boundary (its latest `In Progress` entry, or the latest `## Awaiting Slice Resolution` after it), it is not taken again: a fix spawned again after a failure, or continued after a handoff, keeps the snapshot of its first attempt — a new one would hide what the first attempt changed. The *after fix* snapshot is taken again before every attempt at the re-review that starts from the beginning — a resumed session's, the second-model route's retry, its fallback to the Claude route — because a failed attempt may have left a change behind; the latest line is the one passed. Only a continuation after a handoff (`phases/protocols.md` → Mid-Phase Handoff) is given the one its first spawn had. **Before passing the pair, the orchestrator checks that git still has both** (`git cat-file -e <sha>^{commit}` for each). With the *before fix* line there, the re-review is passed both SHAs and the previous review (4b). **An iteration with no *before fix* line is reviewed in full** — the first iteration after an `## Awaiting Slice Resolution` block (the user's own changes were never snapshotted). So is an iteration whose snapshot git cannot find, or could not take — the check above fails, or a snapshot command fails: append `## Snapshot SLICE-XXX iter <k> - unusable (<the error, one line>)` and pass the review none of `SNAPSHOT`, `FIXED`, `PREVIOUS REVIEW`; that line is the latest for the iteration, so a resumed session does the same.

**On halt (cap exhausted or progress stall)** the flow stops — building later slices on unresolved findings compounds them. The slice does NOT proceed to 4c.5 or 4c.6, and no later slice starts. The orchestrator:

1. Spawns an **`agent-engineering:sdd-workhorse`** subagent with `bodies/slice-retro.md` and the line `MODE: halt-note`, passing `SLICE-XXX`, the active spec, the IMPLEMENTATION-PLAN path, the latest review, and the ledger path. It appends the unresolved findings to `LEARNINGS-FEATURE-[feature-name].md` under *Open recommendations awaiting user decision* and a short `## Slice SLICE-XXX - Halt Note Recorded` entry to `progress.md`, and writes nothing else — no retrospective, no table change. The orchestrator does not write the ledger itself.
2. Appends this halt block to `progress.md`, shows it, and stops:

```markdown
## Awaiting Slice Resolution

SLICE-XXX did not pass its review after <k> fix round(s) (<cap reached | no progress>). Unresolved: <h> HIGH, <m> MEDIUM.
Latest review: <REVIEW-SLICE path>
Resolve the findings (or amend the SPEC), then run `/sdd-flow continue` — the flow re-reviews the slice from a fresh iteration.
```

**On `/sdd-flow continue`** (`phases/protocols.md`): a 4b review in full — no snapshots — at one past the slice's highest `## Review SLICE-XXX iter <k>` line, with a fresh 2-round cap and a stall check that starts over from that review. Never resume from the halted iteration's review: the code or the spec has changed since.

**Tracing (4c).** The fix subagent is passed the **tracing inputs** — TRACE_TREE being the file written by the review it answers, or none when that review wrote none (a trace run that failed or could not be rendered) — and, with the gate on, the fix rule, the active spec (it holds the planned call graph the finding is about), and the IMPLEMENTATION-PLAN path (the fix rule lets it record a deviation there). Nothing else about the loop changes: the 4b re-review that follows a tracing finding runs the lens again, so that finding is re-checked after its fix, and the re-review that passes the slice always runs it — under this same cap, this same stall check, and this same stop.

**Evals (4c).** The fix subagent is passed the **evals inputs** — the eval run line and EVAL_RESULTS being those of the review it answers — and, with the gate on, the evals fix rule and the active spec (it holds the cases the finding is about). The 4b re-review that closes each round is given a fresh eval run of record, so an eval finding is re-checked on real answers after every fix, under this same cap, this same stall check, and this same stop.

### Per-slice 4c.5 — Slice retrospective (REQ-013)
Spawn an **`agent-engineering:sdd-workhorse`** subagent with `bodies/slice-retro.md` for `SLICE-XXX`, passing the active spec, the IMPLEMENTATION-PLAN path, and the slice's latest review document. It copies that review's LOW findings into the ledger's *Open recommendations awaiting user decision*. It writes `RETROSPECTIVE-SLICE-XXX-[feature-name]-YYYY-MM-DD.md` (audit trail; never modified after writing) and updates the rolling ledger in place.

**Read the retrospective — the file, never the subagent's return** (its return supplies the path; self-reports about its own sections have been wrong both ways). Both `## Recommended SPEC Amendments` and `## Recommended Re-planning` are required sections; a body whose first non-empty line is `None.` (case-insensitive, period optional) recommends nothing. Reference matcher:

```bash
# first non-empty line of the named section's body, or empty if the section is absent
section_body() {
  awk -v h="$2" '$0==h{f=1;next} f&&/^## /{exit} f&&NF{print;exit}' "$1"
}
BODY=$(section_body "$RETRO" '## Recommended Re-planning')
[ -z "$BODY" ] && echo "MALFORMED: section absent or empty"        # neither yes nor no
printf '%s\n' "$BODY" | grep -qiv '^none\.\?$' && echo "RE-PLANNING RECOMMENDED"
```

Apply the same test to `## Recommended SPEC Amendments`. A missing or empty section is a **malformed** retrospective, never read as "no recommendation". A body that begins with `None.` and goes on into prose counts as a recommendation — showing advice that was not meant costs one line at the pause; hiding advice that was meant costs a plan.

**Record the result.** Append `## Slice SLICE-XXX - Retro Matched (<none | amendments | re-planning | malformed>)` to `progress.md` — comma-separated when more than one applies. Nothing here stops: the re-plan advice and a malformed retrospective are shown at the slice pause, after the commit. A resumed session that finds `Retrospective Complete` with no later `Retro Matched` for the slice runs the matcher from the retrospective file before anything else.

### Per-slice 4c.6 — Per-slice commit
Reached only when the slice has a `Retro Matched` line. The **orchestrator**, in this order:

1. **Sets the slice's row to `Complete`** in the IMPLEMENTATION-PLAN's `## Slice Progress` table — its last edit before the commit, so the commit carries it. No body sets `Complete`, and the next slice's start refuses while another row is `In Progress` or `Acceptance Check Passing`.
2. **Runs the atomic per-slice commit** (commit conventions in `commands/commit.md`) covering: slice code + tests + the IMPLEMENTATION-PLAN + the slice's `TRACE-TREE-SLICE-XXX-*` (when the tracing gate is on) + every `EVAL-RESULTS-SLICE-XXX-*`, the `.json` files included (when the evals gate is on) + per-slice review doc + fix-findings notes + retrospective + ledger update — and, for the first slice after a re-plan, the 4a.0 archive and moves. Message references `SLICE-XXX` and `SPEC-XXX`; **no co-author attribution**.
3. **Appends `## Slice SLICE-XXX - Committed`** to `progress.md` — one line, the commit's SHA. It is the marker that the slice is finished. A resumed session that finds `Retro Matched` with no `Committed` line re-enters here; both steps are safe to repeat (the row is already `Complete`; with nothing left to commit, no commit is made and the line reads `already committed`).

If `progress.md` exceeds ~500 lines, rotate it now (`phases/protocols.md` → Progress Rotation).

### PAUSE (after every slice)
The flow always pauses after a slice's commit, so the user can try it. The pause is for trying the slice, not for reading its code — the reviews have done that. It writes no halt block — it needs no answer: a plain `/sdd-flow continue` starts the next slice, found from the `Committed` line. The message holds, in this order:

1. **Try it.** The slice's `Try it:` line from the spec's `## Delivery Slices` — what to run or do, and what you should see.
2. **Brief check.** Read the `## Design Brief Check` section of the slice's last review document — the file, not the subagent's return — and quote it as one line: `Brief check: delivers [outline entry]. Outside the approved footprint: [none | N file(s) — list]`. The review already raised each such file as a finding.
3. **Re-plan advice** — only when `Retro Matched` says `re-planning`: the first line of each entry under the retrospective's `## Recommended Re-planning`, with the retrospective's path, and `Say "re-plan" (with what you want changed) to revise the plan; otherwise continue.` When it says `malformed`: `The slice retrospective is malformed, so whether it advises a re-plan is unknown: <path>`. When it says `amendments`: `The retrospective suggests [N] spec change(s) — one line each — <path>. Say which to make, or continue.` A change the user asks for is a re-plan (below).
4. **Evals** (evals gate on only). The latest `## Eval Run SLICE-XXX iter <N> - ` line this slice has after its latest `In Progress` entry, as `Evals: <what follows the dash>`; when that run wrote results, add `Every run's score and output: <its EVAL_RESULTS path>` — the path the orchestrator built; it never opens the file. Information only: the pause accepts nothing (EVALS §9).
5. **Growth.** Run `python3 "$SKILL_ROOT/scripts/growth.py" --base <BASE> --brief <BRIEF>`, `BASE` = the `Base commit:` under `## Feature - Implementing`, and show its three lines as they print: the feature so far against the budget the user approved. The first line ends with tests per source line: a warning sign, never a limit — well above 1 often means tests sized to the code's shape rather than its behaviour (TEST_INTEGRITY §1, rules 4–6). On exit 3 (no budget in the brief) show `Growth: the brief has no growth budget`. Information only: the pause stops anyway, and the budget is checked for a stop once, before the final commit (4h).
6. **LOW findings** — only when the slice's last review marker has a LOW count above zero: `LOW findings, listed and not fixed: <l> — <that review's path>, under LOW Findings`. The orchestrator builds the line from the marker and the path; it does not open the review.
7. **Worth-building** (the plan's first slice only — the first `## Slice SLICE-XXX - Committed` after the latest `## Planning - Accepted`): `First slice done in [N] review round(s) — /worth-building recheck compares the plan with what this slice actually cost, before the next [M] slice(s) are built.` `N` is the slice's `## Review SLICE-XXX iter <k> - ` lines after its latest `In Progress` entry; `M` the slice-table rows not `Complete`. Omit when no slice remains. A reminder only; the orchestrator never runs the skill.
8. **Next:** the next slice in the queue.

**A re-plan, when the user asks for one** at the pause, in words: append `## Re-plan Requested` with the request verbatim to `progress.md`, then run Step 2.5's *Re-plan* (`phases/planning.md`) — the brief is revised, the design gate stops for approval, planning re-runs (3a–3g), and implementation resumes at 4a.0, which clears the replaced plan away.

---

## End-of-feature cycle (runs once after the last slice's 4c.6 lands — its `Committed` line is written and no later row is `Not Started`)

7. **End-of-feature 4d — Critical review across the assembled feature.** By the cycle's **review route** (`references/second-model-review.md`) — on the Claude route, an `agent-engineering:sdd-critical-reviewer` subagent — run `bodies/critical-review.md` (Implementation Phase section); reviews the whole assembled feature, not individual slices. Pass the IMPLEMENTATION-PLAN path, **TEST_INTEGRITY**, **FIT**, and `BASE` = the `Base commit:` under `## Feature - Implementing` (the body's Test Integrity Lens, by reading, and its Fit Lens, across every slice). Pass **TIERS** when the spec carries `tier:`.
8. **End-of-feature 4e — Address critical review findings.** Standard `agent-engineering:sdd-workhorse` fix subagent. It is passed the **tracing inputs** (no TRACE_TREE — the critical review ran no lens) and, with the gate on, the fix rule; and the **evals inputs** (no eval run line and no EVAL_RESULTS — the critical review read no eval run) and, with that gate on, the evals fix rule.
   - **End-of-feature 4e.5 — Final check (always runs).** *(Shared step — see `implementation-whole-feature.md` §4e.5.)* The security verification over the assembled feature — a later slice's path that an earlier slice's security rule must hold on included — the whole suite, and the last-look test checks; with `tracing: on` the Tracing Lens at `SCOPE = FEATURE`, the one comparison of the whole planned call graph with a single run; with `evals: on` the Eval Check on a run of record of every case of the feature. 4f does not start until it passes.
9. **End-of-feature 4f — Implementation completion subagent.** `bodies/implementation-complete.md` — finalize plan, write IMPLEMENTATION-SUMMARY, capture glossary deltas. *(Shared step — see `implementation-whole-feature.md` §4f.)*
10. **End-of-feature 4h — Commit checkpoint.** Stops only when a sign-off is asked for or the feature is over its growth budget. *(Shared — §4h, including its halt block, `## Awaiting Commit Approval`, and its sign-off part.)* The scores it shows are those of the final check's last run, not of any slice's. Its brief-check line, and 4j's report, is the per-slice form: collect each slice review's `## Design Brief Check` (`grep -A3 '^## Design Brief Check' SDD/reviews/REVIEW-SLICE-*-[feature-name]-*.md`) and report how many slices stayed inside the approved footprint, listing the exceptions.
11. **End-of-feature 4i — End-of-feature commit.** For a tiered spec, first run the in-review task mirror *(shared — §4i; it runs right after 4f and before any 4h stop)*. Covers: critical review doc, fix-findings code from 4e, the 4e.5 `FINAL-CHECK-FEATURE-*` / `TRACE-TREE-FEATURE-*` / `EVAL-RESULTS-FEATURE-*` files (the `.json` files included) and its fixes, completion artifacts from 4f. Per-slice code is already committed in each 4c.6. Then append `## Implementation - Committed` *(shared — §4i)*.
12. **End-of-feature 4j — Announcement.** *(Shared — §4j.)* Surface any ADRs. Append `## Feature - Done`. Then perform the **feature-completion rotation** per §4j (`phases/protocols.md` → Progress Rotation).
