# Artifact Paths

Read this when a spawn needs a path its phase chapter does not give. Every subagent MUST use these exact paths; the orchestrator resolves `[###]`/`[feature-name]`/dates before embedding them. What is committed and what is not: `SKILL.md` → Records stay out of git.

---

| Artifact | Path | Created By | Read By |
|---|---|---|---|
| Scope decomposition | `SDD/flow/DECOMPOSITION-[###]-[feature-name].md` | Scope subagent | User |
| Clarification doc | `SDD/research/CLARIFICATION-[###]-[feature-name].md` | User (`/research-clarify`) | Research |
| Ubiquitous glossary | `SDD/UBIQUITOUS_LANGUAGE.md` | research-complete + planning-complete (incremental) | All phase subagents |
| Research doc | `SDD/research/RESEARCH-[###]-[feature-name].md` | Research subagent | Design brief, Planning |
| Design brief | `SDD/requirements/DESIGN-[###]-[feature-name].md` | Design-brief subagent (2.5a, 2.5c) | **The user**; Planning, Spec review, Spec fixes, Code review, Slice review |
| Tier plan | `SDD/flow/TIERS-[feature-name].md` (one per feature across all its tiers — a next-tier cycle keeps the first tier's name) | Design-brief subagent; Completion (4f) | Planning, the next tier's cycle |
| Specification | `SDD/requirements/SPEC-[###]-[feature-name].md` | Planning subagent | Panel, Planning review, Implementation |
| Observability record | `SDD/OBSERVABILITY.md` — only in an application that has the tracing foundation | The user, by running `/observability-init` outside the flow. A flow subagent writes one line of it: with the evals gate on, the implementer that builds the first eval fills its `Eval command` row | Orchestrator (before each design-brief spawn and on approval: is it there?; with the evals gate on, its `Eval command` row before each review); with the evals gate on, the implementer, the reviews (the 4e.5 final check included), and fix subagents — for the env file and the eval command; with the tracing gate on, the implementer, the reviews (the 4e.5 final check included), and fix subagents — for the trace run command, the span file, the env file, and the entry-point test — and the completion subagent, for where traces go |
| **Panel findings (per specialist)** | `SDD/.records/reviews/PANEL-FINDINGS-[panel-value]-[feature-name]-[YYYYMMDD].md` | Each specialist (Stage 1) | Panel synthesis (Stage 2) |
| Spec panel review | `SDD/.records/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md` | Panel synthesis (Stage 2) | Planning fix |
| Spec critical review | `SDD/.records/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md` | Planning review | Planning fix |
| ADRs / ADR index | `SDD/adr/NNNN-slug.md`, `SDD/adr/README.md` | adr-capture subagent | Future runs, humans |
| Implementation plan | `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md` | Implementation subagent | Code review, Completion |
| Trace tree (tracing gate on) | `SDD/.records/reviews/TRACE-TREE-<SLICE-XXX\|FEATURE>-[feature-name]-[YYYYMMDD].md`, and `TRACE-TREE-FEATURE-[feature-name]-iter<N>-[YYYYMMDD].md` for the final check — the call tree a real run recorded, rendered by `scripts/trace-tree.py` | The review that runs the Tracing Lens (per-slice 4b, the feature code review 4b, and each 4e.5 final check) | The fix subagent that answers that review; the completion subagent (the last 4e.5 tree) |
| Eval results (evals gate on) | `SDD/.records/reviews/EVAL-RESULTS-<SLICE-XXX\|FEATURE>-[feature-name]-iter<N>-[YYYYMMDD].md`, with a `.json` file of the same name beside it — what the model answered to each case in the run a review reads, written by the application's eval run | Orchestrator, by running the application's eval command before each review (per-slice 4b, the feature code review 4b, and each 4e.5 final check) | That review; the fix subagent that answers it; the completion subagent (the last 4e.5 run's results); the user at the commit checkpoint (4h), when the spec has a sign-off requirement |
| Final check review | `SDD/.records/reviews/FINAL-CHECK-FEATURE-[feature-name]-iter<N>-[YYYYMMDD].md` | 4e.5 final check | 4e.5 fix, completion |
| Slice file | `SDD/implementation/slices/SLICE-[###]-[NN]-[slice-name]-[YYYY-MM-DD].md` | slice-start subagent | per-slice cycle |
| Slice review | `SDD/.records/reviews/REVIEW-SLICE-*` (its `Re-plan:` line is shown at the slice pause) | Slice review | Slice fix, slice pause, end-of-feature |
| Code review | `SDD/.records/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md` — the one review of the whole feature's code, both delivery modes | Code review (4b) | Code review fix (4c) |
| Implementation summary | `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md` | Completion | — |
| Reviewer call (second-model route) | `SDD/.records/reviewer-calls/[step-id]-[iter]-[YYYY-MM-DD_HH-MM-SS].{prompt.md, log, return.md}` | Orchestrator (prompt); `scripts/second-model-review.py` (log, return) | The reviewer's CLI (prompt); orchestrator (return) |
| Counter file | `SDD/.records/counters/[step-id]-[chunk-or-iter]-[YYYY-MM-DD_HH-MM-SS].md` | Orchestrator (per spawn) | The spawned subagent only |
| Compaction file | `SDD/.records/compacted/[phase]-compacted-[YYYY-MM-DD_HH-MM-SS].md` | Subagent on Safety-Net trip | Continuation subagent |
| Progress file | `SDD/.records/progress.md` | All subagents (append only) | All subagents, orchestrator |

```
SDD/
├── UBIQUITOUS_LANGUAGE.md
├── OBSERVABILITY.md                      # only after /observability-init — the flow reads it, and writes only its Eval command row
├── adr/{NNNN-slug.md, README.md}
├── flow/{DECOMPOSITION-[###]-[feature-name], TIERS-[feature-name]}.md
├── research/{CLARIFICATION-*, RESEARCH-*}.md
├── requirements/{DESIGN-[###]-[feature-name], SPEC-[###]-[feature-name]}.md
├── implementation/
│   ├── IMPLEMENTATION-PLAN-*.md
│   ├── slices/SLICE-*.md   # per-slice mode only
│   └── summaries/IMPLEMENTATION-SUMMARY-*.md
└── .records/                             # git-ignored: process records, never committed
    ├── .gitignore                        # the one line `*`
    ├── {progress.md, progress-archive/, subagent-calls/, reviewer-calls/, counters/, compacted/}
    └── reviews/
        ├── {PANEL-FINDINGS-*, PANEL-SPEC-*, CRITICAL-SPEC-*, REVIEW-*, REVIEW-SLICE-*,
        │    FINAL-CHECK-*, TRACE-TREE-*, EVAL-RESULTS-*}.md
        └── superseded/[YYYY-MM-DD_HH-MM-SS]/   # a replaced plan's slice reviews — kept, never read
```
