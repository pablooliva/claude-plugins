# LangSmith Skills

Three Claude Code skills that drive the [`langsmith` CLI](https://github.com/langchain-ai/langsmith-cli) to work with **your own** LLM applications:

| Skill | Use it when you want to… |
|-------|--------------------------|
| `langsmith-trace` | Add tracing to an app (Python/JS) **or** query/export trace and run data for debugging and analysis |
| `langsmith-dataset` | Create, upload, and manage evaluation datasets (final-response, single-step, trajectory, RAG) |
| `langsmith-evaluator` | Build evaluation pipelines — LLM-as-judge or custom code evaluators, run functions, and run evaluations |

> **Not the same as `langsmith-tracing`.** The official [`langsmith-tracing`](https://github.com/langchain-ai/langsmith-claude-code-plugins) plugin traces *your Claude Code sessions* to LangSmith. This plugin packages skills for instrumenting and evaluating *your own applications*. The names overlap; the purposes don't. You can run both.

## Prerequisites

These skills are thin guides over an external CLI and a hosted API. Two things must exist on the machine before the skills are useful:

### 1. The `langsmith` CLI binary

The skills shell out to a `langsmith` command. Install it (downloads a single binary to `~/.local/bin` or `/usr/local/bin`):

```bash
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh
```

Make sure the install dir is on your `PATH`, then verify:

```bash
langsmith --version      # e.g. "langsmith version 0.2.6"
```

To update later: `langsmith self-update`.

### 2. A LangSmith API key

Set these as environment variables (in `~/.zshrc` / `~/.bashrc`, a project `.env`, or Claude Code's `~/.claude/settings.json` `env` block):

```bash
export LANGSMITH_API_KEY=lsv2_pt_...      # required
export LANGSMITH_PROJECT=your-project     # optional: default project for trace/run queries
export LANGSMITH_WORKSPACE_ID=...         # optional: only for org-scoped keys
export LANGSMITH_ENDPOINT=...             # optional: only for self-hosted LangSmith
```

Get a key at <https://smith.langchain.com> → Settings → API Keys.

> The CLI is all you need to **query** existing traces, datasets, and evaluators. To **instrument** an app, you'll also install the LangSmith SDK in that app's project (`pip install langsmith` or `npm i langsmith`) — the `langsmith-trace` skill walks through it.

## Install the plugin

From within Claude Code:

```
/plugin marketplace add pablooliva/claude-plugins
/plugin install langsmith-skills@pablooliva
/reload-plugins
```

If you already have the `pablooliva` marketplace, refresh it first:

```
/plugin marketplace update pablooliva
/plugin install langsmith-skills@pablooliva
/reload-plugins
```

Verify the skills are available with `/skills` — you should see `langsmith-trace`, `langsmith-dataset`, and `langsmith-evaluator`.

## Migrating from standalone skill copies

If you previously installed these as loose skills under `~/.claude/skills/` (each as a single `SKILL.md`), **remove those copies after installing the plugin** so the same skill name isn't defined twice:

```bash
rm -rf ~/.claude/skills/langsmith-dataset \
       ~/.claude/skills/langsmith-trace \
       ~/.claude/skills/langsmith-evaluator
```

Then `/reload-plugins` (or restart the session). The plugin-managed copies update automatically with `/plugin marketplace update pablooliva`; the loose copies did not.

## Usage

The skills are invoked automatically when relevant, or explicitly:

- "Query the last 10 traces from my-project" → `langsmith-trace`
- "Build an eval dataset from these traces" → `langsmith-dataset`
- "Create an LLM-as-judge evaluator for correctness" → `langsmith-evaluator`
