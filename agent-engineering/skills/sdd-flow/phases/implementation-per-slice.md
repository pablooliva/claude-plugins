# Phase: Implementation — per-slice mode

Reached at Step 4 when the spec's `delivery_mode:` is `per-slice`. The whole-feature 4a–4j steps DO NOT run; the orchestrator iterates `SLICE-XXX` entries from the spec's `## Delivery Slices` section, executing the per-slice cycle for each in order, then runs the end-of-feature cycle once after the last slice lands.

Per-slice subagents carry the Safety-Net Rule + a fresh counter file (`Reads: 0/20` for the implement step and the blind site count, `Reads: 0/15` otherwise) + a compact body path (`site-count-compact.md` for the blind site count, `implementation-compact.md` for every other step). Body paths are `SKILL_ROOT/bodies/<file>.md`, resolved absolute. **STANDARD** = `SKILL_ROOT/references/enforcement-sites.md` (resolved absolute) is passed to the implement, site-count, review, fix, and retro spawns — it defines control, enforcement site, the per-site mutation standard, the three dispositions, and the inventory shape.

---

## Slice-boundary checkpoint axis (REQ-024)

A **separate axis** from the supervised/autonomous (phase-boundary) axis. Default `on` in per-slice mode in BOTH modes — without this default, opting into per-slice would degrade into "more internal gates with no human review," defeating the reason to opt in. Suppressed via `--skip-slice-checkpoints`.

| Phase-boundary | Slice-boundary | Behavior |
|---|---|---|
| supervised | on | Pauses at research-end + each completed slice + impl-end |
| supervised | off | Pauses at research-end + impl-end; slices run continuously inside |
| **autonomous** | **on** (default) | Research + planning autonomous; pause between each fully-completed slice; end-of-feature autonomous through commit |
| autonomous | off (via `--skip-slice-checkpoints`) | Fully autonomous start-to-finish |

---

## Per-slice 4a.0 — Scaffold the implementation tracker (once per feature)

Before the first slice, check whether `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md` already exists with a `## Slice Progress` table (it will, when resuming). If absent, spawn ONE **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/implementation.md` — its `per-slice` branch is **scaffold-only**: create the tracker with the `## Slice Progress` table populated from the spec's `## Delivery Slices` (all rows `Not Started`), then return without implementing anything.
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `progress.md`.
- **Output:** the IMPLEMENTATION-PLAN tracker; append `progress.md`.

After a `--replan`, re-run this step with a post-replan note in the prompt — the orchestrator archives the old table under `## Archived Slice Progress (pre-replan)` first (see `phases/protocols.md`), and the subagent writes a FRESH table from the revised spec. Without this scaffold, `bodies/slice-start.md` halts per FAIL-007 (missing `## Slice Progress` table).

---

## Per-slice cycle (runs once per `SLICE-XXX`, in order)

### Per-slice 4a — Implement slice
Spawn ONE **`agent-engineering:sdd-workhorse`** subagent (strict — no bundling):
- **Body:** `bodies/slice-start.md` (for `SLICE-XXX`).
- **Inputs:** the active spec, the rolling ledger `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md`, the IMPLEMENTATION-PLAN path, and **STANDARD**. **The prompt receives ONLY the ledger** (per OQ-6 — individual retrospectives are out of the prompt path).
- **Outputs:** slice code + tests; the living site inventory `SDD/implementation/sites/SITES-IMPL-[feature-name].md` (rows for every site of every control the slice touches, each with a disposition and per-site mutation evidence); a `## Slice SLICE-XXX - Implemented` entry in `progress.md`.
- **Task:** Implement the slice end-to-end and record its enforcement sites (body Steps 10–12). Bounded return: "Slice X delivered. Acceptance check `<test name>` passes."

### Per-slice 4a.5 — Blind site count + diff (iteration N)

Runs after 4a (as `iter0`) and again after every 4c fix iteration k (as `iter<k>`). **It exists because an implementer's site list shares the implementer's blind spots** — every under-count in the motivating project was found by someone reading the code fresh, never by the implementer checking its own list.

**Spawn** ONE fresh **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/site-count.md`. **Compact body:** `bodies/site-count-compact.md`. **Counter:** `SDD/orchestration/counters/4a5-SLICE-XXX-iter<N>-[timestamp].md` with `Reads: 0/20`. Embed the Safety-Net Rule verbatim.
- **Inputs — the allowlist, and nothing else:** the SPEC path, `SDD/UBIQUITOUS_LANGUAGE.md` (if present), **STANDARD**, `SCOPE = SLICE-XXX`, `ITER = N`, the slice's `Modules touched`, `BASE` = the commit HEAD pointed at when this slice started (the slice's work is uncommitted until 4c.6, so the counter diffs the working tree against `BASE` and lists untracked files — never `BASE..HEAD`), and — only on a recount whose previous review recorded one — the `ALSO INVENTORY` SPEC IDs (IDs only).
- **Output:** `SDD/reviews/SITE-COUNT-SLICE-XXX-[feature-name]-iter<N>-[YYYY-MM-DD].md`; appends `## Site Count SLICE-XXX iter <N> - Complete`.
- **Blindness is enforced by this prompt.** NEVER put in it: the implementer's inventory path or contents, the IMPLEMENTATION-PLAN, `progress.md` excerpts, the implementer's bounded return, earlier `SITE-COUNT-*`/`SITE-DIFF-*`/review paths, or any count. A fresh spawn per iteration — never a continuation of an earlier count. Using `sdd-workhorse` is still independent: the counter shares the implementer's model but not its context or its claims, which is the independence that caught every historical miss (the per-slice reviewers who found them were also `sdd-workhorse`).
- If the counter appends `## Site Count SLICE-XXX iter <N> - BREACHED` (or the output's first line says `BLINDNESS BREACHED`), discard that output and re-spawn a fresh counter for the same iteration (counts toward Error Handling's two-failure limit).

**Diff (orchestrator, mechanical):**

```bash
python3 "$SKILL_ROOT/scripts/site-diff.py" \
  SDD/implementation/sites/SITES-IMPL-[feature-name].md \
  SDD/reviews/SITE-COUNT-SLICE-XXX-[feature-name]-iter<N>-[YYYY-MM-DD].md \
  SDD/reviews/SITE-DIFF-SLICE-XXX-[feature-name]-iter<N>-[YYYY-MM-DD].md \
  --scope SLICE-XXX
```

Exit 0 = `MATCH`, 1 = `MISMATCH`, 2 = input error (missing/malformed inventory — treat as a failed implement or count step and re-spawn it). The script's first stdout line is the `Result:` line. Append to `progress.md`:

```markdown
## Site Diff SLICE-XXX iter <N> - <MATCH | MISMATCH (h HIGH, m MEDIUM)>

- **Diff:** SDD/reviews/SITE-DIFF-SLICE-XXX-[feature-name]-iter<N>-[YYYY-MM-DD].md
```

The orchestrator does not interpret the diff further: every outcome goes to 4b, which turns it into findings. A mismatch is a finding inside the existing review/fix loop — never a separate loop.

### Per-slice 4b — Per-slice code review
Spawn an **`agent-engineering:sdd-workhorse`** subagent with `bodies/slice-review.md` for `SLICE-XXX`. **Mandatory per slice** — not deferred to end-of-feature. Writes `SDD/reviews/REVIEW-SLICE-*`. Pass **STANDARD**, the site inventory, and the latest iteration's `SITE-COUNT` and `SITE-DIFF` paths — the body's Step 5.6 carries every diff finding into the review, resolves `EXTRA` sites by re-running their mutations, re-runs a mutation sample, and verifies dispositions (ii)/(iii) are argued. When the spec's `agent_security:` gate is `true` or `auto`/absent, pass the resolved **CATALOG** path so the body's Agentic-Surface Lens can run over the slice's file set.

### Per-slice 4c — Address per-slice findings
If the review found anything HIGH or MEDIUM, spawn an **`agent-engineering:sdd-workhorse`** fix subagent. Standard fix-and-re-review with the **per-slice iteration cap (REQ-012):** max 3 iterations with progress-stall check (HIGH must strictly decrease, OR MEDIUM when HIGH is zero) — mirrors Step 3c's panel cap exactly.

**One iteration k = fix → 4a.5 recount (`iter<k>`) → diff → 4b re-review.** The fix subagent appends `## Fix SLICE-XXX iter <k> - Complete` to `progress.md` when done; each review appends `## Review SLICE-XXX iter <N> - APPROVED | REJECTED (h HIGH, m MEDIUM)` (pass `ITER` in its prompt). These, with the `Site Count` / `Site Diff` lines, are the phase-detection markers for a resumed run. The fix subagent receives **STANDARD**, the review, and the inventory; for every site-count finding it adds the missing site(s) to `SITES-IMPL-[feature-name].md` with a disposition, a fresh per-site mutation, and `Slice` = this SLICE-XXX; deletes rows for sites its fix removed; fixes or implements any `GAP`, and never deletes a (ii)/(iii) site as dead code. The recount is a fresh blind spawn (its prompt carries no earlier count, diff, or review) — fixes add sites, so a stale count would miss them. Site-count findings are ordinary review findings, so the progress-stall check counts them with everything else; the cap is unchanged.

**On halt (cap exhausted or progress stall):**
- The slice does NOT proceed to 4c.5 or 4c.6.
- Append the unresolved findings to `LEARNINGS-FEATURE-[feature-name].md` under *Open recommendations awaiting user decision*.
- In any mode with slice-checkpoints `on`, surface the halt in the next pause message and do not advance to the next slice without user direction.
- In `autonomous + --skip-slice-checkpoints` mode, **halt the entire flow** — analogous to the panel-review halt, since compounding unresolved findings across subsequent slices is too high a risk.

### Per-slice 4c.5 — Slice retrospective (REQ-013)
Spawn an **`agent-engineering:sdd-workhorse`** subagent with `bodies/slice-retro.md` for `SLICE-XXX`, passing **STANDARD** and every `SITE-DIFF-SLICE-XXX-*` path for this slice. It records count mismatches in the retro's `## Site Count Reconciliation` section and the ledger's `Enforcement-site count mismatches` section, and updates the IMPLEMENTATION-PLAN's `## Control Site Status` rows. It writes `RETROSPECTIVE-SLICE-XXX-[feature-name]-YYYY-MM-DD.md` (audit trail; never modified after writing) and updates the rolling ledger in place.

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

Header-match outcomes:
- `^## Recommended SPEC Amendments$` with a non-`None.` body → routine amendment recommendation; surface it in the slice-boundary pause as a per-recommendation summary (one or two lines per affected `SLICE-XXX`/`MODULE-XXX`/`REQ-XXX` — what should change, why), with the retrospective path for the user to read full wording. No halt block written.
- `^## Recommended Re-planning$` **whose first non-empty body line is not `None.`** → elevated severity. Per **REQ-014**, this HALTS the flow even under `--skip-slice-checkpoints`. The header alone does NOT halt — the body contract above permits `None.` as the declared no-re-plan shape, so halting on bare presence is a false positive. On match, the **orchestrator** writes this halt block to `SDD/orchestration/progress.md`:

```markdown
## Awaiting Re-planning Decision

SLICE-XXX retrospective recommends re-planning. Resume options:
- `/sdd-flow continue --replan` — re-run Step 3 (planning) with the rolling ledger and triggering retro in scope; resumes implementation from SLICE-001.
- `/sdd-flow continue --replan --from-slice SLICE-XXX` — same, but resume from a user-specified slice (must match `^SLICE-\d{3}$` AND reference an existing SLICE-XXX in the new plan's `## Slice Progress` per REQ-025).
- `/sdd-flow continue --override-replan` — continue with the current plan despite the recommendation. Documented but discouraged.

This halt fires even under `--skip-slice-checkpoints` (mirrors the Step 3c panel-review halt).

Triggering retrospective: <retro-path>
```

The pause message uses the re-planning-specific shape:
> **Re-planning recommended.** The slice retrospective has determined the original plan is no longer fit. The flow is halted to await your direction.
> Resume options:
>   1. `/sdd-flow continue --replan` — re-run Step 3 with the ledger + triggering retro; produces a revised SPEC; resumes implementation from `SLICE-001` (or a user-specified slice).
>   2. Edit the SPEC manually, then `/sdd-flow continue`.
>   3. `/sdd-flow continue --override-replan` — explicit override; continue on the current plan.
> See `<retro-path>` for the full rationale.

**In autonomous + --skip-slice-checkpoints mode this halt fires regardless** — compounding subagent runs on a known-broken plan is the higher-cost failure.

**Stage 2 — Resumption-stage match** (Phase Detection on `/sdd-flow continue` from a fresh session) reads `progress.md` for `## Awaiting Re-planning Decision` (the orchestrator-written block, NOT the retro-body header). See `phases/protocols.md` → Phase Detection Priority.

### Per-slice 4c.6 — Per-slice commit
The **orchestrator** runs the atomic per-slice commit (commit conventions in `commands/commit.md`) covering: slice code + tests + site inventory + every `SITE-COUNT-SLICE-XXX-*` / `SITE-DIFF-SLICE-XXX-*` + per-slice review doc + fix-findings notes + retrospective + ledger update. Message references `SLICE-XXX` and `SPEC-XXX`; **no co-author attribution**.

If `progress.md` exceeds ~500 lines, rotate it now (`phases/protocols.md` → Progress Rotation).

### PAUSE (slice-boundary)
Fires when slice-boundary checkpoints are `on`. The pause message includes: slice X completed + brief summary of what landed; acceptance-check status; any matched recommendations (SPEC amendments and/or re-planning) per the matcher; the next slice in queue. Resume via `/sdd-flow continue` (advances to next slice), or a re-planning resume option if re-planning was matched.

When checkpoints are `off` (`--skip-slice-checkpoints`), this pause is skipped — **except** the re-planning halt above, which fires regardless.

---

## End-of-feature cycle (runs once after the last slice's 4c.6 lands)

7. **End-of-feature 4d — Critical review across the assembled feature.** Spawn an `agent-engineering:sdd-critical-reviewer` subagent with `bodies/critical-review.md` (Implementation Phase section); reviews the whole assembled feature, not individual slices.
8. **End-of-feature 4e — Address critical review findings.** Standard `agent-engineering:sdd-workhorse` fix subagent.
   - **End-of-feature 4e.5 — Final blind recount (always runs).** Feature-wide (`SCOPE = FEATURE`) blind count + diff + site-verification loop. *(Shared step — see `implementation-whole-feature.md` §4e.5.)* Catches sites that span slices (a later slice's path needing an earlier slice's control) and sites changed by 4e. 4f does not start until it resolves.
9. **End-of-feature 4f — Implementation completion subagent.** `bodies/implementation-complete.md` — finalize plan, write IMPLEMENTATION-SUMMARY, capture glossary deltas. *(Shared step — see `implementation-whole-feature.md` §4f.)*
10. **End-of-feature 4g — Eval scaffolding.** Conditional on `eval_required:` **or** an open `agent_security:` gate (abuse-case-only mode when just the latter). *(Shared — §4g.)* Uncovered abuse cases flagged in the per-slice reviews carry forward here.
11. **End-of-feature 4h — Supervised checkpoint.** Fires only in supervised phase-boundary mode. *(Shared — §4h.)*
12. **End-of-feature 4i — End-of-feature commit.** Covers: critical review doc, fix-findings code from 4e, the 4e.5 `SITE-COUNT-FEATURE-*` / `SITE-DIFF-FEATURE-*` / `REVIEW-SITES-FEATURE-*` files and inventory updates, completion artifacts from 4f, eval scaffolding from 4g. Per-slice code is already committed in each 4c.6.
13. **End-of-feature 4j — Announcement.** *(Shared — §4j.)* Surface eval scaffold result and any ADRs. Then perform the **feature-completion rotation** per §4j (`phases/protocols.md` → Progress Rotation).

---

## EDGE-006 — plain `continue` while a re-planning recommendation is pending

If `/sdd-flow continue` is invoked **without a flag** while an `## Awaiting Re-planning Decision` block is the pending halt in `progress.md` (no resume-flag block following it), the orchestrator emits an informative refusal naming the three options (`--replan`, manual edit + plain `continue`, `--override-replan`) and exits. **No work is performed.** (Full resumption routing is in `phases/protocols.md`.)
