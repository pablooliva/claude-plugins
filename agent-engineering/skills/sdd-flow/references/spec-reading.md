# Spec Reading — how an implementer reads the SPEC

The one definition of how an implementation spawn reads the SPEC named in its prompt: the per-slice implementer (`bodies/slice-start.md`), the whole-feature implementer and each of its chunks, and the per-slice scaffold (`bodies/implementation.md`). They read this file at the `SPEC_READING` path in their prompt, and never restate it.

A spec can be larger than one Read returns (SPEC-002 was 95 KB; its SLICE-004 implementer's Read of it failed). So the SPEC is **never read whole in one Read**: it is read by section, each found by its heading or its id line and read with offset and limit. What must not be missed — security rules, the state model, deviations, deferrals — lives in sections with fixed names, and those are read in full every time.

## 1. Find, then read

- Find a section with a search for its heading line (`^## Intent`, `^### State model`, `^### SLICE-004:`); it ends at the next heading of the same or a higher level. Find an id with a search for a list item or heading that opens with the id as a whole word, whatever follows it and with or without bold — `^\s*(- |### )\**REQ-012\b` matches `- REQ-012:`, `- REQ-012 (script part):` and `- **REQ-012**:`. An id can be defined in more than one place (a script part and a flow part): read every match. An id's entry ends where the next id's entry, or the next heading, begins (an EDGE or FAIL entry has indented sub-lines — read them too).
- Read each with offset and limit covering exactly that range. A section or entry too long for one Read is read in consecutive parts until its end. Entries that sit close together in one section are read as one range, from the first to the last, when that range fits in one Read.
- **The SPEC counts once on your Safety-Net counter** — the Safety-Net Rule counts a file read in parts once.
- A section that is not in the SPEC (`### State model`, `### Planned call graph`) is not there: go on without it. An id your slice or chunk is given that is not in the SPEC is a gap: build nothing for it, never guess its text, record it under `### Implementation Deviations` in the IMPLEMENTATION-PLAN, and name it in your return.

## 2. Always read, in full

Every implementation spawn reads these, whatever its slice or chunk names:

1. The frontmatter (the block between the first two `---` lines).
2. `## Intent`.
3. `## Deviations from Design Brief`.
4. `## Deferred to Later Tiers` — what is deliberately not built; build none of it, and keep the loud failure its row names.
5. `### Non-Functional Requirements` — every security (`SEC-`) and experience (`UX-`) rule, whichever slice names them; a rule here holds on every path the work adds.
6. `## Implementation Constraints`.
7. `### State model`, when the SPEC has one.
8. `### Planned call graph`, when the SPEC has one and the prompt says `tracing: on`.
9. `## Validation Strategy` — it holds `### Evals` and the abuse-case and integration tests the work may owe.

## 3. Then read what the work names

- **A slice** (`bodies/slice-start.md`): its `### SLICE-XXX:` entry; the `### MODULE-XXX:` entry of each module on its `Modules touched:` line; and the entry of every REQ, EDGE, FAIL, SEC and UX id on its `REQs satisfied:` and `Also covers:` lines.
- **A whole-feature chunk**: the entries of the REQ, EDGE and FAIL ids the prompt gives as its chunk.
- **A whole-feature implementer with no chunk**: every section of the SPEC, each in its own Read (§1).
- **The per-slice scaffold**: `## Delivery Slices`.
- **One level of references.** An id named in what you read whose rule shapes what you build — a REQ that says it prints REQ-012's delimiter lines, a FAIL that names the REQ it degrades — is read by its id too. Ids named in that second read are not followed further.

## 4. What is never done

- No Read of the whole SPEC file without offset and limit.
- No skipping a section of §2 because the slice or chunk does not name it.
- No edit to the SPEC (the bodies' own rules on `### Evals`, `Traced nodes:` and the frontmatter still hold).
