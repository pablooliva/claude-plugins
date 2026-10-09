# Test Integrity — What a Real Test Is, and the Lens That Checks It

The one definition of the flow's **Test Integrity Lens**. The implementer bodies read §1; the code review, the slice review, and the implementation critical review run the lens (§2–§6), and the final verification runs its last-look checks (§5); fix subagents follow §7. No body restates it. The path reaches each of them as **TEST_INTEGRITY** in its prompt.

**Why this exists.** The flow's gates are green test runs: a slice is delivered when its acceptance check passes, a review approves at 100%. An author that is rewarded for green has two ways to get there — make the code right, or make the test agree with the code. The second is cheaper and looks identical in a pass count. It takes several forms: a test whose expected value was copied from what the code happened to return, a test that asserts nothing that could be false, a mock standing where the logic should be, an existing test loosened until it stopped failing, code that recognises the test's inputs. Each one leaves a requirement marked as verified that nothing verifies — and with it goes the tests' second job, which is to make wrong business logic and a badly placed boundary show up as a failure. The enforcement-site standard already closes this for controls (a control whose tests cannot fail is not a control); this standard closes it for every other requirement.

---

## 1. What a real test is (the implementer's rules)

A test of a requirement is **real** when all four hold:

1. **Its expected value comes from the SPEC.** The requirement, an edge case, a failure scenario, or a worked example in the spec says what the outcome must be, and the test asserts that — written out as a literal or derived by reasoning the spec gives. Never obtain an expected value by running the code and pasting what it printed, and never compute it in the test with the same function, formula, or helper the code uses.
2. **It fails when the behaviour is broken.** If the line that implements the requirement were deleted or its condition inverted, this test would go red. A test that only checks that something was returned, that no exception was raised, or that a mock was called does not meet this.
3. **It runs the code that holds the logic.** A stand-in (mock, stub, fake, patch) replaces only what lies outside the application — the network, another service, the clock, randomness, a paid API. The module where the requirement's logic lives is never the thing replaced, and neither is one of the application's own modules that sits between the test's entry point and that logic.
4. **It checks an outcome the spec names** — a returned value, stored state, an emitted message, an error a caller sees. A test that asserts a private helper was called, or the order of internal calls, tests how the code is written today and breaks on a harmless refactor while passing on a wrong result.

And three things the implementer never does to reach a green run:

- **Never weaken a test that fails.** No deleting it, skipping or expected-failing it, loosening its assertion, changing its expected value, or narrowing what the test command collects. A failing test means the code is wrong or the spec changed. If the SPEC really says the behaviour is now different, change the test and record the requirement that says so under `### Test Changes` in the IMPLEMENTATION-PLAN — one line per changed or removed pre-existing test: the test, what changed, the `REQ-XXX` that requires it.
- **Never teach the code about the tests.** No branch on a value because a test passes it, no table of the tests' cases, no behaviour that depends on running under the test runner.
- **Never report a run you did not make.** The pass count in the IMPLEMENTATION-PLAN is from a real run of the whole suite, after the last edit.

## 2. When the lens runs, and with what

| Review | Runs | Changes it reads |
|---|---|---|
| Per-slice 4b (`bodies/slice-review.md`) | the full lens, on the slice's requirements | working tree against the slice's `BASE` |
| Whole-feature 4b (`bodies/code-review.md`) | the full lens, on every requirement | working tree against `BASE` |
| 4d implementation critical review (`bodies/critical-review.md`) | the lens **by reading** (§5) | working tree against `BASE`; in per-slice mode, the committed slices since `BASE` |
| 4e.5 verification (`bodies/code-review.md`, `MODE: site-verification-only`) | the **last-look checks** (§5) — after the last fix round | working tree against `BASE` |

It has no gate: it runs in every cycle. Inputs, all from the prompt: **TEST_INTEGRITY** (this file), the SPEC, the IMPLEMENTATION-PLAN (for `### Test Changes`), and `BASE`. A review with no `BASE` runs every check except T1 and says so.

**Test files** are found, not assumed: the files the project's test command collects, plus fixtures, snapshot or golden files, and the configuration that decides what is collected and how (`pytest.ini`, `pyproject.toml`, `conftest.py`, `jest.config.*`, `package.json` scripts, CI workflow files, a `Makefile` target).

Requirements that are **controls** are already proven site by site under the enforcement-site standard. T4 does not repeat that work for them; every other check applies to their tests as to any other.

## 3. The checks

Each check has an ID. Every finding names the test (`file::name`), the requirement, and the evidence.

**T1 — Tests that existed before were not weakened.** List every test file changed or deleted since `BASE`:

```bash
git diff --stat --no-renames BASE -- <test files and test configuration>
```

For each pre-existing test that was deleted, renamed away, skipped, marked expected-to-fail, or had an assertion removed, loosened, or its expected value changed: find its line under `### Test Changes` in the IMPLEMENTATION-PLAN and open the `REQ-XXX` it cites. The change stands only if that requirement really says the old behaviour is gone. A weakened or removed test with no line, or a line whose requirement does not say so → **HIGH**. A file new since `BASE` has nothing to weaken; it is covered by the checks below.

**T2 — Nothing is kept out of the run.** Read the test command and the configuration: a narrowed collection path, a deselect or ignore, a name filter, a skip or expected-failure marker, a commented-out test or assertion, a test command made unable to fail (`|| true`, a swallowed exit status), a retry-until-green setting — any of these introduced since `BASE`, or covering a test of this feature, is **HIGH** unless the SPEC or the IMPLEMENTATION-PLAN gives a reason that holds. Compare the number of tests the run collected with the number the test files define; a difference nobody explains is a finding.

**T3 — Expected values come from the SPEC.** For each requirement's tests, trace the expected value to its source.
- Stated by the SPEC, or derived from it by reasoning shown in the test → passes.
- Computed in the test by calling the code under test, or by a copy of its formula → **HIGH**: the test compares the code with itself.
- A snapshot or golden file with no sign that anyone checked its content against the SPEC → **MEDIUM**; **HIGH** when it is the requirement's only test.
- A value the SPEC does not give and cannot be derived from it → **MEDIUM**, and say which: the test invented a requirement, or the spec has a gap.

**T4 — The test fails when the behaviour is broken.** For each requirement in the sample (§4): find the line or condition that implements it; break it — invert the condition, return a constant, delete the line — run that requirement's tests; restore; confirm the file is exactly what it was before you broke it (keep a copy, or compare `git diff -- <file>` taken before and after — the work under review is uncommitted, so that diff is not empty to begin with). At least one test must fail, and for the reason the requirement gives.
- No test fails → **HIGH**: the requirement is untested, whatever the coverage map says.
- A test fails only incidentally (an import error, an unrelated assertion) → **MEDIUM**.

Before breaking anything, read the test: one with no assertion, an assertion that cannot be false (`is not None` on a value that is never `None`, a status "in" every possible status), an assertion inside a branch that never runs or after a swallowed exception, or an assertion only on what a mock was told to return → **HIGH** without running anything.

**T5 — Stand-ins sit at the edge of the application.** For each test that uses a mock, stub, fake, or patch, name what it replaces.
- Something outside the application → passes.
- The module that holds the requirement's logic, or the function under test itself → **HIGH**.
- One of the application's own modules on the path between the test's entry point and the logic → **MEDIUM**; **HIGH** when no other test of that requirement runs the real path.
- A requirement that crosses modules and has only tests where every collaborator is replaced → **MEDIUM**: nothing checks that the pieces work together.

**T6 — The code was not fitted to the tests.** Read the production code the feature changed for:
- a literal in a condition that appears as a test input and nowhere in the SPEC;
- a lookup of the tests' cases where the SPEC describes a rule;
- behaviour that depends on running under the test runner (an environment variable, a `testing` flag, the runner's name in `sys.modules`);
- a requirement stated for a range and implemented only for the values the tests use.

Each is **HIGH**. Then **probe**: for each requirement in the sample (§4), choose an input the SPEC covers and **no test uses** — a different valid value, the other side of a boundary — work out from the SPEC what the outcome must be, and run the real code with it (a throwaway script or test; delete it afterwards and confirm nothing is left behind). An outcome that differs from the SPEC's → **HIGH**: the code is right only where it is tested.

**T7 — The test says what it claims.** For each requirement's tests, state in one line the outcome a user or caller would see that the test proves.
- A test named or mapped to `REQ-XXX` that asserts something else → **HIGH**.
- A test that proves only internal structure — a private helper's result, a call count, an order of internal calls — when the SPEC names an observable outcome → **MEDIUM**.
- A requirement whose tests all pass through a seam built only for the test → **MEDIUM**, and say what that implies about the design: logic that can be tested only by reaching inside is logic sitting behind the wrong interface.

## 4. How much to check

T1, T2, and T7 cover every test the changes touch. T3 and T5 cover every test of every requirement in scope. T4 and T6's probe are sampled, by the `Risk:` tier of the module that implements the requirement (SPEC `## Modules`):

| Module risk | T4 mutation and T6 probe |
|---|---|
| `high` | every requirement |
| `medium`, or no tier given | at least one requirement per module and at least **25%** of its requirements, rounded up |
| `low` | at least one requirement per module |

Choose the requirements where a wrong answer costs most — money, permissions, data written, a decision shown to a person — before the ones that are easiest to break. A sample that turns up a HIGH is widened to every requirement of that module.

## 5. The lens by reading (4d), and the last-look checks (4e.5)

The implementation critical review runs T1, T2, T3, T5, T7, the reading half of T4 (the assertions that cannot be false), and the reading half of T6 (the four signs) over the whole feature. It runs a T4 mutation or a T6 probe only where its reading gives it a reason to doubt a specific test, and it says which. It does not re-sample: the 4b review did that, and this pass is there to catch what a second reader sees and what the fixes after 4b changed. T1 here has a particular target — **tests changed by a fix subagent since the 4b review**, where a finding may have been answered by weakening the test that exposed it.

**The last-look checks** are what the 4e.5 verification runs, in every cycle, because it is the only review after the last fix round: **T1, T2, T3, and the reading half of T4** — no mutation, no probe. T1 and T2 catch a pre-existing test weakened or left out. T3 and the reading half of T4 are there for the tests **this feature added**: T1 cannot see a change to them (their files are new since `BASE`, and the work is uncommitted, so there is no earlier version to compare with), so a fix that changed an expected value or loosened an assertion in one is caught by reading it again against the SPEC — is the expected value still the spec's, can the assertion still be false.

## 6. What the review writes

A `## Test Integrity` section in the review document, with this table and the two lists under it:

```markdown
## Test Integrity

| Check | Examined | Result | Findings |
|---|---|---|---|
| T1 Existing tests not weakened | <n> test files changed since BASE; <n> pre-existing tests changed or removed | PASS / FAIL / NOT RUN — no BASE | <#s or —> |
| T2 Nothing kept out of the run | test command + <config files>; collected <n> of <n> defined | PASS / FAIL | <#s or —> |
| T3 Expected values from the SPEC | <n> requirements | PASS / FAIL | <#s or —> |
| T4 Fails when broken | <n> of <n> requirements mutated | PASS / FAIL | <#s or —> |
| T5 Stand-ins at the edge | <n> tests with stand-ins | PASS / FAIL | <#s or —> |
| T6 Code not fitted to tests | <n> files read; <n> probes | PASS / FAIL | <#s or —> |
| T7 Tests say what they claim | <n> requirements | PASS / FAIL | <#s or —> |

**Mutations (T4):** one line each — `REQ-XXX <file>:<symbol>: <what was broken> → <failing test id>` or `→ NO TEST FAILED → finding <#>`. Every one restored: yes.
**Probes (T6):** one line each — `REQ-XXX: input <value> (no test uses it); SPEC says <outcome>; code gave <outcome>` — or `→ finding <#>`.
```

Lens findings are ordinary findings of the review: listed with the others at their severity, counted in the review's marker, resolved in the same fix loop, and — for the slice review and the code review — tagged `[needs-code-or-test]`. **A HIGH lens finding is a rejection criterion.** A check with nothing to examine says so in its row ("no stand-ins used") — never a bare PASS.

## 7. How a lens finding is fixed

- **By making the test real or the code right — never by removing the evidence.** A test that could not fail is given an assertion that can, with an expected value from the SPEC. A mocked-away module is run for real. Fitted code is replaced by the rule the SPEC states.
- **A weakened test is restored** to what it asserted at `BASE` (`git show BASE:<path>`), and the code is fixed until it passes — unless the SPEC requires the new behaviour, in which case the missing `### Test Changes` line is added, citing the requirement.
- **A fix never weakens a test either.** §1's three "never" rules bind a fix subagent exactly as they bind the implementer; the 4d pass reads what the fixes before it changed (§5), and the 4e.5 verification, which always runs, reads the tests once more after the fixes that follow it (the last-look checks, §5).
- **When the expected value cannot be found in the SPEC,** the fix does not invent one. It records the gap under `### Implementation Deviations` in the IMPLEMENTATION-PLAN — the requirement, the question the spec leaves open, the value assumed and why — so the gap reaches the completion summary and the user.
