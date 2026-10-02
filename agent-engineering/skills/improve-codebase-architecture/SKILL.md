---
name: improve-codebase-architecture
description: "Scan an existing codebase for deepening opportunities (shallow modules that could become deep ones), present them as a visual HTML report, then interview you through whichever one you pick. Survey only — never edits code. User-invoked: `/improve-codebase-architecture [area or spec path] [report only]`."
disable-model-invocation: true
---

# Improve Codebase Architecture

Surface architectural friction in code that already exists and propose **deepening opportunities**: refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

This is a **survey**. It produces one HTML file outside the repo and a conversation. It never changes code, and it never writes into the repo. The refactor itself happens later, through the normal build flow.

Adapted from `improve-codebase-architecture` in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT — see the plugin's `THIRD-PARTY-NOTICES.md`). Self-contained: everything it needs is under this skill's `references/`.

## Before you start

Read [references/codebase-design.md](references/codebase-design.md) — the architecture vocabulary (**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**) and its principles (the deletion test, "the interface is the test surface", "one adapter = hypothetical seam, two = real"). Use these terms exactly in every suggestion, and don't drift into "component," "service," "API," or "boundary." The same standard is what `sdd-flow`'s module-depth specialist applies to a spec, so a candidate from this skill and a finding from that review mean the same thing by "shallow".

Then read what the project has already settled, if the files exist. Absence is normal; do not create them.

- **Domain glossary** — the first that exists of `SDD/UBIQUITOUS_LANGUAGE.md`, `GLOSSARY.md`, `CONTEXT.md`. It gives names to good seams.
- **ADRs** — `SDD/adr/` (this plugin's location), else `docs/adr/`. They record decisions this skill must not re-litigate.

## Invocation

- **No argument** — scan the codebase's hot spots (see step 1).
- **An area, module, or pain point** — scope the scan to it.
- **A spec path** (e.g. `SDD/requirements/SPEC-012-….md`) — the question becomes "how can we make this change easy?": scan the code the spec will touch. This is the most useful way to run it before a big build.
- **`report only`** (or "don't interview me") — stop after step 2. Do not start step 3.

## Process

### 1. Explore

**Scope before you scan: YAGNI.** Deepening a module pays off by making future changes to it easier, so put extra weight on the parts of the codebase that have recently changed. Decide *where* to look before you look:

- If the user named a direction (a module, a subsystem, a pain point, a spec), take it, and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline --stat`) to find the hot spots — the files and areas that keep coming up — and let those paths pull your attention first. If the changes are scattered with no clear hot spot, widen the net.

Then spawn a read-only sub-agent (the `Explore` agent type where available; otherwise explore inline) to walk the scoped area. Brief it with the vocabulary file's path and the scope. Don't follow rigid heuristics; explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — a caller must learn nearly as much to use them as to do the work itself?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: imagine it deleted, its code folded into its caller or neighbour. If that *concentrates* complexity behind a smaller interface — callers lose a hop and learn nothing new — it was a pass-through, and it is a candidate. If the complexity would *spread* across its callers, it was earning its keep: drop it. Only the "concentrates" cases earn a card.

**Finding nothing is a valid result.** If no candidate passes the deletion test with real friction behind it, say so plainly — "no Strong candidates in <scope>" — and list what you examined. Do not pad the report with `Speculative` cards to look productive.

### 2. Present candidates as an HTML report

Write a self-contained HTML file to the OS temp directory so nothing lands in the repo. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `<tmpdir>/architecture-review-<timestamp>.html` so each run gets a fresh file. Open it for the user (`open <path>` on macOS, `xdg-open <path>` on Linux, `start <path>` on Windows) and tell them the absolute path.

For each candidate, render a card with:

- **Files**: which files/modules are involved
- **Problem**: why the current architecture is causing friction
- **Solution**: plain English description of what would change
- **Benefits**: explained in terms of locality and leverage, and how tests would improve
- **Before / After diagram**: side-by-side, illustrating the shallowness and the deepening
- **Recommendation strength**: one of `Strong`, `Worth exploring`, `Speculative`, rendered as a badge

End the report with a **Top recommendation** section: which candidate you'd tackle first and why.

**Use the project glossary's vocabulary for the domain, and the codebase-design vocabulary for the architecture.** If the glossary defines "Order," talk about "the Order intake module," not "the FooBarHandler," and not "the Order service."

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly in the card (e.g. a warning callout: _"contradicts ADR-0007, but worth reopening because…"_). Don't list every theoretical refactor an ADR forbids.

See [references/html-report.md](references/html-report.md) for the full HTML scaffold, diagram patterns, styling guidance, and the no-network fallback.

Do NOT propose interfaces yet. After the file is written, ask the user: "Which of these would you like to explore?" — then stop and wait. In `report only` mode, end here.

### 3. Interview loop (one candidate per session)

Once the user picks a candidate, follow [references/interview.md](references/interview.md) to walk the decision tree with them: constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive. Classify the candidate's dependencies with [references/deepening.md](references/deepening.md) — the category decides how the deepened module is tested across its seam.

Take one candidate per session. The report, the interview, and the resulting decision together fill a context window; the remaining candidates stay in the report file for another day.

As decisions crystallize:

- **Naming a deepened module after a concept the glossary lacks, or sharpening a fuzzy term?** Do not edit the glossary. Record the term and its definition in the decision summary (below) so the next build picks it up — in an `sdd-flow` project, `SDD/UBIQUITOUS_LANGUAGE.md` is written by the flow's own completion steps.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR, framed as: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing; skip ephemeral reasons ("not worth it right now") and self-evident ones. On yes, hand the decision to the `cross-cutting-adr` skill (`/adr-capture`), which writes it under `SDD/adr/`.
- **Want to explore alternative interfaces for the deepened module?** Follow [references/design-it-twice.md](references/design-it-twice.md) and its parallel sub-agent pattern.

### 4. Hand off the decision

The output of the interview is a decision, not a diff. Close with a **decision summary** printed in the conversation (not written to the repo):

- the candidate, in glossary terms, and the files involved
- the agreed shape of the deepened module: its interface (everything a caller must know), what sits behind the seam, the adapters
- the dependency category and what it means for tests — which existing tests are replaced, what the new tests assert at the interface
- any new or sharpened domain terms
- what was explicitly ruled out, and why

Tell the user this summary is the task description for the build: paste it into `/sdd-flow` (or `/research-clarify` first, if the shape is still loose). Do not start the refactor here.

## It's working if

- Candidates name the domain's concepts, not invented class names.
- Candidates cluster in recently edited files, not dormant corners.
- No file in the repo changed during the run. The only new file is the HTML report in the temp directory.
- It stopped after the report and asked which candidate to explore.
- Each card states its payoff as locality or leverage and says which tests get simpler — never just "cleaner".
