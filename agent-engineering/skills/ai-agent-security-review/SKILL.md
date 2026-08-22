---
name: ai-agent-security-review
description: "INVOKE THIS SKILL when the user asks for an AI-agent / agentic security review of a specification, research document, diff, or codebase — e.g. 'review this spec for agent security', 'check this for prompt injection', 'run the OWASP agent security checklist', 'is this agent tool scoping safe', 'audit our MCP tools / agent memory / multi-agent trust boundaries'. Applies the OWASP AI Agent Security Cheat Sheet control catalog (tool least-privilege, prompt-injection defense, memory and context security, human-in-the-loop for high-impact actions, output guardrails, monitoring, multi-agent trust, data protection, adversarial validation) and writes a severity-rated findings document. Runs standalone on any target; the same catalog is what sdd-flow's `agent-security` panel value and its agentic-surface code-review lens consume, so a standalone run and a flow run apply identical criteria. NOT for classical appsec (OWASP Top 10, injection into SQL, CSRF, IDOR) — that is the `security` panel value / `/critical-review`."
---

# AI Agent Security Review

Adversarial security review of **agentic** systems against the OWASP AI Agent Security Cheat Sheet.
You find what is missing or wrong; you do not validate. A review that returns "looks fine" without
naming what was checked is rejected output.

**Your control catalog:** `references/owasp-ai-agent-controls.md`, relative to this skill's
directory. Read it before doing anything else. It is the canonical source — do not fetch the OWASP
page at review time, and do not review from memory of it.

---

## 1. Resolve the target

In priority order:

1. **Explicit argument** — a path, glob, PR number, or branch the user named. Use it verbatim.
2. **Active SDD artifacts** — if the user said "the spec" / "the research" or gave no target:
   ```bash
   ls SDD/requirements/SPEC-*.md 2>/dev/null
   ls SDD/research/RESEARCH-*.md 2>/dev/null
   ```
   Most recently modified wins. If several plausibly match, ask which one rather than guessing.
3. **Working diff** — `git diff` plus `git diff --cached`; if both are empty, `git diff main...HEAD`.
4. **Repository** — only when the user asked for a whole-codebase audit. Scope to the agentic
   surface (see §2); do not walk the entire tree.

State the resolved target in one line before reviewing.

## 2. Apply the scope gate

Run the scope gate in §1 of the catalog. If the target has **no agentic surface** — no model call,
no tool/MCP definition, no agent memory or retrieval store, no inter-agent messaging, no model-driven
action on an external system — stop and return:

> No agentic surface found in `<target>`. Checked for: model/LLM calls, tool and MCP definitions,
> agent memory and retrieval stores, inter-agent messaging, and model-driven external actions.
> This catalog does not apply. For classical application security, use `/critical-review` or the
> `security` review panel.

Write no findings document. A forced review of a non-agentic target produces generic advice, which
is the failure mode this skill exists to avoid.

## 3. Pick the table

| Target | Table to apply |
|---|---|
| `SPEC-*.md`, `RESEARCH-*.md`, a design doc, a proposal | §3 Spec-Level Checks |
| A diff, a branch, a PR, source files, a codebase | §4 Code-Level Checks |
| A spec **and** its implementation together | Both, reported in separate sections |

Applying the wrong table is the most common way this review goes wrong: a spec cannot evidence a
runtime control, and a diff cannot evidence a missing requirement.

## 4. Review rules

These match sdd-flow's panel rules exactly, so findings are comparable across entry points.

**Severity rubric**
- **HIGH** — could result in a security breach, data loss, production outage, or irrecoverable
  state if unaddressed.
- **MEDIUM** — a meaningful problem requiring revision; non-trivial to remediate later.
- **LOW** — reduces risk or improves quality; does not block.

**Evidence is mandatory.** Every finding quotes the artifact (spec section or `file:line`). A
finding with no citation is generic advice — delete it rather than shipping it.

**Resolutions match the table.** Spec-level findings resolve to a spec edit (add a requirement,
name a constraint, introduce a `REQ-XXX`). Code-level findings resolve to a concrete code change
with the file named.

**No bare approvals.** If you find nothing, say what you checked, control family by control family.

**Stay in lane.** Classical appsec (SQL injection, CSRF, IDOR, TLS, session handling) belongs to
`/critical-review` or the `security` panel value. Note such an issue in one line under *Out of
scope* and move on — do not develop it into a finding here.

## 5. Write the findings document

**Path:** `SDD/reviews/AGENT-SECURITY-[target-slug]-[YYYYMMDD].md` when an `SDD/` tree exists
(create `SDD/reviews/` if absent). Otherwise report inline in the conversation and offer to write
the file — do not create an `SDD/` tree in a repo that has none.

```markdown
# AI Agent Security Review: [target]

**Target:** [resolved path / diff range]
**Table applied:** [Spec-Level | Code-Level | Both]
**Catalog:** OWASP AI Agent Security Cheat Sheet (vendored, retrieved 2026-08-22)
**Date:** [YYYY-MM-DD]

## Agentic Surface

[What makes this agentic: the model calls, tools, memory, retrieval, agent-to-agent edges, and
external actions you found — with paths. This is the review's scope statement.]

## Findings

### [Control family, e.g. Tool Security & Least Privilege]

- **[HIGH|MEDIUM|LOW]** [Named anti-pattern or finding title]
  - Evidence: [quote + spec section or `file:line`]
  - Risk: [the concrete failure, in the threat vocabulary — e.g. indirect prompt injection into a
    write-scoped tool]
  - Resolution: [spec edit, or code change with the file named]

[Repeat per family that produced findings. Omit families with none — they are covered below.]

## Checked, No Findings

[Per control family with no findings: the specific things you verified. Not "looks fine".]

## Abuse Cases to Cover

[Rows from catalog §5 that this target's threat surface makes relevant, each with its expected
denial. These seed the adversarial regression suite.]

## Out of Scope

[One line each: classical appsec or non-security issues noticed and deliberately not developed.]

## Verdict

[PROCEED | REVISE BEFORE PROCEEDING | STOP AND RECONSIDER]
HIGH: [n] · MEDIUM: [n] · LOW: [n]
```

**Verdict rule** (same thresholds as the sdd-flow panel): any HIGH → `STOP AND RECONSIDER`; 3+
MEDIUM or MEDIUM findings spanning three or more control families → `REVISE BEFORE PROCEEDING`;
otherwise `PROCEED`.

## 6. Return

Report the verdict, the counts, the top findings by title, and the document path. Do not paste
finding bodies into the conversation when a document was written.

If the user asks you to fix the findings, do that as a separate step after they have seen the
verdict — never edit the target during the review pass.

---

## Relationship to sdd-flow

Same catalog, three automatic entry points inside `/sdd-flow` — all gated on the spec's
`agent_security:` frontmatter field:

- **Step 3c** — the `agent-security` panel value spawns `agent-engineering:sdd-spec-agent-security-specialist`
  over §3 during planning.
- **Step 4b** — the code-review body applies §4 as an agentic-surface lens over the implementation.
- **Step 4g** — eval capture seeds the regression dataset from §5's abuse-case matrix.

Running this skill standalone on a spec mid-flow duplicates Step 3c. That is fine for an early
check, but the flow's own pass is what gates the phase.
