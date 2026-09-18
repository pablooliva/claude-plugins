# Prompt Doctor

Manual entry point for the `prompt-doctor` skill. Diagnoses a task prompt you are about to send to an agent against the ten-component anatomy, before you send it.

This is the normal way to reach the skill. It is user-invoked by design — it does not watch the conversation and offer itself whenever a prompt goes by.

## When to Use This Command

- Before kicking off a long or unattended agent run, where a missing early-exit or a mis-worded done-condition costs you the whole run.
- When a previous run went sideways and you suspect the prompt, not the model.
- When you want to know which of the ten components your draft actually covers.

## When NOT to Use This Command

- To optimize `CLAUDE.md` / `AGENTS.md` — use the `improve-claude-md` skill.
- To author a skill, system prompt, or agent definition — different genre, different components.
- To actually run the task. This command reviews the prompt; it never executes it.

## 1. Invoke the Skill

Hand the prompt text to the `prompt-doctor` skill via the Skill tool. The skill will:

1. Confirm exactly which text is the specimen under review.
2. Classify the run shape (autonomous run / scoped task / transform), which sets the bar.
3. Grade all ten components — Present / Weak / Missing / N-A — with quoted evidence.
4. Say, for each gap, what the model is now free to decide for itself.
5. Ask you for the facts only you hold (capped at five questions).
6. Offer a rewrite — and produce one only if you ask, using only your own content.

## 2. Supported Invocation Forms

```
/prompt-doctor
```

With no argument, the skill takes the most recent prompt draft in the conversation and quotes it back for confirmation before grading.

```
/prompt-doctor <paste the prompt inline>
```

```
/prompt-doctor path/to/draft-prompt.md
```

Reads the file. This is the only file the skill reads besides its own component catalog.

## 3. Stop Conditions

The skill stops without a diagnosis if:

- The specimen boundary is unclear and you don't confirm it.
- The target is a `CLAUDE.md`, a skill, or a system prompt — it will redirect rather than mis-apply the anatomy.
- There is no draft to diagnose (it will offer to interview you against the components instead, and say plainly that it is drafting, not diagnosing).

## Remember

The skill never executes the prompt under review and never invents stakes, constraints, deadlines, or priorities. A missing component produces a question for you, not a plausible guess. Unanswered slots survive into any rewrite as visible placeholders.

Highest-value single check: the done-condition. "Come back with a solution" and "come back with a confident *path to* a solution" produce completely different runs.
