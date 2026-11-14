# Phase: Planning — Step 2.5 (Design Gate)

Read when research's last step (2e) is done, with `phases/planning-inputs.md` (the counters and the paths BRIEF, TIERS, TIER_PLAN, TRACING, the observability line, EVALS). On approval, go on to 3a in `phases/planning.md`.

---

## Step 2.5: Design Gate

Runs after 2e and before 3a. The brief is the human's review surface for planning; the spec is held to it.

### 2.5a. Design-Brief Subagent

Spawn an **`agent-engineering:sdd-workhorse`** subagent **with the per-spawn model override `opus`** (the workhorse's instructions and tools, Opus's judgment — `sdd-critical-reviewer` is also Opus but carries an adversarial reviewer's persona, which is wrong for an author):
- **Body:** `bodies/design-brief.md`
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/research/CLARIFICATION-[###]-[feature-name].md` (if present), `SDD/UBIQUITOUS_LANGUAGE.md` (if present), existing `SDD/adr/`, **TIERS**, **TIER_PLAN** (the path, whether or not the file exists yet), `TIER: N` if the user passed `--tier N` or this is a next-tier cycle, **the observability line** copied verbatim, **EVALS** when that line says `present`, **HARVEST** when there is one (below), and on a next-tier cycle the previous tier's research document.
- **HARVEST** — the harvested eval cases still open (`references/evals.md` §2). Derive it just before this spawn, before every revision run, before 3a, and again on a resumed session; it is not recorded. Take every `SDD/flow/HARVEST-….md` path named under the tier plan's `## Feedback` or in the task description; a file's cases are its `## Case <n> — trace <id>` headings. A case is closed when a spec other than the one this cycle writes has adopted or dropped it: `grep -l -F -e 'harvested: <path>, trace <id>' -e 'dropped: <path>, trace <id>' SDD/requirements/SPEC-*.md` lists one. A deferred case stays open. Pass the open cases as `HARVEST: <path> — traces <id>, <id>; <path> — traces <id>`; none open → no line.
- **Outputs:** **BRIEF**, **TIER_PLAN** (none when the brief says tiers are not applicable), append `progress.md`.
- **Task:** Write the design brief. The body's **quality rule** applies: when the observability line says `present` and the feature has a model in it, one Key decision says how the quality of what the model says will be judged; when it says `absent` and the feature has a model in it, the brief's `## Tracing foundation` section recommends running `/observability-init` before approving — or, in an application not written in Python, says the foundation exists only for Python. Carries the Safety-Net Rule, a fresh counter (`Reads: 0/15`), and `planning-compact.md` as the compact body.

### 2.5b. Gate

**Fires every time the brief is written or rewritten. No flag skips it.**

The orchestrator never edits the brief. Approval state is the latest `## Design Brief - ` line in `progress.md` — `Drafted` (written by the brief subagent: not yet decided) or `APPROVED` (written by the orchestrator, below).

Read the brief — the gate message is built from it, not from the subagent's return. Then append this block to `progress.md`, emit the message, and STOP:

```markdown
## Awaiting Design Approval

Brief: SDD/requirements/DESIGN-[###]-[feature-name].md (revision N)
Re-plan: <no | yes — the slice review it follows: <review-path>>
```

> **Design brief ready. No detailed planning happens until you approve it.**
> [After a revision round, first: one line stating what changed.]
> [The brief's "In one paragraph", verbatim]
> **Tiers:** building **Tier [N]** — [one line]. Left for later: Tier 2 — [one line]; Tier 3 — [one line]. [Or: "Tiers: not applicable — [the brief's reason]".]
> **Decisions made:** [D1 title — chosen option] · [D2 …]
> **Growth budget:** [the brief's three `## Growth budget` lines, on one line] — new files: [each path the table names as new]. Approving the brief approves this budget: when the finished feature adds more than one and a half times either line estimate, the flow stops before its final commit.
> **Questions for you:** [Q1 — options — recommended (a)] · [Q2 …] [Or: "None."]
> **Research review:** [one line: critical-review severity and whether findings were resolved] [· ADRs captured: [numbers] — only when an `## ADR Capture - Done` line that names any already follows the latest `## ADR Candidates` entry, as at a re-plan's gate. Otherwise omit this part.]
> **Tracing foundation:** [the brief's `## Tracing foundation` line — only when the brief has that section. Otherwise omit this line.]
> **ADR candidates:** [title — chosen option] · [title — chosen option] — written as decision records when you approve; name any you want dropped. [Only when the latest `## ADR Candidates` entry lists any and no `## ADR Capture - Done` line follows it. Otherwise omit this line.]
> Brief ([N] lines): `SDD/requirements/DESIGN-[###]-[feature-name].md`
> Research: `SDD/research/RESEARCH-[###]-[feature-name].md`
> **Before you approve:** `/worth-building SDD/requirements/DESIGN-[###]-[feature-name].md` asks whether this should be built as planned at all — the cheapest test that could show the idea does not work, and whether the plan runs it first. Optional; the flow does not run it for you.
> Reply with your answers and any changes — including `tier 2` or `tier 3` to build more now. `approve` accepts the brief as written, and is available once every question above has an answer. `stop` halts here.

If the brief's first line under its title is `Too large for one brief — recommend decomposition` or `Too large for one cycle — no cut of this tier fits`, show that line and the seams it names in place of the summary, and offer only a change request or `stop` — there is nothing to approve. On a next-tier cycle, the change request is how the user narrows what this cycle builds (for example, "build only the first of those seams now"); do not suggest running a decomposition, whose items would no longer be tied to the tier plan.

**The `Before you approve` line is a reminder, not a step.** It is shown at every gate — a revision round and a re-plan's gate included. The orchestrator never invokes the `worth-building` skill itself, the gate does not wait for it, and nothing is recorded about whether it was run. If the user runs it, its verdict reaches the flow only as their reply: a change request (2.5c), a different tier, or `stop`. Omit the line in both `Too large for one …` cases — there is no plan to judge yet.

Act on the reply:

- **Answers or changes** (including a different tier) → 2.5c.
- **`approve`** → first look for `SDD/OBSERVABILITY.md` once more. If it is now there and the brief has a `## Tracing foundation` section (it was written while the record was absent, so it holds no decision on how answer quality is judged), do not approve: run 2.5c with the line `OBSERVABILITY: present — apply rules 11 and 13 afresh` in place of a user reply, and the gate fires again. Otherwise the reply is accepted only when the brief's `## Questions for you` is `None.`. Append `## Design Brief - APPROVED (revision N, tier T)` to `progress.md` — `T` is the brief's recommended tier (`1`, `2`, `3`), or `none` when the brief says tiers are not applicable — then append `Observability record: present` or `Observability record: absent` beneath it, from that last look: the cycle's observability line, from which 3c settles the tracing and evals gates. Then proceed to 3a. If any question is still open, **refuse**: reply with the open questions, say that each needs an answer ("use your recommendation" counts as one, given per question), and stay at the gate. Nothing is rewritten and nothing is assumed.
- **`stop`** → leave `## Awaiting Design Approval` as the latest block and halt. `/sdd-flow continue` re-shows this gate.

**ADR candidates.** Research's ADR step (2b) proposes candidates and writes none; this gate is where the user accepts them. The `ADR candidates:` line is built from the latest `## ADR Candidates` entry in `progress.md`, minus any candidate already dropped.

- **A reply that drops a candidate** — at approval or in an earlier round — is recorded at once: append `## ADR Candidate Dropped - <title>` to `progress.md`, one line per candidate, so the choice survives a stop.
- **On `approve`**, after the `## Design Brief - APPROVED` line and before 3a: if the entry lists any candidate not dropped, spawn ONE **`agent-engineering:sdd-workhorse`** subagent with `bodies/adr-capture.md` in **AUTO mode**, passing the research document, the existing `SDD/adr/`, and the accepted candidate titles ("write exactly these"). Then append `## ADR Capture - Done (<ADR numbers | none>)` — `none` when every candidate was dropped or the entry said `none`. The records are committed at 3f.
- A re-plan's gate does not repeat this: a `## ADR Capture - Done` line already follows the candidates.

**Mirror the tiers to BB tasks** on approval, when `T` is not `none` — before spawning 3a, so the task keys the script writes into the tier plan are part of the 3f commit:

```bash
python3 "$SKILL_ROOT/scripts/tier-mirror.py" sync <TIER_PLAN> --active <T> --brief SDD/requirements/DESIGN-[###]-[feature-name].md
```

Record and report the result as `phases/tier-mirror.md` requires. It creates the tracker project (if the BB project has none), the feature's parent task, and one sub-task per tier; sets the approved tier — and any lower tier not yet shipped, which the same cycle builds — to in progress and the rest to backlog; and attaches the brief, and this thread when the flow runs inside a BB thread.

Pass the approved revision number and tier (`Design brief: revision N, approved, Tier T`) in the prompt of every later spawn that reads the brief.

### 2.5c. Revise

Spawn an **`agent-engineering:sdd-workhorse`** subagent, again with the model override `opus`:
- **Body:** `bodies/design-brief.md` — its **Revision runs** section.
- **Inputs:** the 2.5a inputs, the existing brief, and the user's reply **verbatim**.
- **Outputs:** updated brief and tier plan; updated RESEARCH document only if the reply showed it wrong on a point of fact; append `progress.md` (a new `## Design Brief - Drafted (revision N)` line).

Then return to 2.5b. The loop has no cap — every round is requested by the user.

### Re-plan

A re-plan asked for at a slice pause: read `phases/rare/replan.md` → Running the re-plan.
