# Regression Eval Capture

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. You cannot spawn subagents and cannot invoke slash commands; all work happens inline in your own context.

Scaffold a LangSmith regression eval dataset for a just-shipped feature so future model or prompt changes can be tested against golden examples. This sets up the infrastructure; it does NOT populate the dataset with examples. Real golden examples require real runtime data, which only accumulates after the feature runs in production.

Operationalizes the **Observability Imperative**: every model migration or prompt change will silently degrade quality unless you have a fixed reference to regress against.

## When Invoked

This body is invoked at the end of the implementation phase when the spec frontmatter declares `eval_required: true`. It is not intended for manual invocation.

Not every feature needs this. Good candidates: LLM-heavy pipelines (summarization, classification, extraction, RAG), agent workflows with probabilistic output, features where "quality" cannot be verified by a unit test. Bad candidates: deterministic CRUD, UI tweaks, pure data transforms that can be unit-tested.

## 1. Prerequisites Check

Before doing anything, verify the environment is ready:

```bash
# Check langsmith CLI is installed
which langsmith || echo "MISSING: install via curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh"

# Check API key is set
[ -n "$LANGSMITH_API_KEY" ] || echo "MISSING: LANGSMITH_API_KEY environment variable"

# Check project is configured (check env var and .env file)
[ -n "$LANGSMITH_PROJECT" ] || (grep -q "^LANGSMITH_PROJECT=" .env 2>/dev/null && echo "Found in .env") || echo "MISSING: LANGSMITH_PROJECT environment variable or .env entry"
```

If any prerequisite is missing, do NOT halt the flow. Append the following warning to `SDD/orchestration/progress.md` (append-only — never overwrite):

```
## Eval Capture Warning — [YYYY-MM-DD]
Prerequisites missing for regression eval scaffold:
- [list which specific prerequisites are absent]
The feature has shipped. Set up LangSmith credentials and re-run the eval scaffold as a follow-up.
```

Then return immediately with a bounded summary (≤200 words) noting what was missing and the path `SDD/orchestration/progress.md`. The sdd-flow continues to "Done" state unblocked.

## 2. Identify Target Feature and Gather Metadata

Read the current feature's spec from `SDD/requirements/SPEC-[###]-[feature-name].md`. Extract:

- Feature name and slug (from filename).
- `langsmith_project:` frontmatter (if present) — overrides the env var for this feature's dataset.
- `eval_dataset_type:` frontmatter (if present): `final_response` (default) | `single_step` | `trajectory` | `rag`.
- `eval_evaluator_type:` frontmatter (if present): `llm_as_judge` (default) | `custom_code`.
- Success criteria section — these will be transformed into the evaluator's grading rubric.
- Implementation-notes section — tells you the feature's entry point and output shape.

## 3. Detect Language and Eval Directory Layout

Detect the repo's primary language to produce appropriate stubs:

- `package.json` present without `pyproject.toml`/`requirements.txt` → TypeScript.
- `pyproject.toml` or `requirements.txt` present → Python.
- Both present → default to Python and note the ambiguity in the progress log.
- Neither → default to Python (most common for LLM pipelines).

Determine the eval directory. Convention: `evals/` at the repo root. If `evals/` already exists, follow existing layout. Otherwise create:

```
evals/
├── README.md                          # Index of datasets and status
├── datasets/
│   └── [feature-slug].json            # Local dataset file (populated over time)
├── evaluators/
│   └── [feature-slug]_evaluator.{py,ts}
└── run_functions/
    └── [feature-slug]_run.{py,ts}
```

## 4. Create the LangSmith Dataset

Run the following CLI command directly via the shell:

```bash
langsmith dataset create \
  --name "regression-[feature-slug]" \
  --description "Regression eval for [feature-name]. Captured [YYYY-MM-DD] from SPEC-[###]-[feature-name]. Populate with 10-20 golden examples after feature runs in production for ≥1 week."
```

Check the exit code and output. If the command fails with an error indicating the dataset name already exists, do NOT re-create it. Instead, append a note to `SDD/orchestration/progress.md` (append-only):

```
## Eval Dataset Note — [YYYY-MM-DD]
Dataset `regression-[feature-slug]` already exists on LangSmith. Skipping creation; existing dataset retained.
```

Then continue to scaffold the remaining artifacts (evaluator stub, run function stub, README entry) — those files are local and safe to overwrite with updated stubs.

To verify the dataset was created (or already exists), you may run:

```bash
langsmith dataset list
langsmith dataset get "regression-[feature-slug]"
```

## 5. Write the Evaluator Stub

Produce a stub evaluator that encodes the spec's success criteria as a grading rubric. Write to `evals/evaluators/[feature-slug]_evaluator.{py,ts}`.

### Language-specific template — Python (LLM-as-Judge default)

```python
"""
Regression evaluator for [Feature Name].

Spec reference: SDD/requirements/SPEC-[###]-[feature-name].md
Dataset: regression-[feature-slug]

IMPORTANT (Golden Rule):
Before trusting this evaluator, run the feature's entry point on 2-3 real
inputs, inspect the actual output shape, and verify the extraction logic
in `_extract_output` matches what the agent actually produces.
"""
from langsmith import Client
from langchain_openai import ChatOpenAI

GRADING_RUBRIC = """
Grade the output against the following success criteria, derived from the spec:

[For each REQ-XXX in the spec's success criteria section:]
- REQ-XXX: [Requirement summary]
  Acceptance: [Acceptance criteria from spec]

Output shape expected: [Describe from spec's output section]

Score 1 if the output satisfies all criteria. Score 0 if any criterion fails.
Provide a brief comment explaining the score, citing specific criteria.
"""

judge = ChatOpenAI(model="gpt-4o", temperature=0)


def _extract_output(run):
    """Extract the comparable output from the run.

    CUSTOMIZE THIS. The shape depends on how your run function structures its output.
    Handle both local (RunTree) and uploaded (dict) run types.
    """
    outputs = run.outputs if hasattr(run, "outputs") else run.get("outputs", {})
    # e.g., return outputs.get("response") or outputs.get("classification")
    return outputs


def quality_score(run, example) -> dict:
    """LLM-as-Judge evaluator for regression testing.

    Returns one metric: score (0 or 1) + comment.
    """
    actual = _extract_output(run)
    expected = example.outputs

    prompt = f"""{GRADING_RUBRIC}

Expected output:
{expected}

Actual output:
{actual}

Return a JSON object: {{"score": 0 or 1, "comment": "explanation"}}"""

    response = judge.invoke(prompt)
    # Parse response, return {"score": ..., "comment": ...}
    # CUSTOMIZE parsing based on your JSON extraction pattern
    import json
    result = json.loads(response.content)
    return {"score": result["score"], "comment": result["comment"]}
```

### Language-specific template — TypeScript

```typescript
/**
 * Regression evaluator for [Feature Name].
 *
 * Spec reference: SDD/requirements/SPEC-[###]-[feature-name].md
 * Dataset: regression-[feature-slug]
 *
 * IMPORTANT (Golden Rule):
 * Before trusting this evaluator, run the feature's entry point on 2-3 real
 * inputs, inspect the actual output shape, and verify the extraction logic
 * in `extractOutput` matches what the agent actually produces.
 */
import { Client } from "langsmith";
import OpenAI from "openai";

const GRADING_RUBRIC = `
Grade the output against the following success criteria, derived from the spec:

[For each REQ-XXX in the spec's success criteria section:]
- REQ-XXX: [Requirement summary]
  Acceptance: [Acceptance criteria from spec]

Output shape expected: [Describe from spec's output section]

Score 1 if the output satisfies all criteria. Score 0 if any criterion fails.
Provide a brief comment explaining the score, citing specific criteria.
`;

const openai = new OpenAI();

function extractOutput(run: any): any {
  // CUSTOMIZE THIS based on actual run.outputs shape.
  return run.outputs?.response ?? run.outputs;
}

export async function qualityScore(run: any, example: any) {
  const actual = extractOutput(run);
  const expected = example.outputs;

  const response = await openai.chat.completions.create({
    model: "gpt-4o",
    temperature: 0,
    messages: [
      {
        role: "user",
        content: `${GRADING_RUBRIC}\n\nExpected output:\n${JSON.stringify(expected)}\n\nActual output:\n${JSON.stringify(actual)}\n\nReturn a JSON object: {"score": 0 or 1, "comment": "explanation"}`,
      },
    ],
  });

  const result = JSON.parse(response.choices[0].message.content ?? "{}");
  // Note: do NOT include `key` field when uploaded to LangSmith — column name comes from upload name.
  return { score: result.score, comment: result.comment };
}
```

### If spec declares `eval_evaluator_type: custom_code`

Instead of LLM-as-Judge, produce a deterministic evaluator stub that performs exact match or schema validation. Pull the comparison rules from the spec's success criteria. Emit a `TODO:` comment where the user must fill in the specific equality logic.

## 6. Write the Run Function Stub

Produce a stub run function that wraps the feature's entry point so it can be replayed against the dataset. Write to `evals/run_functions/[feature-slug]_run.{py,ts}`.

Python template:

```python
"""
Run function for [Feature Name].

Wraps the feature's entry point so LangSmith's evaluate() can replay
dataset inputs against it.

Dataset type: [final_response | single_step | trajectory | rag]
"""

# TODO: Import the feature's actual entry point.
# from your_package.feature_name import feature_entry_point


def run_feature(inputs: dict) -> dict:
    """Invoke the feature with dataset inputs.

    Inputs come from the dataset's `inputs` field. Return shape must match
    what the evaluator's `_extract_output` expects.

    Args:
        inputs: Dict with the keys defined by your dataset type. For
            `final_response`, typically {"query": "..."} or similar.

    Returns:
        Dict with the feature's output. For `final_response`, typically
        {"response": "..."}.
    """
    # TODO: Replace this with the actual feature invocation.
    # result = feature_entry_point(**inputs)
    # return {"response": result.output}
    raise NotImplementedError(
        "Populate this function with the feature's actual entry point."
    )


if __name__ == "__main__":
    # Local smoke test before running full eval.
    sample_input = {"query": "example"}  # TODO: match dataset shape
    print(run_feature(sample_input))
```

TypeScript template follows the same structure — import the feature's entry point, wrap it to return the expected output shape.

## 7. Update the Evals README

If `evals/README.md` does not exist, create it with:

```markdown
# Evaluations

Regression eval datasets for this repo's features. Each dataset captures golden input/output pairs that let us regression-test model upgrades, prompt changes, and refactors.

## Datasets

| Dataset | Feature | Spec | Status | Examples | Notes |
|---------|---------|------|--------|----------|-------|
| [fill in on capture] | [feature] | [spec path] | needs-population | 0 | Created [date]; populate after ≥1 week of runtime |

## Workflow

1. **Capture** — scaffolds dataset, evaluator stub, run function stub.
2. **Populate** — after feature runs in production, capture 10-20 diverse real examples into the dataset. Export traces and upload:
   ```bash
   langsmith trace export ./traces --project $LANGSMITH_PROJECT --limit 50 --full
   langsmith dataset upload /tmp/curated.json --name regression-[feature-slug]
   ```
3. **Regress** — before any model upgrade or significant prompt change, run the dataset through the evaluator. Compare scores against baseline.

## Populating Examples from Production Traces

The primary workflow is to export traces from LangSmith, select diverse examples, and upload them:

```bash
# Export recent traces from the feature
langsmith trace export ./traces --project $LANGSMITH_PROJECT --limit 50 --full

# Manually curate ~10-20 diverse examples (edge cases, common paths, failure modes)

# Upload curated examples to the dataset
langsmith dataset upload /tmp/curated.json --name regression-[feature-slug]
```
```

If `evals/README.md` already exists, append a new row to the Datasets table for this feature.

## 8. Append to Progress and Return

After scaffolding completes, append the following to `SDD/orchestration/progress.md` (append-only — never overwrite):

```
## Eval Capture Complete — [YYYY-MM-DD]
Feature: [feature-name]
Dataset created on LangSmith: regression-[feature-slug] (empty, awaiting examples)
Artifacts:
- evals/evaluators/[feature-slug]_evaluator.{py,ts}
- evals/run_functions/[feature-slug]_run.{py,ts}
- evals/README.md (created or updated)
Status: needs-population — populate after ≥1 week of production runtime
```

Return a bounded summary (≤200 words) with:

- Confirmation that the LangSmith dataset was created (or already existed and was skipped).
- List of local artifact paths written.
- A concise note of what the user must do to populate the dataset (run feature in production, export traces via `langsmith trace export`, curate examples, upload via `langsmith dataset upload`).

Do not emit interactive prompts or request user confirmation for any task-tracker follow-up. The sdd-flow orchestrator will relay the summary.

## Non-Blocking Failure Conditions

If any of the following occur, do NOT produce partial artifacts. Instead, append a warning to `SDD/orchestration/progress.md` and return immediately — the flow continues to "Done" state unblocked:

- `langsmith` CLI not installed.
- `LANGSMITH_API_KEY` not set.
- `LANGSMITH_PROJECT` not set and spec doesn't provide `langsmith_project:`.
- Repo language cannot be determined (both or neither language markers present).

On early return due to a failure condition, clean up any partially written files so the repo is left in the state it was before invocation — no orphan directories, no partial stubs.

## Remember

This scaffold's honest limitation is that it creates infrastructure, not data. Real golden examples come from real runtime. The stubs explicitly raise `NotImplementedError` and the README tracks `needs-population` status until the user populates.

The value shows up later: when you upgrade models or swap a prompt, you'll have a fixed reference to regress against. Without this scaffold, you'd be starting from zero at the least convenient moment.
