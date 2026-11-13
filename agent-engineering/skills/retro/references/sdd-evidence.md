# SDD records as retrospective evidence

Read this when the repo has an `SDD/` directory. An `sdd-flow` run writes its history to disk as it goes, so these files cover the whole cycle no matter how many times the session was cleared or compacted, and they remain after the session transcripts have expired.

Scope everything to the feature under review: match the feature name or spec number in the filename, or the cycle's date range. Do not read the whole `SDD/` tree. Any of these may be absent — the flow writes most of them only in some modes — and a missing file is not a finding.

| Record | Where | What it tells a retrospective |
|---|---|---|
| Progress log | `SDD/orchestration/progress.md` | The order of events. Halts (`## Awaiting …` blocks), re-planning, and resumed sessions show where the cycle stalled and why. |
| Compaction files | `SDD/orchestration/compacted/[phase]-compacted-*.md` | One per compaction. Their count and spacing show which phase ran out of context; their `Critical Learnings`, test-status, and open-question sections were written while the struggle was fresh. A subagent's Safety-Net compaction means it spent its read budget — a **navigation** or **tool economy** signal. |
| Code and slice reviews | `SDD/reviews/REVIEW-*.md`, `SDD/reviews/REVIEW-SLICE-*.md` | Every finding is a mistake the implementer made. Ask of each: could a machine have caught it (**automated check**)? Does the same finding recur across slices or features (**check**, else **review standard**)? Did the project-checklist walk find a checklist at all? |
| Spec critical reviews | `SDD/reviews/CRITICAL-SPEC-*.md` | Findings the specialist panel missed — evidence for a missing **review standard** at planning. |
| Fix-loop iterations | filenames carrying `iter<N>` (`REVIEW-SLICE-*`, `FINAL-CHECK-*`) | A high `N` is a loop that would not converge. Read the last two iterations to see what kept failing. |
| Final check | `SDD/reviews/FINAL-CHECK-*.md` | Its `## Security Verification` table names every path on which a security rule did not hold — recurring kinds (an error path, an unset setting, a value echoed back) point at a missing **check** or **review standard**. Its `## LOW Findings` list, and those of the other reviews, are what the cycle chose not to fix. |
| Design brief | `SDD/requirements/DESIGN-*.md` | What the user approved before the spec was written. Its `## Answers and changes` section holds every revision round — many rounds, or answers that reversed the brief's recommendation, show what the agent could not have known (**information access**) or guessed wrong. Compare its "What changes where" with the reviews' `## Design Brief Check`: files outside the approved footprint are surprises. |
| Spec deviations and deferrals | the spec's `## Deviations from Design Brief` and `## Deferred to Later Tiers` | Where planning departed from what was approved, and what was left out on purpose. A deferral added by a review (`Came from` = `review`) is scope the brief missed. |
| Tier plan | `SDD/flow/TIERS-*.md` | One per feature across all its tiers: what shipped, what is still sketched, and the `## Feedback` notes from using a shipped tier — the most direct record of what the cycle got wrong for the user. |
| Clarification and research docs | `SDD/research/CLARIFICATION-*.md`, `RESEARCH-*.md` | Facts the agent had to be told or dig for — **information access** when it had no way to reach them itself. |
| Subagent call logs | `SDD/orchestration/subagent-calls/*.md` | A timestamp and a short excerpt per subagent stop. Use them to order events and to find the session id; the session transcript (via `session-digest.py`) holds the detail. |

## Reading order

1. `progress.md`, for the timeline and the halts.
2. Reviews and critical reviews for the feature — list the findings, then group repeats.
3. Compaction files and anything with a high `iter<N>`.

Cite the file (and section) for every candidate drawn from here, the same way a transcript candidate cites a session and line.
