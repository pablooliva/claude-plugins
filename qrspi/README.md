---
tags:
  - knowledge/ai/agentic-coding
  - knowledge/ai/agent-workflow
  - knowledge/ai/claude-code
type: analysis
date_created: 2026-05-13
sources:
  - "/Volumes/Crucial Data/Documents/Obsidian/Knowledge/QRSPI - From RPI to QRSPI - Dexter Horthy.md"
implementation_reviewed: https://github.com/matanshavit/qrspi
local_clone: /Volumes/Crucial Data/Documents/Code & Dev/qrspi
---

# QRSPI — Methodology Analysis & Implementation Review

Analysis of Dexter Horthy's QRSPI methodology (presented at Coding Agents 2026), a fidelity review of Matan Shavit's open-source implementation, a first-principles critique of QRSPI's underlying claims, and a comparison against the SDD methodology shipped from this plugins repo.

**Sources**
- Talk notes: `/Volumes/Crucial Data/Documents/Obsidian/Knowledge/QRSPI - From RPI to QRSPI - Dexter Horthy.md`
- Implementation reviewed: https://github.com/matanshavit/qrspi
- Local clone of implementation: `/Volumes/Crucial Data/Documents/Code & Dev/qrspi`
- SDD methodology compared: `/Volumes/Crucial Data/Documents/Code & Dev/claude-plugins/sdd/` and `/Volumes/Crucial Data/Documents/Code & Dev/claude-plugins/agent-engineering/skills/sdd-flow/SKILL.md`

**Contents**
- Part 1 — What QRSPI Requires (per the talk)
- Part 2 — Local Implementation (`matanshavit/qrspi`)
- Part 3 — Gap Analysis: Presentation vs. Implementation
- Part 4 — Are Dex's Claims Reasonable and True?
- Part 5 — SDD vs QRSPI: Should I Switch?

---

## Part 1 — What QRSPI Requires (per the talk)

The presentation defines a methodology with hard structural constraints, not just an 8-step list. A faithful implementation must satisfy all of the following:

**Pipeline shape**
- Eight steps: Questions → Research → Design → Structure → Plan → Worktree → Implement → PR
- Each step runs in its own context window
- Each step produces a durable markdown artifact that feeds the next step

**Instruction budget**
- Every step's prompt must stay under ~40 instructions (Dex cites Kyle/HumanLayer's reading of arXiv 2507.11538: frontier LLMs follow ~150–200 instructions reliably; CLAUDE.md + tools + MCPs consume the rest)
- Replaces RPI's monolithic 85-instruction `create_plan` prompt

**Information hiding between phases**
- Research runs with the ticket *hidden*: the Question step generates neutral, fact-seeking questions; the researcher never sees what is being built
- Prevents intent contamination — "how do I build X" leaking into a step that should produce facts only

**Mandatory interactivity (no "magic words")**
- Design must ask the human open questions *before* writing the doc — formerly this only happened when expert users knew the magic phrase ("work back and forth with me starting with your open questions"); now structurally enforced

**Artifact shapes**
- Design: ~200 lines covering current state, desired end state, patterns to follow, resolved decisions, open questions for the human
- Structure: ~2 pages — "C header file" view of signatures, types, phase ordering — not implementation
- Vertical slicing (stub/wire/mock/migrate end-to-end through every layer), not horizontal layers (all-DB → all-API → all-UI)
- Plan: same shape as RPI's `create_plan`, trusted because everything upstream is locked

**Agent role discipline**
- Helper sub-agents act as documentarians: describe what exists, never propose changes

**Review surface**
- Human reviews design (~200 lines), not the 1000-line plan
- PR review targets code, not plan ("Don't read the plans. Please read the code.")

---

## Part 2 — Local Implementation (`matanshavit/qrspi`)

Matan Shavit's open-source port. Structure:

```
.claude/
├── commands/qrspi/    1_question.md … 8_pr.md     (~60–90 lines each)
└── agents/            codebase-locator
                       codebase-analyzer
                       codebase-pattern-finder
                       web-search-researcher
```

Each command file has frontmatter (`description`, `model: opus`, `argument-hint`) and emits/reads files under `thoughts/qrspi/<id>/`. Each agent file enforces documentarian behavior with explicit "DO NOT suggest improvements" guardrails.

---

## Part 3 — Gap Analysis: Presentation vs. Implementation

| Requirement | Local implementation | Verdict |
|---|---|---|
| Eight numbered steps | `1_question.md` … `8_pr.md` | Exact match |
| <40 instructions per step | Imperative steps per file ≈ 5–10; file length 60–90 lines but most is YAML / templates | Comfortably under budget |
| Fresh context per phase | README advises it; not mechanically enforced | Doc-only, not enforced |
| Research blind to ticket | `2_research.md:16` explicitly "Do NOT read `task.md`"; `1_question.md:65` forbids task description in `questions.md` | Enforced in prompt |
| Question step | Neutral, fact-seeking, 3–7 questions, with good/bad framing examples (`1_question.md:23–31`) | Faithful |
| Design mandatory interaction | `3_design.md:21–39`: "Do NOT skip this step. Do NOT write the design document without user input." Bolded list of options-with-trade-offs required | Structurally enforced |
| Design ~200 lines + prescribed sections | `3_design.md:43–66`: Current State / Desired End State / Patterns to Follow / Design Decisions / What We're NOT Doing / Open Risks | Close match; "Open Risks" stands in for "Open questions for the human" (those get answered in the interactive step instead) |
| Structure = signatures + vertical slices | `4_structure.md:22–28` shows explicit vertical (correct) vs. horizontal (wrong) examples; rule: "Signatures and types, not full implementation" | Faithful |
| Plan with verification checkboxes | `5_plan.md` — code snippets, `- [ ]` checkboxes mandatory; not a direct copy of RPI's `create_plan` but matches its spirit | Functionally equivalent |
| Worktree | `6_worktree.md` — `~/wt/<repo>/<branch>`, copies artifacts (untracked files don't propagate to worktrees) | Faithful |
| Implement per phase, commit per phase | `7_implement.md:38, 70–77` — one phase at a time, commit after automated verification passes | Goes beyond the talk |
| Checkboxes as resume mechanism | `7_implement.md:56–60` "Resuming After Context Reset" section | Beyond the talk |
| PR grounded in design | `8_pr.md:13` reads `design.md`; PR body template references design + plan | Faithful |
| Documentarian sub-agents | All 4 agent files lead with "CRITICAL: YOUR ONLY JOB IS TO DOCUMENT... DO NOT suggest improvements" | Faithful |
| "When to Go Back" / upstream fixes | Every command has a dedicated section (e.g., `2_research.md:73–75`, `4_structure.md:84–86`) | Beyond the talk |

### Notable deltas

**The implementation adds beyond the talk** (improvements, not violations):
1. Explicit "When to Go Back" sections in every command — operationalizes Dex's verbal "your fix point is upstream" principle
2. Checkboxes as a context-recovery contract — talk mentions static artifacts as memory; implementation commits to checkboxes as the specific resume protocol
3. One commit per phase — gives independent revertability that the talk does not formalize
4. "What We're NOT Doing" scope-creep prevention section in design

**Weaker than or missing from the talk**:
1. Fresh-context enforcement is doc-only ("Start a fresh context window between phases for best results"). The implementation trusts the user to start new sessions. Each command does read only specific inputs (closest mechanical proxy), but a single chat session could blow past that.
2. No orchestrator — the talk mentions HumanLayer is building an IDE that orchestrates QRSPI; this implementation is manual, command-by-command.
3. No instruction-budget telemetry — no awareness of the 40% / 60% "dumb zone" thresholds.
4. Skills vs. commands — talk calls them "skills" (aligned with Claude Code's skill system); implementation uses slash-commands. Functionally equivalent for this use case.
5. Plan-template lineage — talk says the plan stage reuses RPI's exact `create_plan` template; implementation writes its own template that matches the spirit but isn't a direct copy.

### Bottom line on the implementation

A **high-fidelity, ~95% faithful implementation** of QRSPI as Dex describes it. The eight phases, artifact contracts, information-hiding between Question/Research, mandatory Design interactivity, vertical-slicing rule, documentarian sub-agents, and "read the code not the plan" PR phase are all present and structurally enforced in the prompts.

Where it diverges, it mostly *extends* the methodology (checkbox-based resume, per-phase commits, explicit backtracking guidance) rather than weakens it. The two real gaps are operational: fresh-context separation between phases is advised but not enforced, and there is no orchestrator/telemetry layer — both consistent with this being a community port rather than the in-development HumanLayer IDE.

If you wanted to harden it further toward the talk's vision:
1. Wire fresh-context enforcement into hooks (or bake it into the "Next: run X" handoff message more aggressively)
2. Port the actual HumanLayer `create_plan` template into `5_plan.md` to match Dex's claim that the plan step is unchanged from RPI

---

## Part 4 — Are Dex's Claims Reasonable and True?

A first-principles assessment of the methodology's premises, independent of the implementation.

**Headline:** the methodology is well-reasoned and most core claims hold up, but several specific numbers Dex presents as measurements are really folk heuristics, and a few principles he treats as universal are actually trade-offs.

### Claims that are solid

**Information hiding between phases (Research blind to the ticket).** One of the strongest, most defensible moves in QRSPI. LLMs anchor heavily on framing — once an agent knows what you're building, "describe how X works" silently becomes "describe how X works *in the context of building Y*," which contaminates the facts with implicit recommendations. Hiding the ticket is mitigating a known failure mode (sycophancy + goal-conditioned summarization). Empirically the single most defensible structural move in QRSPI.

**Mandatory interactivity instead of "magic words."** Solid. Under instruction overload, LLMs reliably skip the *interactive* steps first — those require a state transition (stop and wait), which is the kind of behavior models lose hold of when their attention is fragmented. Making "ask 3–5 questions and wait" structural rather than optional is the right fix.

**Durable markdown artifacts > auto-compaction.** Solid. Auto-compaction is lossy summarization of a long context — it preserves recency and salience and drops background facts. External artifacts that the next phase reads fresh sidestep that loss. Consistent with retrieval-augmented patterns generally.

**Decompose monolithic prompts into focused steps.** Directionally right. Long, dense prompts produce worse instruction-following than several short, focused ones — well-documented in IFEval-style benchmarks and instruction-density studies.

**Vertical slicing.** True, but this is recycled Agile/XP wisdom from the early 2000s, not an LLM-specific insight. The reason it is *especially* important with agents: horizontal failures are harder for the human reviewer to localize when most of the diff was machine-generated.

**"Read the code, not the plan" (for production SaaS).** Reasonable. The plan is a prediction; the code is the artifact. Reviewing a plan and trusting the diff to match it is a category error — they are different objects. Dex's own caveat (OSS/low-stakes is different) is the right hedge.

### Claims presented as facts that are really heuristics

**"Frontier LLMs follow ~150–200 instructions reliably."** Overstated as a hard number. "Instruction" is not a well-defined unit. What is true: instruction-following degrades smoothly with prompt density and competing demands; some instruction classes (negations, conditionals, "do X *unless* Y") fail much earlier than others. The 150–200 figure is best read as *"there is a real budget, treat it as scarce,"* not as a number you can budget against precisely. The pragmatic conclusion (keep prompts focused) is right; the precision is theater.

**"The dumb zone starts at ~40% context utilization."** Folklore. Jeff Huber's anecdotal heuristic, not a measured threshold. What is true: long-context performance is uneven, models exhibit "lost-in-the-middle" effects, and retrieval over long contexts degrades. What isn't true: there is no sharp knee at 40%. Modern long-context models (Claude 4.x with 1M, Gemini 2.x) handle their windows more uniformly than the 40% number implies. Dex even softens this in Q&A — *"experienced users push to 60%"* — which signals he knows it is a rule of thumb. The underlying intuition (more context ≠ better results, manage it actively) is correct; the threshold is invented.

**"85 instructions → silently skipped steps for 50% of users."** Probably real as an observation, but the causal attribution is mushy. Could be instruction overload (his hypothesis), could be position bias (steps buried in the middle), could be that the "magic words" group was self-selecting for users who *also* did other things well. The fix (split the prompt) works regardless of which mechanism dominates, so the methodology survives even if the diagnosis is partially wrong.

### Claims that are real principles but trade-offs, not laws

**"More steps is better."** True up to a point, then false. Eight steps means seven handoffs, each an opportunity for information loss (artifact didn't capture some detail the next step needed) or contradiction (Phase 3 made an assumption Phase 5 violates). Multi-agent pipelines have a known reliability ceiling that gets *worse* with more stages, not better. QRSPI is probably near the sweet spot for non-trivial features; it would not be the right answer for a one-file change, and Dex says exactly that. But the framing of "more granular = strictly better" is a half-truth — there is a U-curve, and the optimum is task-dependent.

**"The plan stage is unchanged from RPI."** Reasonable claim but implies the plan template is portable across upstream changes. In practice, when design and structure are more detailed/locked, the plan can afford to be terser — so something probably *should* change downstream. Minor point.

**"AI shifts the bottleneck, not the timeline; aim for 2–3x, not 10x."** Value judgment dressed as an empirical claim. For some workloads (greenfield, throwaway, exploratory), 10x is real and the quality cost does not bite. For production SaaS he is right. Treat it as taste, not law.

### What the talk underweights

**Coordination cost.** Eight agents with seven handoffs is more failure surface than three agents with two handoffs. The artifacts mitigate this — they're a typed interface between stages — but they don't eliminate it. Information that wasn't captured in `design.md` is lost to Step 5; the plan agent can't ask the design agent "what did you mean here?" Heavy planners forget this regularly.

**Token cost.** Eight separate context windows with fresh reads of upstream artifacts is non-trivially more expensive than one shared window. For most engineering tasks this is fine, but it is a real budget item that goes unmentioned.

**Sub-agent unreliability.** The documentarian guardrails on the agent files are good prompting practice, but negative instructions ("DO NOT critique") are known to be the *least* reliably followed kind of instruction. The agents will sometimes editorialize despite the guardrails, especially under longer contexts. The methodology mitigates this by treating sub-agent output as input for the parent's synthesis, not as ground truth — which is the right defense.

**The model improves out from under you.** Several of QRSPI's structural choices are responses to *current* model limitations. The "40% dumb zone" was much more punishing in 2024 than it is in 2026 with 1M-context Claude Opus. Some of the splitting won't be needed in 12–18 months. The methodology has expiration risk that the talk does not acknowledge.

### Final assessment

The **structural moves** (decomposition, information hiding, mandatory interaction, durable artifacts, vertical slicing, code-not-plan review) are sound and well-grounded in how LLMs actually fail. The **specific numbers** (150–200 instructions, 40% dumb zone) are heuristics presented with too much precision — useful as directional intuitions, not as engineering thresholds. The **strategic claims** (2–3x not 10x, read code not plans) are value judgments that happen to be defensible but are not load-bearing on the methodology working.

If you stripped out the numbers and kept the principles, you would have a methodology that holds up to first-principles analysis. The numbers are mostly there because audiences want measurable answers, and Dex is honest enough to soften them in Q&A when pressed.

The most underweighted concern: QRSPI is a *2026-specific* methodology optimized for Claude/GPT-class models with current context-handling characteristics. Treat it as state-of-the-art for now, not a permanent template.

---

## Part 5 — SDD vs QRSPI: Should I Switch?

A direct comparison between QRSPI and the SDD methodology that ships from the `claude-plugins` repo containing this analysis (the SDD plugin + the `sdd-flow` skill in `agent-engineering`). Written from the perspective of an SDD user evaluating whether to adopt QRSPI.

### Headline

The existing SDD process is more mature than QRSPI on every dimension that matters except one, and on that one the gain is theoretical rather than observed. If you have not seen real deficiencies — and especially after adopting slice-based delivery — the cost of switching exceeds the benefit. **Stay on SDD. Optionally cherry-pick one QRSPI idea.**

### How the two methodologies map to each other

The 1:1 mapping is closer than expected. The shapes are almost identical. The differences are in *information flow* and *step granularity*, not in *what gets produced*.

| QRSPI step | SDD analog | Notes |
|---|---|---|
| Q — Questions | `/research-clarify` → CLARIFICATION artifact (Step 1.5) | SDD's is optional + external to sdd-flow; QRSPI's is mandatory + inside the flow |
| R — Research | Step 2a research subagent → `RESEARCH-XXX.md` + 2b ADR capture + 2c critical-review + 2d fixes | SDD has more rigor (adversarial review + ADRs) but research subagent **sees the task description** |
| D — Design | Step 3a planning subagent → `SPEC-XXX.md` (frontmatter + `## Modules` + `## Delivery Slices`) | SDD's spec is denser than QRSPI's design.md; includes module risk tiers, slice declarations |
| S — Structure | (no standalone analog — folded into the spec's `## Modules` and `## Delivery Slices` sections) | QRSPI splits into two artifacts; SDD keeps one richer artifact |
| P — Plan | Step 3a–3f planning trio + 3c panel review + 3d critical-review + 3e fixes | SDD adds specialist panel review (security, perf, data-modeling, etc.) that QRSPI does not have |
| W — Worktree | (no analog; user manages worktrees outside the flow) | Trivial; cosmetic difference |
| I — Implement | Step 4 with two routes (whole-feature vs per-slice); per-slice has retro + rolling ledger + re-planning halt | SDD's per-slice mechanics are substantially more sophisticated than QRSPI's vertical-slicing hint |
| PR — Pull Request | `/commit` + commit-per-phase / commit-per-slice (no `/sdd-pr` command) | SDD lacks an explicit PR-creation command; done manually or via separate command |

### Where QRSPI is structurally distinct — and whether it would help

#### 1. Information hiding: research never sees the task

The signature QRSPI move. SDD's research subagent reads the task description directly. QRSPI's research subagent reads only neutral, fact-seeking questions; the ticket is hidden.

**Real or theoretical gain?** Theoretical. Intent contamination is a real LLM failure mode, but SDD has compensating mechanisms:
- The CLARIFICATION artifact (when used) externalizes design intent
- Critical-review's "Design Concept Fidelity" check catches research that drifted into recommendations
- The research subagent's prompt does not invite opinionated output

Whether information hiding would yield measurable quality gains is an empirical question that cannot be answered without an A/B test. Absent observed contamination problems in the SDD output, the gain is probably small. This is **the one place** worth considering borrowing from QRSPI — see "optional cherry-pick" below.

#### 2. Questions phase as mandatory, sequenced step

QRSPI's Q phase is inside the flow and mandatory. SDD's `/research-clarify` is interactive and external — easy to skip.

**Real or theoretical gain?** Depends on user discipline. If `/research-clarify` is invoked routinely, no gain. If it is skipped on ambiguous tasks, QRSPI's structural forcing would help. This is more about discipline than methodology.

#### 3. Structure as a distinct artifact between design and plan

QRSPI's structure outline (~2 pages, "C header file" view) sits between design.md and plan.md. SDD merges both into the spec.

**Real or theoretical gain?** Negative. SDD's spec already contains the structural information (`## Modules` with depth/risk, `## Delivery Slices` with modules-touched + acceptance check). Splitting it into two artifacts would add a handoff for no information gain. Worse, it would lose the spec frontmatter as a single source of truth for `delivery_mode`, `review_panel`, `eval_required`, and `cross_cutting_decisions`.

#### 4. Sub-40-instruction budget per step

QRSPI requires every command under ~40 instructions. SDD's commands are 100–635 lines (though much is YAML/templates/checklists, not imperative instructions).

**Real or theoretical gain?** Possibly real but unclear. The honest concern: dense commands risk silent step-skipping under instruction overload. The honest defense: the count-based bail-out (Reads 0/10, Nested 0/4) + critical-review backstops would surface skipped work. Absent observed silent-skip incidents, the budget isn't binding in practice.

#### 5. Eight phases vs three

Cosmetic. SDD's "three phases" is misleading marketing. Actual execution has 20+ sub-steps (2a, 2b, 2c, 2d, 2e, 2f, 3a–3g, 4a–4j …). SDD is *more* decomposed than QRSPI in execution, not less.

### Where SDD substantially exceeds QRSPI

Switching to QRSPI would cost the user these — none of which QRSPI has any analog for:

1. **Slice mechanics (the big one).** Rolling `LEARNINGS-FEATURE` ledger, two-stage retro matcher, re-planning halt that bypasses skip-checkpoints, forward-only status machine, atomic per-slice commits. QRSPI's "vertical slicing" is a planning recommendation; SDD's is a workflow primitive with state, gates, and recovery semantics.
2. **Specialist panel review** (security, performance, data-modeling, api-contract, module-depth, etc.) with bounded fix-loops and progress-stall detection. QRSPI has nothing equivalent.
3. **ADR capture** for cross-cutting decisions — versioned, auto-indexed, inherited by future features. QRSPI does not formalize this.
4. **Regression eval scaffolding** (`eval_required: true` → LangSmith dataset/evaluator/run-function templates). QRSPI does not formalize this.
5. **Ubiquitous language glossary** with incremental phase-boundary updates. QRSPI does not formalize this.
6. **Risk-tiered code review** (depth scaled by module risk tier). QRSPI does not formalize this.
7. **Count-based bail-out + mid-phase handoff protocol** with explicit compaction commands. QRSPI mentions artifacts-as-memory but does not formalize handoff under context pressure.
8. **Bounded fix-and-re-review loops** with progress-stall detection on three different gates (panel, per-slice, critical-review).

The maturity gap is large, and most of it is in places QRSPI does not even acknowledge as a problem.

### Bottom line

QRSPI is a **methodology talk**, optimized for HumanLayer's IDE prototype. SDD is a **production methodology** with state machines, gates, and recovery semantics, refined through actual use. They are not the same kind of artifact.

The structural moves QRSPI is best known for (information hiding, mandatory interaction, vertical slicing, artifacts-as-memory) are all present in SDD — sometimes more rigorously enforced (panel review, bail-out semantics), sometimes less rigorously enforced (information hiding, mandatory question phase).

**Recommendation: do not switch.** Switching would cost the slice-mechanics work, the entire review-panel system, ADR capture, eval scaffolding, and the glossary. The gain would be a theoretical reduction in intent contamination during research, with no evidence it is hurting SDD output today.

The "I have not seen any real deficiencies" observation is well-calibrated — the absence of pain is real evidence, not a gap in perception.

### Optional cherry-pick (low cost, possible upside)

The one QRSPI idea worth considering grafting onto SDD:

**Make the research subagent read only `CLARIFICATION-XXX.md`, not the original task description.** This is a small change to `research-start.md` and would give SDD QRSPI's information-hiding property while keeping everything else. The cost is: `/research-clarify` must be invoked for every feature (no more skipping). Worth a try if there is suspicion that research output is occasionally too solution-shaped; not worth doing speculatively.

Everything else QRSPI proposes that SDD lacks is either cosmetic, less rigorous than the current approach, or actively worse for the slice-based workflow.

---

## References

- **Source talk notes:** `/Volumes/Crucial Data/Documents/Obsidian/Knowledge/QRSPI - From RPI to QRSPI - Dexter Horthy.md`
- **Talk video:** [YouTube — From RPI to QRSPI](https://www.youtube.com/watch?v=5MWl3eRXVQk) (Dexter Horthy, Coding Agents 2026)
- **Implementation reviewed (GitHub):** https://github.com/matanshavit/qrspi
- **Local clone of implementation:** `/Volumes/Crucial Data/Documents/Code & Dev/qrspi`
- **Original RPI methodology:** https://github.com/humanlayer/advanced-context-engineering-for-coding-agents
- **12 Factor Agents:** https://github.com/humanlayer/12-factor-agents
