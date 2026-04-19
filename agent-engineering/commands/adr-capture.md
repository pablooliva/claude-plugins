# ADR Capture

Manual entry point for capturing a cross-cutting architectural decision as a numbered ADR under `SDD/adr/`. Delegates to the `cross-cutting-adr` skill for the actual capture logic.

Use this command when you want to be explicit about recording a decision, rather than relying on the skill's ambient detection of comparison-with-selection patterns in conversation.

## When to Use This Command

- After a technology selection discussion where a binding choice was made.
- When standardizing on a convention that other features will inherit.
- When superseding or deprecating a prior ADR.
- When the skill's ambient detection didn't fire but you want the decision captured anyway.

## When NOT to Use This Command

- For feature-scoped decisions — those belong in the SDD spec for that feature. The skill will apply the scope test and decline.
- For preference statements without durable scope ("I like X").
- For decisions that are still being actively debated (no selection made yet).

## 1. Invoke the Skill

Hand the user's description of the decision to the `cross-cutting-adr` skill via the Skill tool. The skill will:

1. Apply the scope test (is this cross-cutting?).
2. Gather the required inputs (title, context, decision, alternatives, consequences).
3. Determine the next ADR number.
4. Check for duplicates and supersession opportunities.
5. Render the ADR in the canonical format.
6. Confirm with the user before writing.
7. Write the file and update the index.

If any required input is missing from the invocation, the skill will ask for it.

## 2. Supported Invocation Forms

```
/adr-capture
```

With no argument, the skill extracts the decision from recent conversation context. It will ask clarifying questions if the context is insufficient.

```
/adr-capture <one-line decision statement>
```

Example: `/adr-capture Standardize on pgvector for all RAG features, replacing the prior plan to use Qdrant`.

The skill will treat the statement as seed context and ask for any missing inputs (alternatives considered, consequences, rationale).

```
/adr-capture --supersede NNNN
```

Explicitly flag that this new ADR supersedes an existing one. The skill will update the prior ADR's status and add cross-references.

## 3. Stop Conditions

The skill will stop gracefully without writing if:

- Scope test fails (feature-scoped, not cross-cutting).
- User cannot articulate a rationale for the decision.
- Duplicate ADR already exists and is not being superseded.
- User declines confirmation when shown the rendered ADR.

In each case the skill emits a clear reason and leaves the repo untouched.

## 4. Relationship to sdd-flow

`sdd-flow` invokes the `cross-cutting-adr` skill automatically during research-phase and planning-phase completion for decisions it detects (see the skill for full trigger logic). This command is the **manual** complement — use it any time, inside or outside an sdd-flow session.

## Remember

ADRs are for decisions that bind future work. Apply the scope test: *Will this choice be inherited by other features or parts of the system?* If yes, capture. If no, the decision belongs in the relevant feature's SDD spec, not here.
