# sdd-flow: the code reviews also judge fit and size (2026-11-12)

Status: **decided by the owner 2026-11-12. Not implemented.** Part of release 2 of
`proposals/sdd-flow-simplification-2026-11-12.md` ("in review: fit and size graded like bugs"). It follows
`proposals/enforcement-site-proof-2026-11-12.md` (4.1.0), which already made LOW findings listed, not fixed.
The prompt that implements it is `proposals/review-criteria-prompt-2026-11-12.md`. Target: agent-engineering 4.2.0.

## Problem

Across every task of the sdd-flow evaluation (`sdd-flow-eval`, FINDINGS-001 and FINDINGS-002), sdd-flow tied or
beat plain Claude Code on hidden tests, and lost on the blind judge's size, scope and fit scores every time:

| Task | Scope (plain / sdd) | Fit (plain / sdd) | Size (plain / sdd) |
|---|---|---|---|
| tornado-3744 | 5 / 3 | 5 / 2 | 5 / 2 |
| tomlkit-677 | 5 / 3 | 5 / 3 | 5 / 2 |
| cattrs-765 | 5 / 3 | 5 / 3 | 5 / 1 |
| networkx-8727 (re-judged) | 5 / 4 | 5 / 3 | 5 / 3 |
| eduKate SPEC-002, call 1 / call 2 | 4 / 3, 4 / 3 | 4 / 3, 4 / 4 | 4 / 2, 4 / 2 |

eduKate SPEC-002, one tier of one feature: plain +1,150 lines in 9 files, sdd-flow +4,708 lines in 22 files.

The code reviews never ask the judge's questions. As of 4.1.0, `bodies/code-review.md` (which the slice review
applies to each slice) says:

- code quality is reviewed "ONLY IF ABOVE CRITERIA MET" (spec alignment, context engineering, tests);
- "What NOT to Focus On": "Personal coding style preferences", "Architectural patterns not in specification",
  "Code organization unless it impacts traceability";
- "What TO Focus On": "Can every line trace to a specification requirement?" — a line that serves the spec
  passes however much code there is;
- the Design Brief Check (files changed outside the brief's "What changes where" table) is "Informational
  only" and may not raise a finding. The slice review's Step 5.7 says the same.

So the reviews ask whether the code does what the spec says and whether anything is missing; nothing pushes back
on size or on code that ignores what already exists. Each round of findings adds code. Maintainability — how
easily a later person or agent changes this code — is not a review criterion.

A confound to keep in mind: in the benchmark the plain arm's code was written by Opus and sdd-flow's by Sonnet
subagents. Part of the gap may be the model. This change does not address that.

## Decision

1. **Remove the exclusions** that keep reviewers off organization, patterns and fit ("What NOT to Focus On"
   items above, and "ONLY IF ABOVE CRITERIA MET" as a gate on code quality). Keep the exclusions that still
   make sense (premature optimization; taste with no effect on a reader).
2. **Add a fit-and-size check** to every code review — slice review (4b), whole-feature code review (4b),
   implementation critical review (4d). Its questions are the judge's:
   - Does the change match the surrounding code — its style, naming, helpers, patterns and layering?
   - Does it reuse what exists, or duplicate a helper, type or pattern the code base already has?
   - Could it be smaller, or folded into existing code? Is there a layer, wrapper, option or abstraction the
     approved tier does not need?
   - Will the next person or agent who changes this code find it where they would look, and change it in one
     place?
3. **A footprint overrun is a finding.** A file changed outside the brief's "What changes where" areas is a
   fit finding, unless the spec records it as a departure from the brief (the departures the owner already
   saw at 3g). The Design Brief Check stops being informational.
4. **Grading.** A fit finding is **MEDIUM** when the change adds a file, a layer, or a duplicate of an existing
   helper (an out-of-footprint new file included); otherwise LOW. Since 4.1.0 a LOW finding is only listed, so
   without this rule most fit findings would never be fixed.
5. **Fixer rule.** A fit finding is fixed by removing or merging code — reusing the existing helper, folding
   the new file into the module it belongs to, dropping the layer — never by adding code. A fix round reports
   its net line change.

## Not decided here (out of scope)

- The growth budget (a file/line estimate approved at the design gate) and the reuse map in the brief.
- The required simplicity stop after the spec (3g), the narrowed specialist panel, the end-of-feature
  consolidation pass, the review-loop round cap, the test rules (behaviour, not shape), the implementer model.
- The critical review's "assume there ARE problems to find" stance.

Each is in `proposals/sdd-flow-simplification-2026-11-12.md`.

## How to tell whether it works

Re-run the whole-feature code review (4b) on eduKate SPEC-002's sdd-flow result (`05ab2b4..c836c23`, `SDD/` left
out) with the new body, on Codex. It should name, as MEDIUM findings, what the blind judge named: the large
wording-validation framework, the unrelated `.gitignore` line, files outside the brief's footprint. Then the
benchmark rerun the simplification note describes, comparing the judge's fit and size scores.
