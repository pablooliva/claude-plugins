# agent-engineering

Cross-cutting skills and commands for disciplined AI-assisted software development, based on the [10 Claude Code Principles](https://jdforsythe.github.io/10-principles/) by JD Forsythe. Every skill and command here is independently usable in any session.

## Philosophy

This plugin provides the *agent-engineering discipline* that operates across any methodology — feedback loops, institutional memory, specialist review, token economy, and observability. Its flagship is `sdd-flow`: a self-contained, end-to-end Specification-Driven Development orchestrator that drives a feature from Research → Planning → Implementation → Done through subagents with a fresh context window per phase.

## Self-contained as of 1.0.0

`sdd-flow` is a **permanent fork** of the SDD plugin's content, adapted for orchestrated (subagent-driven) execution. It is the **single source of truth for the flow** and depends on nothing outside this plugin at runtime:

- **Phase bodies** — the complete instruction set each spawned subagent reads lives under `skills/sdd-flow/bodies/` (one file per phase/review/capture step). The orchestrator passes each body **by absolute path** ("read this first"); it never pastes body content into a prompt and never reads from the SDD plugin's cache.
- **Agents** — the ten routed subagent types ship in `agents/` (`sdd-workhorse` at Sonnet, the eight `sdd-spec-*-specialist` agents at Sonnet, `sdd-critical-reviewer` at Opus). Model routing is carried entirely by agent frontmatter — no runtime model switching.
- **Hook** — `hooks/log_subagent_call.py` logs subagent transcripts via a `SubagentStop` hook registered in this plugin's `plugin.json`.

**The SDD plugin is no longer required and need not be installed.** The SDD plugin remains frozen at 2.2.0 as a standalone, human-driven methodology for its external users; this fork diverges from it deliberately so each can evolve independently. Nothing in `sdd-flow` references `/sdd:` commands or the SDD plugin cache.

### Why a permanent fork (rather than depending on SDD)

Before 1.0.0, `sdd-flow` embedded SDD command bodies at runtime and relied on SDD's shipped agents. That coupling meant a version skew between the two plugins could silently misbehave, and the orchestrated path could not diverge from the interactive SDD commands even where orchestration demanded it (e.g., a subagent cannot spawn or invoke slash commands, so "delegate to an Explore subagent" instructions had to become inline work). Forking permanently removes the dependency, lets the flow own its own evolution, and lets the SDD plugin stay stable for the people who use it directly.

### Architecture (1.0.0)

- **One-level spawning.** Every spawn happens at the orchestrator (main-conversation) level; spawned subagents must not spawn subagents and must not invoke slash commands or skills. Every body is pre-adapted for inline execution. *(Was a platform limit on Claude Code ≤2.1.171; since 2.1.172 the platform allows nesting to depth 5 — the flat design is retained deliberately. See `proposals/nested-subagents-analysis-2026-06-12.md` before refactoring toward nesting.)*
- **Two-stage specialist panel.** During planning, the orchestrator spawns one specialist subagent per `review_panel:` value in parallel (Stage 1; each writes a `PANEL-FINDINGS-*` file), then one `sdd-critical-reviewer` synthesis subagent reads those files from disk and emits the verdict (Stage 2). The bounded fix-and-re-review loop (max 3 iterations, progress-stall halt) is unchanged.
- **Reads-only safety net.** Spawned subagents do not spawn in this flow, so there is no nested-subagent counter — the only safety-net signal is file Reads (default trigger >15; >20 for implementation chunks). On trip, the subagent compacts and hands off.
- **Per-slice authoring default.** The planning body sets `delivery_mode: per-slice` unless the feature yields fewer than 2 genuine vertical slices (then `whole-feature` with a one-line justification). The PARSE default (frontmatter absent → whole-feature) is unchanged for backward compatibility.
- **Gated AI-agent security review (2.1.0).** Spec frontmatter `agent_security: auto|true|false` gates three hook points: the `agent-security` panel value at Step 3c (spec-level checks), the Agentic-Surface Lens in the Step 4b / per-slice code review (code-level checks), and abuse-case seeding at Step 4g eval capture. `auto` resolves by detecting an agentic surface — a model call, a tool/MCP definition, agent memory or a retrieval store, inter-agent messaging, or a model output driving an external action.
- **Progressive disclosure.** `SKILL.md` is a slim orchestrator core; per-phase detail lives in `skills/sdd-flow/phases/` (`setup`, `research`, `planning`, `implementation-whole-feature`, `implementation-per-slice`, `protocols`), read at each phase boundary.

## Contents

### Skills

- **`sdd-flow`** — Self-contained end-to-end SDD lifecycle orchestration (see above).
- **`correction-codifier`** — When you correct Claude's behavior mid-session, proposes a durable `Always|Never [X] BECAUSE [Y]` rule and appends it to the project's `CLAUDE.md`. Operationalizes Principle 5 (Institutional Memory).
- **`cross-cutting-adr`** — Captures cross-cutting architectural decisions as numbered ADRs under `SDD/adr/`. Triggers on comparison-with-selection patterns, explicit invocation, or ambient detection. Operationalizes Principle 3 (Living Documentation).
- **`improve-claude-md`** — Audits `CLAUDE.md`/`AGENTS.md` and `CLAUDE.local.md` to strip discoverable content and concentrate on preferences, behavioral nudges, and corrections. Mirrored from [pablooliva/claude-skills](https://github.com/pablooliva/claude-skills).
- **`ai-agent-security-review`** — Adversarial security review of **agentic** systems against the OWASP AI Agent Security Cheat Sheet (tool least-privilege, prompt-injection defense, memory/context security, human-in-the-loop for high-impact actions, output guardrails, monitoring, multi-agent trust, data protection, adversarial validation). Runs standalone on a spec, research doc, diff, or codebase; the same vendored control catalog (`skills/ai-agent-security-review/references/owasp-ai-agent-controls.md`) is what `sdd-flow` consumes at its three gated hook points. Distinct from classical appsec, which stays with the `security` panel value and `/critical-review`.
- **`worktree-create`** — Creates an isolated git worktree at a sibling path (`../<project>-WT/<you>/<type>-<desc>`) on its own branch, provisions the untracked runtime config git never checks out per the repo's `.worktreeinclude` + `.env-setup.sh` contract, reserves collision-free SDD ADR/SPEC numbers across every live worktree and branch, and writes a `WORKTREE.md` breadcrumb. Both `.worktreeinclude` and an env-setup script are hard requirements — it stops before creating anything if either is missing.
- **`bb-worktree-init`** — One-time, per repo: makes a new or existing project ready for BB IDE and `worktree-create` worktrees. Inspects untracked config, env keys (names and value shapes only — never values), lockfiles, and local databases; proposes a plan for approval; renders bundled templates into `.worktreeinclude`, `.env-setup.sh`, a `.bb-env-setup.sh` symlink, and (only when needed) `.bb-env-teardown.sh`; then validates statically and, on approval, in a throwaway worktree. In a repo that already has the files it proposes edits instead. Does not commit.
- **`worktree-handoff`** — Closes the loop on a `worktree-create` worktree. Context-aware: from inside the worktree it writes `HANDOFF.md` and a paste-ready merge request; from the main repo it merges the branch, settles the worktree's `.env*` files, and removes the worktree and branch with confirmation before each destructive step.
- **`prompt-doctor`** — Diagnoses a task prompt *before* you send it to an agent, against a ten-component anatomy (grounding link, stakes, priorities, ranked priorities, hard constraints, marked-negotiable opinion, knowledge-gap disclosure, the one clear ask, early-exit permission, precise done-condition). Grades each Present/Weak/Missing/N-A with quoted evidence, names what each gap lets the model decide for itself, and asks you for the facts only you hold. Never executes the prompt under review and never invents stakes or constraints; the rewrite is opt-in and keeps unanswered slots as visible placeholders. Anatomy from Theo (T3.gg) plus Goedecke's ranked priorities and hard constraints.
- **`todo-tidy`** — Promotes a free-form `scratch.md` working list into a structured `TODO.md` (renaming, or folding both together when both exist) and reorganizes the contents into a consistent, hierarchical checkbox list. Reformats only — it never acts on an item, drops content, or edits `.gitignore` (it checks and warns).

### Commands

These are **interactive commands you run yourself** (depth 0, so they may delegate to subagents):

- **`/adr-capture`** — Manual entry point for the `cross-cutting-adr` skill.
- **`/prompt-doctor`** — Manual entry point for the `prompt-doctor` skill. Takes a pasted prompt, a file path, or the last draft in the conversation.
- **`/regression-eval-capture`** — After a feature ships, scaffolds a LangSmith regression eval dataset. Operationalizes Principle 7 (Observability). Requires the `langsmith` CLI.
- **`/research-clarify`** — Structured interview that externalizes your design concept before any codebase research. Satisfies the `sdd-flow` Step 1.5 clarification gate.
- **`/critical-review`** — Standalone adversarial review of a research doc, spec, or implementation.
- **`/continue`** — Resume an interrupted SDD session from `progress.md`.
- **`/adhoc-compact`** — Generic mid-phase compaction, for ad-hoc or follow-up work. Detects an active SDD phase and redirects to the phase-specific command below.
- **`/research-compact`**, **`/planning-compact`**, **`/implementation-compact`** — Phase-specific compaction. Thin wrappers that read `sdd-flow`'s own compaction bodies (`skills/sdd-flow/bodies/<phase>-compact.md`) and run them interactively, so a manual compaction produces the same artifact an orchestrated run would — no second copy of the templates to drift.
- **`/commit`** — Commit conventions (no co-author attribution), including atomic per-slice commits.

## Coexisting with the SDD plugin

The SDD plugin is **optional and uninstallable** — `sdd-flow` does not need it. If you keep both installed:

- **Command-name disambiguation.** Several command names exist in both plugins (`/critical-review`, `/continue`, `/commit`, `/adhoc-compact`, `/research-clarify`, `/research-compact`, `/planning-compact`, `/implementation-compact`). Claude Code may require the `/agent-engineering:` prefix (e.g. `/agent-engineering:critical-review`) to pick this plugin's copy.
- **Duplicate transcript logs.** Both plugins register a `SubagentStop` hook pointing at their own `log_subagent_call.py`. With both installed, each subagent stop is logged twice — harmless, just duplicate transcript entries.

## Other dependencies

- **`langsmith` CLI** — required by `/regression-eval-capture` and by `sdd-flow`'s eval-capture step (non-blocking: if absent, the flow logs a warning and continues). Install: `curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh`.

## Status

Version 2.7.0.

### What's new in 2.7.0

The blind site count kept finding every real miss, but the diff around it was mostly noise. A project running per-slice `sdd-flow` (SPEC-024, eight slices) saw one slice's diff report **23 HIGH, of which 0 needed a fix**, and the next **6 HIGH, 0 needing a fix**. Reviewers spent every iteration sorting findings by hand, and orchestrators edited artifacts to get the script to run at all. 2.7.0 makes a HIGH from the diff mean a real miss again, without giving the counter any more information about the implementer's list.

- **Disagreements on code the slice did not change are LOW, not HIGH (items 3–4).** `site-diff.py` takes a new optional `--base <commit>` at `SLICE-XXX` scope (the per-slice phase always passes it). The script itself checks git to decide which sites the slice changed — by file, and by function span for Python — and applies that same test to both inventories, so neither side's labels can move a site out of comparison. A disagreement on unchanged code is listed under `## Carried`, is not a finding for the slice, and leaves the control `Partial` until the feature-wide recount (4e.5), which always runs and compares every row. Anything the script cannot place with certainty (a file new since the base, including git-ignored ones, a missing file, `<module>` in a changed file, a non-Python changed file) is compared as the slice's own. Declined as proposed: an `Owner` column filled in by each side. The blind counter cannot name an owning slice without reading material it is barred from, and a filter trusting the implementer's `Slice` cell would drop real sites whenever that cell was stale.
- **Declared partial scope (item 3).** A blind count that deliberately counted a control over only part of the code declares that in a machine-readable `## Declared Scope` table. At slice scope, implementer rows outside that scope are set aside as `OUT-OF-SCOPE-BY-DECLARED-SCOPE`: LOW when the code is unchanged, MEDIUM when the slice changed it (the counter skipped code it was responsible for). At `FEATURE` scope a declaration is itself a MEDIUM finding and the comparison stays complete.
- **Escaped symbols key correctly (item 5).** The diff strips Markdown backslash-escapes and wrapping backticks from Control, File, and Symbol, so `\<module\>` and `<module>` are the same site. The counter is also told to write them plain.
- **Lettered slice IDs (item 6).** `SLICE-005a` is valid everywhere: the diff's `--scope`, and the path-traversal guard in `slice-start`, `slice-review`, `slice-retro`, `protocols`, and the per-slice phase (`^SLICE-\d{3}[a-z]?$`). The planning body says a letter is only for a slice split during re-planning.
- **The stall check counts only HIGH that need code (item 2).** Reviews tag each site-count HIGH `[row-only]` (the reviewer re-ran the missed site's mutation and a test failed, so only an inventory row is missing) or `[needs-code-or-test]`. The review marker reports the row-only count (`REJECTED (h HIGH [r row-only], m MEDIUM)`; markers without the bracket read as 0). The fix loop's progress-stall check applies to needs-code-or-test HIGH, so a recount that finds more already-tested sites no longer halts the loop. Row-only HIGH still block approval, and the 3-iteration cap is unchanged.
- **One shared, count-free filing-conventions file (item 1).** New `SDD/implementation/sites/SITE-CONVENTIONS-[feature-name].md`: reviewers append rulings on how sites are keyed and filed ("a registry declaration read by a statement is data; file the site at the reading statement"). The implementer, fixers, and every blind count read it, so both sides file the same site the same way. The standard forbids site counts, site rows, site locations, control lists, and scope rules in it, and the reviewers' leak check enforces that. Declined as proposed: sending the recount a settled list of in-scope controls. That would narrow what the counter looks for, and the counter must decide its own scope.
- **No totals in `progress.md` (item 7).** The counter's `progress.md` template itself asked for `**Controls in scope:** n; **sites:** n; **gaps:** n`. That line is gone; the counter appends the marker with one exact `printf` and nothing else. The totals remain in the count file's header, which later counters may not read.
- **Tests.** `skills/sdd-flow/scripts/tests/test_site_diff.py` (22 cases, stdlib `unittest`, temporary git repos). Worked example, a SLICE-005a-shaped input with an escaped `\<module\>`, carried disagreements, and one declared partial scope: 2.6.1 (run with the scope relabelled `SLICE-995`, as orchestrators had to do) reported `MISMATCH (3 HIGH, 2 MEDIUM)`; 2.7.0 reports `MATCH (3 LOW carried or out-of-scope, owed to the FEATURE recount)`. Add one genuinely missed site in code the slice changed: 2.6.1 reports 4 HIGH, 2.7.0 exactly 1 HIGH.
- **Compatible.** Existing `SITES-IMPL-*` and `SITE-COUNT-*` files parse unchanged: no column was added. Without `--base` the diff behaves as in 2.6.1, apart from the escape normalisation, and a count whose only issue for a control is a gap now reads `GAP` for that control instead of also raising a second HIGH "MISSED control".

### What's new in 2.6.1

- **Per-slice review now sees the slice's changes.** `bodies/slice-review.md` computed the slice's changed files with `git diff <slice-start-commit>..HEAD`, but a slice is committed only after its review, fixes, and retro — so during review that range compared two identical commits and was always empty (and `git diff` never lists new, untracked files anyway). The reviewer now diffs the working tree against the slice's base commit (excluding `SDD/`, with renames split into old and new paths), lists untracked files and reviews them in full, and prefers this git list over the SPEC's module list when they disagree.
- **Each slice records its base commit.** `slice-start` writes a `Base commit:` line into its `In Progress` progress entry. The review and the blind site count read it from there, so a resumed session never guesses the base from HEAD, which may already contain the slice.

### What's new in 2.6.0

`sdd-flow` no longer takes the implementer's word that a control is closed. Before 2.6.0 the skill had no concept of enforcement sites or mutation evidence at all.

**Why.** A project running `sdd-flow` (SPEC-024, 2026-09-20/21) had to write its own rule into its spec because it kept shipping controls whose tests could not fail: *every control ships with a test that drives the real entry point with the adverse precondition present, plus a per-site mutation check — delete one enforcement site, confirm a test fails, restore.* The rule worked, but only on the sites someone listed, and the list was always the implementer's. Across four slices the implementers under-counted every time:

| Control | Implementer recorded | Actually present | Found by |
|---|---|---|---|
| D-10 stdout line-1 rule | 1 → 3 → 17 → 23 (over 3 fix passes) | ≥ 26 | each successive reviewer |
| REQ-018 unchanged-skip filter | 3 | 4 (missing one: full unit suite stayed green when it was deleted) | reviewer |
| SEC-003 URL safety check | "proven" via one mutation of a shared loop | 2 (final-URL site deletable with all 1,303 tests green) | reviewer |
| SEC-002 neutralisation | 2 | 3 | reviewer |

Twice a control was recorded closed while still broken. Every miss was found by a reviewer reading the code fresh; none by the implementer checking its own list. Two slices were rejected for it and one burned the full 3-iteration fix cap. The implementer's list comes from memory of what it just built, so it shares the implementer's blind spots. The fix is structural, not a reminder to count harder.

**What changed.**

- **The standard is in the skill.** New `skills/sdd-flow/references/enforcement-sites.md` defines *control* (any rule the spec says must hold on every path — guards, refusals, write controls, output contracts, invariants, security controls; not only `SEC-xxx`), *enforcement site*, *gap*, the per-site mutation standard, the three site dispositions — (i) proven by its own mutation, (ii) not provable alone with the argument written at the site, (iii) not proven and kept with a named owner — and the inventory table both sides write.
- **Implementers record sites.** `slice-start.md` and `implementation.md` write a per-feature inventory (`SDD/implementation/sites/SITES-IMPL-*.md`) with a disposition and mutation evidence per site, and must not leak counts into code comments or `progress.md`.
- **A blind count runs before any control can be Complete.** New step **4a.5** (`bodies/site-count.md`): a fresh `sdd-workhorse` spawn inventories sites from the SPEC and production code only, under a read allowlist that excludes the implementer's inventory, the plan, `progress.md`, tests, and earlier counts. It runs after each slice's implementation and after every fix iteration; in whole-feature mode after implementation. A new always-on **4e.5** recounts feature-wide before completion.
- **The orchestrator diffs mechanically.** New `scripts/site-diff.py` compares counts per control, file, and function and reports `MATCH`, `MISSED` (HIGH), `EXTRA` (MEDIUM, confirmed or rejected by the reviewer re-running the mutation), `UNCOUNTED`, and blind-found gaps (HIGH). Mismatches become ordinary review findings inside the existing fix loop — the per-slice cap and stall check are unchanged.
- **Reviews verify the evidence.** `slice-review.md` and `code-review.md` re-run a sample of mutations, check (ii)/(iii) are argued rather than asserted, and require a real-subprocess test per exit-path class for stdout/stderr contracts (`CliRunner` hid a `click.confirm(err=True)` writing to stdout).
- **Uncounted means Partial.** A new `## Control Site Status` table in the implementation plan; a control with no independent count stays `Partial`, and completion refuses while any control is `Partial`.
- **Retros learn the pattern.** `slice-retro.md` records count mismatches in a `## Site Count Reconciliation` section and a new ledger section, so the next slice's implementer sees which kinds of site get missed.
- **Resumable.** New `progress.md` markers (`Implemented`, `Site Count`, `Site Diff`, `Review`, `Fix`, `## Awaiting Site-Count Resolution`) let `/sdd-flow continue` resume inside the new step; a blind count interrupted mid-way is redone fresh or continued from its own compaction only.

### What's new in 2.5.0

- **New skill `prompt-doctor`.** Reviews a task prompt before you send it, grading it against the ten-component anatomy from Theo's (T3.gg) prompt dissection plus Sean Goedecke's ranked priorities and hard constraints. Each component gets Present / Weak / Missing / N-A with the quoted span that earns the verdict, and every gap is paired with what the model is now free to decide on its own — in the prompt's own subject matter, not in the abstract.
- **It grades against the right bar.** The run shape (autonomous run / scoped task / one-shot transform) is classified first, so a paragraph rewrite isn't docked for missing stakes and hard constraints. An honest N/A is a passing grade. Only the clear ask and the done-condition are never N/A.
- **It never runs the prompt.** The prompt is a specimen, not an instruction — the skill won't open the issue URL or start the audit the prompt describes. The only files it reads are its own component catalog and, if you point at one, the file holding the draft.
- **It never invents your context.** A missing component produces a question for you, capped at five; it never guesses stakes, deadlines, budgets, or a priority ranking. The rewrite is opt-in, uses only your own words plus your answers, and leaves anything unanswered as a visible `<placeholder>`.
- **`/prompt-doctor`** is the manual entry point.

### What's new in 2.4.0

A one-time setup skill for the BB IDE worktree contract that `worktree-create` requires:

- **New skill `bb-worktree-init`.** Makes a new or existing repo ready for BB IDE and `worktree-create` worktrees. It inspects untracked config, env keys (names and value shapes only — never values), lockfiles, and local databases; proposes a plan for approval; and renders bundled templates into `.worktreeinclude`, `.env-setup.sh`, the `.bb-env-setup.sh` symlink, and — only when setup creates resources outside the worktree — `.bb-env-teardown.sh`. In a repo that already has these files it proposes edits instead of replacing them. It does not commit.
- **The symlink is required, not decoration.** BB IDE only runs `.bb-env-setup.sh`, and a missing one is not an error: BB copies `.env`, skips setup, and opens a worktree whose paths still point at main. The skill always creates the link, checks it, and runs its trial through it.
- **The setup template fails safe.** It refuses to run in the main checkout (comparing symlink-resolved paths, so macOS `/var` vs `/private/var` can't slip past), rewrites *every* copied `.env`/`.env.*` rather than a fixed list, verifies each rewritten path without printing values, fails if main has `.env` but the copy never arrived, and emits the marker line `worktree-handoff` uses to skip reconciliation.
- **Validation before commit.** Syntax, leftover placeholders, symlink, a guard test on a truncated copy of the script, a dry-run of the copy list, and — on approval — a throwaway worktree that is removed afterwards.
- **`worktree-create` points to it** when its precondition gate finds either file missing.

### What's new in 2.3.0

A planning-time gate for goals and constraints that can't both hold:

- **Quantitative Ledger in the spec template.** `bodies/planning.md` adds one table of every numeric goal and constraint, with units and a `Bears on` cross-reference; requirement placeholders now demand numbers, and the planning self-check and quality checklist cover it.
- **Feasibility Arithmetic gate in critical review.** `bodies/critical-review.md` does the subtraction no single reviewer does: when required headroom exceeds what the constraints permit, it is a blocking HIGH finding and an automatic HOLD. Specs with no quantities short-circuit; qualitative stand-ins for quantitative criteria are flagged.

### What's new in 2.2.1

Two defects found running a real per-slice flow, plus one missing review step:

- **The re-planning halt matched too eagerly.** `sdd-flow`'s Step 4c.5 Stage-1 matcher halted the flow on the mere presence of a `## Recommended Re-planning` header — while the retro-body contract explicitly permitted emitting that header with a `None.` body to mean *no re-planning*. A compliant retro could therefore halt the whole flow and demand an operator `--replan` decision for a plan it had just declared fit. The match is now conjunctive: header present **AND** first non-empty body line is not `None.`
- **The section is now required, not optional.** `## Recommended Re-planning` joins `## Recommended SPEC Amendments` as a mandatory retro section with a mandatory bare `None.` body when there is nothing to recommend. An absent section is a malformed retro, not a "no" — previously nothing distinguished "no re-planning" from "the subagent forgot the section".
- **Never trust the subagent's self-report.** A retro subagent stated it had not emitted the re-planning header; it had. Stage 1 now says explicitly that the artifact is the only evidence — the return supplies the path, the file supplies the answer — and the retro body's return contract requires quoting the section bodies re-read from disk rather than from memory of what it meant to write.
- **New: Project Review Checklist Walk.** Both `bodies/slice-review.md` (Step 5.5) and `bodies/code-review.md` (Step 4b) now discover and walk the project's own review checklist — a `CLAUDE.md`/`AGENTS.md` pre-merge section, a PR template, a named docs checklist — with a PASS/FAIL/N-A verdict and evidence per item. Project bookkeeping items (indexes, status tables, registries) apply even when the code didn't touch them, which is exactly the class of obligation a spec-driven review misses.

### What's new in 2.2.0

Phase-specific compaction is reachable again from an interactive session:

- **New commands `/research-compact`, `/planning-compact`, `/implementation-compact`.** `/adhoc-compact` and `/continue` had redirected to these three names since the 1.0.0 fork, but they only ever existed in the `sdd` plugin — with `agent-engineering` installed alone the redirect pointed at nothing, and with both installed it silently reached sdd's frozen 2.2.0 copies.
- **Wrappers, not a second fork.** Each command resolves `skills/sdd-flow/bodies/<phase>-compact.md` (the same body the orchestrator passes on a Safety-Net trip), tells the model to drop the spawned-subagent framing — no orchestrator, no Reads-counter, no ≤100-word return contract — and follow the rest interactively. The templates stay single-source, so manual and orchestrated compactions cannot drift.
- **Prefixed references.** All three names collide with the `sdd` plugin, so `/adhoc-compact` and `/continue` now name them as `/agent-engineering:<phase>-compact`.
- **`/implementation-compact` confirms before committing.** The body's commit step is correct for a subagent but not for an interactive run; the wrapper requires showing the user what will be staged first.

### What's new in 2.1.0

OWASP AI Agent Security review, as one catalog with two entry points:

- **New skill `ai-agent-security-review`** — standalone, target-detecting (explicit path → active SDD artifact → working diff → repo), writes `SDD/reviews/AGENT-SECURITY-*.md` with the same severity rubric and verdict thresholds as the sdd-flow panel.
- **Vendored control catalog** — `skills/ai-agent-security-review/references/owasp-ai-agent-controls.md`, split into spec-level checks (§3), code-level checks (§4), and the abuse-case test matrix (§5). Deliberately not fetched at review time: reviews must be deterministic and offline-safe. Refresh by re-reading the source and bumping the retrieval date.
- **`sdd-flow` hook points** — `agent-security` panel value (Step 3c, new `sdd-spec-agent-security-specialist` agent, Sonnet); Agentic-Surface Lens in `code-review.md` and `slice-review.md` (Step 4b — a HIGH finding is a rejection criterion); abuse-case seeding in `eval-capture.md` (Step 4g, including an abuse-case-only mode when `eval_required: false`).
- **New spec frontmatter field `agent_security:`** — `auto` (default) | `true` | `false`. The planning body resolves `auto` by agentic-surface detection and appends `agent-security` to `review_panel:`.
- **New orchestrator constant `CATALOG`** — resolved at Step 0 alongside `SKILL_ROOT`. A missing catalog closes the gate for the run with a warning; the flow does not halt.

### What's new in 1.0.3

Hardening from the first live test of the 1.0.2 rotation procedure (three real-fixture runs; findings in `proposals/rotation-test-findings-2026-06-12.md`) plus annotations for the Claude Code 2.1.172 nested-subagents platform change:

- **Byte-fidelity invariant (F1).** Everything that remains in the live `progress.md` after a rotation is preserved byte-identical — never retyped, reflowed, re-encoded, or summarized; the only newly written text is the `## Current State` head and the rotation stamp. (The live test caught a rotation silently mutating 55 kept lines, including meaning changes.)
- **Sub-feature archival granularity (F2).** Size rotation now also archives completed-phase history of the still-active feature (phases with a recorded COMPLETE banner); blocks of the active phase always stay live. Previously a single long-running feature could keep the live file over the ~500-line target indefinitely.
- **Open halt-header matching (F3).** Pending halt blocks are matched by prefix (`## Awaiting *`, `## PARTIAL*`), not a fixed five-entry list — real files contain custom halt headers.
- **Literal phase markers (F4).** The rewritten `## Current State` must carry canonical phase-state lines verbatim (e.g., `Implementation Phase - COMPLETE`) — Phase Detection matches these literal markers, not paraphrases.
- **Nested-subagents annotations.** Claude Code 2.1.172 (2026-06-09) allows nested subagent spawning to depth 5; the flow's one-level rule is now documented everywhere as a deliberate design contract rather than a platform fact, and shipped agents are instructed not to spawn even where the tool works. Analysis, empirical results (including a `general-purpose` spawn-delivery failure on 2.1.174 — prefer named subagent types), and refactor gate criteria: `proposals/nested-subagents-analysis-2026-06-12.md`. The flat architecture is unchanged.

### What's new in 1.0.2

- **Progress hygiene.** `progress.md` no longer grows unboundedly (it sits in the read path of nearly every spawn): feature-completion rotation archives a finished feature's history to `SDD/orchestration/progress-archive/`, leaving a one-line summary; a ~500-line size checkpoint fires at phase-boundary commits; pending halt blocks always carry forward verbatim (phase detection never scans archives). Subagent progress entries are bounded to ≤10 lines — narrative belongs in artifacts. The interactive `/adhoc-compact` and `/continue` commands apply the same rotation in manual sessions.

### What's new in 1.0.1

Post-review fixes to 1.0.0 (no behavioral redesign):

- **Per-slice tracker scaffolding.** New per-slice step 4a.0: the orchestrator spawns `bodies/implementation.md` in scaffold-only mode to create the IMPLEMENTATION-PLAN with its `## Slice Progress` table before the first slice (previously nothing created it, and `slice-start` would halt per FAIL-007). The body's per-slice branch is now explicitly scaffold-only — it never implements slices inline.
- **Interactive `research-clarify` model check stripped** (was carried over from the source verbatim).
- **Consistency fixes:** compaction files and the continuation body now agree on `## Continuation Priorities`; the default panel is enumerated (`security`, `performance`, `data-modeling`, `api-contract`, `module-depth`, + `slice-integrity` in per-slice mode); the tracker template regains its `## Context Management → Essential Files Loaded` section for handoffs; panel specialists return bounded severity counts; residual context-percentage fields replaced with Safety-Net wording; assorted stale labels and cross-references cleaned up.

### What's new in 1.0.0

- **Self-contained fork.** `sdd-flow` no longer depends on the SDD plugin; it ships its own phase bodies, agents, and hook. The SDD plugin is optional and uninstallable.
- **Progressive disclosure.** Slim `SKILL.md` orchestrator core; per-phase chapters under `phases/`; complete subagent instruction sets under `bodies/`.
- **Read-by-path spawning.** Bodies are passed by absolute path, never embedded — there is nothing to strip at runtime.
- **Two-stage specialist panel.** Parallel specialists write `PANEL-FINDINGS-*` files; a synthesis subagent reads them from disk and renders the verdict.
- **Reads-only safety net.** The nested-subagent counter is gone (subagents can't spawn); Reads is the whole signal (>15 default, >20 for implementation chunks).
- **Per-slice authoring default.** Planning favors `delivery_mode: per-slice`; whole-feature requires an explicit one-line justification.
- **Sonnet/Opus routing via shipped agents.** Routing lives in agent frontmatter; the orchestrator may escalate a single spawn via a per-spawn model override.
- **New interactive commands** forked in: `/research-clarify`, `/critical-review`, `/continue`, `/adhoc-compact`, `/commit`.

### History

- **0.4.0–0.6.0** — `sdd-flow` Step 4 became mode-aware (`delivery_mode: whole-feature` | `per-slice`), with the per-slice state machine, slice-boundary checkpoints, rolling learnings ledger, and re-planning halt. At the time this still depended on the SDD plugin (≥ 2.0.0) for embedded command bodies and shipped agents — a coupling 1.0.0 removes.
- **0.3.0 and earlier** — Initial releases of `correction-codifier`, `cross-cutting-adr`, `improve-claude-md`, `sdd-flow` (whole-feature only), and the `/regression-eval-capture` and `/adr-capture` commands.
